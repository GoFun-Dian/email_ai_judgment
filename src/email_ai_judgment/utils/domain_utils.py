# 域名与 URL 辅助工具。


from __future__ import annotations

import difflib
import ipaddress
from urllib.parse import urlparse

SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly", "cutt.ly", "shorturl.at"
}
BRAND_DOMAINS = ["microsoft.com", "google.com", "apple.com", "amazon.com", "paypal.com", "office.com"]

def normalize_domain(domain: str | None) -> str | None:
    if not domain:
        return None
    domain = domain.strip().lower().rstrip(".")
    if not domain:
        return None
    try:
        return domain.encode("idna").decode("ascii")
    except UnicodeError:
        return domain

def extract_domain_from_email(address: str | None) -> str | None:
    if not address or "@" not in address:
        return None
    return normalize_domain(address.rsplit("@", 1)[-1].strip("> "))

def extract_domain_from_url(url: str) -> str | None:
    parsed = urlparse(url)
    return normalize_domain(parsed.hostname)

def is_ip_literal(value: str | None) -> bool:
    if not value:
        return False
    try:
        ipaddress.ip_address(value.strip("[]"))
        return True
    except ValueError:
        return False

def is_shortener(domain: str | None) -> bool:
    domain = normalize_domain(domain)
    return bool(domain and domain in SHORTENER_DOMAINS)

def edit_distance(a: str, b: str) -> int:
    matcher = difflib.SequenceMatcher(a=a, b=b)
    return int(round(max(len(a), len(b)) * (1 - matcher.ratio())))

def detect_spoof_domain(domain: str | None) -> tuple[str | None, int | None]:
    domain = normalize_domain(domain)
    if not domain:
        return None, None
    best_domain: str | None = None
    best_distance: int | None = None
    for brand in BRAND_DOMAINS:
        if domain == brand or domain.endswith("." + brand):
            continue
        distance = edit_distance(domain, brand)
        if best_distance is None or distance < best_distance:
            best_domain, best_distance = brand, distance
    if best_distance is not None and best_distance <= 3:
        return best_domain, best_distance
    return None, None
