---
name: btp-cloud-logging
description: SAP BTP Cloud Logging service — OpenTelemetry integration, structured logging with SAP Cloud Logging (OpenSearch), log correlation IDs, Kibana dashboards, log retention policies, service instance creation, binding to applications, log levels configuration. Use when configuring application logging on SAP BTP, troubleshooting production issues, or setting up observability pipelines.
---

# SAP BTP Cloud Logging

Centralized observability on SAP BTP based on OpenSearch (Elasticsearch-compatible) + Kibana dashboards.

## Service Instance

```bash
cf create-service cloud-logging standard my-logging
cf bind-service my-app my-logging
cf restage my-app
```

## Structured Logging (CAP / Node.js)

```javascript
const cds = require('@sap/cds')
const LOG = cds.log('procurement')

// Standard levels
LOG.debug('Query parameters', { params: req.query })
LOG.info('Order created', { orderId: 'ORD123', userId: 'USER1', duration: 245 })
LOG.warn('Slow query detected', { query: sql, elapsed: 5200 })
LOG.error('BAPI call failed', new Error('Connection timeout'))

// Log entry appears in OpenSearch as:
// {
//   "correlation_id": "abc-123",
//   "component": "procurement",
//   "level": "info",
//   "message": "Order created",
//   "custom_fields": { "orderId": "ORD123", "userId": "USER1", "duration": 245 }
// }
```

## OpenTelemetry Integration

```javascript
const { trace } = require('@opentelemetry/api')
const tracer = trace.getTracer('procurement-service')

async function processOrder(orderId) {
  const span = tracer.startSpan('processOrder')
  span.setAttribute('order.id', orderId)
  span.setAttribute('order.type', 'purchase')

  try {
    await callBapi(orderId)
    span.setStatus({ code: trace.SpanStatusCode.OK })
  } catch (e) {
    span.setStatus({ code: trace.SpanStatusCode.ERROR, message: e.message })
    span.recordException(e)
  } finally {
    span.end()
  }
}
```

## Kibana Query Examples

```
# Find all errors for a specific order
component:"procurement" AND level:"error" AND custom_fields.orderId:"ORD123"

# Slow requests over 5 seconds
response_time:>5000

# All activity by user in last 24h
custom_fields.userId:"USER1" AND @timestamp:>now-24h
```

## Log Retention

| Plan | Retention | Daily Volume |
|---|---|---|
| Lite | 7 days | 500 MB |
| Standard | 14 days | 10 GB |
| Enterprise | 30 days | 100 GB |

## Python Integration

```python
import logging
from sap_cloud_logging import CloudLoggingHandler

logger = logging.getLogger('my-btp-app')
handler = CloudLoggingHandler(
    component='procurement',
    correlation_id=request.headers.get('X-Correlation-ID')
)
logger.addHandler(handler)
logger.info('Processing batch job', extra={'batch_size': 1000})
```

## Gotchas

- **Log ingestion delay**: up to 2 minutes — not real-time
- **Logs are immutable**: cannot modify or delete after ingestion
- **Free tier 500MB/day**: exceeded → logs dropped (no error to app)
- **Component name**: use consistent naming across all app instances
- **Correlation ID propagation**: must pass X-Correlation-ID header between services
