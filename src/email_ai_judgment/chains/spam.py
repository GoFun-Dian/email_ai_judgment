from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableLambda

from email_ai_judgment.chains.base import build_dimension_chain
from email_ai_judgment.prompts.spam_prompt import spam_prompt

def create_spam_chain(llm: BaseChatModel) -> RunnableLambda:
    return build_dimension_chain("spam", spam_prompt(), llm)
