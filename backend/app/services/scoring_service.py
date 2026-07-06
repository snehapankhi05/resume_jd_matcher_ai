from difflib import SequenceMatcher


def calculate_skill_score(matched_skills, jd_skills):
    """
    Percentage of JD skills found in Resume.
    """

    if not jd_skills:
        return 0

    return round((len(matched_skills) / len(jd_skills)) * 100, 2)


def calculate_semantic_similarity(resume_text, jd_text):
    """
    Simple semantic similarity.
    Later we'll replace this with embedding similarity.
    """

    return round(
        SequenceMatcher(
            None,
            resume_text.lower(),
            jd_text.lower()
        ).ratio() * 100,
        2
    )


def calculate_overall_score(skill_score, semantic_score):
    """
    Weighted Score
    """

    return round(
        (skill_score * 0.7) +
        (semantic_score * 0.3),
        2
    )


def calculate_scores(
    matched_skills,
    jd_skills,
    resume_text,
    jd_text
):

    skill_score = calculate_skill_score(
        matched_skills,
        jd_skills
    )

    semantic_score = calculate_semantic_similarity(
        resume_text,
        jd_text
    )

    overall_score = calculate_overall_score(
        skill_score,
        semantic_score
    )

    return {
        "overall_score": overall_score,
        "technical_score": skill_score,
        "semantic_similarity": semantic_score
    }