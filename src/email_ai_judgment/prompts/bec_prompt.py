# BEC 检测提示词。


from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

from email_ai_judgment.prompts.common import COMMON_EXAMPLE_SAFE, build_dimension_prompt

def bec_prompt() -> ChatPromptTemplate:
    examples = "\n".join(
        [
            "示例1：普通内部项目同步，无付款请求 -> " + COMMON_EXAMPLE_SAFE,
            "示例2：冒充 CEO 要求紧急转账 -> {\"score\": 90, \"confidence\": 0.88, \"threat_types\": [\"bec\"], \"summary\": \"疑似商业邮件诈骗\", \"evidence\": [\"权威冒充\", \"紧急财务请求\"]}",
            "示例3：供应商变更收款账户且域名相似 -> {\"score\": 86, \"confidence\": 0.84, \"threat_types\": [\"bec\"], \"summary\": \"疑似供应商付款诈骗\", \"evidence\": [\"收款信息变更\", \"发件域名存在仿冒迹象\"]}",
        ]
    )
    return build_dimension_prompt(
        role="BEC 商业诈骗检测链",
        focus="重点分析发件人伪装、财务请求、上下文异常、权威冒充和供应商账户变更。",
        examples=examples,
    )
