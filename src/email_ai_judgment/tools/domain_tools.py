# 域名与规则生成工具。


from __future__ import annotations

from langchain_core.tools import tool

from email_ai_judgment.utils.domain_utils import detect_spoof_domain, extract_domain_from_email

@tool
def generate_rule_condition(indicators: list[str]) -> str:
    """Generate a readable advisory rule condition from indicators."""
    escaped = [item.replace('"', '\\"') for item in indicators if item]
    if not escaped:
        return "true"
    return " OR ".join(f'contains(email, "{item}")' for item in escaped)

@tool
def detect_sender_spoof(sender: str) -> dict:
    """Detect whether sender domain looks similar to known brand domains."""
    domain = extract_domain_from_email(sender)
    suspected, distance = detect_spoof_domain(domain)
    return {"domain": domain, "suspected_brand": suspected, "distance": distance}
