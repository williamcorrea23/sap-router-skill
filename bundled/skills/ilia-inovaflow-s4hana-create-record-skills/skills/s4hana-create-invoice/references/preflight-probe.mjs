#!/usr/bin/env node
// Preflight probe — checks whether the tenant is ready to accept supplier invoice POSTs.
// Reads SAP_HOST / SAP_CLIENT / SAP_USERNAME / SAP_PASSWORD from env.
// Posts one minimal envelope. Categorizes the response.
//
// Usage:
//   SAP_HOST=https://<tenant>-api.s4hana.cloud.sap \
//   SAP_CLIENT=100 \
//   SAP_USERNAME=<user> \
//   SAP_PASSWORD=<pass> \
//   PROBE_PO=4500000000 \
//   PROBE_ITEM=10 \
//   node preflight-probe.mjs
import fs from 'node:fs';

const HOST = process.env.SAP_HOST;
const SAP_CLIENT = process.env.SAP_CLIENT || '100';
const USER = process.env.SAP_USERNAME;
const PASS = process.env.SAP_PASSWORD;
const PROBE_PO = process.env.PROBE_PO;
const PROBE_ITEM = process.env.PROBE_ITEM || '10';

if (!HOST || !USER || !PASS || !PROBE_PO) {
  console.error('Required env: SAP_HOST, SAP_USERNAME, SAP_PASSWORD, PROBE_PO. Optional: SAP_CLIENT, PROBE_ITEM.');
  process.exit(1);
}

const authHeader = 'Basic ' + Buffer.from(`${USER}:${PASS}`).toString('base64');
const SOAP_PATH = '/sap/bc/srt/scs_ext/sap/ecc_suplrinvcerpcrtrc';
const SOAP_ACTION = 'http://sap.com/xi/APPL/Global2/SupplierInvoiceERPCreateRequestConfirmation_In/SupplierInvoiceERPCreateRequestConfirmation_InRequest';

async function getJson(url) {
  const res = await fetch(url, { headers: { Authorization: authHeader, Accept: 'application/json' } });
  return res.json();
}

// Fetch PO line data
const poItemUrl = `${HOST}/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrderItem(PurchaseOrder='${PROBE_PO}',PurchaseOrderItem='${PROBE_ITEM}')?$format=json&sap-client=${SAP_CLIENT}`;
const poItemJ = await getJson(poItemUrl);
if (!poItemJ.d) {
  console.error(`PO ${PROBE_PO}/${PROBE_ITEM} not found or not accessible. Body:`, JSON.stringify(poItemJ).slice(0, 500));
  process.exit(1);
}
const item = poItemJ.d;
const poJ = await getJson(`${HOST}/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrder('${PROBE_PO}')?$format=json&sap-client=${SAP_CLIENT}`);
const po = poJ.d;
const qty = Math.max(1, Math.round(parseFloat(item.OrderQuantity) * 0.1));
const amount = (qty * parseFloat(item.NetPriceAmount)).toFixed(2);
const dateISO = `${new Date().getFullYear() - 1}-08-15`;  // assume Aug of prior year is in open period

