from __future__ import annotations

from email.message import EmailMessage
from email.utils import getaddresses, parsedate_to_datetime

from email_ai_judgment.models.email import EmailMetadata

def extract_headers(message: EmailMessage) -> EmailMetadata:
    headers = {key: str(value) for key, value in message.items()}
    x_headers = {key: value for key, value in headers.items() if key.lower().startswith("x-")}
    received_path = [str(value) for value in message.get_all("Received", [])]

    sent_at = None
    if message.get("Date"):
        sent_at = parsedate_to_datetime(str(message.get("Date")))

    auth_results = "\n".join(str(v) for v in message.get_all("Authentication-Results", []))
    return EmailMetadata(
        sender=str(message.get("From")) if message.get("From") else None,
        recipients=[addr for _, addr in getaddresses(message.get_all("To", [])) if addr],
        cc=[addr for _, addr in getaddresses(message.get_all("Cc", [])) if addr],
        bcc=[addr for _, addr in getaddresses(message.get_all("Bcc", [])) if addr],
        subject=str(message.get("Subject")) if message.get("Subject") else None,
        sent_at=sent_at,
        headers=headers,
        spf=_extract_auth_value(auth_results, "spf"),
        dkim=_extract_auth_value(auth_results, "dkim"),
        dmarc=_extract_auth_value(auth_results, "dmarc"),
        received_path=received_path,
        x_headers=x_headers,
    )

def _extract_auth_value(auth_results: str, key: str) -> str | None:
    lower = auth_results.lower()
    marker = f"{key}="
    if marker not in lower:
        return None
    start = lower.index(marker) + len(marker)
    value = lower[start:].split()[0].strip(";,")
    return value or None
