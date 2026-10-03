---
name: sap-nw-java-pi
description: >-
  SAP NetWeaver AS Java and PI/PO operations — NWA, the J2EE sapcontrol functions, jcmon and the
  telnet admin shell on 5<nr>08 as out-of-band channels, the AS Java log set (defaultTrace,
  std_server*.out, dev_jcontrol), and on PI: PIMON, message monitoring, the EOIO stuck-message
  decision tree, CPA cache and adapter traces. Explains why JCo is the WRONG tool for AS Java
  and what the real programmatic surfaces are (SOAP web services, monitor servlets, sapcontrol
  SOAP, JMX/P4, telnet). Use for "AS Java", "NWA", "PIMON", "PI message stuck", "To be
  delivered", "EOIO HOLD", "CPA cache refresh", "ESR", "Integration Directory", "defaultTrace",
  "server0", "adapter trace".
---

# SAP NetWeaver AS Java & PI/PO operations

**Sources.** **SAP Note 1514898 — *Troubleshooting SAP Process Orchestration / Integration***,
version **112**, released **17.08.2026**, component BC-XI-CON-AFW **[V]** — fetched and read.
URL surface, auth behaviour and monitor content **live-verified 2026-08-31 against a real PI 7.50
AS Java system** — marked **[LV]**. **[G]** = cited but not re-read in full.

> ## The boundary that decides what can be automated
>
> AS Java splits into two very different surfaces:
>
> | Surface | Technology | Automatable? |
> |---|---|---|
> | **NWA, PIMON, monitor servlets, SLD, MDT** | HTTP / WebDynpro / JSP | ✅ Browser or `curl` |
> | **ESR, Integration Directory, Config Tool, Visual Admin** | **Java Web Start / Swing** | 🚫 **No** — the browser only serves the `.jnlp` launcher; a local Java runtime runs the app |
>
> `/rep/start/index.jsp` and `/dir/start/index.jsp` returning HTTP 200 **[LV]** proves only that the
> *launch pages* exist — the **UIs** cannot be driven by a browser or headlessly.
>
> **But the UI is not the only door.** Integration Directory *content* has a **SOAP API** —
> `CommunicationChannelInService` exposes `Create`/`Read`/`Change`/`Delete`/`Query`/`OpenForEdit`/
> `Revert`, verified live **[LV]** (§2a). So "channel configuration is a desktop task" is **wrong for
> the objects, right for the tool**. Mapping design and repository browsing remain human work;
> channel and configuration objects are scriptable.

---

## 1. The URL map — live-verified on PI 7.50 **[LV]**

All on the Java HTTP port **`5<nr>00`** (instance 00 → 50000):

| Path | What | Verified behaviour |
|---|---|---|
| `/nwa` | **NetWeaver Administrator** — the central admin UI | 302 → WebDynpro `FloorPlanApp`; needs a browser session, not plain curl |
| `/pimon` | **PI Monitoring** home (7.3x+) | 200 |
| `/dir/start/index.jsp` | Integration Directory **launch page** | 200 (tool itself is Web Start) |
| `/rep/start/index.jsp` | ESR **launch page** | 200 (tool itself is Web Start) |
| `/mdt` | Message Display Tool | 302 → `/mdt/` |
| `/rwb` | Runtime Workbench (legacy, pre-7.3 style) | 302 → `/rwb/` |
| `/sld` | System Landscape Directory | 302 → `/sld/` |
| `/MessagingSystem/monitor/monitor.jsp` | **Messaging System monitor** — queues, System Status, Sequence Status | 401 → **works with Basic auth**; links `systemStatus.jsp`, `sequenceStatus.jsp` |
| `/CPACache/monitor.jsp` | **CPA cache monitor** | 401 → works with Basic auth |
| `/CPACache/history.jsp` | Cache-update history (incl. the update XML) | [G, Note 1514898] |
| `/AdapterFramework/scheduler/scheduler.jsp?xml` | AFW scheduling table as XML | 401 → Basic auth [G] |

