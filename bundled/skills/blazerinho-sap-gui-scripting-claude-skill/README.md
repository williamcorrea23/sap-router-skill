# SAP GUI Scripting Skill for Claude Code

A Claude Code skill for automating SAP GUI using Python and the SAP GUI Scripting API (`win32com.client`).

## What this skill does

When installed, Claude Code gains specialised knowledge for:

- Connecting to a running SAP GUI session from Python
- Finding and interacting with SAP screen controls (`findById`)
- Handling SAP-specific error patterns (COM exceptions, session synchronisation, modal popups)
- Extracting data from ALV grids and classic table controls
- Automating SE16H queries for data analytics (BKPF, BSEG, BSET, and other FI tables)
- Structuring reusable, production-ready SAP automation scripts

## Prerequisites

- Windows (SAP GUI Scripting API is Windows-only via COM)
- SAP GUI for Windows installed and logged in
- SAP GUI Scripting enabled: `Customize Local Layout (Alt+F12) → Scripting → Enable Scripting`
- Python packages: `pywin32`, `pandas`, `openpyxl`

```bash
pip install pywin32 pandas openpyxl
```

## Installation

### Claude.ai (Settings → Capabilities)

1. Download `sap-gui-scripting.zip` from this repository (Code → Download ZIP, or use the Releases page)
2. Go to **Settings → Capabilities → Skills**
3. Click **Upload skill** and select the ZIP file

### Claude Code (CLI)

Copy the skill folder to your global Claude skills directory:

```bash
# Windows (PowerShell)
Copy-Item -Recurse sap-gui-scripting "$env:USERPROFILE\.claude\skills\sap-gui-scripting"

# macOS / Linux
cp -r sap-gui-scripting ~/.claude/skills/sap-gui-scripting
```

Or for a single project, place it in the project's `.claude/skills/` folder.

### Via npx openskills (if you use the openskills CLI)

```bash
npx openskills install blazerinho/sap-gui-scripting-skill --global
```

## Usage

Once installed, Claude Code will automatically use this skill when you ask SAP GUI scripting questions. You can also invoke it directly:

```
/sap-gui-scripting
```

Example prompts that trigger this skill:

- *"Write a Python script to extract all BKPF documents for company code 1000 from SE16H"*
- *"How do I handle a SAP popup dialog in my automation script?"*
- *"My findById call is failing intermittently — how do I fix it?"*
- *"Create a reusable function to connect to a SAP GUI session"*
- *"Script SE16H to query BSEG for a specific GL account range"*

## Skill structure

```
sap-gui-scripting/
├── SKILL.md                          # Main skill — session setup, error handling,
│                                     # dialog handling, table extraction, SE16H patterns,
│                                     # script template, key behaviours
└── references/
    ├── se16h-reference.md            # SE16H field IDs, BKPF/BSEG/BSET query patterns,
    │                                 # deferred tax analytics, export patterns
    └── advanced-patterns.md          # Batch processing, multi-transaction workflows,
                                      # clipboard extraction, logging
```

## ⚠️ Important: Validate control IDs in your system

SAP GUI control IDs, field names, and menu paths **vary between SAP releases, screen variants, and client configurations**. The patterns in this skill are based on standard ECC 6.0 / S/4HANA behaviour, but you must verify them in your own system before using in production.

**How to verify:**
1. Open SAP GUI and navigate to the transaction you want to automate
2. Go to `Customize Local Layout (Alt+F12) → Script Recording and Playback`
3. Record your manual steps
4. Open the generated `.vbs` file — the `findById(...)` paths are your correct IDs

Sections in the skill that require system-specific validation are marked with `[VERIFY IN YOUR SYSTEM]`.

## SAP version compatibility

| SAP Release | Status |
|-------------|--------|
| SAP ECC 6.0 | ✅ Patterns validated |
| S/4HANA (on-premise) | ✅ Core patterns apply |
| S/4HANA Cloud | ⚠️ SAP GUI Scripting may be restricted — check with your admin |
| SAP GUI 7.60+ | ✅ Tested |
| SAP GUI 7.40 and earlier | ⚠️ Some ALV grid API differences — verify |

## Contributing

This skill is a community resource. If you discover control IDs, patterns, or fixes that differ from what's documented here — especially for specific SAP releases or transactions — please open a PR or issue. The goal is to build the most complete public reference for SAP GUI scripting with AI assistance.

Areas where contributions are especially welcome:
- SE16H aggregation scripting (field selection dialog navigation)
- ALV grid export via local menu (menu paths vary by release)
- S/4HANA-specific patterns
- Additional transaction patterns (FB03, FK03, ME23N, etc.)

## Disclaimer

This skill is a community contribution and is not affiliated with, endorsed by, or supported by SAP SE or Anthropic. SAP GUI Scripting API usage is subject to your SAP licence agreement. The skill uses only the public SAP GUI Scripting API as documented in SAP's official scripting guide.

## License

Apache 2.0 — see [LICENSE](LICENSE)
