import os

import requests


def api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://localhost:8000")


def get(path: str, params: dict | None = None) -> dict:
    response = requests.get(f"{api_base_url()}{path}", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def post(path: str, payload: dict | None = None) -> dict:
    response = requests.post(f"{api_base_url()}{path}", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()
