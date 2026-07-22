INTERFACE zif_gm_movement_types PUBLIC.

  TYPES: BEGIN OF ty_scale_ticket,
           ticket_id    TYPE c LENGTH 20,
           matnr        TYPE c LENGTH 18,
           werks        TYPE c LENGTH 4,
           gross_weight TYPE p LENGTH 13 DECIMALS 3,
           tare_weight  TYPE p LENGTH 13 DECIMALS 3,
           processed    TYPE abap_bool,
         END OF ty_scale_ticket.

  TYPES: BEGIN OF ty_movement,
           matnr TYPE c LENGTH 18,
           werks TYPE c LENGTH 4,
           bwart TYPE c LENGTH 3,
           menge TYPE p LENGTH 13 DECIMALS 3,
           meins TYPE c LENGTH 3,
         END OF ty_movement.

  TYPES ty_movements TYPE STANDARD TABLE OF ty_movement WITH DEFAULT KEY.

  CONSTANTS c_bwart_goods_receipt TYPE c LENGTH 3 VALUE '101'.
  CONSTANTS c_bwart_consumption  TYPE c LENGTH 3 VALUE '261'.

ENDINTERFACE.
