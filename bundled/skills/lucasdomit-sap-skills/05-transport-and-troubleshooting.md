# Transport Management & Troubleshooting

### Role Transport Flow
1. Create or modify role in **Development (DEV)** system.
2. Include role in transport request via PFCG → Transport → Add to Request.
3. Release request in SE10 or STMS.
4. Import into **Quality (QAS)** and **Production (PRD)** systems.

### Logs and Tools
| Tool | Purpose |
|-------|----------|
| SCUL | User change logs |
| SUIM | User information and analysis |
| ST22 | Dumps (short error analysis) |
| SM21 | System log |
| SU53 | Authorization check for last failed action |

### Troubleshooting
- **Error:** “No authorization to execute transaction” → Check S_TCODE and S_USER_AGR.
- **Profile not active:** Regenerate role (PFCG → Authorizations → Generate).
- **User missing role after transport:** Perform user comparison (PFCG → User tab → User Comparison).