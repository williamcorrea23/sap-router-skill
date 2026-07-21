#!/usr/bin/env node
// Bulk PO Confirmation poster with PATCH-then-POST flow.
// Step 1: PATCH eligible PO lines with SupplierConfirmationControlKey if empty.
// Step 2: POST SOAP confirmation with WS-Addressing headers.
//
// Usage:
//   SAP_HOST=https://<tenant>-api.s4hana.cloud.sap SAP_CLIENT=100 \
//   SAP_USERNAME=<user> SAP_PASSWORD=<pass> \
//   TARGET_COUNT=10 \
//   OUT_DIR=/tmp/create-po-confirmations \
//   node bulk-poc-poster.mjs
import fs from 'node:fs';
import path from 'node:path';

const HOST = process.env.SAP_HOST;
const SAP_CLIENT = process.env.SAP_CLIENT || '100';
const USER = process.env.SAP_USERNAME;
const PASS = process.env.SAP_PASSWORD;
const TARGET_COUNT = parseInt(process.env.TARGET_COUNT || '10', 10);
const CCK_VALUE = process.env.CCK_VALUE || '0001';
const OUT_DIR = process.env.OUT_DIR || '/tmp/create-po-confirmations';

if (!HOST || !USER || !PASS) { console.error('Missing SAP_HOST/USERNAME/PASSWORD'); process.exit(1); }
fs.mkdirSync(OUT_DIR, { recursive: true });

const PO_SVC = '/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV';
const SOAP_PATH = '/sap/bc/srt/scs_ext/sap/supplierconfirmationrequest_i1';
const SOAP_ACTION = 'http://sap.com/xi/Procurement/SupplierConfirmationRequest_In/SupplierConfirmationRequest_InRequest';
const authHeader = 'Basic ' + Buffer.from(`${USER}:${PASS}`).toString('base64');
const LOG = path.join(OUT_DIR, 'create-log.jsonl');
const CCK_LOG = path.join(OUT_DIR, 'cck-patches.jsonl');

async function getJson(url) { const r = await fetch(url, { headers: { Authorization: authHeader, Accept: 'application/json' } }); return r.json(); }
async function fetchCsrf() {
  const r = await fetch(`${HOST}${PO_SVC}/?sap-client=${SAP_CLIENT}`, { headers: { Authorization: authHeader, 'X-CSRF-Token': 'Fetch', Accept: 'application/json' } });
  return { token: r.headers.get('x-csrf-token'), cookieHeader: (r.headers.getSetCookie?.() ?? []).map(c => c.split(';')[0]).join('; ') };
}
function uuid() {
  return 'urn:uuid:' + Array.from({length: 32}, () => Math.floor(Math.random()*16).toString(16)).join('').replace(/(.{8})(.{4})(.{4})(.{4})(.{12})/, '$1-$2-$3-$4-$5');
}
function fnv1a(s) { let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = (h * 0x01000193) >>> 0; } return h; }
function isoUnit(sapUnit) { return { PC: 'PCE', AU: 'AU', KG: 'KGM', H: 'HUR' }[sapUnit] || sapUnit; }

// 1. Eligible PO lines
console.log('Fetching eligible PO lines...');
const itemsJ = await getJson(`${HOST}${PO_SVC}/A_PurchaseOrderItem?$top=200&$filter=PurchaseOrderItemCategory eq '0' and IsCompletelyDelivered eq false&$select=PurchaseOrder,PurchaseOrderItem,Material,Plant,OrderQuantity,PurchaseOrderQuantityUnit,SupplierConfirmationControlKey&$format=json&sap-client=${SAP_CLIENT}`);
const items = itemsJ.d?.results || [];
console.log(`  ${items.length} eligible lines`);

// 2. Load idempotency log
const done = new Set();
if (fs.existsSync(LOG)) {
  for (const line of fs.readFileSync(LOG, 'utf8').split('\n')) { if (!line.trim()) continue; try { const e = JSON.parse(line); if (e.ok) done.add(`${e.po}/${e.item}`); } catch {} }
}
const todo = items.filter(i => !done.has(`${i.PurchaseOrder}/${i.PurchaseOrderItem}`)).slice(0, TARGET_COUNT);
console.log(`Plan: ${todo.length} confirmations (${done.size} already done)`);

// 3. PATCH SupplierConfirmationControlKey on lines that don't have it
const csrf = await fetchCsrf();
const cckFh = fs.openSync(CCK_LOG, 'a');
for (const it of todo) {
  if (it.SupplierConfirmationControlKey && it.SupplierConfirmationControlKey.trim() !== '') continue;
  const url = `${HOST}${PO_SVC}/A_PurchaseOrderItem(PurchaseOrder='${it.PurchaseOrder}',PurchaseOrderItem='${it.PurchaseOrderItem}')?sap-client=${SAP_CLIENT}`;
  const r = await fetch(url, {
    method: 'PATCH',
    headers: { Authorization: authHeader, 'X-CSRF-Token': csrf.token, Cookie: csrf.cookieHeader, 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ SupplierConfirmationControlKey: CCK_VALUE }),
  });
  const ok = r.status === 204 || r.status === 200;
  console.log(`  CCK PATCH ${it.PurchaseOrder}/${it.PurchaseOrderItem} → ${r.status} ${ok ? '✓' : '✗'}`);
  fs.writeSync(cckFh, JSON.stringify({ ts: new Date().toISOString(), po: it.PurchaseOrder, item: it.PurchaseOrderItem, status: r.status, ok }) + '\n');
  await new Promise(r => setTimeout(r, 100));
}
fs.closeSync(cckFh);

