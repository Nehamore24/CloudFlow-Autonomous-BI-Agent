import streamlit as st
from app.agent import run_analysis
from app.data import load_demo_data
from app.ui import render_dashboard

st.set_page_config(page_title="CloudFlow | Autonomous BI", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container {padding: 1.5rem 2.2rem 3rem; max-width: 1500px;}
[data-testid="stMetric"] {border: 1px solid rgba(120,120,140,.18); padding: 14px 16px; border-radius: 14px; background: rgba(255,255,255,.72);}
.hero {padding: 1.35rem 1.55rem; border-radius: 18px; border: 1px solid rgba(99,102,241,.18); background: linear-gradient(135deg, rgba(99,102,241,.12), rgba(16,185,129,.08)); margin-bottom: 1.2rem;}
.badge {display:inline-block;padding:5px 9px;border-radius:999px;background:#eef2ff;font-size:.78rem;font-weight:600;margin-right:6px;}
.small {color:#64748b;font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("# ◈ CloudFlow")
st.sidebar.caption("Autonomous Business Intelligence Platform")
st.sidebar.divider()
page = st.sidebar.radio("Workspace", ["Executive Overview", "AI Analyst", "Agent Control Room", "Data Explorer"])
st.sidebar.divider()
st.sidebar.markdown("**Agent status**")
st.sidebar.success("● Monitoring")
st.sidebar.caption("Synthetic demo data • No paid API required")

st.markdown("""
<div class="hero">
<div><span class="badge">AI-ASSISTED BI</span><span class="badge">ANOMALY MONITORING</span><span class="badge">DECISION SUPPORT</span></div>
<h1>CloudFlow Autonomous BI Agent</h1>
<p class="small">A SaaS intelligence workspace that profiles business data, detects anomalies, explains performance changes, prioritizes issues, and recommends the next investigation.</p>
</div>
""", unsafe_allow_html=True)

data = load_demo_data()
result = run_analysis(data)
render_dashboard(page, data, result)

st.divider()
st.caption("CloudFlow BI Agent • Analytical decision support only — recommendations do not execute business actions automatically.")
