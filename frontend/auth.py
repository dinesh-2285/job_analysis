import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


def get_authenticator() -> stauth.Authenticate:
    with open("frontend/auth.yaml", "r", encoding="utf-8") as file:
        config = yaml.load(file, Loader=SafeLoader)
    return stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )


def require_auth() -> tuple[str | None, bool]:
    authenticator = get_authenticator()
    name, authentication_status, _ = authenticator.login("Login", "sidebar")
    if authentication_status:
        authenticator.logout("Logout", "sidebar")
        st.session_state["user_name"] = name
    return name, bool(authentication_status)
