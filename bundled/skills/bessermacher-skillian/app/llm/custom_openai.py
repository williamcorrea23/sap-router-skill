"""Custom OpenAI-compatible LLM provider."""

from dataclasses import dataclass

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI


@dataclass
class CustomOpenAIProvider:
    """Provider for custom OpenAI-compatible API endpoints."""

    api_key: str
    base_url: str
    model: str
    temperature: float = 0.1
    max_tokens: int = 4096
    timeout: int = 60
    max_retries: int = 3

    def get_chat_model(self) -> BaseChatModel:
        """Return a LangChain chat model."""
        return ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

    @property
    def model_name(self) -> str:
        return self.model

    @property
    def provider_name(self) -> str:
        return "custom_openai"
