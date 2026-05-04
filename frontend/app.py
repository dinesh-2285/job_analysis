import streamlit as st

from frontend.auth import require_auth


def apply_theme():
    dark_mode = st.sidebar.toggle("🌙 Dark mode", value=False)
    if dark_mode:
        st.markdown(
            """
            <style>
            body, .stApp { background-color: #0e1117; color: #fafafa; }
            .stMetric { background-color: #1e1e1e; }
            </style>
            """,
            unsafe_allow_html=True,
        )


def main():
    st.set_page_config(
        page_title="Job Analytics Platform",
        page_icon="🚀",
        layout="wide",
    )
    st.sidebar.title("🚀 Job Analytics Platform")
    apply_theme()

    name, authenticated = require_auth()
    if not authenticated:
        st.warning("Please log in to access the platform.")
        st.stop()

    st.title("Welcome to the Upscaled Job Analytics Platform")
    st.markdown(
        """
        Use the navigation menu to explore analytics, resume matching, ML models,
        and real-time job search.
        """
    )
    try:
        from frontend.services.api_client import get

        status = get("/health")
        st.success(f"API Status: {status.get('status', 'unknown')}")
    except Exception:
        st.warning("API Status: unavailable")
    if name:
        st.success(f"Logged in as {name}")


if __name__ == "__main__":
    main()
