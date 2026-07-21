# Product create — OData V4 vs SOAP MDM Replicate

`SAP_COM_0009` "Product Integration" arrangement exposes **both** API paths for product master inbound writes:

| | OData V4 | SOAP MDM Replicate |
|---|---|---|
| Endpoint | `/sap/opu/odata4/sap/api_product/srvd_a2x/sap/product/0002/Product` | `/sap/bc/srt/scs_ext/sap/productmdmbulkreplicaterequest` |
| Method | `POST` (single resource) | `POST` SOAP envelope (bulk wrapper) |
| Sync/Async | Synchronous (HTTP 201 on commit) | Asynchronous one-way (HTTP 202 acknowledged, processed later) |
| Auth | Basic + CSRF | Basic |
| Per-call payload size | Lightweight (one product header + descriptions) | Heavy (bulk wrapper with up to N products) |
| Error visibility | Inline JSON `error.message` | Errors only in Fiori "Message Dashboard" (F4516) |
| Cloud Public Lean tenants | ✅ **Works out of the box** | ⚠️ Silent drops unless Sender Business System is registered AND outbound `ProductMDMBulkReplicateConfirmation_Out` is wired to the sender's HTTPS receiver |

## Decision rule for this skill

**Always use the OData V4 path.** Use SOAP only if:
- You're integrating SAP MDG → SAP S/4HANA Cloud and the MDG side is already a registered Business System, AND
- You need bulk semantics (>50 products per call), AND
- You can monitor failures via Fiori "Message Dashboard"

If you don't meet ALL three: V4 is faster, gives real errors, and doesn't need additional tenant config.

## The SOAP silent-drop trap (why probing SOAP wastes hours)

The SOAP runtime accepts any well-formed envelope on the published endpoint with HTTP 202. The actual processing happens in an async ABAP job that runs Sender Determination. If the inbound message's `<MessageHeader><SenderBusinessSystemID>` doesn't match a registered Business System in the "Communication Systems" Fiori app, the message is **silently discarded** — no SOAP fault, no entry in `SLG1` / Application Logs, no notification.

The only place these drops surface is:
- **Fiori app "Message Dashboard"** (app F4516, business role `SAP_BR_CONF_EXPERT_BUS_NET_INT`) — the Cloud Public equivalent of `SXMB_MONI` / `SRT_MONI`.

If you must use SOAP, the activation steps are:
1. Open Fiori "Communication Systems" → confirm the "Business System" field on the system that owns inbound traffic. That string is the *only* legal value for `<SenderBusinessSystemID>`.
2. Open Fiori "Communication Arrangements" → for `SAP_COM_0009`, activate the **outbound** service "Product Master - Confirmation from SAP S/4HANA Cloud to Client". The runtime needs receiver determination configured for the confirmation leg even if you don't consume the confirmation. Point at a dummy HTTPS receiver if necessary.
3. Confirm `MessageHeader/CreationDateTime`, `MessageHeader/ID`, and `SenderBusinessSystemID` are all populated in your envelope.
4. After every test POST, check Message Dashboard for the actual rejection reason.

But seriously: **just use V4.**

## OData V4 path — the working recipe

```http
GET  /sap/opu/odata4/sap/api_product/srvd_a2x/sap/product/0002/
     ?sap-client=<n>
Header: X-CSRF-Token: Fetch
→ captures token + cookie

POST /sap/opu/odata4/sap/api_product/srvd_a2x/sap/product/0002/Product
     ?sap-client=<n>
Headers: Authorization, Content-Type: application/json, X-CSRF-Token, Cookie
Body: deep-insert payload (see field-reference.md)
→ HTTP 201, full entity in response body
```

## References

- SAP S/4HANA Cloud API Hub — Product Master (A2X): https://api.sap.com/api/PRODUCTMDMBULKREPLICATEREQUEST/overview
- KBA 2893968 — "No business system ID was provided" (same silent-drop pattern on the parallel SalesOrder service)
- KBA 3220190 — "Receiver for Sender Business System ID could not be determined"
- Community: [Key mapping feature in Product SOAP service](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/key-mapping-feature-in-product-soap-service-productmdmbulkreplicaterequest/ba-p/12864287)
- Community: [SOAP interfaces for replication of Product Master data in SAP S/4HANA](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/soap-interfaces-for-replication-of-product-master-data-in-sap-s-4hana/ba-p/13332165)
- Fiori Apps Library — F4516 Message Monitoring: https://fioriappslibrary.hana.ondemand.com/sap/fix/externalViewer/#/detail/Apps('F4516')/S25
