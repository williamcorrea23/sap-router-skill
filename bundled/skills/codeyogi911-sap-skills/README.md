# SAP Skills

AI agent skills for integrating with SAP S/4HANA APIs. Each skill is a self-contained folder with a `SKILL.md` entry point and domain-specific reference files that agents load on demand.

## Skills

| Skill | Description |
|-------|-------------|
| [sap-s4hana-sales](sap-s4hana-sales/) | ~119 Sales APIs — orders, quotations, contracts, billing, returns, leads, opportunities, pricing conditions (OData V2/V4, SOAP A2A/B2B) |

## Usage

Point your agent at a skill folder and reference it by name:

```
Use $sap-s4hana-sales to create a sales order via the SAP S/4HANA OData V4 API.
```

Each skill's `SKILL.md` contains protocol guidance, an API selection guide, authentication patterns, and pointers to detailed reference files.

## Repository Structure

```
sap-skills/
├── sap-s4hana-sales/
│   ├── SKILL.md              # Entry point — protocol ref, API selection, common patterns
│   ├── agents/openai.yaml    # UI metadata
│   └── references/           # Detailed API specs loaded on demand
│       ├── sales-force-support.md
│       ├── order-contract-management.md
│       ├── pricing-and-master-data.md
│       ├── billing.md
│       ├── returns-and-claims.md
│       └── solution-business-and-index.md
└── (future: sap-s4hana-procurement/, sap-s4hana-finance/, ...)
```

## Source

API reference data extracted from the [SAP Help Portal — APIs for Sales](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/19d48293097f4a2589433856b034dfa5/3bac8c01d7024ae1b15cf848ce12544e.html) for SAP S/4HANA 2025 FPS01.
