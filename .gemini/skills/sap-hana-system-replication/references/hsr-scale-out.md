# HSR on scale-out systems

Scale-out changes four things about HSR: **topology must match exactly**, `-sr_state` grows a **host
mapping** section, **node-count changes have an order that inverts** depending on direction, and the
cluster needs a **third site**. Everything in `SKILL.md` and [hsr-operations.md](hsr-operations.md)
still applies — this file only covers what is *different*.

Sources: SR Guide **2.0 SPS 08** **[V]**, SAP Note **1999880** v297 **[V]**, SUSE/Red Hat cluster
documentation **[G]**.

> **A command I named and had to withdraw.** `hdbnsutil -sr_stateHostMapping` does **not** appear in
> the SPS 08 guide — zero occurrences. Host mapping is **output of `-sr_state`**, not a separate verb.
> If you see that command in a blog, check it against your revision before trusting it.

---

## 1. Topology must be identical — this is absolute

> "The topology of primary and secondary site of a system replication scenario must be **identical**."
> **[V, Note 1999880 Q52]**

Consequences:

- **You cannot replicate non-MDC → MDC** (SAP Note 2101244).
- You cannot replicate a 4-node scale-out to a 3-node one.
- Worker/standby layout has to match, not just the host count.

Combined with the scale-up rules, the secondary needs: **same SID, same instance number, same
topology.**

---

## 2. `-sr_state` on scale-out and multitier — read the host mapping

On a multi-host or multitier landscape, `-sr_state` prints which hosts pair with which, per site:

```
$ hdbnsutil -sr_state
mode: primary
site id: 1
site name: SITEA
Host Mappings:
~~~~~~~~~~~~~~
ld2131 -> [SITEA] ld2131
ld2131 -> [SITEC] ld2133
ld2131 -> [SITEB] ld2132
```

**Use `--sapcontrol=1` whenever a script consumes this** — it emits parseable key=value lines
instead of the boxed layout **[V]**:

```
$ hdbnsutil -sr_state --sapcontrol=1
SAPCONTROL-OK: <begin>
mode=primary
site id=1
site name=SITEA
mapping/ld2131=SITEA/ld2131
mapping/ld2131=SITEC/ld2133
mapping/ld2131=SITEB/ld2132
SAPCONTROL-OK: <end>
```

On a **tier-2 secondary** the same command adds two fields **[V]**:

```
mode=sync
site id=2
site name=SITEB
active primary site=1
mapping/ld2132=SITEA/ld2131
mapping/ld2132=SITEB/ld2132
primary masters=ld2131
```

**Field reference** **[V]**:

| Field | Meaning |
|---|---|
| `mode` | `primary`, `sync`, `syncmem` or `async` — **the mode as seen from the host you ran it on**. In multitier, tier 2 may be `sync`/`syncmem` while tier 3 is `async`. |
| `site id` | Unique, incremented per system attached. **Removed when replication is disabled.** |
| `site name` | What you passed to `--name` at enable/register time. |
| `mapping/<currentHost>` | Which hosts participate, with their site name. |
| `active primary site` | Site ID of the currently active primary. |
| `primary masters` | Host names of the **current master candidates** of the primary. |

> ⚠️ **On an offline HANA, no host mapping is shown** — and on secondaries it cannot be shown at all
> when the database is down (SAP Note **2315257**). So an empty Host Mappings block is **not**
> evidence that replication is misconfigured; check whether the database is actually up first. **[V]**

---

## 3. Changing the number of nodes — the order inverts

This is the rule most likely to cost you an unplanned full data shipment. **[V, Note 1999880 Q45]**

**With downtime (simplest):**
1. Stop system replication
2. Adjust the node layout **on the primary first, then the secondary**
3. Register the secondary again

**Without stopping replication — and note the direction flips:**

| Operation | Order |
|---|---|
| **Adding** a node | **Secondary first**, then primary |
| **Removing** a node | **Primary first**, then secondary |

The logic is that the topologies must never diverge in the direction where the primary demands
something the secondary cannot yet provide. Get it backwards and you break the topology-identity rule
in §1 mid-flight.

---

## 4. Initial sync time in scale-out

The scale-up formula still applies per host, but the total is **the maximum of the per-host times,
not the sum** — hosts ship in parallel **[V, Note 1999880 Q25]**:

```
initial sync time  >  backup size × compression factor / available bandwidth     (per host)
scale-out total    =  MAX(per-host times)
```

`datashipping_parallel_channels` (default **4**, secondary-side) matters more here — but throughput is
still capped by primary-side I/O. See [hsr-parameters.md](hsr-parameters.md).

---

## 5. Network speed check

The HANA cockpit exposes two measurement tabs **[V]**:

| Tab | Measures |
|---|---|
| **Network Speed Check (System Replication Communication)** | Host-to-host, primary → secondary (and to a third tier) |
| **Network Speed Check (Internal Communication)** | Every host to every other host **within** the scale-out system, **both directions** — each pair appears twice with Sender/Receiver swapped, fastest first |

Two caveats, both from the guide:

- **Standby hosts cannot be measured.** They have no access to the data and log volumes, so they are
  not relevant for replication in that state — an empty result for a standby is expected, not a fault.
- **Measuring degrades the network while it runs**, affecting the live system. Do not run it casually
  on production during business hours.

---

## 6. Cluster integration on scale-out

See [hsr-cluster-integration.md](hsr-cluster-integration.md) for the hook API and the
SAPHanaSR → SAPHanaSR-angi break. Scale-out adds: **[G — SUSE/Red Hat, not SAP]**

- **A third site is required.** Scale-out clusters need a **majority maker (MM)** node on a third
  site to resolve split brain. An **odd** node count is what makes automatic resolution possible.
- **The majority maker does not run HANA.** It needs no HANA installation and **must not** run any
  SAP HANA resource for the same SID.
- **`SAPHanaController` and `SAPHanaTopology` install on *all* cluster nodes — including the
  majority maker.**
- **The cluster defers to HANA.** It acts only when the HANA landscape status shows HANA cannot
  recover on its own *and* replication is in sync. The documented exception: it reacts when HANA
  **moves the master nameserver role to another candidate** — which is why `primary masters` in
  `-sr_state` is worth watching.
- `SAPHanaSR-angi` **unifies scale-up and scale-out**; classic `SAPHanaSR` needed the separate
  `SAPHanaSR-ScaleOut` package. Check which is installed before following any procedure.

---

## 7. Other scale-out gotchas

- **`hdbuserstore` is per host.** In scale-out the command **must be run on all hosts**. Change the
  repository import user's password and you must update the userstore too. **[V]**
- **HA/DR providers can inform external entities about scale-out events**, including host
  auto-failover — not just replication state changes. **[V]**
- **Standby hosts** appear in topology but hold no volumes; expect them to be inert in replication
  monitoring rather than reporting healthy.
