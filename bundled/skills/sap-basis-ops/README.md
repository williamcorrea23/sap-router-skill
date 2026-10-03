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

SAP operations commands stop production, delete data, and import transports.

### Rule 0 — nothing runs unbacked (non-negotiable)

**Every command executed must be traceable to one of exactly three things:** an **official SAP source**
(help.sap.com / Operations or Administration Guide), an **SAP Note / KBA**, or an **explicit instruction
from the user**. Backed by none of those → **don't run it**, and say what backing is missing. Recall,
plausibility and "this is standard" are not backing.

**Ambiguity ⇒ stop and confirm before executing.** If running the command requires *assuming* anything
the user didn't state — client number, SID, instance, scope, read-only vs state-changing, PRD vs
non-PRD, a retention cut-off, a restore target — confirmation is **obligatory**, not optional.

**But verify programmatically first, then ask.** Asking the user for something the system can answer is
a failure. Determine what is derivable (`echo $dbms_type`, `GetSystemInstanceList`, `disp+work -version`,
`df -h`, `T000`) *before* raising a question, asking the user to go and look, or requesting Computer Use.
Only intent, approval and business decisions are legitimate questions.
Order: **verify programmatically → ask what remains → never assume.**

**Prefer programmatic over GUI.** CLI/API/SQL/report beats screen-driving — it's repeatable, reviewable
and diffable. Use the GUI or Computer Use only where there's no programmatic path, and say why.

**Ask how output should be handled** — persist logs/screenshots to a file (say where), or execute and
report a final status. Don't dump large output unasked; don't silently discard evidence either.

### Then, before any state-changing command

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

Each skill carries the full **"Execution discipline"** and **"Run as the correct OS user"** sections
(the latter with the SAP / HANA / Oracle / ASE / Db2 / MaxDB / SQL Server / Host Agent matrix for UNIX and
Windows) so both apply even when a skill is loaded on its own.

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

The skills then use its tools — `search` (find Notes by topic), `fetch` (full Note text, validity,
support packages, references, prerequisites, side effects, and — with `includeCorrections=true` —
**correction instructions per software component and release range**, including the `downloadUrl` that
identifies a **TCI** and points at its transport package), and **`fetch_attachment`** (download a Note's
attached files — SAP routinely ships the real deliverable as an attachment: sizing guides, SQL script
collections, configuration PDFs, spreadsheets). **The MCP is optional**: without it the skills still work from their cited
help.sap.com sources, but they will say the currency check was skipped rather than assume they are current.

## Layout

```
sap-basis-ops/
├── .claude-plugin/plugin.json
└── skills/
    ├── sap-gui-landscape/           # SLMT + SAPUILandscape.xml, connection strings, SNC params
    ├── sap-db-command-reference/     # DB matrix: HANA, Oracle, ASE, Db2, MaxDB, SQL Server
    ├── sap-system-lifecycle/         # start / stop / restart, instance order, sapcontrol
    ├── sap-health-triage/            # is-it-up + first-response triage (+ sappfpar)
    ├── sap-troubleshooting/          # method + rules of thumb; enumerate ALL log sources
    ├── sap-log-reference/            # log/trace locator: symptom→log, per component & per DB
    ├── sap-housekeeping/             # reorg jobs, work-dir/audit/spool cleanup, cleanipc
    ├── sap-space-reclaim/           # what can be deleted, retention fixes, sized reclaim
    ├── sap-dormant-clients/         # assess & retire unused clients (000/001/066, sandboxes)
    ├── sap-client-copy-accelerator/ # rescue a client copy stalled on one huge table (HANA SDA / Oracle dblink)
    ├── sap-transport-mgmt/           # OS-layer tp / R3trans, buffer, unconditional modes
    ├── sap-sscr-keys/               # SSCR developer & object keys (and when they're not needed)
    ├── sap-kernel-patch/             # kernel swap (SAPCAR/saproot.sh) + Host Agent update
    ├── sap-software-download/        # Software Center: find/qualify files, SP queues, checksums
    ├── sap-hana-system-replication/ # HSR: setup, takeover, failback, multitier/multitarget
    ├── sap-ase-hadr/             # ASE HADR/Always-On: RMA sap_* commands, Fault Manager, split-brain
    ├── sap-oracle-dataguard/     # Data Guard: physical standby, DGMGRL, protection modes
    ├── sap-db2-hadr/             # Db2 HADR: sync modes, VIP vs ACR, SA MP/Pacemaker
    ├── sap-sqlserver-alwayson/   # Always On: availability groups, listener, SWPM node config
    ├── sap-maxdb-ha/             # MaxDB/liveCache: Hot Standby, shadow DB, cluster failover
    ├── sap-btp-cli/              # btp + cf CLI, MultiApps/MTA plugin, mbt
    ├── sap-crypto-pse/           # sapgenpse: PSE, SNC/SSL certs, SAProuter cert renewal
    ├── sap-hana-lifecycle-tools/ # hdblcm (lifecycle) + hdbcons (expert console)
    ├── sap-os-executables/       # sapevt, sapxpg (SM49/SM69), sapinst/SWPM
    ├── sap-hana-xsa/             # XS Advanced: xs CLI + XSA local fallback CLI
    ├── sap-nw-java-pi/           # AS Java admin (/nwa) + PI/PO: PIMON, EOIO, CPA cache, adapter traces
    ├── sap-backup-recovery/          # backup + restore/recover per DB, PITR
    ├── sap-support-case/        # raise an SAP case: earn it, route it, verify the text before submit
    ├── sap-security-patch/           # monthly Security Patch Day workflow
    ├── sap-web-dispatcher/           # HTTP reverse proxy / load balancer
    ├── sap-saprouter/                # NI proxy + saprouttab
    ├── sap-cloud-connector/          # BTP ↔ on-prem secure tunnel
    └── sap-compliance-docs/          # Trust Center certs, SOC/ISO mapping, ALM usage rights
```

