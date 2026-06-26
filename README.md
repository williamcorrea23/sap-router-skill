# SAP Router Orchestrator v4.0

> **Build SAP applications from your IDE. No SAP GUI required.**
>
> Talk to SAP in plain English. Read ABAP source, create materials, post documents,
> deploy iFlows, run transports — all from VS Code. Self-learning router picks the
> fastest path: ADT direct, SAP GUI fallback, or ZROUTER batch. Every action verified.
> Every route learned. Every response compressed.

---

## What It Does

You type **"create material FERT with these fields"** in VS Code chat. The router:

1. **Thinks** — surfaces assumptions, picks the best BAPI, checks authorizations
2. **Routes** — ADT? GUI? RFC? Picks fastest available path, learns from every call
3. **Executes** — calls the BAPI, checks BAPIRET2, commits the transaction
4. **Verifies** — confirms in MM03, logs to BAL, runs ABAP Unit tests
5. **Learns** — records MCP latency, adapts future routes to be faster

**No SAP GUI. No Eclipse. No SE80. No transaction codes to memorize.**

---


---

## Quick Overview

```mermaid
flowchart TB
    subgraph User["User"]
        REQ["SAP Development Request"]
    end

    subgraph Karpathy["Karpathy Wrapper"]
        direction TB
        P0["0. Healthcheck — verify .env + MCPs"]
        P1["1. Think — surface assumptions, state tradeoffs"]
        P2["2. Simplify — pick simplest path"]
        P3["3. Surgical — touch only what's needed"]
        P4["4. Goal-Verify — loop until criteria met"]
        P0 --> P1 --> P2 --> P3 --> P4
    end

    subgraph Routing["Self-Learning Router"]
        R1["Caveman? → cavecrew-investigator/builder/reviewer"]
        R2["ADT? → arc-1 / aibap"]
        R3["GUI? → mcp-sap-gui (immediate)"]
        R4["Batch? → ZROUTER RFC"]
        R5["Pipeline? → 8-stage workflow"]
        R6["LLM? → sap-llm-engineering"]
        R1 --> R2 --> R3 --> R4 --> R5 --> R6
        LEARN["Self-learn adapts routing weights<br/>based on MCP latency + success rates"]
        LEARN -.-> R1
    end

    subgraph Targets["SAP Systems"]
        S4H["S/4HANA (ADT + RFC + GUI)"]
        BTP["SAP BTP"]
        CPI["SAP CPI"]
        SF["SuccessFactors"]
        S4H --- BTP --- CPI --- SF
    end

    REQ --> Karpathy
    Karpathy --> Routing
    Routing --> Targets
```

## Routing Decision Tree

```mermaid
flowchart TD
    REQ["User Request"] --> Q1{"CAVEMAN scope?<br/>1-2 files, find/fix/review"}
    Q1 -->|"YES"| CV["cavecrew-investigator<br/>cavecrew-builder<br/>cavecrew-reviewer"]
    Q1 -->|"NO"| Q2{"ADT operation?<br/>read, write, search, activate"}
    Q2 -->|"YES"| ADT["arc-1 (primary)<br/>aibap (secondary)<br/>mcp-abap-adt (tertiary)"]
    Q2 -->|"NO"| Q3{"GUI required?<br/>SPRO,SM30,SU01,MM01,VA01..."}
    Q3 -->|"YES"| GUI["IMMEDIATE GUI fallback<br/>mcp-sap-gui → kts → Go<br/>Missing data? Web-enrich"]
    Q3 -->|"NO"| Q4{"BAPI batch?<br/>create PO, post FI..."}
    Q4 -->|"YES"| RFC["ZROUTER RFC<br/>9 module handlers"]
    Q4 -->|"NO"| Q5{"Spec pipeline?<br/>implement specification"}
    Q5 -->|"YES"| PL["8-stage pipeline<br/>Spec → Transport"]
    Q5 -->|"NO"| Q6{"LLM optimize?"}
    Q6 -->|"YES"| LLM["sap-llm-engineering<br/>eval → optimize → retry"]
    Q6 -->|"NO"| DEF["Default: ZROUTER RFC"]

    style CV fill:#4a9,color:#fff
    style ADT fill:#48f,color:#fff
    style GUI fill:#f80,color:#fff
    style RFC fill:#94f,color:#fff
    style PL fill:#f4a,color:#fff
    style LLM fill:#0af,color:#fff
```

---

## Quick Start

### Option A — Global Skill (Recommended)

```bash
# Install as global Claude Code skill
/plugin marketplace add forrestchang/andrej-karpathy-skills
# SAP Router auto-activates on any SAP task — skills trigger by file context + keywords
```

### Option B — Project Clone

```bash
git clone https://github.com/<your-username>/sap-router-orchestrator.git
cd sap-router-orchestrator/sap-router-skill
```

### Option C — Update Existing Installation

