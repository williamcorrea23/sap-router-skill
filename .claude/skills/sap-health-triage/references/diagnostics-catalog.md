# SAPControl read-only diagnostics, `sappfpar`, and the work directory

Reference detail for [../SKILL.md](../SKILL.md). All `sapcontrol`/`sappfpar`/`disp+work` here are kernel
tools — **identical on Linux, Windows and AIX** (path/extension aside). Prefix every `sapcontrol` call
with `-nr <nr> -function`.

## Getting the definitive `-function` list for **your** kernel

The set of supported webmethods **varies by kernel release and patch level**, so never assume a function
exists — ask the binary. SAP documents the command-line help as the authoritative list: [V, T4]

```bash
# UNIX
/usr/sap/<SAPSID>/<INSTANCE><NUMBER>/exe/sapcontrol --help
# Windows
<Drive>:\usr\sap\<SAPSID>\<INSTANCE><NUMBER>\exe\sapcontrol.exe --help
```

Practical filters:
```bash
sapcontrol --help 2>&1 | grep -iE "read|list|get"      # the read-only surface
sapcontrol --help 2>&1 | grep -ciE "^ +[A-Z]"          # how many functions this kernel exposes
sapcontrol -nr <nr> -function AccessCheck <Function>   # is this one permitted for me?
```

> Per the plugin's execution discipline: derive the list with `--help` rather than assuming from this
> file, and use `AccessCheck` before concluding a method is unavailable — it may simply be *protected*
> (see `service/protectedwebmethods` below) rather than missing.

## Function map by category

Availability varies by release — confirm with `--help`. **⚠️ = state-changing**; those belong to
[sap-system-lifecycle](../../sap-system-lifecycle/SKILL.md), not to triage, and are listed here only so
you recognise them and *don't* fire one while diagnosing. [T5]

| Category | Functions |
|---|---|
| **Instance lifecycle ⚠️** | `Start` · `Stop` · `Restart` · `StartWait` · `StopWait` · `RestartWait` |
| **System lifecycle ⚠️** | `StartSystem` · `StopSystem` · `RestartSystem` |
| **Control service ⚠️** | `StartService` · `StopService` · `RestartService` |
| **Database ⚠️** | `StartDatabase` · `StopDatabase` (only if registered with the Host Agent) |
| **Status / inventory** | `GetProcessList` · `GetSystemInstanceList` · `GetInstanceProperties` · `GetVersionInfo` · `GetEnvironment` · `GetStartProfile` · `GetAccessPointList` |
| **Logs & traces** | `ABAPReadSyslog` · `ABAPReadRawSyslog` · `ListDeveloperTraces` · `ReadDeveloperTrace` · `ListLogFiles` · `ReadLogFile` |
| **Work processes / sessions** | `ABAPGetWPTable` · `GetQueueStatistic` · `ABAPGetComponentList` |
| **Enqueue** | `EnqGetStatistic` · `EnqGetLockTable` · `EnqRemoveLock` ⚠️ |
| **ICM** | `ICMGetThreadList` · `ICMGetConnectionList` · `ICMGetCacheEntries` · `ICMGetProxyConnectionList` |
| **Alerts / monitoring** | `GetAlerts` · `GetAlertTree` · `ABAPAcknowledgeAlert` ⚠️ |
| **Parameters** | `ParameterValue` (read; **setting** a parameter is ⚠️ and belongs to a change, not triage) |
| **High availability** | `HACheckConfig` · `HACheckFailoverConfig` · `HAGetFailoverConfig` · `HAFailoverToNode` ⚠️ |
| **Security / permission** | `AccessCheck <Function>` (unprotected — safe first call) |

> Note the naming convention: **`Get*` / `List*` / `Read*` / `*Check*` are read-only**; `Start*`,
> `Stop*`, `Restart*`, `Remove*`, `Acknowledge*`, `Failover*` change state. When in doubt, run
> `--help` and read the description before executing.

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

## `sappfpar` — profile parameter validator

Kernel profile validator; **works while the system is down**, which makes it the tool for "won't start"
and for validating a profile change *before* a restart.

### Commands & arguments

