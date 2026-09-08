# 解释接口路由
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from email_ai_judgment.api.dependencies import get_explainer
from email_ai_judgment.api.schemas import ExplainRequest
from email_ai_judgment.exceptions.judgment_exceptions import JudgmentException, LLMInvocationError, TimeoutError
from email_ai_judgment.explain.judgment_explainer import JudgmentExplainer
from email_ai_judgment.models.error import JudgmentResponse

router = APIRouter(prefix="/explain", tags=["explain"])


def _sse(event: str, data: dict) -> str:
    """构造标准 SSE 事件帧。"""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("", response_model=JudgmentResponse[str])
async def explain(request: ExplainRequest, explainer: JudgmentExplainer = Depends(get_explainer)):
    return await explainer.explain(request.result, request.format)


@router.post("/stream")
async def explain_stream(
    request: ExplainRequest,
    raw_request: Request,
    explainer: JudgmentExplainer = Depends(get_explainer),
):
    async def generate():
        """内部异步生成器"""

        # 避免前端因 TTFT 长而超时
        yield _sse("meta", {"event": "meta", "format": request.format})
        try:
            async for chunk in explainer.astream(request.result, request.format):
                if await raw_request.is_disconnected():
                    return
                yield _sse("delta", {"event": "delta", "data": chunk})
            yield _sse("done", {"event": "done"})
        except JudgmentException as exc:
            yield _sse("error", {"event": "error", "error": exc.to_error().model_dump(mode="json")})
        except asyncio.TimeoutError as exc:
            err = TimeoutError("judgment_explainer", "Explanation LLM call timed out", repr(exc)).to_error()
            yield _sse("error", {"event": "error", "error": err.model_dump(mode="json")})
        except Exception as exc:
            err = LLMInvocationError("judgment_explainer", "Explanation LLM call failed", repr(exc)).to_error()
            yield _sse("error", {"event": "error", "error": err.model_dump(mode="json")})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
