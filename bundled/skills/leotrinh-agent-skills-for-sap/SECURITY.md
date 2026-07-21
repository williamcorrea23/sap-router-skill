# Security Policy

## Supported Versions

This repository does not currently publish tagged releases. Only the latest
version on the default branch is actively maintained and eligible for security
fixes. If a release process is introduced later, this document will be updated
to reflect the supported version range.

## Reporting a Vulnerability

Please report any suspected vulnerability privately.

- Preferred: use **GitHub Private Vulnerability Reporting** or open a **GitHub
  Security Advisory** on this repository, if available.
- Do **not** open a public issue, pull request, discussion, or comment
  describing an exploitable vulnerability. Public disclosure before a fix is
  available can put downstream users at risk.

When reporting a vulnerability, please include:

- The affected skill, script, or file path.
- A clear description of the issue and its impact.
- Steps to reproduce, ideally with a minimal example.
- Any mitigations or workarounds you are already aware of.

Please do **not** include:

- SAP passwords, session cookies, bearer tokens, or client certificates.
- Real customer system hostnames, SIDs, usernames, or business data.
- Screenshots, logs, or captures that contain credentials or personal data.

If reproducing the issue requires such data, redact it before submitting and
describe the general shape of the input instead.

## Handling Credentials

This project is designed so that users never need to paste SAP passwords into
an AI conversation.

- Skills that need SAP credentials read them from environment variables or
  another secure local mechanism (for example, values set with `setx` on
  Windows, stored in a system keychain, or resolved from a secret manager).
- The optional `--pwd` flag on the CLI exists for backward compatibility only.
  Documentation discourages plaintext passwords on the command line, and the
  skill guidance instructs agents to prefer destination-based resolution.
- Contributors must never commit real credentials or example values that could
  be mistaken for real credentials. Use clearly fictional placeholders such as
  `<password>` or `DEVELOPER` in documentation.

## Destructive Operations

Some ADT operations exposed by this repository are difficult to reverse. This
includes, but is not limited to:

- Writing or overwriting source code.
- Activating objects.
- Unlocking objects that are held by another user's session.
- Deleting ABAP objects.
- Creating, releasing, or deleting transport requests.
- Moving objects between transport tasks.

The `SKILL.md` for `sap-adt-commands` instructs agents to:

- Prefer read-only inspection before any modification.
- Confirm the exact object, package, transport, and target system.
- Require an explicit human authorization immediately before running a
  destructive command.
- Never infer authorization to delete or release something from a general
  request such as "clean up" or "deploy".

If you discover a workflow or prompt pattern that reliably bypasses these
guardrails, please treat it as a security issue and report it privately.

## Binary Distribution

This repository does **not** distribute a prebuilt executable from the
default branch. The Python source at
`skills/sap-adt-commands/scripts/adt-client.py` is the reference
implementation and the only supported entry point.

- `skills/sap-adt-commands/scripts/adt-client.spec` is included as a
  contributor PyInstaller build configuration. It is a build hint, not a
  runtime artifact. It does not produce any executable that ships with
  the repository.
- Users who want a single-file executable may build one locally with
  PyInstaller. Locally built binaries are the responsibility of the
  builder: they are not code-signed, not independently audited, and not
  reproducibly built by this project.
- If an official binary is introduced later, it will be published through
  **GitHub Releases** with a controlled build process rather than
  committed to the default branch.

Running the Python source directly remains the supported and preferred
workflow, especially in environments with strict binary policies.

## TLS Verification

The `sap-adt-commands` Python client verifies the SAP server certificate
by default. This is intentional and matches standard `requests` behavior.

- Corporate SAP systems that use a private certificate authority should
  supply the CA bundle path with `--ca-bundle <path>` or the environment
  variable `SAP_ADT_CA_BUNDLE`.
- `--insecure` disables TLS verification for the current invocation. It
  is intended only for controlled troubleshooting and non-production
  environments. When active the client prints a warning to `stderr` and
  suppresses only the expected `urllib3` insecure-request warning; it
  does not print credentials, cookies, tokens, or authorization headers.
- The client never falls back from secure verification to insecure
  behavior automatically. A TLS failure remains a failure unless the
  user explicitly opts in with `--insecure` or supplies a working CA
  bundle.
- `--insecure` combined with `--ca-bundle` (or `SAP_ADT_CA_BUNDLE`) is a
  configuration error. The client fails fast with a user-facing
  validation message instead of silently choosing one.

Users should never paste real SAP passwords, session cookies, tokens, or
private certificate material into an AI conversation, regardless of the
TLS mode. The credential-handling rules in the section above apply in
every mode.

## Public Disclosure

We will coordinate public disclosure with reporters where reasonably possible.
By default, once a fix is available on the default branch, the underlying
issue may be described in the commit history, changelog, or advisory. If you
require a specific embargo period, please state it clearly in your report.