```
sappfpar <command> [pf=<profile>] [nr=<nr>] [name=<SID>]
  check          validate parameters, check the shared-memory configuration,
                 and estimate the memory requirement
  all            print EVERY parameter the kernel knows + the effective value
  <param-name>   print a single parameter's value  (e.g. sappfpar rdisp/wp_no_dia pf=…)
  help           usage / the command list for this kernel
```

| Argument | Meaning |
|---|---|
| `pf=<profile>` | the profile to read — **use the full path** (see the trap below) |
| `nr=<nr>` | instance number to evaluate for |
| `name=<SID>` | system ID to evaluate for |

### Getting the definitive parameter list

There is no fixed list to memorise — the parameter set is **kernel-release specific**, so enumerate it
from the system rather than from this file:

```bash
sappfpar all pf=/usr/sap/<SID>/SYS/profile/<SID>_<INST><nr>_<host>          # every parameter + effective value
sappfpar all pf=<profile> | grep -i "^rdisp/"                                # one family
sappfpar <param> pf=<profile>                                                # a single value
sapcontrol -nr <nr> -function ParameterValue <param>                         # value in the RUNNING instance [V, T3]
```
In the system: **RZ11** (parameter documentation + current/effective values), **RZ10** (profile
maintenance), report **RSPFPAR** / **RSPARAM** (parameter list with defaults).

> Read `sappfpar all` output correctly: the effective values shown are those that apply **after the next
> startup**, and the `SAP:` column is the **kernel default**, not your setting. To see what the *running*
> instance actually has, use `sapcontrol … ParameterValue` or RZ11.

### ⚠️ The `<no_profile>` trap (why "the error never goes away")

Classic symptom: you fix a parameter, re-run `sappfpar check`, and it reports **the same error**. Cause:
the profile was not read at all, so you are looking at **kernel defaults**, not your instance. [V, T3]

- Tell-tale: the first line of the output reads
  `== Checking profile: <no_profile>`
- Causes: a relative/short profile name, a **space after `pf=`**, illegal characters, or omitting `pf=`.
- Fix — full path, no space after `=`:
  ```bash
  sappfpar check pf=/usr/sap/<SID>/SYS/profile/<SID>_<INST><nr>_<host>    # correct
  # wrong: sappfpar check pf=<profile name>      (not a full path)
  # wrong: sappfpar check pf= /usr/sap/...       (space after '=')
  ```
- Cross-check a value against the running system with
  `sapcontrol -nr <nr> -function ParameterValue <param>`. [V, T3]

### Parameter families worth knowing (orientation for triage)

Not exhaustive — use `sappfpar all` for the real list. These are the families that come up when a system
won't start or misbehaves:

| Family | Controls |
|---|---|
| `rdisp/…` | dispatcher & work processes — `wp_no_dia`, `wp_no_btc`, `wp_no_upd`, `wp_no_enq`, `wp_no_spo`, `max_wprun_time`, `TRACE` |
| `abap/…` | ABAP runtime — `heap_area_dia`, `heap_area_total`, `buffersize`, `swap_reserve` |
| `em/…`, `ztta/…`, `PHYS_MEMSIZE` | extended/roll memory sizing — the usual suspects in memory errors |
| `ipc/shm_psize_<key>` | **shared-memory pools** — the "pool too small" errors `check` reports |
| `enque/…` | enqueue server (lock table size, server host/port) |
| `icm/…` | ICM: `server_port_<n>`, `trace_level`, `HTTP/logging_<n>` |
| `gw/…` | gateway: `logging`, `sec_info`, `reg_info` |
| `login/…`, `rsau/…` | logon policy / password rules; Security Audit Log config |
| `DIR_…`, `SAPGLOBALHOST`, `SAPSYSTEMNAME`, `INSTANCE_NAME` | directories & identity — wrong values here break startup |
| `dbs/…`, `dbms/type` | database connection / type |

Cross-ref: raise/lower trace parameters per
[sap-log-reference → app-and-component-logs](../../sap-log-reference/references/app-and-component-logs.md).

## `disp+work` — the work-process binary (and version check)

