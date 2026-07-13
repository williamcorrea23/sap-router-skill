---
name: sapui5-framework
description: SAPUI5/OpenUI5 framework development — async module loading, OData V2/V4 binding, i18n, CSP compliance, TypeScript migration, form/table control selection. Use when writing or modernizing SAPUI5 applications.
trigger:
  - user writes or modifies SAPUI5/OpenUI5 controller or view code
  - user asks about UI5 module loading, data binding, or TypeScript setup
  - user encounters CSP errors or deprecated control warnings in UI5
  - user needs to choose between sap.m.Table, sap.ui.table.Table, SmartTable, or MDC
---

# SAPUI5 Framework Development

## Prerequisites

- UI5 runtime ≥ 1.115 (async APIs, CSP enforcement, TS support)
- Node.js ≥ 18 with `@ui5/cli` installed globally: `npm install -g @ui5/cli`
- For TypeScript: `npm install --save-dev @ui5/ts-types-esm typescript`
- Access to a target OData V2 or V4 service (or local mock server)

## 1. Bootstrap an App

```bash
# Create a new UI5 app with TypeScript
npx ui5-app-ts my-app
cd my-app
npm install
```

Verify `manifest.json` contains `"sap.ui5": { "dependencies": { "minUI5Version": "1.120" } }`.

## 2. Async Module Loading (Controller Pattern)

```javascript
sap.ui.define([
  "sap/ui/core/mvc/Controller",
  "sap/ui/model/json/JSONModel",
  "sap/m/MessageToast"
], function (Controller, JSONModel, MessageToast) {
  "use strict";
  return Controller.extend("my.app.controller.Main", {
    onInit: function () {
      this.getView().setModel(new JSONModel({ items: [] }));
    }
  });
});
```

**Never** use `jQuery.sap.require` — it is synchronous and deprecated since 1.58.

## 3. OData Binding

```javascript
// V4 (preferred) — context binding with expand
this.getView().bindElement({
  path: "/Products('ABC123')",
  parameters: { $expand: "to_Text" }
});

// V2 (legacy) — manual read with filter
var oModel = this.getView().getModel();
oModel.read("/Products", {
  filters: [new sap.ui.model.Filter("Material", "EQ", "MAT001")],
  success: function (oData) { /* ... */ }
});
```

## 4. i18n Resource Bundle

```json
// manifest.json — register model
"models": {
  "i18n": {
    "type": "sap.ui.model.resource.ResourceModel",
    "settings": { "bundleName": "my.app.i18n.i18n" }
  }
}
```

```javascript
// Controller usage
var sText = this.getView().getModel("i18n").getResourceBundle().getText("appTitle");
```

## 5. TypeScript Migration

```typescript
import Controller from "sap/ui/core/mvc/Controller";
import Button$PressEvent from "sap/m/Button$PressEvent";

export default class MainController extends Controller {
  onButtonPress(event: Button$PressEvent): void {
    const oButton = event.getSource();
    // type-safe access
  }
}
```

Build with `npx ui5 build --all --config ui5.yaml` then `npx tsc --noEmit` for type checking.

## 6. Choose the Right Table Control

- **sap.m.Table** — simple lists, < 200 rows, mobile-first
- **sap.ui.table.Table** — large datasets, column resize/reorder, desktop
- **sap.ui.comp.smarttable.SmartTable** — Fiori Elements, OData annotation-driven
- **sap.ui.mdc.Table** — metadata-driven, newest API (UI5 ≥ 1.86)

## 7. Form Controls

Use `sap.ui.layout.form.Form` with `ColumnLayout` for all new code.
Avoid `SimpleForm` — it is deprecated and does not support responsive grid.

## 8. CSP Compliance

UI5 ≥ 1.115 enforces CSP by default. Rules:
- No inline `<script>` blocks — all JS goes in controller files
- No `eval()` or `new Function()`
- No inline `on*` event handler attributes in HTML/XML views

## Pitfalls

**Inline scripts rejected by CSP**
- Cause: JavaScript embedded in `<script>` tags inside XML views or index.html
- Solution: Move all logic into controller files loaded via `sap.ui.define`

**OData V4 binding silently fails**
- Cause: Using `bindElementContext` (V2 API) instead of `bindElement` (V4 API)
- Solution: Use `bindElement({ path, parameters })` for V4 models

**TypeScript event types not found**
- Cause: Missing `@ui5/ts-types-esm` package or wrong import path
- Solution: `npm install --save-dev @ui5/ts-types-esm` and import using `$` syntax (`Button$PressEvent`)

**SimpleForm renders incorrectly on desktop**
- Cause: `SimpleForm` is deprecated, lacks responsive column layout
- Solution: Replace with `Form` + `ColumnLayout` — single column on phone, multi on desktop

**`jQuery.sap.require` causes sync load warning**
- Cause: Legacy synchronous module loader
- Solution: Replace with `sap.ui.define` async dependency array

## Verification

```bash
# Type-check TypeScript
npx tsc --noEmit

# Lint with UI5 tooling
npx ui5 lint

# Start dev server and verify app loads
npx ui5 serve --port 8080
# Open http://localhost:8080 — check console for CSP or module errors
```

Confirm:
- [ ] No `jQuery.sap.require` calls remain (`grep -r "jQuery.sap.require" webapp/`)
- [ ] No `SimpleForm` in new views
- [ ] No inline scripts in XML views
- [ ] `npx tsc --noEmit` passes with zero errors
