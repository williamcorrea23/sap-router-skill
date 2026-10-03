# ASE HADR — operations

Companion to the parent skill. Failover, the Fault Manager's decision boundary, post-failover data
loss handling, and monitoring. Source: *SAP ASE HADR Users Guide* 16.0 **SP04** **[V]** unless marked.

---

## 1. Planned failover

```
# connect to the primary or companion RMA, then:
sap_failover <primary>,<companion>,<deactivation_timeout_seconds>

# example from the guide — 60-second deactivation timeout:
sap_failover SFHADR1,SJHADR2,60
```

The timeout is the bound on the **Deactivating** internal state (see parent §3): how long the system
waits for unprivileged transactions to finish gracefully before rolling back to Active or advancing
to Inactive. **[V]**

Use `sap_failover_drain_to_er` instead when external replication is configured and must be drained
first.

---

## 2. Unplanned failover — where the Fault Manager stops and you start

This is the most important boundary in the whole feature, and it is easy to over-trust. **[V]**

**If the Fault Manager is configured**, it handles primary ASE failure and triggers automatic
failover **only when it is safe to do so**:

> **If the Fault Manager detects potential data loss when failover is triggered, it does not proceed.
> You must manually intervene** — either restore the old primary site, **or accept the data loss** and
> promote the companion as the new primary. **[V]**

So automatic failover is not a guarantee of automatic recovery. A stalled failover with an alert is
the Fault Manager working correctly, not failing.

**If failover itself fails partway:**

| When it fails | What happens |
|---|---|
| **Before** the new primary is activated | **RMA attempts to set the old primary back to primary** automatically |
| **After** that point | **Manual recovery required**: activate the new primary, start Replication Agent on it, then run `sap_host_available` there once the new standby is running |

---

## 3. After an unplanned failover — managing data loss

**First question: was the path synchronous at the moment of failure?** That determines whether data
loss is even possible. **[V]**

```
sap_status path
```

If the replication path was in the **synchronous** replication state at failure time, zero data loss
applies. If it was asynchronous — or had dropped out of synchronous — assume in-flight loss and
quantify before promoting.

Also review the **Fault Manager alerts** as part of post-failover checks. **[V]**

> A healthy-looking status on both nodes does **not** by itself mean the system is sound — the guide
> documents a troubleshooting symptom where "the status of the primary and companion HADR nodes is
> healthy, but the sanity report" still flags a problem. **[V]** Check the sanity report too.

---

## 4. Monitoring

| Command | Answers |
|---|---|
| `sap_status path` | **Start here.** Is the HADR path healthy, is a given database actually in replication, and what synchronization state is it in |
| `sap_status active_path` | Which path is currently active |
| `sap_status route` | Route status |
| `sap_status resource` | Resource status |
| `sap_status spq_agent` | SPQ Agent status (external replication) |
| `sap_status synchronization` | Synchronization detail |
| `sap_status task` | Task progress — e.g. determining when `Materialize` has completed |

**SAP ASE Cockpit** also manages and monitors the HADR system (guide §8.6). **[G]**

For **health evaluation** of the cluster as a whole, the guide has a dedicated section (§8.15
*Evaluating the Health of an HADR Cluster*). **[G]**

---

## 5. Database-level operations

| Task | Command |
|---|---|
| Add a database after installation | `sap_enable_replication` (guide §8.3 covers the command-line path) |
| Materialize / rematerialize | `sap_materialize`; track with `sap_status task` |
| Suspend / resume / enable / disable | guide §8.7 |
| Load from an external dump | guide §8.4 — see also `sap-backup-recovery` |
| Start / stop the HADR system | guide §8.8 |
| Remove the configuration entirely | `sap_teardown` |

---

## 6. Read-only companion

The guide documents **read-only support from the companion node** (§8.16) **[G]** — the ASE analogue
of HANA's Active/Active (read enabled). Confirm licensing before offering it to a customer, the same
way `logreplay_readaccess` needs an add-on licence on HANA.

---

## 7. Rolling upgrade

`sap_upgrade_server` supports rolling upgrade (guide §3.6 / §4.8). There is also a documented path
for **upgrading SAP ASE 15.7 DR to 16.0 HADR** (§3.7 / §4.9) — note that 15.7 "DR" is the older
mechanism, so this is a migration between technologies, not a version bump. **[G]**

---

## 8. Security

| Topic | Section |
|---|---|
| Enabling SSL for the HADR system | §5.1 |
| SSL for external replication | §5.2 |
| Fault Manager in an SSL-enabled environment | §5.3 |
| Encrypting databases under HADR | §5.4 — cross-check `sap-backup-recovery` on key handling |

All **[G]** — located but not read in full.

> **LDAP cannot be the network security mechanism inside HADR**, and **Kerberos is supported in
> stream replication but not in HADR**. Both are in the parent skill's unsupported list. **[V]**
