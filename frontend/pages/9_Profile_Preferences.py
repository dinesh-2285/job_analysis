import streamlit as st

from frontend.auth import require_auth
from frontend.services.api_client import get, post


st.set_page_config(page_title="Profile & Preferences", page_icon="👤", layout="wide")
_, authenticated = require_auth()
if not authenticated:
    st.stop()

st.title("👤 Profile & Preferences")
username = st.session_state.get("user_name", "anonymous")

prefs = get("/preferences", params={"username": username})
target_stream = st.text_input("Target Stream", value=prefs.get("target_stream") or "")
target_salary = st.text_input("Target Salary", value=prefs.get("target_salary") or "")
location = st.text_input("Preferred Location", value=prefs.get("location") or "")
email_digest = st.checkbox("Receive weekly email digest", value=prefs.get("email_digest", False))

if st.button("Save Preferences"):
    post(
        "/preferences",
        {
            "username": username,
            "target_stream": target_stream,
            "target_salary": target_salary,
            "location": location,
            "email_digest": email_digest,
        },
    )
    st.success("Preferences saved.")

st.subheader("Bookmarks")
bookmarks = get("/bookmarks", params={"username": username}).get("bookmarks", [])
if bookmarks:
    st.write(bookmarks)
else:
    st.info("No bookmarks yet.")
