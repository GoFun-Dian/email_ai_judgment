from __future__ import annotations

from email_ai_judgment.models.email import SenderProfile
from email_ai_judgment.utils.domain_utils import detect_spoof_domain, extract_domain_from_email

def extract_sender_profile(sender: str | None) -> SenderProfile:
    domain = extract_domain_from_email(sender)
    suspected, distance = detect_spoof_domain(domain)
    return SenderProfile(
        domain=domain,
        domain_age_days=None,
        ip_reputation="unknown",
        suspected_spoof_domain=suspected,
        spoof_distance=distance,
    )
