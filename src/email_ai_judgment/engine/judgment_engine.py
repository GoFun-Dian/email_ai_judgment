from __future__ import annotations

import asyncio
import logging
from operator import itemgetter
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableParallel

from email_ai_judgment.chains.attachment import create_attachment_chain
from email_ai_judgment.chains.bec import create_bec_chain
from email_ai_judgment.chains.fusion import create_fusion_chain
from email_ai_judgment.chains.phishing import create_phishing_chain
from email_ai_judgment.chains.spam import create_spam_chain
from email_ai_judgment.config.settings import Settings, get_settings
from email_ai_judgment.exceptions.judgment_exceptions import JudgmentException, TimeoutError, unknown_error
from email_ai_judgment.extractors.email_feature_extractor import EmailFeatureExtractor
from email_ai_judgment.llm.chat_model import create_chat_model
from email_ai_judgment.models.error import JudgmentResponse
from email_ai_judgment.models.judgment import JudgmentResult
from email_ai_judgment.utils.logging import log_step

logger = logging.getLogger(__name__)

class AIJudgmentEngine:
    def __init__(
        self,
        settings: Settings | None = None,
        llm: BaseChatModel | None = None,
        feature_extractor: Any | None = None,
        phishing_chain: Any | None = None,
        attachment_chain: Any | None = None,
        bec_chain: Any | None = None,
        spam_chain: Any | None = None,
        fusion_chain: Any | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.llm = llm or create_chat_model(self.settings)
        self.feature_extractor = feature_extractor or EmailFeatureExtractor().as_runnable()
        self.phishing_chain = phishing_chain or create_phishing_chain(self.llm)
        self.attachment_chain = attachment_chain or create_attachment_chain(self.llm)
        self.bec_chain = bec_chain or create_bec_chain(self.llm)
        self.spam_chain = spam_chain or create_spam_chain(self.llm)
        self.fusion_chain = fusion_chain or create_fusion_chain(self.settings)
        self.pipeline = self._build_pipeline()

    def _build_pipeline(self):
        parallel = RunnableParallel(
            {
                "phishing": self.phishing_chain,
                "attachment": self.attachment_chain,
                "bec": self.bec_chain,
                "spam": self.spam_chain,
                "features": itemgetter("features"),
            }
        )
        return self.feature_extractor | parallel | self.fusion_chain

    async def ajudge(self, raw_email: str | dict[str, Any]) -> JudgmentResponse[JudgmentResult]:
        email_id = raw_email.get("email_id") if isinstance(raw_email, dict) else None
        try:
            with log_step(logger, email_id, "judgment_pipeline"):
                result = await asyncio.wait_for(
                    self.pipeline.ainvoke(raw_email),
                    timeout=self.settings.llm_timeout_seconds + 5,
                )
            return JudgmentResponse[JudgmentResult](success=True, data=result, error=None)
        except JudgmentException as exc:
            return JudgmentResponse[JudgmentResult](success=False, data=None, error=exc.to_error())
        except asyncio.TimeoutError as exc:
            err = TimeoutError("judgment_pipeline", "AI judgment pipeline timed out", repr(exc)).to_error()
            return JudgmentResponse[JudgmentResult](success=False, data=None, error=err)
        except Exception as exc:
            logger.debug("unknown_judgment_error", exc_info=True)
            return JudgmentResponse[JudgmentResult](success=False, data=None, error=unknown_error("judgment_pipeline", exc))

    def judge(self, raw_email: str | dict[str, Any]) -> JudgmentResponse[JudgmentResult]:
        return asyncio.run(self.ajudge(raw_email))

    async def abatch(self, emails: list[str | dict[str, Any]]) -> list[JudgmentResponse[JudgmentResult]]:
        """异步批量异步执行研判。"""
        return await asyncio.gather(*(self.ajudge(email) for email in emails))
