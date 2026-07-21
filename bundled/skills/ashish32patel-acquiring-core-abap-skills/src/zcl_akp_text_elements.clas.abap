CLASS zcl_akp_text_elements DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC .

  PUBLIC SECTION.
  INTERFACES if_oo_adt_classrun.
  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.



CLASS zcl_akp_text_elements IMPLEMENTATION.
  METHOD if_oo_adt_classrun~main.

   out->write(  TEXT-001          ).
   out->write( 'How are you'(hau) ).

  ENDMETHOD.

ENDCLASS.
