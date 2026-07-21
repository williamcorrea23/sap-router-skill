---
item_id: SI-8.2
title: "8.2 S4TWL - DATA MODEL CHANGES IN FIN"
pages: 239-247
sap_notes: [1976487, 2270333, 2332030]
components: [CO, FI]
objects: []
---
Application Components:CO, FI

Related Notes:

| Note Type       |   Note Number | Note Description                  |
|-----------------|---------------|-----------------------------------|
| Business Impact |       2270333 | S4TWL - Data Model Changes in FIN |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Business Value

The universal journal significantly changes the way transactional data is stored for financial reporting. It offers huge benefits in terms of the ability to harmonize internal and external reporting requirements by having both read from the same document store where the account is the unifying element. You still create general journal entries in General Ledger Accouting, acquire and retire assets in Asset Accounting, run allocation and settelement in Controlling, capitalize research and development costs in Investment Management, and so on, but in reporting, you read from one source, regardless of whether you want to supply data to your consolidation system, report to tax authorities, or make internal mangement decisions.

Totals records that store the data in the General Ledger, Controlling, Material Ledger, Asset Accounting, Accounts Payable and Accounts Receivable by period have been removed as have index tables that are designed to optimize certain selections. This simplifies the data structure and makes accounting more flexible in the long term as reporting is no longer limited by the number of fields in the totals records.

## Description

With the installation of SAP Simple Finance, on-premise edition totals and application index tables were removed and replaced by identically-named DDL SQL views, called compatibility views. These views are generated from DDL sources. This replacement takes place during the add-on installation of SAP Simple Finance using SUM - related data is secured into backup tables. The compatibility views ensure database SELECTs work as before. However, write access (INSERT, UPDATE, DELETE, MODIFY) was removed from SAP standard, or has to be removed from custom code - refer to SAP note 1976487.

| Original Table   | Compatibility View (identically-named view in DDIC)   | DDL Source (for the identically-named DDIC View)   | Backup Table (for original table content)   |
|------------------|-------------------------------------------------------|----------------------------------------------------|---------------------------------------------|
| BSAD             | BSAD                                                  | BSAD_DDL                                           | BSAD_BCK                                    |
| BSAK             | BSAK                                                  | BSAK_DDL                                           | BSAK_BCK                                    |
| BSAS             | BSAS                                                  | BSAS_DDL                                           | BSAS_BCK                                    |
| BSID             | BSID                                                  | BSID_DDL                                           | BSID_BCK                                    |
| BSIK             | BSIK                                                  | BSIK_DDL                                           | BSIK_BCK                                    |
| BSIS             | BSIS                                                  | BSIS_DDL                                           | BSIS_BCK                                    |
| FAGLBSAS         | FAGLBSAS                                              | FAGLBSAS_DDL                                       | FAGLBSAS_BCK                                |
| FAGLBSIS         | FAGLBSIS                                              | FAGLBSIS_DDL                                       | FAGLBSIS_BCK                                |
| GLT0             | GLT0                                                  | GLT0_DDL                                           | GLT0_BCK                                    |
| KNC1             | KNC1                                                  | KNC1_DDL                                           | KNC1_BCK                                    |
| KNC3             | KNC3                                                  | KNC3_DDL                                           | KNC3_BCK                                    |
| LFC1             | LFC1                                                  | LFC1_DDL                                           | LFC1_BCK                                    |
| LFC3             | LFC3                                                  | LFC3_DDL                                           | LFC3_BCK                                    |
| COSP             | COSP                                                  | V_COSP_DDL                                         | COSP_BAK                                    |
| COSS             | COSS                                                  | V_COSS_DDL                                         | COSS_BAK                                    |
| FAGLFLEXT        | FAGLFLEXT                                             | V_FAGLFLEXT_DDL                                    | FAGLFLEXT_BCK                               |

In SAP Simple Finance, on-premise edition add-on 2.0 and SAP S/4HANA on-premise edition 1511, additional tables were (partially) replaced by Universal Journal (ACDOCA). The approach for compatibility views in release 2.0 differs from 1.0 in the following ways:

Compatibility views do not have the same name as the original tables.

Instead, the database interface (DBI) redirects all related database table SELECTs to a compatibility view, which retrieves the same data based on the new data model (ACDOCA, and so on).

The connection between table and compatibility view is NOT created during the installation w/ SUM

Again, write access (INSERT, UPDATE, DELETE, MODIFY) was adapted in SAP standard, or has to be adapted in custom code - refer to SAP note 1976487.

