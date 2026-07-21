# Quality Checks and Testing Commands

This file documents the static analysis and unit test commands. Load this
file when the agent needs to run ATC or ABAP Unit against a set of objects,
or when it needs to reason about the meaning of a `gate` outcome.

Placeholders used throughout: `DEV_100_DEVELOPER_EN`, `ZEXAMPLE_PROGRAM`,
`ZCL_EXAMPLE`.

## `atc-check`

- **Purpose:** Run ABAP Test Cockpit (ATC) static analysis on one or more
  objects.
- **Class:** Read-only from the SAP perspective. The command does not change
  the objects being checked, but it does create ATC worklists on the server.
- **Underlying flow:**
  1. `POST /sap/bc/adt/atc/worklists` — create a worklist.
  2. `POST /sap/bc/adt/atc/runs` — run the check.
  3. `GET /sap/bc/adt/atc/worklists/{id}` — read findings.
- **Syntax:**
  ```bash
  adt-client ... atc-check ZEXAMPLE_PROGRAM:PROG/P
  adt-client ... atc-check ZEXAMPLE_PROGRAM:PROG/P ZCL_EXAMPLE:CLAS/OC
  ```
- **Input format:** `NAME:TYPE` per positional argument.
- **Result:** JSON with `findings_count`, `findings[]`, and `gate`.
- **`gate` values:**
  - `PASS` — no findings above the configured severity.
  - `FAIL` — one or more findings.
  - `UNKNOWN_POLL_UNSUPPORTED` — the target release did not return worklist
    data through the REST endpoint. The check itself may or may not have run;
    the agent must not treat this as `PASS`.
- **System limitations:** Some S/4HANA Cloud and older releases return
  HTTP 406 on the worklist endpoint. When this happens the check must be run
  from SE38 or SCI. Do not report `PASS` when the check could not complete.

## `abap-unit`

- **Purpose:** Run ABAP Unit tests defined in one or more objects.
- **Class:** Read-only from the object perspective, but tests may exercise
  side effects if they touch the database.
- **Syntax:**
  ```bash
  adt-client ... abap-unit ZEXAMPLE_PROGRAM:PROG/P
  adt-client ... abap-unit ZEXAMPLE_PROGRAM:PROG/P ZCL_EXAMPLE:CLAS/OC
  ```
- **Input format:** `NAME:TYPE` per positional argument. Type defaults to
  `PROG/P` when omitted.
- **Result:** `gate` (`PASS` or `FAIL`), `total`, `passed`, `failed`, a
  method list, and failure details for each failing test.
- **System limitations:** The XML schema returned by ABAP Unit varies by SAP
  release. Some releases return HTTP 400 for the current request shape. When
  this occurs, run the tests through SE80 or ADT in Eclipse to confirm.

## Interpreting Outcomes

- **`PASS`** means the endpoint responded and the response contains no
  failures above the configured gate.
- **`FAIL`** means the endpoint responded and at least one failure or ATC
  finding is present.
- **Unknown or unsupported** means the endpoint did not return usable data.
  This is not a `PASS`. Do not use the absence of findings from a failed poll
  to justify releasing a transport or activating other dependent objects.

## Safety Rules

1. Do not declare a change "safe to activate" solely because `atc-check`
   returned `PASS`. ATC is a static analysis and does not exercise runtime
   behavior.
2. Do not declare a change "safe to release" solely because `abap-unit`
   returned `PASS`. Unit test coverage is bounded by the tests actually
   defined for the code.
3. When either command returns unknown or unsupported, treat the result as
   inconclusive and either run the check through SAP GUI (SE38, SCI, SE80)
   or ask the human whether it is acceptable to proceed without the check.
4. Never retry a `FAIL` outcome as if repeated calls could change the
   verdict. Fix the underlying issue and rerun.

## Recommended Verification Flow

1. `atc-check NAME:TYPE ...` — early quality signal, especially on new
   objects.
2. `abap-unit NAME:TYPE ...` — confirm existing behavior still works.
3. `object-properties NAME --type TYPE` — confirm the object is active.
4. `inactive-objects` — verify no leftover inactive objects remain.
5. Only after these checks and a human confirmation, proceed to
   `release-transport`. Transport release is covered in
   `command-transports-and-lifecycle.md`.
