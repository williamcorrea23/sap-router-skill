# Skills/MCP implementation evidence

## Delivered locally

- Canonical, offline-by-default healthcheck; explicit live probes, per-server/total deadlines, JSON output only persisted with `--output`.
- Read readiness separated from mutation authorization. MCP handshake and local configuration alone never imply domain readiness.
- Semantic reads for ADT, CPI/APIM, SAP GUI and local UI5/Fiori/CAP/Context Mode fixtures. No installs in probes or launcher; planned providers cannot launch.
- Pinned runtime resolver: ARC-1 1.1.2, UI5 0.2.14, Fiori 1.8.1, CAP 0.0.5. Existing exact-version local packages are reused. ARC-1 was installed under `.sap-router/runtimes` with lifecycle scripts disabled.
- Context Mode uses an embedded entrypoint, bypassing upstream bootstrap repair, hooks and startup update checks. Runtime cache stays under `.sap-router/context-mode`.
- CPI/APIM approval verifies actual argument/precondition hashes, reserves execution atomically, then consumes on success. Unknown outcomes cannot replay; reconcile the target, reject the old approval and create a new approved plan if necessary.
- Skill metadata/link validation, scoped Codex skill sync with backups, and project MCP config reconciliation preserving unrelated entries and the global `aibap-39912` alias.
- `.sap-router/` is ignored by Git: runtime packages, approval records and credential/config backups must stay local.

## Verification and reproducibility

```text
python -m unittest discover -s tests -v
python .agents/skills/run-sap-router-skill/driver.py
python scripts/sap_harness.py eval --suite all
python scripts/validate_catalog.py --strict
python scripts/validate_skills.py --output reports/skills-validation.json
python scripts/generate_ide_assets.py check
python scripts/healthcheck.py --offline --read-only --json
python scripts/healthcheck.py --execute --read-only --timeout 30 --output reports/health/implemented.json
python scripts/sync_codex_config.py
```

The offline healthcheck returns `DEGRADED`/exit 1 by design: no semantic execution occurred. This is not a claim that every integration is broken. Exit 0 requires actual readiness; exit 2 means a blocking policy/configuration condition.

On 2026-10-03, the router skill driver passed 78/78 CLI checks. An earlier snapshot
recorded 165/165 skill metadata checks. The controlled-harness verification passes 148
unit tests on Python 3.11.15 and 3.14, 33/33 offline evaluation checks, strict catalog
validation, 203-skill IDE parity, ABAP review, and secret audit with zero findings. These
local checks do not prove every skill's behavior on a live SAP system.

## Operational evidence and remaining dependencies

Read-only probes have demonstrated AIBAP repository access and local UI5 project inspection, Fiori app discovery, CAP model search and Context Mode statistics. Reload the Codex session to expose the revised project MCP configuration; availability in this existing session is not proof of the new configuration.

- ARC-1: startup/initialization timeout remains; AIBAP remains the proven development read provider.
- SAP GUI: an existing non-busy scripting session must be available; COM probe timeout remains environmental evidence, not READY.
- CPI API: direct connection test returned HTTP 404. Validate the configured API/token endpoints and authorizations before further testing.
- APIM API/browser and CPI browser: domain read not proved; configure the proper service key or logged-in tenant session locally. Never paste credentials into reports or chat.
- TLS bypass was disabled in the project `.env`, with a local backup. Certificate errors must be solved by configuring trust, never by restoring the bypass.

`reports/health/implemented.json` contains timestamped probe results. Later individually repeated probes may be newer; rerun the command above for one consolidated current snapshot.

## DEV writes — not executed

Fill `docs/dev-validation.example.json` and run:

```text
python scripts/validate_dev_manifest.py docs/dev-validation.example.json
```

The template intentionally fails closed. It needs system/client, isolated objects/tenants, MM material type/sector/unit/views/organizational levels, expected outcomes and cleanup. A valid manifest is **not** an approval. Each operation still requires an explicit, target-bound approval. No production, stock movement, financial posting, automatic ZROUTER enablement or implicit material deletion is authorized.

## Candidate review — static evidence only

The earlier `reports/mcp-candidates-review.json` snapshot inventories 63 planned entries (62 candidates plus SmartForms), with 27 mapped to local snapshots. The current MCP configuration has 70 planned entries; none can launch or route. Missing security, dependency, maintenance and semantic/approval tests remain promotion blockers. This is an evidence inventory, not a completed security certification or blanket rejection.

## Backups

- Project config and original TLS configuration: `.sap-router/backups/`.
- Replaced global skills: `~/.codex/sap-router-backups/`.
- No unrelated global skills, global AGENTS instructions, or third-party MCP entries were removed.
