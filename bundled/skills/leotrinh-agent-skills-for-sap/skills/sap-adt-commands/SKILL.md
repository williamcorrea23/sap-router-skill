---
name: sap-adt-commands
description: >-
  Executes SAP ABAP Development Tools (ADT) REST operations for object
  discovery, source management, object creation, activation, testing, transport
  handling, history, where-used analysis, message classes, and text elements.
  Use when working with an SAP ABAP system and the required ADT operation is
  unavailable through the currently configured MCP tools.
license: Apache-2.0
compatibility: >-
  Requires network access to an SAP system with the relevant ADT services
  enabled. Requires Python 3.10 or newer. No prebuilt executable is
  distributed; contributors may optionally build one locally with the
  provided PyInstaller spec.
metadata:
  author: Leo Trinh
  version: "3.5.0"
  category: sap-abap
  repository: leotrinh/agent-skills-for-sap
---

# SAP ADT Commands

Command-line access to SAP ABAP Development Tools (ADT) REST services from an
AI agent workflow. The client covers areas that many existing MCP tools do not
expose: repository search, object creation, message-class and text-element
maintenance, transport lifecycle, and quality checks.

## Purpose

Give the agent a safe, scriptable way to inspect and modify ABAP objects on a
target SAP system when no MCP tool covers the operation. Every command
returns JSON so results can be routed into subsequent steps.

## When to Use

Activate this skill when the user is working with an SAP ABAP system and any
of the following are true:

- The task requires an ADT operation not exposed by the configured MCP
  tooling (search, package browsing, transport management, message-class
  edits, text-element edits, CDS creation, and similar).
- The user asks to inspect, create, or modify an ABAP object and only ADT
  REST endpoints can do it.
- The user asks for repository-level reporting, such as "list all objects
  owned by user X" or "which objects are inactive".

## When Not to Use

Do not activate this skill when:

- An existing MCP tool already handles the requested operation. Prefer the
  MCP path.
- The user needs SAP GUI-only capabilities such as ATC baseline management,
  runtime debugging with breakpoints, ABAP dictionary DDIC screens, or
  update-task processing.
- The target system is a production tenant and the user has not confirmed
  the intent to run against production.
- The user asks the agent to type or transmit an SAP password directly.

## Safety Rules

The agent must:

1. Prefer an existing MCP tool when it fully supports the requested
   operation.
2. Use this client only when the configured MCP tool does not support the
   required operation.
3. Start with read-only discovery before modifying anything.
4. Never ask the user to paste a password into the chat.
5. Never place a password directly on a generated command line.
6. Use destination-based environment resolution (`--dest`) when it is
   available.
7. Confirm the exact target object, package, transport, and system before a
   write operation.
8. Treat source writes, deletes, unlocks, activation, transport release,
   transport deletion, and object moves as sensitive operations.
9. Require explicit human authorization immediately before any destructive
   or hard-to-reverse operation.
10. Never infer authorization to delete or release something from a broader
    task description such as "clean up", "deploy", or "ship".
11. Report the exact command, the response, and any remaining risk after
    every operation.
12. Stop and report when ADT services, authorizations, object locks, or
    transport configuration prevent safe execution.
13. Never loop retries on authorization failures or malformed requests.
14. Never claim a write succeeded unless the tool response confirms it.

## Tool Selection

When faced with a task, decide in this order:

1. Is there a matching MCP tool? If yes, use it.
2. Does this skill implement the operation? See **Command Groups** below.
3. If neither can do it, tell the user what is missing and suggest SAP GUI
   (SE38, SE80, SM12, SE01/SE09/SE10, SCI) or Eclipse ADT.

Do not fall through to this client "just in case". Every write here is a
real change on the target system.

## Connection Model

The client accepts either explicit flags (`--url`, `--user`, `--pwd`,
`--client`, `--lang`) or a destination name:

```text
--dest SID_CLIENT_USER_LANG
```

Generic example:

```text
--dest DEV_100_DEVELOPER_EN
```

For `--dest DEV_100_DEVELOPER_EN`, the client resolves:

- `url` from `SAP_DEV_URL`
- `user` from `SAP_DEV_DEVELOPER_USER`, else the `DEVELOPER` part of the
  name
- `pwd` from `SAP_DEV_DEVELOPER_PWD` (**must exist**)
- `client` = `100`
- `lang` = `EN`

The one-time setup below is performed by the human. The agent may set the
URL variable when the URL is not secret, but must never set a password
variable itself:

