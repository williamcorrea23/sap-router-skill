---
name: sap-software-download
description: >-
  Find, qualify and download SAP software from the SAP for Me Software Center — Support
  Packages, kernel and patches, installation media, add-ons — and build a correct SP import
  queue. Resolves a component (e.g. "ST-PI 740") to exact filenames, object keys, sizes, SHA-256
  checksums, the required SPAM/SAINT level and the EPS .PAT name via the Software Center's OData
  service, then covers where files go and how to verify them. Downloads are scriptable with
  X.509 client-certificate auth. For add-ons it walks the INSTALLATION vs EXCHANGE-UPGRADE tree.
  Use for "download a support package", "which SP is latest", "get the kernel SAR", "SP queue
  from SP28 to latest", "software center", "automate SAP downloads", "SAPCAR extract", "EPS/in",
  "SAINT installation package".
---

# SAP Software Download (SAP for Me Software Center)

Getting the *right* file is most of this job. A Basis download is only correct when four things line up:
the **component + release**, the **patch/SP level**, the **platform** (OS + DB + Unicode, for kernel), and
the **prerequisites** (SPAM/SAINT level, minimum SAP_BASIS, mandatory co-imports). This skill resolves all
four before anything is fetched.

> **Guardrail — the whole workflow is automatable, with the right credential.**
> - Search, metadata **and the file download itself** work end-to-end without a browser, using
>   **X.509 client-certificate authentication** (§5). Verified: 7 support packages fetched unattended,
>   all SHA-256 verified against the service. **[V]**
> - **Authentication method decides everything.** A *browser session* download redirects into interactive
>   SAML and needs a human (the account picker alone blocks it). A *client certificate* completes the same
>   SAML chain non-interactively. Same URL, different outcome — see §5.
> - **Never guess a filename or an SP level.** Resolve it from the service (§2) and quote the object key.
> - **Verify the SHA-256 before importing, always** (§5). The service publishes it; there is no excuse for
>   discovering a truncated `.SAR` during `IMPORT_PROPER`.
> - **Check the component's release-strategy Note and known-issue Notes before building a queue** (§4) —
>   locked packages and mandatory co-imports are announced there, not in the file list.
> - **Add-ons: identify the delivery type, and download both** (§2a). INSTALLATION (SAINT) and
>   EXCHANGE-UPGRADE are near-identical in size and both valid archives — nothing but the tree node you
>   descended tells them apart.

Verification legend: **[V]** verified against the live service during authoring · **[G]** cited to the
official guide/Note.

---

## 1. Where the Software Center actually lives

`https://me.sap.com/softwarecenter` is a **shell that embeds `launchpad.support.sap.com` in an iframe**.
The UI has three tabs — *Installations & Upgrades*, *Support Packages & Patches*, *Databases* — but all of
them are driven by one OData service: **[V]**

```
https://launchpad.support.sap.com/services/odata/svt/swdcuisrv/
```

Practical consequences:

- Browser automation pointed at the **top frame sees nothing** — the accessibility tree, the network log
  and page JS are all scoped to the shell, not the Software Center. Query the **service** instead.
- Every downloadable object has one identifier — the **`Fastkey` / `ObjectKey`**, a 19-digit number. It is
  the key to both URLs you care about: **[V]**

| Purpose | URL pattern |
|---|---|
| Direct download | `https://softwaredownloads.sap.com/file/<ObjectKey>` |
| Object info page | `https://me.sap.com/softwarecenter/object/<ObjectKey>` |

- Unlike the SAP Notes `CorrInsSet` service, **`$format=json` works here** — no need to strip it.
  (See [sap-security-patch](../sap-security-patch/SKILL.md) for the Notes-side quirk.)

Full endpoint reference, entity sets and field lists: **[references/software-center-api.md](references/software-center-api.md)**

---

## 2. Resolve a component to real files (read-only)

