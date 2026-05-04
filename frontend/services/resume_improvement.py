import os
import requests


def generate_suggestions(resume_text: str, missing_skills: list[str]) -> list[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return call_openai(resume_text, missing_skills, api_key)
    suggestions = []
    if missing_skills:
        suggestions.append(
            f"Consider adding these missing skills to your resume: {', '.join(missing_skills[:8])}."
        )
    suggestions.append("Highlight measurable achievements using metrics (e.g., % improvements).")
    suggestions.append("Tailor your summary to align with the target job stream.")
    return suggestions


def call_openai(resume_text: str, missing_skills: list[str], api_key: str) -> list[str]:
    payload = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": [
            {
                "role": "system",
                "content": "You are a resume coach providing concise improvement suggestions.",
            },
            {
                "role": "user",
                "content": (
                    "Review this resume and suggest 3 improvements. "
                    f"Missing skills to consider: {', '.join(missing_skills)}. "
                    f"Resume: {resume_text[:2000]}"
                ),
            },
        ],
        "max_tokens": 300,
    }
    response = requests.post(
        os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1") + "/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return [line.strip("- ").strip() for line in content.split("\n") if line.strip()]
