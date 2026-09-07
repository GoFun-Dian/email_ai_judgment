from __future__ import annotations

import hashlib
from email.message import EmailMessage

from email_ai_judgment.models.email import AttachmentFeature

MACRO_EXTENSIONS = {".docm", ".xlsm", ".pptm"}
SUSPICIOUS_EXTENSIONS = {".exe", ".scr", ".js", ".vbs", ".bat", ".cmd", ".ps1", ".jar", ".docm", ".xlsm"}

def extract_attachments(message: EmailMessage) -> list[AttachmentFeature]:

    attachments: list[AttachmentFeature] = []
    for part in message.walk():
        if part.get_content_disposition() != "attachment":
            continue
        filename = part.get_filename() or "unnamed"
        payload = part.get_payload(decode=True) or b""
        lower_name = filename.lower()
        extension = "." + lower_name.rsplit(".", 1)[-1] if "." in lower_name else ""
        attachments.append(
            AttachmentFeature(
                filename=filename,
                content_type=part.get_content_type(),
                size=len(payload),
                md5=hashlib.md5(payload).hexdigest(),
                sha256=hashlib.sha256(payload).hexdigest(),
                has_macro=extension in MACRO_EXTENSIONS or b"vbaProject" in payload[:200000],
                is_password_protected=_looks_password_protected(payload, lower_name),
                is_suspicious_type=extension in SUSPICIOUS_EXTENSIONS,
            )
        )
    return attachments

def _looks_password_protected(payload: bytes, filename: str) -> bool:
    markers = [b"EncryptedPackage", b"/Encrypt", b"password"]
    if any(marker.lower() in payload[:200000].lower() for marker in markers):
        return True
    return filename.endswith(".zip") and payload.startswith(b"PK") and b"\x01\x00\x00\x00" in payload[:100]
