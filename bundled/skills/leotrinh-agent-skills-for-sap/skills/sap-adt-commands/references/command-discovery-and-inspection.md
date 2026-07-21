# Discovery and Inspection Commands

This file documents the read-only commands provided by `adt-client`. Load this
file when the agent needs to browse, search, or inspect an SAP ABAP system
without modifying anything. Every command in this file is safe to run
repeatedly and does not require a transport request.

Placeholders used throughout: `sap.example.com:44300`, `DEV`, `100`,
`DEVELOPER`, `EN`, `ZEXAMPLE_PACKAGE`, `DEVK900001`. Replace them with values
from the actual configured destination.

## `discovery`

- **Purpose:** List available ADT services and endpoints on the target
  system. Useful for probing which capabilities are enabled before attempting
  a workflow that depends on them.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client --dest DEV_100_DEVELOPER_EN discovery
  ```
- **Result:** JSON containing `workspaces[]`, `collections[]` (each with
  `href` and `title`), and a `total` href count.
- **Limitations:** Some collections listed by discovery may still fail with
  authorization errors when actually called.

## `search`

- **Purpose:** Search ABAP objects by name pattern, type, or package.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client ... search "Z*" --type PROG/P --package ZEXAMPLE_PACKAGE --max 50
  adt-client ... search "ZCL_*" --type CLAS/OC
  ```
- **Arguments:**
  | Arg          | Description                                                             |
  | ------------ | ----------------------------------------------------------------------- |
  | `query`      | Name pattern, for example `Z*`, `ZCL_*`, `*`.                           |
  | `--type`     | Object type filter such as `PROG/P`, `CLAS/OC`, `INTF/OI`, `DEVC/K`.    |
  | `--package`  | Restrict results to a package.                                          |
  | `--author`   | Passed to the ADT quickSearch API, but **ignored by most systems**.     |
  | `--max`      | Maximum number of results (default 100).                                |
- **Limitations:** ADT quickSearch does not respect `--author` on most
  releases. Use `objects-by-user` or `reports-by-user` when filtering by user.

## `objects`

- **Purpose:** List all objects assigned to a package.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client ... objects '$TMP'
  adt-client ... objects ZEXAMPLE_PACKAGE --max 500
  ```
- **Arguments:** `package` (positional), `--max` (default 999).

## `packages`

- **Purpose:** List sub-packages of a parent package.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client ... packages '$TMP'
  adt-client ... packages ZEXAMPLE_PACKAGE_ROOT
  ```

## `packages-by-responsible`

- **Purpose:** List packages whose `adtcore:responsible` field matches a
  given user. Fetches each matching package's properties and filters by
  responsible.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client ... packages-by-responsible DEVELOPER
  adt-client ... packages-by-responsible DEVELOPER --pattern "Z*" --max 500
  ```
- **Arguments:** `responsible` (positional), `--pattern` (default `Z*`),
  `--max` (default 500).

## `objects-by-user`

- **Purpose:** List all objects across packages owned by a user. Combines
  `packages-by-responsible` and `objects` into a single call. This is the
  correct proxy for "what does this developer own" because ADT quickSearch
  does not filter reliably by author.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client ... objects-by-user DEVELOPER
  adt-client ... objects-by-user DEVELOPER --type PROG/P
  adt-client ... objects-by-user DEVELOPER --type CLAS/OC --pattern "ZEXAMPLE*"
  ```
- **Arguments:** `USER` (positional), `--type`, `--pattern` (default `Z*`).
- **Result:** `by_type` summary plus a flat `objects[]` list.

## `reports-by-user`

- **Purpose:** Convenience alias for `objects-by-user USER --type PROG/P`.
  Returns programs and executable reports only.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client ... reports-by-user DEVELOPER
  adt-client ... reports-by-user DEVELOPER --pattern "ZEXAMPLE*"
  ```

## `source`

- **Purpose:** Read the active source code of an ABAP object.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client ... source ZEXAMPLE_PROGRAM --type PROG/P
  adt-client ... source ZCL_EXAMPLE --type CLAS/OC
  ```