| Original Table   | Compatibility View (view in DDIC for redirect)   | DDL Source (for the identically-named DDIC view)   | View to read the content of the database table (w/o redirect to compatibility view)   |
|------------------|--------------------------------------------------|----------------------------------------------------|---------------------------------------------------------------------------------------|
| ANEA             | FAAV_ANEA                                        | FAA_ANEA                                           | FAAV_ANEA_ORI                                                                         |
| ANEK             | FAAV_ANEK                                        | FAA_ANEK                                           | FAAV_ANEK_ORI                                                                         |
| ANEP             | FAAV_ANEP                                        | FAA_ANEP                                           | FAAV_ANEP_ORI                                                                         |
| ANLC             | FAAV_ANLC                                        | FAA_ANLC                                           | FAAV_ANLC_ORI                                                                         |
| ANLP             | FAAV_ANLP                                        | FAA_ANLP                                           | FAAV_ANLP_ORI                                                                         |
| BSIM             | V_BSIM                                           | BSIM_DDL                                           | V_BSIM_ORI                                                                            |
| COEP             | V_COEP                                           | V_COEP                                             | V_COEP_ORI                                                                            |
| FAGLFLEXA        | FGLV_FAGLFLEXA                                   | FGL_FAGLFLEXA                                      | V_FAGLFLEXA_ORI                                                                       |
| T012K            | V_T012K_BAM                                      | V_T012K_BAM_DDL                                    | V_T012K_MIG                                                                           |
| T012T            | V_T012T_BAM                                      | V_T012T_DDL                                        | V_T012T_MIG                                                                           |
| FMGLFLEXA        | FGLV_FMGLFLEXA                                   | FGL_FMGLFLEXA                                      | V_ FMGLFLEXA _ORI                                                                     |
| FMGLFLEXT        | FGLV_FMGLFLEXT                                   | FGL_FMGLFLEXT                                      | V_ FMGLFLEXT _ORI                                                                     |
| PSGLFLEXA        | FGLV_PSGLFLEXA                                   | FGL_PSGLFLEXA                                      | -                                                                                     |
| PSGLFLEXT        | FGLV_PSGLFLEXT                                   | FGL_PSGLFLEXT                                      | -                                                                                     |
| JVGLFLEXA        | FGLV_JVGLFLEXA                                   | FGL_JVGLFLEXA                                      | V_ JVGLFLEXA _ORI                                                                     |
| JVGLFLEXT        | FGLV_JVGLFLEXT                                   | FGL_JVGLFLEXT                                      | V_ JVGLFLEXT _ORI                                                                     |
| ZZ<CUST>A *      | ZFGLV_GLSI_C<number>                             | ZFGL_GLSI_C<number>                                | -                                                                                     |
| ZZ<CUST>T *      | ZFGLV_GLTT_C<number>                             | ZFGL_GLTT_C<number>                                | -                                                                                     |

Any access to the following tables (Material Ledger) is supported up to release S/4 HANA OP 1809:

Read access via redirection to compatibility views

Write access (INSERT, UPDATE, DELETE, MODIFY) was adapted in SAP standard, or has to be adapted in custom code - refer to SAP note 1976487.

## From release S/4 HANA OP 1909 and subsequent these tables and views are obsolete. No read or write access is allowed anymore.

( (*) The tables MLHD/MLIT/MLPP/MLCR are still used for the ML documents created by the specific processes "ML Post Closing" and "Price Changes". But their views have been deleted.)

| Original Table   | Compatibility View (view in DDIC for redirect)   | DDL Source (for the identically-named DDIC view)   | View to read the content of the database table (w/o redirect to compatibility view)   |
|------------------|--------------------------------------------------|----------------------------------------------------|---------------------------------------------------------------------------------------|
| CKMI1            | V_CKMI1                                          | V_CKMI1_DDL                                        | V_CKMI1_ORI                                                                           |
| MLCD             | V_MLCD                                           | V_MLCD_DDL                                         | V_MLCD_ORI                                                                            |
| MLCR(*)          | V_MLCR                                           | V_MLCR_DDL                                         | V_MLCR_ORI                                                                            |
| MLHD(*)          | V_MLHD                                           | V_MLHD_DDL                                         | V_MLHD_ORI                                                                            |
| MLIT(*)          | V_MLIT                                           | V_MLIT_DDL                                         | V_MLIT_ORI                                                                            |
| MLPP(*)          | V_MLPP                                           | V_MLPP_DDL                                         | V_MLPP_ORI                                                                            |

Besides the database tables, some old, related DDIC database views were replaced, either by equivalent code, a new identically-named DDL SQL compatibility view, or an automatic redirect to a new compatibility view. For the views that have been replaced by code, custom code also needs to be adapted - refer to SAP note 1976487. Similarly, customer-owned DDIC views referencing the database tables or views affected need to be replaced by equivalent code.

