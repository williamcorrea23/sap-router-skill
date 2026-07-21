#!/usr/bin/env node
// Bulk Goods Receipt creator. Finds eligible PO lines (not yet fully delivered), posts partial-qty GR.
//
// Usage:
//   SAP_HOST=https://<tenant>-api.s4hana.cloud.sap SAP_CLIENT=100 \
//   SAP_USERNAME=<user> SAP_PASSWORD=<pass> \
//   TARGET_COUNT=10 POSTING_YEAR_MONTH=2025-08 \
//   OUT_DIR=/tmp/create-grs \
//   node bulk-gr-poster.mjs
import fs from 'node:fs';
import path from 'node:path';

const HOST = process.env.SAP_HOST;
const SAP_CLIENT = process.env.SAP_CLIENT || '100';
const USER = process.env.SAP_USERNAME;
const PASS = process.env.SAP_PASSWORD;
const TARGET_COUNT = parseInt(process.env.TARGET_COUNT || '10', 10);
const POSTING_YEAR_MONTH = process.env.POSTING_YEAR_MONTH || '2025-08';
const STORAGE_LOCATION = process.env.STORAGE_LOCATION || '101A';
const PARTIAL_FRACTION = parseFloat(process.env.PARTIAL_FRACTION || '0.25');
const OUT_DIR = process.env.OUT_DIR || '/tmp/create-grs';

if (!HOST || !USER || !PASS) { console.error('Missing SAP_HOST/USERNAME/PASSWORD'); process.exit(1); }
fs.mkdirSync(OUT_DIR, { recursive: true });

const GR_SVC = '/sap/opu/odata/sap/API_MATERIAL_DOCUMENT_SRV';
const PO_SVC = '/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV';
const authHeader = 'Basic ' + Buffer.from(`${USER}:${PASS}`).toString('base64');
const LOG = path.join(OUT_DIR, 'create-log.jsonl');

async function getJson(url) { const r = await fetch(url, { headers: { Authorization: authHeader, Accept: 'application/json' } }); return r.json(); }
async function fetchCsrf() {
  const r = await fetch(`${HOST}${GR_SVC}/?sap-client=${SAP_CLIENT}`, { headers: { Authorization: authHeader, 'X-CSRF-Token': 'Fetch', Accept: 'application/json' } });
  return { token: r.headers.get('x-csrf-token'), cookieHeader: (r.headers.getSetCookie?.() ?? []).map(c => c.split(';')[0]).join('; ') };
}
function fnv1a(s) { let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = (h * 0x01000193) >>> 0; } return h; }

// 1. Find eligible PO lines (goods, not yet fully delivered)
console.log('Fetching eligible PO lines...');
const itemsJ = await getJson(`${HOST}${PO_SVC}/A_PurchaseOrderItem?$top=200&$filter=ProductType eq '1' and PurchaseOrderItemCategory eq '0' and IsCompletelyDelivered eq false&$select=PurchaseOrder,PurchaseOrderItem,Material,Plant,OrderQuantity,PurchaseOrderQuantityUnit&$format=json&sap-client=${SAP_CLIENT}`);
const items = itemsJ.d?.results || [];
console.log(`  ${items.length} eligible lines`);

// 2. Load idempotency log
const done = new Set();
if (fs.existsSync(LOG)) {
  for (const line of fs.readFileSync(LOG, 'utf8').split('\n')) { if (!line.trim()) continue; try { const e = JSON.parse(line); if (e.ok) done.add(`${e.po}/${e.item}`); } catch {} }
}
const todo = items.filter(i => !done.has(`${i.PurchaseOrder}/${i.PurchaseOrderItem}`)).slice(0, TARGET_COUNT);
console.log(`Plan: ${todo.length} GRs (${done.size} already done)`);

// 3. Compute posting date
const [year, month] = POSTING_YEAR_MONTH.split('-').map(Number);
const daysInMonth = new Date(year, month, 0).getDate();
const csrf = await fetchCsrf();
let consecFails = 0;
const results = [];
const logFh = fs.openSync(LOG, 'a');

for (let i = 0; i < todo.length; i++) {
  const it = todo[i];
  const dayOffset = fnv1a(`${it.PurchaseOrder}/${it.PurchaseOrderItem}`) % daysInMonth;
  const postingMs = Date.UTC(year, month - 1, 1 + dayOffset);
  const qty = Math.max(1, Math.floor(parseFloat(it.OrderQuantity) * PARTIAL_FRACTION));

  const payload = {
    DocumentDate: `/Date(${postingMs})/`,
    PostingDate: `/Date(${postingMs})/`,
    MaterialDocumentHeaderText: `API GR ${it.PurchaseOrder}`.slice(0, 25),
    GoodsMovementCode: '01',
    to_MaterialDocumentItem: [{
      Material: it.Material,
      Plant: it.Plant,
      StorageLocation: STORAGE_LOCATION,
      GoodsMovementType: '101',
      GoodsMovementRefDocType: 'B',
      PurchaseOrder: it.PurchaseOrder,
      PurchaseOrderItem: it.PurchaseOrderItem,
      QuantityInEntryUnit: String(qty),
      EntryUnit: it.PurchaseOrderQuantityUnit,
    }],
  };

  const r = await fetch(`${HOST}${GR_SVC}/A_MaterialDocumentHeader?sap-client=${SAP_CLIENT}`, {
    method: 'POST',
    headers: { Authorization: authHeader, 'X-CSRF-Token': csrf.token, Cookie: csrf.cookieHeader, 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(payload),
  });
  const t = await r.text(); let b; try { b = JSON.parse(t); } catch { b = { raw: t.slice(0, 200) }; }
  const ok = !!b.d;
  const id = b.d?.MaterialDocument;
  const year2 = b.d?.MaterialDocumentYear;
  const note = !ok ? (b.error?.innererror?.errordetails?.slice(0, 2).map(d => `${d.code}: ${d.message}`).join(' | ') || b.error?.message?.value) : null;
  console.log(`  [${i+1}/${todo.length}] PO ${it.PurchaseOrder}/${it.PurchaseOrderItem} qty ${qty} → ${ok ? `✅ MatDoc ${id}/${year2}` : `❌ ${note}`}`);
  fs.writeSync(logFh, JSON.stringify({ ts: new Date().toISOString(), ok, matDoc: id, year: year2, po: it.PurchaseOrder, item: it.PurchaseOrderItem, qty, note }) + '\n');
  results.push({ po: it.PurchaseOrder, item: it.PurchaseOrderItem, qty, ok, matDoc: id, year: year2 });
  if (ok) consecFails = 0; else consecFails++;
  if (consecFails >= 3) { console.log('\nHALT — 3 consecutive failures.'); break; }
  await new Promise(r => setTimeout(r, 200));
}
fs.closeSync(logFh);

const okCount = results.filter(r => r.ok).length;
fs.writeFileSync(path.join(OUT_DIR, 'results.json'), JSON.stringify({ ts: new Date().toISOString(), attempted: results.length, succeeded: okCount, results }, null, 2));
console.log(`\nDone: ${okCount}/${results.length} GRs created`);
