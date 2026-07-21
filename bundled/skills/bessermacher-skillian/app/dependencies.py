"""FastAPI dependency injection."""

from collections.abc import AsyncGenerator
from functools import lru_cache
from pathlib import Path

from langchain_core.language_models import BaseChatModel

from app.api.sessions import SessionStore
from app.config import get_settings
from app.connectors.datasphere import DatasphereConnector
from app.connectors.postgres import PostgresConnector
from app.core import Agent, SkillRegistry
from app.core.skill_loader import SkillLoader
from app.db.connection import get_db_session
from app.llm import LLMProvider, create_llm_provider
from app.rag import RAGManager, VectorStore, create_embeddings


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Get cached LLM provider instance."""
    settings = get_settings()
    return create_llm_provider(settings)


def get_chat_model() -> BaseChatModel:
    """Get LangChain chat model for dependency injection."""
    provider = get_llm_provider()
    return provider.get_chat_model()


@lru_cache
def get_business_connector() -> PostgresConnector | None:
    """Get cached PostgreSQL connector for business data, or None if not configured."""
    settings = get_settings()
    if not settings.business_database_url:
        return None
    return PostgresConnector(settings.business_database_url)


@lru_cache
def get_datasphere_connector() -> DatasphereConnector | None:
    """Get cached Datasphere connector if configured."""
    settings = get_settings()

    if not settings.datasphere_host:
        return None

    return DatasphereConnector(
        host=settings.datasphere_host,
        user=settings.datasphere_user,
        password=settings.datasphere_password,
        port=settings.datasphere_port,
        encrypt=settings.datasphere_encrypt,
        ssl_validate_certificate=settings.datasphere_ssl_validate_certificate,
        timeout=settings.datasphere_timeout,
        pool_size=settings.datasphere_pool_size,
    )


@lru_cache
def get_skill_loader() -> SkillLoader:
    """Get cached skill loader with connector factory."""
    connector_factory = {}

    business = get_business_connector()
    if business:
        connector_factory["postgres"] = business
        connector_factory["business"] = business

    datasphere = get_datasphere_connector()
    if datasphere:
        connector_factory["datasphere"] = datasphere

    return SkillLoader(
        skills_dir=Path("app/skills"),
        connector_factory=connector_factory,
    )


@lru_cache
def get_skill_registry() -> SkillRegistry:
    """Get cached skill registry with auto-discovered skills."""
    registry = SkillRegistry()
    loader = get_skill_loader()

    for skill in loader.load_all_skills():
        registry.register(skill)

    return registry


@lru_cache
def get_vector_store() -> VectorStore:
    """Get cached vector store instance."""
    settings = get_settings()
    embeddings = create_embeddings(settings)
    return VectorStore(
        embeddings=embeddings,
        connection_string=settings.database_url,
        collection_name=settings.vector_collection_name,
    )


@lru_cache
def get_rag_manager() -> RAGManager:
    """Get cached RAG manager instance."""
    store = get_vector_store()
    registry = get_skill_registry()
    return RAGManager(store=store, registry=registry)


def get_agent() -> Agent:
    """Get a configured agent instance."""
    settings = get_settings()
    chat_model = get_chat_model()
    registry = get_skill_registry()
    rag_manager = get_rag_manager()
    return Agent(
        chat_model,
        registry,
        max_iterations=settings.max_iterations,
        llm_timeout=settings.llm_timeout,
        tool_timeout=settings.tool_timeout,
        rag_manager=rag_manager,
    )


async def get_session_store() -> AsyncGenerator[SessionStore]:
    """Get session store with database session."""
    async for db_session in get_db_session():
        yield SessionStore(db_session, get_agent)
