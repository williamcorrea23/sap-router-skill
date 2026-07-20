CLASS zcx_mm DEFINITION
  PUBLIC
  INHERITING FROM cx_static_check
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_t100_message.
    DATA mv_text TYPE string READ-ONLY.
    METHODS constructor
      IMPORTING
        textid   LIKE if_t100_message=>t100key OPTIONAL
        previous LIKE previous OPTIONAL
        mv_text  TYPE string OPTIONAL.
    METHODS get_text REDEFINITION.
ENDCLASS.


CLASS zcx_mm IMPLEMENTATION.
  METHOD constructor.
    super->constructor( previous = previous ).
    me->mv_text = mv_text.
    IF textid IS INITIAL.
      if_t100_message~t100key = if_t100_message=>default_textid.
    ELSE.
      if_t100_message~t100key = textid.
    ENDIF.
  ENDMETHOD.

  METHOD get_text.
    IF mv_text IS NOT INITIAL.
      result = mv_text.
    ELSE.
      result = super->get_text( ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.
