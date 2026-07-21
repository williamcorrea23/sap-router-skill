CLASS lhc_connection DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS:
      get_global_authorizations FOR GLOBAL AUTHORIZATION
        IMPORTING
        REQUEST requested_authorizations FOR Connection
        RESULT result,
      CheckSemanticKey FOR VALIDATE ON SAVE
        IMPORTING keys FOR Connection~CheckSemanticKey,
      CheckCarrierID FOR VALIDATE ON SAVE
        IMPORTING keys FOR Connection~CheckCarrierID,
      CheckOriginDestination FOR VALIDATE ON SAVE
        IMPORTING keys FOR Connection~CheckOriginDestination,
      GetCities FOR DETERMINE ON SAVE
        IMPORTING keys FOR Connection~GetCities.
ENDCLASS.

CLASS lhc_connection IMPLEMENTATION.
  METHOD get_global_authorizations.
  ENDMETHOD.
  METHOD CheckSemanticKey.

    CHECK keys IS NOT INITIAL.

    READ ENTITIES OF z_r_akp_aconn IN LOCAL MODE
           ENTITY Connection
           FIELDS ( CarrierID ConnectionID )
             WITH CORRESPONDING #( keys )
           RESULT DATA(connections).

    LOOP AT connections INTO DATA(connection).
      SELECT FROM zakp_aconn
             FIELDS uuid
              WHERE carrier_id    = @connection-CarrierID
                AND connection_id = @connection-ConnectionID
                AND uuid          <> @connection-uuid
        UNION
        SELECT FROM zakp_aconn_d
             FIELDS uuid
              WHERE carrierid     = @connection-CarrierID
                AND connectionid  = @connection-ConnectionID
                AND uuid          <> @connection-uuid

         INTO TABLE @DATA(check_result).

      IF check_result IS NOT INITIAL.

        DATA(message) = me->new_message(
                          id       = 'ZAKP_M_SD400'
                          number   = '001'
                          severity = ms-error
                          v1       = connection-CarrierID
                          v2       = connection-ConnectionID
                        ).

        APPEND INITIAL LINE TO reported-connection ASSIGNING FIELD-SYMBOL(<reported_connection>).
        <reported_connection>-%tky = connection-%tky.
        <reported_connection>-%msg = message.
        <reported_connection>-%element-carrierid = if_abap_behv=>mk-on.
        <reported_connection>-%element-connectionid = if_abap_behv=>mk-on.

        APPEND INITIAL LINE TO failed-connection ASSIGNING FIELD-SYMBOL(<failed_connection>).
        <failed_connection>-%tky = connection-%tky.

      ENDIF.

    ENDLOOP.


  ENDMETHOD.

  METHOD CheckCarrierID.

    READ ENTITIES OF z_r_akp_aconn IN LOCAL MODE
           ENTITY Connection
           FIELDS (  CarrierID )
             WITH CORRESPONDING #(  keys )
           RESULT DATA(connections).


    LOOP AT connections INTO DATA(connection).

      SELECT SINGLE
        FROM /DMO/I_Carrier
      FIELDS @abap_true
       WHERE airlineid = @connection-CarrierID
       INTO @DATA(exists).


      IF exists = abap_false.

        DATA(message) = me->new_message(
                            id       = 'ZAKP_M_SD400'
                            number   = '002'
                            severity =  ms-error
                            v1       = connection-CarrierID
                          ) .

        APPEND INITIAL LINE TO reported-connection ASSIGNING FIELD-SYMBOL(<reported_connection>).
        <reported_connection>-%tky = connection-%tky.
        <reported_connection>-%msg = message.
        <reported_connection>-%element-carrierid = if_abap_behv=>mk-on.

        APPEND INITIAL LINE TO failed-connection ASSIGNING FIELD-SYMBOL(<failed_connection>).
        <failed_connection>-%tky = connection-%tky.

      ENDIF.

    ENDLOOP.

  ENDMETHOD.

  METHOD CheckOriginDestination.

    READ ENTITIES OF z_r_akp_aconn IN LOCAL MODE
           ENTITY Connection
           FIELDS ( AirportFromID AirportToID )
             WITH CORRESPONDING #(  keys )
           RESULT DATA(connections).


    LOOP AT connections INTO DATA(connection).
      IF connection-AirportFromID = connection-AirportToID.
        DATA(message) = me->new_message(
                          id       = 'ZAKP_M_SD400'
                          number   = '003'
                          severity = ms-error
                       ).


        "Clera message
        APPEND INITIAL LINE TO reported-connection ASSIGNING FIELD-SYMBOL(<reported_connection>).
        <reported_connection>-%tky = connection-%tky.
        <reported_connection>-%state_area = 'DEST_CHECK'.

        UNASSIGN <reported_connection>.

        APPEND INITIAL LINE TO reported-connection ASSIGNING <reported_connection>.
        <reported_connection>-%tky = connection-%tky.
        <reported_connection>-%msg = message.
        <reported_connection>-%state_area = 'DEST_CHECK'.
        <reported_connection>-%element-airportfromid = if_abap_behv=>mk-on.
        <reported_connection>-%element-airporttoid = if_abap_behv=>mk-on.

        APPEND INITIAL LINE TO failed-connection ASSIGNING FIELD-SYMBOL(<failed_connection>).
        <failed_connection>-%tky = connection-%tky.

      ENDIF.

    ENDLOOP.

  ENDMETHOD.
  METHOD GetCities.
    READ ENTITIES OF z_r_akp_aconn IN LOCAL MODE
    ENTITY Connection
    FIELDS ( AirportFromID AirportToID )
    WITH CORRESPONDING #( keys )
    RESULT DATA(connections).


    LOOP AT connections INTO DATA(connection).

      SELECT SINGLE
        FROM /DMO/I_Airport
      FIELDS city, CountryCode
       WHERE AirportID = @connection-AirportFromID
        INTO ( @connection-CityFrom, @connection-CountryFrom ).

      SELECT SINGLE
        FROM /DMO/I_Airport
      FIELDS city, CountryCode
       WHERE AirportID = @connection-AirportToID
        INTO ( @connection-CityTo, @connection-CountryTo ).

      MODIFY connections FROM connection.

    ENDLOOP.


    DATA connections_upd TYPE TABLE FOR UPDATE z_r_akp_aconn.

    connections_upd = CORRESPONDING #( connections ).

    MODIFY ENTITIES OF z_r_akp_aconn IN LOCAL MODE
    ENTITY Connection
    UPDATE
    FIELDS ( CityFrom CountryFrom CityTo CountryTo )
    WITH connections_upd
    REPORTED DATA(ls_reported).


  ENDMETHOD.

ENDCLASS.
