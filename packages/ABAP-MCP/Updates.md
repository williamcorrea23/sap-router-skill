# ABAP MCP Server — Updates & Changelog

---

## 2026-06-14 — README: SAPs offizieller „ABAP MCP Server" (Q2 2026 GA) bestätigt

### Recherche: Offizielle SAP-Quellen zur GA

Zur Q2-2026-GA des SAP-eigenen Angebots wurden zwei offizielle Quellen ausgewertet
([SAP Community Blog](https://community.sap.com/t5/technology-blog-posts-by-sap/entering-the-new-era-of-agentic-ai-for-abap-development/ba-p/14394643),
[SAP News Center DE](https://news.sap.com/germany/2026/06/mit-agentic-ai-erreicht-abap-die-naechste-stufe-der-evolution/)).
Ergebnisse in den "Vergleich"-Abschnitt der README eingearbeitet:

1. **Namenskollision:** SAPs Produkt heißt offiziell ebenfalls **„ABAP MCP Server"** —
   identisch zu diesem Projekt (`package.json` name: `abap-mcp-server`). Hinweis als
   Warnbox im README-Vergleich ergänzt; relevant falls dieses Paket je auf npm landet.
2. **Architektur:** SAPs Server basiert auf dem **ABAP Language Server** (IDE-unabhängige
   Abstraktionsschicht), MCP-Schicht darüber. Eclipse + VS Code als native Clients,
   GitHub Copilot/Amazon Q als Drittanbieter-Agenten darin — IDE-Bindung-Zeile präzisiert.
3. **Keine Tool-/API-Referenz öffentlich:** Die granulare Vergleichstabelle (67 Tools vs.
   ~10 Kategorien etc.) bleibt Best-Effort-Einschätzung; Quellen-Footnote ergänzt.

Inhaltliche Kernaussage der Tabelle (breiter/tiefer/kostenlos, einzige Lücke
SAP-ABAP-1-Modell) unverändert — keine neuen Gegenargumente in den Quellen gefunden.

---

## 2026-06-09 — Scan Runde 6: Stillschweigend ignorierte Parameter & Schema-Lücken

### Bugfix-Cluster: Tool-Parameter, die akzeptiert aber nie ausgewertet wurden

Vollständiger Review von `schemas.ts` gegen die Handler deckte fünf Parameter auf,
die das Schema dokumentierte, die aber wirkungslos waren:

1. **`get_short_dumps.maxResults`** — ignoriert. Jetzt: `maxResults` hat Vorrang
   vor `MAX_DUMPS` (env-Default).
2. **`get_short_dumps.since`** — Zeitfilter ohne Implementierung; die Dump-Feed-
   Einträge der abap-adt-api tragen keinen Zeitstempel, clientseitig nicht
   implementierbar → Parameter entfernt (Zod strippt unbekannte Keys, alte
   Aufrufer bleiben kompatibel).
3. **`get_traces.maxResults`** — ignoriert, Trace-Liste unbegrenzt. Jetzt: `runs`
   wird auf das Limit (Default 10) gekürzt, mit Hinweis im Output.
4. **`create_abap_class.superClass`** — akzeptiert und stillschweigend verworfen
   (ADT-Create kann keine Superklasse setzen). Jetzt: expliziter Hinweis im
   Output, dass `INHERITING FROM` per `write_abap_source` nachgezogen werden muss.
5. **`execute_abap_snippet.timeout`** — versprach eine Laufzeitbegrenzung, die nie
   durchgesetzt wurde → Parameter entfernt (inkl. internem Aufruf in `workflow.ts`).

### Schema-Beschreibungen vervollständigt

- **`SAPWrite.operation`** (Kern-Tool!) listete nur 12 von 18 unterstützten
  Operationen — `create_metadata_extension`, `create_service_definition`,
  `create_service_binding`, `publish_service_binding`, `create_dcl`, `create_bdef`
  waren für Clients unauffindbar. Liste vervollständigt.
- **`find_tools`/`list_tools`** Kategorie-Beschreibung um `BATCH | ANALYSIS | INTENT` ergänzt.

### Konsistenz-Audit (programmatisch, ohne Befund)

Registry-Quervergleich: jede Tool-Definition hat einen Handler und umgekehrt,
alle Kategorie-Einträge existieren, `TOOL_SHORT_DESCRIPTIONS` vollständig ohne
Waisen, Intent-Maps zeigen auf registrierte Handler, `MODULE_BEST_PRACTICES`-Keys
decken das Schema-Enum exakt ab. Ebenfalls geprüft ohne Befund: `adt-endpoints.ts`,
`btp/credentials.ts` (vorbildliche cf-Fehlerdiagnose), `btp/index.ts`,
`saprouter.ts` (NI-Paketaufbau).

**Geänderte Dateien:**
- `src/schemas.ts` — Parameter entfernt/ergänzt, Beschreibungen vervollständigt
- `src/tools/handlers/diagnostics.ts` — maxResults für Dumps & Traces wirksam
- `src/tools/handlers/create.ts` — superClass-Hinweis
- `src/tools/handlers/workflow.ts` — toten `timeout`-Parameter entfernt

---

## 2026-06-09 — Scan Runde 5: `analyze_workflow` SQL-Literale & Sprach-Hardcoding

### Bugfix: Unescaptes User-Input in den Workflow-SQL-Abfragen

**Problem:** `workflowId`, `user` und `status` wurden unverändert in die
SELECT-Statements interpoliert (`WHERE WI_AAGENT = '${p.user}'`). Ein Wert mit
Hochkomma erzeugte ein kaputtes Statement mit verwirrendem Backend-Fehler. Das
Data-Preview-Backend ist read-only, daher kein Mutations-Risiko — aber ein
Korrektheits-/Robustheitsproblem.

**Fix:** Neuer Helper `sqlLit()` (ABAP-SQL-Literal-Escaping per `''`-Verdopplung),
angewendet auf alle interpolierten Parameter in allen fünf Modi.

### Bugfix: Workflow-Knotentexte hart auf Deutsch (`LANGU = 'D'`)

**Problem:** `mode='graph'` las die Knotenbeschreibungen aus SWD_NODET mit fest
verdrahtetem `LANGU = 'D'` — auf EN-Systemen (Default `SAP_LANGUAGE=EN`) blieben
alle Beschreibungen leer.

**Fix:** Sprachschlüssel wird aus `cfg.language` abgeleitet (EN → E, DE → D).

**Geprüft ohne Befund:** `workflow.ts` übrige Logik (sauberes `safeQuery`-Muster,
durchdachte Mermaid-Generierung), `documentation.ts`-Handler (eine kosmetische
Redundanz im „local/GitHub"-Label), `btp/agent.ts` (Header-Callback liest Token
live — korrekt), `saprouter.ts` (NI-Frame-Reader mit Cleanup/Leftover-Unshift —
vorbildlich), Rest von `clean-abap.ts` und `prompt.ts` (alle referenzierten
Tool-Namen existieren).

**Geänderte Dateien:**
- `src/tools/handlers/workflow.ts` — `sqlLit()`-Escaping + `LANGU` aus `cfg.language`

---

## 2026-06-09 — Scan Runde 4: CDATA-Escaping, Token-Timeout & Clean-ABAP-Regel

### Bugfix: `create_cds_view` — `]]>` im CDS-Source brach das Create-XML

**Problem:** Der initiale CDS-Source wurde unescaped in eine CDATA-Sektion eingebettet
(`<![CDATA[${source}]]>`). Enthielt der Source die Zeichenfolge `]]>` (z.B. in einem
String/Kommentar), endete die CDATA-Sektion vorzeitig → malformed XML → verwirrender
ADT-Fehler.

**Fix:** Standard-CDATA-Escaping — `]]>` wird auf zwei CDATA-Sektionen aufgeteilt
(`]]]]><![CDATA[>`).

### Bugfix: XSUAA-Token-Request ohne Timeout

**Problem:** `btp/token.ts` war der einzige Netzwerk-Call im Codebase ohne Timeout —
ein hängender XSUAA-Endpunkt blockierte den ersten Login (und Hintergrund-Refreshes)
unbegrenzt.

**Fix:** `AbortSignal.timeout(15_000)` wie bei allen übrigen fetch-Aufrufen.

### Bugfix: Clean-ABAP-Regel `CHECK_IN_METHOD` war case-sensitiv

**Problem:** Als einzige der 11 Regeln fehlte das `/i`-Flag — kleingeschriebenes ABAP
(`method … check …`) wurde nie geflaggt, obwohl ABAP case-insensitiv ist.

**Fix:** `/i`-Flag ergänzt (konsistent mit allen anderen Regeln).

**Geprüft ohne Befund:** `create.ts` (alle übrigen Handler — Guards vollständig,
False-Success-Verifikation via `objectStructure`, durchdachte Workarounds für
abap-adt-api-Lücken), `helpers/documentation.ts`, `helpers/ddic-validation.ts`
(Parsing-Teil), `helpers/clean-abap.ts` (übrige Regeln + Laden), `btp/token.ts`
(In-Flight-Dedup, Refresh-Skew, `unref` — sauber), `btp/credentials.ts`,
`saprouter-agent.ts`, `prompt.ts`, `schemas.ts` (Constraints konsistent).

**Geänderte Dateien:**
- `src/tools/handlers/create.ts` — CDATA-Escaping
- `src/btp/token.ts` — Timeout
- `src/helpers/clean-abap.ts` — `/i`-Flag

---

## 2026-06-09 — Scan Runde 3: Schema-Beschreibungen, Kontext-Limit & MAX_DUMPS

### Bugfix: Parameter-Beschreibungen fehlten für alle optionalen Tool-Parameter

**Problem:** Der Zod→JSON-Schema-Konverter (`helpers/json-schema.ts`) verwarf bei
`ZodOptional`/`ZodDefault`/`ZodEffects` die Beschreibung des Wrappers. Da fast alle
Schemas das Muster `z.string().optional().describe(…)` nutzen, sahen MCP-Clients für
die meisten optionalen Parameter (z.B. `transport`, `activateAfterWrite`,
`skipSyntaxCheck`) **keine** Beschreibung. Zusätzlich war `z.record` (→ `batch_read.args`)
gar nicht behandelt und wurde als leeres Schema `{}` ausgegeben.

**Fix:** Wrapper-Beschreibungen werden beim Abstieg gemerged (äußere gewinnt);
`ZodRecord` → `{ type: "object" }`. Neue Tests: `test/json-schema.test.ts`.

### Bugfix: 150k-Zeichen-Limit von `analyze_abap_context` war wirkungslos

**Problem:** Die Trunkierung kürzte das Array `allSourceTexts`, die Ausgabe wurde aber
danach aus den ungekürzten Originalen (`mainText`, `inc.source`) gebaut — toter Code.
Die Warnung „Source code limited to 150.000 characters" erschien, der Output war
trotzdem unbegrenzt (Token-Explosion bei großen Objekten).

**Fix:** Budget wird jetzt bei der Ausgabe angewendet (`clipSource()` mit laufendem
Zeichen-Budget); die Referenz-Analyse sieht weiterhin den vollen Text.

### Bugfix: `MAX_DUMPS` war tote Konfiguration

**Problem:** `cfg.maxDumps` (dokumentiert in CLAUDE.md/.env.example/DOCUMENTATION.md)
wurde nirgends verwendet — `get_short_dumps` gab den kompletten Dump-Feed unbegrenzt
zurück.

**Fix:** `get_short_dumps` begrenzt jetzt auf `MAX_DUMPS` (Default 20) und weist im
Output auf die Limitierung hin.

### Kleinfix: `INCLUDE … IF FOUND.` wurde nicht aufgelöst

Die INCLUDE-Erkennung in `read_abap_source` (includeRelated) und
`analyze_abap_context` übersprang Includes mit `IF FOUND`-Zusatz. Regex erweitert.

**Geprüft ohne Befund:** `analysis.ts` (BFS korrekt begrenzt), `meta.ts`, `resolve.ts`,
`search.ts` (XML-Parsing funktional, Attributreihenfolge-abhängig — Hinweis),
`diagnostics.ts` (übrige Handler), `transport.ts`, `abapgit.ts`, `test.ts`,
`workflow.ts` (sauberes `safeQuery`-Muster), `helpers/documentation.ts` (Timeout
vorhanden), `contract.ts`.

**Geänderte Dateien:**
- `src/helpers/json-schema.ts`, `test/json-schema.test.ts` (neu)
- `src/tools/handlers/context.ts` — wirksames Zeichen-Budget + INCLUDE-Regex
- `src/tools/handlers/read.ts` — INCLUDE-Regex
- `src/tools/handlers/diagnostics.ts` — MAX_DUMPS angewendet

---

## 2026-06-09 — Scan Runde 2: `batch_read` Read-Only-Contract repariert

### Security-Fix: `batch_read` ließ sechs mutierende Tools durch

**Problem:** Die `BLOCKED_TOOLS`-Denyliste in `batch.ts` war beim Hinzufügen neuer Tools
nicht mitgepflegt worden. Nicht blockiert waren: `publish_service_binding`,
`create_cds_metadata_extension`, `create_service_definition`, `create_service_binding`,
`create_data_control_language`, `create_behavior_definition`. Bei `ALLOW_WRITE=true`
konnte ein Client, der `batch_read` als „read-only" auto-approved (z.B. Cline-
`autoApprove`), darüber Objekte anlegen oder OData-Endpoints publizieren. Die
serverseitigen Guards (Flags/Rolle/Audit) griffen weiterhin — gebrochen war der
Read-only-Vertrag des Tools gegenüber clientseitigen Permission-Modellen.

**Fix:** Neue Single-Source-of-Truth `src/tools/mutating-tools.ts`:
- `AUDIT_WRAPPED_TOOLS` — speist den `withAudit`-Wrapper in `handler-map.ts`
- `MUTATING_TOOL_NAMES` (abgeleitet, inkl. `SAPWrite` + selbst-auditierende Handler) —
  speist die `batch_read`-Blockliste
- Eigenes Modul, weil `batch.ts` ↔ `handler-map.ts` bereits einen Import-Zyklus bilden
- Neuer Drift-Guard-Test `test/mutating-tools.test.ts`: prüft die Liste gegen die
  WRITE/CREATE/DELETE-Tool-Kategorien — ein vergessenes neues Tool lässt den Test fehlschlagen

**Geprüft ohne Befund:** `method-splice.ts` (Limitationen dokumentiert + getestet),
`adt-client.ts` (Session-/Agent-Handling sauber), `create.ts` (XML via `encXml()`
escaped), `btp/*` (keine Secrets in Logs).

**Geänderte Dateien:**
- `src/tools/mutating-tools.ts` (neu), `src/tools/handlers/batch.ts`,
  `src/tools/handler-map.ts`, `test/mutating-tools.test.ts` (neu)
- `DOCUMENTATION.md`, `CLAUDE.md` — Read-only-Garantie & Wartungshinweis dokumentiert

---

## 2026-06-09 — Targeted Scan: Write-Workflow, Snippet-Executor & Audit-Abdeckung

### Bugfix: Unlock im Fehlerpfad des Write-Workflows nutzte falsche URL

**Problem:** Im Fehlerpfad von `writeWorkflow` (`write-workflow.ts`) wurde
`client.unLock(objectUrl, …)` aufgerufen — der Lock wurde aber auf `lockUrl` gesetzt
(bei Klassen-Includes die Eltern-Klasse). Schlug ein Write auf ein Klassen-Include fehl,
zielte der Unlock auf die falsche URL, scheiterte immer und verließ sich stillschweigend
auf das `dropSession`-Cleanup.

**Fix:** Fehlerpfad nutzt jetzt `lockUrl` — konsistent mit dem Happy-Path.

### Bugfix: `execute_abap_snippet` ignorierte das Aktivierungsergebnis

**Problem:** `client.activate()` wurde aufgerufen, ohne `success` zu prüfen. Schlug die
Aktivierung fehl (Nicht-Syntax-Grund), wurde der `/runs`-POST trotzdem abgesetzt —
das Snippet lief in einer alten/inaktiven Version oder lieferte verwirrende Ausgaben.

**Fix:** Aktivierungsergebnis wird geprüft; bei Fehlschlag bricht das Tool mit den
Aktivierungsmeldungen ab („Activation failed — code not executed").

### Governance: Audit-Abdeckung jetzt vollständig

**Problem:** `audit.ts` versprach „every state-changing action is recorded", aber nur 4
von ~20 mutierenden Handlern riefen `audit()` auf. Nicht auditiert: alle 13 `create_*`,
`activate_abap_object`, `mass_activate`, `publish_service_binding`, `create_test_include`,
`create_transport`, `abapgit_pull`; `execute_abap_snippet` loggte nur „attempt" ohne Ausgang.

**Fix:** Neuer `withAudit`-Wrapper in `handler-map.ts`: die fehlenden mutierenden Tools
werden zentral an der Dispatch-Map dekoriert (`AUDITED_TOOLS`-Liste) — ein Ort, kein
Drift, und die Intent-Facade (`SAPWrite` → `create_*`) erbt die Abdeckung automatisch.
Safety-Guard-Ablehnungen (ALLOW_*-Flags, Rolle, BLOCKED_PACKAGES, Namespace) werden als
`outcome=denied` protokolliert (bisher ungenutzter Outcome-Wert), Fehler mit
`detail`-Auszug. `write_abap_source`/`edit_abap_method`/`delete_abap_object` auditieren
weiterhin in ihren Handlern (Phasen-Detail), um Doppel-Einträge zu vermeiden.

**Geänderte Dateien:**
- `src/write-workflow.ts` — Unlock im Fehlerpfad auf `lockUrl` korrigiert
- `src/tools/handlers/query.ts` — Aktivierungsergebnis-Prüfung vor `/runs`
- `src/tools/handler-map.ts` — `withAudit`-Wrapper + `AUDITED_TOOLS`
- `DOCUMENTATION.md`, `CLAUDE.md` — Audit-Abdeckung dokumentiert

---

## 2026-06-09 — Qualitäts-Review der Web-Search-Implementierung (fetch_url)

### Bugfix: `validate_ddic_references` lieferte ohne ADT-Verbindung stillschweigend falsche Ergebnisse

**Problem:** Die `NO_ADT_TOOLS`-Liste in `server.ts` enthielt `validate_ddic_references`,
obwohl das Tool `client.ddicElement()` aufruft. Wurde es als erstes Tool einer Session
aufgerufen, war der Client `null` — jede Tabelle meldete dann
„⚠️ DDIC not resolvable — Cannot read properties of null…" statt zu validieren.

**Fix:** Die handgepflegte Liste wurde durch ein `requiresAdt: false`-Flag direkt an den
Tool-Definitionen ersetzt (`src/types.ts`, `tool-definitions.ts`). Das Set
`NO_ADT_TOOL_NAMES` wird daraus abgeleitet (`tool-registry.ts`) und kann nicht mehr
driften. `validate_ddic_references` erhält wieder einen echten Client; die fünf
DOCUMENTATION-Tools sowie `review_clean_abap` erzwingen umgekehrt **keinen** unnötigen
SAP-Login mehr.

### Security-Fix: Globale TLS-Deaktivierung entfernt

**Problem:** `index.ts` setzte bei `SAP_ALLOW_UNAUTHORIZED=true` global
`NODE_TLS_REJECT_UNAUTHORIZED=0` — damit war die Zertifikatsprüfung für **alle**
ausgehenden TLS-Verbindungen aus (inkl. Tavily-Calls mit dem API-Key).

**Fix:** Der globale Override ist entfernt; `SAP_ALLOW_UNAUTHORIZED` bleibt wie zuvor
auf die ADT-Verbindung beschränkt (`adt-client.ts`). Für Corporate-Proxies mit
TLS-Interception gibt es jetzt das separate Opt-in `WEB_ALLOW_UNAUTHORIZED`, das nur
die Tavily-Fetches betrifft (undici-`Agent` als `dispatcher`). Der Startup-Banner
warnt, wenn es aktiv ist.

### Verbesserung: `fetch_url` nennt jetzt die echte Fehlerursache

Bisher wurden alle Fehler verschluckt — bei ungültigem API-Key (HTTP 401) oder
erschöpfter Quota (HTTP 429/432) kam die irreführende Meldung „Seite blockiert
automatisierte Zugriffe". Jetzt werden die Fehlerdetails beider Strategien (Extract +
Search-Fallback) gesammelt und mit konkretem Hinweis ausgegeben; `failed_results` der
Extract-API wird ausgewertet. Tavily-Auth läuft über `Authorization: Bearer`-Header
statt API-Key im Request-Body.

### Refactoring & Tests

- Neue pure Helper in `src/helpers/web.ts`: `truncateContent()` (dedupliziert),
  `normalizeUrlForMatch()` + `pickBestResult()` (URL-Matching im Fallback ignoriert
  jetzt http/https, `www.`, Trailing-Slash, Query & Fragment)
- Neue Unit-Tests: `test/web.test.ts` (10 Tests, ohne Netzwerk)
- Gemeinsame Konstante für die „Tavily nicht konfiguriert"-Meldung
- Neue Dependency: `undici` (für den scoped TLS-Dispatcher)

**Geänderte Dateien:**
- `src/types.ts`, `src/tools/tool-definitions.ts`, `src/tools/tool-registry.ts`,
  `src/server.ts` — `requiresAdt`-Flag + abgeleitetes `NO_ADT_TOOL_NAMES`
- `src/index.ts` — globaler TLS-Override entfernt, Banner-Warnung
- `src/config.ts` — `webAllowUnauthorized` (`WEB_ALLOW_UNAUTHORIZED`)
- `src/tools/handlers/websearch.ts` — Bearer-Auth, Fehlerdetails, scoped Dispatcher
- `src/helpers/web.ts`, `test/web.test.ts` — neue Helper + Tests
- `.env.example`, `readme.md`, `DOCUMENTATION.md`, `CLAUDE.md` — Doku synchronisiert

---

## 2026-06-09 — Bugfix: `create_cds_view` — falscher XML-Root-Namespace

### Fix: DDLS-Anlage schlug mit "System expected the element ddlSource" fehl

**Problem:** `create_cds_view` nutzte `blue:blueSource` als XML-Root-Element mit Namespace
`http://www.sap.com/adt/naming`. Das ADT-Backend lehnte die Anfrage ab:
`"System expected the element ddlSource"`. Derselbe Root ist für TABL/BDEF korrekt, aber
**nicht** für DDL Sources (Typ `DDLS/DF`).

**Ursache:** `objectcreator.js` der `abap-adt-api`-Library verwendet für DDLS den Typ
`rootName: "ddl:ddlSource"` und `nameSpace: 'xmlns:ddl="http://www.sap.com/adt/ddic/ddlsources"'`.

**Fix:**
- XML-Root von `<blue:blueSource …>` auf `<ddl:ddlSource …>` geändert
- Namespace von `http://www.sap.com/adt/naming` auf `http://www.sap.com/adt/ddic/ddlsources`
- `source`/`sourcePath`-Parameter hinzugefügt (optional); da ADT keinen gemischten XML-Inhalt
  (CDATA + Kind-Elemente) akzeptiert, bleibt das empfohlene Muster:
  1. `create_cds_view` → Shell anlegen
  2. `write_abap_source` → CDS-DDL-Quelle füllen

**Geänderte Dateien:**
- `src/tools/handlers/create.ts` — `handleCreateCdsView`: Root-Element und Namespace korrigiert,
  `import * as fs from "fs"` ergänzt, `sourcePath`/`source`-Parameter-Handling
- `src/schemas.ts` — `S_CreateCdsView`: optionale Felder `source`, `sourcePath`
- `src/tools/tool-definitions.ts` — Beschreibung für `create_cds_view` aktualisiert
- `DOCUMENTATION.md` — `create_cds_view`-Abschnitt mit ADT-Hintergrund und Zweistufenmuster

---

## 2026-06-02 — SAP Business Workflow-Analyse: `analyze_workflow`

### Feature: Read-only Workflow-Analyse (SWDD / klassischer WF)

**Hintergrund:** SAP Business Workflow (Transaktion SWDD) speichert seine Metadaten in eigenen
Tabellen außerhalb des normalen ADT-Objektsystems. Das ADT REST API bietet keine dedizierten
Workflow-Endpunkte. Das neue Tool nutzt stattdessen `client.runQuery()` (ADT SELECT), um die
Standard-Workflow-Tabellen abzufragen — vollständig read-only, kein `ALLOW_WRITE` nötig.

**Neues Tool:** `analyze_workflow`
- 4 Modi: `definitions` (Workflow-Templates), `instances` (laufende/beendete WF-Instanzen),
  `steps` (Schrittdefinitionen eines Workflows), `agents` (Agenten-/Rollenzuweisungen)
- Tabellen: `SWF_FLEX_HEADER` (flexible WF, NW 7.40+), `SWFTASKI` (klassisch),
  `SWWWIHEAD` (Instanzen), `SWF_FLEX_STEP`, `SWFSTEPDEF`, `SWF_FLEX_ROLE`, `SWWUSERWI`
- Resilientes `safeQuery`-Muster: fehlt eine Tabelle im System, wird ein Hinweis ausgegeben statt
  der gesamte Aufruf zu scheitern
- Status-Labels (`WISTA`): numerische Codes werden in lesbare Labels umgewandelt
  (WAITING/READY/STARTED/COMPLETED/ERROR/…)
- Via `SAPDiagnose(operation="workflow")` — immer ohne `find_tools` erreichbar

**Geänderte Dateien:**
- `src/schemas.ts` — `S_AnalyzeWorkflow`
- `src/tools/handlers/workflow.ts` — neuer Handler (neu)
- `src/tools/tool-definitions.ts` — Tool-Metadaten + `SAPDiagnose`-Beschreibung
- `src/tools/handler-map.ts` — Import + Dispatch-Eintrag
- `src/tools/tool-registry.ts` — QUERY-Kategorie + Short Description
- `src/tools/handlers/intent.ts` — `DIAGNOSE_OPS.workflow`

---

## 2026-05-30 — RAP vollständig: `create_behavior_definition` (BDEF, direkter ADT-HTTP)

### Feature: BDEF-Anlage ohne Library-Support

**Hintergrund:** `abap-adt-api` v7.1.3 und v8.4.0 haben keinen BDEF-Support (`NonGroupTypeIds`
enthält `BDEF/BF` nicht). Direkter `POST /sap/bc/adt/bo/behaviors` mit XML-Body nach dem
`createBodySimple`-Muster aus `objectcreator.js` — Namespace und Typ aus den SAP-ADT-Konventionen
abgeleitet.

**Neues Tool:** `create_behavior_definition`
- ADT-Endpunkt: `POST /sap/bc/adt/bo/behaviors`
- XML-Namespace: `xmlns:bdef="http://www.sap.com/adt/bo/behaviors"`
- Typ: `BDEF/BF`
- Legt den BDEF-Objekt-Shell an; BDL-Quelle danach per `write_abap_source` füllen
- `rap-bdef`-Skill für vollständige BDL-Syntax verfügbar
- Via `SAPWrite(operation="create_bdef")` — immer erreichbar ohne `find_tools`

**Geänderte Dateien:**
- `src/schemas.ts` — `S_CreateBehaviorDefinition`
- `src/adt-endpoints.ts` — `ADT_BO_BEHAVIORS`
- `src/tools/handlers/create.ts` — `handleCreateBehaviorDefinition` + `encXml` Helper
- `src/tools/tool-definitions.ts` — Tool-Metadaten + SAPWrite-Beschreibung
- `src/tools/handler-map.ts`, `tool-registry.ts`, `handlers/intent.ts` — Registrierung

---

## 2026-05-30 — Core-Tools reduziert: 18 → 12 (Intent-Facade deckt granulare Tools ab)

### Optimierung: Kleinerer initialer Tool-Footprint

**Hintergrund:** Die vier INTENT-Verben (`SAPRead`, `SAPWrite`, `SAPSearch`, `SAPDiagnose`) delegieren
intern an dieselben Handler wie die granularen Tools. Beide gleichzeitig im Core zu haben war redundant
und kostete unnötig Tokens bei jedem Session-Start.

**Änderung:** Folgende 6 granulare Tools aus `CORE_TOOL_NAMES` entfernt — sie sind weiterhin über
`find_tools` aktivierbar und werden durch die INTENT-Facade vollständig abgedeckt:

- `search_abap_objects` → `SAPSearch`
- `search_source_code` → `SAPSearch`
- `read_abap_source` → `SAPRead`
- `get_object_info` → `SAPRead`
- `where_used` → `SAPRead` / `SAPSearch`
- `write_abap_source` → `SAPWrite`

**Ergebnis:** 12 Core-Tools statt 18 — weniger initiale Token-Last ohne Funktionsverlust.

**Geänderte Dateien:** `src/tools/tool-registry.ts`, `CLAUDE.md`, `readme.md`, `DOCUMENTATION.md`, `Updates.md`

---

## 2026-05-30 — RAP Stack: 5 neue Tools für CDS Metadata Extensions, Service Definitions, Service Bindings, DCL

### Feature: OData/RAP-Entwicklung vollständig abdecken

**Hintergrund:** Vergleich mit dem offiziellen SAP ADT for VS Code MCP-Server (Q2 2026 GA) zeigte
eine Lücke: Das SAP-Angebot deckt den vollständigen RAP-Entwicklungsstack ab (CDS-Annotation,
OData-Exposition, Zugriffskontrolle). Diese fünf Tools schließen die Lücke.

**Neue Tools (alle in CREATE-Kategorie):**

- **`create_cds_metadata_extension`** (`DDLX/EX`) — CDS-View mit UI-Annotationen versehen
  (Fiori-Feldlabels, SelectionFields, LineItem, HeaderInfo). Nach der Erstellung die Annotation
  mit `write_abap_source` schreiben.

- **`create_service_definition`** (`SRVD/SRV`) — OData-Service-Definition anlegen, die CDS-Entities
  exponiert. Quelle (EXPOSE ENTITY …) per `write_abap_source` füllen, dann mit
  `create_service_binding` binden.

- **`create_service_binding`** (`SRVB/SVB`) — OData-Service-Binding anlegen und an eine Service
  Definition koppeln. Parameter `bindingType`: `V2_UI` (Fiori/SAPUI5) oder `V2_WEB_API`
  (externe API). Anschließend mit `publish_service_binding` veröffentlichen.

- **`publish_service_binding`** — Binding veröffentlichen (macht den OData-Endpunkt erreichbar).
  Ruft `client.publishServiceBinding(name, version)` auf und liefert den Severity-Status zurück.

- **`create_data_control_language`** (`DCLS/DL`) — DCL-Quelle für instanzbasierte
  Zugriffsberechtigungen auf CDS-Views anlegen (`DEFINE ROLE …`). Quelle per
  `write_abap_source` füllen.

**Intent-Facade aktualisiert:** `SAPWrite` kennt jetzt die Operationen `create_metadata_extension`,
`create_service_definition`, `create_service_binding`, `publish_service_binding`, `create_dcl`.

**Geänderte Dateien:**
- `src/schemas.ts` — 5 neue Zod-Schemata
- `src/adt-endpoints.ts` — 4 neue Endpunkt-Konstanten
- `src/tools/handlers/create.ts` — 5 neue Handler-Funktionen
- `src/tools/tool-definitions.ts` — 5 neue Tool-Definitionen + SAPWrite-Beschreibung
- `src/tools/handler-map.ts` — Dispatch-Einträge ergänzt
- `src/tools/tool-registry.ts` — CREATE-Kategorie + Kurzbeschreibungen ergänzt
- `src/tools/handlers/intent.ts` — WRITE_OPS ergänzt

---

## 2026-05-30 — Gap-Closing: Method-Surgery, Contracts, Cache, Intent-Facade, Governance, Analyse

### Feature: 9 neue Tools + Kontextkompression + Audit/Rollen

**Hintergrund:** Ein Vergleich mit sechs anderen ABAP-MCP-Servern (vibing-steampunk,
ARC-1, mario-andreschak ×2, abap-ai, fr0ster) zeigte Lücken bei (a) Token-Effizienz
(Method-Surgery, Kontextkompression, konsolidierte Tools), (b) Caching und (c)
Multi-User-Governance. Diese sechs Phasen schließen sie.

**Phase 1 — Method-Level Surgery (`read_abap_method`, `edit_abap_method`):**
Lesen/Schreiben eines einzelnen `METHOD…ENDMETHOD`-Blocks statt der ganzen Klasse.
`edit_abap_method` nimmt nur den neuen Methodenrumpf, splittet ihn server-seitig in die
volle Quelle und durchläuft den unveränderten Write-Workflow (lock → DDIC → Syntax →
aktivieren → unlock). Größter Token-Hebel bei iterativem Coding — der Agent gibt nicht
mehr die komplette 800-Zeilen-Klasse aus, um eine Methode zu ändern.

**Phase 2 — Dependency Contracts (`get_abap_contract` + `analyze_abap_context(mode=contract)`):**
Komprimiert eine Klasse/Interface auf ihre öffentliche Signatur-Oberfläche (Methoden,
Interfaces, Events, Public-Types/Data/Constants) — **ohne** Methodenrümpfe. Typischerweise
5–10 % der Quellgröße. `analyze_abap_context` kann Main + Includes als Contracts statt als
Volltext liefern.

**Phase 3 — Source-Cache (`src/cache.ts`):**
TTL-begrenzter In-Memory-Cache für `getObjectSource` (Default 30 s, `SOURCE_CACHE_TTL_MS`,
0 = aus). Wiederholte Reads desselben Objekts (z.B. Context → Method → Contract) treffen den
Cache. **Invalidierung** bei jedem erfolgreichen `setObjectSource` (Write) und Delete — es
wird nie veralteter Quelltext nach einer Mutation ausgeliefert. `read_abap_source` und
`analyze_abap_context` lesen über den Cache.

**Phase 4 — Intent-Facade (`SAPRead`, `SAPWrite`, `SAPSearch`, `SAPDiagnose`):**
Vier konsolidierte Verb-Tools mit `operation`-Discriminator, die an die granularen Handler
delegieren (reine Routing-Schicht, keine Logik-Duplikate — erbt alle Safety-Guards). Clients
ohne Deferred-Loading sehen ~4 statt 50 Schemata. Die 59 granularen Tools bleiben über
`find_tools` verfügbar.

**Phase 5 — Governance (`src/audit.ts`, Rollen):**
Strukturiertes JSON-Audit-Log jeder verändernden Aktion (write/delete/execute) nach
**STDERR** (nie STDOUT — das ist der MCP-Protokollkanal) und optional in `AUDIT_LOG_FILE`.
Rollen `viewer`/`developer`/`admin` über `SAP_ROLE` (Default `admin` = bisheriges Verhalten,
ALLOW_*-Flags bleiben die harte Schranke; Rollen können nur weiter einschränken).

**Phase 6 — Analyse (`get_call_graph`, `find_dead_code`):**
`get_call_graph` expandiert die Where-Used-Relation breitensuchend (Tiefe 1–4, Knoten-Cap)
und rendert Mermaid + Kantenliste für Impact-Analyse. `find_dead_code` markiert Objekte ohne
eingehende Verwendungen als Löschkandidaten (Hinweis — dynamische Calls sind im statischen
Index unsichtbar).

**Technisches:** Neue reine Helfer sind unit-getestet (`method-splice`, `contract`, `cache`).
57 Tests grün, Build sauber. Tools: 50 → **59**, Kategorien: 14 → **16** (+ANALYSIS, +INTENT),
Core-Tools: 13 → **18**.

**Dateien:**
- Neu: `src/cache.ts`, `src/audit.ts`, `src/helpers/method-splice.ts`, `src/helpers/contract.ts`,
  `src/tools/handlers/method.ts`, `src/tools/handlers/contract.ts`, `src/tools/handlers/analysis.ts`,
  `src/tools/handlers/intent.ts`
- Neu (Tests): `test/method-splice.test.ts`, `test/contract.test.ts`, `test/cache.test.ts`
- Geändert: `src/config.ts` (role, auditLogFile), `src/safety.ts` (assertRoleAllows, Rollen-Matrix),
  `src/write-workflow.ts` (Cache-Invalidierung), `src/tools/handlers/{read,context,write,delete,query,batch}.ts`,
  `src/schemas.ts`, `src/tools/tool-definitions.ts`, `src/tools/handler-map.ts`, `src/tools/tool-registry.ts`,
  `.env.example`

---

## 2026-05-30 — Wartung: Tests, Security-Fixes, Robustheit

### Verbesserung: Unit-Tests, Dependency-Sicherheit & Härtung

**Hintergrund:** Eine Projektdurchsicht ergab mehrere Verbesserungspunkte: keinerlei
automatisierte Tests, 12 npm-Schwachstellen (4 hoch, u.a. `axios`/`fast-xml-parser`),
inkonsistente Tool-Zählungen in der Doku sowie zwei Robustheitslücken in der
Eingabevalidierung.

**Lösung:**
- **Test-Infrastruktur (Vitest):** Neues `npm test` / `npm run test:watch`. Tests unter
  `test/*.test.ts` decken die reinen Helfer ab — Clean-ABAP-Parsing
  (`parseMarkdownSections`, `isNavigationSection`, `searchCleanAbapSections`,
  `CLEAN_ABAP_RULES`), SAProuter-Routen-Parsing (`parseSapRouteString`), Safety-Guards
  und das Config-Boolean-Parsing. **Keine** SAP-Verbindung nötig; `vitest.config.ts`
  setzt Dummy-Env und einen `.js`→`.ts`-Resolver für die NodeNext-Imports. 36 Tests grün.
- **Security:** `npm audit fix` → **0 Schwachstellen** (vorher 12). `abap-adt-api` zog
  innerhalb von `^7.1.0` auf 7.1.3 (bereinigtes `fast-xml-parser`), `axios` auf 1.16.1.
- **Robustheit:**
  - `config.bool()` akzeptiert jetzt `true`/`1`/`yes`/`on` (case-insensitiv) statt nur
    exakt `"true"`. Pure, exportierte `parseBoolean()` für Testbarkeit.
  - `assertSelectOnly()` erlaubt nun auch `WITH`-CTEs und lehnt DML-Schlüsselwörter als
    eigenständige Wörter ab (`\b…\b`, d.h. `delete_flag` u.ä. lösen nicht mehr fälschlich
    aus). Kommentar stellt klar: Defense-in-Depth, nicht die primäre Barriere.
- **Doku-Konsistenz:** Tool-Zählung überall auf **50 Tools / 14 Gruppen** korrigiert
  (vorher 30+/47/48/13 verstreut). In `DOCUMENTATION.md` fehlte die Gruppe **WEBSEARCH**
  in der Tabelle und READ war mit 10 statt 11 angegeben — beide ergänzt/korrigiert.
- **Kommentare:** Deutsche Kommentare in `src/helpers/clean-abap.ts` auf Englisch
  vereinheitlicht (Rest des Codebestands ist englisch).

**Dateien:**
- `vitest.config.ts` (neu), `test/clean-abap.test.ts`, `test/saprouter.test.ts`,
  `test/safety.test.ts`, `test/config.test.ts` (neu)
- `package.json` — `test`/`test:watch`-Scripts, `vitest` devDependency, Tool-Zahl in der Description
- `package-lock.json` — Security-Updates (`npm audit fix`)
- `src/config.ts` — `parseBoolean()` extrahiert & gehärtet
- `src/safety.ts` — `assertSelectOnly()` gehärtet (WITH-CTE, Wortgrenzen, Kommentar)
- `src/helpers/clean-abap.ts` — Kommentare auf Englisch
- `DOCUMENTATION.md`, `CLAUDE.md` — Tool-Zählung korrigiert, Test-Workflow dokumentiert

---

## 2026-05-30 — Clean ABAP Suche: Regel-genaue Granularität

### Verbesserung: `search_clean_abap` & `review_clean_abap` finden einzelne Regeln

**Problem:** `parseMarkdownSections` zerlegte den Styleguide nur an `##`-Überschriften — also an den 18 Kategorien (Names, Methods, …). Eine einzelne Regel (115 × `###`, 92 × `####`) war damit kein eigener Suchtreffer. Bei der Ausgabe wurde der Abschnitt zudem auf die ersten ~80 Zeilen gekürzt. Folge: Eine tief in einer großen Kategorie (z.B. „Methods", ~1000 Zeilen) liegende Regel wie *„Prefer RETURNING to EXPORTING"* (Zeile 2512) wurde nie im Auszug gezeigt — die KI bekam nur den Kategorie-Anfang. Zusätzlich gewann das Inhaltsverzeichnis (`## Content`) fast jede Suche, weil es jeden Begriff als Link enthält.

**Lösung:**
- `parseMarkdownSections` splittet jetzt an `##`/`###`/`####` → **226 statt 18** durchsuchbare Abschnitte. Jede Regel ist ein eigener Treffer **inkl. ihrer Code-Beispiele**.
- Headings tragen einen Breadcrumb-Pfad (z.B. `Methods › Parameter Types › Use either RETURNING or EXPORTING …`), damit Kategorie-Kontext für Scoring und Anzeige erhalten bleibt.
- Neuer Helper `isNavigationSection()` filtert das Inhaltsverzeichnis (`Content`) und den Intro-Block aus den Suchergebnissen — gilt für `search_clean_abap` und die Guideline-Auszüge von `review_clean_abap`.

**Wirkung (verifiziert gegen `clean-abap/CleanABAP.md`):** Suchen wie „RETURNING EXPORTING single output", „CASE instead of ELSE IF", „raise exception CX_STATIC_CHECK" liefern jetzt die exakte Regel mit Beispiel statt eines abgeschnittenen Kategorie-Intros.

**Begleitend — verpflichtender Lookup:** Skill (`.claude/skills/clean-abap/SKILL.md`) und `.clinerules` wurden so verschärft, dass die KI pro Thema **zuerst** `search_clean_abap` (bzw. das Lesen der Zeilenbereiche) aufruft und erst dann codet — die Kurz-Zusammenfassung ist explizit nur eine Checkliste, kein Ersatz für den Volltext.

**Dateien:**
- `src/helpers/clean-abap.ts` — `parseMarkdownSections` (h2/h3/h4 + Breadcrumb), neuer `isNavigationSection()`, Filter in `searchCleanAbapSections`
- `src/tools/handlers/documentation.ts` — Navigations-Filter in `handleSearchCleanAbap`
- `.claude/skills/clean-abap/SKILL.md` — verpflichtender Lookup-Block
- `.clinerules` — Step 3 auf verpflichtenden Per-Thema-Lookup verschärft

> **Hinweis:** Änderung wirkt erst nach `npm run build`. (Aktuell schlägt der Build wegen fehlender Dependencies `http-proxy-agent`/`https-proxy-agent` fehl — vorher `npm install` ausführen.)

---

## 2026-05-30 — Clean ABAP Claude Skill

### Neue Claude Skill: `clean-abap`

**Hintergrund:** Das Repository enthält unter `clean-abap/` den vollständigen Clean-ABAP-Styleguide (`CleanABAP.md`, ~5150 Zeilen) inkl. Sub-Sections und Cheat-Sheets. Dieser Inhalt war bisher nur als Referenzdokument vorhanden — Claude Code zog ihn nicht automatisch heran, wenn ABAP-Code geschrieben oder reviewt wurde.

**Lösung:** Eine projektgebundene Claude Skill `clean-abap`, die automatisch greift, sobald ABAP-Code erzeugt, reviewt oder refaktoriert wird. Die `SKILL.md` ist eine kompakte Arbeitszusammenfassung (Golden Rules + die wirkungsvollsten/häufigsten Regeln inline) und verweist per Progressive Disclosure mit Zeilennummern auf den vollständigen `clean-abap/CleanABAP.md` — kein 192-KB-Dump in den Kontext.

**Technische Details:**
- Speicherort: `.claude/skills/clean-abap/SKILL.md` (Project Skill, in den Repo eingecheckt)
- Frontmatter `description` ist auf die Trigger-Fälle (ABAP schreiben/reviewen/refaktorieren) zugeschnitten
- Referenziert die bestehenden Dateien unter `clean-abap/` an Ort und Stelle (keine Duplikation), inkl. Navigations-Tabelle (18 Sektionen → Zeilennummern) und Sub-Section-Verweisen
- Explizite Konflikt-Präzedenz: (1) Konvention des bearbeiteten Objekts → (2) Projektkonventionen (CLAUDE.md / Memory) → (3) Clean-ABAP-Defaults. Dadurch werden projekteigene Vorgaben (z.B. `*` in Spalte 1 für Vollzeilenkommentare) respektiert
- Ergänzt — ohne zu duplizieren — den bestehenden `abap_develop` MCP-Prompt (dessen Schritt 3 die Clean-ABAP-Prüfung ist) und die Quality-/Diagnostics-Tools
- Aktivierung: Project Skills werden beim Session-Start geladen → Claude Code neu starten

**Dateien:**
- `.claude/skills/clean-abap/SKILL.md` — neue Skill-Definition
- `DOCUMENTATION.md` — Abschnitt „Claude Skills“ ergänzt
- `readme.md` — Hinweis auf die Skill ergänzt

---

## 2026-03-25 — get_table_fields Tool

### Neues Tool: `get_table_fields`

**Problem:** `get_ddic_element` nutzt den ADT-Endpoint `/sap/bc/adt/ddic/ddl/elementinfo`, der primär für CDS/DDL-Elemente konzipiert ist. Bei klassischen DDIC-Tabellen (VBAK, MARA etc.) liefert er leere Ergebnisse (`children: [], elementProps: false`).

**Lösung:** Neues Tool `get_table_fields`, das den Data-Preview-Endpoint (`tableContents` mit `rowNumber=1`) nutzt. Dieser liefert zuverlässig den kompletten Feldkatalog für transparente Tabellen, Views und CDS-Entities — inkl. Feldname, ABAP-Typ, Beschreibung, Key-Flag und Länge.

**Technische Details:**
- Ruft `client.tableContents(tableName, 1, false)` auf und gibt nur das `columns`-Array zurück
- Mappt `QueryResultColumn` auf ein kompaktes Feld-Objekt (name, type, description, isKey, length, isKeyFigure)
- Zusammenfassung in der Antwort: Anzahl Felder + Anzahl Key-Felder
- Kategorie: READ
- Nicht in Core Tools (Deferred Loading)

**Dateien:**
- `src/schemas.ts` — `S_GetTableFields` Schema
- `src/tools/tool-definitions.ts` — Tool-Definition
- `src/tools/handlers/read.ts` — `handleGetTableFields` Handler
- `src/tools/handler-map.ts` — Dispatch-Eintrag
- `src/tools/tool-registry.ts` — READ-Kategorie + Short Description
- `DOCUMENTATION.md` — Tool-Referenz
- `readme.md` — Tool-Zähler aktualisiert (49 → 50)

---

## 2026-03-25 — search_source_code als Core Tool

### Änderung: `search_source_code` zu Core Tools hinzugefügt

**Hintergrund:** Quellcode-Volltextsuche ist eine Grundfunktion bei der ABAP-Entwicklung. Zusammen mit `search_abap_objects` bildet es das Such-Paar — Objekte nach Name vs. Inhalte nach Text. Es wird in den meisten Workflows gebraucht (Bug-Suche, Refactoring, Impact-Analyse) und sollte ohne vorheriges `find_tools` verfügbar sein.

**Änderung:** `search_source_code` ist jetzt eines von 12 Core Tools (vorher 11) und wird bei `DEFER_TOOLS=true` immer sofort geladen.

**Core Tools (12):** `find_tools`, `list_tools`, `search_abap_objects`, `search_source_code`, `read_abap_source`, `write_abap_source`, `get_object_info`, `where_used`, `analyze_abap_context`, `search_abap_syntax`, `validate_ddic_references`, `batch_read`

**Dateien:**
- `src/tools/tool-registry.ts` — `CORE_TOOL_NAMES` erweitert
- `CLAUDE.md` — Core-Tool-Liste aktualisiert
- `readme.md` — Banner-Anzeige aktualisiert
- `DOCUMENTATION.md` — Kern-Tool-Anzahl aktualisiert

---

## 2026-03-25 — search_sap_web Tool (Tavily Web Search)

### Neues Tool: `search_sap_web`

**Problem:** Die bestehenden Doku-Tools (`get_abap_keyword_doc`, `search_abap_syntax`) arbeiten mit direkter URL-Konstruktion und finden nur Treffer, wenn der Keyword-Slug exakt passt. Fuer Fehlermeldungen, SAP Notes, Community-Blogartikel, KBAs und allgemeine SAP-Problemloesungen fehlte eine Suchmoeglichkeit.

**Loesung:** Das neue `search_sap_web`-Tool durchsucht SAP Help, SAP Community und SAP Notes via Tavily Search API. Es gibt kompakte Ergebnisse zurueck (Titel + URL + Snippet), um den Token-Verbrauch minimal zu halten.

**Technische Details:**
- Nutzt Tavily Search API (1000 Searches/Monat kostenlos)
- Durchsucht parallel bis zu 3 Quellen: `help.sap.com`, `community.sap.com`, `me.sap.com`
- Query wird automatisch mit "SAP ABAP" angereichert fuer bessere Relevanz
- Parallele Ausfuehrung via `Promise.allSettled()` — alle Quellen gleichzeitig
- Ergebnis pro Treffer: Titel + URL + Snippet (~3 Zeilen) — gesamtes Tool-Ergebnis unter 500 Tokens
- Fehlertoleranz: Einzelne fehlgeschlagene Quellen stoppen nicht die anderen

**Setup:**
1. https://tavily.com/ → Sign up → API Key kopieren
2. `TAVILY_API_KEY` in `.env` eintragen

**Beispiel:**
```json
{
  "tool": "search_sap_web",
  "args": {
    "query": "CX_SY_OPEN_SQL_DB error SELECT",
    "sources": ["help", "community"],
    "maxResults": 5
  }
}
```

**Kosten:** Free Tier: 1000 Searches/Monat.

**Neue Kategorie:** WEBSEARCH (in `TOOL_CATEGORIES`)

**Dateien:**
- `src/config.ts` — `tavilyApiKey` Config-Feld
- `src/schemas.ts` — `S_SearchSapWeb` Schema
- `src/tools/handlers/websearch.ts` — Handler (neu)
- `src/tools/tool-definitions.ts` — Tool-Definition
- `src/tools/handler-map.ts` — Dispatch-Registrierung
- `src/tools/tool-registry.ts` — Kategorie + Short Description
- `.env` / `.env.example` — `TAVILY_API_KEY`
- `src/index.ts` — Banner zeigt WebSearch-Status

---

## 2026-03-25 — batch_read Tool (Performance-Optimierung)

### Neues Tool: `batch_read`

**Problem:** MCP-Clients wie Cline (VS Code Extension) fuehren Tool-Aufrufe sequenziell aus — ein Call nach dem anderen. Bei ABAP-Entwicklungsworkflows, die viele Leseoperationen erfordern (Source lesen, Where-Used, Object Info, Kontext-Analyse), fuehrt das zu langen Wartezeiten.

**Loesung:** Das neue `batch_read`-Tool buendelt mehrere Read-Only-Operationen in einem einzigen MCP-Call. Der Server fuehrt sie intern parallel via `Promise.allSettled()` aus und gibt alle Ergebnisse zusammen zurueck.

**Technische Details:**
- Bis zu 20 Operationen pro Batch-Call
- Jede Operation referenziert ein bestehendes Tool (Name + Args)
- Nur Read-Only-Tools erlaubt — Write/Create/Delete sind blockiert
- Ergebnisse werden pro Operation mit Label und Status (OK/FEHLER) zurueckgegeben
- Fehlertoleranz: Einzelne fehlgeschlagene Operationen stoppen nicht den Batch
- Als Core-Tool registriert (immer verfuegbar, kein `find_tools` noetig)

**Beispiel:**
```json
{
  "tool": "batch_read",
  "args": {
    "operations": [
      { "tool": "read_abap_source", "args": { "objectUrl": "/sap/bc/adt/programs/programs/ztest", "includeRelated": true }, "label": "source" },
      { "tool": "where_used", "args": { "objectUrl": "/sap/bc/adt/programs/programs/ztest" }, "label": "usages" },
      { "tool": "get_object_info", "args": { "objectUrl": "/sap/bc/adt/programs/programs/ztest" }, "label": "info" }
    ]
  }
}
```

**Performance-Gewinn:**
- Cline sieht 1 Tool-Call statt N
- Server feuert N HTTP-Requests parallel an SAP
- Gesamtzeit ~ langsamster Einzelrequest statt Summe aller Requests

**Hintergrund:** ADT (ABAP Development Tools) REST API hat keine native Batch-API. Die Parallelisierung passiert im Node.js MCP Server, der die einzelnen HTTP-Requests via `Promise.allSettled()` gleichzeitig abfeuert.

**Neue Kategorie:** BATCH (in `TOOL_CATEGORIES`)

**Dateien:**
- `src/schemas.ts` — `S_BatchRead` Schema
- `src/tools/handlers/batch.ts` — Handler (neu)
- `src/tools/tool-definitions.ts` — Tool-Definition
- `src/tools/handler-map.ts` — Dispatch-Registrierung
- `src/tools/tool-registry.ts` — Kategorie + Core-Tool + Short Description
