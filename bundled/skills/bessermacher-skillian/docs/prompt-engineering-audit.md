# Prompt Engineering Audit

An assessment of Skillian's prompting approach against industry best practices from Anthropic, OpenAI, Google, and Learn Prompting.

---

## Sources Consulted

- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [OpenAI GPT-4.1 Prompting Guide](https://cookbook.openai.com/examples/gpt4-1_prompting_guide)
- [Google Prompt Design Strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- [Learn Prompting](https://learnprompting.org/docs/introduction)

---

## Summary Scorecard

| Best Practice | Status | Priority |
|---|---|---|
| Role Assignment | Done well | — |
| Clarity & Specificity | Done well | — |
| Persistence / Autonomy | Done well | — |
| Tool Descriptions | Done well | — |
| Error Recovery (Nudges) | Excellent | — |
| Deterministic Branching | Excellent | — |
| Few-Shot Examples | **Missing** | **High** |
| Structured Prompt Sections | **Partial** | **High** |
| Chain-of-Thought / Planning | **Missing** | **Medium** |
| RAG Context Injection | **Missing** | **Medium** |
| Output Format Specification | **Missing** | **Medium** |
| Negative Examples / Guardrails | **Minimal** | **Medium** |
| Context Placement Optimization | **Not optimized** | **Low** |
| Provider-Specific Adaptation | **Missing** | **Low** |

---

## What We Do Well

### 1. Role Assignment

The system prompt clearly establishes identity and domain expertise:

> "You are Skillian, an AI assistant specialized in diagnosing SAP BW data issues."

The skill-level prompts deepen this with specific personas:

> "You are an expert SAP data investigator."

**Best practice alignment:** All four sources recommend assigning specific roles via system instructions. Anthropic notes that a specific role turns the model from a general assistant into a virtual domain expert, enhancing accuracy and focus.

### 2. Explicit Tool-Use Instructions

The prompts are firm about autonomous tool execution:

> "CRITICAL: You MUST call tools at every step. Do NOT respond with text mid-investigation."

**Best practice alignment:** Matches OpenAI's agentic prompting pillar of explicit tool-calling instructions ("If unsure about content, use your tools to read files and gather information: do NOT guess") and Anthropic's guidance on being clear and direct.

### 3. Persistence / Autonomy

> "Always proceed with the full diagnostic autonomously. Do NOT ask the user for confirmation between steps."

**Best practice alignment:** Directly implements OpenAI's recommended agentic persistence pattern ("You are an agent — please keep going until the user's query is completely resolved"). OpenAI reports this instruction alone contributed to ~20% improvement on SWE-bench.

### 4. Structured Playbooks

The SKILL.md files contain numbered, step-by-step investigation playbooks with branching logic (if data found → end, if S_NONE → check ownership, if no data → check BPC mart).

**Best practice alignment:** Matches the universal recommendation to decompose complex tasks into subtasks and use prompt chaining. Anthropic recommends identifying subtasks, using clear handoffs, and having each subtask focus on a single goal.

### 5. Nudging / Error Recovery

The `app/core/agent.py` nudge system detects five categories of LLM misbehavior and corrects them mid-conversation:

| Check | Nudge |
|---|---|
| Malformed tool calls | "Your tool calls were malformed, retry with correct JSON" |
| Tool calls as text | "Do NOT output tool call JSON as text, use proper tool calling" |
| Incomplete investigation | Context-aware nudge pointing to the next required step |
| Tool mentions in text | "Do NOT explain, call the tool NOW" |
| Empty response | Builds a nudge containing all tool results and asks LLM to summarise |

**Best practice alignment:** Goes beyond what most guides recommend. Implements error recovery patterns from OpenAI (fallback behavior) and Google (descriptive error messages that help the model understand what went wrong).

### 6. Detailed Tool Descriptions

Each tool in `tools.yaml` has thorough descriptions explaining what it does, what it returns, and when to use it. Parameters include types, required flags, and descriptive text.

**Best practice alignment:** Matches the universal guideline to design tool descriptions carefully with clear names, thorough descriptions, and strong-typed parameters.

### 7. Field Aliasing Documentation

The data_availability skill documents user-facing names vs. technical column names:

> "Company Code = CoCd = ZCOMPCODE"

**Best practice alignment:** Reduces ambiguity — a core clarity principle across all sources. Anthropic specifically recommends treating the model like "a brilliant but very new employee who needs explicit instructions."

### 8. Deterministic Playbook Engine

The `app/core/playbook.py` auto-chaining removes reliance on the LLM for branching decisions, executing the entire investigation workflow programmatically.

**Best practice alignment:** Smart architectural choice that bypasses prompt limitations entirely. Aligns with OpenAI's recommendation to "offload burden from the model; use code where possible."

---

## Gaps and Recommendations

### 1. No Few-Shot Examples in Prompts — HIGH PRIORITY

**Issue:** None of the system prompts include concrete input/output examples. The SKILL.md files have example sections, but they are parsed as instructions, not formatted as few-shot demonstrations.

**Best practice:**
- **Anthropic:** Include 3-5 diverse, relevant examples wrapped in `<example>` tags. "More examples = better performance."
- **OpenAI:** Try zero-shot first, then add few-shot. Include examples in a dedicated "Examples" section for complex tool use.
- **Google:** "Prompts without few-shot examples are likely to be less effective." Recommend 2-5 varied, specific examples.
- **Learn Prompting:** Few-shot prompting serves as in-context learning where demonstrations condition subsequent responses.

**Impact:** The LLM must infer the expected format of `record_finding` arguments, investigation summaries, and tool call sequences purely from instructions. Examples would reduce hallucination and improve consistency.

**Recommendation:** Add 1-2 complete example interactions in each SKILL.md showing the exact tool call sequence and expected arguments. For instance:

```markdown
## Examples

<example>
User: "No actual data for CoCd 1110 in Dec 2024 in CM report"

Tool calls in sequence:
1. start_investigation(problem_description="No actual data for CoCd 1110 in Dec 2024",
   report_name="Consolidated Management PnL", company_code="1110",
   fiscal_period="2024012", version="001")
2. check_data_availability(table="CV_ZBC_AA61",
   filters={"ZCOMPCODE": "1110", "FISCPER": "2024012", "ZVERSION": "001"})
3. record_finding(step_name="Check reporting table",
   result_summary="Data found in CV_ZBC_AA61 for CoCd 1110, period 2024012, version 001. Scopes: S_LEGAL. Total CS_TRN_LC: 1,234,567.89",
   conclusion="Data exists with expected legal scope. Issue may be in report configuration.",
   tool_used="check_data_availability", status="normal")
4. get_investigation_summary()
</example>
```

### 2. No Structured Prompt Sections — HIGH PRIORITY

**Issue:** The system prompt in `app/core/agent.py` is flat prose. Skill prompts use Markdown headings but aren't consistently structured.

**Best practice:**
- **OpenAI:** Structure system prompts with clear sections: `# Role and Objective`, `# Instructions`, `# Reasoning Steps`, `# Output Format`, `# Examples`, `# Context`, `# Final Instructions`.
- **Anthropic:** Use XML tags (`<instructions>`, `<example>`, `<formatting>`) to structure both inputs and outputs.
- **Google:** Use `<role>`, `<instructions>`, `<constraints>` tags in system instruction templates.

**Recommendation:** Restructure the base system prompt:

```
# Role
You are Skillian, an AI assistant specialized in diagnosing SAP BW data issues.

# Instructions
You have access to tools that can query SAP BW data. Use these tools to help users:
- Analyze financial data (cost centers, profit centers, budgets)
- Investigate data discrepancies
- Generate reports and summaries

# Tool Usage Rules
- Always proceed with the full diagnostic autonomously
- Do NOT ask the user for confirmation between steps
- Call all necessary tools in sequence
- Execute ALL playbook steps via tool calls before producing a final text response

# Output Format
When presenting investigation results, use this structure:
## Problem: [one-sentence description]
## Findings: [numbered list with status indicators]
## Root Cause: [identified root cause or "Undetermined"]
## Recommended Actions: [bulleted list of next steps]

# Context
[skill domain prompts inserted here]
```

### 3. No Chain-of-Thought Guidance — MEDIUM PRIORITY

**Issue:** The prompts tell the LLM *what* to do but never ask it to *reason* before acting. There is no `<thinking>` step before tool calls.

**Best practice:**
- **Anthropic:** Three levels of CoT — basic ("think step-by-step"), guided (outline specific steps), structured (`<thinking>` and `<answer>` tags). Key principle: "Without outputting its thought process, no thinking occurs."
- **OpenAI:** "You MUST plan extensively before each function call, and reflect extensively on outcomes of previous function calls." This contributed to ~20% improvement on SWE-bench.
- **Google:** Request explicit planning: "Before answering, parse the goal into sub-tasks, verify information completeness."

**Impact:** The LLM may make incorrect branching decisions (e.g., wrong table lookup, misinterpreted parameters) because it isn't prompted to reason about the data before acting.

**Recommendation:** Add to the system prompt:

```
# Reasoning
Before each tool call, briefly reason about:
- What you expect to find and why
- Whether all required parameters are available
- Why this is the correct next step

After each tool result, reflect on what the result means before proceeding.
```

**Trade-off:** This increases latency and token usage. Consider enabling it selectively — e.g., only when the playbook is not auto-chaining (since auto-chaining already handles the reasoning deterministically).

### 4. RAG Not Integrated into Prompts — MEDIUM PRIORITY

**Issue:** The RAG pipeline exists (`app/rag/manager.py`) and knowledge is ingested, but it is never injected into the LLM context during conversations. It is only available via the `/knowledge/search` API endpoint.

**Best practice:**
- **Anthropic:** Place reference material at the **top** of prompts. "Longform data at the top can improve performance by up to 30%."
- **OpenAI:** "Provide reference text to reduce fabrication." Tune context reliance for domain-specific knowledge.
- **Google:** Emphasize grounding: "Your answer must be factual and fully truthful to the provided text."

**Impact:** The LLM relies entirely on its training data + static system prompt for SAP BW domain knowledge. The ingested SKILL.md knowledge files are effectively unused during inference.

**Recommendation:** Inject relevant RAG context into the conversation before instructions:

```python
# In agent._run_loop(), before the LLM call:
rag_context = rag_manager.get_context(user_message, k=3)
if rag_context:
    # Place context before instructions (Anthropic's recommendation)
    context_message = f"# Relevant Knowledge\n{rag_context}\n\nUse the above context to inform your response."
```

### 5. No Output Format Specification — MEDIUM PRIORITY

**Issue:** The prompts never specify what the final user-facing response should look like — structure, length, tone, or format.

**Best practice:**
- **OpenAI:** Models may add "excessive prose" without specific format instructions. Be explicit about format.
- **Anthropic:** Use XML tags to structure outputs. Tags enable easy post-processing.
- **Google:** Specify the format: tables, bulleted lists, JSON, paragraphs, summaries.
- **Learn Prompting:** Explicit format instructions reduce post-processing and prevent misunderstandings.

**Impact:** Investigation summaries vary in structure and verbosity across runs, making it harder for users to quickly parse results.

**Recommendation:** Add an output format section to the system prompt (see structured prompt sections recommendation above). At minimum:

```
When presenting investigation results:
- Start with a one-line problem statement
- List findings as a numbered list with [NORMAL], [ISSUE], or [CHECK] status tags
- State the root cause clearly
- End with specific recommended actions
- Keep the total response under 500 words
```

### 6. No Negative Examples / Guardrails — MEDIUM PRIORITY

**Issue:** The prompts tell the LLM what to do, but the only "don't" instructions relate to not stopping mid-investigation. There is no guidance on what NOT to do with tools.

**Best practice:**
- **Google:** Specify when NOT to use each tool. Validate high-consequence function calls with the user.
- **OpenAI:** Avoid "always" instructions without conditional logic — they cause hallucinated tool calls. Add: "If you don't have enough information to call the tool, ask the user."
- **Anthropic:** Include CoT instruction to validate parameters: "If a required parameter is missing, DO NOT invoke the function and instead ask the user."

**Recommendation:** Add explicit guardrails:

```
# Guardrails
- NEVER call check_data_availability without specifying a table name
- NEVER fabricate filter values — use only values from the user's query or previous tool results
- If the user's request is ambiguous about which company code or period, ASK before proceeding
- Do NOT call start_investigation for questions that don't involve data issues (e.g., general SAP questions)
- If a tool returns an error, report it clearly — do NOT retry with made-up parameters
```

### 7. Context Placement Could Be Optimized — LOW PRIORITY

**Issue:** The base system prompt puts instructions first, then skill domains are appended. Tool descriptions are separate (via `bind_tools`).

**Best practice:**
- **Anthropic:** Placing longform context **before** instructions can improve performance by up to 30%.
- **OpenAI:** Place instructions at both beginning and end of provided context, or prioritize placement above context.
- **Learn Prompting:** Place the directive last to ensure the AI focuses on the task after processing context.

**Recommendation:** For sessions with conversation history, consider placing a condensed instruction reminder at the end of the message list:

```python
# Before the final LLM call, add a brief instruction reminder
if len(conversation.messages) > 10:
    reminder = "Remember: execute tools directly, do not explain what you will do."
    # Append as a system message or embed in the last user message
```

### 8. No Provider-Specific Prompt Adaptation — LOW PRIORITY

**Issue:** The same prompt is used for all LLM providers (Ollama, Anthropic, OpenAI, custom).

**Best practice:**
- **OpenAI:** GPT-4.1 follows instructions more literally; implicit inferences are less reliable.
- **Anthropic:** Claude responds well to XML tags for structuring prompts and outputs.
- **Google:** Gemini needs explicit grounding instructions and works best with temperature at 1.0.

**Impact:** A prompt optimized for Claude may underperform on GPT-4 or Llama, and vice versa.

**Recommendation:** At minimum, adapt formatting per provider:

```python
# In agent.py or a new prompt_builder.py
def format_system_prompt(base_prompt: str, provider: str) -> str:
    if provider == "anthropic":
        # Claude responds well to XML tags
        return f"<role>{role}</role>\n<instructions>{instructions}</instructions>"
    elif provider in ("openai", "custom_openai"):
        # GPT models respond well to Markdown headers
        return f"# Role\n{role}\n\n# Instructions\n{instructions}"
    else:
        # Default: plain text for local models
        return base_prompt
```

---

## Best Practices Reference

### Universal Principles (Consensus Across All Sources)

1. **Be explicit and specific** — never assume the model understands implicit context. Provide clear, detailed instructions with desired format, length, tone, and style.

2. **Use structured formatting** — XML tags (Anthropic/Google), Markdown headers (OpenAI), or consistent delimiters to separate instructions, context, examples, and output specifications.

3. **Include few-shot examples** — 3-5 diverse, relevant examples dramatically improve output consistency and quality. Wrap them in clear delimiters.

4. **Chain-of-thought for complex reasoning** — prompt the model to think step-by-step for multi-step analysis, math, or decisions. Use structured CoT (with `<thinking>` tags) for best results. Exception: OpenAI's o-series reasoning models should NOT be given CoT prompts.

5. **Decompose complex tasks** — break large tasks into smaller subtasks, either through prompt chaining or structured workflows. Run independent subtasks in parallel.

6. **Place context before instructions** — put large documents and reference material at the top of the prompt, with your query and instructions at the end.

7. **Design tool descriptions carefully** — provide clear names, thorough descriptions, strong-typed parameters, and explicit usage guidance. Include when to use (and NOT use) each tool.

8. **Handle errors gracefully** — instruct the model to ask for clarification when parameters are missing rather than guessing. Include fallback behaviors and scope limitations. Return descriptive error messages from tool calls.

9. **Iterate and test systematically** — start simple, change one element at a time, measure against success criteria, and refine.

10. **Assign a specific role/persona** — role prompting via system instructions consistently improves accuracy, focus, and tone across all providers and model families.

### Tool / Function Calling Best Practices

- Use the API tools field exclusively rather than manually injecting tool descriptions into prompts (OpenAI: showed 2% improvement).
- Provide a CoT prompt for tool use with smaller models: "Before calling a tool, think about which tool is relevant and whether all required parameters are present" (Anthropic).
- Use enums and object structure to make invalid states unrepresentable (OpenAI).
- Explicitly outline the order of tool calls for complex tasks (OpenAI).
- Add explicit instructions about when to use each tool and when NOT to (Google).
- Implement validation and error handling that returns descriptive error messages (Google).

### Agent / Agentic Patterns

- Three essential agentic prompting components: **Persistence**, **Tool-calling**, **Planning** (OpenAI).
- Planning explicitly increases pass rates by ~4% on agentic benchmarks (OpenAI).
- For complex problem-solving: understand → investigate → plan → implement → debug → test → iterate → reflect (OpenAI).
- Use `contextvars` for request-scoped state isolation in concurrent scenarios (Anthropic).
- Agent development is iterative: start simple, test often, refine (Google).
