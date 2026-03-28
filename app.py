from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Mission Assurance Dashboard", layout="wide")

DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load_csv(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    return pd.read_csv(path)

requirements = load_csv("requirements.csv")
tests = load_csv("tests.csv")
anomalies = load_csv("anomalies.csv")
risks = load_csv("risks.csv")
subsystems = load_csv("subsystems.csv")
decision_log = load_csv("decision_log.csv")

def compute_readiness() -> tuple[str, list[str]]:
    reasons = []

    critical_blockers = anomalies[
        (anomalies["severity"].str.lower() == "critical") &
        (anomalies["status"].str.lower() != "closed") &
        (anomalies["blocks_readiness"].str.lower() == "yes")
    ]

    red_critical_subsystems = subsystems[
        (subsystems["mission_critical"].astype(str).str.lower() == "yes") &
        (subsystems["status"].str.lower() == "red")
    ]

    verified_count = requirements["status"].str.lower().isin(["pass", "verified"]).sum()
    verified_pct = (verified_count / len(requirements)) * 100 if len(requirements) else 0.0

    if not critical_blockers.empty:
        reasons.append("Open critical anomaly blocks readiness.")
    if not red_critical_subsystems.empty:
        reasons.append("At least one mission-critical subsystem is red.")
    if verified_pct < 85:
        reasons.append(f"Requirements verified below threshold ({verified_pct:.1f}%).")

    if reasons:
        return "No-Go", reasons

    if verified_pct < 95:
        return "Conditional Go", [f"Requirements verified at {verified_pct:.1f}%."]
    
    return "Go", [f"Requirements verified at {verified_pct:.1f}% and no critical blockers detected."]

readiness, reasons = compute_readiness()

verified_count = requirements["status"].str.lower().isin(["pass", "verified"]).sum()
verified_pct = (verified_count / len(requirements)) * 100 if len(requirements) else 0.0
open_anomalies = anomalies[anomalies["status"].str.lower() != "closed"]
critical_open = open_anomalies[open_anomalies["severity"].str.lower() == "critical"]
passed_tests = tests["result"].str.lower().eq("pass").sum()
test_pass_rate = (passed_tests / len(tests)) * 100 if len(tests) else 0.0

st.title("Mission Assurance Dashboard")
st.caption("Human-gated readiness support for a mission-critical system")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Readiness", readiness)
col2.metric("Requirements Verified", f"{verified_pct:.1f}%")
col3.metric("Open Anomalies", int(len(open_anomalies)))
col4.metric("Test Pass Rate", f"{test_pass_rate:.1f}%")

st.subheader("Why this recommendation?")
for reason in reasons:
    st.write(f"- {reason}")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Requirements",
    "Tests",
    "Anomalies & Risks",
    "Decision Log"
])

with tab1:
    st.write("### Subsystem Status")
    st.dataframe(subsystems, use_container_width=True)

with tab2:
    st.write("### Requirements Traceability")
    st.dataframe(requirements, use_container_width=True)

with tab3:
    st.write("### Test Status")
    st.dataframe(tests, use_container_width=True)

with tab4:
    st.write("### Open Anomalies")
    st.dataframe(anomalies, use_container_width=True)
    st.write("### Risk Register")
    st.dataframe(risks, use_container_width=True)

with tab5:
    st.write("### Latest Decision Record")
    st.dataframe(decision_log, use_container_width=True)
