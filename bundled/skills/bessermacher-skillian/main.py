"""Skillian - SAP BW AI Assistant."""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import get_settings
from app.db import close_db, init_db
from app.dependencies import (
    get_business_connector,
    get_datasphere_connector,
    get_llm_provider,
    get_rag_manager,
    get_skill_registry,
)


def _setup_logging(debug: bool = False) -> None:
    """Configure application logging."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    settings = get_settings()
    _setup_logging(settings.debug)

    provider = get_llm_provider()
    registry = get_skill_registry()

    logger.info("Starting %s v%s", settings.app_name, settings.app_version)

    # Initialize database
    await init_db()
    logger.info("Database initialized")
    logger.info("Environment: %s", settings.env)
    logger.info("LLM Provider: %s (%s)", provider.provider_name, provider.model_name)
    logger.info("Skills registered: %d", registry.skill_count)
    logger.info("Tools available: %d", registry.tool_count)

    # Initialize Datasphere connector if configured
    datasphere = get_datasphere_connector()
    if datasphere:
        try:
            await datasphere.connect()
            logger.info("Datasphere connector initialized for space: %s", settings.datasphere_space)
        except Exception as e:
            logger.warning("Datasphere initialization failed: %s", e)

    # Ingest knowledge on startup
    try:
        rag_manager = get_rag_manager()
        results = rag_manager.ingest_all_skills()
        total = sum(results.values())
        logger.info("Knowledge ingested: %d chunks from %d skills", total, len(results))
    except Exception as e:
        logger.warning("RAG initialization failed: %s", e)

    yield

    # Cleanup resources
    logger.info("Shutting down...")

    # Close Datasphere connector
    if datasphere:
        try:
            await datasphere.close()
            logger.debug("Datasphere connector closed")
        except Exception as e:
            logger.warning("Error closing Datasphere connector: %s", e)

    try:
        connector = get_business_connector()
        await connector.close()
        logger.debug("Business database connection closed")
    except Exception as e:
        logger.warning("Error closing business database: %s", e)

    await close_db()
    logger.info("Shutdown complete")


settings = get_settings()

# Configure CORS based on environment
allowed_origins = (
    ["*"]
    if settings.is_development
    else [
        # Add production origins here, e.g.:
        # "https://skillian.example.com",
    ]
)

app = FastAPI(
    title=settings.app_name,
    description="SAP BW AI Assistant with domain-specific skills for data diagnostics",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
    )
