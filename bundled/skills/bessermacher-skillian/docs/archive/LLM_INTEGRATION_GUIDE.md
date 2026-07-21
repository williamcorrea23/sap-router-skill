# LLM Integration Guide

This guide explains how to connect Skillian to a new LLM provider with OpenAI-compatible endpoints (regular chat and structured output).

## Architecture Overview

Skillian uses a **protocol-based factory pattern** for LLM providers:

```
Settings (config.py)
    ↓
create_llm_provider() (factory.py)
    ↓
LLMProvider Protocol Implementation
    ↓
LangChain BaseChatModel
    ↓
Agent (tool binding + conversation)
```

## Step 1: Add Configuration Settings

Edit `app/config.py` to add your new provider settings:

```python
class Settings(BaseSettings):
    # ... existing settings ...

    # LLM Provider - add your provider to the Literal
    llm_provider: Literal["ollama", "anthropic", "openai", "custom_openai"] = "ollama"

    # Custom OpenAI-compatible provider
    custom_openai_api_key: str | None = None
    custom_openai_base_url: str = "https://your-api-endpoint.com/v1"
    custom_openai_chat_model: str = "your-chat-model"
    custom_openai_structured_model: str = "your-structured-model"  # For structured output
    custom_openai_timeout: int = 60
    custom_openai_max_retries: int = 3

    @model_validator(mode="after")
    def validate_provider_config(self) -> Self:
        """Validate that required API keys are present for the selected provider."""
        # ... existing validations ...

        if self.llm_provider == "custom_openai" and not self.custom_openai_api_key:
            raise ValueError(
                "CUSTOM_OPENAI_API_KEY is required when using custom_openai provider"
            )
        return self
```

## Step 2: Create the Provider Implementation

Create `app/llm/custom_openai.py`:

```python
"""Custom OpenAI-compatible LLM provider."""

from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel


@dataclass
class CustomOpenAIProvider:
    """Provider for custom OpenAI-compatible API endpoints.

    Supports two endpoint modes:
    - Regular chat: Standard conversational responses
    - Structured output: JSON schema-constrained responses
    """

    api_key: str
    base_url: str
    chat_model: str
    structured_model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 60
    max_retries: int = 3

    def get_chat_model(self) -> BaseChatModel:
        """Return a LangChain chat model for regular conversations."""
        return ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.chat_model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

    def get_structured_model(self) -> BaseChatModel:
        """Return a LangChain chat model for structured output.

        Use this when you need JSON schema-constrained responses.
        Bind a Pydantic model using .with_structured_output() method.
        """
        return ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.structured_model,
            temperature=0.0,  # Lower temperature for consistent structured output
            max_tokens=self.max_tokens,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

    @property
    def model_name(self) -> str:
        """Return the primary model name being used."""
        return self.chat_model

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "custom_openai"
```

## Step 3: Update the Factory

Edit `app/llm/factory.py` to include the new provider:

```python
"""LLM provider factory."""

from app.config import Settings
from app.llm.protocol import LLMProvider
from app.llm.ollama import OllamaProvider
from app.llm.anthropic import AnthropicProvider
from app.llm.openai import OpenAIProvider
from app.llm.custom_openai import CustomOpenAIProvider


class LLMFactoryError(Exception):
    """Error creating LLM provider."""
    pass


def create_llm_provider(settings: Settings) -> LLMProvider:
    """Create an LLM provider based on settings."""
    match settings.llm_provider:
        case "ollama":
            return OllamaProvider(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model,
            )
        case "anthropic":
            if not settings.anthropic_api_key:
                raise LLMFactoryError(
                    "ANTHROPIC_API_KEY is required for Anthropic provider"
                )
            return AnthropicProvider(
                api_key=settings.anthropic_api_key,
                model=settings.anthropic_model,
            )
        case "openai":
            if not settings.openai_api_key:
                raise LLMFactoryError(
                    "OPENAI_API_KEY is required for OpenAI provider"
                )
            return OpenAIProvider(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
            )
        case "custom_openai":
            if not settings.custom_openai_api_key:
                raise LLMFactoryError(
                    "CUSTOM_OPENAI_API_KEY is required for custom OpenAI provider"
                )
            return CustomOpenAIProvider(
                api_key=settings.custom_openai_api_key,
                base_url=settings.custom_openai_base_url,
                chat_model=settings.custom_openai_chat_model,
                structured_model=settings.custom_openai_structured_model,
                timeout=settings.custom_openai_timeout,
                max_retries=settings.custom_openai_max_retries,
            )
        case _:
            raise LLMFactoryError(
                f"Unknown LLM provider: {settings.llm_provider}. "
                "Supported: ollama, anthropic, openai, custom_openai"
            )
```

