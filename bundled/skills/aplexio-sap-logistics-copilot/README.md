# sap-logistics-copilot

Claude Code skill pack for SAP logistics teams. Paste an SAP export, get the root cause in seconds.

## What's inside (v1)

| Skill | Triggers on | Output |
|---|---|---|
| `idoc-error-translator` | WE02 / WE05 IDoc error output | Plain-English cause, resolution steps, related SAP Notes |
| `delivery-blocker-diagnoser` | VL06O / SD delivery list | Per delivery: block cause, owner, resolution |
| `stock-discrepancy-explainer` | MB52 / MMBE stock list | Ranked root causes, TCodes to investigate |
| `freight-cost-reviewer` | TM shipment cost / freight invoice | Anomaly flags, recovery estimates |
| `overdue-invoice-auditor` | MR8M / FBL3N open invoices | Triaged buckets, owner, action per item |

All five skills share a common 4-section output contract (see `templates/output-contract.md`).

## Install (for SAP consultants using Claude Code)

```
npx skills add aplexio/sap-logistics-copilot --agent claude-code -y
```

Open Claude Code in any directory where the pack is installed, then paste an SAP export. Claude auto-selects the matching skill based on the content.

## For SAP customer teams (no Claude Code required)

See walkthroughs, demos, and guided examples at
**https://www.aplexio.com/ai-assistance/sap-logistics-copilot**

## Paid offerings

Need the pack tuned to your SAP landscape, wired into your systems, or extended with process-specific skills?

- **Custom Skill Build** — 3–4 skills tailored to your SAP configuration. 2-week turnaround. €5k–€10k.
- **SAP + AI Integration Sprint** — 2-week engagement: MCP integration, custom skills, team training. €15k–€25k.

Contact: **https://www.aplexio.com/ai-assistance/sap-logistics-copilot**

## Status

v1 in development. Skills ship one at a time — see commit history for the current state.

## License

MIT.
