# FastAPI 依赖注入
from __future__ import annotations

from functools import lru_cache

from email_ai_judgment.agents.rule_recommendation_agent import RuleRecommendationAgent
from email_ai_judgment.config.settings import get_settings
from email_ai_judgment.engine.judgment_engine import AIJudgmentEngine
from email_ai_judgment.explain.judgment_explainer import JudgmentExplainer
from email_ai_judgment.feedback.feedback_loop import FeedbackLoop
from email_ai_judgment.feedback.sqlite_repository import SQLiteFeedbackRepository
from email_ai_judgment.llm.chat_model import create_chat_model

@lru_cache(maxsize=1)
def get_engine() -> AIJudgmentEngine:
    return AIJudgmentEngine(settings=get_settings())

@lru_cache(maxsize=1)
def get_explainer() -> JudgmentExplainer:
    settings = get_settings()
    return JudgmentExplainer(create_chat_model(settings))

@lru_cache(maxsize=1)
def get_recommender() -> RuleRecommendationAgent:
    settings = get_settings()
    return RuleRecommendationAgent(create_chat_model(settings))

@lru_cache(maxsize=1)
def get_feedback_loop() -> FeedbackLoop:
    settings = get_settings()
    return FeedbackLoop(SQLiteFeedbackRepository(settings.feedback_db_path))
