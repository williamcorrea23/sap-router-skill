#!/usr/bin/env node
// Bulk supplier-invoice creator via SOAP A2X SupplierInvoiceERPCreateRequest_sync.
// Posts N invoices to candidate PO lines, with idempotent logging and per-record verification.
//
// Usage:
//   SAP_HOST=https://<tenant>-api.s4hana.cloud.sap \
//   SAP_CLIENT=100 \
//   SAP_USERNAME=<comm-user> \
//   SAP_PASSWORD=<comm-pass> \
//   TARGET_COUNT=50 \
//   COMPANY_CODE=1010 \
//   CURRENCY=EUR \
//   POSTING_YEAR_MONTH=2025-08 \
//   OUT_DIR=/tmp/create-invoices \
//   node bulk-invoice-poster.mjs
//
// Reads candidates from $OUT_DIR/po-candidates.json (auto-fetched if missing).
// Appends to $OUT_DIR/create-log.jsonl (idempotent — reruns skip already-posted PO lines).
// Halts on 3 consecutive failures.
import fs from 'node:fs';
import path from 'node:path';

const HOST = process.env.SAP_HOST;
const SAP_CLIENT = process.env.SAP_CLIENT || '100';
const USER = process.env.SAP_USERNAME;
const PASS = process.env.SAP_PASSWORD;
const TARGET_COUNT = parseInt(process.env.TARGET_COUNT || '50', 10);
const COMPANY_CODE = process.env.COMPANY_CODE || '1010';
const CURRENCY = process.env.CURRENCY || 'EUR';
const POSTING_YEAR_MONTH = process.env.POSTING_YEAR_MONTH || '2025-08';
const OUT_DIR = process.env.OUT_DIR || '/tmp/create-invoices';
const PARTIAL_QTY_FRACTION = parseFloat(process.env.PARTIAL_QTY_FRACTION || '0.5');

if (!HOST || !USER || !PASS) {
  console.error('Missing SAP_HOST / SAP_USERNAME / SAP_PASSWORD env vars.');
  process.exit(1);
}

const SOAP_PATH = '/sap/bc/srt/scs_ext/sap/ecc_suplrinvcerpcrtrc';
const SOAP_ACTION = 'http://sap.com/xi/APPL/Global2/SupplierInvoiceERPCreateRequestConfirmation_In/SupplierInvoiceERPCreateRequestConfirmation_InRequest';
const authHeader = 'Basic ' + Buffer.from(`${USER}:${PASS}`).toString('base64');

fs.mkdirSync(OUT_DIR, { recursive: true });
const LOG_PATH = path.join(OUT_DIR, 'create-log.jsonl');
const RESULTS_PATH = path.join(OUT_DIR, 'results.json');
const CANDIDATES_PATH = path.join(OUT_DIR, 'po-candidates.json');

async function getJson(url) {
  const res = await fetch(url, { headers: { Authorization: authHeader, Accept: 'application/json' } });
  return res.json();
}

async function fetchCandidates() {
  console.log('Fetching PO candidates...');
  const posJ = await getJson(`${HOST}/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrder?$top=200&$format=json&sap-client=${SAP_CLIENT}`);
  const pos = posJ.d?.results || [];
  const poMap = {};
  for (const po of pos) {
    poMap[po.PurchaseOrder] = { Supplier: po.Supplier, DocumentCurrency: po.DocumentCurrency, CompanyCode: po.CompanyCode };
  }
  const itemsJ = await getJson(`${HOST}/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrderItem?$top=500&$format=json&sap-client=${SAP_CLIENT}`);
  const items = itemsJ.d?.results || [];
  const candidates = [];
  for (const it of items) {
    const po = poMap[it.PurchaseOrder];
    if (!po) continue;
    if (po.DocumentCurrency !== CURRENCY) continue;
    if (po.CompanyCode !== COMPANY_CODE) continue;
    if (it.IsCompletelyInvoiced) continue;
    if (it.PurchaseOrderItemCategory && it.PurchaseOrderItemCategory !== '0') continue;
    if (!it.Material) continue;
    candidates.push({
      PurchaseOrder: it.PurchaseOrder,
      PurchaseOrderItem: it.PurchaseOrderItem,
      Supplier: po.Supplier,
      CompanyCode: po.CompanyCode,
      DocumentCurrency: po.DocumentCurrency,
      Material: it.Material,
      Plant: it.Plant,
      OrderQuantity: it.OrderQuantity,
      PurchaseOrderQuantityUnit: it.PurchaseOrderQuantityUnit,
      NetPriceAmount: it.NetPriceAmount,
    });
  }
  console.log(`  ${candidates.length} candidate PO lines (${CURRENCY}, CC ${COMPANY_CODE}, cat=0, not invoiced)`);
  fs.writeFileSync(CANDIDATES_PATH, JSON.stringify(candidates, null, 2));
  return candidates;
}

