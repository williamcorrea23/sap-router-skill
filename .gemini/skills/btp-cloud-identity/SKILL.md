---
name: btp-cloud-identity
description: SAP Cloud Identity Services — IAS (authentication), IPS (provisioning), AMS (authorization), XSUAA migration, corporate IdP federation.
trigger:
  - cloud identity
  - ias
  - ips
  - ams
  - xsuaa migration
  - identity authentication
  - identity provisioning
  - corporate idp
  - saml federation
  - oidc
  - scim api
  - shadow users
prerequisites:
  - SAP Cloud Identity Services tenant provisioned (IAS + IPS)
  - BTP subaccount admin access
  - Corporate IdP metadata (Azure AD, Okta, Keycloak) — SAML metadata XML
  - `curl` or Postman for SCIM API testing
---

# SAP Cloud Identity Services — IAS / IPS / AMS

## 1. Download IAS Tenant Metadata

```bash
# Download IAS SAML metadata
curl -s https://<tenant>.accounts.ondemand.com/saml2/metadata -o ias-metadata.xml

# Download OIDC discovery document
curl -s https://<tenant>.accounts.ondemand.com/.well-known/openid-configuration | jq .
```

## 2. Configure Corporate IdP Federation (IAS)

**In Corporate IdP (Azure AD / Okta / Keycloak):**
1. Create Enterprise Application (SAML)
2. Upload `ias-metadata.xml` as Service Provider metadata
3. Configure nameID format as `emailAddress`
4. Export corporate IdP SAML metadata XML

**In IAS Admin Console** (`https://<tenant>.accounts.ondemand.com/admin`):
1. Navigate to **Applications** → select your BTP subaccount app
2. **Trust** → **Corporate Identity Provider** → **Add**
3. Upload corporate IdP metadata XML
4. Configure conditional authentication:
   - Corporate IP range → password only
   - External → password + TOTP (Microsoft/Google Authenticator)
5. Save and enable

## 3. Configure IPS — User Provisioning

**In IPS Admin Console** (`https://<tenant>.accounts.ondemand.com/ips`):

1. **Source Systems** → **Add** → select type (e.g. SAP SuccessFactors, Azure AD)
2. Configure source connection properties (URL, credentials)
3. **Target Systems** → **Add** → select type (e.g. SAP BTP XSUAA, S/4HANA)
4. Configure target connection properties
5. **Mapping** → define attribute mappings:
   - `userName` → `userName`
   - `emails[0].value` → `emails[0].value`
   - `groups` → `groups`
6. **Jobs** → **Create** → select source + target → **Run**

## 4. Manage Users via SCIM 2.0 API

```bash
# Create user
curl -X POST https://<tenant>.accounts.ondemand.com/service/scim/Users \
  -H "Content-Type: application/scim+json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
    "userName": "john.doe@corp.com",
    "name": { "givenName": "John", "familyName": "Doe" },
    "emails": [{ "value": "john.doe@corp.com", "primary": true }],
    "active": true
  }'

# List users with filter
curl "https://<tenant>.accounts.ondemand.com/service/scim/Users?filter=userName+eq+%22john.doe%22" \
  -H "Authorization: Bearer <token>"

# Delete user
curl -X DELETE \
  "https://<tenant>.accounts.ondemand.com/service/scim/Users/<user-id>" \
  -H "Authorization: Bearer <token>"
```

## 5. XSUAA → IAS Migration

```bash
# Step 1: Export current XSUAA trust config (BTP Cockpit → Security → Trust Configuration)

# Step 2: In BTP Cockpit → Security → Trust Configuration → New Trust
#         → Select IAS tenant → Save

# Step 3: In IAS → Applications → BTP subaccount → SAML 2.0 →
#         Enable "Default IDP" = Corporate IdP

# Step 4: Map role collections:
#         BTP Cockpit → Security → Role Collections →
#         Assign to IAS user groups instead of individual users

# Step 5: Test login with corporate IdP user
#         BTP Cockpit → click "Go to Application" → should redirect to corporate IdP

# Step 6: After 30-day grace period, disable XSUAA local IdP
```

## 6. Shadow User Cleanup

```bash
# List orphaned shadow users (exist in XSUAA but not in IdP)
curl "https://<tenant>.accounts.ondemand.com/service/scim/Users?filter=active+eq+true" \
  -H "Authorization: Bearer <token>" | jq '.Resources[] | .userName'

# Deactivate orphaned users via IPS cleanup job:
# IPS Admin Console → Jobs → "Cleanup" → Run
```

## Verification

```bash
# Verify IAS metadata is accessible
curl -s https://<tenant>.accounts.ondemand.com/saml2/metadata | head -5
# Expected: XML with EntityDescriptor

# Verify OIDC endpoint
curl -s https://<tenant>.accounts.ondemand.com/.well-known/openid-configuration | jq .issuer
# Expected: "https://<tenant>.accounts.ondemand.com"

# Verify SSO flow: open BTP app URL in browser
# Expected: redirect to corporate IdP login page, then back to BTP app

# Verify IPS provisioning job status
# IPS Admin Console → Jobs → View job log → Status = "Finished"

# Verify SCIM API is working
curl -s https://<tenant>.accounts.ondemand.com/service/scim/Users \
  -H "Authorization: Bearer <token>" | jq '.totalResults'
# Expected: number > 0
```

## Pitfalls

1. **Shadow user orphans after IdP deletion**
   - Cause: Deleting a user in corporate IdP does not remove the shadow user in XSUAA.
   - Solution: Configure IPS cleanup job to run daily. Job deactivates users not present in source system.

2. **SAML certificate expiry breaks SSO**
   - Cause: Signing certificates expire every 1-2 years. No automatic alert by default.
   - Solution: Monitor expiry date in IAS Admin Console → Settings → Certificates. Rotate 30 days before expiry and update corporate IdP trust.

3. **IPS job frequency limit**
   - Cause: IPS minimum sync interval is 5 minutes. Sub-minute syncs are not supported.
   - Solution: Use real-time SCIM API for immediate user creation instead of batch jobs.

4. **Attribute mapping case mismatch**
   - Cause: SCIM/OpenID attribute names are case-sensitive. `givenName` ≠ `givenname`.
   - Solution: Use exact casing from SCIM 2.0 RFC. Test with `curl` before enabling the mapping in production.

5. **XSUAA → IAS migration is one-way**
   - Cause: Once BTP subaccount trust is switched to IAS, reverting requires manual trust reconfiguration.
   - Solution: Keep XSUAA local IdP active for 30-day rollback window. Test with pilot users before full cutover.

6. **IAS tenant URL format confusion**
   - Cause: Different URLs for admin console vs SCIM API vs SAML metadata.
   - Solution: Admin = `https://<tenant>.accounts.ondemand.com/admin`. SCIM = `https://<tenant>.accounts.ondemand.com/service/scim`. SAML metadata = `https://<tenant>.accounts.ondemand.com/saml2/metadata`.

7. **MFA not triggered for external access**
   - Cause: Conditional authentication rules not applied, or corporate IP range too broad.
   - Solution: Verify IP ranges in IAS → Applications → Conditional Authentication. Use CIDR notation (e.g. `10.0.0.0/8`).
