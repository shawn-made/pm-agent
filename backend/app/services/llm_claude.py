"""VPMA LLM Client — Claude (Anthropic) Adapter."""

import os

import anthropic

from app.services.llm_client import LLMClient, LLMError, Provider, _retry_with_backoff

# Default model — Sonnet for balanced speed/quality in MVP
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"


class ClaudeClient(LLMClient):
    """Anthropic Claude adapter implementing the LLMClient interface."""

    provider = Provider.CLAUDE

    def __init__(self, api_key: str | None = None, model: str | None = None):
        """Initialize Claude client.

        Args:
            api_key: Anthropic API key. Falls back to ANTHROPIC_API_KEY env var.
            model: Model ID to use. Defaults to Claude Sonnet.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model or DEFAULT_MODEL

        if not self.api_key:
            raise LLMError(
                "Anthropic API key not configured. "
                "Set ANTHROPIC_API_KEY in .env or provide via Settings."
            )

        self._client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def call(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> str:
        """Send a prompt to Claude and return the response text."""

        async def _do_call() -> str:
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            # Extract text from the response content blocks
            return response.content[0].text

        return await _retry_with_backoff(_do_call)

    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using Claude's ~3.5 chars/token ratio."""
        return max(1, int(len(text) / 3.5))
