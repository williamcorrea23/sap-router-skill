# Fix: Empty LLM Response After Tool Calls

**Date:** 2026-02-17
**Problem:** LLM produces no text conclusion after executing tools (Ollama + tool binding)
**Affected files:** `app/core/agent.py`, `ui/chat.py`, `docker-compose.yml`, `.env`

## Problem Description

When using Ollama (qwen2.5:7b) with LangChain tool binding, the LLM would:
1. Correctly call tools (e.g. `check_data_availability`) at step 1
2. Return **empty `response.content`** at step 2 after ~80 seconds
3. The UI showed no conclusion text despite the tool returning valid data

Secondary issue: the `_mentions_tools` nudge in the agent was too aggressive for
non-investigation queries, potentially causing infinite loops when the LLM mentioned
tool names in its natural-language response.

## Changes Summary

### 1. `app/core/agent.py` — Agent resilience improvements

#### a) New `_extract_content()` static method
Extracts text from LLM responses with fallbacks for provider quirks:
- Primary: `response.content` (string)
- Fallback: list-type content blocks (Anthropic format)
- Fallback: `response.additional_kwargs.message.content` (Ollama)
- Fallback: `response.additional_kwargs.content` (generic)

#### b) New `_build_summarise_nudge()` static method
When the LLM returns empty content after tool calls, builds a retry nudge that
includes the **actual tool results** inline. This prevents the model from
hallucinating on retry (the 7b model was inventing unrelated investigation results).

Template:
```
Your previous response was empty. Here are the tool results you need to
summarise for the user:

Tool: check_data_availability
Args: {...}
Result: {...}

Provide a clear, concise text summary of these findings.
Do NOT call any tools — just answer the user's question based on
the results above.
```

#### c) New `_investigation_started()` method
Returns True when `start_investigation` was called. Used to scope the
`_mentions_tools` nudge.

#### d) Fixed `_mentions_tools` nudge condition
**Before:** triggered for ANY query where tool calls were made and the LLM
mentioned a tool name in its response text. This could cause infinite loops
for simple data checks (non-investigation queries).

**After:** only triggers when `start_investigation` was called but the
investigation is not yet complete.

Changed in both `process()` and `process_stream()`:
```python
# BEFORE
if (
    tool_calls_made
    and self._mentions_tools(content)
    and not self._investigation_completed(tool_calls_made)
):

# AFTER
if (
    self._investigation_started(tool_calls_made)
    and self._mentions_tools(content)
    and not self._investigation_completed(tool_calls_made)
):
```

#### e) Empty content retry (both `process` and `process_stream`)
When the LLM returns empty content after tool calls were made, the agent now
nudges the LLM to summarise instead of returning empty output:
```python
if not content.strip() and tool_calls_made:
    nudge = self._build_summarise_nudge(tool_calls_made)
    self.conversation.add_assistant(content)
    self.conversation.add_user(nudge)
    continue
```

#### f) Debug logging
Added logging at each iteration showing:
- `response.content` type and length
- Whether tool_calls are present
- Warning when content is empty (includes `additional_kwargs` keys)

### 2. `ui/chat.py` — Empty response handling

When `assistant_message` is empty but tool calls were made, shows a warning
instead of blank space:
```python
if assistant_message and assistant_message.strip():
    st.markdown(assistant_message)
elif tool_calls:
    st.warning(
        "The LLM did not produce a text conclusion. "
        "Check the tool call results above for details."
    )
```

### 3. `docker-compose.yml` — Model config

Changed hardcoded model to use `.env` variable:
```yaml
# BEFORE
OLLAMA_MODEL: qwen2.5:7b

# AFTER
OLLAMA_MODEL: ${OLLAMA_MODEL:-qwen2.5:14b}
```

### 4. `.env` — Model upgrade

```
# BEFORE
OLLAMA_MODEL=qwen2.5:7b

# AFTER
OLLAMA_MODEL=qwen2.5:14b
```

## Reproduction Steps

1. Pull the new model:
   ```bash
   ollama pull qwen2.5:14b
   ```

2. Apply all code changes to `app/core/agent.py`, `ui/chat.py`,
   `docker-compose.yml`, and `.env` as described above.

3. Restart the backend (full restart required due to `@lru_cache` on settings):
   ```bash
   docker compose down && docker compose up -d
   # OR for local dev:
   # Stop uvicorn (Ctrl+C), then:
   uv run uvicorn main:app --reload
   ```

4. Verify with:
   ```bash
   uv run pytest tests/ -x -q
   uv run ruff check app/core/agent.py ui/chat.py
   ```

## Test Results

All 193 tests pass. No test changes were needed.
