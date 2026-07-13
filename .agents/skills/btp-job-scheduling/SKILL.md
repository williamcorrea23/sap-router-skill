---
name: btp-job-scheduling
description: >
  SAP BTP Job Scheduling service — cron-based job definitions, REST API, job execution
  monitoring, retry policies, job logs, ABAP Cloud application jobs. Use when scheduling
  recurring BTP tasks, creating cron jobs, or monitoring job executions.
trigger:
  - "schedule recurring BTP job"
  - "create cron job for REST endpoint"
  - "monitor job execution"
  - "configure job retry policy"
  - "create ABAP Cloud application job"
  - "troubleshoot job scheduler"
---

# SAP BTP Job Scheduling Service

Cron-based job scheduler on SAP BTP — schedule REST endpoints with retry, monitoring, and logging.

## Prerequisites

- SAP BTP subaccount with **Job Scheduling service** entitlement
- Service instance created and bound to your application
- Target REST endpoint accessible from BTP (Cloud Foundry app or external URL)
- XSUAA service for authentication token generation
- For ABAP Cloud: ADT (ABAP Development Tools) and `IF_APJ_DT_EXECUTION_OBJECT` interface

## Cron Reference

| Expression | Trigger |
|---|---|
| `0 6 * * *` | Every day at 06:00 UTC |
| `*/15 * * * *` | Every 15 minutes |
| `0 0 1 * *` | First day of month at 00:00 |
| `0 8 * * 1-5` | Weekdays at 08:00 UTC |
| `0 */2 * * *` | Every 2 hours |

## Steps

### 1. Create a Job Definition

Create a JSON file `job.json`:

```json
{
  "job": {
    "name": "daily-sync",
    "description": "Sync orders from S/4HANA to BTP",
    "active": true,
    "httpMethod": "POST",
    "url": "https://my-app.cfapps.us10.hana.ondemand.com/sync",
    "noOverlap": true,
    "retryPolicy": {
      "maxRetries": 3,
      "retryInterval": 300,
      "retryStrategy": "fixed"
    },
    "schedules": [
      {
        "cron": "0 6 * * *",
        "description": "Every day at 06:00 UTC",
        "timezone": "UTC"
      }
    ]
  }
}
```

### 2. Register the Job via REST API

```bash
# Get service credentials from BTP
cf service-key job-scheduler-dev job-scheduler-key

# Extract scheduler URL and credentials, then create job
curl -X POST "https://$SCHEDULER_URL/scheduler/jobs" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d @job.json | jq .

# Verify job was created
curl -s "https://$SCHEDULER_URL/scheduler/jobs/daily-sync" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq .
```

### 3. Trigger a Manual Run

```bash
# Start job immediately (bypass schedule)
curl -X POST "https://$SCHEDULER_URL/scheduler/jobs/daily-sync/schedules" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type": "immediate"}' | jq .

# Check execution runs
curl -s "https://$SCHEDULER_URL/scheduler/jobs/daily-sync/runs" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.runs[] | {status, startTime, endTime}'
```

### 4. Monitor Job Executions

```bash
# List recent runs with status
curl -s "https://$SCHEDULER_URL/scheduler/jobs/daily-sync/runs?\$top=10" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  | jq '.runs[] | {id, status, start: .startTime, end: .endTime, exitCode}'

# Get detailed logs for a specific run
curl -s "https://$SCHEDULER_URL/scheduler/jobs/daily-sync/runs/$RUN_ID/logs" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.logs[]'
```

### 5. Update or Delete a Job

```bash
# Update schedule (e.g., change to every 30 min)
curl -X PUT "https://$SCHEDULER_URL/scheduler/jobs/daily-sync" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"schedules": [{"cron": "*/30 * * * *", "description": "Every 30 min"}]}'

# Deactivate without deleting
curl -X PATCH "https://$SCHEDULER_URL/scheduler/jobs/daily-sync" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"active": false}'

# Delete job entirely
curl -X DELETE "https://$SCHEDULER_URL/scheduler/jobs/daily-sync" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 6. Create ABAP Cloud Application Job (Replaces SM37)

1. In ADT, create a class implementing `IF_APJ_DT_EXECUTION_OBJECT`
2. Define job template in the class via `IF_APJ_DT_EXECUTION_OBJECT~get_parameters`
3. Register template:
```abap
" Class implementing the job step handler
CLASS zcl_daily_sync_job DEFINITION
  PUBLIC
  INTERFACES if_apj_dt_execution_object
  INTERFACES if_apj_rt_execution_object.
ENDCLASS.
```
4. Create Application Job Template via ADT → New → ABAP Application Job Template
5. Schedule via Fiori app **Application Jobs** (transaction `F1076`)

## Pitfalls

| Cause | Solution |
|---|---|
| Job fails with HTTP 401 Unauthorized | Token expired before job runs. Use OAuth client credentials flow in the job definition or configure `Authorization` header dynamically via a destination with `OAuth2ClientCredentials`. |
| Job runs but target endpoint unreachable | Ensure the Cloud Foundry app is running and the URL is correct. Check `cf apps` for status. The scheduler and app must be in the same subaccount or use an internet-facing route. |
| Concurrent runs corrupt data | Missing `noOverlap: true`. Set it to `true` in the job definition to prevent overlapping executions. |
| Job exceeds 2h timeout | Max execution time is 2 hours. Split long-running jobs into smaller batches or implement pagination in the REST endpoint. Use `retryPolicy` for transient failures. |
| Cron fires at wrong time | Cron expressions use **UTC only** — no timezone offset. Calculate the UTC equivalent of your local time. Add `"timezone": "UTC"` explicitly for clarity. |
| Lite plan rejects job creation | Lite plan is limited to 10 active jobs. Deactivate or delete unused jobs, or upgrade to standard plan. |
| Retry storms after backend outage | `retryInterval` too short. Increase to 300+ seconds and set `maxRetries` to 3-5. Consider exponential backoff if supported. |

## Verification

```bash
# Job exists and is active
curl -s "https://$SCHEDULER_URL/scheduler/jobs/daily-sync" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  | jq '{name, active, schedules: .schedules[0].cron}'

# Last run succeeded
LAST_RUN=$(curl -s "https://$SCHEDULER_URL/scheduler/jobs/daily-sync/runs?\$top=1" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq -r '.runs[0].status')
echo "Last run status: $LAST_RUN"   # Should be "COMPLETED" or "SUCCESSFUL"

# Check run count today
curl -s "https://$SCHEDULER_URL/scheduler/jobs/daily-sync/runs?\$top=50" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  | jq '[.runs[] | select(.startTime | startswith("2024-01-15"))] | length'

# ABAP job template registered
# In ADT: Search "zcl_daily_sync_job" → verify IF_APJ_DT_EXECUTION_OBJECT is implemented
# In Fiori: F1076 → filter by template name → should appear in list
```

Checklist:
- [ ] Job definition returns HTTP 201 on creation
- [ ] Manual immediate run completes with status `COMPLETED`
- [ ] Scheduled runs execute at the expected UTC time
- [ ] `noOverlap: true` prevents concurrent executions
- [ ] Retry policy triggers on failure (check run logs for retry attempts)
- [ ] ABAP application job template visible in Fiori app F1076
- [ ] No more than 10 active jobs on Lite plan
