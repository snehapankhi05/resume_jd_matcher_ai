from langchain_groq import ChatGroq
from backend.app.core.config import settings

llm = ChatGroq(
    model=settings.GROQ_MODEL,
    api_key=settings.GROQ_API_KEY,
    temperature=0
)