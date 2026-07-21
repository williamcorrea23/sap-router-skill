CLASS zcl_akp_code_pushdown_abapsql DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC .

  PUBLIC SECTION.

    INTERFACES if_oo_adt_classrun .
  PROTECTED SECTION.
  PRIVATE SECTION.
    METHODS literals
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS cast_expression
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS case_distinctions
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS arithmetic_expression
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS  numeric_functions
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS string_processing
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS date_processing
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS conversion_functions
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS sorting_condensing
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
    METHODS aggregate_group_by
      IMPORTING
        i_out TYPE REF TO if_oo_adt_classrun_out.
ENDCLASS.



CLASS zcl_akp_code_pushdown_abapsql IMPLEMENTATION.


  METHOD if_oo_adt_classrun~main.

*    literals( out ).

*    cast_expression( out ).

*    case_distinctions( out ).

*    arithmetic_expression( out ).

*    numeric_functions( out ).

*    string_processing( out ).


*    date_processing( out ).

*    conversion_functions( out ).

*    sorting_condensing( out ).

*    aggregate_group_by( out ).



    SELECT FROM /dmo/carrier AS a INNER JOIN /dmo/connection AS c
             ON a~carrier_id = c~carrier_id

         FIELDS a~carrier_id,
                a~name AS carrier_name,
                c~connection_id,
                c~airport_from_id,
                c~airport_to_id

          WHERE a~currency_code = 'EUR'
           INTO TABLE @DATA(result).

    out->write(
      EXPORTING
        data   = result
        name   = 'RESULT'
    ).



"Types of JOINS
    SELECT FROM /dmo/Agency AS a
*                   INNER JOIN /dmo/customer AS c
           LEFT OUTER JOIN /dmo/customer AS c
*          RIGHT OUTER JOIN /dmo/customer AS c
                ON a~city         = c~city

            FIELDS agency_id,
                   name AS Agency_name,
                   a~city AS agency_city,
                   c~city AS customer_city,
                   customer_id,
                   last_name AS customer_name

             WHERE ( c~customer_id < '000010' OR c~customer_id IS NULL )
               AND ( a~agency_id   < '070010' OR a~agency_id   IS NULL )

              INTO TABLE @DATA(result_Join).


    out->write(
      EXPORTING
        data   = result_join
        name   = 'RESULT_JOIN'
    ).



  ENDMETHOD.

  METHOD aggregate_group_by.

**********************************************************************
*Aggregate Functions
**********************************************************************
    SELECT FROM /dmo/connection
         FIELDS carrier_id,
                connection_id,
                airport_from_id,
                distance
          WHERE carrier_id = 'LH'
           INTO TABLE @DATA(result_raw).


    i_out->write(
      EXPORTING
        data   = result_raw
        name   = 'RESULT_RAW'
    ).

*********************************************************************

    SELECT FROM /dmo/connection
         FIELDS MAX( distance ) AS max,
                MIN( distance ) AS min,
                SUM( distance ) AS sum,
                AVG( distance ) AS average,
                COUNT( * ) AS count,
                COUNT( DISTINCT airport_from_id ) AS count_dist

          WHERE carrier_id = 'LH'
           INTO TABLE @DATA(result_aggregate).

    i_out->write(
      EXPORTING
        data   = result_aggregate
        name   = 'RESULT_AGGREGATED'
    ).

**********************************************************************
*GROUP BY
**********************************************************************
    SELECT FROM /dmo/connection
        FIELDS
            carrier_id,
            connection_id,
            distance
            INTO TABLE @DATA(raw_result).
    i_out->write(
      EXPORTING
        data   = raw_result
        name   = 'RAW RESULT'
    ).

    SELECT FROM /dmo/connection
    FIELDS
    carrier_id,
    MAX( distance ) AS max,
    MIN( distance ) AS min,
    SUM( distance ) AS sum,
    COUNT( * ) AS count

    GROUP BY carrier_id
    INTO TABLE @DATA(result).

    i_out->write(
      EXPORTING
        data   = result
        name   = 'RESULT GROUP BY'
    ).


  ENDMETHOD.



  METHOD sorting_condensing.

**********************************************************************
*ORDER BY
**********************************************************************
    SELECT FROM /dmo/flight
         FIELDS carrier_id,
                connection_id,
                flight_date,
                seats_max - seats_occupied AS available_seats
          WHERE carrier_id     = 'AA'

       ORDER BY seats_max - seats_occupied DESCENDING,
                flight_date                ASCENDING
           INTO TABLE @DATA(order_by_result).

    i_out->write(
      EXPORTING
        data   = order_by_result
        name   = 'ORDERR_BY_RESULT'
    ).

