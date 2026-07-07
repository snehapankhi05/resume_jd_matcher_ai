from sklearn.metrics.pairwise import cosine_similarity

from backend.app.rag.embeddings import get_embedding_model


def calculate_skill_score(matched_skills, jd_skills):
    if not jd_skills:
        return 0

    return round((len(matched_skills) / len(jd_skills)) * 100, 2)


def calculate_semantic_similarity(resume_text, jd_text):

    embedding_model = get_embedding_model()

    resume_embedding = embedding_model.embed_query(resume_text)

    jd_embedding = embedding_model.embed_query(jd_text)

    similarity = cosine_similarity(
        [resume_embedding],
        [jd_embedding]
    )[0][0]

    return round(similarity * 100, 2)


def calculate_overall_score(skill_score, semantic_score):

    return round(
        (skill_score * 0.6) +
        (semantic_score * 0.4),
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