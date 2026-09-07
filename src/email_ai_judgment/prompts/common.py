# 研判提示词公共片段。


from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

JSON_ONLY_SYSTEM_SUFFIX = "必须只输出一个 JSON 对象，不要输出 Markdown、代码块或额外解释。"

def build_dimension_prompt(role: str, focus: str, examples: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"你是企业邮件网关 AI 研判模块中的{role}。{focus}\n"
                "你只根据输入的 AI 特征做独立研判，不接收规则引擎结果，也不修改规则。\n"
                f"{JSON_ONLY_SYSTEM_SUFFIX}\n\n输出格式要求：\n{{format_instructions}}",
            ),
            ("human", "Few-shot 示例：\n{examples}\n\n邮件特征上下文：\n{feature_context}\n\n请输出 JSON："),
        ]
    ).partial(examples=examples)

COMMON_EXAMPLE_SAFE = '{"score": 5, "confidence": 0.82, "threat_types": [], "summary": "未发现明显威胁", "evidence": ["发件人与内容上下文一致"]}'
COMMON_EXAMPLE_RISK = '{"score": 85, "confidence": 0.9, "threat_types": ["phishing"], "summary": "存在高风险钓鱼特征", "evidence": ["包含紧急施压话术", "URL 指向可疑短链"]}'
