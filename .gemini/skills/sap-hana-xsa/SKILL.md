---
name: sap-hana-xsa
description: >-
  SAP HANA XS Advanced operations — `xs` for normal work and `XSA` for local maintenance when
  remote access is gone (diagnose, collect-traces, restart, du, list-tenants). Covers the
  org/space model, routing mode (unchangeable after installation), the app-working directory and
  its sizing, global_allocation_limit, certificate expiry, tenant-database registration and the
  joint-recovery backup rule, and XSA under HANA System Replication. Use for "xs CLI", "XSA",
  "xs login", "xs apps", "XSA diagnose", "xscontroller not starting", "xs command not found",
  "routing mode", "app_working". NOT the BTP `cf` CLI.
---

# SAP HANA XS Advanced (XSA)

**Sources.** *The SAP HANA XS Command-Line Interface Reference*, SAP HANA Platform **2.0 SPS 04**,
Document Version 1.1 – 2019-10-31 **[V]** — downloaded and read. **SAP Note 2596466 — *FAQ: SAP HANA
XS advanced***, version **74**, released **22.05.2026**, component BC-XS-RT **[V]** — fetched and
read; 51 questions. Marks: **[V]** verified, **[G]** cited but not read in full.

> ## ⚠️ `xs` is not `cf` — and the resemblance is the trap
>
> The XSA CLI deliberately mirrors Cloud Foundry's shape: `xs login`, `xs target`, `xs apps`,
> `xs push`, `xs logs`, orgs and spaces. **It administers XS Advanced on an on-premise HANA system,
> not SAP BTP.** The platforms are unrelated, the commands are not interchangeable, and a runbook
> that says "log in and push" is ambiguous unless it names the CLI.
>
> If your landscape has both, be explicit. See **`sap-btp-cli`** for the BTP side.

**Licensing:** *"except a valid SAP HANA platform license, no additional license is required to
install and run SAP HANA XS advanced."* **[V]**

---

## 1. Two CLIs — and the second one is your fallback

This is the distinction that matters operationally, and Note 2596466 states it directly **[V]**:

| Tool | Scope | Documented purpose |
|---|---|---|
| **`xs`** | Remote **or** local | Operate XSA — *"either remotely and locally after logging in as `<sid>adm`"* |
| **`XSA`** | **Local only** | XSA **maintenance** locally as `<sid>adm`, *"**e.g. when remote access is not possible any more**"* |

> ## 🔑 `XSA` is the out-of-band channel for XS Advanced
>
> Exactly the same pattern as `sapcontrol` for a jammed ABAP stack (see **`sap-health-triage` §0**):
> when the normal API path is unreachable — the controller is down, the router is broken, the
> certificate expired — you fall back to a **local** tool run as `<sid>adm` on the host.
>
> **`xs` needs a working XSA API. `XSA` does not.** When `xs login` will not connect, stop retrying
> it and go to `XSA diagnose`.

### The `XSA` commands worth memorising **[V]**

```bash
# as <sid>adm on the HANA host
XSA diagnose          # check + display KNOWN configuration issues, and recommend fixes
XSA collect-traces    # bundle ALL system traces into one file — do this before opening a case
XSA restart           # restart XS advanced
XSA list-tenants      # which databases XSA uses; prints "XS advanced platform persistence: YES"
XSA du                # how much disk XSA applications and file-system services consume
```

**`XSA diagnose` is the first command in almost any XSA incident.** It reports known configuration
problems, warns about **expired certificates**, and recommends next steps. **[V]**

Some `XSA` service commands need the **`SYSTEM` user temporarily activated** on the system database
and every XSA-enabled tenant **[V]**: `update-tenants`, `unlock-technical-users`,
`renew-passwords-of-technical-users`, `select-xsa-runtime-db`.

---

## 2. The `xs` CLI

```bash
xs login [-a <API_URL>] [-u <USER>] [-p <PASSWORD>] [-o <ORG>] [-s <SPACE>]
xs-admin-login          # shortcut: log on as XSA_ADMIN when already <sid>adm on the host
xs target [-o <ORG>] [-s <SPACE>]
xs api                  # set or view the API URL
```

**[V]** — command families from the CLI Reference:

