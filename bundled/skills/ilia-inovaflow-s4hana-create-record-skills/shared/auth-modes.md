# Auth modes for SAP S/4HANA — basic / cc / oauth

Pick **one** mode up-front for the whole run, confirmed with the user. All three modes use the same skill phases — only the `Authorization` header differs.

## Mode A — `basic` (Cloud Public, comm user)

For tenants like `my<id>-api.s4hana.cloud.sap`. Read from `.env`:

```
SAP_HOST=https://my<id>-api.s4hana.cloud.sap
SAP_CLIENT=100
SAP_USERNAME=<comm-user> # typically named like <comm-user>, COMMUSER_01, etc.
SAP_PASSWORD=<comm-pass>
SAP_AUTH_MODE=basic
```

Auth header:
```
Authorization: Basic <base64(user:pass)>
```

Same header on the CSRF GET and the data POST. CSRF flow applies for OData V2 writes (not for SOAP A2X).

## Mode B — `cc` (on-prem private edition, OAuth client credentials)

For tenants like `<host>.duvo.inovaflow.io` (on-prem private edition). Cloud blocks inbound CC; on-prem requires it. Read from `.env`:

```
SAP_HOST=https://<host>.<domain>
SAP_TOKEN_URL=https://<host>/sap/bc/sec/oauth2/token?sap-client=100
SAP_CLIENT_ID=<oauth-client>
SAP_CLIENT_SECRET=<oauth-secret>
SAP_CLIENT=100
SAP_AUTH_MODE=cc
```

Token flow:
```
POST <SAP_TOKEN_URL>
 Authorization: Basic <base64(client_id:client_secret)>
 Content-Type: application/x-www-form-urlencoded
 body: grant_type=client_credentials
```

Response includes `access_token` (~48 chars, `expires_in: 3600`).

Auth header for subsequent calls:
```
Authorization: Bearer <access_token>
```

Refresh proactively at ~50min if the run is longer than 55min. Token + CSRF + write all work cleanly under bearer for `API_PURCHASEORDER_PROCESS_SRV`, `API_SUPPLIERINVOICE_PROCESS_SRV`, `API_INFORECORD_PROCESS_SRV` (verified 2026-05-05 against `s4hana.duvo.inovaflow.io`).

## Mode C — `oauth` (Cloud Public, per-request bearer)

For Cloud tenants where the user wants to delegate via interactive OAuth (Auth Code + PKCE). The user obtains a bearer token via their named-user login and passes it per-request.

```
SAP_HOST=https://my<id>-api.s4hana.cloud.sap
SAP_CLIENT=100
SAP_AUTH_MODE=oauth
# No long-lived SAP_USERNAME/SAP_PASSWORD needed — token arrives at runtime
```

Auth header:
```
Authorization: Bearer <user-provided-token>
```

Use case: when the comm user lacks a scope but a named user has it (rare — comm users on Cloud Public generally cover what's needed if the right scenario is in the arrangement).

## Mode detection logic

In auto-detect mode:
- If `SAP_AUTH_MODE` is set, use it.
- Else if `SAP_TOKEN_URL` is present and host matches → `cc`.
- Else if `SAP_USERNAME` / `SAP_PASSWORD` are both present → `basic`.
- Else `oauth` (require user-supplied token at runtime).

Confirm the chosen tenant + mode with the user before any POST.

## .env quirk to watch for

Some `.env` files have overlapping `SAP_HOST` / `SAP_USERNAME` lines for both modes (last-one-wins under naive dotenv parsers). When in doubt, hardcode the target host in the script header rather than trusting env order. See parser snippet in `csrf-flow.md`.
