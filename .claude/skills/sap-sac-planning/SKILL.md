---
name: sap-sac-planning
description: >-
  SAC Planning — models, versions, allocations, data actions, value driver
  trees, calendar tasks, predictive forecasting, BPC migration. Use when
  building SAC planning apps, creating allocations, or migrating from BPC.
trigger:
  keywords:
    - SAC planning
    - planning model
    - allocation
    - data action
    - value driver tree
    - BPC migration
    - SAC calendar
    - predictive forecast
  file_patterns:
    - "*planning*model*"
---

# SAP Analytics Cloud Planning

SAC Planning = **Model** (structure) → **Process** (actions) → **Governance**
(versions, calendars). Each layer builds on the previous.

## Prerequisites

- SAC tenant with Planning license (not BI-only)
- Model Builder role or `planning_model.create` permission
- Source data: BW/4HANA, S/4HANA, or flat-file upload
- BPC migration: access to BPC 10.x/11.x (NW or MS) environment

## 1. Planning Model

```
Model: Financial_Plan
├── Dimensions (max 20): Account, CostCenter, Time, Version, Currency
├── Measures: Amount, Quantity, Price, Calculated
├── Versions: Actual (RO), Budget, Forecast, Plan (what-if)
└── Security: R/W per dimension member
```

```bash
curl -X POST "https://$SAC_TENANT/api/v1/planningmodels" \
  -H "Authorization: Bearer $SAC_TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"Financial_Plan","dimensions":["Account","CostCenter","Time","Version","Currency"],"defaultCurrency":"USD"}'
```

## 2. Version Management

| Version | Purpose | Behavior |
|---|---|---|
| Actual | Historical data | Read-only, loaded from source |
| Budget | Annual plan | Locked after approval |
| Forecast | Rolling forecast | Open to contributors |
| Plan | What-if scenario | Temporary, user-scoped |

```bash
curl -X POST "https://$SAC_TENANT/api/v1/versions" \
  -H "Authorization: Bearer $SAC_TOKEN" \
  -d '{"model":"Financial_Plan","source":"Actual","target":"Budget_2026","copyData":true}'
```

## 3. Allocation Process

Distributes costs from source to targets using a driver measure.

```javascript
// SAC Data Action — Allocation step (Advanced Formula)
var alloc = PlanningModel_1.createAllocationStep({
  source: { dimension:"CostCenter", member:"CC_ADMIN", measure:"Amount",
            filter:[["Account","=","SALARIES"]] },
  target: { dimension:"CostCenter", members:["CC_SALES","CC_MKTG","CC_RD"],
            driver:{ measure:"Headcount", includeZero:false } },
  method:"COPY", amount:100   // COPY | PERCENTAGE | SHARE, % of source
});
alloc.execute();
```

**Key:** Driver measure must be in the same model. Cross-model references
require a calculated measure workaround.

## 4. Data Actions

Multi-step scripts that copy/transform/calculate plan data across versions.

```
Data Action: Copy_Plan_to_Forecast
  Step 1 — Copy:     Plan/2026 → Forecast/2026
  Step 2 — Override:  SALARIES × 1.05 (5% raise)
  Step 3 — Allocate:  Overhead by revenue share
  Step 4 — Publish:   Lock Forecast version
```

```bash
curl -X POST "https://$SAC_TENANT/api/v1/dataactions/Copy_Plan_to_Forecast/execute" \
  -H "Authorization: Bearer $SAC_TOKEN" \
  -d '{"parameters":{"SOURCE_VERSION":"Plan","TARGET_VERSION":"Forecast_2026"}}'
```

## 5. Value Driver Trees (VDT)

Decompose KPIs into adjustable levers for what-if simulation.

```
Revenue
├── Price × Quantity
│   ├── Price ──→ Pricing Strategy (manual input)
│   └── Quantity ──→ Market Size × Market Share
└── [ML: Market Share = 73% influence — top driver]
```

**RAG insight:** SAC augmented analytics auto-detects KPI drivers via ML.
Use "Smart Insights" on VDT nodes to surface hidden correlations before
manual modeling. Build planning models from predictive forecasts to blend
ML + human input.

