from langchain_chroma import Chroma

from backend.app.core.config import settings
from backend.app.rag.embeddings import get_embedding_model


def get_context(
    session_id: str,
    query: str
):
    """
    Retrieve Resume and JD context
    """

    embedding_model = get_embedding_model()

    resume_db = Chroma(
        persist_directory=settings.CHROMA_DB_PATH,
        embedding_function=embedding_model,
        collection_name="resume_collection"
    )

    jd_db = Chroma(
        persist_directory=settings.CHROMA_DB_PATH,
        embedding_function=embedding_model,
        collection_name="jd_collection"
    )

    resume_docs = resume_db.similarity_search(
        query=query,
        k=4,
        filter={
            "session_id": session_id
        }
    )

    jd_docs = jd_db.similarity_search(
        query=query,
        k=4,
        filter={
            "session_id": session_id
        }
    )

    resume_context = "\n\n".join(
        doc.page_content for doc in resume_docs
    )

    jd_context = "\n\n".join(
        doc.page_content for doc in jd_docs
    )

    return {
        "resume_context": resume_context,
        "jd_context": jd_context
    }