`disp+work` **is** the ABAP dispatcher/work-process executable, not a utility — the admin use is reading
what kernel is actually installed. Run as `<sid>adm` from the instance `exe` directory.

```bash
disp+work -version          # kernel release, patch level, DB client library, Unicode, compile info
disp+work -V                # same on most releases
disp+work -h                # option list for THIS kernel (definitive; options vary by release)
```

What the output answers, and why it matters in triage:

| Field | Use |
|---|---|
| **kernel release** (e.g. 7.53/7.77/7.89) + **patch level** | did the kernel patch actually land? matches the SAR you extracted? |
| **DB client library** / `dbsl` | wrong or missing DBSL ⇒ "database not available" despite a healthy DB |
| **Unicode** | wrong Unicode/platform binary ⇒ instance won't start at all |
| compilation / platform | confirms you are on the binary you think you are |

In-system equivalents: **SM51** → Release info, or *System → Status*.
Cross-ref [sap-kernel-patch](../../sap-kernel-patch/SKILL.md) — `disp+work -version` is the before/after
check for a kernel swap.

## `dpmon` — dispatcher monitor from the OS (SM50 when you can't log on)

`dpmon` is the **OS-level work-process monitor**: the SM50 view without a SAP GUI session. Its value is
precisely the case where the system is *partially* up — dispatcher alive, but logon impossible — so SM50
is unreachable. SAP documents it as the fallback *"in situations where SM50 is not accessible."* [V, T6]

```bash
# as <sid>adm, from the instance exe directory
dpmon pf=/usr/sap/<SID>/SYS/profile/<SID>_<INST><nr>_<host>     # interactive, menu-driven
```
It opens a menu; the entries are single letters. The ones that matter in triage:

| Key | Shows / does |
|---|---|
| **`m`** | work-process list (the SM50 equivalent: PID, type, status, reason, action, user, table) |
| **`q`** | dispatcher **queue** information — a growing queue means requests are not being served |
| **`t`** | show the current **trace level** per work process; press `t` again to **set** level + components [V, T6] |
| `c` / `l` | communication / logon information (release-dependent) |
| `x` or `q`-to-quit | leave the monitor (the exact key is shown in the menu) |

> The menu differs by kernel release — read the on-screen list rather than assuming a key. `dpmon` is
> read-only **except** the trace-level option (`t`), which changes instance behaviour: treat that as a
> change, and lower it again afterwards.

### Work-process trace levels (what `t`, `rdisp/TRACE` and SM50 all set) [V, T6]

| Level | Meaning | Cost |
|---|---|---|
| **0** | store nothing | — |
| **1** | errors only — **the default** | — |
| **2** | + trace messages | *"slight (negligible) impact"* — **sufficient for most troubleshooting** |
| **3** | + fully trace data blocks | *"often significantly impact performance"* — only when SAP asks |

Component-level tracing is `rdisp/TRACE_COMPS` (RZ11 → *Display docu* for the component list; Taskhandler
is usually enough for request-handling issues).

**Four ways to change it, in SAP's order of preference** [V, T6]:

1. **SM50** → *Administration → Trace → Active Components* (recommended; per-WP or a selected group;
   *Default Values* restores it). Dispatcher-only via *Administration → Trace → Dispatcher*.
2. **`dpmon`** option `t` — when SM50 is not accessible.
3. **RZ11 → `rdisp/TRACE`** — but this changes **all** processes on the instance (WPs, dispatcher,
   gateway, ICM), so prefer 1 or 2 if you only want work processes.
4. **Instance profile + restart** — for problems that occur *during startup*, where the running-system
   methods can't help. (`AL11` → `DIR_PROFILE` to find the file.)

Gateway only: **SMGW → Goto → Trace → Gateway → Increase Level**.

> Reminder from the skill body: **raise → reproduce → lower.** Level 3 left on will fill the work
> directory and slow the instance. Trace files land as `dev_w*` — see
> [sap-log-reference](../../sap-log-reference/SKILL.md).

## `saposcol` — the OS collector (what feeds ST06)

