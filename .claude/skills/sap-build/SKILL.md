---
name: sap-build
description: >
  SAP Build — low-code/no-code platform covering SAP Build Apps (app development),
  SAP Build Process Automation (workflows, decisions, approvals, RPA), and
  SAP Build Work Zone integration. Use when building low-code apps, creating
  automated workflows, or designing approval processes on SAP BTP.
trigger:
  keywords:
    - sap build apps
    - sap build process automation
    - low-code app sap
    - approval workflow btp
    - decision table sap build
    - rpa automation sap
    - citizen developer sap
    - build lobby
  intent: "Build low-code apps or automated workflows using SAP Build"
---

# SAP Build

SAP Build platform — low-code apps, process automation, and workflow design on SAP BTP.

## Three Products

- **SAP Build Apps**: drag-and-drop app builder → mobile/web apps from templates
- **SAP Build Process Automation**: workflows, decisions, approvals, RPA bots
- **SAP Build Work Zone**: enterprise portal (see `sap-btp-launchpad` skill for comparison)

## Prerequisites

- SAP BTP subaccount with **Build Apps** and/or **Process Automation** entitlements
- BTP Cockpit admin access to assign Build roles
- For S/4HANA integration: destination configured with `PrincipalPropagation`
- For RPA: SAP Build Process Automation desktop agent installed on target machine
- For Build Apps mobile: SAP Mobile Services entitlement (offline sync)

## Steps — SAP Build Process Automation

### 1. Create a Process

1. BTP Cockpit → **SAP Build Process Automation** → open
2. **Build Lobby** → **Create** → **Process**
3. Name it, add description, select environment

### 2. Define Trigger

```
Trigger types:
  - API call       → POST to /v1/process/instances/{processId}
  - Form submission → user fills a form
  - Event          → S/4HANA business event (e.g., PR created)
  - Schedule       → time-based (cron)
```

### 3. Add Approval Step

```yaml
# Process flow YAML (conceptual — configured in visual editor)
steps:
  - name: Manager Approval
    type: approval
    approvers: [ "${PR.Manager}" ]
    deadline: 5d

  - name: Create Purchase Order
    type: automation
    api: create_po  # calls S/4HANA via destination

  - name: Notify Requester
    type: notification
    channel: email
    template: po_created
```

### 4. Configure API Automation Step

```json
{
  "name": "Create PO in S/4HANA",
  "type": "API",
  "endpoint": "{{destination.S4HANA}}/sap/opu/odata/sap/Z_PO_SRV/PurchaseOrder",
  "method": "POST",
  "authentication": "PrincipalPropagation",
  "body": {
    "Supplier": "${formData.vendor}",
    "Amount": "${formData.amount}"
  }
}
```

### 5. Add Decision Table (Business Rules)

```
| Amount     | Department | Action            |
|------------|------------|-------------------|
| <= 1000    | Any        | Auto-approve      |
| 1001-5000  | Sales      | Manager approval  |
| 1001-5000  | R&D        | Director approval |
| > 5000     | Any        | VP approval       |
```

Configure in: Process → **Decisions** → **Decision Table** → add conditions and actions.

### 6. Deploy and Test

1. **Build Lobby** → select process → **Deploy** to test environment
2. Trigger via API or test form
3. Monitor: **Monitor** tab → **Process Instances** → check status, timing, errors
4. Promote to production via **Transport** (CTMS integration)

## Steps — SAP Build Apps

### 1. Create App from Template

1. **Build Lobby** → **Create** → **Build an Application**
2. Choose template: Approval Dashboard / Inspection App / Time Tracking / Blank
3. Drag-drop UI components, bind to data sources

### 2. Connect Data Source (CDS View / OData)

```
Data tab → Add Data Source → OData Service
  URL: {{destination.S4HANA}}/sap/opu/odata/sap/Z_C_PRODUCT_LIST_CDS/
  Auth: PrincipalPropagation
```

Query directly in app logic:
```sql
SELECT Material, Description, Plant
FROM Z_C_PRODUCT_LIST
WHERE Plant = :user_plant
```

### 3. Deploy App

1. **Build** → **Deploy** → select BTP space
2. App deployed to HTML5 Application Repository
3. Expose via Launchpad Service (see `sap-btp-launchpad` skill)

## Governance

- **Build Lobby**: central dashboard for all Build projects
- **Role-based access**: Citizen Developer vs Professional Developer roles
- **Transport**: Build projects transported via CTMS (Cloud Transport Management)
- **Lifecycle**: Draft → Test → Production stages
- **Audit**: all approvals and process instances logged for compliance

## Pitfalls

| # | Pitfall | Cause | Solution |
|---|---------|-------|----------|
| 1 | Process instance stuck in "In Progress" | Approval deadline not set or approver inactive | Set deadline (e.g., `5d`); configure escalation rule to auto-approve/reject |
| 2 | API automation step fails with 401 | Destination auth not `PrincipalPropagation` | Edit destination in BTP Cockpit → set `Authentication=PrincipalPropagation`; add `scope` matching XSUAA |
| 3 | Decision table not triggering correct action | Row order matters — first match wins | Reorder rows: most specific conditions first (e.g., `> 5000` before `<= 1000`) |
| 4 | Build Apps offline sync not working | SAP Mobile Services not configured | Add Mobile Services entitlement; enable offline in app settings → configure sync interval |
| 5 | Process timeout after 30 days | Single process instance max lifetime is 30 days | Split long-running processes into chained subprocesses; use event-based handoff |
| 6 | Form submission exceeds limits | Max 50 fields per form | Split into multi-step form; or use Fiori app for complex data capture |
| 7 | Transport to production fails | CTMS not configured or version mismatch | Configure CTMS in BTP Cockpit → verify Build project version matches target environment |
| 8 | RPA bot fails on unattended machine | Desktop agent not running or screen locked | Ensure agent runs as service; configure auto-login or headless execution |

## Verification

```bash
# Process Automation — verify process deployed
# BTP Cockpit → SAP Build Process Automation → Monitor → Process Definitions
# Your process should show status "Deployed"

# Trigger process via API and check instance
curl -X POST \
  "https://<spa-tenant>.processautomation.cloud.sap/v1/process/instances/{processId}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"formData": {"vendor": "V001", "amount": "3500"}}'

# Check instance status
# Monitor → Process Instances → filter by creation date → verify "Completed"

# Build Apps — verify deployment
# Build Lobby → My Projects → app status = "Deployed"
# App accessible via URL from HTML5 Application Repository
```

Confirm:
- Process triggers correctly (API, form, or event)
- Approval notifications sent to correct approvers
- Decision table routes to correct action
- API automation step returns success (200)
- Process completes end-to-end in Monitor tab
