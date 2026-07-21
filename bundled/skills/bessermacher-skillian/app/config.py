"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import Literal, Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    app_name: str = "Skillian"
    app_version: str = "0.1.0"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # LLM Provider
    llm_provider: Literal["ollama", "anthropic", "openai", "custom_openai"] = "ollama"
    llm_temperature: float = 0.1
    llm_timeout: float = 120.0  # seconds for LLM call timeout
    tool_timeout: float = 60.0  # seconds for individual tool execution timeout
    max_iterations: int = 15  # max agent loop iterations

    # Embedding model override (None = provider default)
    embedding_model: str | None = None

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Anthropic (for production)
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-20250514"

    # OpenAI (optional)
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"

    # Custom OpenAI-compatible provider
    custom_openai_api_key: str | None = None
    custom_openai_base_url: str = "https://your-api-endpoint.com/v1"
    custom_openai_model: str = "your-model"
    custom_openai_timeout: int = 60
    custom_openai_max_retries: int = 3

    # Vector Store (uses database_url for pgvector)
    vector_collection_name: str = "skillian_knowledge"

    # Database
    database_url: str = "postgresql+asyncpg://skillian:skillian@localhost:5432/skillian"

    # Business Database (SAP BW data) — leave empty to disable
    business_database_url: str = ""

    # SAP Datasphere (hdbcli)
    datasphere_host: str | None = None
    datasphere_port: int = 443
    datasphere_space: str = "BW2AI"
    datasphere_user: str | None = None
    datasphere_password: str | None = None
    datasphere_encrypt: bool = True
    datasphere_ssl_validate_certificate: bool = True
    datasphere_timeout: int = 60
    datasphere_pool_size: int = 4

    @property
    def is_development(self) -> bool:
        return self.env == "development"

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    _PROVIDER_API_KEYS: dict[str, str] = {
        "anthropic": "anthropic_api_key",
        "openai": "openai_api_key",
        "custom_openai": "custom_openai_api_key",
    }

    @model_validator(mode="after")
    def validate_provider_config(self) -> Self:
        """Validate that required API keys are present for the selected provider."""
        key_field = self._PROVIDER_API_KEYS.get(self.llm_provider)
        if key_field and not getattr(self, key_field):
            raise ValueError(
                f"{key_field.upper()} is required when LLM_PROVIDER={self.llm_provider}"
            )
        return self

    @model_validator(mode="after")
    def validate_datasphere_config(self) -> Self:
        """Validate Datasphere config when connector is needed."""
        if self.datasphere_host and not all(
            [
                self.datasphere_user,
                self.datasphere_password,
            ]
        ):
            raise ValueError(
                "DATASPHERE_USER and DATASPHERE_PASSWORD are required when DATASPHERE_HOST is set"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
