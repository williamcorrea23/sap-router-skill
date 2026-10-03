---
name: sap-gui-landscape
description: >-
  Central SAP GUI landscape configuration — SLMT (report RSLSMT) and the SAPUILandscape.xml /
  SAPUILandscapeGlobal.xml files SAP Logon, Business Client and SAP GUI for Java read:
  maintaining them centrally, distribution by UNC or HTTP(S), the LandscapeFileOnServer registry
  keys and HKCU-vs-HKLM precedence, and the full connection-string grammar (/H/ /S/ /M/ /G/
  router chains) including SNC parameters. Also Windows client deployment: SAPSetup /
  NwSapSetup, silent install, AWUS, frontend SNC (SNC_LIB, SNC_LIB_64). Use for "SLMT",
  "SAPUILandscape.xml", "distribute SAP GUI connections", "connection string", "SAP GUI for Java
  SNC", "sncqop", "logon group not working", "NwSapSetup", "silent install SAP GUI",
  "SNCERR_UNKNOWN_MECH".
---

# SAP GUI Landscape & Connection Configuration

Two halves of one job: **SLMT** maintains the landscape centrally in the ABAP system, and the resulting
**SAP UI Landscape XML** is what every SAP GUI client reads to know which systems exist and how to reach
them. The connection strings and SNC settings live *inside* that XML — so a malformed connection string
and a mis-distributed landscape file present identically to the user ("I can't see/reach the system").

> **Guardrail — this is user-facing configuration for a whole landscape.**
> - **A bad central file breaks every user at once.** Validate against the XSD (**SAP Note 2112449**)
>   before distributing, and keep the previous version to roll back to. [G, VAL]
> - **Never put a router password in a file you distribute.** `/P/<password>` in a connection string is
>   readable by anyone who can read the XML. Prefer SNC, or `/W/` (prompted) — see §3.
> - **Renaming the "Local" workspace is mandatory** when building a server file. Skipping it collides with
>   users' local configuration. [G, DIST]
> - Changing `LandscapeFileOnServer` is a **registry change on every workstation** — treat it as a
>   client-side rollout, not an SAP change.

Verification legend: **[V]** verified against the live source during authoring · **[G]** cited to an SAP
Note or guide.

---

## 1. SLMT — the central maintenance tool

**Transaction `SLMT`**, or report **`RSLSMT`**. It lets an administrator *"centrally create, display, and
edit SAP UI Landscape XML data"*, with the XML **persisted in the database**. [G, SLMT]

| | |
|---|---|
| **Delivered by** | **SAP Note 2311166** — as a **TCI** or the support package below |
| **Minimum SP** | SAP_BASIS **740** SAPKB74018 · **750** SAPK-75009 · **751** SAPK-75104 · **752** SAPK-75201 [G, SLMT] |
| **Authorization** | role **`SAP_SLMT`**, authorization object **`S_LSMT`** — `02` change, `03` display [G, DIST] |
| **In-system help** | the **i-button** on the initial screen carries the functional documentation |

> Because SLMT ships as a **TCI**, implementing it needs TCI enablement and a minimum SPAM/SAINT level —
> see [sap-security-patch](../sap-security-patch/SKILL.md) §5a, and **SAP Note 2187425**. If SNOTE refuses
> the note, that is the reason, not the note itself. [G, SLMT]

---

## 2. The files, and which is which

Introduced with **SAP GUI for Windows 7.40**; the format is activated automatically as of **7.50** (and by
installing SAP Business Client / NWBC 5.0+). [G, DIST]

| File | Holds |
|---|---|
| **`SAPUILandscape.xml`** | the **user-facing** entries — connections, SAP shortcuts, favourites, workspaces/folders |
| **`SAPUILandscapeGlobal.xml`** | the **infrastructure** — `<Messageservers>` and `<Routers>` |

**Migrated from the old INI files** on first start of SAP Logon: [G, DIST]

