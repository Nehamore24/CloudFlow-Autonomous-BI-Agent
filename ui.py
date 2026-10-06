import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from app.agent import answer_question


def money(x):
    return f"₹{x/100000:.2f}L"


def chart_theme(fig):
    fig.update_layout(template="plotly_white", height=390, margin=dict(l=10, r=10, t=55, b=10), font=dict(family="Inter, Arial"), hovermode="x unified")
    return fig


def render_dashboard(page, df, r):
    if page == "Executive Overview":
        st.markdown("## Executive command center")
        st.caption(f"Automated monitoring for {r['latest_month']:%B %Y} • CloudFlow SaaS")
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Latest revenue", money(r["latest_revenue"]), f"{r['mom_growth']:.1f}% MoM")
        c2.metric("Orders", f"{int(r['latest_orders']):,}")
        c3.metric("Customers", f"{int(r['latest_customers']):,}")
        c4.metric("Avg. order value", money(r["latest_aov"]))
        c5.metric("Active alerts", f"{len(r['anomalies'])}", "2σ+ anomalies")

        st.markdown("### AI business brief")
        with st.container(border=True):
            for insight in r["insights"]:
                st.markdown(f"**•** {insight}")

        left, right = st.columns([1.6, 1])
        with left:
            fig = px.line(r["monthly"], x="month", y="revenue", markers=True, title="Revenue trajectory")
            chart_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            latest_seg = df[df.month == r["latest_month"]].groupby("region", as_index=False).revenue.sum().sort_values("revenue", ascending=False)
            fig = px.bar(latest_seg, x="region", y="revenue", title="Latest revenue by region")
            chart_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Segment performance matrix")
        heat = df.groupby(["region", "channel"], as_index=False).revenue.sum()
        pivot = heat.pivot(index="region", columns="channel", values="revenue")
        fig = px.imshow(pivot, text_auto=".2s", aspect="auto", title="Revenue by region × channel")
        chart_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    elif page == "AI Analyst":
        st.markdown("## Ask the CloudFlow analyst")
        st.caption("Natural-language business questions are answered from the current analysis state.")
        examples = ["Why did revenue drop?", "Show anomalies", "What should we do?", "What is the revenue trend?"]
        q = st.text_input("Ask a business question", placeholder="Why did revenue drop?", key="question")
        cols = st.columns(4)
        for i, ex in enumerate(examples):
            if cols[i].button(ex, use_container_width=True):
                q = ex
        if q:
            with st.container(border=True):
                st.markdown("**Agent response**")
                st.write(answer_question(q, r))

        st.markdown("### Agent reasoning trace")
        steps = [
            ("1", "Profile", "Scanned revenue, orders, customers and AOV."),
            ("2", "Compare", "Compared latest period with the prior period across segments."),
            ("3", "Detect", "Applied statistical anomaly detection using segment-level z-scores."),
            ("4", "Prioritize", "Ranked issues as Critical, High or Normal."),
            ("5", "Recommend", "Generated targeted investigation actions."),
        ]
        for n, title, desc in steps:
            st.markdown(f"**{n}. {title}** — {desc}")

    elif page == "Agent Control Room":
        st.markdown("## Agent control room")
        issues = r["issues"]
        critical = issues[issues.priority == "Critical"]
        high = issues[issues.priority == "High"]
        c1,c2,c3 = st.columns(3)
        c1.metric("Critical", len(critical))
        c2.metric("High", len(high))
        c3.metric("Anomalies", len(r["anomalies"]))

        st.markdown("### Priority queue")
        display = issues.copy()
        display["segment"] = display.region + " × " + display.channel
        st.dataframe(display[["priority","segment","change_pct","orders_change_pct","revenue_latest"]].round(1), use_container_width=True, hide_index=True)

        st.markdown("### Automated recommendations")
        for rec in r["recommendations"]:
            if rec["priority"] == "Critical": st.error(f"**{rec['priority']}** — {rec['issue']}\n\n{rec['action']}")
            elif rec["priority"] == "High": st.warning(f"**{rec['priority']}** — {rec['issue']}\n\n{rec['action']}")
            else: st.info(f"**{rec['priority']}** — {rec['issue']}\n\n{rec['action']}")

        st.markdown("### Anomaly monitor")
        if r["anomalies"].empty:
            st.success("No anomalies above the 2σ threshold.")
        else:
            a = r["anomalies"].copy()
            a["segment"] = a.region + " × " + a.channel
            st.dataframe(a[["month","segment","revenue","z_score","severity"]].round(2), use_container_width=True, hide_index=True)

    else:
        st.markdown("## Data explorer")
        c1,c2,c3 = st.columns(3)
        with c1: regions = st.multiselect("Region", sorted(df.region.unique()), default=sorted(df.region.unique()))
        with c2: channels = st.multiselect("Channel", sorted(df.channel.unique()), default=sorted(df.channel.unique()))
        with c3: min_revenue = st.number_input("Minimum revenue", min_value=0, value=0, step=10000)
        filtered = df[df.region.isin(regions) & df.channel.isin(channels) & (df.revenue >= min_revenue)]
        st.metric("Rows in view", f"{len(filtered):,}")
        st.dataframe(filtered, use_container_width=True, hide_index=True)
