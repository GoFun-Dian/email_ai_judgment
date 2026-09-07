from __future__ import annotations

from email_ai_judgment.exceptions.judgment_exceptions import JudgmentException, ValidationError, unknown_error
from email_ai_judgment.feedback.repository import FeedbackRepository
from email_ai_judgment.models.error import JudgmentResponse
from email_ai_judgment.models.rule import FeedbackRecord

class FeedbackLoop:

    def __init__(self, repository: FeedbackRepository):
        self.repository = repository

    async def submit(self, record: FeedbackRecord) -> JudgmentResponse[FeedbackRecord]:
        try:
            saved = await self.repository.insert(record)
            return JudgmentResponse[FeedbackRecord](success=True, data=saved, error=None)
        except JudgmentException as exc:
            return JudgmentResponse[FeedbackRecord](success=False, data=None, error=exc.to_error())
        except Exception as exc:
            err = ValidationError("feedback_submit", "Feedback submission failed", repr(exc)).to_error()
            return JudgmentResponse[FeedbackRecord](success=False, data=None, error=err)

    async def export_jsonl(self) -> JudgmentResponse[str]:
        try:
            data = await self.repository.export_jsonl()
            return JudgmentResponse[str](success=True, data=data, error=None)
        except Exception as exc:
            return JudgmentResponse[str](success=False, data=None, error=unknown_error("feedback_export", exc))

    async def stats(self) -> JudgmentResponse[dict[str, int]]:
        try:
            stats = await self.repository.bad_case_stats()
            return JudgmentResponse[dict[str, int]](success=True, data=stats, error=None)
        except Exception as exc:
            return JudgmentResponse[dict[str, int]](success=False, data=None, error=unknown_error("feedback_stats", exc))
