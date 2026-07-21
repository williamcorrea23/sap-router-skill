#!/usr/bin/env node
// Bulk PIR creator via API_INFORECORD_PROCESS_SRV.
// Pairs eligible (supplier, material) deterministically; one PIR per pair.
//
// Usage:
//   SAP_HOST=... SAP_CLIENT=100 SAP_USERNAME=... SAP_PASSWORD=... \
//   TARGET_COUNT=20 PURCH_ORG=1010 PLANT=1010 \
//   OUT_DIR=/tmp/create-pirs \
//   node bulk-pir-poster.mjs
import fs from 'node:fs';
import path from 'node:path';

const HOST = process.env.SAP_HOST;
const SAP_CLIENT = process.env.SAP_CLIENT || '100';
const USER = process.env.SAP_USERNAME;
const PASS = process.env.SAP_PASSWORD;
const TARGET_COUNT = parseInt(process.env.TARGET_COUNT || '10', 10);
const PURCH_ORG = process.env.PURCH_ORG || '1010';
const PLANT = process.env.PLANT || '1010';
const PURCH_GROUP = process.env.PURCH_GROUP || '001';
const CURRENCY = process.env.CURRENCY || 'EUR';
const OUT_DIR = process.env.OUT_DIR || '/tmp/create-pirs';

if (!HOST || !USER || !PASS) { console.error('Missing SAP_HOST/USERNAME/PASSWORD'); process.exit(1); }
fs.mkdirSync(OUT_DIR, { recursive: true });

const PIR_SVC = '/sap/opu/odata/sap/API_INFORECORD_PROCESS_SRV';
const authHeader = 'Basic ' + Buffer.from(`${USER}:${PASS}`).toString('base64');
const LOG = path.join(OUT_DIR, 'create-log.jsonl');

async function getJson(url) { const r = await fetch(url, { headers: { Authorization: authHeader, Accept: 'application/json' } }); return r.json(); }
async function fetchCsrf() {
  const r = await fetch(`${HOST}${PIR_SVC}/?sap-client=${SAP_CLIENT}`, { headers: { Authorization: authHeader, 'X-CSRF-Token': 'Fetch', Accept: 'application/json' } });
  return { token: r.headers.get('x-csrf-token'), cookieHeader: (r.headers.getSetCookie?.() ?? []).map(c => c.split(';')[0]).join('; ') };
}
function fnv1a(s) { let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = (h * 0x01000193) >>> 0; } return h; }

// 1. Pull eligible materials (ProcurementType=F at target plant)
console.log(`Fetching eligible materials at plant ${PLANT}...`);
const matJ = await getJson(`${HOST}/sap/opu/odata/sap/API_PRODUCT_SRV/A_ProductPlant?$filter=Plant eq '${PLANT}' and ProcurementType eq 'F'&$top=500&$select=Product,Plant&$format=json&sap-client=${SAP_CLIENT}`);
const materials = matJ.d?.results || [];
console.log(`  ${materials.length} eligible materials`);

// 2. Get BaseUnit for each material (batch via $filter or individual)
const matMeta = {};
for (const m of materials) {
  const pj = await getJson(`${HOST}/sap/opu/odata/sap/API_PRODUCT_SRV/A_Product('${m.Product}')?$select=Product,BaseUnit&$format=json&sap-client=${SAP_CLIENT}`);
  matMeta[m.Product] = pj.d?.BaseUnit || 'PC';
}

// 3. Pull suppliers with PurchOrg setup
console.log(`Fetching suppliers on PurchOrg ${PURCH_ORG}...`);
const supJ = await getJson(`${HOST}/sap/opu/odata/sap/API_BUSINESS_PARTNER/A_SupplierPurchasingOrg?$filter=PurchasingOrganization eq '${PURCH_ORG}'&$top=500&$select=Supplier,PurchasingOrganization,PurchaseOrderCurrency&$format=json&sap-client=${SAP_CLIENT}`);
const suppliers = (supJ.d?.results || []).filter(s => s.PurchaseOrderCurrency === CURRENCY);
console.log(`  ${suppliers.length} eligible suppliers`);

// 4. Load idempotency log
const done = new Set();
if (fs.existsSync(LOG)) {
  for (const line of fs.readFileSync(LOG, 'utf8').split('\n')) { if (!line.trim()) continue; try { const e = JSON.parse(line); if (e.ok) done.add(`${e.supplier}/${e.material}`); } catch {} }
}

// 5. Pair deterministically and pick first TARGET_COUNT not-yet-done
const pairs = [];
for (const m of materials) for (const s of suppliers) pairs.push({ supplier: s.Supplier, material: m.Product, baseUnit: matMeta[m.Product] });
pairs.sort((a, b) => fnv1a(`${a.supplier}/${a.material}`) - fnv1a(`${b.supplier}/${b.material}`));
const todo = pairs.filter(p => !done.has(`${p.supplier}/${p.material}`)).slice(0, TARGET_COUNT);
console.log(`Plan: ${todo.length} POSTs (${done.size} already done)`);

const csrf = await fetchCsrf();
let consecFails = 0;
const results = [];
const logFh = fs.openSync(LOG, 'a');

for (let i = 0; i < todo.length; i++) {
  const p = todo[i];
  const price = (10 + (fnv1a(`${p.supplier}/${p.material}/price`) % 990)).toFixed(2);
  const payload = {
    Supplier: p.supplier, Material: p.material, BaseUnit: p.baseUnit, PurgDocOrderQuantityUnit: p.baseUnit,
    to_PurgInfoRecdOrgPlantData: [{
      PurchasingOrganization: PURCH_ORG, Plant: PLANT, PurchasingInfoRecordCategory: '0',
      PurchasingGroup: PURCH_GROUP, Currency: CURRENCY,
      NetPriceAmount: price, MinimumPurchaseOrderQuantity: '1', StandardPurchaseOrderQuantity: '10',
      MaterialPlannedDeliveryDurn: '7',
    }],
  };
  const r = await fetch(`${HOST}${PIR_SVC}/A_PurchasingInfoRecord?sap-client=${SAP_CLIENT}`, {
    method: 'POST',
    headers: { Authorization: authHeader, 'X-CSRF-Token': csrf.token, Cookie: csrf.cookieHeader, 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(payload),
  });
  const t = await r.text(); let b; try { b = JSON.parse(t); } catch { b = { raw: t.slice(0, 200) }; }
  const ok = !!b.d;
  const id = b.d?.PurchasingInfoRecord;
  const note = !ok && b.error?.innererror?.errordetails?.[0] ? `${b.error.innererror.errordetails[0].code}: ${b.error.innererror.errordetails[0].message}` : b.error?.message?.value;
  console.log(`  [${i+1}/${todo.length}] ${p.supplier}/${p.material} → ${ok ? `✅ PIR ${id}` : `❌ ${note}`}`);
  fs.writeSync(logFh, JSON.stringify({ ts: new Date().toISOString(), ok, pir: id, supplier: p.supplier, material: p.material, price, note }) + '\n');
  results.push({ supplier: p.supplier, material: p.material, ok, pir: id });
  if (ok) consecFails = 0; else consecFails++;
  if (consecFails >= 3) { console.log('\nHALT — 3 consecutive failures.'); break; }
  await new Promise(r => setTimeout(r, 200));
}
fs.closeSync(logFh);

const okCount = results.filter(r => r.ok).length;
fs.writeFileSync(path.join(OUT_DIR, 'results.json'), JSON.stringify({ ts: new Date().toISOString(), attempted: results.length, succeeded: okCount, results }, null, 2));
console.log(`\nDone: ${okCount}/${results.length} PIRs created`);
