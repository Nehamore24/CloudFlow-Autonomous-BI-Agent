import pandas as pd
import numpy as np


def _pct_change(current, previous):
    if previous == 0 or pd.isna(previous):
        return np.nan
    return (current - previous) / previous * 100


def run_analysis(df):
    df = df.copy()
    df["month"] = pd.to_datetime(df["month"])
    monthly = df.groupby("month", as_index=False).agg(revenue=("revenue", "sum"), orders=("orders", "sum"), customers=("customers", "sum"))
    monthly["aov"] = monthly["revenue"] / monthly["orders"]
    monthly["mom_growth_pct"] = monthly["revenue"].pct_change() * 100
    monthly["orders_growth_pct"] = monthly["orders"].pct_change() * 100

    latest_month = monthly["month"].max()
    previous_month = monthly["month"].sort_values().iloc[-2]
    latest = monthly[monthly.month == latest_month].iloc[0]
    previous = monthly[monthly.month == previous_month].iloc[0]

    segment = df.groupby(["region", "channel"], as_index=False).agg(revenue=("revenue", "sum"), orders=("orders", "sum"), customers=("customers", "sum"))
    segment["aov"] = segment["revenue"] / segment["orders"]

    latest_seg = df[df.month == latest_month].groupby(["region", "channel"], as_index=False).agg(revenue_latest=("revenue", "sum"), orders_latest=("orders", "sum"))
    prev_seg = df[df.month == previous_month].groupby(["region", "channel"], as_index=False).agg(revenue_previous=("revenue", "sum"), orders_previous=("orders", "sum"))
    issues = latest_seg.merge(prev_seg, on=["region", "channel"])
    issues["change_pct"] = (issues.revenue_latest / issues.revenue_previous - 1) * 100
    issues["orders_change_pct"] = (issues.orders_latest / issues.orders_previous - 1) * 100
    issues["priority"] = np.select([issues.change_pct <= -15, issues.change_pct <= -8], ["Critical", "High"], default="Normal")
    issues["signal"] = np.where(issues.change_pct <= -8, "Revenue decline", "Stable")
    issues = issues.sort_values("change_pct").reset_index(drop=True)

    # Statistical anomaly detection: flag segment-month revenue changes beyond 2.0 std from the segment's normal monthly pattern.
    seg_month = df.groupby(["month", "region", "channel"], as_index=False)["revenue"].sum()
    stats = seg_month.groupby(["region", "channel"])["revenue"].agg(["mean", "std"]).reset_index()
    seg_month = seg_month.merge(stats, on=["region", "channel"])
    seg_month["z_score"] = (seg_month.revenue - seg_month["mean"]) / seg_month["std"].replace(0, np.nan)
    anomalies = seg_month[seg_month.z_score.abs() >= 2].copy().sort_values("z_score")
    anomalies["severity"] = np.select([anomalies.z_score.abs() >= 3, anomalies.z_score.abs() >= 2], ["Critical", "Warning"], default="Watch")

    growth = _pct_change(latest.revenue, previous.revenue)
    insights = []
    if growth < 0:
        insights.append(f"Revenue declined {abs(growth):.1f}% month over month.")
    else:
        insights.append(f"Revenue grew {growth:.1f}% month over month.")
    worst = issues.iloc[0]
    best = segment.sort_values("revenue", ascending=False).iloc[0]
    insights.append(f"{worst.region} × {worst.channel} is the weakest latest-month segment at {worst.change_pct:.1f}% MoM.")
    insights.append(f"{best.region} × {best.channel} is the largest revenue segment across the analysis period.")
    if len(anomalies):
        a = anomalies.iloc[0]
        insights.append(f"Anomaly detected in {a.region} × {a.channel} during {a.month:%b %Y}; the movement is {abs(a.z_score):.1f} standard deviations from its normal pattern.")

    recommendations = []
    for _, row in issues[issues.priority != "Normal"].head(5).iterrows():
        action = "Validate channel conversion, order volume and campaign/source quality." if row.orders_change_pct < 0 else "Investigate pricing, mix and average order value before changing acquisition spend."
        recommendations.append({"priority": row.priority, "issue": f"{row.region} × {row.channel}: {row.change_pct:.1f}% revenue change", "action": action})
    if not recommendations:
        recommendations.append({"priority": "Normal", "issue": "No material segment decline detected", "action": "Continue monitoring and compare the next reporting period."})

    return {
        "monthly": monthly, "segment": segment, "issues": issues, "anomalies": anomalies,
        "insights": insights, "recommendations": recommendations,
        "latest_month": latest_month, "previous_month": previous_month,
        "total_revenue": df.revenue.sum(), "latest_revenue": latest.revenue,
        "latest_orders": latest.orders, "latest_customers": latest.customers,
        "latest_aov": latest.revenue / latest.orders, "mom_growth": growth,
    }


def answer_question(question, result):
    q = question.lower().strip()
    m = result["monthly"]
    latest = m.iloc[-1]
    prev = m.iloc[-2]
    growth = result["mom_growth"]
    if any(k in q for k in ["why did revenue drop", "why revenue drop", "why did revenue decline", "why revenue decline"]):
        issues = result["issues"]
        top = issues.head(3)
        lines = [f"Revenue changed {growth:.1f}% MoM in {latest.month:%b %Y}."]
        for _, r in top.iterrows():
            lines.append(f"• {r.region} × {r.channel}: {r.change_pct:.1f}% revenue change; orders changed {r.orders_change_pct:.1f}%.")
        if result["anomalies"].empty:
            lines.append("No statistical segment anomaly crossed the detection threshold in the latest period.")
        else:
            a = result["anomalies"].iloc[0]
            lines.append(f"• The strongest anomaly signal is {a.region} × {a.channel} in {a.month:%b %Y} ({a.z_score:.1f}σ).")
        lines.append("Agent recommendation: validate traffic/conversion, order volume, pricing/mix and source-level performance before changing strategy.")
        return "\n".join(lines)
    if "anomal" in q:
        if result["anomalies"].empty:
            return "No anomalies crossed the 2σ threshold in the current demo dataset."
        return "\n".join([f"• {r.region} × {r.channel} — {r.month:%b %Y}: {r.z_score:.1f}σ ({r.severity})" for _, r in result["anomalies"].head(5).iterrows()])
    if "recommend" in q or "action" in q or "what should" in q:
        return "\n".join([f"• {x['priority']}: {x['issue']} → {x['action']}" for x in result["recommendations"]])
    if "growth" in q or "trend" in q or "revenue" in q:
        return f"Latest revenue is ₹{latest.revenue:,.0f}, versus ₹{prev.revenue:,.0f} previously ({growth:.1f}% MoM). Latest AOV is ₹{latest.aov:,.0f}."
    return "Try: ‘Why did revenue drop?’, ‘Show anomalies’, ‘What should we do?’, or ‘What is the revenue trend?’"
