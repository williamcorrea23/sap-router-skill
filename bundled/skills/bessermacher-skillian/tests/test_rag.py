"""Tests for RAG functionality."""

import os
from pathlib import Path

import pytest

from app.rag import VectorStore


class MockEmbeddings:
    """Mock embeddings for testing."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # Return simple mock embeddings
        return [[0.1] * 384 for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [0.1] * 384


# Use test database URL from environment or default to local test DB
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://skillian:skillian@localhost:5432/skillian",
)


@pytest.mark.integration
class TestVectorStore:
    @pytest.fixture
    def temp_dir(self, tmp_path):
        return str(tmp_path)

    @pytest.fixture
    def store(self):
        """Create a VectorStore with unique collection for test isolation."""
        import uuid

        collection_name = f"test_collection_{uuid.uuid4().hex[:8]}"
        store = VectorStore(
            embeddings=MockEmbeddings(),
            connection_string=TEST_DATABASE_URL,
            collection_name=collection_name,
        )
        yield store
        # Cleanup: delete the test collection
        try:
            store.clear()
        except Exception:
            pass

    def test_create_store(self, store):
        assert store is not None
        assert store.count == 0

    def test_add_documents_from_directory(self, store, temp_dir):
        # Create test knowledge directory
        knowledge_dir = Path(temp_dir) / "knowledge"
        knowledge_dir.mkdir()

        # Create test markdown file
        test_file = knowledge_dir / "test.md"
        test_file.write_text("# Test Document\n\nThis is test content.")

        chunks = store.add_documents_from_directory(str(knowledge_dir))

        assert chunks >= 1
        assert store.count >= 1

    def test_add_documents_empty_directory(self, store, temp_dir):
        empty_dir = Path(temp_dir) / "empty"
        empty_dir.mkdir()

        chunks = store.add_documents_from_directory(str(empty_dir))
        assert chunks == 0

    def test_add_documents_nonexistent_directory(self, store):
        chunks = store.add_documents_from_directory("/nonexistent/path")
        assert chunks == 0

    def test_clear(self, store, temp_dir):
        # Add some documents
        knowledge_dir = Path(temp_dir) / "knowledge"
        knowledge_dir.mkdir()
        (knowledge_dir / "test.md").write_text("# Test\n\nContent here.")

        store.add_documents_from_directory(str(knowledge_dir))
        assert store.count >= 1

        store.clear()
        assert store.count == 0

    def test_search(self, store, temp_dir):
        # Add some documents
        knowledge_dir = Path(temp_dir) / "knowledge"
        knowledge_dir.mkdir()
        (knowledge_dir / "test.md").write_text(
            "# Budget Analysis\n\nThis document covers budget variance analysis."
        )

        store.add_documents_from_directory(str(knowledge_dir))

        results = store.search("budget variance", k=2)
        assert len(results) >= 1
        assert "budget" in results[0].page_content.lower()

    def test_search_with_scores(self, store, temp_dir):
        # Add some documents
        knowledge_dir = Path(temp_dir) / "knowledge"
        knowledge_dir.mkdir()
        (knowledge_dir / "test.md").write_text("# Test Document\n\nSample content.")

        store.add_documents_from_directory(str(knowledge_dir))

        results = store.search_with_scores("test document", k=2)
        assert len(results) >= 1
        assert isinstance(results[0], tuple)
        assert len(results[0]) == 2  # (document, score)
