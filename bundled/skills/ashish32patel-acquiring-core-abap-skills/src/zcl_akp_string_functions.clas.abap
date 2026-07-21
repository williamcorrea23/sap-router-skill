CLASS zcl_akp_string_functions DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC .

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
  PROTECTED SECTION.
  PRIVATE SECTION.
    METHODS description_functions
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS common_parameters
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS processing_functions
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
ENDCLASS.



CLASS zcl_akp_string_functions IMPLEMENTATION.
  METHOD if_oo_adt_classrun~main.

*    common_parameters( out ).

*    description_functions( out ).

    processing_functions( out ).
  ENDMETHOD.

  METHOD processing_functions.

    DATA text TYPE string      VALUE ` SAP BTP,   ABAP Environment  `.

    i_out->write( |Original Text    = { text } | ).
* Change Case of characters
    i_out->write( |TO_UPPER         = {   to_upper(  text ) } | ).
**********************************************************************
    i_out->write( |TO_LOWER         = {   to_lower(  text ) } | ).
    i_out->write( |TO_MIXED         = {   to_mixed(  text ) } | ).
    i_out->write( |FROM_MIXED       = { from_mixed(  text ) } | ).


* Change order of characters
**********************************************************************
    i_out->write( |REVERSE             = {  reverse( text ) } | ).
    i_out->write( |SHIFT_LEFT  (places)= {  shift_left(  val = text places   = 3  ) } | ).
    i_out->write( |SHIFT_RIGHT (places)= {  shift_right( val = text places   = 3  ) } | ).
    i_out->write( |SHIFT_LEFT  (circ)  = {  shift_left(  val = text circular = 3  ) } | ).
    i_out->write( |SHIFT_RIGHT (circ)  = {  shift_right( val = text circular = 3  ) } | ).


* Extract a Substring
**********************************************************************
    i_out->write( |SUBSTRING       = {  substring(        val = text off = 4 len = 10 ) } | ).
    i_out->write( |SUBSTRING_FROM  = {  substring_from(   val = text sub = 'ABAP'     ) } | ).
    i_out->write( |SUBSTRING_AFTER = {  substring_after(  val = text sub = 'ABAP'     ) } | ).
    i_out->write( |SUBSTRING_TO    = {  substring_to(     val = text sub = 'ABAP'     ) } | ).
    i_out->write( |SUBSTRING_BEFORE= {  substring_before( val = text sub = 'ABAP'     ) } | ).


* Condense, REPEAT and Segment
**********************************************************************
    i_out->write( |CONDENSE         = {   condense( val = text ) } | ).
    i_out->write( |REPEAT           = {   repeat(   val = text occ = 2 ) } | ).

    i_out->write( |SEGMENT1         = {   segment(  val = text sep = ',' index = 1 ) } |  ).
    i_out->write( |SEGMENT2         = {   segment(  val = text sep = ',' index = 2 ) } |  ).


  ENDMETHOD.



  METHOD common_parameters.

    DATA text   TYPE string VALUE `  Let's talk about ABAP  `.
    DATA result TYPE i.

    i_out->write(  text ).

    result = find( val = text sub = 'A' ).
*
*    result = find( val = text sub = 'A' case = abap_false ).
*
*    result = find( val = text sub = 'A' case = abap_false occ =  -1 ).
*    result = find( val = text sub = 'A' case = abap_false occ =  -2 ).
*    result = find( val = text sub = 'A' case = abap_false occ =   2 ).
*
*    result = find( val = text sub = 'A' case = abap_false occ = 2 off = 10 ).
*    result = find( val = text sub = 'A' case = abap_false occ = 2 off = 10 len = 4 ).

    i_out->write( |RESULT = { result } | ).


  ENDMETHOD.



  METHOD description_functions.


    DATA result TYPE i.

    DATA text    TYPE string VALUE `  ABAP  `.
    DATA substring TYPE string VALUE `AB`.
    DATA offset    TYPE i      VALUE 1.

* Call different description functions
******************************************************************************
*    result = strlen(     string ).
*    result = numofchar(  string ).

*    result = count(             val = text sub = substring off = offset ).
    result = find(             val = text sub = substring off = offset ).

*    result = count_any_of(     val = string sub = substring off = offset ).
*    result = find_any_of(      val = string sub = substring off = offset ).

*    result = count_any_not_of( val = string sub = substring off = offset ).
*    result = find_any_not_of(  val = string sub = substring off = offset ).

    i_out->write( |Text      = `{ text }`| ).
    i_out->write( |Substring = `{ substring }` | ).
    i_out->write( |Offset    = { offset } | ).
    i_out->write( |Result    = { result } | ).


  ENDMETHOD.



ENDCLASS.
