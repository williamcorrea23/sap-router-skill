"""Session management for conversations with PostgreSQL persistence."""

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import Agent
from app.core.messages import Conversation, Message, MessageRole
from app.db.models import SessionModel


def _serialize_conversation(conversation: Conversation) -> dict[str, Any]:
    """Serialize a Conversation to a dict for JSONB storage."""
    return {
        "messages": [
            {
                "role": msg.role.value,
                "content": msg.content,
                "tool_call_id": msg.tool_call_id,
                "tool_calls": msg.tool_calls,
            }
            for msg in conversation.messages
        ]
    }


def _deserialize_conversation(data: dict[str, Any]) -> Conversation:
    """Deserialize a dict from JSONB to a Conversation."""
    conversation = Conversation()
    for msg_data in data.get("messages", []):
        message = Message(
            role=MessageRole(msg_data["role"]),
            content=msg_data["content"],
            tool_call_id=msg_data.get("tool_call_id"),
            tool_calls=msg_data.get("tool_calls"),
        )
        conversation.add(message)
    return conversation


@dataclass
class SessionInfo:
    """Lightweight session metadata (no agent attached)."""

    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    message_count: int = 0


@dataclass
class Session:
    """A conversation session with an active agent."""

    session_id: str
    agent: Agent
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    message_count: int = 0

    def touch(self) -> None:
        """Update last accessed time."""
        self.last_accessed = datetime.now()

    def increment_messages(self) -> None:
        """Increment message count."""
        self.message_count += 1


class SessionStore:
    """PostgreSQL-backed session store."""

    def __init__(self, db: AsyncSession, agent_factory: Callable[[], Agent]):
        """Initialize the session store.

        Args:
            db: SQLAlchemy async session.
            agent_factory: Callable that creates a new Agent instance.
        """
        self._db = db
        self._agent_factory = agent_factory

    async def create(self) -> Session:
        """Create a new session.

        Returns:
            New session with a fresh agent.
        """
        session_id = uuid.uuid4()
        agent = self._agent_factory()

        db_session = SessionModel(
            id=session_id,
            message_count=0,
            conversation_data=_serialize_conversation(agent.conversation),
        )
        self._db.add(db_session)
        await self._db.flush()

        return Session(
            session_id=str(session_id),
            agent=agent,
            created_at=db_session.created_at,
            last_accessed=db_session.last_accessed,
            message_count=0,
        )

    async def get(self, session_id: str) -> Session | None:
        """Get a session by ID.

        Args:
            session_id: Session identifier.

        Returns:
            Session if found, None otherwise.
        """
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            return None

        result = await self._db.execute(select(SessionModel).where(SessionModel.id == session_uuid))
        db_session = result.scalar_one_or_none()

        if db_session is None:
            return None

        # Recreate agent and restore conversation
        agent = self._agent_factory()
        agent.conversation = _deserialize_conversation(db_session.conversation_data)

        return Session(
            session_id=session_id,
            agent=agent,
            created_at=db_session.created_at,
            last_accessed=db_session.last_accessed,
            message_count=db_session.message_count,
        )

    async def update(self, session: Session) -> None:
        """Update a session in the database.

        Args:
            session: Session to update.
        """
        session_uuid = UUID(session.session_id)
        result = await self._db.execute(select(SessionModel).where(SessionModel.id == session_uuid))
        db_session = result.scalar_one_or_none()

        if db_session:
            db_session.message_count = session.message_count
            db_session.conversation_data = _serialize_conversation(session.agent.conversation)
            await self._db.flush()

    async def delete(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session to delete.

        Returns:
            True if deleted, False if not found.
        """
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            return False

        result = await self._db.execute(select(SessionModel).where(SessionModel.id == session_uuid))
        db_session = result.scalar_one_or_none()

        if db_session:
            await self._db.delete(db_session)
            await self._db.flush()
            return True
        return False

    async def list_all(self) -> list[SessionInfo]:
        """List all sessions (metadata only — no agent created)."""
        result = await self._db.execute(select(SessionModel))
        db_sessions = result.scalars().all()

        return [
            SessionInfo(
                session_id=str(db_session.id),
                created_at=db_session.created_at,
                last_accessed=db_session.last_accessed,
                message_count=db_session.message_count,
            )
            for db_session in db_sessions
        ]

    async def count(self) -> int:
        """Get the number of active sessions."""
        result = await self._db.execute(select(func.count()).select_from(SessionModel))
        return result.scalar() or 0
