CLASS zcl_akp_type_conversions DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC .

  PUBLIC SECTION.

    INTERFACES if_oo_adt_classrun .
  PROTECTED SECTION.
  PRIVATE SECTION.
    METHODS successful_assignments
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS truncating_rounding
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS unexpected_assignment_result
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS forced_conversion_with_conv
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS preventing_rounding_truncation
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS time_date_timestamps
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out
      RAISING
        cx_abap_context_info_error.
ENDCLASS.



CLASS zcl_akp_type_conversions IMPLEMENTATION.


  METHOD if_oo_adt_classrun~main.

*    successful_assignments( out ).
*    truncating_rounding( out ).
*    unexpected_assignment_result( out ).
*    forced_conversion_with_conv( out ).
*    preventing_rounding_truncation( out ).

    time_date_timestamps( out ).

  ENDMETHOD.

  METHOD time_date_timestamps.

    DATA timestamp1 TYPE utclong.
    DATA timestamp2 TYPE utclong.
    DATA difference TYPE decfloat34.
    DATA date_user TYPE d.
    DATA time_user TYPE t.


    timestamp1 = utclong_current( ).
    i_out->write( |Current UTC time { timestamp1 }| ).

    timestamp2 = utclong_add( val = timestamp1 days = 7 ).
    i_out->write( |Added 7 days to current UTC time { timestamp2 }| ).

    difference = utclong_diff( high = timestamp2 low = timestamp1 ).
    i_out->write( |Difference between timestamps in seconds: { difference }| ).

    i_out->write( |Difference between timestamps in days: { difference / 3600 / 24 }| ).

    CONVERT UTCLONG utclong_current( )
    INTO DATE date_user
    TIME time_user
    TIME ZONE cl_abap_context_info=>get_user_time_zone( ).

    i_out->write( |UTC timestamp split into date (type D) and time (type T )| ).
    i_out->write( |according to the user's time zone (cl_abap_context_info=>get_user_time_zone( ) ).| ).
    i_out->write( |{ date_user DATE = USER }, { time_user TIME = USER }| ).

  ENDMETHOD.



  METHOD preventing_rounding_truncation.

    DATA var_date TYPE d.
    DATA var_pack TYPE p LENGTH 3 DECIMALS 2.
    DATA var_string TYPE string.
    DATA var_char TYPE c LENGTH 3.


    var_pack = 1 / 8.
    i_out->write( |1/8 = { var_pack NUMBER = USER }| ).


    TRY.
        var_pack = EXACT #( 1 / 8 ).
      CATCH cx_sy_conversion_error.
        i_out->write( |1/8 has to be rounded. EXACT triggered an exception| ).
    ENDTRY.


    var_string = 'ABCDE'.
    var_Char = var_string.
    i_out->write( var_char ).


    TRY.
        var_char = EXACT #( var_string ).
      CATCH cx_sy_conversion_error.
        i_out->write( 'String has to be truncated. EXACT triggered an exception' ).
    ENDTRY.


    var_date = 'ABCDEFGH'.
    i_out->write( var_Date ).


    TRY.
        var_date = EXACT #( 'ABCDEFGH' ).
      CATCH cx_sy_conversion_error.
        i_out->write( |ABCDEFGH is not a valid date. EXACT triggered an exception| ).
    ENDTRY.


    var_date = '20221232'.
    i_out->write( var_date ).


    TRY.
        var_date = EXACT #( '20221232' ).
      CATCH cx_sy_conversion_error.
        i_out->write( |2022-12-32 is not a valid date. EXACT triggered an exception| ).
    ENDTRY.

  ENDMETHOD.



  METHOD forced_conversion_with_conv.

* result has type C.
* and is displayed unformatted in the console
    DATA(result1) = '20230101'.
    i_out->write( result1 ).


* result2 is forced to have type D
* and is displayed with date formatting in the console
    DATA(result2) = CONV d( '20230101' ).
    i_out->write( result2 ).




* The method do_something( ) has an importing parameter of type string.
* Attempting to pass var results in a syntax error
* The CONV #( ) expression converts var into the expected type
* Note that CONV #( ) can lead to conversion exceptions


* lcl_class=>do_something( var ).

  ENDMETHOD.



  METHOD unexpected_assignment_result.

    DATA var_date TYPE d.
    DATA var_int TYPE i.
    DATA var_string TYPE string.
    DATA var_n TYPE n LENGTH 4.

    var_date = cl_abap_context_info=>get_system_date( ).
    var_int = var_date.

    i_out->write( |Date as date| ).
    i_out->write( var_date ).
    i_out->write( |Date assigned to integer| ).
    i_out->write( var_int ).      "number of days since 01.01.0001

    var_string = `R2D2`.
    var_n = var_string.

    i_out->write( |String| ).
    i_out->write( var_string ).
    i_out->write( |String assigned to type N| ).
    i_out->write( var_n ).

  ENDMETHOD.



  METHOD truncating_rounding.

    DATA long_char TYPE c LENGTH 10.
    DATA short_char TYPE c LENGTH 5.


    DATA result TYPE p LENGTH 3 DECIMALS 2.


    long_char = 'ABCDEFGHIJ'.
    short_char = long_char.


    i_out->write( long_char ).
    i_out->write( short_char ).


    result = 1 / 8.
    i_out->write( |1 / 8 is rounded to { result NUMBER = USER }| ).

  ENDMETHOD.



  METHOD successful_assignments.

    DATA var_string TYPE string.
    DATA var_int TYPE i.
    DATA var_date TYPE d.
    DATA var_pack TYPE p LENGTH 3 DECIMALS 2.


    var_string = `12345`.
    var_int = var_string.


    i_out->write( 'Conversion successful' ).


    var_string = `20230101`.
    var_date = var_string.


    i_out->write( |String value: { var_string }| ).
    i_out->write( |Date Value: { var_date DATE = USER }| ).

  ENDMETHOD.


ENDCLASS.
