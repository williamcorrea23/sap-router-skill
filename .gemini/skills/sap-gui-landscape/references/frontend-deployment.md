# SAP GUI frontend deployment (Windows) — SAPSetup, packages, AWUS, SNC

Companion to the parent skill. Where that file covers *what the client connects to* (landscape XML,
connection strings), this covers *how the client gets installed, updated and secured*.

**Windows only.** SAP GUI for Java has no SAPSetup equivalent — it ships as its own installer/JAR.

Primary sources, both **[V]** (retrieved during authoring): the **SAPSetup Guide, SAPSetup 9.0**
(Administration Guide, help.sap.com) and **SAP Note 1587566** (*Installation problems with SapSetup Version
9.0*, v206 — the running release-notes note).

---

## 1. The toolchain — know which binary does what

| Binary | Role |
|---|---|
| **`NwSapSetup.exe`** | the **workstation** installer. Its file version *is* the SAPSetup version |
| **`NwSapSetupAdmin.exe`** | the **Installation Server admin** console — create packages, import products/patches, configure AWUS and LSH |
| **`NwCreateInstServer.exe`** | creates a new installation server |
| **`NwUpdateInstServer.exe`** | updates an existing installation server |
| `NwSapSetupIS.exe` | installation-server-side component |
| `NwSapAutoWorkstationUpdateService.exe` | the AWUS service on the workstation |
| `NwSapSetupUserNotificationTool.exe` | AWUS user notification on the workstation |

> ⚠️ **SAPSetup requires the Windows optional feature “VBScript” (`vbscript.dll`).** Since **Windows 11
> 24H2 VBScript is an optional feature** (still enabled by default) — if it is removed by hardening policy,
> SAPSetup breaks. [V, 1587566]

The older names in **SAP Note 510048** (`SAPSETUP.EXE`, `SAPADMIN.EXE`, `/p:`, `/server:`) are the
**SAP GUI 6.20-era** tools — that note is from 2004. Do not use it for current releases; it is listed here
only because it still surfaces in search results.

---

## 2. Workstation command line — `NwSapSetup.exe`

Parameters are **not case-sensitive**. **[V, GUIDE]**

| Parameter | Effect |
|---|---|
| `/silent` | No UI at all, not even a splash. **Requires** a product name, a package name, or `/all` |
| `/nodlg` | Progress dialog only, nothing else. Same requirement as `/silent` |
| `/nosplash` | Suppress the startup splash only |
| `/product` | Run the installer in **product mode** (cannot switch to Package View) |
| `/package` | Run the installer in **package mode** (cannot switch to Product View) |
| `/product:"<name>"` | Process only that product. Ignored with `/repair` |
| `/package:"<name>"` | Process only that package. With `/repair`, only that package is repaired |
| `/uninstall` | Uninstall components. Combine with `/product=` or `/package=`. **Works only with `/nodlg` or `/silent`** |
| `/update` | Update installed components. **Works only with `/nodlg` or `/silent`**; without `/package`, packages are ignored |
| `/repair` | Repair all installed components (supersedes `/force`) |
| `/force` | Overwrite all files/registry artefacts from earlier runs, **even newer file versions**; on uninstall, removes SAP files even when the shared-DLL counter disagrees |
| `/once:"<OnceTag>"` | Run this installation exactly once per workstation; a repeat with the same tag does nothing |
| `/ForceWindowsRestart` | Force a restart after completion. Use after `/silent` or `/nodlg` with `/package` or `/product` |
| `/SMS[:"<pkg>"]` | Write a `<package>.MIF` status file to `%TEMP%` — for SCCM/SMS-style distribution to detect success |
| `/MaintenanceMode` | Allow components beyond those currently on the installation server |
| `/skip=wtscheck` | Skip the "is the WTS server in install mode" check |
| `/extract:<dir>` | Extract a single-file installer to a directory |
| `/?` | Help |

```bat
:: silent package install, then report the exit code
start /wait <src>\Setup\NwSapSetup.exe /package="<pkg cmd line name>" /silent && echo %ERRORLEVEL%

:: silent uninstall by product
NwSapSetup.exe /Silent /Uninstall /Product="<product command line name>"

:: install and force the reboot
NwSapSetup.exe /silent /product="SAPGUI" /ForceWindowsRestart
```

### Return codes — `%ERRORLEVEL%` **[V, GUIDE]**

| Code | Meaning |
|---|---|
| **0** | ended without detected errors |
| 3 | another instance of SAPSetup is running |
| 4 | **LSH failed** |
| 16 | started on WTS without administrator privileges |
| 26 | WTS is not in install mode |
| 27 | COM error |
| 48 | general error |
| 67 | cancelled by user |
| 68 | invalid patch |
| 69 | installation engine registration failed |
| **70** | a **prerequisite was not met** while running `/silent` or `/nodlg`, **or** invalid XML files |
| **129** | **reboot recommended** |