| Original DDIC database view   | Obsole te databa se table used   | As of release   | Replaced by                 | Compatibility View   | DDL Source (for the compatibility view)   |
|-------------------------------|----------------------------------|-----------------|-----------------------------|----------------------|-------------------------------------------|
| BKPF_BSAD                     | BSAD                             | sFIN 1.0        | Identically -named DDL view | BKPF_BSAD            | BKPF_BSAD_DDL                             |
| BKPF_BSAD_AE DAT              | BSAD                             | sFIN 1.0        | Identically -named DDL view | BKPF_BSAD_AE DAT     | BKPF_BSAD_AEDAT_D DL                      |
| BKPF_BSAK                     | BSAK                             | sFIN 1.0        | Identically -named DDL view | BKPF_BSAK            | BKPF_BSAK_DDL                             |

| BKPF_BSAK_AE DAT   | BSAK   | sFIN 1.0   | Identically -named DDL view   | BKPF_BSAK_AE DAT   | BKPF_BSAK_AED_DDL    |
|--------------------|--------|------------|-------------------------------|--------------------|----------------------|
| BKPF_BSID          | BSID   | sFIN 1.0   | Identically -named DDL view   | BKPF_BSID          | BKPF_BSID_DDL        |
| BKPF_BSID_AED AT   | BSID   | sFIN 1.0   | Identically -named DDL view   | BKPF_BSID_AED AT   | BKPF_BSID_AEDAT_D DL |
| BKPF_BSIK          | BSIK   | sFIN 1.0   | Identically -named DDL view   | BKPF_BSIK          | BKPF_BSIK_DDL        |
| BKPF_BSIK_AED AT   | BSIK   | sFIN 1.0   | Identically -named DDL view   | BKPF_BSIK_AED AT   | BKPF_BSIK_AEDAT_DD L |
| GLT0_AEDAT         | GLT0   | sFIN 1.0   | Identically -named DDL view   | GLT0_AEDAT         | GLT0_AEDAT_DDL       |
| KNC1_AEDAT         | KNC1   | sFIN 1.0   | Identically -named DDL view   | KNC1_AEDAT         | KNC1_AEDAT_DDL       |
| KNC3_AEDAT         | KNC3   | sFIN 1.0   | Identically -named DDL view   | KNC3_AEDAT         | KNC3_AEDAT_DDL       |
| LFC1_AEDAT         | LFC1   | sFIN 1.0   | Identically -named DDL view   | LFC1_AEDAT         | LFC1_AEDAT_DDL       |
| LFC3_AEDAT         | LFC3   | sFIN 1.0   | Identically -named DDL view   | LFC3_AEDAT         | LFC3_AEDAT_DDL       |
| TXW_J_WITH         | BSAK   | sFIN 1.0   | Identically -named DDL view   | TXW_J_WITH         | TXW_J_WITH_DDL       |
| V_COSP_A           | COSP   | sFIN 1.0   | Code                          |                    |                      |
| V_COSS_A           | COSS   | sFIN 1.0   | Code                          |                    |                      |
| VB_DEBI            | BSID   | sFIN 1.0   | Identically -named DDL view   | VB_DEBI            | VB_DEBI_DDL          |
| VF_BSID            | BSID   | sFIN 1.0   | Identically -named DDL view   | VF_BSID            | VF_BSID_DDL          |
| VFC_DEBI           | KNC1   | sFIN 1.0   | Identically -named DDL view   | VFC_DEBI           | VFC_DEBI_DDL         |
| VFC_KRED           | LFC1   | sFIN 1.0   | Identically -named DDL view   | VFC_KRED           | VFC_KRED_DDL         |
| ENT2006            | GLT0   | sFIN 1.0   | Code                          |                    |                      |

