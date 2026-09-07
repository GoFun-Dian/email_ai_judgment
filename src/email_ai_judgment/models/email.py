# 邮件输入与特征模型。


from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

class RawEmailInput(BaseModel):


    model_config = ConfigDict(extra="forbid")

    email_id: str | None = None
    raw: str | None = None
    data: dict[str, Any] | None = None

class EmailMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sender: str | None = None
    recipients: list[str] = Field(default_factory=list)
    cc: list[str] = Field(default_factory=list)
    bcc: list[str] = Field(default_factory=list)
    subject: str | None = None
    sent_at: datetime | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    spf: str | None = None
    dkim: str | None = None
    dmarc: str | None = None
    received_path: list[str] = Field(default_factory=list)
    x_headers: dict[str, str] = Field(default_factory=dict)

class HtmlAnomalies(BaseModel):

    model_config = ConfigDict(extra="forbid")

    hidden_div_count: int = 0
    zero_font_count: int = 0
    meta_refresh_count: int = 0
    suspicious_forms: int = 0
    external_resource_count: int = 0

class EmailBody(BaseModel):

    model_config = ConfigDict(extra="forbid")

    text: str = ""
    html: str = ""
    html_text: str = ""
    html_anomalies: HtmlAnomalies = Field(default_factory=HtmlAnomalies)

class AttachmentFeature(BaseModel):

    model_config = ConfigDict(extra="forbid")

    filename: str
    content_type: str | None = None
    size: int = 0
    md5: str | None = None
    sha256: str | None = None
    has_macro: bool = False
    is_password_protected: bool = False
    is_suspicious_type: bool = False

class UrlFeature(BaseModel):

    model_config = ConfigDict(extra="forbid")

    url: str
    domain: str | None = None
    scheme: str | None = None
    is_shortened: bool = False
    contains_ip: bool = False

class SenderProfile(BaseModel):

    model_config = ConfigDict(extra="forbid")

    domain: str | None = None
    domain_age_days: int | None = None
    ip_reputation: str | None = None
    suspected_spoof_domain: str | None = None
    spoof_distance: int | None = None

class EmailFeatures(BaseModel):

    model_config = ConfigDict(extra="forbid")

    email_id: str
    metadata: EmailMetadata
    body: EmailBody
    attachments: list[AttachmentFeature] = Field(default_factory=list)
    urls: list[UrlFeature] = Field(default_factory=list)
    sender_profile: SenderProfile = Field(default_factory=SenderProfile)
