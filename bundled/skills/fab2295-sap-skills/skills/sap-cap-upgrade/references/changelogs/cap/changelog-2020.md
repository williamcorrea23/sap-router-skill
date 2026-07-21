<!-- mirror: https://cap.cloud.sap/docs/releases/2020/changelog -->
<!-- fetched: 2026-05-09T02:26:11.913Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# Changelog 2020 ​

## December 2020 ​

### Changed ​

- [cds-dk@3.3.3] Bump version of `@sap/cds`, `@sap/cds-runtime`, and `@sap/cds-sidecar-client`
- [cds-dk@3.3.2] Bump version of `@sap/cds` to `4.4.5`

### Fixed ​

- [cds@4.4.7] `cds build` for Java now also creates a default edmx file (the one w/o language suffix) if the `cds.i18n.languages` array is configured with a set of languages. Runtime systems expect this file.
- [cds@4.4.7] `cds build` now skips empty lines in CSV files when preparing SAP HANA deployment. This does not happens if the build target folder is `.`, because there CSV files are sources that aren't touched.
- [cds@4.4.7] `cds build` for SAP HANA now writes CSV files more reliably, avoiding sporadic `ENOENT` errors.

## November 2020 ​

### Added ​

- [cds-dk@3.3.1] `cds init` and `cds add` now support the feature `notebook` to create a Jupyter Notebook in a project.
- [cds-dk@3.3.1] `cds compile --to openapi` adds support for OpenAPI 3 to `cds compile`.
- [cds-dk@3.3.1] If the server port is in use, `cds watch` offers to restart the server with a new port.
- [cds-dk@3.3.1] `cds init` uses latest `Maven Java archetype` version `1.11.0` for creating Java projects.
- [cds-dk@3.3.1] `cds init --add pipeline` and `cds add pipeline` will now use the general purpose pipeline of project "Piper".
- [cds-dk@3.3.1] `cds login`, `cds extend`, and `cds activate` now also support clientid/clientsecret as parameters. This is needed when extending multitenant applications provided as reusable services (see SAP Cloud Platform documentation).
- [cds@4.4.4] `cds.User.default` allows to override the default user, e.g. to be `cds.User.Privileged` in tests. By default this is `cds.User.Anonymous`.
- [cds@4.4.4] `cds.context` always allows access to the current request context when running in Node v12.18 and higher. It uses Node.js' `async_hooks` API for so-called continuation-local storage, and supercedes the need for `srv.tx(req)` in custom handlers.
- [cds@4.4.4] Custom functions/actions can now be implemented with plain JavaScript methods in subclasses of `cds.Service`
- [cds.java@1.12.0] OData V4 `$apply` now supports the transformations `skip`, `top`, and `orderby`.
- [cds.java@1.12.0] OData V4 `$apply` now supports the transformation `concat` (not to be combined with other system query options).
- [cds.java@1.12.0] OData V4 `$apply` now supports custom aggregates with aggregation methods declared by `@Aggregation.default` Beta.
- [cds.java@1.12.0] OData V4 `$apply` now supports unique value aggregates for currency codes and units of measure.
- [cds.java@1.12.0] OData V2 error responses now contain additional error messages written to the Messages API in their inner error.
- [cds.java@1.12.0] The HTTP method, the URI, and the response code of individual requests within a `$batch` are now logged by the OData adapters. This makes it easier to interpret `$batch` requests in application log files. You can control this through the dedicated loggers `com.sap.cds.adapter.odata.v2.BatchAccess` and `com.sap.cds.adapter.odata.v4.BatchAccess`.
- [cds.java@1.12.0] Finished initial version of the technical messaging foundation.
- [cds.java@1.12.0] You can now configure the connection pools of datasources, which are auto-configured by CAP Java SDK based on available service bindings using the properties prefix `cds.dataSource..hikari`.
- [cds.java@1.12.0] The property `cds.environment.local.defaultEnvPath` now also accepts paths pointing to an arbitrarily named environment JSON file. Earlier, this property only accepted a directory, in which it looked for a default-env.json file. This behaviour is still in place, when this property specifies a directory path.
- [cds.java@1.12.0] The `install-node` goal of the `cds-maven-plugin` now exposes the locations of installed executables in project properties: `${cds.node.executable}`, `${cds.npm.executable}`, `${cds.npx.executable}`, and `${cds.node.directory}.`
- [cds.java@1.12.0] The database connection cache of a tenant is now cleared directly during unsubscription of the tenant. This improves test scenarios, where unsubscription and subscriptions of the same tenant happen frequently after each other. Earlier these scenarios usually ran into connection pool timeouts, as old database connections could have been reused for the tenant.
- [cds4j@1.16.0] The comparison operators `IS` and `IS NOT` now allow to compare any two values for [in]equality. `NULL` values are treated as any other value in the comparison. Corresponding builder methods `is(Value other)` and `isNot(Value other)` have been added to the `Value` interface.
- [cds4j@1.16.0] Support arrayed elements with simple and structured type
- [cds-runtime@2.7.5] Deprecation warning for private function `req.run`, which will be removed
- [cds-runtime@2.7.5] Custom aggregates in `$apply` Beta
- [cds-runtime@2.7.5] Support for string keys with dots in value (for example, `a.b.c`) when using keys as segments
- [cds-runtime@2.7.5] `$filter`, `$groupby`, and `$orderby` works with path navigation to key for managed association to-one on SQLite
- [cds-runtime@2.7.5] Support for tracing database statements with Dynatrace when using `@sap/hana-client` driver
- [cds-runtime@2.7.5] Internal (for mtx) parameter `poolOnly` to `HanaDatabase.disconnect()` for clearing generic pool entry in case of credentials update
- [cds-runtime@2.7.5] `@assert.range enum { ... }` for decimals
- [cds-runtime@2.7.5] Draft: Lock active entity on edit action to prevent duplicate drafts
- [cds-runtime@2.7.5] Set batch response header Content-Transfer-Encoding
- [cds-runtime@2.6.8] Support for tracing database statements with Dynatrace when using `hdb` driver
- [cds-mtx@1.0.25] Added enhanced authentication API needed for the `@sap/cds-sidecar-client` to support authentication with clientid/clientsecret from subscriber account. This is needed to extend multitenant applications that are provided as services.
- [cds-sidecar-client@1.1.11] `login`, `extend`, and `activate` now also support clientid/clientsecret as parameters. This is needed when extending multitenant applications provided as reusable services

### Changed ​

- [cds-dk@3.3.1] Bump version of `@sap/cds` to `4.4.4` and `@sap/cds-runtime` to `2.7.5`
- [cds-dk@3.3.1] `cds add cf-manifest` now adds a dependency to the `java_buildpack`.
- [cds-dk@3.3.1] `sqlite3` is now an optional dependency to `cds-dk`. This means that an installation failure of `sqlite3`, for example, in environments w/o Internet connectivity, no longer leads to an overall installation error. This behavior suits Java applications, as these usually don't need an SQLite database. Node.js applications still require a proper installation of `sqlite3` if they use this database.
- [vscode-cds@3.1.4] updated npm modules `cds-lsp 4.1.2`

- [vscode-cds@3.1.2] updated npm modules `cds-lsp 4.1.1`

- [cds-compiler@1.46.0] to.edm(x): V4 structured key ref path aliases are now the basenames, colliding aliases are numbered.
- Lower level to `info` for "‹Term› isn't applied" message if an annotation can't be applied.

- [cds-compiler@1.46.0] OData: Update vocabulary 'UI'
- Correctly handle `not null` during flattening. Only if the parent and all subelements in the chain are `not null`, make the corresponding flat leaf element `not null`.

- [cds@4.4.4] `cds compile` and `build` now do a faster localization of EDMX files. If there are no text keys inside these files, the content is no longer duplicated in memory.
- [cds@4.4.4] `cds serve --at` / now can overwrite the default `/index.html` route
- [cds@4.4.4] `cds.unfold` was long-term deprecated, and removed now → use `cds.compile`
- [cds@4.4.4] `cds.config` was long-term deprecated, and removed now → use `cds.env`
- [cds@4.4.4] `cds.session` was long-term deprecated, and removed now → use `cds.db`
- [cds@4.4.4] Propagate correlation id header to subrequests
- [cds.java@1.12.0] The CAP Java SDK won't configure a random data source as primary anymore. If multiple services are bound to the application, it's necessary to explicitly configure the service used for the primary data source through `cds.dataSource.serviceName`.
- [cds.java@1.12.0] Artifact names of projects generated with the cds-services-archetype, are now allowed to contain underscores again.
- [cds.java@1.12.0] The `ErrorStatus` interface now allows to return string-based error codes using the new method `String getCodeString()`. With this change, the integer-based error code method `int getCode()` is deprecated.
- [cds.java@1.12.0] The OData V2 and V4 adapter now map comparison operators `eq` and `ne` to the operators `CqnComparisonPredicate.Operator.IS`, `IS_NOT`, respectively. This guarantees Boolean comparison semantics in the presence of `NULL` values.
- [cds.java@1.12.0] The archetype won't generate a `requires -> db -> kind -> sql` configuration into the .cdsrc.json anymore. The generated Java application still has all dependencies in place to run with HANA or SQLite locally. To initialize the project for a HANA-based cloud deployment, run `cds add hana` in addition.
- [cds-runtime@2.7.5] Logging is now done using `cds.log`
- [cds-runtime@2.7.5] CREATE and UPDATE requests that aren't allowed due to `@restrict.where` are rejected with `403` instead of `404`
- [cds-runtime@2.7.5] No usage of private `req._model` in generic handlers
- [cds-runtime@2.7.5] Service consumption: Print Cloud SDK logs only in debug mode
- [cds-runtime@2.7.5] Transaction state handling moved to core
- [cds-runtime@2.7.5] Correlation ID at `req.headers['x-correlation-id']` in subrequests
- [cds-runtime@2.6.8] No separate logging of error message and stack in OData server
- [cds-runtime@2.6.8] Not extended tenants reuse default OData service instance

### Fixed ​

- [cds-dk@3.3.0] `cds add cf-manifest` now only adds db-deployer module if SAP HANA service binding exists.
- [cds-dk@3.3.0] `cds init --add hana` now adds `requires.db.kind: "sql"` to cds configuration for Node.js and Java
- [cds-dk@3.3.0] `cds watch` no longer fails in SAP Business Application Studio when trying to find `sqlite3`. `cds deploy --to sqlite` still has that issue, which is to be solved in a future version.
- [cds-dk@3.2.1] `cds import` no longer creates .csn files with invalid `kind:ComplexType` fields
- [vscode-cds@3.1.4] file system watching no longer worked with latest VS Code
- [vscode-cds@3.1.3] internal refactoring and bug fixes
- [vscode-cds@3.1.2] support for mono repo file system layouts didn't work in certain cases
- [vscode-cds@3.1.2] completion proposals for annotations weren't shown at top of the list if inside an annotation
- [vscode-cds@3.1.2] only update workspace settings file if needed due to changed fileSystemWatch setting
- [cds-compiler@1.46.6] OData identifiers can now include all unicode characters, which are described in the OData specification.
- [cds-compiler@1.46.4] Association to Join translation: Fix using forward association target as table alias in ON condition.
- [cds-compiler@1.46.2] to.edm(x) Fix a bug in the alias calculation for key references in structured OData.
- [cds-compiler@1.46.0] Don't consider events to be potential targets for implicit redirections: strange warnings for multiple projections or other strange errors disappear.
- [cds-compiler@1.46.0] to.hdbcds/hdi/sql: Reject structured view parameters for HANA.
- Correctly handle `not null` during flattening. Only if the parent and all subelements in the chain are `not null`, make the corresponding flat leaf element `not null`.

