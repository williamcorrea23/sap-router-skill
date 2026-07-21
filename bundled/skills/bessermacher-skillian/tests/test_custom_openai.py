"""Tests for custom OpenAI provider."""

from unittest.mock import MagicMock, patch

import pytest

from app.llm.custom_openai import CustomOpenAIProvider


@pytest.fixture
def custom_provider():
    """Create a test provider instance."""
    return CustomOpenAIProvider(
        api_key="test-key",
        base_url="https://test-api.example.com/v1",
        model="test-model",
    )


def test_provider_properties(custom_provider):
    """Test provider property methods."""
    assert custom_provider.provider_name == "custom_openai"
    assert custom_provider.model_name == "test-model"


def test_get_chat_model(custom_provider):
    """Test chat model creation."""
    with patch("app.llm.custom_openai.ChatOpenAI") as mock_chat:
        mock_chat.return_value = MagicMock()

        custom_provider.get_chat_model()

        mock_chat.assert_called_once_with(
            api_key="test-key",
            base_url="https://test-api.example.com/v1",
            model="test-model",
            temperature=0.1,
            max_tokens=4096,
            timeout=60,
            max_retries=3,
        )


def test_factory_creates_custom_provider():
    """Test factory creates custom provider with correct settings."""
    from app.config import Settings
    from app.llm.factory import create_llm_provider

    settings = Settings(
        llm_provider="custom_openai",
        custom_openai_api_key="test-key",
        custom_openai_base_url="https://api.example.com/v1",
        custom_openai_model="test-model",
    )

    with patch("app.llm.custom_openai.ChatOpenAI"):
        provider = create_llm_provider(settings)

        assert isinstance(provider, CustomOpenAIProvider)
        assert provider.api_key == "test-key"
