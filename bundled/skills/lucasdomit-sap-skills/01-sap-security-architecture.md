# SAP Security Architecture Overview

SAP Security architecture is built upon multiple layers: authentication, authorization, audit, and governance.

## Core Components
- **User Master Record (USR02, USR21):** Contains user credentials and logon data.
- **Authorization Concept:** Uses objects (S_*) and fields (ACTVT) to control access.
- **Role Concept:** Groups transactions and authorizations under a business function.
- **Profiles:** Generated technical artifacts providing executable permissions.
- **Audit Layer:** Logging via SM19, SM20, SCUL.

### Logical Security Flow
1. User logs in → Authentication validated.
2. System checks Authorization Objects.
3. Activities (ACTVT) mapped to roles and profiles.
4. Audit logs capture system actions.

### Relevant Transactions
| Purpose | Transaction |
|----------|--------------|
| Maintain Users | SU01 |
| Maintain Roles | PFCG |
| Mass Changes | SU10 |
| Display Users | SUIM |
| Audit Logs | SM19 / SM20 |
| Transport Roles | STMS |