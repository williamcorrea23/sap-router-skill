CLASS zcl_akp_sd400 DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC .

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.



CLASS zcl_akp_sd400 IMPLEMENTATION.
  METHOD if_oo_adt_classrun~main.
    DATA connection TYPE REF TO lcl_connection.
    DATA connections TYPE TABLE OF REF TO lcl_connection.

  ENDMETHOD.

ENDCLASS.
