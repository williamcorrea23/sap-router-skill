# Stream handling — file upload & download in RAP

RAP supports **binary stream properties** for uploading and downloading
files (PDFs, images, attachments) as part of a BO instance. The consumer
sees them as standard OData V4 stream properties: the entity has metadata
fields (filename, MIME type, size) plus a binary payload accessed via a
dedicated URL.

> **Anchored to**:
> https://help.sap.com/docs/abap-cloud/abap-rap/large-object-handling
> https://help.sap.com/docs/abap-cloud/abap-cds-development-user/semantics-annotations

> **OData version**: this file assumes OData V4. OData V2 streams have a
> different mechanism and are out of the skill's default — produce V2
> stream handling only on explicit request.

---

## 1. The stream property pattern

A streamed file on a BO instance needs **four columns** on the persistence
and the interface view:

| Column                       | Type                       | Purpose                              |
|------------------------------|----------------------------|--------------------------------------|
| The content                  | `abap.rstr` (`RawString`)  | Raw bytes — the file payload.        |
| The MIME type                | `abap.char(128)`            | e.g. `application/pdf`, `image/png`. |
| The filename                 | `abap.char(255)`            | Original filename (display + download). |
| The size                     | `abap.int4`                 | Bytes (optional but recommended).    |

### 1.1 DDIC table

```abap
@EndUserText.label: 'Travel attachment'
define table ztravel_att {
  key client          : abap.clnt not null;
  key attachment_uuid : sysuuid_x16 not null;
  travel_uuid         : sysuuid_x16;                     " parent reference

  attachment          : abap.rstr;                       " the bytes
  mime_type           : abap.char(128);                  " MIME type
  filename            : abap.char(255);                  " original name
  filesize            : abap.int4;                       " bytes

  last_changed_at     : abp_lastchange_tstmpl;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;
}
```

### 1.2 Interface view

```abap
@AccessControl.authorizationCheck: #CHECK
@EndUserText.label: 'Travel attachment — interface'
define view entity I_TravelAttachment
  as select from ztravel_att
  association to parent I_Travel as _Travel on $projection.TravelUUID = _Travel.TravelUUID
{
  key attachment_uuid as AttachmentUUID,
      travel_uuid     as TravelUUID,

      @Semantics.largeObject:
        { mimeType:           'MimeType',
          fileName:           'FileName',
          contentDispositionPreference: #ATTACHMENT,
          acceptableMimeTypes: [ 'application/pdf', 'image/png', 'image/jpeg' ] }
      attachment      as Attachment,
      mime_type       as MimeType,
      filename        as FileName,
      filesize        as FileSize,

      @Semantics.systemDateTime.lastChangedAt: true
      last_changed_at as LastChangedAt,

      @Semantics.systemDateTime.localInstanceLastChangedAt: true
      local_last_changed_at as LocalLastChangedAt,

      _Travel
}
```

### 1.3 The `@Semantics.largeObject` annotation

| Property                          | Meaning                                                              |
|-----------------------------------|----------------------------------------------------------------------|
| `mimeType: 'MimeType'`            | Field that carries the MIME type.                                    |
| `fileName: 'FileName'`            | Field that carries the original filename.                            |
| `contentDispositionPreference`    | `#INLINE` (browser displays) or `#ATTACHMENT` (browser downloads).   |
| `acceptableMimeTypes: [ ... ]`    | Whitelist of allowed MIME types — RAP enforces this on upload.       |
| `maxOctetLength`                  | Optional max bytes — RAP rejects uploads larger than this.           |

Whitelisting `acceptableMimeTypes` is **the primary RAP-side defense
against malicious uploads**. Restrict it to the MIME types your business
actually accepts. Never use a wildcard.

---

## 2. Projection and BDEF

The projection exposes the attachment to the service:

```abap
@AccessControl.authorizationCheck: #CHECK
define view entity R_TravelAttachment
  as projection on I_TravelAttachment
{
  key AttachmentUUID,
      TravelUUID,
      @Semantics.largeObject:
        { mimeType: 'MimeType', fileName: 'FileName' }
      Attachment,
      MimeType,
      FileName,
      FileSize,
      _Travel : redirected to parent R_Travel
}
```

The BDEF treats `Attachment` like any field but flags it streamable:

```abap
managed implementation in class zbp_i_travel_att unique;
strict ( 2 );

define behavior for I_TravelAttachment alias Attachment
persistent table ztravel_att
lock dependent by _Travel
authorization dependent by _Travel
etag master LocalLastChangedAt
{
  update;
  delete;

  field ( numbering : managed, readonly ) AttachmentUUID;
  field ( readonly ) LastChangedAt, LocalLastChangedAt, FileSize;

  /* allow upload through the standard OData binary endpoint */
  /* (no extra clauses needed — the @Semantics.largeObject annotation drives it) */

  mapping for ztravel_att
  {
    AttachmentUUID     = attachment_uuid;
    TravelUUID         = travel_uuid;
    Attachment         = attachment;
    MimeType           = mime_type;
    FileName           = filename;
    FileSize           = filesize;
    LastChangedAt      = last_changed_at;
    LocalLastChangedAt = local_last_changed_at;
  }
}
```