| Old file | Default location | Becomes |
|---|---|---|
| `sapmsg.ini` (message servers) | Windows directory | `SAPUILandscapeGlobal.xml` |
| `saproute.ini` (SAProuters) | Windows directory | `SAPUILandscapeGlobal.xml` |
| `services` (port numbers) | `system32\drivers\etc` | `SAPUILandscapeGlobal.xml` |
| `saplogon.ini`, `sapshortcut.ini`, `saplogontree.xml` | per-user | `SAPUILandscape.xml` |

Control the migration explicitly:

```bat
saplogon.exe /INI_FILE=C:\Saplogon\740\admin\saplogon.ini ^
             /LSXML_FILE=\\Servername\Saplogon\740\SAPUILandscape.xml
```

`/LSXML_FILE` (or env `SAPLOGON_LSXML_FILE`) names the landscape file to create; `/INI_FILE` (or
`SAPLOGON_INI_FILE`) names the INI to migrate. Without `/LSXML_FILE` the files are created under the
*Path of Local Configuration Files* — registry `HKEY_CURRENT_USER\Software\SAP\SAPLogon\Options` →
`PathConfigFilesLocal`. [G, DIST]

---

## 3. Connection strings — the grammar

This is the part people hand-edit and get wrong. The formal EBNF, verbatim from the SAP GUI for Java
documentation: **[V, JAVA]**

```ebnf
<connection string> := [<router prefix>]<local>
<router prefix>     := <router>[<router(2)>...<router(n)>]
<router>            := "/H/"<host>"/S/"<service>[("/P/"<password>) | ("/W/"<password>)]
<local>             := <simple>|<message server>|<symbolic>
<simple>            := "/H/"<host>"/S/"<service>
<messageserver>     := "/M/"<host>"/S/"<service>"/G/"<group>
<symbolic>          := "/R/"<system>"/G/"<group>
<host>              := <hostname>|<ipaddr>
<service>           := <servicename>|<port number>
<string data>       := (any ASCII string not containing '/' or '&')
```

| Prefix | Meaning |
|---|---|
| `/H/` | host (SAProuter, or the application server) |
| `/S/` | service — port number or service name |
| `/P/` | SAProuter password **in clear** |
| `/W/` | SAProuter password, **prompted** rather than stored |
| `/M/` | message server host |
| `/G/` | logon group |
| `/R/` | symbolic SAP system name (resolved via the Message Server List) |

**Three ways to address a system**, in increasing friendliness: [V, JAVA]

```
/H/host.example.org/S/3200                    direct application server
/M/msghost/S/4253/G/SPACE                     message server + logon group (load balanced)
/R/ALR/G/SPACE                                symbolic system name + group
```

**Router chains** prepend, left to right — *"a connection string with SAP routers generally has the form
`<router 1><router 2>…<router n><destination>`"*: [V, JAVA]

```
/H/gate.remote.org/S/3299/P/secret/H/gate.example.org/S/3298/H/host.example.org/S/3200
└────────── 1st router (with pw) ──────────┘└──── 2nd router ────┘└──── app server ────┘
```

Two operational consequences worth knowing: **[V, JAVA]**

- **Message server strings need network access to the message server at resolution time** — the client
  contacts it to get an application server. A firewall that allows 32xx but not the message server port
  produces "works with `/H/`, fails with `/M/`".
- Message server ports are conventionally named **`sapms<SID>`**. *"Care should be taken that the
  application server's port number is not confused with the message server's port number."*

> ⚠️ **`/R/<SID>/G/<group>` can fail once the SAP UI Landscape format is active** in NWBC / SAP shortcut —
> **SAP Note 2218496**. If symbolic-name logon broke right after a GUI or Business Client upgrade, start
> there. [G, RSID]

---

## 4. Connection parameters (SAP GUI for Java)

Fields are `<key>=<value>` joined by `&`. **All are optional except `conn`, which is mandatory and should
come first. Unknown fields are silently ignored** — which is exactly why a typo'd parameter fails quietly.
**[V, JAVA]**

