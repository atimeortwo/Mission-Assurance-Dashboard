from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt

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

def prettify_columns(df: pd.DataFrame) -> pd.DataFrame:
    pretty_df = df.copy()
    pretty_df.columns = [
        col.replace("_", " ").title()
        for col in pretty_df.columns
    ]
    return pretty_df

def capitalize_values(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()

    for col in df_copy.columns:
        df_copy[col] = df_copy[col].apply(
            lambda x: x.replace("_", " ").title() if isinstance(x, str) else x
        )

    return df_copy

def requirements_card(verified_pct: float) -> str:
    if verified_pct >= 95:
        bg, fg = "#28a745", "white"
    elif verified_pct >= 85:
        bg, fg = "#ffc107", "black"
    else:
        bg, fg = "#dc3545", "white"

    return f"""
    <div style="
        background-color: {bg};
        color: {fg};
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 24px;
        margin-bottom: 10px;
    ">
        <div style="font-size: 14px; font-weight: 600;">REQUIREMENTS VERIFIED</div>
        <div>{verified_pct:.1f}%</div>
    </div>
    """

def blocker_style(val):
    if pd.isna(val):
        return ""

    value = str(val).strip().lower()

    color_map = {
        "critical": "background-color: #dc3545; color: white; font-weight: bold;",
        "high": "background-color: #fd7e14; color: white; font-weight: bold;",
        "medium": "background-color: #ffc107; color: black; font-weight: bold;",
        "low": "background-color: #17a2b8; color: white; font-weight: bold;",
        "open": "background-color: #fd7e14; color: white; font-weight: bold;",
        "closed": "background-color: #6c757d; color: white; font-weight: bold;",
        "yes": "background-color: #dc3545; color: white; font-weight: bold;",
        "no": "background-color: #28a745; color: white; font-weight: bold;",
    }

    style = color_map.get(value, "")
    if style:
        style += " text-align: center;"
    return style

def status_box_style(val):
    if pd.isna(val):
        return ""

    value = str(val).strip().lower()

    color_map = {
        "green": "background-color: #28a745; color: white; font-weight: bold;",
        "red": "background-color: #dc3545; color: white; font-weight: bold;",
        "yellow": "background-color: #ffc107; color: black; font-weight: bold;",
        "pass": "background-color: #28a745; color: white; font-weight: bold;",
        "fail": "background-color: #dc3545; color: white; font-weight: bold;",
        "open": "background-color: #fd7e14; color: white; font-weight: bold;",
        "closed": "background-color: #28a745; color: white; font-weight: bold;",
        "mitigating": "background-color: #ffc107; color: black; font-weight: bold;"
    }

    base_style = color_map.get(value, "")
    if base_style:
        base_style += " text-align: center; border-radius: 4px;"

    return base_style

def readiness_card(status: str) -> str:
    status_lower = str(status).strip().lower()

    colors = {
        "go": ("#28a745", "white"),
        "conditional go": ("#ffc107", "black"),
        "no-go": ("#dc3545", "white"),
    }

    bg, fg = colors.get(status_lower, ("#6c757d", "white"))

    return f"""
    <div style="
        background-color: {bg};
        color: {fg};
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 24px;
        margin-bottom: 10px;
    ">
        <div style="font-size: 14px; font-weight: 600;">READINESS</div>
        <div>{status}</div>
    </div>
    """


def anomaly_card(open_count: int) -> str:
    if open_count == 0:
        bg, fg = "#28a745", "white"
    elif open_count <= 2:
        bg, fg = "#ffc107", "black"
    else:
        bg, fg = "#dc3545", "white"

    return f"""
    <div style="
        background-color: {bg};
        color: {fg};
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 24px;
        margin-bottom: 10px;
    ">
        <div style="font-size: 14px; font-weight: 600;">OPEN ANOMALIES</div>
        <div>{open_count}</div>
    </div>
    """


def pass_rate_card(pass_rate: float) -> str:
    if pass_rate >= 95:
        bg, fg = "#28a745", "white"
    elif pass_rate >= 80:
        bg, fg = "#ffc107", "black"
    else:
        bg, fg = "#dc3545", "white"

    return f"""
    <div style="
        background-color: {bg};
        color: {fg};
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 24px;
        margin-bottom: 10px;
    ">
        <div style="font-size: 14px; font-weight: 600;">TEST PASS RATE</div>
        <div>{pass_rate:.1f}%</div>
    </div>
    """

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

with col1:
    st.markdown(readiness_card(readiness), unsafe_allow_html=True)

with col2:
    st.markdown(requirements_card(verified_pct), unsafe_allow_html=True)

with col3:
    st.markdown(anomaly_card(int(len(open_anomalies))), unsafe_allow_html=True)

with col4:
    st.markdown(pass_rate_card(test_pass_rate), unsafe_allow_html=True)

st.subheader("Why this recommendation?")
for reason in reasons:
    st.write(f"- {reason}")
    
st.write("### Current Blockers")

critical_blockers = anomalies[
    (anomalies["severity"].str.lower() == "critical") &
    (anomalies["status"].str.lower() != "closed") &
    (anomalies["blocks_readiness"].str.lower() == "yes")
]

if critical_blockers.empty:
    st.markdown("""
    <div style="
        background-color: #28a745;
        color: white;
        padding: 14px;
        border-radius: 10px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    ">
        NO CRITICAL BLOCKERS DETECTED
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="
        background-color: #dc3545;
        color: white;
        padding: 14px;
        border-radius: 10px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    ">
        CRITICAL BLOCKERS PRESENT
    </div>
    """, unsafe_allow_html=True)

    blockers_display = capitalize_values(prettify_columns(critical_blockers))

    blockers_styled = blockers_display.style.map(
        blocker_style,
        subset=["Severity", "Status", "Blocks Readiness"]
    )

    st.dataframe(blockers_styled, use_container_width=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Requirements",
    "Tests",
    "Anomalies & Risks",
    "Decision Log"
])

