CLASS zcl_akp_seq_of_constructors DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC .

  PUBLIC SECTION.

    INTERFACES if_oo_adt_classrun .
  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.



CLASS zcl_akp_seq_of_constructors IMPLEMENTATION.


  METHOD if_oo_adt_classrun~main.
    "Put break points in Class constructors , Constructors of both super class and subclasses
    "in the Local types tab and run F9.
    DATA(l_o_passenger_plane) = NEW lcl_passenger_plane(
      iv_manufacturer = 'Boeing'
      iv_type         = 'A320'
      iv_seats        = 100
    ).
  ENDMETHOD.
ENDCLASS.
