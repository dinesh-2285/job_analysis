import re

DEFAULT_SKILLS = {
    "python",
    "sql",
    "javascript",
    "java",
    "c++",
    "c#",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "react",
    "node.js",
    "tensorflow",
    "pytorch",
    "spark",
    "airflow",
    "tableau",
    "power bi",
    "excel",
}


def extract_skills(text: str, skills: set[str] | None = None) -> list[str]:
    if not text:
        return []
    candidates = skills or DEFAULT_SKILLS
    found = set()
    lowered = text.lower()
    for skill in candidates:
        if re.search(rf"\b{re.escape(skill.lower())}\b", lowered):
            found.add(skill)
    return sorted(found)
