# ABAP Reference — Scripts & Tables

### Useful Queries

**List all roles assigned to a user:**
```ABAP
SELECT agr_name FROM agr_users WHERE uname = 'USERNAME'.
```

**List authorization objects for a role:**
```ABAP
SELECT objct, field, low, high FROM agr_1251 WHERE agr_name = 'Z_BASIS_ADMIN'.
```

**Check users with SAP_ALL:**
```ABAP
SELECT * FROM agr_1251 WHERE object = 'S_USER_AGR' AND agr_name = 'SAP_ALL'.
```

### Common Tables
| Table | Description |
|--------|--------------|
| AGR_DEFINE | Role definitions |
| AGR_1251 | Authorization data per role |
| AGR_USERS | Users per role |
| USR02 | User logon data |
| USR04 | Profiles assigned |
| USR10 | Authorization values |

### Export Example
Use **SE16N** → Enter table (e.g., AGR_USERS) → Execute → Download as spreadsheet for documentation.
