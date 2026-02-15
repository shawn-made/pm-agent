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

    def test_create_ollama_raises(self):
        with pytest.raises(ValueError, match="not yet implemented"):
            create_client(Provider.OLLAMA)

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
        assert call_kwargs["messages"] == [
            {"role": "user", "content": "User input."}
        ]

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

        # Mock the Gemini API response
        mock_response = MagicMock()
        mock_response.text = "Gemini response text."

        with patch("google.generativeai.GenerativeModel") as MockModel:
            mock_model_instance = MagicMock()
            mock_model_instance.generate_content_async = AsyncMock(
                return_value=mock_response
            )
            MockModel.return_value = mock_model_instance

            result = await client.call(
                system_prompt="You are a PM assistant.",
                user_prompt="Summarize these notes.",
            )

            assert result == "Gemini response text."

    @patch.dict("os.environ", {"GOOGLE_AI_API_KEY": "test-key"})
    def test_estimate_tokens(self):
        from app.services.llm_gemini import GeminiClient

        client = GeminiClient()
        # Gemini uses ~4 chars/token
        assert client.estimate_tokens("a" * 40) == 10
        assert client.estimate_tokens("") == 1
