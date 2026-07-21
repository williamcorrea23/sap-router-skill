# CSRF + POST flow — exact pattern (Node)

SAP OData v2 requires a CSRF token + cookies on every write. Reuse the token across a batch.

The flow is identical for both auth modes — the only thing that changes is the value of the `Authorization` header. Compute it once up-front and pass it as `authHeader` everywhere below:

- **`basic` mode (Cloud TDD):** `'Basic ' + Buffer.from(\`${user}:${pass}\`).toString('base64')`
- **`cc` mode (on-prem Duvo, OAuth client credentials):** `'Bearer ' + accessToken` (see "OAuth token fetch" at bottom)

## Step 1 — Fetch token

```js
async function fetchCsrf(host, sapClient, authHeader, servicePath) {
  // servicePath e.g. '/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV'
  const url = `${host}${servicePath}/?sap-client=${sapClient}`;
  const res = await fetch(url, {
    method: 'GET',
    headers: {
      Authorization: authHeader,
      'X-CSRF-Token': 'Fetch',
      Accept: 'application/json',
    },
  });
  if (res.status !== 200) throw new Error(`CSRF fetch failed: ${res.status}`);
  const token = res.headers.get('x-csrf-token');
  // capture all Set-Cookie values, join into one Cookie header
  const cookies = res.headers.getSetCookie?.() ?? res.headers.raw?.()['set-cookie'] ?? [];
  const cookieHeader = cookies.map((c) => c.split(';')[0]).join('; ');
  return { token, cookieHeader };
}
```

## Step 2 — POST a record

```js
async function postRecord(host, sapClient, authHeader, csrf, servicePath, entitySet, payload) {
  // NOTE: no $format=json on POST URL — SAP rejects it as SystemQueryOption
  const url = `${host}${servicePath}/${entitySet}?sap-client=${sapClient}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: authHeader,
      'X-CSRF-Token': csrf.token,
      Cookie: csrf.cookieHeader,
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(payload),
  });
  const text = await res.text();
  let body;
  try { body = JSON.parse(text); } catch { body = { raw: text }; }
  return { status: res.status, body, headers: res.headers };
}
```

## Step 3 — Handle CSRF expiry

```js
// In the POST loop:
if (result.status === 403 && /csrf token validation failed/i.test(JSON.stringify(result.body))) {
  csrf = await fetchCsrf(host, sapClient, authHeader, servicePath);
  // retry once
  result = await postRecord(...);
}
```

For `cc` (bearer) mode, also handle bearer expiry: a 401 (not 403) means the access token expired — refetch it and retry once. Default token TTL is 3600s; refresh proactively at ~3000s for runs longer than 50min.

## Step 4 — Throttle

```js
await new Promise((r) => setTimeout(r, 200));   // 200ms between POSTs
```

## Halt rule

Track consecutive failures. After 3 in a row, stop and report — don't burn through the batch on a systemic error.

## OAuth token fetch (cc mode, on-prem Duvo)

```js
async function fetchAccessToken(tokenUrl, clientId, clientSecret) {
  const basic = 'Basic ' + Buffer.from(`${clientId}:${clientSecret}`).toString('base64');
  const res = await fetch(tokenUrl, {
    method: 'POST',
    headers: {
      Authorization: basic,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'grant_type=client_credentials',
  });
  if (!res.ok) throw new Error(`Token fetch failed: ${res.status} ${await res.text()}`);
  const { access_token, expires_in } = await res.json();
  return { token: access_token, expiresAt: Date.now() + (expires_in - 60) * 1000 };
}
```

Verified 2026-05-05 against `s4hana.duvo.inovaflow.io`: token + bearer GET + CSRF fetch all work for `API_PURCHASEORDER_PROCESS_SRV`, `API_SUPPLIERINVOICE_PROCESS_SRV`, and `API_INFORECORD_PROCESS_SRV`. Cookies still come back as `sap-XSRF_S4H_<client>` — capture and forward exactly the same way as basic auth.

## .env parsing gotcha

If a value contains `#` and isn't quoted, naive parsers truncate at the comment marker. Use this:

```js
function parseEnvLine(line) {
  const t = line.trim();
  if (!t || t.startsWith('#')) return null;
  const m = t.match(/^([A-Z_][A-Z0-9_]*)\s*=\s*(.*)$/);
  if (!m) return null;
  let v = m[2];
  if (!(v.startsWith('"') || v.startsWith("'"))) {
    const hashIdx = v.indexOf('#');
    if (hashIdx !== -1) v = v.slice(0, hashIdx);
  }
  v = v.trim();
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) v = v.slice(1, -1);
  return [m[1], v];
}
```
