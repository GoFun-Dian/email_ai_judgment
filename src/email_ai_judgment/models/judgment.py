# 研判结果与证据模型。


from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

class ThreatLevel(str, Enum):

    TRUSTED = "TRUSTED"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    MALICIOUS = "MALICIOUS"

class EvidenceItem(BaseModel):

    model_config = ConfigDict(extra="forbid")

    dimension: str
    description: str
    contribution: float = Field(ge=0, le=100)

class DimensionResult(BaseModel):

    model_config = ConfigDict(extra="forbid")

    score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    threat_types: list[str] = Field(default_factory=list)
    summary: str
    evidence: list[str] = Field(default_factory=list)

class JudgmentResult(BaseModel):

    model_config = ConfigDict(extra="forbid")

    email_id: str
    threat_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    threat_level: ThreatLevel
    threat_types: list[str] = Field(default_factory=list)
    summary: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    dimension_scores: dict[str, DimensionResult]