| Parameter | Meaning |
|---|---|
| **`conn`** | the connection string (§3) — **mandatory, first** |
| `clnt` | client to prefill (e.g. `001`) |
| `user` | user name to prefill |
| `lang` | logon language (e.g. `EN`) |
| `tran` | transaction to start after logon |
| `systemName` | system ID of the system, so its message server can be contacted — lets you turn off expert mode after data entry |
| **`sncon`** | `true` enables SNC. **Requires `sncname`** |
| **`sncname`** | SNC name of the SAP system, e.g. `p/secude:CN=example, O=organization, C=DE`. **Requires `sncon`** |
| **`sncqop`** | SNC quality of protection — **`1` Authentication · `2` Integrity · `3` Encryption · `4` Maximum available** |
| `manualLogin` | disable SNC automatic login; force manual logon |
| `cpg` | SAP codepage number (`0` = default; e.g. `8000` Shift-JIS) |
| `wan` | `true` enables WAN optimisations for low-speed links |
| `wp`, `ssot`, `sso2`, `rfcid` | reserved (workplace / SSO / dialog RFC) |

```
conn=/H/host.example.org/S/3200
conn=/H/host.example.org/S/3200&tran=BIBS
conn=/M/msghost/S/3600/G/PUBLIC&clnt=100&lang=EN&sncon=true&sncname=p:CN=SAP_SID,O=Example,C=MY&sncqop=3
```

> 🚨 **`sncqop` values above 4 are not documented for SAP GUI for Java.** The classic SNC scale used in
> RFC/`sapgui` for Windows configuration runs `1,2,3,8,9` where **9 = "maximum available"** — and a value
> copied from there (`sncqop=9`) is **outside the 1–4 range this client documents**. The documented
> equivalent of "maximum available" here is **`sncqop=4`**; plain encryption is **`3`**. If you inherited a
> string with `sncqop=9`, test `4` and confirm against the server's `snc/data_protection/*` profile
> parameters rather than assuming it is being honoured. **[V, JAVA]**

> **`sncname` prefix:** the documentation's example uses `p/secude:CN=…`; `p:CN=…` is the form used with
> CommonCryptoLib and is what most current systems show. Whichever you use, it must match the server's
> **`snc/identity/as`** exactly — including spaces after commas. Read it from the server profile rather
> than retyping it ([sap-health-triage](../sap-health-triage/SKILL.md) covers `sappfpar`).

> Simplest form only: a bare connection string with no `conn=` still works *"for reasons of simplicity and
> downwards compatibility"*, but the documentation says this *"is not recommended with respect to possible
> future changes."* **[V, JAVA]**

---

## 5. Distributing the landscape file

Three mechanisms; pick one and be consistent. [G, DIST]

**a) Command line / environment** — central file, explicitly named:

```bat
saplogon.exe /LSXML_FILE=\\Servername\Saplogon\740\SAPUILandscape.xml
:: or set SAPLOGON_LSXML_FILE=\\Servername\Saplogon\740\SAPUILandscape.xml
```

**b) HTTP/HTTPS web server** — the file references the global file via an include:

```xml
<Includes>
  <Include index="0" url="http://webserver:port/config/SAPUILandscapeGlobal.xml" />
</Includes>
```

**c) Registry** — `LandscapeFileOnServer`, an **Expandable String (`REG_EXPAND_SZ`)**, so it may contain
`%VAR%` references:

| Scope | Key |
|---|---|
| Machine | `HKEY_LOCAL_MACHINE\SOFTWARE\SAP\SAPLogon\Options` |
| Machine, 32-bit GUI on 64-bit Windows | `HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\SAP\SAPLogon\Options` |
| User | `HKEY_CURRENT_USER\Software\SAP\SAPLogon\Options` |

> 🔑 **Precedence differs between the two executables** — the single most confusing behaviour here:
> **`saplogon.exe` → HKCU wins.  `saplgpad.exe` (Logon Pad) → HKLM wins.** [G, DIST]
> If you set HKLM and users still see their old list, they are probably on `saplogon.exe` with a stale
> HKCU value — delete the HKCU value.

