---
name: sap-smartform-generator
description: SAP Smart Form (SSFO) generation skill — document analysis (PDF/DOCX/XLSX/HTML), FormSpec validation, SSFO XML generation, ABAP OO driver creation, layout preview comparison, and dry-run deployment safeguards.
---

# SAP Smart Form AI Generator Skill

Specialized skill for document-driven SAP Smart Form (SSFO) creation, FormSpec validation, ABAP driver program generation, and fail-closed deployment governance.

## Execution Workflow

1. **Analyze Source Document**: Read PDF, DOCX, XLSX, or HTML using `analyze_document`. Extract layout, text blocks, table grids, headers, and footers.
2. **Present Visual Inventory**: Display extracted sections, separating static text from candidate dynamic ABAP fields.
3. **Generate Intermediate FormSpec**: Call `create_formspec` to synthesize the `FormSpec` JSON model.
4. **Human Review Gate**: Highlight inferred fields with confidence score < 0.95 or `requires_review = true`. Solicit human confirmation for ambiguous field mappings.
5. **Validate FormSpec**: Execute `validate_formspec` to ensure ABAP 7.40 naming compliance (max 30 chars), MAIN window presence, and DDIC consistency.
6. **Generate Smart Form Package**: Run `generate_smartform_package` to produce:
   - Validated SSFO XML (`abapGit` compatible serializer)
   - Modular ABAP 7.40 OO driver program (`SSF_FUNCTION_MODULE_NAME`)
   - DDIC structure & table type specifications
   - abapGit object payload files
7. **Preview & Layout Comparison**: Run `compare_preview` to generate HTML/JSON layout match reports comparing the source document against the FormSpec layout.
8. **Deployment Governance (Fail-Closed)**:
   - Default mode is **dry-run** (`dry_run=True`).
   - Deployment requires `confirmed=True`, `target_system="DEV"`, valid package & CTS transport ID, zero unresolved review flags, and a valid token from `approval_broker.py` for capability `sap.smartform.deploy`.
   - Never auto-deploy or release transports to QAS or PRD.

## Available MCP Tools

- `analyze_document(path, extract_images, ocr)`
- `create_formspec(document_analysis, form_name, target_package)`
- `validate_formspec(formspec_dict)`
- `generate_smartform_package(formspec_dict)`
- `inspect_existing_smartform(form_name)`
- `deploy_smartform(form_name, ssfo_xml, package, transport, target_system, dry_run, confirmed)`
- `compare_preview(document_analysis, formspec_dict)`

## CLI Reference Validation Script

Validate FormSpec JSON files offline:

```powershell
python .agents/skills/sap-smartform-generator/scripts/validate_formspec.py --input path/to/formspec.json
```
