# Agent Architecture

This document explains how the Skillian agent works end-to-end: how skills are defined and loaded, how the agent loop processes requests, and how tools are executed.

---

## Overview

Skillian follows a simple pipeline:

```
User message
    → Agent receives message
    → LLM decides which tools to call
    → Agent executes tools
    → LLM summarises results
    → Response returned to user
```

The agent is a **ReAct-style loop**: the LLM reasons about what to do, acts by calling tools, observes the results, and repeats until it has a final answer. A **playbook** layer can bypass the LLM for deterministic multi-step workflows.

---

## Core Components

### 1. Skill (`app/core/skill.py`)

A **Skill** is a domain-specific capability. It is defined as a Protocol with these properties:

| Property | Type | Purpose |
|---|---|---|
| `name` | `str` | Unique identifier (e.g. `"data-investigation"`) |
| `description` | `str` | What the skill does |
| `tools` | `list[Tool]` | Callable functions the LLM can invoke |
| `system_prompt` | `str` | Domain instructions injected into the system message |
| `knowledge_paths` | `list[str]` | Paths to markdown docs for RAG ingestion |

Skills are implemented by `ConfiguredSkill` (`app/core/configured_skill.py`), a dataclass populated from config files rather than hand-written Python classes.

### 2. Tool (`app/core/tool.py`)

A **Tool** is a single callable function exposed to the LLM:

```python
@dataclass(frozen=True)
class Tool:
    name: str                        # Unique name across all skills
    description: str                 # Shown to LLM in tool schema
    function: Callable[..., Any]     # The implementation
    input_schema: type[BaseModel]    # Pydantic model for validation
```

Execution flow:
1. **Coerce** — fix common LLM type mistakes (`{}` → `[]`, `"123"` → `123`, etc.)
2. **Validate** — run through Pydantic schema
3. **Call** — invoke the function (supports both sync and async)

The `to_langchain_tool()` method converts the Tool to a dict with a JSON schema, which is what the LLM sees when deciding which tools to call.

### 3. SkillRegistry (`app/core/registry.py`)

The registry is the central index. It holds all skills and provides:

- **`register(skill)`** — adds a skill, rejects duplicate names or tool names
- **`get_tool(name)`** — routes a tool name to the correct skill and returns the Tool
- **`get_all_tools()`** — flat list of every tool from every skill
- **`get_combined_system_prompt()`** — merges all skill instructions into one prompt

The registry enforces **global tool name uniqueness** — no two skills can define a tool with the same name. This is critical because the LLM sees a flat list of tools with no skill prefix.

### 4. Conversation (`app/core/messages.py`)

A simple message list with four roles:

| Role | LangChain type | Purpose |
|---|---|---|
| `SYSTEM` | `SystemMessage` | Base prompt + all skill instructions |
| `USER` | `HumanMessage` | User input (and nudges) |
| `ASSISTANT` | `AIMessage` | LLM responses (may include tool calls) |
| `TOOL` | `ToolMessage` | Tool execution results |

The conversation is converted to LangChain message objects before each LLM call via `_convert_to_langchain_messages()`.

---

## Skill Loading Pipeline

Skills are loaded from the filesystem at startup. Each skill lives in its own directory under `app/skills/`.

### Directory Structure

```
app/skills/<skill_name>/
├── SKILL.md          # Metadata + instructions (required)
├── tools.yaml        # Tool definitions (required for tools)
├── tools.py          # Tool implementations (required for tools)
└── knowledge/        # Optional RAG documents
    └── *.md
```

### SKILL.md Format

Uses YAML frontmatter for metadata, followed by markdown sections for instructions:

```markdown
---
name: data-investigation
description: Orchestrate multi-step data investigations.
version: "1.0.0"
domain: sap
tags: [investigation, diagnostics]
connector: datasphere
---

Instructions for the LLM go here as markdown.

## Instructions

Detailed step-by-step instructions...

## Capabilities

- Capability one
- Capability two
```

The `skill_parser.py` module parses the frontmatter and extracts markdown sections (`Instructions`, `Capabilities`, `When to Use`, `Examples`) into structured data. The combined instructions become the skill's `system_prompt`.

### tools.yaml Format

```yaml
tools:
  - name: check_data_availability
    description: Check if data exists in a table for given filters.
    parameters:
      - name: table
        type: string
        required: true
        description: Table name
      - name: filters
        type: object
        required: false
        description: Column:value filter pairs
    implementation: app.skills.data_availability.tools:check_data_availability
```

