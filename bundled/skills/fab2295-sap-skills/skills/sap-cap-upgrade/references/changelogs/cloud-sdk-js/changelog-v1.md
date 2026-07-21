<!-- mirror: https://sap.github.io/cloud-sdk/docs/js/v1/release-notes -->
<!-- fetched: 2026-05-09T02:26:57.074Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
This is documentation for SAP Cloud SDK **v1**, which is no longer actively maintained.For up-to-date documentation, see the **[latest version](/cloud-sdk/docs/js/release-notes)** (v4).[](https://github.com/SAP/cloud-sdk-js)
[](https://opensource.org/licenses/Apache-2.0)

## Should I Update?​

We highly recommend updating to the latest SAP Cloud SDK version regularly.

It will help you:

- Ensure access to the latest SAP Cloud SDK features

- Keep up with the latest changes on SAP Business Technology Platform

- Update client libraries giving access to the latest SAP services on SAP Business Technology Platform and SAP S/4HANA.

- Protect yourself from bugs and breaking changes in the future

What are pregenerated typed client libraries (VDM)?

These libraries are free (but not open-source) and distributed under the SAP Developer license through [npmjs.com](https://www.npmjs.com/search?q=%40sap%2Fcloud-sdk-vdm-*).
You can generate a typed client library yourself by using our [OData generator](/cloud-sdk/docs/js/v1/features/odata/generate-client) and [Open API](/cloud-sdk/docs/js/v1/features/openapi/generate-client).
To easily search for services and get typed client library for them, use our [API Business Hub integration](https://blogs.sap.com/2021/09/17/the-sap-cloud-sdk-integrates-with-the-sap-api-business-hub/).

## 1.54.1 [Core Modules] - Feb 18, 2022​

### Improvements​

- [core] Announce 2.0 release in the `postinstall` script.

## 2.0.0 [Client Libraries] - Feb 10, 2022​

### New Functionality​

- We released a regular update for pregenerated client libraries (also known as VDM) for the latest SAP S/4HANA Cloud release 2022.

The update covers all the changes to existing OData services and introduces new ones.

- We released a regular update for pregenerated client libraries (also known as VDM) for the latest RTC release 2021 FPS1 of SAP S/4HANA On-premise.

The update covers all the changes to existing OData services and introduces new ones.

## 2.0.0 [Core Modules] - Feb 03, 2022​

We released version 2 :partying_face:
Be mindful of breaking changes when upgrading.
Enjoy multiple improvements and new features.
Check the [upgrade guide](https://sap.github.io/cloud-sdk/docs/js/guides/upgrade-to-version-2).

### Compatibility Notes​

- Upgrade the ES version to `es2019`.

### New Functionality​

- [connectivity] Create a new package with minimal API.

- [connectivity] Add `registerDestination` function to create destinations in the `destinations` environment variable.

- [connectivity] Support the `SamlAssertion` flow in destination retrieval.

- [http-client] Create a new package with minimal API.

### Removed functionality​

- [generator] Remove the option: `aggregatorDirectoryName` and `aggregatorNpmPackageName`

- [generator] Remove the option: `generateTypedocJson`

- [generator] Remove `packageJson` function from aggregator-package

- [core] Remove some functions

- [analytics] Remove the `@sap-cloud-sdk/analytics` package

### New module structure​

- [core] We have split the `core` package into smaller packages, so functions are moved to the target package.

### Changed signatures​

- [core] `EdmTypeField` only support EDM types, no field types in generics

### Changed implementation​

- [generator] changed the following implementations

`ServiceNameFormatter` deprecated constructor removed, reserverdName parameter from typeNameToFactoryName method removed

- `VdmNavigationpropety` multiplicity, isMultiLink removed

- `VdmFunctionImportReturnType` isMulti removed

- [openapi] changed the following implementations

`execute` Request Builder APIs changed to use a single parameter, either a Destination or DestinationFetchOptions.

- `executeRaw` Request Builder APIs changed to use a single parameter, either a Destination or DestinationFetchOptions.

- [odata-common] changed the following implementations

`ComplexTypeField` deprecated constructors removed

- `Constructable` Selectable removed

- `CreateRequestBuilderBase` prepare removed

- `EntityBase` getCurrentMapKey, initializeCustomFields removed

- `EnumField` edmType removed

- `Filter` _fieldName property removed

- `FilterFunction` toString, transformParameter removed

- `Link` clone, selects removed

- `MethodRequestBuilder` withCustomHeaders, withCustomQueryParameters, withCustomServicePath removed, build protected

- `ODataRequestConfig` contentType, deprecated constructor removed

- `ODataBatchRequestConfig` batchId, content_type_prefix removed

- `OneToOneLink` clone removed

- `UpdateRequestBuilderBase` prepare, requiredFields, ignoredFields, withCustomVersionIdentifier removed

- `execute` Request Builder APIs changed to use a single parameter, either a Destination or DestinationFetchOptions..

- `executeRaw` Request Builder APIs changed to use a single parameter, either a Destination or DestinationFetchOptions.

- [odata-v2] changed the following implementations

`execute` Request Builder APIs changed to use a single parameter, either a Destination or DestinationFetchOptions.

- `executeRaw` Request Builder APIs changed to use a single parameter, either a Destination or DestinationFetchOptions.

- [odata-v4] changed the following implementations

`execute` Request Builder APIs changed to use a single parameter, either a Destination or DestinationFetchOptions.

- `executeRaw` Request Builder APIs changed to use a single parameter, either a Destination or DestinationFetchOptions.

- [connectivity] changed the following implementations

`getDestination` changed to use DestinationFetchOptions as single parameter.

- `getProxyRelatedAuthHeaders` legacyNoAuthOnPremiseProxy case removed

- `serviceToken` uses `JWT` instead of userJwt now.

- `jwtBearerToken` uses `JWT` instead of userJwt now.

- `fetchVerificationKeys` merged with `executeFetchVerificationKeys`, now only accepts URL as parameter

- [http-client] changed the following implementations

`executeHttpRequest` fetches CsrfToken for non-GET requests by default.

## 1.54.0 [Core Modules] - Feb 02, 2022​

### New Functionality​

- [core] A new proxy type `PrivateLink` is now supported. This proxy type is used when your destination represents a tunnel created via Private Link Service.

## 1.53.1 [Core Modules] - Jan 18, 2022​

[GitHub](https://github.com/SAP/cloud-sdk-js/releases/tag/v1.53.1) | [npm](https://www.npmjs.com/search?q=%40sap-cloud-sdk)

### Improvements​

- We updated the version of `@sap/edm-converters` to ensure Node 14 compatibility for the OData code generator.

### Fixed Issues​

- We fixed the missing token in the header issue for `OAuth2Password` authentication type.

## [CLI] - Jan 5, 2022​

[GitHub](https://github.com/SAP-archive/cloud-sdk-cli) | [npm](https://www.npmjs.com/package/@sap-cloud-sdk/cli)

- Archive the GitHub repository.

- Deprecate the npm package.

## [Sample Projects] - Jan 5, 2022​

[GitHub](https://github.com/SAP-samples/cloud-sdk-js)

- Publish the GitHub repository, showcasing the SAP Cloud SDK for JavaScript.

## 1.53.0 [Core Modules] - December 9, 2021​

[GitHub](https://github.com/SAP/cloud-sdk-js/releases/tag/v1.53.0) | [npm](https://www.npmjs.com/search?q=%40sap-cloud-sdk)

### Fixed Issues​

- Fix destination retrieval in multi-tenant use cases and user based authorization flows like `OAuth2UserTokenExchange`, `OAuth2SAMLBearerAssertion` or `OAuth2JWTBearer`.
If the destination is maintained in the provider account and a subscriber JWT is provided the `X-user-token` is set with the subscriber JWT.
This is crucial to determine the tenant, if the `tokenServiceUrlType` of the destination is common.

- Fix missing X-tenant header, if the authentication flow is `OAuth2ClientCredentials` and the `tokenServiceUrlType` of the destination is common.

## 1.28.2 [Client Libraries] - November 17, 2021​

### Compatibility Notes​

- We stopped generating API documentation for typed client libraries.
You can discover all required API information via your IDE features like autocomplete and IntelliSense.

### New Functionality​

- We released a regular update for pregenerated client libraries (also known as VDM) for the latest RTC release 2111 of SAP S/4HANA Cloud.

The update covers all the changes to existing OData services and introduces new ones.

- We released a regular update for pregenerated client libraries (also known as VDM) for the latest RTC release 2021 FPS0 of SAP S/4HANA On-premise.

The update covers all the changes to existing OData services and introduces new ones.

- We released a regular update for pregenerated client libraries for Workflow API for Cloud Foundry.

## 1.52.0 [Core Modules] - November 5, 2021​

[GitHub](https://github.com/SAP/cloud-sdk-js/releases/tag/v1.52.0) | [npm](https://www.npmjs.com/search?q=%40sap-cloud-sdk)

### Compatibility Notes​

- We changed default cache isolation strategy from `IsolationStrategy.Tenant` to `IsolationStrategy.Tenant_User`.
This applies when you set `useCache` to `true` while using a `getDestination` method for a destination lookup.

### Fixed Issues​

- We now cache a destination only when a `JWT` contains all necessary information about a `Tenant` and a `User`.
For example, when using `IsolationStrategy.Tenant_User`, the JWT has to contain both tenant id and user id.

- If `JWT` has an expiration time, we'll use it to override the default cache expiration time of 5 minutes.

- A provider token won't be used to retrieve a destination from cache from now on.

## 1.27.0 [Client Libraries] - Aug 20, 2021​

### New Functionality​

- We released a regular update for pregenerated client libraries (also known as VDM) for the latest RTC release 2108 of SAP S/4HANA Cloud.

The update covers all the changes to existing OData services and introduces new ones.

- The service `API_CDR_FILE_DOWNLOAD_SRV` is not included and will be released with the next release or on-demand.

## 1.26.0 [Client Libraries] - June 04, 2021​

- API documentation

- We released a regular update for pregenerated client libraries (also known as VDM) for the latest RTC release 2020 FPS2 of SAP S/4HANA On-premise.

The update covers all the changes to existing OData services and introduces new ones.

- We released a regular update for pregenerated client libraries (also known as VDM) for the latest RTC release 2105 of SAP S/4HANA Cloud.

The update covers all the changes to existing OData services and introduces new ones.

- The missing service `CACREDITWORTHINESS_0001` is included.

- We released a regular update for pregenerated client libraries for Workflow API for Cloud Foundry.

## 1.25.0 [Client Libraries] - May 20, 2021​

### New Functionality​

- We released a regular update for pregenerated client libraries (also known as VDM) for the latest RTC release 2105 of SAP S/4HANA Cloud.

The update covers all the changes to existing OData services and introduces new ones.

- The service `CACREDITWORTHINESS_0001` is not included and will be released later.

## 1.24.0 [Client Libraries] - January 18, 2021​

- API documentation

### Compatibility Notes​

- A few operations were removed from some SAP S/4HANA Cloud 2102 services. These operations were never supported by the SAP S/4HANA system (like CRUD support for some entities), so no existing functionality is affected. The following services are affected:

Nota Fiscal – Create, Update - `API_LOGBR_NOTAFISCAL_SRV`

- Purchase Contracts - `API_PURCHASECONTRACT_PROCESS_SRV`

- Outbound Delivery (A2X) - `API_OUTBOUND_DELIVERY_SRV_0002`

- The service `@sap/cloud-sdk-vdm-purchasing-inforecord-service` was renamed to `@sap/cloud-sdk-vdm-purchasing-info-record-service`.

### New Functionality​

- We released a regular update for pregenerated client libraries (also known as VDM) for the latest RTC release 2102 of SAP S/4HANA Cloud.

The update covers all the changes to existing OData services and introduces new ones.

- We released a regular update for pregenerated client libraries (also known as VDM) for the latest RTC release 2020 FPS1 of SAP S/4HANA On-premise.

The update covers all the changes to existing OData services and introduces new ones.

## 1.22.0 [Client Libraries] - November 6, 2020​

- API documentation

### New Functionality​

- We released a regular update for pregenerated client libraries (also known as VDM) for the latest RTC release 2011 of SAP S/4HANA Cloud.

The update covers all the changes to existing OData services and introduces new ones.

## 1.21.0 [Client Libraries] - September 10, 2020​

- API documentation

### New Functionality​

- We released an extracurricular update for pregenerated client libraries (also known as VDM) for the latest RTC release 2008 of SAP S/4HANA Cloud.

The update introduces new libraries for the SAP S/4HANA OData v4 services.

## 1.20.0 [Client Libraries] - August 13, 2020​

- API documentation

- npm

### New Functionality​

- We released a regular update for pregenerated client libraries (also known as VDM) for the latest RTC release 2008 of SAP S/4HANA Cloud.

The update covers all the changes to existing OData v2 services and introduces new ones.

- Should I Update?
- 1.54.1 [Core Modules] - Feb 18, 2022Improvements

- 2.0.0 [Client Libraries] - Feb 10, 2022New Functionality

- 2.0.0 [Core Modules] - Feb 03, 2022Compatibility Notes
- New Functionality
- Removed functionality
- New module structure
- Changed signatures
- Changed implementation

- 1.54.0 [Core Modules] - Feb 02, 2022New Functionality

- 1.53.1 [Core Modules] - Jan 18, 2022Improvements
- Fixed Issues

- [CLI] - Jan 5, 2022
- [Sample Projects] - Jan 5, 2022
- 1.53.0 [Core Modules] - December 9, 2021Fixed Issues

- 1.28.2 [Client Libraries] - November 17, 2021Compatibility Notes
- New Functionality

- 1.52.0 [Core Modules] - November 5, 2021Compatibility Notes
- Fixed Issues

- 1.27.0 [Client Libraries] - Aug 20, 2021New Functionality

- 1.26.0 [Client Libraries] - June 04, 2021
- 1.25.0 [Client Libraries] - May 20, 2021New Functionality

- 1.24.0 [Client Libraries] - January 18, 2021Compatibility Notes
- New Functionality

- 1.22.0 [Client Libraries] - November 6, 2020New Functionality

- 1.21.0 [Client Libraries] - September 10, 2020New Functionality

- 1.20.0 [Client Libraries] - August 13, 2020New Functionality
