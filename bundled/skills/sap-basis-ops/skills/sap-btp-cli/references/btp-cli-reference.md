# BTP CLI — login, workflow, troubleshooting, and the wider CLI landscape

Companion to the parent skill. **[V]** = read directly from SAP's published docs
(`SAP-docs/btp-cloud-platform`); **[G]** = cited but not read in full.

---

## 1. Login — and the client/server split that explains version behaviour

```bash
btp login          # prompts; confirm the proposed server URL
btp login --sso    # REQUIRED for SAP Universal ID
```

> **SAP Universal ID needs `--sso`.** *"To log on with SAP Universal ID, you need to use the `--sso`
> parameter. Otherwise log on with the password associated with your account."* **[V]** See SAP Note
> **3085908**. This is the single most common login confusion.

**Recommended form is `btp login --sso` or `btp login` with no parameters**, then confirm the
proposed server URL. **[V]**

**A connection error usually means certificates, not credentials.** *"If you get an error message
about connecting to the server, you should update your root CA or install the custom CA for the login
URL."* **[V]** Do not start rotating passwords over a connection error.

### The client is thin — most functionality lives server-side

> *"Most new functionality is added via the CLI server, so no update [of the client] is required."*
> **[V]**

```bash
btp --info     # which client version am I on
btp --help     # overview of all commands
```

**But:** *"If new commands are available but cannot be used with your client version"* you do need to
update. **[V]** So the diagnostic order is: does `btp --help` list the command? If yes and it fails,
it is not a version problem. If the command is absent, update the client.

---

## 2. Verbose mode is the real diagnostic

Default output is a clean table:

```
btp list security/role-collection
name                            description
Global Account Administrator    Administrative access to the global account
Global Account Viewer           Read-only access to the global account

OK
```

`btp --verbose list security/role-collection` returns *"much more lengthy"* output including client
version and request detail. **[V]** Reach for `--verbose` **before** raising an incident — SAP's own
troubleshooting page positions it as the first step when an error message is not helpful enough.

Note the two flags do different jobs and are easy to confuse:

| Flag | Purpose |
|---|---|
| `--verbose` | Diagnostics — what the client did, request/response detail |
| `--format json` | **Machine-readable output for scripting** |

Use `--format json` in automation; use `--verbose` when something is wrong.

---

## 2a. One login = one global account — and how to run several

> **"Log in with the btp CLI is on global account level."** **[V]**

If your S-user has access to several global accounts, one authentication **surfaces** them all —
*"in the interactive login, after successful authentication, the btp CLI will offer all of your
global accounts so you can select the one to log in to"* **[V]** — but you are logged in to **one**.
*"All commands are executed in this global account, unless you provide a subaccount or directory ID
with the command."* **[V]**

```bash
btp login --subdomain <global-account-subdomain>   # skip the picker
```

The subdomain comes from your operator, or from the global account's page in the cockpit.

### Running several global accounts at once

A login stores a **session token in a local configuration file** **[V]**:

| OS | Default `config.json` |
|---|---|
| Windows | `C:\Users\<username>\AppData\Roaming\SAP\btp\config.json` |
| macOS | `~/Library/Application Support/.btp/config.json` |
| Linux | `~/.config/.btp/config.json` |

Because the session lives in that file, **pointing different shells at different config files gives
you genuinely parallel sessions** — SAP documents exactly this pattern for working in two places at
once **[V]**:

```bash
# terminal A — global account 1
export BTP_CLIENTCONFIG=~/.btp/ga1.json
btp login --subdomain <ga1-subdomain>

# terminal B — global account 2, at the same time
export BTP_CLIENTCONFIG=~/.btp/ga2.json
btp login --subdomain <ga2-subdomain>
```

or per command:

```bash
btp --config ~/.btp/ga1.json login
btp --config ~/.btp/ga1.json list accounts/subaccount
```

> **`BTP_CLIENTCONFIG` was introduced in client version 2.14.** On older clients the variable is
> **`SAPCP_CLIENTCONFIG`**. **[V]**

**Practical shape for five global accounts:** one config file each, and a shell alias or function per
account (`btp-cust-a`, `btp-cust-b`, …) that sets `BTP_CLIENTCONFIG` and calls `btp`. That removes the
single most dangerous BTP-CLI mistake — running a `create`/`delete` against the account you were in
last rather than the one you meant. Confirm with `btp --info` (target and context) before anything
destructive.

