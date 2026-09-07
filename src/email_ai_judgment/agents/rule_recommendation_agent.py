# 规则推荐 Agent。


from __future__ import annotations

import asyncio

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from email_ai_judgment.exceptions.judgment_exceptions import JudgmentException, LLMInvocationError, OutputParseError, TimeoutError
from email_ai_judgment.models.error import JudgmentResponse
from email_ai_judgment.models.rule import LabeledEmailSample, RuleSuggestion
from email_ai_judgment.tools.domain_tools import generate_rule_condition
from email_ai_judgment.tools.reputation_tools import validate_rule
from email_ai_judgment.tools.sample_tools import analyze_email_samples

class RuleRecommendationAgent:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.tools = [analyze_email_samples, generate_rule_condition, validate_rule]
        self.parser = PydanticOutputParser(pydantic_object=RuleSuggestion)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是邮件安全规则推荐 Agent。你只能给出参考规则建议，绝不能修改或发布任何生效规则。"
                    "工具分析结果仅作为上下文。只输出 JSON。\n{format_instructions}",
                ),
                ("human", "已标注恶意样本：\n{samples}\n\n工具分析结果：\n{tool_context}\n\n请输出规则建议 JSON。"),
            ]
        ).partial(format_instructions=self.parser.get_format_instructions())

    async def recommend(self, samples: list[LabeledEmailSample]) -> JudgmentResponse[RuleSuggestion]:
        try:
            sample_dicts = [sample.model_dump() for sample in samples]
            analysis = analyze_email_samples.invoke({"samples": sample_dicts})
            indicators = _collect_indicators(samples)
            condition = generate_rule_condition.invoke({"indicators": indicators})
            validation = validate_rule.invoke({"condition": condition})
            tool_context = {"analysis": analysis, "draft_condition": condition, "validation": validation}
            chain = self.prompt | self.llm | self.parser
            suggestion = await chain.ainvoke({"samples": sample_dicts, "tool_context": tool_context})
            return JudgmentResponse[RuleSuggestion](success=True, data=suggestion, error=None)
        except JudgmentException as exc:
            return JudgmentResponse[RuleSuggestion](success=False, data=None, error=exc.to_error())
        except asyncio.TimeoutError as exc:
            err = TimeoutError("rule_recommendation_agent", "Rule recommendation timed out", repr(exc)).to_error()
            return JudgmentResponse[RuleSuggestion](success=False, data=None, error=err)
        except Exception as exc:
            if exc.__class__.__name__.endswith("ParserException"):
                err = OutputParseError("rule_recommendation_agent", "Rule suggestion parsing failed", repr(exc)).to_error()
            else:
                err = LLMInvocationError("rule_recommendation_agent", "Rule recommendation failed", repr(exc)).to_error()
            return JudgmentResponse[RuleSuggestion](success=False, data=None, error=err)

def _collect_indicators(samples: list[LabeledEmailSample]) -> list[str]:
    indicators: list[str] = []
    keywords = ["urgent", "password", "verify", "invoice", "wire", "transfer", "login"]
    combined = "\n".join(sample.raw_email.lower() for sample in samples)
    for keyword in keywords:
        if keyword in combined:
            indicators.append(keyword)
    return indicators or ["high_risk_sample_cluster"]
