---
name: sap-build
description: SAP Build — SAP Build Apps (low-code app development), SAP Build Process Automation (workflows, decisions, automations), SAP Build Work Zone integration, citizen developer governance, process automation triggers, API-based automation steps, form building, approval flows. Use when building low-code apps with SAP Build, creating automated workflows, designing approval processes, or empowering citizen developers on SAP BTP.
---

# SAP Build

SAP Build platform — low-code apps, process automation, and workflow design on SAP BTP.

## Three Products

| Product | Use Case | Output |
|---|---|---|
| SAP Build Apps | Low-code app development | Mobile/web apps from templates + drag-drop |
| SAP Build Process Automation | Workflow + decision + RPA | Automated business processes |
| SAP Build Work Zone | Enterprise portal | Unified entry point (covered in btp-build-work-zone) |

## SAP Build Process Automation

### Process Components

```
Process (end-to-end flow)
├── Trigger (API call, form submission, event)
├── Forms (data input by users)
├── Automations (RPA Bots or API calls)
│   ├── API-based (REST/OData)
│   └── UI-based (SAP GUI, web apps)
├── Decisions (business rules / decision tables)
└── Approvals (human tasks)
```

### Decision Table Example

```
| Condition: Amount | Condition: Department | Action: Approval |
|---|---|---|
| <= 1000 | Any | Auto-approve |
| 1001-5000 | Sales | Manager approval |
| 1001-5000 | R&D | Director approval |
| > 5000 | Any | VP approval |
```

### API Automation Step

```json
{
  "automation": {
    "name": "Create PO in S/4HANA",
    "type": "API",
    "endpoint": "{{destination.S4HANA}}/sap/opu/odata/sap/Z_PO_SRV/PurchaseOrder",
    "method": "POST",
    "authentication": "PrincipalPropagation",
    "body": {
      "Supplier": "${formData.vendor}",
      "Amount": "${formData.amount}",
      "Department": "${formData.department}"
    }
  }
}
```

### Process Trigger Example

```yaml
# Trigger: new purchase requisition in S/4HANA
trigger:
  type: event
  source: SAP S/4HANA
  event: sap.s4.beh.purchaserequisition.created

# Process flow
steps:
  - name: Manager Approval
    type: approval
    approvers: [ "${PR.Manager}" ]

  - name: Create Purchase Order
    type: automation
    api: create_po

  - name: Notify Requester
    type: notification
    channel: email
    template: po_created
```

## SAP Build Apps

### App from Template

```
Build Lobby → Create → Build an Application → Choose Template
  Templates:
    - Approval Dashboard (approval inbox + analytics)
    - Inspection App (checklists, photos, offline)
    - Time Tracking (clock in/out, approvals)
```

### Data Integration

```sql
-- Build Apps can query CDS views directly
SELECT Material, Description, Plant
FROM Z_C_PRODUCT_LIST
WHERE Plant = :user_plant
```

## Governance

| Control | Description |
|---|---|
| Build Lobby | Central dashboard for all Build projects |
| Role-based access | Citizen Developer vs Professional Developer roles |
| Transport | Build projects transported via CTMS |
| Lifecycle | Draft → Test → Production stages |
| Audit | All approvals logged for compliance |

## Gotchas

- **Build Apps offline sync**: SAP Mobile Services required for offline capability
- **Process automation timeout**: 30 days max for a single process instance
- **API-based automation**: destination must be configured in BTP subaccount
- **Decision tables**: max 50 rows per table; split complex logic across tables
- **Forms**: max 50 fields per form; complex data capture → use Fiori instead
