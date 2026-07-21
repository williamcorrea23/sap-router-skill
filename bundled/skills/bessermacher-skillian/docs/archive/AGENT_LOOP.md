# Agent Loop: How the AI "Thinks"

This document explains the agent orchestration loop - how Skillian processes user messages, decides which tools to call, and generates responses.

## Table of Contents

1. [Overview](#overview)
2. [The ReAct Pattern](#the-react-pattern)
3. [Agent Orchestration Algorithm](#agent-orchestration-algorithm)
4. [Message Flow](#message-flow)
5. [Tool Execution](#tool-execution)
6. [Conversation State](#conversation-state)
7. [Error Handling](#error-handling)
8. [Example Walkthrough](#example-walkthrough)

---

## Overview

The Agent (`app/core/agent.py`) implements a **ReAct-style loop** (Reasoning + Acting):

1. **Receive** user message
2. **Think** - LLM decides what to do
3. **Act** - Execute tools if needed
4. **Observe** - Process tool results
5. **Repeat** until final response

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AGENT LOOP OVERVIEW                                   │
└─────────────────────────────────────────────────────────────────────────┘

User Question ──▶ Agent ──▶ LLM ──▶ Tool Call? ──▶ Execute ──▶ Back to LLM
                   ▲                    │
                   │                    │ No tool calls
                   │                    ▼
                   └──────────── Final Response
```

---

## The ReAct Pattern

Skillian uses the ReAct (Reasoning + Acting) pattern popularized by LangChain:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           ReAct CYCLE                                     │
└──────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │   REASON    │  LLM thinks about the question
    │  (Thought)  │  and decides what information
    └──────┬──────┘  is needed
           │
           ▼
    ┌─────────────┐
    │    ACT      │  LLM calls a tool with
    │  (Action)   │  specific parameters
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │   OBSERVE   │  Tool result is added
    │(Observation)│  to conversation
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │   REPEAT    │  LLM continues reasoning
    │   or END    │  or provides final answer
    └─────────────┘
```

---

## Agent Orchestration Algorithm

The main algorithm in `agent.process()`:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    AGENT PROCESS ALGORITHM                                │
└──────────────────────────────────────────────────────────────────────────┘

                          ┌───────────────────┐
                          │  User Message     │
                          │  Received         │
                          └─────────┬─────────┘
                                    │
                                    ▼
                          ┌───────────────────┐
                          │ Add to            │
                          │ Conversation      │
                          └─────────┬─────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           ▼                           │
        │                 ┌───────────────────┐                 │
        │                 │ Convert to        │                 │
        │    ITERATION    │ LangChain         │                 │
        │      LOOP       │ Messages          │                 │
        │   (max = 10)    └─────────┬─────────┘                 │
        │                           │                           │
        │                           ▼                           │
        │                 ┌───────────────────┐                 │
        │                 │ Call LLM          │                 │
        │                 │ model.ainvoke()   │                 │
        │                 └─────────┬─────────┘                 │
        │                           │                           │
        │                           ▼                           │
        │                 ┌───────────────────┐                 │
        │                 │ Has Tool Calls?   │                 │
        │                 └─────────┬─────────┘                 │
        │                           │                           │
        │              ┌────────────┴────────────┐              │
        │              │                         │              │
        │            YES                        NO              │
        │              │                         │              │
        │              ▼                         ▼              │
        │    ┌─────────────────┐      ┌─────────────────┐      │
        │    │ For each tool   │      │ Add Final       │      │
        │    │ call:           │      │ Response        │      │
        │    │ 1. Get tool     │      │ to Conversation │      │
        │    │ 2. Validate     │      └────────┬────────┘      │
        │    │ 3. Execute      │               │                │
        │    │ 4. Add result   │               │                │
        │    └────────┬────────┘               │                │
        │             │                        │                │
        │             │ (loop back)            │                │
        └─────────────┘                        │
                                               ▼
                                    ┌───────────────────┐
                                    │ Return            │
                                    │ AgentResponse     │
                                    └───────────────────┘
```

### Pseudocode

```python
async def process(self, user_message: str) -> AgentResponse:
    # 1. Add user message to conversation
    self.conversation.add_user(user_message)
    tool_calls_made = []

    # 2. Iteration loop (max 10 iterations)
    for iteration in range(self.max_iterations):

        # 3. Convert conversation to LangChain format
        messages = self._convert_to_langchain_messages()

        # 4. Call LLM with system prompt + conversation
        response = await self.model.ainvoke(messages)

        # 5. Check for tool calls
        if response.tool_calls:
            # 6. Execute each tool
            for tool_call in response.tool_calls:
                tool = self.registry.get_tool(tool_call["name"])
                result = await tool.aexecute(**tool_call["args"])

                # Add tool result to conversation
                self.conversation.add_tool_result(
                    json.dumps(result),
                    tool_call["id"]
                )
                tool_calls_made.append(...)

            # Loop back to step 3

        else:
            # 7. No tool calls - final response
            self.conversation.add_assistant(response.content)
            return AgentResponse(
                content=response.content,
                tool_calls_made=tool_calls_made,
                finished=True
            )

    # Max iterations exceeded
    return AgentResponse(
        content="Max iterations reached",
        finished=False
    )
```

---

## Message Flow

### How Messages Are Sent to the LLM

```
┌────────────────────────────────────────────────────────────────────────┐
│ MESSAGES TO LLM (Iteration 1)                                           │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ [SYSTEM]  You are Skillian, an AI assistant specialized in SAP BW      │
│           data analysis. You have access to tools for querying and     │
│           comparing data sources...                                     │
│                                                                         │
│           Available tools:                                              │
│           - list_sources: List all available data sources              │
│           - query_source: Query a single data source                   │
│           - compare_sources: Compare data between two sources          │
│                                                                         │
│ [USER]    Compare amounts between fi_reporting and bpc_reporting       │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ LLM RESPONSE                                                            │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ content: ""  (empty when calling tools)                                 │
│                                                                         │
│ tool_calls: [                                                           │
│   {                                                                     │
│     "id": "call_abc123",                                                │
│     "name": "compare_sources",                                          │
│     "args": {                                                           │
│       "source_a": "fi_reporting",                                       │
│       "source_b": "bpc_reporting",                                      │
│       "measure": "amount"                                               │
│     }                                                                   │
│   }                                                                     │
│ ]                                                                       │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

### After Tool Execution

```
┌────────────────────────────────────────────────────────────────────────┐
│ MESSAGES TO LLM (Iteration 2)                                           │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ [SYSTEM]    (same system prompt)                                        │
│                                                                         │
│ [USER]      Compare amounts between fi_reporting and bpc_reporting     │
│                                                                         │
│ [ASSISTANT] (tool_calls: compare_sources)                               │
│                                                                         │
│ [TOOL]      {                                                           │
│               "summary": {                                              │
│                 "total_rows": 90,                                       │
│                 "matches": 87,                                          │
│                 "minor_differences": 2,                                 │
│                 "major_differences": 1,                                 │
│                 "total_diff": 8000                                      │
│               },                                                        │
│               "top_differences": [...],                                 │
│               "interpretation": "Good alignment (96.7%)"                │
│             }                                                           │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ LLM RESPONSE (Final)                                                    │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ content: "The comparison between fi_reporting and bpc_reporting        │
│           shows excellent alignment with 96.7% of rows matching.       │
│                                                                         │
│           Summary:                                                      │
│           - Total rows compared: 90                                     │
│           - Perfect matches: 87                                         │
│           - Minor differences: 2                                        │
│           - Major differences: 1                                        │
│                                                                         │
│           The total difference is $8,000, which is within              │
│           acceptable thresholds..."                                     │
│                                                                         │
│ tool_calls: []  (empty - no more tools needed)                          │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Tool Execution

When the LLM decides to call a tool:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      TOOL EXECUTION ALGORITHM                             │
└──────────────────────────────────────────────────────────────────────────┘

              Tool Call: { name: "compare_sources",
                           args: { source_a: "fi_reporting", ... } }
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 1: REGISTRY LOOKUP                                                  │
│                                                                          │
│   registry.get_tool("compare_sources")                                  │
│                                                                          │
│   ┌─────────────────┐                                                   │
│   │  tool_index     │                                                   │
│   │  ─────────────  │                                                   │
│   │  "compare_      │───▶ "data_analyst" (skill name)                   │
│   │   sources"      │                                                   │
│   └─────────────────┘                                                   │
│            │                                                             │
│            ▼                                                             │
│   ┌─────────────────┐                                                   │
│   │  skills         │                                                   │
│   │  ─────────────  │                                                   │
│   │  "data_analyst" │───▶ DataAnalystSkill instance                     │
│   └─────────────────┘                                                   │
│            │                                                             │
│            ▼                                                             │
│   skill.get_tool("compare_sources") → Tool instance                     │
│                                                                          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 2: INPUT VALIDATION (Pydantic)                                      │
│                                                                          │
│   ┌─────────────────────────────────────────┐                           │
│   │  CompareSourcesInput.model_validate({   │                           │
│   │    "source_a": "fi_reporting",          │                           │
│   │    "source_b": "bpc_reporting",         │                           │
│   │    "measure": "amount"                  │                           │
│   │  })                                      │                           │
│   └─────────────────────────────────────────┘                           │
│                         │                                                │
│           ┌─────────────┴─────────────┐                                 │
│           │                           │                                 │
│        VALID                       INVALID                              │
│           │                           │                                 │
│           ▼                           ▼                                 │
│   Continue execution       Return validation error                      │
│                            as tool result                               │
│                                                                          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 3: ASYNC FUNCTION EXECUTION                                         │
│                                                                          │
│   result = await tool.aexecute(                                         │
│       source_a="fi_reporting",                                          │
│       source_b="bpc_reporting",                                         │
│       measure="amount"                                                  │
│   )                                                                      │
│                                                                          │
│   Internally calls:                                                      │
│   ┌─────────────────────────────────────────┐                           │
│   │  comparison_engine.compare(             │                           │
│   │    source_a_name="fi_reporting",        │                           │
│   │    source_b_name="bpc_reporting",       │                           │
│   │    measure="amount",                    │                           │
│   │    ...                                   │                           │
│   │  )                                       │                           │
│   └─────────────────────────────────────────┘                           │
│                                                                          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 4: RETURN RESULT                                                    │
│                                                                          │
│   Tool result serialized to JSON and added to conversation:             │
│                                                                          │
│   conversation.add_tool_result(                                         │
│       content=json.dumps(result),                                       │
│       tool_call_id="call_abc123"                                        │
│   )                                                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Conversation State

The `Conversation` class (`app/core/messages.py`) manages message history:

```python
class Message:
    role: MessageRole  # "system" | "user" | "assistant" | "tool"
    content: str
    tool_call_id: str | None       # For tool results
    tool_calls: list[dict] | None  # For assistant tool calls

class Conversation:
    messages: list[Message]

    def add_user(self, content: str) -> None
    def add_assistant(self, content: str, tool_calls: list | None = None) -> None
    def add_tool_result(self, content: str, tool_call_id: str) -> None
    def to_langchain_messages(self) -> list[BaseMessage]
```

### Message Role Mapping

| Role | LangChain Type | Purpose |
|------|----------------|---------|
| `system` | `SystemMessage` | Instructions and available tools |
| `user` | `HumanMessage` | User's question |
| `assistant` | `AIMessage` | LLM's response or tool calls |
| `tool` | `ToolMessage` | Tool execution results |

---

## Error Handling

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        ERROR HANDLING FLOW                                │
└──────────────────────────────────────────────────────────────────────────┘

                    Tool Execution
                         │
          ┌──────────────┼──────────────┐
          │              │              │
    Pydantic        Tool Function    Runtime
    Validation       Error           Error
          │              │              │
          ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   All errors are caught and returned as JSON tool result:           │
│                                                                      │
│   {                                                                  │
│     "error": true,                                                   │
│     "message": "Source 'invalid_source' not found",                 │
│     "available_sources": ["fi_reporting", "bpc_reporting", ...]     │
│   }                                                                  │
│                                                                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   Error JSON added to conversation as ToolMessage                   │
│                                                                      │
│   LLM sees error and can:                                           │
│     • Retry with corrected parameters                               │
│     • Inform user of the issue                                      │
│     • Try an alternative approach                                   │
│     • Ask user for clarification                                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Example Error Recovery

```
User: "Compare amounts between fi_reports and bpc"

LLM calls: compare_sources(source_a="fi_reports", ...)

Tool returns: {
    "error": true,
    "message": "Source 'fi_reports' not found",
    "available_sources": ["fi_reporting", "bpc_reporting"]
}

LLM sees error, retries: compare_sources(source_a="fi_reporting", ...)

Tool returns: { "summary": { ... }, "top_differences": [...] }

LLM: "The comparison shows..."
```

---

## Example Walkthrough

Complete example of a comparison request:

### User Message

```
"Compare the amount totals between fi_reporting and consolidation_mart
for company 1001 in period 202401"
```

### Iteration 1: LLM Decides to Call Tool

**Input to LLM:**
```
[SYSTEM] You are Skillian... (system prompt + tool descriptions)
[USER] Compare the amount totals between fi_reporting and consolidation_mart
       for company 1001 in period 202401
```

**LLM Output:**
```json
{
  "content": "",
  "tool_calls": [{
    "id": "call_xyz789",
    "name": "compare_sources",
    "args": {
      "source_a": "fi_reporting",
      "source_b": "consolidation_mart",
      "measure": "amount",
      "filters": {
        "company": "1001",
        "period": "202401"
      }
    }
  }]
}
```

### Tool Execution

```
1. Registry lookup: "compare_sources" → DataAnalystSkill

2. Pydantic validation: ✓ Valid

3. Execute compare_sources():
   └─▶ ComparisonEngine.compare()
       ├─▶ QueryEngine.query(fi_reporting, ...)
       │   └─▶ SQL: SELECT company, period, SUM(amount) FROM fi_reporting
       │           WHERE company = '1001' AND period = '202401'
       │           GROUP BY company, period
       ├─▶ QueryEngine.query(consolidation_mart, ...)
       │   └─▶ SQL: SELECT company, period, SUM(amount) FROM consolidation_mart
       │           WHERE company = '1001' AND period = '202401'
       │           GROUP BY company, period
       ├─▶ Align rows by (company, period)
       ├─▶ Calculate differences
       └─▶ Return ComparisonResult

4. Result added to conversation as ToolMessage
```

### Iteration 2: LLM Generates Final Response

**Input to LLM:**
```
[SYSTEM] ...
[USER] Compare the amount totals...
[ASSISTANT] (tool_call: compare_sources)
[TOOL] {
  "summary": {
    "total_rows": 1,
    "matches": 0,
    "minor_differences": 0,
    "major_differences": 1,
    "total_source_a": 1500000,
    "total_source_b": 1492000,
    "total_diff": 8000
  },
  "top_differences": [{
    "key": {"company": "1001", "period": "202401"},
    "source_a_value": 1500000,
    "source_b_value": 1492000,
    "absolute_diff": 8000,
    "percentage_diff": 0.53,
    "status": "major_diff"
  }],
  "interpretation": "1 row with major difference"
}
```

**LLM Output (Final Response):**
```
The comparison between fi_reporting and consolidation_mart for company 1001
in period 202401 shows a discrepancy:

**fi_reporting**: $1,500,000
**consolidation_mart**: $1,492,000
**Difference**: $8,000 (0.53%)

This is classified as a major difference (exceeds the 1% threshold).

Possible causes to investigate:
1. Timing differences in data loads
2. Missing transactions in consolidation
3. Rounding or currency conversion differences
```

### Final Agent Response

```python
AgentResponse(
    content="The comparison between fi_reporting and consolidation_mart...",
    tool_calls_made=[
        {
            "tool": "compare_sources",
            "args": {"source_a": "fi_reporting", ...},
            "result": {"summary": {...}, ...}
        }
    ],
    finished=True
)
```

---

## Key Files

| File | Purpose |
|------|---------|
| `app/core/agent.py` | Agent class with process() loop |
| `app/core/messages.py` | Conversation and Message classes |
| `app/core/registry.py` | Tool routing and lookup |
| `app/core/tool.py` | Tool execution and validation |

---

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_iterations` | 10 | Maximum tool call cycles |
| System prompt | Skill-defined | Combined from all registered skills |
| Tool binding | Automatic | All tools from registry bound to LLM |

---

## Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Overall system architecture
- [COMPARISON_ENGINE.md](./COMPARISON_ENGINE.md) - How data comparison works