Run these either from a browser tab **on the `launchpad.support.sap.com` origin** (so the session cookie
applies — the shell's own origin will not work, see §1), or headless with **client-certificate auth** (§5).

**Search** — `SEARCH_STRING` takes what you'd type in the UI: **[V]**

```
GET /services/odata/svt/swdcuisrv/SearchResultSet
      ?SEARCH_STRING=ST-PI%20740
      &SEARCH_MAX_RESULT=200&RESULT_PER_PAGE=200&$format=json
```

Each hit gives `Title` (the filename, e.g. `SAPK-74035INSTPI`), `Description` (`ST-PI 740: SP 0035`),
`Infotype` (`Support Package` / `Installation Software Component` / …), `Fastkey`, and
`DownloadDirectLink`.

> ⚠️ **Filter by name pattern, not by result count.** A search for `ST-PI 740` returns **60** rows, but only
> **35** are the mainline SP stack `SAPK-740NNINSTPI`. The rest are differently-scoped deliveries that share
> the component name (e.g. `SAPK74000NCPSTPI`, *Business Transformation Center*). Importing the wrong family
> is a real and easy mistake. **[V]**

> 🚨 **For add-ons, search returns almost no files — it returns *navigation nodes*.** A search for
> `ST-A/PI` returns **57 rows of which only 3 are downloadable**; the other 54 are nodes with an **empty
> `Fastkey`**. A search for `ST-A/PI 01X_731` returns **two rows, identical `Title`, zero files** —
> differing only by `Infotype`. Taking "the file from the search result" for an add-on is how you end up
> with the wrong delivery type. Descend properly — §2a. **[V]**

**Qualify** — the search row does not tell you whether you can actually use the file. `ObjectSet` does: **[V]**

```
GET /services/odata/svt/swdcuisrv/ObjectSet('0010000000343432026')?$format=json
```

| Field | Why a Basis admin cares |
|---|---|
| `Status` / `StatusDescr` | `AVAILABLE` vs **locked**. Locked packages exist — see §4. |
| `FileName`, `FileType`, `FileSize` | Exact filename; `SAR`; size in **KB**. |
| `Checksum` | **SHA-256** — verify after download (§5). |
| `RequiredSpamVersion` | **The prerequisite that ruins change windows.** Update SPAM/SAINT *first*. |
| `MinimalBasisRelease` | Minimum SAP_BASIS for this package. |
| `PackageLevel` | Zero-padded SP level (`0035`). |
| `EpsFileName` | The `.PAT` name it becomes in `EPS/in` — what SPAM actually lists. |
| `PatchType` | e.g. `CSP` (component support package). |

Two navigation properties matter: **[V]**

- `ObjectSet('<key>')/ObjectAttributes` — includes **`EQUIVALENT`** entries mapping this SP to the same fix
  on other releases (e.g. ST-PI 740 SP35 ≡ ST-PI 758 SP02). Use this when the landscape is mixed-release.
- `ObjectSet('<key>')/ObjectConditions` — the import conditions (software component, release, package
  category, alternative set) that SPAM enforces.

Confirm you're even allowed to download: `DownloadAuthProfileSet` returns your S-user with `Active: true`.
If `Active` is false, it's an authorization problem, not a technical one. **[V]**

---

## 2a. Add-ons: INSTALLATION vs EXCHANGE-UPGRADE — get **both**

Add-ons (ST-A/PI, ST-PI, and friends) are not published as a flat file list. They sit behind a two-level
tree, and **each level splits into two variants that look almost identical**. Pick the wrong branch and you
get a file that is the right size, the right component and the wrong thing.

**Level 1 — `Infotype`, carried in `SubtreeEvent` as `V=`:** **[V]**

| `Infotype` | `V=` | Meaning |
|---|---|---|
| Installation Software Component | `INST` | fresh installs and upgrades |
| Maintenance Software Component | `MAINT` | maintenance deliveries |

(*Archive View* variants of both exist for older releases.)

**Level 2 — the delivery type, carried in `ListEvent` as `SWTYPSC=`:** **[V]**

| Child node | `SWTYPSC=` | What it is |
|---|---|---|
| **INSTALLATION** | `N` | the **SAINT installation package** — installing the add-on |
| **EXCHANGE-UPGRADE** | `X` | the **exchange/update package** — moving an existing add-on up |

> 🚨 **Download both, every time.** Which one applies depends on whether the target system already has the
> add-on at a lower level, and you often cannot confirm that until SAINT/SPAM tells you. Having the wrong
> one at the change window means a second download round-trip under time pressure. Both together are
> usually a modest download; the delay is not.
>
> **The sizes will not save you.** For ST-A/PI 01X_731 the two files are **77,646,332** and **77,643,960**
> bytes — **0.003 % apart**. Both are valid `CAR 2.01` archives. Nothing about the size, type or checksum
> tells you that you fetched the wrong *kind*. Only the node you descended through does. **[V]**

### Walking the tree

Search gives you a node whose `SubtreeEvent` holds the parameters; **pass that raw event string as the
query string** to `HierarchyItemSet` (it is not an OData `$filter` — filtering on `Id` returns 0 rows), then
pass the child's `ListEvent` to **`DownloadItemSet`**: **[V]**

```
# 1. node → children (INSTALLATION / EXCHANGE-UPGRADE)
GET /services/odata/svt/swdcuisrv/HierarchyItemSet
      ?_EVENT=DISPHIER&EVENT=TREE&NE=NAVIGATE&ENR=<ENR>&V=INST&TA=ACTUAL&$format=json

# 2. child → files.  SWTYPSC=N installation | SWTYPSC=X exchange-upgrade
GET /services/odata/svt/swdcuisrv/DownloadItemSet
      ?_EVENT=LIST&EVENT=LIST&ENR=<ENR>&SWTYPSC=N&PECCLSC=NONE&V=INST&TA=ACTUAL&$format=json

# 3. file → full metadata (checksum, SPAM level, status)
GET /services/odata/svt/swdcuisrv/ObjectSet('<Fastkey>')?$format=json
```

`ENR` is the software-component-release number, taken from the search row's `SubtreeEvent`. Note
`DownloadItemSet` — **not** `ObjectListItemSet`, which returns 0 rows for these events. **[V]**

**Worked example — ST-A/PI 01X_731** (`ENR=73555000100200023403`), both fetched and SHA-256 verified: **[V]**

| Delivery type | `SWTYPSC` | Title | Fastkey | Bytes |
|---|---|---|---|---|
| **INSTALLATION** (SAINT) | `N` | `SAPKITABCA` | `0010000000965332025` | 77,646,332 |
| **EXCHANGE-UPGRADE** | `X` | `SAPK-01XCAINSSA` | `0010000001017592025` | 77,643,960 |

Both require **SPAM/SAINT 0020**. Note the naming gives a hint once you know to look — `SAPK-…INSSA`
carries the exchange/update marker — but do not rely on filename shape across components; rely on the node.

---

## 3. Build the SP queue (the common real task)

Going from an installed level to a target is **not** "download the latest one". SPAM imports a **queue**, and
you generally need every SP between current and target.

1. **Read the installed level** — SAP GUI `System → Status → Component information`, or table `CVERS`. [G]
2. **List candidates** and filter to the mainline family (§2).
3. **Take the whole span** — installed+1 … target.
4. **Take the max `RequiredSpamVersion` across the span**, not of the last package — and update SPAM/SAINT
   before starting. [G, SPAM1]
5. **Check known-issue Notes for that span** (§4) before committing to the list.

**Worked example — ST-PI 740, installed SP28 → latest.** Resolved live: **[V]**

| SP | File | ObjectKey | Bytes (measured) | SPAM |
|---|---|---|---|---|
| 0029 | `SAPK-74029INSTPI` | `0010000000024712025` | 19,280,927 | 0081 |
| 0030 | `SAPK-74030INSTPI` | `0010000000213932025` | 5,393,658 | 0081 |
| 0031 | `SAPK-74031INSTPI` | `0010000000642592025` | 7,334,387 | 0081 |
| 0032 | `SAPK-74032INSTPI` | `0010000000952762025` | 2,875,877 | 0081 |
| 0033 | `SAPK-74033INSTPI` | `0010000001271602025` | 6,696,119 | 0081 |
| 0034 | `SAPK-74034INSTPI` | `0010000000129182026` | 5,412,413 | 0081 |
| 0035 | `SAPK-74035INSTPI` | `0010000000343432026` | 11,923,989 | 0081 |

All seven `AVAILABLE`; **58,917,370 bytes** total; all requiring **SPAM/SAINT 0081**. Downloaded unattended
via certificate auth and **every SHA-256 matched `ObjectSet.Checksum`**. **[V]**

Note the `ObjectSet.FileSize` field is KB and rounds — SP29 reports `18830` KB against 19,280,927 actual
bytes. Use it for planning, use `Checksum` for verification.

---

## 4. Check the component's Notes *before* downloading

The file list will not tell you a package was withdrawn, relocked, or must be co-imported. The Notes will.
Two searches, every time:

- **Release strategy for the add-on/component** — e.g. **SAP Note 539977** *Release strategy for add-on
  ST-PI*. [G, ST1]
- **Known issues for the specific SP** — search the exact SP designation.

**Why this is not optional — the same ST-PI 740 example.** **SAP Note 3570638** (*ST-PI 740 SP29 not
downloadable*) records that SP29 shipped with an inadvertent dependency on SAP_BASIS 740 SP08+, causing DDIC
activation errors on older SAP_BASIS levels, and was **locked**. It was corrected in SP30 and re-released, and
now: **[V, ST2]**

> **SP29 and SP30 can only be imported in the same import queue** — enforced by SUM/SPAM and package import
> conditions. Systems that already imported SP29 successfully can import SP30 on top; anyone who hit DDIC
> activation errors follows **SAP Note 3574464** for the manual correction. [G, ST2]

A queue built purely from the file list would look identical whether or not you knew this. The Note is what
tells you SP29 cannot travel alone.

---

## 5. Download, verify, stage

### Download

The URL is always `https://softwaredownloads.sap.com/file/<ObjectKey>`. What differs is **how you
authenticate**, and that decides whether a human is required.

| Credential | Behaviour | Use for |
|---|---|---|
| **Browser session** (cookies) | Redirects into interactive SAML; an account picker appears when one e-mail maps to several S-users. **Needs a human.** | Ad-hoc, one file |
| **X.509 client certificate** | Completes the same SAML chain **non-interactively**. | Automation, bulk, CI |
| Download Basket + SAP Download Manager | SAP's own multi-file tool; resumable | Very large media sets |

**The certificate path, verified end to end.** Download an SAP passport / support certificate for your
S-user, then present it. The chain is three hops and needs nothing but a cookie jar: **[V]**

1. `GET /file/<key>` → 302 to `origin-az.softwaredownloads.sap.com/tokengen/?file=<key>`, which returns an
   HTML **auto-POST form** carrying `SAMLRequest` + `RelayState`.
2. **POST those to `https://accounts.sap.com/saml2/idp/sso`.** With the certificate the IdP authenticates
   silently and returns a second auto-POST form containing `SAMLResponse` — *and a `downloadId`* appended
   to the form action.
3. **POST that back to the `tokengen` action.** The response is the file:
   `Content-Type: application/octet-stream`.

```bash
# curl needs the cert in a config file (0600) so the passphrase never hits the process list
umask 077
printf 'cert-type = "P12"\ncert = "%s:%s"\n' "$PFX_PATH" "$PFX_PASS" > ~/.sapdl.cfg
curl -K ~/.sapdl.cfg -sSL -c jar.txt -b jar.txt \
     -o SAPK-74035INSTPI.SAR \
     'https://softwaredownloads.sap.com/file/0010000000343432026'
```

`curl -L` alone is not enough — it follows redirects but **does not submit HTML forms**, so you must parse
each form's `action` + `input` fields and re-POST them (2 hops). Any HTTP client works; the auth is the
only hard part.

> The **OData service in §2 accepts the same certificate**, so search → qualify → download → verify runs
> with no browser anywhere in the loop. **[V]**

**Sanity-check what you got.** A valid SAPCAR archive starts with the magic string `CAR 2.01`, and contains
one or more `EPS/in/*.PAT` entries. Note *one or more* — `EpsFileName` from the service names one PAT, but
archives can carry several (ST-PI 740 SP30 and SP33 each contain two). **[V]**

### Verify the checksum — always, and per OS

Compare against `Checksum` from `ObjectSet` (SHA-256):

```bash
# Linux
sha256sum SAPK-74035INSTPI.SAR
```
```bash
# AIX  (openssl is the portable choice; csum -h SHA256 also exists on newer AIX)
openssl dgst -sha256 SAPK-74035INSTPI.SAR
```
```powershell
# Windows
certutil -hashfile SAPK-74035INSTPI.SAR SHA256
```

A size/checksum mismatch means a truncated or proxy-mangled transfer — re-download rather than discovering
it during the import.

### Stage for SPAM

ABAP Support Packages are staged in the transport directory's EPS inbox, then loaded by SPAM: [G, SPAM2]

| OS | EPS inbox |
|---|---|
| Linux / AIX | `/usr/sap/trans/EPS/in` |
| Windows | `\\<SAPTRANSHOST>\sapmnt\trans\EPS\in` |

```bash
# as <sid>adm — extract the .PAT into EPS/in
SAPCAR -xvf SAPK-74035INSTPI.SAR -R /usr/sap/trans/EPS/in
```

Then in SPAM: **Support Package → Load packages → From Application Server**, define the queue, import.
Ownership matters — files must be readable by `<sid>adm`; root-owned files in `EPS/in` are a classic
"SPAM can't see the package" cause. See [sap-transport-mgmt](../sap-transport-mgmt/SKILL.md) for the
transport directory layout and [sap-kernel-patch](../sap-kernel-patch/SKILL.md) for kernel `.SAR` handling.

---

## OS note

Finding and qualifying software is **OS-independent** — same service, same object keys. The OS matters at
three points only: the **checksum command** (§5), the **EPS/transport path** (§5), and — for **kernel**
downloads specifically — choosing the right platform build (Linux x86_64 / ppc64le, Windows x64, AIX
ppc64), which [sap-kernel-patch](../sap-kernel-patch/SKILL.md) covers.

---

## Cross-references

- **`sap-kernel-patch`** — what to do with the kernel archives once downloaded; SP Stack Kernel vs hotfix.
- **`sap-security-patch`** — the monthly Notes workflow that drives most download decisions.
- **`sap-compliance-docs`** — entitlement and the Service Description Guide behind what you may download.
- **`sap-sscr-keys`** — the sibling SAP for Me OData service, same authentication chain.

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

- **[SC1]** SAP for Me **Software Center** — `https://me.sap.com/softwarecenter`; embeds
  `launchpad.support.sap.com`. Backing OData service `/services/odata/svt/swdcuisrv/` (namespace
  `SVT_SWDC_UI_SRV`). Entity sets, field lists and the `Fastkey`→URL mapping **verified live against the
  service during authoring**, signed in as an S-user with an active download profile. **[V]**
  See [references/software-center-api.md](references/software-center-api.md).
- **[SC2]** Download endpoint `https://softwaredownloads.sap.com/file/<ObjectKey>` — SP-initiated SAML via
  `origin-az.softwaredownloads.sap.com/tokengen/` → `accounts.sap.com/saml2/idp/sso` → back to `tokengen`
  with an IdP-minted `downloadId`. **Verified end to end with X.509 client-certificate auth**: 7 ST-PI 740
  support packages (SP29–SP35) downloaded unattended, 58,917,370 bytes, **every SHA-256 matching
  `ObjectSet.Checksum`**, each a valid `CAR 2.01` archive. With browser-session cookies the same URL needs a
  human. Object info page `https://me.sap.com/softwarecenter/object/<ObjectKey>`. **[V]**
- **[SC4]** Add-on tree navigation — `SearchResultSet` returns navigation nodes (empty `Fastkey`,
  populated `SubtreeEvent`) as well as files; `V=INST`/`V=MAINT` selects the `Infotype`, and
  `SWTYPSC=N`/`SWTYPSC=X` selects **INSTALLATION** vs **EXCHANGE-UPGRADE**. Events are raw query strings,
  consumed by `HierarchyItemSet` then `DownloadItemSet` (**not** `ObjectListItemSet`, which returns 0 rows).
  **Verified live on ST-A/PI 01X_731** (`ENR=73555000100200023403`): `SAPKITABCA` (installation,
  77,646,332 B) and `SAPK-01XCAINSSA` (exchange-upgrade, 77,643,960 B), both downloaded and SHA-256
  verified, both valid `CAR 2.01`, both requiring SPAM/SAINT 0020. **[V]**
- **[SC5]** Correction of record: revisions before 0.6.0 documented only the "filter by filename pattern"
  trap, which does not help for add-ons — their search results contain **almost no files at all**. Reported
  from the field after an ST-A/PI 01X_731 download produced the EXCHANGE-UPGRADE package where the
  INSTALLATION (SAINT) package was wanted. The two are 0.003 % apart in size, so nothing downstream catches
  it. Guidance is now: identify the delivery type explicitly, and **fetch both**. **[V]**
- **[SC3]** Correction of record: an earlier revision of this skill stated the download "does not complete
  under automation". That was generalised from a single surface (a browser extension driving a cookie
  session) and is **wrong** — the credential, not the automation, is what gates it. Certificate auth
  completes the chain non-interactively. **[V]**
