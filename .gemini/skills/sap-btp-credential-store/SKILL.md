---
name: sap-btp-credential-store
description: SAP BTP Credential Store — secure credential storage on BTP, credential retrieval API, service binding secrets, encrypted password vault, credential rotation, integration with CAP and Cloud Foundry apps, Vault API. Use when securely storing credentials on BTP, managing service credentials, implementing credential rotation, or accessing stored passwords/secrets from BTP applications.
---

# SAP BTP Credential Store

Secure vault for credentials and secrets on SAP BTP — encrypted password storage with access control.

## Service Instance

```bash
cf create-service credential-store standard my-credstore
cf bind-service my-app my-credstore
```

## Store and Retrieve Credentials

```javascript
// CAP service using credential store
const cds = require('@sap/cds')
const axios = require('axios')
const xsenv = require('@sap/xsenv')
const { CredentialStore } = require('@sap/credential-store')

module.exports = class PaymentService extends cds.ApplicationService {
  async init() {
    this.on('processPayment', async (req) => {
      // Retrieve credential from vault
      const credStore = new CredentialStore()
      const { username, password } = await credStore.readPassword('PAYMENT_GATEWAY')

      const result = await axios.post('https://payment.vendor.com/api/charge', {
        amount: req.data.amount,
        customerId: req.data.customerId
      }, {
        auth: { username, password }
      })
      return result.data
    })
    await super.init()
  }
}
```

## REST API

```bash
# Create credential (via service broker CLI)
cf create-service-key my-credstore admin-key

# Store a password
curl -X POST https://credstore.cfapps.us10.hana.ondemand.com/api/v1/credentials/password \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "PAYMENT_GATEWAY",
    "value": "super_secret_password",
    "username": "payment_user"
  }'

# Read credential
curl https://credstore.cfapps.us10.hana.ondemand.com/api/v1/credentials/password/PAYMENT_GATEWAY \
  -H "Authorization: Bearer <token>"
```

## Credential Rotation

```javascript
// Automated password rotation
const credStore = new CredentialStore()

async function rotateCredentials() {
  const current = await credStore.readPassword('DB_ADMIN')

  // Generate new password
  const newPassword = generateSecurePassword()

  // Update database with new password
  await updateDatabasePassword(current.username, current.password, newPassword)

  // Store new password in Credential Store
  await credStore.writePassword('DB_ADMIN', {
    username: current.username,
    password: newPassword
  })

  console.log('Credential rotated successfully')
}

// Run every 30 days
setInterval(rotateCredentials, 30 * 24 * 60 * 60 * 1000)
```

## When to Use

| Use Case | Use Credential Store? | Why |
|---|---|---|
| Database passwords | ✅ | Rotated credentials, never in code |
| API keys for 3rd party | ✅ | Encrypted, auditable |
| SAP destination auth | ❌ | Use Destination Service (PrincipalPropagation) |
| App config values | ❌ | Use App Configuration Service or env vars |
| JWT signing keys | ❌ | Use XSUAA OAuth2 keys |

## Gotchas

- **Never hardcode credentials** — credential store or destination service always
- **Credential rotation**: automate via scheduled job (btp-job-scheduling)
- **Access logging**: all credential reads are logged (auditable)
- **Service plan**: standard plan supports up to 1000 credentials per instance
- **Read performance**: cached in-app after first read; TTL 5 min
