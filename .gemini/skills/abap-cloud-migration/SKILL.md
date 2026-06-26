---
name: abap-cloud-migration
description: ABAP Cloud migration patterns — custom code analysis with ATC cloud readiness checks, deprecated object replacement strategies, Dynpro → Fiori Elements migration, RFC → RAP OData migration, IDoc → SOAP migration, authorization object migration to IAM, DB access → CDS views, FILE → Document Management Service. Use when migrating ABAP code to cloud, planning S/4HANA cloud migration, or assessing custom code cloud readiness.
---

# ABAP Cloud Migration

Strategies for migrating existing ABAP code to ABAP Cloud (Steampunk-ready).

## Migration Assessment

### ATC Cloud Readiness Check
```
ATC Transaction → Check Variant: SAP_CP_READINESS_REMOTE
  → Run on custom code packages (Z* and Y*)
    → Results:
      1. Released API violations
      2. Direct DB access
      3. Dynpro usage
      4. Deprecated function modules
```

## Migration Patterns by Technology

### Dynpro → Fiori Elements
```
Old: Dynpro transaction (SE80 screen painter)
  1. Extract PBO/PAI logic into RAP behavior implementation
  2. Map screen fields to CDS view entity
  3. Generate Fiori Elements UI via Service Binding
  4. Annotate CDS for UI layout (@UI.lineItem, @UI.selectionField)

New: Fiori Elements List Report + Object Page
```

### RFC → RAP OData
```
Old: Custom RFC function module (SE37)
  1. Map RFC parameters to CDS entity fields
  2. Create BDEF with actions for each RFC function
  3. Expose via OData V4 service binding
  4. Replace RFC consumers with OData clients

New: RAP OData V4 endpoint
```

### IDoc → SOAP
```
Old: IDoc processing (WE19/WE20)
  1. Map IDoc segments to SOAP message types
  2. Create Enterprise Service (SOA Manager)
  3. Configure SAP_COM_0465 communication scenario
  4. Migrate IDoc partner profiles to SOA consumers

New: SOAP Web Service via released scenario
```

### Direct DB Access → CDS Views
```
Old: SELECT * FROM mara INTO TABLE lt_mara.
  1. Create CDS View Entity for mara (or use SAP standard I_Product)
  2. Replace SELECT with CDS view access
  3. Add DCL role for authorization

New: SELECT * FROM z_i_custom_product INTO TABLE lt_products.
```

### FILE → Document Management
```
Old: OPEN DATASET / TRANSFER / READ DATASET
  1. Split file logic into upload (GUI) and processing (backend)
  2. Upload → Fiori file uploader control
  3. Processing → cl_bc_file_upload_download API
  4. Store → SAP Document Management Service (BTP)

New: Fiori upload + DM Service
```

## Migration Phases

```
Phase 1: Assess (ATC scan) → Cloud readiness report
Phase 2: Replace deprecated APIs → C1 contract alternatives
Phase 3: Rearchitect (Dynpro → Fiori) → UI modernization
Phase 4: Validate (ABAP Unit) → Functional equivalence tests
Phase 5: Cutover (dual maintenance → cloud-only)
```

## Gotchas

- **Not all ABAP code can migrate** — some on-premise capabilities have no cloud equivalent
- **Custom Dynpros must be replaced** — no Dynpro runtime in ABAP Cloud
- **Third-party RFC destinations** — must go through SAP_COM_0064 with Destination service
- **Dual landscape during migration** — on-premise ABAP + BTP ABAP coexisting