**********************************************************************
*SELECT DISTINCT
**********************************************************************

    SELECT FROM /dmo/connection
       FIELDS
              DISTINCT
              airport_from_id,
              distance_unit

     ORDER BY airport_from_id
         INTO TABLE @DATA(distinct_result).

    i_out->write(
      EXPORTING
        data   = distinct_result
        name   = 'DISTINCT_RESULT'
    ).



  ENDMETHOD.



  METHOD conversion_functions.

    SELECT FROM /dmo/travel
           FIELDS lastchangedat,
                  CAST( lastchangedat AS DEC( 15,0 ) ) AS latstchangedat_short,

                  tstmp_to_dats( tstmp = CAST( lastchangedat AS DEC( 15,0 ) ),
                                 tzone = CAST( 'EST' AS CHAR( 6 ) )
                               ) AS date_est,
                  tstmp_to_tims( tstmp = CAST( lastchangedat AS DEC( 15,0 ) ),
                                 tzone = CAST( 'EST' AS CHAR( 6 ) )
                               ) AS time_est

*            WHERE customer_id = '000001'
             INTO TABLE @DATA(result_date_time)
             UP TO 10 ROWS.

    i_out->write(
      EXPORTING
        data   = result_date_time
        name   = 'RESULT_DATE_TIME'
    ).


*********************************************************************

*    DATA(today) = cl_abap_context_info=>get_system_date(  ).
*
*    SELECT FROM /dmo/travel
*         FIELDS total_price,
*                currency_code,
*
*                currency_conversion( amount             = total_price,
*                                     source_currency    = currency_code,
*                                     target_currency    = 'EUR',
*                                     exchange_rate_date = @today
*                                   ) AS total_price_EUR
*
*          WHERE customer_id = '000001' AND currency_code <> 'EUR'
*           INTO TABLE @DATA(result_currency).
*
*    i_out->write(
*      EXPORTING
*        data   = result_currency
*        name   = 'RESULT__CURRENCY'
*    ).


**********************************************************************

    SELECT FROM /dmo/connection
         FIELDS distance,
                distance_unit,
                unit_conversion( quantity = CAST( distance AS QUAN ),
                                 source_unit = distance_unit,
                                 target_unit = CAST( 'MI' AS UNIT ) )  AS distance_MI

          WHERE airport_from_id = 'FRA'
           INTO TABLE @DATA(result_unit).

    i_out->write(
      EXPORTING
        data   = result_unit
        name   = 'RESULT_UNIT'
    ).


  ENDMETHOD.



  METHOD date_processing.

    SELECT
         FROM /dmo/travel
         FIELDS
                begin_date,
                end_date,
                is_valid( begin_date  )              AS valid,
                add_days( begin_date, 7 )            AS add_7_days,
                add_months(  begin_date, 3 )         AS add_3_months,
                days_between( begin_date, end_date ) AS duration,
                weekday(  begin_date  )              AS weekday,
                extract_month(  begin_date )         AS month,
                dayname(  begin_date )               AS day_name,
                dayname(  add_days( begin_date, 1 )  )               AS day_name1
          WHERE
            days_between( begin_date, end_date ) > 10

           INTO TABLE @DATA(result)
                     UP TO 10 ROWS.

    i_out->write(
      EXPORTING
        data   = result
        name   = 'RESULT'
    ).

  ENDMETHOD.



  METHOD string_processing.

    SELECT FROM /dmo/customer
         FIELDS customer_id,

                street && ',' && ' ' && postal_code && ' ' && city   AS address_expr,

                concat( street,
                        concat_with_space(  ',',
                                             concat_with_space( postal_code,
                                                                upper(  city ),
                                                                1
                                                              ),
                                            1
                                         )
                     ) AS address_func

          WHERE country_code = 'ES'
           INTO TABLE @DATA(result_concat).

    i_out->write(
      EXPORTING
        data   = result_concat
        name   = 'RESULT_CONCAT'
    ).

**********************************************************************

    SELECT FROM /dmo/carrier
         FIELDS carrier_id,
                name,
                upper( name )   AS name_upper,
                lower( name )   AS name_lower,
                initcap( name ) AS name_initcap

         WHERE carrier_id = 'SR'
          INTO TABLE @DATA(result_transform).

    i_out->write(
      EXPORTING
        data   = result_transform
        name   = 'RESULT_TRANSLATE'
    ).

