# Streaming Chat Progress Guide

This guide explains how to add real-time progress updates to the Skillian chat UI,
so users see what the agent is doing (calling the LLM, executing tools, etc.)
instead of just a "Thinking..." spinner.

## Architecture Overview

```
┌─────────────┐      SSE stream       ┌─────────────────┐
│  Streamlit   │ ◄──────────────────── │   FastAPI        │
│  ui/chat.py  │  event: thinking      │   /api/v1/chat/  │
│              │  event: tool_call     │     stream       │
│  st.status() │  event: tool_result   │                  │
│  st.write_   │  event: text_delta    │  Agent.process   │
│    stream()  │  event: done          │    _stream()     │
└─────────────┘                        └─────────────────┘
```

**What changes:**
- `app/core/agent.py` — new `process_stream()` method that yields events
- `app/api/schemas.py` — new `StreamEvent` schema
- `app/api/routes.py` — new `/chat/stream` endpoint using `StreamingResponse`
- `ui/chat.py` — consume SSE stream, show live progress with `st.status`

**What stays the same:**
- The existing `/chat` endpoint (non-streaming) keeps working
- `Conversation`, `Message`, `SessionStore` — no changes needed
- Tool execution logic — identical, just wrapped with event yields

---

## Step 1: Define SSE Event Types

Add these to `app/api/schemas.py`:

```python
# --- Streaming events ---

class StreamEventType(StrEnum):
    """Types of events emitted during streaming."""

    THINKING = "thinking"          # LLM is being called
    TOOL_CALL = "tool_call"        # About to execute a tool
    TOOL_RESULT = "tool_result"    # Tool finished executing
    TEXT_DELTA = "text_delta"      # A chunk of the final response text
    DONE = "done"                  # Processing complete
    ERROR = "error"                # Something went wrong


class StreamEvent(BaseModel):
    """A single SSE event sent during streaming."""

    event: StreamEventType
    data: dict = {}
```

Import `StrEnum` from `enum` at the top of the file.

### Event payloads

Each event type carries specific data:

| Event | `data` payload | Example |
|-------|----------------|---------|
| `thinking` | `{"iteration": 1}` | Agent starting LLM call #1 |
| `tool_call` | `{"tool": "query_cost_center", "args": {"cc_id": "CC-1001"}}` | About to run a tool |
| `tool_result` | `{"tool": "query_cost_center", "result": "..."}` | Tool finished |
| `text_delta` | `{"content": "The budget"}` | Chunk of streamed text |
| `done` | `{"tool_calls": [...], "finished": true}` | Final summary |
| `error` | `{"message": "..."}` | Error occurred |

---

## Step 2: Add `process_stream()` to the Agent

In `app/core/agent.py`, add a new async generator method alongside the existing
`process()`. The existing method stays untouched — this is a parallel code path.

```python
from collections.abc import AsyncGenerator

async def process_stream(self, user_message: str) -> AsyncGenerator[dict, None]:
    """Process a user message, yielding SSE events as work happens.

    Yields dicts with keys: event (str), data (dict).
    The final event is always "done".
    """
    self.conversation.add_user(user_message)

    tool_calls_made: list[dict[str, Any]] = []
    iterations = 0

    while iterations < self.max_iterations:
        iterations += 1

        # --- Signal: about to call LLM ---
        yield {"event": "thinking", "data": {"iteration": iterations}}

        # Get LLM response
        lc_messages = self._convert_to_langchain_messages()
        response = await self.model.ainvoke(lc_messages)

        # Check for tool calls
        if hasattr(response, "tool_calls") and response.tool_calls:
            self.conversation.add_assistant(
                content=response.content or "",
                tool_calls=response.tool_calls,
            )

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]

                # --- Signal: about to execute tool ---
                yield {
                    "event": "tool_call",
                    "data": {"tool": tool_name, "args": tool_args},
                }

                result = await self._execute_tool(tool_name, tool_args)
                self.conversation.add_tool_result(result, tool_id)

                tool_calls_made.append({
                    "tool": tool_name,
                    "args": tool_args,
                    "result": result,
                })

                # --- Signal: tool finished ---
                yield {
                    "event": "tool_result",
                    "data": {"tool": tool_name, "result": result},
                }

            continue

        # No tool calls — final response
        content = response.content or ""
        self.conversation.add_assistant(content)

        # --- Signal: stream the final text ---
        yield {"event": "text_delta", "data": {"content": content}}

        # --- Signal: done ---
        yield {
            "event": "done",
            "data": {
                "response": content,
                "tool_calls": tool_calls_made,
                "finished": True,
            },
        }
        return

    # Max iterations
    yield {
        "event": "done",
        "data": {
            "response": "I couldn't complete the request within the allowed iterations.",
            "tool_calls": tool_calls_made,
            "finished": False,
        },
    }
```

### Key design decisions

- **`ainvoke` not `astream`**: We keep using `ainvoke` for now. This gives us
  event-level streaming (you see when tools start/finish) without needing to
  handle token-by-token streaming from the LLM. This is the simplest approach
  and gives 80% of the UX benefit. See the "Optional Enhancements" section
  for how to add token streaming later.

