from __future__ import annotations

import logging
import uuid
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser, Parser
from typing import Any

from langchain_core.runnables import RunnableLambda

from email_ai_judgment.exceptions.judgment_exceptions import FeatureExtractionError
from email_ai_judgment.extractors.attachment_extractor import extract_attachments
from email_ai_judgment.extractors.body_extractor import extract_body
from email_ai_judgment.extractors.header_extractor import extract_headers
from email_ai_judgment.extractors.sender_profile_extractor import extract_sender_profile
from email_ai_judgment.extractors.url_extractor import extract_urls
from email_ai_judgment.models.email import EmailFeatures, RawEmailInput
from email_ai_judgment.utils.logging import log_step

logger = logging.getLogger(__name__)

class EmailFeatureExtractor:
    step_name = "feature_extraction"

    def __init__(self) -> None:
        self.runnable = RunnableLambda(self.extract, afunc=self.aextract)

    def as_runnable(self) -> RunnableLambda:
        return self.runnable

    def invoke(self, raw_email: str | dict[str, Any] | RawEmailInput) -> dict[str, EmailFeatures]:
        return self.extract(raw_email)

    async def ainvoke(self, raw_email: str | dict[str, Any] | RawEmailInput) -> dict[str, EmailFeatures]:
        return await self.aextract(raw_email)

    async def aextract(self, raw_email: str | dict[str, Any] | RawEmailInput) -> dict[str, EmailFeatures]:
        return self.extract(raw_email)

    def extract(self, raw_email: str | dict[str, Any] | RawEmailInput) -> dict[str, EmailFeatures]:
        email_id = _get_email_id(raw_email)
        with log_step(logger, email_id, self.step_name):
            try:
                model = _normalize_input(raw_email)
                message = _parse_message(model)
                metadata = extract_headers(message)
                body = extract_body(message)
                attachments = extract_attachments(message)
                urls = extract_urls(body.text, body.html)
                sender_profile = extract_sender_profile(metadata.sender)
                features = EmailFeatures(
                    email_id=model.email_id or str(uuid.uuid4()),
                    metadata=metadata,
                    body=body,
                    attachments=attachments,
                    urls=urls,
                    sender_profile=sender_profile,
                )
                return {"features": features}
            except FeatureExtractionError:
                raise
            except Exception as exc:
                raise FeatureExtractionError(
                    failed_step=self.step_name,
                    message="Email feature extraction failed",
                    detail=repr(exc),
                ) from exc

def _get_email_id(raw_email: str | dict[str, Any] | RawEmailInput) -> str | None:
    if isinstance(raw_email, RawEmailInput):
        return raw_email.email_id
    if isinstance(raw_email, dict):
        return raw_email.get("email_id")
    return None

def _normalize_input(raw_email: str | dict[str, Any] | RawEmailInput) -> RawEmailInput:
    if isinstance(raw_email, RawEmailInput):
        return raw_email
    if isinstance(raw_email, str):
        return RawEmailInput(raw=raw_email)
    if isinstance(raw_email, dict):
        return RawEmailInput.model_validate(raw_email)
    raise TypeError(f"Unsupported email input type: {type(raw_email)!r}")

def _parse_message(raw: RawEmailInput) -> EmailMessage:
    if raw.raw:
        if isinstance(raw.raw, bytes):
            return BytesParser(policy=policy.default).parsebytes(raw.raw)
        return Parser(policy=policy.default).parsestr(raw.raw)
    if raw.data:
        message = EmailMessage(policy=policy.default)
        for key, value in dict(raw.data.get("headers", {})).items():
            message[key] = str(value)
        message["From"] = str(raw.data.get("sender", raw.data.get("from", "")))
        message["To"] = ", ".join(raw.data.get("recipients", [])) if isinstance(raw.data.get("recipients"), list) else str(raw.data.get("recipients", ""))
        if raw.data.get("subject"):
            message["Subject"] = str(raw.data["subject"])
        body = str(raw.data.get("text") or raw.data.get("body") or "")
        html = str(raw.data.get("html") or "")
        if html:
            message.set_content(body or " ")
            message.add_alternative(html, subtype="html")
        else:
            message.set_content(body)
        return message
    raise ValueError("RawEmailInput requires raw or data")
