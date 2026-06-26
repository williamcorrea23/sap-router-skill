---
name: sap-btp-document-mgmt
description: SAP BTP Document Management Service — document storage, folder management, file upload/download, versioning, CMIS integration, document repository for cloud apps, BTP Document Service vs SAP DMS, integration with ABAP Cloud (FILE replacement), document SDK for Node.js/Java. Use when migrating FILE/DATASET ABAP ops to BTP cloud, storing documents for CAP apps, or implementing document management on SAP BTP.
---

# SAP BTP Document Management Service

Cloud-native document storage replacing legacy file operations on SAP BTP.

## Why This Matters for ABAP Cloud Migration

```abap
" NOT available in ABAP Cloud:
OPEN DATASET lv_file FOR INPUT IN TEXT MODE.
READ DATASET lv_file INTO lv_data.

" Cloud alternative: Document Management Service
" via cl_bc_file_upload_download (C1 released)
DATA(lo_file) = cl_bc_file_upload_download=>create_instance( ).
lo_file->upload_file(
  iv_file_name    = 'materials.csv'
  iv_content_type = 'text/csv'
  iv_data         = lv_csv_content
).
```

## Service Instance

```bash
cf create-service document-management standard my-doc-store
cf create-service-key my-doc-store my-key
cf service-key my-doc-store my-key  # → get credentials
```

## CMIS API (Content Management Interoperability Services)

```bash
# List repository
curl https://<doc-service>.cfapps.us10.hana.ondemand.com/browser/<repo-id>/root \
  -u <user>:<password>

# Create folder
curl -X POST https://<doc-service>.cfapps.us10.hana.ondemand.com/browser/<repo-id>/root \
  -H "Content-Type: application/json" \
  -u <user>:<password> \
  -d '{"cmisaction":"createFolder","propertyId[0]":"cmis:name","propertyValue[0]":"invoices"}'

# Upload file
curl -X POST https://<doc-service>.cfapps.us10.hana.ondemand.com/browser/<repo-id>/root/invoices \
  -F "file=@invoice.pdf" \
  -u <user>:<password>
```

## CAP Integration

```javascript
const cds = require('@sap/cds')
const FormData = require('form-data')
const axios = require('axios')
const { getDestination } = require('@sap-cloud-sdk/connectivity')

module.exports = class InvoiceService extends cds.ApplicationService {
  async init() {
    this.on('uploadInvoice', async (req) => {
      const { file } = req.data
      const dest = await getDestination('DOC_SERVICE')
      const form = new FormData()
      form.append('file', file.buffer, { filename: file.name })

      const result = await axios.post(
        `${dest.url}/browser/${dest.repoId}/root/invoices`,
        form,
        {
          headers: {
            ...form.getHeaders(),
            Authorization: `Basic ${Buffer.from(`${dest.username}:${dest.password}`).toString('base64')}`
          }
        }
      )
      return { documentId: result.data.properties['cmis:objectId'].value }
    })
    await super.init()
  }
}
```

## Key Features

| Feature | Description |
|---|---|
| Versioning | Automatic version control for documents |
| CMIS standard | Industry-standard API for document management |
| Access control | Role-based access per folder/document |
| Full-text search | Search document content and metadata |
| Folder hierarchy | Create organizational folder structures |
| SAP DMS integration | Sync with SAP Document Management System |

## Gotchas

- **Service plan**: choose `standard` for production, `free` for dev (100MB limit)
- **CMIS is the API** — do not use proprietary APIs; CMIS is standard + portable
- **File size limit**: 100MB per file (standard plan)
- **Document retention**: configure in admin UI, not via API
- **ABAP Cloud FILE replacement**: Document Management Service replaces OPEN DATASET