```powershell
# URL — non-secret; may be scripted by the agent when known
setx SAP_DEV_URL "https://sap.example.com:44300"

# Password — set by the human only
setx SAP_DEV_DEVELOPER_PWD "<password>"
```

When any required variable is missing, the client returns a JSON error that
names the exact `setx` commands to run. Treat this as a configuration issue,
not a network failure.

Full details are in
[references/connection-and-credentials.md](references/connection-and-credentials.md).

## Execution Pattern

Every invocation looks like:

```powershell
python $client --dest DEV_100_DEVELOPER_EN <command> [options]
```

Where `$client` holds the repo-root-relative path to the Python source:

```powershell
$client = ".\skills\sap-adt-commands\scripts\adt-client.py"
```

The examples below assume the current working directory is the repository
root. When the skill is installed by an AI client (for example via
`npx skills add`), the on-disk layout is client-specific — resolve the
installed skill directory for that client instead of assuming this path.

Do **not** define the client variable as a two-element string array such
as `$exe = "python", "scripts/adt-client.py"` and then invoke it with
`& $exe ...`. That pattern relies on PowerShell array splatting, is
flagged by PSScriptAnalyzer, and breaks in subtle ways when arguments
contain spaces or quotes. Keep the variable as a single script path and
put `python` on the command line explicitly, or invoke `python` directly
without a variable.

The output is JSON on stdout. Non-zero exit codes accompany connection or
runtime failures. See
[references/development.md](references/development.md) for installation,
dependencies, and the optional local build procedure.

## Command Groups

Each group has a dedicated reference file. Load a reference only when the
agent is actively working on that group.

- **Discovery and inspection** — read-only browsing, search, source read,
  metadata, where-used, history, diff. Load
  [references/command-discovery-and-inspection.md](references/command-discovery-and-inspection.md)
  when the task begins, before any write.
  Commands: `discovery`, `search`, `objects`, `packages`,
  `packages-by-responsible`, `objects-by-user`, `reports-by-user`, `source`,
  `object-properties`, `where-used`, `history`, `diff`, `inactive-objects`,
  `transports`, `transport-contents`, `read-message-class`,
  `read-text-elements`.

- **Source and object management** — writes, creations, activation, unlock,
  and delete. Load
  [references/command-source-and-object-management.md](references/command-source-and-object-management.md)
  when the confirmed task involves modifying or creating ABAP objects.
  Commands: `write-source`, `create-package`, `create-program`,
  `create-class`, `create-interface`, `create-function-group`,
  `create-function-module`, `create-cds`, `create-transaction`,
  `create-message-class`, `activate`, `unlock`, `delete`.

- **Message classes and text elements** — read and edit T100 messages and
  program text elements. Load
  [references/command-messages-and-text-elements.md](references/command-messages-and-text-elements.md)
  when the task involves messages or selection-screen / symbol / heading
  texts.
  Commands: `read-message-class`, `write-messages`, `add-message`,
  `update-message`, `delete-message`, `read-text-elements`,
  `write-text-elements`.

- **Quality checks and testing** — static analysis and unit tests. Load
  [references/command-quality-and-testing.md](references/command-quality-and-testing.md)
  before proposing an activation or release for changes the agent authored.
  Commands: `atc-check`, `abap-unit`.

- **Transports and object lifecycle** — CTS operations. Load
  [references/command-transports-and-lifecycle.md](references/command-transports-and-lifecycle.md)
  when the task involves creating, moving, releasing, or deleting transport
  requests, or when moving objects between tasks.
  Commands: `transports`, `create-transport`, `release-transport`,
  `move-object`, `transport-contents`, `delete-transport`.

- **Troubleshooting** —
  [references/troubleshooting.md](references/troubleshooting.md). Load when
  a command fails with an authorization, endpoint availability, lock,
  activation, transport, or TLS error.

- **Development** —
  [references/development.md](references/development.md). Load when
  installing Python dependencies or when a contributor wants to build a
  local executable with PyInstaller.

## Recommended Workflows

Each workflow is a short sequence, not an exhaustive script. Read the
relevant reference file before running write steps.

### Browse and inspect

```powershell
python $client --dest DEV_100_DEVELOPER_EN discovery
python $client --dest DEV_100_DEVELOPER_EN search "Z*" --type PROG/P
python $client --dest DEV_100_DEVELOPER_EN objects ZEXAMPLE_PACKAGE
python $client --dest DEV_100_DEVELOPER_EN objects-by-user DEVELOPER --type CLAS/OC
python $client --dest DEV_100_DEVELOPER_EN object-properties ZEXAMPLE_PROGRAM --type PROG/P
```

