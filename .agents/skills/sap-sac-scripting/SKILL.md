---
name: sap-sac-scripting
description: SAP Analytics Cloud scripting — scripting API, custom widgets, data analyzer scripts, chart scripting, planning scripts, button scripts, application design, custom calculations. Use when building SAC custom widgets, adding scripting to SAC stories, or implementing custom analytics logic in SAC.
trigger:
  keywords: [scripting, SAC, analytics cloud, custom widgets, data analyzer, chart scripting, planning scripts, application design, custom calculations]
  intent: >-
    Use when building SAC custom widgets, adding scripting to SAC stories, or implementing custom analytics logic in SAC.
---

# SAP Analytics Cloud Scripting

Custom scripting for SAP Analytics Cloud stories and analytic applications.

## Scripting API Overview

SAC Scripting uses JavaScript-like syntax in SAC Designer.

## Basic Navigation

```javascript
// Navigate between pages
Dashboard_1.getPage("Page1").setVisible(false);
Dashboard_1.getPage("Page2").setVisible(true);

// Set filter value programmatically
InputField_1.setValue("2026.Q2");

// Get selected member from table
var selected = Table_1.getSelectedMembers();
var memberId = selected[0].id;
```

## Chart Manipulation

```javascript
// Toggle chart type
Chart_1.setChartType("bar");

// Set chart title
Chart_1.setTitle("Revenue by Region");

// Change dimension
Chart_1.setDimension("Region");
Chart_1.setMeasure("Revenue");
```

## Data Analyzer

```javascript
// Apply filter from dropdown
var selectedMonth = DropdownMonth.getSelectedKey();
DataSource_1.setFilter("Month", selectedMonth);
DataSource_1.reload();

// Get data cell value
var revenue = DataSource_1.getData({
  measures: ["Revenue"],
  filters: [["Month", "=", "2026.06"]]
}).value;
```

## Button Actions

```javascript
// Button triggers planning function
Button_1.onPress = function() {
  var plan = PlanningModel_1;
  plan.createAllocationStep({
    source: { dimension: "CostCenter", member: "CC000" },
    target: { dimension: "CostCenter", member: "CC001" },
    driver: { measure: "Headcount", percentage: 30 }
  });
  plan.execute();
};
```

## Custom Widgets

```javascript
// Custom widget via Web Component
customwidgets.define("my-forecast", {
  template: "<div><canvas id='chart'></canvas></div>",
  onUpdate: function(data) {
    var ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, { type: 'line', data: { labels: data.labels,
      datasets: [{ label: 'Forecast', data: data.values }] } });
  }
});
```

## Application Design

SAC Analytic Applications allow full-page custom logic — scripting, custom widgets, and data binding. Deploy via SAC → Transport to BTP.

## Gotchas
- No debugging tools in SAC — use console.log and browser dev tools
- Scripts are synchronous — async operations need callback pattern
- Maximum script execution time: 30 seconds
- Custom widgets loaded from external URL — requires CSP whitelist
