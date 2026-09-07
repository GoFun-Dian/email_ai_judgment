from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableLambda

from email_ai_judgment.chains.base import build_dimension_chain
from email_ai_judgment.prompts.attachment_prompt import attachment_prompt

def create_attachment_chain(llm: BaseChatModel) -> RunnableLambda:
    return build_dimension_chain("attachment", attachment_prompt(), llm)
