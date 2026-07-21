<!-- mirror: https://cap.cloud.sap/docs/releases/2021/jan21 -->
<!-- fetched: 2026-05-09T02:26:26.747Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# January 2021 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtx?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

### New and Revised Guides ​

- New guide Project-Specific Configurations for the Node.js runtime has been created, which also apply for `@cds-compiler` and `@sap/cds`.
- Documentation for `cds build` configuration is now available. This is useful for projects that deviate from the standard folder layout.

### Improved Navigation ​

We take feedback seriously and therefore we've improved the navigation in our documentation. The section you're currently in will be now highlighted in the navigation on the left-hand side.

### Real-Time Search ​

The search ranking algorithm has been updated to show more accurate results. Additionally, capire can now be searched in real-time.

Full-text search results will be automatically highlighted and the scroll position is adjusted to display the first result.

## Command Line / Toolkit ​

### Important Changes❗️ ​

Both, preview for SAP Fiori and the `--with-mocks` option of `cds run`, are now disabled if `NODE_ENV` environment variable is set to `production`. These features are meant to help you during development and should not be used in productive applications.

You can still enable them with `cds.features.fiori_preview: true` and `cds.features.mocked_bindings: true`, respectively. As an example, this is how can you configure them in your project's *package.json*:

json

```
"cds": {
  "features": {
    "fiori_preview": true,
    "mocked_bindings": true
  }
}
```

### Create Projects with Multitenancy Support Beta ​

With `cds init --add mtx`, you can now create projects that are configured for multitenancy right from the start. This includes both, runtime and deploy configuration.
 In a future version, we'll also allow augmenting existing projects with `cds add mtx`.

## CDS Editors & Tools ​

