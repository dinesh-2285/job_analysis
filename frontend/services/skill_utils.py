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


def extract_skills(text: str) -> list[str]:
    lowered = text.lower()
    found = [
        skill
        for skill in DEFAULT_SKILLS
        if re.search(rf"\\b{re.escape(skill.lower())}\\b", lowered)
    ]
    return sorted(set(found))
