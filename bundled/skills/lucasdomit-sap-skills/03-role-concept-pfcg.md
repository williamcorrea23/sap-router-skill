# Role Concept and PFCG

Roles define *who can do what* in SAP. The transaction **PFCG (Role Maintenance)** is the central point for defining and managing them.

## Role Types
| Type | Description |
|-------|--------------|
| Single Role | Contains transactions and authorizations |
| Composite Role | Group of single roles |
| Derived Role | Inherits authorizations from parent roles |

## PFCG Workflow
1. Create Role → Define Menu (Transactions, Reports, URLs)  
2. Maintain Authorizations → Adjust Org Levels  
3. Generate Profile → Technical link to authorizations  
4. Assign Role to User → Sync with SU01  

### Core Tables
| Table | Description |
|--------|--------------|
| AGR_DEFINE | Role definitions |
| AGR_1251 | Authorization objects per role |
| AGR_PROF | Profile linked to role |
| AGR_USERS | Users assigned to roles |

### Best Practices
- Use **Z_*** naming convention for custom roles.
- Document business justification for each authorization.
- Avoid **SAP_ALL** and **SAP_NEW** except in sandbox systems.