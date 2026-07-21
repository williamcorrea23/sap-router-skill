CLASS zcl_akp_internal_tables DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC .

  PUBLIC SECTION.

    INTERFACES if_oo_adt_classrun .
  PROTECTED SECTION.
  PRIVATE SECTION.
    METHODS Sorting_standard_int_table
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS Table_Comprehensions
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS Table_Reduction
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
ENDCLASS.



CLASS zcl_akp_internal_tables IMPLEMENTATION.


  METHOD if_oo_adt_classrun~main.

*    Sorting_standard_int_table( out ).
*    Table_Comprehensions( out ).
    Table_Reduction( out ).


  ENDMETHOD.

  METHOD Table_Reduction.

    TYPES: BEGIN OF t_results,
             occupied TYPE /dmo/plane_seats_occupied,
             maximum  TYPE /dmo/plane_seats_max,
           END OF t_results.


    TYPES: BEGIN OF t_results_with_Avg,
             occupied TYPE /dmo/plane_seats_occupied,
             maximum  TYPE /dmo/plane_seats_max,
             average  TYPE p LENGTH 16 DECIMALS 2,
           END OF t_results_with_avg.


    DATA flights TYPE TABLE OF /dmo/flight.
    SELECT FROM /dmo/flight FIELDS * INTO TABLE @flights UP TO 5 ROWS.

    i_out->write( 'Raw Data' ).
    i_out->write( '_____________ ______________' ).
    i_out->write( flights ).

* Result is a scalar data type
    DATA(sum) = REDUCE i( INIT total = 0
                            FOR line IN flights
                            NEXT total += line-seats_occupied ).
    i_out->write( 'Result is a scalar data type' ).
    i_out->write( '_____________ ______________' ).
    i_out->write( sum ).
    i_out->write( ` ` ).


* Result is a structured data type
    DATA(results) = REDUCE t_results( INIT totals TYPE t_results
                                      FOR line IN flights
                                      NEXT totals-occupied += line-seats_occupied
                                           totals-maximum += line-seats_max ).
    i_out->write( 'Result is a structure' ).
    i_out->write( '_____________________' ).
    i_out->write( results ).
    i_out->write( ` ` ).


* Result is a structured data type
* Reduction uses a local helper variable
* Result of the reduction is always the *first* variable declared after init
    DATA(result_with_Average) = REDUCE t_results_with_avg( INIT totals_avg TYPE t_results_with_avg
                                                                count = 1
                                                           FOR line IN flights
                                                           NEXT totals_avg-occupied += line-seats_occupied
                                                                totals_avg-maximum += line-seats_max
                                                                totals_avg-average = totals_avg-occupied / count
                                                                count += 1 ).

    i_out->write( 'Result is a structure. The average is calculated using a local helper variable' ).
    i_out->write( '______________________________________________________________________________' ).
    i_out->write( result_with_average ).


  ENDMETHOD.



  METHOD Table_Comprehensions.


    TYPES: BEGIN OF t_connection,
             carrier_id             TYPE /dmo/carrier_id,
             connection_id          TYPE /dmo/connection_id,
             departure_airport      TYPE /dmo/airport_from_id,
             departure_airport_Name TYPE /dmo/airport_Name,
           END OF t_connection.
    TYPES t_connections TYPE STANDARD TABLE OF t_connection WITH NON-UNIQUE KEY carrier_id connection_id.

    DATA connections TYPE TABLE OF /dmo/connection.
    DATA airports TYPE TABLE OF /dmo/airport.
    DATA result_table TYPE t_connections.

* Aim of the method:
* Read a list of connections from the database and use them to fill an internal table result_table.
* This contains some data from the table connections and adds the name of the departure airport.
    SELECT FROM /dmo/airport FIELDS * INTO TABLE @airports.
    SELECT FROM /dmo/connection FIELDS * INTO TABLE @connections.

    i_out->write( 'Connection Table' ).
    i_out->write( '________________' ).
    i_out->write( connections ).
    i_out->write( ` ` ).

* The VALUE expression iterates over the table connections. In each iteration, the variable line
* accesses the current line. Inside the parentheses, we build the next line of result_table by
* copying the values of line-carrier_Id, line-connection_Id and line-airport_from_id, then
* loooking up the airport name in the internal table airports using a table expression

    result_table = VALUE #( FOR line IN connections
                                     ( carrier_Id = line-carrier_id
                                       connection_id = line-connection_id
                                       departure_airport = line-airport_from_id
                                       departure_airport_name = airports[ airport_id = line-airport_from_id ]-name )
                          ).

    i_out->write( 'Results' ).
    i_out->write( '_______' ).
    i_out->write( result_table ).

  ENDMETHOD.



  METHOD Sorting_standard_int_table.

    TYPES: t_flights TYPE STANDARD TABLE OF /dmo/flight WITH NON-UNIQUE KEY carrier_id connection_id flight_date.
    DATA: flights TYPE t_flights.


    flights = VALUE #( ( client = sy-mandt carrier_id = 'LH' connection_id = '0400' flight_date = '20230201' plane_type_id = '747-400' price = '600' currency_code = 'EUR' )
    ( client = sy-mandt carrier_id = 'LH' connection_id = '0400' flight_date = '20230115' plane_type_id = '747-400' price = '600' currency_code = 'EUR' )
    ( client = sy-mandt carrier_id = 'QF' connection_id = '0006' flight_date = '20230112' plane_type_id = 'A380' price = '1600' currency_code = 'AUD' )
    ( client = sy-mandt carrier_id = 'AA' connection_id = '0017' flight_date = '20230110' plane_type_id = '747-400' price = '600' currency_code = 'USD' )
    ( client = sy-mandt carrier_id = 'UA' connection_id = '0900' flight_date = '20230201' plane_type_id = '777-200' price = '600' currency_code = 'USD' ) ).


    i_out->write( 'Contents Before Sort' ).
    i_out->write( '____________________' ).
    i_out->write( flights ).
    i_out->write( ` ` ).


* Sort with no additions - sort by primary table key carrier_id connection_id flight_date
    SORT flights.


    i_out->write( 'Effect of SORT with no additions - sort by primary table key' ).
    i_out->write( '____________________________________________________________' ).
    i_out->write( flights ).
    i_out->write( ` ` ).


* Sort with field list - default sort direction is ascending
    SORT flights BY currency_code plane_type_id.
    i_out->write( 'Effect of SORT with field list - ascending is default direction' ).
    i_out->write( '________________________________________________________________' ).
    i_out->write( flights ).
    i_out->write( ` ` ).


* Sort with field list and sort directions.
    SORT flights BY carrier_Id ASCENDING flight_Date DESCENDING.
    i_out->write( 'Effect of SORT with field list and sort direction' ).
    i_out->write( '_________________________________________________' ).
    i_out->write( flights ).
    i_out->write( ` ` ).

  ENDMETHOD.


ENDCLASS.
