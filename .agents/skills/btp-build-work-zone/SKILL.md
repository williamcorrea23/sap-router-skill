---
name: btp-build-work-zone
description: >
  SAP Build Work Zone (advanced edition) — workspace configuration, content federation,
  UI integration cards, workspace templates, SAP Mobile Start, role-based homepage.
  Use when configuring SAP Build Work Zone, federating SAP content, or building workspace templates.
trigger:
  - "configure SAP Build Work Zone"
  - "federate Fiori apps into Work Zone"
  - "create UI integration card"
  - "set up workspace template"
  - "integrate SAP Mobile Start"
  - "configure role-based homepage"
---

# SAP Build Work Zone (Advanced Edition)

Central entry point for SAP business applications — unified shell for Fiori, CAP, custom UIs, and external content.

## Prerequisites

- SAP BTP subaccount with **SAP Build Work Zone, advanced edition** entitlement
- Admin role assigned: `AuthGroup_SpaceAdmin`
- Content manager role: `SAP_APP_FND_LAUNCHPAD_CONTENT_MANAGER`
- BTP destinations configured to backend systems (S/4HANA, CAP apps, etc.)
- Principal propagation enabled on destinations for federated content

## Steps

### 1. Federate S/4HANA Fiori Apps

1. Open **Work Zone Admin Console** → Content → Content Providers
2. Click **Add Content Provider** → Type: `SAP S/4HANA` or `SAP BTP ABAP`
3. Select the BTP destination pointing to your S/4HANA backend
4. Configure: Destination with `PrincipalPropagation` authentication
5. Click **Fetch Content** → catalogs and groups auto-discovered
6. Navigate to **Content Manager** → assign catalogs/groups to roles

### 2. Federate CAP Applications

1. Content Provider → Type: `SAP BTP`
2. Enter CAP app URL (e.g., `https://my-app.cfapps.us10.hana.ondemand.com`)
3. Ensure CAP app has Fiori launchpad plugin manifest in `app/` directory
4. Fetch content → apps appear in Content Manager

### 3. Create a UI Integration Card

Create a card manifest JSON file:

```json
{
  "sap.app": { "id": "my.card", "type": "card" },
  "sap.card": {
    "type": "List",
    "header": {
      "title": "Open Purchase Orders",
      "icon": { "src": "sap-icon://purchase-order" }
    },
    "content": {
      "data": {
        "request": {
          "url": "{{destinations.s4}}/sap/opu/odata/sap/Z_PO_SRV/PO_HEADER?$top=5"
        }
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

Deploy via:
```bash
# Upload card via Admin Console → UI Integration Cards → Import
# Or deploy via MTA with card resource type
mbt build && cf deploy mta_archives/my-workzone-content.mtar
```

### 4. Configure Workspace Templates

1. Admin Console → **Workspace Templates** → **Create**
2. Select template type:
   - **Project Workspace**: tasks + documents + team
   - **Department Workspace**: KPIs + apps + news
   - **Process Workspace**: workflow steps + approvals
3. Add widgets and apps to the template layout
4. Save and assign to roles for self-service workspace creation

### 5. Enable SAP Mobile Start

1. Admin Console → **Settings** → **SAP Mobile Start**
2. Ensure Work Zone content is published (apps, cards visible in Content Manager)
3. Configure push notifications via SAP Notification service binding
4. Mobile users: install **SAP Mobile Start** app → scan QR code from Work Zone
5. Offline-capable cards require marking them as offline-enabled in card manifest

### 6. Configure Role-Based Homepage

1. Admin Console → **Home Page** → **Edit Layout**
2. Add sections: visualizations, cards, app launcher tiles
3. Assign visibility by **role** (e.g., `Sales_Manager` sees different tiles than `Employee`)
4. Save → users see personalized homepage based on their role assignment

## Pitfalls

| Cause | Solution |
|---|---|
| Federated content not appearing after fetch | Content cache has up to 5 min delay. Wait, then click **Refresh** in Content Manager. Verify destination has `PrincipalPropagation` auth type. |
| CORS error on card data source | Card data sources must have CORS configured. Add `Access-Control-Allow-Origin` header on the backend OData service or use a BTP destination with `HTML5.DynamicDestination=true`. |
| Card shows no data / blank | Check the `{{destinations.<name>}}` placeholder matches a destination configured in Admin Console → Destinations. Verify the OData service path is correct. |
| Workspace member limit exceeded | Max 5000 members per workspace. Split large orgs into multiple workspaces or use role-based membership rules. |
| Cards not refreshing in real-time | UI integration cards refresh on user interaction, not real-time. Configure auto-refresh interval in card manifest (`refreshInterval` in seconds, min 30). |
| Mobile Start content missing | Ensure content is published (not just saved) in Admin Console. Check that the user's role includes the catalog/group assignments. |

## Verification

```bash
# Check content provider status
curl -s https://<workzone-host>/api/v1/contentproviders \
  -H "Authorization: Bearer $TOKEN" | jq '.[].status'

# Verify card endpoint resolves
curl -s "{{destinations.s4}}/sap/opu/odata/sap/Z_PO_SRV/PO_HEADER?\$top=1" \
  -H "Authorization: Bearer $TOKEN" | jq '.d.results[0]'

# Confirm workspace template is active
curl -s https://<workzone-host>/api/v1/workspacetemplates \
  -H "Authorization: Bearer $TOKEN" | jq '.[].status'
```

Checklist:
- [ ] Content providers show status `ACTIVE` in Admin Console
- [ ] Federated Fiori apps appear in Content Manager and are assigned to roles
- [ ] UI Integration Cards render data correctly in preview
- [ ] Workspace template is published and self-service creation works
- [ ] Mobile Start app shows Work Zone homepage after QR scan
- [ ] Role-based homepage shows correct tiles for each test role