One collector **per host**, SID-independent. It samples CPU/memory/disk/network into shared memory;
ST06/OS07N, CCMS, Solution Manager and EarlyWatch all read from it. **No saposcol ⇒ no OS data anywhere.**

> **Modern model:** saposcol is started and supervised by the **SAP Host Agent**, *not* per instance.
> The old "one saposcol per instance from the instance `exe` dir" model is **no longer supported**. [V, T7]

```bash
saposcol -s        # status — check "Current Time" vs "Last write access"
saposcol -m        # dump the data collected in the last collection interval
saposcol -d        # dialog mode; inside: `stat` (shows trace level), `trace` (toggle 1<->3)
saposcol -b        # generate the hardware-info file
ps -ef | grep saposcol      # UNIX — expect exactly ONE (up to 3 briefly at startup)
```

**"No OS data in ST06" ladder** [V, T7]:

1. **Is it running?** `ps -ef | grep saposcol`. If not, check `host_profile`
   (`/usr/sap/hostctrl/exe` or `…\SAP\hostctrl\exe`) for `hostexec/startoscol = false` — delete/comment
   it, then `saphostexec -restart`.
2. **Is the data fresh?** `saposcol -s` — *"'Last write access' should be not more than 'Collection
   interval' older than 'Current time'."* Collection interval should be **60s, not 10**.
3. **Shared memory stuck?** Stop it (`saphostexec -stop`), confirm no saposcol running, then on UNIX
   `ipcs | grep 4dbe` → remove with `ipcrm -M 0x00004dbe` (that key is saposcol's only, nothing else is
   affected), delete the **`coll.put`** backup file (`/usr/sap/tmp`), and `saphostexec -restart`.
4. **Web-service path** (NWA/SolMan read via the Host Agent, not saposcol directly): `host_profile` must
   contain `SAPOscol` in `service/porttypes` (**case-sensitive**), then
   `saphostctrl -function GetSAPOSColVersion` and `GetSAPOSColHWConf` must return *"Webmethod returned
   successfully"*.
5. **Too many processes?** Exactly one is correct. Several usually means the obsolete per-instance model
   — move to the SAP Host Agent.
6. **Tracing:** `hostexec/oscol/arguments = -t3 -tl0` in `host_profile` + `saphostexec -restart`, or
   without a restart via `saposcol -d` → `trace`. Trace lands in **`dev_coll`** (`/usr/sap/tmp`); it
   grows, so turn it off afterwards. *(Trace changes only take effect from the next collection interval.)*

> `WaitFree() failed. No write access to shared memory` in the log is **not** an error by itself —
> saposcol's shared memory is exclusive, and it skips a write if a reader holds it. [V, T7]

## `cleanipc` — remove orphaned shared memory / semaphores

After a crash or a hard kill, an instance can leave IPC resources behind that block the next start.

```bash
cleanipc <nr> show          # list the IPC resources of instance <nr>   (read-only, safe)
cleanipc <nr> remove        # ⚠️ remove them — ONLY when that instance is DOWN
```

> ⚠️ **Verify the instance is stopped first.** `cleanipc … remove` wipes the instance's shared memory; run
> against a *running* instance it will take it down / corrupt it. Confirm with
> `sapcontrol -nr <nr> -function GetProcessList` and `ps -ef | grep <SID>` before removing. Run as
> `<sid>adm`. Related but separate: saposcol's own shared memory is cleaned with `ipcrm` (above), not
> `cleanipc`. [G]

**Reading the output — three things people get wrong.** [V]

1. **`Running SAP-Systems (Nr)...:` is the safety gate, and it is at the top for a reason.** If that list is
   **empty**, nothing was up and the removal was safe. If it names an instance, you are about to damage a
   running system. Read it before the removal lines, not after.
2. **The instance number is the one you typed, not the one you meant.** `cleanipc 00 remove all` cleans
   instance **00** only. If you are recovering a failed start of ASCS **01**, cleaning 00 achieves nothing
   and the blocking segments are still there. Confirm which number is which
   (`sapcontrol -nr <nr> -function GetProcessList`) and use **`cleanipc <nr> show`** — read-only — before
   committing to a removal.