```bash
# Update to latest version
cd sap-router-skill
git pull origin main
python scripts/healthcheck.py          # Verify health after update
npm install                             # Update abaplint + deps
python scripts/self_learn.py persist   # Preserve learned context
```

### Post-Install — Healthcheck + .env Setup

```bash
# Run healthcheck — probes all 19 MCPs + verifies .env
npm run hc

# If .env missing, generate interactive prompt
npm run hc:prompt

# Copy template and fill credentials
cp .env.template .env
# Edit .env — fill ARC_SAP_URL, ARC_SAP_USER, ARC_SAP_PASSWORD, ARC_SAP_CLIENT
```

---

## Core Commands

```mermaid
flowchart LR
    subgraph Health["Healthcheck"]
        HC["npm run hc<br/>probes 19 MCPs + .env"]
        HCP["npm run hc:prompt<br/>interactive setup"]
    end
    subgraph Routes["Routing"]
        RT["npm run router<br/>route any action"]
        RG["npm run router:gui<br/>force GUI fallback"]
        RC["npm run router:caveman<br/>check delegation"]
    end
    subgraph Pipeline["Pipeline"]
        PL["npm run pipeline<br/>8-stage spec→transport"]
        PF["npm run pipeline:fast<br/>skip deep analysis"]
    end
    subgraph SelfLearn["Self-Learn"]
        LM["npm run learn:mcp<br/>record MCP outcome"]
        LR["npm run learn:route<br/>track routing success"]
        LC["npm run learn:ctx<br/>inject context"]
    end
    subgraph Lint["ABAP Quality"]
        AL["npm run abap:lint"]
        AR["npm run abap:review"]
        AC["npm run abap:review:ci"]
    end
```

| Category | Command | What It Does |
|---|---|---|
| **Install** | `git clone ... && python scripts/healthcheck.py` | Clone + verify everything works |
| **Update** | `git pull && npm install && npm run hc` | Pull latest + refresh deps + healthcheck |
| **Health** | `npm run hc` | Probes 19 MCPs + .env completeness |
| **Health** | `npm run hc:prompt` | Interactive setup wizard for missing vars |
| **Route** | `npm run router -- --action MM_CREATE_MATERIAL` | Route action: ADT → GUI → RFC |
| **Route** | `npm run router:gui -- --action SPRO_CONFIG` | Force SAP GUI fallback |
| **Route** | `npm run router:caveman -- --task "find all BAPI"` | Check caveman delegation |
| **Pipeline** | `npm run pipeline -- requirements.md` | Full spec-to-transport (8 stages) |
| **Pipeline** | `npm run pipeline:fast -- requirements.md` | Fast pipeline (skip deep analysis) |
| **Learn** | `npm run learn:mcp -- --mcp arc-1 --latency 245 --success true` | Record MCP call outcome |
| **Learn** | `npm run learn:route -- --action MM_CREATE --success true` | Track routing success |
| **Learn** | `npm run learn:ctx` | Inject learned context into routing |
| **Lint** | `npm run abap:lint` | Static ABAP code analysis |
| **Lint** | `npm run abap:review` | Full review: lint + security + clean |
| **Lint** | `npm run abap:review:ci` | CI mode: fails on CRITICAL |
| **GUI** | `npm run gui:enrich -- --tcode MM01` | Web-search enrich GUI nav data |
| **GUI** | `npm run gui:status` | Show GUI enrichment cache status |
| **Data** | `npm run template -- --module MM --action CREATE_MATERIAL` | Generate XLS template |
| **Data** | `npm run convert -- --input data.csv --module MM` | XLS/CSV → BAPI JSON |
| **Serialize** | `npm run serialize -- --source file.abap --name ZCL_FOO` | Package ABAP for abapGit/.nugg/XML |
| **CPI** | `python scripts/cpi_iflow_packager.py template --name my-flow` | Create CPI iFlow ZIP |

---

## Complete Skill Catalog (75 skills)

