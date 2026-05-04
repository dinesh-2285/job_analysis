import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.auth import require_auth
from frontend.services.api_client import get


st.set_page_config(page_title="Salary Insights", page_icon="💰", layout="wide")
_, authenticated = require_auth()
if not authenticated:
    st.stop()

st.title("💰 Salary Insights")

jobs = get("/jobs", params={"limit": 200}).get("jobs", [])
df = pd.DataFrame(jobs)
if df.empty or df["salary_min"].isna().all():
    st.info("No salary data available yet.")
else:
    df["salary_mid"] = (df["salary_min"] + df["salary_max"]) / 2
    fig = px.box(df, x="stream", y="salary_mid", title="Salary Distribution by Stream")
    st.plotly_chart(fig, use_container_width=True)
