# GitHub Spec Kit provenance

- Source: https://github.com/github/spec-kit
- Release: `v1.0.6`
- CLI package: `specify-cli` installed from
  `git+https://github.com/github/spec-kit.git@v1.0.6`
- Integration: `codex`
- Script type: `ps`
- Initialization: `specify init <temporary-directory> --integration codex --script ps --non-interactive --ignore-agent-tools`

The repository contains upstream Codex integration skills under
`.agents/skills/speckit-*` and shared infrastructure under `.specify/`. They
were scaffolded from the pinned CLI in a temporary directory, then copied
without modification. `sap-spec-kit` is the SAP Router wrapper around those
upstream resources.

Workflow order: constitution (when needed) → specify → clarify (when needed) →
plan → checklist → tasks → analyze → implement → converge.

The upstream project is MIT licensed. See the upstream repository for license
text and release notes.
