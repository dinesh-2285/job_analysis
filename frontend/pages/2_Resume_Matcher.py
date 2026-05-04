import streamlit as st

from frontend.auth import require_auth
from frontend.services.api_client import get, post
from frontend.services.resume_improvement import generate_suggestions
from frontend.services.resume_parser import detect_experience_level, extract_text
from frontend.services.reporting import build_match_report
from frontend.services.skill_utils import extract_skills


st.set_page_config(page_title="Resume Matcher", page_icon="🎯", layout="wide")
_, authenticated = require_auth()
if not authenticated:
    st.stop()

st.title("🎯 Resume Matcher")
uploaded = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt", "md"])

if uploaded:
    resume_text = extract_text(uploaded.name, uploaded.read())
    experience_level = detect_experience_level(resume_text)
    st.info(f"Detected experience level: {experience_level}")

    if st.button("Find Matches"):
        matches = post("/resume/match", {"resume_text": resume_text, "top_k": 5})
        match_rows = matches.get("matches", [])
        if not match_rows:
            st.warning("No matches found yet. Run the data pipeline first.")
        else:
            st.subheader("Top Matches")
            st.dataframe(match_rows)

            job_skills = []
            for match in match_rows:
                job = get(f"/jobs/{match['job_id']}")
                if job.get("skills"):
                    job_skills.extend([skill.strip().lower() for skill in job["skills"].split(",")])
            resume_skills = set(extract_skills(resume_text))
            missing_skills = sorted(set(job_skills) - resume_skills)[:10]
            suggestions = generate_suggestions(resume_text, missing_skills)

            st.subheader("Skill Gaps")
            st.write(missing_skills or "No major gaps detected.")

            st.subheader("Resume Improvement Suggestions")
            for suggestion in suggestions:
                st.write(f"- {suggestion}")

            report_bytes = build_match_report(
                candidate_name=uploaded.name,
                experience_level=experience_level,
                matched_skills=sorted(resume_skills),
                missing_skills=missing_skills,
                recommendations=suggestions,
            )
            st.download_button(
                "Download Match Report (PDF)",
                data=report_bytes,
                file_name="resume_match_report.pdf",
                mime="application/pdf",
            )

            if st.button("Save Match History"):
                username = st.session_state.get("user_name", "anonymous")
                for match in match_rows:
                    post(
                        "/resume/history",
                        {
                            "username": username,
                            "resume_name": uploaded.name,
                            "matched_job_id": match["job_id"],
                            "match_score": match["score"],
                        },
                    )
                st.success("Match history saved.")

st.markdown("---")
st.subheader("Match History")
username = st.session_state.get("user_name")
if username:
    history = get("/resume/history", params={"username": username}).get("history", [])
    if history:
        st.dataframe(history)
    else:
        st.info("No history saved yet.")
