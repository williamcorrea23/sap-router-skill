CLASS zcl_akp_atc_unused_variables DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC .

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.



CLASS zcl_akp_atc_unused_variables IMPLEMENTATION.
  METHOD if_oo_adt_classrun~main.
    DATA carrier_list TYPE TABLE OF /dmo/carrier.
*    DATA connection_list TYPE TABLE OF /dmo/connection.

    SELECT FROM /dmo/connection
    FIELDS *
    INTO TABLE @DATA(connections).

*    connection_list = connection_list.

    out->write( connections ).

  ENDMETHOD.

ENDCLASS.
