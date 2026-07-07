from backend.app.services.context_service import get_context
from backend.app.services.skill_service import extract_and_match_skills
from backend.app.services.scoring_service import calculate_scores
from backend.app.services.llm_service import generate_analysis


def analyze_documents(session_id: str):

    query = "skills experience education projects technologies"

    context = get_context(
        session_id=session_id,
        query=query
    )

    resume_context = context["resume_context"]
    jd_context = context["jd_context"]

    skills = extract_and_match_skills(
        resume_context,
        jd_context
    )

    scores = calculate_scores(
        matched_skills=skills["matched_skills"],
        jd_skills=skills["jd_skills"],
        resume_text=resume_context,
        jd_text=jd_context
    )

    llm_response = generate_analysis(
        resume_context=resume_context,
        jd_context=jd_context,
        scores=scores,
        matched_skills=skills["matched_skills"],
        missing_skills=skills["missing_skills"]
    )

    return {
        **scores,
        **skills,
        **llm_response
    }