"""Message types for agent conversations.

This module provides a thin wrapper around LangChain message types,
designed for eventual migration to LangGraph's state management.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MessageRole(StrEnum):
    """Message role in conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """A message in the conversation."""

    role: MessageRole
    content: str
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] | None = None

    @classmethod
    def system(cls, content: str) -> "Message":
        return cls(role=MessageRole.SYSTEM, content=content)

    @classmethod
    def user(cls, content: str) -> "Message":
        return cls(role=MessageRole.USER, content=content)

    @classmethod
    def assistant(cls, content: str, tool_calls: list[dict] | None = None) -> "Message":
        return cls(role=MessageRole.ASSISTANT, content=content, tool_calls=tool_calls)

    @classmethod
    def tool(cls, content: str, tool_call_id: str) -> "Message":
        return cls(role=MessageRole.TOOL, content=content, tool_call_id=tool_call_id)


@dataclass
class Conversation:
    """A conversation with message history.

    Note: This will be replaced by LangGraph state management
    in a future iteration.
    """

    messages: list[Message] = field(default_factory=list)

    def add(self, message: Message) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)

    def add_user(self, content: str) -> None:
        """Add a user message."""
        self.add(Message.user(content))

    def add_assistant(self, content: str, tool_calls: list[dict] | None = None) -> None:
        """Add an assistant message."""
        self.add(Message.assistant(content, tool_calls))

    def add_tool_result(self, content: str, tool_call_id: str) -> None:
        """Add a tool result message."""
        self.add(Message.tool(content, tool_call_id))

    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()

    def __len__(self) -> int:
        return len(self.messages)
