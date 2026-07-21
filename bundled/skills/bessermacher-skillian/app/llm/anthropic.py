"""Anthropic Claude LLM provider for production."""

from dataclasses import dataclass

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel


@dataclass
class AnthropicProvider:
    """Anthropic Claude provider."""

    api_key: str
    model: str = "claude-sonnet-4-20250514"
    temperature: float = 0.1
    max_tokens: int = 4096

    def get_chat_model(self) -> BaseChatModel:
        """Return Anthropic chat model."""
        return ChatAnthropic(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

    @property
    def model_name(self) -> str:
        return self.model

    @property
    def provider_name(self) -> str:
        return "anthropic"
