---
name: sap-crypto-pse
description: >-
  sapgenpse and CommonCryptoLib — managing the PSEs behind SNC and SSL/TLS: get_pse, gen_pse,
  import_own_cert, export_own_cert, maintain_pk, seclogin, the PSE/cred_v2 pairing that causes
  "works as one user, fails as another", SECUDIR, PSE types, SAProuter certificate renewal,
  HSM-backed PSEs. Use for "sapgenpse", "PSE", "SNC certificate", "SSL certificate SAP",
  "import_own_cert", "seclogin", "cred_v2", "SECUDIR", "renew SAProuter certificate", "GSS-API
  no credentials". Linux/Windows/AIX.
---

# SAP cryptography — `sapgenpse` and PSE management

**What this is.** `sapgenpse` is the command-line tool of **CommonCryptoLib** (`libsapcrypto.so` /
`sapcrypto.dll`) for creating and maintaining **PSEs** — Personal Security Environments. A PSE is the
container holding a keypair, the own certificate and the trusted certificate list. **SNC and SSL/TLS
in SAP both stand on PSEs**, which is why this one tool sits underneath SAProuter security, SAP GUI
SNC, RFC encryption, and AS ABAP/Java HTTPS.

Marks: **[V]** verified against SAP documentation, **[G]** cited but not read in full. Command syntax
below is **[G]** from the SAP Help Portal *Maintaining the Server's Certificate List Using SAPGENPSE*
and related pages unless noted.

> ## 🛑 Before anything else: two environment variables decide what you touch
>
> ```bash
> echo $SECUDIR      # where PSEs and credentials live
> echo $SNC_LIB      # which crypto library is loaded
> ```
>
> **`SECUDIR`** normally points at `/usr/sap/<SID>/<INSTANCE>/sec` (or `.../DVEBMGS00/sec`). If it is
> unset or points somewhere else, `sapgenpse` will happily operate on **a different PSE than the one
> your system is using**, and everything will look successful while nothing changes. Check it first,
> every time.

---

## 1. The concept that explains most failures

A PSE has **two** artefacts, and they are not the same thing:

| Artefact | What it is |
|---|---|
| **`<name>.pse`** | The PSE itself — keypair, own cert, trusted list. Protected by a PIN. |
| **`cred_v2`** | The **credential** file: an *OS-user-bound* record that lets a process open the PSE **without** supplying the PIN. |

> ## ⚠️ "It works for me but not for the SAP system"
>
> This is nearly always the `cred_v2` binding. `sapgenpse` run interactively as `<sid>adm` can open
> the PSE because you type the PIN — but the running process opens it via **`cred_v2`**, created by
> **`seclogin`** for a **specific OS user**. If the credential is missing, was created for the wrong
> user, or the PSE was replaced without re-running `seclogin`, the process fails while your manual
> test succeeds.
>
> **After replacing or re-importing any PSE, re-create the credential.**

```bash
sapgenpse seclogin -p <name>.pse -x <PIN> -O <OS_user>
sapgenpse seclogin -p <name>.pse -l            # list existing credentials
```

Typical symptom of a broken binding: `GSS-API(maj): No credentials were supplied` — the SNC layer
could not open the PSE as the running user. **[G, e.g. SAP Note 2820130]**

---

## 2. Core commands

```bash
# What identity does this PSE actually hold?
sapgenpse get_my_name -p <name>.pse -x <PIN>          # own DN + validity — the first diagnostic

# Create a PSE with a self-signed cert (SNC, or a starting point for a CSR)
sapgenpse gen_pse -p <name>.pse -x <PIN> "CN=<host>, O=<org>, C=<cc>"

# Client/SNC PSE for a given SNC name
sapgenpse get_pse -p <name>.pse <snc_name>

# Produce a CSR to send to a CA
sapgenpse get_pse -r <req_file>.csr -p <name>.pse -x <PIN> "CN=…, O=…, C=…"

# Install the CA's signed reply back into the same PSE
sapgenpse import_own_cert -c <signed_cert> -p <name>.pse -x <PIN>

# Export your own certificate to hand to a partner
sapgenpse export_own_cert -o <out_file> -p <name>.pse -x <PIN>

# Trusted certificate list (the "who do I trust" side)
sapgenpse maintain_pk -p <name>.pse -x <PIN>            # list
sapgenpse maintain_pk -a <cert_file> -p <name>.pse -x <PIN>   # add
sapgenpse maintain_pk -d <number> -p <name>.pse -x <PIN>      # delete entry <number>
```

**The rhythm to remember:** `get_pse -r` (request) → CA signs → `import_own_cert` (install reply)
→ `seclogin` (bind to the OS user) → restart what uses it.