```mermaid
flowchart TB
    subgraph ABAP["ABAP Development — 15 skills"]
        A1["abap — classical ABAP, dynpro, ALV"]
        A2["abap-cloud — steampunk, released APIs"]
        A3["abap-cloud-migration — custom code to cloud"]
        A4["abap-code-patterns — BAPI/RFC, dynamic ABAP"]
        A5["abap-sql-amdp — SQL, AMDP, HANA procedures"]
        A6["abap-unit-testing — ABAP Unit, test doubles"]
        A7["abapgit — Git workflows for ABAP"]
        A8["atc-cloudification — ATC checks, quality gates"]
        A9["authorization-iam — AUTHORITY-CHECK, IAM"]
        A10["badi-enhancement — BAdI, enhancement spots"]
        A11["clean-abap — Clean ABAP Style Guide"]
        A12["rap — RAP managed/unmanaged, EML"]
        A13["rap-business-events — event mesh, CloudEvents"]
        A14["cds-view-entities — CDS DDL, annotations"]
        A15["released-abap-classes — C1/C2/C3 contracts"]
    end

    subgraph BTP["SAP BTP — 18 skills"]
        B1["btp-abap-environment — BTP ABAP projects"]
        B2["btp-best-practices — CF vs Kyma, resilience"]
        B3["btp-build-work-zone — workspaces, cards"]
        B4["btp-business-application-studio — BAS dev spaces"]
        B5["btp-cias — CIAS automation"]
        B6["btp-cloud-identity — IAS/IPS/AMS"]
        B7["btp-cloud-logging — OpenTelemetry, Kibana"]
        B8["btp-cloud-platform — accounts, entitlements"]
        B9["btp-cloud-transport-management — CTM, gCTS"]
        B10["btp-connectivity — Cloud Connector"]
        B11["btp-developer-guide — BTP reference"]
        B12["btp-diagram-generator — architecture diagrams"]
        B13["btp-integration-suite — CPI, API Mgmt"]
        B14["btp-job-scheduling — cron jobs"]
        B15["btp-master-data-integration — MDI"]
        B16["btp-service-manager — instances, bindings"]
        B17["sap-btp-audit-log — audit trails"]
        B18["sap-btp-credential-store — secrets vault"]
    end

    subgraph FRONT["UI5 / Fiori / CAP — 7 skills"]
        F1["sapui5-framework — UI5 patterns"]
        F2["sap-fiori-tools — Fiori generation"]
        F3["sap-fiori-apps-reference — apps catalog"]
        F4["sap-cap — CAP CDS + Node.js/Java"]
        F5["sap-build — low-code apps, workflows"]
        F6["odata — OData V2/V4 protocol"]
        F7["odata-abap — SEGW, CDS-exposed OData"]
    end

    subgraph INT["Integration — 4 skills"]
        I1["cpi-iflow-development — iFlow, Groovy"]
        I2["sap-bapi-integration — BAPI discovery, patterns"]
        I3["sap-code-search — full-text ABAP search"]
        I4["sap-api-style — OpenAPI specs, standards"]
    end

    subgraph HANA["HANA / AI / Data — 10 skills"]
        H1["sap-hana-sqlscript — SQLScript procedures"]
        H2["sap-hana-cli — HANA CLI operations"]
        H3["sap-hana-ml — ML on HANA"]
        H4["sap-ai-core — AI Core, model deployment"]
        H5["sap-cloud-sdk-ai — GenAI Hub, LLM orchestration"]
        H6["sap-datasphere — data modeling, federation"]
        H7["sap-hana-cloud-data-intelligence — DI"]
        H8["sap-sac-scripting — SAC automation"]
        H9["sap-sac-planning — SAC planning"]
        H10["sap-sac-custom-widget — custom widgets"]
    end

    subgraph VNEW["v4.0 NEW — 5 skills"]
        V1["karpathy-guidelines — Think→Simplify→Surgical→Verify"]
        V2["sap-gui-scripting — SAP GUI automation, BDC, ALV"]
        V3["sap-gui-web-enrich — web-search for missing nav data"]
        V4["sap-self-learn — Hermes-style environment adaptation"]
        V5["sap-llm-engineering — eval harness, prompt optimization"]
    end
```

### Skill Categories

| Domain | Count | Skills |
|---|---|---|
| **ABAP Core** | 15 | `abap`, `abap-cloud`, `abap-cloud-migration`, `abap-code-patterns`, `abap-sql-amdp`, `abap-unit-testing`, `abapgit`, `atc-cloudification`, `authorization-iam`, `badi-enhancement`, `clean-abap`, `rap`, `rap-business-events`, `cds-view-entities`, `released-abap-classes` |
| **SAP BTP Platform** | 18 | `btp-abap-environment`, `btp-best-practices`, `btp-build-work-zone`, `btp-business-application-studio`, `btp-cias`, `btp-cloud-identity`, `btp-cloud-logging`, `btp-cloud-platform`, `btp-cloud-transport-management`, `btp-connectivity`, `btp-developer-guide`, `btp-diagram-generator`, `btp-integration-suite`, `btp-job-scheduling`, `btp-master-data-integration`, `btp-service-manager`, `sap-btp-audit-log`, `sap-btp-credential-store` |
| **UI5 / Fiori / CAP** | 7 | `sapui5-framework`, `sap-fiori-tools`, `sap-fiori-apps-reference`, `sap-cap`, `sap-build`, `odata`, `odata-abap` |
| **Integration** | 4 | `cpi-iflow-development`, `sap-bapi-integration`, `sap-code-search`, `sap-api-style` |
| **HANA / AI / Data** | 10 | `sap-hana-sqlscript`, `sap-hana-cli`, `sap-hana-ml`, `sap-ai-core`, `sap-cloud-sdk-ai`, `sap-datasphere`, `sap-hana-cloud-data-intelligence`, `sap-sac-scripting`, `sap-sac-planning`, `sap-sac-custom-widget` |
| **Security / Infra** | 7 | `sap-dependency-security`, `sap-btp-document-mgmt`, `sap-btp-feature-flags`, `sap-btp-html5-repo`, `sap-btp-kyma`, `sap-btp-launchpad`, `sap-btp-saas` |
| **Router / Tooling** | 8 | `run-sap-router-skill`, `sap-transport-management`, `sap-crew-analysis`, `sap-rap-gen`, `sap-rpt1`, `sap-sac-test-automation`, `sap-api-policy`, `sap-workflow-pipeline` |
| **v4.0 NEW** | 5 | **`karpathy-guidelines`**, **`sap-gui-scripting`**, **`sap-gui-web-enrich`**, **`sap-self-learn`**, **`sap-llm-engineering`** |
| **Shared** | 1 | `abap-code-review` (GitHub: `shrek-abaper/sap-engineering-skill`) |

