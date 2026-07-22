REPORT zgm_pricing_margin_report.

"* Margin analysis for finished-goods deliveries: reads sales orders and the
"* classic pricing condition table KONV to compute realized surcharges.

PARAMETERS p_vkorg TYPE c LENGTH 4 OBLIGATORY.
PARAMETERS p_datab TYPE d.

TYPES: BEGIN OF ty_price,
         knumv TYPE c LENGTH 10,
         kposn TYPE n LENGTH 6,
         kschl TYPE c LENGTH 4,
         kbetr TYPE p LENGTH 11 DECIMALS 2,
       END OF ty_price.

DATA gt_orders TYPE STANDARD TABLE OF vbak WITH DEFAULT KEY.
DATA gt_prices TYPE STANDARD TABLE OF ty_price WITH DEFAULT KEY.

START-OF-SELECTION.
  PERFORM load_orders.
  PERFORM load_conditions.
  PERFORM check_order_status.
  PERFORM write_margins.

FORM load_orders.
  SELECT * FROM vbak
    INTO TABLE gt_orders
    UP TO 500 ROWS
    WHERE vkorg = p_vkorg
      AND erdat >= p_datab.
ENDFORM.

FORM load_conditions.
  " NOTE: KONV was replaced by PRCD_ELEMENTS in S/4HANA.
  LOOP AT gt_orders INTO DATA(ls_order).
    SELECT knumv kposn kschl kbetr
      APPENDING TABLE gt_prices
      FROM konv
      WHERE knumv = ls_order-knumv
        AND kschl IN ('ZPRS', 'ZSUR').
  ENDLOOP.
ENDFORM.

FORM check_order_status.
  " NOTE: VBUK (header status) was eliminated in S/4HANA; status fields moved
  " into VBAK. This read must be redirected.
  LOOP AT gt_orders INTO DATA(ls_order).
    SELECT SINGLE gbstk FROM vbuk
      INTO @DATA(lv_gbstk)
      WHERE vbeln = @ls_order-vbeln.
    IF lv_gbstk = 'C'.
      DELETE gt_orders.
    ENDIF.
  ENDLOOP.
ENDFORM.

FORM write_margins.
  DATA lv_sum TYPE p LENGTH 15 DECIMALS 2.
  LOOP AT gt_prices INTO DATA(ls_price).
    lv_sum = lv_sum + ls_price-kbetr.
  ENDLOOP.
  WRITE: / 'Orders analyzed:', lines( gt_orders ).
  WRITE: / 'Condition lines:', lines( gt_prices ).
  WRITE: / 'Surcharge total:', lv_sum.
ENDFORM.
