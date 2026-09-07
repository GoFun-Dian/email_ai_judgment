# API 请求与响应模型
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from email_ai_judgment.models.judgment import JudgmentResult
from email_ai_judgment.models.rule import FeedbackRecord, LabeledEmailSample

class JudgeEmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email_id: str | None = None
    raw: str | None = None
    data: dict | None = None

class BatchJudgeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    emails: list[JudgeEmailRequest] = Field(min_length=1)

class ExplainRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    result: JudgmentResult
    format: Literal["markdown", "text"] = "markdown"

class RecommendRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    samples: list[LabeledEmailSample] = Field(min_length=1)

class FeedbackRequest(FeedbackRecord):
    pass
