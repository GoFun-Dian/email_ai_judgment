from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from email_ai_judgment.config.settings import Settings
from email_ai_judgment.engine.judgment_engine import AIJudgmentEngine
from email_ai_judgment.llm.chat_model import MockChatModel


async def main() -> None:
    raw = Path("examples/sample_emails/phishing.eml").read_text(encoding="utf-8")
    responses = [
        '{"score": 88, "confidence": 0.92, "threat_types": ["phishing"], "summary": "疑似钓鱼邮件", "evidence": ["紧急验证账号", "短链跳转"]}',
        '{"score": 5, "confidence": 0.8, "threat_types": [], "summary": "无附件风险", "evidence": ["未发现附件"]}',
        '{"score": 30, "confidence": 0.7, "threat_types": [], "summary": "存在轻微冒充迹象", "evidence": ["发件域名可疑"]}',
        '{"score": 20, "confidence": 0.7, "threat_types": [], "summary": "垃圾邮件特征不明显", "evidence": ["非营销邮件"]}',
    ]
    engine = AIJudgmentEngine(settings=Settings(llm_provider="mock"), llm=MockChatModel(responses))
    response = await engine.ajudge({"email_id": "demo-phishing", "raw": raw})
    print(json.dumps(response.model_dump(mode="json"), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
