---
name: btp-diagram-generator
description: SAP BTP Diagram Generator — generate BTP architecture diagrams from JSON specifications, landscape topology visualization, service dependency graphs, Mermaid/PlantUML output for BTP solutions. Use when creating BTP architecture diagrams, visualizing BTP solution landscapes, or generating deployment topology diagrams.
trigger:
  keywords: [BTP diagram, architecture diagram, landscape topology, service dependency, Mermaid, PlantUML, JSON specification, deployment topology, BTP solution, visualization]
  intent: >-
    Generate SAP BTP architecture diagrams from JSON specifications using Mermaid or PlantUML output.
---

# SAP BTP Diagram Generator

Generate BTP architecture diagrams from structured specifications.

## Mermaid Output

```mermaid
graph TD
  subgraph "SAP BTP - DEV Subaccount"
    CAP[CAP Application] --> HANA[(HANA Cloud)]
    CAP --> XSUAA{XSUAA Auth}
    CAP --> DEST[Destination Service]
    FIO[Fiori Elements] --> CAP
  end
  DEST --> CC[Cloud Connector]
  CC --> S4[(S/4HANA On-Premise)]
  XSUAA --> IAS[Identity Authentication]
```

## PlantUML Output

```plantuml
@startuml
!include <C4/C4_Container>
Person(user, "Business User")
System_Boundary(btp, "SAP BTP") {
  Container(cap, "CAP Service", "Node.js", "Business logic")
  ContainerDb(hana, "HANA Cloud", "HDI", "Persistence")
  Container(fiori, "Fiori Elements", "SAPUI5", "UI")
}
System_Ext(s4, "S/4HANA", "On-Premise")
Rel(user, fiori, "Uses", "HTTPS")
Rel(fiori, cap, "OData V4", "JSON")
Rel(cap, hana, "SQL", "HDI")
Rel(cap, s4, "OData", "Principal Propagation")
@enduml
```

## JSON Specification

```json
{
  "solution": "Procurement Hub",
  "subaccount": "DEV",
  "nodes": [
    { "id": "cap", "type": "application", "runtime": "Node.js CAP",
      "name": "procurement-srv" },
    { "id": "hana", "type": "database", "service": "hana-cloud",
      "name": "Procurement HDI" },
    { "id": "s4", "type": "external", "system": "S/4HANA",
      "connection": "Cloud Connector" }
  ],
  "connections": [
    { "from": "cap", "to": "hana", "protocol": "SQL", "binding": true },
    { "from": "cap", "to": "s4", "protocol": "OData V2",
      "destination": "S4HANA_DEV" }
  ]
}
```

## Generating Diagrams

```bash
# Convert JSON spec to Mermaid
python scripts/btp_diagram.py --input landscape.json --format mermaid

# Convert JSON spec to PlantUML
python scripts/btp_diagram.py --input landscape.json --format plantuml

# Render PlantUML to PNG
plantuml landscape.puml
```

## Gotchas
- Mermaid rendering limited in some tools — PlantUML is more portable
- BTP landscape diagrams should include security boundaries (XSUAA, IAS)
- Service instance names should match CF naming (lowercase, no spaces)