### Rules that bite

- **Rename the `Local` workspace.** When building the server file, activate *Workspace View*, open the
  root folder *Workspaces* and rename the `Local` subfolder (e.g. to `Server`). *"This renaming from
  'Local' to another name is mandatory! Otherwise there will be conflicts between the server and local
  files for your users."* Also **SAP Note 2935614**. [G, DIST]
- **You cannot ship `SAPUILandscape.xml` alone** if it does not contain as much message-server information
  as `SAPUILandscapeGlobal.xml` does. Ship both, or ship only the Global file. [G, DIST]
- **HTTPS is not supported on 7.40** for the web-server file. Supported **as of SAP GUI 7.50 patch level 6**
  and newer. [G, DIST]
- Don't change users' existing INI-format settings (e.g. the `ConfigFileOnServer` registry value) while
  migrating. [G, DIST]

---

## 6. Validate, then roll out

1. **Validate the XML against the XSD** — **SAP Note 2112449** supplies the schema; a template is in the
   SAP GUI Installation Guide. [G, VAL]
2. **Duplicate UUIDs** are a real failure mode — **SAP Note 2954513** changed the behaviour to warn rather
   than abort. Deduplicate before distributing.
3. **Keep the previous file.** Rollback is copying it back; there is no in-product undo.
4. **Pilot on a handful of workstations** before setting the registry value estate-wide.
5. Expect **cached** behaviour when the server file is unreachable — **SAP Note 2257512** adds an
   administrative option to suppress the popup in that case.

**Housekeeping the stored XML:** landscape data persisted by SLMT lives in the database and accumulates —
**SAP Note 3310726** (*Delete unnecessary entries from landscape XML data*) and **SAP Note 2734896**
(*Deletion of SAP UI Landscape XML data from the database table*). See
[sap-space-reclaim](../sap-space-reclaim/SKILL.md). [G, SLMTFIX]

**Moving entries between clients:** **SAP Note 3458923** covers copying connections from SAP GUI for
Windows to SAP GUI for Java.

---

## 7. Deploying the client itself (Windows)

The landscape file tells an installed client *where to connect*. Getting the client installed, updated and
SNC-capable is a separate toolchain — **SAPSetup**:

| Binary | Role |
|---|---|
| **`NwSapSetup.exe`** | workstation installer; its file version **is** the SAPSetup version |
| **`NwSapSetupAdmin.exe`** | Installation Server admin console — packages, product/patch import, AWUS, LSH |
| `NwCreateInstServer.exe` / `NwUpdateInstServer.exe` | create / update an installation server |

```bat
start /wait <src>\Setup\NwSapSetup.exe /package="<pkg cmd line name>" /silent && echo %ERRORLEVEL%
NwSapSetup.exe /Silent /Uninstall /Product="<product command line name>"
NwCreateInstServer.exe /dest="C:\MyInstServerPath" /silent
```

Three things that catch people out, each covered in full in the reference: **[V, DEPLOY]**

- **Return codes are not binary.** `0` success, **`129` = reboot recommended**, **`70` = prerequisite not
  met under `/silent`/`/nodlg` (or invalid XML)**, `4` = LSH failed. A script testing only `ERRORLEVEL 0`
  mis-reports reboot-pending machines — and on older SAPSetup an unmet prerequisite returned `0` while
  installing nothing.
- **AWUS** (Automatic Workstation Update Service) auto-updates workstations from the installation server,
  **including rebooting them unattended when no user is logged on**. It requires guest account enabled,
  anonymous "Everyone" permissions and a **null-session-accessible share** — a security trade-off to agree
  with whoever owns Windows hardening *before* promising it.
- **`SNC_LIB` must match the server's `snc/gssapi_lib`**, must equal `SSF_LIBRARY_PATH`, and must be set as
  a **real environment variable** — `SET SNC_LIB=…` in a shell changes nothing permanent. The SAP Logon
  *SNC Name* needs **no mechanism prefix**; a wrong one gives `SNCERR_UNKNOWN_MECH`.

