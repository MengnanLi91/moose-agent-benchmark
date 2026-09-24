"""Central configuration for semantic-judge language models."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import Field, model_validator

from ..contracts import StrictModel


class LLMProvider(StrEnum):
    OPENAI = "openai"
    CLAUDE = "claude"
    LITELLM = "litellm"
    OLLAMA = "ollama"


class LLMConfig(StrictModel):
    provider: LLMProvider
    model: str = Field(min_length=1)
    base_url: str | None = None
    api_key_env: str | None = None
    timeout_seconds: float = Field(default=120, gt=0)
    temperature: float = Field(default=0, ge=0, le=2)
    max_output_tokens: int = Field(default=4096, gt=0)
    max_retries: int = Field(default=1, ge=0, le=5)

    @model_validator(mode="after")
    def validate_provider_fields(self) -> LLMConfig:
        if self.provider == LLMProvider.LITELLM and self.base_url is None:
            raise ValueError("litellm requires an OpenAI-compatible base_url")
        if self.provider == LLMProvider.OLLAMA and self.base_url is None:
            self.base_url = "http://localhost:11434"
        if self.provider == LLMProvider.OPENAI and self.api_key_env is None:
            self.api_key_env = "OPENAI_API_KEY"
        if self.provider == LLMProvider.CLAUDE and self.api_key_env is None:
            self.api_key_env = "ANTHROPIC_API_KEY"
        return self


def load_llm_config(path: str | Path) -> LLMConfig:
    resolved = Path(path).resolve()
    data = yaml.safe_load(resolved.read_text(encoding="utf-8"))
    return LLMConfig.model_validate(data)
