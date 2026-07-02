---
name: sap-btp-credential-store
description: SAP BTP Credential Store — secure credential vault on BTP, credential retrieval API, service binding secrets, encrypted password storage, credential rotation, integration with CAP and Cloud Foundry apps. Use when securely storing credentials on BTP, managing service credentials, or implementing credential rotation.
trigger:
  - credential store BTP setup
  - secure password storage BTP
  - credential rotation automation
  - CAP retrieve credentials from vault
  - encrypted secrets management BTP
  - credential store REST API
---

# SAP BTP Credential Store

Secure vault for credentials and secrets on SAP BTP — encrypted storage with access control and audit logging.

## Prerequisites

- SAP BTP subaccount with Cloud Foundry enabled
- CF CLI installed and logged in (`cf login`)
- Credential Store entitlement (standard plan)
- CAP project with `@sap/cds` ≥ 7.x and `@sap/credential-store` package
- Node.js ≥ 18

## 1. Create and Bind the Credential Store Service

```bash
# Create service instance
cf create-service credential-store standard my-credstore

# Bind to your application
cf bind-service my-app my-credstore

# Create a service key for admin API access
cf create-service-key my-credstore admin-key

# Retrieve credentials for API calls
cf service-key my-credstore admin-key
```

## 2. Store Credentials (REST API)

```bash
# Store a password credential
curl -X POST "https://credstore.cfapps.<region>.hana.ondemand.com/api/v1/credentials/password" \
  -H "Authorization: Bearer $CREDSTORE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "PAYMENT_GATEWAY",
    "value": "super_secret_password",
    "username": "payment_user"
  }'

# Read credential back
curl "https://credstore.cfapps.<region>.hana.ondemand.com/api/v1/credentials/password/PAYMENT_GATEWAY" \
  -H "Authorization: Bearer $CREDSTORE_TOKEN"
```

## 3. Retrieve Credentials in CAP

```bash
# Install the SDK
npm install @sap/credential-store
```

```javascript
const cds = require('@sap/cds')
const { CredentialStore } = require('@sap/credential-store')

module.exports = class PaymentService extends cds.ApplicationService {
  async init() {
    this.on('processPayment', async (req) => {
      const credStore = new CredentialStore()
      const { username, password } = await credStore.readPassword('PAYMENT_GATEWAY')

      const result = await axios.post('https://payment.vendor.com/api/charge', {
        amount: req.data.amount,
        customerId: req.data.customerId
      }, { auth: { username, password } })
      return result.data
    })
    await super.init()
  }
}
```

## 4. Automate Credential Rotation

```javascript
const { CredentialStore } = require('@sap/credential-store')
const credStore = new CredentialStore()

async function rotateCredentials() {
  const current = await credStore.readPassword('DB_ADMIN')
  const newPassword = generateSecurePassword()

  // Step 1: Update database with new password
  await updateDatabasePassword(current.username, current.password, newPassword)

  // Step 2: Store new password in Credential Store
  await credStore.writePassword('DB_ADMIN', {
    username: current.username,
    password: newPassword
  })

  console.log('Credential rotated:', new Date().toISOString())
}
```

Schedule rotation via SAP BTP Job Scheduling service (every 30 days recommended).

## 5. When to Use vs Alternatives

- ✅ **Database passwords** — Rotated, never in source code
- ✅ **Third-party API keys** — Encrypted, auditable
- ❌ **SAP destination auth** → Use Destination Service (Principal Propagation)
- ❌ **App config values** → Use App Configuration Service or env vars
- ❌ **JWT signing keys** → Use XSUAA OAuth2 keys

## Pitfalls

- **Pitfall: Credentials hardcoded in source code**
  - Cause: Developers paste passwords in `default-env.json` or source files.
  - Solution: Always read from Credential Store at runtime. Add pre-commit hook to scan for secrets.

- **Pitfall: Rotation breaks the running app**
  - Cause: New password stored before the downstream system accepts it (ordering).
  - Solution: Update the target system first, then write to Credential Store. Keep old password valid during transition window.

- **Pitfall: Credential read latency on cold start**
  - Cause: First read fetches from service over network; no local cache yet.
  - Solution: Pre-warm cache at app startup. In-app cache TTL is ~5 min. For high-frequency access, cache in memory with fallback.

- **Pitfall: Service key token expired**
  - Cause: OAuth token from service key has limited lifetime.
  - Solution: Use the binding credentials from `VCAP_SERVICES` in the app. For CLI scripts, fetch a fresh token before each batch.

- **Pitfall: Exceeded credential limit**
  - Cause: Standard plan allows up to 1000 credentials per instance.
  - Solution: Clean up unused credentials. Use naming convention with prefix for org/team. Split into multiple instances if needed.

## Verification

```bash
# 1. Verify service instance and binding
cf services | grep my-credstore
cf env my-app | grep -A5 credential-store

# 2. Test credential read via API
curl "https://credstore.cfapps.<region>.hana.ondemand.com/api/v1/credentials/password/PAYMENT_GATEWAY" \
  -H "Authorization: Bearer $CREDSTORE_TOKEN"
# → Should return JSON with username + masked password

# 3. Test from CAP app
curl -X POST https://my-app.cfapps.<region>.hana.ondemand.com/odata/v4/Payments/processPayment \
  -H "Content-Type: application/json" \
  -d '{"amount":100,"customerId":"C001"}'
# → Should succeed without credential errors

# 4. Verify rotation job ran
# Check Job Scheduling service logs or run: rotateCredentials() manually and confirm no auth errors
```