Task skills cross-link `sap-db-command-reference` rather than duplicating DB commands; only
OS-variant snippets live inline in each skill.

## Status

Phases 1 & 2 complete — 33 skills.

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
- ✅ `sap-troubleshooting` — troubleshooting method: establish facts, **enumerate every log/trace source**
  (complete inventory: ABAP transactions, security/SAL, interfaces, Java, kernel, DB, OS), correlate by
  timestamp, rules of thumb, and what to send SAP when escalating.
- ✅ `sap-log-reference` — log/trace locator: symptom→log, instance work-dir traces, ABAP logs, standalone
  components (Web Disp/SAProuter/Cloud Connector/Host Agent), and each DB's logs; how to read (OS + SAPControl).
- ✅ `sap-web-dispatcher`, `sap-saprouter`, `sap-cloud-connector` — the standalone components: start/stop/status,
  config, ports, HA, admin UIs.
- ✅ `sap-transport-mgmt` — OS-layer `tp`/`R3trans`: buffer, import single/all, transport dir, unconditional
  modes, return codes, RDDIMPDP; STMS-preferred guidance.
- ✅ `sap-kernel-patch` — kernel swap (SAPCAR/SAPEXE/SAPEXEDB/`saproot.sh`/`sapcpe`) + Host Agent update
  (`saphostexec -upgrade`); SUM/SPAM pointer for larger updates.
- ✅ `sap-gui-landscape` — central SAP GUI configuration: **SLMT** / report `RSLSMT` maintaining the SAP UI
  Landscape XML in the database, the `SAPUILandscape.xml` / `SAPUILandscapeGlobal.xml` split, INI migration,
  distribution by UNC or HTTP(S) with the `LandscapeFileOnServer` registry keys and their HKCU-vs-HKLM
  precedence, plus the full connection-string EBNF (`/H/ /S/ /M/ /G/ /R/ /P/` router chains) and every
  connection parameter including SNC (`sncon`, `sncname`, `sncqop`). Also the Windows client-deployment
  plane: SAPSetup (`NwSapSetup.exe` / `NwSapSetupAdmin.exe`), silent install/uninstall flags and return
  codes, package creation, **AWUS**, Local Security Handling, and frontend SNC (`SNC_LIB`).
- ✅ `sap-sscr-keys` — SSCR developer/object keys: first decides whether the system needs them at all
  (S/4HANA, BW/4HANA and AS ABAP 7.51+ do not), the 14-day post-upgrade SPAU grace window, key
  parameters and the SAP for Me SSCR service, reassignment via `RS_SSCR_KEY_UPLOAD`, and why
  `DEVACCESS`/`ADIRACCESS` must never be edited by hand.
- ✅ `sap-dormant-clients` — evidence-based dormancy assessment (RSUSR200/SUIM, ST03N settlement
  statistics, TBTCO+TBTCP job checks, last-changed dates, TAANA volumes), then safe retirement via SCC5 —
  including what SCC5 leaves behind (TemSe, T000, SAP* access) and why space needs a reorg after.
- ✅ `sap-space-reclaim` — landscape cleanup assessment: size first (HANA/Oracle largest-technical-table
  SQL, TAANA distributions), then the reclaimable inventory across ABAP technical tables, the Security
  Audit Log archive/delete path, DB-layer traces/audit files and OS-layer leftovers (core dumps, old
  kernels, SUM dirs, LSMW extracts). Flags which items have a **configurable retention** worth fixing
  permanently, and is explicit that deleting rows frees no disk without reorganization.
- ✅ `sap-software-download` — SAP for Me **Software Center**: resolve a component to exact filenames,
  object keys, sizes, SHA-256 checksums, required SPAM level and EPS `.PAT` names via the Software
  Center's own OData service; build a correct SP import queue; verify and stage per OS. **Downloads are
  fully scriptable with client-certificate auth** — the SAML chain is documented hop by hop and was
  verified by fetching 7 support packages unattended, all checksums matching.
- ✅ `sap-backup-recovery` — backup types + recovery types (most-recent / PITR / specific), log-mode
  prerequisites, and per-DB restore/recover commands (HANA/Oracle/ASE/Db2/MaxDB/SQL Server).
- ✅ `sap-hana-system-replication` — HSR end to end: the full `hdbnsutil` command table verbatim from the
  SR Guide (which side, online vs offline), replication modes vs operation modes, the **version matrix**
  gating every feature from HANA 1.0 SPS 09 through 2.0 SPS 08, multitier/multitarget, takeover with
  handshake, failback, `systemReplicationStatus.py` / `landscapeHostConfiguration.py` return codes, and
  HA/DR provider hooks incl. the **SAPHanaSR → SAPHanaSR-angi** breaking change, plus
  **scale-out**: the identical-topology rule, host mapping via `-sr_state --sapcontrol=1`, the node-count
  ordering that inverts between add and remove, and the third-site majority maker.

- ✅ `sap-compliance-docs` — governance & audit evidence: the Trust Center **Compliance Finder** and its
  four dimensions (offering / **compliance entity** / assessment period / region), the certification
  catalogue (ISO 27001/27017/27018/27701/42001, SOC 1 & 2 + bridge letters, C5, PCI DSS, CSA STAR, TISAX,
  GxP, EU Cloud CoC), regional schemes (FedRAMP, CMMC, PBMM, NIS2), AI governance (ISO 42001, EU AI Act,
  Joule Agents), and **ALM usage rights** for SAP Cloud ALM / Solution Manager / Focused Run / Tricentis.
  Locates authoritative documents; explicitly does not give legal or licensing advice.

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
