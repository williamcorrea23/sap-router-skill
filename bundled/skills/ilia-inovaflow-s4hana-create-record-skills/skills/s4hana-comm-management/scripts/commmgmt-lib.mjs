// Helper library for SAP S/4HANA Cloud Communication Management (SAP_COM_0A48, OData V4 A2X).
// .env-driven, CSRF-aware. Cloud Public + basic auth (the comm user must be the inbound user
// of a SAP_COM_0A48 arrangement). Import this from a short run script; never hardcode a tenant.
//
//   import { BASES, apiGet, csrf, apiPost, apiPatch, genSecret, logResult } from './commmgmt-lib.mjs';
//
import { readFileSync } from 'node:fs';
import { randomBytes } from 'node:crypto';

// ---- .env parsing (tolerant of quotes / trailing comments; pins the FIRST SAP_HOST/-style key) ----
function loadEnv(path = '.env') {
  const out = {};
  let raw = '';
  try { raw = readFileSync(path, 'utf8'); } catch { /* fall back to process.env */ }
  for (const line of raw.split('\n')) {
    const m = line.match(/^\s*([A-Z_]+)\s*=\s*(.*?)\s*$/);
    if (!m || out[m[1]] !== undefined) continue;          // first-wins (avoid dup SAP_HOST trap)
    let v = m[2];
    const q = v.match(/^"([^"]*)"/);                       // exact quoted content
    out[m[1]] = q ? q[1] : v.replace(/\s+#.*$/, '').trim();
  }
  for (const k of ['SAP_HOST', 'SAP_CLIENT', 'SAP_USERNAME', 'SAP_PASSWORD'])
    if (out[k] === undefined && process.env[k] !== undefined) out[k] = process.env[k];
  return out;
}

const env = loadEnv();
export const HOST = (env.SAP_HOST || '').replace(/\/+$/, '');
export const CLIENT = env.SAP_CLIENT || '100';
if (!HOST || !env.SAP_USERNAME || !env.SAP_PASSWORD)
  throw new Error('Missing SAP_HOST / SAP_USERNAME / SAP_PASSWORD (Cloud Public basic auth required for SAP_COM_0A48).');
export const AUTH = 'Basic ' + Buffer.from(`${env.SAP_USERNAME}:${env.SAP_PASSWORD}`).toString('base64');

export const BASES = {
  CU: '/sap/opu/odata4/sap/aps_com_cu_a4c_odata/srvd_a2x/sap/aps_com_cu_a4c_odata/0001',
  CS: '/sap/opu/odata4/sap/aps_com_cs_a4c_odata/srvd_a2x/sap/aps_com_cs_a4c_odata/0001',
  CA: '/sap/opu/odata4/sap/aps_com_ca_a4c_odata/srvd_a2x/sap/aps_com_ca_a4c_odata/0001',
};

function url(path) { return HOST + path + (path.includes('?') ? '&' : '?') + 'sap-client=' + CLIENT; }
function parse(t) { try { return JSON.parse(t); } catch { return t; } }

export async function apiGet(path) {
  const r = await fetch(url(path), { headers: { Authorization: AUTH, Accept: 'application/json' } });
  const raw = await r.text();
  return { status: r.status, body: parse(raw), raw };
}

// CSRF token + session cookies from a service root (pass BASES.CU/CS/CA)
export async function csrf(base) {
  const r = await fetch(url(base + '/'), {
    headers: { Authorization: AUTH, Accept: 'application/json', 'X-CSRF-Token': 'Fetch' },
  });
  return {
    token: r.headers.get('x-csrf-token'),
    cookies: (r.headers.getSetCookie?.() || []).map(c => c.split(';')[0]).join('; '),
  };
}

async function write(method, base, pathAfterBase, payload, sess) {
  const r = await fetch(url(base + pathAfterBase), {
    method,
    headers: {
      Authorization: AUTH, Accept: 'application/json', 'Content-Type': 'application/json',
      'X-CSRF-Token': sess.token, Cookie: sess.cookies,
    },
    body: JSON.stringify(payload),
  });
  const raw = await r.text();
  return { status: r.status, body: parse(raw), raw };
}
export const apiPost = (base, collection, payload, sess) => write('POST', base, '/' + collection, payload, sess);
export const apiPatch = (base, keyPath, payload, sess) => write('PATCH', base, '/' + keyPath, payload, sess);

// Strong secret: 24 chars, guaranteed upper/lower/digit/special, OAuth-secret-friendly alphabet.
export function genSecret() {
  const U = 'ABCDEFGHJKLMNPQRSTUVWXYZ', L = 'abcdefghijkmnpqrstuvwxyz', D = '23456789', S = '-_.!*+';
  const pick = set => set[randomBytes(1)[0] % set.length];
  const out = [pick(U), pick(L), pick(D), pick(S)];
  while (out.length < 24) out.push(pick(U + L + D + S));
  for (let i = out.length - 1; i > 0; i--) { const j = randomBytes(1)[0] % (i + 1); [out[i], out[j]] = [out[j], out[i]]; }
  return out.join('');
}

export function logResult(label, r) {
  const ok = r.status >= 200 && r.status < 300;
  console.log(`${ok ? '✓' : '✗'} ${label} -> HTTP ${r.status}`);
  if (!ok) console.log('   ', typeof r.body === 'object' ? JSON.stringify(r.body?.error?.message ?? r.body) : r.raw.slice(0, 300));
  return ok;
}