- **[ST1]** **SAP Note 539977** — *Release strategy for add-on ST-PI* (BC-UPG-ADDON). The component's
  release-strategy Note is the first thing to read before planning any add-on SP queue.
  https://me.sap.com/notes/539977
- **[ST2]** **SAP Note 3570638** — *ST-PI 740 SP29 not downloadable* (BC-UPG-ADDON, Program error, v4,
  released 2025-03-10). **[V]** Retrieved via the SAP Notes MCP during authoring. Records the SAP_BASIS
  740 SP08+ dependency, the lock, and — after correction in SP30 — that *"LM-tools (SUM & SPAM) and package
  import conditions ensure that ST-PI 740 SP29 and SP30 can only be imported in the same import queue."*
  Manual correction for systems that already hit DDIC activation errors: **SAP Note 3574464**.
  https://me.sap.com/notes/3570638
- **[SPAM1]** **SAP Note 1913676** — *IMPORT_PROPER: Troubleshooting guide for Support Package / Add-On
  installation errors during the main import in SPAM or SAINT* (BC-UPG-OCS-SPA). **[V]** Located via the
  SAP Notes MCP. The reference for import-phase failures.
  https://me.sap.com/notes/1913676
- **[SPAM2]** *Support Package Manager (SPAM)* — loading packages from the application server via the
  transport directory EPS inbox (`/usr/sap/trans/EPS/in`), and `SAPCAR -xvf … -R <dir>` to extract the
  `.PAT`. SAP Software Logistics documentation, help.sap.com. [G]
- **[SPAM3]** **SAP Note 822379** — *Known problems with support packages in SAP NW 7.0x AS ABAP*
  (BC-UPG-OCS). https://me.sap.com/notes/822379

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID):
the **release-strategy Note for the component you are downloading**, any **known-issue Note naming the exact
SP** in your queue, and **SAP Note 1913676** if an import fails. Notes are where withdrawals, locks and
mandatory co-imports are published — the file list never shows them.