### Read and diff source

```powershell
python $client --dest DEV_100_DEVELOPER_EN source ZEXAMPLE_PROGRAM --type PROG/P
python $client --dest DEV_100_DEVELOPER_EN diff ZEXAMPLE_PROGRAM --type PROG/P
python $client --dest DEV_100_DEVELOPER_EN history ZEXAMPLE_PROGRAM --type PROG/P
```

### Create and activate an object

```powershell
python $client --dest DEV_100_DEVELOPER_EN create-package ZEXAMPLE_PACKAGE `
    --description "Example package" --superpackage ZEXAMPLE_ROOT --transport DEVK900001
python $client --dest DEV_100_DEVELOPER_EN create-program ZEXAMPLE_PROGRAM `
    --description "Example report" --package ZEXAMPLE_PACKAGE --transport DEVK900001
python $client --dest DEV_100_DEVELOPER_EN write-source ZEXAMPLE_PROGRAM `
    --text "REPORT zexample_program." --type PROG/P --transport DEVK900001
python $client --dest DEV_100_DEVELOPER_EN activate ZEXAMPLE_PROGRAM:PROG/P
```

Confirm each step with the human when the write is destructive or targets a
tracked transport.

### Manage messages

```powershell
python $client --dest DEV_100_DEVELOPER_EN create-message-class ZEXAMPLE_MSAG `
    --description "Example messages" --package ZEXAMPLE_PACKAGE --transport DEVK900001
python $client --dest DEV_100_DEVELOPER_EN add-message ZEXAMPLE_MSAG --id 001 --text "No data found" --transport DEVK900001
python $client --dest DEV_100_DEVELOPER_EN update-message ZEXAMPLE_MSAG --id 001 --text "No data for selection" --transport DEVK900001
python $client --dest DEV_100_DEVELOPER_EN activate ZEXAMPLE_MSAG:MSAG/N
```

### Manage transports

```powershell
python $client --dest DEV_100_DEVELOPER_EN transports --owner DEVELOPER
python $client --dest DEV_100_DEVELOPER_EN transport-contents DEVK900001
python $client --dest DEV_100_DEVELOPER_EN create-transport --description "TICKET-1234: Feature X" --package ZEXAMPLE_PACKAGE
python $client --dest DEV_100_DEVELOPER_EN move-object ZEXAMPLE_PROGRAM:PROG/P --transport DEVK900002
```

Never release or delete a transport without contemporaneous human
authorization.

### Run quality gates

```powershell
python $client --dest DEV_100_DEVELOPER_EN atc-check ZEXAMPLE_PROGRAM:PROG/P
python $client --dest DEV_100_DEVELOPER_EN abap-unit ZEXAMPLE_PROGRAM:PROG/P
```

An `UNKNOWN` gate is not a `PASS`. See
[references/command-quality-and-testing.md](references/command-quality-and-testing.md).

## Error Handling

- If the client returns `{"error": "Missing connection values ..."}`, follow
  the connection reference; do not retry blindly.
- On HTTP 401 or 403, stop and report; do not retry with the same
  credentials.
- On HTTP 404 for CTS or workarea endpoints, report the endpoint absence
  and suggest the SAP GUI fallback (SE01, SE09, SE10, SE80).
- On HTTP 406 for message-class or text-element reads, use the client
  default (`Accept: */*`); the client already handles this.
- On any partial success from `release-transport`, stop and report per-task
  results before deciding whether to retry.

Detailed decision trees are in
[references/troubleshooting.md](references/troubleshooting.md).

## Bundled Resources

- `scripts/adt-client.py` — Python source (authoritative and only
  distributed entry point).
- `scripts/adt-client.spec` — optional PyInstaller build configuration for
  contributors who want to package a local executable for their own use.
  No prebuilt binary is committed to the default branch.
- `requirements.txt` — Python runtime dependencies.
- `references/*.md` — focused documentation for each command group.

## Completion Checklist

Before reporting a task complete, verify:

- [ ] The last written object was activated, or the user explicitly asked to
      leave it inactive.
- [ ] Any transport that received new objects is either still open (and
      documented) or was released with explicit human authorization.
- [ ] `object-properties` or a similar read-only call confirms the final
      state matches the intent.
- [ ] The final response to the user includes the exact commands run, the
      resulting transport numbers, and any inconclusive quality-check
      outcomes.