---

## MCP Server Reference (19 servers)

```mermaid
flowchart TB
    subgraph Primary["Primary Path"]
        ARC["arc-1<br/>12 intent tools<br/>npm package<br/>3,474 tests"]
        AIB["aibap.mcp<br/>69 granular tools<br/>Go binary<br/>comprehensive ABAP"]
        ADT2["mcp-abap-adt<br/>13 tools<br/>TypeScript<br/>Smithery deploy"]
    end

    subgraph Fallback["GUI Fallback (3 tiers)"]
        G1["mcp-sap-gui<br/>mario-andreschak<br/>TypeScript<br/>PRIMARY fallback"]
        G2["mcp-sap-gui-kts<br/>kts982<br/>Python<br/>SECONDARY"]
        G3["sapgui-mcp-go<br/>Hochfrequenz<br/>Go<br/>TERTIARY"]
        G1 --> G2 --> G3
    end

    subgraph RFC["RFC Dispatch"]
        RFCM["sap-rfc-mcp-server<br/>ZROUTER_DISPATCH_FM<br/>9 module handlers<br/>BAPI batch operations"]
    end

    subgraph HCM["HCM"]
        SF["sf-mcp<br/>SuccessFactors OData<br/>Employee data, org structure"]
    end

    subgraph BTP2["BTP / OData"]
        BT["btp-mcp<br/>7 entity sets<br/>OData-based"]
        OD1["odata-mcp-proxy<br/>32 entities<br/>config-driven"]
        OD2["btp-sap-odata-to-mcp<br/>3 progressive tools<br/>token-optimized"]
    end

    subgraph RAG["RAG (pre-ready)"]
        R1["pinecone-rag<br/>vector DB"]
        R2["supabase-rag<br/>pgvector"]
        R3["azure-ai-search<br/>semantic search"]
    end

    subgraph Plugins["IDE Plugins"]
        P1["ui5-mcp-server"]
        P2["fiori-mcp-server"]
        P3["mdk-mcp-server"]
        P4["cds-mcp-server"]
    end
```

### MCP Details

| # | MCP Server | Type | Tools/Entities | Criticality | Description |
|---|---|---|---|---|---|
| 1 | `arc-1` | stdio (npx) | 12 intent tools | **HIGH** | Enterprise ADT — SAPRead, SAPWrite, SAPSearch, SAPActivate, SAPTransport, SAPDiagnose |
| 2 | `aibap` | stdio (Go) | 69 tools | **HIGH** | ABAP dev — source, objects, testing, ST22, BAdI, DEBUG, transport |
| 3 | `mcp-abap-adt` | stdio (node) | 13 tools | MEDIUM | TypeScript ADT bridge — GetProgram, GetClass, GetTable, SearchObject |
| 4 | `mcp-sap-gui` | stdio (node) | GUI automation | MEDIUM | Primary GUI fallback — navigate, BDC, ALV read, popup handling |
| 5 | `mcp-sap-gui-kts` | stdio (python) | GUI automation | LOW | Secondary GUI (kts982) — broader transaction coverage |
| 6 | `sapgui-mcp-go` | stdio (Go) | GUI automation | LOW | Tertiary GUI (Hochfrequenz) — lightweight Go bridge |
| 7 | `sap-rfc-mcp-server` | stdio (python) | RFC dispatch | MEDIUM | ZROUTER dispatch — 9 module handlers via BAPI/RFC |
| 8 | `sf-mcp` | stdio (node) | OData V2 | LOW | SuccessFactors HCM — Employee, Org, Compensation, Time |
| 9 | `mcp-sap-notes` | stdio (node) | 2 tools | LOW | SAP Notes search + fetch from me.sap.com |
| 10 | `btp-mcp` | stdio (node) | 7 entities | LOW | BTP account management — GlobalAccount, Subaccounts, Entitlements |
| 11 | `odata-mcp-proxy` | stdio (node) | 32 entities | LOW | CPI admin OData bridge — config-driven |
| 12 | `btp-sap-odata-to-mcp` | stdio (node) | 3 tools | MEDIUM | Progressive discovery OData — discover → metadata → execute |
| 13 | `pinecone-rag` | stdio (node) | vector store | OPTIONAL | Pinecone vector DB — RAG pipeline for SAP knowledge |
| 14 | `supabase-rag` | stdio (node) | pgvector | OPTIONAL | Supabase pgvector — RAG pipeline alternative |
| 15 | `azure-ai-search` | stdio (node) | semantic search | OPTIONAL | Azure AI Search — enterprise semantic search |
| 16 | `ui5-mcp-server` | plugin | 10 tools | LOW | UI5/SAPUI5 app creation, linter, API reference |
| 17 | `fiori-mcp-server` | plugin | 8 tools | LOW | Fiori app generation (CAP/RAP), metadata, modification |
| 18 | `mdk-mcp-server` | plugin | 5 tools | LOW | MDK project creation, page/action generation, deploy |
| 19 | `cds-mcp-server` | plugin | 2 tools | LOW | CAP CDS model search, documentation |