> **SAPSetup needs the Windows optional feature `VBScript` (`vbscript.dll`)** — an optional feature since
> **Windows 11 24H2**. Hardening that removes it breaks the installer. [V, DEPLOY]

**Full reference — every command-line parameter for workstation and installation server, all return codes,
AWUS configuration, LSH, and frontend SNC troubleshooting:
[references/frontend-deployment.md](references/frontend-deployment.md).**

---

## Cross-references

- **`sap-crypto-pse`** — the server-side PSE behind SNC (`sapgenpse`, `SECUDIR`, `cred_v2`); this
  skill covers the **client** half (`SNC_LIB`, `sncname`, `sncqop`).
- **`sap-saprouter`** — routing strings in connection definitions.
- **`sap-software-download`** — obtaining SAP GUI and SAPSetup packages.
- **`sap-os-executables`** — `sapinst`/SWPM, the provisioning counterpart to SAPSetup.

## OS note

| | |
|---|---|
| **Windows** | full picture — SAP Logon / Logon Pad, the registry keys above, INI migration, UNC and HTTP(S) distribution, **plus the whole SAPSetup deployment plane (§7)** |
| **Linux / macOS (SAP GUI for Java)** | **no SAPSetup and no registry** — the Java client ships its own installer; connections come from the Java client's own configuration, and the **connection string + parameter syntax in §3–4 is the SAP GUI for Java documentation**, so it applies directly. Central distribution is by pointing the client at the landscape file location |
| **AIX** | SAP GUI for Java is the only client; same as Linux |

**SLMT itself is OS-independent** — it is an ABAP transaction; only the *consumption* of the XML is
platform-specific.

---

## Execution discipline (non-negotiable)

### The holy rule — nothing runs unbacked

**Every command executed must be traceable to one of exactly three things:**

1. an **official SAP source** — help.sap.com page / Operations or Administration Guide, or
2. an **SAP Note / KBA**, or
3. an **explicit instruction from the user**.

If a command is backed by none of those, **do not run it** — say what backing is missing and stop.
"It's probably fine", "this is standard", and "I recall the syntax" are not backing. When the backing is
a source, name it (page or Note number) alongside the command; when it is the user, quote the instruction.

### Ambiguity ⇒ stop and confirm, before any execution

If executing would require **assuming** anything the user did not state, you are **obliged** to confirm
first. Never fill a gap with a plausible default. Common gaps that force a stop:

- **client number**, SID, instance number, target host/node
- **read-only vs state-changing** — if it is not explicit which was wanted, ask
- **scope** — one instance vs the whole system, one tenant vs all, one client vs cross-client
- which **database / dbms_type**, which environment (**PRD vs non-PRD**)
- retention/age cut-offs, recovery points, target of a restore, transport target

A wrong assumption here is not a typo — it is the difference between reading a log and stopping production.

### But verify programmatically FIRST — *then* ask

**Asking the user for something the system can answer is a failure.** Before you raise a question, ask
the user to go and look, or request Computer Use / GUI access, you **must** first try to determine it
programmatically. Only what genuinely cannot be derived — intent, authorization, a business decision, a
value that exists only in the user's head — is a legitimate question.

| Determine programmatically (do NOT ask) | Ask the user (cannot be derived) |
|---|---|
| Which DB — `echo $dbms_type`, profile `dbms/type` | Which **client** to act on |
| SIDs / instances / hosts / ports — `sapcontrol … GetSystemInstanceList`, `ls /usr/sap` | Whether this system is in scope / approved |
| Is it up, is the DB up — `GetProcessList`, `R3trans -d` | PRD change approval, downtime window |
| Kernel / release / patch — `disp+work -version`, `saphostexec -version` | The intended recovery point or retention policy |
| Which clients **exist** — table `T000` | Which of those clients is **meant** |
| Free space, log locations, parameter values — `df -h`, `sappfpar`, profile | Business impact / urgency |

Order, always: **verify programmatically → ask only what remains → never assume.**

### Prefer programmatic over manual or GUI

