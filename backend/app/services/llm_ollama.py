"""VPMA LLM Client — Ollama (Local LLM) Adapter."""

import os
import shutil
import subprocess  # nosec B404 — used only for hardcoded 'ollama serve' command

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


def check_ollama_installed() -> dict:
    """Check if the Ollama binary is installed on the system.

    Returns:
        Dict with 'installed' (bool) and 'path' (str or None).
    """
    path = shutil.which("ollama")
    return {
        "installed": path is not None,
        "path": path,
    }


async def get_ollama_info(base_url: str | None = None) -> dict:
    """Get comprehensive Ollama status: installed, running, models.

    Returns:
        Dict with 'installed' (bool), 'install_path' (str|None),
        'running' (bool), 'models' (list), 'error' (str|None).
    """
    install_info = check_ollama_installed()
    status = await check_ollama_status(base_url)

    return {
        "installed": install_info["installed"],
        "install_path": install_info["path"],
        "running": status["available"],
        "models": status["models"],
        "error": status["error"],
    }


def start_ollama_serve(base_url: str | None = None) -> dict:
    """Start Ollama server as a detached subprocess.

    Returns:
        Dict with 'started' (bool) and 'error' (str|None).
    """
    install_info = check_ollama_installed()
    if not install_info["installed"]:
        return {
            "started": False,
            "error": "Ollama is not installed. Download it from https://ollama.com",
        }

    try:
        # Start ollama serve as a detached process (not tracked by VPMA)
        subprocess.Popen(  # nosec B603 B607 — hardcoded command, no user input
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return {
            "started": True,
            "error": None,
        }
    except Exception as e:
        return {
            "started": False,
            "error": f"Failed to start Ollama: {e}",
        }
