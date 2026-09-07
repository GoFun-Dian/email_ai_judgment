# 规则校验与信誉占位工具。


from __future__ import annotations

from langchain_core.tools import tool

@tool
def validate_rule(condition: str) -> dict:
    """Validate advisory rule syntax for balanced quotes and non-empty condition."""
    if not condition or not condition.strip():
        raise ValueError("condition cannot be empty")
    return {
        "valid": condition.count('"') % 2 == 0 and "DROP" not in condition.upper(),
        "reason": "basic syntax check only",
    }

@tool
def lookup_ip_reputation(ip: str) -> dict:
    """Placeholder IP reputation lookup that returns unknown without external calls."""
    return {"ip": ip, "reputation": "unknown", "source": "placeholder"}
