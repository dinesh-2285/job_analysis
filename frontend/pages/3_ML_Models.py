import streamlit as st

from frontend.auth import require_auth
from frontend.services.api_client import post


st.set_page_config(page_title="ML Models", page_icon="🤖", layout="wide")
_, authenticated = require_auth()
if not authenticated:
    st.stop()

st.title("🤖 ML Models")

if st.button("Train All Models"):
    result = post("/ml/train")
    st.success("Training completed.")
    st.json(result)

st.subheader("Predict Job Stream")
description = st.text_area("Paste a job description")
if st.button("Predict Stream"):
    response = post("/ml/predict-stream", {"description": description})
    st.write(response)

st.subheader("Salary Estimate")
stream = st.text_input("Stream")
location = st.text_input("Location")
if st.button("Estimate Salary"):
    response = post("/ml/salary-estimate", {"stream": stream, "location": location})
    st.write(response)