---

## 8-Stage Spec-to-Transport Pipeline

```mermaid
flowchart LR
    S1["Stage 1<br/>Spec Analysis<br/>~10s"] --> S2["Stage 2<br/>Technical Proposal<br/>~3min"]
    S2 --> S3["Stage 3<br/>Peer Review 1<br/>~1min"]
    S3 -->|"GO"| S4["Stage 4<br/>Implementation<br/>cavecrew + ADT"]
    S3 -->|"NO-GO"| S2
    S4 --> S5["Stage 5<br/>Static Analysis<br/>abaplint ~30s"]
    S5 --> S6["Stage 6<br/>Deep Analysis<br/>7-agent Crew ~5min"]
    S6 --> S7["Stage 7<br/>Peer Review 2<br/>~1min"]
    S7 -->|"GO"| S8["Stage 8<br/>Transport Gate<br/>10-dim risk check"]
    S7 -->|"NO-GO"| S4
    S8 -->|"PASS"| TR["TRANSPORT RELEASED"]
    S8 -->|"BLOCK"| S4

    style S1 fill:#48f,color:#fff
    style S2 fill:#94f,color:#fff
    style S3 fill:#f4a,color:#fff
    style S4 fill:#4a9,color:#fff
    style S5 fill:#0af,color:#fff
    style S6 fill:#94f,color:#fff
    style S7 fill:#f4a,color:#fff
    style S8 fill:#f80,color:#fff
    style TR fill:#4a9,color:#fff
```

### Pipeline Stages Detail

| Stage | Skill/Tool | Verification | Resumable |
|---|---|---|---|
| 1 — Spec Analysis | `sap_router.py analyze-spec` | Module identified, BAPIs listed | Yes |
| 2 — Technical Proposal | `sap-crew-analysis` (7 agents) | Architecture review pass | Yes |
| 3 — Peer Review 1 | `abap-code-review` (9 dimensions) | Score >= 70/100 | Yes |
| 4 — Implementation | `cavecrew-builder` + ADT MCP | Syntax OK, unit tests pass | Yes |
| 5 — Static Analysis | `npm run abap:review` (abaplint) | 0 CRITICAL, 0 HIGH | Yes |
| 6 — Deep Analysis | `sap-crew-analysis` (full mode) | Score >= 70/100 | Yes |
| 7 — Peer Review 2 | `abap-code-review` (GO/NO-GO) | All dimensions pass | No (restart from 4) |
| 8 — Transport Gate | `sap-transport-gate` (10 dims) | Transport released | No (restart from 4) |

---

## Self-Learning Engine

```mermaid
flowchart TB
    subgraph Input["Every MCP Call / Route Decision"]
        MCP["MCP call: arc-1, latency=245ms, success=true"]
        RTE["Route: MM_CREATE_MATERIAL, success=true"]
    end

    subgraph Learn["Self-Learn Engine"]
        direction TB
        REC["Record observation<br/>EMA latency + success rate"]
        ADAPT["Adapt routing weights<br/>prefer faster, reliable MCPs"]
        DISC["Discover system features<br/>SAP version, HANA, gCTS, RAP"]
        PATT["Learn user patterns<br/>batch preference, ADT preference"]
        REC --> ADAPT
        ADAPT --> DISC
        DISC --> PATT
    end

    subgraph Output["Persisted Context"]
        MEM["MEMORY.md ## LEARN section"]
        CTX["Compressed prompt injection<br/>~50 tokens"]
    end

    Input --> Learn
    Learn --> Output
    Output -.->|"next routing decision"| Input
```

### Learning Dimensions

| Dimension | What It Tracks | Adaptation |
|---|---|---|
| **MCP Latency** | Exponential moving average per MCP | Prefer MCPs < 300ms when equivalent |
| **MCP Reliability** | Success rate (ok/total) | Skip MCPs with < 50% success |
| **Route Confidence** | ok/total per action type | Warn when < 30%, suggest alternatives |
| **System Features** | ADT version, HANA, gCTS, RAP | Adapt code generation targets |
| **User Patterns** | Batch vs single, ADT vs GUI | Memorize preferences per module |
| **Decay** | 24h half-life on observations | Recent data weighted heavier |

