# ABAP MCP Server

Standalone MCP Server für agentives ABAP-Development — 67 Tools via ADT REST API.

---

## Top-Features — was diesen MCP unterscheidet

Die ABAP-MCP-Landschaft reicht von reinen Read-only-ADT-Wrappern bis zu großen Tool-Sammlungen. Dieser Server verfolgt einen anderen Schwerpunkt: nicht *möglichst viele* Tools, sondern **qualitativ hochwertige, agentengetriebene Entwicklung gegen real erreichbare Systeme**. Die folgenden drei Punkte gibt es in dieser Kombination bei keinem anderen ABAP-MCP-Server:

### 🧹 Clean ABAP als erzwungener Workflow — nicht als Linter-Nachgedanke
Andere Server bieten bestenfalls einen optionalen Lint-Aufruf. Hier ist Clean Code in den Entwicklungsprozess **eingebaut**: Der `abap_develop`-Prompt erzwingt einen **6-Schritte-Workflow** (Kontextanalyse → Referenzrecherche → Clean-ABAP-Check → Code-Platzierung → Implementierung → Qualitätsprüfung). Zusätzlich liegt eine Claude-Code-Skill `clean-abap` bei, die den [Clean-ABAP-Styleguide](https://github.com/SAP/styleguides) automatisch anwendet, sobald Code geschrieben oder reviewt wird, plus `review_clean_abap` und `search_clean_abap` als Werkzeuge. Ergebnis: Der Agent produziert styleguide-konformen Code — ohne dass du ihn ständig daran erinnern musst.

### 🔍 DDIC-Validierung VOR dem Coding — gegen Halluzination an der Wurzel
Mit `validate_ddic_references` prüft der Agent Tabellen-, Struktur- und Feldnamen **gegen das echte Data Dictionary, bevor** er sie im Code verwendet. Das eliminiert die häufigste Halluzinationsquelle bei ABAP-Generierung — erfundene Feldnamen, die sonst erst bei der Aktivierung auffliegen. Andere Server prüfen Code erst *nachträglich* per Syntaxcheck oder ATC; hier wird die Fehlerquelle *vorab* abgeschnitten.

### 🌐 Vier Netzwerk-Routing-Modi — erreicht Systeme, die andere nicht erreichen
Die meisten ADT-Bridges sprechen nur direktes HTTPS. Dieser Server probiert vier Modi in fester Reihenfolge und nimmt den ersten konfigurierten: **BTP Connectivity Proxy → SAProuter-NI-Tunnel → HTTP-CONNECT-Proxy → direktes HTTPS**. Damit erreichst du das ABAP-System auch in klassischen B2B-VPNs (nur Port 3299 offen) und in hybriden CAP-/Cloud-Connector-Szenarien — Konstellationen, an denen reine HTTPS-Wrapper scheitern.

### Weitere starke Merkmale

- **🚀 Lokale `.abap`-Datei + Bulk-Push — 15 Minuten → Sekunden** — Andere KI-Ansätze schreiben ABAP-Code zeichenweise direkt in das ADT-System; bei einem großen Programm dauert das bis zu **15 Minuten pro Schreibvorgang**. Dieser Server arbeitet stattdessen mit einer lokalen `.abap`-Datei: der Agent editiert lokal, und `write_abap_source` pusht den vollständigen Stand in einem einzigen ADT-API-Aufruf — in **Sekunden**. Bei 10 iterativen Korrekturen sind das bis zu **150 gesparte Minuten** pro Session.

- **🔁 Rekursives Coding bis zur erfolgreichen Aktivierung** — Der Write-Workflow läuft `lock → write → Syntaxcheck → aktivieren → unlock` und **aktiviert nur bei sauberem Syntaxcheck**. Schlägt etwas fehl, bekommt der Agent die konkrete Fehlerliste zurück und korrigiert iterativ weiter, bis das Objekt fehlerfrei aktiviert ist. Du erhältst aktivierten, lauffähigen Code statt eines Entwurfs mit roten Markern.
- **🎯 Deferred Tools — ~75–80 % Token-Ersparnis** — Statt alle 67 Tools in jeden Kontext zu laden, startet der Server mit nur **13 Core-Tools**. Der Rest wird bei Bedarf über das Meta-Tool `find_tools` aktiviert (`find_tools(category=…)` oder `find_tools(query=…)`).
- **✂️ Method-Level Surgery** — `read_abap_method` / `edit_abap_method` lesen bzw. ersetzen einen einzelnen `METHOD…ENDMETHOD`-Block. Der Agent gibt nicht mehr die ganze Klasse aus, um eine Methode zu ändern — der Server splittet den neuen Rumpf server-seitig in die Quelle und durchläuft den normalen Write-Workflow. Größter Token-Hebel bei iterativem Coding.
- **🗜️ Dependency Contracts** — `get_abap_contract` (und `analyze_abap_context(mode=contract)`) komprimieren eine Klasse/Interface auf ihre öffentliche Signatur-Oberfläche ohne Methodenrümpfe — typischerweise 5–10 % der Quellgröße. So bekommt der Agent die API einer Abhängigkeit billig, bevor er dagegen codet.
- **⚡ Source-Cache** — TTL-Cache für `getObjectSource` (`SOURCE_CACHE_TTL_MS`, Default 30 s); wiederholte Reads treffen den Cache, Writes/Deletes invalidieren automatisch — nie veralteter Quelltext nach einer Mutation.
- **🧰 Intent-Facade** — vier konsolidierte Verben `SAPRead`/`SAPWrite`/`SAPSearch`/`SAPDiagnose` für Clients, die eine kleine Tool-Oberfläche statt 67 Einzeltools wollen. Reine Routing-Schicht — alle Safety-Guards bleiben aktiv.
- **🛂 Governance (Rollen + Audit)** — Rollen `viewer`/`developer`/`admin` (`SAP_ROLE`) schränken zusätzlich zu den ALLOW_*-Flags ein; jede verändernde Aktion wird als JSON-Audit-Zeile nach STDERR (und optional `AUDIT_LOG_FILE`) protokolliert.
- **🕸️ Impact-Analyse** — `get_call_graph` rendert den rekursiven Where-Used-Graph als Mermaid-Diagramm; `find_dead_code` markiert Objekte ohne eingehende Verwendungen als Löschkandidaten.
- **🧠 Voller Kontext vor dem Schreiben** — `analyze_abap_context`, `where_used` und `read_abap_source(includeRelated=true)` lesen rekursiv alle verbundenen Objekte (Includes, Funktionsbausteine, Klassen), damit der Agent das gesamte Programm versteht, bevor er es anfasst.
- **⚡ Sichere Ad-hoc-Ausführung** — `execute_abap_snippet` führt Code in einem temporären `$TMP`-Programm aus und **löscht es immer** (auch bei Laufzeitfehlern). Eine statische Verbotsliste (`COMMIT WORK`, DB-`INSERT/UPDATE/DELETE`, …) blockiert datenverändernde Operationen vorab.
- **🛡️ Default-sichere Safety-Guards** — Schreiben, Löschen und Ausführen sind standardmäßig **deaktiviert** und müssen explizit freigeschaltet werden. Kundennamensraum-Zwang (Z/Y) und `BLOCKED_PACKAGES` schützen SAP-eigene Objekte. PROD bleibt komplett gesperrt.
- **🔒 Concurrency-Safe** — Serieller Write-Lock und Stateful-Sessions mit automatischer Lock-Recovery verhindern Konflikte bei parallelen Schreiboperationen.
- **📚 Integrierte SAP-Doku-Suche** — `search_sap_web`, `fetch_url` (liest beliebige URLs inkl. SPAs wie das SAP Help Portal) und versionsabhängige help.sap.com-Verweise (`SAP_ABAP_VERSION`) liefern dem Agenten aktuelle, korrekte Referenzen statt veraltetem Trainingswissen.

### Token-effizient arbeiten — Beispiele

```jsonc
// Nur die API-Oberfläche einer Abhängigkeit holen (statt der ganzen Klasse):
get_abap_contract({ objectUrl: "/sap/bc/adt/oo/classes/zcl_billing" })

// Eine einzelne Methode lesen bzw. ersetzen (statt Voll-Read/-Write der Klasse):
read_abap_method({ objectUrl: "/sap/bc/adt/oo/classes/zcl_billing", methodName: "calculate" })
edit_abap_method({ objectUrl: "/sap/bc/adt/oo/classes/zcl_billing",
                   methodName: "calculate", source: "    rv_total = iv_net * ( 1 + iv_tax )." })

// Kontext als komprimierte Contracts statt Volltext:
analyze_abap_context({ objectUrl: "...", mode: "contract" })

// Impact-Analyse vor einer Änderung:
get_call_graph({ objectUrl: "/sap/bc/adt/oo/classes/zcl_billing", depth: 2 })

// Kleine Tool-Oberfläche via Intent-Verben (delegiert an die granularen Tools):
SAPRead({ operation: "method", args: { objectUrl: "...", methodName: "calculate" } })
```

---

## Quickstart

**1. Abhängigkeiten installieren & bauen**
```bash
npm install
npm run build
```

**2. Konfiguration**
```bash
cp .env.example .env
# .env öffnen und SAP_URL, SAP_USER, SAP_PASSWORD eintragen
```

**3. Starten**
```bash
npm start
# oder direkt:
node dist/index.js
```

Wenn alles klappt, siehst du:
```
╔══════════════════════════════════════════╗
║   ABAP MCP Server v2.0 — Extended        ║
╚══════════════════════════════════════════╝
  System  : https://<SAP_SYSTEM>:<PORT>
  User    : <USERNAME>  Client: <CLIENT>  Lang: EN
  Write   : ❌ deaktiviert
  Delete  : ❌ deaktiviert
  Tools   : 13 initial (67 gesamt, deferred)
  Doku    : help.sap.com vlatest
  Prompts : 1 (abap_develop)
  ADT     : ✅ Verbunden
✅ MCP Server läuft auf stdio — bereit für Verbindungen
```

---

## Vergleich: Dieser MCP vs. SAPs offizieller „ABAP MCP Server" (Q2 2026 GA)

> ⚠️ **Namenskollision:** SAPs offizielles Angebot trägt laut [SAP News Center](https://news.sap.com/germany/2026/06/mit-agentic-ai-erreicht-abap-die-naechste-stufe-der-evolution/)
> denselben Namen wie dieses Projekt — „ABAP MCP Server". Dieses Projekt ist **kein** SAP-Produkt
> und steht in keiner Verbindung zu SAP; der `package.json`-Name `abap-mcp-server` kollidiert
> ggf. mit SAPs Produktnamen, falls dieses Paket je auf npm veröffentlicht wird.

SAP hat mit dem ABAP MCP Server (Eclipse + VS Code, Q2 2026 GA) ein ähnliches Konzept geliefert —
ein MCP-Server, aufgesetzt auf dem ABAP Language Server (IDE-unabhängige Abstraktionsschicht für
ABAP-Entwicklungsfunktionen). Drittanbieter-Agenten wie GitHub Copilot und Amazon Q docken darüber
an. Der Vergleich zeigt, wo die Unterschiede liegen:

| Feature | Dieser MCP | SAPs ABAP MCP Server |
|---|---|---|
| **Tool-Anzahl** | **67 Tools** | ~10 Capability-Kategorien |
| **IDE-Bindung** | Keine — jeder MCP-Client | Eclipse + VS Code (ADT-Core); GitHub Copilot/Amazon Q als Agenten darin |
| **Systemunterstützung** | ECC 6.0+, S/4HANA on-prem, BTP | BTP + on-prem (RFC); erster Release ABAP-Cloud-fokussiert |
| **Klassisches ABAP** (Programme, FuGr, BAPIs, Nachrichten) | ✅ Vollständig | ❌ Noch nicht (FuGr/Programme für späteren Release geplant) |
| **SAP Business Workflow (SWDD)** | ✅ `analyze_workflow` (definitions/instances/steps/agents) | ❌ |
| **CDS Views (DDLS)** | ✅ | ✅ |
| **CDS Metadata Extensions (DDLX)** | ✅ | ✅ |
| **Service Definitions (SRVD)** | ✅ | ✅ |
| **Service Bindings (SRVB) + Publish** | ✅ | ✅ |
| **Data Control Language (DCLS)** | ✅ | ✅ |
| **Behavior Definitions (BDEF)** | ✅ `create_behavior_definition` | ✅ |
| **Behavior Implementations (ABP)** | ✅ via Klassen-Tools | ✅ |
| **Method-Level Surgery** | ✅ `read/edit_abap_method` | ❌ |
| **Context Compression (Contracts)** | ✅ `get_abap_contract` | ❌ |
| **Call Graph / Dead-Code-Erkennung** | ✅ | ❌ |
| **Parallele Batch-Reads** | ✅ `batch_read` | ❌ |
| **ABAP-Snippet-Ausführung** | ✅ ephemer + Cleanup | ❌ |
| **Deferred Tool Loading** | ✅ 75–80 % Token-Ersparnis | N/A |
| **Audit-Logging** | ✅ Strukturiertes JSON | ❌ |
| **RBAC-Governance** | ✅ viewer/developer/admin | ❌ |
| **Paket-Guards + Namespace-Zwang** | ✅ | ❌ |
| **SAProuter / BTP Proxy / HTTP Proxy** | ✅ Alle 4 Routing-Modi | BTP + direkt |
| **Web-Suche** | ✅ `search_sap_web` + `fetch_url` (Tavily) | ❌ |
| **Clean ABAP Lint** | ✅ `review_clean_abap` + Skill | ✅ ATC clean-core |
| **Unit Tests** | ✅ Ausführen + Include erstellen | ✅ Generieren + Ausführen |
| **DDIC-Feldvalidierung (Pre-Write)** | ✅ Statische Analyse vor Write | ❌ |
| **RAP BDEF-Wissen** | ✅ `rap-bdef`-Skill | ✅ SAP-eigenes Modell |
| **Spezialisiertes ABAP-LLM** | ❌ (nutzt Client-Modell) | ✅ SAP-ABAP-1 |
| **Native VS Code UX** | ❌ (bewusst IDE-agnostisch) | ✅ |
| **Enterprise SLA** | ❌ Open Source | ✅ |
| **Lizenzkosten** | **Kostenlos** | AI Units (BTP-Subscription) |

**Fazit:** SAP hat ein schmaleres initiales Angebot (BTP-fokussiert, Eclipse + VS Code, ~10 Kategorien)
mit einem proprietären ABAP-Modell. Dieser Server ist breiter (alle SAP-Systeme, alle ABAP-Artefakte,
jeder MCP-Client), tiefer (67 Tools, Governance, Audit, Kontextkompression) und kostenlos.
Die einzige echte Lücke ist das spezialisierte SAP-ABAP-1 Sprachmodell.

**Quellen (Stand 2026-06-14):** [SAP Community Blog – „Entering the New Era of Agentic AI for ABAP Development"](https://community.sap.com/t5/technology-blog-posts-by-sap/entering-the-new-era-of-agentic-ai-for-abap-development/ba-p/14394643) ·
[SAP News Center DE](https://news.sap.com/germany/2026/06/mit-agentic-ai-erreicht-abap-die-naechste-stufe-der-evolution/).
Eine vollständige Tool-/API-Referenz für SAPs ABAP MCP Server ist bisher nicht veröffentlicht —
die Tabelle oben basiert auf den öffentlichen Ankündigungen, nicht auf einer 1:1-Tool-Liste.

---

## MCP-Client Konfiguration

**Wichtig:** Den Server rufst du normalerweise **nicht manuell** auf — er wird vom MCP-Client (Claude Desktop, Claude Code usw.) automatisch gestartet. Du trägst ihn einmalig in die Config ein:

### Claude Desktop

`%APPDATA%\Claude\claude_desktop_config.json` (Windows):
```json
{
  "mcpServers": {
    "abap": {
      "command": "node",
      "args": ["/pfad/zum/abap-mcp-server/dist/index.js"],
      "env": {
        "SAP_URL": "https://<SAP_SYSTEM>:<PORT>",
        "SAP_USER": "<USERNAME>",
        "SAP_PASSWORD": "<PASSWORD>",
        "SAP_CLIENT": "<CLIENT>",
        "ALLOW_WRITE": "true"
      }
    }
  }
}
```

Dann Claude Desktop neu starten — der Server läuft im Hintergrund sobald du eine Konversation öffnest.

### Claude Code

Im Projektordner `.claude/mcp.json`:
```json
{
  "mcpServers": {
    "abap": {
      "command": "node",
      "args": ["/pfad/zum/abap-mcp-server/dist/index.js"]
    }
  }
}
```

#### Clean ABAP Skill (optional, Claude Code)

Das Repo enthält eine Claude-Code-Skill `clean-abap` (`.claude/skills/clean-abap/SKILL.md`), die den Clean-ABAP-Styleguide automatisch anwendet, sobald ABAP-Code geschrieben oder reviewt wird. Sie ist bereits eingecheckt — nach dem Klonen Claude Code im Projektordner neu starten, dann greift sie automatisch. Details siehe `DOCUMENTATION.md` → Abschnitt „Claude Skills“.

### Cline (VS Code Extension)

In VS Code öffne die Cline Settings (Cline-Symbol → Settings) und gehe zu "MCP Server Configuration". Dort ergänze:

```json
{
  "mcpServers": {
    "ABAP Server": {
      "autoApprove": [
        "search_abap_objects",
        "read_abap_source",
        "where_used",
        "write_abap_source",
        "analyze_abap_context",
        "abap_develop"
      ],
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "node",
      "args": [
        "/pfad/zum/abap-mcp-server/dist/index.js"
      ],
      "env": {
        "SAP_URL": "https://<SAP_SYSTEM>:<PORT>",
        "SAP_USER": "<USERNAME>",
        "SAP_PASSWORD": "<PASSWORD>",
        "SAP_CLIENT": "<CLIENT>",
        "SAP_LANGUAGE": "EN",
        "ALLOW_WRITE": "true",
        "ALLOW_DELETE": "false",
        "ALLOW_EXECUTE": "true",
        "BLOCKED_PACKAGES": "SAP,SHD,SMOD",
        "DEFAULT_TRANSPORT": "",
        "SYNTAX_CHECK_BEFORE_ACTIVATE": "true",
        "SAP_ALLOW_UNAUTHORIZED": "true",
        "MAX_DUMPS": "20",
        "DEFER_TOOLS": "true",
        "SAP_ABAP_VERSION": "latest",
        "NODE_TLS_REJECT_UNAUTHORIZED": "0",
        "TAVILY_API_KEY": "<TAVILY_KEY>"
      }
    }
  }
}
```

**Hinweise:**
- `autoApprove` listet die Tools auf, die ohne Benutzerbestätigung ausgeführt werden dürfen. Erweitere die Liste nach Bedarf (z.B. `search_abap_syntax`, `validate_ddic_references`, `get_object_info`, `find_tools`).
- `timeout`: Maximale Laufzeit pro Tool-Aufruf in Sekunden (60 empfohlen für ATC-Checks u.ä.).
- `SAP_ALLOW_UNAUTHORIZED=true` / `NODE_TLS_REJECT_UNAUTHORIZED=0`: Nur bei Self-signed Zertifikaten (DEV-Systeme) setzen!
- `TAVILY_API_KEY`: Optional — wird für die Tools `fetch_url` und `search_sap_web` benötigt. API-Key von [tavily.com](https://tavily.com) beziehen.
- Alle `env`-Variablen können alternativ in einer `.env`-Datei im Server-Verzeichnis konfiguriert werden.

Nach dem Speichern: Cline neu starten oder die MCP-Verbindung neu laden.

---

## Credentials konfigurieren

Der Server lädt die Credentials aus der `.env`-Datei im Projekt:

```bash
# Pflicht
SAP_URL=https://<SAP_SYSTEM>:<PORT>
SAP_USER=<USERNAME>
SAP_PASSWORD=<PASSWORD>
SAP_CLIENT=<CLIENT>
SAP_LANGUAGE=EN

# Sicherheit (alle default-safe)
ALLOW_WRITE=false
ALLOW_DELETE=false
ALLOW_EXECUTE=false
BLOCKED_PACKAGES=SAP,SHD,SMOD

# Governance (Rollen & Audit)
# SAP_ROLE schränkt zusätzlich zu den ALLOW_*-Flags ein (kann nur weiter
# einschränken, nie freischalten): viewer = nur lesen, developer = write+execute
# (kein delete), admin = alles (Default = bisheriges Verhalten).
SAP_ROLE=admin
# Optionales JSON-Audit-Log aller verändernden Aktionen (zusätzlich immer nach STDERR).
AUDIT_LOG_FILE=

# Optionen
SYNTAX_CHECK_BEFORE_ACTIVATE=true
DEFER_TOOLS=true
SAP_ABAP_VERSION=latest
DEFAULT_TRANSPORT=
MAX_DUMPS=20
# Source-Cache-TTL in ms für getObjectSource (Default 30000; 0 = aus).
# Writes/Deletes invalidieren automatisch.
SOURCE_CACHE_TTL_MS=30000

# Web Search (optional — für fetch_url & search_sap_web Tools)
TAVILY_API_KEY=
```

Du brauchst die Credentials **nicht** in der MCP-Config zu wiederholen — der Server lädt sie automatisch beim Start.

**Empfohlene Einstellungen pro Umgebung:**

| Variable | DEV | QAS/TEST | PROD |
|---|---|---|---|
| `ALLOW_WRITE` | `true` | `false` | `false` |
| `ALLOW_DELETE` | `false` | `false` | `false` |
| `ALLOW_EXECUTE` | `true` | `false` | `false` |
| `SAP_ROLE` | `admin`/`developer` | `viewer` | `viewer` |

---

## Warum braucht der Server keinen Port?

Der ABAP MCP Server läuft im **stdio-Modus** (Standard Input/Output), nicht im HTTP-Modus:

- **stdio-Modus** (dieser Server) ✅
  - Der Server kommuniziert über stdin/stdout direkt mit dem Client
  - Kein HTTP-Server, kein TCP-Port nötig
  - Das ist der Standard für MCP (Model Context Protocol)
  - Wird vom Client automatisch gestartet, wenn benötigt
  - Perfekt für: Claude Desktop, Claude Code, Cline

- **HTTP-Modus** (optional, z.B. für externe Clients)
  - Server lauscht auf TCP-Port (z.B. 4847)
  - Clients verbinden sich via HTTP
  - Nötig wenn du mehrere Client-Prozesse hast oder externe Integration brauchst

**Kurz:** Du brauchst keinen Port, weil dein Client (Claude, Cline) den Server direkt startet und über stdio mit ihm spricht. Das ist schneller und sicherer.

---

## Netzwerk-Routing

Das ABAP-System muss vom Rechner, auf dem der MCP-Server läuft, erreichbar sein. Der Server unterstützt vier Routing-Modi — er probiert sie in dieser Reihenfolge und nimmt den **ersten konfigurierten**:

| Priorität | Modus | Wann sinnvoll |
|---|---|---|
| 1 | **BTP Connectivity Proxy** | Hybride CAP-Entwicklung; ABAP-System nur via Cloud Connector erreichbar |
| 2 | **SAProuter NI-Tunnel** | Klassische B2B-VPN, in denen nur Port 3299 von außen offen ist |
| 3 | **HTTP-CONNECT-Proxy** | Corporate-Proxy oder lokaler SSH-/socat-Tunnel |
| 4 | **Direkt HTTPS** | DNS und Firewall erlauben direkten Zugriff |

### Modus 1 — BTP Connectivity Proxy (empfohlen für CAP-Dev)

Routet HTTPS durch den vom BTP-Subaccount vertrauten Cloud Connector. Der MCP-Server piggybacked auf dem lokal weitergeleiteten Connectivity Proxy einer Cloud-Foundry-App, die das `connectivity`-Service gebunden hat.

**Einmalige Vorbereitung:**
```bash
# In separatem Terminal — solange aktiv lassen, wie der MCP läuft.
cf ssh <app> -N -L 20003:connectivityproxy.internal.cf.<region>.hana.ondemand.com:20003

# Im CAP-Projekt: connectivity-Service binden (einmalig)
cds bind --to <connectivity-instance> --credentials '{"onpremise_proxy_host":"localhost"}' --for hybrid
```

**MCP-Konfiguration (`.env` oder MCP-Client `env`):**
```env
SAP_URL=http://mdadneap1.example.com:44300        # http:// auf Port 20003!
SAP_BTP_CONNECTIVITY_PROXY=http://localhost:20003
SAP_BTP_CONNECTIVITY_LOCATION_ID=                  # leer = Default-CC; ggf. mit dem Diagnose-Tool ermitteln
SAP_BTP_CONNECTIVITY_CDS_BIND_FILE=/abs/path/<project>/.cdsrc-private.json
SAP_BTP_CONNECTIVITY_CDS_BIND_NAME=connectivity
SAP_BTP_CF_HOME=/abs/path/<project>                # optional, projekteigene cf-Session
```

Drei JWT-Quellen werden in dieser Reihenfolge probiert: `*_CREDS_FILE` → `*_CDS_BIND_FILE` + `*_CDS_BIND_NAME` → direkte `*_CLIENT_ID/_SECRET/_TOKEN_URL`. Details siehe [`.env.example`](.env.example).

**Hinweise zum Protokoll:**
- Connectivity Proxy auf Port **20003** ist ein HTTP-Forward-Proxy → `SAP_URL` muss `http://...` sein. Der Cloud Connector übernimmt die Backend-TLS.
- Auf Port **20004** spricht der Proxy CONNECT-Tunneling → `SAP_URL=https://...`.
- Der Cloud Connector muss `/sap/bc/adt/*` als Resource freigeben.

**Diagnose:**
```bash
npm run diag:btp-proxy           # End-to-End-Probe gegen SAP_URL/sap/bc/adt/discovery
npm run diag:btp-token           # XSUAA-JWT-Claims anzeigen (subaccount, audience, scope)
npm run diag:btp-destination -- --list             # alle Destinations auflisten
npm run diag:btp-destination -- <DESTINATION_NAME> # Location-ID + virtual host ermitteln
npm run diag:adt                                   # End-to-End-Test via getClient()
```

### Modus 2 — SAProuter NI-Tunnel

```env
SAP_URL=https://<target-host>:<port>
SAP_ROUTER=/H/saproutprd.example.com/S/3299        # oder kurz: host:port
# SAP_ROUTER_PASSWORD=                              # falls saprouttab Passwort verlangt
# SAP_ROUTER_DEBUG=true                             # NI-Frames auf stderr
```
Voraussetzung: der `saprouttab` muss eine Permit-Regel für (deine Quelle → target host:port) enthalten. Sonst antwortet der SAProuter mit `NI_RTERR`. Die Backend-Hosts müssen außerdem HTTPS auf dem genannten Port wirklich akzeptieren (Web Dispatcher oder ICM `icm/server_port`).

### Modus 3 — HTTP-CONNECT-Proxy

```env
SAP_PROXY_URL=http://proxy.corp.example.com:8080    # oder http://localhost:8443 (SSH-Tunnel)
```
Standard-Env-Variablen `HTTPS_PROXY` / `HTTP_PROXY` werden ebenfalls honoriert.

### Modus 4 — Direkt HTTPS

Keine zusätzlichen Variablen. Falls das Backend ein selbst signiertes Zertifikat hat, zusätzlich `SAP_ALLOW_UNAUTHORIZED=true` (nur DEV-Systeme).

### Was NICHT in `SAP_URL` gehört
- **SAProuter-Routes** (`/H/.../S/...`): SAProuter spricht SAP-NI-Binärprotokoll, nicht HTTP. Gehört in `SAP_ROUTER`.
- **Cloud-Connector-virtual-host-only-Pfade**: das ist die `SAP_URL`. Der Pfad-Präfix-Mapping macht der Cloud Connector.

---

## Authentifizierung & Connectivity — unterstützte Verfahren

Übersicht, welche Auth- und Connectivity-Mechanismen dieser Server abdeckt — und welche bewusst (noch) nicht, im Vergleich zu anderen ABAP-MCP-Implementierungen, die z.B. zusätzlich RFC, mTLS-Client-Zertifikate, Kerberos/SPNEGO oder den SAP BTP Destination Service mit Principal Propagation anbieten.

### ✅ Unterstützt

| Mechanismus | Wo greift es | Details |
|---|---|---|
| **Basic Auth** (User/Passwort) | ADT REST API | `SAP_USER` / `SAP_PASSWORD` — einziger Auth-Mechanismus gegen das ABAP-Backend selbst |
| **XSUAA Client-Credentials (JWT)** | BTP Connectivity Proxy | Signiert nur den Tunnel zum Cloud Connector (`Proxy-Authorization`-Header), **nicht** die ADT-Session selbst — siehe Abschnitt „BTP Connectivity Proxy" oben |
| **SAProuter NI-Tunnel** (optional mit Router-Passwort) | Transport-Layer | `SAP_ROUTER`, `SAP_ROUTER_PASSWORD` |
| **HTTP-CONNECT-Proxy** | Transport-Layer | `SAP_PROXY_URL` / `HTTPS_PROXY` / `HTTP_PROXY` |
| **Self-signed-Zertifikate** (TLS-Verifikation deaktivierbar) | ADT-Verbindung + Web-Calls | getrennt geregelt: `SAP_ALLOW_UNAUTHORIZED` (ADT) vs. `WEB_ALLOW_UNAUTHORIZED` (Tavily) |

### ❌ Nicht unterstützt (Stand v2.0)

| Mechanismus | Wofür man es braucht | Alternative in diesem Server |
|---|---|---|
| **mTLS-Client-Zertifikate** | X.509-basierte Systemauthentifizierung statt User/Passwort | Basic Auth; Netzwerk zusätzlich über VPN/SAProuter absichern |
| **Kerberos / SPNEGO (SSO)** | Windows-AD-Integration ohne Passwort im Klartext | Basic Auth — Credentials liegen in `.env` |
| **RFC/BAPI-Direktverbindungen** (`node-rfc`) | Funktionsbaustein-Aufrufe ohne ADT-Wrapper | `execute_abap_snippet` kann Funktionsbausteine per `CALL FUNCTION` aufrufen |
| **SAP BTP Destination Service** (Laufzeit-Lookup, Principal Propagation) | Zentrale Credential-Verwaltung, User-Identity-Weiterleitung an das Backend | Statische `.env`-Credentials bzw. BTP-Connectivity-Service-Key (siehe Modus 1) |
| **SSE / HTTP-MCP-Transport** | Mehrere Clients gegen einen laufenden Server-Prozess | Nur **stdio** (siehe „Warum braucht der Server keinen Port?“) — pro Client startet der MCP-Client einen eigenen Server-Prozess |

Diese Lücken sind bewusste Scope-Entscheidungen für v2.0 (Fokus: Single-User-Dev-Workflow gegen ein ADT-System). Für Multi-User-/Enterprise-Szenarien mit zentraler Identity-Verwaltung wären RFC-, mTLS-, Kerberos- oder Destination-Service-Integration sinnvolle, aber eigenständige Erweiterungen.

---

## Troubleshooting

**"ADT Fehler: User ist currently editing..."**
- Der Server versucht, eine Datei zu sperren, die schon gesperrt ist (z.B. von einem vorherigen Fehler).
- Lösung: SAP Studio öffnen und die Lock-Session beenden, oder Server neu starten.

**Include-Aktivierungsfehler**
- Includes können nicht standalone aktiviert werden. Der Server erkennt das automatisch und aktiviert die Include im Kontext des Hauptprogramms. Falls nötig, `mainProgram`-Parameter beim Schreiben angeben.

**"SAP_URL, SAP_USER and SAP_PASSWORD must be set"**
- `.env`-Datei fehlt oder Server wurde aus dem falschen Verzeichnis gestartet. Bei Cline: `cwd`-Feld in der MCP-Config prüfen.

**Connection refused / `ENOTFOUND <host>`**
- VPN aktiv? SAP-System erreichbar? URL korrekt? `nslookup <host>` muss von dieser Maschine funktionieren — falls nicht, ist es kein Codeproblem, sondern DNS/VPN.

**BTP Connectivity Proxy: HTTP 503 "no SAP Cloud Connector matching the requested tunnel"**
- Falsche Subaccount-Audience im JWT (z.B. Service-Key aus anderem Subaccount) oder fehlende/falsche `SAP_BTP_CONNECTIVITY_LOCATION_ID`.
- `npm run diag:btp-token` zeigt die `zid` (Subaccount-ID) und `aud` des Tokens an.
- `npm run diag:btp-destination -- --list` zeigt alle in deinem Subaccount konfigurierten Location-IDs.

**BTP Connectivity Proxy: HTTP 405 "HTTPS proxying is not supported"**
- `SAP_URL` ist `https://...`, aber der Proxy läuft auf dem HTTP-Forward-Port (20003). Entweder `SAP_URL` auf `http://` umstellen oder die SSH-Weiterleitung auf Port 20004 setzen.

**`cf service-key` schlägt fehl (login expired / no org targeted)**
- Der Server gibt eine präzise Fehlermeldung mit `cf`-Befehl-Vorschlag aus. Üblicherweise reicht: `CF_HOME=<projekt> cf login --sso`.

**Self-signed Zertifikat (nur DEV)**
- `SAP_ALLOW_UNAUTHORIZED=true` setzen. Niemals in Produktion!
