"""VPMA LLM Client — Abstract interface for LLM providers.

All LLM calls go through this interface. Never call provider APIs directly.
This enables Claude ⟷ Gemini ⟷ Ollama switching.

Usage:
    client = create_client(Provider.CLAUDE)
    response = await client.call(
        system_prompt="You are a PM assistant.",
        user_prompt="Summarize these meeting notes.",
    )
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class Provider(str, Enum):
    """Supported LLM providers."""

    CLAUDE = "claude"
    GEMINI = "gemini"
    OLLAMA = "ollama"  # Phase 2


class LLMError(Exception):
    """Base exception for LLM client errors."""

    pass


class LLMClient(ABC):
    """Abstract base class for LLM providers.

    All providers must implement the `call` method with the same signature.
    """

    provider: Provider

    @abstractmethod
    async def call(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> str:
        """Send a prompt to the LLM and return the response text.

        Args:
            system_prompt: Instructions for the LLM's behavior.
            user_prompt: The user's input/question.
            max_tokens: Maximum tokens in the response.

        Returns:
            The LLM's response as a string.

        Raises:
            LLMError: If the call fails after all retries.
        """
        ...

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for a text string.

        Rough approximation: ~4 characters per token for English text.
        Providers can override with more accurate counting.
        """
        return max(1, len(text) // 4)


async def _retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> str:
    """Retry an async function with exponential backoff.

    Args:
        func: Async callable that returns a string.
        max_retries: Maximum number of attempts.
        base_delay: Initial delay in seconds (doubles each retry).

    Returns:
        The function's return value.

    Raises:
        LLMError: If all retries are exhausted.
    """
    last_error: Optional[Exception] = None

    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                delay = base_delay * (2**attempt)
                logger.warning(
                    "LLM call attempt %d/%d failed: %s. Retrying in %.1fs...",
                    attempt + 1,
                    max_retries,
                    str(e),
                    delay,
                )
                await asyncio.sleep(delay)

    raise LLMError(f"LLM call failed after {max_retries} attempts: {last_error}") from last_error


def create_client(provider: Provider, **kwargs) -> LLMClient:
    """Factory: create an LLM client for the specified provider.

    Args:
        provider: Which LLM provider to use.
        **kwargs: Provider-specific configuration.

    Returns:
        An LLMClient instance ready to use.

    Raises:
        ValueError: If the provider is not supported.
    """
    if provider == Provider.CLAUDE:
        from app.services.llm_claude import ClaudeClient

        return ClaudeClient(**kwargs)

    if provider == Provider.GEMINI:
        from app.services.llm_gemini import GeminiClient

        return GeminiClient(**kwargs)

    if provider == Provider.OLLAMA:
        from app.services.llm_ollama import OllamaClient

        return OllamaClient(**kwargs)

    raise ValueError(f"Unknown provider: {provider}")
