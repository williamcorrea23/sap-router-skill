<!-- mirror: https://cap.cloud.sap/docs/releases/2023/changelog -->
<!-- fetched: 2026-05-09T02:26:16.940Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# Changelog 2023 ​

## December 2023 ​

### Added ​

- [cds-dk@7.5.0] `cds add` plugin support Beta.
- [cds-dk@7.5.0] `cds compile` to `openapi` now creates readonly endpoints for entities annotated with `@cds.autoexpose(d)`.
- [cds-dk@7.5.0] `cds compile` to `openapi` now supports deepInsert and deepUpdate in case of entity property containing a composition.
- [cds-dk@7.5.0] `cds add liquibase` support for Java.
- [vscode-cds@7.5.0] Unused imports are reported as warning and grayed out incl. quickfix to remove them
- [vscode-cds@7.5.0] Snippet proposals for artifact elements in an `annotate` statement
- [vscode-cds@7.5.0] New user setting `cds.contributions.enablement.additionalAnalyticalAnnotations` (default: off) to get annotation support for analytical queries (experimental)
- [cds-compiler@4.5.0] parser: `annotate` can now annotate entity parameters, elements and bound actions in one statement.
- [cds-compiler@4.5.0] compiler: A single `annotate` statement can now be used to annotate parameters, elements and bound actions in one statement.
- [cds-compiler@4.5.0] to.edm(x): Key elements of type `cds.UUID` are annotated with `@Core.ComputedDefaultValue` if they are defined directly in the entity. Elements of type `cds.UUID` that are defined in a named structured type and used to define a key element are not annotated, instead a warning is raised if such elements are not annotated with `@Core.ComputedDefaultValue`.
- [cds-compiler@4.5.0] to.sql|hdi: Add option `withHanaAssociations` which, for sqlDialect `hana`, allows suppressing the generation of the `WITH ASSOCIATIONS`.
- [cds.java@2.5.0] EDMX metadata loaded from MTXS sidecar is now localized lazily, if `cds.odata-v4.lazy-i18n.enabled` is set to `true`. This avoids caching different translations of the same EDMX in memory.
- [cds.java@2.5.0] `CqnService` beans, whose name match their CDS definition are now marked as primary, avoiding `@Qualifier` annotations when autowiring these.
- [cds.java@2.5.0] `app_tid` is now preferred over `zoneId` when reading tenants from Subscription Manager Service.
- [cds.java@2.5.0] The function `matchesPattern` is now supported in incoming and outgoing OData V4 requests.
- [cds.java@2.5.0] The `where` property of `@restrict` annotations now supports expressions as alternative to the String format.
- [cds.java@2.5.0] Draft GC for a specific tenant and service now occurs asynchronously as a side effect of a draft activation.
- [cds.java@2.5.0] Feature `cds-feature-auditlog-v2` now also supports the service plan `premium` of the Audit Log Service and, by that, can be used by external customers.
- [cds.java@2.5.0] Creation of CAP-specific spans for Open Telemetry can be controlled using a dedicated logger `com.sap.cds.otel.span`.
- [cds4j@2.5.0] CDS Model Reader: Support expressions in annotations
- [cds4j@2.5.0] SAP HANA JSON Document Store: support `orderBy` for queries that target a document collection
- [cds4j@2.5.0] New `CQL.matchesPattern` filter with regular expression support
- [cds4j@2.5.0] The code generator supports annotating services with `@cds.java.name` to customize the name of the corresponding generated service interface
- [cds4j@2.5.0] Beta: Support using session context variable `$tenant` in view definitions
- [cds4j@2.5.0] Beta: Capture transformation from OData v4's `$apply` option as `CqnTransformation`s
- [cds4j@2.5.0] Beta: Support updates with expressions via `Update::set` method
- [cds@7.5.0] Support for expressions in where clause of `@restrict` annotation.Example: `@(restrict : [{ grant : ['*'], where : (NAME = $user) }])`

- [cds@7.5.0] Function `cds.unboxed(srv)` to get the non-outboxed variant of the service
- [cds@7.5.0] Service implementations can now be provided in .mjs modules.
- [cds@7.5.0] Remote services: advanced configurable `CSRF` token fetching HTTP method and the URL. For example, in the configuration of your remote services, you can now configure the HTTP method and URL as follows:json

```
"cds": {
  "requires": {
    "API_BUSINESS_PARTNER": {
      "kind": "odata",
      "model": "srv/external/API_BUSINESS_PARTNER",
      "csrf": { // this configuration implies `csrf: true`
        "method": "get",
        "url": "..."
      }
    }
  }
}
```
- [cds@7.5.0] `cds.log`'s built-in JSON formatter:Extract custom fields (`cds.env.log.als_custom_fields`) and categories from args (not only error-like first objects) Example: `LOG.info('foo', { query: 'SELECT * FROM DUMMY' }, 'bar', { categories: ['baz'] })`

- `cds.env.log.mask_headers = [...]` allows to specify a list of matchers for which the header value shall be masked (i.e., printed as `***`) Default: `['/authorization/i', '/cookie/i']`

- [cds@7.5.0] `cds.env.fiori.bypass_draft` feature flag, designed to enable direct modifications via `POST` and `PATCH` of active instances in lean draft mode (`cds.env.fiori.lean_draft=true`). For example:

http

```
POST /Orders
{
  "IsActiveEntity": true
}
```

- [cds@7.5.0] Auth kind `ias`: same SAML attr API as auth kind `xsuaa` for easier migration

### Changed ​

- [cds-dk@7.5.0] `cds add application-logging` can now be used in place of `cds add kibana`. `cds add kibana` is deprecated.
- [cds-dk@7.5.0] `cds add application-logging` now uses the `standard` service plan in the `mta.yaml`, instead of `lite`.
- [cds-dk@7.5.0] `cds add application-logging` doesn't add the `cds.features.kibana_formatter` flag any more.
- [cds-dk@7.5.0] `cds v -i` will now insert a default placeholder if `repository` or `repository.url` is undefined in your `package.json`.
- [cds-dk@7.5.0] Use supported node versions in SAP HANA database modules.
- [cds-dk@7.5.0] `cds build` uses console.log to correctly format log output.
- [cds-dk@7.5.0] Retrofit `cds build` plugin register API.
- [cds-dk@7.5.0] `cds build` log output has been streamlined.
- [cds-compiler@4.5.0] Update OData Vocabulary: 'Common'.
- [cds-compiler@4.5.0] api: Reject CSN as input in backends, if it is a CSN in flavor `parsed` with a non-empty `requires` array. Reason being that the model is not considered a "full" CSN, as dependencies were not resolved.
- [cds.java@2.5.0] The periodic draft GC job pauses for some time after each GC execution for a tenant to reduce load on the MTXS sidecar.
- [cds.java@2.5.0] The outbox processor now checks existence of outbox entries using the base model, before processing outbox entries, to reduce load on the MTXS sidecar.
- [cds@7.5.0] Removed and integrated former `ctx-auth` middleware into `cds.auth` middleware
- [cds@7.5.0] `cds.log`: `cds.env.log.format = 'plain'|'json'` allows to configure which built-in formatter is used. Defaults to `json` in production, `plain` otherwise.
- If a built-in JSON formatter is used: Field `tenant_subdomain` is filled if running on CF and information is available through authentication
- Additional CF-related fields are filled if running on CF
- Custom fields (`cds.env.log.als_custom_fields`) are filled if bound to an instance of Application Logging Service
- Field `categories` is filled if bound to an instance of Application Logging Service

- Config `cds.env.log.kibana_custom_fields` changed to `cds.env.log.als_custom_fields` (ALS = Application Logging Service) with compatibility until the next major

- [cds@7.5.0] Package `passport` is no longer required (if `cds.env.requires.middlewares` is not set to `false`)
- [cds@7.5.0] Type definitions for the APIs of this package are now maintained in package `@cap-js/cds-types`. If you used one of the types `CSN`, `Definitions`, `entity` of @sap/cds/apis/reflect, use the `Linked` counterparts instead.
- If you used the type `CQNQuery` of @sap/cds/apis/cqn, use `SELECT` or a union type instead.
- This also includes various fixes to Typings for `req.subject` like `SELECT.from(req.subject)`
- `SELECT.columns([...])`
- `cds.db`
- `cds.util`
- `cds.context.features`

- [cds@7.5.0] The number of files logged on `cds serve` is now limited to 30 by default. You can run with `DEBUG=serve` to show all files.
- [cds@7.5.0] `express.static` is only mounted if the target folder (`cds.folders.app`) exists
- [cds@7.5.0] `cds.outbox.Messages` no longer uses aspect `cuid` to reduce model size impact in case `@sap/cds/common` is not used otherwise
- [cds-mtxs@1.14.1] `lazyT0` now also works in a sidecar scenario with `multitenancy` not explicitly set to `true`.
- [cds-mtxs@1.14.1] The default for `cds.requires.multitenancy.jobCleanupIntervalStale` is reduced from one week to two days.
- [cds-mtxs@1.14.0] Various performance improvements for retrieving EDMX or CSN models.
- [cds-mtxs@1.14.0] Improved logging for `cds.xt.JobsService` or `cds.xt.DeploymentService`.
- [cds-mtxs@1.13.4] The built-in Service Manager client uses async APIs for creating or deleting service bindings by default.

### Fixed ​

- [cds-dk@7.5.0] `cds add postgres` for Java now uses the `default` profile when called without the `--for` option.
- [cds-dk@7.5.0] `cds compile` to `openapi` now adds `title` and `description` from `@Core.Description` and `@Core.LongDescription` respectively to reduce duplicate descriptions.
- [cds-dk@7.5.0] `cds build --production` now loads cds plugins from `devDependencies`.
- [cds-dk@7.5.0] Less redundant messages on request errors.
- [cds-dk@7.5.0] Avoid empty error message when `cds push` fails.
- [cds-dk@7.5.0] Better type definitions for programmatic APIs provided by `cds-dk`.
- [cds-dk@7.5.0] Better error message if old `@sap/cds` versions <= 5 are used.
- [cds-dk@7.5.0] Calls from Yeoman generator are now handled correctly.
- [cds-dk@7.5.0] `cds compile` to `openapi` now adds correct schema `$ref` for patch operation.
- [vscode-cds@7.5.0] CDS schema loading is more robust
- [vscode-cds@7.5.0] Removed failing `copy` function for code blocks from `CAP Release Notes`
- [vscode-cds@7.5.0] CAP with Typescript Beta: command line for creating types now also works correctly on Windows
- [vscode-cds@7.5.0] Padding and highlighting of identifiers with Unicode characters
- [vscode-cds@7.5.0] Highlighting of `stored` keyword
- [cds-compiler@4.5.0] compiler: Fix false positives of cyclic dependencies for calculated elements.
- Fix cardinality on source associations when publishing them with a filter (+ different cardinality) in a projection. The cardinality was incorrectly changed on the source as well.

- [cds-compiler@4.5.0] CDL parser: More numbers that would lose relevant digits due to precision loss are stored as strings in CSN (i.e. `{ "literal":"number", "val": "1.0000000000000001" }`).
- Nested table expressions and queries in the FROM clause (with surrounding parentheses) could cause some constructs such as `virtual` to be not properly parsed.

- [cds-compiler@4.5.0] to.hdi.migration: Don't drop-create the primary key when only a doc-comment has changed.
- [cds-compiler@4.5.0] to.cdl: Fix edge case where `@A.![B#]` was not rendered correctly.
- [cds-compiler@3.9.12] compiler: SQL function `STDDEV(*)` was not parsable.
- Numbers in scientific notation `-1e1` were sometimes not recognized via CSN input.

- [cds-compiler@3.9.12] for.odata: Fix crash when using a projection with associations as action parameter type.
- [cds-compiler@3.9.12] for.hana: Fix a bug in association to join translation, expect ON condition operand to be a function without arguments.
- [cds-compiler@3.9.12] to.edm(x): Omit `EntitySet` attribute on `Edm.FunctionImport` and `Edm.ActionImport` that return a singleton.
- Don't render `Scale: variable` for `cds.Decimal(scale:0)`.

- [cds-compiler@3.9.12] to.sql/hdi/hdbcds: consider `having` predicate for `exists` expansion
- [cds.java@2.5.0] Fixed a bug, causing `internal-user` role not correctly set on the system user of the provider tenant.
- [cds.java@2.5.0] Fixed a bug, causing OData Serializer to return `0E-8` for zero-value (`0`) Decimals.
- [cds.java@2.5.0] Fixed a bug, causing `/$count` requests to fail on draft-enabled entities.
- [cds.java@2.5.0] Fixed a bug, causing number values to be handled incorrectly for messaging queue configurations.
- [cds.java@2.4.1] Fixed a bug, causing requests to MTX Sidecar during shutdown of the application.
- [cds.java@1.34.8] Fixed a bug, causing audit log messages not being written on behalf of the named user when the persistent outbox is used.
- [cds@7.5.1] Resolving custom authentication implementation pointer
- [cds@7.5.0] Messaging: Listen to `*`
- [cds@7.5.0] Drafts of `@readonly` entities cannot be deleted
- [cds@7.5.0] Made `srv.prepend()` robust by not allowing async callbacks and hence not being an async function itself anymore
- [cds@7.5.0] Formatting for stringified number-literal value
- [cds@7.5.0] Secrets are now masked with `DEBUG=cds.service.factory`
- [cds@7.5.0] The timestamp of cds.context is not propagated to new root contexts
- [cds@7.5.0] `cds.localize` uses less memory to create translation bundles
- [cds@7.5.0] `UPSERT` operation failed to fill DateTime/Timestamp fields
- [cds@7.5.0] Use original logic (based on `NODE_ENV`) to load cds plugins from `devDependencies`
- [cds@7.5.0] Property `tenant` also available on express' `req` object with basic and mocked auth
- [cds@7.5.0] Empty `req.data` in before `DELETE` handler in draft
- [cds@7.5.0] Loading `cds-plugins` now offers a hook to add a more flexible plugin loader, e.g., for corrupt `package.json` files.
- [cds@7.5.0] Ignore default values of associations for draft entities
- [cds@7.5.0] OData: client-side errors (4xx) logged as warnings instead of errors
- [cds@7.5.0] IAS authentication: use `tokenInfo.getClientId()` instead of `payload.azp` as it implements a fallback
- [cds@7.5.0] Deep updates with binary keys
- [cds@7.5.0] Allow `null` values in `cds.env` (example package.json excerpt: `{ "cds": { "features": { "foo": null } } }`)
- [cds@7.5.0] Collection-bound actions/functions called via navigation
- [cds-mtxs@1.14.1] A sidecar setup can be started for local development even with `multitenancy: false`.
- [cds-mtxs@1.14.1] Additional resilience measures for the new Service Manager APIs if a healthy instance exists, but no binding.
- [cds-mtxs@1.14.1] `cds.env.requires.['cds.xt.ModelProvideService'].loadSync = true` can be set to skip using worker threads when loading the application model.
- [cds-mtxs@1.13.3] `PUT /-/cds/saas-provisioning/tenant` can now be used for upgrade purposes with shared deployment directories in non-extensible apps.
- [cds-mtxs@1.13.3] `POST /-/cds/saas-provisioning/upgrade` correctly determines the deployment directory in non-extensible apps if just one tenant is passed in the request body.
- [cds-mtxs@1.13.2] Projects with `cds.features.assert_integrity = 'db'` don't generate constraints for `t0` any more.
- [cds-mtxs@1.13.2] Deployment resources for `t0` are not created in the `base` directory any more.
- [cds-mtxs@1.13.2] Fixed a race condition for the shared `base` directory.

### Removed ​

- [cds-compiler@4.5.0] to.edm(x): Remove option `--odata-open-type` introduced with 4.4.0.
- [cds@7.5.0] Deprecated global configuration feature flag `cds.env.features.fetch_csrf`. Instead, please use `csrf` and `csrfInBatch` to configure your remote services. These options will allow to configure CSRF-token handling.
- [cds@7.5.0] Compat for deprecated `cds.env.auth.passport`. Use `cds.env.requires.auth` instead.

## November 2023 ​

### Added ​

- [cds-dk@7.4.0] `cds init` for Node.js now has `@cds-models` for `@cap-js/cds-typer` in its `.gitignore`.
- [cds-dk@7.4.0] `cds add local-messaging` is now supported for Node.js.
- [cds-dk@7.4.0] `cds add postgres` is now supported for Java.
- [cds-dk@7.4.0] `cds build` now supports the command line argument `--no-clean` Beta. Clients need to clean the output folder(s) manually for consistent build results.
- [cds-dk@7.4.0] `cds build` now supports the build task option `flavorLocalizedEdmx` to generate localized instead of non-localized edmx files for Java apps - default is `false`.
- [cds-dk@7.4.0] `cds subscribe`, `cds unsubscribe`, `cds upgrade` now also support the `--resolve-bindings` flag.
- [cds-dk@7.4.0] `cds build` now supports the command line argument `--ws` to enable tarball based packaging of npm workspace dependencies for Node.js apps. Beta
- [cds-dk@7.4.0] `cds build` now supports SAP HANA schema evolution for draft tables.
- [cds-compiler@4.4.0] compiler: International letters such as `ä` can now be used in CDS identifiers without quoting. Unicode letters similar to JavaScript are allowed.
- [cds-compiler@4.4.0] to.edm(x):Allow to render all complex types within a requested service as `OpenType=true` with option `--odata-open-type`. Explicit `@open: false` annotations are not overwritten.
- Allow to annotate the generated draft artifacts but not generated foreign keys (as with any other managed association).

- [cds-compiler@4.4.0] to.sql|hdi|hdbcds: Allow annotating the generated `.drafts` tables.
- [cds.java@2.4.0] Select queries on draft-enabled entities are now optimized and executed with simpler SQL statements, avoiding JOINs and subselects between active and draft persistence whenever this introduces a performance gain.
- [cds.java@2.4.0] Events for reading of active instances and draft instances of draft-enabled entities can now be handled in distinct event handlers. This enables redirection of all events on active instances to a different datasource, for example a remote S/4 system. The property `cds.drafts.persistence` should be set to `split` in that case to ensure JOINs and subselects are avoided in all SAP Fiori UI queries.
- [cds.java@2.4.0] Queries to remote OData services now support tuple comparisons and tuple IN predicates.
- [cds.java@2.4.0] EDMX metadata loaded from JAR resources is now localized lazily upon request, if unlocalized EDMX resources are generated by `cds build`. This avoids caching different translations of the same EDMX in memory.
- [cds.java@2.4.0] Introduced a `EdmxV4Provider` interface, allowing custom code to overwrite how EDMX metadata is loaded.
- [cds.java@2.4.0] Introduced a new generic interface `CdsProvider`, implemented by all specific provider interfaces, for example `UserInfoProvider`.
- [cds.java@2.4.0] The `generate` goal of the `cds-maven-plugin` now generate typed `CqnService` interfaces based on the CDS model definitions. These typed interfaces contain explicit methods for all actions and functions the service defines.
- [cds.java@2.4.0] CqnServices registered during startup are automatically proxied with a typed interface, if available.
- [cds.java@2.4.0] The goal `install-node` of the `cds-maven-plugin` supports re-tries, if the download of the Node.js distribution fails.
- [cds.java@2.4.0] The goal `install-node` of the `cds-maven-plugin` supports installing Node.js on the architecture `aarch64`.
- [cds.java@2.4.0] A new property `cds.csdk-version` can be set in `pom.xml` for the `cds-maven-plugin`. If this property is set `@sap/cds-dk` is referenced using `npx --package` in the `cds` goal. This avoids installing npm modules into the project.
- [cds.java@2.4.0] The `watch` goal of the `cds-maven-plugin` now includes a new `testRun` property, which helps to configure the specific goal for starting the application in the `spring-boot-maven-plugin`.
- [cds.java@2.4.0] The goal `add` of the `cds-maven-plugin` supports adding PostgreSQL and Liquibase support to a CAP Java project.
- [cds.java@2.4.0] Pagination is now handled when retrieving subscribed tenants from Subscription Manager Service (SMS).
- [cds.java@2.4.0] The new method `systemUserProvider()` of `RequestContextRunner` allows to easily execute code as a system user on behalf of the provider tenant.
- [cds.java@2.4.0] The new method `systemUser()` of `RequestContextRunner` allows to easily execute code as a system user on behalf of the current tenant.
- [cds.java@2.4.0] The new method `systemUser(tenantId)` of `RequestContextRunner` allows to easily execute code as a system user on behalf of a specific tenant.
- [cds.java@2.4.0] CSV file loader now supports files with headers and content quoted with double quotes.
- [cds.java@2.4.0] Setting the new property `cds.sql.hana.optimizationMode` to `hex` generates SQL specific for the SAP HANA HEX engine.
- [cds4j@2.4.0] Default values for to-one managed associations to entities with one key element
- [cds4j@2.4.0] CqnAnalyzer: support in predicates, which compare list-values
- [cds4j@2.4.0] Generate SQL specific for SAP HANA HEX engine using configuration `cds.sql.hana.compatibilityMode: "hex"` or statement hint `"hdb.USE_HEX_PLAN"`
- [cds4j@2.4.0] Typed entity refs via `CQL.entity(type)`
- [cds4j@2.4.0] Resolved segments of analyzed refs now provide the element
- [cds@7.4.0] Any service is outboxable via `srv = cds.outboxed(srv)`
- [cds@7.4.0] Draft: support `HasActiveEntity eq false` by read
- [cds@7.4.0] Check if OData function/action params exist for complex types
- [cds@7.4.0] Remote services: destination option `jwt` set to `null` instructs that an incoming request's JWT shall not be passed to SAP Cloud SDK, e.g., when it shall use a fresh client credentials flow tokenExample:json

```
"requires": {
  "API_BUSINESS_PARTNER": {
    [...]
    "destinationOptions": {
      "jwt": null
    }
  }
}
```

