# SAPControl functions, instance types & per-OS boot wiring

Reference detail for [../SKILL.md](../SKILL.md). Everything here is Linux/Windows/AIX unless noted.

## sapcontrol — invocation

```bash
# UNIX — host agent copy (works for any instance/host):
/usr/sap/hostctrl/exe/sapcontrol -nr <nr> -function <Function> [args]
# UNIX — instance copy:
/usr/sap/<SID>/<INST><nr>/exe/sapcontrol -nr <nr> -function <Function> [args]
# Windows:
%ProgramFiles%\SAP\hostctrl\exe\sapcontrol.exe -nr <nr> -function <Function> [args]
```
Common options: `-host <host> -user <sidadm> <password>` (remote), `-format script` (parseable output),
`-prot NI_HTTP|NI_HTTPS`. Run as `<sidadm>` (or root). [L1]

## Lifecycle function catalog

| Function | Effect | Scope |
|----------|--------|-------|
| `StartSystem` | start **all** instances of the system, ascending `startPriority` | whole system [V, L1] |
| `StopSystem` | stop **all** instances, descending priority ⚠️ | whole system [V, L1] |
| `RestartSystem` | stop then start all instances (DB untouched) | whole system [L5] |
| `Start` | start the **local** instance (`-nr`) | one instance [V, L1] |
| `Stop` | stop the local instance ⚠️ | one instance [V, L1] |
| `Restart` | stop+start the local instance | one instance [L5] |
| `StartService <SID>` / `StopService` | start/stop the **sapstartsrv** service itself | control layer |
| `GetProcessList` | processes of the instance + colour status | one instance [V, L1] |
| `GetSystemInstanceList` | all instances: host, ports, `startPriority`, `features`, `dispstatus` | whole system [L4] |
| `GetInstanceProperties` / `GetVersionInfo` | instance metadata / kernel version | one instance |

**Status colours:** `GREEN` running · `YELLOW` starting/stopping · `GRAY` stopped · `RED` error. Treat
a step as done only when the expected instances reach the expected colour.

## Instance types (`features` tokens → type)

| Type | Role | `features` tokens | `startPriority` |
|------|------|-------------------|-----------------|
| **ERS** | Enqueue Replication Server (HA lock table replica) | `ENQREP` | **0.5** — start first / stop last |
| **ASCS** | ABAP Central Services: Message Server + Enqueue Server | `MESSAGESERVER, ENQUE` | **1** |
| **SCS** | Java Central Services (Message + Enqueue) | `MESSAGESERVER, ENQUE, J2EE` | **1** |
| **PAS** | Primary Application Server (was "central instance") | `ABAP, ICMAN, IGS, GATEWAY` (+ `MESSAGESERVER` if it hosts it) | **3** |
| **AAS** | Additional Application Server (dialog instance) | `ABAP, ICMAN, IGS, GATEWAY` | **3** |
| **Web Dispatcher** | reverse proxy / load balancer (front) | `WEBDISP, ICMAN` | 3 (front layer) |
| **Gateway** | standalone gateway | `GATEWAY` | 3 |
| **DB (HANA)** | database instance | `HDB` | started via the **DB reference**, not SAPControl |

## The full order (why)

- **ERS before ASCS**, **ASCS stopped before ERS** — so the enqueue lock table can be handed to/from
  its replica without loss. [L2/L3]
- **ASCS/SCS** (enqueue + message server) is DB-independent; **PAS/AAS need a running DB**. [L3]
- Net: **start** DB → ERS → ASCS/SCS → PAS → AAS; **stop** AAS → PAS → ASCS/SCS → ERS → DB.
- `StartSystem`/`StopSystem` sequence the **instances** automatically; **you** handle the DB before
  (start) or after (stop) via [../../sap-db-command-reference/SKILL.md](../../sap-db-command-reference/SKILL.md).

## Control layer & boot-time autostart (per OS)

`sapstartsrv` (per instance) + the **SAP Host Agent** (`saphostexec`, `/usr/sap/hostctrl/exe`) must be
running for SAPControl to work. Check them:
```bash
/usr/sap/hostctrl/exe/saphostexec -status          # UNIX
/usr/sap/hostctrl/exe/saphostctrl -function ListInstances
```

| OS | Boot wiring |
|----|-------------|
| **Linux** | `sapstartsrv`/host agent started via **systemd** (unit derived from `sapinit`); `/usr/sap/sapservices` lists the `sapstartsrv` start commands. Per-instance autostart on system start is the `Autostart` parameter in the instance's START/instance profile. |
| **AIX** | `sapinit` launched from **`/etc/inittab`** (`/usr/sap/sapservices` drives the `sapstartsrv` processes). Same `Autostart` profile parameter; identical `sapcontrol` behaviour. |
| **Windows** | `sapstartsrv` runs as the Windows service **`SAP<SID>_<nr>`** per instance, plus the **`SAPHostExec` / `SAPHostControl`** host-agent services — set to **Automatic**. Managed from the **SAP MMC**. |

> The host agent and `sapstartsrv` running does **not** mean the SAP system is up — they are the control
> layer that lets you start it. `GetProcessList` GREEN is what confirms the instance is actually up.

## Sources

Same as [../SKILL.md](../SKILL.md) §Sources: SAPControl page [L1], SAP Note 897933 [L2], the S/4HANA
Technical Operation curriculum [L3], `GetSystemInstanceList` fields [L4], and *Starting and Stopping SAP
System Instances Using Commands* [L5]. SAP Host Agent: *SAP Host Agent* guide (BC-CST) on help.sap.com.
