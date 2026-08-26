# SAPControl read-only diagnostics, `sappfpar`, and the work directory

Reference detail for [../SKILL.md](../SKILL.md). All `sapcontrol`/`sappfpar`/`disp+work` here are kernel
tools — **identical on Linux, Windows and AIX** (path/extension aside). Prefix every `sapcontrol` call
with `-nr <nr> -function`.

## Read-only SAPControl function catalog (triage-relevant)

**Status / inventory**
| Function | Shows |
|----------|-------|
| `GetProcessList` | processes of the instance + colour status |
| `GetSystemInstanceList` | all instances: host, ports, `startPriority`, `features`, `dispstatus` |
| `GetInstanceProperties` | instance metadata (dirs, ports, SID, nr) |
| `GetVersionInfo` | kernel patch level of the running instance |
| `GetEnvironment` | the instance's OS environment |

**Logs & traces** *(protected — see below)*
| Function | Equivalent |
|----------|-----------|
| `ABAPReadSyslog` | SM21 system log |
| `ABAPReadRawSyslog` | raw syslog stream |
| `ListDeveloperTraces` | list `dev_*` trace files in `DIR_HOME` |
| `ReadDeveloperTrace <file> <size>` | read a trace file (`size=0` → whole file) |
| `ReadLogFile <path> <filter>` | read an arbitrary instance log |

**Work processes / sessions / locks** *(protected)*
| Function | Equivalent |
|----------|-----------|
| `ABAPGetWPTable` | SM50 (work processes of this instance) |
| `GetQueueStatistic` | dispatcher request queues |
| `EnqGetStatistic` / `EnqGetLockTable` | enqueue server stats / lock table (on ASCS/SCS) |
| `ICMGetThreadList` / `ICMGetConnectionList` | ICM threads / connections |

**Alerts / HA / checks**
| Function | Shows |
|----------|-------|
| `GetAlertTree` / `GetAlerts` | CCMS alert tree (RZ20-style) |
| `HACheckConfig` / `HACheckFailoverConfig` | HA configuration validation |
| `AccessCheck <Function>` | whether a given web method is permitted (no auth needed) |

## `service/protectedwebmethods` (security)

Most logs/traces/WP methods are **protected by default** — governed by the profile parameter
`service/protectedwebmethods` (SAP Note 1439348). A protected method returns an authorization error
unless you either:
- call it **authenticated**: `sapcontrol -nr <nr> -user <sidadm> <password> -function <Function> …`, or
- it is **allow-listed** in the profile, e.g. `service/protectedwebmethods = SDEFAULT -GetProcessList`
  (start from the secure `SDEFAULT` set and add/remove specific methods deliberately).

Check first: `sapcontrol -nr <nr> -function AccessCheck <Function>` (this one is not protected).

## `sappfpar` argument reference

Kernel profile validator — works while the system is **down**. [KBA 2733511]
```
sappfpar <command> [pf=<profile>] [nr=<nr>] [name=<SID>]
  check     validate parameters, check shared-memory config, estimate memory requirement
  all       print every parameter the kernel knows + effective value from the profile
  <name>    print a single parameter's value
  help      usage
```
- Effective values shown are those that apply **after the next startup**; the `SAP:` column = kernel
  default.
- Typical use: `sappfpar check pf=/usr/sap/<SID>/SYS/profile/<SID>_<INST><nr>_<host>` after any profile
  change, **before** `StartSystem`.

## Instance work directory — what to read

`/usr/sap/<SID>/<INST><nr>/work/` (Windows: `…\work\`). First stop when an instance won't start:

| File | Content |
|------|---------|
| `dev_disp` | dispatcher trace (start failures show here first) |
| `dev_w0` … `dev_w<n>` | work-process traces |
| `dev_ms` | message server trace (ASCS/SCS) |
| `dev_rd` | gateway trace |
| `dev_icm` | Internet Communication Manager trace |
| `dev_enq*` / `enserver` logs | enqueue server |
| `stderr1`, `stderr2`, … | instance stdout/stderr per start |
| `available.log`, `sapstart.log` | start-service / availability logs |

Reading these from the shell = `sapcontrol … ReadDeveloperTrace <file> 0`; on disk = your pager. Cleanup
of old traces/logs is **`sap-housekeeping`**, not triage.

## Sources

Same as [../SKILL.md](../SKILL.md) §Sources — SAP S/4HANA Technical Operation curriculum [T1], SAP Note
1439348 (`service/protectedwebmethods`) [T2], SAP KBA 2733511 (`sappfpar`) [T3], the SAPControl page
[T4], and *How to use the SAPControl Web Service Interface* [T5].
