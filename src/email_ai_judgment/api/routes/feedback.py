# 反馈接口路由
from __future__ import annotations

from fastapi import APIRouter, Depends

from email_ai_judgment.api.dependencies import get_feedback_loop
from email_ai_judgment.api.schemas import FeedbackRequest
from email_ai_judgment.feedback.feedback_loop import FeedbackLoop
from email_ai_judgment.models.error import JudgmentResponse
from email_ai_judgment.models.rule import FeedbackRecord

router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.post("", response_model=JudgmentResponse[FeedbackRecord])
async def submit_feedback(request: FeedbackRequest, loop: FeedbackLoop = Depends(get_feedback_loop)):
    return await loop.submit(FeedbackRecord.model_validate(request.model_dump()))

@router.get("/export", response_model=JudgmentResponse[str])
async def export_feedback(loop: FeedbackLoop = Depends(get_feedback_loop)):
    return await loop.export_jsonl()

@router.get("/stats", response_model=JudgmentResponse[dict[str, int]])
async def feedback_stats(loop: FeedbackLoop = Depends(get_feedback_loop)):
    return await loop.stats()
