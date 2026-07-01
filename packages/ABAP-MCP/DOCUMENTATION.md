# ABAP MCP Server v2 — Dokumentation

> Standalone MCP Server für agentives ABAP-Development.  
> Vollständige Tool-Parität mit vscode_abap_remote_fs MCP + Write-Erweiterungen.

---

## Inhaltsverzeichnis

1. [Überblick](#überblick)
2. [Architektur](#architektur)
3. [Installation & Setup](#installation--setup)
4. [Konfiguration (.env)](#konfiguration-env)
5. [MCP Client Integration](#mcp-client-integration)
6. [Tool-Referenz](#tool-referenz)
   - [SEARCH — Objektsuche](#search--objektsuche)
   - [READ — Lesen](#read--lesen)
   - [WRITE — Schreiben](#write--schreiben)
   - [CREATE — Anlegen](#create--anlegen)
   - [DELETE — Löschen](#delete--löschen)
   - [TEST — Unit Tests](#test--unit-tests)
   - [QUALITY — Codequalität](#quality--codequalität)
   - [DIAGNOSTICS — Diagnose](#diagnostics--diagnose)
   - [TRANSPORT — Transporte](#transport--transporte)
   - [ABAPGIT — Git-Integration](#abapgit--git-integration)
   - [QUERY — SQL-Abfragen](#query--sql-abfragen)
   - [DOCUMENTATION — SAP-Dokumentation](#documentation--sap-dokumentation)
7. [MCP Prompts](#mcp-prompts)
   - [abap_develop — Entwicklungsworkflow](#abap_develop--entwicklungsworkflow)
8. [ADT Write-Workflow](#adt-write-workflow)
9. [Sicherheitskonzept](#sicherheitskonzept)
10. [ADT Objekt-URL Referenz](#adt-objekt-url-referenz)
11. [Fehlerbehebung](#fehlerbehebung)
12. [Bekannte Einschränkungen](#bekannte-einschränkungen)

---

## Überblick

Der ABAP MCP Server ermöglicht KI-Assistenten (Claude, GitHub Copilot, Cursor usw.) direkten
Zugriff auf ein SAP ABAP-System über die ADT REST API — ohne VS Code als Brücke.

**59 Tools** in 16 Gruppen + 2 Meta-Tools + 1 MCP Prompt decken den kompletten ABAP-Entwicklungsworkflow ab:

| Gruppe | Anzahl Tools | Beschreibung |
|--------|-------------|--------------|
| SEARCH | 2 | Objektsuche mit Wildcards, Quellcode-Volltextsuche |
| READ | 13 | Quellcode, **einzelne Methode** (`read_abap_method`), **Contract** (`get_abap_contract`), Metadaten, Where-Used, Code Completion, Definitionen, Revisionen, DDIC, Tabellenfelder, Tabelleninhalte, Fix-Vorschläge, Kontext-Analyse |
| WRITE | 5 | Quellcode schreiben, **einzelne Methode ersetzen** (`edit_abap_method`), aktivieren, Massen-Aktivierung, formatieren |
| CREATE | 13 | Programme, Klassen, Interfaces, FuGr, CDS, Tabellen, Messages, CDS Metadata Extensions, Service Definitions, Service Bindings, DCL, Behavior Definitions |
| DELETE | 1 | Objekte löschen |
| TEST | 2 | Unit Tests ausführen, Test-Includes erstellen |
| QUALITY | 4 | Syntaxcheck, ATC-Prüfungen, DDIC-Feldvalidierung, Clean ABAP Code-Review |
| DIAGNOSTICS | 4 | Short Dumps, Performance Traces |
| TRANSPORT | 3 | Transport-Infos, Transport-Inhalte, Transport erstellen |
| ABAPGIT | 2 | Repos auflisten, Pull ausführen |
| QUERY | 4 | Workflow-Analyse, SELECT-Statements, inaktive Objekte, ABAP-Snippets ausführen |
| DOCUMENTATION | 5 | ABAP-Keyword-Doku, Klassen-Doku, Modul-Best-Practices, Clean ABAP, ABAP-Syntax |
| WEBSEARCH | 2 | URL-Inhalte lesen (`fetch_url`), Websuche in SAP Help, Community & Notes |
| BATCH | 1 | Parallele Ausführung mehrerer Read-Only-Tools in einem MCP-Call |
| ANALYSIS | 2 | Where-Used-Call-Graph (Mermaid), Dead-Code-Erkennung |
| INTENT | 4 | Konsolidierte Verben `SAPRead`/`SAPWrite`/`SAPSearch`/`SAPDiagnose` |
| META | 2 | Tool-Finder und Tool-Übersicht für dynamische Tool-Registrierung |
| PROMPTS | 1 | `abap_develop` — Intelligenter ABAP-Entwicklungsworkflow |

> **Token-Optimierung:** Mit `DEFER_TOOLS=true` (Default) werden initial nur 12 Kern-Tools geladen.
> Weitere Tools werden on-demand über `find_tools` aktiviert — das spart ~75-80% Tokens pro `tools/list`-Aufruf.
> Die vier **INTENT**-Verben (`SAPRead`/`SAPWrite`/`SAPSearch`/`SAPDiagnose`) sind immer im Core und decken
> die häufigsten granularen Tools ab (`read_abap_source`, `write_abap_source`, `search_abap_objects` usw.) —
> diese granularen Tools sind deferred und werden bei Bedarf über `find_tools` aktiviert.

---

## Architektur

```
Claude / MCP Client
       │  stdio (MCP Protocol)
       ▼
┌─────────────────────────────┐
│   ABAP MCP Server (Node.js) │
│   src/index.ts              │
│                             │
│   ┌─────────────────────┐   │
│   │  abap-adt-api       │   │  ← TypeScript-Bibliothek
│   │  (ADTClient)        │   │    von Marcello Urbani
│   └──────────┬──────────┘   │
└──────────────┼──────────────┘
               │  HTTPS / ADT REST API
               ▼
┌──────────────────────────────┐
│   SAP NetWeaver / S/4HANA    │
│   /sap/bc/adt/* (SICF)       │
└──────────────────────────────┘
```

Der Server läuft lokal und kommuniziert über **stdio** mit dem MCP-Client.
Die SAP-Verbindung wird einmalig beim Start aufgebaut (Lazy Init) und dann wiederverwendet.

---

## Installation & Setup

### Voraussetzungen

- **Node.js** >= 20
- **SAP-System** mit aktiviertem ADT-Service (Transaktion SICF → `/sap/bc/adt` aktivieren)
- **SAP-User** mit Berechtigung `S_ADT_RES` (ADT-Zugriff)
- Für Write-Operationen: **NetWeaver >= 7.51** (oder [abapfs_extensions](https://github.com/marcellourbani/abapfs_extensions) auf dem System installiert)

### Installation

```bash
git clone <REPOSITORY_URL>
cd abap-mcp-server
npm install
npm run build
```

### SICF-Aktivierung (SAP-Seite)

Transaktion SICF ausführen und folgende Services aktivieren:

```
/sap/bc/adt/           (ADT Root — Pflicht)
/sap/bc/adt/programs/  (Programme)
/sap/bc/adt/oo/        (Klassen, Interfaces)
/sap/bc/adt/ddic/      (DDIC-Objekte)
/sap/bc/adt/atc/       (ATC — optional)
/sap/bc/adt/runtime/   (Dumps, Traces — optional)
```

---

## Konfiguration (.env)

```bash
cp .env.example .env
```

| Variable | Pflicht | Default | Beschreibung |
|----------|---------|---------|--------------|
| `SAP_URL` | ✓ | — | System-URL, z.B. `https://dev-system:8000` |
| `SAP_USER` | ✓ | — | Benutzername |
| `SAP_PASSWORD` | ✓ | — | Passwort |
| `SAP_CLIENT` | | `100` | Mandant |
| `SAP_LANGUAGE` | | `EN` | Anmeldesprache |
| `ALLOW_WRITE` | | `false` | Write-Tools aktivieren. **Nur auf DEV!** |
| `ALLOW_DELETE` | | `false` | Löschen aktivieren. Zusätzlich zu ALLOW_WRITE |
| `ALLOW_EXECUTE` | | `false` | `execute_abap_snippet` aktivieren. Zusätzlich zu ALLOW_WRITE |
| `BLOCKED_PACKAGES` | | `SAP,SHD` | Kommaliste gesperrter Paket-Präfixe |
| `DEFAULT_TRANSPORT` | | — | Standard-Transport wenn nicht angegeben |
| `SYNTAX_CHECK_BEFORE_ACTIVATE` | | `true` | Syntaxcheck vor Aktivierung erzwingen |
| `MAX_DUMPS` | | `20` | Maximale Anzahl Short Dumps |
| `SAP_ABAP_VERSION` | | `latest` | ABAP-Version für help.sap.com Dokumentation (z.B. `latest`, `758`, `754`) |
| `SAP_ALLOW_UNAUTHORIZED` | | `false` | Self-signed SSL-Zertifikate akzeptieren — nur ADT-Verbindung (nur DEV!) |
| `WEB_ALLOW_UNAUTHORIZED` | | `false` | TLS-Prüfung nur für Web-Calls (`fetch_url`/`search_sap_web`) deaktivieren — Corporate-Proxies mit TLS-Interception |
| `DEFER_TOOLS` | | `true` | Tool-Deferred-Modus: initial nur 13 Kern-Tools laden |
| `TAVILY_API_KEY` | | — | Tavily API Key (für `fetch_url` und `search_sap_web`). Free: 1000/Monat |

### Beispiel .env (Entwicklungssystem)

```env
SAP_URL=https://<SAP_SYSTEM>:<PORT>
SAP_USER=<USERNAME>
SAP_PASSWORD=<PASSWORD>
SAP_CLIENT=<CLIENT>
SAP_LANGUAGE=<LANGUAGE>
ALLOW_WRITE=true
ALLOW_DELETE=false
BLOCKED_PACKAGES=SAP,SHD,SMOD
DEFAULT_TRANSPORT=<TRANSPORT_ID>
MAX_DUMPS=50
```

> ⚠️ **Sicherheitshinweis**: Die `.env`-Datei enthält Klartext-Passwörter.  
> Datei in `.gitignore` aufnehmen und nicht committen!

---

## MCP Client Integration

### Claude Desktop (`claude_desktop_config.json`)

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

### Claude Code (`.claude/mcp.json` oder `mcp.json`)

```json
{
  "mcpServers": {
    "abap": {
      "command": "node",
      "args": ["dist/index.js"],
      "cwd": "/pfad/zum/abap-mcp-server"
    }
  }
}
```

### Cursor / Windsurf (`cursor_mcp_config.json`)

```json
{
  "mcpServers": {
    "abap": {
      "command": "node",
      "args": ["<path/to/abap-mcp-server>/dist/index.js"]
    }
  }
}
```

---

## Tool-Referenz

---

### META — Tool Discovery

#### `find_tools`

Findet und aktiviert ABAP-Tools nach Suchbegriff oder Kategorie. Wird nur im Deferred-Modus (`DEFER_TOOLS=true`) benötigt — dann werden initial nur 12 Kern-Tools geladen und weitere Tools on-demand über dieses Meta-Tool aktiviert.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `query` | string | | Suchmuster für Tool-Namen/Beschreibungen |
| `category` | string | | Kategorie: `SEARCH`, `READ`, `WRITE`, `CREATE`, `DELETE`, `TEST`, `QUALITY`, `DIAGNOSTICS`, `TRANSPORT`, `ABAPGIT`, `QUERY`, `DOCUMENTATION`, `WEBSEARCH`, `BATCH`, `ANALYSIS`, `INTENT` |
| `enable` | boolean | | Tools aktivieren/deaktivieren (Default: true) |

**Beispiele:**
```
Alle Create-Tools aktivieren
→ find_tools(category="CREATE")

Tools zum Thema "test" finden
→ find_tools(query="test")

Kategorieübersicht anzeigen
→ find_tools()
```

**Kern-Tools (immer verfügbar):** `find_tools`, `list_tools`, `analyze_abap_context`, `search_abap_syntax`, `validate_ddic_references`, `batch_read`, `fetch_url`, `search_sap_web`, `get_abap_contract`, `SAPRead`, `SAPWrite`, `SAPSearch`, `SAPDiagnose`

---

#### `list_tools`

Gibt eine kompakte Übersicht aller verfügbaren Tools mit Kurzbeschreibungen zurück, gruppiert nach Kategorie. Zeigt welche Tools aktiv (core/enabled) vs. deferred sind. Aktiviert **keine** Tools — nutzt man nur zur Orientierung.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `category` | string | | Filter nach Kategorie: `SEARCH`, `READ`, `WRITE`, `CREATE`, `DELETE`, `TEST`, `QUALITY`, `DIAGNOSTICS`, `TRANSPORT`, `ABAPGIT`, `QUERY`, `DOCUMENTATION`. Leer = alle. |

**Beispiele:**
```
Alle verfügbaren Tools anzeigen
→ list_tools()

Nur READ-Tools anzeigen
→ list_tools(category="READ")
```

---

### SEARCH — Objektsuche

#### `search_abap_objects`

Sucht ABAP-Objekte im System per Namensmuster. Wildcards (`*`) werden unterstützt.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `query` | string | ✓ | Suchmuster, z.B. `ZCL_*SERVICE*` |
| `maxResults` | number | | Maximale Ergebnisse (1–100, Default: 20) |
| `objectType` | string | | ADT-Typ-Filter (s. Tabelle unten) |

**Unterstützte Objekttypen (`objectType`):**

| Wert | Beschreibung |
|------|-------------|
| `PROG/P` | Programme (Reports) |
| `CLAS/OC` | ABAP-Klassen |
| `INTF/OI` | ABAP-Interfaces |
| `FUGR/F` | Funktionsgruppen |
| `DDLS/DF` | CDS Views (DDL Source) |
| `TABL/DT` | Transparente Tabellen |
| `DOMA/DE` | Domänen |
| `DTEL/DE` | Datenelemente |
| `MSAG/E` | Nachrichtenklassen |
| `SICF/SC` | ICF-Services |

**Beispiel:**
```
Suche alle Klassen die "BILLING" im Namen haben
→ search_abap_objects(query="*BILLING*", objectType="CLAS/OC")
```

---

#### `search_source_code`

Volltextsuche über allen ABAP-Quellcode im System. Findet Objekte, deren Quelltext den angegebenen Text enthält. Benötigt NW 7.31+ (ADT Text-Search-Service).

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `searchString` | string | ✓ | Suchtext, z.B. `Hallo`, `READ TABLE`, `BAPI_USER_GET_DETAIL` |
| `maxResults` | number | | Maximale Ergebnisse (1–200, Default: 50) |

**Beispiel:**
```
Finde alle Programme die "Hallo" ausgeben
→ search_source_code(searchString="Hallo")

Finde alle Stellen wo BAPI_USER_GET_DETAIL verwendet wird
→ search_source_code(searchString="BAPI_USER_GET_DETAIL")
```

**Hinweis:** Nutzt den ADT-Endpoint `/sap/bc/adt/repository/informationsystem/textsearch`. Erfordert ggf. die Business-Funktion `SRIS_SOURCE_SEARCH` auf dem SAP-System.

---

### READ — Lesen

#### `read_abap_source`

Liest den vollständigen Quellcode eines ABAP-Objekts. Mit `includeRelated=true` werden alle zugehörigen Objekte automatisch mitgelesen: Klassen-Includes (Definitionen, Implementierungen, Makros, Test-Klassen), Programm-Includes (INCLUDE-Statements aufgelöst), Funktionsgruppen-Includes.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL des Objekts |
| `includeRelated` | boolean | | Alle zugehörigen Objekte mitlesen (Default: false). Empfohlen um den vollen Kontext zu verstehen. |

**Beispiel:**
```
Lies den Quellcode von ZCL_BILLING_SERVICE mit allen Includes
→ read_abap_source(objectUrl="/sap/bc/adt/oo/classes/zcl_billing_service", includeRelated=true)
```

---

#### `get_object_info`

Liest die Struktur und Metadaten eines Objekts (Methoden, Attribute, Includes, DDIC-Felder).

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL des Objekts |

---

#### `where_used`

Findet alle Stellen im System wo ein Objekt verwendet wird.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL des gesuchten Objekts |
| `maxResults` | number | | Max. Ergebnisse (1–200, Default: 50) |

---

#### `get_code_completion`

Holt Code-Vervollständigungsvorschläge vom SAP-System für eine Cursor-Position.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL (Kontext) |
| `source` | string | ✓ | Aktueller Quellcode |
| `line` | number | ✓ | Cursor-Zeile (1-basiert) |
| `column` | number | ✓ | Cursor-Spalte (0-basiert) |

---

#### `find_definition`

Navigiert zur Definition eines Tokens (Variable, Methode, Klasse usw.) im Quellcode. Gibt URI, Zeile und Spalte der Definition zurück.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL des Quellobjekts (Kontext) |
| `source` | string | ✓ | Aktueller Quellcode |
| `line` | number | ✓ | Token-Zeile (1-basiert) |
| `startColumn` | number | ✓ | Token Start-Spalte (0-basiert) |
| `endColumn` | number | ✓ | Token End-Spalte (0-basiert) |
| `mainProgram` | string | | Hauptprogramm (für Includes) |

**Beispiel:**
```
Definition einer Methode finden
→ find_definition(objectUrl="/sap/bc/adt/oo/classes/zcl_foo", source="...", line=10, startColumn=5, endColumn=15)
```

---

#### `get_revisions`

Liest die Versionshistorie eines ABAP-Objekts. Gibt alle gespeicherten Revisionen mit Datum, Autor und Transportauftrag zurück.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL des Objekts |

**Beispiel:**
```
Versionshistorie einer Klasse abrufen
→ get_revisions(objectUrl="/sap/bc/adt/oo/classes/zcl_billing_service")
```

---

#### `get_ddic_element`

Liest detaillierte DDIC-Informationen für eine Tabelle, View, Datenelement oder Domäne. Gibt Felder, Typen, Annotationen und Assoziationen zurück.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `path` | string | ✓ | DDIC-Pfad, z.B. Tabellenname oder CDS-View-Name |

**Beispiel:**
```
Felder der Tabelle T001 anzeigen
→ get_ddic_element(path="T001")
```

---

#### `get_table_fields`

Gibt den Feldkatalog (Spalten) einer DDIC-Tabelle zurück: Feldname, ABAP-Typ, Beschreibung, Key-Flag und Länge. Nutze dieses Tool, um Tabellenstrukturen zu erkunden, bevor du SELECT-Statements schreibst oder Feldreferenzen validierst. Funktioniert für transparente Tabellen, Views und CDS-Entities.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `tableName` | string | ✓ | Name der DDIC-Tabelle (z.B. VBAK, MARA, BKPF) |

**Beispiel:**
```
Feldstruktur der Verkaufsbelege anzeigen
→ get_table_fields(tableName="VBAK")
```

**Rückgabe:** Anzahl Felder, Anzahl Schlüsselfelder, Array mit Feld-Objekten (name, type, description, isKey, length, isKeyFigure).

---

#### `get_table_contents`

Liest Tabelleninhalte direkt aus einer DDIC-Tabelle. Gibt die Daten als JSON zurück.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `tableName` | string | ✓ | Name der DDIC-Tabelle |
| `maxRows` | number | | Max. Anzahl Zeilen (1–1000, Default: 100) |

**Beispiel:**
```
Erste 10 Buchungskreise lesen
→ get_table_contents(tableName="T001", maxRows=10)
```

---

#### `get_fix_proposals`

Holt Quick-Fix-Vorschläge für eine bestimmte Position im Quellcode (z.B. fehlende Methode implementieren, Variable deklarieren).

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL des Objekts |
| `source` | string | ✓ | Aktueller Quellcode |
| `line` | number | ✓ | Fehler-Zeile (1-basiert) |
| `column` | number | ✓ | Fehler-Spalte (0-basiert) |

**Beispiel:**
```
Fix-Vorschläge für Zeile 15 abrufen
→ get_fix_proposals(objectUrl="/sap/bc/adt/oo/classes/zcl_foo", source="...", line=15, column=0)
```

---

#### `analyze_abap_context`

Analysiert den vollständigen Kontext eines ABAP-Objekts. Liest Quellcode inkl. aller Includes, erkennt referenzierte Funktionsbausteine, Klassen und Interfaces per Regex, ruft deren Metadaten ab und liefert einen strukturierten Kontext-Report. **Empfohlener Einstiegspunkt** vor jeder Code-Änderung.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL des Haupt-Objekts |
| `depth` | enum | | `shallow` = nur Hauptquelle + direkte Includes; `deep` = rekursiv alle Referenzen (Default: `deep`) |

**Rückgabe:** Strukturierter Report mit folgenden Abschnitten:

```
══ KONTEXT-ANALYSE: <OBJEKTNAME> ══

📋 PROGRAMMSTRUKTUR
  Typ, Paket, Anzahl Includes, Methoden, Attribute

📄 QUELLCODE (Main + Includes)
  Vollständiger Quellcode aller Abschnitte

🔗 REFERENZIERTE OBJEKTE
  Funktionsbausteine (mit Beschreibung)
  Klassen/Interfaces (mit Methoden-Liste)
  Statische Aufrufe

⚡ ZUSAMMENFASSUNG
  Anzahl Includes, FMs, Klassen
```

**Erkannte Referenz-Patterns:**
- `CALL FUNCTION 'FM_NAME'` → Funktionsbausteine
- `CREATE OBJECT ... TYPE classname` / `NEW classname(` → Klassen
- `CLASSNAME=>METHOD` → Statische Aufrufe
- `TYPE REF TO interface` → Interfaces

**Beispiel:**
```
Vollständigen Kontext eines Reports analysieren
→ analyze_abap_context(objectUrl="/sap/bc/adt/programs/programs/zrybak_test", depth="deep")
```

> **Hinweis:** Dieses Tool ist ein Kern-Tool und immer verfügbar (auch im Deferred-Modus). Es wird vom MCP Prompt `abap_develop` als erster Schritt im Entwicklungsworkflow verwendet.

---

### WRITE — Schreiben

> ⚠️ Alle Write-Tools erfordern `ALLOW_WRITE=true` in der `.env`.

#### `write_abap_source`

Schreibt Quellcode in ein bestehendes Objekt und führt den vollständigen ADT-Workflow aus:

```
🔒 lock → ✏️ write → 🔍 syntax check → 🚀 activate → 🔓 unlock
```

Bei Syntaxfehlern wird **nicht aktiviert** und der Lock automatisch freigegeben.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL (ohne `/source/main`) |
| `source` | string | | Vollständiger ABAP-Quellcode — nur für kurze Snippets (< 20 Zeilen). Für größere Programme `sourcePath` verwenden. |
| `sourcePath` | string | | **BEVORZUGT:** Pfad zu einer lokalen Datei mit dem ABAP-Quellcode. Schneller, günstiger und vermeidet JSON-Escaping-Probleme. |
| `transport` | string | | Transportauftrag |
| `activateAfterWrite` | boolean | | Aktivieren nach dem Schreiben (Default: true) |
| `skipSyntaxCheck` | boolean | | Syntaxcheck überspringen (Default: false) |
| `mainProgram` | string | | Hauptprogramm für Syntaxcheck von Includes — Name (z.B. ZRYBAK_AI_TEST) oder ADT-URL |

> **Hinweis:** Entweder `source` oder `sourcePath` muss angegeben werden.

---

#### `activate_abap_object`

Aktiviert ein bereits gespeichertes Objekt.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL |
| `objectName` | string | ✓ | Objektname (z.B. `ZCL_FOO`) |

---

#### `mass_activate`

Aktiviert mehrere Objekte in einem Schritt. Max. 50 Objekte pro Aufruf.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objects` | array | ✓ | Array mit `{objectUrl, objectName}` |

---

#### `pretty_print`

Formatiert ABAP-Quellcode über den SAP Pretty Printer. **Speichert nichts**, liefert nur formatierten Code zurück.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `source` | string | ✓ | Zu formatierender Quellcode |
| `objectUrl` | string | | ADT-URL für Kontext (optional) |

> **Hinweis:** Einrückung und Keyword-Schreibweise werden serverseitig konfiguriert (SE38 → Einstellungen).

---

### CREATE — Anlegen

> ⚠️ Alle Create-Tools erfordern `ALLOW_WRITE=true`.  
> Objektnamen müssen im Customer-Namespace liegen (Z/Y-Prefix).

#### `create_abap_program`

Legt ein neues ABAP-Programm an. Name muss mit `Z` oder `Y` beginnen.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `name` | string | ✓ | Programmname (max. 30 Zeichen) |
| `description` | string | ✓ | Kurztext (max. 40 Zeichen) |
| `devClass` | string | ✓ | Paket (z.B. `ZLOCAL` oder `$TMP`) |
| `transport` | string | | Leer für lokale Objekte ($TMP) |

---

#### `create_abap_class`

Legt eine neue Klasse an. Name muss mit `ZCL_` oder `YCL_` beginnen.

**Zusätzlicher Parameter:**

| Parameter | Typ | Beschreibung |
|-----------|-----|-------------|
| `superClass` | string | Superklasse, z.B. `CL_ABAP_UNIT_ASSERT` |

---

#### `create_abap_interface`

Legt ein neues Interface an. Name muss mit `ZIF_` oder `YIF_` beginnen.

---

#### `create_function_group`

Legt eine neue Funktionsgruppe an. Name muss mit `Z` oder `Y` beginnen (max. 26 Zeichen).

---

#### `create_cds_view`

Legt eine neue CDS View (DDL Source, Typ `DDLS/DF`) an. Name muss mit `Z` oder `Y` beginnen.

**Zweistufiges Muster:** Das ADT-Backend akzeptiert keinen gemischten XML-Inhalt (CDATA +
Kind-Elemente im selben Root). Daher zuerst den Shell anlegen, dann Quelle per
`write_abap_source` füllen:

```
1. create_cds_view   → legt DDLS-Objekt-Shell an (kein source-Parameter nötig)
2. write_abap_source → schreibt die CDS-DDL-Quelle (define view entity …)
```

**ADT-Technischer Hintergrund:** Der korrekte XML-Root-Namespace für DDL Sources ist
`xmlns:ddl="http://www.sap.com/adt/ddic/ddlsources"` mit Root-Element `ddl:ddlSource`.
Frühere Implementierungen nutzten `blue:blueSource` (korrekt für TABL/BDEF), was zu
`"System expected the element ddlSource"` führte. Behoben in 2026-06.

**Optionale Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `name` | string | ✅ | CDS View-Name (max. 30 Zeichen, Z/Y-Prefix) |
| `description` | string | ✅ | Kurzbeschreibung (max. 40 Zeichen) |
| `devClass` | string | ✅ | Paket, z.B. `ZLOCAL` oder `$TMP` |
| `transport` | string | | Transportauftrag |

---

#### `create_database_table`

Legt eine neue transparente Tabelle (TABL) an. Name muss mit `Z` oder `Y` beginnen (max. 16 Zeichen).

---

#### `create_message_class`

Legt eine neue Nachrichtenklasse (MSAG) an. Name muss mit `Z` oder `Y` beginnen.

---

#### `create_cds_metadata_extension`

Legt eine neue CDS-Metadata-Extension (DDLX) an. Wird verwendet, um eine CDS-View mit
UI-Annotationen zu versehen (z.B. `@UI.lineItem`, `@UI.selectionField`, `@UI.headerInfo`).
Name muss mit `Z` oder `Y` beginnen. Nach der Anlage die Quelle (`@Metadata.extension ...`)
mit `write_abap_source` füllen.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `name` | string | ✅ | Extension-Name (max. 30 Zeichen, Z/Y-Prefix) |
| `description` | string | ✅ | Kurzbeschreibung (max. 40 Zeichen) |
| `devClass` | string | ✅ | Paket, z.B. `ZLOCAL` oder `$TMP` |
| `transport` | string | | Transportauftrag |

---

#### `create_service_definition`

Legt eine neue OData-Service-Definition (SRVD) an, die CDS-Entities als OData-Service
exponiert. Name muss mit `Z` oder `Y` beginnen. Nach der Anlage die Quelle
(`EXPOSE ENTITY … AS …`) mit `write_abap_source` füllen, dann mit `create_service_binding` binden.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `name` | string | ✅ | Service-Definition-Name (max. 30 Zeichen, Z/Y-Prefix) |
| `description` | string | ✅ | Kurzbeschreibung (max. 40 Zeichen) |
| `devClass` | string | ✅ | Paket |
| `transport` | string | | Transportauftrag |

---

#### `create_service_binding`

Legt ein neues OData-Service-Binding (SRVB) an und verknüpft es mit einer Service-Definition.
Nach der Anlage mit `publish_service_binding` veröffentlichen.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `name` | string | ✅ | Binding-Name (max. 26 Zeichen, Z/Y-Prefix) |
| `description` | string | ✅ | Kurzbeschreibung (max. 40 Zeichen) |
| `devClass` | string | ✅ | Paket |
| `transport` | string | | Transportauftrag |
| `serviceDefinition` | string | ✅ | Name der SRVD-Service-Definition, z.B. `ZSD_ORDERS_SRV_D` |
| `bindingType` | string | | `V2_UI` (Fiori/SAPUI5, Default) oder `V2_WEB_API` (externe API) |

---

#### `publish_service_binding`

Veröffentlicht (aktiviert) ein OData-Service-Binding und macht den OData-Endpunkt erreichbar.
Muss nach `create_service_binding` aufgerufen werden.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `name` | string | ✅ | Service-Binding-Name, z.B. `ZSD_ORDERS_SRV_B` |
| `version` | string | | Content-Version, typischerweise `0001` (Default: `0001`) |

---

#### `create_data_control_language`

Legt eine neue CDS-Data-Control-Language-Quelle (DCLS) an für instanzbasierte
Zugriffsberechtigungen auf CDS-Views (`DEFINE ROLE …`). Name muss mit `Z` oder `Y` beginnen.
Quelle mit `write_abap_source` füllen.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `name` | string | ✅ | DCL-Source-Name (max. 30 Zeichen, Z/Y-Prefix) |
| `description` | string | ✅ | Kurzbeschreibung (max. 40 Zeichen) |
| `devClass` | string | ✅ | Paket |
| `transport` | string | | Transportauftrag |

---

#### `create_behavior_definition`

Legt eine neue RAP Behavior Definition (BDEF) an. Der Name muss **exakt** dem Root-CDS-Entity-Namen
entsprechen, auf den sich die BDEF bezieht. Name muss mit `Z` oder `Y` beginnen.

Nach der Anlage die BDL-Quelle mit `write_abap_source` schreiben — erster Ausdruck muss
`managed;`, `unmanaged;`, `projection;`, `abstract;` oder `interface;` sein. Für vollständige
BDL-Syntax steht der **`rap-bdef`**-Skill bereit.

> ⚠️ **Implementierungshinweis:** `abap-adt-api` unterstützt BDEF nicht — dieser Handler
> verwendet einen direkten `POST /sap/bc/adt/bo/behaviors`. Das ADT-Endpoint und der
> XML-Namespace folgen den SAP-Konventionen und wurden aus den Pattern der Library abgeleitet;
> bei Fehlern liefert SAP eine eindeutige Fehlermeldung mit dem korrekten Wert.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `name` | string | ✅ | BDEF-Name = Root-CDS-Entity-Name (max. 30 Zeichen, Z/Y-Prefix) |
| `description` | string | ✅ | Kurzbeschreibung (max. 40 Zeichen) |
| `devClass` | string | ✅ | Paket |
| `transport` | string | | Transportauftrag |

**Typischer RAP-Entwicklungsablauf:**

```
1. create_cds_view          → Root Entity (ZI_MY_ENTITY)
2. create_cds_view          → Projection View (ZC_MY_ENTITY)
3. create_behavior_definition → BDEF (ZI_MY_ENTITY) — gleicher Name wie Root Entity
4. write_abap_source        → BDL-Quelle (managed; strict(2); ...)
5. create_cds_metadata_extension → UI-Annotationen
6. create_service_definition → SRVD
7. create_service_binding   → SRVB
8. publish_service_binding  → OData-Endpoint aktivieren
```

---

### DELETE — Löschen

> ⛔ **Achtung**: Löschen ist **nicht rückgängig** machbar!  
> Erfordert sowohl `ALLOW_WRITE=true` als auch `ALLOW_DELETE=true`.

#### `delete_abap_object`

Löscht ein ABAP-Objekt dauerhaft aus dem System.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL des Objekts |
| `objectName` | string | ✓ | Name (zur Bestätigung) |
| `transport` | string | | Transportauftrag |

---

### TEST — Unit Tests

#### `run_unit_tests`

Führt ABAP Unit Tests für eine Klasse oder ein Programm aus.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL der Klasse oder des Programms |

**Rückgabe:** Liste der Test-Ergebnisse mit Pass/Fail-Status, Fehlermeldungen und Stack Traces.

---

#### `create_test_include`

Erstellt ein Test-Include (CCAU) für eine vorhandene Klasse und generiert die Grundstruktur für ABAP Unit Tests.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `classUrl` | string | ✓ | ADT-URL der Klasse |

**Generierter Code-Rahmen:**
```abap
CLASS ltcl_<classname> DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.
  PRIVATE SECTION.
    METHODS: test_<method> FOR TESTING.
ENDCLASS.

CLASS ltcl_<classname> IMPLEMENTATION.
  METHOD test_<method>.
    " Test-Code hier
  ENDMETHOD.
ENDCLASS.
```

---

### QUALITY — Codequalität

#### `run_syntax_check`

Führt einen ABAP-Syntaxcheck durch **ohne zu speichern**.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL (Kontext) |
| `source` | string | ✓ | Zu prüfender Quellcode |
| `mainProgram` | string | | Hauptprogramm (für Includes) |

**Rückgabe:** Liste von Meldungen mit Severity (`E`=Error, `W`=Warning, `I`=Info), Zeilennummer und Text.

---

#### `run_atc_check`

Startet eine ATC-Prüfung (ABAP Test Cockpit) für ein Objekt.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL des Objekts |
| `checkVariant` | string | | Prüfvariante (Default: `DEFAULT`) |

**Rückgabe:** Liste der Befunde mit Priorität (1=kritisch, 2=wichtig, 3=Hinweis), Kategorie, Beschreibung und Position.

---

#### `validate_ddic_references`

Analysiert ABAP-Quellcode statisch und prüft alle referenzierten Tabellenfelder gegen die DDIC-Metadaten. Findet ungültige Feldnamen **vor** dem Schreiben des Codes und verhindert so Trial-and-Error-Zyklen mit "No component exists"-Syntaxfehlern.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `source` | string | ✓ | ABAP-Quellcode der zu prüfenden Programmlogik |

**Erkannte Patterns:**

- `TYPE tablename-fieldname` — Feldtypreferenzen
- `LIKE tablename-fieldname` — Feldähnlichkeitsreferenzen

**Filter & Exceptions:**

Die Validierung ignoriert automatisch:
- Lokale Variablen-Namen (lt_*, ls_*, lv_*, gs_*, etc.) als Tabellennamen
- ABAP Built-in Typen (C, N, I, F, P, X, D, T, STRING, XSTRING)
- ABAP-interne Typen (ABAP_*, etc.)

**Rückgabe:**

Bei gültigen Feldern:
```
✅ Keine DDIC-Tabellen-Feldreferenzen gefunden. Kein Validierungsbedarf.
```

oder

```
🔍 DDIC-Feldvalidierung für 2 Tabellen/Strukturen:
  ✅ T001: 1 referenzierte Felder geprüft
  ✅ BKPF: 2 referenzierte Felder geprüft

✅ Alle 3 Feldreferenzen sind valide.
```

Bei ungültigen Feldern:
```
❌ 1 ungültige Feldreferenzen gefunden:
  ❌ T001-ABKRS: Feld nicht gefunden (Tabelle hat 20 Felder)

⚠️ Diese Felder existieren nicht in der DDIC — korrigiere die Feldnamen bevor du write_abap_source aufrufst!
💡 Tipp: Nutze get_table_fields mit dem Tabellennamen um alle verfügbaren Felder zu sehen.
```

**Empfohlener Workflow:**

```
1. Schreibe deinen geplanten ABAP-Code (lokal)
2. Rufe validate_ddic_references(source="...") auf
3. Behebe alle gefundenen Feldnamen-Fehler
4. Rufe write_abap_source auf (sollte jetzt ohne Fehler aktiviert werden)
```

**Beispiel:**

```abap
CODE mit Fehler:
DATA lv_bukrs TYPE T001-BUKRS.     ✅ Valid — BUKRS existiert
DATA lv_foo TYPE T001-ABKRS.       ❌ Invalid — ABKRS existiert NICHT

→ validate_ddic_references() findet den Fehler VOR write_abap_source
```

> **Hinweis:** Dieses Tool ist hilfreich um DDIC-Fehler früh zu erkennen, ersetzt aber nicht den kompletten Syntaxcheck durch `run_syntax_check` oder `write_abap_source`.

---

#### `review_clean_abap`

Prüft ABAP-Quellcode auf Einhaltung der Clean ABAP Richtlinien. Statische Analyse — **keine SAP-Systemverbindung erforderlich**. Erkennt Anti-Patterns und liefert zu jedem Finding den relevanten Abschnitt aus dem offiziellen Clean ABAP Styleguide.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `source` | string | ✓ | ABAP-Quellcode zur Prüfung |
| `maxFindings` | number | | Max. Anzahl Findings (1–50, Default: 10) |

**Erkannte Anti-Patterns (11 Regeln):**

| Regel | Kategorie | Beschreibung |
|-------|-----------|--------------|
| `HUNGARIAN_NOTATION` | Names | Typ-Präfixe wie `lv_`, `lt_`, `gs_` |
| `MOVE_STATEMENT` | Language | Veraltetes `MOVE ... TO` |
| `COMPUTE_STATEMENT` | Language | Veraltetes `COMPUTE` |
| `ADD_SUBTRACT` | Language | Veraltetes `ADD/SUBTRACT ... TO` |
| `MULTIPLY_DIVIDE` | Language | Veraltetes `MULTIPLY/DIVIDE ... BY` |
| `CALL_METHOD` | Language | Veraltetes `CALL METHOD` |
| `FORM_DEFINITION` | Language | `FORM`-Subroutinen statt Methoden |
| `CONCATENATE_STATEMENT` | Strings | `CONCATENATE` statt String Templates |
| `SELECT_ENDSELECT` | Tables | `SELECT...ENDSELECT` statt `INTO TABLE` |
| `CHECK_IN_METHOD` | Methods | `CHECK` in Methoden statt `IF ... RETURN` |
| `CALL_FUNCTION_SYSUBRC` | ErrorHandling | `CALL FUNCTION` + `sy-subrc` statt `TRY/CATCH` |

**Beispiel-Ausgabe:**

```
# Clean ABAP Review — 2 finding(s), 3 occurrence(s)

## [Names] HUNGARIAN_NOTATION — line 1 (2x in source)
❌ Hungarian notation prefix (e.g. lv_, lt_, gs_). Clean ABAP avoids type-encoding prefixes.
   `DATA lv_test TYPE string.`

→ Clean ABAP § **Avoid encodings, esp. Hungarian notation and prefixes**
   <Excerpt aus dem Clean ABAP Guide>

---

## [Language] MOVE_STATEMENT — line 2
❌ Obsolete MOVE ... TO. Use = operator instead.
   `MOVE lv_test TO lv_other.`

→ Clean ABAP § **Prefer functional to procedural language constructs**
   <Excerpt aus dem Clean ABAP Guide>

---
11 rules checked | 📖 clean-abap
```

> **Hinweis:** Dieses Tool ergänzt `run_atc_check` — ATC prüft System-Regeln und technische Korrektheit, `review_clean_abap` prüft Clean ABAP Style-Konventionen. Für optimale Ergebnisse beide kombinieren.

---

### DIAGNOSTICS — Diagnose

#### `get_short_dumps`

Liest die Liste der neuesten Short Dumps. Entspricht Transaktion **ST22**.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `maxResults` | number | | Max. Anzahl (1–100, Default: 20) |
| `user` | string | | Auf bestimmten User einschränken |
| `since` | string | | Zeitfilter ISO-8601, z.B. `2025-03-01T00:00:00Z` |

---

#### `get_short_dump_detail`

Liest die vollständigen Details eines Short Dumps.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `dumpId` | string | ✓ | Dump-ID aus `get_short_dumps` |

**Rückgabe:** Fehlertext, Ausnahme-Kategorie, Call Stack, lokale Variablen zum Zeitpunkt des Fehlers, Quellcode-Position.

---

#### `get_traces`

Liest die Liste der Performance Traces. Entspricht Transaktion **SAT**.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `maxResults` | number | | Max. Anzahl (1–50, Default: 10) |
| `user` | string | | Auf bestimmten User einschränken |

---

#### `get_trace_detail`

Liest die Details eines Performance Traces.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `traceId` | string | ✓ | Trace-ID aus `get_traces` |

**Rückgabe:** Gesamtlaufzeit, Anzahl DB-Zugriffe, teuerste ABAP-Statements und SQL-Selects.

---

### TRANSPORT — Transporte

#### `get_transport_info`

Gibt verfügbare Transportaufträge für ein Objekt zurück.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL des Objekts |
| `devClass` | string | ✓ | Paket des Objekts |

---

#### `get_transport_objects`

Listet alle Objekte in einem Transportauftrag auf.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `transportId` | string | ✓ | Transportnummer, z.B. `DEVK900123` |

**Rückgabe:** Liste aller transportierten Objekte mit Typ, Name und Status.

---

#### `create_transport`

Erstellt einen neuen Transportauftrag. Gibt die Transportnummer zurück. ⚠️ Erfordert `ALLOW_WRITE=true`.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL des Objekts |
| `description` | string | ✓ | Transportbeschreibung (max. 60 Zeichen) |
| `devClass` | string | ✓ | Paket |
| `transportLayer` | string | | Transport-Layer (optional) |

**Beispiel:**
```
Neuen Transport erstellen
→ create_transport(objectUrl="/sap/bc/adt/oo/classes/zcl_foo", description="Neue Billing-Logik", devClass="ZLOCAL")
```

---

### ABAPGIT — Git-Integration

#### `get_abapgit_repos`

Listet alle abapGit-Repositories auf die im System konfiguriert sind.

**Rückgabe:** Liste mit Repo-ID, Name, Remote-URL, Branch, Package und Status.

---

#### `abapgit_pull`

Führt einen abapGit Pull für ein Repository durch (importiert Code aus Git ins System).

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `repoId` | string | ✓ | Repository-ID aus `get_abapgit_repos` |
| `transport` | string | | Transportauftrag für importierte Objekte |

> ⚠️ Erfordert `ALLOW_WRITE=true`. Kann viele Objekte im System verändern!

---

### QUERY — SQL-Abfragen

#### `analyze_workflow`

Analysiert SAP Business Workflow-Metadaten (klassischer WF / Transaktion SWDD) durch Abfrage der Standard-Workflow-Tabellen via ADT SELECT. **Vollständig read-only — kein `ALLOW_WRITE` erforderlich.**

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `mode` | string | | `definitions` (Default), `instances`, `steps`, `agents`, `graph` |
| `workflowId` | string | | Workflow-ID, z.B. `WS12300111`. Pflicht für `steps`, `agents` und `graph`. |
| `status` | string | | Instanzfilter: `all` (Default), `READY`, `STARTED`, `COMPLETED`, `ERROR` — nur für `instances` |
| `user` | string | | SAP-User als Agenten-Filter — nur für `instances` |
| `maxResults` | number | | Max. Ergebnisse (1–100, Default: 20) |

**Modi im Detail:**

| Modus | Tabellen | Beschreibung |
|-------|----------|--------------|
| `definitions` | `SWF_FLEX_HEADER`, `SWFTASKI` | Alle Workflow-Templates (flexible WF NW 7.40+ und klassische WS-Tasks) |
| `instances` | `SWWWIHEAD` | Laufende/beendete Workflow-Instanzen, filterbar nach Status/User/Workflow-ID |
| `steps` | `SWF_FLEX_STEP`, `SWFSTEPDEF` | Schrittdefinitionen eines bestimmten Workflows |
| `agents` | `SWF_FLEX_ROLE`, `SWWUSERWI` | Agenten- und Rollenzuweisungen eines Workflows |
| `graph` | `SWD_NODES`, `SWD_LINES`, `SWD_STEPS`, `SWD_WFCONT` | **SWDD Schritt-zu-Schritt-Graph** mit Knoten, Kanten, Step-Details und Mermaid-Diagramm |

**Status-Labels (instances-Modus):**
- `0` WAITING, `1` READY, `2` SELECTED, `3` STARTED, `4` COMPLETED, `5` CANCELLED, `6` ERROR, `7` EXECUTED

**Beispiele:**
```
// Alle Workflow-Definitionen auflisten
analyze_workflow({ mode: "definitions" })

// Laufende Instanzen für einen bestimmten Workflow
analyze_workflow({ mode: "instances", workflowId: "WS12300111", status: "STARTED" })

// Schritte eines Workflows anzeigen
analyze_workflow({ mode: "steps", workflowId: "WS12300111" })

// Agenten-Zuweisungen analysieren
analyze_workflow({ mode: "agents", workflowId: "WS12300111" })

// SWDD Schritt-zu-Schritt-Graph mit Mermaid-Diagramm
analyze_workflow({ mode: "graph", workflowId: "WS12300111" })

// Via Intent-Facade (immer erreichbar ohne find_tools)
SAPDiagnose({ operation: "workflow", args: { mode: "definitions" } })
SAPDiagnose({ operation: "workflow", args: { mode: "graph", workflowId: "WS12300111" } })
```

**Graph-Modus Ausgabe:**

Der `graph`-Modus liefert eine vollständige Darstellung des SWDD-Workflow-Graphen:

- **Workflow Definition**: ID, Beschreibung, Ersteller, Änderungsdatum
- **Nodes-Tabelle**: Alle Knoten mit NodeID, Typ (Start/End/Activity/Condition/Fork/...), Beschreibung, Task, Block-ID, Verschachtelungsebene
- **Edges-Tabelle**: Alle Verbindungen mit Vorgänger, Nachfolger, Linientyp, Bedingung/Returncode
- **Step Details**: JSON mit detaillierten Step-Informationen (Task, Agent-Rolle, Priorität, etc.)
- **Container Elements**: Datenelemente die zwischen Steps fließen
- **Mermaid-Diagramm**: Visualisierbarer Flowchart des Workflows

**Node-Typen:**
`S`=Start, `E`=End, `A`=Activity, `C`=Condition, `D`=Decision, `F`=Fork, `J`=Join, `L`=Loop Start, `M`=Loop End, `W`=Wait, `U`=User Decision, `X`=Exception Handler, etc.

**Line-Typen:**
`N`=Normal, `C`=Condition True, `F`=Condition False, `E`=Exception, `D`=Default, `R`=Return, `T`=Timeout, `O`=Outcome

> **Hinweis:** Workflow-IDs haben das Format `WS<8 Stellen>` (z.B. `WS12300111`). Alle Workflows des Systems sind in Transaktion SWDD sichtbar. Sind Tabellen auf einem System nicht vorhanden, gibt das Tool Warnhinweise aus statt abzubrechen.

> **Systemvoraussetzung:** SAP BC-BMT-WFM (Business Workflow) muss installiert und konfiguriert sein. Auf Systemen ohne Workflow sind die Tabellen leer oder nicht vorhanden.

---

#### `run_select_query`

Führt ein SELECT-Statement direkt gegen SAP-Tabellen aus.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `query` | string | ✓ | SELECT-Statement |

**Beispiele:**
```sql
SELECT * FROM T001 WHERE MANDT = '100' UP TO 10 ROWS
SELECT BELNR, BUKRS, BLDAT FROM BKPF WHERE GJAHR = '2025' UP TO 50 ROWS
SELECT COUNT(*) FROM EKKO
```

> ⚠️ Nur lesende Zugriffe erlaubt. DML-Statements (INSERT, UPDATE, DELETE) werden vom System abgelehnt.

---

#### `execute_abap_snippet`

Führt einen temporären ABAP-Code-Schnipsel live im SAP-System aus und gibt die Ausgabe zurück. Das Programm wird in `$TMP` angelegt, sofort ausgeführt und danach automatisch gelöscht — kein permanenter Zustand im System.

Ideal für: Tabellenwerte prüfen, Berechnungen testen, API-Rückgaben inspizieren, Debugging-Hypothesen validieren.

> ⚠️ Erfordert `ALLOW_WRITE=true` **und** `ALLOW_EXECUTE=true`.
> ⚠️ Nur lesende Logik verwenden — schreibende Anweisungen werden statisch geprüft und blockiert.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `source` | string | ✓ | Vollständiger ABAP-Code. Muss mit `REPORT` oder `PROGRAM` beginnen. Ausgabe über `WRITE`. |
| `timeout` | number | | Maximale Laufzeit in Sekunden (1–30, Default: 10) |

**Workflow:**
```
1. Statische Sicherheitsprüfung (verbotene Anweisungen)
2. Temporäres Programm in $TMP anlegen (ZZ_MCP_<timestamp>)
3. Quellcode schreiben (lock → write → unlock)
4. Syntaxcheck — bei Fehlern: abbrechen
5. Aktivieren
6. Ausführen → Ausgabe zurückgeben
7. Programm löschen (immer — auch bei Fehler)
```

**Verbotene Anweisungen (statisch geprüft):**
- `COMMIT WORK`, `ROLLBACK WORK`
- `INSERT`, `UPDATE`, `DELETE`, `MODIFY` auf DB-Tabellen
- `CALL FUNCTION ... IN UPDATE TASK`
- `BAPI_TRANSACTION_COMMIT`

**Beispiele:**
```abap
Tabellenwerte prüfen
→ execute_abap_snippet(source="REPORT ztest.\nSELECT * FROM t001 INTO TABLE @DATA(lt_t001) UP TO 5 ROWS.\nLOOP AT lt_t001 INTO DATA(ls).\n  WRITE: / ls-bukrs, ls-butxt.\nENDLOOP.")

Systemvariablen ausgeben
→ execute_abap_snippet(source="REPORT ztest.\nWRITE: / sy-sysid, sy-mandt, sy-uname, sy-datum.")
```

> **Bekannte Limitation:** Ausgabe-Format hängt von der ADT-Version ab (NW 7.52+). Der `/runs`-Endpunkt ist auf älteren Systemen nicht verfügbar.

---

#### `get_inactive_objects`

Listet alle inaktiven (noch nicht aktivierten) Objekte des aktuellen Benutzers auf.

**Parameter:** Keine.

**Beispiel:**
```
Inaktive Objekte anzeigen
→ get_inactive_objects()
```

---

### DOCUMENTATION — SAP-Dokumentation

#### `get_abap_keyword_doc`

Ruft ABAP-Keyword-Dokumentation von help.sap.com ab. Liefert die offizielle SAP-Doku als formatierten Text.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `keyword` | string | ✓ | ABAP-Keyword (z.B. `SELECT`, `LOOP`, `READ TABLE`, `MODIFY`) |
| `version` | string | | ABAP-Version (z.B. `latest`, `758`, `754`). Default: `SAP_ABAP_VERSION` |

**Beispiele:**
```
SELECT-Dokumentation abrufen
→ get_abap_keyword_doc(keyword="select")

READ TABLE Dokumentation für NW 7.54
→ get_abap_keyword_doc(keyword="read table", version="754")
```

**Verhalten bei 404:** Versucht automatisch eine alternative URL mit Underscores (z.B. `read_table` statt `readtable`).

---

#### `get_abap_class_doc`

Ruft ABAP-Klassen/Interface-Dokumentation von help.sap.com ab.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `className` | string | ✓ | ABAP-Klassenname oder Interface (z.B. `CL_SALV_TABLE`, `IF_AMDP_MARKER_HDB`) |
| `version` | string | | ABAP-Version (z.B. `latest`, `758`, `754`). Default: `SAP_ABAP_VERSION` |

**Beispiel:**
```
CL_SALV_TABLE Dokumentation abrufen
→ get_abap_class_doc(className="CL_SALV_TABLE")
```

---

#### `get_module_best_practices`

Liefert modulspezifische SAP ABAP Best Practices. Jeder Eintrag enthält:
- Wichtige Tabellen & Strukturen
- Empfohlene BAPIs/Klassen (statt Direktzugriff)
- ABAP-Coding-Richtlinien (modulspezifisch)
- Häufige Fehler & Fallstricke
- S/4HANA-Migrationshinweise

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `module` | enum | ✓ | SAP-Modul: `FI`, `CO`, `MM`, `SD`, `PP`, `PM`, `QM`, `HR`, `HCM`, `PS`, `WM`, `EWM`, `BASIS`, `BC`, `ABAP` |

**Beispiel:**
```
FI Best Practices abrufen
→ get_module_best_practices(module="FI")

Allgemeine ABAP Best Practices
→ get_module_best_practices(module="ABAP")
```

> **Aliase:** `HCM` liefert HR-Inhalte, `BC` liefert BASIS-Inhalte.

---

#### `search_clean_abap`

Durchsucht den offiziellen SAP Clean ABAP Styleguide (github.com/SAP/styleguides) nach Best Practices, Namenskonventionen, Coding-Richtlinien und Anti-Patterns. Gibt die relevantesten Abschnitte zurück. **Vor dem Schreiben neuen Codes aufrufen** um Clean ABAP Konventionen einzuhalten.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `query` | string | ✓ | Suchbegriff im Clean ABAP Guide (z.B. `naming conventions`, `error handling`, `method length`) |
| `maxResults` | number | | Max. Anzahl Abschnitte (1–5, Default: 2) |

**Beispiele:**
```
Namenskonventionen nachschlagen
→ search_clean_abap(query="naming conventions")

Error Handling Best Practices
→ search_clean_abap(query="error handling", maxResults=3)
```

---

#### `search_abap_syntax`

Durchsucht die offizielle ABAP-Syntaxdokumentation von help.sap.com anhand einer Freitext-Suche. Identifiziert automatisch das Haupt-Keyword, lädt die Dokumentationsseite und gibt den relevanten Syntax-Abschnitt zurück. **Vor dem Schreiben von ABAP-Code aufrufen** um korrekte Syntax sicherzustellen.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `query` | string | ✓ | Freitext-Suche für ABAP-Syntax (z.B. `SELECT UP TO ROWS`, `LOOP AT clause order`, `READ TABLE WITH KEY`) |
| `version` | string | | ABAP-Version (z.B. `latest`, `758`, `754`). Default: `SAP_ABAP_VERSION` |

**Beispiele:**
```
SELECT-Syntax nachschlagen
→ search_abap_syntax(query="SELECT UP TO ROWS")

LOOP AT Klausel-Reihenfolge prüfen
→ search_abap_syntax(query="LOOP AT clause order")
```

> **Hinweis:** Dieses Tool ist ein Kern-Tool und immer verfügbar (auch im Deferred-Modus).

---

### Konfiguration: `SAP_ABAP_VERSION`

| Variable | Default | Beschreibung |
|----------|---------|--------------|
| `SAP_ABAP_VERSION` | `latest` | ABAP-Version für help.sap.com URLs (z.B. `latest`, `758`, `754`) |

Die Version wird für `get_abap_keyword_doc` und `get_abap_class_doc` verwendet, kann aber pro Aufruf über den `version`-Parameter überschrieben werden.

---

## MCP Prompts

### `abap_develop` — Entwicklungsworkflow

Ein MCP Prompt der einen strukturierten 6-Schritte-Workflow für ABAP-Entwicklung erzwingt. Der Prompt stellt sicher, dass die KI vor dem Coding den vollständigen Kontext erfasst, moderne ABAP-Prinzipien anwendet und Qualitätsprüfungen durchführt.

**Argumente:**

| Argument | Pflicht | Beschreibung |
|----------|---------|--------------|
| `object_name` | ✓ | Name des ABAP-Objekts (z.B. `ZRYBAK_TEST`) |
| `task` | ✓ | Aufgabe (z.B. `ALV-Grid mit CL_SALV_TABLE einbauen`) |

**Workflow-Schritte:**

1. **Kontext erfassen** — `search_abap_objects` → `analyze_abap_context(depth="deep")` → vollständigen Report lesen
2. **Referenzen recherchieren** — Veraltete Patterns erkennen, moderne Alternativen suchen (z.B. `REUSE_ALV_GRID_DISPLAY` → `CL_SALV_TABLE`). Mit `search_sap_web` SAP Notes, Blogs und Community-Lösungen zum Thema finden
3. **Clean ABAP anwenden** — Bestehenden Code mit `review_clean_abap` prüfen, Inline-Deklarationen, String Templates, funktionale Methoden, ABAP SQL, CX_*-Ausnahmen, OOP
4. **Code-Platzierung** — Richtiges Include / richtige Methode anhand des Kontext-Reports bestimmen
5. **Implementierung** — `write_abap_source` mit Retry bei Syntax-/Aktivierungsfehlern. Bei hartnäckigen Fehlern: `search_sap_web` mit der Fehlermeldung aufrufen
6. **Qualitätsprüfung** — `run_atc_check`, Findings Priorität 1+2 beheben

**Verwendung in MCP-Clients:**

Der Prompt wird über die MCP Prompt-API aufgerufen. In Claude Desktop oder anderen MCP-Clients kann er direkt als Prompt ausgewählt werden. Er generiert eine User-Message mit dem vollständigen Workflow-Template, das die KI Schritt für Schritt abarbeitet.

---

## Claude Skills

### `clean-abap` — Clean-ABAP-Styleguide als Skill

Eine projektgebundene [Claude Code Skill](https://docs.claude.com/en/docs/claude-code), die den Clean-ABAP-Styleguide automatisch heranzieht, sobald ABAP-Code geschrieben, reviewt oder refaktoriert wird. Im Gegensatz zum `abap_develop` MCP-Prompt (der explizit aufgerufen wird) greift die Skill automatisch anhand ihrer `description`.

**Speicherort:** `.claude/skills/clean-abap/SKILL.md` (in den Repo eingecheckt)

**Funktionsweise (Progressive Disclosure):**
- Claude lädt zunächst nur die `description` der Skill.
- Passt der Kontext (ABAP schreiben/reviewen/refaktorieren), wird die `SKILL.md` geladen — eine kompakte Zusammenfassung mit Golden Rules und den wirkungsvollsten/häufigsten Regeln inline.
- Erst bei Bedarf liest Claude den vollständigen `clean-abap/CleanABAP.md` (~5150 Zeilen) bzw. die Sub-Sections — die `SKILL.md` enthält dafür eine Navigations-Tabelle mit Zeilennummern. So bleibt der Token-Verbrauch gering.

**Inhalt der `SKILL.md`:**

| Block | Inhalt |
|-------|--------|
| Golden Rules | Team rules, Optimize for reading, Consistency, Boy-scout rule, OO/funktional |
| Highest-impact rules | Names, Methods, Language/Data, Booleans/Conditions/Ifs, Tables, Error Handling, Comments/Formatting, Constants, Classes, Testing — je mit Zeilenverweis |
| Reference map | 18 Sektionen von `CleanABAP.md` → Zeilennummern |
| Sub-sections | Verweise auf `clean-abap/sub-sections/` (Exceptions, Enumerations, InterfacesVsAbstractClasses, …) |
| Verifikation | code pal for ABAP, ATC/Code Inspector, abaplint + Projekt-Tools (Quality-Handler, `review_clean_abap`) |

**Konflikt-Präzedenz:** Bei Widersprüchen gilt (1) Konvention des bearbeiteten Objekts → (2) Projektkonventionen (CLAUDE.md / Memory) → (3) Clean-ABAP-Defaults. Beispiel: Vollzeilenkommentare mit `*` in Spalte 1 (Projektvorgabe) haben Vorrang vor der Clean-ABAP-Empfehlung `"`.

**Aktivierung:** Project Skills werden beim Session-Start geladen. Nach dem Anlegen Claude Code neu starten, dann greift die Skill automatisch.

**Hinweis:** Die Skill referenziert die Dateien unter `clean-abap/` über repo-root-relative Pfade. Sessions müssen vom Repo-Root laufen; wird der Ordner `clean-abap/` verschoben, müssen die Pfade in der `SKILL.md` angepasst werden.

---

## ADT Write-Workflow

Alle Write-Operationen auf Quellcode folgen diesem Protokoll:

```
┌──────────────────────────────────────────────────────────────┐
│                    ADT Write Workflow                         │
├──────────┬───────────────────────────────────────────────────┤
│ Schritt  │ Beschreibung                                       │
├──────────┼───────────────────────────────────────────────────┤
│ 1. Lock  │ POST objectUrl?_action=LOCK → lockHandle          │
│          │ Sperrt das Objekt exklusiv für diesen User         │
├──────────┼───────────────────────────────────────────────────┤
│ 2. Write │ PUT objectUrl/source/main (mit lockHandle)         │
│          │ Schreibt den Quellcode auf den Server              │
├──────────┼───────────────────────────────────────────────────┤
│ 3. Check │ POST /sap/bc/adt/abapsource/syntaxcheck            │
│          │ Syntaxfehler → STOP (kein Activate)                │
├──────────┼───────────────────────────────────────────────────┤
│ 4. Act.  │ POST /sap/bc/adt/activation                        │
│          │ Aktiviert das Objekt (Inactive → Active)           │
├──────────┼───────────────────────────────────────────────────┤
│ 5. Unlock│ DELETE objectUrl/locks/lockHandle                   │
│          │ Immer ausgeführt — auch bei Fehlern                │
└──────────┴───────────────────────────────────────────────────┘
```

**Fehlerverhalten:**
- Lock fehlgeschlagen → Exception (Objekt durch anderen User gesperrt)
- Schreiben fehlgeschlagen → Exception + Auto-Unlock
- Syntaxfehler → kein Activate + Auto-Unlock + Fehlerliste zurückgeben
- Activation fehlgeschlagen → Exception + Auto-Unlock
- Beim Auto-Unlock-Fehler → Warnung im Log (manuell in SE03 freigeben)

---

## Sicherheitskonzept

### Mehrstufige Schutzebenen

```
┌─────────────────────────────────────────────────────┐
│  ALLOW_WRITE=false (Default)                        │
│  → Alle schreibenden Tools werfen Fehler            │
├─────────────────────────────────────────────────────┤
│  ALLOW_DELETE=false (Default)                       │
│  → delete_abap_object wirft Fehler                  │
├─────────────────────────────────────────────────────┤
│  BLOCKED_PACKAGES=SAP,SHD,...                       │
│  → Keine Schreibzugriffe auf SAP-Namensräume        │
├─────────────────────────────────────────────────────┤
│  Customer Namespace Check                           │
│  → Namen müssen mit Z/Y beginnen                    │
├─────────────────────────────────────────────────────┤
│  SAP-Autorisierungen (S_ADT_RES, S_DEVELOP)         │
│  → Letzte Verteidigungslinie im System              │
└─────────────────────────────────────────────────────┘
```

### Empfohlene Konfiguration pro Systemtyp

| System | ALLOW_WRITE | ALLOW_DELETE | ALLOW_EXECUTE | BLOCKED_PACKAGES |
|--------|-------------|--------------|---------------|------------------|
| DEV | `true` | `false` | `true` | `SAP,SHD` |
| QAS/TEST | `false` | `false` | `false` | `SAP,SHD` |
| PRD | `false` | `false` | `false` | `SAP,SHD` (nie ändern!) |

---

## ADT Objekt-URL Referenz

| Objekttyp | ADT-URL-Muster |
|-----------|----------------|
| Programm | `/sap/bc/adt/programs/programs/{name}` |
| Klasse | `/sap/bc/adt/oo/classes/{name}` |
| Interface | `/sap/bc/adt/oo/interfaces/{name}` |
| Funktionsgruppe | `/sap/bc/adt/function/groups/{name}` |
| Funktionsbaustein | `/sap/bc/adt/function/groups/{group}/fmodules/{name}` |
| CDS View | `/sap/bc/adt/ddic/ddl/sources/{name}` |
| Tabelle | `/sap/bc/adt/ddic/tables/{name}` |
| Datenelement | `/sap/bc/adt/ddic/dataelements/{name}` |
| Domäne | `/sap/bc/adt/ddic/domains/{name}` |
| Nachrichtenklasse | `/sap/bc/adt/messageclass/{name}` |

Quellcode einer Einheit lesen/schreiben: URL + `/source/main`

---

## Fehlerbehebung

| Fehler | Mögliche Ursache | Lösung |
|--------|-----------------|--------|
| `401 Unauthorized` | Falsche Credentials | SAP_USER/SAP_PASSWORD prüfen |
| `ADT_SRV not found` | SICF nicht aktiviert | `/sap/bc/adt` in SICF aktivieren |
| `Lock failed` | Objekt durch anderen User gesperrt | In SE03 oder ADT Lock manuell freigeben |
| `Write disabled` | ALLOW_WRITE=false | In `.env` auf `true` setzen (nur DEV!) |
| `Package blocked` | Package in BLOCKED_PACKAGES | BLOCKED_PACKAGES anpassen oder anderes Paket verwenden |
| `Namespace violation` | Name beginnt nicht mit Z/Y | Customer Namespace einhalten |
| `Connection refused` | System nicht erreichbar | VPN-Verbindung prüfen, SAP-System läuft? |
| `SSL error` | Self-signed Zertifikat | `NODE_TLS_REJECT_UNAUTHORIZED=0` setzen (nur DEV!) |
| `codeCompletion is not a function` | Alte abap-adt-api Version | `npm update abap-adt-api` |
| `dumpsList is not a function` | System zu alt (< NW 7.52) | Feature nicht verfügbar auf diesem System |

---

## WEBSEARCH — Web-Zugriff & SAP Web-Suche

### `fetch_url`

Liest und extrahiert den lesbaren Inhalt einer beliebigen URL. Funktioniert auch mit JavaScript-gerenderten Seiten (SPAs) wie dem SAP Help Portal, SAP Community Blogs, SAP Notes oder jeder anderen Webseite. Gibt den extrahierten Textinhalt zurück.

**Voraussetzungen:** `TAVILY_API_KEY` muss in der `.env` gesetzt sein.

> **Ja, `fetch_url` benötigt Tavily.** Das Tool nutzt die Tavily Extract API, um JavaScript-gerenderte Seiten (SPAs) zu lesen. Ein einfacher HTTP-Request würde bei SPAs wie dem SAP Help Portal nur eine leere HTML-Hülle zurückgeben. Tavily rendert die Seite serverseitig und extrahiert den lesbaren Text.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `url` | string | ✓ | URL der zu lesenden Seite (z.B. `https://help.sap.com/docs/...`) |

**Beispiele:**
```
SAP Help Seite lesen
→ fetch_url(url="https://help.sap.com/docs/SAP_DATASPHERE/e4059f908d16406492956e5dbcf142dc/df2dd6a7deaa4e34ad2f4ebff85881f7.html?locale=en-US")

SAP Community Blog lesen
→ fetch_url(url="https://community.sap.com/t5/...")

Beliebige Webseite lesen
→ fetch_url(url="https://example.com/some-page")
```

**Verhalten:**
1. **Strategie 1:** Tavily Extract API — rendert JavaScript und extrahiert den Seiteninhalt
2. **Strategie 2 (Fallback):** Tavily Search mit `include_raw_content` — sucht die URL und gibt den gecachten Inhalt zurück (URL-Vergleich ignoriert http/https, `www.`, Trailing-Slash, Query & Fragment)
3. Sehr lange Inhalte werden auf ~15.000 Zeichen gekürzt, um Token-Explosion zu vermeiden
4. Schlagen beide Strategien fehl, listet die Fehlermeldung die konkreten Ursachen pro Strategie auf — inkl. Hinweis bei ungültigem API-Key (HTTP 401/403) oder erschöpfter Quota (HTTP 429/432)

> **Corporate-Proxy mit TLS-Interception?** `WEB_ALLOW_UNAUTHORIZED=true` deaktiviert die Zertifikatsprüfung **nur** für die Tavily-Calls (nicht für die ADT-Verbindung).

**Unterschied zu `search_sap_web`:** `fetch_url` liest den Inhalt einer **bekannten URL**. `search_sap_web` **sucht** nach Inhalten anhand von Suchbegriffen.

> **Hinweis:** Dieses Tool ist ein Kern-Tool und immer verfügbar (auch im Deferred-Modus). Benötigt keine SAP-Systemverbindung.

---

### `search_sap_web`

Durchsucht SAP Help, SAP Community und SAP Notes via Tavily Search API. Gibt kompakte Ergebnisse zurück (Titel + URL + Snippet), um den Token-Verbrauch minimal zu halten. Ideal für: Fehlermeldungen nachschlagen, SAP Notes finden, Community-Lösungen suchen, Best Practices recherchieren.

**Voraussetzungen:** `TAVILY_API_KEY` muss in der `.env` gesetzt sein.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `query` | string | ✓ | Suchbegriff — Fehlermeldung, Thema, SAP Note-Nummer, SAP-Frage |
| `sources` | string[] | | Quellen: `help` (help.sap.com), `community` (community.sap.com), `notes` (me.sap.com). Default: alle drei |
| `maxResults` | number | | Max. Treffer pro Quelle (1–10, Default: 5) |

**Beispiele:**
```
Fehlermeldung nachschlagen
→ search_sap_web(query="CX_SY_OPEN_SQL_DB error SELECT")

SAP Note suchen
→ search_sap_web(query="SAP Note 2081285")

Nur SAP Community durchsuchen
→ search_sap_web(query="ALV grid editable", sources=["community"])

Migrations-Guide suchen
→ search_sap_web(query="S/4HANA migration BAPI_MATERIAL_SAVEDATA", sources=["help", "community"])
```

**Ergebnis-Format:** Pro Treffer werden Titel, URL und ein 2-Zeilen-Snippet zurückgegeben — das gesamte Ergebnis bleibt unter 500 Tokens.

> **Hinweis:** Dieses Tool ist ein Kern-Tool und immer verfügbar (auch im Deferred-Modus).

**Setup:**
1. https://tavily.com/ → Sign up → API Key kopieren
2. In `.env` eintragen:
```
TAVILY_API_KEY=tvly-...
```

**Kosten:** Free Tier: 1000 Searches/Monat. Danach Pay-as-you-go verfügbar.

---

## BATCH — Parallele Operationen

### `batch_read`

Führt mehrere Read-Only-Tool-Aufrufe in einem einzigen MCP-Request parallel aus. Der Server führt alle Operationen gleichzeitig via `Promise.allSettled()` aus und gibt die Ergebnisse gebündelt zurück.

**Anwendungsfall:** MCP-Clients wie Cline führen Tool-Aufrufe sequenziell aus. Mit `batch_read` wird aus 5 sequenziellen Aufrufen ein einzelner paralleler Call — die Gesamtzeit entspricht dem langsamsten Einzelrequest statt der Summe aller Requests.

**Parameter:**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `operations` | Array | Ja | Liste von 1–20 Operationen |
| `operations[].tool` | String | Ja | Tool-Name (jedes Read-Only-Tool) |
| `operations[].args` | Object | Ja | Argumente (identisch mit direktem Tool-Aufruf) |
| `operations[].label` | String | Nein | Optionales Label zur Identifikation im Ergebnis |

**Erlaubte Tools:** Alle Read-Only-Tools (SEARCH, READ, QUALITY, DIAGNOSTICS, TRANSPORT, ABAPGIT, QUERY, DOCUMENTATION). Nicht erlaubt: WRITE, CREATE, DELETE, META, `execute_abap_snippet`.

**Beispiel:**
```json
batch_read({
  operations: [
    { tool: "read_abap_source", args: { objectUrl: "/sap/bc/adt/programs/programs/ztest", includeRelated: true }, label: "source" },
    { tool: "where_used", args: { objectUrl: "/sap/bc/adt/programs/programs/ztest" }, label: "usages" },
    { tool: "get_object_info", args: { objectUrl: "/sap/bc/adt/programs/programs/ztest" }, label: "info" }
  ]
})
```

**Ergebnis-Format:**
```
batch_read: 3 operations, 3 OK, 0 errors

═══ source [OK] ═══
[Quellcode...]

═══ usages [OK] ═══
[Where-Used-Ergebnisse...]

═══ info [OK] ═══
[Objektmetadaten...]
```

**Hinweise:**
- Als **Kern-Tool** registriert — immer verfügbar, kein `find_tools` nötig
- Fehlertoleranz: Einzelne fehlgeschlagene Operationen stoppen nicht den gesamten Batch
- ADT hat keine native Batch-API — die Parallelisierung erfolgt im Node.js MCP Server
- **Read-only-Garantie:** Alle mutierenden Tools (write/edit/create/delete/activate/publish/
  abapGit/execute, inkl. `SAPWrite`) sind blockiert. Die Blockliste wird aus
  `tools/mutating-tools.ts` abgeleitet und per Unit-Test gegen die Tool-Kategorien geprüft —
  neue mutierende Tools sind automatisch abgedeckt

---

## Method-Level Surgery, Contracts, Analyse & Intent-Facade

Diese Tools wurden ergänzt, um Token-Effizienz, Kontextkompression und Impact-Analyse
zu verbessern. Sie nutzen denselben ADTClient und Write-Workflow wie die übrigen Tools.

### READ — `read_abap_method`

Liest einen einzelnen `METHOD…ENDMETHOD`-Block einer Klasse/eines Interfaces statt der
ganzen Quelle. Token-sparend, wenn nur eine Methode interessiert.

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL der Klasse, z.B. `/sap/bc/adt/oo/classes/zcl_foo` |
| `methodName` | string | ✓ | Methodenname (case-insensitiv). Interface-Methoden: `if_x~method` |

```
→ read_abap_method(objectUrl="/sap/bc/adt/oo/classes/zcl_foo", methodName="calculate")
```

### READ — `get_abap_contract`

Gibt die komprimierte öffentliche Schnittstelle (Signaturen ohne Methodenrümpfe) einer
Klasse/eines Interfaces zurück — typischerweise 5–10 % der Quellgröße. **Kern-Tool.**

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL einer Klasse oder eines Interface |

> `analyze_abap_context(mode="contract")` liefert Main + Includes ebenfalls als Contracts statt Volltext.

### WRITE — `edit_abap_method`

Ersetzt einen einzelnen Methodenrumpf, ohne die ganze Klasse neu zu senden. Der Server
splittet den neuen Rumpf in die volle Quelle und durchläuft `lock → DDIC → Syntax →
aktivieren → unlock`. ⚠️ Erfordert `ALLOW_WRITE=true`.

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL der Klasse (ohne `/source/main`) |
| `methodName` | string | ✓ | Name der zu ersetzenden Methode (case-insensitiv) |
| `source` | string | ✓ | Neuer **Methodenrumpf** (Statements; `METHOD`/`ENDMETHOD` werden ergänzt/abgestreift) |
| `transport` | string | | Transportauftrag |
| `activateAfterWrite` | boolean | | Nach dem Schreiben aktivieren (Default: true) |
| `skipSyntaxCheck` | boolean | | Syntaxcheck überspringen (nicht empfohlen) |

```
→ edit_abap_method(objectUrl="/sap/bc/adt/oo/classes/zcl_foo", methodName="add",
                   source="    r = a + b.")
```

### ANALYSIS — `get_call_graph`

Expandiert die Where-Used-Relation breitensuchend und rendert ein Mermaid-Diagramm plus
Kantenliste. Für Impact-Analyse („was bricht, wenn ich das ändere?“).

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrl` | string | ✓ | ADT-URL des Wurzelobjekts |
| `depth` | number | | Where-Used-Ebenen (1–4, Default 2) |
| `maxNodes` | number | | Knoten-Cap (5–200, Default 60) |

### ANALYSIS — `find_dead_code`

Prüft eine Objektliste auf eingehende Verwendungen und markiert Objekte ohne Verwendung
als Löschkandidaten. **Hinweis:** dynamische Calls (`CALL FUNCTION` zur Laufzeit, BAdIs,
Dynpro-Ablauflogik) sind im statischen Where-Used-Index unsichtbar.

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `objectUrls` | string[] | ✓ | ADT-URLs der zu prüfenden Objekte (1–50) |

### INTENT — `SAPRead` / `SAPWrite` / `SAPSearch` / `SAPDiagnose`

Konsolidierte Verben für Clients, die eine kleine Tool-Oberfläche bevorzugen. Jedes Tool
nimmt `operation` + `args` und delegiert an das granulare Tool — reine Routing-Schicht,
alle Safety-Guards/Audit bleiben aktiv. **Kern-Tools.**

| Tool | `operation`-Werte |
|------|-------------------|
| `SAPRead` | source, method, contract, info, where_used, table, table_fields, ddic, revisions, context |
| `SAPWrite` | source, method, activate, pretty_print, create_program, create_class, create_interface, create_function_group, create_cds_view, create_table, create_message_class, create_metadata_extension, create_service_definition, create_service_binding, publish_service_binding, create_dcl, create_bdef, delete |
| `SAPSearch` | objects, source, call_graph, dead_code |
| `SAPDiagnose` | syntax, atc, unit, ddic_validate, clean_abap, dumps, dump_detail, traces, trace_detail |

```
→ SAPRead(operation="contract", args={ objectUrl: "/sap/bc/adt/oo/classes/zcl_foo" })
→ SAPWrite(operation="method", args={ objectUrl: "...", methodName: "add", source: "  r = a + b." })
```

---

## Governance — Rollen & Audit

**Rollen (`SAP_ROLE`):** schränken zusätzlich zu den `ALLOW_*`-Flags ein und können nur
*weiter* einschränken, nie freischalten. Durchgesetzt via `assertRoleAllows()` in `safety.ts`.

| Rolle | write | delete | execute |
|-------|:-----:|:------:|:-------:|
| `viewer` | – | – | – |
| `developer` | ✓ | – | ✓ |
| `admin` (Default) | ✓ | ✓ | ✓ |

> Default `admin` = bisheriges Verhalten: die `ALLOW_*`-Flags bleiben die einzige Schranke.

**Audit (`AUDIT_LOG_FILE`):** Jede verändernde Aktion (write/delete/execute) wird als
JSON-Zeile protokolliert — immer nach **STDERR** (Präfix `AUDIT `, nie STDOUT = MCP-Kanal)
und optional zusätzlich in die angegebene Datei. Felder: `ts`, `instance`, `user`, `role`,
`tool`, `action`, `target`, `outcome`, `detail`.

Abgedeckt sind **alle** mutierenden Tools: `write_abap_source`, `edit_abap_method` und
`delete_abap_object` auditieren in ihren Handlern (mit Phasen-Detail); alle übrigen
(`create_*`, `activate_abap_object`, `mass_activate`, `publish_service_binding`,
`create_test_include`, `create_transport`, `abapgit_pull`, `execute_abap_snippet`) werden
zentral über einen Audit-Wrapper in `handler-map.ts` erfasst — auch bei Aufruf über die
Intent-Facade (`SAPWrite` etc.). `outcome=denied` kennzeichnet Ablehnungen durch
Safety-Guards (ALLOW_*-Flags, Rolle, BLOCKED_PACKAGES, Namespace).

**Source-Cache (`SOURCE_CACHE_TTL_MS`):** TTL-Cache für `getObjectSource` (Default 30 s,
`0` = aus). Writes/Deletes invalidieren automatisch — nie veralteter Quelltext nach einer Mutation.

---

## Bekannte Einschränkungen

- **Pretty Print**: Erfordert NW 7.51+ und abapfs_extensions Plugin auf dem System.
- **Code Completion**: Liefert systemspezifische Vorschläge — auf älteren Systemen ggf. eingeschränkt.
- **ATC-Checks**: Asynchrone Prüfungen können je nach System-Last mehrere Sekunden dauern.
- **Short Dumps / Traces**: Nur verfügbar auf NW >= 7.52; auf älteren Systemen gibt `get_short_dumps` eine Fehlermeldung zurück.
- **abapGit Pull**: Erfordert dass abapGit im System installiert ist und der User abapGit-Berechtigung hat.
- **Debugger**: Der ABAP-Debugger ist nicht per MCP steuerbar — das ist eine VS Code-spezifische Funktion.
- **Gleichzeitige Locks**: Der Server hält nur eine ADT-Session. Bei parallelen Write-Operationen können Lock-Konflikte entstehen.

---

*Letzte Aktualisierung: [Aktuelle Version]*
*Basiert auf: abap-adt-api v8.x, @modelcontextprotocol/sdk v1.x*
