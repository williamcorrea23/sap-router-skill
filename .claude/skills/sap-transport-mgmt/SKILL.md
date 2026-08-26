---
name: sap-transport-mgmt
description: >-
  Move SAP transport requests at the OS layer with tp and R3trans — add to the import buffer, import single
  requests or import all, check status, and understand the transport directory, unconditional modes, and
  return codes — on Linux, Windows and AIX. Use for "import a transport at OS level", "tp import", "tp
  addtobuffer / showbuffer", "R3trans", "transport won't import", "/usr/sap/trans", "unconditional mode".
  STMS is the preferred front-end; this is the command-line layer beneath it. Cited to help.sap.com.
---

# SAP Transport Management (tp / R3trans, OS layer)

`tp` is the transport control program; `R3trans` is the lower-level engine it calls. **STMS** (transaction)
is the preferred, controlled front-end — it sequences dependencies via *Import All*. Use the OS layer for
scripted buffer building, recovery, and when STMS is unavailable.

> **Guardrail — highest blast radius in the plugin.** Transports change **code, config and data** in the
> target (often PRD).
> - **Order matters** — imports must run in the buffer/release sequence; importing out of order corrupts
>   objects. Prefer STMS *Import All* (it resolves dependencies).
> - **Test through the route** (DEV → QAS → PRD); never import untested requests straight into PRD.
> - **Unconditional (`U`) modes bypass safety rules** (§4) — use only with a specific reason and approval.
> - Identify SID/host, classify PRD, **preview the buffer**, confirm (typed for PRD), import, verify RC.
> - Take a backup/snapshot before a large or unconditional import.

---

## 1. Transport directory & naming

Shared **transport directory** — UNIX `/usr/sap/trans` (NFS-shared across the domain); Windows a shared
folder (`TRANSDIR`, e.g. `\\<transhost>\sapmnt\trans`). [X3]

