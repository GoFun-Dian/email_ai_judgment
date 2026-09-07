from __future__ import annotations

from datetime import UTC, datetime

from email_ai_judgment.models.error import ErrorType, JudgmentError

class JudgmentException(Exception):
    error_type: ErrorType = ErrorType.UNKNOWN_ERROR

    def __init__(self, failed_step: str, message: str, detail: str | None = None):
        super().__init__(message)
        self.failed_step = failed_step
        self.message = message
        self.detail = detail
        self.timestamp = datetime.now(UTC)

    def to_error(self) -> JudgmentError:
        return JudgmentError(
            failed_step=self.failed_step,
            error_type=self.error_type,
            message=self.message,
            detail=self.detail,
            timestamp=self.timestamp,
        )

class FeatureExtractionError(JudgmentException):
    error_type = ErrorType.FEATURE_EXTRACTION_ERROR

class LLMInvocationError(JudgmentException):
    error_type = ErrorType.LLM_INVOCATION_ERROR

class OutputParseError(JudgmentException):
    error_type = ErrorType.OUTPUT_PARSE_ERROR

class TimeoutError(JudgmentException):
    error_type = ErrorType.TIMEOUT_ERROR

class ValidationError(JudgmentException):
    error_type = ErrorType.VALIDATION_ERROR

def unknown_error(failed_step: str, exc: Exception) -> JudgmentError:
    return JudgmentError(
        failed_step=failed_step,
        error_type=ErrorType.UNKNOWN_ERROR,
        message="Unexpected error in AI judgment module",
        detail=repr(exc),
    )
