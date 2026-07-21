"""Ollama LLM provider for local development."""

from dataclasses import dataclass

from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama


@dataclass
class OllamaProvider:
    """Ollama provider for local LLM inference."""

    base_url: str
    model: str
    temperature: float = 0.1

    def get_chat_model(self) -> BaseChatModel:
        """Return Ollama chat model."""
        return ChatOllama(
            base_url=self.base_url,
            model=self.model,
            temperature=self.temperature,
        )

    @property
    def model_name(self) -> str:
        return self.model

    @property
    def provider_name(self) -> str:
        return "ollama"
