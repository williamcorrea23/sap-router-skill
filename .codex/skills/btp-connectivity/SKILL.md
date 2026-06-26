---
name: btp-connectivity
description: SAP BTP Connectivity service — Cloud Connector installation, on-premise system exposure to BTP, destination types (on-premise vs internet), principal propagation, mutual TLS, SOCKS5 proxy, RFC connectivity from cloud, connectivity health monitoring. Use when connecting BTP to on-premise SAP, setting up Cloud Connector, or configuring principal propagation.
---

# SAP BTP Connectivity Service

Secure tunnel between SAP BTP and on-premise systems via Cloud Connector.

## Architecture

```
SAP BTP Cloud → Connectivity Service (SOCKS5 proxy)
    ↑ TLS Tunnel (port 443)
SAP Cloud Connector (on-premise VM)
    ↓ Internal network (ports 80xx/33xx)
SAP S/4HANA / ECC / BW
```

## Cloud Connector Setup

1. Download from SAP Development Tools portal
2. Install on Windows/Linux VM in DMZ (Java 17+)
3. Login: https://<host>:8443 (initial: Administrator / manage)
4. Connect to BTP subaccount (region + subaccount ID)
5. Map: Virtual Host → Internal Host (Access Control)
6. Add resource paths: /sap/bc/adt, /sap/opu/odata

## Principal Propagation

```
BTP User (email) → Cloud Connector → X.509 short-lived cert → SAP ABAP user
```
Requires trust configuration in STRUST on ABAP side.

## Destination Configuration

```json
{
  "Name": "s4hana-onprem",
  "Type": "HTTP",
  "URL": "https://s4hana.internal:443",
  "ProxyType": "OnPremise",
  "Authentication": "PrincipalPropagation"
}
```

## Gotchas
- CC v2.15+ required for ABAP Cloud integration
- One CC instance per BTP subaccount (HA: 2+ instances with shared master)
- Principal propagation requires both CC and ABAP trust configs
