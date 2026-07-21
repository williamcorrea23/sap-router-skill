# Communication Management API reference (SAP_COM_0A48, OData V4 A2X)

Cloud Public Edition only. Verified against `my438741-api.s4hana.cloud.sap` (system H2Y, client 100), 2026-06.

## Services
Base path pattern: `<host>/sap/opu/odata4/sap/<svc>/srvd_a2x/sap/<svc>/0001`

| Object | `<svc>` | api.sap.com ID |
|---|---|---|
| Communication User | `aps_com_cu_a4c_odata` | `CE_APS_COM_CU_A4C_ODATA_0001` |
| Communication System | `aps_com_cs_a4c_odata` | `CE_APS_COM_CS_A4C_ODATA_0001` |
| Communication Arrangement | `aps_com_ca_a4c_odata` | `CE_APS_COM_CA_A4C_ODATA_0001` |

Metadata: `<base>/$metadata`. Always re-check `$metadata` against the live tenant before bulk — field sets can vary by release.

## CSRF (all writes)
1. `GET <base>/` with header `X-CSRF-Token: Fetch` → response header `X-CSRF-Token: <token>` + `Set-Cookie`.
2. Resend `X-CSRF-Token: <token>` + `Cookie: <session cookies>` on the POST/PATCH.
`Accept` / `Content-Type`: `application/json`. (JSON `$batch` is rejected — only `multipart/mixed`.)

## CommunicationUsers (key `ID`)
Props: `ID` (auto `CC0000000NN`), `Name` (user-facing), `Type` (`customer_communication`), `Description`, `IsLocked`, `LockStatus`, `Password`, `PasswordStatus`, `ChangedAt/By`. Sub-entity `Certificates`.

