# 解释接口路由
from __future__ import annotations

from fastapi import APIRouter, Depends

from email_ai_judgment.api.dependencies import get_explainer
from email_ai_judgment.api.schemas import ExplainRequest
from email_ai_judgment.explain.judgment_explainer import JudgmentExplainer
from email_ai_judgment.models.error import JudgmentResponse

router = APIRouter(prefix="/explain", tags=["explain"])

@router.post("", response_model=JudgmentResponse[str])
async def explain(request: ExplainRequest, explainer: JudgmentExplainer = Depends(get_explainer)):
    return await explainer.explain(request.result, request.format)
