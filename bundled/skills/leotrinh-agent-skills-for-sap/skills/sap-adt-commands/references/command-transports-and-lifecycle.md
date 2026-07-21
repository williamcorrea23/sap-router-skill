# Transports and Object Lifecycle

This file documents transport-related commands. Load this file when the
agent is asked to inspect, create, modify, release, or delete SAP transport
requests, or when moving objects between transport tasks. Transport
operations are among the most difficult to reverse in SAP; the safety rules
in this file are non-optional.

Placeholders used throughout: `DEV_100_DEVELOPER_EN`, `DEVK900001`,
`DEVK900002`, `ZEXAMPLE_PROGRAM`, `ZEXAMPLE_PACKAGE`.

## Common Prerequisites

All transport commands require the CTS REST services on the target SAP
system:

- `/sap/bc/adt/cts/transports`
- `/sap/bc/adt/cts/transportrequests`
- `/sap/bc/adt/cts/workbench`

If a command returns HTTP 404, the CTS REST endpoints are almost certainly
not exposed. On such systems, transports must be managed through SE01, SE09,
SE10, or STMS. Do not treat HTTP 404 as authorization failure.

## `transports`

- **Purpose:** List open transport requests.
- **Class:** Read-only.
- **Syntax:**
  ```bash
  adt-client ... transports
  adt-client ... transports --owner DEVELOPER
  ```
- **Notes:** Use before creating a new transport to check for an existing
  one that already fits the work item.

## `transport-contents`

- **Purpose:** Show the objects inside a transport.
- **Class:** Read-only.
- **Syntax:**
  ```bash
  adt-client ... transport-contents DEVK900001
  ```
- **Result:** `objects[]` with `pgmid`, `type`, `name`. Inspect this before
  releasing or deleting anything.

## `create-transport`

- **Purpose:** Create a new Workbench transport request.
- **Class:** Write. Reversible only by deleting the transport while empty.
- **Underlying call:** POSTs an ABAP-serialized `CreateCorrectionRequest`
  structure to `/sap/bc/adt/cts/transports`.
- **Syntax:**
  ```bash
  adt-client ... create-transport --description "TICKET-1234: My feature"
  adt-client ... create-transport --description "TICKET-1234: My feature" \
    --package ZEXAMPLE_PACKAGE
  ```
- **Arguments:**
  | Arg             | Description                                                       |
  | --------------- | ----------------------------------------------------------------- |
  | `--description` | Required transport description.                                   |
  | `--package`     | Package that determines the transport route (optional).           |
  | `--target`      | Deprecated. Target follows the package's transport layer.         |
  | `--type-tr`     | `K` (Workbench, default). `W` (Customizing) is not supported.     |
- **Result:** `transport` number on success, plus a hint to use SE01/SE09
  when CTS REST is not enabled.

## `release-transport`

- **Purpose:** Release a transport request. Releases all open tasks first,
  then the request itself. Each step calls
  `POST /sap/bc/adt/cts/transportrequests/{nr}/newreleasejobs`.
- **Class:** Destructive from an SAP process perspective. Once released, the
  transport begins its journey through downstream systems. This is
  difficult to reverse.
- **Syntax:**
  ```bash
  adt-client ... release-transport DEVK900001
  ```
- **Result:** `released: true` when the release succeeded, plus per-task
  results.
- **Rules:**
  1. Always run `transport-contents DEVK900001` before releasing to confirm
     the objects.
  2. Verify the requester and expected downstream target system with the
     human.
  3. Do not release just because the surrounding task is described as
     "deploy" or "ship". Wait for an explicit release authorization.

## `move-object`

- **Purpose:** Record an object into a different transport task. The
  underlying mechanism re-locks the object with the target `corrNumber`,
  which registers the object in that transport task and automatically
  de-registers it from the previous task.
- **Class:** Write. The object itself is not modified; only the CTS
  association is.
- **Fallback:** If the lock-based approach fails, the client falls back to a
  direct task-objects PUT.
- **Syntax:**
  ```bash
  adt-client ... move-object ZEXAMPLE_PROGRAM:PROG/P --transport DEVK900002
  adt-client ... move-object ZEXAMPLE_PROGRAM:PROG/P --transport DEVK900002 --task DEVK900003
  ```
- **Arguments:**
  | Arg           | Description                                                              |
  | ------------- | ------------------------------------------------------------------------ |
  | `object`      | `NAME:TYPE` (positional).                                                |
  | `--transport` | Required target transport.                                               |
  | `--task`      | Optional task; auto-detected as the first task when omitted.             |
- **Rule:** Confirm both the source and target transports before running.

## `delete-transport`

- **Purpose:** Delete one or more empty transport requests.
- **Class:** Destructive. Cannot be undone.
- **Preconditions:** The transport must be empty. If it contains objects,
  move them first with `move-object`.
- **Syntax:**
  ```bash
  adt-client ... delete-transport DEVK900002 --force
  adt-client ... delete-transport DEVK900003 DEVK900004 --force
  ```
- **Result:** Per-transport results.
- **Rules:**
  1. Always confirm each transport number with the human before deletion.
  2. The `--force` flag suppresses the interactive prompt only; it does not
     replace human authorization.
  3. Do not delete a transport unless the client confirms the transport is
     empty and unreleased.

## Safety Rules for Transport Operations

1. **Read before write.** Use `transports` and `transport-contents` first.
2. **Confirm the target system.** Transports flow to downstream clients
   defined by the transport layer. Verify with the human.
3. **Never assume production intent.** Even if the surrounding task refers
   to a release, do not release or delete a transport without explicit,
   contemporary authorization.
4. **Never batch destructive operations.** Release and delete transports one
   at a time so a human can verify the outcome between each step.
5. **Never treat CTS REST 404 as authorization failure.** It means the
   endpoints are not enabled on the SAP system. Fall back to SE01/SE09/SE10
   through SAP GUI or ADT in Eclipse.
6. **Do not release a transport to fix a bug you have not verified is
   fixed.** Run `atc-check` and `abap-unit` first (see
   `command-quality-and-testing.md`).
