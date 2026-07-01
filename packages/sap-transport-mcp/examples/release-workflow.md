# Transport Release Workflow

The standard 6-step sequence Claude follows for every transport release.

---

## Scenario

A developer has added ABAP objects to `DEVK900123` and wants to release it to QA.

---

## Step 1 — Confirm Systems

**Claude calls:** `transport_list_systems`

```json
{
  "configuredSystems": [
    { "id": "DEV", "hostname": "dev.sap.company.com", "client": "100", "isDefault": true },
    { "id": "QA",  "hostname": "qa.sap.company.com",  "client": "200", "isDefault": false }
  ],
  "defaultSystem": "DEV"
}
```

---

## Step 2 — List Open Transports

**Claude calls:** `transport_list_requests` with `status=Modifiable`

```json
{
  "system": "DEV",
  "totalCount": 3,
  "transports": [
    { "transportNumber": "DEVK900123", "description": "Add plant 1000 config for Q2", "status": "Modifiable", "owner": "JSMITH", "targetSystem": "QA1", "objectCount": 5 },
    ...
  ]
}
```

---

## Step 3 — Inspect the Transport

**Claude calls:** `transport_get_request` with `transportNumber=DEVK900123`

Returns full detail: tasks, all objects, current status.

---

## Step 4 — Verify Object List

**Claude calls:** `transport_list_objects` with `transportNumber=DEVK900123`

```json
{
  "transportNumber": "DEVK900123",
  "objectCount": 5,
  "objects": [
    { "objectType": "TABL", "objectName": "ZPLANT_CONFIG", "programId": "Repository Object" },
    { "objectType": "PROG", "objectName": "ZPLANT_UPLOAD", "programId": "Repository Object" },
    ...
  ]
}
```

**Claude presents this to the user:**
> "Transport DEVK900123 contains 5 objects: table ZPLANT_CONFIG, program ZPLANT_UPLOAD, [etc.].
> Target system: QA1. Release is irreversible. Do you want to proceed?"

---

## Step 5 — Check Import Queue

**Claude calls:** `transport_check_import_queue` with `targetSystemId=QA1`

Confirms QA1 is not backlogged before adding another transport.

---

## Step 6 — Release (after user confirms)

**Claude calls:** `transport_release_request` with `transportNumber=DEVK900123`

Policy checks run first:
- DRY_RUN=false ✓
- objectCount=5 > 0 ✓
- status=Modifiable ✓

SAP release executes, then reads back to verify:

```json
{
  "success": true,
  "transportNumber": "DEVK900123",
  "message": "Transport DEVK900123 released successfully on DEV. 5 object(s) exported to QA1.",
  "verification": {
    "status": "Released",
    "objectCount": 5,
    "targetSystem": "QA1",
    "releasedAt": "2026-05-26T14:30:00.000Z"
  }
}
```

**Claude confirms to user:**
> "Transport DEVK900123 has been released. Status is now Released, 5 objects exported to QA1 at 2:30 PM.
> Your Basis team can now import it into QA."

---

## What Happens if Release is Blocked

| Reason | Error | Fix |
|--------|-------|-----|
| DRY_RUN=true | Policy violation [DRY_RUN] | Set DRY_RUN=false |
| No objects | Policy violation [EMPTY_TRANSPORT] | Add objects in SE09/ADT |
| Already released | Policy violation [DELETE_RELEASED] | Nothing to do — already released |