**Work down this ladder. Take the highest rung that does the job — and within that rung, the lowest
privilege that suffices. Never skip a rung because you assume it is unavailable (see the burden of
proof below).**

| # | Path | Privilege | Notes |
|---|---|---|---|
| **1** | **REST / OData** — `GET` first | Narrowest. Scoped service user | Read-only by construction when you stay on `GET`. `$metadata` gives you the contract |
| **2** | **SOAP / web service** | Scoped service user | Typed contract via `?wsdl`. Client-cert auth where offered — no password in a script |
| **3** | **RFC / BAPI** (`creds exec`, JCo, `pyrfc`) | RFC user with `S_RFC` | **For ABAP *writes*, prefer this over 1–2**: BAPIs have real commit/rollback semantics and land in SM19/SM20 |
| **4** | **OS shell as the *correct* user** → **DB utility** | ⚠️ Escalates — see below | The chain matters more than the rung |
| **5** | **Browser automation** (headless or in-app) | Interactive user | Session-based UIs only. Fragile across releases |
| **6** | **Computer Use / screen driving** | Interactive user | **Last resort.** Not repeatable, not diffable, breaks on any UI change |

> ## ⚠️ Rung 4 is a chain, and each link widens the blast radius
>
> ```
> ssh <host>                    ← host access
>   → su - <sid>adm             ← SAP admin: can stop/start the system
>   → su - ora<sid> / syb<sid>  ← DB owner: can drop data
>   → sudo / root               ← everything
>        → hdbsql | isql | dbmcli | sqlplus | db2   ← the actual command
> ```
>
> **Stop at the least-privileged user that can run the command.** Most read-only checks need only
> `<sid>adm`; DB utilities usually need the DB owner; **root is almost never the right answer** and
> `saproot.sh` is the rare legitimate exception. Say which user you used and why.

> ## Two axes, and they do not agree
>
> The ladder ranks by **automation quality** — repeatable, reviewable, loggable, diffable. Privilege
> runs on a *different* axis and is **worst in the middle**: rung 4 (OS/root) can destroy a system,
> while rung 6 (Computer Use) is merely an interactive user clicking. So Computer Use ranks last for
> *reproducibility*, not because it is the most dangerous.
>
> **The practical rule: prefer the highest rung, but never escalate privilege to climb it.** A
> read-only OData call beats an RFC that needs a write-capable user; an `<sid>adm` shell beats a root
> shell. If climbing a rung requires more privilege than the task needs, stay where you are and say so.

> ## 🛑 You must **demonstrate** the absence of a programmatic path, not assume it
>
> "There is no API for this" is a **finding that requires evidence**, not a default. Before dropping to
> rung 5 or 6, actually probe:
>
> - **HTTP status codes tell you the access mode.** `401` → Basic auth works, **scriptable**.
>   `302` regardless of credentials → session UI, browser needed. `404` → not deployed. `503` →
>   deployed but stopped.
> - **Look for a contract**: append `?wsdl`, `$metadata`, `/api`, `?sap-client=` and see what answers.
> - **Ask the platform what it exposes**: `sapcontrol -function J2EEGetApplicationAliasList`,
>   `hdbcons help`, `btp --help`, `xs help`, `<tool> -h`.
> - **A Swing or WebDynpro *UI* being un-automatable does not mean the *objects* are.** The editor and
>   the API are different doors — check for the second before declaring the first is the only one.
>
> Programmatic execution is repeatable, reviewable, loggable and diffable; screen-driving is none of
> those. When you do drop to a lower rung, **say which rung you are on and what you probed** to rule
> out the higher ones — so the user can correct you if they know of a path you missed.

### Ask how output should be handled

Work that produces evidence (logs, traces, command output, screenshots, reports) has two reasonable
endings. **Ask which the user wants** rather than guessing:

- **(a) persist it** — write the output/logs/screenshots to a file, and say exactly where; or
- **(b) execute and report** — just run it and give a short final status summary.

