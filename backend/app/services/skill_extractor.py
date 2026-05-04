import re

from shared.skills import DEFAULT_SKILLS


def extract_skills(text: str, skills: set[str] | None = None) -> list[str]:
    candidates = skills or DEFAULT_SKILLS
    lowered = text.lower()
    found = [
        skill
        for skill in candidates
        if re.search(rf"\b{re.escape(skill.lower())}\b", lowered)
    ]
    return sorted(set(found))
