# OAuth client model, scenario quirks & error decoder

The hard-won lessons from building dev/staging/prod OAuth2 setups. Read before touching inbound OAuth.

## The OAuth client_id model (read twice)
For inbound **authorization_code** on S/4HANA Cloud:
- The OAuth `client_id` the external app presents == the **literal `OAuth2ClientID`** string on the system's oauth2 inbound user.
- The **client secret** == the password of the **communication user whose `Name` equals that `OAuth2ClientID`**. (So an OAuth client `MCP_API2` is secured by comm user `MCP_API2`'s password.)
- The **working inbound-user shape** is: `AuthenticationMethod="oauth2"`, `OAuth2ClientID="<name>"`, **`CommunicationUserID=""` (empty)**, `OAuth2GrantType="authorization_code"`. In authorization_code the resource owner is decided by the interactive login, so no fixed `CommunicationUserID`.
- The client is **registered/usable only while its inbound user is referenced by an active arrangement**.

### Why API-created clients often "are unknown"
The API won't let you POST an oauth2 inbound user with `OAuth2ClientID` alone (`CM_APS_CS/026`). If you POST with `CommunicationUserID:"CC..."`, it **derives `OAuth2ClientID` to that `CC` id**. Result: the registered client is `CC0000000002`, but the app sends `client_id=MCP_API2` → **"OAuth 2.0 client is unknown."**

### The fix (idempotent, no recreate)
After creating the oauth2 inbound user:
```
PATCH InboundUsers(<uuid>) { "OAuth2ClientID":"MCP_API2", "CommunicationUserID":"" }
```
- If `OAuth2ClientID` is rejected as "already assigned to Comm. System X", that name is held elsewhere (often an orphaned inbound user). Free it first: `PATCH InboundUsers(<other uuid>) {OAuth2ClientID:"MCP_API2_RETIRED"}`.
- Always end by **diffing against a known-working client** on the same tenant; the working one has `CommunicationUserID=""`. If yours has a `CC` id there, it's malformed.
- If the friendly id still won't authenticate after the PATCH, the registration is stale from when the arrangement was first saved. Re-save the arrangement (Fiori Save, or toggle the inbound OAuth user) to force re-registration.

### Re-authorization impact
De-registering and re-registering a client (renaming its id, moving its arrangements between systems, resetting the comm user's password) **invalidates previously issued access/refresh tokens and user consents**. Plan for authorized users to **re-consent once**. The `client_id`/secret staying the same does NOT preserve old grants if the registration was rebuilt.

## Inbound-only vs outbound users
`IsInboundOnly:true` avoids needing an outbound user for purely-inbound scenarios — but **does not exempt** `0008/0009/0108/0827`, which still demand a suitable outbound user. If any of those are in scope, set `IsInboundOnly:false` (needs a `HostName`) and add an outbound user with a password. Basic outbound with no password → `CM_APS_CA/100: Password missing` at arrangement create.

## DRF scenarios 0008 / 0009
Bidirectional (Business Partner / Product). With an outbound user present, arrangement create still fails `Enter Output Mode for Outbound Interface` because the replication outbound services demand `REPLICATION_MODE`/`OUTPUT_MODE`. Don't guess those values. Instead deep-insert the replication services as **inactive** (how Fiori leaves them):
- 0008: `DEBMAS_IDOC`, `CREMAS_IDOC`, `CO_MDG_BP_RPLCTRQ_SPRX` → `Status:"inactive"`.
- 0009: `MATMAS_IDOC`, `CO_MDM_PRD_BULK_REPL_REQ_OUT_SPRX`, `CO_MDM_PRD_BULK_REP_CONF_OUT_SPRX` → `Status:"inactive"`.

## Comm-user lockout
The tenant locks a comm user after a burst of failed logons. Symptoms: every call returns **401 with the HTML "Anmeldung fehlgeschlagen" / "401 Nicht autorisiert"** page (note: it's an *auth* failure page, not an OData error). A comm user with **no inbound arrangement at all** can also return 401 (not 403). Don't keep retrying — ask the user to **unlock** it in Maintain Communication Users (and reset/confirm the password). Verify the parsed password is correct (length, no smart quotes/CR) before assuming it's wrong.

## Error-code → cause
| Code / message | Cause | Action |
|---|---|---|
| `401` HTML "Anmeldung fehlgeschlagen" | bad password, locked user, or user not on any inbound arrangement | unlock / fix password / add to `SAP_COM_0A48` |
| HTTP 500 (empty) on the service root | service not available (on-prem/Private Edition) | not a Cloud Public tenant — use Fiori |
| `CM_APS_CS/026` "user ID or OAuth client ID is missing" | oauth2 inbound posted with `OAuth2ClientID` only | POST with `CommunicationUserID`, then PATCH the shape |
| `...OAuth2 Client ID X is already assigned to Comm. System Y` | client id is tenant-unique | free the name on the other inbound user first |
| `MaxLength=10` on `LogicalSystemID` | value > 10 chars | shorten it |
| `CM_APS_CS/025` "host name is missing" | setting `IsInboundOnly:false` without `HostName` | include `HostName` in the PATCH |
| `CM_APS_CA/010` / `CM_APS_CA/027` "no suitable outbound user" | scenario needs an outbound user; system has none | add an outbound user (with password) |
| `CM_APS_CA/100` "Password missing" | basic outbound user has no password | give the outbound user a password |
| `CM_APS_CA/037` "OAuth 2.0 not supported for inbound in SAP_COM_0827" | 0827 is basic-only | bind 0827 to a basic inbound user |
| `Enter Output Mode for Outbound Interface` (0008/0009) | DRF replication service wants a mode | deep-insert those outbound services as `Status:"inactive"` |
| `User CC... must have a description` | comm user create without `Description` | add `Description` |
