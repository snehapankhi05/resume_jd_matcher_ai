import re

from backend.app.core.skills import TECH_SKILLS


def normalize_text(text: str) -> str:
    return text.lower()


def extract_skills(text: str):

    text = normalize_text(text)

    extracted = set()

    for skill in TECH_SKILLS:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text):
            extracted.add(skill.title())

    return sorted(extracted)


def extract_and_match_skills(
    resume_text: str,
    jd_text: str
):

    resume_skills = set(extract_skills(resume_text))

    jd_skills = set(extract_skills(jd_text))

    matched_skills = sorted(
        resume_skills.intersection(jd_skills)
    )

    missing_skills = sorted(
        jd_skills - resume_skills
    )

    return {
        "resume_skills": sorted(resume_skills),
        "jd_skills": sorted(jd_skills),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }