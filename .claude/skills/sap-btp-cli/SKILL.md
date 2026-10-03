---
name: sap-btp-cli
description: >-
  SAP BTP command-line administration — the btp CLI (subaccounts, directories, entitlements,
  role collections, environments, service instances) and the cf CLI as SAP uses it, including
  the MultiApps plugin (deploy, bg-deploy, rollback-mta, undeploy) and mbt. Use for "btp CLI",
  "btp login", "create subaccount", "assign entitlement", "role collection", "cf CLI", "cf
  push", "deploy MTA", "mtar", "blue-green deploy", "mbt build".
---

# SAP BTP command-line administration

**Sources.** SAP's own documentation, fetched as raw markdown from the **`SAP-docs/btp-cloud-platform`**
repository (the published source behind help.sap.com) **[V]**. Marks: **[V]** read directly, **[G]**
cited but not read in full.

> ## ⚠️ Different world from the rest of this repo
>
> Every other skill here targets an **on-premise ABAP/database stack** — `sapcontrol`, `R3trans`,
> `hdbnsutil`, BR\*Tools. This one targets **SAP BTP**, where you administer a *tenant*, not a host.
> There is no `<sid>adm`, no profile, no `/usr/sap`. Do not carry assumptions across.

**Two CLIs, one platform.** They are not alternatives — they own different layers:

| | **btp CLI** | **cf CLI** |
|---|---|---|
| Scope | The **account model**: global accounts, directories, subaccounts, entitlements, users, role collections, environments, service instances via SAP Service Manager | The **Cloud Foundry runtime inside** a subaccount: orgs, spaces, apps, routes, services, builds |
| Who ships it | SAP | Cloud Foundry Foundation (+ SAP plugins) |
| Typical user | Platform / account administrator | Developer, deployer |

You will routinely use both in one session: `btp` to create and entitle the subaccount, then `cf` to
deploy into it.

---

## 1. btp CLI — the syntax that explains everything

```
btp [OPTIONS] ACTION GROUP/OBJECT [PARAMS]
```

**[V]** Every command is that shape. Once you internalise it the CLI stops needing memorisation:

- **`btp`** — the base call.
- **OPTIONS** — e.g. `--format json` to change output format, `--verbose` for verbose execution.
- **ACTION** — the verb: `get`, `list`, `create`, `delete`, `assign`, and others depending on the
  group/object.
- **GROUP/OBJECT** — the entity acted on. Three groups **[V]**:

  | Group | Contains |
  |---|---|
  | **`accounts`** | The account model, subscriptions, environments |
  | **`security`** | Authorization objects and users |
  | **`services`** | Objects related to **SAP Service Manager** |

- **PARAMS** — passed with most commands.

```bash
btp --verbose list accounts/subaccount     # documented sample
btp --format json list accounts/subaccount # machine-readable, for scripting
```

**`help` is a special ACTION and can go anywhere in the command** **[V]** — put it at the front and
still append the rest:

```bash
btp help accounts            # every object + action available in the accounts group
btp help list accounts/subaccount
```

> ⚠️ **A parameter value beginning with `-` can be mistaken for a parameter name.** SAP flags this
> explicitly. **[V]** Quote such values, and remember the **shell** interprets your line before the
> CLI ever sees it.

**Getting started, straight from the docs** **[V]**:

```bash
btp login
btp list accounts/subaccount
btp list security/user
btp get security/user "name@example.com"
```

Autocompletion exists and is worth enabling. **[V]**

---

## 2. cf CLI and the MultiApps plugin

Plain Cloud Foundry commands (`cf login`, `cf target`, `cf push`, `cf apps`, `cf services`,
`cf logs`) work as upstream. What is **SAP-specific** is the **MultiApps plugin**, which extends cf
with multitarget-application commands. **[V]**

**Install it** **[V]**:

```bash
cf plugins                                                    # is MtaPlugin already there?
cf add-plugin-repo CF-Community https://plugins.cloudfoundry.org
cf install-plugin multiapps -f
cf plugins                                                    # verify
```

> ## 🛑 Uninstall the old `MtaPlugin` first
>
> The plugin was **formerly named `MtaPlugin`**. If the old one is still installed, the new one
> refuses to install, because the command names collide **[V]**:
>
> ```
> Plugin multiapps v<version> could not be installed as it contains commands with names
> and aliases that are already used:
> bg-deploy, deploy, download-mta-op-logs, mta, mta-ops, mtas, purge-mta-config, undeploy, dmol
> ```
>
> That error is a **name clash, not a corrupt download** — uninstall `MtaPlugin`, then retry.

**Prerequisite:** cf CLI **6.40 or higher** **[V]**; **v8** is supported for MTA work **[G]**.

**The MTA command set** **[V]**:

| Command | Purpose |
|---|---|
| **`cf deploy`** | Deploy a new MTA, or synchronise changes to an existing one |
| **`cf bg-deploy`** | **Blue-green (zero-downtime)** deployment |
| **`cf rollback-mta`** | Roll back to a previously deployed MTA |
| **`cf undeploy`** | Remove an MTA |
| **`cf mta`** | Detail on one deployed MTA |
| **`cf mtas`** | List deployed MTAs |
| **`cf mta-ops`** | List MTA **operations** — where you look when a deploy is stuck |
| **`cf download-mta-op-logs`** (`dmol`) | Pull the logs of an MTA operation |
| **`cf purge-mta-config`** | Purge stale MTA configuration entries |