Create:
```json
POST CommunicationUsers
{ "Name":"MCP_DEV", "Type":"customer_communication", "Description":"<required>", "Password":"<>=20 chars, mixed>" }
```
- `Description` is **mandatory** (`User CC... must have a description`).
- `Password` IS writable here (older SAP docs wrongly say it isn't). It becomes the basic password AND the OAuth client secret for the same-named OAuth client.
- Existence/idempotency: `GET CommunicationUsers?$filter=Name eq 'MCP_DEV'`.

## CommunicationSystems (key `UUID`, string field `ID`)
Key write props: `ID`, `Name`, `Type:"customer_managed"`, `Description`, `TCPPort` (443), `HostName`, `LogicalSystemID` (**max 10 chars**), `BusinessSystemID`, `IsInboundOnly`, `IsOwnSystem`, `IsCipherSuiteDefault`. OAuth/IdP block: `IsOAuth2IdentityProviderActive`, `OAuth2IdentityProviderName`, `OAuth2AuthorizationEndpoint`, `OAuth2TokenEndpoint`, `OAuth2Audience`, **`OAuth2RedirectURI`** (the app callback URL). Nav: `InboundUsers`, `OutboundUsers`, `OpenIDConnect`, `BusinessPartners`, `EventChannel`.

Create (bare — no deep-insert of users):
```json
POST CommunicationSystems
{ "ID":"MCP_DUVO_DEV_OAUTH2", "Name":"MCP_DUVO_DEV_OAUTH2", "Type":"customer_managed",
  "Description":"...", "TCPPort":443, "HostName":"mcp.local.dev",
  "LogicalSystemID":"MCPLOGDEV", "BusinessSystemID":"MCPBIZSYSDEV",
  "OAuth2RedirectURI":"https://app.example.com/v1/oauth/callback/saps4hana",
  "IsOAuth2IdentityProviderActive":false }
```
- **Deep-inserting `InboundUsers` in this POST fails `CM_APS_CS/026`** — create the system, then POST inbound users to the standalone set.
- `LogicalSystemID` > 10 chars → `MaxLength=10` facet error. `BusinessSystemID` tolerates longer.
- `LogicalSystemID`/`BusinessSystemID` need NOT be unique (two systems can share `LogicalSystemID`).
- Existence: `GET CommunicationSystems?$filter=ID eq 'MCP_DUVO_DEV_OAUTH2'`. Sub-entities: `GET CommunicationSystems(<uuid>)/InboundUsers` etc.

## InboundUsers (standalone entity set, key `UUID`)
Props: `UUID`, `CommunicationSystemUUID`, `CommunicationUserID`, `OAuth2ClientID`, `OAuth2GrantType`, `IsOAuth2RefreshTokenAllowed`, `OAuth2RefreshTokenExpiryValue`, `OAuth2RefreshTokenExpiryUnit`, `AuthenticationMethod` (`basic`|`oauth2`|`x509`|`none`|...).

Basic:
```json
POST InboundUsers
{ "CommunicationSystemUUID":"<sys uuid>", "CommunicationUserID":"CC0000000003", "AuthenticationMethod":"basic" }
```
OAuth2 authorization_code — **target shape (matches what authenticates):**
```json
{ "CommunicationSystemUUID":"<sys uuid>", "OAuth2ClientID":"MCP_DEV", "CommunicationUserID":"",
  "AuthenticationMethod":"oauth2", "OAuth2GrantType":"authorization_code",
  "IsOAuth2RefreshTokenAllowed":true, "OAuth2RefreshTokenExpiryValue":1, "OAuth2RefreshTokenExpiryUnit":"years" }
```
- Creating with `OAuth2ClientID` ALONE (no `CommunicationUserID`) fails `CM_APS_CS/026`. Creating with `CommunicationUserID` derives `OAuth2ClientID` to the `CC` id. So: create with `CommunicationUserID`, then **PATCH** `{OAuth2ClientID:"MCP_DEV", CommunicationUserID:""}` to reach the target shape. See `oauth-and-gotchas.md`.
- `OAuth2ClientID` is **tenant-unique** (`...already assigned to Comm. System ...`).

## OutboundUsers (standalone entity set, key `UUID`)
Props: `UUID`, `CommunicationSystemUUID`, `Name`, `OAuth2ClientID`, `OAuth2ClientAuthenticationMethod`, `CertificateID`, `AuthenticationMethod`, `Password`.
```json
POST OutboundUsers
{ "CommunicationSystemUUID":"<sys uuid>", "Name":"not-in-use", "AuthenticationMethod":"basic", "Password":"<any 20+>" }
```
Basic outbound **must** have a `Password`, else arrangement create fails `CM_APS_CA/100: Password missing`.

## CommunicationArrangements (key `UUID`)
Props: `UUID`, `CommunicationScenarioID`, `CommunicationSystemID` (string system `ID`), `Name`, `Description`. Navs: `InboundUser` (single → `CommunicationSystemInboundUserUUID`), `InboundServices`, `OutboundServices`, `OutboundUser`, `Properties`.

Create:
```json
POST CommunicationArrangements
{ "CommunicationScenarioID":"SAP_COM_0008", "CommunicationSystemID":"MCP_DUVO_DEV_OAUTH2",
  "Name":"MCP_BUSINESS_PARTNER_DEV_OAUTH2",
  "InboundUser":{ "CommunicationSystemInboundUserUUID":"<oauth2 inbound uuid>" } }
```
- For DRF scenarios (0008/0009) add `OutboundServices:[{ID:"...",Status:"inactive"}, ...]` — see SKILL quirks.
- 0827 must bind to a **basic** inbound user.
- Existence: `GET CommunicationArrangements?$filter=Name eq '<name>'`.
- Repoint inbound user: `PATCH CommunicationArrangements(<uuid>)/InboundUser {CommunicationSystemInboundUserUUID:"<uuid>"}`.
- Rename: `PATCH CommunicationArrangements(<uuid>) {Name:"<new>"}`.

## Auth to the API
Basic, as a comm user that is the inbound user of a `SAP_COM_0A48` arrangement. The first such arrangement is bootstrapped once in Fiori (Maintain Communication Users + Communication Arrangements). On-prem/Private Edition: these services return 500 — not available; use Fiori there.
