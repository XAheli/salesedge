"""LLM client that works with OpenRouter, OpenAI, or any OpenAI-compatible API.

Usage:
    # Set SE_LLM_API_KEY in .env, then:
    client = LLMClient()
    response = await client.complete("Analyze this deal risk...")

    # Or with structured output:
    result = await client.complete_json("Extract key entities from: ...", schema=MySchema)
"""

from __future__ import annotations

import json
from typing import Any, TypeVar, Type

import httpx
import structlog
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings

logger = structlog.get_logger(__name__)
T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """Universal LLM client compatible with OpenRouter, OpenAI, Ollama, etc."""

    def __init__(self, model_override: str | None = None):
        settings = get_settings()
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_base_url.rstrip("/")
        self.model = model_override or settings.llm_model
        self.fallback_model = settings.llm_fallback_model
        self.max_tokens = settings.llm_max_tokens
        self.temperature = settings.llm_temperature
        self.timeout = settings.llm_timeout_seconds
        self.provider = settings.llm_provider

        self._headers: dict[str, str] = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            self._headers["Authorization"] = f"Bearer {self.api_key}"
        if self.provider == "openrouter":
            self._headers["HTTP-Referer"] = "https://salesedge.app"
            self._headers["X-Title"] = "SalesEdge AI Platform"

    @property
    def is_configured(self) -> bool:
        """Check if LLM is configured (has API key or is local)."""
        if self.provider in ("local", "ollama"):
            return True
        return bool(self.api_key)

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=5))
    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> str:
        """Send a completion request and return the text response."""
        if not self.is_configured:
            logger.warning("llm.not_configured", provider=self.provider)
            return self._fallback_response(prompt)

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]

                logger.info(
                    "llm.completion",
                    model=payload["model"],
                    prompt_len=len(prompt),
                    response_len=len(content),
                    usage=data.get("usage"),
                )
                return content

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 or e.response.status_code >= 500:
                if (model or self.model) != self.fallback_model:
                    logger.warning(
                        "llm.fallback",
                        original_model=model or self.model,
                        fallback=self.fallback_model,
                    )
                    return await self.complete(
                        prompt,
                        system_prompt,
                        temperature,
                        max_tokens,
                        model=self.fallback_model,
                    )
            logger.error(
                "llm.api_error",
                status=e.response.status_code,
                body=e.response.text[:500],
            )
            return self._fallback_response(prompt)
        except Exception as e:
            logger.error("llm.error", error=str(e), type=type(e).__name__, api_key_prefix=self.api_key[:10] if self.api_key else "NONE", base_url=self.base_url)
            return self._fallback_response(prompt)

    async def complete_json(
        self,
        prompt: str,
        schema: Type[T] | None = None,
        system_prompt: str | None = None,
    ) -> dict[str, Any] | T:
        """Request structured JSON output from the LLM."""
        json_instruction = "\n\nRespond ONLY with valid JSON. No markdown, no explanation."
        if schema:
            json_instruction += (
                f"\n\nJSON schema to follow:\n"
                f"{json.dumps(schema.model_json_schema(), indent=2)}"
            )

        full_prompt = prompt + json_instruction
        raw = await self.complete(full_prompt, system_prompt)

        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)

        try:
            parsed = json.loads(cleaned)
            if schema:
                return schema.model_validate(parsed)
            return parsed
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("llm.json_parse_failed", error=str(e), raw=raw[:200])
            if schema:
                return schema.model_construct()
            return {}

    def _fallback_response(self, prompt: str) -> str:
        """Return a helpful fallback when LLM is not available."""
        return (
            "[LLM not configured] To enable AI-powered analysis, set SE_LLM_API_KEY "
            "in your .env file. Supported providers:\n"
            "- OpenRouter (recommended): Get a free key at https://openrouter.ai/keys\n"
            "- OpenAI: Set SE_LLM_PROVIDER=openai and SE_LLM_BASE_URL=https://api.openai.com/v1\n"
            "- Ollama (local): Set SE_LLM_PROVIDER=ollama and SE_LLM_BASE_URL=http://localhost:11434/v1\n"
            "- Any OpenAI-compatible API: Set SE_LLM_BASE_URL to your endpoint"
        )


def get_llm_client() -> LLMClient:
    return LLMClient()
