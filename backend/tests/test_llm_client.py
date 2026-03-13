"""Tests for VPMA LLM Client — Base interface (Task 6), Claude (Task 7), Gemini (Task 8)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.llm_client import (
    LLMClient,
    LLMError,
    Provider,
    _retry_with_backoff,
    create_client,
)

# ============================================================
# TASK 6: BASE ABSTRACT INTERFACE
# ============================================================


class TestProvider:
    def test_provider_values(self):
        assert Provider.CLAUDE == "claude"
        assert Provider.GEMINI == "gemini"
        assert Provider.OLLAMA == "ollama"

    def test_provider_from_string(self):
        assert Provider("claude") == Provider.CLAUDE
        assert Provider("gemini") == Provider.GEMINI


class TestLLMClient:
    def test_cannot_instantiate_abstract(self):
        """LLMClient cannot be instantiated directly."""
        with pytest.raises(TypeError):
            LLMClient()

    def test_estimate_tokens(self):
        """Token estimation uses ~4 chars per token."""

        class DummyClient(LLMClient):
            provider = Provider.CLAUDE

            async def call(self, system_prompt, user_prompt, max_tokens=4096):
                return ""

        client = DummyClient()
        assert client.estimate_tokens("Hello world!") == 3  # 12 chars / 4
        assert client.estimate_tokens("") == 1  # minimum 1
        assert client.estimate_tokens("a" * 400) == 100


class TestRetryWithBackoff:
    @pytest.mark.asyncio
    async def test_success_first_try(self):
        func = AsyncMock(return_value="success")
        result = await _retry_with_backoff(func, base_delay=0.01)
        assert result == "success"
        assert func.call_count == 1

    @pytest.mark.asyncio
    async def test_success_after_retries(self):
        func = AsyncMock(side_effect=[Exception("fail"), Exception("fail"), "success"])
        result = await _retry_with_backoff(func, max_retries=3, base_delay=0.01)
        assert result == "success"
        assert func.call_count == 3

    @pytest.mark.asyncio
    async def test_all_retries_exhausted(self):
        func = AsyncMock(side_effect=Exception("persistent failure"))
        with pytest.raises(LLMError, match="persistent failure"):
            await _retry_with_backoff(func, max_retries=3, base_delay=0.01)
        assert func.call_count == 3

    @pytest.mark.asyncio
    async def test_custom_retry_count(self):
        func = AsyncMock(side_effect=Exception("fail"))
        with pytest.raises(LLMError):
            await _retry_with_backoff(func, max_retries=2, base_delay=0.01)
        assert func.call_count == 2


class TestCreateClient:
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_create_claude_client(self):
        client = create_client(Provider.CLAUDE)
        assert client.provider == Provider.CLAUDE

    @patch.dict("os.environ", {"GOOGLE_AI_API_KEY": "test-key"})
    def test_create_gemini_client(self):
        client = create_client(Provider.GEMINI)
        assert client.provider == Provider.GEMINI

    def test_create_ollama_client(self):
        client = create_client(Provider.OLLAMA)
        assert client.provider == Provider.OLLAMA

    def test_create_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown provider"):
            create_client("nonexistent")


# ============================================================
# TASK 7: CLAUDE ADAPTER
# ============================================================


class TestClaudeClient:
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": ""})
    def test_missing_api_key_raises(self):
        from app.services.llm_claude import ClaudeClient

        with pytest.raises(LLMError, match="API key not configured"):
            ClaudeClient()

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key-123"})
    def test_creates_with_env_key(self):
        from app.services.llm_claude import ClaudeClient

        client = ClaudeClient()
        assert client.api_key == "test-key-123"
        assert client.provider == Provider.CLAUDE

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "default-key"})
    def test_explicit_key_overrides_env(self):
        from app.services.llm_claude import ClaudeClient

        client = ClaudeClient(api_key="explicit-key")
        assert client.api_key == "explicit-key"

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_default_model(self):
        from app.services.llm_claude import DEFAULT_MODEL, ClaudeClient

        client = ClaudeClient()
        assert client.model == DEFAULT_MODEL

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_custom_model(self):
        from app.services.llm_claude import ClaudeClient

        client = ClaudeClient(model="claude-opus-4-6")
        assert client.model == "claude-opus-4-6"

    @pytest.mark.asyncio
    async def test_call_returns_text(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        from app.services.llm_claude import ClaudeClient

        client = ClaudeClient()

        # Mock the Anthropic API response
        mock_content = MagicMock()
        mock_content.text = "This is the LLM response."
        mock_response = MagicMock()
        mock_response.content = [mock_content]

        client._client.messages.create = AsyncMock(return_value=mock_response)

        result = await client.call(
            system_prompt="You are a PM assistant.",
            user_prompt="Summarize these notes.",
        )

        assert result == "This is the LLM response."
        client._client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_passes_correct_params(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        from app.services.llm_claude import ClaudeClient

        client = ClaudeClient(model="claude-sonnet-4-5-20250929")

        mock_content = MagicMock()
        mock_content.text = "response"
        mock_response = MagicMock()
        mock_response.content = [mock_content]

        client._client.messages.create = AsyncMock(return_value=mock_response)

        await client.call(
            system_prompt="System instructions.",
            user_prompt="User input.",
            max_tokens=2048,
        )

        call_kwargs = client._client.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-sonnet-4-5-20250929"
        assert call_kwargs["max_tokens"] == 2048
        assert call_kwargs["system"] == "System instructions."
        assert call_kwargs["messages"] == [{"role": "user", "content": "User input."}]

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_estimate_tokens(self):
        from app.services.llm_claude import ClaudeClient

        client = ClaudeClient()
        # Claude uses ~3.5 chars/token
        assert client.estimate_tokens("a" * 35) == 10
        assert client.estimate_tokens("") == 1


# ============================================================
# TASK 8: GEMINI ADAPTER
# ============================================================


class TestGeminiClient:
    @patch.dict("os.environ", {"GOOGLE_AI_API_KEY": ""})
    def test_missing_api_key_raises(self):
        from app.services.llm_gemini import GeminiClient

        with pytest.raises(LLMError, match="API key not configured"):
            GeminiClient()

    @patch.dict("os.environ", {"GOOGLE_AI_API_KEY": "test-key-456"})
    def test_creates_with_env_key(self):
        from app.services.llm_gemini import GeminiClient

        client = GeminiClient()
        assert client.api_key == "test-key-456"
        assert client.provider == Provider.GEMINI

    @patch.dict("os.environ", {"GOOGLE_AI_API_KEY": "default-key"})
    def test_explicit_key_overrides_env(self):
        from app.services.llm_gemini import GeminiClient

        client = GeminiClient(api_key="explicit-key")
        assert client.api_key == "explicit-key"

    @patch.dict("os.environ", {"GOOGLE_AI_API_KEY": "test-key"})
    def test_default_model(self):
        from app.services.llm_gemini import DEFAULT_MODEL, GeminiClient

        client = GeminiClient()
        assert client.model == DEFAULT_MODEL

    @patch.dict("os.environ", {"GOOGLE_AI_API_KEY": "test-key"})
    def test_custom_model(self):
        from app.services.llm_gemini import GeminiClient

        client = GeminiClient(model="gemini-2.0-pro")
        assert client.model == "gemini-2.0-pro"

    @pytest.mark.asyncio
    async def test_call_returns_text(self, monkeypatch):
        monkeypatch.setenv("GOOGLE_AI_API_KEY", "test-key")
        from app.services.llm_gemini import GeminiClient

        client = GeminiClient()

        # Mock the new google-genai async response
        mock_response = MagicMock()
        mock_response.text = "Gemini response text."

        mock_generate = AsyncMock(return_value=mock_response)
        client._client.aio.models.generate_content = mock_generate

        result = await client.call(
            system_prompt="You are a PM assistant.",
            user_prompt="Summarize these notes.",
        )

        assert result == "Gemini response text."
        mock_generate.assert_called_once()

    @patch.dict("os.environ", {"GOOGLE_AI_API_KEY": "test-key"})
    def test_estimate_tokens(self):
        from app.services.llm_gemini import GeminiClient

        client = GeminiClient()
        # Gemini uses ~4 chars/token
        assert client.estimate_tokens("a" * 40) == 10
        assert client.estimate_tokens("") == 1


# ============================================================
# TASK 38: OLLAMA ADAPTER
# ============================================================


class TestOllamaClient:
    def test_creates_with_defaults(self):
        from app.services.llm_ollama import DEFAULT_BASE_URL, DEFAULT_MODEL, OllamaClient

        client = OllamaClient()
        assert client.base_url == DEFAULT_BASE_URL
        assert client.model == DEFAULT_MODEL
        assert client.provider == Provider.OLLAMA

    def test_creates_with_explicit_config(self):
        from app.services.llm_ollama import OllamaClient

        client = OllamaClient(base_url="http://myhost:11434", model="mistral")
        assert client.base_url == "http://myhost:11434"
        assert client.model == "mistral"

    @patch.dict("os.environ", {"OLLAMA_BASE_URL": "http://env-host:11434", "OLLAMA_MODEL": "phi3"})
    def test_creates_with_env_vars(self):
        from app.services.llm_ollama import OllamaClient

        client = OllamaClient()
        assert client.base_url == "http://env-host:11434"
        assert client.model == "phi3"

    def test_explicit_overrides_env(self):
        from app.services.llm_ollama import OllamaClient

        client = OllamaClient(base_url="http://explicit:11434", model="llama3.1")
        assert client.base_url == "http://explicit:11434"
        assert client.model == "llama3.1"

    def test_strips_trailing_slash(self):
        from app.services.llm_ollama import OllamaClient

        client = OllamaClient(base_url="http://localhost:11434/")
        assert client.base_url == "http://localhost:11434"

    @pytest.mark.asyncio
    async def test_call_returns_text(self):
        from app.services.llm_ollama import OllamaClient

        client = OllamaClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Ollama response text."}

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            result = await client.call(
                system_prompt="You are a PM assistant.",
                user_prompt="Summarize these notes.",
            )

        assert result == "Ollama response text."

    @pytest.mark.asyncio
    async def test_call_passes_correct_params(self):
        from app.services.llm_ollama import OllamaClient

        client = OllamaClient(base_url="http://test:11434", model="llama3.2")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "response"}

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            await client.call(
                system_prompt="System instructions.",
                user_prompt="User input.",
                max_tokens=2048,
            )

            call_args = mock_instance.post.call_args
            assert call_args[0][0] == "http://test:11434/api/generate"
            payload = call_args[1]["json"]
            assert payload["model"] == "llama3.2"
            assert payload["system"] == "System instructions."
            assert payload["prompt"] == "User input."
            assert payload["stream"] is False
            assert payload["options"]["num_predict"] == 2048

    @pytest.mark.asyncio
    async def test_call_raises_on_http_error(self):
        from app.services.llm_ollama import OllamaClient

        client = OllamaClient()

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            with pytest.raises(LLMError, match="Ollama API error"):
                await client.call("system", "prompt")

    @pytest.mark.asyncio
    async def test_call_raises_on_empty_response(self):
        from app.services.llm_ollama import OllamaClient

        client = OllamaClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": ""}

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            with pytest.raises(LLMError, match="empty response"):
                await client.call("system", "prompt")

    def test_estimate_tokens(self):
        from app.services.llm_ollama import OllamaClient

        client = OllamaClient()
        # Ollama uses ~4 chars/token (same as Gemini)
        assert client.estimate_tokens("a" * 40) == 10
        assert client.estimate_tokens("") == 1


class TestCheckOllamaStatus:
    @pytest.mark.asyncio
    async def test_returns_available_with_models(self):
        from app.services.llm_ollama import check_ollama_status

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "llama3.2"}, {"name": "mistral"}]}

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            result = await check_ollama_status()

        assert result["available"] is True
        assert result["models"] == ["llama3.2", "mistral"]
        assert result["error"] is None

    @pytest.mark.asyncio
    async def test_returns_unavailable_on_connect_error(self):
        import httpx as httpx_module
        from app.services.llm_ollama import check_ollama_status

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.get.side_effect = httpx_module.ConnectError("Connection refused")
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            result = await check_ollama_status()

        assert result["available"] is False
        assert "Cannot connect" in result["error"]

    @pytest.mark.asyncio
    async def test_returns_unavailable_on_timeout(self):
        import httpx as httpx_module
        from app.services.llm_ollama import check_ollama_status

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.get.side_effect = httpx_module.TimeoutException("timeout")
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            result = await check_ollama_status()

        assert result["available"] is False
        assert "timed out" in result["error"]

    @pytest.mark.asyncio
    async def test_uses_custom_base_url(self):
        from app.services.llm_ollama import check_ollama_status

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_instance

            result = await check_ollama_status("http://custom:11434")

        assert result["available"] is True
        call_args = mock_instance.get.call_args
        assert "custom:11434" in call_args[0][0]


class TestCheckOllamaInstalled:
    def test_returns_installed_when_binary_found(self):
        from app.services.llm_ollama import check_ollama_installed

        with patch("shutil.which", return_value="/usr/local/bin/ollama"):
            result = check_ollama_installed()

        assert result["installed"] is True
        assert result["path"] == "/usr/local/bin/ollama"

    def test_returns_not_installed_when_binary_missing(self):
        from app.services.llm_ollama import check_ollama_installed

        with patch("shutil.which", return_value=None):
            result = check_ollama_installed()

        assert result["installed"] is False
        assert result["path"] is None


class TestGetOllamaInfo:
    @pytest.mark.asyncio
    async def test_returns_full_info_when_running(self):
        from app.services.llm_ollama import get_ollama_info

        with patch(
            "app.services.llm_ollama.check_ollama_installed",
            return_value={"installed": True, "path": "/usr/local/bin/ollama"},
        ):
            with patch(
                "app.services.llm_ollama.check_ollama_status",
                new_callable=AsyncMock,
                return_value={"available": True, "models": ["llama3.2"], "error": None},
            ):
                result = await get_ollama_info()

        assert result["installed"] is True
        assert result["install_path"] == "/usr/local/bin/ollama"
        assert result["running"] is True
        assert result["models"] == ["llama3.2"]
        assert result["error"] is None

    @pytest.mark.asyncio
    async def test_returns_not_installed_not_running(self):
        from app.services.llm_ollama import get_ollama_info

        with patch(
            "app.services.llm_ollama.check_ollama_installed",
            return_value={"installed": False, "path": None},
        ):
            with patch(
                "app.services.llm_ollama.check_ollama_status",
                new_callable=AsyncMock,
                return_value={"available": False, "models": [], "error": "Cannot connect"},
            ):
                result = await get_ollama_info()

        assert result["installed"] is False
        assert result["install_path"] is None
        assert result["running"] is False

    @pytest.mark.asyncio
    async def test_installed_but_not_running(self):
        from app.services.llm_ollama import get_ollama_info

        with patch(
            "app.services.llm_ollama.check_ollama_installed",
            return_value={"installed": True, "path": "/opt/homebrew/bin/ollama"},
        ):
            with patch(
                "app.services.llm_ollama.check_ollama_status",
                new_callable=AsyncMock,
                return_value={"available": False, "models": [], "error": "Cannot connect"},
            ):
                result = await get_ollama_info()

        assert result["installed"] is True
        assert result["running"] is False


class TestStartOllamaServe:
    def test_returns_error_when_not_installed(self):
        from app.services.llm_ollama import start_ollama_serve

        with patch(
            "app.services.llm_ollama.check_ollama_installed",
            return_value={"installed": False, "path": None},
        ):
            result = start_ollama_serve()

        assert result["started"] is False
        assert "not installed" in result["error"]

    def test_starts_ollama_when_installed(self):
        from app.services.llm_ollama import start_ollama_serve

        with patch(
            "app.services.llm_ollama.check_ollama_installed",
            return_value={"installed": True, "path": "/usr/local/bin/ollama"},
        ):
            with patch("subprocess.Popen") as mock_popen:
                result = start_ollama_serve()

        assert result["started"] is True
        assert result["error"] is None
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args
        assert call_args[0][0] == ["ollama", "serve"]
        assert call_args[1]["start_new_session"] is True

    def test_returns_error_on_subprocess_failure(self):
        from app.services.llm_ollama import start_ollama_serve

        with patch(
            "app.services.llm_ollama.check_ollama_installed",
            return_value={"installed": True, "path": "/usr/local/bin/ollama"},
        ):
            with patch("subprocess.Popen", side_effect=OSError("Permission denied")):
                result = start_ollama_serve()

        assert result["started"] is False
        assert "Failed to start" in result["error"]
