from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from email_ai_judgment.config.settings import Settings
from email_ai_judgment.engine.judgment_engine import AIJudgmentEngine


async def main() -> None:
    engine = AIJudgmentEngine(settings=Settings(llm_provider="mock"))
    response = await engine.ajudge({"email_id": "broken", "raw": None})
    print(json.dumps(response.model_dump(mode="json"), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
