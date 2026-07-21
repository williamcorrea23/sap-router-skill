#!/usr/bin/env node
// Generic GET-PATCH-GET helper for any S/4HANA entity. Always verifies the change actually took effect.
//
// Usage (single):
//   SAP_HOST=https://<tenant>-api.s4hana.cloud.sap SAP_CLIENT=100 \
//   SAP_USERNAME=<user> SAP_PASSWORD=<pass> \
//   SERVICE=/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV \
//   ENTITY_KEY="A_PurchaseOrder('4500000020')" \
//   FIELDS_JSON='{"PurchaseOrderDate":"/Date(1755216000000)/"}' \
//   node safe-update.mjs
//
// Usage (batch from JSON file):
//   BATCH_FILE=/path/to/updates.json node safe-update.mjs
//   # updates.json: [{ service, entityKey, fields, select? }, ...]
import fs from 'node:fs';
import path from 'node:path';

const HOST = process.env.SAP_HOST;
const SAP_CLIENT = process.env.SAP_CLIENT || '100';
const USER = process.env.SAP_USERNAME;
const PASS = process.env.SAP_PASSWORD;
const DRY_RUN = process.env.DRY_RUN === 'true';
const OUT_DIR = process.env.OUT_DIR || '/tmp/update-record';

if (!HOST || !USER || !PASS) { console.error('Missing SAP_HOST/USERNAME/PASSWORD'); process.exit(1); }
fs.mkdirSync(OUT_DIR, { recursive: true });

const authHeader = 'Basic ' + Buffer.from(`${USER}:${PASS}`).toString('base64');

async function getJson(url) {
  const r = await fetch(url, { headers: { Authorization: authHeader, Accept: 'application/json' } });
  if (!r.ok) throw new Error(`GET failed: ${r.status} ${await r.text()}`);
  return r.json();
}

async function fetchCsrf(service) {
  const r = await fetch(`${HOST}${service}/?sap-client=${SAP_CLIENT}`, { headers: { Authorization: authHeader, 'X-CSRF-Token': 'Fetch', Accept: 'application/json' } });
  return { token: r.headers.get('x-csrf-token'), cookieHeader: (r.headers.getSetCookie?.() ?? []).map(c => c.split(';')[0]).join('; ') };
}

async function patchOne(service, entityKey, fields) {
  const csrf = await fetchCsrf(service);
  const r = await fetch(`${HOST}${service}/${entityKey}?sap-client=${SAP_CLIENT}`, {
    method: 'PATCH',
    headers: { Authorization: authHeader, 'X-CSRF-Token': csrf.token, Cookie: csrf.cookieHeader, 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(fields),
  });
  const text = await r.text();
  let body; try { body = JSON.parse(text); } catch { body = { raw: text.slice(0, 300) }; }
  return { status: r.status, body };
}

/**
 * Update one record with GET-PATCH-GET verification.
 * Returns { ok, before, after, silentFailures, errors }
 */
async function safeUpdate({ service, entityKey, fields, selectFields }) {
  const fieldNames = Object.keys(fields);
  const selectClause = selectFields || fieldNames.join(',');

  // 1. GET before
  const beforeUrl = `${HOST}${service}/${entityKey}?$select=${selectClause}&$format=json&sap-client=${SAP_CLIENT}`;
  const beforeJ = await getJson(beforeUrl);
  const before = beforeJ.d ? Object.fromEntries(fieldNames.map(f => [f, beforeJ.d[f]])) : {};

  if (DRY_RUN) {
    return { ok: false, dryRun: true, before, planned: fields };
  }

  // 2. PATCH
  const r = await patchOne(service, entityKey, fields);
  if (r.status >= 400) {
    const details = r.body?.error?.innererror?.errordetails?.slice(0, 3).map(d => `${d.code}: ${d.message}`).join(' | ')
      || r.body?.error?.message?.value || JSON.stringify(r.body).slice(0, 200);
    return { ok: false, status: r.status, before, error: details };
  }

  // 3. GET after
  await new Promise(res => setTimeout(res, 300));
  const afterJ = await getJson(beforeUrl);
  const after = afterJ.d ? Object.fromEntries(fieldNames.map(f => [f, afterJ.d[f]])) : {};

  // 4. Diff
  const silentFailures = [];
  for (const f of fieldNames) {
    if (String(before[f]) === String(after[f]) && String(before[f]) !== String(fields[f])) {
      silentFailures.push({ field: f, before: before[f], requested: fields[f], after: after[f] });
    }
  }

  return {
    ok: silentFailures.length === 0,
    status: r.status,
    before,
    after,
    silentFailures,
  };
}

// Main
const items = process.env.BATCH_FILE
  ? JSON.parse(fs.readFileSync(process.env.BATCH_FILE, 'utf8'))
  : [{ service: process.env.SERVICE, entityKey: process.env.ENTITY_KEY, fields: JSON.parse(process.env.FIELDS_JSON || '{}'), selectFields: process.env.SELECT_FIELDS }];

console.log(`Plan: ${items.length} update(s)${DRY_RUN ? ' [DRY RUN]' : ''}`);
const logFh = fs.openSync(path.join(OUT_DIR, 'update-log.jsonl'), 'a');
const results = [];

for (let i = 0; i < items.length; i++) {
  const item = items[i];
  console.log(`\n[${i+1}/${items.length}] ${item.entityKey}`);
  console.log(`  Fields: ${JSON.stringify(item.fields)}`);
  let r;
  try { r = await safeUpdate(item); } catch (e) { r = { ok: false, error: e.message }; }
  console.log(`  Before: ${JSON.stringify(r.before)}`);
  if (r.dryRun) {
    console.log(`  Planned: ${JSON.stringify(r.planned)}`);
  } else if (r.error) {
    console.log(`  ❌ ${r.status || 'ERROR'}: ${r.error}`);
  } else {
    console.log(`  After:  ${JSON.stringify(r.after)}`);
    if (r.silentFailures?.length) {
      console.log(`  ⚠️  ${r.silentFailures.length} silent failure(s) (returned 204 but field unchanged):`);
      for (const sf of r.silentFailures) console.log(`     ${sf.field}: ${sf.before} → still ${sf.after} (requested ${sf.requested})`);
    } else {
      console.log(`  ✅ Verified change`);
    }
  }
  fs.writeSync(logFh, JSON.stringify({ ts: new Date().toISOString(), ...item, ...r }) + '\n');
  results.push({ entityKey: item.entityKey, ok: r.ok, before: r.before, after: r.after, silentFailures: r.silentFailures, error: r.error });
  await new Promise(r => setTimeout(r, 200));
}
fs.closeSync(logFh);

const okCount = results.filter(r => r.ok).length;
const silentCount = results.filter(r => r.silentFailures?.length).length;
fs.writeFileSync(path.join(OUT_DIR, 'results.json'), JSON.stringify({ ts: new Date().toISOString(), attempted: results.length, verified: okCount, silentFailures: silentCount, results }, null, 2));
console.log(`\nDone: ${okCount}/${results.length} verified changes, ${silentCount} silent failures.`);
