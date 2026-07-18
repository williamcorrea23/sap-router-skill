*&---------------------------------------------------------------------*
*& ZROUTER_TMPL_HD — Template Header
*&---------------------------------------------------------------------*
* Central repository for reusable code templates. Each row = one
* template identified by module + action (or a custom template ID).
*
* Used by ZROUTER_DISPATCH evaluate_expression to resolve dynamic
* ABAP at runtime, and by the offline Python toolchain
* (scripts/template_repo.py) for template-driven code generation.
*
* Delivery Class = E (allow customer extends).
*----------------------------------------------------------------------*
" To activate in SAP GUI / ADT:
" 1. SE11 → Database table → ZROUTER_TMPL_HD
" 2. Fields tab → paste structure below
" 3. Technical Settings → Applies to all table categories
" 4. Activate

" TABLE: ZROUTER_TMPL_HD
" DELIVERY_CLASS: E
" CONT: A

" Field        Key   Data Element         Data Type  Length  Decimals  Short Text
" CLIENT       X     MANDT                CLNT       3       0         Client
" TEMPLATE_ID  X     ZROUTER_TMPL_ID      CHAR       32      0         Template ID (GUID)
" MODULE              ZROUTER_MODULE       CHAR       10      0         Module (MM/SD/FI/QM/PP/WM/CO/HCM/BASIS)
" ACTION              ZROUTER_ACTION       CHAR       30      0         Action name (CREATE_MATERIAL etc.)
" VERSION             ZROUTER_VERSION      NUMC       4       0         Version number
" TITLE               ZROUTER_TITLE        CHAR       80      0         Template title
" DESCRIPTION         ZROUTER_DESCR        STRING              0         Template description
" CATEGORY            ZROUTER_CATEG        CHAR       20      0         Category (bapi/report/screen/rfc/sicf)
" LANGUAGE            SYLANGU              LANG       1       0         Original language
" CREATED_BY          UNAME                CHAR       12      0         Created by
" CREATED_AT          TIMESTAMPL           DEC        21      7         Created at (UTC long)
" CHANGED_BY          UNAME                CHAR       12      0         Last changed by
" CHANGED_AT          TIMESTAMPL           DEC        21      7         Last changed at (UTC long)
" ACTIVE_FLAG         ZROUTER_BOOL         CHAR       1       0         Active flag (X=active)
" SOURCE_SYSTEM       ZROUTER_SRCSYS       CHAR       10      0         Source system / transport layer


*&---------------------------------------------------------------------*
*& ZROUTER_TMPL_CD — Template Code Body
*&---------------------------------------------------------------------*
* Stores the actual ABAP source code for each template. Multi-row.
* LINE_NUM defines execution order. Code supports placeholders in
* {{PLACEHOLDER_NAME}} syntax.
*
* At runtime, evaluate_expression replaces placeholders with actual
* values before GENERATE SUBROUTINE POOL / INSERT REPORT.
*----------------------------------------------------------------------*
" TABLE: ZROUTER_TMPL_CD
" DELIVERY_CLASS: E
" CONT: A

" Field        Key   Data Element         Data Type  Length  Decimals  Short Text
" CLIENT       X     MANDT                CLNT       3       0         Client
" TEMPLATE_ID  X     ZROUTER_TMPL_ID      CHAR       32      0         Template ID (GUID)
" LINE_NUM     X     ZROUTER_LINE_NO      NUMC       6       0         Line number
" CODE_LINE          ZROUTER_CODE_LINE    CHAR       200     0         ABAP source line (with {{placeholders}})
" ACTIVE_FLAG        ZROUTER_BOOL         CHAR       1       0         Active flag


*&---------------------------------------------------------------------*
*& ZROUTER_TMPL_PL — Template Placeholders
*&---------------------------------------------------------------------*
* Declares expectable placeholders for each template. Each row defines
* one {{PLACEHOLDER}} that appears in ZROUTER_TMPL_CD.
*
* At generation time, the toolchain reads this table to:
* - Validate that all required placeholders are filled
* - Prompt for missing values
* - Auto-generate conversion parameters for xls_to_bapi
*----------------------------------------------------------------------"
" TABLE: ZROUTER_TMPL_PL
" DELIVERY_CLASS: E
" CONT: A

" Field        Key   Data Element         Data Type  Length  Decimals  Short Text
" CLIENT       X     MANDT                CLNT       3       0         Client
" TEMPLATE_ID  X     ZROUTER_TMPL_ID      CHAR       32      0         Template ID
" PLACEHOLDER  X     ZROUTER_PLACEHOLDER   CHAR       30      0         Placeholder name (without {{}})
" REQUIRED           ZROUTER_BOOL         CHAR       1       0         Required (X) or optional
" DEFAULT_VAL        ZROUTER_PL_DEFAULT   CHAR       200     0         Default value
" DATA_TYPE          ZROUTER_PL_TYPE      CHAR       10      0         Data type hint (CHAR/NUMC/DATE/STRING/RAW)
" DESCRIPTION        ZROUTER_PL_DESCR     CHAR       80      0         Placeholder description
" MAX_LENGTH         ZROUTER_PL_MAXLEN    NUMC       4       0         Max allowed input length


*&---------------------------------------------------------------------*
*& ZROUTER_TMPL_PKG — Template Package (abapGit / Nugget)
*&---------------------------------------------------------------------*
* Groups one or more templates into a deployable package for abapGit
* export or nugget (.nugg) distribution.
*
* One package = one folder. JSON export format:
*   { "pkgId": "...", "version": 1, "templates": ["id1","id2"] }
*----------------------------------------------------------------------"
" TABLE: ZROUTER_TMPL_PKG
" DELIVERY_CLASS: E
" CONT: A

" Field        Key   Data Element         Data Type  Length  Decimals  Short Text
" CLIENT       X     MANDT                CLNT       3       0         Client
" PKG_ID       X     ZROUTER_PKG_ID       CHAR       32      0         Package ID (GUID)
" PKG_NAME            ZROUTER_PKG_NAME     CHAR       40      0         Package name
" VERSION             ZROUTER_VERSION      NUMC       4       0         Package version
" DESCRIPTION         ZROUTER_DESCR        STRING              0         Package description
" CREATED_BY          UNAME                CHAR       12      0         Created by
" CREATED_AT          TIMESTAMPL           DEC        21      7         Created at
" EXPORT_FORMAT       ZROUTER_EXPORT_FMT   CHAR       10      0         Export format (abapGit/nugget/json)


*&---------------------------------------------------------------------*
*& ZROUTER_TMPL_PKG_T — Package-Template Assignment
*&---------------------------------------------------------------------*
* M:N relationship between packages and templates.
*----------------------------------------------------------------------"
" TABLE: ZROUTER_TMPL_PKG_T
" DELIVERY_CLASS: E
" CONT: A

" Field        Key   Data Element         Data Type  Length  Decimals  Short Text
" CLIENT       X     MANDT                CLNT       3       0         Client
" PKG_ID       X     ZROUTER_PKG_ID       CHAR       32      0         Package ID
" TEMPLATE_ID  X     ZROUTER_TMPL_ID      CHAR       32      0         Template ID
" SEQNR              ZROUTER_LINE_NO      NUMC       6       0         Sequence in package
