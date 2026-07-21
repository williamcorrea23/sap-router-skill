# IDoc Status Codes — Reference

Covers the status codes most commonly seen in SAP logistics / supply-chain IDocs (ORDERS, DESADV, DELVRY, INVOIC, SHPMNT, WMMBXY, PAYEXT). Non-exhaustive; focuses on errors that land in key-users' laps.

Each entry: **status** → **meaning** → **common concrete causes** → **first place to look**.

---

## Outbound statuses

### 01 — IDoc created
Not an error. Baseline.

### 03 — Data passed to port OK
Successful handoff to the tRFC / file / HTTP port. Not an error; if stuck here too long, the partner system never confirmed receipt — check port (WE21, SM59) and status 16 ack.

### 12 — Dispatch OK
Passed to the external channel. Still not a guarantee the partner processed it.

### 16 — Functional ack positive
Partner confirmed successful processing.

### 17 — Functional ack negative
Partner rejected. Read the message text — it contains the partner's reason.
**First place:** BD87 → find the IDoc → double-click status → message text.

### 26 — Error during syntax check (outbound)
Outbound segment structure is invalid. Usually a Z-segment custom field with a wrong data type, or a mandatory segment not filled by the user exit.
**First place:** WE19 → test tool → re-run outbound → watch which segment fails.

### 29 — Error in ALE service
Distribution model misconfiguration. The receiver is missing from BD64 for this message type, or the filter on a segment rejected the IDoc.
**First place:** BD64 (distribution model), then WE21 (ports) and WE20 (partner profile outbound params).

### 30 — IDoc ready for dispatch (ALE service)
Held up in ALE service; will move to 03/12 after the next RSEOUT00 run.
**First place:** SM37 → check RSEOUT00 schedule, or run it manually.

---

## Inbound statuses

### 50 — IDoc added
Received by SAP, not yet processed. If stuck here, the inbound processing job hasn't picked it up.
**First place:** SM37 → RBDAPP01 job.

### 51 — Application document not posted
The big one. The inbound function module ran but the application (SD order, goods receipt, invoice, etc.) rejected the data. Message text is application-specific.

Common concrete causes by message type:
- **ORDERS05 (sales order inbound):** customer / material number not in master data; delivery plant missing for material; pricing condition missing; credit check hard-blocked the order.
- **DELVRY07 (inbound delivery):** purchase order line not found or already fully delivered; plant/storage location determination failed; batch split data mismatched; handling-unit references not found.
- **DESADV (ASN inbound):** reference PO number unknown; expected quantity mismatch with open PO qty; supplier partner not matched to vendor master.
- **INVOIC02 (invoice receipt, LIV):** price/quantity variance outside tolerance (MM-IV block); tax code missing on PO; GR-based IV but no GR posted; currency not set up for vendor.
- **SHPMNT05 (shipment inbound):** carrier not in vendor master; route determination failed.
- **WMMBXY (goods movement):** movement type not valid for plant/sloc; stock insufficient for reversal; batch not found; serial number required but missing.

**First place:** BD87 → select IDoc → status record 51 → full message text. Then go to the application: VA02 (sales order), MIGO/VL32N (inbound delivery), MIRO (invoice).

### 52 — Application document not fully posted
Partial posting. Rare. Usually a parallel-processing race — reprocess via BD87.

### 53 — Application document posted
Success.

### 56 — IDoc with errors added
Partner / port / process-code misconfiguration at the inbound gate. The IDoc never reached the application.
Common concrete causes:
- Sender partner not maintained in WE20 inbound parameters.
- Partner exists but the specific message type has no inbound process code assigned.
- Partner role mismatch (e.g., sender as LI but profile defined for LS).
- Port in the IDoc control record doesn't match a WE21 definition.

**First place:** WE20 → partner profile of the sending partner → Inbound parameters tab.

### 61 — Error passing data to application
ALE intermediate step failed. Usually a permission / authorization issue in the inbound service user.
**First place:** SU53 after reprocessing via BD87.

### 62 — IDoc passed to application
Transitional status; becomes 51/52/53 quickly.

### 64 — IDoc ready to be transferred to application
Waiting on RBDAPP01. Same as 50 but post-ALE-service. If stuck, processing job is not running.
**First place:** SM37 → RBDAPP01 job schedule.

### 65 — Error in ALE service (inbound)
Inbound distribution model missing the sending LS for this message type, or filter rejected.
**First place:** BD64.

### 68 — Error — no further processing
Manually set by an admin to stop reprocessing. Review the IDoc before clearing.

### 69 — IDoc edited
A user manually edited the IDoc (WE19 or BD87 edit). Next processing attempt will use the edited content.

---

## Acknowledgement statuses (ALEAUD / ack IDoc)

### 39 / 40 — Positive / negative functional ack received
These are on the original outbound IDoc. Status 40 = the partner rejected the business content; message text contains their reason. Don't re-send the same content; fix first.

### 41 — Application document created at receiver
Receiver confirmed successful application-side posting.

---

## Quick-triage rules

- **Any 51:** application rejected → go straight to message text, it names the missing/invalid field.
- **Any 56:** partner/port/process-code issue → WE20 first, not the application.
- **Any 29 or 65:** ALE distribution model → BD64.
- **Any 64 or 50 stuck for hours:** RBDAPP01 not running → SM37.
- **Any 26:** outbound syntax → a Z-segment data-type or mandatory-segment bug; WE19 to reproduce.
- **Status 17 or 40:** partner rejected a successfully-sent IDoc; read their reason in the message text.

## Reprocessing

After fixing root cause:
- **WE20 / BD64 / WE21 config issues:** reprocess via BD87 → select IDoc(s) → *Process*.
- **Application data issues (51):** either edit via BD87 → *Edit* (for small tweaks) or fix the source data (master data, PO, order) and reprocess.
- **Mass reprocessing:** BD87 with multi-select, or program RBDAPP01 with IDoc-number range.