## 6. Calendar Tasks

Orchestrates planning workflows with task dependencies and lock gates.

```
Q4 Cycle:
  Task 1 (Oct 1–7):   CC Managers → Input headcount & expenses
  Task 2 (Oct 8–14):  Finance → Review & consolidate
  Task 3 (Oct 15–21): Controller → Finalize, allocate, lock
```

```bash
curl -X POST "https://$SAC_TENANT/api/v1/calendar/tasks" \
  -H "Authorization: Bearer $SAC_TOKEN" \
  -d '{"name":"Input_Headcount_Q4","model":"Financial_Plan","assignees":["cc_sales_mgr"],"startDate":"2026-10-01","endDate":"2026-10-07","taskType":"DATA_ENTRY"}'
```

## 7. BPC → SAC Migration

| BPC Concept | SAC Equivalent | Notes |
|---|---|---|
| Environment | Planning Model | One model per BPC app |
| Input Schedules | Stories + Tables | Rebuild as grid widgets |
| Script Logic | Data Actions | Rewrite in Advanced Formula |
| Work Status | Calendar Tasks | Map locks to task gates |
| EPM Add-in | SAC Excel Add-in | Re-link to SAC model |
| Dimensions | Dimensions | Max 20 (BPC allowed more) |

**Steps:** Export BPC metadata → Create SAC model → Migrate master data →
Rebuild script logic as Data Actions (30–40% rewrite) → Recreate schedules
as Stories → Map work status → Calendar → Validate row-by-row (delta < 0.01%).

## 8. Predictive Forecasting

```bash
curl -X POST "https://$SAC_TENANT/api/v1/predictive/forecasts" \
  -H "Authorization: Bearer $SAC_TOKEN" \
  -d '{"model":"Financial_Plan","target":"Revenue","horizon":12,"version":"Forecast_2026","explanatoryVariables":["Price","Quantity","MarketShare"]}'
```

## Pitfalls

- **20 dimensions max** — BPC models with more need consolidation
- **100 Data Action steps max** — split complex chains into sequential actions
- **Actual is read-only** — copy to planning version before writing
- **Allocation driver scope** — must be same model; cross-model needs workaround
- **Currency conversion** — set up rates table before loading data; retroactive
  triggers full recalc
- **Version proliferation** — each public version costs storage; archive quarterly
- **Calendar ownership** — if assignee leaves, task stalls; set fallback owner
- **BPC `*WHEN`/`*IS`** — don't map 1:1 to SAC Advanced Formula; 30–40% rewrite
- **Large model perf** — > 100M cells degrades rendering; use private versions

## Verification

```bash
# 1. Model structure
curl -s "https://$SAC_TENANT/api/v1/planningmodels/Financial_Plan" \
  -H "Authorization: Bearer $SAC_TOKEN" | jq '.dimensions, .versions'

# 2. Data action status
curl -s "https://$SAC_TENANT/api/v1/dataactions/Copy_Plan_to_Forecast/status" \
  -H "Authorization: Bearer $SAC_TOKEN" | jq '.status, .lastRun, .rowsAffected'

# 3. Allocation check (source zeroed, targets populated)
curl -s "https://$SAC_TENANT/api/v1/dataexport/Financial_Plan" \
  -H "Authorization: Bearer $SAC_TOKEN" \
  -d '{"filter":{"CostCenter":"CC_ADMIN","Account":"SALARIES"}}' | jq '.data'

# 4. Open calendar tasks
curl -s "https://$SAC_TENANT/api/v1/calendar/tasks?status=OPEN" \
  -H "Authorization: Bearer $SAC_TOKEN" | jq '.tasks | length'

# 5. BPC migration — row count delta < 0.01% = pass
```

## Quick Reference

- Max dims: 20 | Max DA steps: 100 | Alloc methods: COPY, PERCENTAGE, SHARE
- Versions: Public (shared), Private (user-scoped)
- API: `https://$SAC_TENANT/api/v1/` | Auth: OAuth 2.0 (Settings → App Integration)
