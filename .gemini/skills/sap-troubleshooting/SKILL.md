---
name: sap-troubleshooting
description: >-
  Method and rules of thumb for troubleshooting any SAP issue — establish the facts, enumerate
  EVERY relevant log/trace source (SM21, ST22, SLG1, ST01/STAUTHTRACE, ST05, RSAU_READ_LOG,
  SM58/SMQ1, /IWFND/ERROR_LOG, Java defaultTrace, kernel dev_* traces, DB and OS logs),
  correlate by timestamp, ask what changed, and escalate to SAP with the right evidence. Use
  whenever something is broken, slow, failing intermittently, or "worked yesterday" — before
  reaching for a restart. Pairs with sap-log-reference and sap-health-triage.
---

# SAP Troubleshooting — method & rules of thumb

Applies to any SAP problem: an error, a hang, "slow", an interface that stopped, a job that fails at
night. The method matters more than any single command, because the common failure is **concluding too
early from one log**.

> ## Rule 0 — capture evidence *before* you restart
> A restart is the most common first move and it **destroys the evidence** (work-process state, locks,
> shared memory, in-flight traces). If the system is up enough to look at, spend two minutes collecting
> (§2) first. If you must restart to restore service, say explicitly what evidence was lost.

---

## 1. Establish the facts first (never skip)

Before opening any log, pin down:

| Question | Why it changes everything |
|---|---|
| **What exactly happened?** Error text/number, dump name, screenshot | "It doesn't work" is not a symptom |
| **When?** First occurrence, last occurrence, frequency | Drives the log time window; "since Tuesday" points at a change |
| **Who / how many?** One user, one client, everyone | One user → authorizations/data. Everyone → system/infra |
| **Where?** SID, client, instance/host, which app server | Instance-local logs mean you must look on the *right* host |
| **Reproducible?** Always / sometimes / once | Intermittent → collect over time, don't chase one trace |
| **Scope** — dialog, batch, interface, all? | Tells you which log families apply (§2) |
| **PRD or not?** | Sets the guardrails on what you may do next |

Then: **what changed?** Transport imported, kernel/SP patched, note applied, profile parameter, OS/DB
patch, certificate expiry, network/firewall change, data volume growth. Most "suddenly broken" has a
change behind it — check [sap-transport-mgmt](../sap-transport-mgmt/SKILL.md) import history,
[sap-kernel-patch](../sap-kernel-patch/SKILL.md), and the change record.

---

## 2. Enumerate ALL log sources for the layers involved  ← the core rule

**Do not open one log and stop.** Walk the request path and list every source that could hold evidence,
then say which you checked. The full catalogue is
**[sap-log-reference → complete-log-inventory.md](../sap-log-reference/references/complete-log-inventory.md)**.

Minimum sweep by symptom type:

| Symptom | Sources to enumerate |
|---|---|
| **Error / dump in a transaction** | ST22 · SM21 · SLG1 (app log) · SU53/STAUTHTRACE (if authorization) · dev_w* |
| **"No authorization"** | SU53 (that user) · STAUTHTRACE (system-wide) · SUIM · SAL (`RSAU_READ_LOG`) |
| **Slow / performance** | ST05 (SQL) · SAT/ST12 · ST03N · STAD · ST02 (buffers) · ST06 (OS) · ST04/DBACOCKPIT (DB) · DB02 |
| **Interface/RFC failure** | SM58 · SMQ1/SMQ2 · SBGRFCMON · SM59 test · SMGW · dev_rd |
| **IDoc problem** | WE02/WE05 · BD87 · SM58 · SLG1 |
| **Fiori / OData / HTTP** | `/IWFND/ERROR_LOG` **and** `/IWBEP/ERROR_LOG` · ST22 (backend!) · SMICM · SICF · dev_icm |
| **Web service / SOAP** | SRT_UTIL · SRT_MONI · SOAMANAGER · ST22 |
| **Job / batch fails** | SM37 job log **and** spool (SP01) · ST22 · SLG1 · SM13 |
| **Update terminates** | SM13 · ST22 · dev_w* of the update WP |
| **Printing/spool** | SP01/SP02 · SPAD · SP12 (TemSe) · SM21 |
| **Instance won't start / crashed** | dev_disp · stderr* · sapstart.log · `df -h` · `dmesg` (OOM) · sappfpar check · DB log |
| **Database-side** | The DB's own log (HANA trace/alert, Oracle alert, `db2diag.log`, ASE errorlog, `KnlMsg`, SQL Server `ERRORLOG`) + ST04/DB02/DB12 |
| **Security / "who did this"** | SAL (`RSAU_READ_LOG`) · SM21 · SCU3/`DBTABLOG` · CDHDR/CDPOS |
| **Java stack** | NWA Log Viewer · `defaultTrace.<n>.trc` · `std_server<n>.out` · `dev_server<n>` |

**Layer sweep** for anything non-trivial — check *each*, top to bottom:
front-end/Web Dispatcher → ICM/ICF → ABAP app server → interface layer → **database** → **OS/host** →
storage/network. Problems are frequently reported at one layer and caused at another.

---

## 3. Correlate — timestamps, user, host

- **Normalize time zones before comparing.** SM21/ABAP use the *system* time zone, OS logs the *host*
  zone, HANA often UTC, and a user's screenshot their local time. Most "the logs show nothing at that
  time" is a time-zone mismatch.
- Pin the exact window (a few minutes either side) and pull **all** sources for that window.
- Pivot on the same **user / terminal / host / WP number / transaction** across logs.
- Build a timeline: first symptom → what preceded it. The *first* error usually matters; later ones are
  often consequences.

---

## 4. Rules of thumb

1. **Read the whole error, not the headline.** ST22 holds the failing line, variables and the caller;
   `dev_w*` around the timestamp usually shows the DB/RFC cause.