> **Scripting tip [LV]:** the monitor servlets accept Basic auth directly, so health checks are one
> `curl -u` away — no login form, no cookies. `/nwa` is the exception: WebDynpro wants a real session,
> so drive it with a browser, not curl.

**NWA paths that matter** (inside `/nwa`): *Troubleshooting → Logs and Traces → Log Viewer* and
*Log Configuration*; *SOA → Monitoring → Message Monitoring* (the NWA route to the same monitor);
*Troubleshooting → Security Troubleshooting Wizard* (see §5). **[V, Note 1514898]**

---

## 2a. Programmatic access — and why JCo is the wrong tool

> ## 🛑 **JCo does not administer AS Java**
>
> SAP Java Connector speaks **RFC to an ABAP stack**. AS Java is not an RFC server — there is no
> JCo destination that gets you a Java admin session. Handing a script JCo credentials buys you
> nothing here.
>
> The confusion is understandable: PI's **IDoc_AAE and RFC adapters** do use JCo (`com.sap.mw.jco`,
> `com.sap.conn.jco` appear in their trace locations). But that is the *adapter runtime* calling
> **out** to ABAP systems — not you calling **in** to administer Java.

**What is actually scriptable, in order of usefulness:**

| # | Surface | Port | Auth | Verified |
|---|---|---|---|---|
| 1 | **SOAP web services** (below) | `5<nr>00` / `5<nr>01` | Basic **/ SSL / client cert** | **[LV]** |
| 2 | **Monitor servlets** (`MessagingSystem`, `CPACache`, AFW scheduler) | `5<nr>00` | **Basic** | **[LV]** |
| 3 | **`sapcontrol` SOAP web service** | `5<nr>13` / `5<nr>14` | Basic / none | **[G]** |
| 4 | **JMX over P4** — what NWA and the old Visual Admin use underneath | `5<nr>04` | Java client only | **[G]** |
| 5 | **Telnet admin shell** | `5<nr>08` | Interactive | **[G]** |

**Browser genuinely required for only two things:** **NWA** (WebDynpro — needs a real session, curl
gets a 302 into `FloorPlanApp` **[LV]**) and the **Swing clients** (ESR/ID GUI, Config Tool, Visual
Admin).

### The two APIs worth knowing **[LV]**

```bash
# 1. Message monitoring — the API behind PIMON's message search
curl -su "$U:$P" "http://<host>:5<nr>00/AdapterMessageMonitoring/basic?wsdl"
```

Three binding ports are published, which is the interesting part **[LV]**:

| Port | Endpoint |
|---|---|
| `basicPort` | `http://<host>:5<nr>00/AdapterMessageMonitoring/basic` |
| `sslPort` | `https://<host>:5<nr>01/AdapterMessageMonitoring/ssl` |
| **`clientCertPort`** | `.../AdapterMessageMonitoring/clientCert` |

> **A client-certificate binding exists.** For unattended monitoring, that is the right auth —
> no service password in a script or a `ps` listing. Certificate handling is `sap-crypto-pse`.

```bash
# 2. Integration Directory — communication channel CRUD
curl -su "$U:$P" \
  "http://<host>:5<nr>00/CommunicationChannelInService/CommunicationChannelInImplBean?wsdl"
```

Operations verified live **[LV]**: `Query`, `Read`, `Check`, `Create`, `CreateFromTemplate`,
`Change`, `Delete`, `OpenForEdit`, `Revert`.

> ⚠️ **`Change`, `Create` and `Delete` alter the Integration Directory.** `Query`/`Read` are the safe
> pair for inventory and drift-detection; the mutating operations are change-controlled work that
> normally goes through ID with an approval trail. A script that edits channels bypasses that trail —
> and the change still needs a **CPA cache** update to take effect (§4).