> 🚨 **Treat 129 as success-with-reboot, and 70 as the silent-failure code.** A deployment script that only
> tests `ERRORLEVEL 0` will mark reboot-pending machines as failed and — worse — historically a missing
> prerequisite under `/silent` returned **0** and installed nothing. That was corrected to return **70**;
> if you are on an older SAPSetup, unmet prerequisites can look like success. [V, 1587566]

---

## 3. Installation server command line

**`NwCreateInstServer.exe` / `NwUpdateInstServer.exe`** — **[V, GUIDE]**

| Parameter | Effect |
|---|---|
| `/dest="<path>"` | destination directory for the installation server |
| `/silent` | no UI — **`/dest` becomes mandatory** |
| `/nodlg` | progress dialog only — **`/dest` becomes mandatory** |
| `/DontConfigureServerPath` | do **not** auto-configure the share (network share creation and null-session accessibility) |

**`NwSapSetupAdmin.exe`**

| Parameter | Effect |
|---|---|
| `/checkserver` | verify installation-server integrity silently; returns errorlevel > 0 and writes an error file if discrepancies are found |

```bat
NwCreateInstServer.exe /dest="C:\MyInstServerPath" /silent
NwSapSetupAdmin.exe /checkserver
```

---

## 4. Packages — the point of the installation server

Packages are built in **`NwSapSetupAdmin.exe`** and then deployed by command line with
`/package:"<command line name>"`. The *command line name* — not the display name — is what you pass.

