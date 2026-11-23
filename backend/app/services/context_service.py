from langsmith import traceable

from backend.app.rag.bm25 import BM25Retriever

from backend.app.rag.hybrid_search import hybrid_search
from backend.app.rag.vectordb import (
    get_session_documents,
    get_vector_store,
)

RESUME_COLLECTION = "resume_collection"
JD_COLLECTION = "jd_collection"

# Aspects used to pull the most useful chunks for the LLM prompt.
CONTEXT_QUERIES = [
    "technical skills and technologies",
    "work experience and internships",
    "projects and achievements",
    "education and certifications",
]

CHUNKS_PER_QUERY = 3
MAX_CONTEXT_CHUNKS = 8


class MissingDocumentError(Exception):
    """Raised when a session has no resume and/or no job description."""


def _retrieve_context(
    collection_name: str,
    session_id: str,
    all_docs,
    queries=CONTEXT_QUERIES
):
    """
    Hybrid retrieval (BM25 keyword search + vector search, fused with
    Reciprocal Rank Fusion) restricted to one session.
    """

    bm25_retriever = BM25Retriever.from_documents(
        all_docs,
        k=CHUNKS_PER_QUERY
    )

    vector_retriever = get_vector_store(collection_name).as_retriever(
        search_kwargs={
            "k": CHUNKS_PER_QUERY,
            "filter": {"session_id": session_id}
        }
    )

    selected = []
    seen = set()

    for query in queries:

        for doc in hybrid_search(
            query,
            bm25_retriever,
            vector_retriever
        ):
            if doc.page_content in seen:
                continue

            seen.add(doc.page_content)
            selected.append(doc)

    return selected[:MAX_CONTEXT_CHUNKS]


@traceable(name="get_context", run_type="chain")
def get_context(
    session_id: str,
    query: str = None
):
    """
    Load the Resume and JD of a session.

    Returns
    -------
    resume_context / jd_context : the most relevant chunks, joined, for
        the LLM prompt (keeps the prompt small).
    resume_text / jd_text : the FULL text, for skill extraction. Skills
        must be extracted from the whole document, not from a few chunks.
    resume_chunks / jd_chunks : all chunks, for semantic similarity.
    """

    resume_docs = get_session_documents(RESUME_COLLECTION, session_id)
    jd_docs = get_session_documents(JD_COLLECTION, session_id)

    if not resume_docs:
        raise MissingDocumentError(
            "No resume found for this session. Please upload a resume."
        )

    if not jd_docs:
        raise MissingDocumentError(
            "No job description found for this session. "
            "Please upload a job description."
        )

    queries = [query] if query else CONTEXT_QUERIES

    resume_selected = _retrieve_context(
        RESUME_COLLECTION, session_id, resume_docs, queries
    )

    jd_selected = _retrieve_context(
        JD_COLLECTION, session_id, jd_docs, queries
    )

    resume_chunks = [doc.page_content for doc in resume_docs]
    jd_chunks = [doc.page_content for doc in jd_docs]

    return {
        "resume_context": "\n\n".join(
            doc.page_content for doc in resume_selected
        ),
        "jd_context": "\n\n".join(
            doc.page_content for doc in jd_selected
        ),
        "resume_text": "\n".join(resume_chunks),
        "jd_text": "\n".join(jd_chunks),
        "resume_chunks": resume_chunks,
        "jd_chunks": jd_chunks
    }
