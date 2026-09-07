from __future__ import annotations

import asyncio
from typing import Any

from langchain_core.exceptions import OutputParserException
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from pydantic import ValidationError as PydanticValidationError

from email_ai_judgment.exceptions.judgment_exceptions import LLMInvocationError, OutputParseError, TimeoutError
from email_ai_judgment.models.email import EmailFeatures
from email_ai_judgment.models.judgment import DimensionResult

DIMENSION_STEPS = {
    "phishing": "phishing_chain",
    "attachment": "attachment_chain",
    "bec": "bec_chain",
    "spam": "spam_chain",
}

def feature_context(features: EmailFeatures) -> str:
    return features.model_dump_json(indent=2, exclude_none=True)

def build_dimension_chain(name: str, prompt: ChatPromptTemplate, llm: BaseChatModel) -> RunnableLambda:
    step = DIMENSION_STEPS[name]
    parser = PydanticOutputParser(pydantic_object=DimensionResult)
    raw_chain = prompt.partial(format_instructions=parser.get_format_instructions()) | llm | parser

    def invoke(inputs: dict[str, Any]) -> DimensionResult:
        try:
            return raw_chain.invoke({"feature_context": feature_context(inputs["features"])})
        except (OutputParserException, PydanticValidationError) as exc:
            raise OutputParseError(step, f"{step} output parsing failed", repr(exc)) from exc
        except asyncio.TimeoutError as exc:
            raise TimeoutError(step, f"{step} timed out", repr(exc)) from exc
        except Exception as exc:
            raise LLMInvocationError(step, f"{step} LLM invocation failed", repr(exc)) from exc

    async def ainvoke(inputs: dict[str, Any]) -> DimensionResult:
        try:
            return await raw_chain.ainvoke({"feature_context": feature_context(inputs["features"])})
        except (OutputParserException, PydanticValidationError) as exc:
            raise OutputParseError(step, f"{step} output parsing failed", repr(exc)) from exc
        except asyncio.TimeoutError as exc:
            raise TimeoutError(step, f"{step} timed out", repr(exc)) from exc
        except Exception as exc:
            raise LLMInvocationError(step, f"{step} LLM invocation failed", repr(exc)) from exc

    return RunnableLambda(invoke, afunc=ainvoke)
