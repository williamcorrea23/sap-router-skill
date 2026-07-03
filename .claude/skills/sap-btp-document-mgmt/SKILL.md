---
name: sap-btp-document-mgmt
description: >
  SAP BTP Document Management Service — document storage, folder management,
  file upload/download, versioning, CMIS integration. Use when migrating FILE/DATASET
  ABAP ops to BTP cloud, storing documents for CAP apps, or implementing document
  management on SAP BTP.
trigger:
  keywords:
    - BTP document management
    - CMIS repository
    - OPEN DATASET replacement
    - document storage SAP cloud
    - file upload CAP
  intent: User needs to store, manage, or retrieve documents on SAP BTP, or replace legacy ABAP file operations in a cloud migration.
---

# SAP BTP Document Management Service

Cloud-native document storage replacing legacy `OPEN DATASET` / `READ DATASET` ABAP operations.

## Prerequisites

- SAP BTP subaccount with Cloud Foundry enabled
- `cf` CLI installed and logged in (`cf login`)
- Space Developer role in the target BTP space
- (Optional) Node.js 18+ for CAP integration

## 1. Create Service Instance and Get Credentials

```bash
# Create service (standard plan for prod, free for dev — 100MB limit)
cf create-service document-management standard my-doc-store

# Create service key
cf create-service-key my-doc-store my-key

# Retrieve credentials (save URL, user, password, repositoryId)
cf service-key my-doc-store my-key
```

## 2. Create a Folder via CMIS API

```bash
curl -X POST \
  "https://<doc-service-url>/browser/<repo-id>/root" \
  -H "Content-Type: application/json" \
  -u "<user>:<password>" \
  -d '{
    "cmisaction": "createFolder",
    "propertyId[0]": "cmis:name",
    "propertyValue[0]": "invoices"
  }'
```

## 3. Upload a Document

```bash
curl -X POST \
  "https://<doc-service-url>/browser/<repo-id>/root/invoices" \
  -F "file=@invoice.pdf" \
  -u "<user>:<password>"
```

The response includes `cmis:objectId` — store this as the document reference.

## 4. List Documents in a Folder

```bash
curl "https://<doc-service-url>/browser/<repo-id>/root/invoices" \
  -u "<user>:<password>"
```

## 5. CAP Integration (Node.js)

```javascript
const cds = require('@sap/cds')
const FormData = require('form-data')
const axios = require('axios')
const { getDestination } = require('@sap/cloud-sdk/connectivity')

module.exports = class InvoiceService extends cds.ApplicationService {
  async init() {
    this.on('uploadInvoice', async (req) => {
      const { file } = req.data
      const dest = await getDestination('DOC_SERVICE')
      const form = new FormData()
      form.append('file', file.buffer, { filename: file.name })

      const res = await axios.post(
        `${dest.url}/browser/${dest.repoId}/root/invoices`,
        form,
        {
          headers: {
            ...form.getHeaders(),
            Authorization: `Basic ${Buffer.from(
              `${dest.username}:${dest.password}`
            ).toString('base64')}`,
          },
        }
      )
      return { documentId: res.data.properties['cmis:objectId'].value }
    })
    await super.init()
  }
}
```

## 6. ABAP Cloud Replacement (C1 Released API)

```abap
" Replaces OPEN DATASET / READ DATASET in ABAP Cloud
DATA(lo_file) = cl_bc_file_upload_download=>create_instance( ).
lo_file->upload_file(
  iv_file_name    = 'materials.csv'
  iv_content_type = 'text/csv'
  iv_data         = lv_csv_content
).
```

## Pitfalls

- **Cause:** `free` plan used in production → **Solution:** `free` has 100MB limit; switch to `standard` plan before go-live.
- **Cause:** CMIS call returns 401 Unauthorized → **Solution:** Service key credentials rotate; re-run `cf service-key` to get fresh credentials.
- **Cause:** File upload fails silently above 100MB → **Solution:** Standard plan enforces 100MB per-file limit; chunk large files or use SAP Object Storage.
- **Cause:** CMIS folder not found after creating → **Solution:** Folder creation is eventually consistent; retry after 2 seconds or check with a list call.
- **Cause:** Using proprietary APIs instead of CMIS → **Solution:** Always use CMIS endpoints — they are standard, portable, and documented.
- **Cause:** Document retention rules missing → **Solution:** Retention policies are configured in the admin UI, not via API.

## Verification

```bash
# 1. Verify service instance exists and is running
cf services | grep my-doc-store

# 2. Verify CMIS endpoint responds
curl -s -o /dev/null -w "%{http_code}" \
  "https://<doc-service-url>/browser/<repo-id>/root" \
  -u "<user>:<password>"
# Expected: 200

# 3. Verify uploaded document is retrievable
curl -s \
  "https://<doc-service-url>/browser/<repo-id>/root/invoices" \
  -u "<user>:<password>" | jq '.objects[].properties["cmis:name"].value'
# Expected: list including your file name
```