---

## Functional Module Coverage

```mermaid
flowchart TB
    MM["MM — Materials Management<br/>BAPI_MATERIAL_SAVEDATA<br/>BAPI_PO_CREATE1/CHANGE<br/>MM01/MM02/ME21N/MIGO<br/>Config: T134, T161, T024"]
    SD["SD — Sales & Distribution<br/>BAPI_SALESORDER_CREATEFROMDAT2<br/>BAPI_BILLINGDOC_CREATEMULTIPLE<br/>VA01/VA02/VL01N/VF01<br/>Config: TVAK, TVKO, TVFK"]
    FI["FI — Financial Accounting<br/>BAPI_ACC_DOCUMENT_POST<br/>BAPI_ACC_DOCUMENT_REV_POST<br/>FB01/FB02/FS00/F110<br/>Config: T001, T004, SKA1"]
    QM["QM — Quality Management<br/>BAPI_INSPLOT_CREATE<br/>BAPI_INSRES_RECORD<br/>QA01/QA02/QE01<br/>Config: TQ01, TQ02"]
    PP["PP — Production Planning<br/>BAPI_PRODORD_CREATE<br/>BAPI_PRODORDCONF_CREATE_HDR<br/>CO01/CO02/CS01/CA01<br/>Config: T003O, T399D"]
    WM["WM — Warehouse Management<br/>BAPI_GOODSMVT_CREATE<br/>L_TO_CREATE_MOVE_SU<br/>MIGO/LT01/LT02<br/>Config: T311, T312, T300"]
    CO["CO — Controlling<br/>BAPI_INTERNALORDER_CREATE<br/>BAPI_ACC_ACTIVITY_ALLOC_POST<br/>KO01/KS01/KA01<br/>Config: TKA01, CSKS"]
    HCM["HCM — Human Capital Mgmt<br/>BAPI_EMPLOYEE_GETDATA<br/>HR_INFOTYPE_OPERATION<br/>PA20/PA30/PA40<br/>SuccessFactors: sf-mcp"]
    BASIS["BASIS — ABAP Dev + Admin<br/>TR_INSERT_REQUEST_WITH_TASKS<br/>TH_GET_DUMP_LOG<br/>SPRO/SU01/SU53/PFCG/SNOTE<br/>ST22/SM37/SM50/SE16"]
```

### Module BAPI/Transaction Reference

| Module | BAPIs Available | GUI Fallback T-codes | Config Tables |
|---|---|---|---|
| **MM** | BAPI_MATERIAL_SAVEDATA, BAPI_PO_CREATE1, BAPI_PO_CHANGE, BAPI_GOODSMVT_CREATE | MM01, MM02, ME21N, MIGO, MMBE | T134, T023, T161, T024, T001W, T156 |
| **SD** | BAPI_SALESORDER_CREATEFROMDAT2, BAPI_SALESORDER_CHANGE, BAPI_BILLINGDOC_CREATEMULTIPLE | VA01, VA02, VL01N, VF01 | TVAK, TVKO, TVFK, TVLK, TVSB, KNVV |
| **FI** | BAPI_ACC_DOCUMENT_POST, BAPI_ACC_DOCUMENT_REV_POST, BAPI_ACC_ACTIVITY_ALLOC_POST | FB01, FB02, FS00, F110 | T001, T004, T003, SKA1, SKB1, TABW |
| **QM** | BAPI_INSPLOT_CREATE, BAPI_INSRES_RECORD | QA01, QA02, QE01 | TQ01, TQ02, QALS, T156Q |
| **PP** | BAPI_PRODORD_CREATE, BAPI_PRODORDCONF_CREATE_HDR, CS_BOM_EXPL_MAT_V2 | CO01, CO02, CS01, CA01 | T003O, T399D, MARC, T024F |
| **WM** | BAPI_GOODSMVT_CREATE, L_TO_CREATE_MOVE_SU | MIGO, LT01, LT02, LS01 | T311, T312, T300, T301 |
| **CO** | BAPI_INTERNALORDER_CREATE, BAPI_ACC_ACTIVITY_ALLOC_POST | KO01, KS01, KA01 | TKA01, CSKS, CSKA, TKA02 |
| **HCM** | BAPI_EMPLOYEE_GETDATA, HR_INFOTYPE_OPERATION | PA20, PA30, PA40 | T500P, T001P, T503, T582A |
| **BASIS** | TR_INSERT_REQUEST_WITH_TASKS, TR_RELEASE_REQUEST, TH_GET_DUMP_LOG | SPRO, SU01, SU53, PFCG, SNOTE | E070, E071, SNAP, SNAPT |

---

## Project Structure

