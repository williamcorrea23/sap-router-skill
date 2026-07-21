"""Embeddings factory for different providers."""

import logging
from typing import Literal

from langchain_core.embeddings import Embeddings

from app.config import Settings

logger = logging.getLogger(__name__)

EmbeddingsType = Literal["ollama", "openai"]

_DEFAULT_OLLAMA_MODEL = "nomic-embed-text"
_DEFAULT_OPENAI_MODEL = "text-embedding-3-small"


class EmbeddingsFactoryError(Exception):
    """Raised when embeddings cannot be created."""


def create_embeddings(settings: Settings) -> Embeddings:
    """Create embeddings based on settings.

    Uses the same provider as the LLM for consistency.
    Falls back to Ollama embeddings for providers without native embeddings.

    Args:
        settings: Application settings.

    Returns:
        Configured embeddings instance.
    """
    match settings.llm_provider:
        case "ollama":
            from langchain_ollama import OllamaEmbeddings

            model = settings.embedding_model or _DEFAULT_OLLAMA_MODEL
            return OllamaEmbeddings(
                base_url=settings.ollama_base_url,
                model=model,
            )

        case "openai":
            if not settings.openai_api_key:
                raise EmbeddingsFactoryError("OPENAI_API_KEY required for OpenAI embeddings")
            from langchain_openai import OpenAIEmbeddings

            model = settings.embedding_model or _DEFAULT_OPENAI_MODEL
            return OpenAIEmbeddings(
                api_key=settings.openai_api_key,
                model=model,
            )

        case "anthropic":
            # Anthropic doesn't have embeddings — fall back to Ollama.
            try:
                from langchain_ollama import OllamaEmbeddings

                model = settings.embedding_model or _DEFAULT_OLLAMA_MODEL
                logger.info(
                    "Anthropic has no embeddings API; falling back to Ollama "
                    "(base_url=%s, model=%s)",
                    settings.ollama_base_url,
                    model,
                )
                return OllamaEmbeddings(
                    base_url=settings.ollama_base_url,
                    model=model,
                )
            except ImportError as e:
                raise EmbeddingsFactoryError(
                    "langchain-ollama is required for Anthropic fallback embeddings. "
                    "Install it with: pip install langchain-ollama"
                ) from e

        case "custom_openai":
            if not settings.custom_openai_api_key:
                raise EmbeddingsFactoryError(
                    "CUSTOM_OPENAI_API_KEY required for custom OpenAI embeddings"
                )
            from langchain_openai import OpenAIEmbeddings

            model = settings.embedding_model or "text-embedding-3-small"
            return OpenAIEmbeddings(
                api_key=settings.custom_openai_api_key,
                openai_api_base=settings.custom_openai_base_url,
                model=model,
            )

        case _:
            raise EmbeddingsFactoryError(
                f"Unknown provider for embeddings: {settings.llm_provider}"
            )
