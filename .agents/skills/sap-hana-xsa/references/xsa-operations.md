# XSA — troubleshooting and operations

Companion to the parent skill. **[V]** from **SAP Note 2596466** v74 unless marked **[G]**.

---

## 1. The triage order

```bash
# as <sid>adm on the HANA host — works when the API does not
XSA diagnose                 # 1. known config issues + recommended fixes + certificate warnings
XSA list-tenants             # 2. which DBs XSA uses; which holds the platform persistence
XSA du                       # 3. disk consumed by apps and file-system services
XSA collect-traces           # 4. bundle ALL system traces — do this BEFORE opening a case
```

Only once the platform is reachable:

```bash
xs-admin-login               # as XSA_ADMIN, from the host
xs apps                      # what is running / crashed / stopped
xs logs <app> --recent
xs ps                        # PIDs of app instances in the space
xs traces / xs enable-trace  # component tracing
```

> **`XSA diagnose` before `xs` anything.** If XSA itself is misconfigured, every `xs` command fails
> with a connection error that tells you nothing about the cause.

---

## 2. Startup failures — the known-issue Notes

`xscontroller` not starting is the most common XSA incident. SAP documents specific causes **[G]**:

| Symptom | Note |
|---|---|
| `xscontroller` not starting in multi-host and/or additional installations | **2601631** |
| `xscontroller` does not start due to **invalid FQDN** | **2673550** |
| `XSController` fails after **renaming a tenant** — `JDBCDriverException — database does not exist` | **2650790** |
| `SSFS-1670: Update of the secure storage is locked by user …` | **2617735** |
| `SQLInvalidAuthorizationSpecException` — authentication failed | **2451953**, **2611608** |
| `Received shutdown request via signal TERM 15` | **2651225** |
| XSA fails to start — **`No space left on device`** | **3061944** |
| XSA or HANA cockpit installation fails due to **OS resources** | **2482144** |
| `auditlog-db`, `component-registry-db`, `jobscheduler-db` do not start after install | **2640407** |

**Renaming a tenant registered for XSA requires `XSA restart` afterwards** — and is only supported
from **XSA 1.0.82**. **[V]**

---

## 3. Upgrade and downgrade

**Upgrade failures** **[G]**:

| Symptom | Note |
|---|---|
| *"Cannot resume failed upgrade"* | **2607706** |
| *"Service `product-installer-database` already exists, but is bound to application(s)…"* | **2458406** |
| `java.lang.RuntimeException: Execution of command 'mtas' failed` | **2707416** |
| *"Unable to map tenant: org \[name\] not found"* | **2713737** |
| Timeout caused by **large log files** | **2607727** |
| Installation timeout | **2588921** |

**The execution-agent lock** — a documented workaround worth knowing **[V]**:

```
FAILED to start SAP XS Execution Agent: Execution agent process with pid <pid> is still
running on same path /hana/shared/.../xs/app_working/...
com.sap.xs2rt.utils.ExclusivePathException: ...
```

Log in as `<sid>adm`, `kill -9 <pid>` using the PID from the message, then re-run the update. **[V]**

**Downgrade** is possible but only if you planned for it **[V]**:

1. **Back up all XSA content *before* the update** (*Performing a Backup of XS Advanced*).
2. Uninstall XSA (SAP Note **2520710**).
3. Install the previous version.
4. Restore from the backup image.

> Step 1 is the one that gets skipped. Without a pre-update XSA backup there is no clean route back.

**Update strategy** **[V]**: XSA ships a feature release with each HANA SPS, plus irregular patch
releases. It is **backwards compatible with HANA back to 1.0 SPS12**, and **upgrading XSA does not
require a HANA upgrade** — though a given HANA version may impose a *minimum* XSA version
(Note 2422421). For regular patching use the **XS Advanced Collection** (Note 2711421).

---

## 4. Logs and traces

| What | Where |
|---|---|
| **System traces** | *Logging and Auditing in XS Advanced*, HANA Administration Guide **[G]** |
| **Bundle for support** | **`XSA collect-traces`** **[V]** |
| **Application logs** | `xs logs <app>`; *Displaying Application Information* **[G]** |
| **Central log server** | Syslog drain services — *Maintaining Services in XS Advanced* **[G]** |
| **Platform Router logs** | SAP Note **2488170** **[G]** |
| **Startup-issue collection** | SAP Note **2462741** **[G]** |
| **Huge logs in `executionroot`** | SAP Note **2775467** **[G]** — see also `sap-space-reclaim` |

**Support user:** on XSA **< 1.0.82** the `SYSTEM` user can read internal XSA schemas; on **≥ 1.0.82**
privileges must be granted explicitly — SAP Note **2656132**. **[V]**

---

## 5. Installation-time choices to get right

| Choice | Why it matters |
|---|---|
| **Routing mode** | **Cannot be changed later.** Hostname routing recommended for production; needs wildcard DNS |
| **Default domain** | Changeable later, but a DNS-visible decision |
| **Port ranges** | Only if installing **multiple XSA systems on one host** — must be disjoint (Note **2507070**). SAP recommends **one HANA+XSA system per host** |
| **System vs tenant DB** | Determines whether XSA data can be backed up separately, and whether deleting a tenant destroys XSA |
| **App working path** | Disk performance drives deployment/startup speed; ≥100 GB, ≥500 GB for busy dev systems |
| **`global_allocation_limit`** | XSA is outside HANA memory management — must leave room |
| **OS users / sudoers** | Restricted OS users isolate app processes from DB processes (Note **2243156**); custom space users need sudoers maintenance |

---

## 6. Tenant databases

```bash
XSA list-tenants                     # includes "XS advanced platform persistence: YES"
xs create-tenant-database <name>     # creates AND registers for XSA
xs map-tenant-database / unmap-tenant-database
xs tenant-database-mappings
```

**Rules** **[V]**:

- Registering a tenant lets applications use it as persistence.
- **All registered tenants must be backed up and recovered — or moved — together.** Individually is
  not possible.
- A registered tenant **can** be cloned within the same HANA system, but the clone **cannot also be
  registered** alongside the original.
- System copy / refresh with XSA: SAP Note **3445668** **[G]**.
- Migrating XSA between system DB and tenant DB: SAP Note **2767842** **[G]**.

---

## 7. Monitoring

- **SAP Solution Manager** can monitor XSA applications — see *SAP HANA XSA System Monitoring setup*
  **[G]**.
- **`XSA diagnose`** doubles as a lightweight health check; running it on a schedule surfaces
  certificate expiry before it becomes an outage.
- Node.js runtimes inside XSA follow their **own maintenance intervals** (SAP Note **2955324**)
  **[G]** — plan version adoption separately from the platform.
