// bulk-product-poster.mjs — reference implementation for s4hana-create-product
// Usage: node bulk-product-poster.mjs <count> [<type-mix>]
//   count: number of products to create (default 5)
//   type-mix: comma-separated ProductTypes (default: HAWA,FERT,SERV)
// Reads .env from CWD. Writes log + results to ./.s4hana-tmp/create-products-<ts>/

import 'dotenv/config';
import fs from 'node:fs/promises';
import path from 'node:path';

const HOST = process.env.SAP_HOST;
const CLIENT = process.env.SAP_CLIENT ?? '100';
const AUTH_MODE = process.env.SAP_AUTH_MODE ?? 'basic';
if (!HOST) { console.error('SAP_HOST not set in .env'); process.exit(1); }

const argCount = Number(process.argv[2] ?? 5);
const argTypes = (process.argv[3] ?? 'HAWA,FERT,SERV').split(',').map(s => s.trim().toUpperCase());

// --- auth ---
async function getAuthHeader() {
  if (AUTH_MODE === 'basic') {
    return 'Basic ' + Buffer.from(`${process.env.SAP_USERNAME}:${process.env.SAP_PASSWORD}`).toString('base64');
  }
  if (AUTH_MODE === 'cc') {
    const tokRes = await fetch(process.env.SAP_TOKEN_URL, {
      method: 'POST',
      headers: {
        Authorization: 'Basic ' + Buffer.from(`${process.env.SAP_CLIENT_ID}:${process.env.SAP_CLIENT_SECRET}`).toString('base64'),
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: 'grant_type=client_credentials',
    });
    const { access_token } = await tokRes.json();
    return 'Bearer ' + access_token;
  }
  throw new Error(`Auth mode ${AUTH_MODE} not yet wired in this script`);
}
const auth = await getAuthHeader();

// --- workspace ---
const ts = new Date().toISOString().slice(0, 16).replace(/[T:-]/g, '').slice(0, 13);
const workDir = path.join(process.cwd(), '.s4hana-tmp', `create-products-${ts}`);
await fs.mkdir(workDir, { recursive: true });
const logPath = path.join(workDir, 'create-log.jsonl');

const base = `${HOST}/sap/opu/odata4/sap/api_product/srvd_a2x/sap/product/0002`;
const sapClientParam = `sap-client=${CLIENT}`;

// --- Phase 2: discover tenant unit + group pools per ProductType ---
const discovery = {};
for (const type of argTypes) {
  const r = await fetch(`${base}/Product?$filter=ProductType eq '${type}'&$top=10&$select=BaseUnit,ProductGroup,IndustrySector&${sapClientParam}`, {
    headers: { Authorization: auth, Accept: 'application/json' },
  });
  const j = await r.json();
  const rows = j.value ?? [];
  const units = [...new Set(rows.map(r => r.BaseUnit))].filter(Boolean);
  const groups = [...new Set(rows.map(r => r.ProductGroup))].filter(Boolean);
  const sectors = [...new Set(rows.map(r => r.IndustrySector))].filter(Boolean);
  discovery[type] = {
    baseUnits: units.length ? units : (type === 'SERV' ? ['LE'] : ['ST']),
    productGroups: groups.length ? groups : ['A001'],
    industrySector: sectors[0] ?? 'M',
  };
}
await fs.writeFile(path.join(workDir, 'tenant-discovery.json'), JSON.stringify(discovery, null, 2));
console.error('Discovery:', JSON.stringify(discovery, null, 2));

// --- Phase 4: CSRF ---
let csrf, cookie;
async function refreshCsrf() {
  const r = await fetch(`${base}/?${sapClientParam}`, {
    headers: { Authorization: auth, Accept: 'application/json', 'X-CSRF-Token': 'Fetch' },
  });
  csrf = r.headers.get('x-csrf-token');
  cookie = r.headers.getSetCookie?.()?.join('; ') ?? r.headers.get('set-cookie');
}
await refreshCsrf();

// --- generate IDs + payloads ---
const seed = Date.now().toString().slice(-4);
const records = [];
for (let i = 0; i < argCount; i++) {
  const type = argTypes[i % argTypes.length];
  const conf = discovery[type];
  const prefix = type[0];
  const id = `${prefix}${seed}${i + 1}`;
  records.push({
    id, type,
    payload: {
      Product: id,
      ProductType: type,
      BaseUnit: conf.baseUnits[i % conf.baseUnits.length],
      ProductGroup: conf.productGroups[i % conf.productGroups.length],
      IndustrySector: conf.industrySector,
      _ProductDescription: [
        { Product: id, Language: 'EN', ProductDescription: `Auto-created ${type} #${i + 1}` },
      ],
    },
  });
}
await fs.writeFile(path.join(workDir, 'payloads.json'), JSON.stringify(records, null, 2));

// --- POST loop ---
let consecutiveFails = 0;
const results = [];
for (const r of records) {
  if (consecutiveFails >= 3) { console.error('Halt: 3 consecutive failures'); break; }
  let attemptCsrfRetry = false;
  while (true) {
    const pr = await fetch(`${base}/Product?${sapClientParam}`, {
      method: 'POST',
      headers: {
        Authorization: auth, 'Content-Type': 'application/json', Accept: 'application/json',
        'X-CSRF-Token': csrf, Cookie: cookie,
      },
      body: JSON.stringify(r.payload),
    });
    if (pr.status === 403 && !attemptCsrfRetry) {
      attemptCsrfRetry = true;
      await refreshCsrf();
      continue;
    }
    const t = await pr.text();
    const ok = pr.status === 201;
    if (ok) consecutiveFails = 0; else consecutiveFails++;
    const errMsg = ok ? null : (t.match(/"message":"([^"]+)"/)?.[1] ?? t.slice(0, 300));
    const entry = { ok, productID: r.id, productType: r.type, status: pr.status, ts: new Date().toISOString(), errMsg };
    await fs.appendFile(logPath, JSON.stringify(entry) + '\n');
    results.push(entry);
    console.error(`${ok ? '✓' : '✗'} ${r.id} (${r.type}) -> ${pr.status}${errMsg ? '  ' + errMsg : ''}`);
    break;
  }
  await new Promise(rr => setTimeout(rr, 200));
}

await fs.writeFile(path.join(workDir, 'results.json'), JSON.stringify({
  total: records.length, created: results.filter(r => r.ok).length,
  failed: results.filter(r => !r.ok).length, results,
}, null, 2));

// --- verify sample ---
const sample = results.filter(r => r.ok).slice(0, 3);
const verify = [];
for (const s of sample) {
  const vr = await fetch(`${base}/Product('${s.productID}')?$expand=_ProductDescription&${sapClientParam}`, {
    headers: { Authorization: auth, Accept: 'application/json' },
  });
  verify.push({ id: s.productID, status: vr.status, body: await vr.json() });
}
await fs.writeFile(path.join(workDir, 'verify-sample.json'), JSON.stringify(verify, null, 2));

console.error(`\n=== Summary ===`);
console.error(`Workspace: ${workDir}`);
console.error(`Created: ${results.filter(r => r.ok).length}/${records.length}`);
console.error(`IDs: ${results.filter(r => r.ok).map(r => r.productID).join(', ')}`);
