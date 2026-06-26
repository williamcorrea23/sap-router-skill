---
name: btp-job-scheduling
description: SAP BTP Job Scheduling service — cron-based job definitions, REST endpoints, job execution monitoring, retry policies, job logs, SAP S/4HANA integration, application job templates in ABAP Cloud. Use when scheduling recurring BTP tasks, creating cron jobs, or monitoring job executions.
---

# SAP BTP Job Scheduling Service

Cron-based job scheduler on SAP BTP — schedule REST endpoints with retry and monitoring.

## Job Definition

```json
{
  "job": {
    "name": "daily-sync",
    "active": true,
    "action": {
      "url": "https://my-app.cfapps.us10.hana.ondemand.com/sync",
      "method": "POST",
      "headers": { "Authorization": "Bearer {{token}}" }
    },
    "schedules": [{ "cron": "0 6 * * *", "description": "Every day at 06:00 UTC" }],
    "retryPolicy": { "maxRetries": 3, "retryInterval": 300 }
  }
}
```

## Cron Expressions

| Expression | Trigger |
|---|---|
| `0 6 * * *` | Every day 06:00 |
| `*/15 * * * *` | Every 15 minutes |
| `0 0 1 * *` | First day of month |
| `0 8 * * 1-5` | Weekdays at 08:00 |

## REST API

```bash
# Create job
curl -X POST https://jobscheduler.cfapps.<region>.hana.ondemand.com/scheduler/jobs \
  -H "Authorization: Bearer <token>" -d @job.json

# Get executions
curl https://jobscheduler.cfapps.<region>.hana.ondemand.com/scheduler/jobs/daily-sync/runs
```

## ABAP Cloud Application Jobs

ABAP Cloud replaces SM37 with Application Job Templates (ADT-based):
- Template defines: job name, step handler (IF_APJ_DT_EXECUTION_OBJECT), parameters
- Scheduled via Fiori app "Application Jobs" (F1076)

## Gotchas
- Job timeout: 2h maximum per execution
- noOverlap: true prevents concurrent runs
- Cron timezone: UTC only
- Lite plan limited to 10 active jobs
