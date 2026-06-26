---
name: btp-business-application-studio
description: SAP Business Application Studio (BAS) — dev spaces, CAP project creation, Fiori tools integration, debugger setup, terminal access, extension management, BTP service integration in BAS, source control (git), deployment workflows. Use when working in BAS, creating dev spaces, configuring extensions, or troubleshooting BAS connectivity.
---

# SAP Business Application Studio (BAS)

Cloud IDE on SAP BTP for CAP, Fiori, and full-stack development. Browser-based, no local install needed.

## Dev Space Types

| Type | Pre-installed Extensions | Best For |
|---|---|---|
| Full Stack Cloud Application | CAP, CDS, Fiori tools, MTA tools | CAP + Fiori apps |
| SAP Fiori | Fiori tools, SAPUI5 Adaptation | Freestyle UI5, Fiori adaptation |
| SAP HANA Native Application | HANA tools, DB explorer, HDI | HANA DB artifacts |
| Basic | None | Custom setup, non-SAP languages |

## Creating Dev Spaces

1. BAS → Create Dev Space
2. Choose type (Full Stack for CAP + Fiori)
3. Choose extensions (defaults OK)
4. Start → wait ~2 min → open

## Project Creation Flow

```bash
# From BAS terminal — CAP project
cd /home/user/projects
cds init my-app --add java,nodejs,mta,fiori,sample

# Fiori from template
# BAS → Start from Template → Choose floorplan → Select OData service → Configure

# Clone existing
git clone https://github.com/myorg/my-cap-app.git
```

## Service Integration

```
BAS → SAP BTP Destination service → SAP S/4HANA / other backend
     → run configuration with hybrid profile
```

### Hybrid Testing

```bash
cds bind -2 my-hdi-container,my-xsuaa    # bind to BTP services
cds watch --profile hybrid               # local runtime + BTP backends
```

## Debugger

1. Open .js handler file in BAS
2. Set breakpoint by clicking line gutter
3. F5 → select "CDS with Node.js" debug configuration
4. Step through: F10 (step over), F11 (step into), Shift+F11 (step out)

## Terminal Commands

```bash
cds build          # compile CDS → CSN/EDMX/SQL
cds watch          # auto-reload dev server
mbt build          # build MTA archive
cf login -a https://api.cf.us10.hana.ondemand.com
cf deploy mta_archives/my-app.mtar
git push origin main
```

## Gotchas

- **Dev space idle timeout**: 30 min — stops automatically. Save work before leaving
- **10GB per dev space**: large node_modules may need pruning
- **Only one running dev space** on free-tier subaccounts
- **Internet required**: no offline mode — BAS is cloud-hosted
- **Extensions from Open VSX Registry**: SAP extensions auto-installed, custom ones must be added manually
