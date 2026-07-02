---
name: btp-business-application-studio
description: >
  SAP Business Application Studio (BAS) — dev spaces, CAP project creation, Fiori tools,
  debugger setup, hybrid testing, deployment workflows, source control. Use when working
  in BAS, creating dev spaces, configuring extensions, or troubleshooting BAS connectivity.
trigger:
  - "create BAS dev space"
  - "create CAP project in BAS"
  - "debug CAP application in BAS"
  - "deploy from BAS to BTP"
  - "configure BAS extensions"
  - "hybrid testing in BAS"
---

# SAP Business Application Studio (BAS)

Cloud IDE on SAP BTP for CAP, Fiori, and full-stack development. Browser-based, no local install needed.

## Prerequisites

- SAP BTP subaccount with **SAP Business Application Studio** entitlement
- Subscribed to BAS app (BTP Cockpit → Service Marketplace → Subscribe)
- Space Quota with sufficient memory (min 4 GB for dev space)
- Cloud Foundry CLI installed locally for `cf` commands outside BAS
- GitHub/GitLab account or SAP Git repository for source control

## Dev Space Types

| Type | Key Extensions | Best For |
|---|---|---|
| Full Stack Cloud Application | CAP, CDS, Fiori tools, MTA | CAP + Fiori apps |
| SAP Fiori | Fiori tools, UI5 Adaptation | Freestyle UI5, adaptation |
| SAP HANA Native | HANA tools, DB Explorer, HDI | HANA DB artifacts |
| Basic | None (manual install) | Custom setup, non-SAP |

## Steps

### 1. Create a Dev Space

1. Open BTP Cockpit → **Service Marketplace** → **SAP Business Application Studio** → **Go to Application**
2. Click **Create Dev Space** → Enter name
3. Select type: **Full Stack Cloud Application** (for CAP + Fiori)
4. Optionally add extensions (defaults are sufficient for most workflows)
5. Click **Create** → wait ~2 min → status shows **RUNNING**
6. Click dev space name to open the IDE in browser

### 2. Create a CAP Project

```bash
# In BAS terminal (Terminal → New Terminal)
cd /home/user/projects
cds init my-app --add java,nodejs,mta,fiori,sample
cd my-app
npm install

# Create Fiori app from template
# Use View → Find Command → "Fiori: Open Application Generator"
# Choose floorplan (List Report, Object Page, etc.)
# Select OData service → Configure → Generate
```

### 3. Clone an Existing Project

```bash
cd /home/user/projects
git clone https://github.com/myorg/my-cap-app.git
cd my-cap-app
npm install
```

### 4. Hybrid Testing with BTP Services

Bind local CAP runtime to BTP-backed services (HDI, XSUAA, destination) for realistic testing:

```bash
# Bind to running BTP service instances
cds bind -2 my-hdi-container,my-xsuaa

# Start dev server with hybrid profile
cds watch --profile hybrid

# Test endpoint locally — hits real BTP backends
curl http://localhost:4004/odata/v4/catalog/Books
```

### 5. Set Up the Debugger

1. Open the `.js` or `.ts` handler file in BAS editor
2. Click the gutter next to a line number to set a breakpoint (red dot)
3. Press `F5` → select debug configuration: **CDS with Node.js**
4. Debugger pauses at breakpoint — use:
   - `F10`: Step Over
   - `F11`: Step Into
   - `Shift+F11`: Step Out
   - `F5`: Continue
5. Watch variables in the left panel; use Console for expressions

### 6. Build and Deploy

```bash
# Compile CDS → CSN/EDMX/SQL
cds build

# Build MTA archive
mbt build

# Deploy to Cloud Foundry
cf login -a https://api.cf.us10.hana.ondemand.com -o <org> -s <space>
cf deploy mta_archives/my-app_1.0.0.mtar

# Push to git
git add -A && git commit -m "feat: initial CAP app"
git push origin main
```

## Pitfalls

| Cause | Solution |
|---|---|
| Dev space stopped unexpectedly | Dev spaces auto-stop after 30 min idle. In BAS launcher, click **Start** to resume. Work is preserved. |
| `cds bind` fails with "service not found" | Service instances must exist in the current CF space. Run `cf services` to verify. Create missing instances with `cf create-service`. |
| Large node_modules exceeds 10 GB limit | Dev spaces have 10 GB storage. Run `npm prune --production` or delete `.cache/` dir. Use `npm ci` instead of `npm install` for deterministic builds. |
| Only one dev space running | Free-tier subaccounts allow only 1 running dev space. Stop others before starting a new one. |
| Extension not found in marketplace | BAS uses the Open VSX Registry, not the VS Code Marketplace. Install custom extensions from `.vsix` files via Extensions → `...` → **Install from VSIX**. |
| `mbt build` fails — Makefile not found | Run `cds add mta` first to generate the `mta.yaml` and Makefile. Ensure `mbt` CLI is installed: `npm install -g mbt`. |
| Debugger won't attach | Ensure `cds watch` is not already running on the same port. Stop it, then start via `F5` debug config. Check `.vscode/launch.json` exists. |

## Verification

```bash
# Dev space is running
# (Check in BAS launcher — status should be "RUNNING")

# CAP project structure is valid
cds compile srv/ -2 sql 2>&1 | head -5   # No errors = valid model

# Dev server responds
curl -s http://localhost:4004/odata/v4/catalog/$metadata | head -3

# MTA archive built
ls -la mta_archives/*.mtar               # Should show .mtar file

# Deployment succeeded
cf apps                                  # App should show "started" state
curl -s https://my-app.cfapps.<region>.hana.ondemand.com/odata/v4/catalog/$metadata | head -3

# Git push succeeded
git log --oneline -3                      # Shows recent commits
git status                                # Shows "up to date"
```

Checklist:
- [ ] Dev space shows status **RUNNING** in BAS launcher
- [ ] `cds watch` serves OData endpoint at `localhost:4004`
- [ ] Hybrid binding resolves real BTP service instances
- [ ] Breakpoints hit correctly in debugger
- [ ] `mbt build` produces `.mtar` without errors
- [ ] `cf deploy` completes with all modules started
- [ ] Git repository is up to date (`git status` clean)