**Practical uses of the read side:** inventory every channel across environments, diff DEV/QA/PRD
configuration, detect channels stopped outside a change window, feed monitoring. All read-only, all
scriptable, no desktop Java anywhere.

**Discovery:** not every service is deployed on every system — `/MessagingSystem/services/...` and
`/mdt/messagemonitor` returned **404** on the test system **[LV]**. Probe for `?wsdl` before assuming.

---

## 2. AS Java administration — the process model first

Everything else makes sense once the process chain is clear:

```
sapstartsrv → jcontrol/jstart → server0..serverN (the JVMs doing the work)
                              → ICM (7.1+: HTTP enters via ICM, as in ABAP)
```

**Out-of-band channels, in escalation order** (same philosophy as `sap-health-triage` §0):

| # | Channel | Needs | Gives |
|---|---|---|---|
| 1 | **NWA** | A working server node + session | Everything, visually |
| 2 | **`sapcontrol` J2EE functions** | Only `sapstartsrv` (port `5<nr>13`) | Process/thread/session state when NWA is dead |
| 3 | **`jcmon pf=<profile>`** | Shared memory on the host | Cluster/process view when even sapcontrol is unreachable |
| 4 | **Telnet admin shell, port `5<nr>08`** | A reachable server node, admin user | Command-line administration: `lsc`, `jump <n>`, `list_app`, `stop_app`/`start_app` |
| 5 | **OS**: traces in `work/` and `j2ee/cluster/server<n>/log/` | Filesystem | Post-mortem |

```bash
# the J2EE-specific sapcontrol surface [G]
sapcontrol -nr <nr> -function J2EEGetProcessList2     # server nodes + their real state
sapcontrol -nr <nr> -function J2EEGetThreadList2      # thread state per node
sapcontrol -nr <nr> -function J2EEGetSessionList
sapcontrol -nr <nr> -function J2EEGetCacheStatistic
sapcontrol -nr <nr> -function GetProcessList          # jcontrol/jstart level only
```

> ⚠️ **`GetProcessList` GREEN is not "AS Java is up."** It reports the jcontrol/jstart layer. A
> server node can be in endless restart, or running with the application layer dead, while
> `GetProcessList` stays GREEN — the same trap as `PRIV` mode on ABAP. Use
> **`J2EEGetProcessList2`** for the truth about server nodes.

**The telnet shell** (rung 4) is the AS Java equivalent of `dpmon`: local, session-based, works when
HTTP does not. `telnet <host> 5<nr>08`, log on with an administrator, `lsc` lists cluster nodes,
`jump <node>` attaches, `list_app` / `stop_app <app>` / `start_app <app>` manage applications. Treat
`stop_app` with the same discipline as killing a work process — capture state first.

**Where the logs are:**

| File | Where | What |
|---|---|---|
| `defaultTrace.trc` | `/usr/sap/<SID>/<inst>/j2ee/cluster/server<n>/log/` | **The** AS Java trace — first stop |
| `applications.log` | same | Application-level log |
| `std_server<n>.out` | `work/` | JVM stdout — **OOM and GC evidence lands here** |
| `dev_jcontrol`, `dev_server<n>` | `work/` | Process-level start/crash traces |

Read them via **NWA Log Viewer**, or directly on the filesystem (`sap-log-reference` covers the
work-directory family). Trace paths per Note 1514898: `/usr/sap/<SID>/<instance>/j2ee/cluster/server<n>/log`. **[V]**

---

## 3. PI messaging — status model and the stuck-message tree

The message statuses you triage by: **TBDL** (to be delivered), **DLNG** (delivering), **HOLD**
(EOIO, waiting on a predecessor), **WAIT/NDLV** (retry/not delivered), **FAIL**, **DLVD**.

