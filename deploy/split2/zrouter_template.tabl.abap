*&---------------------------------------------------------------------*
*& ZROUTER_TEMPLATE -- Request Template DDIC Table
*& Stores pre-built JSON payload templates for common ZROUTER actions
*&
*& Fields:
*&   MANDT         - Client
*&   MODULE        - Module (MM, SD, FI, QM, PP, WM, CO, HCM, BASIS)
*&   ACTION        - Action (CREATE_MATERIAL, CREATE_ORDER, etc.)
*&   TEMPLATE_NAME - Human-readable name
*&   TEMPLATE_JSON - JSON payload template with default values
*&   CREATED_BY    - Username who created
*&   CREATED_AT    - Timestamp
*&   CHANGED_BY    - Username who last changed
*&   CHANGED_AT    - Timestamp of last change
*&---------------------------------------------------------------------*
* DDIC creation via SE11:
*   Table: ZROUTER_TEMPLATE
*   Delivery class: A (Application table)
*   Fields:
*     MANDT         MANDT   CLNT 3  KEY
*     MODULE        CHAR    10       KEY
*     ACTION        CHAR    40       KEY
*     TEMPLATE_NAME CHAR    80
*     TEMPLATE_JSON STRING
*     CREATED_BY    SYUNAME CHAR 12
*     CREATED_AT    TIMESTAMPL DEC 21,7
*     CHANGED_BY    SYUNAME CHAR 12
*     CHANGED_AT    TIMESTAMPL DEC 21,7
*&---------------------------------------------------------------------*
"
* Usage from ZROUTER:
*   DATA(lv_template) = zcl_zrouter_template=>get_json(
*     iv_module = 'MM'
*     iv_action = 'CREATE_MATERIAL' ).
"
* Seed data examples:
"
* -- MM: Create Material
* MODULE=MM, ACTION=CREATE_MATERIAL, TEMPLATE_NAME='Create Raw Material'
* {
*   "material": "MAT_{{TIMESTAMP}}",
*   "industrySector": "M",
*   "materialType": "ROH",
*   "description": "Material created via ZROUTER",
*   "baseUom": "EA",
*   "plant": "1000",
*   "storLoc": "0001",
*   "movingAvgPrice": "10.00",
*   "priceControl": "V"
* }
"
* -- SD: Create Sales Order
* MODULE=SD, ACTION=CREATE_ORDER, TEMPLATE_NAME='Standard Sales Order'
* {
*   "salesOrg": "1000",
*   "distrChan": "10",
*   "division": "00",
*   "docType": "OR",
*   "soldToParty": "{{CUSTOMER_ID}}",
*   "purchaseDate": "{{DATE}}",
*   "items": [
*     {
*       "material": "{{MATERIAL}}",
*       "plant": "1000",
*       "quantity": 1,
*       "uom": "EA"
*     }
*   ]
* }
"
* -- FI: Post Document
* MODULE=FI, ACTION=POST_DOCUMENT, TEMPLATE_NAME='Standard FI Posting'
* {
*   "docType": "SA",
*   "companyCode": "1000",
*   "docDate": "{{DATE}}",
*   "postingDate": "{{DATE}}",
*   "currency": "BRL",
*   "reference": "ZROUTER-{{TIMESTAMP}}",
*   "headerText": "Posted via ZROUTER",
*   "items": [
*     {
*       "glAccount": "{{GL_ACCOUNT}}",
*       "amount": 100.00,
*       "dcIndicator": "S",
*       "costCenter": "{{COST_CENTER}}"
*     },
*     {
*       "glAccount": "{{GL_ACCOUNT_2}}",
*       "amount": 100.00,
*       "dcIndicator": "H",
*       "costCenter": "{{COST_CENTER}}"
*     }
*   ]
* }
"
* Template variables (replaced at runtime):
*   {{TIMESTAMP}}   -- Current timestamp
*   {{DATE}}        -- Current date (YYYYMMDD)
*   {{USER}}        -- Current user
*   {{MATERIAL}}    -- User-provided material
*   {{CUSTOMER_ID}} -- User-provided customer
*   {{GL_ACCOUNT}}  -- User-provided GL account
*   {{COST_CENTER}} -- User-provided cost center
