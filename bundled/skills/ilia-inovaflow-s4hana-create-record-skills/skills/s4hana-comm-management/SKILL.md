---
name: s4hana-comm-management
description: Set up SAP S/4HANA Cloud Public communication / integration administration via API — create Communication Users, Communication Systems (with OAuth 2.0 authorization_code + redirect URI), and Communication Arrangements, and wire them together. Use whenever the user wants to create/configure/clone/mirror communication setup, inbound API access, OAuth clients, comm users/systems/arrangements, or "integration setup" / "admin work" on S/4HANA — phrases like "create a communication user", "set up a communication system", "add an OAuth client", "create comm arrangements for SAP_COM_0008", "mirror staging to prod/dev", "register an inbound OAuth client", "set the redirect URI". Handles the SAP_COM_0A48 OData V4 A2X services, CSRF, the create order (user → system → inbound/outbound users → arrangements), the OAuth client_id shape that actually authenticates, scenario quirks (0827 basic-only, 0008/0009 DRF), and idempotent GET-before-create. Do NOT use for creating business records (invoices/POs/suppliers) — those have their own skills.
---

# s4hana-comm-management

Create and wire up **Communication Management** objects on SAP S/4HANA Cloud Public Edition via API: Communication **Users**, **Systems** (incl. OAuth 2.0 inbound + redirect URI), and **Arrangements** — plus the admin work around inbound/outbound user assignment and OAuth client registration. **Verified end-to-end 2026-06-24/26 on `my438741-api.s4hana.cloud.sap`**: built 3 full environments (dev/staging/prod), each with a comm user, an OAuth2 system, and 9 arrangements, authenticating live.

> This is a **Cloud Public Edition** capability (scenario **SAP_COM_0A48**, delivered 2408). On-prem / Private Edition does **not** expose these OData V4 services (returns 500) — there, comm objects are Fiori-only. Confirm the tenant before starting.

## When to trigger
Verbs: create / set up / configure / register / clone / mirror / wire up / repoint
Objects: communication user(s), communication system(s), communication arrangement(s), OAuth client, inbound/outbound user, redirect URI, integration setup, "admin work"

Do **NOT** use for business-record creation — defer to `s4hana-create-invoice`, `s4hana-create-po`, `s4hana-create-supplier`, or generic `s4hana-create-record`.

## Hard rules
1. **Confirm the boundary first.** Default to CREATE-only. Modifying/deleting *existing* comm objects (especially anything serving prod) is destructive — get explicit authorization and sequence for zero-downtime. The harness may block writes that look like "modify/delete" until the user authorizes.
2. **Idempotent.** GET-before-create on every object (filter by `ID`/`Name`); skip if present, create if missing. Never overwrite blindly.
3. **Never improvise DRF/replication values** against the tenant. For 0008/0009 use the documented "inactive outbound services" trick (below), not guessed `OUTPUT_MODE` values.
4. **Bootstrap + auth.** The comm user you authenticate as must be the inbound user of a `SAP_COM_0A48` arrangement (set up once in Fiori "Maintain Communication Users" + "Communication Arrangements"). Comm users **lock after a burst of failed logons** — if you see repeated 401 "Logon failed" / "Anmeldung fehlgeschlagen", the account is likely locked; ask the user to unlock in Maintain Communication Users. Stop hammering it.
5. **Stop and report** on any ambiguous required field or unrecoverable error. Do not guess against the tenant.

## The three services (OData V4 A2X)
All under `<host>/sap/opu/odata4/sap/<svc>/srvd_a2x/sap/<svc>/0001/`. Writes need CSRF (GET `<base>/` with `X-CSRF-Token: Fetch`, resend token + cookies on POST). Full field lists in `references/api-reference.md`.

| Object | `<svc>` | entity set | key |
|---|---|---|---|
| Communication **User** | `aps_com_cu_a4c_odata` | `CommunicationUsers` | `ID` (auto `CC0000000NN`; name is `Name`) |
| Communication **System** | `aps_com_cs_a4c_odata` | `CommunicationSystems` | `UUID` (string field `ID`) |
| Communication **Arrangement** | `aps_com_ca_a4c_odata` | `CommunicationArrangements` | `UUID` |

## Create order (dependencies)
Always in this order — later objects reference earlier ones:

1. **Comm user** — `POST CommunicationUsers {Name, Type:"customer_communication", Description, Password}`. `Description` is **required**. `Password` **is** settable via API and becomes the OAuth client secret / basic password.
2. **Communication system** — `POST CommunicationSystems {ID, Name, Type:"customer_managed", Description, TCPPort:443, HostName, LogicalSystemID (≤10 chars), BusinessSystemID, OAuth2RedirectURI, IsOAuth2IdentityProviderActive:false}`. **Deep-insert of inbound users on create is rejected** — create the bare system, then add users separately. `OAuth2RedirectURI` is where the app's callback URL goes. Turning `IsInboundOnly:false` requires a non-empty `HostName`.
3. **Inbound users** — `POST InboundUsers` (standalone set) per system:
   - **OAuth2 (authorization_code):** `{CommunicationSystemUUID, OAuth2ClientID:"<friendly-name>", AuthenticationMethod:"oauth2", OAuth2GrantType:"authorization_code", IsOAuth2RefreshTokenAllowed:true, OAuth2RefreshTokenExpiryValue:1, OAuth2RefreshTokenExpiryUnit:"years"}`. **See the OAuth client_id rule below — this is the #1 gotcha.**
   - **Basic:** `{CommunicationSystemUUID, CommunicationUserID:"CC...", AuthenticationMethod:"basic"}`.
