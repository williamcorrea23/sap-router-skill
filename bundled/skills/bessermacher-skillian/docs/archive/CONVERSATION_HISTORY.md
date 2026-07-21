# Conversation History Architecture

This document explains how Skillian maintains conversation history for multi-turn interactions.

## Overview

Skillian uses a **session-based architecture** where conversation history is:
1. Stored in-memory within an `Agent` instance during a session
2. Persisted to PostgreSQL as JSONB for durability
3. Restored when a session is retrieved

```
┌─────────────┐      ┌──────────────┐      ┌────────────────┐
│  Streamlit  │─────▶│  /api/v1/    │─────▶│  SessionStore  │
│     UI      │      │    chat      │      │                │
└─────────────┘      └──────────────┘      └───────┬────────┘
      │                                            │
      │ session_id                                 ▼
      │◀──────────────────────────────────┌────────────────┐
      │                                   │   PostgreSQL   │
      │                                   │  (sessions)    │
      └──────────────────────────────────▶└────────────────┘
```

## Key Components

### 1. Message Types (`app/core/messages.py`)

Messages are the fundamental unit of conversation:

```python
class MessageRole(StrEnum):
    SYSTEM = "system"      # System instructions (always first)
    USER = "user"          # User's input
    ASSISTANT = "assistant"  # LLM's response
    TOOL = "tool"          # Tool execution result

@dataclass
class Message:
    role: MessageRole
    content: str
    tool_call_id: str | None = None    # For TOOL messages
    tool_calls: list[dict] | None = None  # For ASSISTANT messages with tools
```

### 2. Conversation Container (`app/core/messages.py`)

The `Conversation` class holds an ordered list of messages:

```python
@dataclass
class Conversation:
    messages: list[Message] = field(default_factory=list)

    def add_user(self, content: str) -> None: ...
    def add_assistant(self, content: str, tool_calls=None) -> None: ...
    def add_tool_result(self, content: str, tool_call_id: str) -> None: ...
    def clear(self) -> None: ...
```

### 3. Agent (`app/core/agent.py`)

Each `Agent` instance holds a `Conversation`:

```python
class Agent:
    def __init__(self, chat_model, registry, max_iterations=10):
        self.conversation = Conversation()
        self._setup_system_prompt()  # Adds initial SYSTEM message

    async def process(self, user_message: str) -> AgentResponse:
        self.conversation.add_user(user_message)  # Add user input
        # ... LLM processing ...
        self.conversation.add_assistant(content)  # Add response
        return AgentResponse(content=content, ...)
```

### 4. Session Persistence (`app/api/sessions.py`)

Sessions wrap an Agent and persist to PostgreSQL:

```python
@dataclass
class Session:
    session_id: str
    agent: Agent
    created_at: datetime
    message_count: int
```

## Data Flow

### First Message (New Session)

```
1. User sends: POST /api/v1/chat {"message": "What's the budget for CC-1001?"}

2. SessionStore.create() is called:
   - Creates new Agent with empty Conversation (except system prompt)
   - Generates UUID for session
   - Saves to PostgreSQL with empty conversation_data

3. Agent.process(message) is called:
   - Adds USER message to conversation
   - Sends to LLM
   - Receives response (possibly with tool calls)
   - Adds ASSISTANT message to conversation

4. SessionStore.update(session) is called:
   - Serializes conversation to JSONB
   - Updates PostgreSQL record

5. Response returned with session_id:
   {"response": "...", "session_id": "abc-123-..."}
```

### Follow-up Message (Existing Session)

```
1. User sends: POST /api/v1/chat {
     "message": "Show me the top differences",
     "session_id": "abc-123-..."
   }

2. SessionStore.get(session_id) is called:
   - Fetches SessionModel from PostgreSQL
   - Creates new Agent instance
   - Deserializes conversation_data back to Conversation object
   - Agent now has full message history

3. Agent.process(message) is called:
   - History includes all previous messages
   - LLM sees full context when generating response

4. Session updated and response returned
```

## Database Schema

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    message_count INTEGER DEFAULT 0,
    conversation_data JSONB DEFAULT '{}'
);
```

### conversation_data Structure

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are Skillian, an AI assistant...",
      "tool_call_id": null,
      "tool_calls": null
    },
    {
      "role": "user",
      "content": "What's the budget for CC-1001?",
      "tool_call_id": null,
      "tool_calls": null
    },
    {
      "role": "assistant",
      "content": "",
      "tool_call_id": null,
      "tool_calls": [
        {
          "id": "call_xyz",
          "name": "get_budget",
          "args": {"cost_center": "CC-1001"}
        }
      ]
    },
    {
      "role": "tool",
      "content": "{\"budget\": 50000, \"spent\": 35000}",
      "tool_call_id": "call_xyz",
      "tool_calls": null
    },
    {
      "role": "assistant",
      "content": "The budget for CC-1001 is $50,000...",
      "tool_call_id": null,
      "tool_calls": null
    }
  ]
}
```

