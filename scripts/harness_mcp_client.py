"""Bounded stdio MCP transport through the canonical launcher.

An optional Python command argument exists solely for isolated fixtures. Runtime
CLI callers select a canonical server id, never a caller-provided command.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import queue
import signal
import subprocess
import sys
import threading
import time
from typing import Any

from harness_contracts import validate_arguments

ROOT = Path(__file__).resolve().parents[1]
MAX_MESSAGE_BYTES = 1_048_576
MAX_TOOLS = 256


class McpProtocolError(RuntimeError):
    pass


class _WindowsJob:
    """Own the launcher and descendants even if the launcher exits first."""
    def __init__(self, process):
        import ctypes
        from ctypes import wintypes

        class BasicLimits(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64), ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t), ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD), ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD), ("SchedulingClass", wintypes.DWORD)]

        class IoCounters(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount", "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

        class ExtendedLimits(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", BasicLimits), ("IoInfo", IoCounters), ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        kernel.CreateJobObjectW.restype = wintypes.HANDLE
        kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        kernel.SetInformationJobObject.restype = wintypes.BOOL
        kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        kernel.AssignProcessToJobObject.restype = wintypes.BOOL
        kernel.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        kernel.TerminateJobObject.restype = wintypes.BOOL
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.CloseHandle.restype = wintypes.BOOL
        self.kernel = kernel
        self.handle = kernel.CreateJobObjectW(None, None)
        if not self.handle:
            raise McpProtocolError("cannot create MCP process job")
        limits = ExtendedLimits()
        limits.BasicLimitInformation.LimitFlags = 0x00002000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)) or not kernel.AssignProcessToJobObject(self.handle, wintypes.HANDLE(int(process._handle))):
            self.close()
            raise McpProtocolError("cannot contain MCP process descendants")

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None

    def terminate(self):
        if self.handle:
            # Terminate explicitly before closing the kill-on-close job handle.
            # This also makes cleanup deterministic when other code temporarily
            # holds a duplicate job handle.
            self.kernel.TerminateJobObject(self.handle, 1)


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


class McpClient:
    def __init__(self, server_id: str, timeout: float = 30, *, command: list[str] | None = None,
                 root: Path | str | None = None, deadline: float | None = None):
        if not isinstance(server_id, str) or not server_id or len(server_id) > 160:
            raise ValueError("invalid MCP server id")
        if timeout <= 0 or timeout > 120:
            raise ValueError("MCP timeout must be within 0-120 seconds")
        self.server_id = server_id
        self.timeout = timeout
        self.deadline = deadline
        self.root = Path(root or ROOT).resolve()
        if not (self.root / "scripts/source_catalog.py").is_file():
            raise ValueError("canonical SAP Router root missing")
        self.command = list(command) if command is not None else [sys.executable, str(self.root / "scripts/mcp_launcher.py"), "run", "--server", server_id]
        if not self.command or any(not isinstance(arg, str) or "\x00" in arg for arg in self.command):
            raise ValueError("invalid fixture command")
        self.process: subprocess.Popen | None = None
        self._messages: queue.Queue = queue.Queue(maxsize=64)
        self._reader_error: str | None = None
        self._next_id = 0
        self._tools: list[dict] | None = None
        self._closed = False
        self._job = None
        self._lock = threading.Lock()

    def __enter__(self):
        if self.process is not None:
            raise RuntimeError("MCP transport cannot be reused")
        flags: dict[str, Any] = {}
        if os.name == "nt":
            flags["creationflags"] = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            flags["start_new_session"] = True
        env = os.environ.copy()
        env["SAP_ROUTER_ROOT"] = str(self.root)
        self.process = subprocess.Popen(self.command, cwd=self.root, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, **flags)
        try:
            if os.name == "nt":
                self._job = _WindowsJob(self.process)
            threading.Thread(target=self._read_stdout, daemon=True).start()
            threading.Thread(target=self._drain_stderr, daemon=True).start()
            initialized = self._request("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "sap-router-harness", "version": "1.0.0"}})
            if initialized.get("protocolVersion") not in {"2024-11-05", "2025-03-26", "2025-06-18"} or not isinstance(initialized.get("capabilities", {}).get("tools"), dict):
                raise McpProtocolError("MCP initialization did not negotiate tools")
            self._write({"jsonrpc": "2.0", "method": "notifications/initialized"})
            return self
        except BaseException:
            self.close()
            raise

    def __exit__(self, *_):
        self.close()

    def _read_stdout(self):
        try:
            while not self._closed:
                raw = self.process.stdout.readline(MAX_MESSAGE_BYTES + 1)
                if not raw:
                    self._reader_error = "MCP stdout closed"
                    return
                if len(raw) > MAX_MESSAGE_BYTES or not raw.endswith(b"\n"):
                    self._reader_error = "MCP response exceeds message limit"
                    return
                try:
                    message = json.loads(raw.decode("utf-8"), object_pairs_hook=_json_object)
                except (UnicodeError, ValueError, RecursionError):
                    self._reader_error = "MCP emitted invalid JSON"
                    return
                if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
                    self._reader_error = "MCP emitted invalid protocol message"
                    return
                try:
                    self._messages.put_nowait(message)
                except queue.Full:
                    self._reader_error = "MCP message queue limit exceeded"
                    return
        except (OSError, ValueError):
            if not self._closed:
                self._reader_error = "MCP stdout read failed"

    def _drain_stderr(self):
        # Stderr is drained to prevent deadlock. It is never copied into prompts,
        # logs or errors because third-party runtimes can print credentials.
        try:
            while not self._closed and self.process.stderr.read(8192):
                pass
        except (OSError, ValueError):
            pass

    def _write(self, message: dict, *, deadline: float | None = None):
        if self._closed or self.process is None or self.process.poll() is not None:
            raise McpProtocolError("MCP transport is closed")
        deadline = deadline if deadline is not None else time.monotonic() + self.timeout
        raw = json.dumps(message, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode() + b"\n"
        if len(raw) > MAX_MESSAGE_BYTES:
            raise ValueError("MCP request exceeds message limit")
        completed = threading.Event()
        failures = []

        def write_request():
            try:
                self.process.stdin.write(raw)
                self.process.stdin.flush()
            except (BrokenPipeError, OSError, ValueError):
                failures.append(McpProtocolError("MCP input closed"))
            finally:
                completed.set()

        writer = threading.Thread(target=write_request, name="sap-mcp-stdin-writer", daemon=True)
        writer.start()
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not completed.wait(remaining):
            raise TimeoutError("MCP request timed out")
        if failures:
            raise failures[0]
        if time.monotonic() >= deadline:
            raise TimeoutError("MCP request timed out")

    def _request(self, method: str, params: dict) -> dict:
        with self._lock:
            deadline = time.monotonic() + self.timeout
            if self.deadline is not None:
                deadline = min(deadline, self.deadline)
            try:
                self._next_id += 1
                expected = self._next_id
                self._write({"jsonrpc": "2.0", "id": expected, "method": method, "params": params}, deadline=deadline)
                notifications = 0
                while True:
                    # A final response already queued must be consumed before EOF.
                    try:
                        message = self._messages.get_nowait()
                    except queue.Empty:
                        if self._reader_error:
                            raise McpProtocolError(self._reader_error)
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            raise TimeoutError("MCP request timed out")
                        try:
                            message = self._messages.get(timeout=min(remaining, 0.05))
                        except queue.Empty:
                            continue
                    if "id" not in message and isinstance(message.get("method"), str):
                        notifications += 1
                        if notifications > 64:
                            raise McpProtocolError("MCP notification limit exceeded")
                        continue
                    if type(message.get("id")) is not int or message["id"] != expected:
                        raise McpProtocolError("MCP response id mismatch")
                    if "error" in message:
                        raise McpProtocolError("MCP JSON-RPC error")
                    if not isinstance(message.get("result"), dict):
                        raise McpProtocolError("MCP response result must be an object")
                    return message["result"]
            except (McpProtocolError, TimeoutError):
                self.close()
                raise

    def tools(self) -> list[dict]:
        if self._tools is None:
            response = self._request("tools/list", {})
            items = response.get("tools")
            if not isinstance(items, list) or len(items) > MAX_TOOLS or response.get("nextCursor"):
                self.close()
                raise McpProtocolError("MCP tool list is invalid, too large or paginated")
            seen = set()
            for item in items:
                if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item["name"] or item["name"] in seen or not isinstance(item.get("inputSchema"), dict):
                    self.close()
                    raise McpProtocolError("MCP tool definition invalid or duplicated")
                seen.add(item["name"])
            self._tools = items
        return copy.deepcopy(self._tools)

    def call(self, tool: str, args: dict) -> dict:
        definition = next((item for item in self.tools() if item["name"] == tool), None)
        if definition is None:
            raise ValueError("tool not in negotiated MCP tool list")
        validate_arguments(definition["inputSchema"], args)
        return self._request("tools/call", {"name": tool, "arguments": args})

    def close(self):
        if self._closed:
            return
        self._closed = True
        process = self.process
        if process is None:
            return
        if self._job is not None:
            self._job.terminate()
            self._job.close()
        elif os.name != "nt":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if process.poll() is None:
            if os.name == "nt" and self._job is None:
                taskkill = str(Path(os.environ.get("SystemRoot", "C:/Windows")) / "System32/taskkill.exe")
                try:
                    subprocess.run([taskkill, "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW, shell=False)
                except (OSError, subprocess.TimeoutExpired):
                    process.kill()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream:
                try:
                    stream.close()
                except (OSError, ValueError):
                    pass
