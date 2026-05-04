import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.auth import require_auth
from frontend.services.api_client import get


st.set_page_config(page_title="Skill Trends", page_icon="📈", layout="wide")
_, authenticated = require_auth()
if not authenticated:
    st.stop()

st.title("📈 Skill Trends")

data = get("/skills/trends")
trends = data.get("trends", {})
if not trends:
    st.info("No skill trend data available yet.")
else:
    rows = []
    for month, skills in trends.items():
        for skill, count in skills:
            rows.append({"month": month, "skill": skill, "count": count})
    df = pd.DataFrame(rows)
    fig = px.line(df, x="month", y="count", color="skill", title="Top Skills Over Time")
    st.plotly_chart(fig, use_container_width=True)
