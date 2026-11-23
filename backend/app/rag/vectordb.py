from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.documents import Document

from backend.app.core.config import settings
from backend.app.rag.embeddings import get_embedding_model


@lru_cache(maxsize=None)
def get_vector_store(collection_name: str) -> Chroma:
    """Return a cached handle to a persistent Chroma collection."""
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embedding_model(),
        persist_directory=settings.CHROMA_DB_PATH
    )


def create_vector_store(
    documents,
    collection_name: str,
    session_id: str
):
    """
    Store the chunks of one document for one session.

    Any chunks previously stored for the same session in this collection
    are removed first, so re-uploading a file never creates duplicates.
    """

    vector_store = get_vector_store(collection_name)

    vector_store.delete(where={"session_id": session_id})

    ids = [
        f"{session_id}-{index}"
        for index in range(len(documents))
    ]

    vector_store.add_documents(
        documents=documents,
        ids=ids
    )

    return vector_store


def session_has_documents(
    collection_name: str,
    session_id: str
) -> bool:
    """True if at least one chunk exists for this session."""

    data = get_vector_store(collection_name).get(
        where={"session_id": session_id},
        limit=1,
        include=[]
    )

    return bool(data["ids"])


def get_session_documents(
    collection_name: str,
    session_id: str
):
    """Return every stored chunk of a session, in document order."""

    data = get_vector_store(collection_name).get(
        where={"session_id": session_id},
        include=["documents", "metadatas"]
    )

    documents = [
        Document(page_content=text, metadata=metadata or {})
        for text, metadata in zip(
            data["documents"] or [],
            data["metadatas"] or []
        )
    ]

    documents.sort(
        key=lambda doc: (
            doc.metadata.get("page", 0),
            doc.metadata.get("start_index", 0)
        )
    )

    return documents
