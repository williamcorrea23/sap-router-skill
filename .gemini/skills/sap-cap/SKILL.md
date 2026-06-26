---
name: sap-cap
description: SAP Cloud Application Programming Model (CAP) — CDS modeling, service definitions, custom handlers, OData V4, Fiori Elements integration, SAP AI Core integration, XSUAA security, MTA deployment, hybrid testing. Use when building CAP applications, defining CDS models, writing service handlers, or deploying CAP apps to SAP BTP.
---

# SAP Cloud Application Programming Model (CAP)

Full-stack development framework for SAP BTP — CDS modeling, Node.js/Java services, Fiori UIs.

## Project Structure

```
my-cap-app/
├── db/
│   ├── schema.cds          — Data model (entities, types, annotations)
│   └── data/               — CSV seed data
├── srv/
│   ├── service.cds         — Service definitions
│   └── service.js          — Custom handlers
├── app/
│   └── risks/              — Fiori Elements UI
├── mta.yaml                — Multi-Target Application descriptor
├── package.json            — Node.js manifest
└── xs-security.json        — XSUAA auth config
```

## CDS Data Model

```cds
namespace sap.capire.risks;

entity Risks : cuid {
  title        : String(100);
  prio         : String(5) @(title: '{i18n>Priority}');
  impact       : Integer;
  criticality  : Integer;
  businessPartner : Association to BusinessPartners;
  miti         : Composition of many Mitigations on miti.risk = $self;
}

entity Mitigations : cuid {
  description : String;
  owner       : String;
  risk        : Association to Risks;
}

@cds.autoexpose
entity BusinessPartners {
  key ID : String(10);
  name   : String;
}
```

## Service Definition (srv/risk-service.cds)

```cds
using sap.capire.risks from '../db/schema';

service RiskService @(requires: 'authenticated-user') {
  entity Risks       as projection on risks.Risks;
  entity Mitigations as projection on risks.Mitigations;
  @readonly entity BusinessPartners as projection on risks.BusinessPartners;

  action analyzeRisks() returns Risks;
}
```

## Custom Handler (srv/risk-service.js)

```javascript
const cds = require('@sap/cds')

module.exports = class RiskService extends cds.ApplicationService {
  async init() {
    this.before('CREATE', 'Risks', (req) => {
      req.data.criticality = Math.ceil(req.data.impact / 20) * 20
    })

    this.on('analyzeRisks', async (req) => {
      const risks = await cds.run(SELECT.from('Risks'))
      for (const risk of risks) {
        risk.title = risk.title.toUpperCase()
        await cds.run(UPDATE.entity('Risks').set({title: risk.title}).where({ID: risk.ID}))
      }
      return risks
    })

    await super.init()
  }
}
```

## Fiori Elements UI

```cds
// app/risks/annotations.cds
using RiskService as service from '../../srv/risk-service';

annotate service.Risks with @(
  UI: {
    LineItem: [
      { $Type: 'UI.DataField', Value: title },
      { $Type: 'UI.DataField', Value: prio },
      { $Type: 'UI.DataField', Value: criticality,
        Criticality: criticality }
    ],
    SelectionFields: [ title, prio ],
    HeaderInfo: {
      TypeName: 'Risk', TypeNamePlural: 'Risks',
      Title: { Value: title }
    }
  }
);
```

## Hybrid Testing

```bash
cds bind -2 my-hdi,my-xsuaa  # bind local dev to BTP services
cds watch --profile hybrid    # local server + BTP backends
```

## Deployment (MTA)

```bash
mbt build
cf deploy mta_archives/risks_1.0.0.mtar
```

## Gotchas
- cuid aspect auto-generates UUID key + managed fields
- @cds.autoexpose makes the entity available in all services
- @readonly restricts entity to GET only
- Hybrid profile: local CDS runtime + BTP HANA + BTP XSUAA
