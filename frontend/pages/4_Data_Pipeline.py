import streamlit as st

from frontend.auth import require_auth
from frontend.services.api_client import post


st.set_page_config(page_title="Data Pipeline", page_icon="⚙️", layout="wide")
_, authenticated = require_auth()
if not authenticated:
    st.stop()

st.title("⚙️ Data Pipeline")
st.write("Run the real-data ingestion pipeline.")

if st.button("Run Pipeline"):
    result = post("/pipeline/run")
    st.success("Pipeline finished.")
    st.json(result)
