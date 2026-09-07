# 项目运行配置与环境变量校验。


from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EMAIL_AI_", env_file=".env", extra="ignore")

    llm_provider: Literal["openai", "mock"] = "openai"
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    llm_model: str = "gpt-4o-mini"
    llm_timeout_seconds: float = Field(default=30.0, gt=0)
    llm_temperature: float = 0.0
    llm_max_retries: int = 0

    enable_langsmith: bool = False
    langsmith_api_key: str | None = None
    langsmith_project: str = "email-ai-assistant"
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_tracing: bool = True

    phishing_weight: float = Field(default=0.35, ge=0)
    attachment_weight: float = Field(default=0.25, ge=0)
    bec_weight: float = Field(default=0.25, ge=0)
    spam_weight: float = Field(default=0.15, ge=0)

    trusted_threshold: float = Field(default=10.0, ge=0, le=100)
    low_threshold: float = Field(default=30.0, ge=0, le=100)
    medium_threshold: float = Field(default=60.0, ge=0, le=100)
    high_threshold: float = Field(default=85.0, ge=0, le=100)

    log_level: str = "INFO"
    feedback_db_path: Path = Path("data/feedback.sqlite3")
    enable_langsmith: bool = False
    enable_langfuse: bool = False

    def apply_langsmith_env(self) -> None:
        """把配置写入 os.environ，必须在 import langchain 之前调用。"""
        if not self.enable_langsmith:
            return
        os.environ["LANGSMITH_API_KEY"] = self.langsmith_api_key
        os.environ["LANGSMITH_TRACING"] = "true" if self.langsmith_tracing else "false"
        os.environ["LANGSMITH_PROJECT"] = self.langsmith_project
        os.environ["LANGSMITH_ENDPOINT"] = self.langsmith_endpoint

    @field_validator("llm_temperature")
    @classmethod
    def enforce_zero_temperature(cls, value: float) -> float:
        if value != 0:
            raise ValueError("Fail-Fast judgment requires deterministic LLM temperature=0")
        return value

    @field_validator("llm_max_retries")
    @classmethod
    def enforce_no_retries(cls, value: int) -> int:
        if value != 0:
            raise ValueError("Fail-Fast judgment forbids retries; llm_max_retries must be 0")
        return value

    @model_validator(mode="after")
    def validate_weights_and_thresholds(self) -> "Settings":
        total = self.phishing_weight + self.attachment_weight + self.bec_weight + self.spam_weight
        if total <= 0:
            raise ValueError("At least one dimension weight must be positive")
        thresholds = [self.trusted_threshold, self.low_threshold, self.medium_threshold, self.high_threshold]
        if thresholds != sorted(thresholds):
            raise ValueError("Threat thresholds must be ascending")
        return self

    @model_validator(mode="after")
    def require_langsmith_api_key(self) -> "Settings":
        if self.enable_langsmith and not self.langsmith_api_key:
            raise ValueError("enable_langsmith=true 时必须设置 EMAIL_AI_LANGSMITH_API_KEY")
        return self

    @property
    def dimension_weights(self) -> dict[str, float]:
        return {
            "phishing": self.phishing_weight,
            "attachment": self.attachment_weight,
            "bec": self.bec_weight,
            "spam": self.spam_weight,
        }

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    s = Settings()
    s.apply_langsmith_env()
    return s