| Subdir | Contents |
|--------|----------|
| `bin` | **`TPPARAM`** / `TP_DOMAIN_<SID>.PFL` — the tp parameter file for all systems in the domain |
| `buffer` | per-system import buffers (what's queued for each SID) |
| `cofiles` | command/control files `K9xxxxx.<SID>` (control the import of the data file) |
| `data` | data files `R9xxxxx.<SID>` (the actual object content) |
| `log` | tp/import logs (`ALOG`, `SLOG`, `<TR>.<SID>`) |
| `tmp`, `sapnames`, `EPS`, `actlog` | temp / name / package / action logs |

Request naming: `<SID>K9xxxxx` (e.g. `DEVK900123`) → cofile `K900123.DEV`, data `R900123.DEV`.

Run tp/R3trans as **`<sid>adm`**. If tp reports `transdir not set`, `TRANS_DIR`/the profile isn't found —
pass `pf=`.

---

## 2. R3trans (the low-level engine)

```bash
R3trans -d                          # DB connect test — RC 0000 = database reachable (great health check)
R3trans -v <controlfile>            # verbose export/import per a control file
R3trans -w <logfile> <controlfile>  # write a log
```
`R3trans -d` is the fastest "can the kernel reach the DB?" check (used in triage too). tp calls R3trans
internally for the actual data movement. [X5]

---

## 3. tp — the buffer & import workflow

Always as `<sid>adm`; add `pf=<path>/TP_DOMAIN_<SID>.PFL` if the default profile isn't picked up.

```bash
# inspect the target's import buffer:
tp showbuffer <SID> pf=<TPPARAM>          # requests queued for <SID>            [X2]
tp count <SID> pf=<TPPARAM>               # how many are queued

# add a released request to the buffer (copies cofile+data if needed):
tp addtobuffer <SID>K9xxxxx <SID> pf=<TPPARAM>                                   [X2]

# import ONE request:
tp import <SID>K9xxxxx <TARGETSID> client=<nnn> pf=<TPPARAM>                     [V, X1]
#   example (from the SAP doc): tp import T11k904711 P11 U06

# import the WHOLE buffer in dependency order (what STMS Import All does):
tp import all <TARGETSID> client=<nnn> pf=<TPPARAM>                              [X1/X2]

# buffer maintenance:
tp delfrombuffer <SID>K9xxxxx <TARGETSID> pf=<TPPARAM>
tp cleanbuffer <TARGETSID> pf=<TPPARAM>
```
Windows: identical, `tp.exe` / `R3trans.exe`; the transport dir is the shared `TRANSDIR`.

> **Prefer STMS.** SAP's own guidance: build the buffer at OS level if you must, but let **STMS Import All**
> do the actual import so dependencies/sequence are handled. [X2]

---

## 4. Unconditional (`U`) modes  ⚠️

Append `U` + digit(s) to bypass specific CTS rules — powerful and dangerous. Verified meanings [V, X1]:

| Mode | Effect |
|------|--------|
| `U1` | ignore incorrect cofile status / that it was already imported (re-import) |
| `U2` | skip TADIR bracket expansion; **overwrite originals** |
| `U3` | overwrite system-dependent (originals) objects on import |
| `U6` | overwrite objects in **unconfirmed repairs** |
| `U8` | ignore table classification (delivery-class) restrictions |
| `U9` | bypass the system lock / transport-type restriction |

Combine as digits, e.g. `U126`. Use only for a known reason (e.g. re-importing after a failure) with change
approval — several of these **overwrite** or **re-import** and can damage the target if misused.

---

## 5. Return codes (check after every tp/import)  [G, X4]

| RC | Meaning | Action |
|----|---------|--------|
| **0** | OK | done |
| **4** | warnings (e.g. activation/generation warnings) | review the log; usually acceptable |
| **8** | errors (objects not imported / import errors) | inspect the import log; often needs a fix + re-import |
| **12** | fatal error (import aborted) | do not proceed; investigate |
| **16** | internal/tp error (environment, TPPARAM, transdir) | fix the tp environment |

Read the import log: `tp import` writes to `/usr/sap/trans/log/` (`SLOG`, `ALOG`, `<TR>.<SID>`); or STMS →
Import Monitor / import history. Cross-ref [sap-log-reference](../sap-log-reference/SKILL.md).

---

## 6. The transport daemon (RDDIMPDP)

Imports are driven on the target by the event-triggered background job **`RDDIMPDP`** (scheduled by
`RDDNEWPP`). If imports hang in "waiting", check/repair it:
```bash
tp checkimpdp <SID> pf=<TPPARAM>          # check the transport dispatcher on the target
```
In the system, re-schedule via **STMS → Import Overview** / report `RDDNEWPP` (SE38). [G]

---

## Cross-references

- **Import logs / where they live:** [sap-log-reference](../sap-log-reference/SKILL.md).
- **DB reachable? (`R3trans -d`) / won't-start triage:** [sap-health-triage](../sap-health-triage/SKILL.md).
- **Restart after kernel/transport-tool changes:** [sap-system-lifecycle](../sap-system-lifecycle/SKILL.md).

## Run as the correct OS user

**Identify the right OS user *before* running anything, and switch with a login shell.** Wrong-user
execution is a top cause of SAP failures, and the damage outlives the command: files created by `root`
under `/usr/sap`, `/sapmnt` or a DB directory break every later start by the real owner. A login shell
also matters because each user carries the environment the tools need (`SAPSYSTEMNAME`, `ORACLE_HOME`/
`ORACLE_SID`, `SYBASE`, `DB2INSTANCE`, library paths) — without it, commands fail or act on the wrong system.

| What you're operating | UNIX user | Windows |
|---|---|---|
| SAP instances — `sapcontrol`, `startsap`/`stopsap`, `tp`, `R3trans`, `disp+work`, `sappfpar`, `cleanipc` | **`<sid>adm`** (lower-case **SAP** SID) | `<SID>adm`; services run as `SAPService<SID>` |
| SAP HANA — `HDB`, `hdbsql`, `hdbnsutil` | **`<sid>adm` of the HANA SID** (e.g. `h10adm` — may differ from the SAP SID) | n/a (HANA server is Linux-only) |
| Oracle — `sqlplus`, `lsnrctl`, BR\*Tools | **`ora<dbsid>`** (BR\*Tools also runs as `<sid>adm`; generic installs may use `oracle`) | `<SID>adm`; DB runs as a service |
| SAP ASE — `isql`, `startserver`, Backup Server | **`syb<dbsid>`** | `syb<dbsid>` / `SAPService<SID>` |
| IBM Db2 — `db2start`/`db2stop`, `db2` CLP | **`db2<dbsid>`** (the instance owner = `DB2INSTANCE`) | same; Db2 runs as a service |
| SAP MaxDB / liveCache — `dbmcli`, `x_server` | **`sdb`** (software owner, group `sdba`) + a DBM operator at DB level | install/service account |
| MS SQL Server — `sqlcmd`, service control | n/a (Windows-only for SAP) | `<SID>adm` / the SQL Server service account |
| SAP Host Agent — `saphostexec`, `saphostctrl` | **`root`** | Administrator / `SAPHostExec` service |

**Rules**

- **Switch with a login shell:** `su - <user>` (the `-` is what loads the environment) or `sudo -iu <user>`.
  Windows: use the correct account, or an elevated shell only where documented.
- **`root` only where the procedure explicitly says so** — e.g. `saproot.sh` after a kernel extract, SAP Host
  Agent install/upgrade. Never as a shortcut around a permission error; that is how root-owned files get
  created and break the system later.
- **Verify before acting:** `whoami` / `id`, plus the env actually being set (`echo $SAPSYSTEMNAME`,
  `echo $ORACLE_SID`, `echo $DB2INSTANCE`, `echo $SYBASE`).
- **State the user in every command you hand over** (e.g. "as `<sid>adm`:"), and if the required user is not
  available, say so and stop — do not substitute another user.

## Staying current — check SAP Notes first

SAP Notes supersede this file. Landscapes differ by release, patch level, DB and OS, and SAP changes
procedures via Notes/KBAs between doc revisions.

**If the [SAP Notes MCP](https://github.com/marianfoo/sap-mcp-servers) is configured, use it before
acting on anything version-specific** — especially any destructive step, or when a command here doesn't
behave as documented:

1. `search` the topic (e.g. the component + symptom, or a Note number cited below).
2. `fetch` the promising Note IDs for the current text, validity (affected releases/components),
   prerequisites and side effects.
3. Prefer the Note over this file where they disagree, and say which Note you followed.

No MCP available? Look the Note up on `me.sap.com/notes/<id>` and say the check was skipped rather than
assuming this file is current.

## Sources

- **[X1]** *tp Options* — SAP Change and Transport System. **[V]** `tp import <request> <SID>` (example
  `tp import T11k904711 P11 U06`), unconditional modes `U1/U2/U3/U6/U8/U9`, `client=`, `pf=`.
  https://help.sap.com/doc/saphelp_snc700_ehp01/7.0.1/en-US/3d/ad5b814ebc11d182bf0000e829fbfe/content.htm
- **[X2]** *Import Process* + `tp addtobuffer` / `showbuffer` / `count` / `import all`; STMS-preferred
  guidance — SAP S/4HANA Technical Operation curriculum + SAP Help Portal (Change and Transport System).
- **[X3]** Transport directory `/usr/sap/trans` structure + **TPPARAM** in `bin` — SAP CTS documentation
  (BC-CTS).
- **[X4]** tp/import **return codes** (0/4/8/12/16) — SAP Change and Transport System documentation.
- **[X5]** `R3trans` (`-d` connect test, control files) — SAP R3trans documentation.

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID): the central CTS notes (component
**BC-CTS-TLS**) for your release, and the *tp / R3trans* reference for the full option list.
