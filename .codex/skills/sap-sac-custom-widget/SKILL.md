---
name: sap-sac-custom-widget
description: SAP Analytics Cloud Custom Widgets — web component development, widget manifest, data binding, styling, deployment to SAC tenant, custom analytics extensions. Use when building custom SAC widgets, extending SAC analytic applications, or integrating external charts and visualizations into SAC.
---

# SAP Analytics Cloud Custom Widgets

Extend SAC with custom web components for advanced visualization.

## Widget Structure

```
my-widget/
├── widget.json              — Manifest
├── main.js                   — Widget logic
├── styling.css               — CSS
└── assets/                   — Images, fonts
```

## Widget Manifest

```json
{
  "name": "my-forecast-chart",
  "description": "Custom forecast visualization",
  "version": "1.0.0",
  "vendor": "SAP",
  "webComponent": {
    "tag": "my-forecast-chart",
    "url": "https://my-cdn.com/widgets/forecast/main.js",
    "properties": {
      "data": { "type": "ResultSet" },
      "chartType": { "type": "string", "default": "line" }
    },
    "events": { "onDataPointClick": { "description": "Data point clicked" } }
  }
}
```

## Widget Implementation

```javascript
class ForecastChart extends HTMLElement {
  constructor() {
    super();
    this._data = null;
  }

  connectedCallback() {
    this.innerHTML = '<canvas id="chart" width="400" height="200"></canvas>';
    this._render();
  }

  set data(value) {
    this._data = value;
    this._render();
  }

  _render() {
    if (!this._data) return;
    var ctx = this.querySelector('#chart').getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: this._data.map(r => r.period),
        datasets: [{ label: 'Actual', data: this._data.map(r => r.actual) },
                   { label: 'Forecast', data: this._data.map(r => r.forecast) }]
      }
    });
  }
}
customElements.define('my-forecast-chart', ForecastChart);
```

## Data Binding in SAC

```javascript
// In SAC Analytics Designer
var widget = CustomWidget_1;
widget.setDataBinding({
  dataSource: "SalesData",
  measures: ["Revenue"],
  dimensions: [["Month"]]
});

// Widget receives ResultSet JSON:
// [{period: "2026.01", actual: 1000, forecast: 1100}, ...]
```

## Deployment

1. Host widget files on public CDN or SAC widget repository
2. Import widget.json in SAC → System → Custom Widgets
3. Widget appears in SAC Designer widget palette
4. Drag and drop, bind data

## Gotchas
- Widget URL must be HTTPS (SAC CSP requires it)
- CORS headers required on widget hosting server (Access-Control-Allow-Origin: *)
- Widget cannot call SAC internal APIs directly
- Custom widget max size: 2MB per widget
