"""Tests for Agent."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

from app.core import Agent, ConfiguredSkill, SkillRegistry, Tool


class DummyInput(BaseModel):
    query: str


class FlexInput(BaseModel):
    """Accepts any keyword arguments — used for auto-chain tests."""

    model_config = {"extra": "allow"}


def dummy_tool_func(query: str) -> dict:
    return {"result": f"Processed: {query}"}


def create_dummy_skill() -> ConfiguredSkill:
    return ConfiguredSkill(
        name="dummy",
        description="Dummy skill for testing",
        system_prompt="You are a dummy assistant.",
        tools=[
            Tool(
                name="dummy_query",
                description="A dummy query tool",
                function=dummy_tool_func,
                input_schema=DummyInput,
            )
        ],
    )


class TestAgent:
    @pytest.fixture
    def registry(self):
        reg = SkillRegistry()
        reg.register(create_dummy_skill())
        return reg

    @pytest.fixture
    def mock_model(self):
        model = MagicMock()
        model.bind_tools = MagicMock(return_value=model)
        return model

    def test_agent_creates_with_empty_registry(self, mock_model):
        registry = SkillRegistry()
        agent = Agent(mock_model, registry)
        assert agent is not None
        # Should not call bind_tools with no tools
        mock_model.bind_tools.assert_not_called()

    def test_agent_binds_tools(self, mock_model, registry):
        _agent = Agent(mock_model, registry)  # noqa: F841
        mock_model.bind_tools.assert_called_once()

    def test_agent_has_system_prompt(self, mock_model, registry):
        agent = Agent(mock_model, registry)
        assert len(agent.conversation) == 1
        assert agent.conversation.messages[0].content is not None

    @pytest.mark.asyncio
    async def test_process_simple_response(self, mock_model, registry):
        # Mock a simple response without tool calls
        mock_response = MagicMock()
        mock_response.content = "Hello! How can I help?"
        mock_response.tool_calls = None
        mock_response.invalid_tool_calls = []

        mock_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        agent = Agent(mock_model, registry)
        response = await agent.process("Hello")

        assert response.content == "Hello! How can I help?"
        assert response.finished is True
        assert len(response.tool_calls_made) == 0

    @pytest.mark.asyncio
    async def test_process_with_tool_call(self, mock_model, registry):
        # First response has tool call
        tool_call_response = MagicMock()
        tool_call_response.content = ""
        tool_call_response.tool_calls = [
            {"id": "call_123", "name": "dummy_query", "args": {"query": "test"}}
        ]

        # Second response is final
        final_response = MagicMock()
        final_response.content = "The result is: Processed: test"
        final_response.tool_calls = None
        final_response.invalid_tool_calls = []

        mock_model.ainvoke = AsyncMock(side_effect=[tool_call_response, final_response])
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        agent = Agent(mock_model, registry)
        response = await agent.process("Query something")

        assert "Processed: test" in response.content
        assert response.finished is True
        assert len(response.tool_calls_made) == 1
        assert response.tool_calls_made[0]["tool"] == "dummy_query"

    @pytest.mark.asyncio
    async def test_process_nudges_on_text_tool_calls(self, mock_model, registry):
        """When LLM outputs tool calls as text, agent should nudge and retry."""
        # First response: tool call as text (no actual tool_calls)
        text_response = MagicMock()
        text_response.content = (
            'I will call the tool now:\n{"name": "dummy_query", "arguments": {"query": "test"}}'
        )
        text_response.tool_calls = []
        text_response.invalid_tool_calls = []

        # Second response: proper tool call
        tool_call_response = MagicMock()
        tool_call_response.content = ""
        tool_call_response.tool_calls = [
            {"id": "call_456", "name": "dummy_query", "args": {"query": "test"}}
        ]

        # Third response: final answer
        final_response = MagicMock()
        final_response.content = "The result is: Processed: test"
        final_response.tool_calls = []
        final_response.invalid_tool_calls = []

        mock_model.ainvoke = AsyncMock(
            side_effect=[text_response, tool_call_response, final_response]
        )
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        agent = Agent(mock_model, registry)
        response = await agent.process("Query something")

        assert response.finished is True
        assert len(response.tool_calls_made) == 1
        assert "Processed: test" in response.content
        # Verify the nudge message was added to conversation
        nudge_messages = [
            m
            for m in agent.conversation.messages
            if m.role.value == "user" and "tool calling mechanism" in m.content
        ]
        assert len(nudge_messages) == 1

    @pytest.mark.asyncio
    async def test_process_handles_invalid_tool_calls(self, mock_model, registry):
        """When LLM makes malformed tool calls, agent should nudge and retry."""
        # First response: invalid tool call
        invalid_response = MagicMock()
        invalid_response.content = ""
        invalid_response.tool_calls = []
        invalid_response.invalid_tool_calls = [
            {
                "name": "dummy_query",
                "args": "{bad json",
                "id": "call_bad",
                "error": "parse error",
            }
        ]

        # Second response: proper tool call
        tool_call_response = MagicMock()
        tool_call_response.content = ""
        tool_call_response.tool_calls = [
            {"id": "call_789", "name": "dummy_query", "args": {"query": "test"}}
        ]

        # Third response: final answer
        final_response = MagicMock()
        final_response.content = "Done."
        final_response.tool_calls = []
        final_response.invalid_tool_calls = []

        mock_model.ainvoke = AsyncMock(
            side_effect=[invalid_response, tool_call_response, final_response]
        )
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        agent = Agent(mock_model, registry)
        response = await agent.process("Query something")

        assert response.finished is True
        assert len(response.tool_calls_made) == 1

    @pytest.mark.asyncio
    async def test_process_no_false_positive_on_json_response(self, mock_model, registry):
        """Normal JSON in response should not trigger the nudge."""
        mock_response = MagicMock()
        mock_response.content = '{"result": "some data", "name": "not_a_tool"}'
        mock_response.tool_calls = []
        mock_response.invalid_tool_calls = []

        mock_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        agent = Agent(mock_model, registry)
        response = await agent.process("Show me data")

        assert response.finished is True
        # Should NOT have any nudge messages
        nudge_messages = [
            m
            for m in agent.conversation.messages
            if m.role.value == "user" and "tool calling mechanism" in m.content
        ]
        assert len(nudge_messages) == 0

    @pytest.mark.asyncio
    async def test_process_nudges_on_incomplete_investigation(self, mock_model, registry):
        """When start_investigation was called but get_investigation_summary
        was not, the agent should nudge the LLM to complete the workflow."""
        inv_registry = SkillRegistry()
        inv_registry.register(
            ConfiguredSkill(
                name="investigation",
                description="Investigation skill",
                system_prompt="You are an investigator.",
                tools=[
                    Tool(
                        name="start_investigation",
                        description="Start an investigation",
                        function=lambda **kw: {"status": "started"},
                        input_schema=DummyInput,
                    ),
                    Tool(
                        name="check_data_availability",
                        description="Check data",
                        function=lambda **kw: {"data_found": True},
                        input_schema=DummyInput,
                    ),
                    Tool(
                        name="record_finding",
                        description="Record a finding",
                        function=lambda **kw: {"recorded": True},
                        input_schema=DummyInput,
                    ),
                    Tool(
                        name="get_investigation_summary",
                        description="Get investigation summary",
                        function=lambda **kw: {"summary": "done"},
                        input_schema=DummyInput,
                    ),
                ],
            )
        )

        mock_model.bind_tools = MagicMock(return_value=mock_model)

        # Response 1: tool call to start_investigation
        start_response = MagicMock()
        start_response.content = ""
        start_response.tool_calls = [
            {"id": "call_1", "name": "start_investigation", "args": {"query": "test"}}
        ]

        # Response 2: LLM tries to respond with text (skipping check_data)
        text_response = MagicMock()
        text_response.content = "Here are the results of my investigation..."
        text_response.tool_calls = []
        text_response.invalid_tool_calls = []

        # Response 3: after nudge, LLM calls check_data_availability
        check_response = MagicMock()
        check_response.content = ""
        check_response.tool_calls = [
            {
                "id": "call_2",
                "name": "check_data_availability",
                "args": {"query": "check"},
            }
        ]

        # Response 4: LLM calls record_finding
        record_response = MagicMock()
        record_response.content = ""
        record_response.tool_calls = [
            {"id": "call_3", "name": "record_finding", "args": {"query": "finding"}}
        ]

        # Response 5: LLM calls get_investigation_summary
        summary_call_response = MagicMock()
        summary_call_response.content = ""
        summary_call_response.tool_calls = [
            {
                "id": "call_4",
                "name": "get_investigation_summary",
                "args": {"query": "summary"},
            }
        ]

        # Response 6: final text answer
        final_response = MagicMock()
        final_response.content = "Investigation complete. No issues found."
        final_response.tool_calls = []
        final_response.invalid_tool_calls = []

        mock_model.ainvoke = AsyncMock(
            side_effect=[
                start_response,
                text_response,
                check_response,
                record_response,
                summary_call_response,
                final_response,
            ]
        )

        agent = Agent(mock_model, inv_registry)
        response = await agent.process("Investigate missing data")

        assert response.finished is True
        # All four tools should have been called
        tools_called = [tc["tool"] for tc in response.tool_calls_made]
        assert "start_investigation" in tools_called
        assert "check_data_availability" in tools_called
        assert "record_finding" in tools_called
        assert "get_investigation_summary" in tools_called
        # Verify the context-aware nudge was injected (mentions check_data_availability
        # since that's the next step after start_investigation)
        nudge_messages = [
            m
            for m in agent.conversation.messages
            if m.role.value == "user" and "check_data_availability" in m.content
        ]
        assert len(nudge_messages) == 1

    @pytest.mark.asyncio
    async def test_no_nudge_when_investigation_complete(self, mock_model, registry):
        """When get_investigation_summary was called, no nudge should fire."""
        inv_registry = SkillRegistry()
        inv_registry.register(
            ConfiguredSkill(
                name="investigation",
                description="Investigation skill",
                system_prompt="You are an investigator.",
                tools=[
                    Tool(
                        name="start_investigation",
                        description="Start",
                        function=lambda **kw: {"status": "started"},
                        input_schema=DummyInput,
                    ),
                    Tool(
                        name="get_investigation_summary",
                        description="Summary",
                        function=lambda **kw: {"summary": "done"},
                        input_schema=DummyInput,
                    ),
                ],
            )
        )

        mock_model.bind_tools = MagicMock(return_value=mock_model)

        # Response 1: start_investigation
        start_response = MagicMock()
        start_response.content = ""
        start_response.tool_calls = [
            {"id": "call_1", "name": "start_investigation", "args": {"query": "test"}}
        ]

        # Response 2: get_investigation_summary
        summary_response = MagicMock()
        summary_response.content = ""
        summary_response.tool_calls = [
            {
                "id": "call_2",
                "name": "get_investigation_summary",
                "args": {"query": "s"},
            }
        ]

        # Response 3: final text
        final_response = MagicMock()
        final_response.content = "Investigation complete."
        final_response.tool_calls = []
        final_response.invalid_tool_calls = []

        mock_model.ainvoke = AsyncMock(
            side_effect=[start_response, summary_response, final_response]
        )

        agent = Agent(mock_model, inv_registry)
        response = await agent.process("Investigate")

        assert response.finished is True
        # No investigation-incomplete nudge should exist
        nudge_messages = [
            m
            for m in agent.conversation.messages
            if m.role.value == "user" and "continue the current one" in m.content
        ]
        assert len(nudge_messages) == 0

    def test_investigation_incomplete_detection(self, mock_model, registry):
        """Test _investigation_incomplete logic directly."""
        agent = Agent(mock_model, registry)

        # No tools called → not incomplete
        assert agent._investigation_incomplete([]) is False

        # Only unrelated tool → not incomplete
        assert agent._investigation_incomplete([{"tool": "dummy_query"}]) is False

        # start_investigation called, no summary → incomplete
        assert agent._investigation_incomplete([{"tool": "start_investigation"}]) is True

        # Both called → complete
        assert (
            agent._investigation_incomplete(
                [
                    {"tool": "start_investigation"},
                    {"tool": "get_investigation_summary"},
                ]
            )
            is False
        )

    def test_investigation_nudge_is_context_aware(self, mock_model, registry):
        """The investigation nudge should point to the correct next tool."""
        agent = Agent(mock_model, registry)

        # After start_investigation only → nudge to check_data_availability
        nudge = agent._get_investigation_nudge([{"tool": "start_investigation"}])
        assert "check_data_availability" in nudge
        assert "Do NOT start a new investigation" in nudge

        # After check_data_availability → nudge to record_finding
        nudge = agent._get_investigation_nudge(
            [
                {"tool": "start_investigation"},
                {"tool": "check_data_availability"},
            ]
        )
        assert "record_finding" in nudge

        # After record_finding → nudge to get_investigation_summary
        nudge = agent._get_investigation_nudge(
            [
                {"tool": "start_investigation"},
                {"tool": "check_data_availability"},
                {"tool": "record_finding"},
            ]
        )
        assert "get_investigation_summary" in nudge

    def test_investigation_completed_detection(self, mock_model, registry):
        """Test _investigation_completed logic directly."""
        agent = Agent(mock_model, registry)

        assert agent._investigation_completed([]) is False
        assert agent._investigation_completed([{"tool": "dummy_query"}]) is False
        assert agent._investigation_completed([{"tool": "start_investigation"}]) is False
        assert (
            agent._investigation_completed(
                [
                    {"tool": "start_investigation"},
                    {"tool": "get_investigation_summary"},
                ]
            )
            is True
        )

    @pytest.mark.asyncio
    async def test_mentions_tools_nudge_skipped_after_completed_investigation(
        self, mock_model, registry
    ):
        """After investigation is complete, _mentions_tools nudge should not
        fire even if the final text mentions tool names."""
        inv_registry = SkillRegistry()
        inv_registry.register(
            ConfiguredSkill(
                name="investigation",
                description="Investigation skill",
                system_prompt="You are an investigator.",
                tools=[
                    Tool(
                        name="start_investigation",
                        description="Start",
                        function=lambda **kw: {"status": "started"},
                        input_schema=DummyInput,
                    ),
                    Tool(
                        name="check_data_availability",
                        description="Check data",
                        function=lambda **kw: {"data_found": True},
                        input_schema=DummyInput,
                    ),
                    Tool(
                        name="record_finding",
                        description="Record",
                        function=lambda **kw: {"recorded": True},
                        input_schema=DummyInput,
                    ),
                    Tool(
                        name="get_investigation_summary",
                        description="Summary",
                        function=lambda **kw: {"summary": "done"},
                        input_schema=DummyInput,
                    ),
                ],
            )
        )

        mock_model.bind_tools = MagicMock(return_value=mock_model)

        # 1. start_investigation
        r1 = MagicMock()
        r1.content = ""
        r1.tool_calls = [{"id": "c1", "name": "start_investigation", "args": {"query": "t"}}]

        # 2. check_data_availability
        r2 = MagicMock()
        r2.content = ""
        r2.tool_calls = [{"id": "c2", "name": "check_data_availability", "args": {"query": "t"}}]

        # 3. record_finding
        r3 = MagicMock()
        r3.content = ""
        r3.tool_calls = [{"id": "c3", "name": "record_finding", "args": {"query": "t"}}]

        # 4. get_investigation_summary
        r4 = MagicMock()
        r4.content = ""
        r4.tool_calls = [{"id": "c4", "name": "get_investigation_summary", "args": {"query": "t"}}]

        # 5. Final text that mentions tool names — should NOT be nudged
        r5 = MagicMock()
        r5.content = (
            "I used check_data_availability to verify the data in CV_ZBC_AA61. "
            "The start_investigation and record_finding steps confirmed the issue."
        )
        r5.tool_calls = []
        r5.invalid_tool_calls = []

        mock_model.ainvoke = AsyncMock(side_effect=[r1, r2, r3, r4, r5])

        agent = Agent(mock_model, inv_registry)
        response = await agent.process("Check data for CoCd 1110")

        assert response.finished is True
        # The final text should pass through without nudging
        assert "check_data_availability" in response.content
        # No continue-nudge should have been injected
        continue_nudges = [
            m
            for m in agent.conversation.messages
            if m.role.value == "user" and "Do NOT explain or narrate" in m.content
        ]
        assert len(continue_nudges) == 0

    @pytest.mark.asyncio
    async def test_auto_chain_runs_full_playbook(self, mock_model, registry):
        """When start_investigation returns next_step, the entire playbook
        should be auto-chained: check_data → record_finding → summary."""
        inv_registry = SkillRegistry()
        inv_registry.register(
            ConfiguredSkill(
                name="investigation",
                description="Investigation skill",
                system_prompt="You are an investigator.",
                tools=[
                    Tool(
                        name="start_investigation",
                        description="Start",
                        function=lambda **kw: {
                            "status": "started",
                            "investigation_id": "inv_1",
                            "next_step": {
                                "action": "call check_data_availability now",
                                "table": "CV_ZBC_AA61",
                                "filters": {
                                    "ZCOMPCODE": "1110",
                                    "FISCPER": "2026001",
                                },
                            },
                        },
                        input_schema=FlexInput,
                    ),
                    Tool(
                        name="check_data_availability",
                        description="Check data",
                        function=lambda **kw: {
                            "data_found": True,
                            "table": kw.get("table", ""),
                            "groups": [
                                {"ZSCOPE": "S_LEGAL", "CS_TRN_LC": 1000},
                                {"ZSCOPE": "S_NONE", "CS_TRN_LC": 2000},
                            ],
                            "totals": {"CS_TRN_LC": 3000},
                        },
                        input_schema=FlexInput,
                    ),
                    Tool(
                        name="record_finding",
                        description="Record",
                        function=lambda **kw: {"recorded": True},
                        input_schema=FlexInput,
                    ),
                    Tool(
                        name="get_investigation_summary",
                        description="Summary",
                        function=lambda **kw: {"summary": "done"},
                        input_schema=FlexInput,
                    ),
                ],
            )
        )

        mock_model.bind_tools = MagicMock(return_value=mock_model)

        # Response 1: LLM calls start_investigation
        # (full playbook auto-chains after this)
        start_response = MagicMock()
        start_response.content = ""
        start_response.tool_calls = [
            {
                "id": "call_1",
                "name": "start_investigation",
                "args": {"query": "test"},
            }
        ]

        # Response 2: LLM produces final text (playbook already done)
        final_response = MagicMock()
        final_response.content = "Investigation complete. Data found with S_LEGAL scope."
        final_response.tool_calls = []
        final_response.invalid_tool_calls = []

        mock_model.ainvoke = AsyncMock(side_effect=[start_response, final_response])

        agent = Agent(mock_model, inv_registry)
        response = await agent.process("Check data for CoCd 1110")

        assert response.finished is True
        tools_called = [tc["tool"] for tc in response.tool_calls_made]
        # Full playbook auto-chained: start → check → record → summary
        assert tools_called == [
            "start_investigation",
            "check_data_availability",
            "record_finding",
            "get_investigation_summary",
        ]
        # check_data used the next_step params
        check_call = response.tool_calls_made[1]
        assert check_call["args"]["table"] == "CV_ZBC_AA61"
        assert check_call["args"]["filters"]["ZCOMPCODE"] == "1110"
        # record_finding used correct data (not hallucinated)
        record_call = response.tool_calls_made[2]
        assert "S_LEGAL" in record_call["args"]["result_summary"]
        assert record_call["args"]["status"] == "normal"
        # LLM only needed 2 calls (start + final text)
        assert mock_model.ainvoke.call_count == 2

    @pytest.mark.asyncio
    async def test_auto_chain_s_none_branch_checks_ownership(self, mock_model, registry):
        """When check_data returns only S_NONE scopes, playbook should
        branch to check_ownership."""
        inv_registry = SkillRegistry()
        inv_registry.register(
            ConfiguredSkill(
                name="investigation",
                description="Investigation skill",
                system_prompt="You are an investigator.",
                tools=[
                    Tool(
                        name="start_investigation",
                        description="Start",
                        function=lambda **kw: {
                            "status": "started",
                            "next_step": {
                                "table": "CV_ZBC_AA61",
                                "filters": {
                                    "ZCOMPCODE": "1110",
                                    "FISCPER": "2026001",
                                },
                            },
                        },
                        input_schema=FlexInput,
                    ),
                    Tool(
                        name="check_data_availability",
                        description="Check data",
                        function=lambda **kw: {
                            "data_found": True,
                            "table": kw.get("table", ""),
                            "groups": [{"ZSCOPE": "S_NONE"}],
                            "totals": {"CS_TRN_LC": 1000},
                        },
                        input_schema=FlexInput,
                    ),
                    Tool(
                        name="check_ownership",
                        description="Check ownership",
                        function=lambda **kw: {
                            "result": True,
                            "rows_found": 3,
                        },
                        input_schema=FlexInput,
                    ),
                    Tool(
                        name="record_finding",
                        description="Record",
                        function=lambda **kw: {"recorded": True},
                        input_schema=FlexInput,
                    ),
                    Tool(
                        name="get_investigation_summary",
                        description="Summary",
                        function=lambda **kw: {"summary": "done"},
                        input_schema=FlexInput,
                    ),
                ],
            )
        )

        mock_model.bind_tools = MagicMock(return_value=mock_model)

        start_response = MagicMock()
        start_response.content = ""
        start_response.tool_calls = [
            {"id": "c1", "name": "start_investigation", "args": {"query": "t"}}
        ]

        final_response = MagicMock()
        final_response.content = "Consolidation incomplete."
        final_response.tool_calls = []
        final_response.invalid_tool_calls = []

        mock_model.ainvoke = AsyncMock(side_effect=[start_response, final_response])

        agent = Agent(mock_model, inv_registry)
        response = await agent.process("Check data")

        tools_called = [tc["tool"] for tc in response.tool_calls_made]
        assert tools_called == [
            "start_investigation",
            "check_data_availability",
            "record_finding",  # Step 1 finding
            "check_ownership",  # Step 2A
            "record_finding",  # Step 2A finding
            "get_investigation_summary",
        ]
        # check_ownership used correct params from investigation context
        ownership_call = next(
            tc for tc in response.tool_calls_made if tc["tool"] == "check_ownership"
        )
        assert ownership_call["args"]["param_cocd"] == "1110"
        assert ownership_call["args"]["param_fiscper"] == "2026001"

    @pytest.mark.asyncio
    async def test_auto_chain_no_data_branch_checks_bpc_mart(self, mock_model, registry):
        """When check_data returns no data, playbook should check BPC mart."""
        inv_registry = SkillRegistry()
        inv_registry.register(
            ConfiguredSkill(
                name="investigation",
                description="Investigation skill",
                system_prompt="You are an investigator.",
                tools=[
                    Tool(
                        name="start_investigation",
                        description="Start",
                        function=lambda **kw: {
                            "status": "started",
                            "next_step": {
                                "table": "CV_ZBC_AA61",
                                "filters": {
                                    "ZCOMPCODE": "2200",
                                    "FISCPER": "2025012",
                                },
                            },
                        },
                        input_schema=FlexInput,
                    ),
                    Tool(
                        name="check_data_availability",
                        description="Check data",
                        function=lambda **kw: {
                            "data_found": False,
                            "table": kw.get("table", ""),
                            "groups": [],
                            "totals": {},
                        },
                        input_schema=FlexInput,
                    ),
                    Tool(
                        name="record_finding",
                        description="Record",
                        function=lambda **kw: {"recorded": True},
                        input_schema=FlexInput,
                    ),
                    Tool(
                        name="get_investigation_summary",
                        description="Summary",
                        function=lambda **kw: {"summary": "done"},
                        input_schema=FlexInput,
                    ),
                ],
            )
        )

        mock_model.bind_tools = MagicMock(return_value=mock_model)

        start_response = MagicMock()
        start_response.content = ""
        start_response.tool_calls = [
            {"id": "c1", "name": "start_investigation", "args": {"query": "t"}}
        ]

        final_response = MagicMock()
        final_response.content = "Data missing everywhere."
        final_response.tool_calls = []
        final_response.invalid_tool_calls = []

        mock_model.ainvoke = AsyncMock(side_effect=[start_response, final_response])

        agent = Agent(mock_model, inv_registry)
        response = await agent.process("Check data")

        tools_called = [tc["tool"] for tc in response.tool_calls_made]
        assert tools_called == [
            "start_investigation",
            "check_data_availability",  # Step 1: reporting table
            "record_finding",  # Step 1 finding
            "check_data_availability",  # Step 2B: BPC mart
            "record_finding",  # Step 2B finding
            "get_investigation_summary",
        ]
        # Second check_data should target CV_ZFI_AA01
        bpc_call = response.tool_calls_made[3]
        assert bpc_call["args"]["table"] == "CV_ZFI_AA01"
        assert bpc_call["args"]["filters"]["ZCOMPCODE"] == "2200"

    @pytest.mark.asyncio
    async def test_auto_chain_skipped_without_next_step(self, mock_model, registry):
        """Auto-chain should not fire when start_investigation has no next_step."""
        inv_registry = SkillRegistry()
        inv_registry.register(
            ConfiguredSkill(
                name="investigation",
                description="Investigation skill",
                system_prompt="You are an investigator.",
                tools=[
                    Tool(
                        name="start_investigation",
                        description="Start",
                        function=lambda **kw: {"status": "started"},
                        input_schema=DummyInput,
                    ),
                    Tool(
                        name="get_investigation_summary",
                        description="Summary",
                        function=lambda **kw: {"summary": "done"},
                        input_schema=DummyInput,
                    ),
                ],
            )
        )

        mock_model.bind_tools = MagicMock(return_value=mock_model)

        start_response = MagicMock()
        start_response.content = ""
        start_response.tool_calls = [
            {"id": "c1", "name": "start_investigation", "args": {"query": "t"}}
        ]

        summary_response = MagicMock()
        summary_response.content = ""
        summary_response.tool_calls = [
            {
                "id": "c2",
                "name": "get_investigation_summary",
                "args": {"query": "s"},
            }
        ]

        final_response = MagicMock()
        final_response.content = "Done."
        final_response.tool_calls = []
        final_response.invalid_tool_calls = []

        mock_model.ainvoke = AsyncMock(
            side_effect=[start_response, summary_response, final_response]
        )

        agent = Agent(mock_model, inv_registry)
        response = await agent.process("Test")

        tools_called = [tc["tool"] for tc in response.tool_calls_made]
        # No auto-chain — only the tools the LLM explicitly called
        assert tools_called == [
            "start_investigation",
            "get_investigation_summary",
        ]

    def test_reset_keeps_system_prompt(self, mock_model, registry):
        agent = Agent(mock_model, registry)
        agent.conversation.add_user("Test message")

        assert len(agent.conversation) == 2

        agent.reset()

        assert len(agent.conversation) == 1
        assert agent.conversation.messages[0].role.value == "system"

    def test_system_prompt_has_structured_sections(self, mock_model, registry):
        """System prompt should contain structured sections with markdown headers."""
        agent = Agent(mock_model, registry)
        prompt = agent.conversation.messages[0].content
        assert "# Role" in prompt
        assert "# Instructions" in prompt
        assert "# Tool Usage Rules" in prompt
        assert "# Reasoning" in prompt
        assert "# Guardrails" in prompt
        assert "# Output Format" in prompt

    @pytest.mark.asyncio
    async def test_rag_context_injected_when_manager_provided(self, mock_model, registry):
        """When a RAG manager is provided, its context should be injected."""
        mock_rag = MagicMock()
        mock_rag.get_context.return_value = "Relevant knowledge about SAP data."

        mock_response = MagicMock()
        mock_response.content = "Here is the answer."
        mock_response.tool_calls = None
        mock_response.invalid_tool_calls = []
        mock_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        agent = Agent(mock_model, registry, rag_manager=mock_rag)
        await agent.process("Tell me about data")

        mock_rag.get_context.assert_called_once_with("Tell me about data", k=3)
        # RAG context should appear as a system message in the conversation
        rag_messages = [
            m
            for m in agent.conversation.messages
            if m.role.value == "system" and "Relevant Knowledge" in m.content
        ]
        assert len(rag_messages) == 1
        assert "Relevant knowledge about SAP data." in rag_messages[0].content

    @pytest.mark.asyncio
    async def test_no_rag_context_when_manager_not_provided(self, mock_model, registry):
        """When no RAG manager is provided, no RAG context should be injected."""
        mock_response = MagicMock()
        mock_response.content = "Here is the answer."
        mock_response.tool_calls = None
        mock_response.invalid_tool_calls = []
        mock_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        agent = Agent(mock_model, registry)
        await agent.process("Tell me about data")

        # Only one system message (the base prompt), no RAG context
        system_messages = [
            m for m in agent.conversation.messages if m.role.value == "system"
        ]
        assert len(system_messages) == 1

    @pytest.mark.asyncio
    async def test_rag_failure_does_not_break_agent(self, mock_model, registry):
        """If RAG retrieval fails, the agent should continue normally."""
        mock_rag = MagicMock()
        mock_rag.get_context.side_effect = RuntimeError("DB connection failed")

        mock_response = MagicMock()
        mock_response.content = "Here is the answer."
        mock_response.tool_calls = None
        mock_response.invalid_tool_calls = []
        mock_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_model.bind_tools = MagicMock(return_value=mock_model)

        agent = Agent(mock_model, registry, rag_manager=mock_rag)
        response = await agent.process("Tell me about data")

        assert response.finished is True
        assert response.content == "Here is the answer."
