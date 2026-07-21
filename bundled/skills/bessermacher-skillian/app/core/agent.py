"""Main agent orchestration."""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from app.core.messages import Conversation, Message, MessageRole
from app.core.playbook import InvestigationPlaybook
from app.core.registry import SkillRegistry

if TYPE_CHECKING:
    from app.rag import RAGManager

logger = logging.getLogger(__name__)

_TOOL_CALL_NUDGE = (
    "You appear to have described tool calls in your text response instead of "
    "invoking them. Do NOT output tool call JSON as text. You MUST use the "
    "proper tool calling mechanism to invoke tools. Please proceed with the "
    "investigation by making the actual tool calls now."
)

_CONTINUE_NUDGE = (
    "You described what you intend to do instead of actually doing it. "
    "Do NOT explain or narrate — call the tool NOW. "
    "Use the structured tool calling mechanism to invoke the next tool."
)

_INVESTIGATION_NUDGE_PREFIX = (
    "Do NOT start a new investigation — continue the current one. "
    "Do NOT respond with text until the workflow is complete. "
)


@dataclass
class AgentResponse:
    """Response from agent processing."""

    content: str
    tool_calls_made: list[dict[str, Any]] = field(default_factory=list)
    finished: bool = True
    timing: dict[str, Any] = field(default_factory=dict)


