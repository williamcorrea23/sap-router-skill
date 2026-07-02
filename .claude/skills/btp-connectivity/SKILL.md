---
name: btp-connectivity
description: SAP BTP Connectivity — Cloud Connector setup, Destination Service, principal propagation, on-premise tunneling.
trigger:
  - cloud connector
  - btp connectivity
  - on-premise connection
  - principal propagation
  - scc
  - destination service
  - btp to sap tunnel
  - connect btp to on-premise
prerequisites:
  - Java 17+ installed on DMZ host
  - BTP subaccount admin access
  - VM (Linux/Windows) in DMZ network with outbound HTTPS to BTP
  - SAP system (S/4HANA, ECC, etc.) reachable from DMZ host
---

# BTP Connectivity — Cloud Connector + Principal Propagation

## 1. Download and Install Cloud Connector

```bash
# Download (Linux x64)
wget https://tools.hana.ondemand.com/additional/sapcc-2.17.0-linux-x64.zip
unzip sapcc-2.17.0-linux-x64.zip -d /opt/sapcc
/opt/sapcc/go.sh
```

## 2. Access Admin UI and Change Password

```bash
# Admin UI — default credentials: Administrator / manage
open https://localhost:8443
```

In the SCC UI:
1. Login as `Administrator` / `manage` → **change password immediately**
2. Navigate to **Connector** → **Add Subaccount**

## 3. Configure Subaccount Connection

In SCC UI → **Connector** → **Add Subaccount**:
1. Copy **Region** and **Subaccount ID** from BTP Cockpit
2. Enter **Display Name** (e.g. `s4hana-prod`)
3. Click **Save** — verify status shows **Connected** (green)

## 4. Map Cloud To On-Premise

In SCC UI → **Cloud To On-Premise** → **Add**:

| Field | Value |
|---|---|
| Virtual Host | `s4hana-virtual:443` |
| Internal Host | `s4hana.internal.corp:443` |
| Protocol | HTTPS |
| Backend Type | ABAP System |

Add resource paths:
- `/sap/bc/adt`
- `/sap/opu/odata`
- `/sap/opu/odata/sap/`

## 5. Create Destination in BTP Cockpit

BTP Cockpit → **Connectivity** → **Destinations** → **New Destination**:

```json
{
  "Name": "s4hana-onprem",
  "Type": "HTTP",
  "URL": "https://s4hana-virtual:443",
  "ProxyType": "OnPremise",
  "Authentication": "PrincipalPropagation",
  "Description": "S/4HANA on-premise via Cloud Connector"
}
```

For BasicAuth instead of PrincipalPropagation:
```json
{
  "Name": "s4hana-onprem-basic",
  "Type": "HTTP",
  "URL": "https://s4hana-virtual:443",
  "ProxyType": "OnPremise",
  "Authentication": "BasicAuthentication",
  "User": "SAP_USER",
  "Password": "***"
}
```

## 6. Principal Propagation (Optional)

On the ABAP system (transaction `STRUST`):
1. Import the Cloud Connector root certificate into PSE
2. Configure SAML2: map email from BTP → SAP user ID
3. Ensure `icm/HTTPS/trust_client_with_subject` profile parameter is set

## Verification

```bash
# Check SCC tunnel status from Admin UI → Connector → Status = Connected

# Test destination from BTP Cockpit (Destinations → "Test Connection" button)

# Test via curl through destination service (OAuth flow):
curl -s -X POST \
  https://<subaccount>.authentication.us10.hana.ondemand.com/oauth/token \
  -d "grant_type=client_credentials" \
  -u "<clientid>:<clientsecret>"

# Use the access token to call the destination service:
curl -s \
  "https://<destination-api>/destination-configuration/v1/destinations/s4hana-onprem" \
  -H "Authorization: Bearer <token>"
# Expected: JSON with destination details + auth tokens
```

## Pitfalls

1. **SCC version too old**
   - Cause: ABAP Cloud requires SCC 2.15+; older versions lack principal propagation support.
   - Solution: Upgrade SCC before configuring subaccount. Check version at Admin UI → About.

2. **Resources path case mismatch**
   - Cause: Cloud Connector resources are case-sensitive. `/sap/bc/adt` ≠ `/sap/bc/ADT`.
   - Solution: Copy exact path casing from the SAP system's SICF transaction.

3. **Principal propagation fails silently**
   - Cause: STRUST certificate not imported on ABAP side, or SAML2 name mapping missing.
   - Solution: Verify STRUST PSE has SCC root cert. Check SAML2 → Trusted Provider → Name ID format = email.

4. **SCC shows "Disconnected"**
   - Cause: Outbound HTTPS (port 443) blocked by firewall, or wrong subaccount region.
   - Solution: Open outbound 443 to `*.hana.ondemand.com`. Verify region matches BTP Cockpit.

5. **One SCC per subaccount limitation**
   - Cause: Each subaccount expects one primary SCC. Multiple SCCs need HA/shared master config.
   - Solution: For HA, configure 2+ SCC instances with `--shared` mode pointing to same subaccount.

6. **Destination "Test Connection" fails with 502**
   - Cause: Virtual host in destination URL does not match SCC mapping, or internal host unreachable.
   - Solution: Verify virtual host name in destination matches SCC Cloud To On-Premise mapping exactly.
