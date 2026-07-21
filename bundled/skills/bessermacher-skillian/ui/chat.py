"""Streamlit chat interface for Skillian SAP BW Assistant."""

import json
import os

import requests
import streamlit as st

DEFAULT_BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="Skillian - SAP BW Assistant",
    page_icon="🔧",
    layout="wide",
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Sidebar
with st.sidebar:
    st.title("Skillian")
    st.caption("SAP BW AI Assistant")

    backend_url = st.text_input(
        "Backend URL",
        value=DEFAULT_BACKEND_URL,
        help="FastAPI backend URL",
    )

    if st.button("New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = None
        st.rerun()

    # Show current session
    if st.session_state.session_id:
        st.caption(f"Session: {st.session_state.session_id[:8]}...")

    st.divider()

    # Health check
    try:
        health = requests.get(f"{backend_url}/api/v1/health", timeout=2)
        if health.status_code == 200:
            data = health.json()
            st.success(f"Backend: {data.get('status', 'ok')}")
            st.caption(f"LLM: {data.get('llm_provider', 'unknown')}")
        else:
            st.error("Backend unhealthy")
    except requests.exceptions.RequestException:
        st.warning("Backend not reachable")

# Main chat area
st.header("SAP BW Assistant")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Show timing if present
        if msg.get("timing"):
            with st.expander("Timing", expanded=False):
                st.write(f"**Total:** {msg['timing']['total_seconds']:.1f}s")

        # Show tool calls if present
        if msg.get("tool_calls"):
            with st.expander("Tool calls", expanded=False):
                for tc in msg["tool_calls"]:
                    duration = tc.get("duration_seconds")
                    duration_str = f" ({duration:.1f}s)" if duration else ""
                    st.code(
                        f"{tc['tool']}({tc['args']}){duration_str}\n→ {tc['result']}",
                        language="text",
                    )


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
            if event_type and data_lines:
                data = json.loads("".join(data_lines))
                yield event_type, data
            event_type = None
            data_lines = []


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
                st.error(f"Error: {response.status_code} - {response.text}")
            else:
                assistant_message = ""
                tool_calls = []

                timing_info = None

                with st.status("Processing...", expanded=True) as status:
                    for event_type, data in parse_sse_stream(response):
                        if event_type == "thinking":
                            iteration = data.get("iteration", "?")
                            status.update(label=f"Calling LLM (step {iteration})...")
                            st.write(f"Calling LLM (step {iteration})...")

                        elif event_type == "llm_response":
                            iteration = data.get("iteration", "?")
                            duration = data.get("duration_seconds", 0)
                            st.write(f"LLM responded (step {iteration}) in **{duration:.1f}s**")

                        elif event_type == "tool_call":
                            tool_name = data.get("tool", "unknown")
                            tool_args = data.get("args", {})
                            status.update(label=f"Running {tool_name}...")
                            st.write(f"Running **{tool_name}**(`{tool_args}`)")

                        elif event_type == "tool_result":
                            tool_name = data.get("tool", "unknown")
                            result = data.get("result", "")
                            duration = data.get("duration_seconds", 0)
                            st.write(f"Got result from **{tool_name}** in **{duration:.1f}s**")
                            tool_calls.append(
                                {
                                    "tool": tool_name,
                                    "args": data.get("args", {}),
                                    "result": result,
                                }
                            )

                        elif event_type == "text_delta":
                            assistant_message += data.get("content", "")

                        elif event_type == "done":
                            done_data = data
                            assistant_message = done_data.get("response", assistant_message)
                            tool_calls = done_data.get("tool_calls", tool_calls)
                            timing_info = done_data.get("timing")
                            total = timing_info.get("total_seconds", 0) if timing_info else 0
                            status.update(
                                label=f"Done in {total:.1f}s",
                                state="complete",
                                expanded=False,
                            )

                        elif event_type == "session":
                            session_id = data.get("session_id")
                            if session_id:
                                st.session_state.session_id = session_id

                        elif event_type == "error":
                            st.error(f"Error: {data.get('message', 'Unknown error')}")
                            status.update(label="Error", state="error")

                # Show the final response
                if assistant_message and assistant_message.strip():
                    st.markdown(assistant_message)
                elif tool_calls:
                    st.warning(
                        "The LLM did not produce a text conclusion. "
                        "Check the tool call results above for details."
                    )

                # Show timing summary
                if timing_info:
                    with st.expander("Timing", expanded=False):
                        st.write(f"**Total:** {timing_info['total_seconds']:.1f}s")
                        for llm in timing_info.get("llm_calls", []):
                            st.write(
                                f"LLM call (step {llm['iteration']}): "
                                f"{llm['duration_seconds']:.1f}s"
                            )
                        for tc in timing_info.get("tool_calls", []):
                            st.write(f"Tool `{tc['tool']}`: {tc['duration_seconds']:.1f}s")

                # Show tool calls in an expander
                if tool_calls:
                    with st.expander("Tool calls", expanded=False):
                        for tc in tool_calls:
                            duration = tc.get("duration_seconds")
                            duration_str = f" ({duration:.1f}s)" if duration else ""
                            line = (
                                f"{tc['tool']}({tc.get('args', {})})"
                                f"{duration_str}\n→ {tc['result']}"
                            )
                            st.code(line, language="text")

                # Save to history
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_message,
                        "tool_calls": tool_calls,
                        "timing": timing_info,
                    }
                )

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect: {e}")
