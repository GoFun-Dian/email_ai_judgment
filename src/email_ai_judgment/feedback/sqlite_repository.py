# SQLite 反馈仓储实现。


from __future__ import annotations

import json
from pathlib import Path

import aiosqlite

from email_ai_judgment.models.rule import FeedbackLabel, FeedbackRecord

class SQLiteFeedbackRepository:
    # 功能：SQLiteFeedbackRepository。
    # 说明：该类用于封装当前模块的核心数据或行为。

    def __init__(self, db_path: str | Path):
        # 功能：__init__。
        # 参数：db_path。
        # 返回：返回处理结果；若无显式返回则为 None。
        # 异常：发生校验失败、解析失败、超时或外部依赖异常时会向上抛出。
    
        self.db_path = Path(db_path)

    async def init(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id TEXT NOT NULL,
                    label TEXT NOT NULL,
                    original_result TEXT,
                    corrected_result TEXT,
                    comment TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            await db.commit()

    async def insert(self, record: FeedbackRecord) -> FeedbackRecord:
        await self.init()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO feedback_records(email_id, label, original_result, corrected_result, comment, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.email_id,
                    record.label.value,
                    json.dumps(record.original_result, ensure_ascii=False) if record.original_result is not None else None,
                    json.dumps(record.corrected_result, ensure_ascii=False) if record.corrected_result is not None else None,
                    record.comment,
                    record.created_at.isoformat(),
                ),
            )
            await db.commit()
            return record.model_copy(update={"id": cursor.lastrowid})

    async def list(self, limit: int = 100) -> list[FeedbackRecord]:
        await self.init()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT id, email_id, label, original_result, corrected_result, comment, created_at FROM feedback_records ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            rows = await cursor.fetchall()
        return [_row_to_record(row) for row in rows]

    async def export_jsonl(self) -> str:
        records = await self.list(limit=100000)
        lines = [record.model_dump_json() for record in reversed(records)]
        return "\n".join(lines) + ("\n" if lines else "")

    async def bad_case_stats(self) -> dict[str, int]:
        await self.init()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT label, COUNT(*) FROM feedback_records GROUP BY label")
            rows = await cursor.fetchall()
        stats = {label.value: 0 for label in FeedbackLabel}
        stats.update({row[0]: row[1] for row in rows})
        return stats

def _row_to_record(row: tuple) -> FeedbackRecord:
    return FeedbackRecord(
        id=row[0],
        email_id=row[1],
        label=FeedbackLabel(row[2]),
        original_result=json.loads(row[3]) if row[3] else None,
        corrected_result=json.loads(row[4]) if row[4] else None,
        comment=row[5],
        created_at=row[6],
    )
