"""OpenAI LLM provider (optional alternative)."""

from dataclasses import dataclass

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI


@dataclass
class OpenAIProvider:
    """OpenAI provider."""

    api_key: str
    model: str = "gpt-4o"
    temperature: float = 0.1

    def get_chat_model(self) -> BaseChatModel:
        """Return OpenAI chat model."""
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
        )

    @property
    def model_name(self) -> str:
        return self.model

    @property
    def provider_name(self) -> str:
        return "openai"