function loadCandidates() {
  if (fs.existsSync(CANDIDATES_PATH)) return JSON.parse(fs.readFileSync(CANDIDATES_PATH, 'utf8'));
  return null;
}

function loadDoneKeys() {
  const done = new Set();
  if (!fs.existsSync(LOG_PATH)) return done;
  for (const line of fs.readFileSync(LOG_PATH, 'utf8').split('\n')) {
    if (!line.trim()) continue;
    try {
      const e = JSON.parse(line);
      if (e.ok) done.add(`${e.po}/${e.item}`);
    } catch {}
  }
  return done;
}

function fnv1a(s) {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = (h * 0x01000193) >>> 0;
  }
  return h;
}

function xmlEscape(s) {
  return String(s).replace(/[<>&"']/g, (c) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&apos;' }[c]));
}

function buildEnvelope(c, dateISO, refId) {
  const qty = Math.max(1, Math.round(parseFloat(c.OrderQuantity) * PARTIAL_QTY_FRACTION));
  const amount = (qty * parseFloat(c.NetPriceAmount)).toFixed(2);
  return `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:n2="http://sap.com/xi/SAPGlobal20/Global">
  <soap:Header/>
  <soap:Body>
    <n2:SupplierInvoiceERPCreateRequest_sync>
      <MessageHeader><CreationDateTime>${new Date().toISOString()}</CreationDateTime></MessageHeader>
      <SupplierInvoice>
        <BillFromID>${xmlEscape(refId)}</BillFromID>
        <CompanyID>${xmlEscape(c.CompanyCode)}</CompanyID>
        <TypeCode>004</TypeCode>
        <IssueDate>${dateISO}</IssueDate>
        <PostingDate>${dateISO}</PostingDate>
        <CompletenessAndValidationStatusCode>5</CompletenessAndValidationStatusCode>
        <BillFromParty><InternalID>${xmlEscape(c.Supplier)}</InternalID></BillFromParty>
        <CashDiscountTerms><Code>0004</Code></CashDiscountTerms>
        <PriceCalculation><GrossAmount currencyCode="${xmlEscape(c.DocumentCurrency)}">${amount}</GrossAmount></PriceCalculation>
        <TaxCalculation>
          <AutomaticIndicator>false</AutomaticIndicator>
          <TaxDeterminationDate>${dateISO}</TaxDeterminationDate>
        </TaxCalculation>
        <Item>
          <ID>1</ID>
          <ReceivingPlantID>${xmlEscape(c.Plant)}</ReceivingPlantID>
          <TypeCode>002</TypeCode>
          <ProcessingTypeCode>M</ProcessingTypeCode>
          <Quantity unitCode="PCE">${qty}</Quantity>
          <Product><InternalID>${xmlEscape(c.Material)}</InternalID></Product>
          <PriceCalculation><NetAmount currencyCode="${xmlEscape(c.DocumentCurrency)}">${amount}</NetAmount></PriceCalculation>
          <TaxCalculation>
            <ProductTaxDetails>
              <TaxAmount currencyCode="${xmlEscape(c.DocumentCurrency)}">0.00</TaxAmount>
              <TaxBaseAmount currencyCode="${xmlEscape(c.DocumentCurrency)}">${amount}</TaxBaseAmount>
              <TaxationCharacteristicsCode>V0</TaxationCharacteristicsCode>
            </ProductTaxDetails>
          </TaxCalculation>
          <PurchaseOrderReference>
            <ID>${xmlEscape(c.PurchaseOrder)}</ID>
            <ItemID>${xmlEscape(c.PurchaseOrderItem)}</ItemID>
          </PurchaseOrderReference>
        </Item>
      </SupplierInvoice>
    </n2:SupplierInvoiceERPCreateRequest_sync>
  </soap:Body>
</soap:Envelope>`;
}

async function postOne(envelope) {
  const url = `${HOST}${SOAP_PATH}?sap-client=${SAP_CLIENT}`;
  const res = await fetch(url, {
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
  const resultMatch = text.match(/<BusinessDocumentProcessingResultCode>(\d+)/);
  const noteMatch = text.match(/<Note>([^<]+)<\/Note>/);
  return {
    status: res.status,
    result: resultMatch?.[1],
    invoiceId: idMatch?.[1],
    fiscalYear: idMatch?.[2],
    note: noteMatch?.[1],
  };
}

const candidates = loadCandidates() || await fetchCandidates();
const doneKeys = loadDoneKeys();
const todo = candidates.filter((c) => !doneKeys.has(`${c.PurchaseOrder}/${c.PurchaseOrderItem}`)).slice(0, TARGET_COUNT);
console.log(`Plan: ${todo.length} POSTs (${doneKeys.size} already done from prior runs)`);

const [year, month] = POSTING_YEAR_MONTH.split('-').map(Number);
const daysInMonth = new Date(year, month, 0).getDate();
let consecFails = 0;
const results = [];
const logFh = fs.openSync(LOG_PATH, 'a');

for (let i = 0; i < todo.length; i++) {
  const c = todo[i];
  const dayOffset = fnv1a(`${c.PurchaseOrder}/${c.PurchaseOrderItem}`) % daysInMonth;
  const date = new Date(Date.UTC(year, month - 1, 1 + dayOffset));
  const dateISO = date.toISOString().slice(0, 10);
  const refId = `INV-${c.PurchaseOrder}-${c.PurchaseOrderItem}`.slice(0, 16);

  const envelope = buildEnvelope(c, dateISO, refId);
  let r;
  try { r = await postOne(envelope); } catch (e) { r = { status: 0, error: e.message }; }
  const ok = r.result === '1' || r.result === '3';
  const summary = ok ? `✓ ${r.invoiceId}/${r.fiscalYear}` : `✗ ${r.note || r.error || 'unknown'}`;
  console.log(`  [${i+1}/${todo.length}] PO ${c.PurchaseOrder}/${c.PurchaseOrderItem} (${c.Supplier}, ${dateISO}) → ${summary}`);

  const logLine = JSON.stringify({ ts: new Date().toISOString(), po: c.PurchaseOrder, item: c.PurchaseOrderItem, supplier: c.Supplier, date: dateISO, refId, ok, invoiceId: r.invoiceId, year: r.fiscalYear, result: r.result, note: r.note, status: r.status });
  fs.writeSync(logFh, logLine + '\n');
  results.push({ ...c, dateISO, refId, ok, invoiceId: r.invoiceId, year: r.fiscalYear, note: r.note });

  if (ok) consecFails = 0; else consecFails++;
  if (consecFails >= 3) {
    console.log('\nHALT — 3 consecutive failures.');
    break;
  }
  await new Promise((r) => setTimeout(r, 200));
}
fs.closeSync(logFh);

const okCount = results.filter((r) => r.ok).length;
fs.writeFileSync(RESULTS_PATH, JSON.stringify({
  ts: new Date().toISOString(),
  attempted: results.length,
  succeeded: okCount,
  failed: results.length - okCount,
  results,
}, null, 2));

console.log(`\nDone: ${okCount} succeeded, ${results.length - okCount} failed.`);
if (okCount) {
  const ids = results.filter((r) => r.ok).map((r) => `${r.invoiceId}/${r.year}`);
  console.log(`Invoice ID range: ${ids[0]} … ${ids[ids.length-1]}`);
}
console.log(`Log: ${LOG_PATH}`);
console.log(`Results: ${RESULTS_PATH}`);
