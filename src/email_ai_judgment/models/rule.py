# 规则推荐与反馈模型。


from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

class FeedbackLabel(str, Enum):

    CONFIRMED = "confirmed"
    CORRECTED = "corrected"
    FALSE_POSITIVE = "false_positive"
    FALSE_NEGATIVE = "false_negative"

class LabeledEmailSample(BaseModel):

    model_config = ConfigDict(extra="forbid")

    email_id: str
    raw_email: str
    label: str
    notes: str | None = None

class RuleSuggestion(BaseModel):

    model_config = ConfigDict(extra="forbid")

    condition: str
    description: str
    expected_hit_rate: float = Field(ge=0, le=1)
    expected_false_positive_rate: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)

class FeedbackRecord(BaseModel):

    model_config = ConfigDict(extra="forbid")

    id: int | None = None
    email_id: str
    label: FeedbackLabel
    original_result: dict | None = None
    corrected_result: dict | None = None
    comment: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
