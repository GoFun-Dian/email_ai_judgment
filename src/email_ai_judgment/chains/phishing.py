from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableLambda

from email_ai_judgment.chains.base import build_dimension_chain
from email_ai_judgment.prompts.phishing_prompt import phishing_prompt

def create_phishing_chain(llm: BaseChatModel) -> RunnableLambda:
    return build_dimension_chain("phishing", phishing_prompt(), llm)
