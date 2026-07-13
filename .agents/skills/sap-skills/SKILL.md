---
name: sap-skills
description: General SAP skills repository reference (secondsky/sap-skills). Use for cross-module SAP capability lookup and reference patterns.
trigger:
  keywords: [sap skills, capability lookup, which module, which tcode, which bapi, cross-module, module map, sap reference, business capability]
  intent: Finding which SAP module, transaction, or BAPI covers a business capability and routing the question to the right module map, router action, or consultant agent
prerequisites:
  - Repo module maps present in references/module_maps/ (15 files, MM through BW)
  - references/data/ populated (sap-notes.yaml, symptom-index.yaml, tcodes.yaml)
  - Python available for scripts/rag_ingest.py, scripts/sap_router.py, scripts/fallback_engine.py
---

# SAP Skills — Cross-Module Capability Lookup

Answers "which module / tcode / BAPI does X?" using local reference data, the routing engine, and module consultant agents. Lookup flow: **RAG search → module map → router map → consultant agent**.

## 1. RAG Search (first stop)

TF-IDF index built from `references/data/` (SAP notes, symptom index, tcodes YAML) plus `references/module_maps/`.

```bash
# Build/rebuild the local index (run once, or after editing references/)
python scripts/rag_ingest.py ingest

# Search for a capability, symptom, note, or tcode
python scripts/rag_ingest.py search --query "goods receipt purchase order" --top 3
python scripts/rag_ingest.py search --query "credit memo billing" --top 5
```

## 2. Module Maps (curated per-module reference)

15 files in `references/module_maps/` — open the one matching the domain:

| File | Module |
|---|---|
| `mm_operations.md` | Materials Management |
| `sd_operations.md` | Sales & Distribution |
| `fi_operations.md` | Financial Accounting |
| `co_operations.md` | Controlling |
| `pp_operations.md` | Production Planning |
| `qm_operations.md` | Quality Management |
| `pm_operations.md` | Plant Maintenance |
| `wm_operations.md` / `ewm_operations.md` | Warehouse Mgmt / Extended WM |
| `tm_operations.md` | Transportation Management |
| `tr_operations.md` | Treasury |
| `hcm_onprem_operations.md` / `hcm_sf_operations.md` | HCM on-prem / SuccessFactors |
| `bw_operations.md` | Business Warehouse |
| `basis_operations.md` | Basis / system administration |

## 3. Router Map (action → execution path)

Once the capability maps to an action ID, ask the router how it executes:

```bash
# Route an action through ADT-first / GUI-fallback decision tree
python scripts/sap_router.py route --action MM_CREATE_MATERIAL
python scripts/sap_router.py route --action SD_CREATE_ORDER --functional

# Show GUI tcode / BDC / BAPI alternatives for an action
python scripts/fallback_engine.py map --action MM_CREATE_MATERIAL

# Execute the full 6-tier fallback chain (ADT→RFC→GUI→BDC→Offline→Manual)
python scripts/fallback_engine.py execute --action FI_POST_DOCUMENT --module FI
```

## 4. Core Module → Tcode → BAPI Quick Table

| Module | Core Tcodes | Core BAPIs |
|---|---|---|
| MM | MM01, ME21N, MIGO | BAPI_MATERIAL_SAVEDATA, BAPI_PO_CREATE1, BAPI_GOODSMVT_CREATE |
| SD | VA01, VL01N, VF01 | BAPI_SALESORDER_CREATEFROMDAT2, BAPI_OUTB_DELIVERY_CREATE_SLS, BAPI_BILLINGDOC_CREATEMULTIPLE |
| FI | FB01, FB03, F110 | BAPI_ACC_DOCUMENT_POST, BAPI_ACC_DOCUMENT_REV_POST, BAPI_GL_GETACCOUNTSALDO |
| CO | KS01, KO01, KB21N | BAPI_COSTCENTER_CREATEMULTIPLE, BAPI_INTERNALORDER_CREATE |
| PP | CO01, MD02, CS01 | BAPI_PRODORD_CREATE, BAPI_MATERIAL_BOM_GROUP_CREATE |
| QM | QA01, QM01, QA32 | BAPI_INSPLOT_CREATE, BAPI_QUALNOT_CREATE |
| PM | IW31, IW21, IE01 | BAPI_ALM_ORDER_MAINTAIN, BAPI_EQUI_CREATE |
| HCM | PA30, PA20, PT60 | BAPI_EMPLOYEE_GETDATA, HR_INFOTYPE_OPERATION |
| EWM/WM | /SCWM/MON, LT01 | BAPI_WHSE_TO_CREATE_STOCK (WM) / EWM via /SCWM APIs |
| TR | FF7A, FI12, F110 | BAPI_ACC_DOCUMENT_POST (bank postings), DMEE for formats |
| BW | RSA1, RSPC, RSRT | BAPI_IPAK_START, RSPC_API_CHAIN_START |

## 5. Delegate to Consultant Agents

When the lookup needs domain judgment, spawn the matching agent via the Agent tool:

- Module-specific: `sap-mm-consultant`, `sap-sd-consultant`, `sap-fi-consultant`, `sap-co-consultant`, `sap-pp-consultant`, `sap-qm-consultant`, `sap-pm-consultant`, `sap-hcm-consultant`, `sap-ewm-consultant`, `sap-tm-consultant`, `sap-tr-consultant`, `sap-bw-consultant`
- General / unclear module: `sap-tutor` (classifier) — it redirects to the right specialist and answers cross-module architecture questions

Rule: route general "how does SAP handle X" questions to `sap-tutor`; route "configure/troubleshoot X in module Y" to the module consultant.

## Pitfalls

- **RAG search returns nothing** → Cause: index never built or references/ edited since last build. Solution: run `python scripts/rag_ingest.py ingest`, then retry the search.
- **Action ID unknown to router** → Cause: capability phrased as free text, not a mapped action (36 actions mapped). Solution: run `python scripts/fallback_engine.py map --action <GUESS>` to see the map, or check the module map file for the canonical action name.
- **Wrong module guess for a capability** → Cause: overlapping terms (e.g., "invoice" exists in MM, SD, and FI). Solution: disambiguate by document direction — inbound/vendor = MM/FI-AP (MIRO/FB60), outbound/customer = SD/FI-AR (VF01/FB70) — then confirm in the module map.
- **BAPI exists but fails in cloud/S4** → Cause: classic BAPI not released for ABAP Cloud. Solution: check released APIs first (see abap-cloud skill); fall back to OData/RAP equivalents.
- **`--module` passed to `sap_router.py route`** → Cause: route subcommand has no `--module` flag. Solution: module context goes to `fallback_engine.py execute --module <X>`; the router infers module from the action prefix (MM_, SD_, FI_...).

## Verification

```bash
# Index built and searchable
python scripts/rag_ingest.py search --query "material master" --top 3
# Expect: hits from mm_operations.md and/or tcodes.yaml

# Router resolves a known action
python scripts/sap_router.py route --action MM_CREATE_MATERIAL
# Expect: route decision (arc-1 ADT primary or GUI fallback)

# Fallback map lists tcode/BDC/BAPI alternatives
python scripts/fallback_engine.py map --action MM_CREATE_MATERIAL
```

## Related

- **sap-router-skill** — master orchestrator; this skill feeds its routing decisions
- **run-sap-router-skill** — smoke-testing the CLI scripts used here
- **abap-code-patterns / sap-bapi-integration** — implementing the BAPI once identified
- **abap-cloud** — released-API check before using a classic BAPI in cloud context
- `references/module_maps/*.md`, `references/data/{sap-notes,symptom-index,tcodes}.yaml` — the underlying data