class Agent:
    """Main agent for processing user queries with skills.

    The agent:
    1. Binds all skill tools to the LLM
    2. Processes user messages via a unified event loop
    3. Executes tool calls when requested by LLM
    4. Returns responses to the user

    Example:
        agent = Agent(chat_model, registry)
        response = await agent.process("What's the budget for CC-1001?")
        print(response.content)
    """

    def __init__(
        self,
        chat_model: BaseChatModel,
        registry: SkillRegistry,
        max_iterations: int = 15,
        llm_timeout: float = 120.0,
        tool_timeout: float = 60.0,
        rag_manager: RAGManager | None = None,
    ):
        """Initialize the agent.

        Args:
            chat_model: LangChain chat model to use.
            registry: Skill registry with available tools.
            max_iterations: Maximum tool call iterations to prevent loops.
            llm_timeout: Timeout in seconds for each LLM call.
            tool_timeout: Timeout in seconds for each tool execution.
            rag_manager: Optional RAG manager for context retrieval.
        """
        self.registry = registry
        self.max_iterations = max_iterations
        self.llm_timeout = llm_timeout
        self.tool_timeout = tool_timeout
        self._rag_manager = rag_manager
        self.conversation = Conversation()

        # Cache tool names for O(1) lookups
        tools = registry.get_all_tools()
        self._tool_names: frozenset[str] = frozenset(t.name for t in tools)

        # Bind tools to the model
        if tools:
            langchain_tools = [t.to_langchain_tool() for t in tools]
            self.model = chat_model.bind_tools(langchain_tools)
        else:
            self.model = chat_model

        # Investigation playbook for deterministic auto-chaining
        self._playbook = InvestigationPlaybook()

        # Set up system prompt
        self._setup_system_prompt()

    def _setup_system_prompt(self) -> None:
        """Set up the system prompt with skill context."""
        base_prompt = """\
# Role

You are Skillian, an AI assistant specialized in diagnosing SAP BW data issues.

# Instructions

You have access to tools that can query SAP BW data. Use these tools to help users:
- Analyze financial data (cost centers, profit centers, budgets)
- Investigate data discrepancies
- Generate reports and summaries

When asked about data, use the appropriate tools to fetch real information.
Be concise and accurate in your responses.

# Tool Usage Rules

- Always proceed with the full diagnostic autonomously. Do NOT ask the user for \
confirmation between steps.
- Call all necessary tools in sequence and present the final findings when done.
- When investigating data issues, you MUST execute every playbook step by calling \
the appropriate tools. Do NOT stop after a single tool call to summarize or \
explain — complete the entire investigation workflow via tool calls first, then \
present the final summary as text.
- If unsure about a parameter value, use your tools to gather information rather \
than guessing.

# Reasoning

Before each tool call, briefly consider:
- Whether all required parameters are available from the user's query or previous tool results
- Which tool is the correct next step in the workflow

After each tool result, reflect on what the result means before proceeding to \
the next step.

# Guardrails

- NEVER fabricate filter values (company codes, periods, versions). Use only \
values from the user's query or previous tool results.
- NEVER call check_data_availability without specifying a table name.
- If the user's request is ambiguous about which company code, period, or version, \
ask for clarification before starting an investigation.
- Do NOT call start_investigation for questions that are not about data issues \
(e.g., general SAP questions, explanations of terminology).
- If a tool returns an error, report it clearly to the user — do NOT retry with \
made-up parameters.

# Output Format

When presenting investigation results, use this structure:

**Problem:** One-sentence description of the reported issue.

**Findings:**
1. [NORMAL|ISSUE|CHECK] Finding description with exact values from tool results.
2. ...

**Root Cause:** Identified root cause, or "Undetermined — further investigation needed."

**Recommended Actions:**
- Specific next steps for the user.
"""
        skill_context = self.registry.get_combined_system_prompt()

        if skill_context:
            full_prompt = f"{base_prompt}\n# Skill Domains\n\n{skill_context}"
        else:
            full_prompt = base_prompt

        self.conversation.add(Message.system(full_prompt))

    def _convert_to_langchain_messages(self) -> list[BaseMessage]:
        """Convert conversation to LangChain message format."""
        lc_messages: list[BaseMessage] = []

        for msg in self.conversation.messages:
            match msg.role:
                case MessageRole.SYSTEM:
                    lc_messages.append(SystemMessage(content=msg.content))
                case MessageRole.USER:
                    lc_messages.append(HumanMessage(content=msg.content))
                case MessageRole.ASSISTANT:
                    if msg.tool_calls:
                        lc_messages.append(
                            AIMessage(content=msg.content, tool_calls=msg.tool_calls)
                        )
                    else:
                        lc_messages.append(AIMessage(content=msg.content))
                case MessageRole.TOOL:
                    lc_messages.append(
                        ToolMessage(content=msg.content, tool_call_id=msg.tool_call_id or "")
                    )

        return lc_messages

    async def _execute_tool(self, tool_name: str, tool_args: dict[str, Any]) -> str:
        """Execute a tool and return the result as a string.

        Includes timeout protection and structured error logging.
        """
        try:
            tool = self.registry.get_tool(tool_name)
            result = await asyncio.wait_for(
                tool.aexecute(**tool_args),
                timeout=self.tool_timeout,
            )

            if isinstance(result, str):
                return result
            return json.dumps(result, separators=(",", ":"), default=str)

        except TimeoutError:
            logger.error(
                "Tool '%s' timed out after %.1fs (args: %s)",
                tool_name,
                self.tool_timeout,
                tool_args,
            )
            return json.dumps({"error": f"Tool execution timed out after {self.tool_timeout}s"})

        except Exception:
            logger.exception("Tool '%s' execution failed (args: %s)", tool_name, tool_args)
            return json.dumps({"error": f"Tool '{tool_name}' failed unexpectedly"})

    def _mentions_tools(self, content: str) -> bool:
        """Check if text response mentions registered tool names."""
        if not content:
            return False
        content_lower = content.lower()
        return any(tool_name in content_lower for tool_name in self._tool_names)

    def _looks_like_tool_calls(self, content: str) -> bool:
        """Detect if LLM response text contains tool call JSON."""
        if not content or not self._tool_names:
            return False
        pattern = r'\{\s*"name"\s*:\s*"([^"]+)"'
        matches = re.findall(pattern, content)
        return any(match in self._tool_names for match in matches)

    def _investigation_incomplete(self, tool_calls_made: list[dict[str, Any]]) -> bool:
        """Check if an investigation was started but not completed."""
        tools_called = {tc["tool"] for tc in tool_calls_made}
        return (
            "start_investigation" in tools_called
            and "get_investigation_summary" not in tools_called
        )

    def _investigation_completed(self, tool_calls_made: list[dict[str, Any]]) -> bool:
        """Check if an investigation workflow was fully completed."""
        tools_called = {tc["tool"] for tc in tool_calls_made}
        return "start_investigation" in tools_called and "get_investigation_summary" in tools_called

    @staticmethod
    def _extract_content(response: AIMessage) -> str:
        """Extract text content from an LLM response with provider fallbacks."""
        # Primary: string content
        if isinstance(response.content, str) and response.content.strip():
            return response.content

        # Fallback: list-type content blocks (Anthropic format)
        if isinstance(response.content, list):
            text_parts = []
            for block in response.content:
                if isinstance(block, str):
                    text_parts.append(block)
                elif isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            combined = "".join(text_parts)
            if combined.strip():
                return combined

        # Fallback: Ollama additional_kwargs
        kwargs = getattr(response, "additional_kwargs", {})
        if isinstance(kwargs.get("message"), dict):
            ollama_content = kwargs["message"].get("content", "")
            if ollama_content and ollama_content.strip():
                return ollama_content

        # Fallback: generic additional_kwargs.content
        if kwargs.get("content") and isinstance(kwargs["content"], str):
            if kwargs["content"].strip():
                return kwargs["content"]

        return response.content if isinstance(response.content, str) else ""

    @staticmethod
    def _build_summarise_nudge(tool_calls_made: list[dict[str, Any]]) -> str:
        """Build a nudge that includes actual tool results for the LLM to summarise."""
        parts = [
            "Your previous response was empty. Here are the tool results you "
            "need to summarise for the user:\n"
        ]
        for tc in tool_calls_made:
            parts.append(f"Tool: {tc['tool']}")
            parts.append(f"Args: {json.dumps(tc['args'], default=str)}")
            parts.append(f"Result: {tc['result']}\n")

        parts.append(
            "Provide a clear, concise text summary of these findings.\n"
            "Do NOT call any tools — just answer the user's question based on "
            "the results above."
        )
        return "\n".join(parts)

    def _investigation_started(self, tool_calls_made: list[dict[str, Any]]) -> bool:
        """Check if start_investigation was called."""
        return any(tc["tool"] == "start_investigation" for tc in tool_calls_made)

    def _select_nudge(
        self,
        content: str,
        response: Any,
        tool_calls_made: list[dict[str, Any]],
    ) -> str | None:
        """Return a nudge message if the LLM needs redirection, else None."""
        # Invalid (malformed) tool calls
        if hasattr(response, "invalid_tool_calls") and response.invalid_tool_calls:
            invalid_names = [tc.get("name", "unknown") for tc in response.invalid_tool_calls]
            logger.warning("LLM made invalid tool calls: %s. Nudging.", invalid_names)
            return (
                "Your tool call(s) were malformed and could not be parsed "
                f"(tools: {', '.join(invalid_names)}). Please retry the "
                "tool call(s) with correct JSON arguments."
            )

        # Tool calls written as text
        if self._looks_like_tool_calls(content):
            logger.warning("LLM output tool-call-like text. Nudging.")
            return _TOOL_CALL_NUDGE

        # Investigation started but not completed
        if self._investigation_incomplete(tool_calls_made):
            nudge = self._get_investigation_nudge(tool_calls_made)
            logger.warning("Investigation incomplete. Nudging: %s", nudge)
            return nudge

        # LLM described a tool call during investigation
        if (
            self._investigation_started(tool_calls_made)
            and self._mentions_tools(content)
            and not self._investigation_completed(tool_calls_made)
        ):
            logger.warning("LLM mentioned tools in text during investigation. Nudging.")
            return _CONTINUE_NUDGE

        # Empty content after tool calls
        if not content.strip() and tool_calls_made:
            return self._build_summarise_nudge(tool_calls_made)

        return None

    def _get_investigation_nudge(self, tool_calls_made: list[dict[str, Any]]) -> str:
        """Build a context-aware nudge based on investigation progress."""
        tools_called = {tc["tool"] for tc in tool_calls_made}

        if "check_data_availability" not in tools_called:
            return (
                _INVESTIGATION_NUDGE_PREFIX
                + "Call check_data_availability NOW using the table and filters "
                "from the next_step directive returned by start_investigation."
            )
        if "record_finding" not in tools_called:
            return (
                _INVESTIGATION_NUDGE_PREFIX
                + "Call record_finding NOW to record your analysis of the "
                "check_data_availability results."
            )
        return (
            _INVESTIGATION_NUDGE_PREFIX
            + "Call get_investigation_summary NOW to present the final results."
        )

    async def _track_tool_call(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        tool_calls_made: list[dict[str, Any]],
        tool_timings: list[dict[str, Any]],
    ) -> tuple[str, float]:
        """Execute a tool, record timing and call data. Returns (result, duration)."""
        tool_start = time.perf_counter()
        result = await self._execute_tool(tool_name, tool_args)
        duration = round(time.perf_counter() - tool_start, 3)

        tool_timings.append({"tool": tool_name, "duration_seconds": duration})
        tool_calls_made.append(
            {
                "tool": tool_name,
                "args": tool_args,
                "result": result,
                "duration_seconds": duration,
            }
        )
        return result, duration

    async def _auto_execute_tool(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        tool_calls_made: list[dict[str, Any]],
        tool_timings: list[dict[str, Any]],
    ) -> str:
        """Execute a tool as part of auto-chaining and track it."""
        call_id = f"auto_{tool_name}_{len(tool_calls_made)}"

        self.conversation.add_assistant(
            content="",
            tool_calls=[{"name": tool_name, "args": tool_args, "id": call_id}],
        )

        result, _ = await self._track_tool_call(tool_name, tool_args, tool_calls_made, tool_timings)
        self.conversation.add_tool_result(result, call_id)

        logger.info("Auto-chained %s", tool_name)
        return result

    # ------------------------------------------------------------------
    # Unified event loop
    # ------------------------------------------------------------------

    async def _run_loop(self, user_message: str) -> AsyncGenerator[dict]:
        """Core agent loop yielding SSE-style events.

        Both ``process()`` and ``process_stream()`` delegate to this
        single implementation, eliminating duplication.

        Yields dicts with keys: ``event`` (str), ``data`` (dict).
        The final event is always ``"done"``.
        """
        request_start = time.perf_counter()

        # Inject RAG context before the user message (first query only)
        if self._rag_manager is not None:
            try:
                rag_context = self._rag_manager.get_context(user_message, k=3)
                if rag_context:
                    self.conversation.add(
                        Message.system(
                            f"# Relevant Knowledge\n\n{rag_context}\n\n"
                            "Use the above context to inform your response."
                        )
                    )
            except Exception:
                logger.warning("RAG context retrieval failed", exc_info=True)

        self.conversation.add_user(user_message)

        tool_calls_made: list[dict[str, Any]] = []
        llm_timings: list[dict[str, Any]] = []
        tool_timings: list[dict[str, Any]] = []
        iterations = 0

        def _build_timing() -> dict[str, Any]:
            return {
                "total_seconds": round(time.perf_counter() - request_start, 3),
                "llm_calls": llm_timings,
                "tool_calls": tool_timings,
            }

        # Callback for the playbook to execute tracked tools
        async def _tracked_execute(name: str, args: dict[str, Any]) -> str:
            return await self._auto_execute_tool(
                name,
                args,
                tool_calls_made,
                tool_timings,
            )

        while iterations < self.max_iterations:
            iterations += 1

            yield {"event": "thinking", "data": {"iteration": iterations}}

            # --- LLM call with timeout ---
            lc_messages = self._convert_to_langchain_messages()
            llm_start = time.perf_counter()

            try:
                response = await asyncio.wait_for(
                    self.model.ainvoke(lc_messages),
                    timeout=self.llm_timeout,
                )
            except TimeoutError:
                logger.error(
                    "LLM call timed out after %.1fs on iteration %d",
                    self.llm_timeout,
                    iterations,
                )
                yield {
                    "event": "done",
                    "data": {
                        "response": "The AI model took too long to respond. Please try again.",
                        "tool_calls": tool_calls_made,
                        "finished": False,
                        "timing": _build_timing(),
                    },
                }
                return

            llm_duration = round(time.perf_counter() - llm_start, 3)
            llm_timings.append({"iteration": iterations, "duration_seconds": llm_duration})

            yield {
                "event": "llm_response",
                "data": {
                    "iteration": iterations,
                    "duration_seconds": llm_duration,
                },
            }

            # Debug logging
            has_tool_calls = hasattr(response, "tool_calls") and response.tool_calls
            logger.debug(
                "Iteration %d: content type=%s len=%d, tool_calls=%s",
                iterations,
                type(response.content).__name__,
                len(response.content) if isinstance(response.content, (str, list)) else 0,
                bool(has_tool_calls),
            )

            # --- Handle tool calls ---
            if has_tool_calls:
                self.conversation.add_assistant(
                    content=response.content or "",
                    tool_calls=response.tool_calls,
                )

                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    tool_id = tool_call["id"]

                    yield {
                        "event": "tool_call",
                        "data": {"tool": tool_name, "args": tool_args},
                    }

                    result, duration = await self._track_tool_call(
                        tool_name, tool_args, tool_calls_made, tool_timings
                    )
                    self.conversation.add_tool_result(result, tool_id)

                    yield {
                        "event": "tool_result",
                        "data": {
                            "tool": tool_name,
                            "result": result,
                            "duration_seconds": duration,
                        },
                    }

                    # Auto-chain: run full playbook if start_investigation
                    pre_chain_count = len(tool_calls_made)
                    chained = await self._playbook.try_auto_chain(
                        tool_name,
                        result,
                        _tracked_execute,
                    )
                    if chained:
                        for rec in tool_calls_made[pre_chain_count:]:
                            yield {
                                "event": "tool_call",
                                "data": {
                                    "tool": rec["tool"],
                                    "args": rec["args"],
                                },
                            }
                            yield {
                                "event": "tool_result",
                                "data": {
                                    "tool": rec["tool"],
                                    "result": rec["result"],
                                    "duration_seconds": rec["duration_seconds"],
                                },
                            }

                continue

            # --- No tool calls — check nudges ---
            content = self._extract_content(response)

            if not content.strip():
                logger.warning(
                    "Iteration %d: empty content. additional_kwargs keys: %s",
                    iterations,
                    list(getattr(response, "additional_kwargs", {}).keys()),
                )

            nudge = self._select_nudge(content, response, tool_calls_made)
            if nudge is not None:
                self.conversation.add_assistant(content)
                self.conversation.add_user(nudge)
                continue

            # --- Final response ---
            self.conversation.add_assistant(content)

            yield {"event": "text_delta", "data": {"content": content}}
            yield {
                "event": "done",
                "data": {
                    "response": content,
                    "tool_calls": tool_calls_made,
                    "finished": True,
                    "timing": _build_timing(),
                },
            }
            return

        # Max iterations reached
        yield {
            "event": "done",
            "data": {
                "response": "I couldn't complete the request within the allowed iterations.",
                "tool_calls": tool_calls_made,
                "finished": False,
                "timing": _build_timing(),
            },
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def process(self, user_message: str) -> AgentResponse:
        """Process a user message and return a response.

        Args:
            user_message: The user's input message.

        Returns:
            AgentResponse with the assistant's response.
        """
        last_event: dict | None = None
        async for event in self._run_loop(user_message):
            last_event = event

        if last_event is None or last_event.get("event") != "done":
            return AgentResponse(
                content="No response generated.",
                finished=False,
            )

        data = last_event["data"]
        return AgentResponse(
            content=data["response"],
            tool_calls_made=data["tool_calls"],
            finished=data["finished"],
            timing=data["timing"],
        )

    async def process_stream(self, user_message: str) -> AsyncGenerator[dict]:
        """Process a user message, yielding SSE events as work happens.

        Yields dicts with keys: event (str), data (dict).
        The final event is always "done".
        """
        async for event in self._run_loop(user_message):
            yield event

    def reset(self) -> None:
        """Reset the conversation, keeping only the system prompt."""
        system_msg = self.conversation.messages[0] if self.conversation.messages else None
        self.conversation.clear()
        if system_msg and system_msg.role == MessageRole.SYSTEM:
            self.conversation.add(system_msg)
