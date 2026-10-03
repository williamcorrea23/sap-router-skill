# HSR parameter reference

All in **`global.ini → [system_replication]`** unless noted. Every row below was read from the
per-parameter block in the *SAP HANA System Replication Guide* **2.0 SPS 08** §3.8 **[V]** — the
"System" column is the guide's own, and states **which side the parameter is set on**. Setting a
secondary-side parameter on the primary is a silent no-op.

> **Rule that catches most drift:** keep parameters **identical on both sites** wherever possible.
> Deviations surface as unexpected behaviour *during or after* a takeover, not before.
> As of **1.0 SPS 12** the primary can replicate its parameters to the secondary automatically. **[V, Note 1999880 Q17]**

## Log shipping

| Parameter | Type | Unit | Default | System |
|---|---|---|---|---|
| `logshipping_timeout` | Integer | seconds | **30** | Primary |
| `logshipping_max_retention_size` | Integer | MB | **1048576 (1 TB)** | Primary |
| `logshipping_async_wait_on_buffer_full` | Boolean | — | **true** | Primary |
| `reconnect_time_interval` | Integer | seconds | **30** | Secondary |

**`logshipping_timeout` is both the poll interval and the threshold.** The effective timeout
therefore falls between 1× and 2× the value — budget for ~60 s at the default, not 30. **[V]**

**`logshipping_max_retention_size` is per service, not per system.** The 1 TB default applies to
*every service that owns a persistence* (data + log volume). A system with a nameserver, two tenant
indexservers and an xsengine is configured for **4 TB** of retention — which can hit disk-full before
the `RetainedFree` segments are ever overwritten. Override in `global.ini`, or per service in the
service `.ini` (the service-level setting wins). **[V]**

- Set to **0** → segments needed for syncing are never reused; a log-full **halts the primary** until
  the cause is cleared.
- Set **> 0** → on reaching the limit (or a log-full) the segments are reused: the primary keeps
  running, but **the secondary can no longer sync**. That is the trade.

**`logshipping_async_wait_on_buffer_full`** — keep enabled until the initial data shipment finishes.
On **< 2.0 SPS 03** an interrupted full data shipment **restarts from scratch**. **[V]**

**`logshipping_async_buffer_size`** — set it on the high-log services (typically `indexserver.ini`),
not `global.ini`, since a global setting inflates the buffer for every service. **Broken on
2.00.080–2.00.088** (issue 350189): the setting may not take effect and the default is used; the
workaround is to set it again via `reconfigure`. **[V]**

## Operation and data shipping

| Parameter | Type | Values / Default | System |
|---|---|---|---|
| `operation_mode` | enum | `delta_datashipping` / `logreplay` / `logreplay_readaccess` — default **`logreplay`** | **Secondary** |
| `datashipping_min_time_interval` | Integer | **600 s (10 min)** | Secondary |
| `datashipping_logsize_threshold` | Integer | **5 GB** (`5*1024*1024*1024` bytes) | Secondary |
| `datashipping_parallel_channels` | Integer | **4** | Secondary |
| `datashipping_snapshot_max_retention_time` | Integer | **300** | Primary |
| `preload_column_tables` | Boolean | **true** | Primary and Secondary |

A data-shipping request is sent when **either** the time interval elapses **or**
`datashipping_logsize_threshold` is reached — whichever comes first. **[V]**

`datashipping_parallel_channels` helps only for **multi-GB** shipments where a single stream
underuses the link; overall throughput is still capped by primary-side I/O. Set **0** to deactivate. **[V]**

> `preload_column_tables` interacts with the operation mode: **`preload` is no longer available for
> `delta_datashipping` above 2.0 SPS 07.** **[V]**

## Compression, sync and retention

| Parameter | Type | Default | System |
|---|---|---|---|
| `enable_log_compression` | Boolean | **false** | Secondary |
| `enable_data_compression` | Boolean | **false** | Secondary |
| `enable_full_sync` | Boolean | **false** | Primary |
| `enable_log_retention` | enum | `auto`/`off`/`on`/`force`/`force on takeover` — default **`auto`** | Primary, Secondary |
| `enable_takeover_with_uninitialized_volumes` | Boolean | **False** | Secondary |
| `alternative_sources` | VARCHAR | *(empty)* | Secondary |

Compression is available from **1.0 SPS 09** and reduces bandwidth at CPU cost — both default off. **[V]**

`enable_takeover_with_uninitialized_volumes`: `false` = **strict** (takeover blocked unless databases
are initialized); `true` = **relaxed** (allowed once at least the system database is initialized, with
a warning for the others). **[V]**

`alternative_sources` — candidate sources to register to when the current source is unavailable:

```
alternative_sources=SiteA,SiteB,...
alternative_sources=SiteA:sync,SiteB:async,...
```

## Runtime dumps

Parameters governing automatic runtime-dump generation in replication scenarios are **not** in this
guide — they are documented in **SAP Note 2400007** (*FAQ: SAP HANA Runtime Dumps*). **[V, pointer]**

## Useful SQL / diagnostics

Via **SAP Note 1969700** (SQL statement collection):

| Statement | Purpose |
|---|---|
| `HANA_Replication_SystemReplication_KeyFigures` | Historical key figures — **> 1.0 SPS 09** |
| `HANA_Replication_SystemReplication_LogShipping_RetentionTime` | Max tolerable disconnection in `logreplay` before retained segments are lost — **> 1.0 SPS 11** |
| `HANA_Replication_TenantCopy` | Monitor tenant copy/move (uses the same mechanics as HSR) |
| `HANA_Memory_PageMemory` | Page-cache dispositions on the secondary |

From **1.0 SPS 11**, secondary-site monitoring views are exposed on the primary under the schema
**`_SYS_SR_SITE_<site_name>`**. **[V]**
