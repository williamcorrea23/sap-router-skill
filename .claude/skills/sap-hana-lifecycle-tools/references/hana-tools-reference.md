# `hdbcons` and `hdblcm` — extended reference

Companion to the parent skill. hdbcons content is **[V]** from **SAP Note 2222218** v122; hdblcm is
**[G]**.

---

## 1. hdbcons command table by purpose **[V]**

### Diagnostics for SAP support

| Command | Purpose |
|---|---|
| `runtimedump dump [-c] [-f <file>] [-i] [-s <sections>]` | Generate a runtime dump (Notes 2400007, 1813020) |
| `runtimedump l` | List available dump sections |
| `context l -s [-f]` | Call stacks for active threads; `-f` includes inactive (Note 2313619) |
| `deadlockdetector wg -w -o <file>.dot` | Deadlock graph for internal locks. **Only a subset of deadlocks is recognised — semaphore waits are not considered** |
| `profiler start\|stop\|print\|clear` | Kernel profiler (Note 2800030), filterable by user/connection/statement hash |

### Memory

| Command | Purpose |
|---|---|
| `mm ipmm -d` | Inter-process memory management + flight recorder |
| `mm l -s -S -p` | Heap allocator list, statistics, sorted by size, with peaks |
| `mm poolallocator` | Heap fragmentation |
| `mm numa -p / -t / -v` | Physical / topology / virtual per NUMA node (Note 2470289) |
| `mm gc [-f]` | **Return free memory to the OS.** *"Can cause significant performance issues and follow-up problems, so should only be used if requested by SAP support"* |
| `mm ru` | Reset memory measurements |
| `pageaccess a [ext] [d]` | Pages currently in memory; `d` inspects disk pages — **very high runtime** |

> Several `mm` subcommands (`bl`, `cg`, `top`) **crash** older revisions — see the parent skill's
> crash table.

### Sessions and transactions

| Command | Purpose |
|---|---|
| `connection c <id>` / `connection d <id>` | Cancel / disconnect a connection (Note 2092196) |
| `transaction c <id>` / `transaction c -a` | Cancel active operations in one / all transactions |
| `transaction d <consistent_view>` | Force-deactivate a consistent view. **Can cause instability if the token is still required** |

### Persistence

| Command | Purpose |
|---|---|
| `savepoint execute` | Trigger a savepoint |
| `log backup` / `log release` | Force log backup / release free log segments |
| `dvol shrink -o 120` | Data-volume defragmentation. **Never on a secondary replication site** |
| `dvol sbtouch -n <blocks>` | Mark superblocks dirty to improve reclaim (> 2.00.048.02 / > 2.00.053) |
| `encryption status` | Persistence encryption status |
| `snapshot l / a <id> / d <id>` | List / analyse / delete snapshots |

### Replication and distribution

| Command | Purpose |
|---|---|
| `replication i` | System replication overview (Notes 2063657, 2086024) |
| `distribute e <host>:<port> <cmd>` | Run a command on a remote service. **TREXNet-based and can fail under load — prefer a direct connection for critical work like runtime dumps** |

### Housekeeping

| Command | Purpose |
|---|---|
| `output l` | **List directories hdbcons may write to** — check this before `-o`/`-f` |
| `help` / `help <command>` / `hdbcons -?` | Server-side / per-command / client-side help |
| `\?` / `\< <file>` / `\> <file>` | Internal commands: help, read commands from file, write output to file |

---

## 2. Automatic hdbcons execution at startup **[V]**

```sql
ALTER SYSTEM ALTER CONFIGURATION ('daemon.ini','SYSTEM')
  SET ('daemon','environment') 'HDB_INITIAL_COMMAND<hdbcons_command>' WITH RECONFIGURE;
```

Special characters such as commas must be escaped with a backslash:

```
'HDB_INITIAL_COMMANDmm f Pool -rs ffence\,bfence\,areset\,dreset'
```

Use only when SAP asks for a trace active from startup.

---

## 3. Detecting hdbcons usage **[V]**

| Approach | Detail |
|---|---|
| **Trace file** (HANA 2.0 SPS 03+) | `<service>_<host>.<port>.hdbcons.trc` records **every** call with parameters, timestamp and duration |
| **Thread samples** | Thread type `Request` with method `core/ngdb_console` or `ngdb_console`, or `JobWorker`/`ServerJob` |
| **Mini-checks** | `M2320` (time since last hdbcons execution), `T2300`/`T2301` (transactions/connections terminated with hdbcons) |

`M_SERVICE_THREAD_CALLSTACKS` implicitly triggers hdbcons (`context l -s -f -n -p`), and from
**2.0 SPS 04** the statistics server persists that view **every five minutes** — so periodic hdbcons
activity in traces is normal, not evidence of someone poking the system. **[V]**

---

## 4. hdblcm — actions and options **[G]**

```bash
./hdblcm --help                        # authoritative
./hdblcm --action=<action> [options]
./hdblcm --dump_configfile_template=<file>
./hdblcm --batch --configfile=<file>
```

| Action | Purpose |
|---|---|
| `install` | Install a new system (media hdblcm) |
| `update_components` | Update HANA / components |
| `add_hosts` / `remove_hosts` | Scale out / in |
| `add_host_roles` | Change roles on an existing host |
| `configure_internal_network` | Dedicate an internal network on a distributed system |
| `register_rename_system` / `unregister_system` | System registration |
| `print_component_list` | What is installed |
| `check_installation` | Validate an installation |

**Password handling:** prefer `--read_password_from_stdin=xml` over passing passwords as arguments.
Arguments appear in the process table and shell history.

**Reproducibility:** generate a config file template, fill it, run with `--batch`. That file is the
artefact to attach to the change record.

**Before an update, read SAP Note 2082466** (*Known Issues in HDBLCM*) — it is maintained
continuously and is the difference between a clean update and an incident.

---

## 5. Choosing between hdblcm forms **[G]**

| Situation | Use |
|---|---|
| New installation | **Media** hdblcm from the extracted archive |
| Update to a new revision | **Media** hdblcm of the *target* revision |
| Add/remove hosts, roles, network, rename | **Resident** hdblcm — `/hana/shared/<SID>/hdblcm/hdblcm` |
| Resident hdblcm missing | SAP Note **2651885** |
| Update media not found | SAP Note **3469115** |
