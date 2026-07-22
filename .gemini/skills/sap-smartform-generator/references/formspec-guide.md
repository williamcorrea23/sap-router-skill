# FormSpec Specification & Schema Guide

`FormSpec` is an intermediate JSON model that bridges raw document parsing (PDF, DOCX, XLSX, HTML) and SAP Smart Form SSFO XML generation.

## Key Sections

- `form`: Name (Z*/Y* max 30 chars), description, language ("E"), target package ("$TMP" or "Z*").
- `page`: Format ("DINA4", "DINA5", "LETTER"), orientation ("PORTRAIT", "LANDSCAPE"), margins in mm.
- `interface`: Import parameters, export parameters, tables (e.g., `IT_ITEMS` -> `ZSF_T_ITEM`), changing parameters.
- `global_definitions`: Global ABAP data declarations, types, initialization code, form routines.
- `windows`: Window node list. Must contain at least one `MAIN` window for multi-page document overflow.
- `inferred_fields`: List of candidate fields with `confidence` scores (0.0 to 1.0) and `requires_review` flags.
- `warnings`: Operational and parsing notices.
