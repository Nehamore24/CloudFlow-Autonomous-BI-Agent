from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

@st.cache_data
def load_demo_data(seed=42):
    rng = np.random.default_rng(seed)
    months = pd.date_range("2026-01-01", "2026-09-01", freq="MS")
    regions = ["North", "South", "East", "West"]
    channels = ["Direct Sales", "Partner", "Online", "Referral"]

    rows = []
    for m in months:
        for region in regions:
            for channel in channels:
                base = {"Direct Sales": 260000, "Partner": 190000, "Online": 145000, "Referral": 110000}[channel]
                seasonal = 1 + 0.06*np.sin(m.month/9*np.pi)
                region_factor = {"North":1.08,"South":1.02,"East":0.91,"West":1.04}[region]
                revenue = base * seasonal * region_factor * rng.normal(1, .055)
                orders = int(max(30, revenue / rng.uniform(3200, 5200)))
                customers = int(max(15, orders * rng.uniform(.68, .92)))
                rows.append([m, region, channel, revenue, orders, customers])
    df = pd.DataFrame(rows, columns=["month","region","channel","revenue","orders","customers"])

    # Add a realistic anomaly so the agent has something useful to detect.
    mask = (df["month"] == pd.Timestamp("2026-08-01")) & (df["region"] == "East") & (df["channel"] == "Online")
    df.loc[mask, "revenue"] *= .70
    df.loc[mask, "orders"] = (df.loc[mask, "orders"] * .78).astype(int)

    df["avg_order_value"] = df["revenue"] / df["orders"]
    return df
