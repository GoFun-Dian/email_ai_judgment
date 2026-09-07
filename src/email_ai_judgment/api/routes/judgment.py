# 研判接口路由
from __future__ import annotations

from fastapi import APIRouter, Depends

from email_ai_judgment.api.dependencies import get_engine
from email_ai_judgment.api.schemas import BatchJudgeRequest, JudgeEmailRequest
from email_ai_judgment.engine.judgment_engine import AIJudgmentEngine
from email_ai_judgment.models.error import JudgmentResponse
from email_ai_judgment.models.judgment import JudgmentResult

router = APIRouter(prefix="/judgment", tags=["judgment"])

@router.post("", response_model=JudgmentResponse[JudgmentResult])
async def judge_email(request: JudgeEmailRequest, engine: AIJudgmentEngine = Depends(get_engine)):
    return await engine.ajudge(request.model_dump(exclude_none=True))

@router.post("/batch", response_model=list[JudgmentResponse[JudgmentResult]])
async def judge_batch(request: BatchJudgeRequest, engine: AIJudgmentEngine = Depends(get_engine)):
    emails = [item.model_dump(exclude_none=True) for item in request.emails]
    return await engine.abatch(emails)