with tab1:
    st.write("### Subsystem Status")
    subsystems_display = prettify_columns(subsystems)

    subsystems_styled = subsystems_display.style.map(
        status_box_style,
        subset=["Status"]
    )

    st.dataframe(subsystems_styled, use_container_width=True)
    
    st.write("### Subsystem Status Summary")

    status_order = ["Green", "Yellow", "Red"]

    subsystem_status_counts = (
        subsystems["status"]
        .astype(str)
        .str.strip()
        .str.title()
        .value_counts()
        .reindex(status_order, fill_value=0)
    )

    chart_df = pd.DataFrame({
        "Status": status_order,
        "Count": [subsystem_status_counts[s] for s in status_order]
    })

    chart = alt.Chart(chart_df).mark_bar().encode(
        x=alt.X("Status:N", sort=status_order),
        y="Count:Q"
    )

    st.altair_chart(chart, use_container_width=True)

with tab2:
    st.write("### Requirements Traceability")
    requirements_display = prettify_columns(requirements)

    requirements_styled = requirements_display.style.map(
        status_box_style,
        subset=["Status"]
    )

    st.dataframe(requirements_styled, use_container_width=True)

with tab3:
    st.write("### Test Status")
    tests_display = prettify_columns(tests)

    tests_styled = tests_display.style.map(
        status_box_style,
        subset=["Result"]
    )

    st.dataframe(tests_styled, use_container_width=True)

with tab4:
    st.write("### Open Anomalies")
    anomalies_display = prettify_columns(anomalies)

    anomalies_styled = anomalies_display.style.map(
        status_box_style,
        subset=["Status"]
    )

    st.dataframe(anomalies_styled, use_container_width=True)

    st.write("### Risk Register")
    risks_display = prettify_columns(risks)

    risks_styled = risks_display.style.map(
        status_box_style,
        subset=["Status"]
    )

    st.dataframe(risks_styled, use_container_width=True)

with tab5:
    st.write("### Latest Decision Record")
    decision_log_display = prettify_columns(decision_log)
    st.dataframe(decision_log_display, use_container_width=True)
