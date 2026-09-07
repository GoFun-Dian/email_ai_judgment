# 统一错误模型与响应包装。


from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

class ErrorType(str, Enum):

    FEATURE_EXTRACTION_ERROR = "FEATURE_EXTRACTION_ERROR"
    LLM_INVOCATION_ERROR = "LLM_INVOCATION_ERROR"
    OUTPUT_PARSE_ERROR = "OUTPUT_PARSE_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

class JudgmentError(BaseModel):

    model_config = ConfigDict(extra="forbid")

    failed_step: str
    error_type: ErrorType
    message: str
    detail: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

T = TypeVar("T")

class JudgmentResponse(BaseModel, Generic[T]):

    model_config = ConfigDict(extra="forbid")

    success: bool
    data: T | None = None
    error: JudgmentError | None = None

    @model_validator(mode="after")
    def validate_envelope(self) -> "JudgmentResponse[T]":
        if self.success and self.error is not None:
            raise ValueError("Successful response cannot contain error")
        if not self.success and self.error is None:
            raise ValueError("Failed response must contain error")
        if not self.success and self.data is not None:
            raise ValueError("Failed response cannot contain data")
        return self
