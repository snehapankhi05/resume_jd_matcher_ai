from functools import lru_cache
from langchain_groq import ChatGroq
from backend.app.core.config import settings


@lru_cache(maxsize=1)
def get_llm():
    return ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0
    )