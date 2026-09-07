# 恶意附件检测提示词。


from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

from email_ai_judgment.prompts.common import COMMON_EXAMPLE_SAFE, build_dimension_prompt

def attachment_prompt() -> ChatPromptTemplate:
    examples = "\n".join(
        [
            "示例1：无附件或仅 PDF 会议资料 -> " + COMMON_EXAMPLE_SAFE,
            "示例2：附件为 invoice.docm 且含宏 -> {\"score\": 88, \"confidence\": 0.91, \"threat_types\": [\"malicious_attachment\"], \"summary\": \"附件存在宏代码和伪装风险\", \"evidence\": [\"docm 宏文档\", \"发票文件名诱导打开\"]}",
            "示例3：附件为 .exe 或脚本文件 -> {\"score\": 92, \"confidence\": 0.89, \"threat_types\": [\"malicious_attachment\"], \"summary\": \"附件类型高危\", \"evidence\": [\"可执行附件不适合作为普通业务邮件附件\"]}",
        ]
    )
    return build_dimension_prompt(
        role="恶意附件检测链",
        focus="重点分析附件类型、文件名伪装、宏代码、密码保护和可疑行为迹象。",
        examples=examples,
    )