- [cds@7.4.0] Alpha feature flag `cds.env.fiori.wrap_multiple_errors` to toggle the following behaviour for OData errors meant to be consumed by SAP Fiori Elements: In cases where multiple errors occur and the flag is set to `false`, the first error is presented as the top-level error (replacing the generic "multiple errors" wrapper). The default value is `true`, but `false` will become the default value in cds^8.
- [cds@7.4.0] On CF, the default keep alive timeout of the server is set to 91s (to exceed the 90s of CF's gorouter)
- [cds@7.4.0] `cds deploy` now auto-fills the `ID_texts` field (which get created for entities marked with `@fiori.draft.enabled`) in csv and json data files with a stable UUID. This way, it does not need to be manually added to data files. Also, as the value is stable (a hash of the semantic key fields `ID` and `locale`), it works with `UPSERT` statements.
- [cds-mtxs@1.13.1] `DEBUG=mtx` will now log all outgoing requests to Service Manager.
- [cds-mtxs@1.13.1] For `multitenancy.jobs.clusterSize > 1` the Service Manager request will throw an error for a corrupt tenant without credentials.
- [cds-mtxs@1.13.0] `GET /-/cds/saas-provisioning/tenant` now also returns `createdAt` and `modifiedAt` fields.
- [ux-cds-odata-language-server-extension@1.11.5] Enhanced code completion and validation to support annotating inline composition

### Changed ​

- [cds-dk@7.4.1] `cds push` uses the synchronous server API by default again due to stability problems. Use `--async` for the asynchronous call.
- [cds-dk@7.4.1] `cds add enterprise-messaging` will now correctly replace all `_` by `-`.
- [cds-dk@7.4.0] `cds build` plugins can now require their APIs directly from `@sap/cds` (instead of `@sap/cds-dk`).
- [cds-dk@7.4.0] `cds init` uses latest Maven Java archetype version 2.4.0 for creating Java projects.
- [vscode-cds@7.4.0] Formatting Projections now similar to that of views
- Markdown formatting inside doc comments is now done with `marked` parser AST instead of `remark`. Previously, this was enabled by default but due to slightly different formatting this feature is disabled by default, now. Thus, already formatted markdown won't be changed and thus won't lead to file changes when used in CI/CD via `format-cds` command. Enable it via format setting `formatDocComments`.

- [vscode-cds@7.4.0] Simplified trace configuration - just use `cds.trace.level`
- [cds-compiler@4.4.0] CDL parser: improve error recovery inside structured annotation values
- [cds-compiler@4.4.0] Update OData vocabularies: 'Aggregation', 'Common', 'Core', 'Hierarchy', 'ODM', 'UI'.
- [cds.java@2.4.0] The `cds-maven-plugin` installs Node.js 18 by default.
- [cds.java@2.4.0] The archetype now supports creating projects for Java 21 and no longer for Java 20.
- [cds4j@2.4.0] To-many expand SQL: only add hidden @-prefixed key elements if not already selected
- [cds4j@2.3.1] Reduce statement-level collating on SAP HANA to order relations on String elements in where/having of Select statements
- [cds4j@2.3.1] Don't use `COLLATE` in orderBy clause of SAP HANA queries with statement-level collating or if type propagation yields a non-string type
- [cds4j@2.3.1] Don't use statement-wide collating in update and delete statements
- [cds4j@1.38.8] SAP HANA: Don't use statement-wide collating in update and delete statements
- [cds4j@1.38.8] SAP HANA: Reduce statement-wide collating to order relations on String elements in where/having
- [cds4j@1.38.8] SAP HANA: Don't use COLLATE in queries using statement-level collating
- [cds@7.4.0] Default outbox configuration (overridable via `cds.env.requires.outbox = { ... }`): `kind` changed to `persistent-outbox` (was `in-memory-outbox`)
- `parallel` changed to `true` (i.e., messages are not emitted in sequence)

- [cds@7.4.0] Internal class `OutboxService` is deprecated and will be removed
- [cds-mtx@2.6.6] Upgraded `@sap/instance-manager` to version 4.
- [cds-mtxs@1.13.1] For non-extensibility projects, a shared deployment folder is used across tenants for resource extraction. For `n` simultaneous tenant upgrades, this decreases the number of extracted files `n`-fold.
- [cds-mtxs@1.13.0] The internal job runner now has an in-memory queuing mechanism. For non-scaled sidecar instances, this avoids tasks for the same tenant from being run at the same time.

### Fixed ​

- [cds-dk@7.4.1] `semver` is bumped to version `^7` to mitigate CVE-2022-25883
- [cds-dk@7.4.0] `cds deploy --to hana --dry` now prints out the SAP HANA SQL files which will be deployed if `--dry` is not specified.
- [cds-dk@7.4.0] `cds build` no longer fails if multiple service protocols are configured in object notation.
- [cds-dk@7.4.0] `cds build` now uses configured compiler options when building Node.js projects.
- [cds-dk@7.4.0] `cds pull` when amending package.json applies the original indentation
- [cds-dk@7.4.0] `cds watch --profile hybrid` no longer produces a value `hybrid,hybrid` for `process.env.CDS_ENV`
- [cds-dk@7.4.0] `cds.schema` now loads lazily.
- [cds-dk@7.4.0] `cds init` does not print `cd` hint if creating a project in current folder.
- [vscode-cds@7.4.0] Formatting Padding of quoted identifiers
- Treat only /** (no additional asterisks) as start of doc comments

- [vscode-cds@7.4.0] Syntax highlighting of comments within braced select item lists
- [vscode-cds@7.4.0] Update of diagnostic messages could have got lost
- [cds-compiler@4.4.4] to.hdi.migration: Changes in only `doc`-comments should not result in a drop-create of the primary key.
- [cds-compiler@4.4.2] for.odata: Fix crash when using a projection with associations as action parameter type.
- [cds-compiler@4.4.2] to.edm(x): `Edm.AnyPropertyPath` is hard to `Edm.PropertyPath`. As there is no dynamic path evaluation, `Edm.NavigationPropertyPath` must be enforced via `$edmJson`. `Edm.AnyPropertyPath` has been used in `@Aggregation.ApplySupported.GroupableProperties` for the first time after vocabulary update with 4.4.0.
- [cds-compiler@4.4.0] parser: `/**/` was incorrectly parsed as an unterminated doc-comment, leading to parse errors.
- Doc-comments consisting only of `*` were not correctly parsed.

- [cds-compiler@4.4.0] compiler: do not propagate `default`s in a CSN of flavor `xtended`/`gensrc`.
- [cds-compiler@4.4.0] to.hana: Fix various bugs in association to join translation. Support `$self` references in filter expressions.
- [cds-compiler@4.4.0] to.edm(x): Omit `EntitySet` attribute on `Edm.FunctionImport` and `Edm.ActionImport` that return a singleton.
- [cds-compiler@4.4.0] to.sql|hdi.migration: Improve handling of primary key changes - detect them and render corresponding drop-create.
- [cds.java@2.4.0] Fixed a bug, causing applications without `spring-boot-starter-web` dependencies to fail during startup.
- [cds.java@2.4.0] Fixed a bug, causing a hard to understand error message, when custom handlers don't implement `/$count` queries correctly.
- [cds.java@2.4.0] Fixed a bug, causing statements with incorrect comparisons when using OData singletons.
- [cds.java@2.4.0] Fixed a bug, causing `@cds.collate: false` to be ignored on draft-enabled entities.
- [cds.java@2.4.0] Fixed a bug, causing selection of too many elements in remote OData V2 and V4 queries.
- [cds.java@2.4.0] Fixed a bug, causing the annotation-based audit log handling, not to send a data modification event if a personal data attribute was deleted.
- [cds.java@2.4.0] Fixed a bug in the `add` goal of the `cds-maven-plugin`, causing an incomplete MTX setup for local testing.
- [cds.java@2.4.0] Fixed a bug in the `resolve` goal of the `cds-maven-plugin`, causing CDS reuse dependencies in the same reactor build to be omitted.
- [cds.java@2.4.0] Fixed a bug in goal `generate` of the `cds-maven-plugin`, causing the POJO generation to fail in Eclipse and other IDEs.
- [cds.java@2.4.0] Fixed a bug, causing HTTP requests to be rejected with status code 401 when technical user JWT tokens issued by IAS were used.
- [cds.java@2.3.1] Fixed a bug, causing audit log messages not being written on behalf of the named user when the persistent outbox is used.
- [cds4j@2.4.1] Fix exception on queries using elements of undefined type in `order by` or in ordering relations in filters
- [cds4j@2.4.1] Fix to-many expand for queries using where exists subqueries with paths
- [cds4j@2.4.1] Fixed a code generation issue, if there is no CDS model available and typed service interface should be generated
- [cds4j@2.4.1] Consider `cds.sql.hana.ignoreLocale: true` in `ORDER BY` for SAP HANA
- [cds4j@2.4.1] Fixed a code generation issue, if an action or function is renamed with `@cds.java.name`.
- [cds4j@2.4.1] Fix HEX hint for queries using search
- [cds4j@2.4.0] Fixed a bug, causing memory leak when the methods of the accessor interfaces that return a list were called
- [cds4j@2.4.0] Values of virtual elements are no longer removed from the payload of the `Insert`, `Update` and `Upsert` statements and are available in the `Result` of these statements
- [cds4j@1.38.8] SAP HANA: Render COLLATE in order by only if type propagation yields STRING
- [cds@7.4.2] Typing for `DELETE.from(.drafts)`
- [cds@7.4.2] UUID keys must not be generated for associations
- [cds@7.4.1] Add dynamic properties to result when experimental feature `cds.env.features.okra_skip_query_options` is active
- [cds@7.4.1] Allow negative integers in new parser
- [cds@7.4.1] Allow deletion of instances outside the draft tree
- [cds@7.4.1] Tenant lookup in OData metadata requests
- [cds@7.4.1] `cds.parse.csv` and `cds deploy` correctly parse CSV files with Windows file endings (CRLF) and quoted values
- [cds@7.4.1] Typescript Typings
- [cds@7.4.0] `req.subject` in lean-draft handlers
- [cds@7.4.0] `cds.odata.batch_limit` wasn't taken into account
- [cds@7.4.0] Enterprise-Messaging: Only set tenant information for multitenant apps
- [cds@7.4.0] Enterprise-Messaging: Race condition in `subscribe` event
- [cds@7.4.0] Draft: delete of active entity is forbidden, if draft exist
- [cds@7.4.0] Draft: sorting of draft entities in `list status: all`
- [cds@7.4.0] Draft: invalid delete draft request now rejects with error
- [cds@7.4.0] Draft: Enhance Draft Edit functionality with exclusive record lock
- [cds@7.4.0] Typings for `req.reject/error/info/warn`
- [cds@7.4.0] Deep delete with mixins on new db layer did not work
- [cds@7.4.0] Special strings like `'$now'`, `'$user'` and `'$uuid'` expanded automatically
- [cds@7.4.0] Only services that are served via OData are precompiled during startup
- [cds@7.4.0] Response status of not existing mocks returned 200 instead of 404
- [cds@7.4.0] Calculation of @Capabilities in case of complex $apply
- [cds@7.4.0] `test.data.reset()` did not delete drafts
- [cds@7.4.0] `resolveView` considers `list` for renamed columns
- [cds@7.4.0] `cds.schema` now loads lazily
- [cds@7.4.0] `odata_new_parser`: `$expand=` no longer throws an error with and is simply ignored
- [cds@7.4.0] `odata_new_parser`: Empty custom query params like `Foo?bar` are ignored
- [cds@7.4.0] `odata_new_parser`: generated wrong CQN for queries like `$filter=false or ref eq 5`

### Removed ​

- [cds-dk@7.4.0] `cds repl` no longer loads `cds.plugins` on startup to keep `cds` lazy.
- [vscode-cds@7.4.0] Workspace validation modes `OpenEditorsAndDirectSources` and `OpenEditorsDirectSourcesAndDirectDependencies` are no longer supported. In real-world models they led to high CPU usage and slow responsiveness. Any of these user setting values are now treated as `ActiveEditorOnly` if supported by IDE, else `OpenEditorsOnly`.

## October 2023 ​

### Added ​

- [cds-dk@7.3.1] `cds build` supports the option `contentLocalizedEdmx` to enable/disable the generation of localized edmx files for Java apps - default is `true`.
- [cds-dk@7.3.1] `cds repl` now loads `cds.plugins` on startup.
- [cds-dk@7.3.1] `cds add enterprise-messaging-shared` also supports Kyma deployment.
- [cds-dk@7.3.1] `cds add notifications` adds configurations for notifications plugin.
- [cds-dk@7.3.0] `cds push` now uses the asynchronous server API by default. Use `--sync` for the synchronous one.
- [cds-dk@7.3.0] `cds activate` and `cds push` now support the `-2` shortcut for the `--to` option.
- [cds-dk@7.3.0] Improved error logging for failed HTTP requests.
- [cds-dk@7.3.0] `cds build` support for custom build plugins.
- [cds-dk@7.3.0] `cds compile` support for custom compile plugins.
- [cds-dk@7.3.0] `cds build` creates non-localized edmx files for the nodejs apps. Translations will be applied at runtime.
- [cds-dk@7.3.0] `cds.schema.overlay4` gets the cds default schema plus overlays from cds-dk.
- [cds-dk@7.3.0] `cds build` creates non-localized edmx files for the java apps. Translations will be applied at runtime.
- [cds-dk@7.3.0] `cds import` now introduces new option `--config` to add custom configuration data in the package.json.
- [cds-dk@7.3.0] `cds add helm` now adds `html5-apps-repo-runtime` binding for `approuter` if `html5-repo` is present.
- [cds-dk@7.3.0] (BETA) `cds add postgres` adds configuration for PostgreSQL. This requires `@cap-js/postgres` 1.3.0.
- [eslint-plugin-cds@2.6.4] New `auth-restrict-grant-service` rule that validates events on restricted services.
- [vscode-cds@7.3.0] support for `cdsc.moduleLookupDirectories`
- [vscode-cds@7.3.0] Support for merged cds schemas returned by `cds-dk`
- [cds.java@2.3.0] Feature `cds-feature-identity` is now supporting pure XSUAA-based scenarios. A service binding to IAS is not mandatory anymore. With this change, it is feature compatible with `cds-feature-xsuaa` which eventually will be removed in a future release.
- [cds.java@2.3.0] `UserInfo.isInternalUser()` is now supported in case of IAS-based authentication.
- [cds.java@2.3.0] The archetype now generates projects with encoding UTF-8 configured for the Java compile plugin.
- [cds.java@2.3.0] Service Bindings from `default-env.json` are now provided through a plugin in the Service Binding Library and are therefore visible to other libraries, for example Cloud SDK.
- [cds.java@2.3.0] Cloud SDK's new `ServiceBindingDestinationLoader` API is now used to create destinations from service bindings.
- [cds.java@2.3.0] PostgreSQL SSL connections are now properly configured to validate the SSL certificate and hostname.
- [cds.java@2.3.0] CAP Java is now tested with SapMachine 21 and no longer with SapMachine 20.
- [cds.java@2.3.0] Out of the box integration with Subscription Manager Service (SMS) to offer IAS tenant lifecycle.
- [cds.java@2.3.0] The goal `add` of the `cds-maven-plugin` merges changes into existing profiles in application.yaml instead of replacing them.
- [cds4j@2.3.0] Allow to control collating on SAP HANA per statement via hint "collating.hana"
- [cds4j@2.3.0] Config option `cds.sql.collate: "localized-strings"`
- [cds4j@2.3.0] Annotation `@cds.collate` to disable/enable collation for specific elements
- [cds4j@2.3.0] Support tuples in CDS QL `IN` clauses
- [cds4j@2.3.0] Annotation `@cds.java.expand: {using: 'load-single'}` to expand by parent keys with individual selects
- [cds4j@2.3.0] Support Runtime Views annotated with `@cds.persistence.skip`
- [cds@7.3.0] `cds.localized` now caches i18n bundles per locale and per model to speed up repeated usages of the same bundle at runtime, for example, in repeated calls to `cds.compile.for.edmx()`.
- [cds@7.3.0] Based on `cds.localized` with cached bundles, a new operation `cds.localized.lookup(i18n_key, locale)` is provided.
- [cds@7.3.0] If env variable `CDS_TEST_ENV_CHECK` is set, `cds.test.in()` detects if `cds.env` was loaded before from a different folder.
- [cds@7.3.0] `cds.test.log()` allows to capture and analyze any console log output. `cds.test.verbose()` is now deprecated.
- [cds@7.3.0] Typings for `cds.tx`
- [cds@7.3.0] Add method `cds.schema.default4(schemaId)` to retrieve json schema based on its id
- [cds@7.3.0] Support for pseudo role `internal-user` with authentication kind `ias`
- [cds@7.3.0] CSV files with multiline values, i.e. line breaks, are now supported with `cds deploy`
- [cap-js/graphql@0.8.0] [beta] Translate CDS error messages and include additional error properties in `GraphQLError` `extensions`. Only specific allowed properties are exposed when running in production.
- [cap-js/graphql@0.8.0] [beta] Option `errorFormatter` that can be pointed to a function that overwrites the default logic of how CDS errors are formatted before they are added to the GraphQL error response. Please note that this may overwrite sanitization logic that is otherwise applied to error messages in production.
- [cap-js/graphql@0.8.0] [beta] Logging of errors that occur during query and mutation execution
- [cap-js/audit-logging@0.4.0] Support for Premium plan of SAP Audit Log Service
- [cap-js/audit-logging@0.4.0] Support for XSUAA credential type `x509`
- [cap-js/audit-logging@0.4.0] Support for generic outbox
- [cap-js/postgres@1.3.0] `cds build` is now natively supported in `@cap-js/postgres`. Thus, a `cds build` will automatically generate deployment artifacts for Postgres-enabled projects.
- [cds-mtxs@1.12.0] Beta: Setting `cds.requires.multitenancy.humanReadableInstanceName = true` will create human-readable tenant IDs for instances created via Service Manager, instead of hashed strings. This is incompatible with existing tenants using hashed instance names.
- [cds-mtxs@1.12.0] Extensions of internal entities / services starting with `cds.xt.` are no longer allowed.
- [cds-mtxs@1.12.0] If no extensions exist, `ModelProviderService.getEdmx()` now uses edmx files prebuilt by `cds build`.
- [cds-mtxs@1.12.0] `ModelProviderService.getEdmx()` with empty `locale` parameter returns non-translated edmx.
- [cds-mtxs@1.12.0] `ModelProviderService.getI18n()` returns the translated texts for a given `locale` and `tenant`.
- [cds-mtxs@1.12.0] Migrated extension projects can now be downloaded using `cds extend  --download-migrated-projects`.

### Changed ​

- [cds-dk@7.3.1] `cds watch --livereload` now reload the client w/o a server restart, so that for e.g. an `.html` file, a reload event is sent, but the server is not restarted. Previously, the two events were coupled.
- [cds-dk@7.3.1] `cds build` now provides a programmatic plugin API instead of the former configuration based one.
- [cds-dk@7.3.0] `cds login` now eagerly detects expired token and asks for a new passcode if applicable
- [cds-dk@7.3.0] `cds login` now presents the passcode URL as early as possible
- [cds-dk@7.3.0] `cds env` now requires `@sap/cds` >= 7.3 to resolve configuration contributed by cds plugins
- [cds-dk@7.3.0] `cds add connectivity` does not add `connectivity: true` to your `package.json` any more.
- [cds-dk@7.3.0] `cds watch` now ignores more files/folders: `app/(webapp|dist|target)`, `app/*/(webapp|dist|target)`, `tsconfig.json`, `*.tsbuildinfo`
- [cds-dk@7.3.0] `cds build` now uses `compile.to.hdbtable` if no migration tables exist.
- [cds-dk@7.3.0] Refactoring `cds build plugin` API
- [vscode-cds@7.3.0] formatting of action and function parameters according to existing newlines
- [vscode-cds@7.3.0] Minimum VS Code version is now 1.80.0. Note: This is likely the last version that supports NodeJS 16
- [cds.java@2.3.0] `4.24.0` is the new minimum required Cloud SDK version.
- [cds.java@2.3.0] For event brokers that don't provide an explicit unique message ID the ID is now determined from the cloudevents `ID` property, if available. Message IDs are no longer generated when receiving an event without any ID.
- [cds.java@2.3.0] Active instances of draft-enabled entities are now locked for deletion, if a locked draft exists, that is owned by a different user. The user owning the draft can always delete the active instance and with that also delete the corresponding draft.
- [cds.java@2.3.0] `TenantProviderService.readProviderTenant()` now uses `app_tid` field if present instead of `zone_uuid` field in case of IAS service bindings.
- [cds4j@2.3.0] HANA: Use `COLLATE` in `ORDER BY` clause
- [cds4j@2.3.0] Expand by `parent-keys` is executed as a bulk operation
- [cds4j@2.3.0] Reduce memory allocation of proxies for accessor interfaces
- [cds4j@2.3.0] Simplify `IS` and `IS NULL` if neither operand is nullable
- [cds4j@1.38.7] HANA: Don't enforce statement-level collating on Conjunction, Disjunction and Negation
- [cds@7.3.0] If omitted in the accept header, `ExponentialDecimals` no longer gets defaulted (to `true`), which violated the OData 4.0 specification. This change can temporarily be overridden via `cds.env.odata.defaultExponentialDecimals = 'true/false'`.
- [cds@7.3.0] Make type signature of `extend.with` more general
- [cds@7.3.0] `cds.test.data.autoReset()` is deprecated in favor of explicit `cds.test.data.reset()` call, like `beforeEach (test.data.reset)`.
- [cds@7.3.0] `cds.utils.uuid()` now uses `randomUUID` function of node `crypto` module instead of `uuid` package
- [cds@7.3.0] `@Capabilities` restrictions defined on entity level are also applied if navigating to the entity. Restrictions defined directly on the navigation now override restrictions defined on the target entity.
- [cap-js/graphql@0.8.0] Bump required `@sap/cds` version to `>=7.3`
- [cap-js/graphql@0.8.0] Bump required `graphql-http` version to `^1.18.0`
- [cap-js/audit-logging@0.4.0] Always use outbox (as configured in project)
- [cap-js/db-service@1.3.0] `INSERT.into(...).rows/values()` is not allowed anymore without specifying `.columns(...)`. #209
- [cap-js/db-service@1.3.0] Deep deletion uses correlated subqueries instead of materializing the to be deleted object before. #212
- [cap-js/sqlite@1.3.1] Updated minimum required version of `@cap-js/db-service`.
- [cds-mtxs@1.12.0] The allowlist for HDI deployment parameters (`HDI_DEPLOY_OPTIONS`) is removed. Any option can now be used.
- [cds-mtxs@1.12.0] `PUT /-/cds/saas-provisioning/tenant` now also allows non-UUID strings for `subscribedSubaccountId`.

### Fixed ​

- [cds-dk@7.3.1] `cds` commands will now respect the `NO_COLOR` environment variable.
- [cds-dk@7.3.1] `cds init` no longer adds comments to file `.vscode/launch.json`
- [cds-dk@7.3.1] `cds bind` prints correct command line recommendation to start spring-boot application
- [cds-dk@7.3.1] `cds compile` to `openapi` now generates correct query options with `$` prefix.
- [cds-dk@7.3.1] `cds build` no longer causes `duplicate assignment` compilation errors in some specific feature toggle scenarios.
- [cds-dk@7.3.1] `cds watch` now loads missing service bindings when called from a directory other than cwd.
- [cds-dk@7.3.1] Multitenant `cds` commands now have any trailing slashes removed from app URLs, fixing certain request failures.
- [cds-dk@7.3.1] Multitenant `cds` commands now handle request errors more robustly.
- [cds-dk@7.3.1] `cds build` no longer fails for cds services supporting multiple protocols.
- [cds-dk@7.3.0] `cds login` now prints shorter errors. (Set `DEBUG=req` in env to see all details again.)
- [cds-dk@7.3.0] Fixed issue when creating a CAP project in SAP Business Application Studio's template wizard.
- [cds-dk@7.3.0] `cds import` now handles name collision within a Schema for OData V4 EDMX.
- [cds-dk@7.3.0] `cds build` for mtx extension projects no longer creates CSN containing unresolved model associations.
- [cds-dk@7.3.0] `cds build` no longer creates new migration versions by mistake after schema evolution changes have been manually resolved.
- [cds-dk@7.3.0] `cds add approuter` creates the `xs-app.json` in the `app` folder again, instead of in `app/router`.
- [cds-dk@7.3.0] `cds watch` no longer restarts itself in an endless loop (happened in some Typescript scenarios on Windows)
- [eslint-plugin-cds@2.6.4] In no-join-on-draft, do not run check if there is no valid query.
- [eslint-plugin-cds@2.6.4] In auth-valid-restrict-where, do not consider when missing expression references.
- [vscode-cds@7.3.0] highlighting of identifiers, annotations, actions, functions, comments, and more
- [vscode-cds@7.3.0] highlighting of queries in entity definitions
- [vscode-cds@7.3.0] highlighting of keywords and literals in `type` statements
- [vscode-cds@7.3.0] formatting of escaped names and `order by` clauses
- [cds-compiler@4.3.2] compiler: Fix auto-exposure of composition target entities inside anonymous composition target aspects.
- [cds-compiler@4.3.2] to.hana: Fix a bug in association to join translation, expect ON condition operand to be a function without arguments.
- [cds.java@2.3.0] Fixed a bug in `UserInfo.isSystemUser()` in case of IAS-based authentication.
- [cds.java@2.3.0] Fixed a bug, causing OData V4 PATCH requests setting to-one navigation properties to `null` to not have any effect.
- [cds.java@2.3.0] Fixed a bug, causing incorrect key predicates in OData V4 when executing additional `Select` statements for `$select` or `$expand` on action or function results.
- [cds.java@2.3.0] Fixed a bug, causing OData V4 requests to return wrong values when calling `$value` on entity attributes of type `Edm.LargeBinary` without `@Core.MediaType` annotation.
- [cds.java@2.3.0] Fixed a bug, causing missing subscribed tenants when retrieving tenants from SaaS registry, due to missing pagination handling.
- [cds.java@2.3.0] Fixed a bug, causing generated `schema-*.sql` files to not be git-ignored in generated projects.
- [cds.java@2.3.0] Fixed a bug in the `resolve` goal, that caused the execution to fail, if non JAR dependencies were present in the project.
- [cds.java@2.3.0] Fixed a bug, causing exceptions when using the `cds` actuator endpoint with user-provided services bound to the application.
- [cds.java@2.3.0] Fixed a bug, causing Select statements with search predicates with conjunctions to generate invalid remote OData queries.
- [cds.java@1.34.7] Fixed a bug, causing OData V4 requests to return wrong values when calling `$value` on entity attributes of type `Edm.LargeBinary` without `@Core.MediaType` annotation.
- [cds.java@1.34.7] Fixed a bug, causing missing subscribed tenants when retrieving tenants from SaaS registry, due to missing pagination handling.
- [cds4j@2.3.0] Fixed a bug causing compilation error after generating Java consumption interfaces, for associations annotated with `@cds.java.name`
- [cds4j@1.38.7] HANA: SQL syntax error with `COLLATE` in `ORDER BY` function
- [cds@7.3.1] `cds-ts` no longer fails if configured with an ESM loader. It tries loading files w/ `import()` in this case.
- [cds@7.3.1] `cds deploy` for draft enabled entities
- [cds@7.3.0] Draft: activate managed fields were miscalculated in some cases
- [cds@7.3.0] Error with `exists` predicate in `@restrict.where` when calling compositions
- [cds@7.3.0] `IsActiveEntity` in error target for lean draft
- [cds@7.3.0] Remote Service: OData v2 compliant representation of Edm.Decimal, Edm.Double, and Edm.Int64 in URL
- [cds@7.3.0] In draft activate managed fields were calculated wrongly in some cases
- [cds@7.3.0] On draft save, missing entries in `req.headers`
- [cap-js/graphql@0.8.0] Malformed responses for convoluted queries in which parts of results are supposed to be returned multiple times, caused by formatting results in-place
- [cap-js/audit-logging@0.4.0] Avoid dangling `SELECT`s to resolve data subject IDs, which resulted in "Transaction already closed" errors
- [cap-js/audit-logging@0.3.2] If the request has no tenant (e.g., Unauthorized), the audit log shall be sent to the provider account
- [cap-js/db-service@1.3.2] preserve $count for result of SELECT queries
- [cap-js/db-service@1.3.1] Error message for search with multiple arguments.
- [cap-js/db-service@1.3.0] Various fixes for calculated elements on read. #220 #223 #233
- [cap-js/db-service@1.3.0] Don't release to pool connections twice. #243
- [cap-js/db-service@1.3.0] Syntax error in `matchesPattern` function. #237
- [cap-js/db-service@1.3.0] SELECTs with more than 50 columns does not return `null` values. #238 #261
- [cap-js/postgres@1.3.1] `cds build`-relevant files are now correctly packaged into the release. #266
- [cap-js/sqlite@1.3.0] `CURRENT_TIMESTAMP` in view definition preserves the timezone. #254
- [cds-mtxs@1.12.1] More stable upgrade with extensibility enabled.
- [cds-mtxs@1.12.1] Downloaded migrated extension projects now contain correct base model references.
- [cds-mtxs@1.12.0] Synchronous call of `PUT /-/cds/saas-provisioning/tenant` now returns correct `content-type`: `text/plain`.
- [cds-mtxs@1.12.0] Update of extensions with different tags that depend on each other does no longer result in a compilation error.
- [cds-mtxs@1.12.0] Extensions containing new entities with associations to base entities do no longer cause a compilation error.
- [cds-mtxs@1.12.0] For SAP HANA deployment, no recompilation is done any more for applications not using extensibility.
- [odata-v2-adapter@1.11.8] Automatically activate plugin, if mentioned explicitly in `cds.plugins`
- [odata-v2-adapter@1.11.8] Move custom server section in README under advanced section, as plugin is the preferred way to bootstrap adapter

## September 2023 ​

### Added ​

- [cds-dk@7.2.0] `cds add h2` adds H2 configuration for Java projects.
- [cds-dk@7.2.0] `cds add sqlite` now has full support for Java projects.
- [cds-dk@7.2.0] `cds gen` creates models or data using a descriptive prompt Beta
- [cds-dk@7.2.0] `cds bind` auto detects 'ias-auth' service bindings
- [cds-dk@7.2.0] `cds compile` to `openapi` now introduces new option `--odata-version` to add the OData version functionality to generate the OpenAPI document.
- [cds-dk@7.2.0] `cds add` comes with more templates/facets in the wizard of SAP Business Application Studio: App Router, XSUAA, Kibana logging, enterprise messaging, multitenancy, helm charts, and extended sample files.
- [vscode-cds@7.2.0] CAP with Typescript Beta: add setting to customize type generation command
- [cds-compiler@4.3.0] compiler: it is possible to publish associations with filters in views. Managed associations become unmanaged ones. For example:cds

```
entity Proj as projection on Base {
  assoc[id = 1],
};
```
- [cds.java@2.2.0] Added a new goal `resolve` to the `cds-maven-plugin` which extracts CDS reuse models from JARs to `target/cds/`. The goal is configured in newly generated projects by default and is also run when running `mvn cds:build`.
- [cds.java@2.2.0] `cds-starter-cloudfoundry` now bundles all dependencies required for IAS-based authentication, in particular `cds-feature-identity` and Spring security.
- [cds4j@1.38.6] Allow to control collating on HANA per statement via hint "collating.hana"
- [cds4j@1.38.6] Config option `cds.sql.collate: "localized-strings"`
- [cds4j@1.38.6] Annotation `@cds.collate` to disable/enable collation for specific elements
- [cds@7.2.0] Typescript definition for:[cds@7.2.0] The `cds.exit()` method.
- [cds@7.2.0] The `label` option parameter in the `cds.log()` API. For example: `cds.log('log message', { label: 'adapter' }`.
- [cds@7.2.0] A variant of the `roles` property of the `cds.User` class.

- [cds@7.2.0] `@restrict` annotations can now prevent the creation of drafts (see documentation)
- [cds@7.2.0] JSON Schema validation for `cds.requires.multitenancy.jobs` settings.
- [cds@7.2.0] Managed associations to-one with exactly one foreign key can now have a default value.
- [cds@7.2.0] Experimental feature flag `cds.env.features.okra_skip_query_options`. This feature allows you to bypass the parsing of query options by the legacy OData V4 Server (Okra). Please note that this feature can only be utilized in conjunction with the new OData parser, which is activated by setting the feature flag `cds.env.features.odata_new_parser = true`.
- [cds@7.2.0] Support for `@requires: 'any'` to make service public, i.e., no authenticated user is required
- [cds-mtx@2.6.5] Container creation now adds parameters needed for SAP HANA encryption
- [cap-js/audit-logging@0.2.0] Export class `AuditLogService` for extending in custom implementations as follows:js

```
const { AuditLogService } = require('@cap-js/audit-logging')
class MyAuditLogService extends AuditLogService {
  async init() {
    [...]
    // call AuditLogService's init
    await super.init()
  }
}
module.exports = MyAuditLogService
```
- [cap-js/db-service@1.2.0] support for calculated elements on read. #113 #123
- [cap-js/db-service@1.2.0] support for managed associations with default values. #193
- [cap-js/db-service@1.2.0] introduced new operator `==` which translates to `IS NOT DISTINCT FROM`. #164
- [cap-js/postgres@1.2.0] Reduced the usage of `is not distinct [not] from`. #157
- [cds-mtxs@1.11.0] `/-/cds/extensibility/push` now also accepts the `prefer: respond-async` header for asynchronous requests.
- [cds-mtxs@1.11.0] `/-/cds/model-provider/getCsn` uses an LRU cache for base model CSNs, limited to 5 entries by default. This cache size can be configured using `cds.requires['cds.xt.ModelProviderService'].cacheSize`.
- [cds-mtxs@1.11.0] The `treat_unmodified_as_modified` parameter is now allowed for HDI deployments.
- [odata-v2-adapter@1.11.7] Set CDS OData V2 protocol

### Changed ​

- [cds-dk@7.2.0] `cds add approuter` creates the `xs-app.json` in a dedicated `app/router` folder, instead of in `app`.
- [cds-dk@7.2.0] `cds add multitenancy` now sets up the `cds-feature-mt` dependency in your `pom.xml` for Java projects.
- [cds-dk@7.2.0] `cds watch` ignores all frontend resources in `app/**/webapp/**`. Previously, only `app/**/(*.js|ts)` was ignored.
- [vscode-cds@7.2.0] New data structures and caching to improve performance of where-used requests (e.g. Find References) and code completion
- [vscode-cds@7.2.0] Elements of `mixin`s now use `SymbolKind.Field` (was: Operator) in Outline
- [cds-compiler@4.3.0] Update OData vocabularies: 'Aggregation', 'Capabilities', 'Common', 'PDF', 'PersonalData', 'UI'.
- [cds.java@2.2.0] Removed support for the annotations `@AuditLog.Operation.Read`, `@AuditLog.Operation.Insert`, `@AuditLog.Operation.Update` and `@AuditLog.Operation.Delete`. By default, all operations are logged into auditlog.
- [cds4j@2.2.1] optimized FK filter using `in` for to-many expands in queries using top/skip
- [cds4j@2.2.0] Improved data access performance via getters of generated `CdsData` accessor interfaces
- [cds4j@2.2.0] Optimized queries with to-many expands returning an empty result
- [cds4j@2.2.0] SQLite: Add `COLLATE NOCASE` to columns of String elements only
- [cds4j@1.38.6] HANA: Use `COLLATE` in `ORDER BY` clause
- [cds@7.2.0] The built-in `java` profile sets `build.target` to `.` by default
- [cds@7.2.0] Decimals from query options (e.g., `$filter`) are represented as strings in CQN
- [cds@7.2.0] Improve error message for unsupported transformations with `$apply`
- [cds@7.2.0] For database dialect H2, specialized, localized views for languages `de` and `fr` are no longer generated.
- [cds@7.2.0] Authentication kinds `jwt`, `xsuaa`, and `ias` throw an error during bootstrapping if the necessary credentials are unavailable. Previously, a warning was logged, and authentication was skipped. See `cds bind`/ Hybrid Testing in CAPire for how to combine local development and cloud resources.
- [cds@7.2.0] The Typescript definitions now make use of the default export.
- [cds-mtx@2.6.5] All available HDI deployment parameters can now be passed for tenant deployment.
- [cap-js/graphql@0.7.0] Omit `variables` from log if it is an empty object
- [cap-js/audit-logging@0.3.0] Default value for `cds.requires['audit-log'].handle` changed to `['READ', 'WRITE']`, i.e., accessing sensitive data is now logged by default.
- [cap-js/postgres@1.2.1] Bump minimum required version of `@cap-js/db-service`
- [cap-js/sqlite@1.2.0] `cds.Decimal` and `cds.Float` return numbers instead of strings

### Fixed ​

- [cds-dk@7.2.0] `cds build` adds feature toggles to existing custom build task model options.
- [cds-dk@7.2.0] `cds import` adds the `kind` based on the type of the input file while updating the `package.json`.
- [vscode-cds@7.2.0] CAP notebooks: Do not restrict running of CDS Server cell
- [vscode-cds@7.2.0] Highlighting of custom types starting with built-in name
- [vscode-cds@7.2.0] Outline now only shows first non-empty line of docs when in semantic mode (see user setting `cds.outline.semantical`) as VS Code does not support multi-line docs
- [cds-compiler@4.3.0] parser: Chained methods without arguments such as `b` in `a().b.c()` were lost.
- [cds-compiler@4.3.0] compiler: Type arguments in `cast()` functions, whose column also has an explicit type set, were not properly checked. Now the `cast()`s type and type arguments are checked.
- SQL function `STDDEV(*)` was not parsable.
- In views, published association's ON-conditions containing `$projection` are now rewritten to `$self` in the CSN `elements` property. This ensures recompilability of the CSN.

- [cds-compiler@4.2.4] OData: For compatibility with the Java runtime, don't prepend table aliases to column aliases unless necessary.
- [cds.java@2.2.0] Fixed a bug in the goal `add` of the `cds-maven-plugin`, causing the application start to fail due to incompatible schema.sql.
- [cds.java@2.2.0] Fixed a bug in the goal `add` of the `cds-maven-plugin`, causing the creation of a wrong MTX profile in the `application.yaml`.
- [cds.java@2.2.0] Fixed a bug in interfaces `SaasRegistryUnsubscriptionOptions` and `SaasRegistrySubscriptionOptions`, causing a `ClassCastException` when calling method `getSubscriptionAppAmount`.
- [cds.java@2.2.0] Fixed a bug in the Kafka initialization for public cluster endpoints.
- [cds.java@2.2.0] Fixed a bug, causing an OData V4 requests to fail when the URL contained unnecessary encodings in the URL path.
- [cds.java@2.2.0] Fixed a bug, causing duplicated lambda param names in nested any/all OData v4 remote calls
- [cds.java@1.34.5] Fixed a bug, causing duplicated lambda param names in nested any/all OData v4 remote calls
- [cds.java@1.34.5] Fixed a bug in interfaces `SaasRegistryUnsubscriptionOptions` and `SaasRegistrySubscriptionOptions`, causing a `ClassCastException` when calling method `getSubscriptionAppAmount`.
- [cds4j@2.2.1] OOM on to-many expands in queries with large skip size
- [cds4j@2.2.0] Postgres: Select for update (locks) now also work on localized and draft-enabled entities
- [cds4j@2.2.0] Fixed "Element does not exist" exception on write with structured data for composition of aspects in "odata" transformed csn mode
- [cds4j@2.2.0] SQLite: Fixed 'row value misused' exception on to-many expands in paginated queries with locale
- [cds4j@2.2.0] Reduce memory allocation on large bulk updates
- [cds@7.2.1] HTTP headers argument was not forwarded to remote services when using the `srv.send(...)` API.
- [cds@7.2.1] Not existing draft upon `SAVE` has own error code.
- [cds@7.2.1] Links to documentation in Typescript definitions.
- [cds@7.2.1] Remote service won't check for `credentials.url` in case of messaging.
- [cds@7.2.1] Lean draft: Implicitly added `limit` in some lean draft read scenarios.
- [cds@7.2.1] Lean draft: Association keys in lean draft.
- [cds@7.2.1] Remote service: Preserve namespaces in URLs that do not match the service's namespace.
- [cds@7.2.0] Trace middleware: Adapted usage of `performance.now()` for Node 20.
- [cds@7.2.0] Draft: Associations to non-draft enabled entities must never point to drafts
- [cds@7.2.0] Avoided type error in old db post-processing
- [cds@7.2.0] `.run('/arbitrary-url')` now defaults to a get request and doesn't add request body
- [cds@7.2.0] `@cds.query.limit` is cached per projection
- [cds@7.2.0] Application crash for incorrect usage of REST-style API to run queries
- [cds@7.2.0] The `@requires` annotation on entity level didn't get applied to bound operations
- [cds@7.2.0] `cds.test` run with a profile parameter such as `cds.test('run', '--profile', 'integration-tests')` will use the correct profile.
- [cds@7.2.0] `cds.env.requires.auth.restrict_all_services = false` in combination with `cds.env.requires.middlewares = true` (the default)
- [cap-js/audit-logging@0.3.1] Defaulting of `@PersonalData.DataSubjectRole` to entity name
- [cap-js/audit-logging@0.3.1] Overriding service configuration
- [cap-js/db-service@1.2.1] Association expansion in infix filters. #213
- [cap-js/db-service@1.2.0] resolved a type error which occurred in some cases for deeply nested `expand`s. #173
- [cap-js/db-service@1.2.0] path expression traversing non-foreign-key fields within infix filters are now properly rejected for `exists` predicates. #181
- [cap-js/db-service@1.2.0] CQL functions: In the `args` of the `concat` function an `xpr` is now wrapped in parentheses. #196
- [cap-js/db-service@1.2.0] Make `UPDATE` and `ofarray` typed column compatible. #184
- [cap-js/db-service@1.2.0] Ensure that `INSERT` with `rows` always inserts into the correct column. #193
- [cap-js/db-service@1.2.0] Allow `DateTime` columns to compare against their returned value. #206
- [cap-js/db-service@1.2.0] Deep Insert using backlink associations as key #199.
- [cap-js/postgres@1.2.0] Reserved words are now used to automatically escape reserved words which are used as identifier. #178
- [cap-js/postgres@1.2.0] Remove column count limitation. #150
- [cap-js/sqlite@1.2.1] Adapt implementation to comply with implication of SQLite version 3.43 which is included in `better-sqlite3@8.6.0`. #210
- [cds-mtxs@1.11.0] The Service Manager client now returns all bindings for partial cache misses for `cds.requires.['cds.xt.SaasProvisioningService'].jobs.clusterSize > 1`.
- [cds-mtxs@1.11.0] The Service Manager client will now wait with exponential back-off for unexpected error codes.
- [cds-mtxs@1.11.0] The Service Manager client will now print the correct root cause for errors with a `description` field.
- [cds-mtxs@1.11.0] Command `cds-mtx` now terminates immediately after execution is finished.
- [odata-v2-adapter@1.11.7] Fix absolute service path starting with target path parts e.g. `/odata`
- [odata-v2-adapter@1.11.7] Fix escaping of backslashes in search phrases

### Removed ​

- [cds-dk@7.2.0] Undocumented facet `cds add auditlog`
- [vscode-cds@7.2.0] Legacy `Vanilla` theme - we recommend to use the default theme e.g. `Light Modern` which is similar but covers more token classes

## August 2023 ​

### Added ​

- [cds-compiler@4.2.0] Compiler: Option `moduleLookupDirectories: [ 'strings' ]` can be used to specify additional module lookup directories, similar to `node_modules/`.
- LIMIT and OFFSET clauses can now contain expressions, including parameter references.

- [cds-compiler@4.2.0] to.edm(x): Detect spec violation `scale` > `precision`.

- [cds-compiler@4.2.0] to.sql/for.odata: With the new option `fewerLocalizedViews: true|false`, an entity/view will not get a localized convenience view, if it only has associations to localized entities/views. Only if there is actually a localized element (e.g. new localized element or reference to one), will it get a convenience view.

- [cds-compiler@4.2.0] to.sql In a localized scenario, create foreign key constraints for the generated `.texts` entities.
- Casting `null` to a structure such as `null as field : StructT` is now supported. For each leaf element, an additional `null as field_name` column is added.

- [odata-v2-adapter@1.11.6] Suppress analytical conversion via entity annotation `@cov2ap.analytics.skipForKey`, if all dimension key elements are requested

### Changed ​

- [cds-dk@7.1.1] `cds init` uses latest Maven Java archetype version 2.1.0 for creating Java projects.
- [cds-dk@7.1.1] `cds build` correctly logs build messages based on their severity.
- [cds-dk@7.1.1] `cds build` creates OData EDMX for configured fiori build tasks.
- [cds-compiler@4.2.0] Compiler: Selecting fields of structures or associations (without filters) are now candidates for ON-condition rewrites: It is no longer necessary to select the struct/association directly.
- Consistently handle the case when type elements are defined to be a `key`: the `key` property is not only preserved with `includes`, but also in other cases. Use option `deprecated.noKeyPropagationWithExpansions` to switch to the v3 behavior.
- When including aspects or entities into structured type definitions, do not add actions to the type.
- An `annotate` statement in the `extensions` section of a CSN now consistently uses the `elements` property even if the `annotate` is intended to be used for an enum symbol. Before v4.2, the compiler has used the `enum` property in a CSN of flavor `xtended` (`gensrc`) if it was certain that it was to be applied to an enum symbol.

- [cds-compiler@4.2.0] to.cdl: If a definition has an `actions` property, an `actions {…}` block is now always rendered, and is not ignored if empty.
- [cds-compiler@4.2.0] to.sql: For SQL dialect "sqlite", `cds.DateTime` is now rendered as `DATETIME_TEXT` instead of `TIMESTAMP_TEXT`.
- Casting a literal (except `null`) to a structure now yields a proper error.
- `.texts` entities annotated with `@cds.persistence.skip` (without their original entity having that annotation) lead to deployment issues later. It is now an error.

- [odata-v2-adapter@1.11.6] Switch to `better-sqlite3` via `@cap-js/sqlite`

### Fixed ​

- [cds-dk@7.1.1] When setting `CDS_CONFIG` from the command line, that value is no longer overridden by other env values. Setting `CDS_CONFIG` from the command line in combination with additional command line args, like `--odata`, is not supported at this point.
- [cds-dk@7.1.1] Installing `@sap/cds-dk` now produces a shrinkwrapped layout again if used against npm registries like Artifactory that don't serve the `_hasShrinkwrap` option.
- [cds-dk@7.1.1] `cds import` for OData V4 EDMX imports `Edm.Decimal` data type considering `Precision` and `Scale` facet correctly.
- [cds-dk@7.1.1] `cds import` for OData V4 EDMX imports `DefaultValue="0"` in CSN.
- [cds-compiler@4.2.2] to.sql|hdi.migration: Fix bug that caused a migration to be rendered for the HANA CDS types that were removed from the CSN
- [cds-compiler@4.2.0] Compiler: Reject invalid reference in the `on` of `join`s already while compiling, not just when calling the (SQL) backend.
- Correct the calculation of annotation assignments on the return structure of actions when both `annotate … with {…}` and `annotate … with returns {…}` had been used on the same structure element. Ensure that it works when non-applied, too.
- Do not remove or invent `actions` properties with zero actions or functions in it.
- Correct auto-redirection of direct cycle associations: if the source and target of a model association are the same entity, and the main artifact of the service association based on the model association is a suitable auto-redirection target, then use it as new target, independently from the value of `@cds.redirection.target`.

- [cds-compiler@4.2.0] to.cdl: Indirectly structured types (`type T: Struct;`) with `includes` (`extend T with T2;`), are now properly rendered.
- [cds-compiler@4.2.0] to.sql/hdi/hdbcds: Views on views with parameters did not have localized convenience views based on other localized views (missing `localized.` prefix in FROM clause)
- Run less checks on entities marked with `@cds.persistence.exists`
- Correctly render SELECT items where the column name conflicts with a table alias

- [cds-compiler@4.2.0] to.sql: Casting expressions to a structured type yields a proper error instead of strange compiler error.
- [cds-compiler@4.2.0] to.edm(x): Don't expand `@mandatory` if element has an annotation with prefix `@Common.FieldControl.`.
- Fix a bug when referencing nested many structures, especially referring to a managed association via `$self` comparison.
- Improve handling of non-collection annotation values for collection-like vocabulary types.
- Don't render `Scale: variable` for `cds.Decimal(scale:0)`.

- [cds-compiler@4.2.0] to.sql|hdi.migration: Fixed a bug that caused rendering of `ALTER` statements to abort early and not render some statements.
- CSN output now only contains real `cds` builtins, no early remapping to HANA CDS types or similar.

- [cds-compiler@4.2.0] to.sql.migration: Don't drop-create views marked with `@cds.persistence.exists`
- [cds-compiler@3.9.10] to.edm(x): Error reporting for incorrect handling of "Collection()" has been improved.
- [cds-compiler@3.9.10] to.sql/hdi/hdbcds: Views on views with parameters did not have localized convenience views based on other localized views (missing `localized.` prefix in FROM clause)
- [cds-compiler@3.9.10] to.sql: Casting expressions to a structured type yields a proper error instead of strange compiler error.
- [cds-compiler@3.9.10] to.sql.migration: Don't drop-create views marked with `@cds.persistence.exists` or `@cds.persistence.skip`
- [cds-compiler@3.9.8] to.edm(x): Don't expand `@mandatory` if element has an annotation with prefix `@Common.FieldControl.`.
- Fix a bug when referencing nested many structures, especially referring to a managed association via `$self` comparison.

- [cds-compiler@3.9.8] to.sql/hdi/hdbcds: Detect navigation into arrayed structures and raise helpful errors instead of running into internal errors.
- [cds.java@2.1.1] Fixed a bug, causing draft-related fields to be calculated after custom `@Before` handlers on `DRAFT_CREATE` and `DRAFT_PATCH` events.
- [cds.java@2.1.1] Fixed a bug in MT lib, causing subscriptions to fail with error `class java.lang.Integer cannot be cast to class java.lang.String`.
- [cds4j@2.1.1] Fixed 'Literal value must not be null' exception on nested to-many expands in queries using top (pagination)
- [cds4j@2.1.1] Fixed SQL exception on paginated queries with expands of unmanaged to-many associations that only use constants in the on-condition
- [cds@7.1.2] `req.tenant` is undefined when using new OData parser
- [cds@7.1.2] Draft: replace some occurrences of the `arr.push(...largeArray)` pattern when copying large arrays to prevent maximum call stack size exceeded errors due to large deep update processing when saving the draft
- [cds@7.1.2] Do not add keys to diff as they could be renamed (which leads to SQL error)
- [cds@7.1.2] Custom bound actions for draft-enabled entities don't trigger a READ request on application service anymore
- [cds@7.1.2] `cds.connect.to('db', options)`: add-hoc options for SAP HANA Database Service
- [cds@7.1.2] Reading key-less singleton with `$select` clause while using the new OData parser `cds.env.features.odata_new_parser`
- [cds@7.1.2] Don't use colored logs if `process.env.NO_COLOR` is set or not logging to a terminal (i.e., `!process.stdout.isTTY || !process.stderr.isTTY`)

## July 2023 ​

### Added ​

- [vscode-cds@7.0.2] CAP notebooks: add support for backslash in shell and terminal cells for multiline scripts
- [vscode-cds@7.0.2] CAP notebooks: Shell-type syntax highlighting for Terminal cells
- [cds-compiler@4.1.0] Calculated elements "on-read" can now reference localized elements.
- [cds-compiler@4.1.0] Aliases for columns inside sub-queries and expressions are now optional.
- [cds-compiler@4.1.0] for.odata/to.hdi/to.sql: Specified default value on a managed association is forwarded to a foreign key if the association has exactly one foreign key.
- [cds-compiler@4.1.0] CDL: Annotation-only aspects having no `elements` and `actions` can now be defined with the CDL syntax `@Anno… aspect Name;`. They cannot be extended with elements or actions in order to ensure that they can always be used to extend non-structures. To allow the former but not the latter, use `@Anno… aspect Name {…};`.
- [cds-compiler@4.1.0] to.sql: Support session variables for h2.
- [cds.java@2.1.0] new module `cds-feature-postgresql`, which if present auto-configures DataSource objects for PostgreSQL service bindings.
- [cds.java@2.1.0] new module `cds-feature-pdf` to support PDF export scenarios with OData V4.
- [cds.java@2.1.0] Level of detail for the annotation `@Generated` for generated interfaces is now configurable via `cds-maven-plugin`.
- [cds.java@2.1.0] The property `cds.sql.supportedLocales` now supports a YAML list value, in addition to a comma-separated String value.
- [cds.java@2.1.0] Leverage session context variables on H2 for localized and temporal data.
- [cds.java@2.1.0] The `watch` goal of the `cds-maven-plugion` can be executed from the root directory of the CAP Java application.
- [cds.java@2.1.0] Added the goal `add` to the `cds-maven-plugin`, which supports adding different features to the CAP Java project. Supported features are `sqlite`, `h2` and `multitenancy`.
- [cds.java@2.0.2] The Audit Log OAuth2 plan can now be used with the persistent outbox.
- [cds.java@2.0.2] Reflection Metadata for GraalVM Native Image is now contributed automatically, incl. for event handlers and data and query builder interfaces built and generated in applications.
- [cds.java@1.34.2] The Audit Log OAuth2 plan can now be used with the persistent outbox.
- [cds4j@2.1.0] CQL queries are able to use the alias of the select list item in an `orderBy` clause instead of the element name.
- [cds4j@2.1.0] Introduced an option to configure the level of details for the annotation `@Generated` for generated interfaces.
- [cds4j@2.1.0] Don't enforce locale-specific comparison for equality checks
- [cds4j@2.1.0] Don't enforce locale-specific comparison non-string compares
- [cds4j@2.1.0] H2: support lock with timeout (`FOR UPDATE ... WAIT`)
- [cds4j@2.1.0] H2: use session context variables for localized and temporal data
- [cds@7.1.0] Support to resolve experimental `STREAM` CQN queries that point to views.
- [cds@7.1.0] Enable PDF export via GET to collection with accept header `appplication/pdf`. Custom handler must return the following:js

```
{
  value: ,
  $mediaContentType: , // > optional, defaults to: application/pdf
  $mediaContentDispositionFilename: , // > optional
  $mediaContentDispositionType:  // > optional, defaults to 'attachment' if $mediaContentDispositionFilename is set
}
```
- [cds@7.1.0] Schema for `cds` entry in `package.json` now has a tooltip and default value.
- [cds@7.1.0] `srv.endpoints`: Array containing the information for all endpoints at which the service is served. Example:js

```
[
  { kind: 'odata-v4', path: '/odata/v4/browse' },
  { kind: 'rest', path: '/rest/browse' }
]
```
- [cds@7.1.0] Service level support for @restrict. Limited to grant: '*' and all filter conditions in `where` are ignored. Example:cds

```
@(restrict: [{
  grant: '*',
  to: ['authenticated-user']
}])
```

### Changed ​

- [cds-dk@7.1.0] `cds build` now fails if SAP HANA schema evolution changes exist that need to be manually resolved.
- [cds-dk@7.1.0] `cds build` now throws an error for Java apps using the mtx build task in combination with `@sap/cds-dk` version >= 7.
- [cds-dk@7.1.0] `cds import` now supports OData V4 EDMX files with empty or missing `EntityContainer`.
- [cds-dk@7.0.3] `cds add` adheres to the existing indentation style when changing JSON files.
- [cds-dk@7.0.3] `cds add typer` no longer adds `checkJs: true` to your configuration.
- [cds-dk@7.0.3] `cds init` uses the latest Maven Java archetype version 2.0.2 for creating Java projects.
- [cds-dk@7.0.3] `cds build` now throws an error if the mtx sidecar and application db configuration is inconsistent.
- [cds-dk@7.0.3] `cds watch --open` now delays the opening of the URL by 1s to allow the server to start up. This is needed for plugins that register routes asynchronously.
- [cds-dk@7.0.2] `cds add kibana-logging` is (compatibly) renamed to `cds add kibana`.
- [cds-compiler@4.1.0] api: Function `isInReservedNamespace(name)` handles name `cds` as being in a reserved namespace as well.
- [cds-compiler@4.1.0] `CompilationError.messages` sorting is now severity aware. Errors are listed first.
- [cds-compiler@4.1.0] Compiler: Improve the calculation of semantic code completion candidates.
- Some checks, like those for valid `on` conditions of associations, are now already done with `compile` and not just the backends.
- SQL `cast()`s must always have a `type` property
- Type properties such as `precision` or `length` must be accompanied by a type (possibly inferred).

- [cds-compiler@4.1.0] for.odata/to.hdi/to.sql: No longer reject unmanaged associations as foreign keys of a managed association. Instead, ignore such references during ON-condition rewriting and foreign key generation. Referring to unmanaged associations is incompatible with SAP HANA CDS naming mode 'hdbcds'.
- [cds-compiler@4.1.0] to.sql: Rework session variables for PostgreSQL.
- [cds-compiler@4.1.0] Update OData vocabularies: 'Common', 'HTML5', 'PersonalData', 'UI'.
- [cds.java@2.1.0] The transaction and lock time of the outbox collectors has been significantly reduced, by moving the wait time between failed outbox messages out of the transaction and lock. As part of this change the outbox collectors now require the outbox model from @sap/cds-dk >=6.
- [cds.java@2.1.0] Validating `TopicMessageEventContext` when data, data map or headers map contain `null` values in invalid combinations. An exception is thrown on producer side, if neither data, data map nor headers map is set.
- [cds.java@2.1.0] Use row value comparison for reliable pagination on H2, SQLite and PostgreSQL.
- [cds.java@2.1.0] Conditions for instance-based authorization will have all literal values in them sealed as constants
- [cds.java@2.1.0] Property `cds.sql.supportedLocales` defaults to an empty list as all DBs support session context variables
- [cds.java@2.1.0] The webhook handshake used in integration of Enterprise Messaging (MT) has been removed to avoid synchronization issues introduced by the Deploy main method.
- [cds.java@2.0.2] The Audit Log V2 feature now sets the user name in audit log messages explicitly instead of using `$USER`. By default this is the value of `UserInfo.getName()`. Setting `cds.auditlog.v2.useLogonName` to `true` ensures to use the XSUAA principal name instead, which was used by Audit Log before.
- [cds.java@1.34.4] The webhook handshake used in the integration of Enterprise Messaging (MT) has been removed to avoid synchronization issues introduced by the Deploy main method.
- [cds.java@1.34.2] The Audit Log V2 feature now sets the user name in audit log messages explicitly instead of using `$USER`. By default this is the XSUAA principal, which was used by Audit Log before. Setting `cds.auditlog.v2.useLogonName` to `false` ensures to use the value of `UserInfo.getName()` instead.
- [cap-js/graphql@0.6.2] Pin `graphiql` version to `^3`
- [cap-js/graphql@0.6.2] Pin `@graphiql/plugin-explorer` version to `~0.3`
- [cap-js/graphql@0.6.1] Improved query logging: Don't log queries that are `undefined`
- Log `operationName`
- Log `variables` when not in production
- Sanitize arguments and their values in queries when in production

- [cds4j@2.1.0] Queries and expressions that are defined in the CDS model will have all literals in them sealed as the constants.
- [cds4j@2.1.0] The calculated elements (annotated with the annotation `@Core.Computed`) are no longer searched by default.
- [cds-mtxs@1.9.2] Remove peerDependency to `@sap/cds>=6`. This caused troubles in installation scenarios where sap/cds 7 was fetched while 6 should be used.

### Fixed ​

- [cds-dk@7.1.0] Calls from SAP Business Application Studio `New Project from Template` wizard are now handled correctly.
- [cds-dk@7.1.0] `cds add cf-manifest` correctly generates the XSUAA instance name.
- [cds-dk@7.1.0] `cds build` always uses the configured SAP Hana build task when building the mtx sidecar.
- [cds-dk@7.1.0] `cds import` OData V4 EDMX fix for Annotation Alias and Namespace value replacement.
- [cds-dk@7.0.3] `cds deploy` writes settings under the profile `hybrid` as the default in `.cdsrc-private.json`
- [cds-dk@7.0.3] `cds add sample` uses the default `/odata/v4/` service paths and data source paths in the UI5 `manifest.json` files.
- [cds-dk@7.0.3] When a request fails, shorter errors are printed and secret data is hidden. (Set `DEBUG=req` in env to see all details again.)
- [cds-dk@7.0.3] Now shows all commands when a misspelled command is used along with the similarly named command.
- [cds-dk@7.0.3] `cds import --from edmx` fixes rendering of nested annotations in the CSN.
- [cds-dk@7.0.2] `cds` commands do not swallow error stack traces in some cases any more.
- [cds-dk@7.0.2] `cds watch` does not swallow compiler errors in some cases any more.
- [cds-dk@7.0.2] `cds add sample` has modernized configuration for Fiori-related files in the `app` folder.
- [cds-dk@7.0.2] `cds add sample` now also contains a read-only service for browsing books.
- [cds-dk@7.0.2] `cds add kibana-logging` now also adds the logging service to the MTX sidecar and App Router, if available.
- [cds-dk@7.0.2] `cds build` preferably creates i18n bundle at default location `_i18n` for custom i18n folder configurations.
- [cds-dk@7.0.2] `cds watch` no longer fails if `@sap/cds-dk` is installed as dependency along with `cds-swagger-ui-express`.
- [cds-dk@7.0.2] `cds build` ensures that `@sap/cds` version >= 6 is installed.
- [vscode-cds@7.0.2] CDS Welcome Page does not show an error message if page is not reachable during start up
- [vscode-cds@7.0.2] CDS Welcome Page now starts with correct theme
- [vscode-cds@7.0.2] CAP notebooks: Only allow resolving, but not setting of env vars in Magic command cells
- [cds.java@2.0.2] Fixed a bug, causing wrong data response for complex type requests with path expressions.
- [cds-compiler@4.1.2] to.hdi.migration: Changes in constraints are not rendered as part of the .hdbmigrationtable file, as they belong in other HDI artifacts
- [cds-compiler@4.1.0] Compiler: ensure that annotations of elements in anonymous aspects of managed compositions are not lost.
- issue error for definitions like `entity Self as projection on Base { $self.* };` instead of simply concluding that the projection has zero elements.
- do not report an invalid cyclic dependency if associations between two entities are valid cycles.
- Element type references can follow associations (removed v4.0 incompatibility) again.

- [cds-compiler@4.1.0] to.sql: `$self` references inside a nested projection using `$self` was incorrectly resolved.
- associations to entities marked with `@cds.persistence.skip` were not properly checked inside nested projections.
- Select items casting `null` to an arrayed type work again, e.g. `null as ManyType`.

- [cds-compiler@4.1.0] to.sql/hdi/hdbcds: Raise a nice error message for `@sql.append` on managed associations/compositions, as we do for structured error messages.
- [cds-compiler@4.1.0] to.cdl: Annotations with multiple qualifiers (`#`) are now rendered correctly.
- [cds-compiler@4.1.0] to.edm(x): Revert change introduced with 3.9.0 "Correct referential constraint calculation for `[0..1]` backlink associations".
- [cds-compiler@4.1.0] for.odata: Process shortcut annotations independently of sequence.
- [cds-compiler@4.1.0] to.sql.migration: Respect unique and referential constraints for delta calculation.
- Added a configurable error for primary key additions, as those will lead to errors if the table contains data. This could lead to inconsistent states if some deployments succeed and others fail, so by default it is an error.

- [cds-compiler@3.9.8] to.edm(x): Don't expand `@mandatory` if element has an annotation with prefix `@Common.FieldControl.`.
- Fix a bug when referencing nested many structures, especially referring to a managed association via `$self` comparison.

- [cds-compiler@3.9.8] to.sql/hdi/hdbcds: Detect navigation into arrayed structures and raise helpful errors instead of running into internal errors.
- [cds-compiler@3.9.6] to.edm(x): Revert change introduced with 3.9.0. "Correct referential constraint calculation for `[0..1]` backlink associations".
- [cds-compiler@3.9.6] for.odata: Process shortcut annotations independently of sequence.
- [cds.java@2.1.0] Fixed a bug in the Kafka messaging service, that prohibited the retrieval of the partition key and the partition.
- [cds.java@2.1.0] Fixed a bug, causing overly restrictive key value checks in OData V4 deep updates with delta payloads
- [cds.java@2.1.0] Fixed a bug in the goal `watch` of the cds-maven-plugin, causing the `watch` goal not to use the Spring-Boot Developer Tools, even if they are installed.
- [cds.java@2.1.0] Fixed a bug, causing `ArrayIndexOutOfBoundsException` when updating or deleting draft-enabled entities.
- [cds.java@2.1.0] Fixed a bug in the Kafka messaging service that caused an exception when creating a topic with a replication factor lower than the default.
- [cds.java@2.1.0] Fixed a bug, causing Kafka to not work with service bindings with basic authentication.
- [cds.java@2.1.0] Fixed a bug, causing `XsuaaServiceConfiguration` bean to no longer be overridable by applications if `XsuaaServiceConfigurationDefault` class is not used.
- [cds.java@2.0.2] Fixed a bug, returning an incorrect data response for complex type requests with path expressions.
- [cds.java@2.0.2] Fixed a bug, that caused `NullPointerException` in the OData V2 protocol adapter during an error handling when a payload or the URL contains dates in a wrong format.
- [cds.java@1.34.4] Fixed a bug in the Kafka messaging service that caused an exception when creating a topic with a replication factor lower than the default.
- [cds.java@1.34.3] Fixed a bug, causing Kafka to not work with service bindings with basic authentication.
- [cds.java@1.34.2] Fixed a bug, causing wrong data response for complex type requests with path expressions.
- [cds.java@1.34.2] Fixed a bug, that caused issues with generating the OData V4 nextLink URL, when the original URL had encoded `$` characters in query parameter names.
- [cds.java@1.34.2] Fixed a bug preventing the attributes typed as `Edm.DateTime` in OData V2 to accept the date values with a fractions of a seconds or without the seconds.
- [cds.java@1.34.2] Fixed a bug, that caused `NullPointerException` in the OData V2 protocol adapter during an error handling when a payload or the URL contains dates in a wrong format.
- [cds.java@1.34.2] Fixed a bug, that caused a `ClassCastException` when making use of `SaasRegistryUnsubscriptionOptions` in unsubscription handler of DeployService.
- [cds.java@1.34.2] Fixed a bug, that caused a HTTP request to the MTX Sidecar during startup, if provider tenant normalization was enabled.
- [cds4j@2.1.0] OOM when to-many expand was used with large, paginated result set.
- [cds4j@2.1.0] PostgreSQL: represent timestamps in session context variables in UTC.
- [cds4j@2.0.2] Allow to use enum constants as default values for elements with enum type
- [cds4j@2.0.2] Throw `NullPointerException` when adding `null` to `Select:columns`, `excluding`, `groupBy`, `orderBy` and `Expand:items`, `orderBy`
- [cds@7.1.1] Lean draft: read actives via service on draft edit.
- [cds@7.1.1] Resolve column name for experimental `STREAM` CQN queries that point to views.
- [cds@7.1.1] Only log the error in case of an unhandled rejection.
- [cds@7.1.0] Multiple TypeScript improvements.
- [cds@7.1.0] Proper handling for `expand=*` for OData URL to CQN parser (`cds.env.features.odata_new_parser`).
- [cds@7.1.0] Fully qualified operation names are correctly resolved in the rest adapter.
- [cds@7.1.0] Log level for odata metadata cache was not handled correctly.
- [cds@7.1.0] Protocol paths are normalized to always have a leading slash.
- [cds@7.1.0] `@odata` shortcut for `odata-v4` protocol with custom configuration.
- [cds@7.1.0] Default protocol is `odata-v4`, independent of the order in `cds.env.protocols`.
- [cds@7.1.0] Data is not logged for GET and DELETE remote requests.
- [cds@7.1.0] draft: deep updates without changes should not update the `modifiedAt` field.
- [cds@7.1.0] Lean draft: do not propagate `@Capabilities.NavigationRestrictions.RestrictedProperties`.
- [cds@7.1.0] Commit db transaction only when the outbound streaming has ended.
- [cds@7.1.0] Lean draft: deactivate the legacy `drafts` getter.
- [cds@7.1.0] Updated typings for srv.send.
- [cds@7.1.0] `$search`: exclude calculated fields/expressions from the default search in the projection of projections.
- [cds@7.1.0] Immutable properties are always removed from the payload during UPDATE.
- [cds@7.1.0] `serviceinfo.urlPath` contains the first endpoint of the service (cf. `srv.endpoints`), which is the legacy path if `cds.env.features.serve_on_root === true`.
- [cds@7.0.3] Compile for lean draft no longer adds a draft entity for external entities
- [cds@7.0.3] Rollback awaited in REST adapter
- [cds@7.0.3] `service.on('error')` handler gets invoked only once
- [cds@7.0.3] `SELECT.one.localized`
- [cds@7.0.3] `COPYFILE_DISABLE=1` is now set for building `tar` archives by default
- [cds@7.0.3] Actions of projection target are no longer accessible in the linked models
- [cds@7.0.3] Batch execute model-less mass inputs when on `@sap/hana-client`
- [cds@7.0.3] Requests to `//webapp` return 404 for absolute `@path` specifications
- [cds@7.0.3] `cds compile --to serviceinfo` no longer returns paths w/ Windows `\` path characters
- [cds@7.0.2] Glitch in `cds.deploy` if no change was applied
- [cds@7.0.2] Detection of `.cdsrc-private.json` during startup
- [cds@7.0.2] Respect capabilities annotation for draft events
- [cds@7.0.2] `cds compile --to serviceinfo` returns correct service paths again
- [cds@7.0.1] Feature toggle detection in single tenant mode
- [cds@7.0.1] Log output for OData $batch requests
- [cds@7.0.1] Avoid "catastrophic backtracking" issue in okra's tokenizer
- [cds@7.0.1] Transaction marked as committed too early
- [cap-js/graphql@0.6.2] GraphiQL Explorer Plugin initialization due to upstream implementation pattern change
- [cap-js/graphql@0.6.1] Changed GraphiQL Explorer Plugin CDN URL due to upstream renaming
- [odata-v2-adapter@1.11.4] Remove support for `serve_on_root`. Define path explicitly to `v2` to restore previous behavior
- [odata-v2-adapter@1.11.3] Fix absolute OData V4 paths for `$batch` calls
- [odata-v2-adapter@1.11.2] Fix `$metadata` request for absolute OData V4 paths
- [cds-mtxs@1.9.2] The MTX migration script will not undeploy application database tables if HDI `auto_undeploy` is configured for the `cds.xt.DeploymentService`.
- [cds-mtxs@1.9.2] The result verification of the MTX migration script no longer shows false errors when using `--force`.
- [cds-mtxs@1.9.2] When a request fails, shorter errors are logged and secret data is hidden. (Set `DEBUG=req` in env to see all details again.)
- [cds-mtxs@1.9.1] `GET /-/cds/saas-provisioning/tenant` now doesn't include a duplicate `tenant` field, but only provides the tenant via `subscribedTenantId`.
- [cds-mtxs@1.9.1] After switching from `@sap/cds-mtx` to `@sap/cds-mtxs`, existing tenants will now be taken into account when running an upgrade for all tenants (`['*']`).

### Removed ​

- [cds-compiler@4.1.0] Compiler: forbid wildcards in projection extensions: `extend … with columns { * )`.
- forbid column references such as `$user.*`, `$user.{id}` and `$user {id}`.

## June 2023 ​

### Added ​

- [cds-dk@7.0.0] `cds add connectivity` now supports MTA-based deployment.
- [cds-dk@7.0.0] `cds add destination` now supports MTA-based deployment.
- [cds-dk@7.0.0] `cds add enterprise-messaging` creates scopes for `emcallback` and `emmanagement` in the `xs-security.json` if XSUAA is enabled.
- [cds-dk@7.0.0] `cds add hana` adds the new package `@sap/cds-hana` instead of the direct `hdb` dependency.
- [cds-dk@7.0.0] `cds add mta` writes an `event-mesh.json` if the Event Mesh is set up.
- [cds-dk@7.0.0] `cds add typer` adds type generation support for projects using the Node runtime.
- [cds-dk@7.0.0] `cds add sample` creates a bookshop application incl. Fiori UI.
- [cds-dk@7.0.0] `cds add samples` is deprecated. Use `cds add tiny-sample` instead.
- [cds-dk@7.0.0] `cds env` supports new options `--keys`, `--list`, `-json`, and `--raw`. See `cds env ?` for details.
- [cds-dk@7.0.0] `cds import --from asyncapi` now adds `@topic` annotation for specifying the channel name for the event.
- [cds-dk@7.0.0] `cds import --from asyncapi` now updates the `package.json` for multiple services.
- [cds-dk@7.0.0] `cds init --add java` prints a more specific error message when not using Java 17 in SAP Business Application Studio.
- [cds-dk@7.0.0] New property `cds.cli` allows reflecting on the CLI command and arguments.
- [vscode-cds@7.0.1] CAP notebooks: CDS server cell reacts to regular expression `/started application/i`.
- [vscode-cds@7.0.0] CAP with Typescript Beta: generate TS typings from CDS model files upon save - requires `@cap-js/cds-typer` to be installed in project
- [vscode-cds@7.0.0] CDS language: Support highlighting, formatting and where-used for new language constructs: ternary operator, `stored` elements and annotated `returns` statements
- [cds-compiler@4.0.0] Calculated elements "on-write" are now supported, e.g. `elem = field + 1 stored;` will be rendered in SQL as `GENERATED ALWAYS AS`.
- [cds-compiler@4.0.0] compiler: `returns` of actions and functions can now be annotated, e.g.cds

```
action A() returns @direct { … };
annotate A with returns {
  @anno val;
}
```
- It is now possible to use `*/` inside doc comments by escaping it `*\/`. Only this exact string can be escaped.
- Functions `parse.expr` and `parse.cql` now support `group by`, `having`, `order by`, `limit`, and `offset` in infix filters.
- In expressions, you can now use function names after the `new` keyword which do not start with `st_`, if the name is followed by an open parenthesis.

- [cds@7.0.0] Handling of expand with multiple `*` (e.g. $expand=,) in new parser. When using `*` in an expand the new OData parser now removes all unneeded `*`.
- [cds@7.0.0] Tests run with `cds.test()` now also load `cds-plugins`
- [cap-js/graphql@0.6.0] Support for `@sap/cds^7` middlewares and protocols. Note: services now need to be annotated with protocol annotations such as `@graphql` or `@protocol: 'graphql'`.
- [cds-mtxs@1.9.0] MTXS Migration now checks extensibility configuration if old extensions exist.
- [cds-mtxs@1.9.0] Upgrade now checks if MTXS Migration has been done if old extensions exist and if extensibility is properly configured.
- [cds-mtxs@1.9.0] `GET /-/cds/saas-provisioning/tenant` now returns a `subscribedTenantId` field, even if the tenant was onboarded with no metadata.
- [cds-mtxs@1.9.0] Token resource now accepts the POST method (can be used with @sap/cds-dk version 7).
- [odata-v2-adapter@1.11.0] CDS 7 support
- [odata-v2-adapter@1.11.0] Default route with CDS < 7 or option `middlewares` disabled or feature `serve_on_root` enabled stays `v2`
- [odata-v2-adapter@1.11.0] Default route with CDS >= 7 is `/odata/v2`

### Changed ​

- [cds-dk@7.0.1] `cds add` has a slightly revamped CLI UX.
- [cds-dk@7.0.1] `cds init` and `cds add sqlite` add the new package `@cap-js/sqlite`, which uses `better-sqlite` instead of `sqlite3`.
- [cds-dk@7.0.1] `cds add sample-tiny` is (compatibly) renamed to `cds add tiny-sample`.
- [cds-dk@7.0.0] `--production` as a global flag now sets `CDS_ENV` to `production` instead of `NODE_ENV`.
- [cds-dk@7.0.0] `cds add typer` is now allowed to be used, even if the runtime considers the project to be of Java nature.
- [cds-dk@7.0.0] `cds add typer` now generates to `@cds-models`, which will also be `.gitignore`d by the facet.
- [cds-dk@7.0.0] `cds add typer` now properly handles TypeScript projects, if possible.
- [cds-dk@7.0.0] `cds add connectivity` now supports MTA-based deployment.
- [cds-dk@7.0.0] `cds add data --for` is dropped in favor of `--data:for`.
- [cds-dk@7.0.0] `cds add destinations` is renamed to `cds add destination`.
- [cds-dk@7.0.0] `cds add enterprise-messaging` changes the default for the `topicRules.publish-filter` to `${namespace}/*`.
- [cds-dk@7.0.0] `cds add enterprise-messaging` uses a more unique default (`default//1`) as its `namespace`.
- [cds-dk@7.0.0] `cds add hana` uses a plain `cds.requires.db = 'hana'`, also for multitenancy scenarios.
- [cds-dk@7.0.0] `cds bind` parameter `--for` replaces `--profile` to specify the profile to store connection information in `.cdsrc-private.json`; `cds bind --exec` still uses `--profile`.
- [cds-dk@7.0.0] `cds build` moved to `@sap/cds-dk`.
- [cds-dk@7.0.0] `cds build` no longer supports `@sap/cds-mtx`. Migrate to `@sap/cds-mtxs`, see https://cap.cloud.sap/docs/guides/multitenancy/old-mtx-migration.
- [cds-dk@7.0.0] `cds build` no longer supports the classic CAP Java runtime. Migrate to the current CAP Java runtime SDK, see https://cap.cloud.sap/docs/java/migration.
- [cds-dk@7.0.0] `cds deploy` moved to `@sap/cds-dk`.
- [cds-dk@7.0.0] `cds deploy` now supports `--for` to specify the profile to store connection information in `.cdsrc-private.json`.
- [cds-dk@7.0.0] `cds deploy` parameter `--no-save` is default.
- [cds-dk@7.0.0] `cds import --from asyncapi` now takes event name from key `name` in the message.
- [cds-dk@7.0.0] `cds init` uses latest Maven Java archetype version `2.0.1` for creating Java projects. This also requires Java 17 or higher.
- [cds-dk@7.0.0] `cds watch` and `cds run` don't display stack traces any more if no models are found.
- [cds-dk@7.0.0] `cds login` (and other commands implicitly logging in) now use the POST method to transmit credentials to @sap/cds-mtxs.
- [vscode-cds@7.0.1] Changed default output for generated types to `@cds-models`
- [vscode-cds@7.0.1] Minimum VS Code version is now 1.77.0
- [vscode-cds@7.0.0] CAP notebooks: Default code cell type is 'shell'
- [vscode-cds@7.0.0] Minimum VS Code version is now 1.78.0
- [cds-compiler@4.0.0] API: `messageContext()` is now deprecated; use `messageStringMultiline()` instead with `config.sourceMap`.
- `messageString(err, config)` has a new signature; the old one is still supported for backward compatibility.
- Option `docComment: false` now removes doc comments during compilation even for CSN. If this option is not defined, doc comments are checked, but not put into CSN.

- [cds-compiler@4.0.0] compiler: CSN: Specified elements of queries are now resolved and checked (previously ignored except for annotations). Type properties (`length`, …) and some element properties are now taken from the specified elements instead of relying only on the elements inferred by the compiler.
- CSN: Compiler accepts CSN input with CSN version `0.1.0` (produced by cds-compiler version 1.10.0 and older) only if the version attribute is properly set, i.e. `"version": {"csn": "0.1.0"}`.
- CSN: Type properties (`length`, `precision`, `scale`, and `srid`) next to `elements` or `items` in CSN input is now an error. Previously ignored.
- An extension of the form `extend Def with { name = 42 };` is now represented in parsed CSN as adding a calculated element.
- `having` as the first word in an infix filter is now interpreted as keyword. Write `![having]` to have it parsed as identifier.
- If a definition overrides elements of an included definition, it is sorted according to the included definition's element order. This is similar to how `*` works in projections. It is no longer possible to overwrite a scalar element with a structure and vice versa.
- Two included definitions cannot have the same element. The including entity must override the element.
- If a type with properties precision and scale is extended, the `extend` statement must extend both properties.
- `annotate E:elem with actions {};` is now a parser error and no longer a compiler error. Only relevant if you use `parseCdl`-style CSN.
- Annotations (and other properties) are now propagated to `returns` as well, if the returned artifact is a non-entity, e.g. a type.
- `annotate E with returns {…}` is now only applied to actions/functions. Previous compiler versions autocorrected the `annotate` statements to apply them to an entity's elements.
- Calculated elements can't refer to localized elements.
- Table aliases can't be used in `extend Query with columns {…}` any longer. Use direct element references instead.
- Table alias and mixin names can no longer start with `$`. Choose a different name. With this change we avoid unexpected name resolution effects in combination with built-in `$`-variables.
- A semicolon is now required after a type definition like `type T : many {} null`.
- It is no longer possible to write `type of $self.‹elem›` to refer to the element `‹Def›.‹elem›` where `‹Def›` is the main artifact where the type expression is embedded in. Replace by `type of :‹elem›`.
- Message ID `duplicate-autoexposed` was changed to `def-duplicate-autoexposed`.

- [cds-compiler@4.0.0] Update OData vocabularies 'Common', 'UI'.
- [cds-compiler@4.0.0] to.sql: Change default `length` for `cds.String` for all SQL dialects except `hana` to 255.
- for the sql dialect `postgres`, the `ON DELETE RESTRICT` / `ON UPDATE RESTRICT` rules are omitted from the referential constraint definitions.

- [cds-compiler@4.0.0] to.cdl: If associations are used inside `items`, an error is emitted instead of rendering invalid CDL.
- `items` inside `items`, where the outer one does not have a `type`, is now always an error, because it can't be rendered in CDL

- [cds@7.0.0] Result of `READ` events is now always an array. Previously, it could be `null/undefined` (now empty array), single object (now array with one entry) or array.
- [cds@7.0.0] OData: `PUT`/`PATCH` requests resulting in a new entity (i.e., the `UPSERT` effectively was an `INSERT`) return status code 201
- [cds@7.0.0] Draft: Draft activate requests resulting in an `UPDATE` return status code 200
- [cds@7.0.0] ETags are validated via `WHERE EXISTS` clause attached to query on `GET`, `PUT`/`PATCH`, and `DELETE`
- [cds@7.0.0] OData: `PUT`/`PATCH` with `if-match` header prevents `UPSERT`, i.e., only an existing entity can be updated by such a request
- [cds@7.0.0] Runtime support for `@sap/instance-manager` is removed in favor of the `cds-mtxs` Service Manager client.
- [cds@7.0.0] In multitenant mode, the HANA pool uses the `cds-mtxs` credentials cache
- [cds@7.0.0] Draft handlers are registered for all entities.
- [cds@7.0.0] Decimals in client input are validated in runtime's assert framework (previously OData adapter)
- [cds@7.0.0] `cds build` and `cds deploy --to hana` have moved to `@sap/cds-dk`. Upgrade `@sap/cds-dk` to version 7 to continue using these commands.
- [cds@7.0.0] Changed the behavior of `SELECT` queries for single entities to return `undefined` instead of `null` when no record is found.
- [cds@7.0.0] Fiori preview has moved to new `@sap/cds-fiori` module.
- [cds@7.0.0] Numbers are now always used as placeholders in SQL, except for `SELECT 1 From...`, `LIMIT` and the comparison of two numeric values (e.g. `1 eq 1`).
- [cds@7.0.0] Only new major version 3 of SAP Cloud SDK is from now on supported. Please make sure to upgrade. Version 2 is not maintained anymore.
- [cds@7.0.0] `@protocol` annotation can be used to serve multiple protocols per service.
- [cds@7.0.0] Per default, services are served with a protocol-specific prefix (for example '/odata/v4' for a service using the OData V4 protocol). To also serve without this prefix, as it was the case in older @sap/cds versions, the flag `cds.env.features.serve_on_root` can be set to `true`. Alternatively, the `@path` annotation can be used to explicitly specify an absolute path (with a leading `/`).
- [cds@7.0.0] `cds.requires.middlewares` is enabled by default.
- [cds@7.0.0] The order of csv files that `cds deploy --to sqlite` uses now reflects the dependency order of cds models. This is needed if `UPSERT` is used to create a logically correct deployment.
- [cds@7.0.0] `cds.fiori.lean_draft` is activated by default. You can still set it to `false` as fallback.
- [cap-js/graphql@0.6.0] Bump required `@sap/cds` version to `>=7`
- [cap-js/graphql@0.6.0] `@cap-js/graphql/index.js` now collects individual services and mounts the adapter as a protocol middleware on the `cds.on('served', ...)` event
- [cap-js/graphql@0.6.0] Moved the `GraphQLAdapter` module to `lib/GraphQLAdapter.js` and merged it with `CDSGraphQLAdapter` previously found in `index.js` in the root directory
- [cap-js/graphql@0.6.0] Don't generate fields that represent compositions of aspects within mutation types that represent services
- [cap-js/graphql@0.6.0] Disabled conjunction on the same field for the following operators: `eq` (Equal)
- `gt` (Greater Than)
- `ge` (Greater Than or Equal)
- `le` (Less Than or Equal)
- `lt` (Less Than)
- `startswith`
- `endswith`

### Fixed ​

- [cds-dk@7.0.1] `cds import --from asyncapi` now maps `@topic` annotation to the event key.
- [cds-dk@7.0.1] `cds build` now copies the contents of mtx sidecar subfolders to the deployment layout.
- [cds-dk@7.0.1] `cds compile --to xsuaa` can be used again if `@sap/cds` 6 is installed.
- [cds-dk@7.0.1] `cds env` output is again JSON in non-interactive terminals. This restores the behavior from `@sap/cds-dk` 6.
- [cds-dk@7.0.0] `cds add mta` now correctly generates the `mta.yaml` following a `cds add enterprise-messaging-shared`.
- [cds-dk@7.0.0] `cds add typer` now correctly defaults to `…/cds-models`, instead of `…/cds-modules` as output path for generated types.
- [cds-dk@7.0.0] `cds build` ignores invalid entries in an `undeploy.json` file.
- [cds-dk@7.0.0] `cds build` now correctly copies CAP Node.js service handler implementations contained in different service modules. The service handlers will now be loaded correctly in local as well as in cloud deployment scenarios.
- [cds-dk@7.0.0] `cds build` now correctly copies JavaScript files located in nested folders of a Node.js app into the deployment folder.
- [cds-dk@7.0.0] `cds build` now correctly resolves model files of complex mtx extension projects.
- [cds-dk@7.0.0] `cds build` now correctly supports shortcut options
- [cds-dk@7.0.0] `cds-ts watch` no longer fails with strange compilation errors if called in combination w/ `ts-node`.
- [cds-dk@7.0.0] `cds login` no longer echoes output from an npm subprocess.
- [cds-dk@7.0.0] `cds build` now creates the correct deployment layout for Node.js applications.
- [cds-dk@6.8.3] `@sap/cds` 6.8.4
- [cds-dk@6.8.3] `@sap/cds-compiler` 3.9.4
- [vscode-cds@7.0.0] CAP Release Notes page: remove superfluous footer section
- [vscode-cds@7.0.0] CAP notebooks: Magic command newline issues on windows powershell
- [cds-compiler@4.0.2] to.sql.migration: When drop-creating views, also drop-create (transitively) dependent views.
- [cds-compiler@4.0.2] to.edm(x): Forward `@odata.singleton { nullable }` annotation to parameter entity.
- Annotations assigned to a parameterized entity are propagated to the parameter entity if the annotation is applicable to either an `edm.EntitySet` or `edm.Singleton`. This especially covers all `@Capabilities` and their shortcut forms like `@readonly` and `@insertonly`. The original annotation is not removed from the original entity. Annotations that should be rendered at the parameter `edm.EntityType` can be qualified with `$parameters`. Explicitly qualified annotations are removed from the original entity allowing individual assignments.

- [cds-compiler@4.0.0] compiler: `parseCdl` CSN did not include correct `...` entries for annotations containing `... up to`
- Type references inside calculated elements were not always correctly resolved.
- `USING` empty files were incorrectly marked as "not found".
- If an association was inside `items`, e.g. via type chains, the compiler crashes instead of emitting proper errors.

- [cds-compiler@4.0.0] Localized convenience views for projections (not views) did not have references rewritten. This only affects CSN, the SQL result was correct.
- [cds-compiler@4.0.0] Calculated elements in composition-of-aspect lost their `value` when generating composition targets.
- [cds-compiler@4.0.0] to.sql/to.hdi/for.odata: Foreign keys in ON-conditions were not always properly checked and flattened if explicit `keys` were provided that reference structures.
- [cds-compiler@4.0.0] Extending bound actions with elements is not possible, but was not reported by the compiler and elements were silently lost.
- [cds-compiler@4.0.0] for.odata: Don't propagate `@odata { Type, MaxLength, Precision, Scale }` from structured to flattened leaf elements.
- Remove `type: null` attribute from element definitions referencing an undefined type via `type of`.

- [cds-compiler@4.0.0] to.edm(x): Don't reject untyped properties that are API typed with a valid `@odata.Type` annotation.
- Render correct `EntitySetPath` and annotation target path for actions/functions with explicit binding parameter.

- [cds-compiler@4.0.0] to.cdl: ParseCdl-style CSN containing annotations with `...` were not properly rendered.
- [cds-compiler@3.9.4] compiler: `USING` empty files were incorrectly marked as "not found".
- [cds-compiler@3.9.4] Localized convenience views for projections (not views) did not have references rewritten. This only affects CSN, the SQL result was correct.
- [cds-compiler@3.9.4] to.edm(x): Render correct EntitySetPath and annotation target path for actions/functions with explicit binding parameter.
- [cds.java@2.0.1] Fixed a bug, that caused a `NullPointerException`, if the headers map was set to `null` in `TopicMessageEventContext`.
- [cds.java@2.0.1] Fixed a bug preventing the attributes typed as `Edm.DateTime` in OData V2 to accept the date values with a fractions of a seconds or without the seconds.
- [cds.java@2.0.1] Fixed a bug, that caused a `ClassCastException` when making use of `SaasRegistryUnsubscriptionOptions` in unsubscription handler of DeployService.
- [cds@7.0.0] UUID typed key properties are no longer automatically filled during UPSERT
- [cds@7.0.0] OData: When undefined in the payload, requests for actions with not nullable array-type parameters result in a client-side error
- [cds@7.0.0] Missing `GROUP BY` in request with $apply in combination with aggregate on restricted entity
- [cds@7.0.0] When `@sap/cds` was not installed underneath project root, cds-plugins where not found
- [cds@7.0.0] Support for multiline texts in `properties` files
- [cds@7.0.0] Error when reading auth protected entities with infix filter in expand
- [cds@7.0.0] Glitch in transaction handling in case of concurrent async before handlers
- [cds@6.8.3] `cds build` no longer reports CAP Java Classic runtime usage by mistake.
- [cds@6.8.3] `cds version` prints the local `@sap/cds` version, even if called from a different `@sap/cds` installation.
- [cds@6.8.3] User challenges handling in case of `cds.env.auth.restrict_all_services: false`
- [cds-mtxs@1.8.4] Further improvement of timeout error handling when fetching uaa tokens.
- [cds-mtxs@1.8.3] Enables passing deployment options to the `upgrade` endpoint of `cds.xt.SaasProvisioningService`.
- [cds-mtxs@1.8.3] The Service Manager now requests the authorization token resiliently.
- [cds-mtxs@1.8.3] MTXS migration script now ignores changes caused by sap.common entities when verifying the migration result.
- [odata-v2-adapter@1.11.1] Fix compatibility for option `middlewares` disabled or feature `serve_on_root` enabled
- [odata-v2-adapter@1.10.6] Fix metadata type for managed composition entities and sub-entities

### Removed ​

- [cds-compiler@4.0.0] NodeJs 14 is no longer supported.
- [cds-compiler@4.0.0] `CompileMessage` no longer has property `location`, which was deprecated in v2.1.0, but `$location`, which is supported since v2.1.0
- [cds-compiler@4.0.0] "Smart type references" such as `Entity.myElement` instead of `Entity:myElement` are removed, because since compiler v2, `Entity.myElement` could also be a definition, creating ambiguities.
- [cds-compiler@4.0.0] Element type references can no longer follow associations, i.e. `E:assoc.id` is not allowed.
- [cds@7.0.0] Deprecated `req.run()` function, use `cds.run()` instead.
- [cds@7.0.0] Support for unofficial feature flag `cds.env.features.bigjs`
- [cds@7.0.0] Support for unofficial feature flag `cds.features.parameterized_numbers`
- [cds@7.0.0] Deprecated referential integrity checks at runtime
- [cds@7.0.0] Support for `cds-mtx`
- [cds@7.0.0] Support for Node 14
- [cds@7.0.0] Internal `req.getUriInfo()` and `req.getUrlObject()`
- [cds@7.0.0] `cds deploy --to hana` is now part of `@sap/cds-dk`.
- [cds@7.0.0] Deprecated compat mode `cds.env.features.cds_tx_protection = false`
- [cds@7.0.0] Beta `AuditLogService` and out-of-the-box audit logging. Use plugin `@cap-js/audit-logging` instead.

## May 2023 ​

### Added ​

- [cds-dk@6.8.0] `cds add file-based-messaging` adds configuration for file-based messaging (Node.js).
- [cds-dk@6.8.0] `cds add redis-messaging` adds configuration for Redis messaging (Node.js).
- [cds-dk@6.8.0] `cds add enterprise-messaging-shared` adds configuration for Event Mesh support with `kind = 'enterprise-messaging-shared'` (Node.js).
- [cds-dk@6.8.0] `cds import` now supports OData V4 EDMX file containing multiple `Schemas` with single `EntityContainer`.
- [cds-dk@6.8.0] `cds import` now supports importing of AsyncAPI documents.
- [cds-dk@6.8.0] `cds login -m [:]` now supports X.509 (mTLS) credential-type in XSUAA binding of @sap/cds-mtxs.
- [vscode-cds@6.8.2] CAP notebooks: magic command can also be written inside of line- and block-comments
- [vscode-cds@6.8.0] User setting `cds.typeGenerator.localInstallationOnly` has been added to allow more finely grained control for the user over the resolution of the type generation package
- [vscode-cds@6.8.0] New command `Record Traces for Support Ticket` to assist creation of support tickets for CDS editor issues
- [vscode-cds@6.8.0] CAP notebooks: new cell type `CDS Server`, which is also executable for CDS background processes.
- [cds.java@2.0.0] Added OpenTelemetry instrumentation for Services, RequestContexts and ChangeSetContexts.
- [cds.java@2.0.0] The OpenTelemetry Context is propagated to child threads, when propagating the RequestContext.
- [cds.java@2.0.0] Added basic support for Spring AOT required for Spring Native Images.
- [cds.java@2.0.0] The archetype now supports creating projects using Java 20.
- [cds.java@2.0.0] The OData V4 adapter now supports using `$count` in `$expand` together with `$top` and `$skip`.
- [cds.java@2.0.0] The property `DraftIsProcessedByMe` is now calculated when requesting `DraftAdministrativeData`.
- [cds.java@2.0.0] Added support for using `Result` as POJO argument in `@After` event handlers of CRUD events.
- [cds.java@2.0.0] Writing tenant-specific audit logs to the AuditLog V2 service no longer requires the tenant subdomain to be known.
- [cds.java@2.0.0] Added a new configuration property `structured` to the messaging service configuration. If set to `true` it enforces a structured JSON Map-based representation of the message. Plain strings are transformed into a structured representation. Note that this might have an effect on the representation of the message in the broker. In addition setting this property enables handling of message headers (e.g. cloudevent headers) separately from the message itself on brokers that have a native representation for headers (e.g. Kafka). On incoming messages the flag determines the internal representation of the message either as a plain String or two Maps of message data and message headers.
- [cds.java@2.0.0] The dead-letter queue set in the Event Mesh or Message Queueing queue configuration is now automatically created, if not yet existing.
- [cds.java@1.34.1] Added support for replacing the `$namespace` placeholder in queue configuration values.
- [cds.java@1.34.0] A new starter module `cds-starter-k8s` has been introduced which bundles useful CAP dependencies for the Kubernetes/Kyma environment.
- [cds.java@1.34.0] The CDS Maven archetype now supports the `kubernetes` and `k8s` values as additional option in the `targetPlatform` parameter.
- [cds.java@1.34.0] Introduced hybrid IAS / XSUAA support based on `cds-feature-identity`. In hybrid mode the server accepts both IAS and XSUAA tokens. No automatic conversion between token types occurs. This mode is enabled, when both an IAS and XSUAA binding are present.
- [cds.java@1.34.0] Command main methods like `Deploy` or `Subscribe` no longer initialize adapters and background tasks like for example the draft GC, event subscriptions or persistent outbox processing.
- [cds.java@1.34.0] The tenant upgrade triggered through `DeploymentService.upgrade` now includes the tenant upgrade for multitenant Event Mesh services.
- [cds.java@1.34.0] The OData V4 adapter now supports open types.
- [cds.java@1.34.0] Writing tenant-specific audit logs to the AuditLog V2 service no longer requires the tenant subdomain to be known.
- [cds.java@1.34.0] Kafka service bindings using basic authentication are now supported.
- [cds4j@2.0.0] Calculated elements with a value expression with “on-read” semantics are supported
- [cds4j@2.0.0] Add constants `CQL.TRUE`, `CQL.FALSE` and `CQL.NULL`
- [cds4j@2.0.0] Suppress the execution of DB statements whose filter condition statically evaluates to `false`
- [cds4j@2.0.0] New `CqnExpand.inlineCount()` method to include the count of entries in the expand
- [cds@6.8.0] Global cds-dk version is now included in tabular output of `cds v -i`.
- [cds@6.8.0] Audit logging support for OAuth2 Plan
- [cds@6.8.0] Feature flag to limit the max number of requests in a Odata batch request. The max number can be specified with a number in `cds.odata.batch_limit`.
- [cds@6.8.0] Custom authentication in `enterprise-messaging`
- [cds@6.8.0] Requests with lambda expressions are rejected by remote services of kind `odata-v2`
- [cds@6.8.0] `cds build` ignores invalid entries in `undeploy.json`
- [cds@6.8.0] New `minorUnit` element in `sap.common.Currencies` for how many fractions the minor unit takes (e.g. `0`, or `2`). See https://www.npmjs.com/package/@sap/cds-common-content for matching content.
- [cds@6.8.0] Support for `$user. is null` and `$user. is not null` in `@restrict.where`. `is null` matches `null` and `[]`, `is not null` matches arrays with at least one entry as well as `!= null` if no array.
- [cds@6.8.0] Plugins are now also fetched from `devDependencies`, unless `NODE_ENV === 'production'`
- [cds@6.8.0] Plugins can now provide `cds` configurations in their package.json.
- [cds@6.8.0] Support in OData entities with special letters (like ó,â,ü) in names.
- [cds-mtxs@1.8.0] Token endpoint can now handle UAA binding with X.509 (mTLS) authentication. On CLI side, this requires @sap/cds-dk@>=6.8.0.

### Changed ​

- [cds-dk@6.8.2] `cds compile` to `openapi` now uses `@Common.Label` annotation to generate `x-sap-shortText`.
- [cds-dk@6.8.2] `cds import` now removes `x-` from elements in the `@AsyncAPI.Extensions` annotation while importing AsyncAPI documents.
- [cds-dk@6.8.2] `cds compile` to `openapi` now sorts the `tags` and `paths` in alphabetical order.
- [cds-dk@6.8.2] The livereload feature of `cds watch` can be disabled through `cds.livereload: false` in `package.json`.
- [cds-dk@6.8.0] `cds init` uses latest Maven Java archetype version 1.34.0 for creating Java projects.
- [vscode-cds@6.8.2] Changed default output directory for generated CDS types from `@types` to a `node_modules` subfolder
- [vscode-cds@6.8.1] CAP notebooks: improved Java cell example notebook
- [vscode-cds@6.8.0] Welcome page will be shown based on page's hash code
- [vscode-cds@6.8.0] CDS type generation will now be enabled by default
- [vscode-cds@6.8.0] Improved CAP Notebooks Welcome page (better layout, responsive icons, fixed buttons).
- [vscode-cds@6.8.0] Changing some CDS user settings required a manual restart of the IDE. This is no longer necessary
- [vscode-cds@6.8.0] Minimum VS Code version is now 1.76.0
- [cds.java@2.0.0] Java 17, Spring Boot 3 and Jakarta EE 10 are now required as minimum versions.
- [cds.java@2.0.0] The default value of property `cds.security.authentication.normalizeProviderTenant` is changed to `true`. With this change, the provider tenant is normalized and set to null in the UserInfo by default. If you have subscribed the provider tenant to your application you need to disable this feature.
- [cds.java@2.0.0] The `cds-services-archetype` now generates projects, which use JUnit 5 and include the `spring-boot-starter-test` dependency.
- [cds.java@2.0.0] Removed various deprecated classes and methods.
- [cds.java@2.0.0] Removed various deprecated configuration properties.
- [cds.java@1.34.0] Removed hybrid IAS / XSUAA support based on `cds-feature-xsuaa`, which exchanged incoming IAS tokens with XSUAA tokens. This mode is deprecated by XSUAA and will be removed.
- [cds.java@1.34.0] By default, undefined or empty attributes restrict expressions in where-conditions of instance-based authorization now. For instance, `$user.code = code` evaluates to `false` if the user attribute `code` is not defined or has no value. Note that XSUAA attributes with `valueRequired:true` (i.e. explicitly allowing unset attribute) might need model adaption such as `$user.code = code or $user.code is null'` to support unrestricted access.
- [cds.java@1.34.0] Activated the new faster serializer in OData V4 adapter by default (`cds.odatav4.serializer.enabled` set to `true`).
- [cds4j@2.0.0] Make `Value` type final. Changing the type of a value now returns a new (immutable) value or throws an exception
- [cds4j@2.0.0] Changed signature and default impl of `Modifier::param` to replace immutable params
- [cds4j@2.0.0] Add `null` values to the query result
- [cds4j@2.0.0] Result rows of Updates are not cleared anymore if no entity was updated, instead check the update count
- [cds4j@2.0.0] Removed deprecated `CqnModifier`
- [cds4j@2.0.0] Removed deprecated `CqnLimit` and `Limit` interfaces
- [cds4j@2.0.0] Removed deprecated `Modifier` methods: `expand(ref, items, orderBy, limit)`
- `in(Value value, Collection> list)`
- `selectListItem(Value value, String alias)`
- `limit(Limit limit)`

- [cds4j@2.0.0] Removed deprecated (positional) params from `CQL` and `CqnBuilder`
- [cds4j@2.0.0] Removed deprecated `Segment:accept` and `CqnVisitor:visit(segment)`
- [cds4j@2.0.0] Removed support for deprecated annotations `@Search.cascade`
- [cds4j@2.0.0] Removed deprecated Upsert strategy "replace" (cascading delete + deep insert)
- [cds4j@2.0.0] Removed deprecated `RefSegment`
- [cds4j@2.0.0] Removed deprecated Modifier `CompatibilityDefaults` and mutable refs
- [cds4j@2.0.0] Removed deprecated methods in `ResultBuilder`
- [cds4j@2.0.0] Removed deprecated `CqnXsert.Kind`
- [cds4j@2.0.0] Removed deprecated `ConstraintViolationException`
- [cds4j@2.0.0] Removed deprecated `Select::groupBy(Collection dimensions)`
- [cds4j@2.0.0] Removed deprecated `CdsAssociationType::keys`
- [cds4j@2.0.0] Removed deprecated `Source::getRoot`
- [cds4j@2.0.0] Removed deprecated `CqnParameter::getName`
- [cds4j@2.0.0] Removed deprecated `CqnSelectList::prefix`
- [cds4j@2.0.0] Removed deprecated `CqnSortSpecification::item`
- [cds4j@2.0.0] Removed deprecated `CqnSource::isQuery`, `CqnSource::asQuery`
- [cds4j@2.0.0] Removed deprecated `JDBCDataStoreConnector` constructors
- [cds4j@2.0.0] Removed deprecated `CqnSelectListItem::displayName` and `alias`
- [cds4j@2.0.0] Removed deprecated `CQL::literal`
- [cds4j@2.0.0] Removed deprecated `CdsStructuredType::isInlineDefined`
- [cds@6.8.0] Texts for Country are changed to Country/Region in `@sap.common.Countries`
- [cds@6.8.0] Resolved issue where selection strategies of destination options in multitenant applications were not working correctly, resulting in runtime errors. The fix relies on the `@sap-cloud-sdk/connectivity` npm package to be installed.
- [cds@6.8.0] Precision of timestamp used in outbox message increased to 100 nanoseconds (`YYYY-MM-DD hh:mm:ss.nnnnnnn`)
- [cds@6.8.0] When a draft is locked by another user, the error message now includes the username of that user
- [cap-js/graphql@0.5.0] Improved consistency of handling results of different types returned by custom handlers in CRUD resolvers: Wrap only objects (i.e. not primitive types or arrays) returned by custom handlers in arrays in create, read, and update resolvers
- Delete mutations return the length of an array that is returned by a `DELETE` custom handler or 1 if a single object is returned

- [cap-js/graphql@0.5.0] Don't generate fields for key elements in update input objects
- [cap-js/graphql@0.5.0] Update and delete mutations have mandatory `filter` argument
- [cap-js/graphql@0.5.0] Allow services that are not instances of `cds.ApplicationService`. It is expected that the invoker provides the correct set of service providers when directly using the GraphQL protocol adapter API.
- [cds-mtxs@1.8.0] `JobsService`: the job status will now remain `RUNNING` until all tenant tasks have succeeded or failed, instead moving to `FAILED` as soon as there's the first task failure.

### Fixed ​

- [cds-dk@6.8.2] `@sap/cds-dk` 6.8.2
- [cds-dk@6.8.2] `@sap/cds-mtxs` 1.8.2
- [cds-dk@6.8.2] `cds add mta` adds configuration `enterprise-messaging-shared` if necessary
- [cds-dk@6.8.1] `cds-ts watch` no longer fails with strange compilation errors if called in combination w/ `ts-node`
- [cds-dk@6.8.0] `cds-ts watch` now honors a `tsconfig.json` in the project
- [cds-dk@6.8.0] launch script for `CAP projects` in VS Code fixed
- [vscode-cds@6.8.2] Links on CAP Release Notes page are now pointing to correct locations in Capire.
- [vscode-cds@6.8.1] CAP notebooks: sample notebook `Shell` now uses a cross platform example
- [vscode-cds@6.8.1] CAP notebooks: shellscript syntax highlighting for `Shell` cell
- [vscode-cds@6.8.1] CAP notebooks: cells `CDS`, `Java` and `Javascript` now show error message if needed executable is not found
- [vscode-cds@6.8.1] Fix CAP Release Notes page
- [vscode-cds@6.8.1] `Report issues` url now points to correct SAP Answers location
- [vscode-cds@6.8.0] Where-used index could be incomplete with latest OData annotation plugin
- [vscode-cds@6.8.0] Formatting of quoted identifiers enclosed in square brackets
- [vscode-cds@6.8.0] Extension will no longer crash when using unknown compiler versions, though, compatibility is not guaranteed
- [cds.java@2.0.0] Fixed a bug, that caused a HTTP request to the MTX Sidecar during startup, if provider tenant normalization was enabled.
- [cds.java@2.0.0] Fixed a bug, that caused issues with generating the OData V4 nextLink URL, when the original URL had encoded `$` characters in query parameter names.
- [cds.java@1.34.1] Fixed a bug in instance-based authorization that caused misinterpretation of expressions with `is null` or `is not null`.
- [cds.java@1.34.0] Fixed a bug, causing the new OData V4 serializer to omit expanded properties in the result, which were not requested by the client.
- [cds.java@1.34.0] Fixed a bug, causing the persistent outbox to be used for the provider tenant, when the MT compatibility mode was disabled.
- [cds.java@1.34.0] Fixed a bug, causing `ClassCastException` when setting `cds.errors.extended` to true.
- [cds.java@1.34.0] Fixed a bug, causing warning logs, when activating the CDS actuator endpoint.
- [cds.java@1.34.0] Fixed a bug, causing `NullPointerException` when triggering tenant upgrades.
- [cds4j@2.0.0] The CQL clauses `search()` and `byId()` are supported in an EXISTS subquery
- [cds4j@1.38.1] Fix Update and Delete with path expression to target entity with aliased key elements
- [cds@6.8.2] EDMX texts for extended tenants based on `@sap/cds-mtx` now appear correctly again.
- [cds@6.8.2] `@assert.range` for DateTime/Date/Time/Timestamp
- [cds@6.8.2] Nested `$expand` OData query to the `texts` compiler-generated composition for entities with localized elements. For example, similar OData requests `Entity?$expand=items($expand=item($expand=texts))` now should work as expected.
- [cds@6.8.2] `req.subject` would occasionally be incorrect when a query had been executed prior to it.
- [cds@6.8.2] cds plugins are also fetched from `devDependencies`
- [cds@6.8.2] `cds build` now correctly resolves complex models of mtx extension projects
- [cds@6.8.1] DROP statements for SQLite and PostgreSQL no longer miss a comma at the end
- [cds@6.8.0] fix exported types of the `cds` core API
- [cds@6.8.0] cds build uses the correct path if no project dir is given
- [cds@6.8.0] Read after write for updates on to-one navigation
- [cds@6.8.0] Error in $orderBy in combination with @Core.MediaType property
- [cds@6.8.0] Fixes in lean-draft
- [cds@6.8.0] Fixed an issue where the combined `$search` and `$expand` query and localized data was returning empty results on SAP HANA
- [cds@6.8.0] Tests using `cds.test` no longer crash with a segmentation fault if `injectGlobals: false` is set in the Jest configuration.
- [cds@6.8.0] Handlers registered with `cds.on('shutdown')` are now called with an `err` argument in case the shutdown happened in response to uncaught exceptions or unhandled rejected Promises.
- [cds@6.8.0] Log output on uncaught exceptions or unhandled rejected Promises now is done via `cds.log` instead of `console`.
- [cds@6.8.0] New config option `cds.env.server.force_exit_timeout` allows to configure the timeout in ms after which we force-exit the server (default: 1111) if it didn't do so as expected after a prior `server.close()`. Values `false` or `0` disable force-exit.
- [cds@6.8.0] Require custom auth relative to project root when using pluggable middlewares
- [cap-js/graphql@0.5.0] Aligned `cds.Request` instantiation with other protocols for more consistent usage in custom handlers
- [cds-mtxs@1.8.2] Fix for asynchronous subscriptions with `lazyT0 = true`.
- [cds-mtxs@1.8.2] SAP HANA deployment now correctly evaluates the sql mapping configuration (e. g. `cds.data.sql_mapping.quoted`) also for deployment of `t0`.
- [cds-mtxs@1.8.1] MTXS Migration can now handle empty extension projects.
- [cds-mtxs@1.8.1] MTXS Migration can now handle extension projects with complex folder structure correctly.
- [cds-mtxs@1.8.1] The SaaS registry callback now supports X.509 authentication.
- [cds-mtxs@1.8.1] Sidecar is now using mocked authentication in development mode.
- [cds-mtxs@1.8.1] Fix for asynchronous subscriptions with `lazyT0 = true`.
- [cds-mtxs@1.8.0] MTXS Migration only deploys `cds.xt.Extensions` instead of the full application model.
- [odata-v2-adapter@1.10.5] Replace deprecated usage of `req.run` with `cds.run`
- [odata-v2-adapter@1.10.5] Update of `node-fetch`
- [odata-v2-adapter@1.10.5] Remove soon deprecated `req.getUriInfo`

## April 2023 ​

### Added ​

- [cds-dk@6.7.2] Added option `--skip-verification` to command `cds migrate`. It skips the extension verification to save memory. Requires `@sap/cds-mtxs@1.7.3`.
- [cds-compiler@3.9.0] Variables `$valid.from` and `$valid.to` have been added to the compiler. They behave the same as `$at.from` and `$at.to`.
- [cds-compiler@3.9.0] to.edm(x): Add `--odata-vocabularies` to pass a dictionary `{ : { Alias, Namespace, Uri } }` into the EDM generation. `` must match the value of `Alias`. Entries are ignored if they are incomplete, malformed, redefine an official OASIS/SAP vocabulary or match the name of the current service. Annotations of the form `@.` are added to the API without evaluation including an `edm:Reference`. It is in the users responsibility to provide a URI that a client can resolve against a valid vocabulary document.
- Support annotation `@open` on entity and structured type level to declare the corresponding entity/complex type to be `OpenType=true`. If an open structured type is declared closed (with a falsy annotation value), the corresponding EDM type is closed as well and suffixed with `_closed` (or `_open` vice versa). No further checks are performed on possibly open foreign or primary key types nor on eventually bucket elements to store the additional data.

- [cds4j@1.38.0] Support list values (tuples) in comparisons
- [cds4j@1.38.0] Ignore dynamic properties of `@open` entities on insert/update
- [cds4j@1.38.0] Add `CQL.copy` for `CqnElementRef` and `CqnStructuredTypeRef` returning a ref builder
- [cds4j@1.38.0] Allow to compare list values in predicates, e.g. `(amount, currency) = (100, 'EURO')`
- [cds4j@1.38.0] SQLite: use user-defined `session_context` function for localized/temporal data
- [ux-cds-odata-language-server-extension@1.9.4] The Show All References option for service elements such as entities, properties, and actions displays now also the references to these elements in annotation values. You can use it before modifying a service element to understand if annotations will be affected by the change and avoid the related errors or easily fix them.
- [odata-v2-adapter@1.10.1] Bootstrapping via CDS plugin (`cds.cov2ap.plugin: true`)
- [odata-v2-adapter@1.10.0] Transition to open source code

### Changed ​

- [cds-dk@6.7.1] `cds init` uses latest Maven Java archetype version 1.33.1 for creating Java projects.
- [cds-dk@6.7.1] Bump `@sap/cds` to 6.7.1
- [cds-dk@6.7.1] Bump `@sap/cds-mtxs` to 1.7.2
- [cds-compiler@3.9.0] compiler: Parameter references in filters such as `assoc[field - [cds-compiler@3.9.0] to.edm(x): Fix spec requirement: "Navigation properties of complex types MUST NOT specify a partner".
- Set default target cardinality for unspecified `composition of {}` to `[0..1]`.
- Correct referential constraint calculation for `[0..1]` backlink associations.

- [cds-compiler@3.9.0] for.hana/for.odata: Reject final unmanaged assoc path step in ON Condition if preceded with `$self`.
- [cds-compiler@3.9.0] to.cdl: Parentheses around expressions containing conditions were sometimes missing.
- [cds-compiler@3.9.0] to.sql/hdi/hdbcds: Detect and process calculated elements in functions like `upper`.
- Better detection of calculated elements in `.expand`/`.inline`.
- Entities with calculated elements sometimes had incorrect types. This happened, for example, if they were marked with `@odata.draft.enabled`

- [cds.java@1.33.1] Fixed a bug, causing the upgrade procedures to fail, if MTX Sidecar reported tenant status as `NON-EXISTENT` for one or more tenants.
- [cds.java@1.33.1] Fixed a bug, causing the upgrade procedures to succeed, even if MTX Sidecar reported the job status as `FAILED`, when using MTXS.
- [cds.java@1.33.1] Fixed a bug, causing OData V2 `Edm.Time` typed values in URIs represented as durations (e.g. `PT10H10M20S`) to fail request parsing.
- [cds4j@1.38.0] Change return type of `Modifier:selectAll` to `List`
- [cds4j@1.37.1] Fix parsing of CQN containing "is not"
- [cds@6.7.2] Try to destroy nonexistant socket in case of custom streaming implementation
- [cds@6.7.2] Draft: Missing field `IsActiveEntity` in target path of error messages during `draftActivate`
- [cds@6.7.2] Minor fixes for `cds.fiori.lean_draft`
- [cds@6.7.2] Error in media type check when no `Content-Type` header is found
- [cds@6.7.1] cds build error CreateListFromArrayLike
- [cds@6.7.1] Disabling of arbitrary user config in mock auth config using `"users": { "*": false }`
- [cds@6.7.1] Various fixes for `cds.fiori.lean_draft`
- [cds@6.7.1] User attributes that look like numbers are quoted in SQL clause for `@restrict`
- [cds-mtxs@1.7.2] MTXS Migration now handles multiple generated projects correctly.
- [cds-mtxs@1.7.2] Extensibility Service now contains action `add` for extension modification.
- [cds-mtxs@1.7.2] Model Provider Service now offer action `getExtResources` returning the archive of the uploaded extension.
- [cds-mtxs@1.7.2] CSV files provided in extensions are now correctly re-deployed again with `upgrade`.
- [cds-mtxs@1.7.1] MTXS Migration now behaves more robust with regards to cds build configurations.
- [cds-mtxs@1.7.1] Re-subscribe now also re-deploys extensions again.
- [cds-mtxs@1.7.1] Stability improvements for tenant upgrades.
- [odata-v2-adapter@1.10.4] Fix start of `cds.plugin`
- [odata-v2-adapter@1.10.3] Fix access to `undefined` element during data conversion
- [odata-v2-adapter@1.10.2] Convert array structures
- [odata-v2-adapter@1.10.1] Update `xml2js` dependency to fix security vulnerability
- [odata-v2-adapter@1.10.0] Bound entity operation result is correctly nested with entity name prefix

## March 2023 ​

### Added ​

- [cds-dk@6.6.1] `cds compile --to openapi` now adds extension validation keywords `x-sap-precision` and `x-sap-scale` for decimal values.
- [vscode-cds@6.6.0] CAP notebooks: Uri handler to open notebooks coming from Capire in local VS Code workspaces.
- [vscode-cds@6.6.0] CAP notebooks: All notebook features now have a brief description with examples, available on the CAP Notebooks Welcome page.
- [vscode-cds@6.6.0] type generation now detects project root
- [cds.java@1.32.1] New POJO interfaces `SaasRegistryUnsubscriptionOptions` and `SaasRegistrySubscriptionOptions` that help to access (un)subscription SaaS Registry payload in type-safe manner, e.g. `SaasRegistrySubscriptionOptions options = Struct.access(subscriptionEventContext.getOptions()).as(SaasRegistrySubscriptionOptions.class);`.
- [cds@6.6.1] `cds.xt.TENANT_UPDATED` event is emitted once a tenant was extended
- [cds-dk@6.7.0] `cds upgrade` enables upgrading a tenant subscribed to a multitenant SaaS app to the latest base model.
- [cds-compiler@3.8.0] compiler:Table aliases for sub-queries are no longer required.
- A time zone designator can now be used in time literals, e.g. `time'16:41:01+01:30'`or `time'16:41:01Z'`.

- [cds-compiler@3.8.0] Calculated elements ("on-read") are now enabled per default. When used in views, they are replaced by their value, for example:cds

```
entity E { one: Integer; two = one + 1; };
entity P as projection on E { two };
// P is the same as:
entity P as projection on E { one + 1 as two };
```

This allows to define calculations centrally at the entity, which can be used by other views.
- [cds-compiler@3.8.0] In CDL, a ternary operator was added as a shortcut for `CASE` expressions: `a ? b : c` is a shortcut for `CASE WHEN a THEN b ELSE c END`. There is no CSN representation. The ternary operator is rendered as a `CASE` expression in CSN.
- [cds-compiler@3.8.0] In CDL and CSN, `not null` can now also be used in type definitions.
- [cds-compiler@3.8.0] In CDL (and CSN as before), elements can be defined without specifying a type.
- [cds.java@1.33.0] The `TenantProviderService` now provides, as part of the `TenantInfo` class, the id of the database on which a specific tenant has been onboarded (e.g. `tenantInfo.get("database_id");`). If the information is not available, the call will return `null`.
- [cds.java@1.33.0] Audit Log integration now supports writing entries on behalf of a named user when the CAP application is using IAS instead of XSUAA.
- [cds.java@1.33.0] Two new main methods `com.sap.cds.framework.spring.utils.Subscribe` and `com.sap.cds.framework.spring.utils.Unsubscribe` allow triggering subscriptions or unsubscriptions as tasks.
- [cds@6.7.0] Config `cds.ql.quirks_mode` as a compatibility flag to still support behaviours which are undocumented, or even against the specifications, for example CQN:js

```
let q = INSERT.into('Books')
//> According to CQN spec should return:
{SELECT:{from:{ref:['Books']}}}
//> But today returns:
{SELECT:{from:'Books'}}
```

The default in cds6 is `true` → to be changed to `false` with cds7.
- [cds@6.7.0] `cds build` now checks extension point restrictions defined by the SaaS app provider. `cds build` fails if any restrictions are violated.
- [cds@6.7.0] Typings for `cds.spawn()`
- [cds@6.7.0] Typings for `entity.drafts`
- [cds@6.7.0] Typings for winston logger
- [cds@6.7.0] Typings for `service.on`, `service.before`, and `service.after` for actions and CRUD events
- [cds@6.7.0] CLI command `cds env` now allows property paths with `/` instead of `.`, which allows usages like that:

sh

```
cds env requires/cds.xt.ModelProviderService
```

- [cds@6.7.0] `cds.env` now allows to statically set/add profiles via `cds.profile` and `cds.profiles` in package.json.
- [cds@6.7.0] `cds.env` now also supports using profiles in definitions of presets, i.e., in `cds.requires.kinds`.
- [cds@6.7.0] `cds deploy` now prints a warning when using Cloud Foundry client version less than 8.
- [cds@6.7.0] `req.subject` to conveniently operate on the subjects targeted by the request. Example usage: SELECT.one.from(req.subject) //> returns single SELECT.from(req.subject) //> returns array UPDATE(req.subject) //> updates one or many DELETE(req.subject) //> deletes one or many
- [cds@6.7.0] `cds-serve` as a future replacement for `cds serve` in npm scripts. Applications can adopt this now to ease the transition to the next major version.
- [cap-js/graphql@0.4.0] Supporting new `cds-plugin` technique for zero configuration
- [cap-js/graphql@0.4.0] Support for filtering by `null` values
- [cap-js/graphql@0.4.0] Allow multiple filters on the same field, with the same operator, that are logically joined by `AND`. For example, filtering for all books with titles that contain both strings, "Wuthering" and "Heights":graphql

```
{
  AdminService {
    Books(filter: { title: { contains: ["Wuthering", "Heights"] } }) {
      nodes {
        title
      }
    }
  }
}
```

### Changed ​

- [vscode-cds@6.6.0] extension now uses vscode-languageclient 8.x API consumers may need to adapt access. See changes. Especially `onReady` is no longer needed and was removed.

- [vscode-cds@6.6.0] minimum VS Code version is now 1.74.0
- [vscode-cds@6.6.0] updated capire CDL docs - used in code completion details
- [cds.java@1.32.1] Support for OData V4 PATCH requests with deltas on entity collections has to be enabled via `@Capabilities.UpdateRestrictions.DeltaUpdateSupported:true`.
- [cds.java@1.32.1] Adapted `DeploymentService.dependencies()` and `DependenciesEventContext` to return and use `List>` instead of `List` for dependencies. Use helper class `SaasRegistryDependency` to report dependencies to SaaS Registry.
- [cds-dk@6.7.0] `cds env --for` is now used to specify profiles; before it specified project paths, but never worked correctly.
- [cds-dk@6.7.0] `cds add data` now uses comma as CSV separator by default instead of semicolon. This allows using GitHub tabular display.
- [cds-dk@6.7.0] `cds add approuter` doesn't create entries for `authenticationMethod` and `authenticationType` any more, but uses the equivalent `@sap/approuter` defaults.
- [cds-dk@6.7.0] `cds add multitenancy` will now create a sidecar MTX project for Node.js as well.
- [cds-dk@6.7.0] `cds subscribe` and `cds unsubscribe` no longer require a username in case @sap/cds-mtxs is configured with dummy auth.
- [cds-dk@6.7.0] `cds subscribe` and `cds unsubscribe` now rely on @sap/cds-mtxs (version 1.7.0 or higher).
- [cds-compiler@3.8.0] API: We now report an error for most backends, if the input CSN has `meta.flavor == 'xtended'`, because only client/inferred CSN is supported.
- [cds-compiler@3.8.0] Update OData vocabularies 'PersonalData', 'UI'
- [cds-compiler@3.8.0] for.odata: Shortcut annotations `@label`, `@title`, `@description`, `@readonly` are no longer removed from the OData processed CSN.
- [cds-compiler@3.8.0] to.cdl: Annotation arrays are split into multiple lines, if a single line would be too long.
- Nested `SELECT`s are put into separate lines to make them more readable.
- (Annotation) paths are quoted less often.

- [cds-compiler@3.8.0] to.sql: The list of reserved SAP HANA identifiers was updated (for smart quoting).
- [cds.java@1.33.0] If execution of a `RequestContext` is dispatched to a different thread, the correlation id of the parent thread is propagated to the new thread even if the receiving thread already has a correlation id set in its Mapped Diagnostic Context (MDC). The original correlation id will be restored once the execution of the `RequestContext` is completed. Previously, this led to an `ErrorStatusException`.
- [cds.java@1.33.0] The implicit sorting feature does not add any sort specifications to the statement anymore, if only constant literals are on the select list.
- [cds.java@1.33.0] The `DeploymentService` API no longer validates the subscription and deployment scope. The scopes are now only validated on incoming HTTP requests (e.g. SaaS Registry subscription), that trigger the `DeploymentService` API internally. This enables using the `DeploymentService` API without wrapping the call in a privileged user `RequestContext`. In case the `MtSubscriptionService` compatibility mode is used, the scopes are still enforced when using the API.
- [cds.java@1.33.0] Moved properties `cds.dataSource.csv*` into a new `cds.dataSource.csv.*` section. The previous properties are still supported for backwards compatibility.
- [cds.java@1.33.0] Replaced `cds.multiTenancy.healthcheck.intervalMillis` with a Duration-based property `cds.multiTenancy.healthcheck.interval`. The previous property is still supported for backwards compatibility.
- [cds.java@1.33.0] Removed the Instance Manager support from the codebase, as the service is deprovisioned.
- [cds4j@1.37.0] Replace IsActiveEntity on active entities with `TRUE` in `WHERE`, `ORDER BY` and source ref
- [cds4j@1.37.0] Reflection API: Improve warning on unsupported view definitions
- [cds@6.7.0] `cds.log().trace()` now logs stack traces in `DEBUG` level, before that was on `TRACE`/`SILLY` level only
- [cds@6.7.0] Plain SQL queries now have `req.event === undefined`, formerly this had non-deterministic values.
- [cds@6.7.0] Plain SQL queries don't allow to register custom handlers, other than for event `'*'`.
- [cds@6.7.0] Plain SQL queries are only supported on database services, not on application services.
- [cds@6.7.0] CQN representation of `columns=*` is not allowed anymore, instead `columns=['*']` should be used. This also applies to expand.
- [cds@6.7.0] Only draft roots can be created via direct, non-navigation OData `POST` requests.
- [cds@6.7.0] Flag `cds.features.fiori_preview` changed to `cds.fiori.preview`. The old flag still works as well.
- [cds@6.7.0] Flag `cds.features.fiori_routes` changed to `cds.fiori.routes`. The old flag still works as well.
- [cds-mtxs@1.7.0] Filter duplicate linter messages based on new LinterMessage API.
- [cds-mtxs@1.7.0] cds-mtx script now logs reasons for missing MTXS environment.
- [cds-mtxs@1.7.0] `DeploymentService` plugin handlers are now registered on `serving:cds.xt.DeploymentService`.
- [cap-js/graphql@0.4.0] Improved handling of `null` and `undefined` values in query arguments
- [cap-js/graphql@0.4.0] Empty filter lists resolve to `false` and empty filter objects resolve to `true`

### Fixed ​

- [cds-dk@6.6.1] `cds add helm` fixed html5 cloud service is now read properly.
- [cds-dk@6.6.1] `cds import` now flattens the `@Capabilities` annotation in the CSN for OData V4 files.
- [cds-dk@6.6.1] `cds import` for OData V4 files now captures the `EnumTypes` information in the CSN according to `UnderlyingType`.
- [cds-dk@6.6.1] `cds import` now captures the `@Common.Text` annotation value properly in the CSN for OData V4 files.
- [cds-dk@6.6.1] `cds init --add java` now uses local Java version when creating new Java project.
- [cds-dk@6.6.1] `cds watch` terminates properly in case livereload websocket clients are connected
- [cds-dk@6.6.1] `cds watch`'s livereload feature works again on Node.js >= 17, where local IPv6 addresses are the default (`::1` instead of `127.0.0.1`)
- [vscode-cds@6.6.0] highlighting of the last of a number of element names in a projection
- [vscode-cds@6.6.0] formatting of query `from A:B`: removed colon padding
- [vscode-cds@6.6.0] type generation stopped working after failure until next LSP restart
- [cds.java@1.32.1] Fixed a bug causing system query option `$skip` to be applied on all pages returned when server-driven pagination is used and the configuration option `cds.query.limit.reliable-paging.enabled` is set to `true`. Now the query option `$skip` is applied only on the first page of the results.
- [cds.java@1.32.1] Fixed a bug causing a `NullPointerException` to be thrown when the `Deploy` method is executed when an application is deployed and there are no tenants available. The database upgrade will be skipped with an info message.
- [cds@6.6.1] `TypeError` when using the query API with an unknown target in x4 flavor
- [cds@6.6.1] The setting for `cds.requires['cds.xt.DeploymentService'].lazyT0` is now recognized in the VS Code schema validation.
- [cds@6.6.1] The HDI deployment `stdout` logs are now only visible for `DEBUG` level if triggered via `cds-mtxs`. They are also streamed to `logs/.log` in case you need the full deployment output, even without `DEBUG` enabled.
- [cds@6.6.1] `.forUpdate` when used for etags
- [cds@6.6.1] Prevent `TypeError` if an existing draft does not have admin data
- [cds@6.6.1] Outbound-streaming error handling
- [cds-mtxs@1.6.3] `t0` model DDL files do not end up in application build results any more.
- [cds-mtxs@1.6.3] `cds.xt.SaasProvisioningService`: fixed an error for programmatic usage when sending the callback.
- [cds-mtxs@1.6.3] `cds-mtx` commands now properly exit with code != 1 when receiving an error from the `DeploymentService`.
- [cds-mtxs@1.6.2] Robustness of MTX Migration has been improved.
- [cds-mtxs@1.6.1] The lazily onboarded `t0` will now implicitly be created with the same onboarding parameters (e.g. database ID) as the first onboarded tenant.
- [odata-v2-adapter@1.9.20] Cache invalidation for Streamlined MTX (extensibility enabled) with CDS 6.6.1
- [odata-v2-adapter@1.9.20] Use named parameters for mtxs actions to protect against incompatible changes
- [odata-v2-adapter@1.9.20] Allow status code 304 (not modified) when reading OData V4 metadata (as success)
- [cds-dk@6.7.0] `cds watch`'s livereload feature may now use a local IPv6 address (`::1`) instead of always `localhost`. This is usually the case on Node.js 17 or higher.
- [cds-dk@6.7.0] In all but `cds compile` errors where not handled correctly, especially compiler errors not displayed in human readable format.
- [cds-dk@6.7.0] `cds init` creates project sample files correctly.
- [cds-dk@6.7.0] CLI commands w/ unknown arguments (`cds --foo`) clearly fail again with a proper error message
- [cds-dk@6.7.0] Reduce console output in case of multitenancy-related command failures.
- [cds-dk@6.6.2] Bump `sqlite3` to 5.1.6
- [cds-dk@6.6.2] Bump `@sap/cds` to 6.2.2
- [cds-dk@6.6.2] `cds init` creates project sample files correctly.
- [cds-compiler@3.8.2] parser: Identifiers that are keywords were not allowed in annotation values inside arrays
- [cds-compiler@3.8.2] compiler: Compatibility against cds-lsp was restored.
- [cds-compiler@3.8.2] to.sql/hdbcds/hdi/edm(x): Fix a crash for sub-queries inside nested expressions of on-conditions of JOINs.
- [cds-compiler@3.8.0] The CSN parser now accepts bare `list`s in `columns[]`, similar to the CDL parser.
- [cds-compiler@3.8.0] to.cdl: Delimited identifiers in filters are now surrounded by spaces if necessary, to avoid `]]` being interpreted as an escaped bracket.

- [cds-compiler@3.8.0] to.edm(x): Remove empty `Edm.EntityContainer` again. Removal of an empty entity container has been revoked with version 3.5.0 which was wrong. An empty container must not be rendered as it is not spec compliant.
- Correctly resolve chained enum symbols.
- Fix a program abort during structured rendering in combination with `--odata-foreign-keys` and foreign keys in structured types.
- Correctly render paths to nested foreign keys as primary key in structured mode with `--odata-foreign-keys`.

- [cds-compiler@3.8.0] to.hdi/to.sql/to.edm(x): Reject unmanaged associations as ON-condition path end points.
- Fix bug in message rendering for tuple expansion.
- Correctly detect invalid @sql.append/prepend in projections.

- [cds-compiler@3.8.0] to.hdi/to.sql: The list of SAP HANA keywords was updated to the latest version.
- [cds.java@1.33.0] Fixed a bug, causing exceptions while performing Event Mesh initialization during initial onboarding of a new tenant.
- [cds.java@1.33.0] Fixed a bug, causing `@assert.target` to fail with lock exceptions when used on an association to a draft-enabled entity.
- [cds.java@1.33.0] Fixed a bug, causing failed subscriptions, because no application URL was provided to SaaS Registry.
- [cds@6.7.0] Specifying a key in `SELECT.from(...)` is now typed to produce a single result, instead of an array of results
- [cds@6.7.0] Proper handling of `IsActiveEntity` in error paths
- [cds@6.7.0] For cloudevents using AMQP, the type is set to `application/cloudevents+json`
- [cds@6.7.0] Use `message` property in typings.
- [cds@6.7.0] Typings for `cds.on('bootstrap', app => {app.use(...)`
- [cds@6.7.0] Return types for `User` and `delete` in typescript
- [cds@6.7.0] Typings for connect options
- [cds@6.7.0] Typings for `req.error`
- [cds@6.7.0] Deployment in sidecar
- [cds@6.7.0] Error with restricting an entity and request it with $apply in combination with aggregate
- [cds@6.7.0] Combined usage of `$skiptoken` and `$skip`
- [cds@6.7.0] Error `package.json file is missing` in mtx extension builds
- [cds@6.7.0] CLI commands w/ unknown arguments (`cds --foo`) clearly fail again with a proper error message
- [cds@6.6.2] Exception during `cds deploy` without mtx
- [cds@6.6.2] Service name specified with `cds deploy --to hana:serviceName` takes precedence over environment variables.
- [cds-mtxs@1.7.0] HANA deployment now correctly evaluates the sql mapping configuration (e. g. `cds.data.sql_mappging.quoted`)
- [cap-js/graphql@0.4.1] `cds-plugin.js` was missing in `files` property of `package.json`
- [cap-js/graphql@0.4.0] Handling of GraphQL queries that are sent via `GET` requests using the `query` URL parameter if GraphiQL is enabled
- [odata-v2-adapter@1.9.21] Proxy is open source at https://github.com/cap-js-community/odata-v2-adapter
- [odata-v2-adapter@1.9.21] The new proxy library is fully compatible and can be used as drop-in replacement
- [odata-v2-adapter@1.9.21] This library is now deprecated and will no longer receive

### Removed ​

- [cds-compiler@3.8.0] for.odata: Undocumented shortcut annotation `@important` has been removed.

## February 2023 ​

### Added ​

- [cds-dk@6.6.0] `cds compile` added a new target format `asyncapi` to convert CDS models to AsyncAPI documents.
- [cds-dk@6.6.0] `cds pull` now hints at base-model name for `using` statement.
- [vscode-cds@6.5.1] The special `up_` element is now supported in navigation
- [cds-compiler@3.7.0] Several `annotate` statement can append/prepend values to the same array-valued annotation without an `anno-duplicate` error, even if there is no `using from` dependency between the involved sources
- [cds-compiler@3.7.0] SQL methods such as `point.ST_X()` can be used in views.
- [cds-compiler@3.7.0] The SQL `new` keyword can be used for `ST_*` types such as `new ST_POINT('Point(0.5 0.5)') )`
- [cds.java@1.32.0] Introduced a new API for managing subscriptions, unsubscriptions and tenant upgrades. It is leaner and it is easier to integrate custom handlers, as the API doesn't distinguish between synchronous and asynchronous operations any more.
- [cds.java@1.32.0] The `cds` actuator endpoint now includes datasource pool statistics.
- [cds.java@1.32.0] The CAP Java Maven archetype allows to choose the target JDK version with the new parameter `jdkVersion`. The default version is `17`, supported values are `11` and `17`.
- [cds.java@1.32.0] The new OData V4 serializer now supports a new mode in which it buffers the response before streaming it to the client. This can be enabled in case serialization errors after streaming to the client has already started must be avoided. To enable it set `cds.odataV4.serializer.buffered` to `true`.
- [cds.java@1.32.0] OData V4 adapter now supports PATCH requests with deltas on entity collections (Beta)
- [cds4j@1.36.0] Deduplicate inline defined simple types in CDS models
- [cds4j@1.36.0] `CQL.refSegment(id, filter)` to construct segments with filters
- [cds@6.6.0] Improved error handling for `cds build` if the SaaS base model is missing in an extension project.
- [cds@6.6.0] Support for reliable paging using `$skiptoken`. Can be activated via `cds.query.limit.reliablePaging = true`
- [cds-mtxs@1.6.0] `t0` onboarding can now happen lazily before the first subscription by setting `cds.requires.['cds.xt.DeploymentService'].lazyT0`.
- [cds-mtxs@1.6.0] E-Tag handling for the `getCsn` API in sidecar scenarios has been introduced.
- [cds-mtxs@1.5.1] Jobs are now cleaned up in the database after configurable cutoff times. The following options are possible: `jobCleanupInterval`: Frequency in milliseconds for cleaning up finished or failed jobs. Default is 1 day.
- `jobCleanupAge`: Time in milliseconds for the minimum age of the failed or finished jobs to delete. Default is 1 day.
- `jobCleanupIntervalStale`: Frequency in milliseconds for cleaning up queued or running jobs. Default is 7 days.
- `jobCleanupAgeStale`: Time in milliseconds for the minimum age of the queued or running jobs to delete. Default is 7 days.

- [cds-mtxs@1.5.1] MTXS migration script now allows to cleanup @sap/mtx metadata containers.

### Changed ​

- [cds-dk@6.6.0] `cds env` now allows inspecting entries with optional `get` command. E.g. `cds env requires.db`.
- [cds-dk@6.6.0] `cds add multitenancy` now uses async SaaS Provisioning Service onboarding by default.
- [cds-dk@6.6.0] `cds add multitenancy` for Java will now add `sqlite3` to `devDependencies` in the sidecar `package.json`.
- [cds-dk@6.6.0] `cds add extensibility` now works for Java projects out of the box.
- [cds-dk@6.6.0] `cds import` now captures the Edm Primitive types without CDS mapping with annotation `@odata.Type` and marks the type as `cds.String`.
- [cds-dk@6.6.0] `cds add helm` connectivity service instance is no longer created.
- [cds-dk@6.6.0] `cds init` uses latest Maven Java archetype version 1.32.0 for creating Java projects.
- [cds-dk@6.5.2] New versions of `@sap/cds-mtxs` and `@sap/cds-compiler`
- [cds-dk@6.5.2] `cds init` uses latest Maven Java archetype version 1.31.1 for creating Java projects.
- [cds-dk@6.5.1] `cds init` uses latest Maven Java archetype version 1.31.0 for creating Java projects.
- [eslint-plugin-cds@2.6.3] Filter rule reports using inferred models on $location.
- [eslint-plugin-cds@2.6.2] Fixed rule reports using inferred models to always receive valid file $locations.
- [vscode-cds@6.5.1] `mixin` is now mapped to `LSP.SymbolKind.Operator` (was default `String`)
- [vscode-cds@6.5.1] a commit hash of the last commit is now included in release under dist/state
- [vscode-cds@6.5.1] target platform back to `es2020`
- [cds-compiler@3.7.0] Update OData vocabularies 'Common', 'Core', 'Measures', 'PDF', 'UI'.
- [cds-compiler@3.7.0] to.edm(x): Empty complex types are no longer warned about as they are allowed.
- [cds.java@1.32.0] The old `MtSubscriptionService` API has been deprecated in favour of the new `DeploymentService` API. Event handlers on the `MtSubscriptionService` API are continued to be triggered in a compatibility mode (enabled by default). Migration to the new API is encouraged.
- [cds.java@1.32.0] The HTTP-based deploy endpoints are deprecated and not supported with the new `DeploymentService` API. In case of enabled compatibility mode the HTTP-based deploy endpoints are still available. Migration to the Java `main`-task based deployment is encouraged.
- [cds.java@1.32.0] Programmatic setting of the App UI URL has been deprecated. In case of enabled compatibility mode it is still possible through the old `MtSubscriptionService`-based APIs. Consider migrating to the property-based setting of the application URL.
- [cds4j@1.36.0] Annotations on elements with inline-defined simple type are not repeated on the type
- [cds4j@1.36.0] Deprecate setters `RefSegment:id` and `RefSegment:filter`, instead use `CQL.refSegment(id, filter)`
- [cds4j@1.36.0] Optimized to-many expands are now also executed by path (join/subquery) if only a single root entity is selected
- [cds@6.6.0] `cds.serve(ServiceName)` (and `cds serve -s ServiceName`) now exactly serve services with the given names. Previously, all services that ended with the given name were served as well, e.g. `MyServiceName` and `ServiceName`, which might be problematic for applications that bootstrap services one by one.
- [cds@6.6.0] Optimize `@cds.persistence.journal` filtering for `last-dev` CSN file.
- [cap-js/graphql@0.3.0] Replaced deprecated GraphQL HTTP server `express-graphql` with `graphql-http`
- [cap-js/graphql@0.3.0] Serve GraphiQL 2 via included HTML instead of relying on the server framework (`express-graphql` included GraphiQL 1)
- [cap-js/graphql@0.3.0] Bump `graphql` version to 16
- [cap-js/graphql@0.3.0] Execute query resolvers in parallel and mutation resolvers serially
- [cds-mtxs@1.5.1] `/-/cds/saas-provisioning/tenant`: consumers using the `mtx_status_callback` don't need a SaaS registry binding to the application any more.

### Fixed ​

- [cds-dk@6.6.0] `cds unsubscribe --from` flag now recognized
- [cds-dk@6.6.0] `cds import` now adds `cds.Boolean` as dummy return type if `ReturnType` for `FunctionImport` is missing in the OData V2 edmx.
- [cds-dk@6.6.0] `cds import` resolves the `$Cast` construct in the CSN for OData V4 files.
- [cds-dk@6.6.0] `cds lint` now reports like ESLint in case of missing plugin `@sap/eslint-plugin-cds`
- [cds-dk@6.5.2] `cds migrate` no longer fails because of authorization error
- [cds-dk@6.5.1] `cds deploy` no longer fails to write to a `package.json` file that has no `cds` section
- [vscode-cds@6.5.1] Closing a CDS file led to 'forgetting' the content in the index. This resulted in: `workspace/symbols` not showing all definitions
- error messages of symbols not found
- navigation broken for 'closed' definitions

- [vscode-cds@6.5.1] formatting and highlighting of nested element and enum extensions
- [vscode-cds@6.5.1] code completion for keywords and identifiers may have used wrong compiler messages, thus not working as expected
- [cds-compiler@3.7.2] CSN parser: Structured annotations containing `=` were accidentally interpreted as expressions, even though the corresponding beta flag was not set.
- [cds-compiler@3.7.0] `parse.cql` and `parse.expr` no longer ignore type arguments such as `cast(field as String(12))`. One argument is interpreted as `length` and two are interpreted as `precision` and `scale`, similar to how custom types and their arguments are interpreted.
- [cds-compiler@3.7.0] Previously, the compiler could not always find a unique redirection target if there were one direct projection on the model target and two or more projections on that projection.
- [cds-compiler@3.7.0] The performance of compiler-checks for deeply nested expressions/queries has been improved
- [cds-compiler@3.7.0] Fix various bugs in Association to Join translation: Recursive `$self` dereferencing
- Correct resolution of table alias in non-bijective `$self` backlink associations in combination with explicit redirection.

- [cds-compiler@3.7.0] to.edm(x): Process value help list convenience annotations on unbound action parameters.
- [cds-compiler@3.6.2] to.hdi(.migration): Don't render `-- generated by cds-compiler version` comment at the top of the HDI-based artifacts, as this caused HDI to detect the file as `changed` and redeploy, causing way longer deployment times. Old behavior can be enabled with option `generatedByComment: true`.
- [cds-compiler@3.6.2] to.sql/hdi/hdbcds: Correctly handle variables like `$user` in `exists` filters.
- [cds.java@1.32.0] Fixed a bug causing uncommitted transactions in case different PersistenceServices were used in an `@Transactional`-annotated method, outside of any `ChangeSetContext`. This scenario is currently not supported and now causes an exception to be thrown.
- [cds.java@1.32.0] Fixed a bug causing incorrectly handled URIs in case a combined service and entity path (e.g. `/v1/FooEntity`) was a substring of a service path (e.g. `/v1/Foo`).
- [cds.java@1.32.0] Bumped version of the `jacaco-maven-plugin` in the integration-tests module of a newly created CAP Java project to a version that is compatible with JDK 17.
- [cds.java@1.31.1] OData V4 responses with entities containing stream properties, now indicate if the stream property is set by providing the `property@odata.mediaContentType` annotation.
- [cds4j@1.36.0] Virtual elements of the entity annotated with `@cds.search` or `@Search.defaultSearchElement` are no longer searched
- [cds4j@1.35.1] Fix `equals` and `hashCode` of `CdsData` and `Row` to be equal to `Map:equals` / `Map:hashCode`
- [cds4j@1.35.1] Fix `orderBy` in optimized to-one-to-many expands
- [cds4j@1.35.1] Connect multiple `or` and `and` predicates with shallower tree/call stack
- [cds4j@1.35.1] Prevent unique constraint violations on concurrent deep upserts with full-set payload
- [cds4j@1.35.1] null values are treated as `CqnBoolLiteral.TRUE` in `Conjunction`, `Disjunction` and `Negation`.
- [cds@6.6.0] `cds deploy --to hana` no longer calls `cds bind` when `VCAP_SERVICES` is provided, e.g via `default-env.json`.
- [cds@6.6.0] `$search` on an entity without String elements
- [cds@6.6.0] Only elements from type `cds.String` are searchable when combining `$apply` and `$search`
- [cds@6.6.0] Error message for missing database connection in draft case
- [cds@6.6.0] Extensibility with in-memory Sqlite
- [cds@6.6.0] OData adapter error messages
- [cds@6.6.0] Columns in navigation path are now added to the SELECT.columns in new parser
- [cds@6.6.0] Application service calls on draft enabled entities using aliases
- [cds@6.6.0] Custom mtxs build tasks now use the correct default `src` folder value.
- [cds@6.6.0] `cds build` adds a `.hdiconfig` file when creating HANA migration tables if none is existing.
- [cds@6.6.0] UPSERTs using reserved keywords
- [cds@6.6.0] Fix outbound-streaming error handling
- [cds@6.6.0] Rollback transaction if inbound streaming fails
- [cds@6.6.0] Custom database initialization in `db/init.js` now skips the `t0` tenant for multitenant apps.
- [cds@6.6.0] Concurrent etag calculation for UPDATE and DELETE
- [cds@6.6.0] Typings for `cds.delete()`
- [cds@6.6.0] CQN for `not` operator with OData functions
- [cds@6.6.0] Expand on composition of aspect for draft enabled entities
- [cds@6.6.0] Better error messages are provided for errors with HTTP status code `400`, `500` and `501`
- [cap-js/graphql@0.3.1] Add `app` folder to `files` property of `package.json` to be included for publishing to `npm`
- [cds-mtxs@1.6.0] Fixed input validation for feature toggles containing `_` or `-`.
- [cds-mtxs@1.5.1] `cds migrate` does not crash any more when no options are supplied.
- [cds-mtxs@1.5.1] `cds-mtx-migrate` command now terminates immediately when the migration is finished.
- [cds-mtxs@1.5.1] Parameter `--dry` for `cds migration` now also skips the creation of the `t0`tenant.
- [cds-mtxs@1.5.1] `ModelProviderService`: Non-repeated dots are now allowed in feature toggles, e.g. `foo.bar.baz` is a valid feature toggle name.
- [odata-v2-adapter@1.9.19] Provide subdomain information to logs
- [odata-v2-adapter@1.9.19] Use correct correlation-id for logging (setup CDS context correctly)
- [odata-v2-adapter@1.9.19] React to incompatible change of mtxs getEdmx, to provide (internal) model parameter
- [odata-v2-adapter@1.9.19] Enhance example app to show usage of bound/unbound OData V2 actions in SAP Fiori UI via annotation

## January 2023 ​

### Added ​

- [cds-dk@6.5.0] `cds run/serve/migrate --resolve-bindings` now pulls required service credentials if bound via `cds bind`. Beta
- [cds-dk@6.5.0] `cds add helm` now supports multitenancy.
- [cds-dk@6.5.0] `cds bind` now supports binding of `user-provided service instances` from SAP BTP's Cloud Foundry.
- [cds-compiler@3.6.0] API: There are new API functions for `to.cdl`: `smartId`, `smartFunctionId` and `delimitedId`.
- [cds-compiler@3.6.0] CDL parser: when defining a parameter for entities, actions or functions, you can use a regular identifier for its name even if that is a reserved name like `in`.
- [cds-compiler@3.6.0] The first parameter of a bound action or function can be typed with `$self` or `many $self` even if no type named `$self` exists.
- [cds-compiler@3.6.0] If an aspect `sap.common.TextsAspect` exists in the `sap.common` context, it will be included in all `.texts` entities. This allows to extend `.texts` entities via extending the aspect. Example:cds

```
entity E {
  key id : Integer;
  content: localized String;
}
extend sap.common.TextsAspect with {
  elem: String;
};
// from @sap/cds common.cds
aspect sap.common.TextsAspect {
  key locale: String;
}
```
- [cds-compiler@3.6.0] to.edm(x): Support explicit binding parameter `: [many] $self` for OData V4 only. The explicit binding parameter is rendered as any other parameter and `$self` is replaced with the binding type but only if no `$self` definition exists in the model. This gives full control over the binding parameter including name, nullability, default value and annotations. The explicit binding parameter is ignored for OData V2 and has precedence over `@cds.odata.bindingparameter`.
- [cds@6.5.0] New aspect `sap.common.TextsAspect` in common.cds
- [cds@6.5.0] New syntax for collection bound entities
- [cds-mtxs@1.5.0] The built-in Service Manager client now caches binding information in-memory.
- [cds-mtxs@1.5.0] The `optimise_file_upload` HDI deployment option is now supported.
- [cds-mtxs@1.5.0] MTX migration script now allows to split extensions based on extension file names using regular expressions.
- [cds-mtxs@1.5.0] Now, provisioning supports SaaS applications using extensibility in combination with migration tables. Before, provisioning failed with a HDI deployment error. Note: Extending migration table artifacts is not supported.
- [vscode-cds@6.5.0] Experimental user setting `cds.typeGenerator.enabled` to trigger a globally installed cds type generator when saving a model file.
- [cds4j@1.35.0] New `Update.entry(Map entry)` method to improve the API for single updates with key values in update data.
- [cds4j@1.35.0] Added generation of builder interfaces for CDS defined events.
- [cds4j@1.35.0] New syntax defining the binding parameter for bound functions and actions is supported.
- [cds4j@1.35.0] Added `top` and `skip` methods to `Modifier` to modify pagination settings
- [cds4j@1.35.0] New interfaces `CdsBoundAction` and `CdsBoundFunction` represent bound functions and actions of an entity.

### Changed ​

- [cds-mtxs@1.4.4] `cds.xt.DeploymentService` configuration has been flattened. Instead ofjs

```
"hdi": {
  "create": {
    "provisioning_parameters": {
      "database_id": ""
    },
    "binding_parameters": {
      "key": "value"
    }
  }
}
```

you can now also writejs

```
"hdi": {
  "create": {
    "database_id": ""
  },
  "bind": {
    "key": "value"
  }
}
```

The old configuration is still supported, but you're advised to migrate to the new configuration for improved readability.
- [cds-mtxs@1.4.4] `/-/cds/jobs/pollJob` now also returns a `tenants` field, so tenant-specific tasks don't have to be polled individually. An example response format looks like this:js

```
{
  "status": "FAILED",
  "op": "upgrade",
  "tenants": {
      "non-existing-tenant": {
         "status": "FAILED",
         "error": "Tenant 'non-existing-tenant' does not exist"
      },
      "existing-tenant": {
         "status": "FINISHED"
      }
   }
}
```
- [cds-dk@6.5.0] `cds push` now runs a build of the extension project to update the pushed extension archive (unless custom archive given).
- [cds-dk@6.5.0] `cds init` and `cds bind` no longer use a spinner when performing long running operations.
- [eslint-plugin-cds@2.6.1] Fixed rule name in ESLint config:all to `@sap/cds/start-elements-lowercase`.
- [eslint-plugin-cds@2.6.1] Allow expensive rules to be reported when running from ESLint Cli.
- [eslint-plugin-cds@2.6.1] In auth-valid-restrict-grant, only suggest closely related user roles.
- [eslint-plugin-cds@2.6.1] In auth-valid-restrict-to, only suggest `*` if other entries apart from `*` exist.
- [cds-compiler@3.6.0] Many messages concerning the CDL and CSN syntax are improved: affects message ids (`syntax-…`), message texts and the error locations.
- [cds-compiler@3.6.0] Duplicate doc-comments are now errors, similar to duplicate annotations.
- [cds-compiler@3.6.0] Update OData vocabularies 'Aggregation', 'Analytics', 'Capabilities','Common', 'ODM', 'Offline', 'PDF', 'Session', 'UI'.
- [cds.java@1.30.2] The personal data annotation `@PersonalData.EntitySemantics: 'Other'` now has the same effect on entities like `@PersonalData.EntitySemantics: 'DataSubjectDetails`.
- [cds.java@1.30.2] Renamed the annotation `@kafka.channel` to `@kafka.topic`.
- [cds@6.5.0] Successive calls to `SELECT.where()` wraps existing clause in brackets if it contains `or`. E.g.js

```
SELECT.from `X` .where `x` .or `y` .where `z`
//> SELECT from X where (x or y) and z`
```
- [cds@6.5.0] `cds build` for SAP HANA now adds an `engines.node` version to the generated `db/package.json`. This will help in the future when runtime environments change their default to some version higher than the one supported by `@sap/hdi-deploy`.
- [cds@6.5.0] `cds build` checks the consistency of built-in models for java projects. An error is logged if some model files could not successfully be resolved indicating that a required npm module might be missing.
- [cds@6.5.0] Status code of draft actions are set in respective handler instead of protocol adapter
- [cds@6.5.0] `cds deploy --dry` no longer loads the `sqlite3` module by mistake. This fixes a regression when building Java projects. As a side effect a file with the name `undefined` was created in the project root folder.
- [cds@6.5.0] Internal representation of pseudo roles `internal-user` and `system-user`
- [vscode-cds@6.5.0] CAP notebooks: code cells (`terminal` and `shell`) have now their own working directory
- [vscode-cds@6.5.0] minimum VS Code version is now 1.73.0
- [cds4j@1.35.0] In SQL statements generated by the runtime CDS identifiers are now always in db-specific casing and delimited.
- [cds4j@1.35.0] Moved generation of `CDS_NAME` constant to builder interfaces of CDS events.
- [cds4j@1.35.0] Annotate generated accessor and builder interfaces with `@Generated` from the package `javax.annotation.processing` only if compiled with Java > 8.
- [cds4j@1.35.0] Deprecate interface `CqnModifier`, instead use `Modifier`
- [cap-js/graphql@0.2.0] Register `aliasFieldResolver` during schema generation instead of passing it to the GraphQL server
- [cap-js/graphql@0.2.0] The filters `contains`, `startswith`, and `endswith` now generate CQN function calls instead of generating `like` expressions directly

### Fixed ​

- [cds-compiler@3.5.4] Allow window functions also with a deprecated flag being set.
- [cds-compiler@3.5.4] to.edm(x): Fix program abort due to malformed error location in EDM annotation preprocessing.
- [cds-compiler@3.5.4] to.sql/hdi/hdbcds: The option `pre2134ReferentialConstraintNames` can be used to omit the referential constraint identifier prefix "c__".
- [cds-mtxs@1.4.4] `cds.xt.SaasProvisioningService`: `*` is not allowed as a tenant name any more.
- [cds-mtxs@1.4.4] Namespace check for new entities in extensions now also covers new root entities.
- [cds-mtxs@1.4.4] Asynchronous operations now correctly send the callbacks defined via `status_callback` or `mtx_status_callback`.
- [odata-v2-adapter@1.9.17] Fix special replacement pattern in $filter conversion
- [cds-dk@6.5.0] `cds import` now generates flattened value for `@Common.FieldControl` annotation in the CSN for OData V4 files.
- [cds-dk@6.5.0] `cds import` now treats the `CollectionKind` property attribute in OData V2 similar to `Collection()` in OData V4.
- [cds-compiler@3.6.0] If an entity with parameters is auto-exposed, the generated projection now has the same formal parameters and its query forwards these parameters to the origin entity.
- [cds-compiler@3.6.0] to.hdbcds: Aliases for foreign `keys` were not quoted if necessary.
- [cds-compiler@3.6.0] to.cdl: Aliases for `expand` and foreign `keys` were not quoted if necessary.
- Query functions that are CDL keywords were not properly quoted.
- CSN `doc` properties containing `*/` resulted in invalid CDL. To avoid compilation issues, `*/` is escaped as `*\/`.

- [cds-compiler@3.6.0] to.edm(x): Respect record type hint `$Type` in EDM JSON as a fully qualified `@type` URI property.
- [cds-compiler@2.15.10] If an entity with parameters is auto-exposed, the generated projection now has the same formal parameters and its query forwards these parameters to the origin entity.
- [cds-compiler@2.15.10] to.edm(x): Respect record type hint `$Type` in EDM JSON as a fully qualified `@type` URI property.
- [cds.java@1.30.2] Fixed a bug in the `cds-maven-plugin` which caused the goal `generate` to fail when triggered in IDEs.
- [cds.java@1.30.2] Fixed a bug which caused events to be silently dropped by the logical layer if qualified names of CDS-defined events didn't match, even when using `@topic`.
- [cds4j@1.34.1] Move CDS_NAME constant to generated builder interfaces of CDS events
- [cds4j@1.34.1] Fixed `hashCode` of `Row`
- [cds4j@1.34.1] Fixed structure of empty results for queries w/ toOne expands that only have nested toMany expands
- [cds4j@1.34.1] Don't allow to connect a conjunction/disjunction to itself (fixed stack overflow)
- [cds4j@1.34.1] Fixed search on entities w/ virtual String elements
- [cds@6.5.0] Resolve i18n folders from the root directory
- [cds@6.5.0] Types for `cds.test`
- [cds@6.5.0] Types for `srv.send`
- [cds@6.5.0] Optimized Search: Search queries for localized entities will now use default values, if no localized data is found in the corresponding localized tables on SAP HANA. Corrected aliasing by search queries with navigation.
- [cds@6.5.0] Resolution of `type of` references during minify in bootstrap
- [cds@6.5.0] Generation of odata-v2 URL in case of select=* in `urlify()`
- [cds@6.5.0] Build resets changed `cds.env` and `cds.root` when finished
- [cds@6.5.0] Expand error when using infix filters
- [cds@6.5.0] CDS configuration schema validation for `@sap/cds-mtxs`
- [cds@6.5.0] Typings for QL API
- [cds@6.5.0] Return types of asynchronous service API
- [cds-mtxs@1.5.0] MTX migration script now detects enabled multitenancy also for a sidecar project setup.
- [cds-mtxs@1.5.0] Improved robustness for MTX migration script, e. g. with inconsistent old metadata tenants.
- [odata-v2-adapter@1.9.18] Unicode encode messages header
- [cds-dk@6.5.0] `cds import` now generates flattened value for `@Common.FieldControl` annotation in the CSN for OData V4 files.
- [cds-dk@6.5.0] `cds import` now treates `CollectionKind` property attribute in OData V2 similar to `Collection()` in OData V4.
- [vscode-cds@6.5.0] workspace/symbols request didn't include definitions of a file after it was closed.
- [cds4j@1.35.0] temporal data: truncate `validFrom` and `validTo` to precision supported by DB
- [cap-js/graphql@0.2.0] Schema generation crash that occurred if an entity property is named `localized`
- [cap-js/graphql@0.2.0] The field `totalCount` could not be queried on its own

### Removed ​

- [vscode-cds@6.5.0] `@cds.doc` annotation, which was marked as deprecated for a long time, is no longer considered in requests like document/hover. Use doc comments (`/** ... */`) instead. The quick fix to migrate from @cds.doc to doc comments is still in place, but is likely to be removed in near future.