The child is `lock dependent by _Travel` so uploads participate in the
Travel composition's lock. Authorization is also inherited.

---

## 3. Upload — what the consumer sends

OData V4 binary upload (single request):

```
PUT /sap/opu/odata4/sap/.../Attachment(<uuid>)/Attachment HTTP/1.1
Content-Type: application/pdf
Slug: invoice.pdf

<binary bytes ...>
```

- The path segment `Attachment` after the entity URL is the **stream
  property name** (the field annotated `@Semantics.largeObject`).
- `Content-Type` carries the MIME type — RAP validates it against the
  `acceptableMimeTypes` whitelist.
- `Slug` carries the filename (optional but standard).

For draft-aware uploads, the draft is `PATCH`ed and then activated.

---

## 4. Download — what the consumer requests

```
GET /sap/opu/odata4/sap/.../Attachment(<uuid>)/Attachment HTTP/1.1
```

RAP responds with the binary payload, the MIME type from the `MimeType`
field, and (if `#ATTACHMENT` is the preference) a
`Content-Disposition: attachment; filename="<FileName>"` header so the
browser triggers a download instead of inline display.

---

## 5. Size and performance considerations

| Concern                                       | Recommendation                                                                                  |
|-----------------------------------------------|--------------------------------------------------------------------------------------------------|
| Very large files (>50 MB)                     | Inline `abap.rstr` works but eats memory; for very large content, consider object-store offloading (check the SAP Help Portal for the released option on your target platform — varies between BTP ABAP Env, S/4HC public, S/4HC private, on-prem). |
| Many small files per row                      | Use a 1:N child table (one `Attachment` row per file), not multiple stream fields on the parent. |
| Streaming download                            | The OData runtime streams; you don't read into ABAP memory unless you handle in a behavior pool. |
| Compression                                   | Not in the RAP runtime — handle at the HTTP layer (gateway / approuter / CDN).                  |

---

## 6. Authorization on attachments

`lock dependent by _Travel` + `authorization dependent by _Travel` means
RAP delegates the authorization check to the parent BO. A user who can
read the parent Travel can read its attachments; a user who can update
Travel can upload / replace / delete attachments.

If attachments need **independent** authorization (e.g. confidential
attachments restricted to a subset of users who can otherwise read the
parent), make the attachment BO its own `authorization master ( instance )`
and write a `FOR INSTANCE AUTHORIZATION` handler.

---

## 7. Security checklist (uploads)

- ✅ Whitelist `acceptableMimeTypes` — limit to your business set.
- ✅ Set a sane `maxOctetLength` to prevent storage exhaustion.
- ✅ Use `contentDispositionPreference: #ATTACHMENT` for any user-uploaded
  content that could be HTML/JS/SVG — prevents inline rendering and the
  associated XSS class of attacks.
- ✅ Track `LastChangedBy` / `LastChangedAt` for audit on the attachment.
- ✅ Sanitize filenames before display in the UI (the Fiori control does
  this, but custom UI must not echo `FileName` verbatim).
- ⚠️ Treat MIME-type matching as a coarse filter — the bytes can still be
  something else. For high-risk scenarios (public-facing portals,
  user-shared content) **scan the payload** post-upload in a saver hook
  or downstream pipeline (virus-scan, content-safety) before exposing it
  to other users.
- ⚠️ Be cautious with `contentDispositionPreference: #INLINE` for image
  MIME types — SVGs can contain JavaScript. Either restrict SVG entirely
  or force `#ATTACHMENT`.

---

## 8. Common gotchas

- ❌ Omitting `@Semantics.largeObject` — the field renders as a base64
  string instead of a stream property; uploads/downloads via the binary
  endpoint don't work.
- ❌ Forgetting `acceptableMimeTypes` — any MIME type is accepted,
  including potentially executable content.
- ❌ Storing the file metadata (filename, MIME type) on a different row
  than the bytes — split storage corrupts the link.
- ❌ Trying to upload to a property of the parent's projection that
  doesn't have `@Semantics.largeObject` propagated — the OData binary
  endpoint won't surface it.
- ❌ Using `abap.string` instead of `abap.rstr` for the bytes —
  `abap.string` is for character data; binary uploads will corrupt.

---

## 9. Anchor references

- Large object handling in RAP:
  https://help.sap.com/docs/abap-cloud/abap-rap/large-object-handling
- `@Semantics.largeObject` annotation:
  https://help.sap.com/docs/abap-cloud/abap-cds-development-user/semantics-annotations
- OData V4 stream properties:
  https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#sec_StreamProperty

Related skill files: [cds-view-entity.md](cds-view-entity.md),
[cds-projection-view.md](cds-projection-view.md),
[behavior-definition.md](behavior-definition.md),
[service-binding.md](service-binding.md).
