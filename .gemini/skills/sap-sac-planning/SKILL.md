---
name: sap-sac-planning
description: SAP Analytics Cloud Planning — planning models, version management, allocation processes, value driver trees, data actions, calendar tasks, planning sequences, collaboration (discussions, annotations), BPC migration to SAC Planning. Use when building SAC planning applications, creating allocation processes, or migrating from SAP BPC to SAC.
---

# SAP Analytics Cloud Planning

Financial planning and analysis in SAC — models, allocations, data actions, calendars.

## Planning Model

```
Model: Financial Plan
├── Dimensions: Account, CostCenter, Time, Version, Currency
├── Measures: Amount, Quantity, Price
├── Versions: Budget, Forecast, Actual
└── Security: Read/Write by dimension member
```

## Version Management

| Version | Purpose | Lock/Unlock |
|---|---|---|
| Actual | Actual data (read-only) | Always locked |
| Budget | Annual budget plan | Locked after approval |
| Forecast | Rolling forecast | Open for contributors |
| Plan | What-if scenario | Temporary, user-specific |

## Allocation Process

```javascript
// Distribute cost center costs
var allocation = PlanningModel_1.createAllocationStep({
  source: {
    dimension: "CostCenter", member: "CC_ADMIN",
    measure: "Amount",
    filter: [["Account", "=", "SALARIES"]]
  },
  target: {
    dimension: "CostCenter",
    members: ["CC_SALES", "CC_MARKETING", "CC_RD"],
    driver: { measure: "Headcount", includeZero: false }
  },
  method: "COPY",
  amount: 100  // percent
});
```

## Value Driver Trees

```
Revenue
├── Price × Quantity
│   ├── Price ──→ Pricing Strategy (manual input)
│   └── Quantity ──→ Market Size × Market Share
└── [Sensitivity: Price +10% → Revenue +8%]
```

## Data Actions

```
Data Action: Copy Plan → Forecast
  1. Source: Version = "Plan", Time = "2026"
  2. Target: Version = "Forecast", Time = "2026"
  3. Override: Account = "SALARIES" → multiply by 1.05 (5% raise)
```

## Calendar Tasks

SAC Calendar for planning process orchestration:
```
Q4 Planning Cycle:
  Task 1 (Oct 1-7): Cost Center Managers → Input headcount
  Task 2 (Oct 8-14): Finance → Review submissions
  Task 3 (Oct 15-21): Controller → Finalize and lock
```

## BPC Migration

| BPC Concept | SAC Equivalent |
|---|---|
| BPC Environment | SAC Planning Model |
| Input Schedules | SAC Stories + tables |
| BPC Script Logic | SAC Data Actions |
| BPC Work Status | SAC Calendar Tasks |
| EPM Add-in | SAC Excel Add-in |

## Gotchas
- Planning model dimensions max: 20 per model
- Data action steps: max 100 per action
- Version "Actual" is always read-only
- Allocation driver measure must be in same model
