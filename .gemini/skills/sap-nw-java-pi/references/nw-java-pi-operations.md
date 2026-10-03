# AS Java / PI — extended reference

Companion to the parent skill. **[V]** = SAP Note 1514898 v112, **[LV]** = live-verified on PI 7.50,
**[G]** = cited.

---

## 1. Adapter → trace location table **[V]**

Set these in NWA → *Troubleshooting → Logs and Traces → Log Configuration* (severity ALL), reproduce,
**revert immediately**.

| Adapter / area | Primary locations |
|---|---|
| File | `com.sap.aii.adapter.file` |
| JDBC | `com.sap.aii.adapter.jdbc` |
| SFTP | `com.sap.aii.adapter.sftp` |
| JMS | `com.sap.aii.adapter.jms` (+ third-party client libs under `j2ee/cluster/bin/ext/com.sap.aii.adapter.lib*/lib`) |
| RFC | `com.sap.aii.af.rfc`, `com.sap.aii.adapter.rfc`, `com.sap.mw.jco` (JCo trace level >5 via NWA JCo Monitoring; Note 628962) |
| Mail | `com.sap.aii.adapter.mail`, `com.sap.aii.af.sdk.xi.net`, `...srt`, `...mo`, `...oauth` |
| SOAP | `com.sap.aii.af.mp.soap`, `com.sap.aii.adapter.soap`, `com.sap.aii.af.sdk.xi.net` (client-side HTTP trace: Note 1904944) |
| REST | `com.sap.aii.adapter.rest`, `com.sap.httpclient`, `httpclient`, `com.sap.aii.module.oauth` |
| HTTP_AAE | `com.sap.aii.adapter.http`, `com.sap.httpclient` (client trace: Note 2157425) |
| IDoc_AAE | `com.sap.aii.af.idoc`, `com.sap.mw.jco`, `com.sap.conn.jco` (+ channel/ICO screenshots, RA properties) |
| OData / SFSF | `com.sap.aii.adapter.lib`, `...odata`, `...picao`, `...sfsf` |
| WS | `com.sap.aii.adapter.ws`, `org.apache.cxf`, `com.sap.engine.services.wssec`, `...espbase` |
| Axis | `com.sap.aii.axis`, `org.apache.axis`, SSL set below |
| AS2 / OFTP | `com.sap.aii.adapter.as2` / `...oftp` + `com.sap.aii.security.lib.net.ssl`, `com.sap.security.core.server.https.IAIK` |
| EDI Separator | `com.sap.aii.adapter.ediseparator` |
| Mapping runtime | `com.sap.aii.adapter.xi.mapping`, `com.sap.aii.ibrun`, `com.sap.aii.valueMapping`, `com.sap.aii.mappingtool`, `XIRUN.*` variants |
| Java Proxy | `com.sap.aii.proxy.xiruntime`, `com.sap.xi.services` |
| Routing (java-only) | `com.sap.aii.adapter.xi.routing` |
| Alerting | `com.sap.aii.af.service.alert`, `...alerting`, `com.sap.aii.alert` |
| Auth / SSL | `com.sap.engine.services.ssl`, `...keystore`, `com.sap.security.core.server.https`, `com.sap.aii.security.lib.net.ssl`, `com.sap.security.core.server.https.IAIK`, `com.sap.security.saml2` |
| AFW scheduler | `com.sap.aii.af.service.scheduler`, `...lib.scheduler`, `...app.scheduler` + `/AdapterFramework/scheduler/scheduler.jsp?xml` (download, don't copy-paste) |
| Versioning/transport | `com.sap.aii.ib.server.transport`, `...versioning`, `com.tssap.dtr.pvc.versionmg`; CTS side: `com.sap.aii.ibtransportclient*` |
| Deploy failures | `com.sap.engine.services.deploy` |

**HTTP raw tracing** **[V]**: provider `com.sap.engine.services.httpserver.HttpTraceRequest.traceRaw`
/ `HttpTraceResponse.traceRaw`; client `com.sap.httpclient.traceRaw`, `com.sap.engine.services.ws.http.Client`.

---

## 2. Thread dumps — the universal hang evidence **[V]**

- **When:** TBDL pile-ups, DLNG predecessors, hanging CPA cache updates, any "it's just slow".
- **How many:** 3–5 dumps, 20–30 s apart (Note 710154 per platform; `sapcontrol -nr <nr> -function
  J2EEGetThreadList2` for a quick look without a dump).
- **Read with:** Thread Dump Viewer (Note 1020246); JVM Profiler for CPU/method duration
  (Note 1783031, KBA 2621050 has a video).
- Dumps land in `std_server<n>.out` / the work directory.

---

## 3. Telnet admin shell (port `5<nr>08`) **[G]**

```
telnet <host> 5<nr>08          # local/SSH vantage; administrator logon
lsc                            # list cluster nodes
jump <node-id>                 # attach to a node
list_app                       # applications + state
stop_app <app> / start_app <app>
add <service>                  # load command groups (e.g. add deploy)
man / help                     # discover commands per group
```

Session-scoped, works when HTTP is down, and the only scripted way into some corners of the server.
Treat `stop_app` as change-controlled. Modern releases: also reachable as `shell` via NWA in some
SPs; the raw telnet port is the dependable form.

---

## 4. ESR / Integration Directory — client requirements **[G]**

- Launch pages: `/rep/start/index.jsp`, `/dir/start/index.jsp` — these serve **Java Web Start**
  descriptors (`.jnlp`).
- A workstation needs a matching **JRE/OpenJDK with Web Start support** (IcedTea-Web on newer
  JREs, since Oracle removed Web Start after Java 8).
- Swing UI ⇒ **the tools** cannot be browser-automated or run headless. Mapping design and
  repository browsing are human tasks.
- **The objects are a different matter.** The Integration Directory publishes SOAP services —
  `CommunicationChannelInService` (`Query`/`Read`/`Create`/`Change`/`Delete`/`OpenForEdit`/`Revert`,
  verified live) and siblings for other object types. So configuration *content* is scriptable even
  though the *editor* is not. See parent §2a.
- Note `/dir/wsdl` itself returned **500** on the test system — the per-service `?wsdl` endpoints are
  the reliable discovery route, not a directory-wide WSDL listing. **[LV]**
- `ESR/ID cannot be accessed — "Unable to load resource"`: Note 3085217. ABAP SPROXY cannot reach
  ESR: Note 3369551 / 2957501.

---

## 5. RWB — the legacy map **[G]**

Pre-7.3 (and dual-stack) monitoring lived in the **Runtime Workbench** (`/rwb`): Component
Monitoring, Message Monitoring, End-to-End Monitoring, Alert Inbox (CCMS-based alerting). On
AEX/PO 7.3x+ its successors are `/pimon` + NWA + component-based alerting
(`com.sap.aii.af.service.alerting` for traces). If a runbook says "open RWB" on a 7.5 system, the
answer is `/pimon` — `/rwb` may still respond **[LV]** but is not where current tooling lives.

**Dual-stack reminder:** on XI/PI ≤7.31 half the story is ABAP — `SXMB_MONI`, `SXI_CACHE`, queues
`SMQ1`/`SMQ2`, `IDX1`/`IDX2`. That half is transaction-land, not this skill.

---

## 6. Scripted health check — the pattern **[LV]**

Verified working against 7.50 with plain Basic auth (no session handling):

```bash
B=http://<host>:5<nr>00
# messaging system + queues + sequence monitor entry points
curl -su "$U:$P" "$B/MessagingSystem/monitor/monitor.jsp"        # 200 = MS up
curl -su "$U:$P" "$B/CPACache/monitor.jsp"                       # 200 = cache servlet up
curl -s  -o /dev/null -w '%{http_code}' "$B/pimon"               # 200 = PIMON served
curl -s  -o /dev/null -w '%{http_code}' "$B/dir/start/index.jsp" # 200 = ID launcher served
```

Grep the monitor HTML for queue backlogs rather than screen-scraping pixel UIs. Credentials via a
secret store / env injection only — never inline in the command line of a shared host (`ps` shows
argv; prefer `curl -u "$U:$P"` with the variables injected, or `--netrc-file`).
