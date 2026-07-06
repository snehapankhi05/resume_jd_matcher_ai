from langchain_chroma import Chroma

from backend.app.core.config import settings
from backend.app.rag.embeddings import get_embedding_model


def create_vector_store(documents, collection_name: str):
    embedding_model = get_embedding_model()

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=settings.CHROMA_DB_PATH,
        collection_name=collection_name
    )

    return vector_store