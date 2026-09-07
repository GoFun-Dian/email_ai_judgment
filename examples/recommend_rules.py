from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from email_ai_judgment.agents.rule_recommendation_agent import RuleRecommendationAgent
from email_ai_judgment.llm.chat_model import MockChatModel
from email_ai_judgment.models.rule import LabeledEmailSample


async def main() -> None:
    llm = MockChatModel([
        '{"condition": "contains(email, \\\"urgent\\\") OR contains(email, \\\"password\\\")", "description": "识别紧急密码验证类恶意样本", "expected_hit_rate": 0.75, "expected_false_positive_rate": 0.08, "confidence": 0.7}'
    ])
    agent = RuleRecommendationAgent(llm)
    samples = [LabeledEmailSample(email_id="s1", raw_email="urgent password verify", label="malicious")]
    response = await agent.recommend(samples)
    print(json.dumps(response.model_dump(mode="json"), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