```
sap-router-skill/
├── README.md                    ← This file (Mermaid diagrams)
├── SKILL.md                     ← Master dispatch (Karpathy wrapper)
├── COMPARISON.md                ← 72-repo cross-reference analysis
├── CHANGELOG.md                 ← Version history
├── .mcp.json                    ← 19 MCP servers (3 GUI + 3 RAG)
├── .env.template                ← 30+ env vars grouped by domain
├── .abaplint.json               ← 60+ ABAP lint rules
├── package.json                 ← 34 npm scripts
│
├── .claude/skills/              ← 75 skills (all IDE auto-load)
│   ├── karpathy-guidelines/     ← v4.0: Think→Simplify→Surgical→Verify
│   ├── sap-gui-scripting/       ← SAP GUI automation + BDC + ALV
│   ├── sap-gui-web-enrich/      ← Web-search fill missing nav data
│   ├── sap-self-learn/          ← Hermes-style environment adaptation
│   ├── sap-llm-engineering/     ← LLM eval harness + prompt optimizer
│   ├── sap-workflow-pipeline/   ← 8-stage spec-to-transport
│   ├── sap-api-policy/          ← API Management + OpenAPI specs
│   └── ... (68 more domain skills)
│
├── scripts/                     ← 8 Python CLIs
│   ├── sap_router.py            ← Routing engine (ADT→GUI→RFC→Pipeline)
│   ├── healthcheck.py           ← 19-MCP probe + .env guardian
│   ├── self_learn.py            ← Hermes-style context adaptation
│   ├── memory_manager.py        ← MEMORY.md session lifecycle + ABAPLINT
│   ├── xls_to_bapi.py           ← CSV/XLSX → BAPI JSON (29 actions)
│   ├── template_repo.py         ← ABAP template repository
│   ├── abap_serializer.py       ← .nugg / abapGit / XML packer
│   └── cpi_iflow_packager.py    ← CPI iFlow ZIP creator
│
├── scripts/abap-review-gate.js  ← CI gate (security/clean/transport)
│
├── templates/                   ← 4 ABAP templates
│   ├── ZROUTER_DISPATCH.abap    ← Full framework (1,349 lines)
│   ├── ZCL_ABAP_REPL_V2.abap    ← SICF HTTP REPL handler
│   ├── ZROUTER_DB_TABLES.abap   ← 5 DDIC tables
│   └── ZROUTER_CODE_SEARCH.abap ← ABAP code search integration
│
├── references/                  ← SAP knowledge base
│   ├── module_maps/             ← 10 module operation maps
│   └── trench_knowledge/        ← 14 domain references
│
└── packages/samples/            ← Export samples (.nugg, abapGit, XML, ZIP)
```

---

## Install + Update ZROUTER on SAP

### Fresh Install

```bash
# 1. Create package
aibap: create_object(type="DEVC", name="ZROUTER",
       description="SAP Router Orchestrator")

# 2. Create DDIC data elements (19) + tables (5)
aibap: create_object(type="DTEL", name="ZROUTER_TMPL_ID")
aibap: create_object(type="TABL", name="ZROUTER_TMPL_HD")

# 3. Deploy ABAP classes via abapGit or ADT
python scripts/abap_serializer.py package \
  --source templates/ZROUTER_DISPATCH.abap \
  --name ZCL_ZROUTER_DISPATCH --type CLAS --output deploy/
# Pull deploy/abapgit/ into SAP via abapGit or arc-1 SAPWrite

# 4. Create Function Module
aibap: create_object(type="FUGR", name="ZROUTER")
aibap: create_object(type="FUNC", name="ZROUTER_DISPATCH_FM",
       function_group="ZROUTER")

# 5. Activate + verify
aibap: activate_objects(["ZCL_ZROUTER_DISPATCH","CX_ZROUTER",
       "ZROUTER_DISPATCH_FM","ZROUTER_TMPL_HD","ZROUTER_TMPL_CD",
       "ZROUTER_TMPL_PL","ZROUTER_TMPL_PKG","ZROUTER_TMPL_PKG_T"])
aibap: syntax_check(["ZCL_ZROUTER_DISPATCH","ZROUTER_DISPATCH_FM"])
python scripts/sap_router.py route --action MM_CREATE_MATERIAL
```

### Update Existing Installation

```bash
# Pull latest from GitHub
cd sap-router-skill
git pull origin main

# Refresh dependencies
npm install
pip install --upgrade openpyxl  # if using XLSX features

# Verify health — probes all 19 MCPs
python scripts/healthcheck.py

# Preserve learned context through update
python scripts/self_learn.py persist

# Run linter on updated templates
npm run abap:review

# Update ZROUTER ABAP objects (if template changed)
python scripts/abap_serializer.py package \
  --source templates/ZROUTER_DISPATCH.abap \
  --name ZCL_ZROUTER_DISPATCH --type CLAS --output deploy/
# Re-deploy via abapGit or arc-1 SAPWrite

# Syntax check updated objects
aibap: syntax_check(["ZCL_ZROUTER_DISPATCH","ZROUTER_DISPATCH_FM"])

# Re-run smoke tests
python .claude/skills/run-sap-router-skill/driver.py
```

