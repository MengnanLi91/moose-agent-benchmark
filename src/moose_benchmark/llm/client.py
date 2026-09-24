"""Provider-switching structured generation for private evaluators."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any, TypeVar

from pydantic import BaseModel

from .config import LLMConfig, LLMProvider

OutputT = TypeVar("OutputT", bound=BaseModel)


@dataclass(frozen=True)
class StructuredGeneration:
    output: BaseModel
    provider: str
    model: str
    configuration_sha256: str
    request_sha256: str
    response_sha256: str


class EvaluatorInfrastructureError(RuntimeError):
    """Semantic judge transport or structured-output failure."""


def _sha256_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class LLMClient:
    def __init__(self, config: LLMConfig):
        self.config = config

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[OutputT],
    ) -> StructuredGeneration:
        schema = response_model.model_json_schema()
        request = {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "schema": schema,
        }
        configuration = self.config.model_dump(mode="json")
        last_error: Exception | None = None
        for _attempt in range(self.config.max_retries + 1):
            try:
                raw = self._generate(system_prompt, user_prompt, schema)
                raw_text = raw if isinstance(raw, str) else json.dumps(raw, sort_keys=True)
                data = json.loads(raw) if isinstance(raw, str) else raw
                output = response_model.model_validate(data)
                return StructuredGeneration(
                    output=output,
                    provider=self.config.provider.value,
                    model=self.config.model,
                    configuration_sha256=_sha256_json(configuration),
                    request_sha256=_sha256_json(request),
                    response_sha256=hashlib.sha256(raw_text.encode("utf-8")).hexdigest(),
                )
            except Exception as exc:
                last_error = exc
        raise EvaluatorInfrastructureError(
            f"semantic judge failed after {self.config.max_retries + 1} attempt(s): {last_error}"
        ) from last_error

    def _generate(self, system_prompt: str, user_prompt: str, schema: dict) -> Any:
        if self.config.provider in {LLMProvider.OPENAI, LLMProvider.LITELLM}:
            return self._generate_openai(system_prompt, user_prompt, schema)
        if self.config.provider == LLMProvider.CLAUDE:
            return self._generate_claude(system_prompt, user_prompt, schema)
        if self.config.provider == LLMProvider.OLLAMA:
            return self._generate_ollama(system_prompt, user_prompt, schema)
        raise ValueError(f"unsupported LLM provider: {self.config.provider}")

    def _api_key(self) -> str | None:
        if self.config.api_key_env is None:
            return None
        value = os.environ.get(self.config.api_key_env)
        if not value:
            raise ValueError(f"missing API key environment variable: {self.config.api_key_env}")
        return value

    def _generate_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict,
    ) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("install the 'llm' extra to use OpenAI or LiteLLM") from exc
        client = OpenAI(
            api_key=self._api_key(),
            base_url=self.config.base_url,
            timeout=self.config.timeout_seconds,
        )
        response = client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_output_tokens,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "semantic_judge_result",
                    "strict": True,
                    "schema": schema,
                },
            },
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("OpenAI-compatible provider returned an empty response")
        return content

    def _generate_claude(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict,
    ) -> dict:
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise RuntimeError("install the 'llm' extra to use Claude") from exc
        kwargs: dict[str, Any] = {
            "api_key": self._api_key(),
            "timeout": self.config.timeout_seconds,
        }
        if self.config.base_url is not None:
            kwargs["base_url"] = self.config.base_url
        client = Anthropic(**kwargs)
        response = client.messages.create(
            model=self.config.model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=self.config.temperature,
            max_tokens=self.config.max_output_tokens,
            tools=[
                {
                    "name": "return_semantic_judgment",
                    "description": "Return criterion-level semantic grading.",
                    "input_schema": schema,
                }
            ],
            tool_choice={"type": "tool", "name": "return_semantic_judgment"},
        )
        for block in response.content:
            if getattr(block, "type", None) == "tool_use":
                return block.input
        raise ValueError("Claude did not return the required tool result")

    def _generate_ollama(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict,
    ) -> str:
        try:
            from ollama import Client
        except ImportError as exc:
            raise RuntimeError("install the 'llm' extra to use Ollama") from exc
        client = Client(host=self.config.base_url, timeout=self.config.timeout_seconds)
        response = client.chat(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            format=schema,
            options={
                "temperature": self.config.temperature,
                "num_predict": self.config.max_output_tokens,
            },
        )
        message = response["message"] if isinstance(response, dict) else response.message
        content = message["content"] if isinstance(message, dict) else message.content
        if not content:
            raise ValueError("Ollama returned an empty response")
        return content