> **`import_own_cert` must go back into the *same* PSE that generated the CSR** — the private key
> never leaves it. Generating a CSR in one PSE and importing the reply into another produces a PSE
> whose certificate and key do not match.

---

## 3. PSE types — which file for which job

| PSE | Purpose |
|---|---|
| **`SAPSSLS.pse`** | **S**erver — AS ABAP/Java acting as an **HTTPS server** |
| **`SAPSSLC.pse`** | **C**lient — the system acting as an HTTPS/TLS **client** (outbound) |
| **`SAPSSLA.pse`** | Anonymous client |
| **SNC PSE** | SNC identity for RFC/GUI/dispatcher; often `SAPSNCS.pse` |
| **`local.pse`** | **SAProuter** |

In AS ABAP these are normally maintained through **STRUST**, which is the same PSE store viewed from
inside the system. **`sapgenpse` and STRUST are two doors to one room** — changing a PSE on the file
system and not refreshing STRUST (or vice versa) is a classic source of confusion.

---

## 4. SAProuter certificate renewal

The SAProuter case is the one most Basis teams meet first, because the certificate **expires** and
takes the connection to SAP with it:

```bash
# 1. generate the request (as the saprouter OS user, with SECUDIR set)
sapgenpse get_pse -v -r certreq -p local.pse "<distinguished name from SAP for Me>"

# 2. submit certreq in SAP for Me → receive srcert

# 3. import the signed reply
sapgenpse import_own_cert -c srcert -p local.pse

# 4. bind credentials, then restart saprouter
sapgenpse seclogin -p local.pse -O <saprouter_os_user>
sapgenpse get_my_name -v -n Issuer          # verify what you ended up with
```

The distinguished name is **issued by SAP** and must be used verbatim. See **`sap-saprouter`** in
this repo for the routing and connectivity side.

---

## 5. HSM-backed PSEs

CommonCryptoLib 8 supports PSEs whose private key lives in a **Hardware Security Module** rather than
a file — **SAP Note 2719738** **[G]**. The `sapgenpse` surface is similar but the key is
non-exportable by design, which changes backup and recovery planning: you cannot simply copy the PSE
to restore the identity.

Cross-check with **`sap-backup-recovery`** on key handling — the same principle as database
encryption keys applies: *an identity you cannot restore is an outage waiting for a hardware
failure.*

---

## 6. Where the rest lives

| Topic | File |
|---|---|
| Full command/option reference, troubleshooting, STRUST relationship, platform paths | [references/sapgenpse-reference.md](references/sapgenpse-reference.md) |

## Cross-references

- **`sap-saprouter`** — SAProuter operation; this skill covers its certificate.
- **`sap-gui-landscape`** — SNC on the front end (`SNC_LIB`, `sncname`, `sncqop`) — the client half.
- **`sap-cloud-connector`** — its own certificate stores for BTP connectivity.
- **`sap-backup-recovery`** — key and credential recoverability.
- **`sap-security-patch`** — CommonCryptoLib is itself patched; check its version.
- **`sap-nw-java-pi`** — AS Java keystore lives in NWA; PI SOAP/HTTPS adapter failures are usually certificate-chain errors (same import-the-chain-first rule).

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

| # | Source | Read |
|---|---|---|
| **[CP1]** | SAP Help Portal — *Maintaining the Server's Certificate List Using SAPGENPSE* (SAP NetWeaver 7.5) | **[G]** — `maintain_pk` syntax |
| **[CP2]** | **SAP Note 2719738** — *CommonCryptoLib 8: HSM PSE* | **[G]** |
| **[CP3]** | **SAP Note 2820130** — *Importing Roles following SNC configuration results in `GSS-API(maj): No credentials were supplied`* | **[G]** — the credential-binding symptom |
| **[CP4]** | **SAP Note 1396213** — *How-To: Configure SNC for encryption or SSO* | **[G]** |
| **[CP5]** | SAP Help Portal — SNC and SSL configuration for AS ABAP / AS Java; STRUST documentation | **[G]** |
| **[CP6]** | **SAP Note 2505850** — importing an SSL certificate to AS Java | **[G]** |

> **Verify command syntax on your CommonCryptoLib version.** `sapgenpse` options have accumulated
> over CommonCryptoLib releases and some vary by platform. `sapgenpse <command> -h` on the actual
> host is authoritative; the forms above are the common ones and should be confirmed before use in a
> change.

> **Coverage honesty.** This skill is marked **[G]** throughout rather than **[V]** — the syntax was
> assembled from SAP Help Portal pages and Notes rather than read end-to-end from a single official
> command reference, because SAP does not publish one consolidated `sapgenpse` manual page. Treat it
> as a reliable map, and confirm exact options with `-h` before executing.
