---
name: btp-cloud-identity
description: SAP Cloud Identity Services — Identity Authentication (IAS), Identity Provisioning (IPS), Authorization Management (AMS), XSUAA migration strategies, corporate IdP federation (Azure AD, Okta, Keycloak), SAML 2.0, OIDC, user provisioning, SCIM API, Shadow Users pattern. Use when configuring IAS/IPS/AMS, integrating corporate IdPs with SAP BTP, or planning XSUAA migration to Cloud Identity Services.
---

# SAP Cloud Identity Services

Unified identity management across SAP cloud solutions — IAS, IPS, and AMS.

## Three Services

| Service | Acronym | Purpose | Key Protocol |
|---|---|---|---|
| Identity Authentication | IAS | SSO, MFA, corporate IdP federation | SAML 2.0, OIDC |
| Identity Provisioning | IPS | User lifecycle (create/update/delete across systems) | SCIM 2.0 |
| Authorization Management | AMS | Role assignment, SoD checks | REST APIs |

## Corporate IdP Federation Flow

```
End User → Corporate IdP (Azure AD / Okta / Keycloak)
  → SAML Assertion → IAS (SAP Identity Authentication)
    → OIDC Token / SAML → SAP BTP Subaccount (XSUAA)
      → JWT → SAP Application (CAP, Fiori, etc.)
```

## IAS Configuration Steps

1. Download IAS tenant SAML metadata: `https://<tenant>.accounts.ondemand.com/saml2/metadata`
2. Register IAS as Service Provider in corporate IdP (Azure AD Enterprise App)
3. Download corporate IdP metadata from Azure AD → register in IAS as Corporate IdP
4. Configure conditional authentication:
   - Corporate network → password only
   - External → password + TOTP (Microsoft Authenticator / Google Authenticator)
5. Test SSO flow end-to-end

## IPS — User Provisioning

### Source → Target Systems
```
SAP SuccessFactors (HR hire event) → IPS → SAP S/4HANA (Business User created)
Azure AD (join event)              → IPS → SAP BTP (XSUAA shadow user)
SAP S/4HANA (role change)          → IPS → SAP Analytics Cloud (role update)
```

### SCIM 2.0 API

```bash
# Create user via SCIM
curl -X POST https://<ips-tenant>.accounts.ondemand.com/service/scim/Users \
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
curl "https://<ips-tenant>.accounts.ondemand.com/service/scim/Users?filter=userName+eq+%22john.doe%22" \
  -H "Authorization: Bearer <token>"
```

## Shadow Users Pattern

XSUAA creates lightweight "shadow" user records when a non-SAP IdP authenticates:

```
Corporate IdP user: "john.doe@corp.com"
  ↓ SAML authentication
XSUAA shadow user: uuid <a1b2c3d4...> (no password, linked to IdP origin)
  ↓ JWT token
SAP Application (sees john.doe@corp.com in JWT claims)
```

**Problem**: deleting user in corporate IdP does NOT delete shadow user in XSUAA. Need IPS sync for cleanup.

## XSUAA → IAS Migration Steps

1. **Prepare**: export current XSUAA role collections and trust configuration
2. **Configure IAS**: set up as primary IdP for BTP subaccount (Trust Configuration → New Trust → IAS)
3. **Enable User Attribute Propagation**: map IAS user attributes → XSUAA JWT claims (email, groups, given_name)
4. **Migrate role collections**: map XSUAA role collections → IAS user groups
5. **Cutover**: switch application trust from XSUAA-local to IAS-federated
6. **Deprecate**: mark XSUAA local IdP as inactive (keep for rollback period — 30 days)

## Gotchas

- **IAS tenant URL format**: `https://<tenant>.accounts.ondemand.com`
- **IPS job frequency**: minimum 5 minutes between sync jobs
- **Shadow user orphans**: user deleted in IdP → still exists in XSUAA. Requires IPS cleanup job
- **SAML signing certificate expiry**: 1-2 years. Monitor expiration, rotate before expiry
- **XSUAA → IAS migration is ONE-WAY**: once cut over, reverting is manual and complex
- **Attribute mapping is case-sensitive**: `givenName` ≠ `givenname` in SCIM/OpenID
