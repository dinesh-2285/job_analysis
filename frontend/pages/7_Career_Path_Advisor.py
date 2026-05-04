import streamlit as st

from frontend.auth import require_auth


st.set_page_config(page_title="Career Path Advisor", page_icon="🧭", layout="wide")
_, authenticated = require_auth()
if not authenticated:
    st.stop()

st.title("🧭 Career Path Advisor")

career_map = {
    "Data Analyst": {"next_roles": ["Data Scientist", "Analytics Engineer"], "skills": ["python", "sql", "ml"]},
    "Software Engineer": {"next_roles": ["Senior Engineer", "Tech Lead"], "skills": ["system design", "cloud"]},
    "DevOps Engineer": {"next_roles": ["Platform Engineer", "SRE"], "skills": ["kubernetes", "terraform"]},
}

role = st.selectbox("Current Role", list(career_map.keys()))
if role:
    st.subheader("Next Roles")
    st.write(", ".join(career_map[role]["next_roles"]))
    st.subheader("Skills to Build")
    st.write(", ".join(career_map[role]["skills"]))