const envelope = `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:n2="http://sap.com/xi/SAPGlobal20/Global">
  <soap:Header/>
  <soap:Body>
    <n2:SupplierInvoiceERPCreateRequest_sync>
      <MessageHeader><CreationDateTime>${new Date().toISOString()}</CreationDateTime></MessageHeader>
      <SupplierInvoice>
        <BillFromID>PROBE-${Date.now().toString().slice(-9)}</BillFromID>
        <CompanyID>${po.CompanyCode}</CompanyID>
        <TypeCode>004</TypeCode>
        <IssueDate>${dateISO}</IssueDate>
        <PostingDate>${dateISO}</PostingDate>
        <CompletenessAndValidationStatusCode>5</CompletenessAndValidationStatusCode>
        <BillFromParty><InternalID>${po.Supplier}</InternalID></BillFromParty>
        <CashDiscountTerms><Code>0004</Code></CashDiscountTerms>
        <PriceCalculation><GrossAmount currencyCode="${po.DocumentCurrency}">${amount}</GrossAmount></PriceCalculation>
        <TaxCalculation><AutomaticIndicator>false</AutomaticIndicator><TaxDeterminationDate>${dateISO}</TaxDeterminationDate></TaxCalculation>
        <Item>
          <ID>1</ID>
          <ReceivingPlantID>${item.Plant}</ReceivingPlantID>
          <TypeCode>002</TypeCode>
          <ProcessingTypeCode>M</ProcessingTypeCode>
          <Quantity unitCode="PCE">${qty}</Quantity>
          <Product><InternalID>${item.Material}</InternalID></Product>
          <PriceCalculation><NetAmount currencyCode="${po.DocumentCurrency}">${amount}</NetAmount></PriceCalculation>
          <TaxCalculation>
            <ProductTaxDetails>
              <TaxAmount currencyCode="${po.DocumentCurrency}">0.00</TaxAmount>
              <TaxBaseAmount currencyCode="${po.DocumentCurrency}">${amount}</TaxBaseAmount>
              <TaxationCharacteristicsCode>V0</TaxationCharacteristicsCode>
            </ProductTaxDetails>
          </TaxCalculation>
          <PurchaseOrderReference><ID>${PROBE_PO}</ID><ItemID>${PROBE_ITEM}</ItemID></PurchaseOrderReference>
        </Item>
      </SupplierInvoice>
    </n2:SupplierInvoiceERPCreateRequest_sync>
  </soap:Body>
</soap:Envelope>`;

const res = await fetch(`${HOST}${SOAP_PATH}?sap-client=${SAP_CLIENT}`, {
  method: 'POST',
  headers: {
    Authorization: authHeader,
    'Content-Type': 'text/xml; charset=utf-8',
    SOAPAction: `"${SOAP_ACTION}"`,
    Accept: 'text/xml',
  },
  body: envelope,
});
const text = await res.text();

const idMatch = text.match(/<SupplierInvoice><ID>([^<]+)<\/ID><Year>([^<]+)<\/Year>/);
const codeMatch = text.match(/<BusinessDocumentProcessingResultCode>(\d+)/);
const typeMatch = text.match(/<TypeID>([^<]+)<\/TypeID>/);
const noteMatch = text.match(/<Note>([^<]+)<\/Note>/);

console.log(`\n=== Tenant readiness probe ===`);
console.log(`Host: ${HOST}`);
console.log(`PO: ${PROBE_PO}/${PROBE_ITEM} (${item.Material}, ${po.Supplier}, ${po.DocumentCurrency})`);
console.log(`HTTP status: ${res.status}`);
console.log(`Result code: ${codeMatch?.[1]}`);

if (idMatch) {
  console.log(`\n✅ READY — Test invoice posted: ${idMatch[1]}/${idMatch[2]}`);
  console.log(`   Tenant is configured correctly. You can now run bulk invoice creation.`);
  console.log(`   NOTE: This probe created a real invoice. Cancel it via Fiori "Cancel Supplier Invoice" if you don't want it.`);
} else if (typeMatch?.[1].includes('FINS_ACDOC_CUST/201')) {
  console.log(`\n⛔ LEDGER CONFIG GAP — FINS_ACDOC_CUST/201`);
  console.log(`   Tenant ledger accounting principles are not set up correctly.`);
  console.log(`   See references/ledger-config-preflight.md for the fix path.`);
  console.log(`   Apply via CBC (SSCUI 103556) before any invoice POST will succeed.`);
} else if (typeMatch?.[1].includes('M8/535')) {
  console.log(`\n⚠️  POSTING PERIOD CLOSED`);
  console.log(`   Your test date (${dateISO}) is not in an open posting period.`);
  console.log(`   Either pick a date in the open window (read the error for allowed periods),`);
  console.log(`   or open the current period via Fiori "Open and Close Posting Periods".`);
  console.log(`   ${noteMatch?.[1]}`);
} else if (codeMatch?.[1] === '5') {
  console.log(`\n⚠️  POST REJECTED — see error details below`);
  console.log(`   TypeID: ${typeMatch?.[1]}`);
  console.log(`   Note: ${noteMatch?.[1]}`);
  console.log(`   Cross-reference with references/known-error-codes.md`);
} else {
  console.log(`\n? UNEXPECTED RESPONSE`);
  console.log(text.slice(0, 1500));
}
