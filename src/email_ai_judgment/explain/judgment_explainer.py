from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from email_ai_judgment.exceptions.judgment_exceptions import JudgmentException, LLMInvocationError, TimeoutError, unknown_error
from email_ai_judgment.models.error import JudgmentResponse
from email_ai_judgment.models.judgment import JudgmentResult

class JudgmentExplainer:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "你是企业邮件安全分析师。根据研判结果生成报告，只输出报告正文。"),
                (
                    "human",
                    "输出格式：{format}\n结构：结论摘要 -> 威胁类型分析 -> 关键证据 -> 处置建议。\n研判结果：\n{result}",
                ),
            ]
        )

    async def explain(self, result: JudgmentResult, format: Literal["markdown", "text"] = "markdown") -> JudgmentResponse[str]:
        try:
            chain = self.prompt | self.llm
            message = await chain.ainvoke({"format": format, "result": result.model_dump_json(indent=2)})
            return JudgmentResponse[str](success=True, data=str(message.content), error=None)
        except JudgmentException as exc:
            return JudgmentResponse[str](success=False, data=None, error=exc.to_error())
        except asyncio.TimeoutError as exc:
            err = TimeoutError("judgment_explainer", "Explanation LLM call timed out", repr(exc)).to_error()
            return JudgmentResponse[str](success=False, data=None, error=err)
        except Exception as exc:
            err = LLMInvocationError("judgment_explainer", "Explanation LLM call failed", repr(exc)).to_error()
            return JudgmentResponse[str](success=False, data=None, error=err)

    async def astream(self, result: JudgmentResult, format: Literal["markdown", "text"] = "text") -> AsyncIterator[str]:
        chain = self.prompt | self.llm
        async for chunk in chain.astream({"format": format, "result": result.model_dump_json(indent=2)}):
            text = chunk.content
            if text:
                yield str(text)