- **Generator, not callback**: Using `async for event in agent.process_stream()`
  is simpler than a callback system and maps directly to SSE.

- **`process()` untouched**: The existing non-streaming path keeps working.
  No regressions.

---

## Step 3: Add the Streaming Endpoint

In `app/api/routes.py`, add a new endpoint that wraps `process_stream()` in an
SSE `StreamingResponse`.

### 3a. Add imports

```python
import json

from fastapi.responses import StreamingResponse
```

### 3b. Add the endpoint

```python
@router.post(
    "/chat/stream",
    tags=["Chat"],
)
async def chat_stream(
    request: ChatRequest,
    session_store: SessionStore = Depends(get_session_store),
) -> StreamingResponse:
    """Process a chat message with real-time SSE progress events.

    Returns a text/event-stream with events:
    - thinking: LLM is being called
    - tool_call: Tool is about to execute
    - tool_result: Tool finished
    - text_delta: Chunk of final response
    - done: Processing complete (includes full response + tool_calls)
    """
    # Get or create session (same logic as /chat)
    session = None
    if request.session_id:
        session = await session_store.get(request.session_id)

    if not session:
        session = await session_store.create()

    async def event_generator():
        try:
            async for event in session.agent.process_stream(request.message):
                # SSE format: "event: <type>\ndata: <json>\n\n"
                event_type = event["event"]
                event_data = json.dumps(event["data"])
                yield f"event: {event_type}\ndata: {event_data}\n\n"

            # Persist session after processing
            session.increment_messages()
            await session_store.update(session)

            # Send session_id so the client can track it
            yield f"event: session\ndata: {json.dumps({'session_id': session.session_id})}\n\n"

        except Exception as e:
            logger.exception("Streaming chat failed")
            error_data = json.dumps({"message": str(e)})
            yield f"event: error\ndata: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
```

### How SSE works

The browser/client receives a stream of text lines:

```
event: thinking
data: {"iteration": 1}

event: tool_call
data: {"tool": "query_cost_center", "args": {"cc_id": "CC-1001"}}

event: tool_result
data: {"tool": "query_cost_center", "result": "{\"budget\": 100000}"}

event: thinking
data: {"iteration": 2}

event: text_delta
data: {"content": "The budget for CC-1001 is $100,000."}

event: done
data: {"response": "The budget for CC-1001 is $100,000.", "tool_calls": [...], "finished": true}

event: session
data: {"session_id": "abc-123"}
```

---

## Step 4: Update the Streamlit UI

Replace the `st.spinner("Thinking...")` block in `ui/chat.py` with an SSE
consumer that shows live progress.

### 4a. Add an SSE line parser

```python
def parse_sse_stream(response):
    """Parse an SSE stream from a requests response.

    Yields (event_type, data_dict) tuples.
    """
    event_type = None
    data_lines = []

    for line in response.iter_lines(decode_unicode=True):
        if line.startswith("event: "):
            event_type = line[7:]
        elif line.startswith("data: "):
            data_lines.append(line[6:])
        elif line == "":
            # Empty line = end of event
            if event_type and data_lines:
                import json

                data = json.loads("".join(data_lines))
                yield event_type, data
            event_type = None
            data_lines = []
```

### 4b. Replace the chat handling block

Replace the current block (approximately lines 79-125) with:

```python
# Chat input
if prompt := st.chat_input("Ask about SAP BW data issues..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Call backend with streaming
    with st.chat_message("assistant"):
        payload = {"message": prompt}
        if st.session_state.session_id:
            payload["session_id"] = st.session_state.session_id

        try:
            response = requests.post(
                f"{backend_url}/api/v1/chat/stream",
                json=payload,
                stream=True,
                timeout=600,
            )

            if response.status_code != 200:
                st.error(f"Error: {response.status_code}")
            else:
                assistant_message = ""
                tool_calls = []

                # Use st.status to show live progress
                with st.status("Processing...", expanded=True) as status:
                    for event_type, data in parse_sse_stream(response):

                        if event_type == "thinking":
                            iteration = data.get("iteration", "?")
                            status.update(label=f"Calling LLM (step {iteration})...")
                            st.write(f"Calling LLM (step {iteration})...")

                        elif event_type == "tool_call":
                            tool_name = data.get("tool", "unknown")
                            tool_args = data.get("args", {})
                            status.update(label=f"Running {tool_name}...")
                            st.write(f"Running **{tool_name}**({tool_args})")

                        elif event_type == "tool_result":
                            tool_name = data.get("tool", "unknown")
                            result = data.get("result", "")
                            st.write(f"Got result from **{tool_name}**")
                            tool_calls.append({
                                "tool": tool_name,
                                "args": {},  # args already shown in tool_call event
                                "result": result,
                            })

                        elif event_type == "text_delta":
                            assistant_message += data.get("content", "")

                        elif event_type == "done":
                            done_data = data
                            assistant_message = done_data.get("response", assistant_message)
                            tool_calls = done_data.get("tool_calls", tool_calls)
                            status.update(label="Done", state="complete", expanded=False)

                        elif event_type == "session":
                            session_id = data.get("session_id")
                            if session_id:
                                st.session_state.session_id = session_id

                        elif event_type == "error":
                            st.error(f"Error: {data.get('message', 'Unknown error')}")
                            status.update(label="Error", state="error")

                # Show the final response
                st.markdown(assistant_message)

                # Show tool calls in an expander
                if tool_calls:
                    with st.expander("Tool calls", expanded=False):
                        for tc in tool_calls:
                            st.code(
                                f"{tc['tool']}({tc.get('args', {})})\n→ {tc['result']}",
                                language="text",
                            )

                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "tool_calls": tool_calls,
                })

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect: {e}")
```

