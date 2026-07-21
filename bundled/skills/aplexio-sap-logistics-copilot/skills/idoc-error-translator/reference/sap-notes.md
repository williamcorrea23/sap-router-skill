# SAP Notes — IDoc Error Reference Pointers

Pointer table only. Note numbers and content drift over SAP releases — always cross-check on the SAP Support portal (https://launchpad.support.sap.com/) with the customer's system release before applying.

| Pattern / error clue | Applicable Notes (starting point) | Area |
|---|---|---|
| `Partner <X> is not defined` / status 56 — missing partner profile | 1296259, 366604 | WE20 partner profile setup, ALE partner basics |
| `No inbound process code found` — status 56 | 313113, 384462 | WE42 / WE20 inbound process-code assignment |
| `Port <X> not defined` | 69010, 191765 | WE21 port config; file / tRFC port setup |
| `Function module <X> not assigned` (process code) | 384462 | WE42 process-code → function module mapping |
| Status 29 / 65 — ALE distribution model gaps | 214763, 555975 | BD64 model setup, filtering |
| Status 51 — ORDERS inbound, customer not found | 109367 | Customer / vendor determination from IDoc partner |
| Status 51 — ORDERS inbound, material number conversion | 388091, 31126 | MATNR conversion, MM02 external number |
| Status 51 — DELVRY inbound, PO line not open | 203574, 352063 | VL31N / inbound delivery matching |
| Status 51 — DESADV, quantity mismatch vs PO | 549023 | ASN tolerance and overdelivery |
| Status 51 — INVOIC02 (LIV), tolerance / block | 48819, 126977 | MM-IV tolerance keys (DQ, PP, etc.) |
| Status 51 — INVOIC02, GR-based IV without GR | 322430 | GR-based invoice verification prerequisites |
| Status 51 — WMMBXY, movement type not allowed | 82166 | Movement type / plant config |
| Status 26 — outbound syntax error, Z-segment | 101837 | Custom segment release & extension |
| Status 64 stuck — RBDAPP01 not running | 488757 | Scheduled inbound processing best practices |
| Status 17 / 40 — partner functional ack negative | 752712 | ALEAUD interpretation |
| Large IDoc performance / SM58 stuck | 549543, 1333417 | tRFC tuning, IDoc packaging |
| Serialization / sequencing issues (OM) | 205149 | IDoc serialization groups |
| Reprocessing in BD87 — bulk | 388091 | Mass reprocessing best practices |
| EDI subsystem time-out / ack never arrives | 175945 | EDI subsystem timeouts |

## How to use this table

1. Identify the clue in the paste (status code + message keywords).
2. Pick the closest matching row.
3. Cite the Note number(s) in the per-item analysis **only when the clue is a strong match** — never cite a Note speculatively.
4. If no row is a confident match, skip the Note citation and rely on the status-code reference + message text.

## When to escalate to SAP support

- Status 51 persists after master-data and config look correct.
- Status 26 on a standard (non-Z) segment — likely a release/patch-level bug.
- Status 29/65 with BD64 looking correct — possible ALE service issue; involve Basis.
- Any IDoc status behavior that changed after a recent release/upgrade — check the Notes on the applicable support package.
