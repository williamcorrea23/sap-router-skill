# Web Service Consumption (Outbound HTTP/REST/SOAP)
Parent skill: vaibe-sap-developer
Load when: the user needs ABAP to call an external HTTP/REST API or a SOAP web service — not exposing one (that's `references/odata-fiori.md`), consuming one.

The released API differs by edition — pick the wrong one and the code won't even activate in a Cloud/BTP system.

## On-Premise / Private Edition — classic client, still works
```abap
cl_http_client=>create_by_destination(
  EXPORTING
    destination = 'Z_MY_RFC_DEST'
  IMPORTING
    client      = lo_http_client ).

lo_http_client->request->set_method( 'POST' ).
lo_http_client->request->set_cdata( lv_json_body ).
lo_http_client->send( ).
lo_http_client->receive( ).
lv_response = lo_http_client->response->get_cdata( ).
lo_http_client->close( ).
```

## Cloud Public Edition / BTP ABAP Environment — released API only
`cl_http_client` is **not** a released API there — use the destination-service-based client instead:
```abap
DATA(lo_destination) = cl_http_destination_provider=>create_by_comm_arrangement(
  comm_scenario     = 'Z_MY_SCENARIO'
  service_id        = 'Z_MY_SERVICE' ).

DATA(lo_client) = cl_web_http_client_manager=>create_by_http_destination( lo_destination ).
DATA(lo_request) = lo_client->get_http_request( ).
lo_request->set_text( lv_json_body ).
DATA(lo_response) = lo_client->execute( if_web_http_client=>post ).
lv_response = lo_response->get_text( ).
```
Rule: this requires a Communication Arrangement/Communication Scenario configured on the BTP/cloud side first — that's an admin setup step, not ABAP. Confirm it exists before generating the consuming class against it.

## SOAP web service consumption
Classic SOAP proxy generation (SE80 → consumer proxy from WSDL) is On-Premise/Private Edition only — not available in Cloud Public Edition or BTP ABAP Environment, where REST/OData is the expected integration style instead. If the user needs SOAP under a cloud edition, say so and ask whether a REST/OData equivalent of the target service exists.

## JSON/XML handling
```abap
DATA(lo_writer) = cl_sxml_string_writer=>create( type = if_sxml=>co_xt_json ).
CALL TRANSFORMATION id SOURCE data = ls_payload RESULT XML lo_writer.
lv_json = cl_abap_codepage=>convert_from( lo_writer->get_output( ) ).
```
Rule: use `/ui2/cl_json` or `CALL TRANSFORMATION id` for JSON serialization — don't hand-build JSON strings via concatenation, that's a frequent source of malformed payloads.

## Anti-patterns
- Don't use `cl_http_client` directly for Cloud Public Edition/BTP — it's not released there even though it may compile in some tenants; use the destination-service client instead.
- Don't hardcode endpoint URLs in the ABAP class — always resolve via RFC destination (On-Premise) or Communication Arrangement (cloud).
- Don't skip response status-code checking — treat any non-2xx as an error path, not just a transport-layer failure.
