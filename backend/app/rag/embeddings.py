from langchain_huggingface import HuggingFaceEmbeddings
from backend.app.core.config import settings

embedding_model = HuggingFaceEmbeddings(
    model_name=settings.EMBEDDING_MODEL
)