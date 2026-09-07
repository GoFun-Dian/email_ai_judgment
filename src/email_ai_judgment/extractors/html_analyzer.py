from __future__ import annotations

import re

from email_ai_judgment.models.email import HtmlAnomalies

def analyze_html(html: str | None) -> HtmlAnomalies:
    html = html or ""
    lower = html.lower()
    hidden_div_count = len(re.findall(r"<div[^>]+(?:display\s*:\s*none|visibility\s*:\s*hidden|hidden)", lower))
    zero_font_count = len(re.findall(r"font-size\s*:\s*0(?:px|em|rem)?", lower))
    meta_refresh_count = len(re.findall(r"<meta[^>]+http-equiv=[\"']?refresh", lower))
    suspicious_forms = len(re.findall(r"<form[^>]+action=[\"']?https?://", lower))
    external_resource_count = len(re.findall(r"<(?:img|script|iframe|link)[^>]+(?:src|href)=[\"']?https?://", lower))
    return HtmlAnomalies(
        hidden_div_count=hidden_div_count,
        zero_font_count=zero_font_count,
        meta_refresh_count=meta_refresh_count,
        suspicious_forms=suspicious_forms,
        external_resource_count=external_resource_count,
    )
