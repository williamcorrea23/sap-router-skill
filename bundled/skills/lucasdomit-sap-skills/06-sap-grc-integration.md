# SAP GRC Access Control Integration

SAP GRC (Governance, Risk & Compliance) enhances native SAP security by automating risk analysis and access requests.

## Key Modules
- **Access Risk Analysis (ARA):** Detects SoD (Segregation of Duties) conflicts.
- **Access Request Management (ARM):** Workflow for user creation and role assignment.
- **Emergency Access Management (EAM):** Firefighter access for critical activities.
- **Business Role Management (BRM):** Centralized role repository.

### Risk Remediation Workflow
1. User submits access request (ARM).  
2. System evaluates via ARA against SoD ruleset.  
3. Approvers validate or reject.  
4. Mitigating controls applied if accepted.

### Common Integration Tables
| Table | Description |
|--------|--------------|
| GRACROLE | Business role definition |
| GRACUSERCONN | User connection mapping |
| GRACACTRULE | Action rules (workflow logic) |