---
name: sap-fiori-tools
description: SAP Fiori Tools — Fiori Elements List Report, Object Page, Overview Page configuration, manifest.json settings, annotation-driven UI, custom actions, custom columns, visual filters, flexible column layout, side drawer navigation. Use when configuring Fiori Elements apps, adding custom actions to List Reports, or setting up Fiori application layouts.
trigger:
  keywords: [fiori-elements, list-report, object-page, manifest, annotations, custom-actions, visual-filters, flexible-column, side-drawer, layout]
  intent: >-
    Configure and extend SAP Fiori Elements applications using manifest.json settings, annotations, custom actions, columns, filters, and layout options.
---

# SAP Fiori Tools

Configuring and extending SAP Fiori Elements applications.

## Floorplans Available

| Floorplan | Template ID | Use Case |
|---|---|---|
| List Report + Object Page | FE_LROP | Master-detail, most common |
| Analytical List Page | FE_ALP | Charts + table hybrid |
| Overview Page | FE_OVP | Dashboard cards |
| Worklist | FE_WORKLIST | Task-oriented list |
| Form Entry Object Page | FE_FEOP | Form-centric entry (V4 only) |
| Flexible Programming Model | FE_FPM | Custom page layout (V4 only) |

## manifest.json Configuration

```json
{
  "sap.ui.generic.app": {
    "pages": [{
      "entitySet": "Products",
      "component": { "name": "sap.suite.ui.generic.template.ListReport", "list": true }
    }, {
      "entitySet": "Products",
      "component": { "name": "sap.suite.ui.generic.template.ObjectPage" }
    }]
  }
}
```

## Custom Actions

```json
// manifest.json extension
{
  "sap.ui.generic.app": {
    "pages": [{
      "component": {
        "settings": {
          "tableSettings": {
            "customActions": [{
              "name": "AnalyzeRisks",
              "text": "Analyze Risks",
              "press": "onAnalyzeRisks"
            }]
          }
        }
      }
    }]
  }
}
```

## Custom Controller Extension

```javascript
sap.ui.define(["sap/ui/core/mvc/ControllerExtension"], function(ControllerExtension) {
  return ControllerExtension.extend("my.app.ext.Main", {
    onAnalyzeRisks: function(oEvent) {
      // Custom action logic
    }
  });
});
```

## Layout Types

| Layout | Description |
|---|---|
| FlexibleColumnLayout | 2 or 3 column master-detail |
| BottomNavigation | Mobile-style bottom tabs |
| SideDrawerNavigation | Side panel navigation |
| Tabs | Tab-based page navigation |
| Section | Simple single-page layout |

## Gotchas
- Custom actions only support 8 data fields in create dialog
- Multi-view requires quickVariantSelectionX configuration
- Draft state not maintained for dialog-created objects
- Fiori Elements V2 annotations are XML; V4 annotations are CDS-based
