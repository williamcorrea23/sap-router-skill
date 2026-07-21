# Scripts and Resources

Load this file before adding any script under `scripts/`, and again during
Security Review of scripts and asset files.

Scripts and asset files are the resource tier of a skill. They add value
only when they replace something the agent would improvise incorrectly.

## When a Script Is Warranted

Prefer procedures over scripts. Add a script only when at least one of
the following is true:

- The operation must be deterministic across every run.
- The operation encodes a parser, formatter, schema check, or validator
  the agent should not reimplement.
- The operation is repetitive file generation the agent would otherwise
  produce inconsistently.
- The operation is an offline test suite the agent must run as-is.
- The operation is a conversion between formats where correctness is
  hard to verify by inspection.

If none of these apply, keep the operation as a short procedure in a
reference file. Fewer scripts mean fewer maintenance obligations.

## What Every Script Must Document

Include the following in the script header and, when appropriate, in a
sibling reference file:

```text
Purpose
Inputs
Outputs
Dependencies
Network access
Filesystem writes
Side effects
Exit codes
Failure behaviour
Security considerations
```

Do not ship a script that lacks any of these sections.

## Script Requirements

- Clear CLI help via `--help`.
- Input validation that fails fast with a helpful message.
- Non-zero exit codes on failure. Reserve `2` for invocation errors.
- No hidden network calls. Any network call must be listed in the
  header and reachable via a documented flag.
- No secrets in stdout, stderr, or exit messages.
- No unsafe defaults (for example, TLS verification disabled or
  `shell=True` interpolation).
- No destructive default action. Prefer a `--dry-run` flag by default
  where destruction is possible.
- Timeouts for every network operation.
- Explicit platform assumptions if any (Windows-only, POSIX-only).
- Unit tests for critical behaviour under `tests/`.

## Dependency Rules

- Start with the standard library.
- Add a third-party dependency only when the standard library cannot
  solve the problem safely.
- Pin the dependency to a specific version range.
- Prefer widely used, well-audited libraries.
- Document install steps in a reference file.
- Reject dependencies with install-time network calls beyond package
  resolution.

If a dependency is proposed, justify it explicitly in the pull request or
review notes.

## No Binaries on the Default Branch

- Do not commit prebuilt executables to the default branch.
- Build configurations (for example, PyInstaller `.spec` files) are
  acceptable when documented as build hints, not runtime artefacts.
- Compiled artefacts, when needed, must be published through the
  repository's release process, not the source tree.

## Script Output Guidelines

- Prefer structured output (JSON) for anything the agent will parse.
- Use `stdout` for the primary payload.
- Use `stderr` for warnings and human-facing progress messages.
- Never mix structured and human output on the same stream.

## Assets

Assets are static resources that the agent copies, fills in, or shows to
the user.

### Include

- Templates and skeletons.
- Schemas and JSON examples.
- Checklists.
- Design worksheets.
- Report templates.
- Diagrams.

### Exclude

- Real credentials or credential fragments.
- Real customer data.
- Real SAP hostnames, SIDs, client identifiers, or usernames.
- Binary artefacts unless they are part of the skill's user experience
  (for example, an icon).

### Naming

- Descriptive kebab-case filenames.
- Include the workflow and scope in the name, for example
  `skill-requirements-template.md` or `skill-review-report-template.md`.
- Avoid generic names such as `template.md`, `report.md`, or
  `notes.md`.

## Testing Scripts

Every script that ships with a skill should have at least one automated
test. Place tests under the repository's `tests/` directory using the
existing test framework.

Recommended coverage:

- Happy path with representative input.
- One invalid-input failure.
- One boundary condition (empty input, maximum length, missing optional
  field).
- Output structure invariants.
- Exit-code invariants.

Tests must not require the network. Tests must not require an SAP system
connection.

## Reviewing an Existing Script

During Audit or Refactor, walk the script through this checklist:

- [ ] The script header documents purpose, inputs, outputs, dependencies,
      network access, filesystem writes, side effects, exit codes,
      failure behaviour, and security considerations.
- [ ] `--help` output is accurate and complete.
- [ ] All network operations have timeouts.
- [ ] No `shell=True` or equivalent unsafe interpolation.
- [ ] No secrets in output, logs, or exception messages.
- [ ] Every dependency is pinned and justified.
- [ ] Tests exist and pass locally.
- [ ] No prebuilt executable is committed.
- [ ] Errors return non-zero exit codes with helpful messages.
- [ ] The script does not silently swallow exceptions.

Findings for a script go into the same review report as findings for the
prose material.
