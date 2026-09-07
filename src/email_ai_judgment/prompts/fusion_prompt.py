# 融合链边界说明。


from __future__ import annotations

FUSION_PROMPT_NOTE = """
FusionChain is intentionally deterministic and does not use an LLM prompt.

The requirement asks for prompt modules alongside four dimension prompts. This module documents the boundary:
- Dimension chains use ChatPromptTemplate + LLM + PydanticOutputParser.
- FusionChain uses weighted averaging and threshold mapping only.
- No rule-engine score or result is accepted here.
- No fallback, retry, or degraded scoring is implemented.
"""
