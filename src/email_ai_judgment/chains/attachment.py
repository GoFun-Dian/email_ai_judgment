from __future__ import annotations

from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableLambda

from email_ai_judgment.chains.base import build_dimension_chain
from email_ai_judgment.models.email import EmailFeatures
from email_ai_judgment.models.judgment import DimensionResult
from email_ai_judgment.prompts.attachment_prompt import attachment_prompt

def create_attachment_chain(llm: BaseChatModel) -> RunnableLambda:
    dimension_chain = build_dimension_chain("attachment", attachment_prompt(), llm)

    def invoke(inputs: dict[str, Any]) -> DimensionResult:
        if not _has_attachments(inputs):
            return _no_attachment_result()
        return dimension_chain.invoke(inputs)

    async def ainvoke(inputs: dict[str, Any]) -> DimensionResult:
        if not _has_attachments(inputs):
            return _no_attachment_result()
        return await dimension_chain.ainvoke(inputs)

    return RunnableLambda(invoke, afunc=ainvoke)

def _has_attachments(inputs: dict[str, Any]) -> bool:
    features = inputs["features"]
    if isinstance(features, EmailFeatures):
        return bool(features.attachments)
    return bool(features.get("attachments")) if isinstance(features, dict) else False

def _no_attachment_result() -> DimensionResult:
    return DimensionResult(
        score=0,
        confidence=1.0,
        threat_types=[],
        summary="无附件",
        evidence=["无附件"],
    )
