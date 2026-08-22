---
name: sap-smartform-generator
description: Generate, edit, reconstruct, validate, preview, and safely deploy SAP Smart Forms (SSFO) from PDF, DOCX, XLSX, HTML, or an existing SAP form. Use for AI-assisted document-to-FormSpec extraction, native Smart Forms XML round-trips, ABAP driver generation, abapGit packaging, layout-parity review, activation checks, and governed DEV deployment.
---

# SAP Smart Form AI Generator

Create or edit Smart Forms through a fail-closed, evidence-based workflow. Treat generated XML, previews, mocks, and passing local tests as candidates—not proof that SAP can import, activate, or render the form.

## Required references

- Read [repository-implementation-patterns.md](references/repository-implementation-patterns.md) before generating, importing, or deploying SSFO XML.
- Read [formspec-guide.md](references/formspec-guide.md) when creating or repairing a FormSpec.
- Read [smartform-node-mapping.md](references/smartform-node-mapping.md) before mapping visual elements to a native SAP export.

## Non-negotiable rules

1. Use one canonical form name everywhere: FormSpec, native XML, ABAP driver, package metadata, tests, and transport.
2. Prefer editing a native XML export produced by SAP or abapGit from the target SAP release. Do not invent a generic `<abapGit><SF>` or `<SSFO>` schema and call it importable.
3. Require the Smart Forms namespace `urn:sap-com:SmartForms:2000:internal-structure` and a `SMARTFORM` root for a native candidate.
4. Preserve release-specific topology, node IDs/references, namespaces, language, and code sections. Normalize volatile metadata only with the abapGit pattern.
5. Keep AI extraction schema-constrained. Send every uncertain field mapping (`confidence < 0.95` or `requires_review`) to human review.
6. Use ARC-1 for supported ADT reads/writes, ABAP driver work, and transport evidence. Do not claim ARC-1 imports SSFO unless a reviewed custom tool proves that capability.
7. Never report deployment success from a mock, dry-run, local XML parse, or HTML preview.
8. Never deploy or release transports to QAS or PRD. Default to dry-run and require explicit approval for DEV mutation.

## Workflow

1. **Analyze the source**: Run `analyze_document` for PDF, DOCX, XLSX, or HTML. Extract page geometry, text, images, tables, headers, footers, and repeated regions.
2. **Inventory the layout**: List every visible section and classify it as static text, dynamic field, table/loop, graphic, condition, page command, or unresolved element.
3. **Acquire a native baseline**: Inspect the existing form and export it from the target SAP release through SAP/abapGit. If no same-form export exists, use a minimal active form exported from the same system/release as the structural baseline.
4. **Create FormSpec**: Run `create_formspec`. Preserve source coordinates and review flags in the analysis evidence; use FormSpec only for supported semantic fields.
5. **Review and validate**: Resolve ambiguous mappings, then run `validate_formspec` and the offline validator. Stop on schema, DDIC, naming, or MAIN-window errors.
6. **Generate by native transformation**: Apply the approved FormSpec to the native baseline. Preserve SAP-owned structure and use the abapGit SSFO serializer behavior for round-trip compatibility.
7. **Validate the artifact**: Run `validate_native_ssfo.py`. Reject custom wrappers, inconsistent names, missing MAIN window, forbidden template residue, placeholders, or mojibake requiring review.
8. **Generate and lint the driver**: Use ABAP 7.40-compatible code, `SSF_FUNCTION_MODULE_NAME`, explicit interface mapping, BAPI return handling, and deterministic exception reporting.
9. **Inspect and deploy in DEV**: Keep `dry_run=True` until package, transport, approval token, zero review flags, and a real import adapter are proven. Import with the SAP/abapGit `XML_UPLOAD` and active `STORE` lifecycle or an equivalent reviewed adapter.
10. **Prove activation**: Verify existence and active status in SAP, resolve the generated function module, execute with representative data, and capture the spool/PDF.
11. **Prove visual parity**: Compare rendered pages, geometry, fonts, borders, colors, logos, images, line wrapping, pagination, and dynamic overflow. A table-count or HTML-only score is insufficient.

## Capability contracts

Use these tools only when they are actually registered and healthy:

- `analyze_document(path, extract_images, ocr)`
- `create_formspec(document_analysis, form_name, target_package)`
- `validate_formspec(formspec_dict)`
- `generate_smartform_package(formspec_dict, native_baseline)`
- `inspect_existing_smartform(form_name)`
- `deploy_smartform(form_name, ssfo_xml, package, transport, target_system, dry_run, confirmed)`
- `compare_preview(document_analysis, formspec_dict, rendered_pdf)`

If a tool is planned, mocked, missing a persistent MCP transport, or lacks a real SAP adapter, stop at artifact generation and report the limitation.

## Fail-closed deployment gate

Require all of the following before a DEV mutation:

- `confirmed=True`, `target_system="DEV"`, valid package, and valid CTS transport;
- approval token for capability `sap.smartform.deploy`;
- zero unresolved field, placeholder, encoding, DDIC, naming, or template-residue findings;
- native XML preflight success and a reviewed real import adapter;
- SAP lock/enqueue handling, import result, activation status, and rollback plan;
- rendered-PDF comparison accepted by a human reviewer.

## Offline validation

```powershell
python .agents/skills/sap-smartform-generator/scripts/validate_formspec.py --input path/to/formspec.json
python .agents/skills/sap-smartform-generator/scripts/validate_native_ssfo.py --input path/to/form.xml --form-name Z_FORM --forbid-token W_HEADER
```