**Build then deploy** — two different tools **[G]**:

```bash
mbt build            # Cloud MTA Build Tool → produces the .mtar archive
cf deploy <app>.mtar # MultiApps plugin ships it
```

`mbt` is **not** a cf plugin; it is a separate binary. Building and deploying are separate steps
with separate failure modes — a build failure is `mbt`'s, a deployment failure is the deploy service's
and shows up in `cf mta-ops` / `dmol`.

---

## 3. Which CLI for which task

| Task | Tool |
|---|---|
| Create a subaccount or directory | `btp create accounts/subaccount` |
| Assign or list entitlements | `btp assign` / `btp list accounts/entitlement` |
| Manage users and role collections | `btp` — `security` group |
| Enable the Cloud Foundry environment in a subaccount | `btp` — environments |
| Create a service instance via Service Manager | `btp` — `services` group |
| Target an org/space, push an app, read app logs | `cf` |
| Deploy / roll back a multitarget application | `cf` + **MultiApps plugin** |
| Build the `.mtar` | **`mbt`** |

**Rule of thumb:** if it exists *before* there is a runtime — accounts, entitlements, users — it is
`btp`. If it runs *inside* the runtime, it is `cf`.

> **One login covers one global account.** If your S-user reaches several, the interactive login
> lists them all but you select one, and every command then runs in it. To work in more than one at
> the same time, point each shell at its own config file via **`BTP_CLIENTCONFIG`** — see
> [references/btp-cli-reference.md](references/btp-cli-reference.md) §2a. **[V]**

---

## 4. Scripting

Use **`--format json`** and parse it; do not scrape the human-readable table, which is formatted for
reading and can change. **[V]**

```bash
btp --format json list accounts/subaccount | jq -r '.value[] | "\(.subaccountId)  \(.displayName)"'
```

For credentials in automation, see this repo's convention: never interpolate a secret into a command
whose output is captured. `btp login` prompts rather than taking parameters up front **[V]** — which
is good for interactive use and means automation needs a deliberate approach, not an echoed password.

---

## 5. Where the rest lives

| Topic | File |
|---|---|
| Login/targeting detail, entitlements workflow, troubleshooting, the CLI landscape beyond btp/cf | [references/btp-cli-reference.md](references/btp-cli-reference.md) |

## Cross-references

- **`sap-cloud-connector`** — the on-prem ↔ BTP tunnel; the other half of a hybrid landscape.
- **`sap-compliance-docs`** — BTP service entitlements map to Service Description Guides.
- **`sap-software-download`** — where SAP delivers CLI binaries.
- **`sap-db-command-reference`** — the on-premise counterpart to this file.
- **`sap-hana-xsa`** — the `xs` CLI for XS Advanced on on-prem HANA. **Looks like `cf`, different platform.**
- **`sap-support-case`** — raising a BTP case: verify GUIDs from the CLI rather than reusing a stale one, and mind the troubleshooting-key consent gate.

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
| **[BC1]** | *Command Syntax of the btp CLI* — `SAP-docs/btp-cloud-platform`, `docs/50-administration-and-ops/command-syntax-of-the-btp-cli-69606f4.md` | **[V]** — the `ACTION GROUP/OBJECT` grammar, the three groups, `help` placement, the leading-`-` parameter warning |
| **[BC2]** | *Troubleshooting for the btp CLI* — same repo, `troubleshooting-for-the-btp-cli-4023e15.md` | **[V]** — `--sso` for Universal ID, CA errors, client/server split, `--verbose` |
| **[BC3]** | *Install the MultiApps CLI Plugin in the Cloud Foundry Environment* — same repo, `install-the-multiapps-cli-plugin…-27f3af3.md` | **[V]** — the `MtaPlugin` name-clash error verbatim, cf 6.40+ prerequisite |
| **[BC4]** | *Multitarget Application Commands for the Cloud Foundry Environment* — same repo, `…-65ddb1b.md` (2,074 lines) | **[V]** — the full MTA command set |
| **[BC5]** | *Download and Start Using the btp CLI Client*; *How to Work with the btp CLI*; *Setting Entitlements Using the btp CLI* | **[G]** |
| **[BC6]** | **btp CLI Command Reference** — `help.sap.com/docs/btp/btp-cli-command-reference/btp-cli-command-reference` | **[G]** — per-command syntax |
| **[BC7]** | **SAP Note 3085908** — logging on with SAP Universal ID | **[G]** |
| **[BC8]** | *Deploy to Cloud Foundry* (CAP / capire); `SAP-samples/cf-mta-examples`; Cloud MTA Build Tool | **[G]** |

> **Why raw markdown, not help.sap.com.** The Help Portal renders through JavaScript and returns an
> empty shell to a plain fetch. SAP publishes the same content as markdown in
> **`SAP-docs/btp-cloud-platform`**, which is what was read here. Same text, retrievable — a useful
> trick for any BTP documentation.

> **Currency.** The btp CLI gains most new function **server-side**, so command availability can
> change without a client update. Verify with `btp --help` on the actual client before assuming a
> command is missing, and check the Command Reference **[BC6]** for current syntax.
