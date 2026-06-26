---
name: abap
description: General ABAP development reference — ABAP language syntax, data types, internal tables, field symbols, MODULE POOL, function modules, classical dynpro, selection screens, ALV, batch input, BDC, FILE handling, RFC development, ABAP memory, SAP Memory. Use for general ABAP questions, ABAP syntax help, classical ABAP patterns (non-OO), dynpro/selection screen development, or ALV report creation.
---

# ABAP Development Reference

General ABAP language reference covering classical and modern ABAP (NW 7.40+).

## ABAP Syntax Basics

### Data Types

| ABAP Type | Description | Length | Default |
|---|---|---|---|
| C | Character | 1-65535 | ' ' |
| N | Numeric text | 1-65535 | '0' |
| I | Integer | 4 bytes | 0 |
| P | Packed number | 1-16 bytes | 0 |
| F | Floating point | 8 bytes | 0.0 |
| D | Date (YYYYMMDD) | 8 chars | '00000000' |
| T | Time (HHMMSS) | 6 chars | '000000' |
| STRING | Variable-length string | Dynamic | '' |
| XSTRING | Variable-length byte | Dynamic | '' |

### Internal Tables

```abap
" Standard table (unordered, fastest for appending)
DATA: lt_materials TYPE STANDARD TABLE OF mara.

" Sorted table (ordered by key, no duplicates)
DATA: lt_materials_sorted TYPE SORTED TABLE OF mara WITH UNIQUE KEY matnr.

" Hashed table (key access only, fastest for reads)
DATA: lt_materials_hashed TYPE HASHED TABLE OF mara WITH UNIQUE KEY matnr.

" Inline declaration
DATA(lt_data) = VALUE string_table( ( 'A' ) ( 'B' ) ).

" Append / Insert / Read / Modify / Delete
APPEND ls_row TO lt_data.
INSERT ls_row INTO TABLE lt_data.
READ TABLE lt_data INTO DATA(ls) WITH KEY field = 'X'.
MODIFY TABLE lt_data FROM ls.
DELETE lt_data WHERE field = 'X'.
```

### FIELD-SYMBOLS (Pointers)

```abap
" Assign to structure
ASSIGN COMPONENT 'MATNR' OF STRUCTURE ls_header TO FIELD-SYMBOL(<lv_matnr>).
IF <lv_matnr> IS ASSIGNED.
  lv_result = <lv_matnr>.
ENDIF.

" Loop with field symbol (fastest iteration)
LOOP AT lt_data ASSIGNING FIELD-SYMBOL(<ls_row>).
  <ls_row>-processed = 'X'.
ENDLOOP.
```

## Selection Screen

```abap
PARAMETERS: p_matnr TYPE matnr OBLIGATORY,
            p_werks TYPE werks_d DEFAULT '1000'.
SELECT-OPTIONS: s_date FOR sy-datum NO-EXTENSION.

" At selection-screen event
AT SELECTION-SCREEN ON p_matnr.
  IF p_matnr IS INITIAL.
    MESSAGE 'Material number is required' TYPE 'E'.
  ENDIF.
```

## ALV Grid (SALV)

```abap
" Simple ALV with SALV (released C1)
DATA: lo_alv TYPE REF TO cl_salv_table,
      lt_data TYPE TABLE OF mara.

SELECT * FROM mara INTO TABLE lt_data UP TO 100 ROWS.

TRY.
    cl_salv_table=>factory(
      IMPORTING r_salv_table = lo_alv
      CHANGING  t_table      = lt_data ).
    lo_alv->display( ).
  CATCH cx_salv_msg INTO DATA(lx).
    MESSAGE lx->get_text( ) TYPE 'E'.
ENDTRY.
```

## Batch Input / BDC

```abap
DATA: lt_bdcdata TYPE TABLE OF bdcdata,
      lt_messtab TYPE TABLE OF bdcmsgcoll.

" Build BDC data
APPEND VALUE bdcdata( program = 'SAPLMGMM' dynpro = '0060'
  dynbegin = 'X' ) TO lt_bdcdata.
APPEND VALUE bdcdata( fnam = 'RMMG1-MATNR' fval = 'MAT001' ) TO lt_bdcdata.

" Execute
CALL TRANSACTION 'MM01' USING lt_bdcdata
  MODE 'N'          " N = no display, A = all screens
  UPDATE 'S'        " S = synchronous
  MESSAGES INTO lt_messtab.
```

## FILE Operations

```abap
" Upload from local file (released for ABAP Cloud via Document Service)
" Legacy on-premise only:
DATA: lt_file TYPE TABLE OF string.
CALL FUNCTION 'GUI_UPLOAD'
  EXPORTING
    filename = 'C:\data\materials.csv'
    filetype = 'ASC'
  TABLES
    data_tab = lt_file.

" Direct file read (on-premise only)
DATA lv_filename TYPE string VALUE '/tmp/data.csv'.
OPEN DATASET lv_filename FOR INPUT IN TEXT MODE ENCODING UTF-8.
DO.
  READ DATASET lv_filename INTO DATA(lv_line).
  IF sy-subrc <> 0. EXIT. ENDIF.
  APPEND lv_line TO lt_lines.
ENDDO.
CLOSE DATASET lv_filename.
```

## RFC Development

```abap
" RFC function module
FUNCTION z_rfc_get_material.
*"----------------------------------------------------------------------
*"*"Remote Function Module:
*"  IMPORTING
*"     VALUE(IV_MATNR) TYPE MATNR
*"  EXPORTING
*"     VALUE(ES_DATA) TYPE MARA
*"----------------------------------------------------------------------
  SELECT SINGLE * FROM mara INTO es_data WHERE matnr = iv_matnr.
ENDFUNCTION.

" Call RFC from another system
CALL FUNCTION 'Z_RFC_GET_MATERIAL'
  DESTINATION 'S4H_DEV'
  EXPORTING
    iv_matnr = 'MAT001'
  IMPORTING
    es_data  = ls_data
  EXCEPTIONS
    communication_failure = 1
    system_failure        = 2
    OTHERS                = 3.
```

## SAP Memory / ABAP Memory

```abap
" ABAP Memory (within same session, SET/GET PARAMETER)
SET PARAMETER ID 'MAT' FIELD 'MAT001'.
GET PARAMETER ID 'MAT' FIELD lv_matnr.

" SAP Memory (across sessions, EXPORT/IMPORT to memory)
EXPORT lv_matnr = lv_matnr TO MEMORY ID 'ZMATERIAL'.
IMPORT lv_matnr = lv_matnr FROM MEMORY ID 'ZMATERIAL'.

" Shared memory (cross-user)
EXPORT data = lt_cache TO SHARED BUFFER zcl_cache(ind) ID 'DATA'.
```

## Gotchas

- **SALV replaces ALV Grid** for new code — released C1 contract
- **GUI_UPLOAD not in ABAP Cloud** — use Fiori file uploader
- **OPEN DATASET not in ABAP Cloud** — use Document Management Service
- **CALL TRANSACTION not in ABAP Cloud** — use released BAPIs or APIs
- **BDC is legacy** — prefer BAPI for data creation, BDC for screens without APIs
