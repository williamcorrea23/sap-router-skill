# SOAP envelope — Supplier Invoice ERP Create Request (sync)

**Verified against SAP S/4HANA Cloud Public Edition (S/4HANA Cloud Public Edition) 2026-05-11.** Returns `<SupplierInvoice><ID>...</ID><Year>...</Year></SupplierInvoice>` on success with `BusinessDocumentProcessingResultCode=1` (or `3` with warnings).

## Endpoint

```
POST https://<host>/sap/bc/srt/scs_ext/sap/ecc_suplrinvcerpcrtrc?sap-client=<n>
Authorization: Basic <base64(user:pass)>
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://sap.com/xi/APPL/Global2/SupplierInvoiceERPCreateRequestConfirmation_In/SupplierInvoiceERPCreateRequestConfirmation_InRequest"
Accept: text/xml
```

## Minimal working envelope (one PO-referenced item)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:n2="http://sap.com/xi/SAPGlobal20/Global">
 <soap:Header/>
 <soap:Body>
 <n2:SupplierInvoiceERPCreateRequest_sync>
 <MessageHeader>
 <CreationDateTime>{{ISO8601 timestamp}}</CreationDateTime>
 </MessageHeader>
 <SupplierInvoice>
 <BillFromID>{{supplier invoice ref, max 16 chars}}</BillFromID>
 <CompanyID>{{company code, e.g. 1010}}</CompanyID>
 <TypeCode>004</TypeCode>
 <IssueDate>{{YYYY-MM-DD}}</IssueDate>
 <PostingDate>{{YYYY-MM-DD}}</PostingDate>
 <CompletenessAndValidationStatusCode>5</CompletenessAndValidationStatusCode>
 <BillFromParty>
 <InternalID>{{supplier ID}}</InternalID>
 </BillFromParty>
 <CashDiscountTerms>
 <Code>{{payment terms, e.g. 0004}}</Code>
 </CashDiscountTerms>
 <PriceCalculation>
 <GrossAmount currencyCode="{{currency, e.g. EUR}}">{{header gross amount}}</GrossAmount>
 </PriceCalculation>
 <TaxCalculation>
 <AutomaticIndicator>false</AutomaticIndicator>
 <TaxDeterminationDate>{{YYYY-MM-DD}}</TaxDeterminationDate>
 </TaxCalculation>
 <Item>
 <ID>1</ID>
 <ReceivingPlantID>{{plant from PO line}}</ReceivingPlantID>
 <TypeCode>002</TypeCode>
 <ProcessingTypeCode>M</ProcessingTypeCode>
 <Quantity unitCode="PCE">{{qty}}</Quantity>
 <Product>
 <InternalID>{{material from PO line}}</InternalID>
 </Product>
 <PriceCalculation>
 <NetAmount currencyCode="{{currency}}">{{item net amount}}</NetAmount>
 </PriceCalculation>
 <TaxCalculation>
 <ProductTaxDetails>
 <TaxAmount currencyCode="{{currency}}">0.00</TaxAmount>
 <TaxBaseAmount currencyCode="{{currency}}">{{item net amount}}</TaxBaseAmount>
 <TaxationCharacteristicsCode>V0</TaxationCharacteristicsCode>
 </ProductTaxDetails>
 </TaxCalculation>
 <PurchaseOrderReference>
 <ID>{{PO number}}</ID>
 <ItemID>{{PO line, e.g. 10}}</ItemID>
 </PurchaseOrderReference>
 </Item>
 </SupplierInvoice>
 </n2:SupplierInvoiceERPCreateRequest_sync>
 </soap:Body>
</soap:Envelope>
```

## Field-discovery trail (why these values)

| Field | What was tried & rejected | What worked |
|---|---|---|
| Item `ProcessingTypeCode` | `001`, `002`, `01`, `02`, `1`, `2`, `3`, `H`, `D`, `I`, `IVE`, `INV`, `PO`, `REF`, `GR`, `003-006` | `M` (Material) — and `S` would also progress but lands on G/L-item validation |
| Item `Quantity unitCode` | `PC` (SAP internal) | `PCE` (ISO 6523) |
| Header `CompletenessAndValidationStatusCode` | `1`, `2`, `3`, `4`, `6-10`, `01-05` | `5` (Post) or `A` (Parked) — alphanumeric codes, not 1/2/3 |
| Header reference field | `SupplierInvoiceReference/ID` (rejected — that's for cancellation refs) | `BillFromID` (top-level) |
| Header `ProcessingTypeCode` | `001` (data-loss warning), various | Omit entirely (optional, defaults work) |
| Header `HeaderReferences` with `PurchaseOrderReferences` | Worked at status `A` (parked), but rejected at status `5` (post) with "References only supported for statuses A and D" | Omit for status=5 |
| Header `TaxCalculation/AutomaticIndicator` | `true` with explicit `ProductTaxDetails` → still got config errors | `false` when providing explicit details |
| Item `TaxCalculation/ProductTaxDetails` | Empty → `M8/375 mandatory TaxationCharacteristicsCode` | Must include `TaxAmount`, `TaxBaseAmount`, `TaxationCharacteristicsCode` (V0 passes through) |

## Multi-item invoice

Repeat `<Item>` blocks within `<SupplierInvoice>`. Increment `<ID>1</ID>`, `<ID>2</ID>`, etc. Each item gets its own `PurchaseOrderReference`. Header `GrossAmount` should equal the sum of item NetAmounts (when V0=0% tax).

## Response parsing

Success:
```xml
<SupplierInvoice><ID>5105600103</ID><Year>2025</Year></SupplierInvoice>
<Log><BusinessDocumentProcessingResultCode>1</BusinessDocumentProcessingResultCode></Log>
```
Or `Code=3` with warning items (still posted — typical for backdated invoices, "Net due date in past").

Failure:
```xml
<Log>
 <BusinessDocumentProcessingResultCode>5</BusinessDocumentProcessingResultCode>
 <Item>
 <TypeID>375(M8)</TypeID>
 <SeverityCode>3</SeverityCode>
 <Note>Fill in mandatory field ...</Note>
 </Item>
</Log>
```

The TypeID format is `<msg-number>(<msg-class>)`. Look it up in `known-error-codes.md`.
