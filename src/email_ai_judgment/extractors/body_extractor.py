from __future__ import annotations

from email.message import EmailMessage

from email_ai_judgment.extractors.html_analyzer import analyze_html
from email_ai_judgment.models.email import EmailBody
from email_ai_judgment.utils.text_utils import html_to_text, normalize_whitespace

def extract_body(message: EmailMessage) -> EmailBody:
    text_parts: list[str] = []
    html_parts: list[str] = []

    for part in message.walk():
        if part.get_content_disposition() == "attachment":
            continue
        content_type = part.get_content_type()
        if content_type not in {"text/plain", "text/html"}:
            continue
        payload = part.get_content()
        if not isinstance(payload, str):
            payload = str(payload)
        if content_type == "text/plain":
            text_parts.append(payload)
        else:
            html_parts.append(payload)

    text = normalize_whitespace("\n".join(text_parts))
    html = "\n".join(html_parts)
    return EmailBody(
        text=text,
        html=html,
        html_text=html_to_text(html),
        html_anomalies=analyze_html(html),
    )
