# 垃圾邮件检测提示词。


from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

from email_ai_judgment.prompts.common import COMMON_EXAMPLE_SAFE, build_dimension_prompt

def spam_prompt() -> ChatPromptTemplate:
    examples = "\n".join(
        [
            "示例1：正常工作邮件，内容清晰 -> " + COMMON_EXAMPLE_SAFE,
            "示例2：大段营销话术、夸张优惠且无退订信息 -> {\"score\": 78, \"confidence\": 0.86, \"threat_types\": [\"spam\"], \"summary\": \"疑似垃圾营销邮件\", \"evidence\": [\"营销话术密集\", \"缺少退订信息\"]}",
            "示例3：群发中奖促销并包含多个跳转链接 -> {\"score\": 82, \"confidence\": 0.83, \"threat_types\": [\"spam\"], \"summary\": \"垃圾邮件特征明显\", \"evidence\": [\"群发促销\", \"多跳转链接\"]}",
        ]
    )
    return build_dimension_prompt(
        role="垃圾邮件检测链",
        focus="重点分析群发特征、内容质量、营销话术、退订缺失和多链接诱导。",
        examples=examples,
    )