| Area | Commands |
|---|---|
| **Apps** | `apps`(a), `app`, `push`(p), `scale`(s), `delete`(d), `delete-app-instances`, `rename`, `start`(st), `stop`(sp), `restart`(rs), `restage`(rg), `wait-for-apps`, `events`, `files`(f), `logs`, `set-logging-level`(sll), `unset-logging-level`(ull) |
| **Services** | `services`, `service`, `create-service`, `delete-service`, `bind-service`, `unbind-service`, `service-keys`, `create-user-provided-service`, `update-user-provided-service` |
| **Orgs / spaces** | `orgs`, `org`, `create-space`, `update-space`, `delete-space` |
| **Routes / domains** | `routes`, `create-route`, `map-route`, `unmap-route`, `delete-route`, `domains` |
| **Certificates** | `set-certificate`, `set-hana-broker-client-certificate` |
| **Tenant DBs** | `create-tenant-database`, `map-tenant-database`, `unmap-tenant-database`, `tenant-database-mappings` |
| **Runtimes / tasks / users** | `runtime`, `update-runtime`, `delete-runtime`, `create-user`, `users`, `create-role`, `update-role`, `update-role-collection` |
| **Admin** | `traces`, `enable-trace`, `disable-trace`, `ps` (PIDs of app instances in the space) |
| **Deploy (MTA)** | `deploy`, `bg-deploy`, `undeploy` |

> **`xs create-tenant-database` ≠ creating a tenant at database level.** The `xs` form *also*
> **registers** the database for XS advanced. **[V]** Creating one with SQL leaves it unregistered.

**Remote use** requires installing the XSA command-line client on the remote machine — SAP Note
**2242468** **[G]**. `xs: command not found` on the HANA host itself is Note **2698717** **[G]**.

---

## 3. Decisions you cannot undo after installation

> ## 🛑 **Routing mode cannot be changed after installation.** **[V]**
>
> You choose **port routing** or **hostname routing** at install time. Hostname routing is
> **recommended for productive use** and needs a **wildcard DNS entry** pointing the default domain
> and all sub-domains at the XSA Platform Router. Getting this wrong means a reinstall.
> See SAP Note **2245631**.

What *can* be changed afterwards **[V]**:

| Setting | Changeable? | How |
|---|---|---|
| **Routing mode** | 🚫 **No** | Reinstall |
| Default domain | ✅ Yes | `default_domain` in `xscontroller.ini`, then restart |
| Router port (hostname routing) | ✅ Yes | `router_port` in `xscontroller.ini`, then restart — all routes move |
| Router **port range** (port routing) | ⚠️ Partly | `router_portrange_start`/`_end` — **only affects newly created applications**; existing apps keep their ports |
| App working path | ✅ Yes | `basepath_xsa_appworkspace` in `global.ini`, then `XSA restart` |

**System vs tenant database** is also a design-time decision with lasting consequences **[V]**:

- **In the system database** — XSA services survive deletion of all tenants, but there are
  **restrictions on backing up and restoring XSA data separately**.
- **In a tenant database** — overcomes those backup restrictions, but **XSA stops working and must be
  reinstalled if that tenant is deleted**.

---

## 4. Sizing and memory — the parameter people miss

> ## ⚠️ XSA services are **not** part of SAP HANA memory management
>
> `xscontroller`, `xsexecagent`, `xsuaaserver` and the application processes live **outside** the
> HANA database's memory bookkeeping. On a host carrying both `worker` and `xs_worker` roles you must
> set **`global_allocation_limit`** so the indexserver leaves room for them. **[V]**
>
> Skip this and HANA will happily allocate memory that XSA also needs.

**Disk** **[V]**:

- Application working directory defaults to **`/hana/shared/<SID>/xs/app_working`**.
- Reserve **≥ 100 GB**; **≥ 500 GB** where many developers work concurrently.
- The **file-system sandbox of up to 3 application instances per application** is kept there for
  post-mortem crash analysis — which is why it grows more than expected.
- Its **disk performance is crucial** for deployment and startup speed. If it sits on network
  storage and feels slow, test an alternative first with
  `XSA diagnose --app-working-dir <path>` (XSA 1.3.4+).

**Do not increase `max_lob_prefetch_size`** in `indexserver.ini` — it raises client memory
requirements and **XSA processes can run out of memory during installation, preventing it
entirely**. **[V]**

**Environment-variable limit:** the OS caps an environment variable at roughly **128k**, and all
service-binding credentials are passed in a single **`VCAP_SERVICES`** variable — so at ~1k per HANA
binding, **about 120 services** can bind to one application before it breaks. **[V]**

**Antivirus:** exclude the app working path from scanning. **[V]**

---

## 5. XSA with HANA System Replication and multi-host

> **You cannot install XSA from scratch into an existing HSR setup.** The systems must be
> **decoupled first**, XSA installed on each individually (SAP Note 2300936). **[V]**

> **With HSR active, deploy or update applications on the *current primary only*.** They replicate
> automatically; a secondary starts the updated applications when it comes up. **[V]**

