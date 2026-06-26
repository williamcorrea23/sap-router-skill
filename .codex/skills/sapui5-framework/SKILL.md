---
name: sapui5-framework
description: SAPUI5 Framework — asynchronous module loading (sap.ui.define), ComponentSupport initialization, OData V2/V4 data binding, i18n management, CSP compliance, TypeScript for UI5, form controls (Form vs SimpleForm), table controls (sap.m.Table vs sap.ui.table), SmartTable/MDC patterns. Use when writing SAPUI5 applications, migrating UI5 to TypeScript, or implementing UI5 best practices.
---

# SAPUI5 Framework

Modern SAPUI5 development patterns and best practices.

## Async Module Loading

```javascript
// Modern async define (UI5 >= 1.115)
sap.ui.define([
  "sap/ui/core/mvc/Controller",
  "sap/ui/model/json/JSONModel",
  "sap/m/MessageToast"
], function(Controller, JSONModel, MessageToast) {
  "use strict";
  return Controller.extend("my.app.controller.Main", {
    onInit: function() {
      var oModel = new JSONModel({ data: [] });
      this.getView().setModel(oModel);
    }
  });
});
```

## OData Binding

```javascript
// OData V4 binding (preferred)
this.getView().bindElement({
  path: "/Products('ABC123')",
  parameters: { $expand: "to_Text" }
});

// OData V2 binding (legacy)
oModel.read("/Products", {
  filters: [new sap.ui.model.Filter("Material", "EQ", "MAT001")]
});
```

## i18n Pattern

```javascript
// manifest.json: "i18n": { "bundleUrl": "i18n/i18n.properties" }
// Use in controller:
var sText = this.getView().getModel("i18n").getResourceBundle().getText("myKey");
```

## CSP Compliance

No inline scripts — all JavaScript in separate controller files. UI5 >= 1.115 enforces CSP by default.

## Form Controls

Always use `sap.ui.layout.form.Form` with `ColumnLayout`, never `SimpleForm` (deprecated).

## Table Controls

| Control | When to Use |
|---|---|
| sap.m.Table | Simple lists, < 200 rows |
| sap.ui.table.Table | Large datasets, column resize/reorder |
| sap.ui.comp.smarttable.SmartTable | Fiori Elements, OData annotations |
| sap.ui.mdc.Table | Metadata-driven control (new) |

## TypeScript for UI5

```typescript
// UI5 >= 1.115 TypeScript event handler
import Controller from "sap/ui/core/mvc/Controller";
import Button from "sap/m/Button";
import Button$PressEvent from "sap/m/Button$PressEvent";

export default class MainController extends Controller {
  onButtonPress(event: Button$PressEvent): void {
    const button = event.getSource();
    // ...
  }
}
```

## Gotchas
- sap.ui.define (async) — never use jQuery.sap.require (sync, deprecated)
- CSP blocks eval() and inline event="..." handlers
- OData V4: bindElement not bindElementContext
- SimpleForm → Form + ColumnLayout for new code