3. **`(may be incomplete when not in superuser mode)` is a real limitation, not boilerplate.** Run as
   `<sid>adm`, segments owned by another user (root, or a second `<sid>adm` on a shared host) are invisible
   and stay behind. If a start still fails with shared-memory errors after a "successful" cleanup, re-run
   as **root** — that message is the reason.

**Is it needed at all?** Not routinely. A clean `StopSystem`/`stopsap` releases its own IPC, so a properly
stopped instance normally has **nothing to remove**. `cleanipc` is a *recovery* step for the case where a
crash or `kill -9` left orphans that block the next start (shared-memory create/attach failures in
`dev_w*` or the startup log). Finding orphans on a supposedly clean system is itself a signal that the
previous shutdown was not clean.

Typical orphans after an unclean exit: an **Event Flag** key and the **SCSA** (SAP Communication Segment
Area) shared-memory segment — removing those two is the common case.

## `jsmon` / `jcmon` — the Java-stack equivalent of `dpmon`

Only where **AS Java** is installed (PI/PO, EP, Solution Manager Java, dual-stack). Same idea as `dpmon`:
inspect the instance from the OS with minimal infrastructure, when the admin UI is unreachable. [G, T8]

```bash
jsmon pf=/usr/sap/<SID>/SYS/profile/<SID>_<INSTANCE>_<HOST>    # AS Java 7.1 and higher
jcmon pf=<profile>                                              # releases BEFORE NetWeaver 7.1
```
- Menu-driven (process list, enable/disable/restart a node, shut the instance down, debugging, ports).
- **Version boundary:** use **`jsmon`** on **7.1+**; on older releases the tool is **`jcmon`**. [G, T8]

Process model to recognise on the host:
```bash
ps -ef | grep jcontrol      # jcontrol starts/stops/monitors the Java instance
ps -ef | grep jlaunch       # jlaunch runs the Java nodes (server/dispatcher) that jcontrol starts
```
Logs for these live in the instance work directory (`dev_jcontrol`, `dev_server<n>`, `std_server<n>.out`)
— see [sap-log-reference](../../sap-log-reference/SKILL.md) §7.

> Like `dpmon`, `jsmon`/`jcmon` can **change state** (restart/stop nodes, enable debugging), not just
> read. Treat those entries as changes under the execution-discipline rules, not as triage.

## Connectivity tests — `R3trans`, `tp`, `niping`

These three are owned by other skills for their main jobs (`R3trans`/`tp` →
[sap-transport-mgmt](../../sap-transport-mgmt/SKILL.md), `niping` →
[sap-saprouter](../../sap-saprouter/SKILL.md)). Listed here for their **diagnostic** use: proving
where a connection actually breaks.

### `R3trans -d` — can the kernel reach the database?

The fastest, most decisive DB check at OS level. Run as `<sid>adm`:

```bash
R3trans -d                    # return code 0000 = database reachable
echo $?                       # 0 = OK; non-zero = could not connect
```
- Writes its detail to **`trans.log`** in the current directory — read it on failure; it names the DB
  error (wrong DBSL, credentials, listener down, DB not open).
- Use it to split "SAP is broken" from "the DB is unreachable" in one command. If `R3trans -d` succeeds
  but the instance won't start, the problem is **not** DB connectivity.
- Pair with `disp+work -version` — a mismatched/missing **DBSL** shows as a connect failure here even
  though the database itself is perfectly healthy.

### `tp` — is the transport system healthy?

```bash
tp connect <SID> pf=<TPPARAM>            # tp's own DB connect test
tp showbuffer <SID> pf=<TPPARAM>         # what's queued (read-only)
tp checkimpdp <SID> pf=<TPPARAM>         # is the transport daemon (RDDIMPDP) alive?
```
Return codes: **0** ok · **4** warnings · **8** errors · **12** fatal · **16** tp environment/`TPPARAM`
problem. A **16** almost always means environment, not transports (`transdir not set`, bad `pf=`).
Full detail: [sap-transport-mgmt](../../sap-transport-mgmt/SKILL.md).

### `niping` — is it really the network?

