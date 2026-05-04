import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.auth import require_auth
from frontend.services.api_client import get


st.set_page_config(page_title="Analytics Dashboard", page_icon="📊", layout="wide")
name, authenticated = require_auth()
if not authenticated:
    st.stop()

st.title("📊 Analytics Dashboard")

job_data = get("/jobs", params={"limit": 1})
st.metric("Total Jobs", job_data.get("total", 0))

trend_data = get("/skills/trends")
job_counts = trend_data.get("job_counts", {})

if job_counts:
    df = pd.DataFrame({"month": list(job_counts.keys()), "count": list(job_counts.values())})
    fig = px.line(df, x="month", y="count", title="Job Postings Over Time")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No temporal data available yet.")
