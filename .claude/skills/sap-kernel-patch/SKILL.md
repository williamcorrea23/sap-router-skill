---
name: sap-kernel-patch
description: >-
  Patch the SAP kernel (the executables — disp+work, sapstartsrv, …) and update the SAP Host Agent, on
  Linux, Windows and AIX. Covers assessing versions (disp+work -version, saphostexec -version), the manual
  kernel swap (stop → back up exe → SAPCAR extract SAPEXE/SAPEXEDB → saproot.sh → start → verify), the Host
  Agent self-upgrade (saphostexec -upgrade -archive), SAPCAR usage, and rollback. Use for "patch the
  kernel", "kernel upgrade", "update disp+work", "update the host agent", "SAPCAR extract". Points to
  SUM/SPAM for larger updates. Cited to help.sap.com / SAP Notes.
---

# SAP Kernel Patch & Host Agent Update

Two independent operations:
- **Kernel patch** — swap the SAP executables to a higher patch level (**requires instance downtime**).
- **Host Agent update** — update `/usr/sap/hostctrl` (SID-independent, **no SAP-system downtime**).

> **Guardrail — kernel swap is a controlled change with a rollback.**
> - **Right binary or it won't start:** match **kernel release + patch level + platform + Unicode + DB**
>   (the DB-dependent part). Wrong platform/Unicode = dead instance.
> - **Back up the current `exe` directory first** — that's your rollback.
> - **UNIX: run `saproot.sh <SID>` after extracting** — restores root/setuid bits; the instance won't
>   start without it. (The most-forgotten step.)
> - Downtime: stop the instance(s) before replacing files (they're locked while running).
> - Identify SID/host/OS/DB → classify PRD → preview → confirm (typed for PRD) → step → verify.
> - **Claude does not download** — the SAP Software Center login is yours; Claude tells you exactly which
>   `.SAR` files to get.

Verification legend: **[V]** verified against the live help.sap.com page during authoring · **[G]** cited
to the official guide/Note.

---

## 1. Assess current versions (read-only, safe)

```bash
disp+work -version            # kernel release, patch level, Unicode, DB client   [G, KP2]
# also: SM51 → Release info, or System → Status in SAP GUI
/usr/sap/hostctrl/exe/saphostexec -version    # Host Agent version                [V, HA1]
```

---

## 2. Kernel patch — step by step

The kernel lives in the **central exe** dir — UNIX `/sapmnt/<SID>/exe/uc/<platform>` (e.g.
`linuxx86_64`, `rs6000_64` on AIX); Windows `\\<host>\sapmnt\<SID>\SYS\exe\uc\<platform>`. On start,
**`sapcpe`** copies it to each instance's local `exe`. It ships in two parts: **`SAPEXE.SAR`** (DB-independent)
and **`SAPEXEDB.SAR`** (DB-dependent, matched to your `dbms_type`). [G, KP1]

1. **Assess** — `disp+work -version` (note release/PL/Unicode/DB/platform).
2. **Acquire** (you, SAP Software Center) — `SAPEXE_<PL>.SAR` + `SAPEXEDB_<PL>.SAR` for the exact
   release/platform/DB, plus any add-on archives (`dw.sar`, `lib_dbsl.sar`, IGS). SAP Note 19466. [G]
3. **Stop** the instance(s): `sapcontrol -nr <nr> -function StopSystem`
   ([sap-system-lifecycle](../sap-system-lifecycle/SKILL.md)). DB can stay up.
4. **Back up** the current exe: `cp -pr <exe-dir> <exe-dir>.bak_<date>` (Windows: copy the folder). ← rollback.
5. **Extract** into the central exe with SAPCAR — DB-independent first, then DB-dependent, then the rest: [G, KP1]
   ```bash
   SAPCAR -xvf SAPEXE_<PL>.SAR   -R /sapmnt/<SID>/exe/uc/<platform>
   SAPCAR -xvf SAPEXEDB_<PL>.SAR -R /sapmnt/<SID>/exe/uc/<platform>
   # then any dw.sar / lib_dbsl.sar / igsexe.sar the same way
   ```
6. **UNIX only — fix ownership/permissions:** run `saproot.sh <SID>` from the exe dir (restores
   root-owned/setuid binaries). Windows: the service/installer handles this. [G, KP1]
   > ⚠️ **SAP on ASE:** replacing the kernel resets the **SUID bit on `sybctrl`**, and without it
   > `startdb` cannot switch to `syb<sid>` — so the database fails to start *after* an otherwise clean
   > patch. Either restore the SUID bit, or have the `syb<sid>` password in secure storage (kernel
   > **PL 327 for 7.20**+); note a `startdb` invoked from a **daemon**/start profile still needs the SUID
   > bit. **SAP Note 1796535** — see [sap-db-command-reference → ASE](../sap-db-command-reference/references/sap-ase.md). [V, KP4]
7. **Start:** `sapcontrol -nr <nr> -function StartSystem` — `sapcpe` refreshes each instance's local exe.
8. **Verify:** `disp+work -version` shows the new patch level; `GetProcessList` GREEN; scan `dev_disp`
   ([sap-health-triage](../sap-health-triage/SKILL.md)).

**Rollback:** stop → restore `<exe-dir>.bak_<date>` → `saproot.sh <SID>` (UNIX) → start → verify.

---

## 3. Host Agent update — step by step (no SAP downtime)

The Host Agent (`saphostexec`, `saphostctrl`, `sapstartsrv`) is one per host, runs as **root** (UNIX) /
the SAPHostExec service (Windows), independent of any SID.

**Recommended — self-upgrade (no manual extract):** run from the **existing** hostctrl dir: [V, HA1]
```bash
# UNIX (as root):
/usr/sap/hostctrl/saphostexec -upgrade -archive <path>/SAPHOSTAGENT<PL>.SAR -verify
# Windows:
%ProgramFiles%\SAP\hostctrl\saphostexec -upgrade -archive <path>\SAPHOSTAGENT<PL>.SAR -verify
```
`-verify` validates the package against SAP's digital signature. It stops itself, upgrades, and restarts. [V, HA1]

**Manual alternative:** `saphostexec -stop` → `SAPCAR -xvf SAPHOSTAGENT<PL>.SAR -R /usr/sap/hostctrl/exe`
→ `./saphostexec -install` → start. [G, HA2]

**Verify:** `/usr/sap/hostctrl/exe/saphostexec -version` and `saphostexec -status`. [V, HA1]

---

## 4. SAPCAR quick reference

```bash
SAPCAR -tvf <archive>.SAR                 # list contents (check before extracting)
SAPCAR -xvf <archive>.SAR -R <dest-dir>   # extract to <dest-dir>
SAPCAR -cvf <archive>.SAR <files>         # create
```
SAPCAR itself is a standalone executable (download the matching platform build).

---

## 5. For larger updates → SUM / SPAM (pointer)

This skill is the **standalone kernel/Host-Agent swap**. For bigger, orchestrated changes use SAP's tools —
this skill does not reimplement them:

| Tool | Use for |
|------|---------|
| **SUM** (Software Update Manager) | Support Package Stacks, EHP/release upgrades, combined **kernel + SP**, and **DMO** (update + DB migration, e.g. to HANA) — the orchestrated path, handles downtime phases |
| **SPAM / SAINT** | ABAP **Support Packages** / **Add-Ons** inside the system (uses `tp`/`R3trans` underneath — see [sap-transport-mgmt](../sap-transport-mgmt/SKILL.md)); update SPAM first |

Use a standalone kernel swap (this skill) for a quick kernel patch; use **SUM** when the change is an SP
stack / upgrade / DB migration.

## Cross-references

- **Stop/start & order:** [sap-system-lifecycle](../sap-system-lifecycle/SKILL.md).
- **Verify / troubleshoot after patch:** [sap-health-triage](../sap-health-triage/SKILL.md).
- **Kernel directory & `sapcpe` layout + SAR file map:** [references/kernel-layout.md](references/kernel-layout.md).

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

- **[KP1]** SAP kernel structure (`SAPEXE.SAR` DB-independent + `SAPEXEDB.SAR` DB-dependent), `SAPCAR -xvf …
  -R <exe>`, and post-extract `saproot.sh <SID>` — SAP kernel patching process; download per **SAP Note
  19466** (*Downloading SAP kernel patches*). https://me.sap.com/notes/19466
- **[KP2]** `disp+work -version` / SM51 / System → Status — kernel version verification (help.sap.com).
- **[HA1]** *Upgrading SAP Host Agent Without Extracting the SAPHOSTAGENT Archive* — SAP Help Portal. **[V]**
  `saphostexec -upgrade -archive <SAPHOSTAGENT<PL>.SAR> -verify` from the hostctrl dir; `saphostexec -version`.
  https://help.sap.com/docs/host-agent/sap-host-agent-doc/upgrading-sap-host-agent-without-extracting-saphostagent-archive
- **[HA2]** *Manually Upgrading SAP Host Agent on UNIX / Windows* — SAP Help Portal (stop → SAPCAR extract →
  `saphostexec -install`).
- **[HA3]** **SAP Note 1031096** — *Installing / upgrading Package SAPHOSTAGENT*. https://me.sap.com/notes/1031096
- **[KP4]** **SAP Note 1796535** — *SYB: Start and stop database without SUID bit for sybctrl*. **[V]**
  *"After changing the kernel executables, it is required to set the SUID bit for sybctrl. Otherwise the
  startdb command will not work correctly."* https://me.sap.com/notes/1796535
- **[SUM]** *Software Update Manager (SUM)* and *SPAM/SAINT* — SAP Software Logistics documentation
  (help.sap.com).

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID): SAP Note 19466 for the current download
paths, the kernel release note for your target patch level, and SAP Note 1031096 for Host Agent specifics.
