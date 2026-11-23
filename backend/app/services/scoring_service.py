import numpy as np
from langsmith import traceable
from sklearn.metrics.pairwise import cosine_similarity

from backend.app.core.config import settings
from backend.app.rag.embeddings import get_embedding_model


def calculate_skill_score(matched_skills, jd_skills, related_skills=None):
    """
    Technical score (0-100).

    Every matched JD skill counts fully. A missing JD skill that the
    candidate has a *related* skill for (see skills_extended groups) earns
    partial credit, e.g. 0.5 for Streamlit -> FastAPI. A candidate who is
    adjacent to a role is therefore no longer scored the same as one who is
    unrelated. The total can never exceed 100.
    """
    if not jd_skills:
        return 0

    credit = sum(item["credit"] for item in (related_skills or []))

    score = (len(matched_skills) + credit) / len(jd_skills) * 100

    return round(min(score, 100.0), 2)


def calculate_semantic_similarity(resume_text, jd_text):
    """
    Semantic similarity between resume and job description (0-100).

    Both arguments may be a string or a list of chunks. Embedding one
    huge string is wrong: embedding models truncate long input, so only
    the first few hundred tokens would be compared. Instead every JD chunk
    is matched with its most similar resume chunk and the results are
    averaged ("how well is each JD requirement covered by the resume").
    """

    resume_chunks = [resume_text] if isinstance(resume_text, str) else resume_text
    jd_chunks = [jd_text] if isinstance(jd_text, str) else jd_text

    resume_chunks = [chunk for chunk in resume_chunks if chunk.strip()]
    jd_chunks = [chunk for chunk in jd_chunks if chunk.strip()]

    if not resume_chunks or not jd_chunks:
        return 0

    embedding_model = get_embedding_model()

    resume_embeddings = np.array(
        embedding_model.embed_documents(resume_chunks)
    )

    jd_embeddings = np.array(
        embedding_model.embed_documents(jd_chunks)
    )

    similarity_matrix = cosine_similarity(
        jd_embeddings,
        resume_embeddings
    )

    similarity = float(similarity_matrix.max(axis=1).mean())

    # Cosine similarity can be negative; keep the score within 0-100.
    similarity = min(max(similarity, 0.0), 1.0)

    return round(similarity * 100, 2)


def calculate_overall_score(skill_score, semantic_score, has_jd_skills=True):

    # If no known skill was found in the JD, a technical score of 0 says
    # nothing about the candidate, so rely on semantic similarity only.
    if not has_jd_skills:
        return round(semantic_score, 2)

    skill_weight = settings.SKILL_SCORE_WEIGHT

    return round(
        (skill_score * skill_weight) +
        (semantic_score * (1 - skill_weight)),
        2
    )


@traceable(name="calculate_scores", run_type="tool")
def calculate_scores(
    matched_skills,
    jd_skills,
    resume_text,
    jd_text,
    related_skills=None
):

    skill_score = calculate_skill_score(
        matched_skills,
        jd_skills,
        related_skills
    )

    semantic_score = calculate_semantic_similarity(
        resume_text,
        jd_text
    )

    overall_score = calculate_overall_score(
        skill_score,
        semantic_score,
        has_jd_skills=bool(jd_skills)
    )

    return {
        "overall_score": overall_score,
        "technical_score": skill_score,
        "semantic_similarity": semantic_score
    }
