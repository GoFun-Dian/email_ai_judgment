"""反馈仓储协议。"""

from __future__ import annotations

from typing import Protocol

from email_ai_judgment.models.rule import FeedbackRecord


class FeedbackRepository(Protocol):
    async def init(self) -> None: ...

    async def insert(self, record: FeedbackRecord) -> FeedbackRecord: ...

    async def list(self, limit: int = 100) -> list[FeedbackRecord]: ...

    async def export_jsonl(self) -> str: ...

    async def bad_case_stats(self) -> dict[str, int]: ...
