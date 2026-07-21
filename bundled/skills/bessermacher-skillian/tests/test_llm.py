"""Tests for LLM module."""

import pytest

from app.config import Settings
from app.llm import LLMFactoryError, create_llm_provider
from app.llm.anthropic import AnthropicProvider
from app.llm.ollama import OllamaProvider


class TestLLMFactory:
    def test_create_ollama_provider(self):
        settings = Settings(llm_provider="ollama")
        provider = create_llm_provider(settings)

        assert isinstance(provider, OllamaProvider)
        assert provider.provider_name == "ollama"

    def test_create_anthropic_provider(self):
        settings = Settings(
            llm_provider="anthropic",
            anthropic_api_key="test-key",
        )
        provider = create_llm_provider(settings)

        assert isinstance(provider, AnthropicProvider)
        assert provider.provider_name == "anthropic"

    def test_anthropic_requires_api_key(self):
        # Validation now happens at Settings level, not factory
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is required"):
            Settings(llm_provider="anthropic", anthropic_api_key=None)

    def test_unknown_provider_raises(self):
        settings = Settings()
        settings.llm_provider = "unknown"  # type: ignore

        with pytest.raises(LLMFactoryError):
            create_llm_provider(settings)


class TestOllamaProvider:
    def test_properties(self):
        provider = OllamaProvider(
            base_url="http://localhost:11434",
            model="llama3.2",
        )

        assert provider.provider_name == "ollama"
        assert provider.model_name == "llama3.2"

    def test_get_chat_model(self):
        provider = OllamaProvider(
            base_url="http://localhost:11434",
            model="llama3.2",
        )

        model = provider.get_chat_model()
        assert model is not None