## Step 4: Update the Protocol (Optional)

If your provider needs structured output capabilities, extend the protocol in `app/llm/protocol.py`:

```python
from typing import Protocol, runtime_checkable

from langchain_core.language_models import BaseChatModel


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol for LLM providers."""

    def get_chat_model(self) -> BaseChatModel:
        """Return a LangChain chat model instance."""
        ...

    @property
    def model_name(self) -> str:
        """Return the model name being used."""
        ...

    @property
    def provider_name(self) -> str:
        """Return the provider name (ollama, anthropic, openai, custom_openai)."""
        ...


@runtime_checkable
class StructuredOutputProvider(Protocol):
    """Extended protocol for providers supporting structured output."""

    def get_structured_model(self) -> BaseChatModel:
        """Return a model configured for structured JSON output."""
        ...
```

## Step 5: Export the Provider

Update `app/llm/__init__.py`:

```python
"""LLM providers module."""

from app.llm.protocol import LLMProvider, StructuredOutputProvider
from app.llm.factory import create_llm_provider, LLMFactoryError
from app.llm.ollama import OllamaProvider
from app.llm.anthropic import AnthropicProvider
from app.llm.openai import OpenAIProvider
from app.llm.custom_openai import CustomOpenAIProvider

__all__ = [
    "LLMProvider",
    "StructuredOutputProvider",
    "create_llm_provider",
    "LLMFactoryError",
    "OllamaProvider",
    "AnthropicProvider",
    "OpenAIProvider",
    "CustomOpenAIProvider",
]
```

## Step 6: Configure Environment Variables

Create or update your `.env` file:

```bash
# .env
ENV=production
DEBUG=false

# LLM Provider Selection
LLM_PROVIDER=custom_openai

# Custom OpenAI-compatible Provider
CUSTOM_OPENAI_API_KEY=your-api-key-here
CUSTOM_OPENAI_BASE_URL=https://your-api-endpoint.com/v1
CUSTOM_OPENAI_CHAT_MODEL=your-chat-model-name
CUSTOM_OPENAI_STRUCTURED_MODEL=your-structured-model-name
CUSTOM_OPENAI_TIMEOUT=60
CUSTOM_OPENAI_MAX_RETRIES=3

# Database (keep your existing config)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/skillian
BUSINESS_DATABASE_URL=postgresql://user:pass@host:5432/business_db
VECTOR_COLLECTION_NAME=skillian_knowledge
```

## Using Structured Output

The structured output model is useful when you need guaranteed JSON responses. Here's how to use it:

```python
from pydantic import BaseModel, Field
from app.dependencies import get_llm_provider
from app.llm.custom_openai import CustomOpenAIProvider


class AnalysisResult(BaseModel):
    """Structured output schema for data analysis."""

    summary: str = Field(description="Brief summary of findings")
    issues_found: list[str] = Field(description="List of identified issues")
    severity: str = Field(description="Overall severity: low, medium, high")
    recommendations: list[str] = Field(description="Recommended actions")


async def analyze_with_structure(data: dict) -> AnalysisResult:
    """Example of using structured output."""
    provider = get_llm_provider()

    # Check if provider supports structured output
    if isinstance(provider, CustomOpenAIProvider):
        model = provider.get_structured_model()

        # Bind the Pydantic schema for structured output
        structured_model = model.with_structured_output(AnalysisResult)

        response = await structured_model.ainvoke(
            f"Analyze this data and provide findings: {data}"
        )

        return response  # Returns AnalysisResult instance
    else:
        # Fallback for providers without structured output
        model = provider.get_chat_model()
        # ... handle manually
```

