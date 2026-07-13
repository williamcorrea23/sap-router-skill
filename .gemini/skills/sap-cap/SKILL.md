---
name: sap-cap
description: >-
  SAP Cloud Application Programming Model (CAP) — CDS modeling, service
  definitions, custom handlers, OData V4, Fiori Elements, hybrid testing,
  MTA deployment. Use when building CAP apps, defining CDS models, writing
  service handlers, or deploying to SAP BTP.
trigger: cap, cds, cloud application programming model, cds watch, cds init, ApplicationService, cds bind, mta.yaml, Fiori elements CAP, @sap/cds
---

# SAP Cloud Application Programming Model (CAP)

Full-stack framework for SAP BTP — CDS modeling, Node.js services, Fiori UIs.

## Prerequisites

- Node.js ≥ 18 and npm ≥ 7
- `@sap/cds-dk` installed globally: `npm i -g @sap/cds-dk`
- Cloud Foundry CLI (`cf`) for deployment
- MBT build tool: `npm i -g mbt`

## 1. Create Project

```bash
cds init my-cap-app --add sample,hana
cd my-cap-app
npm install
```

Project layout:

```
my-cap-app/
├── db/schema.cds        # Data model
├── db/data/             # CSV seed data
├── srv/service.cds      # Service definitions
├── srv/service.js       # Custom handlers
├── app/                 # Fiori Elements UIs + annotations
├── mta.yaml             # MTA descriptor (cds add mta)
└── package.json
```

## 2. Define Data Model (db/schema.cds)

```cds
namespace sap.capire.risks;

entity Risks : cuid, managed {
  title           : String(100);
  prio            : String(5);
  impact          : Integer;
  criticality     : Integer;
  miti            : Composition of many Mitigations on miti.risk = $self;
}

entity Mitigations : cuid, managed {
  description : String;
  owner       : String;
  risk        : Association to Risks;
}
```

## 3. Define Service (srv/risk-service.cds)

```cds
using sap.capire.risks from '../db/schema';

service RiskService @(requires: 'authenticated-user') {
  entity Risks       as projection on risks.Risks;
  entity Mitigations as projection on risks.Mitigations;

  action analyzeRisks() returns Risks;
}
```

## 4. Implement Custom Handler (srv/risk-service.js)

```javascript
const cds = require('@sap/cds')

module.exports = class RiskService extends cds.ApplicationService {
  async init() {
    const { Risks } = this.entities

    // Validate before create
    this.before('CREATE', Risks, (req) => {
      req.data.criticality = Math.ceil(req.data.impact / 20) * 20
    })

    // Custom action
    this.on('analyzeRisks', async (req) => {
      return UPDATE(req.subject).with({ title: { '=': req.data.title } })
    })

    // After-read enrichment
    this.after('READ', Risks, (rows) => {
      rows.forEach(r => { if (r.impact > 80) r.criticality = 1 })
    })

    return super.init()
  }
}
```

## 5. Add Fiori Annotations (app/risks/annotations.cds)

```cds
using RiskService as service from '../../srv/risk-service';

annotate service.Risks with @(
  UI: {
    SelectionFields: [ title, prio ],
    LineItem: [
      { $Type: 'UI.DataField', Value: title },
      { $Type: 'UI.DataField', Value: prio },
      { $Type: 'UI.DataField', Value: criticality, Criticality: criticality }
    ],
    HeaderInfo: {
      TypeName: 'Risk', TypeNamePlural: 'Risks',
      Title: { Value: title }
    }
  }
);
```

## 6. Run Locally

```bash
cds watch                    # SQLite, auto-reload on file change
# Visit http://localhost:4004
```

## 7. Hybrid Testing (local server + BTP HANA/XSUAA)

```bash
cds add hana,xsuaa,mta --for production
cf deploy mta_archives/risks_1.0.0.mtar   # deploy once to create services
cds bind -2 my-hdi,my-xsuaa               # bind local dev to BTP services
cds watch --profile hybrid                 # local runtime + cloud backends
```

## 8. Deploy to Cloud Foundry

```bash
cds add mta                 # generate mta.yaml if not present
mbt build -t gen/mta.tar
cf deploy gen/mta.tar
# Or simplified: cds up  (builds + deploys in one step)
```

## Pitfalls

- **`cds run` deprecated** — *Cause:* cds 8+ removed the `cds` executable from `@sap/cds`. *Solution:* use `cds-serve` in npm scripts: `npm pkg set scripts.start="cds-serve"`.

- **Cross-tenant data leak** — *Cause:* caching request-scoped data in module-level variables. *Solution:* use `cds.context` or keep state inside the handler closure.

- **XSUAA scopes not updated** — *Cause:* changing `@requires` annotations doesn't auto-update `xs-security.json`. *Solution:* re-run `cds compile --to xsuaa` after auth annotation changes.

- **`cuid` adds UUID key** — *Cause:* `:cuid` aspect auto-generates a `String(36)` UUID key. *Solution:* don't manually define `key ID` when using `cuid`; it's already included.

- **`@readonly` blocks writes** — *Cause:* `@readonly` restricts entity to GET only. *Solution:* remove annotation or use `@insertonly` / `@updatable` for partial access.

- **Hybrid profile missing bindings** — *Cause:* `cds bind` saves to `.cdsrc-private.json` which isn't committed. *Solution:* re-run `cds bind -2 <service>` after cloning the repo.

## Verification

```bash
# 1. Check model compiles
cds compile srv/risk-service.cds -2 edmx

# 2. Verify local server responds
curl http://localhost:4004/odata/v4/risk/Risks?$top=5

# 3. Check service endpoints
cds eval 'cds.served["RiskService"].endpoints'

# 4. Validate MTA descriptor
mbt build -t gen/mta.tar && cf deploy gen/mta.tar --dry-run

# 5. Confirm Fiori annotations render
# Open http://localhost:4004/risks/webapp/index.html
```