Each tool definition specifies:
- **name** — unique tool name
- **description** — shown to the LLM
- **parameters** — typed, validated inputs (supports: `string`, `integer`, `number`, `boolean`, `array`, `object`, nested objects)
- **implementation** — `module.path:function_name` pointing to the Python function
- **query_template** (alternative) — SQL template with `{param}` placeholders for zero-code tools

### Loading Process (`app/core/skill_loader.py`)

```
SkillLoader.load_all_skills()
    → discover_skills()        # find dirs with SKILL.md
    → for each skill:
        → parse_skill_md()     # extract metadata + instructions
        → load_tools_from_yaml()  # parse YAML, build Pydantic schemas, load functions
        → build ConfiguredSkill
    → return list of skills
```

The `yaml_tools.py` module handles:
1. Parsing the YAML tool definitions
2. Building Pydantic input schemas dynamically via `create_model()`
3. Loading implementation functions via `importlib.import_module()`
4. Injecting connectors into tools that need them (detected by inspecting function signatures for a `connector` parameter)

---

## Agent Loop

The agent (`app/core/agent.py`) orchestrates the full request-response cycle.

### Initialisation

```python
Agent(chat_model, registry, max_iterations=15, llm_timeout=120.0, tool_timeout=60.0)
```

At init:
1. Collect all tools from the registry
2. Cache tool names as a `frozenset` for O(1) lookups
3. Bind tools to the LLM via `chat_model.bind_tools(langchain_tools)`
4. Build the system prompt: base prompt + `registry.get_combined_system_prompt()`
5. Create an `InvestigationPlaybook` instance

### The Loop (`_run_loop`)

Both `process()` (non-streaming) and `process_stream()` (streaming) delegate to a single `_run_loop()` async generator. This eliminates duplication — there is one loop, two thin wrappers.

```
_run_loop(user_message):
    add user message to conversation

    while iterations < max_iterations:
        yield "thinking" event

        convert conversation → LangChain messages
        call LLM (with timeout)
        yield "llm_response" event

        if LLM returned tool calls:
            record assistant message with tool calls
            for each tool call:
                yield "tool_call" event
                execute tool (with timeout)
                record tool result in conversation
                yield "tool_result" event

                if tool was "start_investigation":
                    run playbook auto-chain
                    yield events for chained tools

            continue  ← loop back for next LLM turn

        if no tool calls:
            extract text content
            check if nudge is needed
            if nudge:
                add nudge to conversation
                continue  ← loop back

            yield "text_delta" event
            yield "done" event
            return

    yield "done" with finished=False  ← max iterations reached
```

### Event Types

The loop yields SSE-style events:

| Event | When | Data |
|---|---|---|
| `thinking` | Start of each iteration | `{iteration}` |
| `llm_response` | After LLM call completes | `{iteration, duration_seconds}` |
| `tool_call` | Before tool execution | `{tool, args}` |
| `tool_result` | After tool execution | `{tool, result, duration_seconds}` |
| `text_delta` | Final text response ready | `{content}` |
| `done` | Loop finished | `{response, tool_calls, finished, timing}` |

### Timeouts

Both LLM calls and tool executions are wrapped with `asyncio.wait_for()`:

- **LLM timeout** (default 120s) — if the model takes too long, the loop yields `done` with a timeout error message
- **Tool timeout** (default 60s) — if a tool hangs, it returns a JSON error and the loop continues

---

## Nudge System

LLMs sometimes misbehave — they write tool calls as text, produce empty responses, or stop mid-investigation. The nudge system detects these cases and redirects the LLM.

The `_select_nudge()` method checks, in order:

| Check | Condition | Nudge |
|---|---|---|
| **Malformed tool calls** | `response.invalid_tool_calls` is non-empty | "Your tool calls were malformed, retry with correct JSON" |
| **Tool calls as text** | Response text contains `{"name": "<tool_name>"` patterns | "Do NOT output tool call JSON as text, use proper tool calling" |
| **Incomplete investigation** | `start_investigation` was called but `get_investigation_summary` was not | Context-aware nudge pointing to the next step |
| **Tool mentions in text** | Investigation in progress + response text mentions tool names | "Do NOT explain, call the tool NOW" |
| **Empty response** | No text content after tool calls were made | Builds a nudge containing all tool results and asks LLM to summarise |

When a nudge is selected:
1. The current (bad) LLM response is added as an assistant message
2. The nudge is added as a user message
3. The loop continues to the next iteration

This is invisible to the actual user — nudges appear as internal user messages in the conversation.

---

## Investigation Playbook (`app/core/playbook.py`)

The playbook provides **deterministic auto-chaining** for investigation workflows. Instead of relying on the LLM to decide each next step (which is unreliable), the playbook executes the entire workflow programmatically.

### How It Works

