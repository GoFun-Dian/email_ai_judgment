# 规则推荐接口路由
from __future__ import annotations

from fastapi import APIRouter, Depends

from email_ai_judgment.agents.rule_recommendation_agent import RuleRecommendationAgent
from email_ai_judgment.api.dependencies import get_recommender
from email_ai_judgment.api.schemas import RecommendRequest
from email_ai_judgment.models.error import JudgmentResponse
from email_ai_judgment.models.rule import RuleSuggestion

router = APIRouter(prefix="/recommend", tags=["recommend"])

@router.post("", response_model=JudgmentResponse[RuleSuggestion])
async def recommend(request: RecommendRequest, recommender: RuleRecommendationAgent = Depends(get_recommender)):
    return await recommender.recommend(request.samples)
