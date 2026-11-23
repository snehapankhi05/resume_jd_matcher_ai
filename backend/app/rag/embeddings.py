from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from backend.app.core.config import settings


@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Load the embedding model once and reuse it.

    Re-creating HuggingFaceEmbeddings on every call reloads the model
    weights from disk each time (several seconds per request).
    """
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL
    )