`niping` works on the **TCP socket layer — the same layer SAP applications use** — so unlike ICMP `ping`
it also catches TCP/socket-implementation problems. It ships with the kernel and with SAPROUTER. [V, T9]

```bash
# server on host A (port 3298 by default — check the firewall; -S changes it)
niping -s -I 0                       # last character is ZERO
niping -s -I 0 -S 5010               # non-default port

# client on host B
niping -c -H <server> [-B <buffersize>] [-L <loops>] [-D <delay-ms>]
```

| Test | Command | Read |
|---|---|---|
| **Throughput** | `niping -c -H <srv> -B 100000` (gigabit: `-B 8000000`) | **`tr2`** = kB/s |
| **Round-trip time** | `niping -c -H <srv> -B 1 -L 100` (older builds: `-B 20`) | **`av2`** = ms |
| **MTU problems** | `niping -c -H <srv> -B <n>` for n = 500, 1000, 1400, 1500, 4000, 10000, 40000 | errors at a specific size |
| **Firewall idle timeout** | `niping -c -H <srv> -P -D 3600000` | connection dropped between packets |
| **Stability / intermittent** | `niping -c -H <srv> -B 10000 -D 100 -L 360000` (~10 h) | any `*** ERROR` |

**Reading the output — the two rules that matter** [V, T9]:

- *"NIPING should not abort with an error message under any circumstances. An error is always indicated
  by a line starting with `*** ERROR ...`"*
- `NiIRead: hdl 0 recv would block (errno=EAGAIN)` is **not** an error — ignore it.

> **The decisive rule for "it's the network" claims:** *"If you can reproduce an error using NIPING then
> the problem is definitely related to the network layers, not to the application."* [V, T9]
> That is how you settle the argument instead of trading assertions — see rule of thumb #11 in the
> [troubleshooting skill](../../sap-troubleshooting/SKILL.md).

SAP publishes typical values (Gigabit ≈ 100000 kB/s, Fast Ethernet ≈ 10000 kB/s; RTT: Fast Ethernet <1 ms,
DSL ≈ 40 ms, satellite ≈ 1000 ms) but states explicitly they are dimensional examples — **do not use them
to evaluate a performance test**. [V, T9]

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

On the `-function` list specifically:

- **[T4]** *Starting and Stopping SAP Systems Using SAPControl* — SAP Help Portal. **[V]** verified
  during authoring: *"You can find a detailed list of all SAPControl options and features in the command
  line help, which you can call as follows: UNIX: `/usr/sap/<SAPSID>/<INSTANCE><NUMBER>/exe/sapcontrol
  --help`"* (Windows: `sapcontrol.exe --help`). This is why `--help` — not this file — is authoritative
  for a given kernel.
  https://help.sap.com/docs/ABAP_PLATFORM_NEW/30eef4341efd4a2c86f2f98f187eccb3/471d6feeff6e0d46e10000000a155369.html
- **[T5]** *How to use the SAPControl Web Service Interface* — SAP NetWeaver Server Infrastructure; the
  webmethod reference behind the category map. Function availability differs by release/patch level, so
  treat the map as orientation and `--help` + `AccessCheck` as ground truth. [G]

On `sappfpar`:

- **[T3]** **SAP KBA 2733511** — *sappfpar check pf=&lt;profile name&gt; still shows the same error after
  changing the related parameter* (BC-CST-LL). **[V]** Retrieved via the SAP Notes MCP. Documents the
  `<no_profile>` trap verbatim: *"The value of the profile name is invalid or the input has illegal
  characters. The first line of the sappfpar is `<no_profile>`… The parameter result is from the
  Kernel-Default, not the current instance parameter status."* — including that it also happens *"if the
  command is executed without the pf= value"*, that the fix is *"the full path of the instance profile
  name and without spaces after the `=`"*, and the `sapcontrol -nr <nr> -function ParameterValue
  <param>` cross-check. https://me.sap.com/notes/2733511
- Parameter families are orientation only; the authoritative per-kernel list comes from `sappfpar all`,
  RZ11, or report RSPFPAR/RSPARAM. [G]

On `disp+work` / `dpmon` / trace levels:

- **[T6]** **SAP KBA 3149490** — *How to Increase trace level of Work Process developer traces* (BC-CST).
  **[V]** Retrieved via the SAP Notes MCP. Source for the four trace levels and their cost — *"Level 1 –
  store only error information (default)… Level 2 traces typically result in only a slight (negligible)
  impact on performance while level 3 traces often significantly impact performance. For most
  troubleshooting purposes level 2 is sufficient."* — for `rdisp/TRACE_COMPS`, for the four change
  methods in preference order, and for `dpmon`'s documented role: *"Method 2. Using dpmon (In situations
  where SM50 is not accessible)"* with option `t` to show and set per-WP trace level and components.
  https://me.sap.com/notes/3149490
- **SAP Note 112** — *Trace and error information in the "dev_" files* — the canonical reference for the
  `rdisp/TRACE*` parameters and dev-trace content. https://me.sap.com/notes/112
- `disp+work -version` / SM51 / *System → Status* for kernel release and patch level — see
  [../SKILL.md](../SKILL.md) §Sources [T4] and [sap-kernel-patch](../../sap-kernel-patch/SKILL.md). [G]

On `saposcol` / `cleanipc` / `jsmon`:

- **[T7]** **SAP Note 2179983** — *Basic 'missing OS data' troubleshooting* (BC-CCM-MON-OS). **[V]**
  Retrieved via the SAP Notes MCP. Source for the whole saposcol ladder: `-s` / `-m` / `-d` (`stat`,
  `trace`) / `-b`; the `hostexec/startoscol = false` switch; `saphostexec -restart`; the shared-memory
  cleanup (`ipcs | grep 4dbe`, `ipcrm -M 0x00004dbe`, delete `coll.put`); `service/porttypes` needing
  **`SAPOscol`** and the `saphostctrl -function GetSAPOSColVersion` / `GetSAPOSColHWConf` checks;
  *"There should be one saposcol process running"*; the 60s collection interval; `dev_coll` tracing via
  `hostexec/oscol/arguments = -t3 -tl0`; and that `WaitFree() failed…` is benign. Also states the
  per-instance saposcol model *"is not supported anymore"* — use the SAP Host Agent (SAP Note 1031096).
  https://me.sap.com/notes/2179983
- **[T8]** *Using the Command Line Program `jsmon`* — SAP Help Portal (Java Startup and Control
  Framework, AS Java 7.1+): `jsmon pf=<path to profile>`; on releases **before** NetWeaver 7.1 use
  `jcmon`. `jcontrol` starts/stops/monitors the Java instance and launches the `jlaunch` node processes.
  https://help.sap.com/doc/saphelp_nw74/7.4.16/en-US/c9/291745bd4849e980c5d3b2e1312244/content.htm [G]
- `cleanipc <nr> show|remove` — SAP kernel tool; run as `<sid>adm` **only against a stopped instance**.
  Cross-referenced in [sap-housekeeping](../../sap-housekeeping/SKILL.md) §5. [G]

On `niping` / `R3trans` / `tp`:

- **[T9]** **SAP Note 500235** — *Network Diagnosis with NIPING* (v21, 2025-01-22). **[V]** Retrieved via
  the SAP Notes MCP. Source for: NIPING operating *"on the TCP socket layer, which is the same layer used
  by SAP application programs"*; `niping -s -I 0` / `niping -c -H <srv> -B -L -D`; the **default port
  3298** and `-S` to change it; throughput via **`tr2`** and RTT via **`av2`**; the MTU buffer-size sweep;
  the `-P -D 3600000` idle-timeout test; that *"an error is always indicated by a line starting with
  `*** ERROR`"* while `NiIRead… EAGAIN` is benign; the typical-values table with SAP's own caveat not to
  use it for performance evaluation; and the decisive statement *"If you can reproduce an error using
  NIPING then the problem is definitely related to the network layers, not to the application."*
  https://me.sap.com/notes/500235
- `R3trans -d` (RC 0000 = DB reachable, detail in `trans.log`) and the `tp` return codes / `tp connect` /
  `tp checkimpdp` — see [sap-transport-mgmt](../../sap-transport-mgmt/SKILL.md) §Sources. [G]
