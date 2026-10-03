# HA/DR provider hooks and cluster integration

**Scale-out clusters have extra requirements** (third site, majority maker, odd node count) — see
[hsr-scale-out.md](hsr-scale-out.md) §6.

HSR on its own gives you **replication, not failover**. Nothing promotes a secondary automatically
unless a cluster does it. This file covers the hook API HANA exposes and the two resource-agent
generations that consume it.

**Marks:** **[V]** read during authoring; **[G]** cited but not re-read in full.

---

## 1. HA/DR providers — the hook API

The HANA **nameserver** exposes a Python API called at defined points of host auto-failover and
system-replication takeover. **By default no action is configured** — hooks do nothing until you
install one. **[V, Note 1999880 Q66]**

| Hook method | Called when | Typical use | SUSE script (classic) |
|---|---|---|---|
| `srConnectionChanged()` | A replicating service **loses or establishes** the SR connection. Called on the **master nameserver**, **once**. | Tell the cluster the replication state changed | `SAPHanaSR.py` |
| `preTakeover()` | **Before** an SR takeover is processed | **Block a manual takeover** during normal cluster operation | `susTkOver.py` |
| `postTakeover()` | **After** an SR takeover has happened | Remove the memory limit, re-enable table preload (cost-optimized) | `susCostOpt.py` |
| `srServiceStateChanged()` | A **service status** changes | **Speed up takeover when the indexserver dies** | `susChkSrv.py` |
| `srReadAccessStateChanged()` | Read-access state changes | Active/Active (read enabled) scenarios | — |

**[G — vendor documentation, SUSE/Red Hat; SAP's own list is at help.sap.com "Hook Methods"]**

Hooks are registered in `global.ini` under a `[ha_dr_provider_<name>]` stanza, e.g.:

```ini
[ha_dr_provider_chksrv]
provider = ChkSrv
path = /usr/share/sap-hana-ha/
execution_order = 2
action_on_lost = stop
```

`execution_order` sequences multiple providers. **The path and provider name are distribution- and
version-specific — read your cluster vendor's current guide rather than copying this block.** **[G]**

> **Why `srServiceStateChanged()` matters.** Without it, an indexserver crash is not distinguishable
> from a slow service quickly enough, and takeover waits for a timeout. This hook is the difference
> between a fast and a sluggish failover.

---

## 2. SAPHanaSR vs SAPHanaSR-angi — a breaking change, not an upgrade

SUSE rewrote the resource agents. **"angi"** = *Advanced Next Generation Interface*. **[V, suse.com/c]**

| | Classic `SAPHanaSR` | `SAPHanaSR-angi` |
|---|---|---|
| Scale-up / scale-out | **Separate** implementations | **Unified** |
| Multitarget hook script | `SAPHanaSrMultiTarget.py` | **`susHanaSR.py`** |
| Tool location | `/usr/sbin/` | **`/usr/bin/`** |
| CIB attributes | — | **NOT backward compatible** |
| Takeover on filesystem failure | Slower | Faster (scale-up and scale-out) |
| Takeover when HANA unresponsive | Slower | Faster |

> ⚠️ **CIB attributes are not backward compatible between the two.** You cannot mix them in one
> cluster or roll back casually. The upgrade **can** be done **without HANA downtime**, but it is a
> planned change with a documented procedure — see `SAPHanaSR_upgrade_to_angi(7)` and SUSE's
> *How to upgrade to SAPHanaSR-angi*. **[V]**

**Before touching a clustered HSR pair, establish which generation is installed:**

```bash
rpm -q SAPHanaSR SAPHanaSR-angi SAPHanaSR-ScaleOut 2>/dev/null   # SUSE
rpm -q resource-agents-sap-hana resource-agents-sap-hana-angi     # Red Hat
crm_mon -1                                                        # what the cluster actually runs
grep -A5 '^\[ha_dr_provider' /hana/shared/<SID>/global/hdb/custom/config/global.ini
```

Red Hat has an equivalent generational split — see *Upgrading SAP HANA HA setup to the new generation
of resource agents* (RHEL for SAP Solutions 9). **[G]**

---

## 3. Cluster-side rules that bite

- **The cluster owns takeover.** Once a pacemaker cluster manages HSR, running
  `hdbnsutil -sr_takeover` by hand fights the cluster. That is exactly what `preTakeover()` /
  `susTkOver.py` exists to block. **Put the cluster in maintenance mode first**, or use the cluster's
  own takeover mechanism.
- **`sr_register` by hand on a clustered secondary** will be undone or will confuse the resource
  agent. Follow the vendor procedure.
- **Cost-optimized scenarios** run a non-productive system on the secondary hardware, which is why
  `postTakeover()` must lift the memory limit and re-enable preload. This is also the case where
  primary/secondary parameters legitimately differ — see the parameter-drift note in
  [hsr-parameters.md](hsr-parameters.md).

---

## 4. Sources

| Source | Read |
|---|---|
| SAP Note 1999880 Q66 — *What are HA/DR providers?* | **[V]** |
| help.sap.com — *Hook Methods*, SAP HANA Platform | **[G]** |
| SUSE — *What is SAPHanaSR-angi?* / *How to upgrade to SAPHanaSR-angi* (`suse.com/c/`) | **[V]** |
| SUSE — *SAP HANA SR Scale-Up Performance Optimized / Cost Optimized* best-practice guides (`documentation.suse.com/sbp/`) | **[G]** |
| SUSE — `SAPHanaSR-ScaleOut(7)` man page; *SAPHanaSR-ScaleOut: Automating SAP HANA System Replication for Scale-Out Installations* | **[G]** |
| `susHanaSR.py(7)`, `SAPHanaSR_upgrade_to_angi(7)` man pages | **[G]** |
| Red Hat — *Deploying SAP HANA Scale-Up/Scale-Out System Replication HA*, RHEL for SAP Solutions 9 | **[G]** |

> **Distribution guides move faster than this file.** Hook script names, paths and package names are
> the most volatile things here — verify against the vendor guide for the installed version before
> editing `global.ini`.
