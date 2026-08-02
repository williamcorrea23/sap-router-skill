# SAP application & standalone-component logs

Reference detail for [../SKILL.md](../SKILL.md). Paths shown UNIX (`/usr/sap/…`); Windows uses the same
tree under the SAP drive with `\`.

## Instance work-directory trace files (full)

`/usr/sap/<SID>/<INST><nr>/work/`

| File | Component | Raise trace via |
|------|-----------|-----------------|
| `dev_disp` | dispatcher | `rdisp/TRACE` (0–3) |
| `dev_w<n>` | work process n | `rdisp/TRACE`; per-component via SM50 |
| `dev_ms` | message server | `ms/trace` / `rdisp/TRACE` |
| `dev_rd` | gateway | `gw/logging`, `gw/trace` |
| `dev_icm` | ICM | `icm/trace_level` (0–3) |
| `dev_rfc.trc`, `dev_rfc<n>` | RFC | `rfc/trace`, ST05/RFC trace |
| `dev_enq`, `enserver.*` | enqueue server | enqueue profile params |
| `dev_igs*` | IGS | IGS trace config |
| `dev_sapstartsrv` | sapstartsrv | `service/trace` |
| `stderr<n>` | instance stdout/stderr per start | — |
| `available.log`, `sapstart.log` | start service | — |

> **Raise trace only for diagnosis, then lower it** — high trace levels fill the work directory fast and
> slow the system. Reset live traces cleanly: **SM50** (WP), **SMGW** (gateway), **SMICM** (ICM) →
> menu *Reset Trace* — rather than deleting the active file.

## Trace-level parameters (RZ11 / profile)

| Parameter | Controls | Range |
|-----------|----------|-------|
| `rdisp/TRACE` | dispatcher + WP | 0 (errors) – 3 (full) |
| `icm/trace_level` | ICM / Web Dispatcher | 0 – 3 |
| `gw/logging` | gateway security/logging | action string |
| `ms/trace` | message server | 0 – 3 |

Change transiently in **RZ11** (dynamic where allowed) or persist in the instance profile; some need a
restart ([sap-system-lifecycle](../../sap-system-lifecycle/SKILL.md)).

## Standalone components

### SAP Web Dispatcher
- Logs/traces in the Web Dispatcher instance dir: **`dev_webdisp`** (main trace), **`dev_webdisp_log`**
  (start/stop/config), plus ICM-style HTTP logging.
- Trace level: `icm/trace_level`; HTTP access log: `icm/HTTP/logging_<n>`. Reset via the Web Dispatcher
  admin UI (`/sap/wdisp/admin`) or SMICM-equivalent. [G3]

### SAProuter
- Enable a **level-2 trace** and logging (usually at SAP support's request): start with
  `saprouter -r -T <tracefile>` (trace) and `-L <logfile>` / connection logging; the route permission
  file is `saprouttab`. Exact flags per **SAP KBA 3570238**. [G5]

### SAP Cloud Connector (SCC)
- In the SCC install `log/` directory:
  - **`ljs_trace.log`** — main Java trace (Cloud Connector code); rotates, default **20 files × 50 MB**.
  - `scc_core.trc`, `scc_ui.trc`, audit logs.
- Adjustable and downloadable from the **Cloud Connector admin UI** (Log And Trace Files). [G4]

### SAP Host Agent
- `/usr/sap/hostctrl/work/` — **`dev_saphostexec`**, `dev_sapstartsrv`, host-agent operation logs.
  Check these when `sapcontrol`/monitoring can't reach a host.

### Standalone Gateway / Enqueue Replication
- Standalone gateway: `dev_rd` in its own instance dir. ERS: `dev_enqr`/`enrepserver.*`.

## Sources

Same as [../SKILL.md](../SKILL.md) §Sources: SAP support log map [G1], Web Dispatcher traces [G3], Cloud
Connector logging [G4], SAProuter KBA 3570238 [G5]. Trace parameters: RZ11 / profile documentation on
help.sap.com.
