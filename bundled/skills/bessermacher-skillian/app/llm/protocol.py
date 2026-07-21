"""LLM provider protocol definition."""

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
