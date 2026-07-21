# Data Flow Diagrams

Visual reference for understanding how data flows through Skillian from request to response.

## Table of Contents

1. [Complete Request Flow](#complete-request-flow)
2. [Component Interaction Sequence](#component-interaction-sequence)
3. [Comparison Request Flow](#comparison-request-flow)
4. [Tool Execution Flow](#tool-execution-flow)
5. [Error Handling Flow](#error-handling-flow)

---

## Complete Request Flow

End-to-end flow of a user request through the system:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE REQUEST FLOW                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          Client Request                              │
│                       /chat or /sessions/{id}/chat                    │
└─────────────────┬───────────────────────────────────────────────────┘
                  │
                  ▼
        ┌─────────────────────┐
        │   FastAPI Route     │
        │  (routes.py)        │
        └────────┬────────────┘
                 │ DI: Depends
                 ▼
        ┌─────────────────────────────────────────┐
        │  Agent (dependency injection)            │
        │  ├─ Chat Model (from LLMProvider)        │
        │  ├─ Skill Registry                       │
        │  └─ System Prompt (all skills combined)  │
        └─────┬──────────────────────────────────┘
              │
              │ agent.process(user_message)
              │
              ▼
        ┌──────────────────────────────────────────────────────┐
        │          Agent Loop (max 10 iterations)               │
        │                                                        │
        │  1. Add user message to conversation                  │
        │  2. Call LLM with bound tools                         │
        │  3. Check for tool_calls in response                  │
        │     │                                                  │
        │     ├─ YES: Execute tool                             │
        │     │        │                                        │
        │     │        ▼                                        │
        │     │   ┌────────────────────────────────┐           │
        │     │   │ Tool Execution                 │           │
        │     │   │                                │           │
        │     │   │ compare_sources                │           │
        │     │   │   ├─ Get source defs           │           │
        │     │   │   ├─ Query both sources        │           │
        │     │   │   │  (QueryEngine → SQL →      │           │
        │     │   │   │   PostgreSQL)              │           │
        │     │   │   ├─ Align rows by dimensions  │           │
        │     │   │   ├─ Compare & classify        │           │
        │     │   │   ├─ Cache result              │           │
        │     │   │   └─ Format response           │           │
        │     │   └─────┬──────────────────────────┘           │
        │     │         │                                       │
        │     │         ▼                                       │
        │     │   Add tool result to conversation               │
        │     │   Loop back to step 2                           │
        │     │                                                  │
        │     └─ NO: Final LLM response                         │
        │            Break loop, return response                │
        │                                                        │
        └──────────┬───────────────────────────────────────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │  AgentResponse      │
        │  ├─ content         │
        │  ├─ tool_calls_made │
        │  └─ finished        │
        └────────┬────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │  ChatResponse JSON  │
        │  (API Schema)       │
        └────────┬────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │  HTTP Response      │
        │  (200 OK + JSON)    │
        └─────────────────────┘
```

---

## Component Interaction Sequence

Sequence diagram showing component interactions:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    COMPONENT INTERACTION SEQUENCE                         │
└──────────────────────────────────────────────────────────────────────────┘

   User        FastAPI       Agent      Registry    LLM       Tool     DB
    │            │             │           │         │          │        │
    │  POST /chat│             │           │         │          │        │
    │ ──────────>│             │           │         │          │        │
    │            │             │           │         │          │        │
    │            │ process()   │           │         │          │        │
    │            │────────────>│           │         │          │        │
    │            │             │           │         │          │        │
    │            │             │ get_all_  │         │          │        │
    │            │             │ tools()   │         │          │        │
    │            │             │──────────>│         │          │        │
    │            │             │<──────────│         │          │        │
    │            │             │           │         │          │        │
    │            │             │ bind_tools│         │          │        │
    │            │             │ & invoke  │         │          │        │
    │            │             │──────────────────-->│          │        │
    │            │             │                     │          │        │
    │            │             │   tool_calls:       │          │        │
    │            │             │   compare_sources   │          │        │
    │            │             │<────────────────────│          │        │
    │            │             │           │         │          │        │
    │            │             │ get_tool()│         │          │        │
    │            │             │──────────>│         │          │        │
    │            │             │<──────────│         │          │        │
    │            │             │           │         │          │        │
    │            │             │ execute() │         │          │        │
    │            │             │─────────────────────────────-->│        │
    │            │             │           │         │          │        │
    │            │             │           │         │          │ query  │
    │            │             │           │         │          │───────>│
    │            │             │           │         │          │<───────│
    │            │             │           │         │          │        │
    │            │             │  result   │         │          │        │
    │            │             │<───────────────────────────────│        │
    │            │             │           │         │          │        │
    │            │             │ invoke    │         │          │        │
    │            │             │ (with tool result)  │          │        │
    │            │             │──────────────────-->│          │        │
    │            │             │                     │          │        │
    │            │             │   final response    │          │        │
    │            │             │<────────────────────│          │        │
    │            │             │           │         │          │        │
    │            │ AgentResp.  │           │         │          │        │
    │            │<────────────│           │         │          │        │
    │            │             │           │         │          │        │
    │  ChatResp. │             │           │         │          │        │
    │<───────────│             │           │         │          │        │
    │            │             │           │         │          │        │
```

---

## Comparison Request Flow

Detailed flow for a data comparison request:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    COMPARISON REQUEST FLOW                                │
└──────────────────────────────────────────────────────────────────────────┘

User: "Compare amounts between fi_reporting and bpc_reporting for company 1001"
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   Agent receives message      │
                    │   Adds to conversation        │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   LLM processes with:         │
                    │   - System prompt             │
                    │   - Available tools           │
                    │   - Conversation history      │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   LLM decides:                │
                    │   Call compare_sources        │
                    │   {                           │
                    │     source_a: "fi_reporting", │
                    │     source_b: "bpc_reporting",│
                    │     measure: "amount",        │
                    │     filters: {company: "1001"}│
                    │   }                           │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
        ┌───────────────────────────────────────────────────────────┐
        │                   compare_sources Tool                     │
        │                                                            │
        │   ┌────────────────────────────────────────────────────┐  │
        │   │ 1. Validate inputs (Pydantic)                      │  │
        │   └────────────────────┬───────────────────────────────┘  │
        │                        │                                   │
        │   ┌────────────────────▼───────────────────────────────┐  │
        │   │ 2. Call ComparisonEngine.compare()                 │  │
        │   │    ┌─────────────────────────────────────────────┐ │  │
        │   │    │ a. Generate cache key (MD5)                 │ │  │
        │   │    │ b. Check cache (miss)                       │ │  │
        │   │    │ c. Get source definitions from registry     │ │  │
        │   │    │ d. Query both sources:                      │ │  │
        │   │    │    ┌────────────────────────────────────┐   │ │  │
        │   │    │    │ QueryEngine.query(fi_reporting)    │   │ │  │
        │   │    │    │   → SQL: SELECT company, period,   │   │ │  │
        │   │    │    │          SUM(amount) FROM ...      │   │ │  │
        │   │    │    │   → PostgresConnector.execute()    │   │ │  │
        │   │    │    │   → Result rows                    │   │ │  │
        │   │    │    └────────────────────────────────────┘   │ │  │
        │   │    │    ┌────────────────────────────────────┐   │ │  │
        │   │    │    │ QueryEngine.query(bpc_reporting)   │   │ │  │
        │   │    │    │   → (same pattern)                 │   │ │  │
        │   │    │    └────────────────────────────────────┘   │ │  │
        │   │    │ e. Align rows by (company, period)          │ │  │
        │   │    │    - Build lookup dictionaries              │ │  │
        │   │    │    - Get union of all keys                  │ │  │
        │   │    │ f. Compare each aligned row:                │ │  │
        │   │    │    - Calculate absolute_diff                │ │  │
        │   │    │    - Calculate percentage_diff              │ │  │
        │   │    │    - Classify: match/minor/major            │ │  │
        │   │    │ g. Calculate summary statistics             │ │  │
        │   │    │ h. Cache result (TTL: 1 hour)               │ │  │
        │   │    └─────────────────────────────────────────────┘ │  │
        │   └────────────────────┬───────────────────────────────┘  │
        │                        │                                   │
        │   ┌────────────────────▼───────────────────────────────┐  │
        │   │ 3. Format result for LLM:                          │  │
        │   │    {                                                │  │
        │   │      summary: {...},                                │  │
        │   │      top_differences: [...],                        │  │
        │   │      interpretation: "96.7% match..."               │  │
        │   │    }                                                │  │
        │   └────────────────────────────────────────────────────┘  │
        └───────────────────────────┬───────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   Tool result added to        │
                    │   conversation as ToolMessage │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   LLM processes tool result   │
                    │   Generates human-readable    │
                    │   explanation                 │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   Final response:             │
                    │   "The comparison shows       │
                    │    96.7% alignment between    │
                    │    fi_reporting and           │
                    │    bpc_reporting..."          │
                    └───────────────────────────────┘
```

---

## Tool Execution Flow

How tools are discovered, validated, and executed:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    TOOL EXECUTION FLOW                                    │
└──────────────────────────────────────────────────────────────────────────┘

              Tool Call from LLM:
              { name: "compare_sources", args: {...} }
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 1: REGISTRY LOOKUP                                                  │
│                                                                          │
│   registry.get_tool("compare_sources")                                  │
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                     Skill Registry                                │  │
│   │                                                                   │  │
│   │   _tool_index (fast lookup):                                     │  │
│   │   ┌────────────────────────────────────────────────────────────┐ │  │
│   │   │  "list_sources"     → "data_analyst"                       │ │  │
│   │   │  "query_source"     → "data_analyst"                       │ │  │
│   │   │  "compare_sources"  → "data_analyst"  ◄── MATCH            │ │  │
│   │   └────────────────────────────────────────────────────────────┘ │  │
│   │                              │                                    │  │
│   │                              ▼                                    │  │
│   │   _skills:                                                        │  │
│   │   ┌────────────────────────────────────────────────────────────┐ │  │
│   │   │  "data_analyst" → DataAnalystSkill instance                │ │  │
│   │   └────────────────────────────────────────────────────────────┘ │  │
│   │                              │                                    │  │
│   │                              ▼                                    │  │
│   │   skill.get_tool("compare_sources") → Tool object               │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 2: INPUT VALIDATION                                                 │
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  CompareSourcesInput.model_validate({                            │  │
│   │    "source_a": "fi_reporting",                                   │  │
│   │    "source_b": "bpc_reporting",                                  │  │
│   │    "measure": "amount",                                          │  │
│   │    "filters": {"company": "1001"}                                │  │
│   │  })                                                               │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                         │                                                │
│           ┌─────────────┴─────────────┐                                 │
│           │                           │                                 │
│        VALID                       INVALID                              │
│           │                           │                                 │
│           ▼                           ▼                                 │
│   Continue              Return error as tool result:                    │
│                         {"error": true, "message": "..."}               │
│                                                                          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 3: ASYNC EXECUTION                                                  │
│                                                                          │
│   result = await tool.aexecute(                                         │
│       source_a="fi_reporting",                                          │
│       source_b="bpc_reporting",                                         │
│       measure="amount",                                                 │
│       filters={"company": "1001"}                                       │
│   )                                                                      │
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  Internally calls:                                                │  │
│   │  comparison_engine.compare(                                       │  │
│   │    source_a_name="fi_reporting",                                  │  │
│   │    source_b_name="bpc_reporting",                                 │  │
│   │    measure="amount",                                              │  │
│   │    filters={"company": "1001"}                                    │  │
│   │  )                                                                 │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 4: RESULT HANDLING                                                  │
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  Tool result serialized to JSON:                                  │  │
│   │  {                                                                 │  │
│   │    "summary": {                                                    │  │
│   │      "total_rows": 90,                                             │  │
│   │      "matches": 87,                                                │  │
│   │      "major_differences": 3,                                       │  │
│   │      ...                                                           │  │
│   │    },                                                              │  │
│   │    "top_differences": [...],                                       │  │
│   │    "cache_key": "abc123..."                                        │  │
│   │  }                                                                 │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                         │                                                │
│                         ▼                                                │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  conversation.add_tool_result(                                    │  │
│   │      content=json_result,                                         │  │
│   │      tool_call_id="call_xyz789"                                   │  │
│   │  )                                                                 │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Error Handling Flow

How errors are captured and returned to the LLM:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        ERROR HANDLING FLOW                                │
└──────────────────────────────────────────────────────────────────────────┘

                    Tool Execution
                         │
          ┌──────────────┼──────────────┬──────────────┐
          │              │              │              │
    Pydantic        Source Not     Query          Runtime
    Validation      Found          Error          Error
          │              │              │              │
          ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   All Errors Caught in try/except                        │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  Validation Error:                                               │   │
│   │  {                                                               │   │
│   │    "error": true,                                                │   │
│   │    "type": "validation_error",                                   │   │
│   │    "message": "Missing required field: measure"                  │   │
│   │  }                                                               │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  Source Not Found:                                               │   │
│   │  {                                                               │   │
│   │    "error": true,                                                │   │
│   │    "type": "not_found",                                          │   │
│   │    "message": "Source 'fi_reports' not found",                   │   │
│   │    "available_sources": ["fi_reporting", "bpc_reporting", ...]   │   │
│   │  }                                                               │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  Query Error:                                                    │   │
│   │  {                                                               │   │
│   │    "error": true,                                                │   │
│   │    "type": "query_error",                                        │   │
│   │    "message": "Database connection failed"                       │   │
│   │  }                                                               │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   Error JSON added to conversation as ToolMessage                       │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                   LLM Sees Error                                 │   │
│   │                                                                   │   │
│   │   Options:                                                        │   │
│   │   1. Retry with corrected parameters                             │   │
│   │      "fi_reports" → "fi_reporting"                               │   │
│   │                                                                   │   │
│   │   2. Inform user of the issue                                    │   │
│   │      "I couldn't find a source called 'fi_reports'.              │   │
│   │       Did you mean 'fi_reporting'?"                              │   │
│   │                                                                   │   │
│   │   3. Try alternative approach                                    │   │
│   │      Use list_sources first to find available sources            │   │
│   │                                                                   │   │
│   │   4. Ask user for clarification                                  │   │
│   │      "Which data source would you like to use?"                  │   │
│   │                                                                   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘


                    Example Error Recovery:

User: "Compare amounts between fi_reports and bpc"
                         │
                         ▼
LLM calls: compare_sources(source_a="fi_reports", ...)
                         │
                         ▼
Tool returns: {"error": true, "message": "Source 'fi_reports' not found",
               "available_sources": ["fi_reporting", "bpc_reporting"]}
                         │
                         ▼
LLM sees error and retries: compare_sources(source_a="fi_reporting", ...)
                         │
                         ▼
Tool returns: {"summary": {...}, "top_differences": [...]}
                         │
                         ▼
LLM: "The comparison shows..."
```

---

## Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Overall system architecture
- [AGENT_LOOP.md](./AGENT_LOOP.md) - How the AI orchestration works
- [COMPARISON_ENGINE.md](./COMPARISON_ENGINE.md) - Comparison algorithm details
