# Authentication

SAP Transport MCP supports two authentication methods.

---

## Option A: Basic Auth (Recommended for DEV/QA)

```env
AUTH_METHOD=basic
SAP_USERNAME=your_sap_user
SAP_PASSWORD=your_sap_password
```

The user must have:
- Role `SAP_BC_DWB_ABAPDEVELOPER` or equivalent
- Authorization object `S_ADT_RES` for ADT resource access
- ICF service `/sap/bc/adt/` activated (transaction SICF)

---

## Option B: X.509 Certificate (Enterprise / Production)

Certificate-based auth uses mutual TLS — the SAP system validates your client certificate
against the one registered in transaction STRUST.

```env
AUTH_METHOD=certificate
CERT_THUMBPRINT=AB:CD:EF:12:34:56:78:90:AB:CD:EF:12:34:56:78:90:AB:CD:EF:12
SAP_USERNAME=your_sap_user
SAP_PASSWORD=your_sap_password
```

`SAP_USERNAME` and `SAP_PASSWORD` are still required for ADT identity headers.
The certificate covers the transport-layer auth.

### Getting your SHA-1 thumbprint

**macOS:**
```bash
security find-certificate -a -Z ~/Library/Keychains/login.keychain-db | grep -A1 "SHA-1"
```
Or: Keychain Access → Personal Certificates → double-click your SAP cert → Fingerprints → SHA-1

**Windows (PowerShell):**
```powershell
Get-ChildItem Cert:\CurrentUser\My | Format-Table Subject, Thumbprint, NotAfter
```
Or: Win+R → `certmgr.msc` → Personal → Certificates → double-click → Details tab → Thumbprint

The thumbprint must match the certificate configured in SAP transaction STRUST under SSL Client (Anonymous).

---

## CSRF Tokens

SAP ADT requires a CSRF token for all write operations (create, release, delete).
This is handled automatically by `lib/adt-client.ts` — tokens are fetched and cached per system,
and refreshed if SAP returns 403.

---

## SAP Prerequisites

| Requirement | Value |
|-------------|-------|
| Node.js | v18 or later |
| SAP Authorization | `S_ADT_RES` with full access |
| SAP Role | `SAP_BC_DWB_ABAPDEVELOPER` or equivalent |
| ICF Service | `/sap/bc/adt/` active (transaction SICF) |
| Network | HTTPS access to SAP host on configured port |
