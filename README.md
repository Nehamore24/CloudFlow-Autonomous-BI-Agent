# CloudFlow Autonomous BI Agent

A professional Streamlit decision-support platform for a fictional B2B SaaS company. It automatically profiles business data, monitors revenue performance, detects statistical anomalies, prioritizes issues, answers natural-language business questions, and generates management-ready recommendations.

## What is new
- Professional SaaS-style control-room UI
- Executive KPI cards with MoM movement and alert counts
- Natural-language analyst: “Why did revenue drop?” / “Show anomalies” / “What should we do?”
- Statistical anomaly detection using segment-level z-scores
- Priority queue with Critical / High / Normal signals
- Automated business recommendations
- Revenue trend, regional performance and region × channel heatmap
- Agent reasoning trace showing Profile → Compare → Detect → Prioritize → Recommend
- GitHub-ready structure and Streamlit deployment instructions
- Runs without paid APIs or secrets

## Architecture
Data → KPI Engine → Comparative Analysis → Anomaly Detection → Priority Queue → Natural-Language Analyst → Recommendations → Dashboard

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Push this folder to a GitHub repository.
2. Open Streamlit Community Cloud.
3. Select the repository and `app.py` as the entry point.
4. Deploy.

No API key is required for the current demo analyst because its answers are generated from the live analysis state. If an LLM is added later, keep credentials in Streamlit Secrets and never commit them.

## Project positioning
This is best presented as an **AI-assisted autonomous BI decision-support agent**, not a system that autonomously executes commercial actions. The agent detects and explains issues and recommends what a business user should investigate next.
