# Source and Object Management Commands

This file documents commands that create, modify, activate, unlock, or delete
ABAP objects. Load this file only when the agent has confirmed that the
requested change is authorized and has already gathered the required package,
transport, and object details through the read-only commands in
`command-discovery-and-inspection.md`.

**Safety summary**

| Command                    | Class                             | Notes                                                                    |
| -------------------------- | --------------------------------- | ------------------------------------------------------------------------ |
| `write-source`             | Write                             | Overwrites source. Does not activate. Requires a lock and a transport.   |
| `create-package`           | Write                             | Creates DEVC/K. Local vs transport-tracked depends on the transport layer. |
| `create-program`           | Write                             | Creates PROG/P shell. Follow up with `write-source` and `activate`.       |
| `create-class`             | Write                             | Creates CLAS/OC shell.                                                   |
| `create-interface`         | Write                             | Creates INTF/OI shell.                                                   |
| `create-function-module`   | Write                             | Creates FUNC/FF inside an existing function group.                       |
| `create-function-group`    | Write                             | Creates FUGR/FF shell.                                                   |
| `create-cds`               | Write                             | Creates DDLS/DF; may write initial source when `--source*` provided.     |
| `create-message-class`     | Write                             | Creates an empty MSAG/N shell.                                           |
| `create-transaction`       | Write                             | Creates TRAN/T bound to an existing program.                             |
| `activate`                 | Write (visible to other users)    | Publishes changes. Reversible only by reactivating a prior version.      |
| `unlock`                   | Destructive (may lose work)       | Force-releases a lock. Unsaved changes held by that lock are lost.       |
| `delete`                   | Destructive (irreversible)        | Removes an object; requires transport for non-`$TMP` objects.            |

Placeholders used throughout: `DEV_100_DEVELOPER_EN`, `ZEXAMPLE_PACKAGE`,
`DEVK900001`, `ZEXAMPLE_PROGRAM`, `ZCL_EXAMPLE`, `ZIF_EXAMPLE`,
`ZFUGR_EXAMPLE`, `ZEXAMPLE_MSAG`.

## `write-source`

- **Purpose:** Write or replace the source code of an existing object.
- **Class:** Write. Does not activate. The change is invisible to other users
  until `activate` is called.
- **Workflow:** lock → PUT source → unlock.
- **Syntax:**
  ```bash
  adt-client ... write-source ZEXAMPLE_PROGRAM --file source.abap --type PROG/P
  adt-client ... write-source ZEXAMPLE_PROGRAM --text "REPORT zexample_program." --type PROG/P
  ```
- **Arguments:**
  | Arg           | Description                                                             |
  | ------------- | ----------------------------------------------------------------------- |
  | `--file`      | Path to a UTF-8 `.abap` source file.                                    |
  | `--text`      | Inline source text for small snippets.                                  |
  | `--transport` | Lock into a specific transport. Avoids auto-generated transports.       |
  | `--type`      | Object type (default `PROG/P`).                                         |
- **Risk:** Overwrites the current active version once activated. Diff the
  new source against the current source when appropriate.

## `create-package`

- **Purpose:** Create an ABAP package (DEVC/K).
- **Class:** Write.
- **Syntax:**
  ```bash
  adt-client ... create-package ZEXAMPLE_PACKAGE \
    --description "Example package" \
    --superpackage ZEXAMPLE_ROOT \
    --transport DEVK900001 \
    --sw-component HOME \
    --transport-layer ZDEV
  ```
- **Arguments:**
  | Arg                  | Description                                                    |
  | -------------------- | -------------------------------------------------------------- |
  | `name`               | Package name (positional).                                     |
  | `--description`      | Required short description.                                    |
  | `--superpackage`     | Required parent package.                                       |
  | `--transport`        | Transport request number (required for tracked packages).      |
  | `--sw-component`     | Software component (default `HOME`).                           |
  | `--transport-layer`  | Transport layer, for example `ZDEV`. Leave empty for local.    |

## `create-program`

- **Purpose:** Create an executable ABAP program shell (PROG/P).
- **Class:** Write.
- **Notes:** Uses the `program:abapProgram` XML namespace. Follow with
  `write-source` and `activate` when initial source is needed.
- **Syntax:**
  ```bash
  adt-client ... create-program ZEXAMPLE_PROGRAM \
    --description "Example report" \
    --package ZEXAMPLE_PACKAGE \
    --transport DEVK900001
  ```

## `create-class`

- **Purpose:** Create an ABAP class (CLAS/OC).
- **Class:** Write.
- **Syntax:**
  ```bash
  adt-client ... create-class ZCL_EXAMPLE \
    --description "Example helper class" \
    --package ZEXAMPLE_PACKAGE \
    --transport DEVK900001
  ```

## `create-interface`

- **Purpose:** Create an ABAP interface (INTF/OI).
- **Class:** Write.
- **Syntax:**
  ```bash
  adt-client ... create-interface ZIF_EXAMPLE \
    --description "Example interface" \
    --package ZEXAMPLE_PACKAGE \
    --transport DEVK900001
  ```

## `create-function-group`

- **Purpose:** Create a function group (FUGR/FF) shell.
- **Class:** Write.
- **Syntax:**
  ```bash
  adt-client ... create-function-group ZFUGR_EXAMPLE \
    --description "Example function group" \
    --package ZEXAMPLE_PACKAGE \
    --transport DEVK900001
  ```

