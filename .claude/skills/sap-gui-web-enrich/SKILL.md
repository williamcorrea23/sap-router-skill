---
name: sap-gui-web-enrich
description: Auto-fills missing SAP GUI transaction navigation data (field IDs, screen numbers, BDC sequences) by searching web sources
trigger:
  keywords: [gui missing field, transaction navigation unknown, enrich gui data, find transaction fields, bdc recording missing, screen sequence lookup, gui enrichment]
  intent: Enriching missing SAP GUI transaction navigation data from web sources
---

# SAP GUI Web Enrich — Auto-Fill Missing Navigation Data

When GUI fallback triggers but transaction navigation data is incomplete,
this skill auto-searches the web to fill gaps — then caches results.

## Prerequisites

- SAP GUI Scripting enabled on target system (`RFCNO_SCR 1` in `RZ11`)
- `sap-gui-scripting` skill loaded for execution after enrichment
- Web search tool available (SAP Help Portal, SAP Community, GitHub)
- No real customer data in search queries — use generic field names only

## Workflow

```
GUI Fallback Triggered → Check local cache (MEMORY.md)
  ├─ HIT  → Execute GUI navigation immediately
  └─ MISS → Run enrichment steps below → Cache → Execute
```

## Steps

### 1. Check Local Cache

```bash
grep -A5 "GUI_DATA" MEMORY.md
```

If the transaction is listed with `confidence=HIGH`, skip to `sap-gui-scripting`.

### 2. Search SAP Help Portal (Authoritative)

```
WebSearch: "{tcode} SAP transaction screen fields" site:help.sap.com
WebFetch:  https://help.sap.com/docs/SAP_S4HANA_CLOUD/{version}/...
```

Extract: screen program names, field IDs, OK codes, view selections.

### 3. Search SAP Community (Practical Examples)

```
WebSearch: "{tcode} BDC recording ABAP example" site:community.sap.com
```

Cross-reference field IDs found in Step 2. Require 2+ independent sources
for HIGH confidence.

### 4. Search GitHub (Real ABAP Code)

```
WebSearch: "{tcode} CALL TRANSACTION OR BDC_OPEN_GROUP" language:abap
```

Look for `CALL TRANSACTION` or `BDC_INSERT` calls — extract dynpro
sequences and field mappings.

### 5. Search SAP Notes (Known Issues)

```
mcp-sap-notes: search "{tcode} screen sequence field ID"
```

Check for version-specific field ID changes (ECC vs S/4HANA).

### 6. Build Enriched BDC Map

```python
# Output structure after enrichment
BDC_MAP = {
    'transaction': 'MM01',
    'source': 'help.sap.com + community.sap.com + github.com',
    'confidence': 'HIGH',  # 3+ independent sources verified
    'sap_version': 'S/4HANA 2023',
    'steps': [
        {
            'screen': 'SAPLMGMM 0060',
            'fields': {'RMMG1-MATNR': True, 'RMMG1-MBRSH': True},
            'okcode': '=ENTE',
        },
    ],
    'warnings': ['Field IDs vary between ECC and S/4HANA'],
}
```

### 7. Cache in MEMORY.md

```bash
# Append to GUI_DATA section
echo "- MM01: enriched=2026-07-02 confidence=HIGH sources=3 steps=5 version=S4HANA2023" >> MEMORY.md
```

### 8. Hand Off to sap-gui-scripting

Return enriched data to `sap-gui-scripting` skill for execution.

## CLI Integration

```bash
# Enrich specific transaction
python scripts/sap_router.py gui-enrich --tcode MM01

# Enrich all transactions for a module
python scripts/sap_router.py gui-enrich --module MM

# Check enrichment status
python scripts/sap_router.py gui-enrich --status

# Force re-enrich (ignore cache)
python scripts/sap_router.py gui-enrich --tcode MM01 --force
```

## Fallback Chain

1. **Local cache** (MEMORY.md `GUI_DATA`) → instant
2. **SAP Help Portal** → authoritative, ~2s
3. **SAP Community** → practical examples, ~3s
4. **GitHub code search** → real ABAP code, ~5s
5. **SAP Notes** → known issues, ~2s
6. **Manual recording** → instruct user to run `SHDB` in SAP

## Pitfalls

- **Web search returns wrong SAP version field IDs**
  - Cause: ECC and S/4HANA use different dynpro field names for the same screen.
  - Solution: Tag every cached entry with `sap_version`. Force re-enrich after upgrades (`--force`).

- **BDC fails after enrichment with "field not found"**
  - Cause: Web source documented a screen variant that doesn't match the target system's configuration.
  - Solution: Verify field existence with `mcp_rfc_read_table` on `DD03L` for the screen's table. Fall back to SHDB manual recording.

- **Rate limiting during batch enrichment**
  - Cause: WebSearch tool enforces rate limits; enriching a full module triggers too many calls.
  - Solution: Stagger requests 2s apart. Use `--module` flag which batches internally.

- **Sensitive data leaked in search queries**
  - Cause: User includes real material numbers or customer names in search terms.
  - Solution: Never search with real data. Use generic descriptions only (e.g., "material number field" not "MATNR 1000001234").

- **Cache stale after SAP support package applied**
  - Cause: Support packages can change screen sequences and field IDs.
  - Solution: Re-enrich after any SP update. Set `confidence=STALE` automatically on SP changes if monitoring is configured.

## Verification

- [ ] Enriched data has 2+ independent web sources (HIGH confidence)
- [ ] Every field ID verified against `DD03L` table or SAP Help Portal
- [ ] BDC map includes OK code for each screen
- [ ] Cache entry tagged with SAP version and enrichment date
- [ ] Test execution with `sap-gui-scripting` completes without "field not found"
- [ ] No real customer data appears in any search query or cached output
