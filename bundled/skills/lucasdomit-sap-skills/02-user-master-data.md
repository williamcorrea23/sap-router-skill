# SAP User Master Data

The user master record defines identity, permissions, and connection between business processes and technical authorization.

## Key Tables
| Table | Description |
|--------|--------------|
| USR02 | User logon data (password, lock, validity) |
| USR21 | Assignment between users and address data |
| USR04 | Profiles assigned to users |
| USR05 | User parameters |
| AGR_USERS | Links users with roles |

## SU01 Key Tabs
- **Address:** personal and contact details
- **Logon Data:** type (Dialog, System, Communication, Service)
- **Roles:** business responsibilities and access
- **Profiles:** generated profiles linked to authorizations

### User Types
| Type | Purpose |
|------|----------|
| Dialog | Interactive user |
| System | Background processes |
| Communication | External RFC calls |
| Service | Shared generic user |
| Reference | Inherited authorizations |