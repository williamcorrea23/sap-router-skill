@AccessControl.authorizationCheck: #CHECK
@Metadata.allowExtensions: true
@EndUserText.label: 'Projection View for Z_R_AKP_ACONN'
define root view entity Z_C_AKP_ACONN
  provider contract transactional_query
  as projection on Z_R_AKP_ACONN
{
  key UUID,
      CarrierID,
      ConnectionID,
      AirportFromID,
      CityFrom,
      CountryFrom,
      AirportToID,
      CityTo,
      CountryTo,
      LocalLastChangedAt

}