| ENT2163           | KNC1   | sFIN 1.0                                     | Code                           |                   |                         |
|-------------------|--------|----------------------------------------------|--------------------------------|-------------------|-------------------------|
| ENT2164           | LFC1   | sFIN 1.0                                     | Code                           |                   |                         |
| ENT2165           | KNC3   | sFIN 1.0                                     | Code                           |                   |                         |
| ENT2166           | LFC3   | sFIN 1.0                                     | Code                           |                   |                         |
| EPIC_V_BRS_BS AS  | BSAS   | sFIN 1.0                                     | Code                           |                   |                         |
| EPIC_V_BRS_BS IS  | BSIS   | sFIN 1.0                                     | Code                           |                   |                         |
| EPIC_V_BSID       | BSID   | sFIN 1.0                                     | Code                           |                   |                         |
| EPIC_V_BSIK       | BSIK   | sFIN 1.0                                     | Code                           |                   |                         |
| EPIC_V_CUSTO MER  | BSID   | sFIN 1.0                                     | Code                           |                   |                         |
| EPIC_V_VENDO R    | BSIK   | sFIN 1.0                                     | Code                           |                   |                         |
| FMKK_BKPF_BS AK   | BSAK   | sFIN 1.0                                     | Code                           |                   |                         |
| FMKK_BKPF_BSI K   | BSIK   | sFIN 1.0                                     | Code                           |                   |                         |
| /GRC/V_BANK_A CCT | T012   | SAP Simple Finance, on- premise edition 1503 | Compatibi lity view (redirect) | V_GRC_BANK_A CCT  | V_GRC_BANK_ACCT_D DL    |
| ANEKPV            | ANEP   | SAP Simple Finance, on- premise edition 1503 | Compatibi lity view (redirect) | FAAV_ANEKPV       | FAA_ANEKPV              |
| COPC_V_T012_S KB1 | T012K  | SAP Simple Finance, on- premise edition 1503 | Compatibi lity view (redirect) | V_COPC_T012_S KB1 | V_COPC_V_T012_SKB1 _DDL |
| COPC_V_T035D      | T012K  | SAP Simple Finance, on- premise edition 1503 | Compatibi lity view (redirect) | V_COPC_T035D      | V_COPC_V_T035D_DD L     |

| COVP             | COEP   | SAP Simple Finance, on- premise edition 1503                                                     | Compatibi lity view (redirect)   | V_COVP           | V_COVP_DDL             |
|------------------|--------|--------------------------------------------------------------------------------------------------|----------------------------------|------------------|------------------------|
| FAP_V_CMP_HB ACC | T012   | SAP Simple Finance, on- premise edition 1503                                                     | Compatibi lity view (redirect)   | V_FAP_CMP_HB ACC | V_FAP_V_CMP_HBACC _DDL |
| MLREADST         | MLHD   | SAP Simple Finance, on- premise edition 1503 Obsolete from release S/4 HANA 1909 and subsequ ent | Compatibi lity view (redirect)   | V_MLREADST       | V_MLREADST_DDL         |
| MLREPORT         | MLIT   | SAP Simple Finance, on- premise edition 1503 Obsolete from release S/4 HANA 1909 and subsequ ent | Compatibi lity view (redirect)   | V_MLREPORT       | V_MLREPORT_DDL         |
| MLXXV            | MLHD   | SAP Simple Finance, on- premise                                                                  | Compatibi lity view (redirect)   | V_MLXXV          | V_MLXXV_DDL            |

|            |      | edition 1503 Obsolete from release S/4 HANA 1909 and suseque nt   |                                |                  |                |
|------------|------|-------------------------------------------------------------------|--------------------------------|------------------|----------------|
| V_ANEPK    | ANEP | SAP Simple Finance, on- premise edition 1503                      | Compatibi lity view (redirect) | FAAV_V_ANEPK     | FAA_V_ANEPK    |
| V_ANLAB    | ANEP | SAP Simple Finance, on- premise edition 1503                      | Compatibi lity view (redirect) | FAAV_V_ANLAB     | FAA_V_ANLAB    |
| V_ANLSUM_1 | ANLA | SAP Simple Finance, on- premise edition 1503                      | Compatibi lity view (redirect) | FAAV_V_ANLSU M_1 | FAA_V_ANLSUM_1 |
| V_ANLSUM_2 | ANEP | SAP Simple Finance, on- premise edition 1503                      | Compatibi lity view (redirect) | FAAV_V_ANLSU M_2 | FAA_V_ANLSUM_2 |
| V_ANLSUM_5 | ANLA | SAP Simple Finance, on- premise edition 1503                      | Compatibi lity view (redirect) | FAAV_V_ANLSU M_5 | FAA_V_ANLSUM_5 |

Business Process Related Information There are mandatory configuration steps in General Ledger, Asset Accounting, AccountBased CO-PA, and Cash Management (if used). For detailed information, refer to IMG -> Migration from SAP ERP to SAP Accounting powered by SAP HANA as well as to the respective simplification items for the used financial applications. We also recommend reading the guide attached to SAP note 2332030 - Conversion of accounting to SAP S/4HANA.

You should also consider adapting your reporting strategy to use the new Fiori reports that are designed specifically to handle the many fields in the universal journal, rather than continuing to work with the classic reports that aggregate on the fly according to the fields in the old totals fields.

## Required and Recommended Actions

Adapt access to new simplified finance data model in your customer-specific programs refer to SAP note 1976487.