## Adding Structured Output to Dependencies

If you want structured output available via dependency injection, update `app/dependencies.py`:

```python
from langchain_core.language_models import BaseChatModel
from app.llm.custom_openai import CustomOpenAIProvider


def get_structured_model() -> BaseChatModel | None:
    """Get structured output model if provider supports it."""
    provider = get_llm_provider()

    if isinstance(provider, CustomOpenAIProvider):
        return provider.get_structured_model()

    return None
```

## Testing the Integration

Create a test file `tests/test_custom_openai.py`:

```python
"""Tests for custom OpenAI provider."""

import pytest
from unittest.mock import patch, MagicMock

from app.llm.custom_openai import CustomOpenAIProvider
from app.config import Settings


@pytest.fixture
def custom_provider():
    """Create a test provider instance."""
    return CustomOpenAIProvider(
        api_key="test-key",
        base_url="https://test-api.example.com/v1",
        chat_model="test-chat-model",
        structured_model="test-structured-model",
    )


def test_provider_properties(custom_provider):
    """Test provider property methods."""
    assert custom_provider.provider_name == "custom_openai"
    assert custom_provider.model_name == "test-chat-model"


def test_get_chat_model(custom_provider):
    """Test chat model creation."""
    with patch("app.llm.custom_openai.ChatOpenAI") as mock_chat:
        mock_chat.return_value = MagicMock()

        model = custom_provider.get_chat_model()

        mock_chat.assert_called_once_with(
            api_key="test-key",
            base_url="https://test-api.example.com/v1",
            model="test-chat-model",
            temperature=0.7,
            max_tokens=4096,
            timeout=60,
            max_retries=3,
        )


def test_get_structured_model(custom_provider):
    """Test structured output model creation."""
    with patch("app.llm.custom_openai.ChatOpenAI") as mock_chat:
        mock_chat.return_value = MagicMock()

        model = custom_provider.get_structured_model()

        # Verify lower temperature for structured output
        mock_chat.assert_called_once()
        call_kwargs = mock_chat.call_args.kwargs
        assert call_kwargs["temperature"] == 0.0
        assert call_kwargs["model"] == "test-structured-model"


def test_factory_creates_custom_provider():
    """Test factory creates custom provider with correct settings."""
    from app.llm.factory import create_llm_provider

    settings = Settings(
        llm_provider="custom_openai",
        custom_openai_api_key="test-key",
        custom_openai_base_url="https://api.example.com/v1",
        custom_openai_chat_model="chat-model",
        custom_openai_structured_model="structured-model",
    )

    with patch("app.llm.custom_openai.ChatOpenAI"):
        provider = create_llm_provider(settings)

        assert isinstance(provider, CustomOpenAIProvider)
        assert provider.api_key == "test-key"
```

## Verification Checklist

After integration, verify:

- [ ] Application starts without errors: `uv run python main.py`
- [ ] LLM provider logs correctly on startup
- [ ] Chat endpoint works: `POST /api/v1/chat`
- [ ] Tools are bound and callable
- [ ] Structured output returns valid Pydantic models
- [ ] Error handling works for API failures

## Troubleshooting

### Connection Errors

```python
# Add retry logic in the provider
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def invoke_with_retry(model, messages):
    return await model.ainvoke(messages)
```

### API Key Issues

Ensure your API key is properly set:

```bash
# Verify environment variable
echo $CUSTOM_OPENAI_API_KEY

# Or check in Python
from app.config import get_settings
settings = get_settings()
print(f"API Key set: {bool(settings.custom_openai_api_key)}")
```

### Model Not Found

Verify your model names match what the API expects:

```bash
# Test the endpoint directly
curl -X POST "https://your-api-endpoint.com/v1/chat/completions" \
  -H "Authorization: Bearer $CUSTOM_OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "your-chat-model", "messages": [{"role": "user", "content": "Hello"}]}'
```
