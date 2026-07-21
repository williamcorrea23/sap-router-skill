@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Carrier Value help'
define view entity ZAKP_I_CarrierVH
  as select from /dmo/carrier
{
      @UI.lineItem: [{ position: 10 }]
  key carrier_id as CarrierId,
      @UI.lineItem: [{ position: 20 }]
      name       as Name

}
