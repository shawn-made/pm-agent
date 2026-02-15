"""VPMA LLM Client — Gemini (Google AI) Adapter."""

import os

from google import genai
from google.genai import types

from app.services.llm_client import LLMClient, LLMError, Provider, _retry_with_backoff

# Default model — Flash for fast, affordable responses
DEFAULT_MODEL = "gemini-2.0-flash"


class GeminiClient(LLMClient):
    """Google Gemini adapter implementing the LLMClient interface."""

    provider = Provider.GEMINI

    def __init__(self, api_key: str | None = None, model: str | None = None):
        """Initialize Gemini client.

        Args:
            api_key: Google AI API key. Falls back to GOOGLE_AI_API_KEY env var.
            model: Model ID to use. Defaults to Gemini Flash.
        """
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY", "")
        self.model = model or DEFAULT_MODEL

        if not self.api_key:
            raise LLMError(
                "Google AI API key not configured. "
                "Set GOOGLE_AI_API_KEY in .env or provide via Settings."
            )

        self._client = genai.Client(api_key=self.api_key)

    async def call(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> str:
        """Send a prompt to Gemini and return the response text."""

        async def _do_call() -> str:
            response = await self._client.aio.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=max_tokens,
                ),
            )
            return response.text

        return await _retry_with_backoff(_do_call)

    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using Gemini's ~4 chars/token ratio."""
        return max(1, len(text) // 4)