**********************************************************************

    SELECT FROM /dmo/flight
         FIELDS flight_date,
                CAST( flight_date AS CHAR( 8 ) )  AS flight_date_raw,

                left( flight_Date, 4   )          AS year,

                right(  flight_date, 2 )          AS day,

                substring(  flight_date, 5, 2 )   AS month

          WHERE carrier_id = 'LH'
            AND connection_id = '0400'
           INTO TABLE @DATA(result_substring).

    i_out->write(
      EXPORTING
        data   = result_substring
        name   = 'RESULT_SUBSTRING'
    ).



  ENDMETHOD.



  METHOD  numeric_functions.

    SELECT FROM /dmo/flight
            FIELDS seats_max,
                   seats_occupied,

                   (   CAST( seats_occupied AS FLTP )
                     * CAST( 100 AS FLTP )
                   ) / CAST(  seats_max AS FLTP )                  AS percentage_fltp,

                   div( seats_occupied * 100 , seats_max )         AS percentage_int,

                   division(  seats_occupied * 100, seats_max, 2 ) AS percentage_dec

             WHERE carrier_id    = 'LH'
               AND connection_id = '0400'
              INTO TABLE @DATA(result).

    i_out->write(
      EXPORTING
        data   = result
        name   = 'RESULT'
    ).


  ENDMETHOD.



  METHOD arithmetic_expression.

    SELECT FROM /dmo/flight
            FIELDS seats_max,
                   seats_occupied,

                   seats_max - seats_occupied           AS seats_avaliable,

                   (   CAST( seats_occupied AS FLTP )
                     * CAST( 100 AS FLTP )
                   ) / CAST(  seats_max AS FLTP )       AS percentage_fltp

              WHERE carrier_id = 'LH' AND connection_id = '0400'
               INTO TABLE @DATA(result).

    i_out->write(
      EXPORTING
        data   = result
        name   = 'RESULT'
    ).

  ENDMETHOD.



  METHOD case_distinctions.

    SELECT FROM /dmo/customer
         FIELDS customer_id,
                title,
                CASE title
                  WHEN 'Mr.'  THEN 'Mister'
                  WHEN 'Mrs.' THEN 'Misses'
                  ELSE             ' '
               END AS title_long

        WHERE country_code = 'AT'
         INTO TABLE @DATA(result_simple).

    i_out->write(
      EXPORTING
        data   = result_simple
        name   = 'RESULT_SIMPLE'
    ).

**********************************************************************

    SELECT FROM /DMO/flight
         FIELDS flight_date,
                seats_max,
                seats_occupied,
                CASE
                  WHEN seats_occupied < seats_max THEN 'Seats Avaliable'
                  WHEN seats_occupied = seats_max THEN 'Fully Booked'
                  WHEN seats_occupied > seats_max THEN 'Overbooked!'
                  ELSE                                 'This is impossible'
                END AS Booking_State

          WHERE carrier_id    = 'LH'
            AND connection_id = '0400'
           INTO TABLE @DATA(result_complex).

    i_out->write(
      EXPORTING
        data   = result_complex
        name   = 'RESULT_COMPLEX'
    ).


  ENDMETHOD.



  METHOD cast_expression.

    SELECT FROM /dmo/carrier
         FIELDS '19891109'                           AS char_8,
                CAST( '19891109' AS CHAR( 4 ) )      AS char_4,
                CAST( '19891109' AS NUMC( 8  ) )     AS numc_8,

                CAST( '19891109' AS INT4 )          AS integer,
                CAST( '19891109' AS DEC( 10, 2 ) )  AS dec_10_2,
                CAST( '19891109' AS FLTP )          AS fltp,

                CAST( '19891109' AS DATS )          AS date

           INTO TABLE @DATA(result).

    i_out->write(
      EXPORTING
        data   = result
        name   = 'RESULT'
    ).

  ENDMETHOD.



  METHOD literals.

    CONSTANTS c_number TYPE i VALUE 1234.

    SELECT FROM /dmo/carrier
         FIELDS 'Hello'    AS Character,    " Type c
                 1         AS Integer1,     " Type i
                -1         AS Integer2,     " Type i

                @c_number  AS constant      " Type i  (same as constant)

          INTO TABLE @DATA(result).

    i_out->write(
      EXPORTING
        data   = result
        name   = 'RESULT'
    ).

  ENDMETHOD.


ENDCLASS.
