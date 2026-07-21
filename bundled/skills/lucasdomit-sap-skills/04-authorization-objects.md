# Authorization Objects Reference

Authorization objects control granular access to data and functionality. Each object groups multiple fields.

### Example Object: S_USER_GRP
| Field | Description | Example |
|--------|--------------|----------|
| ACTVT | Activity | 01 = Create, 02 = Change, 03 = Display |
| CLASS | User Group | BASIS, FIN, SALES |

### Common Security Objects
| Object | Purpose |
|---------|----------|
| S_USER_GRP | User group maintenance |
| S_USER_AUT | Authorization profile assignment |
| S_USER_AGR | Role maintenance |
| S_TCODE | Transaction start authorization |
| S_DATASET | File access permissions |
| S_TABU_DIS | Table maintenance access |

### Activity Codes (ACTVT)
| Code | Meaning |
|-------|----------|
| 01 | Create |
| 02 | Change |
| 03 | Display |
| 06 | Delete |
| 16 | Execute |