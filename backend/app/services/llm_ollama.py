"""VPMA LLM Client — Ollama (Local LLM) Adapter."""

import os

import httpx

from app.services.llm_client import LLMClient, LLMError, Provider, _retry_with_backoff

# Default configuration
DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"


class OllamaClient(LLMClient):
    """Ollama adapter implementing the LLMClient interface.

    Connects to a locally running Ollama instance via its HTTP API.
    No API key required — Ollama runs locally.
    """

    provider = Provider.OLLAMA

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
    ):
        """Initialize Ollama client.

        Args:
            base_url: Ollama server URL. Falls back to OLLAMA_BASE_URL env var,
                      then to http://localhost:11434.
            model: Model name to use. Falls back to OLLAMA_MODEL env var,
                   then to llama3.2.
        """
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "") or DEFAULT_BASE_URL
        self.model = model or os.getenv("OLLAMA_MODEL", "") or DEFAULT_MODEL

        # Strip trailing slash for consistent URL building
        self.base_url = self.base_url.rstrip("/")

    async def call(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> str:
        """Send a prompt to Ollama and return the response text."""

        async def _do_call() -> str:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "system": system_prompt,
                        "prompt": user_prompt,
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens,
                        },
                    },
                )

                if response.status_code != 200:
                    error_text = response.text[:500]
                    raise LLMError(f"Ollama API error (HTTP {response.status_code}): {error_text}")

                data = response.json()
                text = data.get("response", "")

                if not text:
                    raise LLMError(
                        "Ollama returned empty response "
                        "(model may not be loaded or prompt was too large)"
                    )

                return text

        return await _retry_with_backoff(_do_call)

    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using ~4 chars/token ratio (conservative)."""
        return max(1, len(text) // 4)


async def check_ollama_status(base_url: str | None = None) -> dict:
    """Check Ollama connectivity and list available models.

    Returns:
        Dict with 'available' (bool), 'models' (list of model names),
        and 'error' (str or None).
    """
    url = (base_url or os.getenv("OLLAMA_BASE_URL", "") or DEFAULT_BASE_URL).rstrip("/")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Check if Ollama is running
            response = await client.get(f"{url}/api/tags")

            if response.status_code != 200:
                return {
                    "available": False,
                    "models": [],
                    "error": f"Ollama returned HTTP {response.status_code}",
                }

            data = response.json()
            models = [m["name"] for m in data.get("models", [])]

            return {
                "available": True,
                "models": models,
                "error": None,
            }

    except httpx.ConnectError:
        return {
            "available": False,
            "models": [],
            "error": "Cannot connect to Ollama. Is it running?",
        }
    except httpx.TimeoutException:
        return {
            "available": False,
            "models": [],
            "error": "Connection to Ollama timed out",
        }
    except Exception as e:
        return {
            "available": False,
            "models": [],
            "error": str(e),
        }
