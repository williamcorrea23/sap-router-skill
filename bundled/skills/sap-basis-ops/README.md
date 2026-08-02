# sap-basis-ops

Claude Code skills for **SAP Basis / technical operations at the OS and DB layer** — the
sysadmin plane that existing SAP skill sets (which focus on ABAP/CAP/Fiori/BTP development)
don't cover.

Targets classic on-premise / IaaS NetWeaver and S/4HANA landscapes on **Linux, Windows and
AIX**. (SAP BTP / cloud operations are a planned separate plugin.)

## What this is — and is not

These are **knowledge + runbook skills**. Each one produces the *exact, source-cited command
sequence* plus the pre- and post-checks for a given SID / DB / OS. Execution is **opt-in** and
happens through an SSH/shell MCP **you** supply at runtime — the skills bundle **no credentials**
and never auto-run destructive commands.

## The guardrail contract (every skill obeys this)

SAP operations commands stop production, delete data, and import transports. Before any command
that changes state, a skill must:

1. **Identify** — confirm SID, hostname, instance number, DB type and OS. Never assume.
2. **Classify** — determine PRD vs non-PRD. Any stop / delete / import against **PRD** requires
   an explicit, typed confirmation from the user.
3. **Run as the correct OS user** — `<sid>adm` for the SAP layer, and the DB's own owner for the DB
   layer (`ora<dbsid>`, `syb<dbsid>`, `db2<dbsid>`, `sdb`, the HANA SID's `<sid>adm`); `root` **only**
   where a procedure explicitly requires it. Switch with a login shell (`su - <user>`) so the
   environment is set, and state the user alongside every command. Wrong-user execution is a top cause
   of failure, and root-owned files under `/usr/sap` break later starts by the real owner.
4. **Preview** — show the exact command and its **blast radius** first. Several SAP/DB stop
   commands have *no* dry-run flag (`stopsap`, `shutdown`), so preview is mandatory, not optional.
5. **Execute** — only via the user-provided MCP, **one step at a time**, never chained across a
   stop boundary.
6. **Verify** — run the documented post-check (`GetProcessList`, return codes, `showserver`, …)
   after each step.

Each skill carries the full **"Run as the correct OS user"** matrix (SAP, HANA, Oracle, ASE, Db2, MaxDB,
SQL Server, Host Agent — UNIX and Windows) so it applies even when a skill is loaded on its own.

## Sourcing rule (every generated command)

Nothing ships unverified. Each command/procedure carries a citation, priority order:

1. Official **Operations / Administration Guide** for the product or DB
2. **help.sap.com** product documentation
3. **SAP Notes / KBA**
4. SAP Community (last resort, labelled as such)

Each reference file ends with a **Sources** section listing the pages actually used, and marks
which commands were verified against the live page vs. cited to a guide.

## Recommended companion: the SAP Notes MCP

Documentation goes stale; **SAP Notes are the living source of truth** — they change procedures between
doc revisions and are release/patch/DB/OS specific. Every skill therefore carries a **"Staying current"**
section instructing it to check SAP Notes *before* acting on anything version-specific (and especially
before anything destructive).

To make that check possible, install the SAP Notes MCP server — [`marianfoo/sap-mcp-servers`](https://github.com/marianfoo/sap-mcp-servers),
package `packages/notes`. It needs an SAP S-user:

```bash
git clone https://github.com/marianfoo/sap-mcp-servers ~/sap-mcp-servers
cd ~/sap-mcp-servers && npm install && npm run build && npm run install:browsers
```
```bash
claude mcp add sap-notes -s user -- bash -lc 'cd ~/sap-mcp-servers/packages/notes && exec node dist/mcp-server.js'
```

Credentials go in a gitignored `packages/notes/.env`:

```bash
SAP_USERNAME="S00XXXXXXXX"
SAP_PASSWORD="your-password"
```

> ⚠️ **Quote any value containing `#`** — dotenv treats it as an inline comment, so an unquoted
> `SAP_PASSWORD=My#Pass` silently becomes `My`. This presents as a login that hangs waiting for a
> redirect, and is easily mistaken for an MFA problem.

The skills then use its two tools — `search` (find Notes by topic) and `fetch` (full Note text, validity,
prerequisites, side effects). **The MCP is optional**: without it the skills still work from their cited
help.sap.com sources, but they will say the currency check was skipped rather than assume they are current.

## Layout

```
sap-basis-ops/
├── .claude-plugin/plugin.json
└── skills/
    ├── sap-db-command-reference/     # DB matrix: HANA, Oracle, ASE, Db2, MaxDB, SQL Server
    ├── sap-system-lifecycle/         # start / stop / restart, instance order, sapcontrol
    ├── sap-health-triage/            # is-it-up + first-response triage (+ sappfpar)
    ├── sap-log-reference/            # log/trace locator: symptom→log, per component & per DB
    ├── sap-housekeeping/             # reorg jobs, work-dir/audit/spool cleanup, cleanipc
    ├── sap-transport-mgmt/           # OS-layer tp / R3trans, buffer, unconditional modes
    ├── sap-kernel-patch/             # kernel swap (SAPCAR/saproot.sh) + Host Agent update
    ├── sap-backup-recovery/          # backup + restore/recover per DB, PITR
    ├── sap-security-patch/           # monthly Security Patch Day workflow
    ├── sap-web-dispatcher/           # HTTP reverse proxy / load balancer
    ├── sap-saprouter/                # NI proxy + saprouttab
    └── sap-cloud-connector/          # BTP ↔ on-prem secure tunnel
```

Task skills cross-link `sap-db-command-reference` rather than duplicating DB commands; only
OS-variant snippets live inline in each skill.

## Status

Phases 1 & 2 complete — 12 skills.

- ✅ `sap-db-command-reference` — **all six databases** complete (HANA, Oracle, SAP ASE, IBM Db2,
  SAP MaxDB/liveCache, MS SQL Server), each cited to help.sap.com with Linux/Windows/AIX handling.
- ✅ `sap-system-lifecycle` — start/stop/restart order (DB ↔ ERS/ASCS/PAS/AAS) via SAPControl.
- ✅ `sap-health-triage` — is-it-up + triage: SAPControl diagnostics (syslog/WP/traces/alerts),
  `sappfpar` profile/memory validation, OS checks, "won't start" checklist.
- ✅ `sap-housekeeping` — standard reorg jobs (Note 16083), work-dir/audit-log/spool cleanup, `cleanipc`,
  filesystem-full triage; DB log cleanup delegated to the DB reference.
- ✅ `sap-security-patch` — monthly Security Patch Day: retrieve the month's Security Notes, narrow to the
  system's applicable subset, compare vs applied (System Recommendations / Focused Run / RSECNOTE),
  prioritize by CVSS/HotNews, implement via SNOTE.
- ✅ `sap-log-reference` — log/trace locator: symptom→log, instance work-dir traces, ABAP logs, standalone
  components (Web Disp/SAProuter/Cloud Connector/Host Agent), and each DB's logs; how to read (OS + SAPControl).
- ✅ `sap-web-dispatcher`, `sap-saprouter`, `sap-cloud-connector` — the standalone components: start/stop/status,
  config, ports, HA, admin UIs.
- ✅ `sap-transport-mgmt` — OS-layer `tp`/`R3trans`: buffer, import single/all, transport dir, unconditional
  modes, return codes, RDDIMPDP; STMS-preferred guidance.
- ✅ `sap-kernel-patch` — kernel swap (SAPCAR/SAPEXE/SAPEXEDB/`saproot.sh`/`sapcpe`) + Host Agent update
  (`saphostexec -upgrade`); SUM/SPAM pointer for larger updates.
- ✅ `sap-backup-recovery` — backup types + recovery types (most-recent / PITR / specific), log-mode
  prerequisites, and per-DB restore/recover commands (HANA/Oracle/ASE/Db2/MaxDB/SQL Server).

## Install (Claude Code plugin)

This repo is a Claude Code plugin marketplace. Add it to `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "sap-basis-ops": { "source": { "source": "github", "repo": "adam0thman/sap-basis-ops" } }
  },
  "enabledPlugins": { "sap-basis-ops@sap-basis-ops": true }
}
```

then run `/reload-plugins` in Claude Code (or use the interactive `/plugin` menu). The skills load
namespaced as `/sap-basis-ops:<skill-name>` (e.g. `/sap-basis-ops:sap-system-lifecycle`), and also
trigger automatically when a task matches a skill's description.

## Contributing

**Contributions are welcome — anyone can contribute.** Open a pull request and we'll review it.

To keep the project consistent, please follow the conventions used throughout:

- **Cite every command** to help.sap.com or an official SAP guide/Note, with the `[V]` (verified against
  the live page) vs `[G]` (cited to a guide) markers.
- **Cover Linux / Windows / AIX** — and state honestly where a platform is N/A (e.g. HANA is Linux-only,
  SQL Server is Windows-only) rather than inventing variants.
- Keep the **Identify → Preview → Confirm → Verify** guardrails, and flag destructive commands.
- Small, focused skills; cross-link rather than duplicate.

Prefer not to use GitHub, or want to reach the maintainer directly? Email **repo@adamoneservices.com**.

## License

[MIT](LICENSE).
