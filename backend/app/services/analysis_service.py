from langchain_core.messages import HumanMessage, SystemMessage

from backend.app.prompts.analysis_prompt import SYSTEM_PROMPT
from backend.app.rag.llm import get_llm


def analyze_resume(resume_context, jd_context):

    llm = get_llm()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=f"""
Resume Context:

{resume_context}

--------------------------------

Job Description Context:

{jd_context}
"""
        )
    ]

    response = llm.invoke(messages)

    return response.content