Video walkthrough: **SAP Note 2283941** (*Tutorial "Creating Self-Installing Packages on an Installation
Server"*).

Related: **SAP Note 1624251** (*Moving an Installation Server to a new machine*), **SAP Note 512040**
(*Distributing "services", "saplogon.ini", and similar files*), **SAP Note 1587566** (running release notes
and known problems).

---

## 5. AWUS — Automatic Workstation Update Service

*"If the automatic workstation update service (AWUS) is configured, the service updates the workstation and
reboots it, if required. This happens whenever the installation server is updated or patched, or installed
packages are updated."* **[V, GUIDE]**

### Prerequisites

- Installation server created and configured with `NwCreateInstServer.exe`
- Hosted on a machine that can act as a file server and serve numerous network sessions
- Windows server with local security policy:
  - *Accounts: Guest account status* = **Enabled**
  - *Network access: Let 'Everyone' permissions apply to anonymous users* = **Enabled**
  - Share is **NULL-session accessible**
- Workstation has network access to the installation server

> 🔐 **Those three policy settings are a real security trade-off** — guest account enabled, anonymous
> "Everyone" permissions, and a null-session-accessible share. Raise them explicitly with whoever owns
> Windows hardening before promising AWUS; they are frequently blocked by policy.

### Behaviour

- **Runs whether or not a user is logged on.** [V, GUIDE]
  - User logged on → informed of the update; **starts only on the user's assent**; reboot only on
    confirmation.
  - No user logged on → update **and reboot** run automatically.
- Checks for updates on the **last 10 installation sources that are network paths**.
- The service updates itself automatically when a patch is available.

### Configure

`NwSapSetupAdmin.exe` → **Services** → **Configure Automatic Workstation Update**:

| Option | Meaning |
|---|---|
| **Update check frequency** | interval between checks — **default 24 hours** |
| **Enforce reboot** | *if needed* (recommended) · *after every update* · *don't enforce* |
| **Additional update sources** | further installation servers, checked **in the listed order**; the server AWUS was installed from is always checked |
| **Disable automatic workstation updates** | stops updates from this server at the next check. To stop AWUS permanently, uninstall it from the workstation |

### Install on the workstation

1. Create a package containing the component **SAP Automatic Workstation Update**.
2. Deploy that package.

Two processes then run in the background: `NwSapSetupUserNotificationTool.exe` and
`NwSapAutoWorkstationUpdateService.exe`.

---

## 6. LSH — Local Security Handling

LSH *"enables users to install SAP front end components on their workstations without"* local administrator
rights. **[V, GUIDE]**

In `NwSapSetupAdmin.exe` → **Services** → **Maintain Local Security Handling**:

| Action | Effect |
|---|---|
| **Stop Distribution Service** | temporarily disable LSH |
| **Start Distribution Service** | re-enable |
| **Uninstall Distribution Service** | permanently disable |

Menu entries are greyed out when the service is not configured. **Return code 4 = LSH failed.**

---

## 7. Frontend SNC — `SNC_LIB` and friends

This is where SNC actually breaks, and it is client-side. **[V, SNCCFG]**

### The three values that must agree

| Where | What to read |
|---|---|
| **Workstation** | run `SET SNC` at a command prompt → value of **`SNC_LIB`** |
| **Server** | transaction **`SNCCONFIG`** → **`snc/gssapi_lib`** and **`snc/identity/as`** |
| **SAP Logon** | right-click the system → *Properties* → **Network** tab → **SNC Name** |

Rules: **[V, SNCCFG]**

- **`SNC_LIB` (client) and `snc/gssapi_lib` (server) must be the same library.** A fresh install of Secure
  Login Client normally sets `SNC_LIB` correctly.
- **`SNC_LIB` and `SSF_LIBRARY_PATH` should have the same value.**
- The **SNC Name needs no mechanism prefix** — it should simply equal `snc/identity/as`
  (e.g. `p:<same subject as the SNC PSE>`). A prefix is harmless *if it matches the library*; a **wrong
  prefix raises `SNCERR_UNKNOWN_MECH`**, a **missing one can raise `SNCERR_INVALID_NAME`**.
- The same library has **different filenames per OS** and that is fine — e.g. workstation
  `C:\Program Files (x86)\SAP\FrontEnd\SecureLogin\lib\sapcrypto.dll` against a Linux server's
  `/usr/sap/<sid>/SYS/exe/uc/linuxx86_64/libsapcrypto.so`.

> ⚠️ **`SNC_LIB` must be set as a real environment variable**, via *Edit the system environment variables*
> (System Properties → Advanced → Environment Variables). Setting it with `SET SNC_LIB=…` in a command
> prompt **only affects that shell** and will appear to change nothing. [V, SNCCFG]

### More than one SNC library

For a second library (third-party Kerberos 5 / NTLM SSO, or legacy Secude) use the secondary variables
**`SNC_LIB_2` / `SNC_LIB_32_2` / `SNC_LIB_64_2`**, per **SAP Note 2025528** (*(Limited Support for) more
than one concurrent SNC_LIB*). Then **each SAP Logon entry's SNC Name must carry the mechanism prefix for
that system's library**, otherwise the library with precedence always wins. Restart SAP GUI after changing
the values. **[V, SNCCFG]**

Bit-width variables `SNC_LIB_64` / `SNC_LIB_32`: **SAP Note 1746967**.
Choosing the right toolkit build: **SAP Note 1375378**.

### Error → cause quick map

| Error | Look at |
|---|---|
| `SNCERR_UNKNOWN_MECH` | wrong mechanism prefix / library mismatch — **SAP Note 3606053** |
| `SNCERR_INVALID_NAME`, *"Specified target is unknown or unreachable"* | missing prefix in a multi-library setup — SAP Note 2025528 |
| `SNCERR_BAD_NT_PREFIX` | KBA **3504340** |
| *Unable to load GSS-API DLL `sapcrypto.dll`* | KBA **2265085** |
| *Unable to load GSS-API DLL `sncgss32.dll`* | SAP Note **2551720** |
| *"No user exists with SNC name"* after SSO migration | SAP Note **2532380** |

---

## Sources

- **[GUIDE]** *SAPSetup Guide — SAPSetup 9.0* (Administration Guide, help.sap.com). **[V]** Downloaded and
  text-extracted during authoring. Source for §1–§6: the binary roles, both command-line tables (workstation
  and installation server), the **return-code table**, the AWUS prerequisites/behaviour/configuration
  options, and the LSH service actions.
  https://help.sap.com/doc/1b770fc9e71e4062851ffe7de158007d/latest/en-US/SAPSetup_Guide.pdf
- **[1587566]** **SAP Note 1587566** — *Installation problems with SapSetup Version 9.0* (BC-FES-INS,
  **v206**, 2025-12-30). **[V]** The running release-notes/known-problems note; source for the **VBScript
  (`vbscript.dll`) requirement and its Windows 11 24H2 optional-feature status**, and for the change that
  made an unmet prerequisite under `/silent` or `/nodlg` return **70** instead of **0**.
  https://me.sap.com/notes/1587566
- **[SNCCFG]** **SAP Note 3606053** — *SNCERR_UNKNOWN_MECH error in SAPGUI when connecting to system via
  SNC* (BC-SEC-SNC-CFG, 2025-06-06). **[V]** Source for the whole of §7: reading `SNC_LIB` with `SET SNC`,
  `SNCCONFIG` for `snc/gssapi_lib` / `snc/identity/as`, the SAP Logon *Network* tab, the rule that SNC Name
  needs no mechanism prefix, that `SNC_LIB` must equal `SSF_LIBRARY_PATH`, that `SNC_LIB` must be set as a
  real environment variable rather than with `SET`, and the cross-OS filename example.
  https://me.sap.com/notes/3606053
- **[510048]** **SAP Note 510048** — *Command line parameter of the front-end installation* (BC-FES-INS,
  2004). Documents the **superseded 6.20-era** `SAPSETUP.EXE` / `SAPADMIN.EXE` switches. Retained here only
  to warn against using it for current releases. https://me.sap.com/notes/510048
- Package/server operations: **SAP Note 2283941** (self-installing packages tutorial, video), **SAP Note
  1624251** (moving an installation server), **SAP Note 512040** (distributing `services` / `saplogon.ini`),
  **SAP Note 508649** (diagnosis of frontend installation problems), **SAP Note 456905** (composite note
  for SAPSetup as of 6.20).
- SNC multi-library and toolkit selection: **SAP Note 2025528**, **SAP Note 1746967**, **SAP Note 1375378**,
  **SAP Note 2115486** (GSSKRB5.DLL / GSSNTLM.DLL download), **SAP Note 150380** (Kerberos 5 support).