After every tool call, the agent calls `playbook.try_auto_chain(tool_name, result, execute_callback)`. The playbook only activates when `tool_name == "start_investigation"`.

### Execution Flow

```
start_investigation returns → playbook takes over

Step 1: check_data_availability on reporting table
    → parse result: data_found? scopes?

Branch A: Data found with legal scope (S_LEGAL, S_LEGAL_DKK, S_LEGAL_SPECIAL)
    → record_finding (status: normal)
    → END

Branch B: Data found but only S_NONE scope
    → record_finding (status: needs_further_check)
    → check_ownership
    → record_finding based on ownership result
    → END

Branch C: No data found
    → record_finding (status: needs_further_check)
    → check_data_availability on BPC mart (CV_ZFI_AA01)
    → record_finding based on BPC result
    → END

Branch D: Mixed/unknown scopes
    → record_finding (status: needs_further_check)
    → END

Always: get_investigation_summary
```

### Decoupling from the Agent

The playbook has no dependency on the Agent class. It receives a `ToolExecutor` callback:

```python
ToolExecutor = Callable[[str, dict[str, Any]], Awaitable[str]]
```

The agent provides `_auto_execute_tool` as this callback, which:
1. Adds an assistant message with the tool call to the conversation
2. Executes the tool with timeout tracking
3. Adds the tool result to the conversation
4. Returns the result string

This means the playbook's tool calls appear in the conversation just like LLM-initiated tool calls — the LLM sees the full history when it takes back over to produce the final summary.

---

## Request Lifecycle (End-to-End)

Here is a complete request from API to response:

```
1. POST /api/v1/chat { message: "..." }
    │
2. Route handler gets Agent (new per request)
    │
3. agent.process(message)
    │
4. _run_loop starts
    │
5. LLM call #1: model sees system prompt + user message
    │  → LLM returns: call start_investigation(...)
    │
6. Execute start_investigation → returns {next_step: {table, filters}}
    │
7. Playbook auto-chains:
    │  → check_data_availability(table, filters)
    │  → record_finding(...)
    │  → [branch-dependent tools]
    │  → get_investigation_summary()
    │
8. Loop continues → LLM call #2
    │  LLM sees: system prompt + user message + all tool calls/results
    │  → LLM returns: text summary of findings
    │
9. No nudge needed → yield text_delta + done
    │
10. AgentResponse returned with content + tool_calls + timing
    │
11. Response serialised as JSON back to client
```

---

## Timing

Every request is instrumented:

```python
timing = {
    "total_seconds": 4.231,        # end-to-end duration
    "llm_calls": [
        {"iteration": 1, "duration_seconds": 1.2},
        {"iteration": 2, "duration_seconds": 0.8},
    ],
    "tool_calls": [
        {"tool": "start_investigation", "duration_seconds": 0.01},
        {"tool": "check_data_availability", "duration_seconds": 0.5},
        {"tool": "record_finding", "duration_seconds": 0.01},
        {"tool": "get_investigation_summary", "duration_seconds": 0.01},
    ],
}
```

---

## Configuration

Key settings from `app/config.py`:

| Setting | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | LLM backend: ollama, anthropic, openai, custom_openai |
| `LLM_TIMEOUT` | `120` | Seconds before LLM call times out |
| `TOOL_TIMEOUT` | `60` | Seconds before tool execution times out |
| `MAX_ITERATIONS` | `15` | Maximum agent loop iterations |

---

## Dependency Wiring (`app/dependencies.py`)

Singletons (cached via `@lru_cache`):
- LLM provider → chat model
- Business database connector
- Datasphere connector
- Skill loader (receives connectors)
- Skill registry (receives loaded skills)
- Vector store + RAG manager

Per-request:
- Agent (needs fresh conversation state)
- Session store (async generator)

```
Config
  → LLM Provider → Chat Model ──────────────────┐
  → Connectors → Skill Loader → Skill Registry ──┤
                                                  ▼
                                               Agent
```

---

## Adding a New Skill

1. Create `app/skills/<name>/SKILL.md` with frontmatter and instructions
2. Create `app/skills/<name>/tools.yaml` with tool definitions
3. Create `app/skills/<name>/tools.py` with implementations
4. Optionally add `knowledge/*.md` for RAG

The skill will be discovered and loaded automatically at startup. No registration code needed.

### Checklist

- [ ] Tool names are globally unique (no collision with other skills)
- [ ] `SKILL.md` has `name` and `description` in frontmatter
- [ ] `tools.yaml` `implementation` paths use `module.path:function_name` format
- [ ] Tool functions accept the parameters defined in `tools.yaml`
- [ ] If the tool needs a database connector, include a `connector` parameter in the function signature
