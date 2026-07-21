"""LLM provider factory."""

from app.config import Settings
from app.llm.anthropic import AnthropicProvider
from app.llm.custom_openai import CustomOpenAIProvider
from app.llm.ollama import OllamaProvider
from app.llm.openai import OpenAIProvider
from app.llm.protocol import LLMProvider


class LLMFactoryError(Exception):
    """Raised when LLM factory cannot create a provider."""


def create_llm_provider(settings: Settings) -> LLMProvider:
    """Create an LLM provider based on settings."""
    match settings.llm_provider:
        case "ollama":
            return OllamaProvider(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model,
                temperature=settings.llm_temperature,
            )
        case "anthropic":
            return AnthropicProvider(
                api_key=settings.anthropic_api_key,
                model=settings.anthropic_model,
                temperature=settings.llm_temperature,
            )
        case "openai":
            return OpenAIProvider(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                temperature=settings.llm_temperature,
            )
        case "custom_openai":
            return CustomOpenAIProvider(
                api_key=settings.custom_openai_api_key,
                base_url=settings.custom_openai_base_url,
                model=settings.custom_openai_model,
                temperature=settings.llm_temperature,
                timeout=settings.custom_openai_timeout,
                max_retries=settings.custom_openai_max_retries,
            )
        case _:
            raise LLMFactoryError(f"Unknown provider: {settings.llm_provider}")
