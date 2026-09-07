# 样本分析工具。


from __future__ import annotations

from langchain_core.tools import tool

from email_ai_judgment.models.rule import LabeledEmailSample

@tool
def analyze_email_samples(samples: list[dict]) -> dict:
    """Analyze labeled email samples and return aggregate label counts."""
    parsed = [LabeledEmailSample.model_validate(sample) for sample in samples]
    counts: dict[str, int] = {}
    for sample in parsed:
        counts[sample.label] = counts.get(sample.label, 0) + 1
    return {"sample_count": len(parsed), "label_counts": counts}