## `create-function-module`

- **Purpose:** Create a function module (FUNC/FF) inside an existing function
  group. Function modules are created under
  `functions/groups/{group}/fmodules` with `adtcore:containerRef`.
- **Class:** Write.
- **Syntax:**
  ```bash
  adt-client ... create-function-module Z_EXAMPLE_FM \
    --description "Calculate example value" \
    --group ZFUGR_EXAMPLE \
    --package ZEXAMPLE_PACKAGE \
    --transport DEVK900001
  ```
- **Arguments:**
  | Arg                  | Description                                                              |
  | -------------------- | ------------------------------------------------------------------------ |
  | `--group`            | Required parent function group.                                          |
  | `--package`          | Ignored — the FM inherits the group's package.                           |
  | `--processing-type`  | Informational only; the ADT creation API cannot set the processing type. |

## `create-cds`

- **Purpose:** Create a CDS Data Definition (DDLS/DF) via
  `/sap/bc/adt/ddic/ddl/sources`. Optionally writes initial source when
  `--source` or `--source-file` is provided.
- **Class:** Write.
- **Syntax:**
  ```bash
  adt-client ... create-cds ZCDS_EXAMPLE \
    --description "Example CDS view" \
    --package ZEXAMPLE_PACKAGE \
    --transport DEVK900001

  adt-client ... create-cds ZCDS_EXAMPLE \
    --description "Example CDS view" \
    --package ZEXAMPLE_PACKAGE \
    --source-file example_view.ddls
  ```
- **Notes:** The `ddic/ddla/sources` endpoint is a different object type
  (annotation definitions). Do not use it for data definitions.
- **Follow-up:** Use `source ... --type DDLS/DF` to read and
  `write-source ... --type DDLS/DF` to update the CDS source later.

## `create-message-class`

- **Purpose:** Create an empty message class (MSAG/N) shell.
- **Class:** Write.
- **Syntax:**
  ```bash
  adt-client ... create-message-class ZEXAMPLE_MSAG \
    --description "Example messages" \
    --package ZEXAMPLE_PACKAGE \
    --transport DEVK900001
  ```
- **Follow-up:** Add messages with `add-message` or `write-messages` and
  activate with `activate ZEXAMPLE_MSAG:MSAG/N`.

## `create-transaction`

- **Purpose:** Create a report transaction code (TRAN/T) bound to an
  existing program.
- **Class:** Write.
- **Syntax:**
  ```bash
  adt-client ... create-transaction ZEXAMPLE_TCODE \
    --description "Example transaction" \
    --program ZEXAMPLE_PROGRAM \
    --package ZEXAMPLE_PACKAGE \
    --transport DEVK900001
  ```

## `activate`

- **Purpose:** Activate one or more ABAP objects using the ADT activation
  endpoint.
- **Class:** Write. Publishes changes to all users of the system.
- **Syntax:**
  ```bash
  adt-client ... activate ZEXAMPLE_PROGRAM:PROG/P
  adt-client ... activate ZEXAMPLE_PROGRAM:PROG/P ZCL_EXAMPLE:CLAS/OC ZEXAMPLE_MSAG:MSAG/N
  ```
- **Input format:** `NAME:TYPE` per positional argument.
- **Result fields:** `success`, `inactive_remaining`, `errors`.
- **Common failure:** HTTP 403 when the object is locked by an interactive
  editor session (typically SE38/SE80). Close the editor and retry.

## `unlock`

- **Purpose:** Force-release a lock held by the current user's ADT session.
- **Class:** Destructive because any unsaved changes tied to the lock are
  dropped.
- **Syntax:**
  ```bash
  adt-client ... unlock ZEXAMPLE_PROGRAM --type PROG/P
  ```
- **Limitations:** Cannot release locks held by other users' sessions. Those
  require an administrator using transaction SM12.
- **Agent rule:** Always confirm with the human that unsaved changes can be
  discarded before running this command.

## `delete`

- **Purpose:** Delete an ABAP object.
- **Class:** Destructive and irreversible outside of transport recovery
  workflows.
- **Syntax:**
  ```bash
  adt-client ... delete ZEXAMPLE_PROGRAM --transport DEVK900001 --force
  ```
- **Arguments:**
  | Arg           | Description                                                              |
  | ------------- | ------------------------------------------------------------------------ |
  | `name`        | Object name (positional).                                                |
  | `--type`      | Object type (default `PROG/P`).                                          |
  | `--transport` | Required for any object outside the `$TMP` local package.                |
  | `--force`     | Skips the interactive confirmation prompt for non-interactive use.       |
- **Agent rule:** The `--force` flag suppresses the interactive prompt but
  never suppresses the requirement for explicit human authorization. Confirm
  the exact object, type, and transport with the human before running.

## Recommended End-to-End Flow

1. Discover the object and confirm ownership using `object-properties`,
   `objects-by-user`, or `source`.
2. Read or diff the current state (`source`, `diff`, `history`).
3. Obtain or create a suitable transport request. Do not write into a
   transport that was created for a different work item.
4. Perform the write (`write-source`, `create-*`).
5. Activate the change (`activate NAME:TYPE`).
6. Verify the resulting state with `object-properties` and `history`.
7. Move the object into the correct transport with `move-object` if required.