4. **Outbound user** (only if a scenario needs it — see quirks) — `POST OutboundUsers {CommunicationSystemUUID, Name:"not-in-use", AuthenticationMethod:"basic", Password:"<any>"}`. Basic outbound **requires a Password**.
5. **Arrangements** — `POST CommunicationArrangements {CommunicationScenarioID, CommunicationSystemID:"<string ID>", Name, InboundUser:{CommunicationSystemInboundUserUUID:"<uuid>"}}`. Bind to the oauth2 inbound user (or basic for 0827). Repoint later via `PATCH CommunicationArrangements(uuid)/InboundUser`; rename via `PATCH Name`.

## ⚠️ The OAuth client_id rule (the thing that breaks auth)
The runtime OAuth `client_id` the app presents is the **literal `OAuth2ClientID` string** on the inbound user — NOT the comm-user name automatically, and NOT the internal `CC` id. **For an authorization_code client the working shape is `OAuth2ClientID="<name>"` with `CommunicationUserID` EMPTY** (the client id implicitly links to the same-named comm user, whose password is the secret).

Pitfalls, in order of how badly they bite:
- Creating the oauth2 inbound user with `CommunicationUserID:"CC..."` makes the API **derive `OAuth2ClientID` to the `CC` id** → the app's `client_id` (the friendly name) is "unknown". **Fix:** after create, `PATCH InboundUsers(uuid) {OAuth2ClientID:"<name>", CommunicationUserID:""}` so it matches the working shape.
- `OAuth2ClientID` is **tenant-unique**. To reuse a name held by another (e.g. orphaned) inbound user, first PATCH that one to free it (e.g. `"<name>_RETIRED"`).
- The client is only registered while its inbound user is referenced by an active arrangement. **Repointing all arrangements away de-registers it** → "OAuth 2.0 client is unknown". If a friendly id still won't authenticate after a PATCH, re-saving the arrangement in Fiori forces re-registration.
- **Re-registering a client invalidates prior tokens/consents** — authorized users must re-consent after such a change.

Verify the shape against a *known-working* client on the tenant before declaring done:
`oauth2  OAuth2ClientID="<name>"  CommunicationUserID=""`.

## Scenario quirks (verified)
- **`SAP_COM_0827`** (Supplier Confirmation): does **not** support OAuth2 inbound (`CM_APS_CA/037`) — must bind to a **basic** inbound user.
- **`SAP_COM_0008`** (Business Partner) & **`SAP_COM_0009`** (Product): DRF/bidirectional. Need a suitable outbound user AND complain `Enter Output Mode for Outbound Interface`. Create them by deep-inserting their replication outbound services as **inactive**, mirroring how Fiori leaves them: `OutboundServices:[{ID:"DEBMAS_IDOC",Status:"inactive"},{ID:"CREMAS_IDOC",Status:"inactive"},{ID:"CO_MDG_BP_RPLCTRQ_SPRX",Status:"inactive"}]` (0008); `[{ID:"MATMAS_IDOC",Status:"inactive"},{ID:"CO_MDM_PRD_BULK_REPL_REQ_OUT_SPRX",Status:"inactive"},{ID:"CO_MDM_PRD_BULK_REP_CONF_OUT_SPRX",Status:"inactive"}]` (0009).
- Several scenarios (`0008/0009/0108/0827`) need the system to have a **suitable outbound user** even when you'd expect inbound-only to exempt them. `IsInboundOnly:true` does NOT exempt them — give the system an outbound user (with password) instead.

## Idempotent environment-mirroring playbook
To clone a working OAuth2 setup to a new env (e.g. dev/staging/prod):
1. **Read the template** system fully (`$expand=InboundUsers,OutboundUsers,OpenIDConnect`) to copy its exact shape and the working `OAuth2ClientID` shape.
2. Create the new comm user (generate + report its secret if the user asks).
3. Create the new system with the env's `OAuth2RedirectURI`; add inbound users (oauth2 + basic), fix the oauth2 `OAuth2ClientID`/empty-`CommunicationUserID` shape, add an outbound user if any bidirectional scenario is in scope.
4. Create arrangements (GET-by-`Name` first), oauth2-bound except 0827 (basic). Use the inactive-outbound-services trick for 0008/0009.
5. **Verify** every arrangement's bound `client_id` and the inbound-user shape against the working template before declaring done. Then have the user test a real token/login.

For a **prod cutover** (move arrangements between systems / change the owning user): create the target side fully FIRST so the user keeps access during overlap, then repoint/retire the source — zero-downtime because S/4 authorizes by OAuth client across systems.

## Helper
`scripts/commmgmt-lib.mjs` — `.env`-driven (host/user/pass), CSRF-aware GET/POST/PATCH, secret generator, idempotent helpers. Import it from a short run script; never hardcode the tenant.

## Reference files
- `references/api-reference.md` — exact service paths, entity fields/keys, payload examples for every object + sub-entity.
- `references/oauth-and-gotchas.md` — the OAuth client_id/registration model in depth, scenario quirks, lockout, and the error-code → cause table.
