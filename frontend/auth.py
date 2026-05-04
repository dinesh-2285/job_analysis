import os
import secrets

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


def get_authenticator() -> stauth.Authenticate:
    with open("frontend/auth.yaml", "r", encoding="utf-8") as file:
        config = yaml.load(file, Loader=SafeLoader)
    cookie_name = os.getenv("AUTH_COOKIE_NAME", config["cookie"]["name"])
    environment = os.getenv("ENVIRONMENT", "dev")
    cookie_key = os.getenv("AUTH_COOKIE_KEY")
    if not cookie_key:
        if environment == "dev":
            cookie_key = secrets.token_urlsafe(32)
            st.sidebar.error("AUTH_COOKIE_KEY not set. Generated a temporary key for this session.")
        else:
            st.error("AUTH_COOKIE_KEY must be set for production/staging environments.")
            st.stop()
    return stauth.Authenticate(
        config["credentials"],
        cookie_name,
        cookie_key,
        config["cookie"]["expiry_days"],
    )


def require_auth() -> tuple[str | None, bool]:
    authenticator = get_authenticator()
    name, authentication_status, _ = authenticator.login("Login", "sidebar")
    if authentication_status:
        authenticator.logout("Logout", "sidebar")
        st.session_state["user_name"] = name
    return name, bool(authentication_status)