**Multi-host** **[V]**:

- `xs_worker` role can be added to existing `worker` hosts or run on separate, individually sized hosts.
- A **failover router** is needed to hide host switches when `xscontroller` runs on the master host
  or master candidate, or when `xs_standby` hosts exist.
- **Shutdown order: shut the active master host down *last*.** Otherwise a master failover during
  shutdown moves the nameserver *and* XSA services — and potentially application instances — to
  another candidate, which is pointless work during a shutdown.

**Backup rule that surprises people** **[V]**:

> **Tenant databases registered for XS advanced cannot be backed up, recovered or moved
> individually.** To keep platform and application data consistent, **all registered tenants must be
> backed up and recovered together.**

---

## 6. Certificates

Right after installation XSA uses a **self-signed** certificate for the default domain on the
platform router. **[V]** Expiry shows up as:

- Browser security warnings on the platform API or applications
- **XSA update fails** with *"Certificate has expired"*
- `xscontroller_0.log` containing **`Own cert expired`**
- **`XSA diagnose`** printing a warning

Renewal and lifetime checks: SAP Note **2243019** **[G]**; `xs set-certificate` is the CLI side.
Chain problems surface as *"Provided chain does not include all certificates up to the root
certificate"* (Note **2666262**) **[G]** — the same "import the chain first" lesson as
**`sap-crypto-pse`**.

---

## 7. Where the rest lives

| Topic | File |
|---|---|
| Troubleshooting playbook, known-issue Notes, trace locations, upgrade/downgrade | [references/xsa-operations.md](references/xsa-operations.md) |

## Cross-references

- **`sap-btp-cli`** — the BTP `cf` CLI that `xs` resembles. **Different platform; not interchangeable.**
- **`sap-hana-lifecycle-tools`** — `hdblcm` installs and updates XSA; `hdbcons` for the DB underneath.
- **`sap-hana-system-replication`** — HSR constraints in §5.
- **`sap-crypto-pse`** — certificate chain handling.
- **`sap-health-triage`** — the same out-of-band thinking, for the ABAP stack.
- **`sap-space-reclaim`** — `app_working` growth and XSA log files.

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
| **[XS1]** | **SAP Note 2596466** — *FAQ: SAP HANA XS advanced*, v**74**, 22.05.2026, BC-XS-RT | **[V]** — 51 questions; source of the `xs` vs `XSA` distinction, routing-mode immutability, memory/disk sizing, HSR and backup rules |
| **[XS2]** | *The SAP HANA XS Command-Line Interface Reference*, HANA Platform **2.0 SPS 04**, Doc v1.1 – 2019-10-31 | **[V]** — command families and `xs login` syntax |
| **[XS3]** | **SAP Note 2245631** — default domain and routing mode | **[G]** |
| **[XS4]** | **SAP Note 2618752** — XSA resource consumption / sizing profiles; **2509043** — high-load configuration | **[G]** |
| **[XS5]** | **SAP Note 2300936** — XSA with System Replication / failover router; **2669931** — NZDU integration | **[G]** |
| **[XS6]** | **SAP Note 2243019** — domain certificates; **2666262** — incomplete chain on `set-certificate` | **[G]** |
| **[XS7]** | **SAP Note 2242468** — installing the XSA CLI client on a remote machine; **2698717** — `xs: command not found` | **[G]** |
| **[XS8]** | **SAP Note 2462741** — collecting traces for XSA runtime/startup issues; **2656132** — granting support-user privileges (XSA ≥ 1.0.82) | **[G]** |
| **[XS9]** | **SAP Note 2243156** — additional restricted OS users and sudoers; **2507070** — port ranges for multiple XSA systems on one host | **[G]** |
| **[XS10]** | **SAP Note 2347931** / **2378962** / **2711421** — XSA component compatibility, maintenance strategy, XS Advanced Collection | **[G]** |
| **[XS11]** | **SAP Note 3445668** — system copy with XSA; **2767842** — migrating XSA between system and tenant DB | **[G]** |
| **[XS12]** | **SAP Note 2082466** — known HDBLCM issues (includes XSA-specific ones); **2520710** — uninstalling XSA | **[G]** |

> **The CLI Reference read here is SPS 04 (2019).** XSA command sets have moved on; treat the command
> families as the shape and confirm exact options with `xs help <command>` on your release. Note
> 2596466 (2026) is the current operational authority and was read in full.

> **XSA is a maturing-out technology.** SAP's strategic application platform is SAP BTP; XSA remains
> supported and widely deployed on-premise, notably as the runtime under **SAP HANA cockpit**. Treat
> new-build proposals on XSA with that context, while operating existing installations normally.
