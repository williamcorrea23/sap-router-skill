---
name: btp-cloud-logging
description: SAP BTP Cloud Logging — OpenSearch-based centralized logging with structured logs, correlation IDs, Kibana dashboards, and retention management.
trigger:
  keywords: [cloud logging, OpenSearch, Kibana, structured logging, correlation ID, observability, log retention, log dashboards, BTP logging]
  intent: Configure SAP BTP Cloud Logging service with structured logs, correlation IDs, and Kibana dashboards
---

# SAP BTP Cloud Logging

Centralized observability on SAP BTP powered by OpenSearch + Kibana dashboards.

## Prerequisites

- CF CLI logged in to target space
- An app deployed on SAP BTP (CAP/Node.js/Python/Java)
- Cloud Logging entitlement assigned to the subaccount (Lite/Standard/Enterprise)

## 1. Create Service Instance and Bind

```bash
cf create-service cloud-logging standard my-logging
cf bind-service my-app my-logging
cf restage my-app
```

Verify the binding appears in `VCAP_SERVICES`:

```bash
cf env my-app | grep -A 20 cloud-logging
```

## 2. Structured Logging (CAP / Node.js)

```javascript
const cds = require('@sap/cds')
const LOG = cds.log('procurement')

LOG.info('Order created', { orderId: 'ORD123', userId: 'USER1', duration: 245 })
LOG.error('BAPI call failed', new Error('Connection timeout'))
```

Log entries appear in OpenSearch with fields: `correlation_id`, `component`, `level`, `message`, `custom_fields`.

## 3. OpenTelemetry Tracing

```javascript
const { trace } = require('@opentelemetry/api')
const tracer = trace.getTracer('procurement-service')

async function processOrder(orderId) {
  const span = tracer.startSpan('processOrder')
  span.setAttribute('order.id', orderId)
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

## 4. Python Integration

```python
import logging
from sap_cloud_logging import CloudLoggingHandler

logger = logging.getLogger('my-btp-app')
handler = CloudLoggingHandler(
    component='procurement',
    correlation_id=request.headers.get('X-Correlation-ID')
)
logger.addHandler(handler)
logger.info('Processing batch', extra={'batch_size': 1000})
```

## 5. Kibana Query Examples

```
# Errors for a specific order
component:"procurement" AND level:"error" AND custom_fields.orderId:"ORD123"

# Slow requests over 5 seconds
response_time:>5000

# All activity by user in last 24h
custom_fields.userId:"USER1" AND @timestamp:>now-24h
```

## 6. Retention Plans

- **Lite** — 7 days, 500 MB/day
- **Standard** — 14 days, 10 GB/day
- **Enterprise** — 30 days, 100 GB/day

## Pitfalls

- **Logs not appearing immediately**
  - Cause: Ingestion delay of up to 2 minutes is expected.
  - Solution: Wait and refresh Kibana. Do not assume logging is broken.

- **Free tier logs silently dropped**
  - Cause: Lite plan has a 500 MB/day hard cap; exceeding it drops logs without error.
  - Solution: Upgrade to Standard plan or reduce log volume via level filters.

- **Correlation ID missing across services**
  - Cause: `X-Correlation-ID` header is not propagated between service calls.
  - Solution: Forward the header in every HTTP call; use CAP middleware or OTel context propagation.

- **Inconsistent component names**
  - Cause: Different instances log under different component names, making Kibana filters unreliable.
  - Solution: Standardize component naming (e.g., `procurement`, `fulfillment`) across all instances.

- **Logs are immutable**
  - Cause: OpenSearch indexes are append-only after ingestion.
  - Solution: Cannot modify or delete — design log content carefully before emitting.

## Verification

```bash
# Confirm service instance is created
cf services | grep my-logging

# Confirm binding exists
cf services | grep my-app

# Check app logs are flowing (from app side)
cf logs my-app --recent | grep "procurement"

# Open Kibana dashboard from BTP Cockpit:
# Subaccount → Instances → my-logging → Open Dashboard
# Run: component:"procurement" AND level:"info"
```
