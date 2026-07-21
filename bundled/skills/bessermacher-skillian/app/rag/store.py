"""Vector store wrapper for RAG functionality using pgvector."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class VectorStoreError(Exception):
    """Raised when vector store operations fail."""


@dataclass
class VectorStore:
    """Wrapper around PGVector for RAG functionality.

    Provides:
    - Document ingestion from markdown files
    - Similarity search for retrieval
    - Persistence to PostgreSQL with pgvector

    Example:
        store = VectorStore(
            embeddings=embeddings,
            connection_string="postgresql+psycopg://...",
            collection_name="skillian_knowledge",
        )
        store.add_documents_from_directory("app/skills/financial/knowledge/")
        results = store.search("budget variance analysis", k=3)
    """

    embeddings: Embeddings
    connection_string: str
    collection_name: str = "skillian_knowledge"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    _store: PGVector | None = field(default=None, init=False)
    _splitter: RecursiveCharacterTextSplitter | None = field(default=None, init=False)
    _sync_connection: str = field(default="", init=False)

    def __post_init__(self):
        """Initialize the vector store and text splitter."""
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", " "],
        )

        # Convert asyncpg URL to psycopg for langchain-postgres
        # langchain-postgres requires psycopg (sync) driver
        self._sync_connection = self.connection_string.replace(
            "postgresql+asyncpg://", "postgresql+psycopg://"
        )

        # Initialize PGVector
        self._store = PGVector(
            collection_name=self.collection_name,
            embeddings=self.embeddings,
            connection=self._sync_connection,
            use_jsonb=True,
        )

    def add_documents(self, documents: list[Document]) -> int:
        """Add documents to the vector store.

        Args:
            documents: List of LangChain documents to add.

        Returns:
            Number of chunks added.
        """
        if not documents:
            return 0

        # Split documents into chunks
        chunks = self._splitter.split_documents(documents)

        if chunks:
            self._store.add_documents(chunks)

        return len(chunks)

    def add_documents_from_directory(
        self,
        directory: str,
        glob_pattern: str = "**/*.md",
    ) -> int:
        """Add all markdown documents from a directory.

        Args:
            directory: Path to the directory.
            glob_pattern: Glob pattern for files to include.

        Returns:
            Number of chunks added.
        """
        path = Path(directory)
        if not path.exists():
            return 0

        documents = []
        for file_path in path.glob(glob_pattern):
            try:
                content = file_path.read_text(encoding="utf-8")
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": str(file_path),
                        "filename": file_path.name,
                        "skill": file_path.parent.parent.name,
                    },
                )
                documents.append(doc)
            except Exception as e:
                logger.warning("Could not read %s: %s", file_path, e)

        return self.add_documents(documents)

    def search(
        self,
        query: str,
        k: int = 4,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[Document]:
        """Search for relevant documents.

        Args:
            query: Search query.
            k: Number of results to return.
            filter_metadata: Optional metadata filter.

        Returns:
            List of relevant documents.
        """
        if filter_metadata:
            return self._store.similarity_search(
                query,
                k=k,
                filter=filter_metadata,
            )
        return self._store.similarity_search(query, k=k)

    def search_with_scores(
        self,
        query: str,
        k: int = 4,
    ) -> list[tuple[Document, float]]:
        """Search with relevance scores.

        Args:
            query: Search query.
            k: Number of results.

        Returns:
            List of (document, score) tuples.
        """
        return self._store.similarity_search_with_score(query, k=k)

    def get_retriever(self, k: int = 4):
        """Get a LangChain retriever for this store.

        Args:
            k: Number of documents to retrieve.

        Returns:
            LangChain retriever instance.
        """
        return self._store.as_retriever(search_kwargs={"k": k})

    def clear(self) -> None:
        """Clear all documents from the store."""
        self._store.delete_collection()
        # Recreate the collection
        self._store = PGVector(
            collection_name=self.collection_name,
            embeddings=self.embeddings,
            connection=self._sync_connection,
            use_jsonb=True,
        )

    @property
    def count(self) -> int:
        """Number of documents in the store."""
        try:
            # Use PGVector's internal engine to avoid creating new connections
            from sqlalchemy import text

            with self._store._make_sync_session() as session:
                result = session.execute(
                    text(
                        "SELECT COUNT(*) FROM langchain_pg_embedding "
                        "WHERE collection_id = ("
                        "SELECT uuid FROM langchain_pg_collection WHERE name = :name"
                        ")"
                    ),
                    {"name": self.collection_name},
                )
                return result.scalar() or 0
        except Exception:
            return 0