### What the user sees

Instead of a static "Thinking..." spinner, the UI now shows a live status box:

```
┌─ Processing... ──────────────────────────────┐
│  Calling LLM (step 1)...                     │
│  Running query_cost_center({"cc_id": "1001"})│
│  Got result from query_cost_center           │
│  Calling LLM (step 2)...                     │
└──────────────────────────────────────────────┘
```

Once done, the status box collapses and the final response appears below it.

---

## Step 5: Testing

### 5a. Unit test for `process_stream()`

In `tests/test_agent.py`, add a test that verifies the event sequence:

```python
@pytest.mark.asyncio
async def test_process_stream_events(mock_agent):
    """Verify process_stream yields the expected event sequence."""
    events = []
    async for event in mock_agent.process_stream("test query"):
        events.append(event)

    event_types = [e["event"] for e in events]

    # Should always start with thinking and end with done
    assert event_types[0] == "thinking"
    assert event_types[-1] == "done"

    # If tools were called, check the pattern
    if "tool_call" in event_types:
        # Every tool_call should be followed by a tool_result
        for i, et in enumerate(event_types):
            if et == "tool_call":
                assert event_types[i + 1] == "tool_result"
```

### 5b. Integration test for the SSE endpoint

```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_chat_stream_endpoint(async_client):
    """Verify the /chat/stream endpoint returns valid SSE."""
    async with async_client.stream(
        "POST",
        "/api/v1/chat/stream",
        json={"message": "Hello"},
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"

        events = []
        async for line in response.aiter_lines():
            if line.startswith("event: "):
                events.append(line[7:])

        assert "done" in events
```

### 5c. Manual test

```bash
# Terminal 1: start the backend
uv run uvicorn main:app --reload

# Terminal 2: test SSE with curl
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the budget for CC-1001?"}'

# You should see events appearing one by one in real-time
```

---

## Optional Enhancements

### Token-by-token streaming

The guide above uses `ainvoke` — the LLM returns the full text at once and we
emit it as a single `text_delta`. To stream tokens as they're generated:

Replace `ainvoke` with `astream` in `process_stream()`:

```python
# Instead of:
response = await self.model.ainvoke(lc_messages)

# Use:
full_content = ""
tool_calls = []
async for chunk in self.model.astream(lc_messages):
    # Accumulate content
    if chunk.content:
        full_content += chunk.content
        yield {"event": "text_delta", "data": {"content": chunk.content}}

    # Accumulate tool calls (they come in chunks too)
    if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
        for tc_chunk in chunk.tool_call_chunks:
            # LangChain streams tool calls in pieces — accumulate them
            # See: langchain_core.messages.AIMessageChunk
            ...
```

This is more complex because LangChain streams tool calls in pieces that need
reassembly. See [LangChain streaming docs](https://python.langchain.com/docs/how_to/chat_streaming/)
for the accumulation pattern. The `ainvoke` approach in the main guide is
recommended as a starting point — it gives you tool-level progress updates
which is the biggest UX improvement, without the chunk-reassembly complexity.

### Parallel tool execution

Currently tools run sequentially in the `for tool_call in response.tool_calls`
loop. If tools are independent, you can run them concurrently:

```python
import asyncio

# Execute all tools in parallel
tasks = []
for tool_call in response.tool_calls:
    yield {"event": "tool_call", "data": {"tool": tool_call["name"], "args": tool_call["args"]}}
    tasks.append(self._execute_tool(tool_call["name"], tool_call["args"]))

results = await asyncio.gather(*tasks)

# Emit results
for tool_call, result in zip(response.tool_calls, results):
    self.conversation.add_tool_result(result, tool_call["id"])
    yield {"event": "tool_result", "data": {"tool": tool_call["name"], "result": result}}
```

---

## File Change Summary

| File | Change | Lines affected |
|------|--------|----------------|
| `app/api/schemas.py` | Add `StreamEventType`, `StreamEvent` | New (append) |
| `app/core/agent.py` | Add `process_stream()` method | New method (~60 lines) |
| `app/api/routes.py` | Add `/chat/stream` endpoint | New endpoint (~50 lines) |
| `ui/chat.py` | Replace spinner with SSE consumer | Lines 72-125 (rewrite) |
| `tests/test_agent.py` | Add streaming tests | New tests |

No existing behavior is modified. The current `/chat` endpoint and the
non-streaming `process()` method continue to work unchanged.