> ## 🔑 The EOIO decision tree — Note 1514898, condensed **[V]**
>
> **Messages heap in TBDL** (dispatcher or adapter queue):
> - Check MS queues on **all nodes** — Messaging System monitor → Queues.
> - Take **4–5 thread dumps at 20–30 s intervals**. Do **not** set DEBUG severities.
> - *"It is usually a stuck/slow receiver processing."* The queue is the symptom.
>
> **Messages heap in HOLD** (EOIO): find the **blocking predecessor** in the EOIO Sequence Monitor
> (`/MessagingSystem/monitor/sequenceMonitor.jsp` or NWA), then act by the predecessor's state:
>
> | Predecessor | Action |
> |---|---|
> | `DLNG` | Thread dumps (2–3, 15–20 s apart) — something is stuck mid-delivery |
> | `TBDL` | Queues overloaded — restarting it puts it at the front of the queue |
> | `FAIL` | **Restart the first HOLD message** |
> | `NDLV`/`WAIT` | Fix the audit-log error, restart the predecessor; if undeliverable, **cancel it** to free the sequence (or *Restart Sequence*) |
> | `DLVD` (yet HOLD persists) | Rare — collect both audit logs for SAP; restarting the first HOLD is the workaround |
> | **missing** | It reached final state and was archived/deleted — restart the first HOLD message |
>
> Restart/cancel are **data-affecting** on an EOIO sequence — ordering is the whole point of EOIO.
> Confirm with the interface owner before cancelling a predecessor.

**Where to search messages:** `/pimon` → *Monitoring → Adapter Engine → Message Monitoring* (or NWA →
*SOA → Monitoring*). The **Database** tab searches persisted messages, **Archive** searches archived
ones; *Advanced* combines all criteria except message-ID search. **[V]**

---

## 4. CPA cache — the "my change does nothing" mechanism

Channel/agreement changes flow **Integration Directory → CPA cache** on activation. When a change
does not take effect, the cache did not update.

```bash
# live-verified surface [LV]
curl -su "$USER:$PASS" http://<host>:5<nr>00/CPACache/monitor.jsp   # cache state
#          .../CPACache/history.jsp                                  # update history + update XML
```

From Note 1514898 **[V]**: a **dummy change** (edit a channel description, activate) forces a delta
update; a hanging cache update calls for **thread dumps from all server nodes while it hangs**; the
`trackCacheUpdateXML` property of the CPA-cache service captures the update XML — **revert it to
`false` immediately**, it degrades performance. Full refresh exists but is the bigger hammer
(Note 2726888 documents interfaces erroring right after one).

---

## 5. Tracing — the NWA way, and the tool that just died

> ## ⚠️ **XPI Inspector is retired.** Note 1514898 v112, verbatim: it is *"no longer available for
> download from 1st of February 2026 and its usage is not recommended. We strongly recommend
> undeploying the tool."* **[V]**
>
> Years of community guides say "run XPI Inspector example 50". That advice is now stale — the
> supported path is NWA's own tools below. If the tool is still deployed on your system, plan its
> removal.

**The two supported flows** **[V, Note 1514898]**:

| Flow | When | Where |
|---|---|---|
| **Security Troubleshooting Wizard** | No restart needed | NWA → *Troubleshooting → Logs and Traces*. With Note **3691989**: 36 ready-made **XPI incidents** (alerting, CPA cache, adapters…) — select scenario, *Start Diagnostics*, reproduce, download |
| **Log Configuration** | Restart involved (custom incidents live in memory and die with it) | Same NWA path — set the adapter's trace **location** to ALL, reproduce, **revert immediately** (*Default Configuration* button) |

Key trace locations (full table in [references/nw-java-pi-operations.md](references/nw-java-pi-operations.md)):
`com.sap.aii.adapter.file`, `...jdbc`, `...sftp`, `...jms`, `com.sap.aii.af.rfc` + `com.sap.mw.jco`
(RFC), `com.sap.aii.adapter.rest` + `com.sap.httpclient` (REST), `com.sap.aii.af.mp.soap` (SOAP),
`com.sap.aii.af.idoc` (IDoc_AAE), mapping runtime `com.sap.aii.ibrun` et al. **[V]**

