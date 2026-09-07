from __future__ import annotations

import re

from email_ai_judgment.models.email import UrlFeature
from email_ai_judgment.utils.domain_utils import extract_domain_from_url, is_ip_literal, is_shortener

URL_RE = re.compile(r"https?://[^\s<>'\")]+", re.IGNORECASE)

def extract_urls(*texts: str) -> list[UrlFeature]:
    seen: set[str] = set()
    urls: list[UrlFeature] = []
    for text in texts:
        for match in URL_RE.findall(text or ""):
            url = match.rstrip(".,;:!?]")
            if url in seen:
                continue
            seen.add(url)
            domain = extract_domain_from_url(url)
            scheme = url.split(":", 1)[0].lower() if ":" in url else None
            urls.append(
                UrlFeature(
                    url=url,
                    domain=domain,
                    scheme=scheme,
                    is_shortened=is_shortener(domain),
                    contains_ip=is_ip_literal(domain),
                )
            )
    return urls
