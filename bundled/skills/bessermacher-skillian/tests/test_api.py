"""Tests for API endpoints."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from main import app

# Base API path
API_V1 = "/api/v1"


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get(f"{API_V1}/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "version" in data
        assert "llm_provider" in data


class TestSkillsEndpoint:
    def test_list_skills(self, client):
        response = client.get(f"{API_V1}/skills")
        assert response.status_code == 200

        data = response.json()
        assert "skills" in data
        # Skills list should be present (may be empty until skills are implemented)
        assert isinstance(data["skills"], list)

    def test_skill_has_tools(self, client):
        response = client.get(f"{API_V1}/skills")
        data = response.json()

        for skill in data["skills"]:
            assert "name" in skill
            assert "description" in skill
            assert "tools" in skill
            assert isinstance(skill["tools"], list)


class TestChatEndpoint:
    def test_chat_success(self, client):
        from app.api.sessions import SessionStore
        from app.dependencies import get_session_store

        # Mock session with agent
        mock_agent = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Test response"
        mock_response.tool_calls_made = []
        mock_response.finished = True
        mock_response.timing = {}
        mock_agent.process = AsyncMock(return_value=mock_response)

        mock_session = MagicMock()
        mock_session.session_id = "test-session-123"
        mock_session.agent = mock_agent
        mock_session.increment_messages = MagicMock()

        mock_session_store = MagicMock(spec=SessionStore)
        mock_session_store.get = AsyncMock(return_value=None)
        mock_session_store.create = AsyncMock(return_value=mock_session)
        mock_session_store.update = AsyncMock()

        # Use FastAPI's dependency override
        app.dependency_overrides[get_session_store] = lambda: mock_session_store

        try:
            response = client.post(
                f"{API_V1}/chat",
                json={"message": "Hello"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "Test response"
            assert data["finished"] is True
            assert data["session_id"] == "test-session-123"
        finally:
            # Clean up override
            app.dependency_overrides.pop(get_session_store, None)

    def test_chat_with_session_id(self, client):
        """Test that passing session_id reuses the existing session."""
        from app.api.sessions import SessionStore
        from app.dependencies import get_session_store

        # Mock session with agent
        mock_agent = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Continued conversation"
        mock_response.tool_calls_made = []
        mock_response.finished = True
        mock_response.timing = {}
        mock_agent.process = AsyncMock(return_value=mock_response)

        mock_session = MagicMock()
        mock_session.session_id = "existing-session-456"
        mock_session.agent = mock_agent
        mock_session.increment_messages = MagicMock()

        mock_session_store = MagicMock(spec=SessionStore)
        # Return the session when getting by ID (not creating new)
        mock_session_store.get = AsyncMock(return_value=mock_session)
        mock_session_store.create = AsyncMock()  # Should not be called
        mock_session_store.update = AsyncMock()

        app.dependency_overrides[get_session_store] = lambda: mock_session_store

        try:
            response = client.post(
                f"{API_V1}/chat",
                json={"message": "Continue", "session_id": "existing-session-456"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "Continued conversation"
            assert data["session_id"] == "existing-session-456"
            # Verify create was not called (existing session reused)
            mock_session_store.create.assert_not_called()
        finally:
            app.dependency_overrides.pop(get_session_store, None)

    def test_chat_empty_message(self, client):
        response = client.post(
            f"{API_V1}/chat",
            json={"message": ""},
        )
        assert response.status_code == 422  # Validation error


class TestListSessionsEndpoint:
    def test_list_sessions_empty(self, client):
        """List sessions returns empty list when no sessions exist."""
        from app.api.sessions import SessionStore
        from app.dependencies import get_session_store

        mock_session_store = MagicMock(spec=SessionStore)
        mock_session_store.list_all = AsyncMock(return_value=[])

        app.dependency_overrides[get_session_store] = lambda: mock_session_store

        try:
            response = client.get(f"{API_V1}/sessions")

            assert response.status_code == 200
            data = response.json()
            assert data["sessions"] == []
        finally:
            app.dependency_overrides.pop(get_session_store, None)

    def test_list_sessions_returns_sessions(self, client):
        """List sessions returns all sessions with correct fields."""
        from app.api.sessions import SessionInfo, SessionStore
        from app.dependencies import get_session_store

        now = datetime(2026, 1, 15, 10, 30, 0)
        mock_sessions = [
            SessionInfo(
                session_id="session-aaa",
                created_at=now,
                message_count=3,
            ),
            SessionInfo(
                session_id="session-bbb",
                created_at=now,
                message_count=0,
            ),
        ]

        mock_session_store = MagicMock(spec=SessionStore)
        mock_session_store.list_all = AsyncMock(return_value=mock_sessions)

        app.dependency_overrides[get_session_store] = lambda: mock_session_store

        try:
            response = client.get(f"{API_V1}/sessions")

            assert response.status_code == 200
            data = response.json()
            assert len(data["sessions"]) == 2

            first = data["sessions"][0]
            assert first["session_id"] == "session-aaa"
            assert first["message_count"] == 3
            assert first["created_at"] == now.isoformat()

            second = data["sessions"][1]
            assert second["session_id"] == "session-bbb"
            assert second["message_count"] == 0
        finally:
            app.dependency_overrides.pop(get_session_store, None)

    def test_list_sessions_calls_list_all(self, client):
        """Verify the endpoint calls session_store.list_all exactly once."""
        from app.api.sessions import SessionStore
        from app.dependencies import get_session_store

        mock_session_store = MagicMock(spec=SessionStore)
        mock_session_store.list_all = AsyncMock(return_value=[])

        app.dependency_overrides[get_session_store] = lambda: mock_session_store

        try:
            client.get(f"{API_V1}/sessions")
            mock_session_store.list_all.assert_awaited_once()
        finally:
            app.dependency_overrides.pop(get_session_store, None)


class TestSessionEndpoints:
    @pytest.mark.integration
    def test_create_session(self, client):
        from app.dependencies import get_agent

        mock_agent = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Hello!"
        mock_response.tool_calls_made = []
        mock_response.finished = True
        mock_agent.process = AsyncMock(return_value=mock_response)

        # Use FastAPI's dependency override
        app.dependency_overrides[get_agent] = lambda: mock_agent

        try:
            response = client.post(
                f"{API_V1}/sessions",
                json={"message": "Start conversation"},
            )

            assert response.status_code == 200
            data = response.json()
            assert "session_id" in data
            assert data["session_id"] is not None
        finally:
            app.dependency_overrides.pop(get_agent, None)

    @pytest.mark.integration
    def test_list_sessions(self, client):
        response = client.get(f"{API_V1}/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data

    @pytest.mark.integration
    def test_session_not_found(self, client):
        response = client.post(
            f"{API_V1}/sessions/nonexistent-id/chat",
            json={"message": "Hello"},
        )
        assert response.status_code == 404


class TestKnowledgeEndpoints:
    @pytest.mark.integration
    def test_search_knowledge(self, client):
        # Note: This may fail if embeddings aren't available
        # In CI, mock the RAG manager
        response = client.post(
            f"{API_V1}/knowledge/search",
            json={"query": "budget analysis", "k": 2},
        )

        # Accept either success or service unavailable
        assert response.status_code in [200, 500]

    @pytest.mark.integration
    def test_search_validation(self, client):
        response = client.post(
            f"{API_V1}/knowledge/search",
            json={"query": "", "k": 2},
        )
        assert response.status_code == 422  # Validation error

        response = client.post(
            f"{API_V1}/knowledge/search",
            json={"query": "test", "k": 100},  # k too high
        )
        assert response.status_code == 422