### Uninstall / Rollback

```bash
# Transport rollback — create return transport
aibap: create_transport(description="Rollback ZROUTER update")

# Or remove objects from transport
aibap: remove_from_transport(objects=["ZCL_ZROUTER_DISPATCH"])
```

---

## Related Repositories

Key integrations:
- [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) — Karpathy behavioral guidelines (adapted as command format)
- [arc-mcp/arc-1](https://github.com/arc-mcp/arc-1) — Enterprise ADT MCP (12 tools, 3,474 tests)
- [Hochfrequenz/aibap.mcp](https://github.com/Hochfrequenz/aibap.mcp) — 69-tool ABAP MCP (Go)
- [mario-andreschak/mcp-sap-gui](https://github.com/mario-andreschak/mcp-sap-gui) — Primary SAP GUI MCP
- [kts982/mcp-sap-gui](https://github.com/kts982/mcp-sap-gui) — Secondary SAP GUI (Python)
- [secondsky/sap-skills](https://github.com/secondsky/sap-skills) — 37 Claude Code SAP plugins
- [shrek-abaper/sap-engineering-skill](https://github.com/shrek-abaper/sap-engineering-skill) — 4 skills: ADT CLI, review, transport gate, RAP gen
- [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) — Caveman mode (integrated as default output)
- [abaplint/abaplint](https://github.com/abaplint/abaplint) — ABAP linter (60+ rules configured)

---

## Contributing

PRs and issues welcome. See [SKILL.md](SKILL.md) for the full dispatch table and
78-skill reference. MIT licensed — use freely.

---

## Tags

**SAP Core:**
`#sap` `#sap-erp` `#sap-s4hana` `#sap-ecc` `#sap-netweaver` `#sap-basis` `#sap-abap`
`#abap` `#abap-cloud` `#abap-steampunk` `#clean-abap` `#abap-oo` `#abap-cds`
`#abap-rap` `#abap-adt` `#abap-development` `#abap-code` `#abap-programming`

**SAP Modules:**
`#sap-mm` `#sap-sd` `#sap-fi` `#sap-co` `#sap-pp` `#sap-qm` `#sap-wm`
`#sap-ewm` `#sap-hcm` `#sap-pm` `#sap-ps` `#sap-bw`

**SAP BTP & Cloud:**
`#sap-btp` `#sap-cloud-platform` `#sap-cloud-foundry` `#sap-kyma`
`#sap-build` `#sap-launchpad` `#sap-workzone` `#sap-ias` `#sap-xsuaa`

**SAP Integration & API:**
`#sap-cpi` `#sap-pi` `#sap-po` `#sap-api-management` `#sap-apim`
`#sap-odata` `#sap-gateway` `#sap-idoc` `#sap-rfc` `#sap-bapi`
`#sap-soap` `#sap-rest` `#sap-event-mesh`

**SAP Fiori & UI:**
`#sap-fiori` `#sap-fiori-elements` `#sapui5` `#openui5` `#sap-fiori-tools`
`#sap-screen-personas` `#sap-build-apps`

**SAP HANA & Data:**
`#sap-hana` `#sap-hana-cloud` `#sap-datasphere` `#sap-sac` `#sap-analytics-cloud`
`#sap-hana-sql` `#sap-hana-sqlscript` `#sap-bw4hana`

**SAP CAP & RAP:**
`#sap-cap` `#cap-cds` `#sap-rap` `#restful-abap` `#sap-business-objects`
**SAP Development Tools:**
`#sap-adt` `#eclipse-adt` `#abapgit` `#abaplint` `#sap-atc` `#sap-sci`
`#sap-code-inspector` `#sap-transport` `#sap-cts` `#sap-charm`
`#sap-solution-manager` `#sap-cloud-alm`
**MCP & AI Agents:**
`#mcp` `#model-context-protocol` `#mcp-server` `#mcp-tool` `#sap-mcp`
`#sap-mcp-server` `#abap-mcp` `#claude-code` `#claude-ai` `#anthropic`
`#ai-agent` `#ai-coding-agent` `#ai-orchestrator` `#llm-agent`
`#sap-ai` `#sap-ai-core` `#sap-genai-hub` `#generative-ai`
**DevOps & Quality:**
`#devops` `#cicd` `#sap-cicd` `#transport-management` `#abap-unit`
`#abap-unit-testing` `#sap-testing` `#sap-automation` `#code-review`
`#security-audit` `#sap-security` `#sap-authorization`
**IDE & Platform:**
`#vscode` `#vscode-extension` `#sap-business-application-studio` `#sap-bas`
`#low-code` `#no-code` `#developer-tools` `#developer-productivity`
**Other:**
`#self-learning` `#routing-engine` `#orchestrator` `#sap-automation-tool`
`#sap-skills` `#claude-skills` `#sap-workflow` `#sap-orchestration`
