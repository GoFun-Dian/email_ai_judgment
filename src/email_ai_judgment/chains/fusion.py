from __future__ import annotations

from typing import Any

from langchain_core.runnables import RunnableLambda

from email_ai_judgment.config.settings import Settings
from email_ai_judgment.exceptions.judgment_exceptions import ValidationError
from email_ai_judgment.models.email import EmailFeatures
from email_ai_judgment.models.judgment import DimensionResult, EvidenceItem, JudgmentResult, ThreatLevel

DIMENSION_LABELS = {
    "phishing": "钓鱼检测",
    "attachment": "恶意附件检测",
    "bec": "BEC 商业诈骗检测",
    "spam": "垃圾邮件检测",
}

class FusionChain:
    # 融合链与最终结果组装
    step_name = "fusion_chain"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.runnable = RunnableLambda(self.fuse, afunc=self.afuse)

    def as_runnable(self) -> RunnableLambda:
        return self.runnable

    async def afuse(self, inputs: dict[str, Any]) -> JudgmentResult:
        """异步融合四个维度的结果。"""
        return self.fuse(inputs)

    def fuse(self, inputs: dict[str, Any]) -> JudgmentResult:
        """融合四个维度的结果。"""
        try:
            features: EmailFeatures = inputs["features"]["features"] if isinstance(inputs.get("features"), dict) else inputs["features"]
            dimensions = {
                name: _coerce_dimension(inputs[name])
                for name in ["phishing", "attachment", "bec", "spam"]
            }
            weights = self.settings.dimension_weights
            total_weight = sum(weights.values())
            threat_score = sum(dimensions[name].score * weights[name] for name in dimensions) / total_weight
            confidence = sum(dimensions[name].confidence * weights[name] for name in dimensions) / total_weight
            threat_types = sorted({t for dim in dimensions.values() for t in dim.threat_types})
            evidence = _build_evidence(dimensions, weights, total_weight)
            level = _threat_level(threat_score, self.settings)
            summary = _summary(level, threat_score, threat_types)
            return JudgmentResult(
                email_id=features.email_id,
                threat_score=round(threat_score, 2),
                confidence=round(confidence, 4),
                threat_level=level,
                threat_types=threat_types,
                summary=summary,
                evidence=evidence,
                dimension_scores=dimensions,
            )
        except Exception as exc:
            raise ValidationError(self.step_name, "Judgment result fusion failed", repr(exc)) from exc

def create_fusion_chain(settings: Settings) -> RunnableLambda:
    """创建 fusion_chain。"""
    return FusionChain(settings).as_runnable()

def _coerce_dimension(value: Any) -> DimensionResult:
    if isinstance(value, DimensionResult):
        return value
    return DimensionResult.model_validate(value)

def _build_evidence(dimensions: dict[str, DimensionResult], weights: dict[str, float], total_weight: float) -> list[EvidenceItem]:
    items: list[EvidenceItem] = []
    for name, result in dimensions.items():
        contribution = result.score * weights[name] / total_weight
        descriptions = result.evidence or [result.summary]
        items.append(
            EvidenceItem(
                dimension=DIMENSION_LABELS.get(name, name),
                description="；".join(descriptions),
                contribution=round(contribution, 2),
            )
        )
    return sorted(items, key=lambda item: item.contribution, reverse=True)

def _threat_level(score: float, settings: Settings) -> ThreatLevel:
    if score >= settings.high_threshold:
        return ThreatLevel.MALICIOUS
    if score >= settings.medium_threshold:
        return ThreatLevel.HIGH
    if score >= settings.low_threshold:
        return ThreatLevel.MEDIUM
    if score >= settings.trusted_threshold:
        return ThreatLevel.LOW
    return ThreatLevel.TRUSTED

def _summary(level: ThreatLevel, score: float, threat_types: list[str]) -> str:
    type_text = "、".join(threat_types) if threat_types else "明显威胁"
    if level in {ThreatLevel.MALICIOUS, ThreatLevel.HIGH}:
        return f"邮件风险较高，综合评分 {score:.1f}，疑似 {type_text}。"
    if level == ThreatLevel.MEDIUM:
        return f"邮件存在中等风险，综合评分 {score:.1f}，建议人工复核。"
    if level == ThreatLevel.LOW:
        return f"邮件风险较低，综合评分 {score:.1f}，未达到高危阈值。"
    return f"邮件可信度较高，综合评分 {score:.1f}，未发现明显威胁。"
