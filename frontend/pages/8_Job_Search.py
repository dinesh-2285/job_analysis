import streamlit as st

from frontend.auth import require_auth
from frontend.services.api_client import get


st.set_page_config(page_title="Job Search", page_icon="🔎", layout="wide")
_, authenticated = require_auth()
if not authenticated:
    st.stop()

st.title("🔎 Job Search")

col1, col2, col3 = st.columns(3)
with col1:
    stream = st.text_input("Stream")
with col2:
    location = st.text_input("Location")
with col3:
    search = st.text_input("Search")

page = st.number_input("Page", min_value=1, value=1)
limit = 20
offset = (page - 1) * limit

result = get(
    "/jobs",
    params={
        "stream": stream or None,
        "location": location or None,
        "search": search or None,
        "limit": limit,
        "offset": offset,
    },
)
jobs = result.get("jobs", [])
st.caption(f"Total jobs: {result.get('total', 0)}")

username = st.session_state.get("user_name", "anonymous")
for job in jobs:
    with st.expander(f"{job['title']} @ {job['company']}"):
        st.write(job.get("location"))
        st.write(job.get("description", "")[:400])
        if st.button("Bookmark", key=f"bookmark-{job['id']}"):
            from frontend.services.api_client import post

            post("/bookmarks", {"username": username, "job_id": job["id"]})
            st.success("Bookmarked")
