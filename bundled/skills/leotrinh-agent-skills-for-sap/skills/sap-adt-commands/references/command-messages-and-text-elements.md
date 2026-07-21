# Message Classes and Text Elements

This file documents the message-class and text-element commands. Load this
file when the agent needs to inspect or modify SAP T100 message classes or
the text elements (selections, symbols, headings) of a program, class, or
function group.

Placeholders used throughout: `DEV_100_DEVELOPER_EN`, `ZEXAMPLE_MSAG`,
`ZEXAMPLE_PROGRAM`, `ZCL_EXAMPLE`, `ZFUGR_EXAMPLE`, `DEVK900001`.

## Message Class Overview

Messages are stored on the server as a single XML document per message class.
The client operates on individual messages through a read-patch-write cycle
so that concurrent messages authored by other developers are preserved.

Common workflow: lock → read current XML → patch in memory → PUT full XML →
unlock → activate.

The `activate` step is a separate command; see
`command-source-and-object-management.md`.

## `read-message-class`

- **Purpose:** Read the current raw XML of a message class. Useful before a
  bulk change or to verify a specific message ID exists.
- **Class:** Read-only.
- **Syntax:**
  ```bash
  adt-client ... read-message-class ZEXAMPLE_MSAG
  ```
- **Limitations:** Path and accepted `Content-Type` vary by SAP release; the
  client auto-probes both known variants.

## `write-messages`

- **Purpose:** Bulk write a full messages XML payload to an existing message
  class. Use this when you have prepared the complete message set offline.
- **Class:** Write. Does not activate.
- **Workflow:** lock → PUT → unlock.
- **Syntax:**
  ```bash
  adt-client ... write-messages ZEXAMPLE_MSAG --file all_messages.xml
  ```
- **Notes:** Follow with `activate ZEXAMPLE_MSAG:MSAG/N`.

## `add-message` / `update-message`

- **Purpose:** Upsert a single message. Both commands share the same
  implementation; `update-message` is provided for readability.
- **Class:** Write. Does not activate.
- **Behavior:**
  - Reads the current XML.
  - Zero-pads the `--id` to three digits automatically (`1` becomes `001`).
  - Inserts the message if the ID does not exist.
  - Replaces the message text if the ID exists.
  - Locks, PUTs the full patched XML, then unlocks.
- **Syntax:**
  ```bash
  adt-client ... add-message ZEXAMPLE_MSAG --id 001 --text "No data found"
  adt-client ... add-message ZEXAMPLE_MSAG --id 015 --text "Export complete: &1 records" \
    --transport DEVK900001
  adt-client ... update-message ZEXAMPLE_MSAG --id 001 --text "Updated text"
  ```
- **Follow-up:** Activate with `activate ZEXAMPLE_MSAG:MSAG/N`.

## `delete-message`

- **Purpose:** Remove a single message from a message class by ID.
- **Class:** Write. The removed message is gone on the next activation.
- **Behavior:** Reads XML → removes the element with the matching ID → locks
  → PUTs → unlocks.
- **Syntax:**
  ```bash
  adt-client ... delete-message ZEXAMPLE_MSAG --id 015
  adt-client ... delete-message ZEXAMPLE_MSAG --id 015 --transport DEVK900001
  ```
- **Errors:** Returns an error if the specified ID is not present in the
  class.
- **Follow-up:** Activate with `activate ZEXAMPLE_MSAG:MSAG/N`.

## Text Elements Overview

Text elements are stored per object under three sections. Each section has
its own vendor-specific content type:

| Section       | Purpose                              | Format                                          |
| ------------- | ------------------------------------ | ----------------------------------------------- |
| `selections`  | Selection screen field texts         | `FIELD_NAME=Description text` per line          |
| `symbols`     | Text symbols                         | `@MaxLength:N\nCODE=Text` per symbol            |
| `headings`    | List and column headings             | `key=value` per line                            |

Supported object types are `PROG/P` (default), `CLAS/OC`, and `FUGR/FF`.

## `read-text-elements`

- **Purpose:** Read one or all text-element sections.
- **Class:** Read-only.
- **Syntax:**
  ```bash
  adt-client ... read-text-elements ZEXAMPLE_PROGRAM --type PROG/P
  adt-client ... read-text-elements ZEXAMPLE_PROGRAM --section selections
  adt-client ... read-text-elements ZCL_EXAMPLE --type CLAS/OC
  adt-client ... read-text-elements ZFUGR_EXAMPLE --type FUGR/FF
  ```
- **Arguments:** `name`, `--type` (default `PROG/P`), `--section` optional.
- **Notes:** Uses `Accept: */*` because a specific content type returns
  HTTP 406 on some releases.

## `write-text-elements`

- **Purpose:** Write a single text-element section.
- **Class:** Write. Does not activate.
- **Workflow:** lock (falls back to program object lock if the text-element
  object lock fails) → PUT section → unlock.
- **Syntax:**
  ```bash
  adt-client ... write-text-elements ZEXAMPLE_PROGRAM \
    --section selections --file selections.txt --transport DEVK900001

  adt-client ... write-text-elements ZEXAMPLE_PROGRAM \
    --section symbols --text "@MaxLength:10\nTITLE=Example title" --transport DEVK900001
  ```
- **Arguments:**
  | Arg           | Description                                              |
  | ------------- | -------------------------------------------------------- |
  | `--section`   | Required: `selections`, `symbols`, or `headings`.        |
  | `--file`      | Path to a UTF-8 text file with section content.          |
  | `--text`      | Inline section content.                                  |
  | `--transport` | Transport request number.                                |
  | `--type`      | Object type (default `PROG/P`).                          |
- **Content:** The payload must exactly match the ADT plain-text format
  returned by `read-text-elements`. Read first when uncertain.
- **Follow-up:** Activate the object with `activate NAME:TYPE`.

## Recommended Flow for Message Changes

1. `read-message-class ZEXAMPLE_MSAG` — confirm current state.
2. Plan the diff (new IDs, changed texts, removed IDs).
3. Perform each mutation with `add-message`, `update-message`, or
   `delete-message`, always passing `--transport` when the class is tracked.
4. `activate ZEXAMPLE_MSAG:MSAG/N` — publish the change.
5. `read-message-class ZEXAMPLE_MSAG` — verify.

## Recommended Flow for Text-Element Changes

1. `read-text-elements NAME --type ... --section ...` — read current content.
2. Edit locally to preserve unrelated entries.
3. `write-text-elements NAME --section ... --file ... --transport ...`.
4. `activate NAME:TYPE` — publish.
5. `read-text-elements NAME --section ...` — verify.