- [cds-compiler@1.46.0] to.edm(x): Render @assert.range enum annotations correctly (enum symbol as value and don't omit zero value).
- [cds-compiler@1.46.0] Fixed CDS module resolution with option `newResolve` on Windows where a superfluous `\` was prepended to absolute paths.
- [cds@4.4.6] Compat `.emit()` for synchronous events with object as first parameter
- [cds@4.4.5] Revert of cds serve --at / now can overwrite the default /index.html route, which caused problems in some applications
- [cds@4.4.4] `srv.on` can now be used for async events w/o having to call `next` in each handler
- [cds@4.4.4] `srv.emit` constructs instances of `cds.Event` from given arguments, as intended
- [cds@4.4.4] `srv.send` constructs instances of `cds.Request` from given arguments
- [cds@4.4.4] Revert of: `cds build` filters `i18n` files for Node.js staging builds
- [cds@4.4.4] When two services `Foo` and `FooBar` were defined with one service's name being a substring of the other service's name, it may have happened that the same EDMX, that means, that of `FooBar`, was erroneously returned for both.
- [cds@4.4.4] On Windows, the index page now shows normalized links to embedded HTML pages, that means, `foo/bar.html` instead of `foo\bar.html`.
- [cds@4.4.4] `cds build` now consistently uses build target folder `'.'` as default for Java projects - also if custom build tasks have been defined.
- [cds@4.4.4] Requests that contain `*` as `Accept-Language` header value do no longer fail.
- [cds@4.4.4] `cds.debug` now reacts on the `DEBUG` environment variable set in a `.env` file
- [cds@4.4.4] Language headers with values `en-US-x-[saptrc, sappsd]` are now mapped to user locale `en-US-[saptrc, sappsd]`.
- [cds@4.4.4] `cds build` filters `i18n` files for nodejs staging builds
- [cds@4.4.4] Messages are kept in their respective request (that means, not propagated to the request's context, if exists)
- [cds@4.4.4] Log requests in atomicity groups
- [cds@4.3.1] `cds build` now creates correct custom handler path for nodejs projects in WebIDE full stack.
- [cds.java@1.12.0] Fixed a bug, that caused the CAP Java SDK to not be fully initialized yet, after Spring Boot started the Tomcat web-server. This issue only occurred as of Spring Boot `2.3.0.RELEASE` or later.
- [cds.java@1.12.0] Fixed a bug, where an exception other than a `ServiceException`, that is thrown in a `beforeClose()` ChangeSetListener method, caused the transaction to be kept open and not correctly rolled back.
- [cds.java@1.12.0] Fixed a bug, where the pseudo-locales `1Q` and `2Q` weren't correctly handled, when loading V2 or V4 EDMX metadata files.
- [cds.java@1.12.0] Fixed the startup log output, to prevent unnecessary warning logs to be displayed during every startup.
- [cds.java@1.12.0] Fixed an incorrect error message text, that occurred when the server required an etag condition.
- [cds.java@1.12.0] Fixed a bug, that caused the possibility for application roles to interfere with CAP's pseudo roles.
- [cds.java@1.12.0] Fixed the format of the `sap-message` header in OData V2.
- [cds.java@1.12.0] Fixed a bug, that caused events originating from OData V2 bound function imports to be emitted incorrectly on services and their event handlers.
- [cds.java@1.12.0] Fixed the handling of failing change sets in OData V2 `$batch` requests. A failing change set now aborts the batch processing.
- [cds.java@1.12.0] Fixed the handling of actions without return types in OData V2.
- [cds.java@1.12.0] Fixed a bug, that caused the authentication on function calls in OData V2 to fail.
- [cds.java@1.12.0] Fixed a bug, that caused etag conditions using timestamp elements to fail in OData V2.
- [cds.java@1.12.0] Fixed a bug, that caused functions with simple return values to fail in OData V2, when the `Content-Type` was set to `application/xml`.
- [cds.java@1.12.0] Fixed a bug, that caused issues, when resolving Maven dependencies of `cds-adapter-odata-v2` from Maven Central.
- [cds.java@1.12.0] Fixed a bug in `cds-maven-plugin`, where a project path containing a space caused an issue in goal `cds` on windows platform.
- [cds.java@1.11.2] Updated repackaged Olingo V4 dependencies, fixing an issue that caused navigation paths without the optional key name to cause a 400 error. For example `/Orders(12)/Items(34)` failed, but `/Orders(12)/Items(ID=34)` worked.
- [cds.java@1.11.2] Updated CDS4j to 1.15.2
- [cds.java@1.11.1] Fixed a bug that caused issues when resolving Maven dependencies of cds-adapter-odata-v2 from Maven Central.
- [cds.java@1.11.1] Updated CDS4j to 1.15.1
- [cds4j@1.16.0] Projection Resolvement: resolve foreign key elements of aliased managed to-one associations
- [cds4j@1.16.0] Fix isPredicate and asPredicate methods of CqnPredicate
- [cds4j@1.15.2] Fix using `isNull` on elements of associated entity
- [cds4j@1.15.2] Projection Resolvement: resolve aliased structured elements
- [cds4j@1.15.1] Projection Resolvement: resolve aliased elements in infix filters
- [cds4j@1.15.1] Projection Resolvement: resolve aliased elements in filtered updates
- [cds-reflect@2.13.4] More improved typings
- [cds-runtime@2.7.8] Null pointer exception when using `$expand`, `$filter`, and `contains` in the same HTTP request
- [cds-runtime@2.7.7] In `hdb` driver, stored procedures without OUT parameters can now return values
- [cds-runtime@2.7.7] Service consumption when using `.get('/')`
- [cds-runtime@2.7.6] Validate pool clients before use
- [cds-runtime@2.7.6] Improved default pool configuration
- [cds-runtime@2.7.6] Remove `req.run` deprecation warning
- [cds-runtime@2.7.5] Messaging incompatibility in combination with `@sap/cds@4.4.3`
- [cds-runtime@2.7.5] `filter-node-package` has to be a dev dependency
- [cds-runtime@2.7.5] No integrity check for events
- [cds-runtime@2.7.5] Race condition in data listener of messaging
- [cds-runtime@2.7.5] External entities are now always automatically resolved
- [cds-runtime@2.7.5] Skip integrity checks for virtual entities
- [cds-runtime@2.7.5] Auto-expand of to-one association of `CREATE` or `UPDATE` requests
- [cds-runtime@2.7.5] `tx.model` in REST requests
- [cds-runtime@2.7.5] Expand to association with projection `as select from where`
- [cds-runtime@2.7.5] Null pointer exception when using `$expand`, `$filter`, and `contains` in the same HTTP request
- [cds-runtime@2.7.5] Problem with navigations that have `null` as value in payload
- [cds-runtime@2.7.5] Response in case of failed changesets in `$batch` requests
- [cds-runtime@2.7.5] UPDATE/INSERT via navigation with foreign key in child
- [cds-runtime@2.7.5] Resolving custom DELETE CQNs
- [cds-runtime@2.7.5] Non-nullable values can't be set to `null` in UPDATE requests
- [cds-runtime@2.7.5] Delete active entity with DELETE restriction
- [cds-runtime@2.7.5] Calculation of HasDraftEntity doesn't involve secure annotations
- [cds-runtime@2.7.5] POST/PATCH on composition of aspect didn't insert keys correctly
- [cds-runtime@2.7.5] Check for different navigation properties with $expand
- [cds-runtime@2.7.5] Streaming from nondraft entity in draft context
- [cds-runtime@2.7.5] REST Adapter: `PUT` requests on collections are forbidden
- [cds-runtime@2.7.5] affected rows in CREATE caused error with hdb
- [cds-runtime@2.7.5] Navigating to composition of aspect with association as key caused error
- [cds-runtime@2.7.5] Wrongly returned value for key calculation in expand caused for loop to break
- [cds-runtime@2.7.5] TypeError by not connected database
- [cds-runtime@2.7.5] Multiple messages in batch change set
- [cds-runtime@2.6.8] Fix for metadata document exceeding cache limit
- [cds-runtime@2.6.7] Previous fix broke service consumption of other systems
- [cds-runtime@2.6.6] Check `req.path` during DoS prevention
- [cds-runtime@2.6.6] Headers handling in service consumption for SAP S/4 On-Premise systems
- [cds-runtime@2.6.6] i18n tests executed in cds-test
- [cds-runtime@2.6.6] Default sorting in combination with $apply
- [cds-runtime@2.6.3] URL and headers handling in service consumption
- [cds-runtime@2.6.2] Augment read after write data with returned values of virtual properties on draft activate
- [cds-runtime@2.6.2] Skip forbidden view check if association to view with foreign key in target
- [cds-mtx@1.0.25] Activation via cds-sidecar-client shows linter errors again
- [cds-mtx@1.0.25] Offboarding of tenants does no longer cause a reconnect of cds (also requires update of @sap/cds dependency to minimum @sap/cds@4.3)
- [cds-mtx@1.0.25] Broken compatibility with hdb driver is now fixed
- [cds-mtx@1.0.25] MTX is now compatible with latest versions of @sap/hana-client
- [cds-mtx@1.0.25] Linters can now handle extension projects with subfolders again
- [cds-mtx@1.0.25] The connection pool used by MTX is now correctly updated on offboarding even with scaled applications
- [cds-odata-v2-adapter-proxy@1.4.58] Support boolean header value in media entity
- [cds-odata-v2-adapter-proxy@1.4.58] Prevent escaping of quotes in url for batch requests
- [cds-odata-v2-adapter-proxy@1.4.58] Add 'media_src' and 'content-type' in __metadata for media entities
- [cds-odata-v2-adapter-proxy@1.4.57] Match headers case insensitive for custom body in media entity
- [cds-odata-v2-adapter-proxy@1.4.57] Parse header string values for non-string types in media entity
- [cds-odata-v2-adapter-proxy@1.4.56] Enable OData V4 'continue-on-error' per default
- [cds-odata-v2-adapter-proxy@1.4.56] Add proxy option to deactivate 'continue-on-error'
- [cds-odata-v2-adapter-proxy@1.4.55] Fix host port in response links
- [cds-odata-v2-adapter-proxy@1.4.55] Handle duplication of link tokens
- [cds-odata-v2-adapter-proxy@1.4.54] Support mapping of __next annotation
- [cds-odata-v2-adapter-proxy@1.4.54] Forward file upload headers to media entity POST call
- [cds-odata-v2-adapter-proxy@1.4.54] Explain annotation '@Core.ContentDisposition.Filename' in README
- [cds-odata-v2-adapter-proxy@1.4.54] Update README on OData API flavors
- [cds-odata-v2-adapter-proxy@1.4.54] Fix links for navigation collections and query options

### Removed ​

- [cds4j@1.16.0] Removed deprecated CqnXpr interface
- [cds-runtime@2.7.5] `req.statements` isn't available anymore
- [cds-runtime@2.7.5] Private function `_ensureOpen` of `cds.DatabaseService`
- [cds-runtime@2.7.5] Support for `defaultLocale` on service level

## October 2020 ​

### Added ​

- [cds-dk@3.2.0] `cds watch` now allows to set the `--in-memory` flag that is passed to `serve`.
- [vscode-cds@3.1.0] release notes page shows loading text while loading content
- [vscode-cds@3.1.0] user setting `cds.releaseNotes.showAutomatically` to enable or disable automatic display of `CAP Release Notes` when a new version is available
- [vscode-cds@3.1.0] support mono repo file system layouts
- [vscode-cds@3.1.0] user setting to disable OData plugin
- [vscode-cds@3.1.0] detection of slow running OData plugin (when validating) incl. user settings to disable and fine-tune
- [vscode-cds@3.1.0] user setting for omitRedundantTypesInSnippets for annotations
- [vscode-cds@3.1.0] user setting to enable file system watching to track installation of @sap/cds in project
- [cds-compiler@1.45.0] OData: Warn about nonapplicable annotations.
- [cds@4.3.0] Support `SELECT[...].limit(0, ...)`
- [cds@4.3.0] `hdbtabledata` generation can be disabled using `cds build` task option `skipHdbtabledataGeneration`.
- [cds.java@1.11.0] The OData V2 and V4 adapter now prefers loading EDMX files from `edmx/v2` or `edmx/v4`. The `edmx` folder is still checked by both adapters. The paths are also configurable through the property `cds.odata-v[2/4].edmx-path`. The configuration options are relative to the resources folder of the Java application.
- [cds.java@1.11.0] OData V4 `$apply` now supports aggregating using the virtual property `$count`.
- [cds.java@1.11.0] Added support for nested expands in OData V2 (e.g. `Orders?$expand=items/book`).
- [cds.java@1.11.0] The annotation `@assert.notNull: false` can now be used to skip server-side checks of elements marked with `not null`.
- [cds.java@1.11.0] The length of a string element is now validated when running insert, update or upsert statements on the persistence service. In case the length is exceeded, an HTTP `Bad request` error with code `400019` is thrown.
- [cds.java@1.11.0] The multitenancy subscription API endpoints now return error responses with localizable error texts in case something goes wrong.
- [cds.java@1.11.0] Made `cds.application.services` configuration more flexible, allowing to create multiple `ApplicationService` instances from the same CDS model service definition, by using the `model` property within the service configuration. By default a single `ApplicationService` is created for each CDS model service.
- [cds.java@1.11.0] Improved programmatic handler registration API to allow directly specifying events and entities, on which the handler should be registered, similarly to what is available in the annotations.
- [cds.java@1.11.0] `CqnInsert`, `CqnUpdate`, and `CqnDelete` statements are now supported on remote OData services. The statements are translated into `POST`, `PATCH`, and `DELETE` OData requests respectively.
- [cds.java@1.11.0] Lambda operators are now supported on CQNs to remote OData services.
- [cds.java@1.11.0] Improved error messages, in case entity instances weren't found (404). The error message now contains the keys of the entity that couldn't be found.
- [cds.java@1.11.0] Improved error messages in the OData V2 adapter, when an invalid JSON payload was provided on create or update requests.
- [cds4j@1.15.0] CqnAnalyzer: Support extracting non-key values
- [cds4j@1.15.0] Support binary literals
- [cds4j@1.15.0] Support lossless de/serialization of temporal and binary literals from/to CQN
- [cds4j@1.15.0] Support deep updates on writable views
- [cds4j@1.15.0] Support inserts & updates on writable views with to-one paths in the projection
- [cds4j@1.15.0] Support default values for parameters in parameterized views
- [cds4j@1.15.0] Support aggregate functions (`max`, `min`, `sum`, `average`, and `countDistinct`) in CQL builder
- [cds4j@1.15.0] Support modifying select from subquery
- [cds4j@1.15.0] Support SAP HANA-specific data types
- [cds-runtime@2.6.0] Support for `$expand` on managed Composition and Association to-one in structured types
- [cds-runtime@2.6.0] Support for CQN partials in `SELECT.orderBy()`
- [cds-runtime@2.6.0] `messages_.properties` files looked for in all i18n folders (not just the first)
- [cds-runtime@2.6.0] Structured types as key
- [cds-runtime@2.6.0] Support for localization in custom handlers
- [cds-runtime@2.6.0] `InsertResult` Beta: iterator that returns the keys of the created entries, for example: Example: `[...result]` -> `[{ ID: 1 }, { ID: 2 }, ...]`
- in case of `INSERT...as(SELECT...)`, the iterator returns `{}` for each row

- `affectedRows`: the number inserted (root) entries or the number of affectedRows in case of INSERT into SELECT
- `valueOf()`: returns `affectedRows` such that comparisons like `result > 0` can be used Note: `===` can't be used as it also compares the type

- [cds-runtime@2.6.0] Authentication strategy `xsuaa` (only with `@sap/xssec^3`) that additionally provides access to saml attributes through `req.user.attr` (for example, `req.user.attr.familyName`)
- [cds-odata-annotations@1.0.3] Enabled navigating to other instances of the annotation term and its properties.
- [cds-odata-annotations@1.0.4] Added a user/workspace setting to omit redundant types in annotation snippets.

### Changed ​

- [cds-dk@3.2.0] `@sap/cds-dk` is again shrinkwrapped, so that builds get reproducible again
- [cds-dk@3.2.0] All `cds` commands now prefer a local installation of `@sap/cds`. This enables applications better control over the version of `@sap/cds`.
- [cds-dk@3.2.0] `cds add cf-manifest` generates the service application with the `random-route: true` flag, which avoids route clashes on CF during development.
- [cds-dk@3.1.2] `cds init` uses latest `Maven Java archetype` version `1.10.0` for creating Java projects.
- [vscode-cds@3.1.0] install/update contributions completely async
- [vscode-cds@3.1.0] completion no longer suggests types when values are meant
- [vscode-cds@3.1.0] project cds-lsp settings overrule all
- [vscode-cds@3.1.0] consumes cds-compiler 1.45.0
- [vscode-cds@3.0.1] release notes page uses longer timeout (30 sec) when waiting for content
- [cds-compiler@1.45.0] A warning is emitted for annotation definitions inside services/contexts as this won't be allowed in the next major cds-compiler release.
- [cds-compiler@1.45.0] OData: Update vocabularies 'Analytics' and 'Common'.
- [cds@4.3.0] Optimized `cds build` performance when creating OData EDMX output.
- [cds.java@1.11.0] The `install-cdsdk` goal of the `cds-maven-plugin` now by default detects when `@sap/cds-dk` is already installed locally and omits reinstallation of the package in that case, to speed up the overall build process. This is achieved by changing the default value of the goal's `force` force parameter to `false`
- [cds.java@1.11.0] Renamed `cds.services` configuration section to `cds.application.services` configuration section. For backwards compatibility `cds.services` is still interpreted.
- [cds.java@1.11.0] Deprecated the `EventPredicate` based programmatic handler registration API, as it doesn't provide access to the registered events and entities.
- [cds.java@1.11.0] Authorization handler now throws internal error if inconsistent restriction with instance-based `where`-condition (`_where` property). If MTX application with sidecar, it's required to update @sap/cds to at least version 4.2.4.
- [cds4j@1.15.0] Map CDS elements without type to Java Object in generated consumption interfaces
- [cds4j@1.15.0] An IS NOT NULL check is now represented by a dedicated `IS_NOT` operator of `CqnComparisonPredicate`.
- [cds4j@1.15.0] The postfix `not` Operator of a Predicate now directly negates the operators of comparison predicates.
- [cds4j@1.15.0] The postfix `not` Operator of a Predicate now directly negates boolean logic.
- [cds4j@1.15.0] The order of CDS elements returned by the `getElements()` method in the Model Reflection API is now stable between consecutive calls.
- [cds-runtime@2.6.0] SQL queries don't use placeholders for rows of LIMIT clause
- [cds-runtime@2.6.0] Replaced `@sap/odata-server` dependency by own copy
- [cds-runtime@2.6.0] On `PATCH` and `PUT`, an `UPDATE` event is followed by a `CREATE` event if there was no matching entity
- [cds-runtime@2.6.0] On `PUT`, not provided properties are defaulted/ nulled
- [cds-runtime@2.6.0] On HTTP requests, `req.data` is a copy to preserve the original payload
- [cds-runtime@2.6.0] Additional properties in payload are preserved for entities with `@cds.persistence.skip` when served to `rest`
- [cds-runtime@2.6.0] RemoteService: Ignore where clause of view definition during INSERT, UPDATE, DELETE instead of throwing error
- [cds-runtime@2.6.0] Don't use SQL placeholders for numbers
- [cds-runtime@2.6.0] Service-level `@requires` are checked in protocol adapter instead of ApplicationService (excluding metadata requests)
- [cds-runtime@2.6.0] Additional translatable messages

### Fixed ​

- [cds-dk@3.2.0] `cds run` finds its `express` module again in the case where no `express` is installed in the application.
- [cds-dk@3.2.0] `cds env` now also displays properties that have a value `false` or `''`.
- [cds-dk@3.2.0] Leading flags in `cds` CLI work again, like `cds --to sql my.cds`
- [cds-dk@3.2.0] `cds compile --to` w/o an argument now fails with a better message
- [cds-dk@3.1.4] `cds run` finds the `sqlite3` module again if `cds` is used from a globally installed `@sap/cds-dk`.
- [cds-dk@3.1.3] `cds run` finds the `express` package again in the case where no `express` is installed in the application's `node_modules`.
- [cds-dk@3.1.2] `cds deploy --to sqlite` finds the `sqlite3` module again if `cds` is used from a globally installed `@sap/cds-dk`.
- [vscode-cds@3.1.0] validation of annotation plugins led to 100% cpu load
- [vscode-cds@3.1.0] globally installed cds wasn't reliably found
- [vscode-cds@3.1.0] code completion for annotation plugins didn't work inside annotations at @ characters
- [vscode-cds@3.1.0] bug fixes
- [vscode-cds@3.0.1] `preview as...` commands now overwrite preview file content instead of appending
- [vscode-cds@3.0.1] `preview as...` commands only fail when `cds compile` returned with exit code != 0 (severe error)
- [cds-compiler@1.45.0] Association to Join translation: Fill empty select blocks with aliased columns.
- [cds-compiler@1.45.0] to.edm(x): Some EDM(x) warnings weren't properly passed to the user.
- Don't render references and annotations for unexposed associations.

- [cds-compiler@1.45.0] to.hdbcds: Warnings during rendering of the hdbcds weren't raised to the user.
- [cds-compiler@1.45.0] Issue, which led to wrong on-conditions for `hdbcds` naming mode.
- [cds-compiler@1.44.4] to.hdbcds/hdi/sql: The processing of managed associations as foreign keys now works regardless of the order in which the possible chains are resolved.
- [cds-compiler@1.44.4] OData: Namespaces are brought back into the exposed types. Dots are replaced with underscores in the name.
- [cds@4.3.0] `cds build` now classifies the severity of compile messages the same way as the low-level compiler. As a consequence, messages with severity warning might now be classified as error.
- [cds@4.3.0] Now, cds CLI logs errors based on log-level setting.
- [cds@4.3.0] `cds compile --to sql` no longer creates SQLite-specific views if in `hana` SQL dialect
- [cds@4.3.0] The `node-cf` build task of `cds build` now also filters ./ file dependencies from package.json in the build output.
- [cds@4.2.8] `cds compile --to edmx --dest` creates files with `.xml` ending again.
- [cds@4.2.7] Fiori preview finds the `express` package again in the case where no `express` is installed in the application's `node_modules`.
- [cds@4.2.6] `cds run` finds the `express` package again in the case where no `express` is installed in the application's `node_modules`.
- [cds@4.2.5] `cds compile --to edmx-v2` and `edmx-v4` now again write to the folder given with `--dest`.
- [cds@4.2.4] `cds compile --to edmx-v2/4` no longer crashes
- [cds@4.2.4] `cds watch` no longer shows an error in absence of model files
- [cds@4.2.4] `cds build` no longer fails with an error about module './old/compile'
- [cds@4.2.4] Stack trace of some errors has been improved
- [cds@4.2.4] The `.hdiconfig` file created by `cds build` now includes HANA artefact types from undeploy.json
- [cds.java@1.11.0] Fixed a bug, where multiple prefixes of an XSUAA scope weren't handled correctly.
- [cds.java@1.11.0] Fixed a bug in remote OData query results, where date types in OData V2 responses weren't parsed correctly
- [cds.java@1.11.0] Fixed a bug, where locales didn't have a consistent value when provided in `sap-language` query parameter or `Accept` request header.
- [cds.java@1.11.0] Fixed a bug, where empty lambda operators (e.g. `$filter=books/any()`) weren't handled correctly in OData V4.
- [cds.java@1.11.0] Fixed a bug, where OData V2 `PATCH` or `MERGE` requests were handled in the same way as `PUT`, therefore setting unspecified values to their default value.
- [cds.java@1.11.0] Fixed a bug, where UUID elements weren't handled as String objects in OData V2.
- [cds.java@1.11.0] Fixed a bug, where milliseconds in time values weren't handled correctly in OData V2 responses.
- [cds.java@1.11.0] Fixed a bug in `cds-maven-plugin`, where multiple usages of the `generate` goal in a pom.xml could cause compiler errors.
- [cds.java@1.11.0] Fixed a bug, where the `install-cds-dk` goal of the `cds-maven-plugin` couldn't correctly detect an already installed `@sap/cds-dk` in case a package-lock.json was present.
- [cds4j@1.15.0] Enable draft for non-cuid entities
- [cds4j@1.15.0] Enable draft for entities with compound keys
- [cds-reflect@2.13.3] Improved typings no longer cause errors in typescript checks
- [cds-reflect@2.13.2] Improved typescript typings
- [cds-runtime@2.6.0] Streamlined debugging output for SQL statements
- [cds-runtime@2.6.0] Integrity check for Associations in structured types
- [cds-runtime@2.6.0] DateTime conversion for HANA
- [cds-runtime@2.6.0] Ensure `req.method` and `req.headers`
- [cds-runtime@2.6.0] DatabaseService: Ignore where clause of view definition during INSERT, UPDATE, DELETE
- [cds-runtime@2.6.0] Activate draft with UPDATE restriction
- [cds-runtime@2.6.0] Add the correct backlink to composition tree if additional association from child to parent
- [cds-runtime@2.6.0] `falsy` default values weren't inserted to the database
- [cds-runtime@2.6.0] Always prepare for temporal data
- [cds-runtime@2.6.0] Internal server error on views with parameters and join
- [cds-runtime@2.6.0] Secure annotation in draft union scenario
- [cds-runtime@2.6.0] Augment read after write data with returned values of virtual properties
- [cds-runtime@2.6.0] `@restrict` with association paths and `$user.` in where
- [cds-runtime@2.6.0] Result of deep insert
- [cds-runtime@2.6.0] `UPDATE` statements in custom handlers on Application Service setting only falsy values or using only expressions like `{stock: {'-=': 1}}`
- [cds-runtime@2.5.6] Messaging: add data listener only once queue was put
- [cds-runtime@2.5.5] `$user.id` in `restrict.where` always treated as string
- [cds-runtime@2.5.4] Certificate issue when consuming remote services
- [cds-runtime@2.5.3] Don't fail in `cds deploy --to sqlite` if `sqlite3` isn't installed
- [cds-mtx@1.0.22] The application url returned to the SaaS registry when using asynchronous onboarding can now also be set in the header field 'application_url'
- [cds-mtx@1.0.22] The build task used when onboarding do now use the right defaults. When being used as sidecar application, build task do no longer have to have the model option.
- [cds-mtx@1.0.22] New entities with namespaces in extensions are now correctly checked by the extensibility linter on extension activation
- [cds-mtx@1.0.22] Call of onboarding and offboarding via javascript API is now fixed ('Cannot read property 'headers' of undefined')
- [cds-odata-v2-adapter-proxy@1.4.53] Support custom body for binary media upload via POST
- [cds-odata-v2-adapter-proxy@1.4.53] Set 'Accept' header for $batch proxy request to "multipart/mixed"
- [cds-odata-v2-adapter-proxy@1.4.53] Set missing response header 'Content-Transfer-Encoding: binary'
- [cds-odata-v2-adapter-proxy@1.4.52] Log warning for change set order violation, instead returning an error response
- [cds-odata-v2-adapter-proxy@1.4.51] Support OData V2 binary media upload via POST
- [cds-odata-v2-adapter-proxy@1.4.51] Support OData V2 multipart/form-data media upload via POST
- [cds-odata-v2-adapter-proxy@1.4.51] Update README on logging layers
- [cds-odata-v2-adapter-proxy@1.4.50] Rewrite batch success status code from 200 to 202
- [cds-odata-v2-adapter-proxy@1.4.50] Remove OData V4 header 'odata-entityid'
- [cds-odata-v2-adapter-proxy@1.4.50] Propagate 'Content-ID' in response to HTTP request headers
- [cds-odata-v2-adapter-proxy@1.4.50] Remove artificially added 'Content-ID' header from batch response
- [cds-odata-v2-adapter-proxy@1.4.50] Fix 'Content-ID' order check for deviations between request and response
- [cds-odata-v2-adapter-proxy@1.4.49] Fix entity uris with "x-forwarded-path" headers for OData batch calls
- [cds-odata-v2-adapter-proxy@1.4.49] Support of 'odata-entityid' header rewrite
- [cds-odata-v2-adapter-proxy@1.4.48] Fix entity uris with "x-forwarded-path" headers
- [cds-odata-v2-adapter-proxy@1.4.48] Forward x-request-id, x-correlationid for metadata request

## September 2020 ​

### Added ​

- [cds-dk@3.1.1] `cds compile --locations` preserves `$location` properties in CSN outputs.
- [cds-dk@3.1.0] `cds compile` now supports option `flavor` with values: `files` `sources` `parsed` `xtended` `inferred`. `cds compile --files` maps to `--flavor files`.
- `cds compile --sources` maps to `--flavor sources`.
- `cds compile --parse` maps to `--flavor parsed`.
- `cds compile` maps to `--flavor inferred`.

- [cds-dk@3.1.0] `cds add cf-manifest` creates `manifest.yml` and `services-manifest.yml` allowing for Cloud Foundry native deployment.
- [cds-dk@3.1.0] `cds init` now supports type `nodejs` to create a Node.js based project. This is the default and can be omitted.
- [cds-dk@3.1.0] `cds watch`: enter `debug` or `debug-brk` to restart process in debug mode. Other commands are `ps` and `rs`.
- [cds-odata-annotations@1.0] SAP Fiori tools CDS OData Language Server enhances the functionality of SAP Cloud Platform core data services plug-in for Visual Studio Code with the features assisting you in defining OData annotations in files serving Fiori UIs.
- [vscode-cds@3.0.0] Plugin support for domain-specific annotation handlers, featuring: diagnostics
- code completion
- hover information
- goto definition
- quickfix to maintain translation
- auto-installation/update with user setting for npm registry

- [vscode-cds@3.0.0] code completion inside string literals and `![...]` identifiers is automatically triggered by `/` character (additionally to `.` and `@`)
- [vscode-cds@3.0.0] snippets applied through code completion are now formatted
- [vscode-cds@3.0.0] `action`s and their parameters are now indexed and support code navigation, hover etc.
- [vscode-cds@2.6.1] command `install cds-dk` now available to install `CDS Development Kit (@sap/cds-dk)` globally
- [cds-compiler@1.43.0] The magic variable `$session` is now supported. All element accesses are unchecked.
- [cds-compiler@1.43.0] Reference paths as annotation values can now contain identifiers starting with `@`.
- [cds-compiler@1.42.0] The compiler now supports the `cast(element as Type)` function in queries. Using this function will also result in a `CAST` SQL function call.
- [cds-compiler@1.42.0] A top-level property `i18n` is now supported. The property can contain translated texts. The compiler expects its entries to be objects where each text value is a string.
- [cds-compiler@1.42.0] CDL: Empty selection lists in views/projections are now allowed and make it possible to extend empty projections. Note that views/projections without any elements aren't deployable.
- [cds-compiler@1.42.0] For CSNs as input, the compiler returns properties as they are (without checks) if their name doesn't match the regexp `/[_$]?[a-zA-Z]+[0-9]*/` and doesn't start with `@`. With more than one CSN input, the compiler only returns the top-level CSN properties of the first source.
- [cds-compiler@1.41.0] OData: Allow the relational comparison of structures or managed associations in an ON condition as described in version 1.32.0 - 2020-07-10 (forHana).
- [cds-compiler@1.41.0] Allow `Struct:elem` with and without preceding `type of` as type reference.
- [cds-compiler@1.40.0] to.hdi/sql: Support default values for view parameters.
- [cds-compiler@1.40.0] OData: lower message severity from Error to Warning for ` has no primary key` and ` has no properties`.
- [cds@4.2.2] `cds.env.odata.containment` to use OData V4 Containment NavigationProperties feature
- [cds@4.2.2] `cds.env.odata.structs` to preserve struct elements as ComplexTypes in OData EDMX instead of flattening
- [cds@4.2.2] `cds.env.odata.refs`, which uses NavigationProperties in OData EDMX instead of adding foreign keys
- [cds@4.2.2] `cds.env.odata.proxies` to add proxy EntityTypes for external Association targets
- [cds@4.2.2] `cds.env.odata.flavors`, which contain presets for the afore-mentioned flags
- [cds@4.2.2] `cds.env.odata.flavor` to choose from the afore-mentioned presets
- [cds@4.2.2] `cds.load` option `plain` replacing former option `clean` (which still is silently supported for compatibility).
- [cds@4.2.2] `cds.get` now supports option `flavor` with values: `files` `sources` `parsed` `resolved` `compiled`.
- [cds@4.2.2] `sap.common.Currencies`, `Countries`, and `Languages` now have their `code` element annotated with `@Common.Text` pointing to the `name`. In Fiori's value list with fixed values, this will show the `name` rather than the code itself. As before, this only has an effect if `@Common.TextArrangement` is set to `#TextOnly` on the entity the code list is used as `ValueList` for.
- [cds@4.1.10] Much like SQLite deployment, `cds deploy --to hana`, and `cds build` can now cope with leading `#` comments in csv files, that means, the comments get removed before deployment.
- [cds@4.1.10] `cds deploy` now can handle empty strings in CSV values (use `""`)
- [cds.java@1.10.0] OData V4 `$apply` now supports arithmetic expressions in aggregate functions
- [cds.java@1.10.0] OData V4 `$apply` now allows to append further transformations to `group by`, `aggregate`, or `compute`
- [cds.java@1.10.0] Basic support for the OData V4 lambda operators `all` and `any` has been added
- [cds.java@1.10.0] Property `cds.security.openMetadataEndpoints = true` will make OData $metadata endpoints public accessible
- [cds.java@1.10.0] Improved thread-safety and concurrent usage of the RequestContext API
- [cds.java@1.10.0] Introduced a new JAR `cds-feature-jdbc`, which bundles all JDBC-related dependencies. It ensures that the default JDBC `PersistenceService` is created from the primary `DataSource` available to the application. In Spring Boot applications, this dependency is optional.
- [cds.java@1.10.0] Introduced a new starter JAR `cds-starter-spring-boot`, which bundles useful dependencies around CAP Java and Spring Boot. It doesn't include the OData V4 adapter. It should be used instead of `cds-starter-spring-boot-odata`, when applications only want to expose an OData V2 or custom REST API.
- [cds.java@1.10.0] Extended support for translating `where` conditions to `$filter` for queries to remote OData APIs
- [cds.java@1.10.0] Session variables from the `RequestContext` (locale, `sap-valid-at`, `sap-valid-from`, `sap-valid-to`) are now set on remote OData requests.
- [cds.java@1.10.0] The artifact `cds-services-utils` now contains the resource bundle `cds-messages-template.properties`, which can be used as a template for a custom resource bundle to customize stack error messages in the application. Use `jar -f cds-services-utils-.jar -x cds-messages-template.properties` to extract the file.
- [cds4j@1.14.0] Allow to filter by values of elements in an associated collection through builder API methods `.anyMatch()` and `.allMatch()`
- [cds4j@1.14.0] Support referencing origin entity from query result: `Row.ref()`
- [cds4j@1.14.0] Support deep in-/upserts through writable views. Note: Paths and key elements with aliases aren't supported.
- [cds4j@1.14.0] Support search by UUID
- [cds4j@1.14.0] `isLocalized` method to check if a `CdsElement` is localized
- [cds4j@1.14.0] Support parsing arithmetic expressions and add consumption interface
- [cds4j@1.14.0] Support parsing arithmetic negations and add consumption interface
- [cds-runtime@2.5.0] Messaging: Transaction-coupled events will only be sent for successful requests (can be disabled by setting outbox=false)
- [cds-runtime@2.5.0] Support for `@assert.notNull: false`
- [cds-runtime@2.5.0] Messaging: Support for non-normalized input in handler registration
- [cds-runtime@2.5.0] Messaging: automatically generate `headers.id`
- [cds-runtime@2.5.0] Support for navigating to association to-one in structured
- [cds-runtime@2.5.0] Initial support for `cds.odata.flavors = { v2, v4, w4, x4 }`
- [cds-runtime@2.5.0] Support custom timezone offset
- [cds-runtime@2.5.0] Support for assertions in structured data
- [cds-runtime@2.5.0] Support for annotation `@Capabilities.ReadRestrictions.Readable`
- [cds-runtime@2.5.0] Input validation for actions and functions
- [cds-runtime@2.5.0] Support language-dependent sorting order for SAP HANA
- [cds-runtime@2.4.0] Structured types in `$orderby`, `$filter`, `$select`
- [cds-runtime@2.4.0] Limited support for Association to-one in structured types

### Changed ​

- [cds-dk@3.1.2] `cds init` uses latest `Maven Java archetype` version `1.10.0` for creating Java projects.
- [cds-dk@3.1.1] `cds compile` prints a better legible JSON output to terminals.
- [cds-dk@3.1.1] `cds compile -p` is no longer a shortcut for `--parse`, to allow `--parse ...more-args` to work.
- [cds-dk@3.1.1] `cds compile -f` is no longer a shortcut for `--from` (which isn't implemented), but for `--flavor`.
- [cds-dk@3.1.0] `@sap/cds-dk` is no longer shrinkwrapped, so that new versions from underlying `@sap` packages (like `@sap/cds`) are available w/o a new `cds-dk` version
- [cds-dk@3.1.0] `cds init` uses latest `Maven Java archetype` version `1.9.0` for creating Java projects.
- [vscode-cds@3.0.0] updated npm modules `cds-lsp 4.0.0`
- `cds-compiler 1.42.2`

- [vscode-cds@2.6.1] using `axios` for HTTPs access to CAP release notes
- [vscode-cds@2.6.1] `CAP release notes` are now displayed when new version is available on `Capire`
- [cds-compiler@1.43.0] OData: Raise message level for illegal OData identifiers from warning to error.
- Update vocabularies 'Aggregation' and 'Common'.

- [cds-compiler@1.42.0] to.cdl: Smart type references are now explicitly rendered through ":"-syntax
- [cds-compiler@1.40.0] OData: The foreign key references in associations aren't flattened anymore with format `structured`.
- [cds@4.2.2] Replaced `cds.PrivilegedUser` with `cds.User.Privileged`
- [cds@4.2.2] `cuid` in `@sap/cds/common` is now defined as an `aspect` to align it with the other definitions. The previous definition as `abstract entity` is equivalent and was only needed for historic reasons.
- [cds@4.2.2] `cds deploy --to sqlite` now skips columns from CSV files if the header value is empty. This allows for ad-hoc 'disabling' of columns. For SAP HANA, the generated `hdbtabledata` files now also skip empty columns, restoring the behavior from CDS 3.
- [cds@4.2.2] `cds deploy --to sqlite` has aligned its escaping rules for parsing CSV data with SAP HANA's `hdbtabledata`. A `"` character can be escaped by another `"` as before, but only if contained in a quoted string, that means, `"A""B"` leads to `A"B`, while `A""B` stays `A""B`, and `""` results in an empty string.
- [cds4j@1.14.0] CqnVisitor: visit arguments of `CqnFunc`
- [cds4j@1.14.0] Deprecate `CqnXpr` in favor of `CqnExpression`
- [cds-runtime@2.5.0] Input processing: Performance improvements through templating mechanism used in single handler per layer
- [cds-runtime@2.5.0] Input processing: Key propagation only on DB layer
- [cds-runtime@2.5.0] Format of file-based messaging
- [cds-runtime@2.4.0] Messaging: The `queue` and `queueConfig` options are now a single object: `{ name, ...queueConfig }`
- [cds-runtime@2.4.0] Messaging: The `file` option is now moved to top level
- [cds-runtime@2.4.0] Messaging: The `prefix` option is removed

### Fixed ​

- [cds-dk@3.1.2] `cds deploy --to sqlite` finds the `sqlite3` module again if `cds` is used from a globally installed `@sap/cds-dk`.
- [cds-dk@3.1.1] `cds deploy --to sqlite` now writes `requires.db.model` in package.json such that `cds.connect.to.('db')` works w/o further `model` options.
- [cds-dk@3.1.1] `cds deploy --to sqlite` with `@sap/cds` 4.2 no longer crashes due to a wrong import
- [cds-dk@3.1.0] `cds watch` now passes all environment variables to the spawned sub processes, enabling, for example, `cds watch --production`
- [cds-dk@3.1.0] `cds init` modifies artifact ID and Java package name for Java projects to be standard conform.
- [cds-dk@3.1.0] `cds` fails with a better error message for misspelled commands
- [vscode-cds@3.0.0] bug fixes
- [vscode-cds@2.6.1] the `preview as...` commands are more robust and generate preview files without cds extension
- [cds-compiler@1.43.0] OData: put default value validation under `beta:odataDefaultValues`
- [cds-compiler@1.42.2] CDL: Action blocks can now be empty, for example, `entity E {…} actions { }`.
- [cds-compiler@1.42.2] An info message is emitted if builtin types are annotated. Use a custom type instead. Annotating builtins in CDL is possible but when transformed into CSN the annotation was silently lost. It's now put into the "extensions" property of the CSN.
- [cds-compiler@1.42.2] Fixed `cast()` for simple values like numbers and strings.
- [cds-compiler@1.42.2] to.sql: Remove simple default value checks and allow the database to reject default values upon activation.
- Render empty actual parameter list when selecting from a view with parameters, which are fully covered with default values and no actual parameters are provided in the query itself.

- [cds-compiler@1.42.2] OData: Correctly render unary operator of default values in EDM.

- [cds-compiler@1.42.0] Annotating an unknown element twice now results in a duplicate annotation error instead of silently loosing the annotation.
- [cds-compiler@1.42.0] Service/context extensions that reference a non-service/non-context now result in a compiler error instead of silently loosing the context/service extension.
- [cds-compiler@1.42.0] to.hdbcds/sql/hdi: fix a bug, which resulted in a malformed on-condition, if an association key was another association pointing to an entity with a structured key.
- in conjunction with assoc-to-joins, the internal CSN reference broke causing missing locations and even internal errors when logging messages
- managed associations in UNION are now correctly processed

- [cds-compiler@1.42.0] The parseCdl mode now correctly resolves type arguments of "many" types.
- [cds-compiler@1.42.0] OData: The annotation `@Capabilities.Readable` is now correctly translated to `@Capabilities.ReadRestrictions.Readable`.
- [cds-compiler@1.41.4] The check for ignored "localized" keywords in subelements has been extended to also include references to structured types.
- [cds-compiler@1.41.4] A warning was added if views/projections are used as element types.
- [cds-compiler@1.41.4] An info message is emitted if a namespace is annotated. Annotating namespaces isn't possible. Previously the annotation was silently lost. It's now put into the "extensions" property of the CSN.
- [cds-compiler@1.41.2] OData: correctly render primary key associations targeting a composition parent but aren't the composition enabling association.
- [cds-compiler@1.41.2] to.hdbcds/sql/hdi: Don't dump if artifact doesn't exist anymore after association to join translation
- [cds-compiler@1.41.2] Only check for unmanaged associations inside of "many"/"array of" in the elements of views and entities, not inside of actions and other members.
- [cds-compiler@1.41.0] to.cdl: Only render enums if they were directly defined there
- [cds-compiler@1.41.0] The parseCdl mode now checks for redefinitions to avoid generating invalid CSN.
- [cds-compiler@1.41.0] OData: An error is thrown if a redirected target has fewer keys than the original one.
- [cds-compiler@1.41.0] OData: Empty structured elements are now handled correctly in `flat` format.
- [cds-compiler@1.40.0] parse.cdl: Properly handle type arguments, most likely relevant for HANA types.
- [cds-compiler@1.40.0] OData: Multilevel anonymously defined `composition of ` is now processed successfully with the OData backend.
- [cds-compiler@1.40.0] OData: Fix a bug in EDM generation that caused a dump.
- [cds-compiler@1.40.0] Update ANTLR dependency to version 4.8.
- [cds@4.2.4] `cds compile --to edmx-v2/4` no longer crashes
- [cds@4.2.4] `cds watch` no longer shows an error in absence of model files
- [cds@4.2.4] `cds build` no longer fails with an error about module './old/compile'
- [cds@4.2.4] Stack trace of some errors have been improved
- [cds@4.2.3] Leading `#` comments in CSV files sporadically caused `cds build` to fail on Windows with error `EPERM: operation not permitted`.
- [cds@4.2.3] Method `req.user.is()` returns boolean
- [cds@4.2.2] A `manifest.yml` file is now also generated for nodejs applications if a sqlite database is used.
- [cds@4.2.2] `cds build` didn't correctly validate custom service handler implementations, warnings have been logged by mistake.
- [cds@4.2.2] The default memory size for nodejs applications has been increased in `manifest.yml` to avoid out-of-memory issues for cloud native deployments.
- [cds@4.2.2] `cds build` is now correctly creating external CSN output for Java multi-tenant applications.
- [cds@4.1.10] `cds v` and `cds --version` now work again when called from `npm run` or `npx`.
- [cds.java@1.10.0] Authorization handler throws internal error if inconsistent restriction with instance-based `where`-condition (`_where` property).
- [cds.java@1.10.0] Fixed a bug, where custom error codes were replaced with HTTP status codes within an OData V4 error response, when setting `cds.error.stackMessages.enabled: false`.
- [cds.java@1.10.0] Fixed a bug, that caused the `cds-maven-plugin` to fail when called from `git-bash` and other cygwin-based shells or via the `mbt` tool on Windows.
- [cds.java@1.10.0] Fixed a bug, where pseudo-variables (like `$user`) weren't correctly handled in `where` conditions inside `exists` subqueries of instance-based authorization conditions
- [cds.java@1.10.0] Fixed a bug, where the `Location` and `OData-EntityID` header weren't correctly set for contained entities in OData V4 responses.
- [cds.java@1.10.0] Fixed a bug, where keyless entities in OData V4 returned `404 Not found` errors on collection requests, if no entity data existed.
- [cds.java@1.10.0] Fixed a bug, that caused an incorrect OData V4 response, when an error occurred within a change set of a `$batch` request.
- [cds.java@1.10.0] Fixed a bug in `cds-maven-plugin`, where the `cds` command wasn't found in some cases if no working directory was configured.
- [cds.java@1.10.0] Fixed a bug in `cds-maven-plugin`, that caused default values for working directories to not be consistently calculated across different goals.
- [cds.java@1.10.0] Fixed handling of info or error messages written in methods of `ChangeSetListener`, when executing OData V4 `$batch` requests with change sets.
- [cds4j@1.14.0] Fix representation of expanded elements of single-valued associations in the row type of a query
- [cds4j@1.14.0] Fix using double negation on SAP HANA
- [cds4j@1.14.0] Improve error message when inserting invalid data
- [cds4j@1.14.0] Reflection API: Fix isView() for views with unsupported queries, such as unions
- [cds4j@1.14.0] Fix deep update through to-one association with generated UUID key
- [cds-reflect@2.13.1] Support for `hana.*` types
- [cds-runtime@2.5.3] Don't fail in `cds deploy --to sqlite` if `sqlite3` isn't installed
- [cds-runtime@2.5.2] Don't fail in `cds deploy --dry` if `sqlite3` isn't installed
- [cds-runtime@2.5.1] Set temporal session contexts on SAP HANA
- [cds-runtime@2.5.1] Multiple invocations of `req.on('failed', () => { ... })`
- [cds-runtime@2.5.0] Outbound REST/OData errors in CQN translation
- [cds-runtime@2.5.0] View resolution for views with static values
- [cds-runtime@2.5.0] Skip transition by view annotated with `@cds.persistence.table:true`
- [cds-runtime@2.5.0] Reading structured types via navigation
- [cds-runtime@2.5.0] Filter on elements having the same name as in `DraftAdministrativeData`
- [cds-runtime@2.5.0] Draft union scenario with filter on elements from `DraftAdministrativeData`
- [cds-runtime@2.5.0] Resolving views for deep deletes
- [cds-runtime@2.5.0] Key generation in some UPDATE queries
- [cds-runtime@2.5.0] SAP HANA: `cds.DateTime` convert to UTC in draft case
- [cds-runtime@2.5.0] Combining `$filter` query option and `$apply` using only filter transformation
- [cds-runtime@2.5.0] Join with draft tables
- [cds-runtime@2.5.0] Determine name of primary key of draft enabled entity in subselect
- [cds-runtime@2.5.0] Improved error message for direct use of auto exposed entity
- [cds-runtime@2.5.0] Empty structured types are now null
- [cds-runtime@2.5.0] Structured properties with the same name as CQN properties failed to execute
- [cds-runtime@2.5.0] Association as key caused wrongly generated SQL statement
- [cds-runtime@2.5.0] Deep update with structured type caused wrongly generated SQL statement
- [cds-runtime@2.4.0] Diff calculates the difference on database level
- [cds-runtime@2.4.0] `sap-messages` header now uses unicode characters for special characters
- [cds-runtime@2.4.0] `req.target` for bound operations
- [cds-runtime@2.4.0] `INSERT.into(...).as(SELECT.from(...)` inside custom handlers
- [cds-runtime@2.4.0] Integrity check for DELETE requests
- [cds-runtime@2.4.0] `Serialization Error` for entities with composition of aspects in `containment` mode
- [cds-runtime@2.4.0] Expand on entity with a backlink as a key
- [cds-mtx@1.0.21] Connections to application after off- and onboarding now work properly
- [cds-mtx@1.0.20] Custom content upload using `/mtx/v1/model/updateCustomTenantContent` now also works with CDS 4
- [cds-mtx@1.0.19] The sequence of extensions added through `cds.mtx.activate()` is now stable, even after a base model update.
- [cds-odata-v2-adapter-proxy@1.4.46] Update README on option `cds.env.odata.v2proxy.urlpath`
- [cds-odata-v2-adapter-proxy@1.4.46] Delta response annotation `@cov2ap.deltaResponse: 'timestamp'`
- [cds-odata-v2-adapter-proxy@1.4.45] Prepare 'Delta Responses' support in proxy (not yet supported by CDS)
- [cds-odata-v2-adapter-proxy@1.4.45] Remove metadata information in request payload deeply
- [cds-odata-v2-adapter-proxy@1.4.45] Update README on CDS modeling restrictions
- [cds-odata-v2-adapter-proxy@1.4.44] Rename proxy option `standalone` to `mtxRemote`
- [cds-odata-v2-adapter-proxy@1.4.44] Allow proxy option `mtxEndpoint` to be absolute HTTP URL
- [cds-odata-v2-adapter-proxy@1.4.44] Support for `cds.env` for proxy options under section `cds.cov2ap`
- [cds-odata-v2-adapter-proxy@1.4.44] Update README and JSDoc documentation

### Removed ​

- [cds-compiler@1.41.4] The length of SAP HANA identifiers aren't checked anymore: no more warnings are issued for long identifiers.
- [cds4j@1.14.0] Remove deprecated limit by expression API
- [cds4j@1.14.0] localized views aren't represented any longer in the `CdsModel`

## August 2020 ​

### Added ​

- [vscode-cds@2.6.0] various commands for generating preview files from a CDS file
- [vscode-cds@2.6.0] Code completion proposes identifiers not yet imported in current file and generates corresponding `using` statement: user setting: minimum number of characters required to propose those identifiers (`cds.completion.workspaceSymbols.minPrefixLength`). Default is -1 (=off)
- user setting: limit number of global identifiers (`cds.completion.workspaceSymbols.maxProposals`). Default is -1 (=unlimited)

- [vscode-cds@2.6.0] Code formatting: options `whitespaceBeforeColon` and `whitespaceAfterColon` are now supported inside `Composition` structs
- [vscode-cds@2.6.0] Code formatting: support configuration of alignment of `Composition` structs (option `alignCompositionStructToRight`)
- [cds-compiler@1.39.0] If the first CDS source (CDL or CSN) provided to the compiler has a `namespace` declaration/property, then that namespace name is put into the property `namespace` of the returned CSN.
- [cds-compiler@1.39.0] An event payload type can now be defined with a type/entity reference or projection (instead of providing the elements directly).
- [cds-compiler@1.39.0] Aspects can now be included when specifying the elements of an event payload type, as it's known for type, entity and aspect definitions.
- [cds-compiler@1.39.0] Projections columns can now use expressions like select items, both for `entity … as projection on` and `extend projection … with`.
- [cds-compiler@1.39.0] OData: `array of ` or `many ` is now allowed in OData V4, flat format.
- [cds-compiler@1.39.0] Query select items can now be declared to be virtual.
- [cds-compiler@1.39.0] CQL now allows to specify a join cardinality. Allowed are any combinations of `{ [ EXACT ] ONE | MANY } TO { [ EXACT ] ONE | MANY }` for `{ INNER | { LEFT | RIGHT | FULL } [ OUTER ] }` joins. The cardinality is added in the for SAP HANA-generated `CREATE VIEW` statements.
- [cds-compiler@1.39.0] Support the creation of unique constraints by assigning `@assert.unique.` to non-query entities or query entities annotated with `@cds.persistence.table`. The value of the annotation is an array of paths referring to elements in the entity. The path leaf may be an element of a scalar, structured or managed association type. Individual foreign keys or unmanaged associations can't be accessed. In case the path points to a structured element, the unique constraint will contain all columns stemming from the structured type. In case the path points to a managed association, the unique constraint will contain all foreign key columns stemming from this managed association. For HANA a `UNIQUE INVERTED INDEX` and for SQLite a `named unique table constraint` is generated.
- [cds@4.1.9] `cds.PrivilegedUser`, for example, for transactions with super user
- [cds@4.1.7] Shortcut to class `cds.ApplicationService` in cds facade
- [cds@4.1.7] Shortcut to class `cds.DatabaseService` in cds facade
- [cds@4.1.7] Shortcut to class `cds.RemoteService` in cds facade
- [cds@4.1.7] Shortcut to class `cds.MessagingService` in cds facade
- [cds@4.1.7] Shortcut to class `cds.Event` as new base class of `cds.Request`
- [cds@4.1.6] `req.notify()` as a new variant besides `req.info()`, which should display as toaster notifications on Fiori elements or other UIs.
- [cds.java@1.9.0] Drafts are now garbage-collected automatically after a default period of 30 days. The period can be customized through the property `cds.drafts.deletionTimeout`
- [cds.java@1.9.0] An OData V4 `PATCH` or `PUT` request on a nonexisting draft-enabled entity with `IsActiveEntity = true` can now directly create a new active entity, bypassing the draft-flow.
- [cds.java@1.9.0] OData V4 `$apply` now supports the transformation `compute` (without paths)
- [cds.java@1.9.0] Added an API annotation `HandlerOrder` to specify the order of an event handler within its registered phase.
- [cds.java@1.9.0] The `Messages` container stored in the `RequestContext` is now automatically propagated to nested request contexts. A new message container can be requested for the request context, by using `clearMessages()` on the `RequestContextRunner`.
- [cds.java@1.9.0] Added an API to elevate a request context to a privileged user, which bypasses all authorization checks automatically. A new request context can be elevated by using `privilegedUser()` on the `RequestContextRunner`. This privileged user can be further modified, for example to set a tenant.
- [cds.java@1.9.0] The messaging adapter now emits external events as the privileged user, to ensure that authorization checks on service-level are passed.
- [cds.java@1.9.0] CQN to OData transformation for remote OData queries: Expand definitions in the CQN query are now transformed to an OData V2/V4 `$expand` query option
- Orderby definitions in the CQN query are now transformed to an OData V2/V4 `$orderby` query option
- Limit definitions in the CQN query are now transformed to an OData V2/V4 `$top`/`$skip` query option
- Search definitions in the CQN query are now transformed to the `$search` query option for V4 and the SAP proprietary `search` query option for V2.
- CQN path expressions in `from` are now translated to corresponding OData V2/V4 URIs
- The types of values from the CQN statement and the result are now correctly handled based on the CDS type defined in the model.

- [cds.java@1.9.0] Improved the text of many error messages to make them easier to understand
- [cds.java@1.9.0] Improved the modularization capabilities of the `cds-framework-spring-boot` auto configurations. By default they no longer include Spring Web or Spring JDBC anymore, allowing to build Spring Boot applications without these features.
- [cds.java@1.9.0] The `cds-maven-plugin` lowered minimum required Maven version from `3.5.0` to `3.3.1`.
- [cds4j@1.13.1] Support parsing the query definition of views with joins
- [cds4j@1.13.1] Support writing via simple views
- [cds4j@1.13.1] Add API method to build ref segments
- [cds4j@1.13.1] Allow to build CQN statements from structured type refs
- [cds4j@1.13.1] Result metadata API Beta: Result.rowType()
- [cds4j@1.13.1] Support select from subquery; Note: `expand` isn't supported in subqueries
- [cds4j@1.12.1] Support managed associations with custom field mapping
- [cds4j@1.12.1] Support @cds.on.insert|update: $now|$user|literal
- [cds4j@1.12.1] Support anonymous types in code generation
- [cds4j@1.12.1] Generate `EventContext` interfaces for events
- [cds4j@1.12.1] Generate static `create()` method for structured types
- [cds4j@1.12.1] Support $now in On conditions
- [cds4j@1.12.1] Support using SessionContext variables in the WHERE clause
- [cds4j@1.12.1] Support using inline count together with group by, having, and distinct
- [cds-reflect@2.13.0] `aspect` to core type system
- [cds-reflect@2.13.0] `Association` class now knows `isAssociation`, `isComposition`, and `isManagedComposition`
- [cds-reflect@2.13.0] `any` has now a `path` getter
- [cds-runtime@2.3.0] Support for Continuation Local Storage (CLS)
- [cds-runtime@2.3.0] Support for access of structured property values in OData
- [cds-runtime@2.3.0] Support for expand for external OData service in REST
- [cds-runtime@2.2.0] Path navigations with keys for managed to-one association in orderby work on sqlite, for example, `$orderby=author/id`
- [cds-runtime@2.2.0] Support for `cds.PrivilegedUser`
- [cds-runtime@2.2.0] Implicit sorting for OData singletons
- [cds-runtime@2.1.7] Composite-Messaging
- [cds-runtime@2.1.7] Support for Message Queuing
- [cds-runtime@2.1.7] Support for `@sap/xssec^3`
- [cds-runtime@2.1.7] `@Common.numericSeverity` in error response
- [cds-runtime@2.1.7] Support expand with '*' in QL API
- [cds-runtime@2.1.7] Headers can be set with tx.emit on remote HTTP services
- [cds-runtime@2.1.7] Propagate @cds.localized:false during deep reads
- [cds-runtime@2.1.7] HANA: support for service manager credentials
- [cds-runtime@2.1.5] Support for `@Capabilities.NavigationRestrictions`
- [cds-runtime@2.1.5] Support queries to a model with nested projections to an external service
- [cds-mtx@1.0.19] The asynchronous model update API now accepts a callback URL (header field `MTX_STATUS_CALLBACK`) that is called when the update is finished

- [cds-sidecar-client@1.1.8] Login/logout: Enable entering the passcode interactively if not given
- [cds-sidecar-client@1.1.6] Login/logout: Support saving authentication token to desktop keyring (needs additional user-installed Node.js module)
- [cds-sidecar-client@1.1.6] Login/logout: Automatic token refresh without the need to provide passcode again
- [cds-sidecar-client@1.1.6] Login/logout: Suggest app URLs from Cloud-Foundry org and space currently logged in to (if applicable) if no app URL is supplied
- [cds-sidecar-client@1.1.6] Login/logout: Determine missing subdomain from Cloud Foundry if possible
- [cds-sidecar-client@1.1.6] Login/logout: Option to clear all invalid settings (where project folder doesn't exist)

### Changed ​

- [cds-dk@3.0.0] `cds watch` now uses version 5 of `sqlite3`
- [cds-dk@3.0.0] `cds watch` doesn't use `nodemon` anymore. You can continue using `cds watch` with `nodemon` by installing `nodemon` globally and setting env variable `CDS_USE_NODEMON` to true.
- [cds-dk@3.0.0] `cds add mta` for Java applications now determines app details like name, version etc. based on `pom.xml` and no longer from package.json.
- [vscode-cds@2.6.0] updated npm modules `cds-lsp 3.5.0`
- `cds-compiler 1.39.0`

- [vscode-cds@2.5.0] now requires Visual Studio Code `>=1.46`
- [vscode-cds@2.5.0] updated npm modules `cds-lsp 3.4.3`
- `cds-compiler 1.35.0`

- [cds-compiler@1.39.0] CSN: The property `payload` of an `event` has been renamed to `elements`.
- [cds-compiler@1.39.0] to.hdbcds/hdi/sql: Messages of id "query-no-undefined" are now raised as errors.
- Aspects/types/abstract entities containing anonymous aspect compositions must not be used as types and are removed during transformation.

- [cds-compiler@1.39.0] OData: Update vocabularies 'Common', 'UI'
- [cds-compiler@1.39.0] The association to join transformation treats foreign key accesses with priority. If a foreign key of a managed association can be accessed without joins, no joins are generated. The priority handling can be turned of with option `joinfk`.
- [cds@4.1.8] `cds deploy --to sqlite` can now cope with leading `#` comments in CSV files
- [cds@4.1.8] `cds version --all` now includes `@sap/cds-sidecar-client`
- [cds.java@1.9.0] The OData V4 `PUT` now follows the same internal semantics as `PATCH`, by first triggering an `UPDATE` event, following a `CREATE` event if the entity didn't yet exist. The `PUT` handling takes care to fill-up unspecified elements with their default values, as long as they can't be determined through a foreign key relation. `PUT` therefore doesn't affect the full composition tree by default anymore, but only the entity that the `PUT` was sent to. The `UPSERT` event is therefore no longer used by the OData V4 adapter.
- [cds.java@1.9.0] Changed HTTP status code of `@mandatory` and `not null` validations errors from `409` to `400`
- [cds.java@1.9.0] The name of the XSUAA system user (JWT with client credential flow) is now set to `system`.
- [cds4j@1.12.1] Disable "unrecognized CDS element" warning during interface generation
- [cds-runtime@2.1.7] Messaging: The configuration is moved to top level (before it was in credentials)
- [cds-runtime@2.1.7] Messaging: The payload type is now 'application/json'
- [cds-sidecar-client@1.1.6] Login/logout: Improved logging
- [cds-sidecar-client@1.1.6] Login/logout: Renamed command line options for clarity
- [cds-sidecar-client@1.1.6] Login/logout: Changed location of settings files to adhere to platform standards

### Fixed ​

- [cds-dk@3.0.0] `cds add mta` now configures the Service Manager for SaaS applications. The Instance Manager is no longer used.
- [cds-dk@3.0.0] `cds import` no longer writes an empty file if the source and the target edmx files are the same
- [cds-dk@3.0.0] `cds import` yields better error messages if the input file doesn't exists or is invalid
- [cds-dk@3.0.0] `cds import` no longer writes a Windows-specific path to package.json
- [cds-dk@3.0.0] `cds init --add java` shows better error message if Maven isn't installed.
- [cds-compiler@1.39.0] Fix a bug in explicit JOIN cardinality CDL parsing
- [cds-compiler@1.39.0] to.hdbcds/hdi/sql: Identifiers are checked and warnings are raised if the identifier exceeds a length limitation, which would result in a deployment error.
- [cds-compiler@1.39.0] OData: Service, entity, and element identifiers are checked and warnings are raised if an identifier isn't compliant with the OData specification.
- [cds-compiler@1.39.0] to.hdbcds/hdi/sql: Correctly handle local-scope refs in on-conditions when flattening structures.
- [cds-compiler@1.39.0] Run checks for associations inside of `many` or `array of` only on entities and views.
- [cds-compiler@1.39.0] to.cdl: Events are rendered.
- [cds-compiler@1.39.0] to.cds: Anonymous aspect compositions are now rendered correctly.
- [cds-compiler@1.39.0] to.hdbcds/hdi/sql: Events are ignored.
- local-scope references in on-conditions are now handled correctly during flattening.
- Removed duplicate messages.

- [cds-compiler@1.39.0] A model with multilevel `composition of ` (spread across several aspect declarations, composing one another) is now processed successfully with the OData backend.
- [cds-compiler@1.39.0] The CSN parser supports explicit join cardinalities.
- [cds-compiler@1.39.0] Prefix a `@assert.unique` table constraint with the table name to avoid name clashes.
- [cds-compiler@1.39.0] Semantic location in messages is now more precise.
- [cds@4.1.8] `cds.entities` w/o namespace parameter now works properly when running out of a compiled model (aka csn.json aka 'on Cloud Foundry').
- [cds@4.1.8] `cds deploy --to hana` now also handles SAP HANA Cloud services on trial, which are created by the `hana` broker (in contrast to the `hanatrial` broker, which still provisions older SAP HANA instances).
- [cds@4.1.8] `cds deploy --to hana` no longer uses `cf marketplace`, which has changed its parameters in CF CLI v7.
- [cds@4.1.8] Fiori preview's html no longer provokes Javascript errors in the SAP Fiori client.
- [cds@4.1.8] For database services of kind `sql` the service implementation is now set correctly in the CDS configuration. Previously, `sql` services got a `sqlite` implementation even if they were set to `hana` in production.
- [cds@4.1.8] Custom event handlers that don't register with a path (only with event and function) no longer crash the runtime
- [cds@4.1.8] In Typescript typings, the API declaration for `cds.load` and the `bootstrap` event is now fixed.
- [cds@4.1.7] Race condition on two parallel `cds.connect` to same service
- [cds@4.1.7] `cds deploy --no-save` extends the list of files it doesn't modify to package.json, default-env.json, and `connection.properties`
- [cds@4.1.7] Add meaningful error message if hdi-deploy can't be loaded — during `cds deploy --to hana`.
- [cds@4.1.6] `req.target` for unbound actions/functions is now `undefined` again, as documented
- [cds@4.1.6] Handlers registered with `srv.on(, 'Some/path', ...)` were never invoked
- [cds@4.1.6] Queries to remote services via `srv.on(..., ()=> other.read('Something'))` weren't sent to remote
- [cds.java@1.9.0] The `cds-maven-plugin` doesn't use npm / npx from local installation cache anymore, if goal `install-node` is skipped or not configured. In this case, a globally installed npm / npx is required and used.
- [cds.java@1.9.0] The archetype now uses `1.0.0-SNAPSHOT` instead of `1.0-SNAPSHOT` as default version, which works better with the `mbt` build tool
- [cds.java@1.9.0] Fixed a bug that caused the archetype to omit generating an (empty) db folder into the project.
- [cds.java@1.9.0] Fixed a bug that caused an exception stating `Only a single member is supported`, when using more than one `PlatformTransactionManager` in Spring Boot applications.
- [cds.java@1.9.0] Fixed a bug that caused a `NullPointerException` when calling an action or function, which returned a contained entity. With this fix, the OData V4 context URL for actions or functions returning an entity is now built based on entity types instead of entity sets.
- [cds.java@1.9.0] Fixed a bug that caused the entity data maps to be cleared during processing in the OData V4 adapter, preventing custom code from being able to store a reference to this data without copying the map.
- [cds.java@1.9.0] Fixed a bug that caused the cds-maven-plugin to determine a `null` working directory, in case the Maven project used an "external" parent project, not part of it's own source tree.
- [cds.java@1.9.0] Fixed a bug that caused an incorrect encoding of non-ASCII characters in `sap-messages` header.
- [cds.java@1.9.0] Fixed a bug where key fields annotated with `@Core.Computed` were removed from the CQN entries when executing an insert or update statement.
- [cds.java@1.9.0] Fixed a bug that occurred when queries with group by, got enriched with implicit sorting.
- [cds.java@1.8.1] Fixed a bug that caused a `NullPointerException` when opening a new transaction in some scenarios.
- [cds.java@1.8.1] Fixed a bug that caused a `IllegalStateException` during application startup, when the property `cds.security.xsuaa.serviceName` was specified.
- [cds4j@1.13.1] Generate builder interfaces for services containing only actions/functions
- [cds4j@1.13.1] Fix typed data access for arrayed types
- [cds4j@1.13.1] Fix `@Core.MediaType` detection
- [cds4j@1.13.1] Fix missing parentheses in join condition when using infix filters
- [cds4j@1.12.1] Improve parameter handling
- [cds4j@1.12.1] Improve Performance Suppress additional query for inline count if possible
- SQL generation
- Finding annotations
- Use joins to expand to-one associations

- [cds-runtime@2.3.0] HTTP Status Code for `GET` requests on `navigation-to-many` in combination with `$filter`
- [cds-runtime@2.2.0] Deep update could potentially insert wrong data
- [cds-runtime@2.2.0] Deep insert was also done on empty composition-to-many
- [cds-runtime@2.2.0] POST via multiple navigations with OData containment activated
- [cds-runtime@2.2.0] localized view with parameters
- [cds-runtime@2.2.0] implicit sorting order
- [cds-runtime@2.2.0] Custom SELECT CQN with join/union in draft enabled service failed for nondraft entities
- [cds-runtime@2.2.0] `req.user.attr` access during @restrict processing with @sap/xssec^3
- [cds-runtime@2.1.9] hdb reconnect on idle timeout
- [cds-runtime@2.1.7] Messaging: Messages are only acknowledged if successful
- [cds-runtime@2.1.7] Race conditions with messaging management
- [cds-runtime@2.1.7] `orderBy` as an empty array
- [cds-runtime@2.1.7] Join transaction during local API call
- [cds-runtime@2.1.7] Support duplicate names of bound and unbound actions and functions in local API
- [cds-runtime@2.1.7] Test read for UPSERT wasn't tenant aware
- [cds-runtime@2.1.7] Prefer `cds.env.requires.uaa.credentials`
- [cds-runtime@2.1.7] Error while activate with missing mandatory fields
- [cds-runtime@2.1.7] Restore `req._.req.authInfo` for compatibility
- [cds-runtime@2.1.7] OData V4 single property access in combination with mode `odata=structured`
- [cds-runtime@2.1.7] empty string in functions like tolower, toupper
- [cds-runtime@2.1.6] Removal of key properties of contained entity
- [cds-runtime@2.1.6] Flattening of to-one association if key is also a to-one association
- [cds-runtime@2.1.6] No localization with `SELECT.forUpdate()`
- [cds-runtime@2.1.6] Multilevel expand with composition backlink as key
- [cds-runtime@2.1.6] Ignore association keys in select for deletion integrity check
- [cds-runtime@2.1.6] POST via multiple navigations
- [cds-runtime@2.1.6] `req.user.id = ` with JWT strategy and `client_credentials` flow
- [cds-runtime@2.1.6] Transaction handling with integrity check and changesets in json batch
- [cds-runtime@2.1.5] `req._.req` in `SAVE` handler
- [cds-runtime@2.1.5] Insert duplicate data during deep update
- [cds-runtime@2.1.5] HANA: prefer `this.options.credentials`
- [cds-runtime@2.1.5] `$orderBy` in case of `DRAFT` with `Union`
- [cds-mtx@1.0.19] The sequence of extensions added through `cds.mtx.activate()` is now stable, even after a base model update.
- [cds-mtx@1.0.17] Asynchronous base model upgrade and job status requests that failed when using `@sap/cds@^4` are now fixed
- [cds-mtx@1.0.17] Extensions that got lost when running onboarding multiple times are now preserved
- [cds-mtx@1.0.17] The cds env configuration is now also available for `service-manager`
- [cds-sidecar-client@1.1.8] Activate: Output additional information in case of error on `job-result` retrieval
- [cds-sidecar-client@1.1.8] Login/logout: Determine running CF apps according to actual number of instances
- [cds-sidecar-client@1.1.8] Login/logout: Clarify error messages
- [cds-sidecar-client@1.1.7] The optional `keytar` package is now resolved if it's installed globally.
- [cds-sidecar-client@1.1.6] Activate: Corrected exclusion of files from upload
- [cds-odata-v2-adapter-proxy@1.4.43] Fix `\$filter` function conversion
- [cds-odata-v2-adapter-proxy@1.4.43] Fix remote CSN fetch for standalone proxy
- [cds-odata-v2-adapter-proxy@1.4.43] Fix `@sap.aggregation.role` annotation detection
- [cds-odata-v2-adapter-proxy@1.4.43] Annotation `@cov2ap.analytics` to suppress analytical conversion
- [cds-odata-v2-adapter-proxy@1.4.43] Update README documentation
- [cds-odata-v2-adapter-proxy@1.4.42] Add missing `Content-ID` header for batch changeset
- [cds-odata-v2-adapter-proxy@1.4.41] CDS 4 compatibility
- [cds-odata-v2-adapter-proxy@1.4.41] Improve logging layers
- [cds-odata-v2-adapter-proxy@1.4.41] Update README documentation
- [cds-odata-v2-adapter-proxy@1.4.41] Improve JWT tenant processing

## July 2020 ​

### Added ​

- [cds-dk@2.0.7] `cds init` supports adding `samples` via `--add samples`. See `cds help init` for more details.
- [cds-dk@2.0.7] Most CLI commands have moved to `@sap/cds-dk` from `@sap/cds`. Make sure to install the latest version with `npm i -g @sap/cds-dk`.
- [cds-dk@2.0.7] `cds` commands now log a hint to update to the latest `@sap/cds` if this one is still of version 3.
- [cds-dk@2.0.7] New command `cds login` added to simplify usage of `cds extend` and `cds activate` by providing them with automatic authentication and saving project settings. Refreshes expired authentication tokens automatically. Optionally uses CF command line client to determine login URLs and subdomains. Saves authentication data in plain-text file or desktop keyring on Linux, macOS, or Windows. The latter requires an optional Node.js module `keytar` to be installed.
- [cds-dk@2.0.7] New command `cds logout` removes authentication data and optionally project settings.
- [vscode-cds@2.4.2] issue reporting url pointing to `https://answers.sap.com/`
- [vscode-cds@2.4.2] new user setting `cds.completion.workspaceSymbols` (default `off`) to add workspace symbols to code completion proposals
- [cds-compiler@1.35.0] Introduce option `localizedLanguageFallback`; if set to value `"none"`, the localized convenience views don't use function `coalesce` to select from a default text as fallback.
- [cds-compiler@1.35.0] Allow to declare `many/array of` elements, parameters, and return types to be `(not) null`. The nullability applies to the array items of the element, not the element itself.
- [cds-compiler@1.35.0] New boolean option `dependentAutoexposed` to avoid name clashes in dependent autoexposed entities (text entities, components of managed compositions).
- [cds-compiler@1.35.0] cdsc: Add toOdata version 'v4x' to combine `{ version: 'v4', odataFormat: 'structured', odataContainment: true }`.
- [cds-compiler@1.35.0] Provide semantic code completion for elements, enums, actions, and parameters in `annotate` and `extend`.
- [cds-compiler@1.35.0] forHana: Allow the relational comparison of structures or managed associations in an ON condition. Both operands must be structurally compatible, that is both structures must be expandable to an identical set of leaf paths. Each leaf path must terminate on a builtin CDS scalar type. The original relational term of the form `s1 op s2` is replaced by the resulting expression `s1.leafpath_0 op s2.leafpath_0 (AND s1.leafpath_i op s2.leafpath_i)*` with `i  ...)` — the former technique to register per-row handlers `srv.after('READ', each => ...)` broke when code was minified. The new method using pseudo event `'each'` is minifier-safe.
- [cds@4.1.5] New `srv.prepend(srv => ...)` — use `srv.prepend(...)` to register event handlers to be executed before the already registered handlers. For example, extensions of reused implementations sometimes need to use this.
- [cds@4.1.5] Reflect `srv.events` — base class `cds.Service` provides a new getter `srv.events` to reflect on declared events in the service definition, similar to the already existing `srv.entities`, `srv.types`, and `srv.operations`.
- [cds@4.1.5] Experimental `cds.ql(req)` — event handlers can now use the like of `const {SELECT} = cds.ql(req)` to ensure transaction-managed and tenant-isolated execution of queries, instead of `srv.tx(req)`. Note though, that this is an experimental feature, which might change or be removed in future versions.
- [cds@4.1.5] Using `await` in `cds repl` — we now support using `await` directly on `cds repl` prompt inputs. This feature is provided through Node's --experimental-repl-await option.
- [cds@4.1.5] CLI shortcut `--odata ` — the newly introduced general CLI option --odata <v2/v4> acts as a shortcut to --odata-version <v2/v4>. In addition, --odata x4 acts as shortcut to --odata-version v4 --odata-format structured --odata-containment true.
- [cds@4.1.5] `cds build --production` — builds the project using the `production` profile - same when `NODE_ENV` or `CDS_ENV` environment variable is set to `production`. This will create SAP HANA deployment artifacts if `kind: "sql"` has been defined.
- [cds@4.1.5] `cds build --for  --opts ` — now supports execution of auto-created or configured build tasks. Individual properties can be overwritten by passing corresponding CLI options, defaults are used otherwise. for example, `cds build --for hana --dest target --opts model=[data,srv,app]`. Note: The parameter `options-model` has been deprecated use `--opts model=[...]`instead.
- [cds@4.1.5] The set of languages that is honored for the i18n.json language pack can now be configured through `i18n.languages`. Default is still `all`, which means the sum of language files found next to models.
- [cds.java@1.8.0] New `RequestContext` API that allows to spawn contexts with modified user or request parameter information.
- [cds.java@1.8.0] New provider API that allows to control how user or request parameter information is derived from the request.
- [cds.java@1.8.0] New API to access the currently active `RequestContext` and `ChangeSetContext`
- [cds.java@1.8.0] Parameterized views are now supported in OData V4.
- [cds.java@1.8.0] Update requests on OData singletons and navigations from singletons to other entities are now supported. The local service API also supports creating and deleting singletons, which is however not supported by the OData V4 specification.
- [cds.java@1.8.0] OData V4 `$metadata` endpoints now properly instruct the browser to allow to reuse the metadata from cache, if the ETag still matches, by setting `Cache-Control: max-age=0`.
- [cds.java@1.8.0] OData V4 now supports using `not` in filter expressions
- [cds.java@1.8.0] OData V4 now allows to order by aggregated values
- [cds.java@1.8.0] OData V4 `$apply` now supports the transformation `search`
- [cds.java@1.8.0] OData V4 `$apply` now supports the standard aggregation methods `avg` and `countdistinct`
- [cds.java@1.8.0] Event handler methods can now use `CdsData`, `List`, or `Stream` as generic POJO argument.
- [cds.java@1.8.0] Simplified the default database build configuration generated by the archetype
- [cds.java@1.8.0] Added new parameter `csnFile` to goal `generate` of cds-maven-plugin. It allows to configure the location of a csn file.
- [cds.java@1.8.0] The `cds-maven-plugin` now uses locations of package.json or .cdsrc.json as an indicator for the default working directory, instead of always defaulting to the root directory of the Maven project.
- [cds.java@1.8.0] Support for draft fields in `orderBy` clause
- [cds.java@1.8.0] Optimization of the number of executed statements when querying a draft enabled entity
- [cds.java@1.8.0] New switch `cds.drafts.associationsToInactiveEntities` to control behavior for associations to draft enabled entities
- [cds.java@1.8.0] The multitenancy feature now supports the Service Manager for SAP HANA DB instance provisioning
- [cds.java@1.8.0] The multitenancy feature now supports combining the connection pools for different tenants pointing to the same SAP HANA database, by setting `cds.multitenancy.datasource.combinePools.enabled: true`.
- [cds.java@1.8.0] Property `cds.security.xsuaa.serviceName` controls which XSUAA service binding is chosen for authorization. This helps in case multiple XSUAA service instances are bound to the CAP application.
- [cds4j@1.12.0] Support managed associations with custom field mapping
- [cds4j@1.12.0] Support @cds.on.insert|update: $now|$user|literal
- [cds4j@1.12.0] Support anonymous types in code generation
- [cds4j@1.12.0] Generate `EventContext` interfaces for events
- [cds4j@1.12.0] Generate static `create()` method for structured types
- [cds4j@1.12.0] Support $now in On conditions
- [cds4j@1.12.0] Support using SessionContext variables in the WHERE clause
- [cds4j@1.12.0] Support using inline count together with group by, having, and distinct
- [cds-reflect@2.12.2] getters `.associations` and `.compositions` on linked entities
- [cds-runtime@2.1.5] Support for `@Capabilities.NavigationRestrictions`
- [cds-runtime@2.1.5] Support queries to a model with nested projections to an external service
- [cds-runtime@2.1.4] Support for structured OData
- [cds-runtime@2.1.4] Support for arrayed elements
- [cds-runtime@2.1.3] Synchronous API for streaming
- [cds-runtime@2.1.3] Support calling SAP HANA stored procedures
- [cds-runtime@2.1.0] `req.warn(code, msg, target, args)`
- [cds-runtime@2.1.0] `req.data` returns array in case of bulk operations
- [cds-runtime@2.1.0] All services as subclasses of new `cds.Service`
- [cds-runtime@2.1.0] Differentiation between "Application Service" (for example, providing OData) and "Persistence Service" (for example, database, remote)
- [cds-runtime@2.0.3] Custom translatable error messages
- [cds-runtime@2.0.3] Support for containment in CRUD
- [cds-runtime@2.0.3] Support for static values in custom on conditions for associations
- [cds-runtime@2.0.2] Support for XSUAA's user attribute value `$UNRESTRICTED`
- [cds-runtime@2.0.2] Default to combination `[...];IEEE754Compatible=true;ExponentialDecimals=true` if IEEE754Compatible or ExponentialDecimals is omitted
- [cds-runtime@2.0.2] Use custom authenticate middleware via `cds.env.requires.auth.impl`
- [cds-runtime@2.0.2] Authentication strategy `dummy` (`cds.env.requires.auth.strategy = 'dummy'`) that creates super users (that means, pass all authorization checks)
- [cds-runtime@2.0.2] Support relative destination path in rest client
- [cds-runtime@1.2.0] The timeout of the exclusive lock of drafts can now be configured using `cds.drafts.cancellationTimeout`
- [cds-runtime@1.2.0] `req.params`: iterable with key value pairs for the key predicates of the addressed resource
- [cds-sidecar-client@1.1.6] Login/logout: Support saving authentication token to desktop keyring (needs additional user-installed Node.js module)
- [cds-sidecar-client@1.1.6] Login/logout: Automatic token refresh without the need to provide passcode again
- [cds-sidecar-client@1.1.6] Login/logout: Suggest app URLs from Cloud-Foundry org and space currently logged in to (if applicable) if no app URL is supplied
- [cds-sidecar-client@1.1.6] Login/logout: Determine missing subdomain from Cloud Foundry if possible
- [cds-sidecar-client@1.1.6] Login/logout: Option to clear all invalid settings (where project folder doesn't exist)

### Changed ​

- [cds-dk@2.0.8] `cds init` uses latest `Maven Java archetype` version `1.8.1` for creating Java projects.
- [cds-dk@2.0.7] `@sap/cdk` no longer warns about `@sap/cds` being globally installed next to it. This was a temporary hint for the transition period to `@sap/cds-dk`.
- [cds-dk@2.0.7] `cds init` generates dependency to `@sap/cds` version `4` for Nodejs projects.
- [cds-dk@2.0.7] Use square brackets to pass array values for options to `cds init --java:mvn`.
- [cds-dk@2.0.7] `cds init --add pipeline` and `cds add pipeline` now create file `config.yml` in `.pipeline` folder.
- [cds-dk@2.0.7] Improved launch.json file, which is created during `cds init`.
- [cds-dk@2.0.7] `cds add mta` now creates a mta.yaml file that sets the production flag for cds build and npm install. This ensures that the SAP HANA artifacts are created if `"kind": "sql"` or some `production` profile has been configured in package.json or .cdsrc.json. Requires `@sap/cds` version >=4.x.
- [cds-dk@2.0.7] `cds init` uses latest `Maven Java archetype` version `1.7.0` for creating Java projects.
- [cds-dk@2.0.7] `cds init` no longer adds package-lock.json to .gitignore file when creating a new project.
- [cds-dk@2.0.7] `cds init --add hana` and `cds add hana` now use `Maven Java archetype` to create SAP HANA-related pom.xml entries.
- [cds-dk@2.0.7] Consistent default naming scheme for applications and services deployed to CF across the following `cds` commands `build`, `deploy`, `init`, and `add`. For an application named `myapp` the SAP HANA deployer app name is `myapp-db-deployer`, the SAP HANA DB service name is `myapp-db`.
- [cds-dk@1.8.6] Service binding names have been adapted in mta.yaml created by `cds add mta` command.
- [cds-dk@1.8.5] `cds init` uses latest `Maven Java archetype` version `1.6.0` for creating Java projects.
- [cds-dk@1.8.4] `cds init` uses latest `Maven Java archetype` version `1.5.2` for creating Java projects.
- [vscode-cds@2.4.2] updated npm modules`cds-lsp 3.4.2`

- [vscode-cds@2.5.0] now requires Visual Studio Code `>=1.46`
- [vscode-cds@2.5.0] updated npm modules`cds-lsp 3.4.3`
- `cds-compiler 1.35.0`

- [vscode-cds@2.4.2] internal refactorings
- [vscode-cds@2.4.1] extension is now hosted on Visual Studio Marketplace and updates from thereupdate configuration and update command have been removed

- [vscode-cds@2.4.0] updated npm modules`cds-lsp 3.4.0`

- [vscode-cds@2.4.0] improved `README.md`updated feature list

- [vscode-cds@2.3.2] using new npm modulesgot 11.1.4

- [cds-compiler@1.35.0] OData:Update vocabularies 'Common', 'Core', 'ODM'.
- The default nullability for collection value properties is `false`, indicating that the returned collection must not contain null value entries.

- [cds-compiler@1.35.0] toCdl: Identifiers are now quoted with `![` and `]`. Inner `]` characters are escaped with `]]`.
- [cds-compiler@1.35.0] toCdl/toSql: Function names containing nonstandard SAP HANA identifier characters are rendered case preserving and quoted if an appropriate naming mode has been set in the options.
- [cds-compiler@1.35.0] toCdl: String enums without a value are no longer rendered with their name's string representation as their value.
- [cds-compiler@1.35.0] Option `beta` now only works with selective feature flags. Instead of `beta: true`, a dictionary of `: true` is expected. Available feature flags are:subElemRedirections
- keyRefError
- aspectCompositions
- odataProxies
- uniqueconstraints

- [cds-compiler@1.35.0] OData V4: Unmanaged associations/compositions with a target cardinality of exactly one (that is `[1..1]`) are rendered as `edmx:NavigationProperty` with attribute `Nullable="false"`
- [cds-compiler@1.35.0] OData: On-condition checks are now performed when generating OData as well.
- [cds-compiler@1.35.0] SQLite: The property length for string parameters isn't longer restricted to 5000 characters.
- [cds-compiler@1.35.0] SAP HANA/SQLite: Improved the error message when an entity without elements is found to make it clearer what is expected.
- [cds-compiler@1.35.0] OData: Update vocabularies 'CodeList', 'Common', 'Graph', 'UI'
- [cds-compiler@1.35.0] Issue error if old backends are used with beta mode.
- [cds-compiler@1.35.0] Raise severity of message `Unmanaged associations cannot be used as primary key` with id `unmanaged-as-key` to error.
- [cds-compiler@1.35.0] Improve warning messages for integer enum missing a value and chained array of.
- [cds-compiler@1.35.0] SAP HANA/SQLEmpty structures aren't allowed as foreign keys.

- [cds-compiler@1.35.0] Report a warning for integer enum elements that don't have values.
- [cds-compiler@1.35.0] Report a warning for enums that aren't integer- or string-like.
- [cds-compiler@1.35.0] ODataUpdate vocabularies 'Common', 'Core', 'Validation'
- Pass through structures without elements
- `cds.Decimal` and `cds.DecimalFloat` (deprecated) without precision/scale are rendered as `Edm.Decimal` with `Scale=variable` (V4) and `sap:variable-scale="true"` (V2)

- [cds-compiler@1.35.0] Report a warning when a deprecated non-snapi backend (OData, SAP HANA/SQL) is called.
- [cds-compiler@1.35.0] OData:Update vocabulary 'UI'
- Add annotation `@Common.Label: '{i18n>Draft_DraftAdministrativeData}'` to entity `DraftAdministrativeData`
- Improve info message for target mismatch on associations that are compared with $self

- [cds@4.1.5] Most CLI commands have moved to `@sap/cds-dk`. Make sure to install the latest version with `npm i -g @sap/cds-dk`.
- [cds@4.1.5] Default OData version in `cds configuration` is now `v4`. For `Node.js` projects and `Java` projects using new stack the cds configuration of `odata.version = 'v4'` is no longer required. For `Java` projects using old Java stack, OData v2 will still be used.
- [cds@4.1.5] Always do `await cds.connect.to()` — in former versions `cds.connect.to()` returned some magic thenables, meant to ease the Promise Hell; now it always returns plain-standard Promises. Likely you never used this undocumented former behavior, but in case: Just ensure to always call `cds.connect` with `await`.
- [cds@4.1.5] Deprecated `cds.connect()` — prefer `cds.connect.to('db')` instead, which has the same effect but is more in line with the notion of potentially working with multiple database services.
- [cds@4.1.5] Deprecated `cds.hana.syntax` configuration. Use `cds.hana.deploy-format`=`hdbtable` instead to switch deployment from `hdbcds` to `hdbtable` for SAP HANA Cloud.
- [cds@4.1.5] Faster generation of `hdbtabledata` files from csv data. It no longer tries to check the existence of element or column names. Such checks are anyways done during SAP HANA deployment. This behavior is now symmetrical to SQLite deployment.
- [cds@4.1.5] Removed legacy cds build system — the fallback using `cds.features.build.legacy` is no longer supported.
- [cds@4.1.5] `cds deploy --to hana` changes kind to `hana` only if it isn't already `sql`.
- [cds@4.1.5] `cds build` — does no longer create service metadata for the UI service binding by default. For SAP Web IDE Full-Stack compatibility, a corresponding metadata.xml is still generated. A `fiori` build task has to be defined otherwise.
- [cds@4.1.5] Consistent default naming scheme for applications and services deployed to CF across the following `cds` commands `build`, `deploy`, , and `add`. For an application named `myapp` the SAP HANA deployer app name is `myapp-db-deployer`, the SAP HANA DB service name is `myapp-db`. `cds build` now generates the application manifest file with a different name `manifest.yml`.
- [cds@4.1.5] `cds build` creates `hana` build results only if either a corresponding build task has been configured or if kind `hana` or kind `sql` has been defined. A `production` build is required for the latter. A fallback is used for Web IDE full stack and legacy build configs.
- [cds@3.35.0] The new compiler implementation, a.k.a SNAPI, is now the default. Can be disabled with `cds.features.snapi=false`.
- [cds@3.34.3] Faster generation of `hdbtabledata` files from csv data. It no longer tries to check the existence of element or column names. Such checks are anyways done during SAP HANA deployment. This behavior is now symmetrical to SQLite deployment.
- [cds@3.34.2] Use `cds.hana.deploy-format`=`hdbtable` instead of `cds.hana.syntax` to switch deployment from `hdbcds` to `hdbtable` for SAP HANA Cloud.
- [cds@3.34.2] `cds run` now supports relative `dataSource` URLs in SAP UI5 manifests again, so that UI5 apps can be served w/o App Router. This support is only active in development mode.
- [cds@3.34.2] `cds deploy --to hana` changes kind to `hana` only if it isn't already `sql`
- [cds.java@1.8.0] `CdsRuntime.runInRequestContext()` has been deprecated and replaced by `CdsRuntime.requestContext()`.
- [cds.java@1.8.0] `CdsRuntime.runInChangeSetContext()` has been deprecated and replaced by `CdsRuntime.changeSetContext()`
- [cds.java@1.8.0] For an OData query with `$count` option the inline count must be specified in the result. In the previous version, if no inline count was contained in the result, the row count was used, which could have resulted in wrong data.
- [cds.java@1.8.0] Removed npm registry configuration from the archetype, to prevent overriding custom values, specified by developers.
- [cds.java@1.8.0] Fields annotated with `@cds.on.insert` are preserved in the draft when editing a draft enabled entity.
- [cds.java@1.8.0] Some error codes were incorrect and have been corrected: The codes ranging from `40008` to `40017` have been changed to `400008` to `400017` respectively, to prevent conflicts in error codes in the future.
- [cds.java@1.8.0] The `ServiceException.getLocalizedMessage()` is only capable of determining the correct locale from the request, if an active `RequestContext` exists. If no active `RequestContext` exists the new method `ServiceException.getLocalizedMessage(Locale)` can be used to explicitly set a locale. The requests locale can be obtained from the `CdsRuntime` using `runtime.getProvidedParameterInfo().getLocale()`
- [cds.java@1.8.0] XSUAA user names aren't normalized to lower case by default anymore (property cds.security.xsuaa.normalizeUserNames). XSUAA delivers stable case-sensitive user names now.
- [cds4j@1.12.0] Disable "unrecognized CDS element" warning during interface generation
- [cds-foss@2.0.0] Bumped dependency versions
- [cds-runtime@2.1.0] Streamlined `req.reject/error/info(code, msg, target, args)`: takes four individual params (number, string, string, array) or one object
- [cds-runtime@2.1.0] Changed behavior by handler registration: -- Handlers registered with entity = '*' aren't called by unbound events anymore. -- Handlers registered without entity aren't called by bound events anymore. -- Special case: Handlers registered in form .before/on/after('*', handler) are called by bound and unbound events.
- [cds-runtime@2.1.0] Expanding association from draft-enabled entity to draft enabled entities always provides active version of the expanded entity.
- [cds-runtime@2.1.0] If you export a function in an `init.js` file, it will be called with the primary database and its result is awaited.
- [cds-runtime@2.1.0] REST: Since the service is now based on the `cds.Service` base class, all convenience functions (`create`, `post`, etc.) are streamlined.
- [cds-runtime@2.1.0] Messaging: Only one queue per app is created, as opposed to one queue per app and external service.
- [cds-runtime@2.1.0] Messaging: You can now directly connect to the (technical) messaging service through `await cds.connect.to('messaging')`, no topic names will be generated here.
- [cds-runtime@2.1.0] Messaging: If you want to link your own or external services to messaging, you need to model your events in CDS.
- [cds-runtime@2.1.0] Messaging: If you want to provide custom topics for modeled events, you need add the `@topic` annotation to the event.
- [cds-runtime@2.1.0] Messaging: The `prefix` option in the service's credentials is prepended to events, which have a `@topic` annotation.
- [cds-runtime@2.1.0] Messaging: The syntax to emit events with headers changed:js

```
srv.emit({ event: 'yourEvent',
           data: { some: 'data' },
           headers: { some: 'headers' }})
```
- [cds-runtime@2.1.0] Messaging: The default file for `file-based-messaging` is ~/.cds-msg-box.
- [cds-runtime@2.1.0] Streamlined handler registration: `srv.before/on/after(, ?, )`Event and handler are mandatory, entity must be omitted if unbound action/function (CREATE, READ, UPDATE, DELETE are considered to be bound)
- Event and entity may be arrayed
- `srv.before/on/after(*, )` matches all as shorthand

- [cds-runtime@2.1.0] `INSERT` statements return an object or array of objects (in case of bulk) with the number of affected rows as result of `valueOf()`, as well as the keys of the inserted entities:js

```
const res = await srv.run(INSERT.into('Books').entries([{ ID: 1, title: 'one' }, { ID: 2, title: 'two' }]))
res > 1 // > true
res.keys // > [{ ID: 1 }, { ID: 2 }]
```
- [cds-runtime@2.0.3] on() function for joins doesn't support the simple conditions like on(x, =, y) anymore. Only fluent expressions and object predicates are supported.
- [cds-runtime@2.0.2] CQN returned for req.query changed — for requests with path expressions the returned CQN of req.query is changed to a simplified format. For `GET /Authors(150)/books` the CQN contains the path in `.from` instead of an `exists` clause in `.where`.

js

```
{ SELECT:  {  from: { "ref": [
        {
          "id": "AdminService.Authors",
          "where": [ { "val": 150 } ]
        },
      "books"
      ] } } }
```

- [cds-runtime@2.0.2] Authorizations as whitelist: if any restrictions exist for the target, all not explicitly allowed operations are forbidden (for example, `@restrict: [{ grant: 'READ', ... }]` -> everything but `READ` is forbidden for all, including bound actions and functions)
- [cds-runtime@2.0.2] Applicable `@requires` and `@restrict` definitions concatenated by AND
- [cds-runtime@2.0.2] Reference to undefined XSUAA user attribute in `@restrict.where` results in forbidden
- [cds-runtime@2.0.2] `req.event` for unbound actions and functions is provided without service prefix
- [cds-runtime@2.0.2] Increased logging in production (temporarily until revised logging concept is implemented)
- [cds-runtime@2.0.2] `cds.serve(..., { passport: [...] }` -> `cds.serve(..., { auth: [...] }`
- [cds-runtime@2.0.1] Passport strategy whitelist: `mock` and `JWT`
- [cds-runtime@2.0.1] Authentication not needed for calls to a service's root or metadata endpoints
- [cds-runtime@2.0.1] Support for "public" entities and actions (that means, no restrictions) in services without `@requires` but other entities and/or actions with `@restrict`
- [cds-runtime@2.0.0] Update major version number
- [cds-runtime@1.2.0] Slightly improved performance for `$expand`
- [cds-runtime@1.2.0] Return key values (single key only) of created entries instead of number of affected rows
- [cds-runtime@1.2.0] Annotations `@cds.onInsert` and `@cds.onUpdate` ignore values from the request
- [cds-runtime@1.2.0] Processing of read-only values moved to initial before handler
- [cds-runtime@1.2.0] Aligned handling of virtual, computed, read-only, immutable with java runtime
- [cds-runtime@1.2.0] Allow deep insert on to one association with non-key property, the non-key property is silently ignored
- [cds-sidecar-client@1.1.6] Login/logout: Improved logging
- [cds-sidecar-client@1.1.6] Login/logout: Renamed command line options for clarity
- [cds-sidecar-client@1.1.6] Login/logout: Changed location of settings files to adhere to platform standards

### Fixed ​

- [cds-dk@2.0.8] Fixed `cds add mta` for java projects. The Spring Cloud Profile is set by default for Java apps in order to enable the SAP HANA service binding, otherwise the sqlite db would still be used at runtime. The environment variable `JBP_CONFIG_RESOURCE_CONFIGURATION` required by the classic Java runtime has been removed.
- [cds-dk@2.0.7] Fixed `cds import` to support imports from symlinked sources
- [cds-dk@2.0.7] Fixing bug in `cds init` and `cds add` when using multiple features separated by comma.
- [cds-dk@2.0.7] Fixing missing log output bug in `cds init` and `cds add` when using feature `samples`.
- [cds-dk@2.0.7] `cds add mta` does no longer crash if no package.json file exists.
- [cds-dk@1.8.6] Simplified `cds env` calculation during `cds init` and `cds add`.
- [cds-dk@1.8.4] An issue in `@sap/edm-converters` with missing entity sets
- [cds-dk@1.8.2] An issue in `@sap/edm-converters` with missing entity sets
- [cds-dk@1.8.1] An issue in `@sap/edm-converters` with missing entity sets
- [vscode-cds@2.4.0] enum keyword was wrongly syntax highlighted
- [vscode-cds@2.4.0] when an ignored source file is closed, potential messages are wiped
- [vscode-cds@2.4.0] annotations of extensions weren't indexed
- [vscode-cds@2.4.0] bug fixes
- [vscode-cds@2.3.3] syntax highlighting: colorize identifiers, including variants delimited with ![...]
- [vscode-cds@2.3.3] minor clean-up in welcome page handling
- [cds-compiler@1.35.0] Properly consider targets of compositions in `mixin`s to be autoexposed.
- [cds-compiler@1.35.0] Uniformly limit propagation of `@cds.autoexposed`, that means, there isn't inheritance from a query source navigating along an association. Previously, compiling a compiled model could lead to new autoexposed entities.
- [cds-compiler@1.35.0] OData: V2: Distribute various `@sap` specific annotations to the entity container.
- Always set attribute `Nullable` on properties of type `Collection()`.

- [cds-compiler@1.35.0] Don't dump with illegal references in explicit `on` conditions of redirections; properly report them via error messages.
- [cds-compiler@1.35.0] forHana: Correctly flatten managed associations as foreign keys used in the definition. of another managed association.
- [cds-compiler@1.35.0] OData: Don't render aspects as `edm.ComplexType`.
- [cds-compiler@1.35.0] parseCdl: Fix missing extensions in files that extend unknown services/contexts.
- [cds-compiler@1.35.0] OData: Don't render an EDM document in case of raised errors
- [cds-compiler@1.35.0] to.cdl: Aspects are now correctly rendered as aspects and not as types
- [cds-compiler@1.35.0] SAP HANA/SQLite: Correctly handle already resolved types when a cds.linked CSN is passed in
- [cds-compiler@1.35.0] SAP HANA/SQLite: Ensure that all elements in a Draft are nonvirtual
- [cds-compiler@1.35.0] An error is emitted if parameters in functions/actions have a default value as it isn't yet supported. For example by using `type of E:element` where `element` has a default value.
- [cds-compiler@1.35.0] OData V2: Derived scalar types aren't rendered as ``, so no annotation assignments to such carriers must be rendered.
- [cds-compiler@1.35.0] SAP HANA/SQLite: Fixed a bug when flattening structured elements - instead of a human-readable error, an exception was thrown.
- [cds-compiler@1.35.0] `doc` comments in CDL now support Windows-style line breaks (CRLF). They're replaced with `\n` in CSN.
- [cds-compiler@1.35.0] `toCdl` no longer renders a `*` column if no columns are used in the original source.
- [cds-compiler@1.35.0] Types that have both `type` and `items`/`elements` properties in CSN are now checked to avoid mismatches if an unstructured / non-arrayed type is referenced but `items`/`elements` exists.
- [cds-compiler@1.35.0] OData: Correctly render CRLF and LF to  in EDMX

- [cds-compiler@1.35.0] Memory usage improvement - compile messages with id `ref-undefined-excluding` uses much less memory.
- [cds-compiler@1.35.0] SAP HANA/SQL: Validate ON conditions of mixin association definitions in all subqueries
- [cds-compiler@1.35.0] OData V2: Assign various `@sap` annotations to the `` and `` if such annotations are assigned to CDS entities or associations.
- [cds-compiler@1.35.0] OData V4 Structured: Omit foreign keys of managed associations that establish the containment relationship to a container, if this association was declared to be primary key.
- [cds-compiler@1.35.0] OData: Warn about non-integer enums as they aren't supported by OData, yet.
- [cds-compiler@1.35.0] Warn about string values in integer enums and vice versa.
- [cds-compiler@1.35.0] OData: Render vocabulary `` and `` if vocabulary namespace was used.
- Reduce memory consumption in EDM Renderer.
- Render annotations for navigation properties if association is annotated with `@cds.api.ignore: true`.

- [cds-compiler@1.35.0] Memory usage improvement - compile messages don't inherit from Error anymore.
- [cds-compiler@1.35.0] SAP HANA types in annotation assignments work again.
- [cds-compiler@1.35.0] SAP HANA/SQL: Correctly handle temporal in conjunction with namespaces.
- [cds-compiler@1.35.0] Fix a bug in Association to Join translation that prevents exposing managed associations via subqueries.
- [cds-compiler@1.35.0] The CSN `val` property is now allowed in enum element extensions. Such CSN can be generated using the `parseCdl` mode and it's now compilable.
- [cds-compiler@1.35.0] Again allow negative values as enum values, fixing a regression introduced with v1.24.6.
- [cds-compiler@1.35.0] OData: Correctly handle associations in arrayed elements (keyword `many`).
- [cds-compiler@1.35.0] Annotation assignment checks now recognize SAP HANA types.
- [cds@4.1.5] Fiori preview is now working again with the latest version of SAP UI5.
- [cds@4.1.5] Use latest SAP CommonCryptoLib help — when SAP CommonCryptoLib is missing during `cds deploy --to hana`.
- [cds@4.1.5] `sql_mapping` is only written to csn.json if the classic Java runtime and no default naming is used.
- [cds@4.1.5] Fiori dev support in `cds run` now also honors `/v2` URLs. These are installed by default by the `@sap/cds-odata-v2-adapter-proxy`.
- [cds@4.1.5] npm scripts that wrap around cds-dk commands like `cds watch` now also work on Windows. Previously they couldn't find the cds command.
- [cds@4.1.5] When extracting the base model of a multi-tenant application `cds build` now ensures that only files having project scope are copied, a warning is logged otherwise.
- [cds@4.1.5] `cds build` now no longer crashes if exactly one custom language is given in `options.lang` of the `java-cf` build task.
- [cds@4.1.5] `cds compile` now fails with a non-zero exit code in case of compilation errors.
- [cds@3.34.2] The `UI.Identification` annotation for `sap.common.CodeList` got a correct value, pointing to its `name` element.
- [cds@3.34.2] Configuration `requires..credentials.destination` is now preserved again when running with `VCAP_SERVICES`. In version 3.34.1, it was cleared.
- [cds@3.34.2] Entities annotated with `@cds.persistence.skip:if-unused` (like `sap.common.Languages`) now again are skipped when compiling to SAP HANA output. This got broken in previous versions when using the new compiler APIs.
- [cds@3.34.2] `sql_mapping` is again written to csn.json as it's required by classic Java runtime.
- [cds@3.34.2] default-env.json is now read even in production, which is in line with the behavior of other modules that honor this file. Real prod environments like CF will still overwrite these defaults.
- [cds@3.34.2] `cds build` caused error `invalid option` — when passing command line options like `log-level`, `src`, or `for`.
- [cds.java@1.8.1] Fixed a bug that caused a `NullPointerException` when opening a new transaction in some scenarios.
- [cds.java@1.8.1] Fixed a bug that caused a `IllegalStateException` during application startup, when the property `cds.security.xsuaa.serviceName` was specified.
- [cds.java@1.8.0] The error message that occurs, when an OData V4 request payload is invalid, now again contains a hint, which field is invalid.
- [cds.java@1.8.0] Fixed a bug, that caused the `.gitignore` file to not be part of new projects generated by the archetype.
- [cds.java@1.8.0] Fixed a bug in goal `generate` of cds-maven-plugin, that caused using a wrong csn.json for Java source code generation.
- [cds.java@1.8.0] Fixed performance problems that could occur when querying a draft enabled entity
- [cds.java@1.8.0] Fixed a bug where fields in result were removed when ordering a draft enabled entity
- [cds.java@1.8.0] Fixed expands from nondraft to draft entity
- [cds.java@1.8.0] Fixed usage of subqueries for draft protection where user information wasn't provided through parameters but plain strings
- [cds.java@1.8.0] Fixed a bug that caused queries using `COUNT(*)`, for example, OData's `/$count` to fail on SAP HANA databases
- [cds.java@1.8.0] Fixed a bug that caused PUT requests and actions to fail on etag-enabled entities on SAP HANA.
- [cds.java@1.8.0] Fixed a bug that caused a `ConcurrentModificationException`, when reading entity collection through OData V4.
- [cds.java@1.8.0] Fixed a bug that caused initialization of a transaction, when accessing the `CdsDataStore` from the `PersistenceService`.
- [cds.java@1.8.0] Ensured that `afterClose()` of a `ChangeSetListener` is called, even if the completion of the ChangeSet fails.
- [cds.java@1.8.0] The `UPDATE` event no longer changes draft-enabled entities in draft-mode (`IsActiveEntity=false`).
- [cds4j@1.12.0] Improve parameter handling
- [cds4j@1.12.0] Improve Performance Suppress additional query for inline count if possible
- SQL generation
- Finding annotations
- Use joins to expand to-one associations

- [cds-runtime@2.1.5] `req._.req` in `SAVE` handler
- [cds-runtime@2.1.5] Insert duplicate data during deep update
- [cds-runtime@2.1.5] SAP HANA: prefer `this.options.credentials`
- [cds-runtime@2.1.5] `$orderBy` in case of `DRAFT` with `Union`
- [cds-runtime@2.1.5] fixed POST via multiple navigations
- [cds-runtime@2.1.4] Large numbers of expands (>26)
- [cds-runtime@2.1.4] Reference integrity check for `DELETE`
- [cds-runtime@2.1.4] Localized in combination with draft
- [cds-runtime@2.1.4] Propagate @cds.localized:false during deep reads (currently limited to one expand)
- [cds-runtime@2.1.4] Fetch specific credentials from multiple xsuaa bindings via `requires.uaa.vcap`
- [cds-runtime@2.1.4] Static values in custom backlinks of compositions
- [cds-runtime@2.1.3] Streaming of null values and not found entities
- [cds-runtime@2.1.3] Temporal session contexts on SAP HANA
- [cds-runtime@2.1.2] SAP HANA credentials handling
- [cds-runtime@2.1.1] SAP HANA pooling with instance manager
- [cds-runtime@2.1.0] Retrieve performance information via `sap-statistics` header in case of batch requests
- [cds-runtime@2.1.0] Direct user authentication challenges in case of /$batch
- [cds-runtime@2.1.0] HTTP error codes from custom handler aren't filtered anymore if in 300...500 range
- [cds-runtime@2.1.0] following projection with undefined name in target entity
- [cds-runtime@2.1.0] Lists and null values in where with fluent expressions
- [cds-runtime@2.0.3] SAP Event Mesh: Received messages are correctly decoded
- [cds-runtime@2.0.3] Reading single properties of draft enabled entities via navigations e. g. `/E0(ID=,IsActiveEntity=false)/e1(ID=,IsActiveEntity=false)/property`
- [cds-runtime@2.0.3] not supported transformation in groupby throws cryptic error
- [cds-runtime@2.0.3] etag check only if odata request
- [cds-runtime@2.0.3] Reading single properties of draft enabled entities via navigations, for example, `/E0(ID=,IsActiveEntity=false)/e1(ID=,IsActiveEntity=false)/property`
- [cds-runtime@2.0.3] Statements if path expression contains keys of type `cds.Timestamp`, `cds.DateTime`, or `cds.Time`
- [cds-runtime@2.0.3] `$filter` lambda `any` operator if no argument is provided
- [cds-runtime@2.0.3] User attributes in `req.user.attr` merge `info.userInfo` and `info.userAttributes` (authentication strategy `JWT`)
- [cds-runtime@2.0.3] User authentication challenges
- [cds-runtime@2.0.2] `INSERT.into.as(SELECT.from...)` with `SELECT` containing placeholders
- [cds-runtime@2.0.2] Requests on a navigation to many with key provided returns 404 if the resource doesn't exist
- [cds-runtime@2.0.2] POST/PATCH requests on `Composition of many` with backlink association as key
- [cds-runtime@2.0.2] Path expressions on SAP HANA are now flat and not structured anymore
- [cds-runtime@2.0.2] `$expand` on `Composition of many` with backlink association as key
- [cds-runtime@2.0.2] Roles from scopes including "."
- [cds-runtime@2.0.2] Ignore unknown arrayed column during input validation
- [cds-runtime@2.0.2] Too early client release
- [cds-runtime@2.0.2] Pool configurations with default values can be set to `0`
- [cds-runtime@2.0.1] `target` added to assert errors
- [cds-runtime@1.2.0] Resolved some performance issues with `@sap/hana-client`
- [cds-runtime@1.2.0] `$filter=false or ...` is now possible
- [cds-runtime@1.2.0] Custom handler registration in multi tenant scenario
- [cds-runtime@1.2.0] Alias in associations wasn't processed correctly in post processing
- [cds-runtime@1.2.0] `$search` is now applied on the query result of `$apply` as specified in OData V4 spec
- [cds-runtime@1.2.0] `evictionRunIntervalMillisForPools` is now treated properly
- [cds-runtime@1.2.0] Searching for `_` or `%` in `$filter` queries with `contains`/`startswith`/`endswith`
- [cds-runtime@1.2.0] Insert of to-one associations with structured elements
- [cds-sidecar-client@1.1.6] Activate: Corrected exclusion of files from upload
- [cds-odata-v2-adapter-proxy@1.4.40] Fix aggregation grouping on filtered elements
- [cds-odata-v2-adapter-proxy@1.4.40] Support `sap:` analytical annotations
- [cds-odata-v2-adapter-proxy@1.4.39] Move annotation ContentDisposition.Filename to data element
- [cds-odata-v2-adapter-proxy@1.4.39] Improve stability of content disposition
- [cds-odata-v2-adapter-proxy@1.4.38] Fix `base` proxy option (follow-up)

### Removed ​

- [cds@4.1.5] `db.disconnect()` → no replacement; no need to disconnect before shutdown.
- [cds@4.1.5] `db.run(()=>{})` → use `cds.run([...multiple queries])` instead.

The previous changes affect undocumented internal implementations, and hence shouldn't affect CAP-based projects. Nevertheless, they're listed here for your reference.

- [cds-runtime@2.1.1] `req.isDraftChange`, , and `req.draftMetadata` in draft-related handlers
- [cds-runtime@2.1.0] Support for run block (`tx.run(() => {})`)
- [cds-runtime@2.0.3] Support for nested user attributes in `@restrict.where`, for example, `$user.name.familyName`
- [cds-runtime@2.0.2] Support for annotation `@cds.persistence.name`
- [cds-runtime@2.0.2] Deprecated SQL dialect `hdbcds`

## June 2020 ​

### Added ​

- [cap.java@1.7.0] Adding CDS Element annotation `@assert.range` on enum elements now validates the input against valid enum values.
- [cap.java@1.7.0] CQN statements querying services defined in the CDS model are augmented with an order by automatically (implicit sorting). The default order by uses the key elements of the target entity and, if the target is a view, the order by definition of the view.
- [cap.java@1.7.0] Read requests on OData singletons are now supported. Limitations are, that navigations from singletons to other entities (for example, `OldestAuthor/books` and CRUD operations don't work out of the box yet.
- [cap.java@1.7.0] ETag conditions on `$metadata` endpoints are now evaluated. OData Responses also now contain the `@metadataEtag` field.
- [cap.java@1.7.0] ETag conditions on OData bound action or function requests are now evaluated.
- [cap.java@1.7.0] ETag conditions evaluated through selection, now lock the affected row for update.
- [cap.java@1.7.0] The OData entity response field `@etag` (>= 4.01) or `@odata.etag` (4.0) is now set when returning collections of entities or expanded entities that have an ETag.
- [cap.java@1.7.0] OData collection requests now automatically apply implicit server-driven paging, if the number of requested entities exceeds a maximum value of 1,000. The maximum value can be controlled through property `cds.query.limit.max` or annotation `@cds.query.limit.max`. In addition, a default page size can be set through `cds.query.limit.default` and `@cds.query.limit.default`.
- [cap.java@1.7.0] The OData system query parameters (for example, `$select`, `$expand`) are now available through the method `ParameterInfo.getQueryParameters()` when processing OData requests.
- [cap.java@1.7.0] UUIDs in OData requests are now normalized by converting them to lowercase.
- [cap.java@1.7.0] The multitenancy feature now supports asynchronous subscriptions.
- [cap.java@1.7.0] New API to register event handler methods on all services or on all services of a specific type.
- [cap.java@1.7.0] New API to register services and event handlers as additional modules loaded through `ServiceLoader`.
- [cap.java@1.7.0] New API to allow creation of custom services, and to enable them to be registered as Spring beans directly.
- [cap.java@1.7.0] Enabled running CAP applications without a JDBC datasource configuration.
- [cap.java@1.7.0] Added support for `$orderby`, `$top`, and `$skip` for draft enabled entities.
- [cap.java@1.7.0] Added several new goals to CDS Maven Plugin: Install Node.js in a specified version
- Install CDS Development Kit in a specified version
- Perform arbitrary CDS commands on a CAP Java project
- Generate Java classes for type safe access
- Clean your CAP Java project from artifacts of previous build

- [cap.java@1.7.0] Adapted `cds-services-archetype` to `use cds-maven-plugin` in generated CAP Java projects
- [cds4j@1.11.0] Support parameterized views on SAP HANA
- [cds4j@1.11.0] Support limit and offset in expand
- [cds4j@1.11.0] Support modifying limit and offset of select
- [cds4j@1.11.0] Support default `$now` (Instant) value on insert
- [cds4j@1.11.0] Result Builder API
- [odata-server@1.8.1] license file: developer-license-3.1.txt
- [vscode-cds@2.3.3] added properties `dest` and `mtx` to code completion list for `tasks` and `for` in CAP project package.json files

### Changed ​

- [cap.java@1.7.0] Replaced the `CdsRuntimeBuilder` with the `CdsRuntimeConfigurer`, allowing the `CdsRuntime` to be incrementally built and configured.
- [cds4j@1.11.0] Lock statements on SQLite are silently ignored and executed as select queries instead of throwing an exception.

### Fixed ​

- [cap.java@1.7.0] Fixed a bug where exception messages of non-framework exceptions were displayed to the end user, despite noncustom error messages being disabled.
- [cap.java@1.7.0] Fixed a bug where a null OData function argument value caused a `NullPointerException`.
- [cap.java@1.7.0] Fixed a misleading error message when patching an entity in draft state with a nested JSON structure.
- [cap.java@1.7.0] Fixed a bug where multiple Spring contexts caused the CAP spring integration to prevent the app from being started.
- [cds4j@1.11.0] Throw `UnsupportedOperationException` on deep updates with more than one entry.
- [cds4j@1.11.0] SQL missing parameter exception when using literals in `orderBy`.
- [cds4j@1.11.0] Allow to modify `CqnElementRefs` w/o alias through `CqnModifier.selectListItem`.
- [cds4j@1.11.0] Remove unused `CqnModifier.expand` w/o `orderBy` and `limit`.
- [odata-server@1.8.2] added license file to "files" in package.json
- [cds-odata-v2-adapter-proxy@1.4.37] Replace 'pathRewrite' option by 'targetPath' option
- [cds-odata-v2-adapter-proxy@1.4.37] Fix 'base' proxy option
- [cds-odata-v2-adapter-proxy@1.4.37] Respect OData annotation '@odata.Type'
- [cds-odata-v2-adapter-proxy@1.4.37] Alternative annotation @Common.ContentDisposition.Filename
- [cds-odata-v2-adapter-proxy@1.4.36] Fix escaping of quote for function parameters
- [cds-odata-v2-adapter-proxy@1.4.36] SAP Fiori Elements v2 sample app
- [cds-odata-v2-adapter-proxy@1.4.35] Fix reserved uri characters (follow-up)
- [cds-odata-v2-adapter-proxy@1.4.34] Fix entity key with (encoded) reserved uri characters

## May 2020 ​

### Added ​

- [cds.java@1.6.0] Enhanced temporal data support: allow date only values (for example, `2020-04-24`) for `sap-valid-from`, `sap-valid-to`, and `sap-valid-at` request parameters
- [cds.java@1.6.0] Support OData V4 GET requests with `$value` URI suffix on primitive entity properties.
- [cds.java@1.6.0] Adding CDS Element annotation `@assert.format` with a Regular Expression now validates string elements.
- [cds.java@1.6.0] Adding CDS Element annotation `@assert.range` now validates ranges on simple data types, numbers, and temporal types.
- [cds.java@1.6.0] Grants for draft events such as `draftEdit`, `DRAFT_CANCEL`, or `DRAFT_NEW` etc. are derived from grants of standard CQN events. For instance, granted event `CREATE` implies also `DRAFT_NEW`. Before that, draft events had to be listed in all relevant `@restrict` annotations in order to allow access.
- [cds.java@1.6.0] Enhanced CSV file import with configurable file locations, more flexible header line delimiters (';' or ',') and more detailed error messages.
- [cds.java@1.6.0] Added a main class to start a DB deployment in MT scenario, which could be executed as task in Cloud Foundry.
- [cds4j@1.10.0] Copy & modify CQL statements through `CQL.copy`
- [cds4j@1.10.0] Support count in CQL builder through `CQL.count()`
- [cds4j@1.10.0] Support case insensitive contains
- [cds4j@1.10.0] Support collation on SAP HANA providing lexicographical comparison and sorting of strings
- [cds4j@1.10.0] Support case-insensitive comparison and sorting of strings on SQLite
- [cds4j@1.10.0] Streaming for `LargeString` and `LargeBinary` types annotated with `@Core.MediaType`
- [cds4j@1.10.0] Support `saptrc` and `sappsd` locales and remove default `en` locale
- [cds4j@1.10.0] Generate UUID values on input if no value is provided
- [cds4j@1.10.0] Extend `CqnStatement` with is/as methods
- [cds4j@1.10.0] Support `CqnUpdate` in `CqnAnalyzer`
- [cds4j@1.10.0] Support new `@cds.search` annotation
- [cds4j@1.10.0] Reflection API Support reading CDS Models from CSN
- Read parameters of views
- Read Enum types
- Read meta properties from CSN

- [cds4j@1.10.0] Code Generator Support Arrayed Types
- Support Streaming of Media Types

- [odata-server@1.8.0] support for server-driven paging and next links in expanded navigation properties
- [odata-server@1.8.0] support for $count option in $expand
- [odata-server@1.8.0] allows double quotes around * in If-Match and If-None-Match headers

### Changed ​

- [cds.java@1.6.0] Instance-based authorization is active by default now, that means, `where` conditions of `@restrict`-annotated entities are evaluated for events `READ`, `UPDATE`, and `DELETE`. There are still some limitations with paths in the `where` condition.
- [cds4j@1.10.0] Lowercase UUID values on input
- [cds4j@1.10.0] Deprecate usage of expressions in limit and offset
- [cds4j@1.10.0] Remove null values from data json
- [cds4j@1.10.0] Refactor `SelectListItems`
- [cds@3.34.2] Use `cds.hana.deploy-format`=`hdbtable` instead of `cds.hana.syntax` to switch deployment from `hdbcds` to `hdbtable` for SAP HANA Cloud.
- [cds@3.34.2] `cds run` now supports relative `dataSource` URLs in SAP UI5 manifests again, so that UI5 apps can be served w/o App Router. This support is only active in development mode.
- [cds@3.34.2] `cds deploy --to hana` changes kind to `hana` only if it isn't already `sql`
- [cds-dk@1.8.5] `cds init` uses latest `Maven Java archetype` version `1.6.0` for creating Java projects.
- [cds-dk@1.8.4] `cds init` uses latest `Maven Java archetype` version `1.5.2` for creating Java projects.
- [odata-server@1.8.0] log stacktrace for server errors with level error (#107)

### Fixed ​

- [cds.java@1.6.0] Fixed server error on malformed OData requests with unknown actions or functions.
- [cds.java@1.6.0] The `where` condition of `@restrict` won't apply anymore for draft entities on events `READ`, `DELETE`, and `UPDATE`. This allows to create and edit drafts not matching the condition.
- [cds.java@1.6.0] The default ON-handlers for AuthorizationService now have a proper default order number, which allows to override them.
- [cds.java@1.6.0] Improved the error message for unsupported star expand on draft enabled entities
- [cds.java@1.5.2] Fixed a bug where inlineCount wasn't set correctly when the $count OData function was used
- [cds.java@1.5.2] Fixed a bug where the handling of the CDS Maven Plugin version in the archetype wasn't correct
- [cds.java@1.5.1] Generate missing Javadoc and Source JARs for `cds-maven-plugin` to enable upload to central Maven repository.
- [cds4j@1.10.0] Fix date conversion in multithreading scenarios
- [cds@3.34.2] The `UI.Identification` annotation for `sap.common.CodeList` got a correct value, pointing to its `name` element.
- [cds@3.34.2] Configuration `requires..credentials.destination` is now preserved again when running with `VCAP_SERVICES`. In version 3.34.1, it was cleared.
- [cds@3.34.2] Entities annotated with `@cds.persistence.skip:if-unused` (like `sap.common.Languages`) now again are skipped when compiling to SAP HANA output. This got broken in previous versions when using the new compiler APIs.
- [cds@3.34.2] `sql_mapping` is again written to csn.json as it's required by classic Java runtime.
- [cds@3.34.2] default-env.json is now read even in production, which is in line with the behavior of other modules that honor this file. Real prod environments like CF will still overwrite these defaults.
- [cds@3.34.2] `cds build` caused error `invalid option` — when passing command line options like `log-level`, `src`, or `for`.
- [cds-dk@1.8.2] An issue in `@sap/edm-converters` with missing entity sets
- [odata-server@1.8.0] status code 200 OK instead of 304 Not Modified for GET requests without If-None-Match header (#106)
- [odata-server@1.8.0] $expand with complex-property path
- [cds-odata-v2-adapter-proxy@1.4.33] Service Document in XML format (default)
- [cds-odata-v2-adapter-proxy@1.4.33] Update dependencies
- [cds-odata-v2-adapter-proxy@1.4.33] Disable network log per default
- [cds-odata-v2-adapter-proxy@1.4.32] Update dependencies
- [cds-odata-v2-adapter-proxy@1.4.32] Update README on localization
- [cds-odata-v2-adapter-proxy@1.4.32] Toggle switch for network logging
- [cds-odata-v2-adapter-proxy@1.4.32] Allow SAP HANA SYSUUID as UUID
- [cds-odata-v2-adapter-proxy@1.4.31] Align model resolving
- [cds-odata-v2-adapter-proxy@1.4.31] Fix data types conversion for numbers
- [cds-odata-v2-adapter-proxy@1.4.31] Fix data types recognition in functions
- [cds-odata-v2-adapter-proxy@1.4.31] Support response compression
- [cds-odata-v2-adapter-proxy@1.4.31] Prevent unnecessary data serialization for tracing
- [cds-odata-v2-adapter-proxy@1.4.31] Performance optimization for entity key/uri calculation
- [cds-odata-v2-adapter-proxy@1.4.31] General performance optimizations
- [cds-odata-v2-adapter-proxy@1.4.31] Update dependencies
- [cds-odata-v2-adapter-proxy@1.4.30] Make function call with request body more robust
- [cds-odata-v2-adapter-proxy@1.4.30] Fallback severity for detail messages to error
- [cds-odata-v2-adapter-proxy@1.4.30] Keep request body for action call
- [cds-odata-v2-adapter-proxy@1.4.30] Update README on Cloud Foundry deployment

## April 2020 ​

### Added ​

- [cds.java@1.5.0] Draft locks now expire after a default timeout of 15 minutes. The locked entity can be reclaimed by other users after that timeout. The timeout duration is configurable via `cds.drafts.cancellationTimeout`
- [cds.java@1.5.0] ETags are now supported via OData V4
- [cds.java@1.5.0] Support for `$select` and `$expand` on actions and functions in OData V4, ensuring compatibility with SAP UI5 >= 1.76.0
- [cds.java@1.5.0] OData V4 error messages listed in the details section of an error response now have the fields `@Common.numericSeverity` and optionally `@Common.longtextUrl`, improving SAP Fiori compatibility
- [cds.java@1.5.0] A Spring property metadata files is now part of our `cds-framework-spring-boot` JAR. This enables code completion and suggestions of `cds` properties in Spring configuration files, if corresponding IDE plugins are installed (see https://spring.io/tools)
- [cds.java@1.5.0] Added localization capabilities for error messages written by the CAP Java SDK
- [cds.java@1.5.0] Added possibility to disable non-localized error messages and only return HTTP-based status codes to clients by setting `cds.errors.stackMessages.enabled: false`
- [cds.java@1.5.0] Added possibility to log enhanced error messages, indicating more information about the event that caused the error and its parameters, by setting `cds.errors.extended: true`
- [cds.java@1.5.0] Enabled type-safe access to additional attributes specific to an authentication strategy (for example, email attribute in JWT). These attributes can also be mocked in the mock-user scenario, using the property `additional` in the mock-user definition.
- [cds.java@1.5.0] Introduced a new `DRAFT_CREATE` event, which is triggered both by a `DRAFT_NEW` and `DRAFT_EDIT` event. Its ON handler by default persists the draft data in the draft table.
- [cds.java@1.5.0] Added a new technical startup Service, which allows to register on events, triggered when the application is prepared (shortly before HTTP port is opened) or started
- [cds.java@1.5.0] New maven plugin `cds-maven-plugin`, providing goals to add additional content to applications generated by the `cds-services-archetype`.
- [cds.java@1.5.0] During archetype project generation, the option -DincludeIntegrationTest can be used to generate an additional integration-tests module.
- [cds4j@1.9.0] Support inline count
- [cds4j@1.9.0] Support where exists
- [cds4j@1.9.0] Support default values for virtual elements
- [cds4j@1.9.0] Support setting writes locks (not supported on SQLite)
- [cds4j@1.9.0] Support `@cds.localized` annotation
- [cds4j@1.9.0] Copy & modify CqnPredicates via `CQL.copy`
- [cds4j@1.9.0] Enhance expression parser
- [cds4j@1.9.0] Enhance copying of CqnStatements: copy refs
- [cds4j@1.9.0] Enhance CqnAnalyzer to return root info and support extracting keys from `in` predicates
- [cds4j@1.9.0] Add StructuredTypeRef with modifiable segments
- [cds4j@1.9.0] Make ElementRef.segments() return modifiable RefSegment
- [cds4j@1.9.0] Reflection API: Support Enum Types
- [cds4j@1.9.0] Code Generator: `@cds.java.extends` annotation to define super-interfaces for generated accessor interfaces
- [cds@3.34.0] `cds version` option `-ls` prints an `npm ls` subtree.
- [cds@3.34.0] `cds serve` / `run` now also accept package names as arguments, for example, `cds serve --project @capire/bookshop`.
- [cds@3.34.0] `cds compile` option `--parse` provides minimal, parsed-only CSN output.
- [cds@3.34.0] New Node.js method `cds.compile.cdl()` allows compiling CDS sources in-process.
- [cds@3.34.0] `cds build` now supports cds configuration `requires.db.kind:"sql"`, which allows seamless production deployments using SAP HANA db and development deployments using sqlite db.
- [cds@3.34.0] Default maximum query size limit of 1000 (overridable via `@cds.query.limit.max`).
- [cds@3.34.0] Improved error message during `cds deploy` on Windows when `SAP CommonCryptoLib` is missing.
- [cds@3.34.0] `cds build` now checks that `entity-whitelist` and `service-whitelist` have been defined for SaaS applications - a warning is reported otherwise. `cds build` will fail if invalid entries exist.
- [cds@3.34.0] Parameter `--vcap-file` lets `cds deploy --to hana` use an existing default-env.json file for the deployment credentials, instead of always creating new credentials from Cloud Foundry. Note that this is a beta feature.
- [cds@3.34.0] `cds build --log-level` allows to choose which messages to see, default log level is `warn`.
- [cds@3.34.0] Labels of `@sap/cds/common` texts are now available in many languages
- [cds-dk@1.8.0] `cds watch` now also accepts package names as arguments, for example, `cds w @capire/bookshop`.
- [cds-dk@1.8.0] `cds add mta` now supports cds configuration `requires.db.kind:"sql"`, which allows seamless production deployments using SAP HANA db while keeping SQLite for local development scenario.
- [cds-compiler@1.26.2] The client tool `cdsc` has a new option `--beta `, which can be used to specify a comma-separated list of experimental features to be enabled.
- [cds-compiler@1.26.2] CSN in parse-cdl mode now has a `requires` property that represents `using`s from CDL.
- [cds-compiler@1.26.2] The client tool `cdsc` has a new command `parseCdl`, which returns a CSN that is close to the original CDL file. It doesn't resolve imports and doesn't apply extensions.
- [cds-compiler@1.26.2] Unmanaged associations as primary keys are now warned about.
- [cds-compiler@1.26.2] `localized` in combination with `key` is now warned about.
- [cds-compiler@1.26.2] Enum values are now checked to only be either numbers or strings - a warning is raised.
- [cds-compiler@1.26.2] Elements in mixin clauses that aren't_ unmanaged associations now produce an error.
- [cds-compiler@1.26.2] Support function calls like `count( distinct ... )` and `count( all ... )`.
- _[cds-compiler@1.24.2 With option comments of the form is preserved, if these comments appear at positions where annotation assignments are allowed. `doc` comments are propagated like annotations until an empty comment `/***/` disrupts the propagation.
- [cds-compiler@1.26.2] OData: Add new OData vocabularies `com.sap.vocabularies.Graph.v1` and `com.sap.vocabularies.ODM.v1`
- With option `--odata-containment`, `parent` association and inferred key elements for `composition of ` as well as inferred keys of `_texts` entities aren't rendered.
- OData V4: Produce primary key paths with length limited alias names.

- [cds-compiler@1.26.2] Add new OData vocabulary `com.sap.vocabularies.odm.v1`
- [cds-compiler@1.26.2] If an entity `E` with localized elements has the annotation `@fiori.draft.enabled`, a new element `ID_texts` of type `cds.UUID` is added to `E_texts` as the only key and the annotation `@odata.draft.enabled` won't be set to false for `E.texts`.
- [cds-compiler@1.26.2] A comment of the form `/**…*/` at "annotation positions" is now considered a doc comment; its "cleaned-up" text is put into the CSN as value of the property `doc`. In the OData/EDMX, it appears as value for the annotation `@Core.Description`.
- [cds-lsp@3.3.0] uses global `@sap/cds/common` if locally not available
- [odata-server@1.7.0] support for navigation properties in complex properties

### Changed ​

- [cds.java@1.5.1] Reverted behavioral changes of PATCH, introduced with 1.5.0. Responses to PATCH request default to `return=representation` again, if no `Prefer` header is explicitly set.
- [cds.java@1.5.0] The `DRAFT_EDIT` event now triggers `UPDATE` instead of an `UPSERT` event on the service to activate the edited draft. Event handlers currently registered on `UPSERT` therefore need to be registered on the `UPDATE` event as well.
- [cds.java@1.5.0] Elements annotated with `@cds.on.insert` or `@cds.on.update` (`managed` aspect) are fully read-only on CDS-Service level. In addition, the PersistenceService only sets new values for these elements, if the key isn't yet present in the data map.
- [cds.java@1.5.0] The OData V4 query option `$count=true` is now handled using `Select.inlineCount()`. This ensures that `READ` event handlers aren't triggered twice (once for reading the entities and once for calculating the count), in case `$count=true` is combined with `$skip` or `$top`.
- [cds.java@1.5.0] Keys listed in the OData V4 URL aren't propagated to the query map (`context.getParameterInfo().getQueryParameter("key")`) anymore, but should be accessed via the CQN Analyzer now: `CqnAnalyzer.create(context.getModel()).analyze(context.getCqn().ref()).targetKeys().get("key")`
- [cds.java@1.5.0] By default an OData V4 PATCH request doesn't return the updated entity in the response anymore. Set the request header `Prefer: return=representation` to ensure that the entity is returned.
- [cds4j@1.9.0] Only return update data on row count > 0
- [cds4j@1.9.0] Rename method to obtain lhs of CqnInPredicate to values()
- [cds4j@1.9.0] Compare plain case-insensitively, allowing for 'AND' instead of 'and'
- [cds@3.34.0] Node.js method `cds.parse()` has been changed to now truly return parsed-only models, with extensions not applied yet. Note: If you need the former (erroneous) behavior, use `cds.compile.cdl` for that from now on.
- [cds@3.34.0] Node.js method `cds.get()` now returns parsed-only models; same as `cds.parse()`.
- [cds@3.34.0] `cds serve` / `run` / `watch` now reduce logging of details for the bound DB on connect, leading to less clutter.
- [cds@3.34.0] Precision for `validTo` and `validFrom` defined in the `temporal` aspect in `@sap/cds/common` changed from `DateTime` to `Timestamp`.
- [cds@3.34.0] Some administrative fields of SAP Fiori draft documents are now hidden on the UI. The rest got labels.
- [cds@3.34.0] Renamed cds configuration setting `features.messageLevel` to `log-level` to be consistent with command line option, for example, `cds build --log-level`.
- [cds@3.34.0] `cds extend` and `cds activate` commands have been moved to `@sap/cds-dk`. `cds disconnect` has been moved there under a different name.
- [cds-dk@1.8.0] Parameter `verbose` in `cds init` and `cds add` is now deprecated. Use environment variable `DEBUG=true` to obtain detailed output.
- [cds-dk@1.8.0] `cds init` uses latest `Java archetype` version `1.4.0` for creating Java projects.
- [cds-compiler@1.26.2] HANA/SQL: Raise warnings `rewrite-not-supported` and `rewrite-undefined-key` to errors.

- [cds-compiler@1.26.2] Compiler: Empty elements are now kept along for the propagation.
- [cds-compiler@1.26.2] OData: Annotate all elements of `DraftAdministrativeData` with `@Common.Label: '{i18n>"Draft_"}'` and elements 'DraftUUID', 'DraftIsCreatedByMe' and 'DraftIsProcessedByMe' with `@UI.Hidden`.
- [cds-compiler@1.26.2] Downgrade `chained array of`-error to a warning
- [cds-compiler@1.26.2] SQLite: Don't render implicit casts
- [cds-compiler@1.26.2] OData: Improve messages for misaligned forward/backlink associations in EDM generator
- For V2 add annotations `@sap.creatable: false`, `@sap.updatable: false`, `@sap.deletable: false`, `@sap.pageable: false` to the Parameter EntityType and `@sap.creatable: false`, `@sap.updatable: false`, `@sap.deletable: false`, `@sap.addressable: false` to the Result EntityType.
- Update vocabularies 'Common' and 'Graph' and 'ODM'.

- [cds-lsp@3.3.2] removes optional odata annotation handler due to build issues
- [cds-compiler@1.26.2] OData: Change foreign key creation order for associations to respect their dependencies.
- Use correct path during on-condition flattening.
- Report error when using elements without types for array of type of (element) and similar definitions.

- [cds-compiler@1.26.2] HANA/SQL: Fix references to `null` enum values in default clauses.

- [cds-compiler@1.26.2] Type arguments are now properly set in CSN when using parse-cdl mode.
- [cds-compiler@1.26.2] Avoid unjust warning if the `extensions` property of an input CSN contains `extend` statements.
- [cds-compiler@1.26.2] Compiler: `type of ` is now handled correctly by raising an error.
- [cds-compiler@1.26.2] Various messages mention more appropriate source locations.
- [cds-compiler@1.26.2] Improve messages for `array of`
- [cds-compiler@1.26.2] OData: Render `array of` for ReturnType correctly
- Report error for view fields with no type information early
- Handle associations in structures with an association as explicit key

- [cds-lsp@3.3.1] consumes cds-compiler 1.26.2
- [cds-lsp@3.3.0] (alpha): diagnostics and hover support for external annotation providers

### Fixed ​

- [cds.java@1.5.0] Fixed handling of authentication for actions and functions
- [cds.java@1.5.0] Fixed processing of predefined filters sent by SAP Fiori draft UIs (for example "editing status" filter).
- [cds.java@1.5.0] Fixed handling of mandatory associations to draft-enabled entities.
- [cds.java@1.5.0] Fixed handling of draft-enabled child entities without a backlink association.
- [cds.java@1.5.0] Fixed issues with transaction handling for OData V4 request not using a changeset.
- [cds.java@1.5.0] Fixed handling of OData V4 actions with no return parameter and no input parameters.
- [cds.java@1.5.0] Fixed handling of OData V4 `$count=true`, when specified with `$skip`, `$top` and `$search`
- [cds.java@1.5.0] Fixed incorrect calculations of the OData V4 context URL
- [cds.java@1.5.0] Fixed handling of CqnUpdate statements with more than one data entry.
- [cds.java@1.5.0] Fixed handling of batch parameters in run methods for delete and update operations
- [cds.java@1.5.0] Fixed a startup issue that could occur, when Spring Integration was used
- [cds.java@1.5.0] Fixed internal server errors, when `@Capabilities` annotations reference an entity element, instead of a simple boolean. On server-side such capabilities not checked anymore, allowing at least SAP Fiori to interpret these parameter-bound capabilities.
- [cds.java@1.5.0] Projects generated with the archetype now by default have the property `spring.test.context.cache.maxSize=1` set, which prevents issues with multiple CdsRuntime objects in different Spring application contexts.
- [cds.java@1.5.0] Patterns in .gitignore generated by the archetype, now use `**/` as glob statement prefix, to ensure compatibility with other tools interpreting the .gitignore file (for example, npm publish)
- [cds4j@1.9.0] Fix NPE on default $now
- [cds4j@1.9.0] Fix serialization of CqnNull
- [cds4j@1.9.0] Fix contains on ref not in select list
- [cds4j@1.9.0] Improve exception on parsing instants
- [cds4j@1.9.0] Avoid duplicates in deep search by using subqueries
- [cds4j@1.9.0] Don't throw SQL exception on update with empty payload
- [cds4j@1.9.0] Improve exception on parsing instants
- [cds4j@1.9.0] Draft: Add security constraints to SiblingEntity association
- [cds4j@1.9.0] Fix FK field computation for $self with unmanaged backlinks
- [cds4j@1.9.0] Fix NPE in cds4j-multitenant MetaDataAccessorSingleMode
- [cds4j@1.9.0] Throw CdsDataException on deep updates w/o key values
- [cds@3.34.0] `cds build` - improvements in the area of error handling and error reporting.
- [cds@3.34.0] `cds env` and Node.js runtime now properly complete configuration like `requires.db.kind.sql` with VCAP_SERVICES, so that in `production` an SAP HANA service is bound.
- [cds@3.34.0] `cds build` now localizes edmx files properly if `cds.env.features.snapi` is turned on.
- [cds@3.34.0] `cds deploy --to hana` no longer crashes if called with `NODE_ENV=production`.
- [cds-dk@1.8.0] Fixing terminology in `cds init` and `cds add` console output.
- [cds-dk@1.8.0] `cds init` is logging `cds env` output only in debug mode.
- [cds-dk@1.8.0] Using `cds build` command in generated mta.yaml file.
- [cds-dk@1.8.0] Fixing Hana dependency during `cds init --add hana` for project type `java`.
- [cds-dk@1.8.0] Fixing bug in `cds init` when `cds-dk` isn't installed globally.
- [cds-dk@1.8.0] Fixing bug in `cds init` when calling log methods.
- [cds-dk@1.8.0] Fixing `cds.env`object by attaching prototype chain.
- [cds-compiler@1.26.2] OData: Process correctly "type of".
- Process correctly elements with underscore as prefix.

- [cds-compiler@1.26.2] Preserve parameter list in localized convenience views.
- [cds-compiler@1.26.2] Force usage of resolve@1.8.1 instead of semver to avoid issues with file cache
- [cds-compiler@1.26.2] When not disabled by `@cds.autoexpose:false`, an entity used as composition target is auto-exposed in the current service; this didn't work always if the target was a query entity.
- [cds-compiler@1.26.2] Foreign key creation in odata flat-mode when following associations.
- [cds-compiler@1.26.2] Rename `@description` to `@Core.Description` in all cases as part of the OData transformation of a CSN.
- [cds-compiler@1.26.2] When generating extensions from EDMX annotations, handle correctly targets from an EntityContainer.
- [cds-compiler@1.26.2] Apply service annotations in EDMX generation.
- [cds-compiler@1.26.2] Resolve backlink mixin association usages uniformly in association to join translation.
- [cds-compiler@1.26.2] HANA CDS: When casting a column to an enum type, don't render it as an enum
- [cds-compiler@1.26.2] Ignore top-level CSN "annotations" like `@sql_mapping` in the CSN frontend.
- [cds-compiler@1.26.2] OData: Key constraint checks for Draft enabled entities consider EDM exposed keys only.
- [cds-compiler@1.26.2] Message level for draft key checks is raised to 'warning' again.
- [cds-compiler@1.26.2] Action and function calls are checked for missing arguments.
- [cds-compiler@1.26.2] All references are correctly transformed in flatten mode.
- [cds-lsp@3.3.0] Minor fixes and improvements
- [odata-server@1.7.1] ETags are never required for transient entities from $apply queries
- [odata-server@1.7.0] context URL in some edge cases with keys
- [odata-server@1.6.1] support for JSON content in type-definition properties with underlying type Edm.Stream (#97)

### Removed ​

- [cds-compiler@1.26.2] The client tool `cdsc` doesn't offer the option `--std-json-parser` anymore, as it had no effect.

## March 2020 ​

### Added ​

- [cds.java@1.4.0] Operations on draft entities are now restricted to the user who created the draft
- [cds.java@1.4.0] Support for returning entities with expanded navigation properties in actions and functions
- [cds.java@1.4.0] `@readonly` can now be used at element level as well
- [cds.java@1.4.0] Elements with default values that are also `not null` or `@mandatory` are now supported
- [cds.java@1.4.0] CSV files are now automatically loaded from `db/data` or `db/csv` during startup of the application
- [cds.java@1.4.0] When using Spring's health check actuators and enabling multitenancy the health of each connected database is checked.
- [cds.java@1.4.0] An actuator providing CDS-related debugging information is now provided on Spring. It's active by default for JMX and can be enabled for web-exposure by adding `cds` to `management.endpoints.web.exposure.include`
- [cds.java@1.4.0] The archetype now generates example event handler classes and an example JUnit test, if the property `includeModel` is set to `true`
- [cds.java@1.4.0] The archetype now enables generation of `EventContext` interfaces for actions and functions in the CDS4J maven plugin settings
- [cds.java@1.4.0] The archetype now automatically adds the cds-starter-cloudfoundry dependency to newly generated projects
- [cds.java@1.4.0] SAP proprietary locales `1Q` (`en-US-x-saptrc`) and `2Q` (`en-US-x-sappsd`) are now handled correctly
- [cds.java@1.4.0] Added a new configuration option `cds.locales.normalization` to specify the whitelist for locales
- [cds.java@1.4.0] Added a new configuration option `cds.odatav4.contextAbsoluteUrl` to control if the URL in the `@context` field of OData V4 responses contains an absolute or a relative URL
- [cds.java@1.4.0] Added the possibility to specify service-related configuration in a new configuration section `cds.services`
- [cds.java@1.4.0] The version and commit information of the CDS Services dependency used are now printed to the logs during startup
- [cds4j@1.8.0] Support deep updates
- [cds4j@1.8.0] Support default values
- [cds4j@1.8.0] Return update data on updates
- [cds4j@1.8.0] Code Generator: Add `CDS_NAME` to action/function interfaces
- [cds4j@1.8.0] Add Value.in(List) method
- [cds4j@1.8.0] Truncate instants in insert/update data
- [cds@3.33.0] `cds version` now also lists all dependencies of your local package.json and has an updated CLI commend help, documenting option `--all`.
- [cds@3.33.0] `cds compile` option `--docs` preserve contents of `/** ... */` doc comments in CSN output as well as in EDMX outputs (as Core.Description annotations).
- [cds@3.33.0] `cds compile` option `--clean` tells the compiler to not add any derived information, but return a CSN, which reflects only what was found in a .cds source.
- [cds@3.33.0] `cds serve` option `--watch` starts the specific serve command in nodemon watch mode
- [cds@3.33.0] Node.js: `cds.env` now supports camel case env variables as well as dot-notated keys in `.env`
- [cds-services@1.27.0] Transaction uses one timestamp for all queries
- [cds-services@1.27.0] Pool acquire timeout is set by default and can be configured in pool options
- [cds-services@1.27.0] Ordered OData singletons (`... as select from  order by `)
- [cds-dk@1.7.0] `cds init --add java` supports `--java:mvn` to add additional parameter.
- [cds-dk@1.7.0] Improvements when logging console output during `cds init`.
- [cds-dk@1.7.0] Link to Maven archetype documentation shown in `cds help init`.
- [cds-lsp@3.1.4] extend definitions are now shown in outline and workspace symbols
- [cds-lsp@3.1.4] api (alpha) for external annotation providers
- [cds-messaging@1.8.2] It's now possible to set the queue configuration with the `queueConfig` property in the credentials section
- [cds-sql@1.24.0] Support for different columns combinations in INSERT.entries
- [cds-sql@1.24.0] Support for $count in SELECT CQN
- [cds-sql@1.24.0] Support String objects in the annotation expressions
- [cds-sql@1.24.0] .setTransactionTimestamp in BaseClient
- [cds-sql@1.24.0] check for @cds.persistence.skip for deep operations
- [cds-hana@1.25.0] Single timestamp per transaction
- [cds-hana@1.25.0] default timeout 20s for acquiring client from pool
- [cds-hana@1.24.0] Streaming from draft
- [cds-hana@1.24.0] Timeout for update and delete statements to handle locked records (@sap/hana-client only, default: 1 s)
- [odata-server@1.6.0] limited support for JSON content in stream properties as described in OASIS issue 1177
- [odata-server@1.5.5] If-Match and If-None-Match headers are allowed with value * on POST requests
- [odata-server@1.5.3] If-Match and If-None-Match headers are allowed with value * on non-conditional DELETE requests

### Changed ​

- [cds.java@1.4.0] XSUAA user names are now normalized by converting them to lower case. This behavior can be turned off by specifying `cds.security.xsuaa.normalizeUserNames` to `false`.
- [cds.java@1.4.0] `@mandatory` annotated elements of type String now also reject any trimmed empty strings.
- [cds.java@1.4.0] Entities that are `@cds.autoexposed` are now read-only (in case of additional `@cds.autoexpose`) or can not be accessed at all, if referenced as root entity in a CQN statement. This behavior doesn't apply, if the entity is draft-enabled or explicitly mentioned in the service definition.
- [cds4j@1.8.0] Move non-SQL/JDBC functionality into new core module
- [cds4j@1.8.0] Remove deprecated methods in CqnReference and deprecate segment setters
- [cds4j@1.8.0] Traverse CqnStatements depth-first
- [cds@3.33.0] Labels for the `createdAt` and `changedAt` in the `@sap/cds/common#managed` entity have been adjusted to reflect the SAP Fiori design guidelines.
- [cds@3.33.0] `cds build` now delegates to the modular build system by default (known as `cds build/all`). The modular build system is compatible, but supports additional features, for example, staging build, SAP HANA Cloud Edition support, populating initial data from .csv by generating .hdbtabledata files, etc. The legacy build is still available as a fallback in case of issues - use setting `cds.features.build.legacy: true` or ENV variable `CDS_FEATURES_BUILD_LEGACY=true`.
- [cds-services@1.27.0] $count=true triggers handlers only once now
- [cds-services@1.27.0] `draftPrepare` action can be called on the entity set of child nodes of the draft enabled entity
- [cds-services@1.27.0] Normalize user.id if an email address
- [cds-services@1.27.0] Allow functions and properties as second param in contains, startswith, endswith
- [cds-dk@1.7.0] `cds add mta` now activates the `production` profile when creating the mta.yaml, which is consistent with what the MTA build does. This way, configuration like `"[production]: {"kind": "hana"}` gets activated automatically.
- [cds-compiler@1.24.4] `doc` comment propagation can now also be stopped by comments that only contain whitespace (including newlines) like `/** */`.
- [cds-compiler@1.24.4] OData: Remove redundant service name and `__` prefix out of dynamically exposed substructures.
- Update vocabularies 'Capabilities' and 'Graph'.

- [cds-compiler@1.24.4] Expressions in mixin-definitions are now validated.
- [cds-compiler@1.24.4] OData: Redirect inbound associations to entities with parameters to corresponding Parameter EntityType.
- Update vocabulary `UI`

- [cds-compiler@1.24.4] Use semver for dependencies
- [cds-lsp@3.2.0] remove option for compiler location - LSP will always search Project->Global(via DK&CDS)->BuiltIn now
- [cds-lsp@3.2.0] removes irrelevant formatting option (trimTrailingWhitespace)
- [cds-rest@1.6.2] In case there's no credentials.destination provided the `destinations` environment variable isn't created anymore. The connection to the remote service is handled internally.
- [cds-sql@1.24.0] Use | | for concat (works for HANA and sqlite)

### Fixed ​

- [cds.java@1.4.0] Timestamps are now correctly truncated based on the type of the element in the CDS model
- [cds.java@1.4.0] The `draftActivate` action now returns an expanded result, to workaround issues with Fiori versions >= 1.75.0
- [cds.java@1.4.0] Fixed `$search` returning duplicate search results
- [cds.java@1.4.0] Fixed a malformed OData response, containing an incorrect `@context` property instead of `@odata.context`
- [cds.java@1.4.0] Fixed the finalName property generated by the archetype, which was incorrectly set to `cds-services-archetype`
- [cds.java@1.4.0] Fixed handling of errors during transaction initialization: NoSuchElementException errors could occur, overriding the original exception
- [cds.java@1.4.0] Fixed nondeterministic order in which the `ChangeSetListeners` were called
- [cds4j@1.8.0] Fix package and interface names in FLUENT mode
- [cds4j@1.8.0] Fix traversal order of StructTypeRef, Comparison & Search pred
- [cds4j@1.8.0] cds4j-multitenant: Fix synchronize in MetaDataAccessor
- [cds@3.33.1] `cds build` now correctly supports options.model definitions of type string
- [cds@3.33.1] Details navigation in Fiori preview works again since it's pinned to SAP UI5 1.73. Actual cause still needs to be investigated.
- [cds@3.33.1] `cds deploy` now adds `@sap/hana-client` to package.json instead of `hdb`.
- [cds@3.33.1] `cds deploy` adds kind `sql` to requires section.
- [cds@3.33.0] `cds build` now correctly logs warnings returned by cds compiler. The message log level can be customized using cds configuration setting `cds.features.messageLevel` - default is `warn`.
- [cds@3.33.0] `cds.env.roots` now properly picks up a changed value of `cds.env.folders`
- [cds@3.33.0] `hdbtabledata` is no longer generated for entities that are marked with `@cds.persistence.skip`
- [cds@3.32.0] An issue where all Node.js runtime sessions where disconnected when one tenant offboard.
- [cds@3.31.2] `cds deploy` doesn't crash if _texts.csv is provided for skipped entities
- [cds@3.31.2] `cds serve foo.cds` does no longer load same model twice
- [cds@3.31.2] `cds compile --to edmx` no longer creates files with csn instead of edmx content in case no language bundles are found
- [cds@3.31.2] Both `cds env` and `cds compile` no longer write terminal escape sequences if only stdout is redirected, but not stderr.
- [cds@3.31.2] No longer enforce Node.js version 8 in db/package.json. Cloud Foundry environment doesn't support it anymore, as this version is out of maintenance.
- [cds@3.31.1] Removed npm-shrinkwrap.json
- [cds-services@1.27.0] Entity is now correctly resolved if there are conflicting names
- [cds-services@1.27.0] Where conditions from security annotations were appended twice when using $count=true
- [cds-services@1.27.0] `req._.req` always contains the incoming request - also in `$batch` requests
- [cds-services@1.27.0] Error in delete when fields are renamed in views
- [cds-services@1.27.0] Using view by draft & localized
- [cds-services@1.27.0] context.diff() returns changes also for `PATCH` of drafts
- [cds-services@1.27.0] OData requests using `/$count` on navigation-to-many
- [cds-services@1.27.0] Authentication-requirement detected if in multi tenant mode (that means, `multiTenant: true`)
- [cds-services@1.27.0] Integrity check of atomicity group
- [cds-services@1.27.0] Where annotation in case of draft and navigations
- [cds-services@1.27.0] `/$count` on parameterized views
- [cds-services@1.27.0] Streaming from draft in case localized and where annotations
- [cds-services@1.27.0] @mandatory: empty strings (whitespaces only = empty) aren't allowed
- [cds-services@1.25.1] update of localized text entries replies with 403 if no changes are detected
- [cds-dk@1.6.3] Proper npm-shrinkwrap.json
- [cds-dk@1.6.3] `cds init` is a bit more relaxed when checking for existing project content
- [cds-lsp@3.2.0] formatting failed (seen in Eclipse, VS Code works) due to off-by-one error
- [cds-lsp@3.2.0] global npm root for Business App Studio wasn't found with compiler.location option ProjectThenGlobalThenBuiltIn
- [cds-sql@1.24.0] Using view by draft & localized
- [cds-sql@1.24.0] Quote alias in orderBy to work on HANA
- [cds-sql@1.24.0] Expand from not draft enabled entity to draft enabled entity
- [cds-sql@1.24.0] `where` and `orderBy`clauses containing navigations in combination with expand are correctly translated to SQL
- [odata-server@1.5.4] stricter determination of related entity set

### Removed ​

- [cds-services@1.25.1] npm-shrinkwrap.json
- [cds-compiler@1.24.4] Warning 'Service shouldn't have more than one draft root artifact'
- [cds-compiler@1.24.4] Experimental annotation `@cds.odata.{v2|v4}.ignore`
- [cds-compiler@1.24.4] OData vocabulary `com.sap.vocabularies.odm.v1` (lowercase 'odm')
- [cds-compiler@1.24.4] `--beta-mode` from option `--odata-containment`.
- [cds-messaging@1.8.2] Bound events aren't supported anymore
- [cds-rest@1.6.2] npm-shrinkwrap.json
- [cds-hana@1.25.1] Timeout for update and delete statements (if needed: increase libuv's thread pool size via environment variable `UV_THREADPOOL_SIZE`)

## January & February 2020 ​

### Added ​

- [cds-compiler@1.23.2] If an entity with localized elements is draft enabled, a new key element `ID_texts` is added to the `texts` entity in `--beta-mode`. The key property is removed from all other elements in the `texts` entity and the annotation assignment `@cds.odata.v4.ignore` as described in Version 1.20.0 is reverted. If the element `ID_texts` already exists, an appropriate warning is raised and no texts entity is created.
- [cds-compiler@1.23.2] Introduce `![identifier body]` in the CDL source for delimited identifiers. (The `!` is inspired by ABAP's identifier tag, `[]` by the delimited identifier syntax in Microsoft SQL Server and Sybase; we can't use `[]` alone, because brackets are used for filter conditions.)
- [cds-compiler@1.23.2] When generating SQL or HDBVIEW, explicit CASTs are now rendered
- [cds-compiler@1.23.2] With `redirected to`, model designers can now explicitly provide the `on` condition / foreign `keys` for "consumers" of the current query (entity). This is useful for situations (mentioned as message) where the compiler doesn't calculate `on`/`keys` (automatically yet).
- [cds-compiler@1.23.2] Add OData vocabularies: `com.sap.vocabularies.CodeList.v1`, `Org.OData.Repeatability.V1`, and `com.sap.vocabularies.Session.v1`
- [cds-lsp@3.1.3] picks up compiler and env via global cds-dk if cds not (yet) in project
- [cds-lsp@3.1.2] code formattingoptions can now be overridden in source comments, for example, // @formatter tabSize:3
- new option to add/remove final line break
- new option to trim trailing whitespace

- [cds-lsp@3.1.1] code formattingoption to keep original empty lines

- [cds-lsp@3.1.1] language server protocol 3.15: implement serverInfo in onInitialize
- [cds-lsp@3.1.0] translation supportnow with all formats supported by runtime (.properties, .json, .csv) incl. quick fixes to create missing entries
- now with customizations supported by runtime (filename, folder name, fallback_bundle, default_language) if entries of fallback language are missing but are defined for default language the latter ones are used
- if property files or json nodes or csv header only has default language defined (and not raw), quick fix will use default language
- quick fix for json and csv formats now try to keep entries sorted
- navigation from translation reference in cds source files to value supported for all formats

- [cds-lsp@3.1.0] allows .cdsprettier.json to be located in user home dir
- [cds-lsp@3.0.0] Official support for code formatting
- [cds.java@1.3.0] Support setting the "target" property in OData V4 error messages to influence the way a Fiori UI displays them.
- [cds.java@1.3.0] Support temporal data
- [cds.java@1.3.0] Support expand for associations pointing to other draft-enabled entities
- [cds.java@1.3.0] Support case-insensitive ordering via OData V4 query option $orderby by using tolower() or toupper() functions, for example, `$orderby=tolower(element)`
- [cds.java@1.3.0] The Maven Archetype now allows to omit local cds-dk installation by means of maven profile "cdsdk-global"
- [cds.java@1.2.0] Support returning messages by means of the "sap-messages" header that are shown in Fiori UIs
- [cds.java@1.2.0] Support returning multiple messages in a single response
- [cds.java@1.2.0] Support returning localized messages
- [cds.java@1.2.0] Support searching entities by means of the OData V4 $search query option (including search expressions AND, OR and NOT)
- [cds.java@1.2.0] Support tolower and toupper functions in $filter expressions
- [cds.java@1.2.0] Support the $format parameter for JSON-based formats
- [cds.java@1.2.0] Support associations between draft-enabled entities, enabling also path expressions to the inactive entity via the active entity and vice versa.
- [cds4j@1.7.0] Introduce `com.sap.cds.ql.CQL` API and deprecate `CqnBuilder`
- [cds4j@1.7.0] Support tree-style usage of logical connectives
- [cds4j@1.7.0] Support postfix `not`
- [cds4j@1.7.0] Support using plain expressions in select list
- [cds4j@1.7.0] Support functions in orderBy
- [cds4j@1.7.0] Support `@Search.defaultSearchElement` annotation and cascaded search via `@Search.cascade`
- [cds4j@1.7.0] Support many-to-many associations via mapping entity
- [cds4j@1.7.0] Support actions/functions in Reflection API
- [cds4j@1.7.0] Generate accessor interfaces for actions/functions
- [cds4j@1.7.0] CDS4j maven plugin: m2e lifecycle mapping to enable model generation within Eclipse
- [cds@3.31.0] Generation of `hdbtabledata` files now reports if CSV file names don't match entity names, and if header names don't match element names in an entity. Watch out for such logs in case CSV files aren't deployed to SAP HANA.
- [cds@3.30.0] `cds compile --log-level` allows to choose which messages to see
- [cds@3.30.0] `cds deploy --dry` prints DDL statements to stdout instead of executing them
- [cds@3.30.0] `cds deploy --with-mocks` also adds tables for required services
- [cds@3.30.0] `cds serve --mocked` allows mocking individual required services
- [cds@3.30.0] `cds.env` now also loads from `.env` files in properties format
- [cds@3.30.0] `cds.resolve/load('*')` resolves or loads all models in a project including those for required services. It's controlled and configurable through `cds.env.folders` and `.roots￼`. Try this in `cds repl` launched from your project root to see that in action:js

```
cds.env.folders         // = folders db, srv, app by default
cds.env.roots           // + schema and services in cwd
cds.resolve('*',false)  // + models in cds.env.requires
cds.resolve('*')        // > the resolved existing files
```
- [cds@3.30.0] Added `cds.debug()` as a convenient helper for debug output controlled by `process.env.DEBUG`. For example, use it as follows:js

```
const DEBUG = cds.debug('my-module')
DEBUG && DEBUG ('my debug info:', foo, ...)
```

sh

```
> DEBUG=my-module cds run
```
- [cds@3.30.0] Added `cds.error()` as a convenient helper for throwing errors whose stack traces start from the actual point of invocation. For example, use it as follows:js

```
const {error} = cds
if (...) throw error `Something's wrong with ${whatever}`
const foo = bar || error `Bar is missing!` // short circuit exits
```
- [cds-dk@1.6.0] `cds init --add java` now also works with `--hana`
- [cds-dk@1.5.0] `cds init` adds `private: true` and `license: "UNLICENSED"` to newly generated projects.
- [cds-dk@1.5.0] `cds init` adds a default `.hdiconfig` file when using template `hana`.
- [cds-dk@1.5.0] `cds init` supports Java package name via `--java:package` parameter.
- [cds-dk@1.5.0] `cds init` generates dependency entry for `@sap/hana-client` when using template `hana`.
- [cds-dk@1.5.0] `cds init` uses latest `Java archetype` version `1.3.0` for creating Java projects.
- [cds-dk@1.5.0] `cds init` now creates a .cdsrc.json file.
- [cds-dk@1.4.0] Abort installation with a hint if `@sap/cds` is installed globally.
- [cds-dk@1.4.0] New project generation using `cds init`. See `cds help init` for details.
- [cds-dk@1.4.0] `cds init --add java` now creates Java projects with Spring Boot support.
- [cds-dk@1.4.0] `cds watch` now also watches `.properties` files
- [cds-services@1.25.0] Support for OData singletons
- [cds-services@1.25.0] Streaming from draft
- [cds-services@1.25.0] Navigations in aggregate expressions
- [cds-services@1.24.1] Support draft for localized texts (to be enabled by `@sap/cds` and `@sap/cds-compiler`)
- [cds-services@1.24.0] Support for OData singletons
- [cds-services@1.24.0] Navigations in aggregate expressions
- [cds-services@1.24.0] Support for OData `$apply` with `count distinct`
- [cds-services@1.23.0] Support non-UUID field as ETags
- [cds-services@1.23.0] Support draft and ETags
- [cds-services@1.23.0] Support for complex where in annotations
- [cds-services@1.23.0] Additional argument `target` for `req.info`
- [cds-services@1.22.0] `@sap/cds-ql` merged into @sap/cds-services
- [cds-services@1.22.0] Support for subselects and aliasing for remote service definitions
- [cds-services@1.22.0] Support for `@cds.persistence.table`.
- [cds-services@1.22.0] Actions/functions support $select and $expand query params in odata
- [cds-services@1.22.0] Support cds annotation on insert and update with # (for example, @cds.on.update: #user)
- [cds-messaging@1.6.0] Support for `prefix` credentials options to prefix topics
- [cds-rest@1.4.0] Where x in (a,b,...) predicates are translated to series of (x eq a) or (x eq b) in OData `$filter` options
- [cds-sql@1.23.1] Support for set and data in UPDATE CQN
- [cds-sql@1.23.1] Support draft for localized texts
- [cds-sql@1.23.1] Support for with and data in UPDATE CQN
- [cds-hana@1.24.0] Streaming from draft
- [cds-hana@1.22.0] Implement statement drop
- [odata-server@1.5.0] support for node.js version 12
- [odata-server@1.5.0] complete support of specified Unicode range in URI parsing of identifiers
- [odata-server@1.5.0] URI parsing of search words according to OData 4.01 CS02
- [odata-server@1.4.0] support for EDM singletons

### Changed ​

- [cds-compiler@1.23.2] Association to Join Transformation: Validate paths of an expression in the projection to be compliant with the ON condition path constraints if such an expression is used in a mixin.
- Reject recursive or non-bijective `$self` expressions.

- [cds-compiler@1.23.2] Reject casting of a structured select item to a different type.
- [cds-compiler@1.23.2] OData: Update vocabularies `Capabilities`, `Common`, `UI`, `Validation`
- [cds-compiler@1.23.2] OData: Lower message for unknown vocabulary annotations from warning to info.
- Lower message for `@Analytics.Measure expects @Aggregation.default` from warning to info.
- Remove empty EntityContainer and raise warning if Schema is empty.

- [cds-compiler@1.23.2] Signal a warning for all uses of `"identifier body"` in the CDL source, as most uses of double-quotes in actual CDS models were likely meant for strings. (Yes, we don't adhere strictly to the lexical rules of the SQL Standard with this change…)
- [cds-compiler@1.23.2] Issue a warning for an `aspect` definition without `{…}`.
- [cds-compiler@1.23.2] In the CSN, `aspect` definitions have a `$syntax` property with value `"aspect"`. A future incompatible change will set the `kind` of aspect definitions to value `"aspect"`.
- [cds-compiler@1.23.2] Removed old CSN frontend and the corresponding options: `stdJsonParser` and `oldCsnFrontend`.
- [cds-compiler@1.23.2] Fix check for arguments and filters in references (might introduce new errors).
- [cds-compiler@1.23.2] Issue an error if explicit `keys` are provided when redirecting unmanaged associations.
- [cds-compiler@1.23.2] File paths given to `cdsc`, which contain symbolic links are now resolved before being passed to the compiler.
- [cds-compiler@1.23.2] Annotating elements with `@Core.Computed` now always overwrites computed value; also expressions in parentheses will now induce to set `@Core.Computed` to `true`.
- [cds-compiler@1.23.2] Update OData vocabulary `UI`
- [cds-compiler@1.23.2] Increase the length of the element `locale` in generated `_texts` entities from `String(5)` to `String(14)`.
- [cds-compiler@1.23.2] Don't overwrite annotations with generated annotations (such as shortcuts and other convenience annotations).
- [cds-compiler@1.23.2] In the `sql`, `hdi`, and `hdbcds` backends with SQL dialect HANA, `$user.id` is translated to `SESSION_CONTEXT('APPLICATIONUSER')`, not `SESSION_CONTEXT('XS_APPLICATIONUSER')` anymore. As with the SQL dialect SQLite, it can now be configured.
- [cds-compiler@1.23.2] The client tool `cdsc` now prints a source excerpt for each message by default; use `cdsc --no-message-context` to get the previous behavior.
- [cds-compiler@1.23.2] Increase severity to `Warning` of messages for a situation where the compiler can't calculate an `on` condition / foreign `keys` automatically.
- [cds-compiler@1.23.2] Issues warnings for annotation definitions, as their CSN representation will be moved from `definitions` into a new property `vocabularies` in a future change.
- [cds-compiler@1.23.2] OData: Update vocabularies: `Analytics`, `Common`, `Communication`, `Core`, `PersonalData`, `UI`
- Set reference base URI for SAP Vocabularies to `https://sap.github.io/odata-vocabularies/vocabularies`

- [cds-lsp@3.1.0] code formatting improve alignment of types, values, and preceding `:` or `=` operators

- [cds-lsp@3.0.0] code completion more snippet variants for extend
- no longer differ entity suggestions between within service or outside
- base types with parameters now suggested as simply keyword w/o params and additional suggestion as snippet (param names now enclosed in < >)
- changed label indicator for snippets from <> to ellipsis

- [cds-lsp@3.0.0] code formatting rework formatting options: add/remove options according to relevance, rename/group options for clarity, change default behavior in some cases
- various improvements, including in case statements and bracketed conditions

- [cds.java@1.3.0] The XSUAA service configuration is now only enabled, when an XSUAA service binding is available. With this change, we don't prevent Spring from configuring its default security config and default user anymore.
- [cds.java@1.3.0] The Spring Boot Plugin in applications generated by the archetype now generates the executable JAR with classifier "exec"
- [cds.java@1.2.0] Timestamps are now written to the database in UTC instead of the timezone of the application.
- [cds.java@1.2.0] Changed incorrect HTTP status 400 Bad Request to 404 Not Found for requests targeting a nonexisting entity
- [cds4j@1.7.0] Store timestamps on SQLite as ISO 8601 Strings
- [cds4j@1.7.0] Truncate Instants for DateTime and Timestamp
- [cds@3.30.0] This version brings a major refactoring and streamlining of service runtime implementations, which stays fully compatible regarding all documented APIs but in case you used internal not documented (non-)APIs, you should know these: Removed undocumented features Annotation `@source` from models loaded for runtime Property `cds.serve.app` → use `cds.app` instead Property `source` from CSN entity/view definition objects

It's unlikely that you ever used these undocumented internal features at all. In case you did, this should never have been done and you should fix that asap.

- [cds@3.30.0] Deprecated features (→ might get removed in upcoming versions) Property `cds.session` → use `cds.db` instead
- Property `cds.options` → use `cds.db.options` instead
- Property `cds.unfold` → use `cds.compile` instead
- Property `cds.config` → use `cds.env` instead

These properties actually were duplicates to the mentioned alternatives.

- [cds@3.30.0] `cds run` and `cds watch` have been reimplemented as convenience shortcuts to `cds serve`, which acts as the central orchestrator for bootstrapping now. (→ see `cds run ?` or `cds watch ?` to learn more)
- [cds@3.30.0] `cds serve` now optionally bootstraps from project-local `./server.js` or `./srv/server.js`, if exist, thus giving more control while still benefitting from `cds serve`'s intrinsic support for options like `--in-memory` or `--with-mocks`.
- [cds@3.30.0] `cds serve` now uses `cds.load('*')` to load a single effective model once, assigned to `cds.model`, and reused for db as well as all provided and required services . As that avoids loading models redundantly, it drastically improves both, bootstrapping performance as well as memory consumption.
- [cds@3.30.0] `cds deploy` doesn't (have to) register the default models to package.json anymore. For example, unlike before, `cds deploy -2 sqlite` will merely add an entry: `db:{kind:'sqlite'}`, without an additional `model` property anymore.
- [cds@3.30.0] `cds deploy --to hana` doesn't create `connection.properties` file any longer, but only modify existing one
- [cds@3.30.0] `modifiedAt` and `modifiedBy` from `@sap/cds/common`Are now mutable for OData, that means, no longer carry the `@Core.Immutable: true` annotation.
- Are set by the Node.js runtime whenever the respective row was modified, that means, also during `CREATE` operations.

- [cds@3.30.0] Support for `cds init` is now moved to `@sap/cds-dk`.
- [cds@3.21.0] In development mode, the `mock` authorization strategy is automatically activated with two fake users `alice` and `bob`, which allows for out-of-the-box testing of `@requires` annotations. This means that, unlike before, the `JWT` authorization strategy needs to be activated explicitly (through `{auth: { passport: { strategy: 'mock' }}}`. In production, no change is required.
- [cds@3.21.0] You might see a `MODULE_NOT_FOUND` error for `@sap/xsenv` in case you use the `JWT` strategy but have not bound any xsuaa service. In this case either bind such a service instance, add the `@sap/xsenv` dependency, or use a different strategy like `mock`. The trigger of this error is `@sap/xssec` 2.2.4 no longer requiring `@sap/xsenv`.
- [cds@3.21.0] Renovated and streamlined `cds init`. It prints a hint now if it's called with old-style parameters, as well as that it wants to be used from `@sap/cds-dk`. Check out `cds help init` for more.
- [cds@3.21.0] Removed the experimental `--args` parameter of `cds compile`. This turned out to be cumbersome to use in shells. Replacement is the standard configuration mechanism, for example, use an environment variable `CDS_FOO_BAR` to activate option `cds.foo.bar`.
- [cds-dk@1.6.0] `cds add mta` now creates resources for SAP HANA with an explicit service type `hana`. If deploying to trial landscapes, this needs to be changed manually to `hanatrial`.
- [cds-dk@1.5.0] `cds init` only supports new syntax. See `cds init help` for more info.
- [cds-dk@1.5.0] `cds init` now supports adding template `hana` to Java projects.
- [cds-services@1.25.0] use odata-server 1.5.2
- [cds-services@1.24.0] use odata-server 1.5.1
- [cds-services@1.23.0] Direct access to auto-exposed entities in draft case
- [cds-services@1.23.0] Errors normalized based on OData v4 standard
- [cds-services@1.23.0] Messages (that means, header `sap-messages`) normalized based on Fiori standard
- [cds-services@1.23.0] Referential integrity checks are now executed before the commit
- [cds-services@1.23.0] Result of create and update queries is read from the data source to include computed values (update: root only, that means, w/o compositions, etc.)
- [cds-services@1.22.0] Improve error messages for return type validation of custom operations
- [cds-services@1.22.0] Draft removal is handled in `onDraftActivateEvent` instead of `onDraftActivate`
- [cds-messaging@1.7.0] Updated version number for public release
- [cds-messaging@1.6.0] You can no longer set the namespace outside of the `credentials` block
- [cds-rest@1.5.0] Updated version number for public release
- [cds-rest@1.4.0] Version of `@sap/cloud-sdk-core` pinned to `1.15.1`
- [cds-rest@1.4.0] Version of `@sap/cloud-sdk-util` pinned to `1.15.1`
- [cds-sql@1.23.0] Convert all search queries using `contains` to `like`
- [cds-sql@1.22.0] Managed fields aren't removed anymore if they don't belong to operation (for example, modifiedAt in INSERT, createdAt in UPDATE)
- [cds-sql@1.22.0] `null` is a valid value for a managed field (e. g. if `null` is provided for `@cds.on.insert`, `null` will be inserted to DB)
- [cds-hana@1.23.0] Use `like` instead of `contains` fuzzy search for `$search` queries
- [cds-hana@1.22.0] SESSION_CONTEXT('APPLICATIONUSER') instead of SESSION_CONTEXT('XS_APPLICATIONUSER')
- [cds-hana@1.22.0] @sap/hana-client is preferred over hdb

### Fixed ​

- [cds-compiler@1.23.2] Association to Join Transformation: Resolve compound ON conditions with multiple logical terms and/or references to different associations via `$self`.
- [cds-compiler@1.23.2] Remove temporary property `viaTransformation` from published CSN.
- [cds-compiler@1.23.2] Don't complain about unaligned `$syntax` attribute in CSN frontend.
- [cds-compiler@1.23.2] Correctly calculate code completion candidates for projection items in all circumstances (regression introduced in v1.22.0).
- [cds-compiler@1.23.2] In the Hana/Sql backend, correctly resolve forward `on` condition when using mixin association that backlinks to an unrelated 3rd party entity and association.
- [cds-compiler@1.23.2] Raise a warning if the element of the forward association and the element of the query source don't originate from the same defining entity. Raise an error if the element of the forward association can't be found in the query source or is ambiguous.
- [cds-compiler@1.23.2] Correctly create localization views with compiled model as input; it was wrong previously in a model with a high view hierarchy.
- [cds-compiler@1.23.2] Automatically calculate `keys` also for published secondary managed associations, that means, associations in a select column, which is reached by following another association. The compiler doesn't yet calculate the `on` condition of published secondary unmanaged associations – provide it explicitly.
- [cds-compiler@1.23.2] Entities/Views without elements are now detected correctly.
- [cds-compiler@1.23.2] Fix check for action/function parameters in services.
- [cds-compiler@1.23.2] OData: Correctly apply annotations to parameters.
- [cds-compiler@1.23.2] In the `sql`, `hdi` and `hdbcds` backends, correctly ignore contexts containing just actions.
- [cds-compiler@1.23.2] In all backends, correctly handle models where an `on` condition of a `join` contains a sub query.
- [cds-compiler@1.23.2] Avoid infloop for cyclic dependencies on select items with explicit redirections.
- [cds-lsp@3.1.2] in some cases csn files with .json extension where not detected and thus workspace symbols were incomplete
- [cds-lsp@3.1.1] formatting options were taken from homedir instead of preferring from project
- [cds-lsp@3.1.0] code formatting fix, improve, and allow to better adjust alignments and whitespace
- fix alignment of annotations in `annotate` statement
- fix casing of and indentation after `Association` and `Composition`
- fix formatting of parts of `select` statement in case of nesting and after `in`
- fix positioning of brace `{` after annotation if requested to be kept in previous line
- fix bug where token starting with `$` was merged

- [cds-lsp@3.1.0] in the past file changes via watcher were automatically sent for all files in VS Code. In recent versions of VS Code this has changed to only sent files supported by language server type (cds). A fix was made to dynamically register for relevant side-files like package.json, .cdsrc.json, all supported translation file formats, ignore files to keep track of changed environment
- [cds-lsp@3.0.0] code formatting fix alignment of annotations in views
- safely identify unreserved keywords

- [cds.java@1.3.0] Handle more timestamp formats on SQLite-based databases: This fixes interoperability issues with cds deploy and the Node.js stack. The suggested timestamp format to be used in CSVs is ISO 8601 (`2020-02-05T07:43:40Z`)
- [cds.java@1.3.0] The sap-messages header is now also written on 204 No Content responses.
- [cds.java@1.3.0] OData V4 navigation paths are now correctly handled also on HTTP requests using the PATCH or PUT verb
- [cds.java@1.2.0] Support compositions of second grade or higher for draft-enabled entities
- [cds.java@1.2.0] Fixed a bug where $count couldn't be combined with $orderby in an OData V4 query
- [cds.java@1.2.0] OData V4 queries with PUT verb didn't work on draft-enabled entities
- [cds.java@1.2.0] Fixed an issue where bound actions returning an entity type ran into an error when returning an entity type that was different from the one they were bound to.
- [cds4j@1.7.0] Fix name clash with 'filter' in generated builder interfaces
- [cds4j@1.7.0] Fix computation of join conditions for association keys
- [cds@3.31.1] Removed npm-shrinkwrap.json
- [cds@3.31.0] `cds compile --to hdbtabledata` no longer crashes with `_texts.csv` files referring to a non-`localized` entity
- [cds@3.31.0] `cds build/all` adds `app` folder to the list of model folders for hana database builds. Draft tables are missing if the corresponding annotation model is missing.
- [cds@3.30.0] There was a bug in that caused a service names `FooBarV2` to erroneously be mapped to mount point `/foo-barv2` instead of `/foo-bar-v2` as intended and was the case before. → in case you started a project in this interims phase and had a service name with that pattern you may encounter this fix as an incompatible change, but it's actually reverting to the former compatible way.
- [cds@3.30.0] `cds.env` erroneously overrode profiled entries depending on properties order
- [cds@3.30.0] Fiori preview now uses latest version of SAP UI5 again
- [cds@3.30.0] `cds deploy` verifies returned service key to ensure that target service isn't of type `managed`.
- [cds@3.21.3] Fiori preview no longer catches service URLs with an arbitrary prefix (for example, `/foo/browse` instead of just `/browse`).
- [cds@3.21.1] Fiori preview no longer crashes since it's pinned to SAP UI5 1.72.3. Actual cause still needs to be investigated.
- [cds@3.21.0] `SELECT.one/distinct(Fool,[...])` failed when passing an array for columns as argument two
- [cds-dk@1.6.0] `cds add mta` now creates valid configuration for `uaa` and `auditlog` resources.
- [cds-dk@1.5.0] `cds add mta` fixes an issue in created mta.yaml for nodejs projects if used in xmake environment.
- [cds-dk@1.5.0] `cds add mta` fixes a build order issue in created mta.yaml for java projects. Now, service module is built before db module.
- [cds-dk@1.5.0] `cds init` doesn't create package.json in db folder.
- [cds-dk@1.4.0] Find locally installed modules like `passport`, so that `cds watch` and `cds run` behave symmetrically.
- [cds-services@1.24.0] Column generation for `SELECT.from()` queries without specifying `.columns()``HasDraftEntity` wasn't properly calculated
- Virtual properties weren't excluded

- [cds-services@1.25.0] Support for OData singletons
- [cds-services@1.25.0] Streaming from draft
- [cds-services@1.25.0] Navigations in aggregate expressions
- [cds-services@1.24.0] Where secure annotations with localized entities
- [cds-services@1.24.0] Handling of `@cds.on.insert/update` annotated properties of draft-enabled entities
- [cds-services@1.24.0] Keys in root element weren't correctly calculated for deep operations
- [cds-services@1.24.0] `@Core.MediaType` couldn't be used in entity annotated with `@cds.persistence.skip`
- [cds-services@1.23.0] Race condition when there are errors when saving draft
- [cds-services@1.23.0] Handling of where from @restrict annotation of draft enabled entity
- [cds-services@1.23.0] Saving a draft won't ignore read-only fields anymore
- [cds-services@1.23.0] Not having a connection for unauthorized users won't crash the server anymore
- [cds-services@1.23.0] In mocked authorization, users don't need the `ID` property
- [cds-services@1.23.0] Filtering using the `NE` operator handles null values properly
- [cds-services@1.23.0] For insertable-only entities default values are correctly handled now
- [cds-services@1.23.0] Immutable values are now ignored during PATCH or UPDATE requests
- [cds-services@1.23.0] Batch input via REST
- [cds-services@1.23.0] SELECT * by customer handlers will work also on Hana in case the columns are lowercase
- [cds-services@1.23.0] Support "userAttributes" by Mocked Authentication, "xs.user.attributes" is deprecated and will be removed in the next releases
- [cds-services@1.23.0] Arbitrary users are allowed if fake user '*'= true exist by Mocked Authentication
- [cds-services@1.22.0] Check whether service requires authentication
- [cds-services@1.22.0] Independent passport configs per service
- [cds-messaging@1.6.0] Fixed bug where non-trimmed data causes problems in file-based messaging
- [cds-sql@1.23.2] Missing alias for orderBy caused column ambiguously defined error
- [cds-sql@1.23.0] Searching for `_` or `%` in `$search`
- [cds-sql@1.22.0] Expand with composition to one for draft enabled entity
- [odata-server@1.5.0] ensures non-null field code in error responses
- [odata-server@1.4.1] If-Match and If-None-Match headers are allowed with value '*' on non-conditional PUT/PATCH requests (for upsert)
- [odata-server@1.4.1] If-Match header with value '*' is allowed for all GET requests
- [odata-server@1.4.1] allows annotations @odata.type in requests if they match the types specified in the metadata
- [odata-server@1.4.0] documentation: actions and functions are supported

### Removed ​

- [cds-services@1.24.0] Annotation `@Search.fuzzinessThreshold`
- [odata-server@1.5.0] support for node.js version 8 due to its end of life
