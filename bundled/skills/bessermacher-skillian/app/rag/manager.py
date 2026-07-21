"""RAG manager for coordinating knowledge retrieval."""

from dataclasses import dataclass

from langchain_core.documents import Document

from app.core import SkillRegistry
from app.rag.store import VectorStore


@dataclass
class RAGManager:
    """Manages RAG functionality across skills.

    Coordinates:
    - Knowledge ingestion from all skills
    - Contextual retrieval for queries
    - Integration with the agent

    Example:
        manager = RAGManager(vector_store, registry)
        manager.ingest_all_skills()
        context = manager.get_context("budget variance analysis")
    """

    store: VectorStore
    registry: SkillRegistry

    def ingest_all_skills(self) -> dict[str, int]:
        """Ingest knowledge from all registered skills.

        Returns:
            Dictionary of skill name to chunks ingested.
        """
        results = {}

        for skill in self.registry.get_all_skills():
            total_chunks = 0
            for knowledge_path in skill.knowledge_paths:
                chunks = self.store.add_documents_from_directory(knowledge_path)
                total_chunks += chunks

            results[skill.name] = total_chunks

        return results

    def ingest_skill(self, skill_name: str) -> int:
        """Ingest knowledge for a specific skill.

        Args:
            skill_name: Name of the skill to ingest.

        Returns:
            Number of chunks ingested.
        """
        skill = self.registry.get_skill(skill_name)
        total_chunks = 0

        for knowledge_path in skill.knowledge_paths:
            chunks = self.store.add_documents_from_directory(knowledge_path)
            total_chunks += chunks

        return total_chunks

    def get_context(
        self,
        query: str,
        k: int = 4,
        skill_filter: str | None = None,
    ) -> str:
        """Get relevant context for a query.

        Args:
            query: The user's query.
            k: Number of documents to retrieve.
            skill_filter: Optional skill name to filter results.

        Returns:
            Formatted context string.
        """
        filter_metadata = None
        if skill_filter:
            filter_metadata = {"skill": skill_filter}

        docs = self.store.search(query, k=k, filter_metadata=filter_metadata)
        return self._format_context(docs)

    def get_context_documents(
        self,
        query: str,
        k: int = 4,
    ) -> list[Document]:
        """Get relevant documents for a query.

        Args:
            query: The user's query.
            k: Number of documents to retrieve.

        Returns:
            List of relevant documents.
        """
        return self.store.search(query, k=k)

    def _format_context(self, docs: list[Document]) -> str:
        """Format documents into a context string.

        Args:
            docs: Documents to format.

        Returns:
            Formatted context string.
        """
        if not docs:
            return ""

        sections = []
        for doc in docs:
            source = doc.metadata.get("filename", "Unknown")
            sections.append(f"### From {source}\n{doc.page_content}")

        return "\n\n".join(sections)

    @property
    def document_count(self) -> int:
        """Total documents in the store."""
        return self.store.count
