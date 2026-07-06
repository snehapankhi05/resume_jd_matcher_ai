from backend.app.services.context_service import get_context
from backend.app.services.skill_service import extract_and_match_skills
from backend.app.services.scoring_service import calculate_scores
from backend.app.services.llm_service import generate_analysis


def analyze_documents(session_id: str):
    """
    Complete Resume-JD Analysis Pipeline
    """

    # Query used for retrieval
    query = "skills experience education projects technologies"

    # Step 1: Retrieve relevant context
    context = get_context(
        session_id=session_id,
        query=query
    )

    resume_context = context["resume_context"]
    jd_context = context["jd_context"]

    # Step 2: Extract & Match Skills
    skills = extract_and_match_skills(
        resume_context,
        jd_context
    )

    # Step 3: Calculate Scores
    scores = calculate_scores(
        matched_skills=skills["matched_skills"],
        jd_skills=skills["jd_skills"],
        resume_text=resume_context,
        jd_text=jd_context
    )

    # Step 4: LLM Analysis
    llm_response = generate_analysis(
        resume_context=resume_context,
        jd_context=jd_context,
        scores=scores,
        matched_skills=skills["matched_skills"],
        missing_skills=skills["missing_skills"]
    )

    # Step 5: Merge Results
    return {
        **scores,
        **skills,
        **llm_response
    }