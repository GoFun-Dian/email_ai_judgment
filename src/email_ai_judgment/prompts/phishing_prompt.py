# 钓鱼检测提示词。


from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

from email_ai_judgment.prompts.common import COMMON_EXAMPLE_RISK, COMMON_EXAMPLE_SAFE, build_dimension_prompt

def phishing_prompt() -> ChatPromptTemplate:
    examples = "\n".join(
        [
            "示例1：正文为正常会议通知，无外链 -> " + COMMON_EXAMPLE_SAFE,
            "示例2：正文要求立即验证账号，含短链登录页 -> " + COMMON_EXAMPLE_RISK,
            "示例3：仿冒 Microsoft 安全通知并要求重置密码 -> " + COMMON_EXAMPLE_RISK,
        ]
    )
    return build_dimension_prompt(
        role="钓鱼检测链",
        focus="重点分析正文语义、品牌仿冒、诱导性语言、紧急施压话术和登录凭证诱导。",
        examples=examples,
    )
