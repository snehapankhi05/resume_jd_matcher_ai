import json

from langchain_core.messages import HumanMessage, SystemMessage
from sympy import content

from backend.app.prompts.analysis_prompt import (
    SYSTEM_PROMPT,
    USER_PROMPT,
)

from backend.app.rag.llm import get_llm


def generate_analysis(
    resume_context: str,
    jd_context: str,
    scores: dict,
    matched_skills: list,
    missing_skills: list,
):

    llm = get_llm()

    prompt = USER_PROMPT.format(
        resume_context=resume_context,
        jd_context=jd_context,
        overall_score=scores["overall_score"],
        technical_score=scores["technical_score"],
        experience_score=scores.get("experience_score", 0),
        education_score=scores.get("education_score", 0),
        semantic_similarity=scores["semantic_similarity"],
        matched_skills=", ".join(matched_skills),
        missing_skills=", ".join(missing_skills),
    )

    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    content = response.content.strip()

    if content.startswith("```json"):
        content = content.replace("```json", "").replace("```", "").strip()

    elif content.startswith("```"):
        content = content.replace("```", "").strip()
    
    try:
        result = json.loads(content)

        

        return result

    except Exception as e:

        
        raise Exception(f"Invalid JSON returned by Groq: {e}")