The following features are available for all editors based on our language server implementation for CDS in SAP Business Application Studio, Visual Studio Code, and Eclipse. The plugins are available for download for Visual Studio Code at [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=SAPSE.vscode-cds#overview) and for Eclipse at [https://tools.hana.ondemand.com](https://tools.hana.ondemand.com/#cloud-vscodecds).

### Renaming VS Code Extension for CDS Language ​

The extension *SAP Cloud Platform core data services plug-in for Visual Studio Code* was renamed to *SAP CDS Language Support*.

Learn more about the [features and commands](/docs/tools/cds-editors) in the documentation and watch this short [video](https://www.youtube.com/watch?v=eY7BTzch8w0).

## Node.js Runtime ​

### Important Changes ❗️ ​

The following changes affect undocumented internal implementations, and hence shouldn't affect CAP-based projects. Nevertheless, they're listed here for your reference.

- Support for deprecated config `cds.auth.passport` was removed. Use `cds.requires.auth` instead.
- `@sap/cds-reflect` is no longer maintained. Use the reflection API of `@sap/cds` instead.

The following private APIs and configuration options are deprecated and will be removed in the future. Make sure you remove their usage.

- `req.run(...)`: use `cds.db.tx(req).run(...)` instead
- `cds.runtime.skipIntegrity`: use `cds.env.features.assert_integrity = false` instead or add annotation `@assert.integrity: false` at the respective service, entity, or association
- `cds.runtime.skipWithParameters`: use `cds.env.features.with_parameters = false` instead

### Logging Beta ​

`cds.log()` is used throughout the Node.js stack, including the inherited `@sap/odata-server`. This results in some changes to the log format. In general, more information is available in the logs. See section [cds.log()/node.js/cds-log) for more details.

Further, text keys are replaced by their language-independent texts before logging, for example, the message "MULTIPLE_ERRORS" will be replaced by the text in the language-independent text bundle with the key `MULTIPLE_ERRORS`, for example, "Multiple errors occurred. See the details for more information.".

### Protecting OData Metadata by Default ​

OData metadata endpoints -- that means, the service root `/` and the metadata endpoint `/$metadata` -- are protected by default if the respective service is protected through annotation `@requires`. This default protection can be deactivated through `cds.env.odata.protectMetadata = false`.

### SAP HANA ​

We've improved the robustness and observability of our SAP HANA usage, respectively its drivers:

- When using `hdb` (CAP's preferred option), the client is additional validated based on its error history. In turn, the automatic reconnect was removed as it can cause more harm in certain situations, which can't be safely determined in the application layer.
- Improved error login case of a timeout with a service unavailable error being returned to the client indicating it shall retry.
- The effective pool configuration is logged with level `info`.

Further, it's now possible to skip SAP HANA's localization feature (`WITH PARAMETERS ('LOCALE' = '')`) through `cds.env.features.with_parameters = false`. As this is a rather costly feature, we recommend doing so if it isn't needed.

### Generic Providers ​

The generic input validation was extended to include the typed parameters of actions and functions, excluding `array of` constructs.

Runtime-based integrity checks can now be deactivated through annotation `@assert.integrity: false` on entity and service level (additional to on association level) or global config `cds.env.features.assert_integrity = false`.

With regards to the draft choreography for SAP Fiori UIs, the Node.js runtime now supports the scenario "all active", that means, reading all active versions even of those entities where a draft exists. Further, the result of a draft activation is no longer expanded by default.

##### Miscellaneous ​

- ETag added for expanded entities
- Upsert target of to-one containment with foreign key in parent during deep update
- Server-side pagination when serving to REST

### Service Consumption ​

On an HTTP error (that means, status code 4xx) during remote service consumption, the error gets logged and a [bad gateway error](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502) is returned to the client. This helps identifying that the error originates in a remote app. Further, the details of the original error may disclose information that shall not reach the client.

##### Miscellaneous ​

- Support for filter on `null` values in service consumption
- The default query option `$format` was removed for `GET` requests to remote OData services

## Java SDK ​

### Important Changes ❗️ ​

#### Fixed ​

- Composite entities that are auto-exposed by the CDS Compiler can't be accessed directly by a request, if they aren't explicitly contained in the service definition.
- Associated entities that are auto-exposed by means of `@cds.autoexpose` are now read-only, if they aren't explicitly contained in the service definition.
- Draft administrative data is now created only once per deep draft document. Thus, changes in child entities are reflected directly in the common draft administrative data.

#### Deprecated ​

- The error messages for constraint violations have been improved by distinguishing not null constraint violations from unique constraint violations. With that, the previous general error code `409001` (`CONSTRAINT_VIOLATED`) has been deprecated and is replaced by the more specific error codes `409003` (`VALUE_REQUIRED`) and `409006` (`UNIQUE_CONSTRAINT_VIOLATED`).
- Renamed the configuration property `cds.datasource.serviceName` to `cds.datasource.binding` (previous name is deprecated, but still available).
- Renamed the configuration property `cds.security.xsuaa.serviceName` to `cds.security.xsuaa.binding` (previous name is deprecated, but still available).
- Added a new API to retrieve authentication information, for example the JWT token of the current user. It can be accessed by means of `CdsRuntime.getProvidedAuthenticationInfo()`. The new API replaces the former internal `AuthenticatedUserClaimProvider`.

### Native OData V2 Adapter GA ​

The native OData V2 is now generally available and can be used productively. We added the following features in this version:

- Support read requests with Parameterized Views.
- Support path expressions in `$filter` conditions. This allows filtering expanded deep documents based on conditions for properties in child entities. Note that the filter applies to the entire document in this case.
- Support multiple expands within a single query.
- OData V2 now provides `__deferred` links for unexpanded navigation properties.

Also, the [cds-services-archetype](/docs/java/developing-applications/building#the-maven-archetype) now supports creating new CAP Java projects with OData V2 support.

### Keys Contained in Data Accessor Objects ​

Key values contained in an OData `PATCH` or `PUT` request can now be accessed by means of the [data accessor objects](/docs/java/cds-data#generated-accessor-interfaces) passed to event handlers.

Previously, you had to use the following code to extract the keys of the entity that is updated:

java

```
@Before(event = CdsService.EVENT_UPDATE)
public void updateOrderItem(CdsUpdateEventContext context, OrderItems orderItem) {
    // access ID of orderItem
    String orderItemId = (String) CqnAnalyzer.create(context.getModel()).analyze(context.getCqn()).targetKeys().get(OrderItems.ID);
    // use it...
}
```

Now, you can achieve this much easier:

java

```
@Before(event = CdsService.EVENT_UPDATE)
public void updateOrderItem(OrderItems orderItem) {
    // access ID of orderItem
    String orderItemId = orderItem.getId();
    // use it...
}
```

### Maven Build Improvements ​

- The goal `install-cdsdk` of the cds-maven-plugin provides a new command line argument:yaml

```
cds.install-cdsdk.force=true
```

to enable updating the cds-dk (see also Maven Build Options
- The cds-maven-plugin now validates the installed version of cds-dk and reports an error for outdated installations.

### Messaging Foundation Beta ​

It's now possible to use technical [messaging services](/docs/java/messaging) with `cds.java@1.13.0`.

### CDS.ql Runtime ​

- The CDS Data Processor API Beta allows to validate, convert, and generate CDS data.
- Indexed parameters are introduced as replacement for the deprecated positional parameters.
- The new @cds.java.name annotation allows to define custom names for elements to be used when generating Java interfaces.
- Improve performance of deep update.
- Improve performance of search on SAP HANA: The SQL rendering for search on SQL backends has been changed for localized elements, besides in the user's language texts are now additionally searched in the default language. This optimization requires the `localized` association to the texts entity in the CDS model. See section Behind the Scenes for more details.
- Draft: Deletion isn't cascaded anymore to the `DraftAdministrativeData` of a non-root draft entity, because one deep draft document shares a single `DraftAdministrativeData` entity now.

### CDS Reflection API ​

- Support for Events referencing other Events, Entities, and Structured Types
- Support for Aspects

### Bug Fixes ​

- Fix projection resolvement of aliased to-many associations
- Fix SQL exception on updates having only key values as data
- Fix NoSuchElementException when using binary elements in where condition