Don't dump large output into the conversation unasked, and don't silently discard evidence either — for
troubleshooting and any change with a rollback, (a) is usually the right default to offer.

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
3. **Check the `attachments` array.** SAP routinely puts the actual deliverable *in an attachment* rather
   than the Note body — sizing guides, SQL script collections, configuration PDFs, spreadsheets. A Note
   whose text says "see the attached document" is not fully read until you have it.
4. Prefer the Note over this file where they disagree, and say which Note you followed.

**Downloading an attachment:** `fetch` returns `attachments[].url` **and `attachments[].filename`**;
**`fetch_attachment`** retrieves the bytes. Pass the URL verbatim — the URLs are opaque and cannot be
constructed. If your MCP build predates that tool, open the URL in a signed-in browser instead and say the
file was fetched manually.

> ⚠️ **Two ways a hand-rolled fetch goes wrong — both verified.**
> **1. Trusting the status code.** An unauthenticated request returns **HTTP 200 with a small HTML login
> stub**, not an error. Check the content type and magic bytes, or you save a JavaScript redirect page
> under a `.pdf` name.
> **2. Naming the file from the URL.** SAP serves many attachments from a *generic endpoint* —
> `…/services/attachment.htm?iv_key=…&iv_guid=…` — so the URL basename is `attachment.htm` even when the
> payload is a 24-page PDF. Take the name from **`attachments[].filename`** or the response's
> **`Content-Disposition`** header, never from the URL path.

No MCP available? Look the Note up on `me.sap.com/notes/<id>` and say the check was skipped rather than
assuming this file is current.

## Sources

- **[SLMT]** **SAP Note 2311166** — *SAP UI Landscape maintenance tool* (BC-SRV-ALV, v10, 2017-10-06).
  **[V]** Retrieved via the SAP Notes MCP during authoring. *"With the SAP UI Landscape maintenance tool,
  you can centrally create, display, and edit SAP UI Landscape XML data. The tool can be called using the
  transaction code SLMT."* Report **`RSLSMT`**; role **`SAP_SLMT`** required; delivered by **TCI** or
  support package — SAP_BASIS **740** `SAPKB74018`, **750** `SAPK-75009INSAPBASIS`, **751**
  `SAPK-75104INSAPBASIS`, **752** `SAPK-75201INSAPBASIS`. TCI preparation per **SAP Note 2187425**.
  https://me.sap.com/notes/2311166
- **[DIST]** **SAP Note 2075073** — *SAP Logon (Pad): Create/distribute server configuration file in the
  SAP UI Landscape format* (BC-FES-GUI, v18, 2021-10-18). **[V]** Source for: the file split
  (`SAPUILandscape.xml` vs `SAPUILandscapeGlobal.xml`); format introduced in SAP GUI for Windows **7.40**
  and auto-activated as of **7.50** or with NWBC 5.0+; INI migration inventory (`sapmsg.ini`,
  `saproute.ini`, `services`, `saplogon.ini`, `sapshortcut.ini`, `saplogontree.xml`); `/INI_FILE` and
  `/LSXML_FILE` switches and their `SAPLOGON_*` environment equivalents; `PathConfigFilesLocal`; the
  `<Includes><Include …/></Includes>` block for HTTP; the **`LandscapeFileOnServer`** `REG_EXPAND_SZ`
  value under HKLM / `Wow6432Node` / HKCU and the precedence rule — *"For SAP Logon (saplogon.exe) the
  setting under HKCU has higher priority. For SAP Logon Pad (saplgpad.exe) the setting under HKLM has
  higher priority"*; the mandatory renaming of the `Local` workspace — *"This renaming from 'Local' to
  another name is mandatory!"*; the rule that `SAPUILandscape.xml` cannot be shipped alone without
  sufficient message-server data; **HTTPS unsupported on 7.40, supported as of 7.50 patch level 6**; and
  the `S_LSMT` authorization values (`02` change, `03` display). https://me.sap.com/notes/2075073