2. **The first error in the chain is the real one.** Downstream errors are noise.
3. **"Nothing in the logs" almost always means "not that log."** Go back to §2.
4. **Check the boring causes first** — filesystem full, expired certificate/password, locked user,
   exhausted number range, full table space, expired license, DNS/port. `df -h` before theory.
5. **One change at a time**, record it, and know how to undo it. Two changes = no learning.
6. **Reproduce in non-PRD** where possible; that's where you may raise traces freely.
7. **Raise trace → reproduce → lower trace.** Never leave ST01/ST05/high `rdisp/TRACE` on.
8. **One user vs everyone** splits the search space in half — always determine it early.
9. **Correlate with a change window** before deep analysis; a recent transport/patch is the likeliest
   cause and the fastest fix (back it out).
10. **Don't fix the symptom.** Deleting the failed queue entry, or restarting nightly, hides a defect
    that will return — capture root cause first (Rule 0).
11. **Beware "it's the network."** Prove it, don't assert it. `niping` runs on the **TCP socket layer**
    (the same one SAP uses), and SAP's own rule settles the argument: *"If you can reproduce an error
    using NIPING then the problem is definitely related to the network layers, not to the application."*
    (SAP Note 500235). Also: `R3trans -d` for kernel→DB, `SM59` connection test, port checks.
12. **Write down what you ruled out**, not just what you found — that's what makes the next round faster.

---

## 5. Check SAP Notes before deep-diving

Most SAP errors are *known*. After §1–2, search the Notes with the **error text, dump name, message ID
or component** — it is often faster than analysis, and tells you whether a fix/patch exists. See
**Staying current** below.

---

## 6. Escalating to SAP

If you open an incident, attach evidence rather than description:
- Exact **error/message ID**, dump (ST22 → download), timestamps **with time zone**
- Relevant **logs** for the window (SM21, `dev_*`, DB log, interface log)
- **System data**: SID, release/SP, kernel patch (`disp+work -version`), DB + version, OS
- What you already **ruled out** and what changed recently
- A **reproduction** if you have one, and the business impact/urgency
- Open a **service connection** if requested ([sap-saprouter](../sap-saprouter/SKILL.md))

## Cross-references

- **Where each log lives + how to read it:** [sap-log-reference](../sap-log-reference/SKILL.md) — and the
  **[complete inventory](../sap-log-reference/references/complete-log-inventory.md)**.
- **Is it even up? / won't start:** [sap-health-triage](../sap-health-triage/SKILL.md).
- **Full filesystem found while triaging:** [sap-housekeeping](../sap-housekeeping/SKILL.md).
- **Recent change suspected:** [sap-transport-mgmt](../sap-transport-mgmt/SKILL.md) ·
  [sap-kernel-patch](../sap-kernel-patch/SKILL.md).
- **DB-side analysis:** [sap-db-command-reference](../sap-db-command-reference/SKILL.md).
- **`sap-health-triage` §0** — the **out-of-band escalation ladder** for a jammed system: `sapcontrol` works when the ABAP stack cannot answer, `dpmon` when `sapstartsrv` cannot.
- **`sap-nw-java-pi`** — PI/PO message triage (TBDL/HOLD/EOIO), adapter tracing, CPA cache; and the ESR/ID automation boundary.

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

Troubleshooting is mostly read-only, but the moment you run a kernel or DB tool the user still matters —
`<sid>adm` for SAP tools (`sapcontrol`, `dpmon`, `sappfpar`, `R3trans -d`), the DB owner for DB tools
(`ora<dbsid>`, `syb<dbsid>`, `db2<dbsid>`, `sdb`, the HANA SID's `<sid>adm`), `root` only where a
procedure requires it. Switch with `su - <user>` so the environment is set, and state the user with each
command. Full matrix: [sap-db-command-reference](../sap-db-command-reference/SKILL.md).

## Staying current — check SAP Notes first

SAP Notes supersede this file, and for troubleshooting they are often *the answer*, not just a check.

**If the [SAP Notes MCP](https://github.com/marianfoo/sap-mcp-servers) is configured:**

1. `search` the **exact error text, message ID, dump name, or component + symptom**.
2. `fetch` the promising Note IDs — check validity (release/SP/component), prerequisites and side effects
   before applying anything.
3. **Check the `attachments` array** — for troubleshooting Notes especially, the diagnostic script,
   trace-analysis spreadsheet or step-by-step PDF is frequently the attachment rather than the Note text.
4. Prefer the Note over this file where they disagree, and say which Note you followed.

**Downloading an attachment:** `fetch` returns `attachments[].url` **and `attachments[].filename`**;
**`fetch_attachment`** retrieves the bytes. Pass the URL verbatim. If your MCP build predates that tool,
open the URL in a signed-in browser and say the file was fetched manually.

> ⚠️ **Two ways a hand-rolled fetch goes wrong — both verified.** An unauthenticated request returns
> **HTTP 200 with a small HTML login stub**, not an error — check content type and magic bytes. And SAP
> serves many attachments from a *generic endpoint* (`…/services/attachment.htm?iv_key=…`), so the URL
> basename is `attachment.htm` even for a PDF — take the name from **`attachments[].filename`** or the
> **`Content-Disposition`** header, never from the URL path.

No MCP available? Look it up on `me.sap.com/notes` and say the check was skipped.

## Sources

- Log/transaction roles and the SAL currency facts are cited in
  [sap-log-reference → complete-log-inventory.md](../sap-log-reference/references/complete-log-inventory.md)
  (SAP Notes **2191612**, **3571619**, and the SAP Help *Log and Traces* map).
- Method is general SAP Basis practice; every concrete command/transaction it points at is cited in the
  skill that owns it.
