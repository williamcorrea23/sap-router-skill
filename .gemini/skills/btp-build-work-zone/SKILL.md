---
name: btp-build-work-zone
description: SAP Build Work Zone (advanced edition) — workspace configuration, content federation, UI integration cards, custom cards, workspace templates, SAP Mobile Start integration, widget catalog, Knowledge Graph, role-based homepage. Use when configuring SAP Build Work Zone, federating SAP content, or building workspace templates.
---

# SAP Build Work Zone (Advanced Edition)

Central entry point for SAP business applications — unified shell for Fiori, CAP, custom UIs, and external content.

## Architecture

```
SAP Build Work Zone
├── Workspaces (collaborative spaces)
├── Home Page (personalized dashboard)
├── Applications (Fiori, CAP, URL, custom)
├── UI Integration Cards (widgets)
├── Knowledge Graph (cross-app search)
└── SAP Mobile Start (mobile companion)
```

## Content Federation

### Federate SAP S/4HANA Fiori Apps

1. Admin Console → Content Provider → "SAP S/4HANA"
2. BTP Destination with PrincipalPropagation to S/4 backend
3. Content → Automatic discovery of Fiori catalogs + groups
4. Assign to roles

### Federate CAP Apps

1. Content provider → type "SAP BTP"
2. Destination to your CAP app URL
3. Fiori Launchpad plugin manifest in CAP app's webapp

## UI Integration Cards

```json
{
  "sap.app": { "id": "my.card", "type": "card" },
  "sap.card": {
    "type": "List",
    "header": { "title": "Open POs", "icon": { "src": "sap-icon://purchase-order" } },
    "content": {
      "data": {
        "request": { "url": "{{destinations.s4}}/sap/opu/odata/sap/Z_PO_SRV/PO_HEADER?$top=5" }
      },
      "item": {
        "title": "{PurchaseOrder}",
        "description": "{Supplier}",
        "info": { "value": "{NetAmount}" }
      }
    }
  }
}
```

## Workspace Templates

Pre-configured workspace layouts for common scenarios:
- Project Workspace: tasks + documents + team
- Department Workspace: KPIs + apps + news
- Process Workspace: workflow steps + approvals

## SAP Mobile Start

Work Zone content automatically available in SAP Mobile Start:
- Same Fiori tiles and cards
- Push notifications via SAP Notification service
- Offline-capable for approved cards

## Gotchas

- **Content manager role required**: SAP_APP_FND_LAUNCHPAD_CONTENT_MANAGER
- **Federated content cache**: up to 5 min delay after invalidation
- **Card data sources**: must have CORS configured for cross-origin requests
- **Workspace member limit**: 5000 members per workspace
- **Card refresh**: UI integration cards refresh on user interaction, not real-time