**Performance/hang evidence:** 3–5 thread dumps at 30 s intervals (Notes 710154, 1020246), SAP JVM
Profiler for CPU/method-duration analysis (Note 1783031). **[V]**

---

## 6. Where the rest lives

| Topic | File |
|---|---|
| Full adapter trace-location table, thread-dump how-to, telnet shell reference, ESR/ID client requirements, RWB legacy map | [references/nw-java-pi-operations.md](references/nw-java-pi-operations.md) |

## Cross-references

- **`sap-health-triage`** — §0 out-of-band ladder; this skill is its AS Java counterpart.
- **`sap-log-reference`** — `defaultTrace`, `std_server*.out`, `dev_jcontrol` in the wider log map.
- **`sap-crypto-pse`** — AS Java keystore/SSL sits in NWA, but the concepts (chains, key/cert match) transfer; SOAP/HTTPS adapter errors are usually certificate errors.
- **`sap-troubleshooting`** — when the PI problem is actually an ABAP-side problem (SM58 for IDoc_AAE, SPROXY/ESR connectivity).
- **`sap-system-lifecycle`** — start/stop ordering; AS Java instances stop like any other via sapcontrol.
- **`sap-hana-xsa`** — a *different* Java-ish runtime with a similar out-of-band story (`XSA` CLI). Do not conflate.

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
| **[NJ1]** | **SAP Note 1514898** — *Troubleshooting SAP Process Orchestration / Integration*, v**112**, 17.08.2026, BC-XI-CON-AFW | **[V]** — trace flows, adapter locations, EOIO tree, CPA cache, XPI Inspector retirement |
| **[NJ2]** | **Live verification** — PI **7.50** AS Java system (dev), 2026-08-31: URL surface, Basic-auth behaviour of monitor servlets, Messaging System monitor content, **`AdapterMessageMonitoring` binding ports (basic/ssl/clientCert) and `CommunicationChannelInService` operation list** | **[LV]** |
| **[NJ3]** | **SAP Note 3691989** — Security Troubleshooting Wizard XPI incidents | **[G]** |
| **[NJ4]** | **SAP Note 2135741** — *Finding the Message Blocking an EOIO Sequence in the PI Adapter Engine* | **[G]** |
| **[NJ5]** | **SAP Notes 710154 / 1020246 / 1783031** — thread dumps, Thread Dump Viewer, SAP JVM Profiler | **[G]** |
| **[NJ6]** | **SAP Note 1623356** — *"To be delivered" messages in Adapter Engine* | **[G]** |
| **[NJ7]** | **SAP Note 2726888** — interface errors after full CPA cache refresh; **1095475** — HTTP Provider trace | **[G]** |
| **[NJ8]** | **SAP Note 854536** — *Adapter Framework: Information Required by SAP Support* | **[G]** |
| **[NJ9]** | **SAP Note 1715441** — deploy/undeploy on AS Java (the supported route for removing XPI Inspector) | **[G]** |

> **Release caveat.** Live verification was against **7.50**, the terminal AS Java release for PI/PO.
> Older dual-stack XI/PI (7.0x–7.31) differs materially: RWB instead of PIMON as primary monitor,
> ABAP-side pipeline (SXMB_MONI) for the Integration Engine half, and different URL surface. This
> skill covers the **AEX/PO single-stack** shape first; the dual-stack ABAP half lives in transaction
> land (SXMB_MONI, SMQ1/SMQ2) — see `sap-troubleshooting`.

> **`sapcontrol` J2EE functions are [G], not [LV]** — port `5<nr>13` was not reachable from the test
> vantage point, so their output shape was not re-verified live. The functions themselves are
> standard sapcontrol web methods.