## UI Integration (Streamlit)

The Streamlit UI (`ui/chat.py`) maintains session continuity:

```python
# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Build request payload
payload = {"message": prompt}
if st.session_state.session_id:
    payload["session_id"] = st.session_state.session_id

# Send request
response = requests.post(f"{backend_url}/api/v1/chat", json=payload)

# Store session_id for next request
if data.get("session_id"):
    st.session_state.session_id = data["session_id"]
```

The UI also displays chat history client-side for immediate rendering:

```python
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
```

## Multi-Turn Tool Usage Example

```
Turn 1:
  User: "Compare FI and BPC for company 1000"

  Conversation state after Turn 1:
  ├── SYSTEM: "You are Skillian..."
  ├── USER: "Compare FI and BPC for company 1000"
  ├── ASSISTANT: "" + tool_calls: [compare_sources(...)]
  ├── TOOL: "{ differences: [...], summary: '...' }"
  └── ASSISTANT: "I found 15 differences between FI and BPC..."

Turn 2:
  User: "Show me the top 3"

  Conversation state after Turn 2:
  ├── SYSTEM: "You are Skillian..."
  ├── USER: "Compare FI and BPC for company 1000"
  ├── ASSISTANT: "" + tool_calls: [compare_sources(...)]
  ├── TOOL: "{ differences: [...], summary: '...' }"
  ├── ASSISTANT: "I found 15 differences between FI and BPC..."
  ├── USER: "Show me the top 3"  <-- NEW
  └── ASSISTANT: "The top 3 differences are..."  <-- LLM has context!
```

## Session Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                      Session Lifecycle                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  CREATE ───▶ First message creates session                   │
│              ├── UUID generated                              │
│              ├── Agent instantiated                          │
│              └── Saved to PostgreSQL                         │
│                                                              │
│  USE ───────▶ Subsequent messages                            │
│              ├── Session retrieved by ID                     │
│              ├── Conversation restored to Agent              │
│              ├── Message processed with full history         │
│              └── Updated conversation saved                  │
│                                                              │
│  DELETE ────▶ Manual cleanup (no automatic TTL)              │
│              └── DELETE /api/v1/sessions/{id}                │
│                                                              │
│  NEW CHAT ──▶ Streamlit "New Chat" button                    │
│              ├── Clears st.session_state.session_id          │
│              └── Next message creates fresh session          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Important Notes

### Agent Recreation
When a session is retrieved, a **new Agent instance** is created and the conversation is restored into it. The Agent itself is not persisted - only the conversation data.

### No Automatic Cleanup
Sessions persist indefinitely until manually deleted. For production, consider implementing:
- TTL-based cleanup (e.g., delete sessions older than 24 hours)
- Maximum sessions per user
- Storage limits

### LangChain Message Conversion
The Agent converts internal `Message` objects to LangChain format before sending to the LLM:

```python
def _convert_to_langchain_messages(self) -> list[BaseMessage]:
    for msg in self.conversation.messages:
        match msg.role:
            case MessageRole.SYSTEM: yield SystemMessage(content=msg.content)
            case MessageRole.USER: yield HumanMessage(content=msg.content)
            case MessageRole.ASSISTANT: yield AIMessage(content=msg.content, ...)
            case MessageRole.TOOL: yield ToolMessage(content=msg.content, ...)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Auto-creates or reuses session |
| `/api/v1/sessions` | GET | List all sessions |
| `/api/v1/sessions` | POST | Explicitly create session |
| `/api/v1/sessions/{id}/chat` | POST | Chat in specific session |
| `/api/v1/sessions/{id}` | DELETE | Delete a session |

## Files Reference

| File | Purpose |
|------|---------|
| `app/core/messages.py` | Message and Conversation classes |
| `app/core/agent.py` | Agent with conversation handling |
| `app/api/sessions.py` | Session persistence logic |
| `app/api/routes.py` | API endpoints |
| `app/db/models.py` | SQLAlchemy SessionModel |
| `ui/chat.py` | Streamlit UI with session tracking |
