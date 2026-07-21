*"* use this source file for the definition and implementation of
*"* local helper classes, interface definitions and type
*"* declarations

CLASS lcl_plane DEFINITION.
  PUBLIC SECTION.
    TYPES: BEGIN OF ts_attributes,
             name  TYPE string,
             value TYPE string,
           END OF ts_attributes,
* declare table - do not allow the same attribute to be used more than once
           tt_attributes TYPE SORTED TABLE OF ts_attributes WITH UNIQUE KEY name.
    CLASS-METHODS class_constructor.


    METHODS constructor IMPORTING iv_manufacturer TYPE string
                                  iv_type         TYPE string.
    METHODS: get_Attributes RETURNING VALUE(rt_Attributes) TYPE tt_attributes.


  PROTECTED SECTION.
    DATA manufacturer TYPE string.
    DATA type TYPE string.

  PRIVATE SECTION.

ENDCLASS.


CLASS lcl_plane IMPLEMENTATION.

  METHOD class_constructor.
    DATA(text) = 'Class constructor of superclass lcl_plane'.
  ENDMETHOD.

  METHOD constructor.
    manufacturer = iv_manufacturer.
    type = iv_type.
  ENDMETHOD.


  METHOD get_attributes.
    rt_attributes = VALUE #( ( name = 'MANUFACTURER' value = manufacturer )
    ( name = 'TYPE' value = type ) ) .
  ENDMETHOD.


ENDCLASS.




CLASS lcl_passenger_plane DEFINITION INHERITING FROM lcl_Plane.
  PUBLIC SECTION.
    CLASS-METHODS class_constructor.
    METHODS constructor IMPORTING iv_manufacturer TYPE string
                                  iv_type         TYPE string
                                  iv_seats        TYPE i.
    METHODS get_Attributes REDEFINITION.
  PRIVATE SECTION.
    DATA seats TYPE i.
ENDCLASS.


CLASS lcl_passenger_plane IMPLEMENTATION.


  METHOD constructor.


    super->constructor( iv_manufacturer = iv_manufacturer iv_type = iv_type ).


  ENDMETHOD.


  METHOD get_attributes.


* Redefinition uses call of superclass implementation

    rt_attributes = super->get_attributes( ).
    rt_Attributes = VALUE #( BASE rt_attributes ( name = 'SEATS' value = seats ) ).

  ENDMETHOD.

  METHOD class_constructor.
    DATA(text) = 'Class constructor of subclass lcl_passenger_plane'.
  ENDMETHOD.

ENDCLASS.