- **Supported types:** `PROG/P`, `CLAS/OC`, `INTF/OI`, `FUGR/FF`, `DDLS/DF`.

## `object-properties`

- **Purpose:** Read full metadata of any ABAP object.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client ... object-properties ZEXAMPLE_PROGRAM --type PROG/P
  adt-client ... object-properties ZEXAMPLE_PACKAGE --type DEVC/K
  ```
- **Result fields:** `description`, `package`, `responsible`, `created_by`,
  `created_at`, `changed_by`, `changed_at`, `master_lang`, `inactive`.

## `where-used`

- **Purpose:** Find objects that reference a given object.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client ... where-used ZCL_EXAMPLE --type CLAS/OC
  adt-client ... where-used ZEXAMPLE_PROGRAM --type PROG/P --max 200
  ```
- **Arguments:** `name`, `--type` (default `CLAS/OC`), `--max` (default 100).
- **Limitations:** Uses
  `POST /sap/bc/adt/repository/informationsystem/usageReferences?uri=...` and
  can return HTTP 500 on some releases.

## `history`

- **Purpose:** Show change history of an ABAP object.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client ... history ZEXAMPLE_PROGRAM --type PROG/P
  ```
- **Result:** `versions[]` with `changed_at`, `changed_by`, plus a `source`
  field indicating the data path used:
  - `versions_endpoint` — full history from `/source/versions`.
  - `revision_atom_feed` — full history from the object's atom versions link.
  - `object_properties_fallback` — latest change only, when no versions data
    source is available on the release.

## `diff`

- **Purpose:** Compare active versus inactive (unsaved) source of an object.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client ... diff ZEXAMPLE_PROGRAM --type PROG/P
  ```
- **Result:** Unified diff. `has_changes: false` when there are no pending
  changes. The diff payload is truncated at 10 000 characters.

## `inactive-objects`

- **Purpose:** List inactive (not-yet-activated) objects visible to the
  session.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client ... inactive-objects
  adt-client ... inactive-objects --user-filter DEVELOPER
  ```
- **Limitations:** Uses `/sap/bc/adt/activation/inactiveobjects` with a
  fallback to `/sap/bc/adt/workarea/inactive`. Returns HTTP 404 on some
  releases.

## `transports`

- **Purpose:** List open transport requests.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client ... transports
  adt-client ... transports --owner DEVELOPER
  ```
- **Arguments:** `--owner` filters by transport owner.
- **Limitations:** Requires CTS REST to be enabled on the SAP system. Returns
  HTTP 404 when the CTS endpoints are not exposed.

## `transport-contents`

- **Purpose:** Show the objects inside a transport request.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client ... transport-contents DEVK900001
  ```
- **Result:** `objects[]` with `pgmid`, `type`, and `name` fields.
- **Limitations:** Depends on CTS REST availability.

## `read-message-class`

- **Purpose:** Read the raw XML of a message class. Useful for inspecting
  existing messages before mutating anything.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client ... read-message-class ZEXAMPLE_MSAG
  ```
- **Limitations:** Path and accepted `Content-Type` vary by SAP release; the
  client auto-probes both known variants.

## `read-text-elements`

- **Purpose:** Read text elements for a program, class, or function group.
  Sections are `selections`, `symbols`, and `headings`. If `--section` is
  omitted, all three are returned.
- **Read-only.**
- **Syntax:**
  ```bash
  adt-client ... read-text-elements ZEXAMPLE_PROGRAM --type PROG/P
  adt-client ... read-text-elements ZCL_EXAMPLE --type CLAS/OC
  adt-client ... read-text-elements ZFUGR_EXAMPLE --type FUGR/FF
  adt-client ... read-text-elements ZEXAMPLE_PROGRAM --section selections
  ```
- **Supported types:** `PROG/P`, `CLAS/OC`, `FUGR/FF`.
- **Limitations:** The read call uses `Accept: */*` because a specific
  content type returns HTTP 406 on some releases.

## Read-Only Workflow Guidance

Start every session by validating connectivity with a cheap read-only call
such as `discovery` or `object-properties`. Verifying that the destination
works before running write commands avoids wasted effort and reduces the
chance of a partial change.