- **[JAVA]** *SAP GUI for the Java Environment* — SAP Help Portal, **Reference → Connection Strings /
  Connection Parameters** (document 780.03). **[V]** Extracted from the official PDF during authoring.
  Source for: the **formal EBNF grammar** of connection strings quoted in §3; the `/H/ /S/ /P/ /W/ /M/ /G/
  /R/` prefixes; router chaining (*"`<router 1><router 2>…<router n><destination>`"*); message-server
  resolution requiring network access at resolution time and the `sapms<SID>` convention with the warning
  not to confuse application-server and message-server ports; and the **complete connection-parameter
  table** (`conn` mandatory and first, `clnt`, `user`, `lang`, `tran`, `systemName`, `sncon`, `sncname`,
  `sncqop`, `manualLogin`, `cpg`, `wan`, `wp`, `ssot`, `sso2`, `rfcid`) with *"Unknown fields are silently
  ignored"* and **`sncqop` documented as 1 Authentication / 2 Integrity / 3 Encryption / 4 Maximum
  available**.
  https://help.sap.com/docs/sap_gui_for_java/e665f2b67dbd4328ab6bd9e029b84581/f2a7a69515114ac59531dc96758a094e.html
- **[VAL]** **SAP Note 2112449** — *Validation of SAP UI Landscape files (XML format)* — the XSD schema.
  Related: **SAP Note 2954513** (duplicate UUIDs → warn instead of abort), **SAP Note 2257512**
  (suppress the popup when the cached landscape file is used because the server file is unavailable).
- **[RSID]** **SAP Note 2218496** — *NWBC/Sapshortcut: login with connection string like `/R/SID/G/GROUP`
  failed when SAP UI landscape format is on (default after NWBC is installed)* (BC-FES-GUI).
  https://me.sap.com/notes/2218496
- **[SLMTFIX]** SLMT-specific issues and landscape-XML housekeeping: **SAP Note 3310726** (*Delete
  unnecessary entries from landscape XML data*), **SAP Note 2734896** (*Deletion of SAP UI Landscape XML
  data from the database table*), **SAP Note 3474137** (`UNCAUGHT_EXCEPTION` editing the landscape XML in
  SLMT), **SAP Note 2645330** (problem uploading an XML file via SLMT), **SAP Note 3620957** (SLMT
  description column greyed out), **SAP Note 3157851** (SLMT does not support `ssoparameter`).
- **[REL]** Further reading: **SAP Note 2075150** (*SAP Logon (Pad) 740: New format of configuration files
  as of SAP GUI for Windows 7.40*), **SAP Note 2107181** (*Collective SAP Note regarding SAP UI Landscape
  format*), **SAP Note 2220930** (*How to enable SAP UI Landscape format for SAP GUI for Windows 7.40*),
  **SAP Note 2175351** (administrative core configuration file), **SAP Note 2935614** (*Server Landscape
  xml file should not have a workspace named "Local"*), **SAP Note 3458923** (*Copy connections from SAP
  GUI for Windows to SAP GUI for Java*), **SAP Note 38119** (*SAP Logon: Administration of functions*).

- **[DEPLOY]** Frontend deployment sources — the **SAPSetup Guide (SAPSetup 9.0)** administration guide,
  **SAP Note 1587566** (*Installation problems with SapSetup Version 9.0*, v206 — running release notes;
  the VBScript requirement and the `/silent` return-code change), and **SAP Note 3606053**
  (*SNCERR_UNKNOWN_MECH …* — the frontend `SNC_LIB` configuration rules). All **[V]**, retrieved during
  authoring. Superseded 6.20-era switches are in **SAP Note 510048** and should not be used for current
  releases. Detail and full citations in
  [references/frontend-deployment.md](references/frontend-deployment.md).

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID):
**2075073** before any distribution change (it is revised often — v18 at time of writing), **2311166** for
SLMT availability on your SAP_BASIS level, and **2107181** as the collective note for the landscape format.
For the connection-string and SNC parameter syntax, prefer the SAP GUI for Java documentation for the
client release you actually run — the parameter set has grown across releases.
