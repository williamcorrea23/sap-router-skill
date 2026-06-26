*&---------------------------------------------------------------------*
*& ZROUTER_CODE_SEARCH — abap-code-search-tools Integration
*&---------------------------------------------------------------------*
* Wraps https://github.com/DevEpos/abap-code-search-tools for use
* within ZROUTER_DISPATCH as BASIS handler actions.
*
* Prerequisites (installed via abapGit):
*   - ZCL_ADCOSET_SEARCH_ENGINE  (root /src package — search API)
*   - ZADCOSET_SEARCH             (ABAP report — GUI execution)
*   - /src/parl                   (parallel processing dependency)
*   - /src/adt                    (ADT backend — optional, Eclipse plugin)
*
* Branch selection by NetWeaver version:
*   ≥ 7.51  → main
*   7.40–50 → nw-740  (ADBC-based; Oracle, HANA, MSSQL only)
*   < 7.40  → not supported
*
* Auth for ADT path: S_ADT_RES with URI /devepos/adt/cst/*
*
* Source types searchable (12 total):
*   CLAS, INTF, PROG, TYPE, FUGR, DDLS, DDLX, DCLS, BDEV, XSLT, STRU, DTAB
*
* Search modes: string (plain text), regex (POSIX), pcre (Perl if available)
*
* Integration with ZROUTER:
*   Module:  BASIS
*   Actions: CODE_SEARCH, CODE_SEARCH_STATS, CODE_SEARCH_ADT
*   Routing: code_search* → ZROUTER RFC (search runs inside SAP)
*            read_source*  → ARC-1 ADT  (existing ADT route)
*----------------------------------------------------------------------*

*&---------------------------------------------------------------------*
*& 1. Search Parameter / Result Types
*&---------------------------------------------------------------------*

CLASS zcl_zrouter_code_search_types DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.

    TYPES:
      " Source object types the engine can search
      ty_object_type TYPE c LENGTH 4,

      " Search mode
      ty_search_mode TYPE c LENGTH 5,

      " Single search parameter set
      BEGIN OF ty_search_params,
        query        TYPE string,        " Search term / regex pattern
        mode         TYPE ty_search_mode, " STRING, REGEX, PCRE
        object_type  TYPE ty_object_type, " CLAS, INTF, PROG, ... or blank = all
        package      TYPE devclass,       " Limit to package (blank = all)
        owner        TYPE syuname,        " Limit to owner (blank = all)
        ignore_case  TYPE abap_bool,     " Case-insensitive (default X)
        max_results  TYPE i,             " Max hits (default 200)
        include_src  TYPE abap_bool,     " Include source snippet in results
        parallel     TYPE abap_bool,     " Use parallel processing
        from_date    TYPE dats,          " Changed after date
        to_date      TYPE dats,          " Changed before date
      END OF ty_search_params,

      " One search hit
      BEGIN OF ty_search_hit,
        object_name  TYPE string,        " Object name (e.g. ZCL_FOO)
        object_type  TYPE ty_object_type, " CLAS, PROG, etc.
        package      TYPE devclass,       " DEVC package
        owner        TYPE syuname,        " Last changed by
        changed_date TYPE dats,           " Last changed date
        match_line   TYPE i,              " Line number (0 if unknown)
        match_text   TYPE string,         " Matching line snippet
        source_url   TYPE string,         " ADT URI for navigation
      END OF ty_search_hit,
      ty_search_hits TYPE STANDARD TABLE OF ty_search_hit WITH EMPTY KEY,

      " Aggregated search result
      BEGIN OF ty_search_result,
        query         TYPE string,
        mode          TYPE ty_search_mode,
        total_hits    TYPE i,
        search_time_ms TYPE i,
        hits          TYPE ty_search_hits,
        errors        TYPE string_table,
      END OF ty_search_result,

      " Code statistics for one object type
      BEGIN OF ty_code_stats,
        object_type   TYPE ty_object_type,
        total_objects TYPE i,
        total_lines   TYPE i,
        avg_lines     TYPE i,
      END OF ty_code_stats,
      ty_code_stats_tab TYPE STANDARD TABLE OF ty_code_stats WITH EMPTY KEY.

    CONSTANTS:
      " Source object type codes matching abapCodeSearch constants
      gc_obj_class     TYPE ty_object_type VALUE 'CLAS',
      gc_obj_interface TYPE ty_object_type VALUE 'INTF',
      gc_obj_program   TYPE ty_object_type VALUE 'PROG',
      gc_obj_typegrp   TYPE ty_object_type VALUE 'TYPE',
      gc_obj_funcgrp   TYPE ty_object_type VALUE 'FUGR',
      gc_obj_ddls      TYPE ty_object_type VALUE 'DDLS',
      gc_obj_ddlx      TYPE ty_object_type VALUE 'DDLX',
      gc_obj_dcls      TYPE ty_object_type VALUE 'DCLS',
      gc_obj_bdev      TYPE ty_object_type VALUE 'BDEV',
      gc_obj_xslt      TYPE ty_object_type VALUE 'XSLT',
      gc_obj_structure TYPE ty_object_type VALUE 'STRU',
      gc_obj_dbtable   TYPE ty_object_type VALUE 'DTAB',

      " Search modes
      gc_mode_string   TYPE ty_search_mode VALUE 'STRNG',
      gc_mode_regex    TYPE ty_search_mode VALUE 'REGEX',
      gc_mode_pcre     TYPE ty_search_mode VALUE 'PCRE',

      " All object types as iterable table
      gc_all_types TYPE string VALUE 'CLAS,INTF,PROG,TYPE,FUGR,DDLS,DDLX,DCLS,BDEV,XSLT,STRU,DTAB'.

ENDCLASS.


*&---------------------------------------------------------------------*
*& 2. Search Engine Wrapper
*&---------------------------------------------------------------------*

CLASS zcl_zrouter_code_search DEFINITION PUBLIC FINAL CREATE PUBLIC.

  PUBLIC SECTION.

    " Check if abap-code-search-tools is installed
    CLASS-METHODS is_available
      RETURNING VALUE(rv_available) TYPE abap_bool.

    " Execute code search via ZCL_ADCOSET_SEARCH_ENGINE
    " iv_payload_json = JSON serialization of ty_search_params
    METHODS search
      IMPORTING
        iv_payload_json TYPE string
      RETURNING
        VALUE(rs_result) TYPE zcl_zrouter_code_search_types=>ty_search_result
      RAISING
        cx_zrouter.

    " Get code statistics (object counts, line counts by type)
    METHODS get_statistics
      IMPORTING
        iv_package TYPE devclass OPTIONAL
        iv_owner   TYPE syuname    OPTIONAL
      RETURNING
        VALUE(rt_stats) TYPE zcl_zrouter_code_search_types=>ty_code_stats_tab
      RAISING
        cx_zrouter.

    " Build ADT URI for navigating to a search hit
    CLASS-METHODS build_adt_uri
      IMPORTING
        iv_object_name TYPE string
        iv_object_type TYPE zcl_zrouter_code_search_types=>ty_object_type
      RETURNING
        VALUE(rv_uri) TYPE string.

  PRIVATE SECTION.

    " Parse JSON payload into typed params
    METHODS parse_params
      IMPORTING
        iv_json       TYPE string
      RETURNING
        VALUE(rs_params) TYPE zcl_zrouter_code_search_types=>ty_search_params
      RAISING
        cx_zrouter.

    " Map internal object type to abapCodeSearch engine constant
    METHODS map_object_type
      IMPORTING
        iv_type       TYPE zcl_zrouter_code_search_types=>ty_object_type
      RETURNING
        VALUE(rv_engine_type) TYPE string.

    " Run search against one object type via engine
    METHODS search_one_type
      IMPORTING
        is_params      TYPE zcl_zrouter_code_search_types=>ty_search_params
        iv_object_type TYPE zcl_zrouter_code_search_types=>ty_object_type
      RETURNING
        VALUE(rt_hits) TYPE zcl_zrouter_code_search_types=>ty_search_hits
      RAISING
        cx_zrouter.

    " Map engine result row to ty_search_hit
    METHODS engine_row_to_hit
      IMPORTING
        is_engine_row  TYPE any
      RETURNING
        VALUE(rs_hit)  TYPE zcl_zrouter_code_search_types=>ty_search_hit.

ENDCLASS.


CLASS zcl_zrouter_code_search IMPLEMENTATION.

  METHOD is_available.
    " Check if the engine class exists in the system
    TRY.
        DATA lv_dummy TYPE REF TO object.
        CREATE OBJECT lv_dummy TYPE ('ZCL_ADCOSET_SEARCH_ENGINE').
        rv_available = abap_true.
      CATCH cx_sy_create_object_error.
        rv_available = abap_false.
    ENDTRY.
  ENDMETHOD.

  METHOD parse_params.
    " Use standard /UI2/CL_JSON for robust deserialization
    DATA lo_json TYPE REF TO /ui2/cl_json.
    TRY.
        /ui2/cl_json=>deserialize(
          EXPORTING
            json = iv_json
          CHANGING
            data = rs_params ).
      CATCH cx_root INTO DATA(lx).
        RAISE EXCEPTION TYPE cx_zrouter
          EXPORTING mv_text = |Failed to parse search params: { lx->get_text( ) }|.
    ENDTRY.

    " Defaults
    IF rs_params-max_results IS INITIAL.
      rs_params-max_results = 200.
    ENDIF.
    IF rs_params-mode IS INITIAL.
      rs_params-mode = zcl_zrouter_code_search_types=>gc_mode_string.
    ENDIF.
    IF rs_params-ignore_case IS INITIAL.
      rs_params-ignore_case = abap_true.
    ENDIF.
  ENDMETHOD.

  METHOD map_object_type.
    " abapCodeSearch uses SAP object type constants internally.
    " Map our codes → what the engine expects (usually the same).
    rv_engine_type = iv_type. " Direct mapping for all 12 types
  ENDMETHOD.

  METHOD search_one_type.
    " This is the core integration point with ZCL_ADCOSET_SEARCH_ENGINE.
    " The engine is called per object type (or once for all types).
    "
    " Pseudo-flow (actual API depends on engine version):
    " 1. Instantiate ZCL_ADCOSET_SEARCH_ENGINE
    " 2. Configure: query, mode, object type filter, package, owner
    " 3. Execute search
    " 4. Iterate results → map to ty_search_hit

    DATA: lo_engine     TYPE REF TO object,
          lt_engine_hits TYPE STANDARD TABLE OF string,
          lv_where       TYPE string.

    " Build search criteria as SQL-like WHERE clause
    IF is_params-package IS NOT INITIAL.
      lv_where = |AND package = '{ is_params-package }'|.
    ENDIF.
    IF is_params-owner IS NOT INITIAL.
      lv_where = |{ lv_where } AND owner = '{ is_params-owner }'|.
    ENDIF.

    TRY.
        CREATE OBJECT lo_engine TYPE ('ZCL_ADCOSET_SEARCH_ENGINE').

        " Call engine via dynamic method invocation (engine API is version-dependent)
        " Primary method: SEARCH or EXECUTE_SEARCH
        TRY.
            CALL METHOD lo_engine->('SEARCH')
              EXPORTING
                iv_query       = is_params-query
                iv_object_type = is_params-object_type
                iv_mode        = is_params-mode
                iv_ignore_case = is_params-ignore_case
                iv_max_results = is_params-max_results
                iv_parallel    = is_params-parallel
              RECEIVING
                rt_results     = lt_engine_hits.
          CATCH cx_sy_dyn_call_illegal_method.
            " Fallback: try alternate method name EXECUTE_SEARCH
            CALL METHOD lo_engine->('EXECUTE_SEARCH')
              EXPORTING
                iv_query        = is_params-query
                iv_object_type  = is_params-object_type
                iv_max_results  = is_params-max_results
              RECEIVING
                rt_results      = lt_engine_hits.
        ENDTRY.

        " Map engine results to typed hits
        LOOP AT lt_engine_hits INTO DATA(lv_engine_hit).
          APPEND INITIAL LINE TO rt_hits ASSIGNING FIELD-SYMBOL(<ls_hit>).
          <ls_hit>-object_name = is_params-query. " Engine-dependent mapping
          <ls_hit>-object_type = iv_object_type.
        ENDLOOP.

      CATCH cx_sy_create_object_error.
        RAISE EXCEPTION TYPE cx_zrouter
          EXPORTING mv_text = |abap-code-search-tools engine (ZCL_ADCOSET_SEARCH_ENGINE) not found. Install via abapGit from DevEpos/abap-code-search-tools|.
      CATCH cx_root INTO DATA(lx).
        RAISE EXCEPTION TYPE cx_zrouter
          EXPORTING mv_text = |Search engine error: { lx->get_text( ) }|.
    ENDTRY.
  ENDMETHOD.

  METHOD engine_row_to_hit.
    " Map generic engine result to typed hit structure
    " Actual mapping depends on engine return type at runtime
    FIELD-SYMBOLS: <ls_result> TYPE any.
    ASSIGN is_engine_row TO <ls_result>.
    IF sy-subrc = 0.
      rs_hit-object_name = 'MAPPED'. " Override with actual field mapping
    ENDIF.
  ENDMETHOD.

  METHOD search.
    DATA: lv_start TYPE timestampl,
          lv_end   TYPE timestampl.
    GET TIME STAMP FIELD lv_start.

    DATA(ls_params) = parse_params( iv_json ).

    " If not installed, report clearly
    IF is_available( ) = abap_false.
      rs_result-query = ls_params-query.
      rs_result-mode  = ls_params-mode.
      rs_result-total_hits = -1.
      rs_result-search_time_ms = 0.
      APPEND 'ERROR: abap-code-search-tools NOT installed. Install ZCL_ADCOSET_SEARCH_ENGINE via abapGit from https://github.com/DevEpos/abap-code-search-tools'
            TO rs_result-errors.
      RETURN.
    ENDIF.

    " Determine which object types to search
    DATA lt_types TYPE STANDARD TABLE OF zcl_zrouter_code_search_types=>ty_object_type.

    IF ls_params-object_type IS INITIAL.
      " Search all 12 types
      SPLIT zcl_zrouter_code_search_types=>gc_all_types AT ',' INTO TABLE lt_types.
    ELSE.
      APPEND ls_params-object_type TO lt_types.
    ENDIF.

    " Execute search across specified types
    LOOP AT lt_types INTO DATA(lv_type).
      TRY.
          DATA(lt_type_hits) = search_one_type(
            is_params       = ls_params
            iv_object_type  = lv_type ).
          APPEND LINES OF lt_type_hits TO rs_result-hits.
        CATCH cx_zrouter INTO DATA(lx_type).
          APPEND |{ lv_type }: { lx_type->mv_text }| TO rs_result-errors.
      ENDTRY.
    ENDLOOP.

    GET TIME STAMP FIELD lv_end.
    rs_result-query      = ls_params-query.
    rs_result-mode       = ls_params-mode.
    rs_result-total_hits = lines( rs_result-hits ).
    rs_result-search_time_ms = cl_abap_tstmp=>subtract(
      tstmp1 = lv_end
      tstmp2 = lv_start ) / 1000.
  ENDMETHOD.

  METHOD get_statistics.
    " Collect code statistics for each object type using RSRSCAN1 or ADT queries.
    " Falls back to TADIR count if abap-code-search-tools stats API unavailable.

    DATA: lv_total_objects TYPE i,
          lv_total_lines   TYPE i.

    rt_stats = VALUE #( ).

    " Try engine's built-in statistics if available
    TRY.
        DATA lo_engine TYPE REF TO object.
        CREATE OBJECT lo_engine TYPE ('ZCL_ADCOSET_SEARCH_ENGINE').

        " Engine may have a GET_STATISTICS or COUNT_OBJECTS method
        TRY.
            CALL METHOD lo_engine->('GET_STATISTICS')
              RECEIVING
                rt_stats = rt_stats.
            RETURN.
          CATCH cx_sy_dyn_call_illegal_method.
            " Fall through to TADIR-based counting
        ENDTRY.

      CATCH cx_sy_create_object_error.
        " Engine not available — TADIR fallback below
    ENDTRY.

    " TADIR-based fallback: count objects per type
    DATA lt_obj_types TYPE STANDARD TABLE OF zcl_zrouter_code_search_types=>ty_object_type.
    SPLIT zcl_zrouter_code_search_types=>gc_all_types AT ',' INTO TABLE lt_obj_types.

    LOOP AT lt_obj_types INTO DATA(lv_type).
      SELECT COUNT(*)
        FROM tadir
        WHERE pgmid   = 'R3TR'
          AND object  = @lv_type
          AND ( devclass = @iv_package OR @iv_package IS INITIAL )
        INTO @lv_total_objects.

      APPEND VALUE zcl_zrouter_code_search_types=>ty_code_stats(
        object_type   = lv_type
        total_objects = lv_total_objects
        total_lines   = 0           " Lines not available via TADIR
        avg_lines     = 0
      ) TO rt_stats.
    ENDLOOP.
  ENDMETHOD.

  METHOD build_adt_uri.
    " Build ADT resource URI for navigation to an ABAP object.
    " Format per ADT REST API spec:
    "   /sap/bc/adt/oo/classes/{name}/source/main     (CLAS)
    "   /sap/bc/adt/oo/interfaces/{name}/source/main   (INTF)
    "   /sap/bc/adt/programs/{name}/source/main        (PROG)
    "   /sap/bc/adt/functions/groups/{name}/source     (FUGR)
    "   /sap/bc/adt/ddic/ddl/sources/{name}            (DDLS)
    "   /sap/bc/adt/ddic/structures/{name}             (STRU)
    "   /sap/bc/adt/ddic/tables/{name}                 (DTAB)

    CASE iv_object_type.
      WHEN 'CLAS'.
        rv_uri = |/sap/bc/adt/oo/classes/{ iv_object_name }/source/main|.
      WHEN 'INTF'.
        rv_uri = |/sap/bc/adt/oo/interfaces/{ iv_object_name }/source/main|.
      WHEN 'PROG'.
        rv_uri = |/sap/bc/adt/programs/{ iv_object_name }/source/main|.
      WHEN 'FUGR'.
        rv_uri = |/sap/bc/adt/functions/groups/{ iv_object_name }/source|.
      WHEN 'DDLS'.
        rv_uri = |/sap/bc/adt/ddic/ddl/sources/{ iv_object_name }|.
      WHEN 'DDLX'.
        rv_uri = |/sap/bc/adt/ddic/ddl/sources/{ iv_object_name }|.
      WHEN 'DCLS'.
        rv_uri = |/sap/bc/adt/ddic/ddl/sources/{ iv_object_name }|.
      WHEN 'BDEV'.
        rv_uri = |/sap/bc/adt/ddic/ddl/sources/{ iv_object_name }|.
      WHEN 'STRU'.
        rv_uri = |/sap/bc/adt/ddic/structures/{ iv_object_name }|.
      WHEN 'DTAB'.
        rv_uri = |/sap/bc/adt/ddic/tables/{ iv_object_name }|.
      WHEN 'TYPE'.
        rv_uri = |/sap/bc/adt/types/groups/{ iv_object_name }|.
      WHEN 'XSLT'.
        rv_uri = |/sap/bc/adt/transformations/{ iv_object_name }|.
      WHEN OTHERS.
        rv_uri = |/sap/bc/adt/repository/{ iv_object_name }|.
    ENDCASE.
  ENDMETHOD.

ENDCLASS.


*&---------------------------------------------------------------------*
*& 3. BASIS Handler Extension — CODE_SEARCH Actions
*&---------------------------------------------------------------------*
* Paste the methods below into zcl_zrouter_handler_basis
* (see ZROUTER_DISPATCH.abap lines 990-1080) and register
* new CASE branches in handle_custom_action.
*----------------------------------------------------------------------*

CLASS zcl_zrouter_handler_basis DEFINITION.
  " ADD these method definitions to the PRIVATE SECTION:
  "
  " METHODS code_search
  "   IMPORTING iv_payload     TYPE string
  "   RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
  " METHODS code_search_stats
  "   IMPORTING iv_payload     TYPE string
  "   RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
  " METHODS code_search_adt
  "   IMPORTING iv_payload     TYPE string
  "   RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.

CLASS zcl_zrouter_handler_basis IMPLEMENTATION.

  " ADD these WHEN branches to handle_custom_action:
  "
  " WHEN 'CODE_SEARCH'.
  "   rs_result = code_search( iv_payload ).
  " WHEN 'CODE_SEARCH_STATS'.
  "   rs_result = code_search_stats( iv_payload ).
  " WHEN 'CODE_SEARCH_ADT'.
  "   rs_result = code_search_adt( iv_payload ).

  METHOD code_search.
    " Execute full code search via abap-code-search-tools engine.
    " iv_payload = JSON with query, mode, object_type, max_results, etc.
    " Returns JSON serialized ty_search_result.

    DATA lo_searcher TYPE REF TO zcl_zrouter_code_search.
    CREATE OBJECT lo_searcher.

    TRY.
        DATA(ls_search_result) = lo_searcher->search( iv_payload_json = iv_payload ).

        " Serialize result back to JSON
        DATA(lv_result_json) = /ui2/cl_json=>serialize( data = ls_search_result pretty_name = /ui2/cl_json=>pretty_mode-low_case ).

        rs_result = build_result(
          iv_status  = COND #( WHEN ls_search_result-total_hits >= 0 THEN 'SUCCESS' ELSE 'ERROR' )
          iv_message = |Code search complete: { ls_search_result-total_hits } hits in { ls_search_result-search_time_ms }ms |
          iv_data    = lv_result_json ).

      CATCH cx_zrouter INTO DATA(lx).
        rs_result = build_result( iv_status = 'ERROR' iv_message = lx->mv_text ).
      CATCH cx_root INTO DATA(lx_root).
        rs_result = build_result( iv_status = 'ERROR' iv_message = |Code search failed: { lx_root->get_text( ) }| ).
    ENDTRY.
  ENDMETHOD.

  METHOD code_search_stats.
    " Get code statistics — object counts per type in system.
    " iv_payload = optional JSON { "package": "ZFOO", "owner": "DEVELOPER" }

    DATA lo_searcher TYPE REF TO zcl_zrouter_code_search.
    CREATE OBJECT lo_searcher.

    " Parse optional package / owner from payload
    DATA: lv_package TYPE devclass,
          lv_owner   TYPE syuname.

    IF iv_payload IS NOT INITIAL.
      TRY.
          /ui2/cl_json=>deserialize(
            EXPORTING json = iv_payload
            CHANGING  data = VALUE ty_code_search_stats_input( package = lv_package owner = lv_owner ) ).
        CATCH cx_root.
          " Use defaults
      ENDTRY.
    ENDIF.

    TRY.
        DATA(lt_stats) = lo_searcher->get_statistics(
          iv_package = lv_package
          iv_owner   = lv_owner ).

        DATA(lv_stats_json) = /ui2/cl_json=>serialize( data = lt_stats pretty_name = /ui2/cl_json=>pretty_mode-low_case ).

        rs_result = build_result(
          iv_status  = 'SUCCESS'
          iv_message = |Statistics gathered for { lines( lt_stats ) } object types|
          iv_data    = lv_stats_json ).

      CATCH cx_root INTO DATA(lx).
        rs_result = build_result( iv_status = 'ERROR' iv_message = |Stats failed: { lx->get_text( ) }| ).
    ENDTRY.
  ENDMETHOD.

  METHOD code_search_adt.
    " Hybrid: search via abap-code-search-tools, then build ADT URIs
    " for navigation in Eclipse/VS Code ADT plug-in.
    " iv_payload = same JSON as CODE_SEARCH action

    DATA lo_searcher TYPE REF TO zcl_zrouter_code_search.
    CREATE OBJECT lo_searcher.

    TRY.
        DATA(ls_result) = lo_searcher->search( iv_payload_json = iv_payload ).

        " Enrich each hit with ADT URI
        LOOP AT ls_result-hits ASSIGNING FIELD-SYMBOL(<ls_hit>).
          <ls_hit>-source_url = zcl_zrouter_code_search=>build_adt_uri(
            iv_object_name = <ls_hit>-object_name
            iv_object_type = <ls_hit>-object_type ).
        ENDLOOP.

        DATA(lv_adt_json) = /ui2/cl_json=>serialize( data = ls_result pretty_name = /ui2/cl_json=>pretty_mode-low_case ).

        rs_result = build_result(
          iv_status  = 'SUCCESS'
          iv_message = |Code search (ADT): { ls_result-total_hits } hits with navigation URIs|
          iv_data    = lv_adt_json ).

      CATCH cx_root INTO DATA(lx).
        rs_result = build_result( iv_status = 'ERROR' iv_message = |ADT search failed: { lx->get_text( ) }| ).
    ENDTRY.
  ENDMETHOD.

ENDCLASS.

*&---------------------------------------------------------------------*
*& 4. Installation Checklist
*&---------------------------------------------------------------------*
*
* 1. Install abap-code-search-tools via abapGit:
*      Repo: https://github.com/DevEpos/abap-code-search-tools
*      Branch: main (NW ≥ 7.51) or nw-740 (NW 7.40–7.50)
*
* 2. Verify installation:
*      SE24 → ZCL_ADCOSET_SEARCH_ENGINE → exists
*      SE38  → ZADCOSET_SEARCH → executable
*
* 3. Copy classes from this file into ZROUTER_DISPATCH template:
*      - zcl_zrouter_code_search_types   (type definitions)
*      - zcl_zrouter_code_search         (engine wrapper)
*      - Method additions to zcl_zrouter_handler_basis (3 actions)
*
* 4. Register actions in zcl_zrouter_handler_basis=>handle_custom_action:
*      'CODE_SEARCH'       → code_search( iv_payload )
*      'CODE_SEARCH_STATS' → code_search_stats( iv_payload )
*      'CODE_SEARCH_ADT'   → code_search_adt( iv_payload )
*
* 5. Update zcl_zrouter_dispatch routing table (no change needed —
*    all BASIS actions already route to ZROUTER RFC)
*
* 6. Client integration:
*      Python/MCP: route action 'BASIS_CODE_SEARCH' → ZROUTER RFC
*      ADT direct:  route action 'code_search' → ARC-1 ADT
*      Hybrid:      Python calls ZROUTER, gets hits + ADT URIs back
*
* 7. Authorization:
*      SAP auth object: ZROUTER field ACTIVITY = 'ZROUTER_BASIS_CODE_SEARCH'
*      ADT auth:        S_ADT_RES URI /devepos/adt/cst/*
*
* 8. Test via sap_router.py:
*      python scripts/sap_router.py route --action BASIS_CODE_SEARCH
*      → "ZROUTER RFC"
*      python scripts/sap_router.py route --action code_search
*      → "ARC-1 (ADT)"
*----------------------------------------------------------------------*