**Region caveat:** the CLI server URL is proposed at login (`https://cli.btp.cloud.sap/`, or
`https://cpcli.cf.eu10.hana.ondemand.com` on clients ≤ 2.49.0) **[V]**. If an operator gave you a
different server URL for a particular landscape, that is a `--url` value and belongs in that
account's config too.

---

## 3. Targeting

The btp CLI keeps a **target** (global account / directory / subaccount) so commands do not each need
the ID:

```bash
btp target                                  # show current target
btp target --global-account <subdomain>
btp target --subaccount <subaccount-id>
```

Mis-targeting is a classic cause of "the command worked but nothing changed where I expected" —
confirm `btp target` before any create/assign/delete.

**cf has its own, separate target.** `cf target -o <org> -s <space>` is unrelated to `btp target`.
Both must be right; neither implies the other.

---

## 4. Typical account-setup workflow

Order matters — each step is a prerequisite for the next.

```bash
btp login --sso
btp target --global-account <subdomain>

btp list accounts/available-region            # where can this global account create subaccounts
btp create accounts/subaccount \
     --display-name "PRD" --region <region> --subdomain <unique-subdomain>

btp list accounts/entitlement                 # what the global account holds
btp assign accounts/entitlement \
     --to-subaccount <id> --for-service <service> --plan <plan> --amount <n>

btp create accounts/environment-instance ...  # e.g. enable Cloud Foundry
btp assign security/role-collection "<Role Collection>" --to-user "name@example.com"
```

Then switch to `cf` for anything inside the runtime. Entitlement detail: SAP's *Setting Entitlements
Using the btp CLI* **[G]**.

> **Entitlement before instance.** A service instance cannot be created in a subaccount that has no
> entitlement for that service and plan. "Service not found" at instance-creation time is usually a
> missing *assignment*, not a missing service.

---

## 5. Documented btp CLI topic areas **[G]**

SAP's own doc set is organised roughly as below — useful as a checklist of what the CLI can do:

| Area | Doc |
|---|---|
| Account administration | *Account Administration Using the btp CLI* |
| Global accounts, directories, subaccounts | *Working with Global Accounts, Directories, and Subaccounts* |
| Users and authorizations | *Managing Users and Their Authorizations Using the btp CLI* |
| Entitlements | *Setting Entitlements Using the btp CLI* |
| Environments | *Working with Environments Using the btp CLI* |
| External resource providers | *Working with External Resource Providers* |
| Org management | *Org Management Using the btp CLI* |
| Theme configuration | *Theme Configuration for the btp CLI* |
| Troubleshooting | *Troubleshooting for the btp CLI* |

Full per-command syntax: the **btp CLI Command Reference** on help.sap.com **[G]**.

---

## 6. The wider SAP CLI landscape — what this skill does *not* cover

Named here so the boundary is explicit rather than implied. All **[G]**.

| Tool | Domain | Covered? |
|---|---|---|
| **`btp`**, **`cf`**, **`mbt`**, MultiApps plugin | BTP account + CF runtime + MTA | **This skill** |
| `xs` | **XS Advanced** on on-prem HANA — *superficially similar to `cf`, different platform* | ✅ **`sap-hana-xsa`** |
| `kyma` | Kyma / Kubernetes runtime on BTP | ✗ |
| `cds` | SAP CAP development | ✗ |
| `ui5` | UI5 Tooling | ✗ |
| `fiori` | SAP Fiori tools | ✗ |
| `sapgenpse` | PSE / SNC / SSL certificate management | ✅ **`sap-crypto-pse`** |
| `hdblcm`, `hdbcons` | HANA lifecycle / expert console | ✅ **`sap-hana-lifecycle-tools`** |
| `hdbrsutil` | HANA row-store | ✗ |
| `sapevt`, `sapxpg`, `sapinst` | ABAP event raising, external commands, installation | ✅ **`sap-os-executables`** |

**Covered elsewhere in this repo:** `sapcontrol`, `sapstartsrv`, `R3trans`, `tp`, `SAPCAR`,
`hdbnsutil`, `hdbsql`, `hdbuserstore`, BR\*Tools, `dbmcli`, `isql`, `sqlcmd`, `db2pd`, `db2haicu`,
`niping`, `dpmon`, `jcmon`, `saposcol`, `saprouter`, `sapcpe`.

> **`xs` vs `cf` is a genuine trap — now covered in `sap-hana-xsa`.** The XS Advanced CLI mimics Cloud Foundry's command shape
> (`xs login`, `xs apps`, `xs push`) but administers **XSA on an on-premise HANA system**, not BTP.
> Commands are not interchangeable and the platforms are unrelated. If a landscape has both, be
> explicit about which one a runbook means.