// Small delay so CCK PATCHes propagate before confirmations
await new Promise(r => setTimeout(r, 2000));

// 4. POST SOAP confirmations
console.log('\nPosting confirmations...');
let consecFails = 0;
const results = [];
const logFh = fs.openSync(LOG, 'a');

for (let i = 0; i < todo.length; i++) {
  const it = todo[i];
  // Deterministic delivery date offset (0-30 days from today)
  const dayOffset = fnv1a(`${it.PurchaseOrder}/${it.PurchaseOrderItem}`) % 30;
  const deliveryDate = new Date(Date.now() + dayOffset * 86400000).toISOString().slice(0, 10);
  const qty = Math.max(1, Math.floor(parseFloat(it.OrderQuantity) * 0.5));
  const unit = isoUnit(it.PurchaseOrderQuantityUnit);
  const externalRef = `API-CONF-${it.PurchaseOrder}-${it.PurchaseOrderItem}`.slice(0, 35);

  const envelope = `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://www.w3.org/2005/08/addressing" xmlns:n0="http://sap.com/xi/Procurement">
<soap:Header>
<wsa:Action soap:mustUnderstand="1">${SOAP_ACTION}</wsa:Action>
<wsa:To soap:mustUnderstand="1">${HOST}${SOAP_PATH}</wsa:To>
<wsa:MessageID>${uuid()}</wsa:MessageID>
<wsa:ReplyTo><wsa:Address>http://www.w3.org/2005/08/addressing/anonymous</wsa:Address></wsa:ReplyTo>
</soap:Header>
<soap:Body>
<n0:SupplierConfirmationRequest>
<MessageHeader><CreationDateTime>${new Date().toISOString()}</CreationDateTime></MessageHeader>
<SupplierConfirmation>
<ActionCode>01</ActionCode>
<SuplrConfExternalReference>${externalRef}</SuplrConfExternalReference>
<PurchaseOrderID>${it.PurchaseOrder}</PurchaseOrderID>
<SupplierConfirmationItem>
<PurchaseOrderItemID>${it.PurchaseOrderItem}</PurchaseOrderItemID>
<SupplierConfirmationLine>
<ConfirmedDeliveryDate>${deliveryDate}</ConfirmedDeliveryDate>
<ConfirmedQuantity unitCode="${unit}">${qty}</ConfirmedQuantity>
</SupplierConfirmationLine>
</SupplierConfirmationItem>
</SupplierConfirmation>
</n0:SupplierConfirmationRequest>
</soap:Body>
</soap:Envelope>`;

  const r = await fetch(`${HOST}${SOAP_PATH}?sap-client=${SAP_CLIENT}`, {
    method: 'POST',
    headers: { Authorization: authHeader, 'Content-Type': 'text/xml; charset=utf-8', SOAPAction: `"${SOAP_ACTION}"`, Accept: 'text/xml' },
    body: envelope,
  });
  const t = await r.text();
  const ok = r.status === 202;
  const fault = !ok ? (t.match(/<faultstring[^>]*>([^<]+)<\/faultstring>/)?.[1] || t.slice(0, 200)) : null;
  console.log(`  [${i+1}/${todo.length}] ${it.PurchaseOrder}/${it.PurchaseOrderItem} (${qty} ${unit} on ${deliveryDate}) → ${ok ? '✅ 202 accepted' : `❌ ${r.status} ${fault}`}`);
  fs.writeSync(logFh, JSON.stringify({ ts: new Date().toISOString(), ok, po: it.PurchaseOrder, item: it.PurchaseOrderItem, qty, unit, deliveryDate, externalRef, status: r.status, fault }) + '\n');
  results.push({ po: it.PurchaseOrder, item: it.PurchaseOrderItem, qty, deliveryDate, ok });
  if (ok) consecFails = 0; else consecFails++;
  if (consecFails >= 3) { console.log('\nHALT — 3 consecutive non-202 responses.'); break; }
  await new Promise(r => setTimeout(r, 200));
}
fs.closeSync(logFh);

const okCount = results.filter(r => r.ok).length;
fs.writeFileSync(path.join(OUT_DIR, 'results.json'), JSON.stringify({ ts: new Date().toISOString(), attempted: results.length, accepted: okCount, results }, null, 2));

// Print verify checklist
const verifyMd = ['# Verify checklist', '', 'After bulk run, spot-check these in Fiori "Manage Purchase Orders" → item → Supplier Confirmation tab:', '', ...results.filter(r => r.ok).map(r => `- [ ] PO ${r.po} / item ${r.item} — expect confirmation qty ${r.qty}, delivery date ${r.deliveryDate}`)].join('\n');
fs.writeFileSync(path.join(OUT_DIR, 'verify-checklist.md'), verifyMd);

console.log(`\nDone: ${okCount}/${results.length} accepted (202).`);
console.log(`⚠️  HTTP 202 = async accepted, NOT committed. Spot-check in Fiori per ${OUT_DIR}/verify-checklist.md`);
