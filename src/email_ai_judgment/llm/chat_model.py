# LLM 抽象与 Mock 实现。


from __future__ import annotations

import asyncio
from collections.abc import Iterable
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field

from email_ai_judgment.config.settings import Settings

def default_dimension_json(score: float = 5.0, confidence: float = 0.8, summary: str = "未发现明显威胁") -> str:
    return (
        '{"score": %.1f, "confidence": %.2f, "threat_types": [], '
        '"summary": "%s", "evidence": ["未发现高风险指标"]}'
    ) % (score, confidence, summary)

class MockChatModel(BaseChatModel):
    responses: list[str] = Field(default_factory=lambda: [default_dimension_json()])
    fail_on_call: int | None = None
    timeout_on_call: int | None = None
    delay_seconds: float = 0.0
    calls: int = 0

    def __init__(self, responses: Iterable[str] | None = None, **kwargs: Any):
        if responses is not None:
            kwargs["responses"] = list(responses)
        super().__init__(**kwargs)

    @property
    def _llm_type(self) -> str:
        return "email-ai-mock-chat"

    def _response_for_call(self) -> str:
        idx = max(self.calls - 1, 0)
        if idx < len(self.responses):
            return self.responses[idx]
        return self.responses[-1]

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        self.calls += 1
        if self.fail_on_call == self.calls:
            raise RuntimeError("mock llm failure")
        if self.timeout_on_call == self.calls:
            raise asyncio.TimeoutError("mock llm timeout")
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=self._response_for_call()))])

    async def _agenerate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        self.calls += 1
        if self.delay_seconds:
            await asyncio.sleep(self.delay_seconds)
        if self.fail_on_call == self.calls:
            raise RuntimeError("mock llm failure")
        if self.timeout_on_call == self.calls:
            raise asyncio.TimeoutError("mock llm timeout")
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=self._response_for_call()))])

def create_chat_model(settings: Settings) -> BaseChatModel:
    if settings.llm_provider == "mock":
        return MockChatModel()
    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            temperature=0,
            max_retries=0,
            timeout=settings.llm_timeout_seconds,
        )
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
