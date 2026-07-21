<!-- mirror: https://cap.cloud.sap/docs/releases/2021/changelog -->
<!-- fetched: 2026-05-09T02:26:13.681Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# Changelog 2021 ​

## December 2021 ​

### Added ​

- [cds-dk@4.7.0] `cds add data --for` can be passed a regular expression, allowing more flexible name filters. For example `--for '^Supplier$'` would only match entity `Supplier`, but not `SupplierAddress`. Note that as before, `--for Supplier` is interpreted as `--for '^Supplier.*'`, i.e. matches both entities.
- [cds-dk@4.7.0] `cds init --add hana` and `cds add hana` now add a undeploy.json file containing wildcards. This ensures that SAP HANA artifacts are automatically cleaned-up in case views, unique keys, or constraint definitions of associations have been changed in CDS model.
- [eslint-plugin-cds@2.2.2] Added new rule 'no-join-on-draft-enabled-entities'
- [vscode-cds@4.4.0] progress monitor for long runners like References and WorkspaceSymbols
- [cds-compiler@2.11.0] Option `defaultBinaryLength` to set a `length` type facet for all definitions with type `cds.Binary`. This option overrides the default binary length in the database backends and is also used as `MaxLength` attribute in OData.
- [cds-compiler@2.11.0] If doc-comments are ignored by the compiler, an info message is now emitted. A doc-comment is ignored, if it can't be assigned to an artifact. For example for two subsequent doc-comments, the first doc-comment is ignored. To suppress these info messages, explicitly set option `docComment` to `false`.
- [cds-compiler@2.11.0] `cdsc`: `cdsc explain list` can now be used to get a list of message IDs with explanation texts.
- `cdsc` now respects the environment variable `NO_COLOR`. If set, no ANSI escape codes will be used. Can be overwritten by `cdsc --color always`.

- [cds-compiler@2.11.0] to.sql/hdi: Support SQL window functions
- [cds-compiler@2.11.0] to.sql/hdi/hdbcds: Support configuration of `$session` and `$user` via option `variableReplacements`.
- Restricted support for SQL foreign key constraints if option `assertIntegrityType` is set to `"DB"`. The behavior of this feature might change in the future.

- [cds.java@1.21.0] Added support for IAS-based authentication with new feature `cds-feature-identity`.
- [cds.java@1.21.0] Added a persistent outbox that stores enrolled messages in a database table and publishes them again asynchronously after the transaction finished. It is used by Messaging and AuditLog services to bind communication with these services to the current database transaction.
- [cds.java@1.21.0] Added support for automatic audit logging based on `@PersonalData` and `@AuditLog` annotations
- [cds.java@1.21.0] The goal `generate` of the `cds-maven-plugin` provides the new parameter `includes` to configure CDS namespaces or entities included into code generation.
- [cds.java@1.21.0] Pool configurations of multi-tenant database bindings now support map-based parameters. This enables additional connection properties to be specified. For Hikari connection pool, you can use `cds.datasource..hikari.data-source-properties.: `
- [cds.java@1.21.0] Values for elements with arrayed types can now be specified in CSV files, by providing them as JSON arrays.
- [cds.java@1.21.0] You can now configure the destination retrieval strategy and the token exchange strategy for a Remote Service, by setting `cds.remote.services..destination.retrievalStrategy` and `cds.remote.services..destination.tokenExchangeStrategy`.
- [cds4j@1.25.0] Support deep insert on structured elements
- [cds4j@1.25.0] Support aliased expands
- [cds4j@1.25.0] Support managed to-one associations on the select list
- [cds4j@1.25.0] Support paths in CdsStructuredType:get/findElement
- [cds4j@1.25.0] Support structured FK/ref element values in updates
- [cds4j@1.25.0] Code generator: Support includes configuration option
- [cds@5.7.0] Deferred emitting via persistent outbox, enabled through service `outbox` of kind `persistent-outbox`
- [cds@5.7.0] Support for compiler-generated referential constraints BetaActivate via `cds.env.features.assert_integrity: ''`
- Available presets: `off`: no database constraints and no runtime checks
- `app`: runtime checks by default
- `db`: database constraints by default

- "by default": if not excluded, the runtime check or database constraint applies
- "opt-in": if included, the runtime check or database constraint applies
- Behavior can be overridden via `@assert.integrity: ` on property, entity, or service level (lowest applies)

- [cds@5.7.0] Allow `--with-mocks` in production via `cds.env.features.with_mocks = true`
- [cds@5.7.0] Set media type from content type header while inbound streaming
- [cds@5.7.0] Support for navigations with `$count` in `$filter`, for example `GET Entity?$filter=toMany/$count gt 0`
- [cds@5.7.0] Draft: Generate UUIDs for request payloads to which extra data items are added (without the UUID keys) in a custom application handler.
- [cds@5.7.0] Generate GraphQL schema via `cds compile -2 gql` (alpha)
- [cds@5.7.0] Log requests to remote services if respective log level is set to `debug`
- [cds@5.7.0] Beta OData URL to CQN parser (`cds.env.features.odata_new_parser`): support for `$skiptoken` query option
- limited support for `$apply` query option Supported are following transformations and their combinations: `aggregate`, `groupby`, `topcount`, `bottomcount`, `filter`, `search`
- Not supported: Transformations `topsum`, `bottomsum`, `toppercent`, `bottompercent`, `expand`, `concat`, `compute`, `identity`
- `rollup` and `$all` in `groupby` transformation
- Filter function `isdefined`
- Custom aggregation methods, arithmetic operators (`add`, `sub`, `mul` and so on) and keyword `from` in `aggregate` transformation
- OData vocabulary for Data Aggregation, `@Aggregation.default` annotation

- Out of scope: Draft handling

- [cds@5.7.0] Out-of-the-box audit logging for draft enabled entities
- [cds@5.7.0] Support for `@sap/instance-manager`'s hybrid mode Enable via `cds.env.features.hybrid_instance_manager`
- Respective version of `@sap/instance-manager` required

- [cds@5.7.0] `cds.minify()` (alpha) as static method
- [cds@5.7.0] Annotation `@open` for actions in new Rest Adapter
- [cds@5.7.0] Audit logging (`cds.env.features.audit_personal_data`) supports annotation `@PersonalData.EntitySemantics: 'Other'` and allows an arbitrary composition of entities with respect to `@PersonalData.EntitySemantics` annotations
- [cds-mtx@2.5.0] Binding of both service-manager and managed-hana is now supported. To enable it, you have to set the feature flag `cds.features.hybrid_instance_manager` to true. Please note that you also need a compatible version of `@sap/instance-manager`.

### Changed ​

- [cds-dk@4.7.0] `cds import` now adds annotations for missing ON conditions in associations instead of appending it in `doc`.
- [cds-dk@4.7.0] `cds import` has updated mapping for OData V2 and V4
- [cds-dk@4.7.0] `cds add lint` now configures `csv` files in .vscode/settings.json
- [cds-dk@4.7.0] `cds add hana` for Java projects now adds an `engines.node` version of `^16` to the generated db/package.json, to pin the Node.js version. This will help in the future when runtime environments change their default to some version higher than the one supported by `@sap/hdi-deploy`.
- [cds-dk@4.7.0] `cds add mta` for Node.js projects now adds `npm ci` commands instead of `npm install`. This makes use of package-lock.json to enforce reproducible builds.
- [cds-dk@4.7.0] `cds watch` now ignores folders named `target`, to avoid restarts when Maven's build output changes
- [eslint-plugin-cds@2.2.2] Compile 'model' files based on CSN flavor 'inferred'
- [eslint-plugin-cds@2.2.2] Compile 'outsider' files based on CSN flavor 'parsed'
- [vscode-cds@4.4.0] new 'cold start' start-up behaviour: workspace is not scanned unless required (references, workspace symbols)
- file contents read during compilation is cached, incl. tried missing paths during path resolution
- many changes to improve performance and reduce required memory

- [vscode-cds@4.4.0] `cds preview` now opens a read-only editor to show the cds file preview.
- [cds-compiler@2.11.0] Updated OData vocabularies 'Common' and 'UI'.
- [cds-compiler@2.11.0] to.sql/hdi/hdbcds: The default length of `cds.Binary` is set to `5000` similar to `cds.String`.
- [cds.java@1.21.0] Changed the Outbox API to behave more like a Messaging Service. Outbox messages can be enrolled in the outbox and are later published by the outbox again. Event handlers can be registered at the Outbox to listen for published messages. The outbox takes care of binding the message to the current ChangeSetContext (transaction).
- [cds.java@1.21.0] The parameter `excludes` of goal `generate` of the `cds-maven-plugin` now expects an Ant Glob style pattern. The new default value for this parameter is `localized.**`.
- [cds@5.7.0] `if-match` and `if-none-match` headers are ignored for entities without etags
- [cds@5.7.0] Improve response time of `SELECT` queries that check referential integrity by adding an upper bound `LIMIT 1`
- [cds@5.7.0] Leaner implementation for `sap-statistics`
- [cds@5.7.0] Leading and trailing whitespaces are allowed for `$search` query parameter
- [cds@5.7.0] Insert / Update of Composition of one with empty object is not allowed for non UUID keys
- [cds@5.7.0] Search behavior of whitespaces changed as follow: Searches for plain whitespace, for example, `"$search= "` matches the complete data set.
- Searches for whitespace surrounded by double-quotes, for example, `$search=" "` matches all entries containing whitespaces.

- [cds@5.7.0] In single tenant mode, the default SQLite database is used, regardless of `context.tenant`
- [cds@5.7.0] `cds build` for Node.js projects now copies package-lock.json files into the staging folder (usually `gen/srv`). This allows the execution of `npm ci` there.
- [cds@5.7.0] Relaxed UUIDs in beta URL to CQN parser (`cds.env.features.odata_new_parser`)
- [cds@5.7.0] Authentication strategies `dummy` and `mock` no longer require `passport`
- [cds@5.7.0] In production, debug logs of `cds.DatabaseService` and `cds.RemoteService` have sanitized values Deactivate via `cds.env.log.sanitize_values = false`

### Fixed ​

- [cds-dk@4.7.2] `cds add lint` uses JSONC parser to read ESLint config files of type .eslintrc[.js,.cjs,.json].
- [cds-dk@4.7.1] `cds activate` authentication no longer fails
- [cds-dk@4.7.1] `cds.compile.to.openapi` does no longer crash if `cds.compile` was already initialized
- [cds-dk@4.7.0] `cds import` throws warning messages for unsupported data types.
- [cds-dk@4.7.0] `cds watch` allows the explicit `--with-mocks` option, although this is anyways included by default
- [cds-dk@4.7.0] `cds watch` no longer runs into multiple restarts if many files are changed at once, like in git branch changes
- [cds-compiler@2.11.4] CDL parser: in many situations, improve message when people use reserved keywords as identifier
- [cds-compiler@2.11.4] Improve error text and error location for ambiguous auto-redirection target
- [cds-compiler@2.11.4] to.sql/hdi/hdbcds: Correctly detect `exists` in projections
- Correctly handle elements starting with `$` in the on-condition of associations
- Correctly handle sub queries in an entity defined with `projection on`
- Correctly handle associations in sub queries in a `from` of a sub query
- foreign key constraints: respect @assert.integrity: false for compositions

- [cds-compiler@2.11.4] to.hdbcds: Correctly quote elements named `$self` and `$projection`
- [cds-compiler@2.11.4] to.cdl: `when` was added to the keyword list for smart quoting
- [cds-compiler@2.11.4] Compiler support for code completion for `$user` and `$session` now respect user provided variables in `options.variableReplacements`.
- [cds-compiler@2.11.4] API: `deduplicateMessages()` no longer removes messages for `duplicate` artifact/annotation errors. Prior to this version, only one of the duplicated artifacts had a message, leaving the user to guess where the other duplicates were.
- [cds-compiler@2.11.2] to.sql/hdi/hdbcds: No foreign key constraint will be rendered for managed `composition of one` if annotated with `@assert.integrity: false`
- Correctly handle managed associations with other managed associations as foreign keys in conjunction with `exists`

- [cds-compiler@2.11.0] CSN parser: doc-comment extensions are no longer ignored.
- [cds-compiler@2.11.0] Properly check for duplicate annotation definitions.
- [cds-compiler@2.11.0] Correctly apply annotations on inherited enum symbols.
- [cds-compiler@2.11.0] Correctly apply annotations on elements in an inherited structure array.
- [cds-compiler@2.11.0] Fix a bug in API `defaultStringLength` value evaluation.
- [cds-compiler@2.11.0] Fix crash if named arguments are used in a function that's inside a `CASE` statement.
- [cds-compiler@2.11.0] to.sql/hdi/hdbcds: Properly flatten ad-hoc defined elements in `returns` / `params` of `actions` and `functions`.
- Correctly handle `*` in non-first position.
- Correctly handle action return types
- Correctly handle mixin association named `$self`

- [cds-compiler@2.11.0] to.cdl: doc-comments are no longer rendered twice.
- [cds-compiler@2.11.0] to.edm(x): Fix a bug in V2/V4 partner ship calculation.
- Remove warning of unknown types for Open Types in `@Core.Dictionary`.
- An empty CSN no longer results in a JavaScript type error

- [cds.java@1.21.1] Fixed a bug, causing the `TenantProviderService` to return tenants that were not (yet) successfully subscribed.
- [cds.java@1.21.1] Fixed a bug, causing exceptions when events were emitted to `MessagingService` or `AuditLogService` without an explicit `RequestContext`
- [cds.java@1.21.1] Fixed a bug, causing `ConcurrentModificationException` during processing of personal data annotations.
- [cds.java@1.21.1] Fixed a bug, causing `NullPointerException` during the outbox message deserialization of the audit-log outbox handler.
- [cds.java@1.21.1] Fixed a bug, causing asynchronous messaging events to be received multiple times, in case multiple event handlers for the asynchronous event were registered on a Remote Service.
- [cds.java@1.21.1] Fixed a bug, causing `NullPointerException` during the namespace handling in the `EnterpriseMessagingService`, in case no namespace was available. This enables usage of the service plan `dev`.
- [cds.java@1.21.1] Fixed a bug, causing blocked messaging requests in case of a high amount of parallel business requests.
- [cds.java@1.21.0] Fixed a bug causing `404 Not Found` errors, when configuring an OData V2 base path with trailing `/`
- [cds.java@1.21.0] Fixed a bug causing the error message for `@assert.range` validations to be incorrectly rendered.
- [cds.java@1.21.0] Fixed a bug in the `cds-maven-plugin` causing the goal `version` to completely fail if only the command `cds version` fails. Now it prints at least the Java SDK related version information on console.
- [cds4j@1.25.0] Code generator: Fix support for excludes
- [cds4j@1.25.0] Fix serialization of CQL statements with null values in data
- [cds@5.7.4] Complex `@restrict.where: 'exists [...] or (... or ...) or ...'` in draft union scenario no longer crashes the application
- [cds@5.7.4] Sanitization of null values for `cds.RemoteService`
- [cds@5.7.4] Handling of boolean values in draft union scenario with `$expand` query option
- [cds@5.7.4]`_4odata` flag in CQN stays non-enumerable when forwarding to another application service
- [cds@5.7.4] Handling of type references on properties of associations in `cds.minify`
- [cds@5.7.3] Message Queuing now accepts `amqp` options
- [cds@5.7.3] OData requests using lambda expressions with `contains` function
- [cds@5.7.3] Result of OData query option `$count=true` when using `$apply`
- [cds@5.7.3] `$filter` with navigation to-one equals value crashes
- [cds@5.7.3] `$skiptoken` query option allows to use arbitrary symbols except of `&` with beta OData URL to CQN parser (`cds.env.features.odata_new_parser`). In this non-integer value case the value will not be parsed into CQN.
- [cds@5.7.3] Function names in `$filter` can now be case insensitive (as per OData 4.01)
- [cds@5.7.3] `$count` in `$expand` caused server to crash
- [cds@5.7.2] Instance-based restriction for activation of draft enabled entities
- [cds@5.7.2]`.columns('*')` on projections of remote services using renamed properties
- [cds@5.7.2] GraphQL filters on nested fields are now applied correctly
- [cds@5.7.2] Performance degradation during processing of `where exists`
- [cds@5.7.2] Read drafts via navigation with complex filter expression
- [cds@5.7.1] Draft (OData flavors `w4`, `x4` and `v4` with structs): Flags `HasActiveEntity`, `HasDraftEntity`, and `IsActiveEntity` are now included in the HTTP response for GET requests.
- [cds@5.7.1] Instance-based restriction on entities using localized fields in draft
- [cds@5.7.1] Results of actions/functions do not ignore nested data if query options are present
- [cds@5.7.0] Path resolution for references in sub selects
- [cds@5.7.0] Where exists without infix filter, for example, `@restrict.where: 'exists author'`
- [cds@5.7.0] `@restrict.where: 'exists [...]'` in draft union scenario
- [cds@5.7.0] Select query with path exists predicates, for example, `WHERE EXISTS books[year = 2000].pages[wordcount > 1000]`
- [cds@5.7.0] Proper registration of audit log event handlers
- [cds@5.7.0] Draft: Generate foreign keys for request payloads to which extra data items are added in a custom application handler.
- [cds@5.7.0] `cds build` correctly merges `hdbmigrationtable` files that have multiple new migration versions defined.
- [cds@5.7.0] `cds.test` converts response data of failed requests to JSON to prevent lost error details
- [cds@5.7.0] Instance based restriction for draft enabled entities
- [cds@5.7.0] Delete requests for localized with compositions
- [cds@5.7.0] Ignore input for static and calculated fields during draft activate
- [cds@5.7.0] Clear extension map entry on error during CSN fetching
- [cds@5.7.0] Do not ignore errors during diff calculation
- [cds@5.7.0] Requests to mocked remote service when using custom service name with `.service` property
- [cds@5.7.0] Rollback on already backrolled or committed transactions are ignored
- [cds@5.7.0] Rollback handling in spawned background job
- [cds@5.7.0] `cds.spawn()` throws error if passed option is an instance of `cds.EventContext`
- [cds@5.7.0] Delete `timestamp` from options passed to `cds.spawn()` (transactions create their own timestamp)
- [cds@5.7.0] Type error during programmatic action/function call if no params defined
- [cds@5.7.0] Fully qualified bound actions/ functions in beta URL to CQN parser (`cds.env.features.odata_new_parser`)
- [cds@5.7.0] Draft handling: `GET` requests with navigation via `SiblingEntity` and expand to-one
- [cds@5.7.0] No audit log if sensitive data not selected
- [cds@5.7.0] Kibana formatter: do not log authorization header value
- [cds@5.7.0] Audit logging (`cds.env.features.audit_personal_data`) no longer crashes the application when using the same entity as a composition child in different parent entities
- when accessing a not existing entity

- [cds-mtx@2.4.2] Authentication request for cds extension client is now returning token again
- [cds-mtx@2.4.2] `hdbmigrationtable` files from an updated model with multiple new migration versions are now correctly merged with tenant-specific `hdbmigrationtable` files
- [cds-odata-v2-adapter-proxy@1.8.4] Unquote action/function parameter of types `cds.UUID`, `cds.Binary`, `cds.LargeBinary`, `cds.Date`, `cds.Time`, `cds.DateTime`, `cds.Timestamp`
- [cds-odata-v2-adapter-proxy@1.8.3] Prevent parsing body for HEAD requests against $batch
- [cds-odata-v2-adapter-proxy@1.8.3] Fix single quotes of URL parameters for request body conversion respecting line breaks
- [cds-odata-v2-adapter-proxy@1.8.3] Introduce proxy option `quoteSearch` to control search expression quoting. Default is `true`
- [cds-odata-v2-adapter-proxy@1.8.3] Fix bound action call to entity key having association type
- [cds-odata-v2-adapter-proxy@1.8.3] Fix action/function parameter of types date, time, datetime
- [cds-odata-v2-adapter-proxy@1.8.2] Catch and handle unexpected errors during proxy request processing
- [cds-odata-v2-adapter-proxy@1.8.2] Validate request body and content-type in request
- [cds-odata-v2-adapter-proxy@1.8.2] Switch of internal npm repository (Nexus -> Artifactory)

### Removed ​

- [cds-compiler@2.11.0] to.hdbcds: Doc comments on view columns are not rendered anymore. Doc comments on string literals will make the deployment fail as the SAP HANA CDS compiler concatenates the doc comment with the string literal. Besides that, doc comments on view columns are not transported to the database by SAP HANA CDS.
- [cds-compiler@2.11.0] to.hdbcds/sql/hdi: Forbid associations in filters after `exists` (except for nested `exists`), as the final behavior is not yet specified.
- [cds@5.7.0] Deprecated feature flags `cds.env.runtime.skipWithParameters` and `cds.env.features.skip_with_parameters`. Use `cds.env.features.with_parameters` instead.

## November 2021 ​

### Added ​

- [cds-dk@4.6.0] `cds bind` binds the given service to a hana instance by storing the credentials in .cdsrc.json in your user home directory [beta].
- [cds-dk@4.6.0] `cds import` introduced option `--include-namespaces`, which imports the custom defined namespaces.
- [cds-dk@4.6.0] `cds import` preserve documentation in CSN file for actions and functions from OData V4 EDMX file.
- [cds-dk@4.6.0] `cds import` now supports reading values of the `as` option from cds.env
- [eslint-plugin-cds@2.2.2] Added new rule 'no-join-on-draft-enabled-entities'
- [eslint-plugin-cds@2.2.1] Optimized model loading and fixed bug in loading of 'outsider' files
- [cds.java@1.20.1] The value of `DraftIsCreatedByMe` of `DraftAdministrativeData` is now properly calculated.
- [cds.java@1.20.0] Built-in validations based on annotations now set the corresponding target in error messages. This ensures that error messages in Fiori are shown directly at the relevant field, instead of in a generic popup.
- [cds.java@1.20.0] It is now possible to build a destination for a Remote Service declaratively in the configuration. All destination properties supported by SAP Cloud SDK can be used under the new section `cds.remote.services..destination.properties`. For a full list of supported destination properties take a look at SAP Cloud SDK's `com.sap.cloud.sdk.cloudplatform.connectivity.DestinationProperty` class.
- [cds.java@1.20.0] New configuration options `cds.remote.services..destination.headers` and `cds.remote.services..destination.queries` have been added and allow to configure key-value pairs of headers / queries to be added to every outgoing request of the Remote Service.
- [cds.java@1.20.0] The requested OData version is now passed to mtx-sidecar, when loading EDMX files. This enables MTX-enabled applications to use OData V2 and V4 in parallel.
- [cds.java@1.20.0] ApplicationInfo and ServiceBindings from CdsEnvironment are now added to the CDS Actuator. In addition, the loaded providers are listed. Also configurations of Remote Services and Messaging Services are now correctly displayed.
- [cds.java@1.20.0] Support for looking up service-manager bindings by tag `service-manager`
- [cds.java@1.20.0] A warning is now printed during startup, if CAP detects a potential mismatch in the `DataSource` and `PlatformTransactionManager` used to create the default Persistence Service.
- [cds-mtx@2.4.0] Added parameter `subscriptionData` to `TenantPersistenceService.deleteTenant` so that custom handlers get more information about the tenant that is deleted. Can be `{}` if there was a failed deletion attempt before that already removed the metadata.
- [cds-mtx@2.4.0] Database deployment is now internally called via cds service `TenantPersistenceService` that applications can add handlers for:cds

```
@protocol:'rest'
service TenantPersistenceService {
    type JSON {
        // any json
    }
    ...
    action deployToDb(sourceDir: String, instanceData: JSON, deploymentOptions: JSON, additionalServices: JSON);
}
```

Note that this API is not meant to be called by applications but has been introduced to allow applications to create handlers for custom logic to be executed with the database deployment.
- [cds-mtx@2.4.0] You can now diagnose deployed tables using `mtx/v1/diagnose/tables/`.

### Changed ​

- [cds-dk@4.6.4] `cds init` uses latest Maven Java archetype version `1.20.3` for creating Java projects.
- [cds-dk@4.6.1] `cds init` uses latest `Maven Java archetype` version `1.20.0` for creating Java projects.
- [cds-dk@4.6.1] `cds watch` now resolves local node modules like `hdb` even though `@sap/cds` is not installed locally. This is useful during development where `@sap/cds` shall only be installed in a 'central' location, while extra modules shall still be found in the app's dir.
- [eslint-plugin-cds@2.2.2] Compile 'model' files based on CSN flavor 'inferred'
- [eslint-plugin-cds@2.2.2] Compile 'outsider' files based on CSN flavor 'parsed'
- [eslint-plugin-cds@2.2.1] Optimized model loading and fixed bug in loading of 'outsider' files
- [cds.java@1.20.0] The enterprise-messaging multitenancy onboarding no longer restricts the application to use asynchronous onboarding by throwing an exception. Nevertheless using synchronous onboarding with enterprise-messaging is highly discouraged, as it can lead to timeout issues.
- [cds.java@1.20.1] The value of `IsActiveEntity` is now removed later in the `@Before` phase of `CREATE` and `UPDATE` events. Specifically after validations have run, in order to give them the chance to build the correct message target.
- [cds.java@1.20.0] The `CdsModelProvider` is now also triggered when using `CdsRuntime.getCdsModel(UserInfo, FeatureTogglesInfo)` with a `UserInfo` object where the tenant is set to `null`. Earlier the method always returned the default CDS model directly.
- [cds-mtx@2.4.0] Parallel tenant upgrades have been optimized so that build results for non-extended tenants are shared and the number of database interactions is reduced.
- [cds-mtx@2.4.0] An `EventTypeMissingError` is now thrown when the `eventType` parameter is missing at tenant creation.

### Fixed ​

- [cds-compiler@2.10.4] to.sql/hdi/hdbcds:Correctly complain about `exists` in conjunction with non-associations/compositions
- Don't resolve types in action returns, as this causes issues with $self-resolution

- [cds-compiler@2.10.4] to.edm(x): Be robust against transitively untyped keys in stacked view hierarchies
- [cds-dk@4.6.4] `cds import` fix for TypeError issue during OData V2 EDMX conversion to CSN.
- [cds-dk@4.6.4] `cds import ` fix now updates the service name in the package.json with only the file name. Earlier, the service name sometimes used to be of the form `A.B`, with `A` being file name and `B` being a part of the schema namespace value in the EDMX file
- [cds-dk@4.6.3] `cds watch` recovers again from compilation errors and properly prints these
- [cds-dk@4.6.3] `cds import` fix for omitting empty `doc` components.
- [cds-dk@4.6.3] `cds add lint` no longer duplicates initial contents in package.json
- [cds-dk@4.6.3] `cds add data` no longer ignores imported services for which credentials are stored in the project
- [cds-dk@4.6.2] `cds add lint` now correctly detects missing local `eslint`
- [cds-dk@4.6.2] `cds add lint` no longer removes parts of package.json
- [cds-dk@4.6.2] `cds add lint` no longer creates duplicate configuration entries
- [cds-dk@4.6.1] `cds repl` now finds modules like `hdb` that are installed locally in the app folder
- [cds-dk@4.6.1] `cds repl` now enables the `await` statement also on Windows
- [cds-dk@4.6.1] `cds lint` now limits all file extensions to those allowed by the @sap/eslint-plugin-cds ESLint configuration
- [cds-dk@4.6.0] `cds import` fix for reflecting only supported data types in csn for actions and functions for OData V4.
- [cds-dk@4.6.0] `cds import` fix for TypeError issue during OData V4 EDMX conversion to CSN.
- [cds-dk@4.6.0] `cds watch` no longer omits starting some services every other time it is restarting the process
- [cds-dk@4.6.0] `cds-ts watch` now honors a local tsconfig.json file
- [cds-dk@4.6.0] `cds import` fix for TypeError issue during OData V2 EDMX conversion to CSN.
- [cds-dk@4.6.0] `cds import` fix to generate the CSN during OData V2 EDMX conversion to CSN.
- [cds-dk@4.6.0] `cds import` fix to replace the aliases with original schema namespace value.
- [cds-dk@4.6.0] `cds import` adds `@cds.persistence.skip` back to imported models. Its accidental removal in 4.5.0 caused wrong database deployments of imported entities.
- [cds@5.6.4] Preserve log level in Kibana formatter
- [cds@5.6.4] RFC 3986 compliant segment recognition in beta URL to CQN parser (`cds.env.features.odata_new_parser`)
- [cds@5.6.4] Support for `$skiptoken` OData query option when using beta URL to CQN parser (`cds.env.features.odata_new_parser`)
- [cds@5.6.4] OData requests with `$skip` and without `$top` query option to services with defined default limit (`cds.query.limit.default`)
- [cds@5.6.4] Creating entities with binary keys. Currently the binary keys may be provided only as Node.js `Buffer` instances using a custom handler.
- _[cds@5.6.4]_Requests with payload containing nested arrayed elements no longer crash the application
- [cds@5.6.3] `cds run` does not fail if `cds.requires.multitenancy` is explicitly set to `false`
- [cds@5.6.3] Calculation of `DraftIsCreatedByMe` or `DraftIsProcessedByMe` when expanding or navigating to `DraftAdministrativeData`
- [cds@5.6.3] Nested `any` in `$filter` query option
- [cds@5.6.3] Crash on draft activate after draft edit for not existing composition of one, if no explicit DB service is defined
- [cds@5.6.3] Typescript definition of `srv.delete` no longer leads to a duplication error
- [cds@5.6.2] Handle arrayed elements using templating mechanism
- [cds@5.6.2] OData requests to `$count` endpoint of ETag enabled entity
- [cds@5.6.2] `cds.test` does no longer crash if executed in `cds repl` on a remote service call
- [cds@5.6.2] Crash on draft activate after draft edit for not existing composition of one
- [cds@5.6.2] Ensure request correlation (with default server)
- [cds@5.6.2] `.texts` points to real text entity
- [cds@5.6.2] Draft union with expand to to-one and to-many
- [cds@5.6.2] No columns in draft lock statement (i.e., use `SELECT 1`)
- [cds@5.6.1] UAA credentials lookup
- [cds@5.6.1] Revert return type validation for `cds.String` for compatibility with older `@sap/cds-mtx` versions
- [cds@5.6.1] Messaging: Ill-defined incoming AMQP messages will not crash the app
- [cds@5.6.1] `cds compile -l` does no longer crash if called without `--to` option
- [cds.java@1.20.3] Fixed a regression causing inconsistent OData responses when querying active entities and expanding `DraftAdministrativeData` (e.g. `GET /odata/v4//(ID=,IsActiveEntity=true)?$expand=DraftAdministrativeData`). In case there is no corresponding draft entity (`IsActiveEntity=false`) the response unexpectedly contains the expanded association `DraftAdministrativeData` with the single field `"DraftIsCreatedByMe": false`.
- [cds.java@1.20.1] Fixed a bug causing incorrectly normalized locales to be passed to the mtx-sidecar, when loading EDMX metadata. This caused metadata for locales like `zh-CN` or `1Q` to not load properly.
- [cds.java@1.20.1] Fixed a bug causing message targets of validations to miss `IsActiveEntity` key values in case of draft-enabled entities.
- [cds.java@1.20.0] Fixed a bug causing the row types to miss on the `Result` in case of draft queries.
- [cds.java@1.20.0] Fixed a bug for remote OData requests where data types were not correctly converted for CQN `in` predicates which lead to `400` responses from remote services
- [cds.java@1.20.0] Fixed a bug causing `NullPointerException` in case an OData V2 bound action was called on an entity with an ETag
- [cds.java@1.20.0] Fixed a bug in the `cds-maven-plugin` causing the base directory to be calculated incorrectly in case an external parent POM was referenced in the project.
- [cds.java@1.20.0] Fixed a bug in the `cds-maven-plugin` causing the goal `build` to fail if there are parameters in plugin configuration which are not valid for the goals `install-node`, `install-cdsdk`, `cds` and `generate`.
- [cds4j@1.24.1] Fix result structure of deeply nested to-one expands
- [cds-odata-v2-adapter-proxy@1.8.1] Change action/function return type value representation for primitive types to include nesting to conform to OData standard
- [cds-odata-v2-adapter-proxy@1.8.1] Introduce proxy options `returnPrimitiveNested: false` to keep previous action/function return value representation for primitive types
- [cds-odata-v2-adapter-proxy@1.8.1] Introduce proxy option `returnCollectionNested` to control collection of entity type nesting into a `results` section. Default is `true`
- [cds-odata-v2-adapter-proxy@1.8.1] Fill standardized `x-correlation-id` request header in addition to `x-correlationid` for proxy requests
- [cds-odata-v2-adapter-proxy@1.8.0] Add README documentation for annotation `@Core.ContentDisposition.Type`
- [cds-odata-v2-adapter-proxy@1.8.0] Change `content-disposition` header default from `inline` to `attachment`
- [cds-odata-v2-adapter-proxy@1.8.0] Proxy option `contentDisposition` to specify default content disposition for media streams (inline, attachment)
- [cds-odata-v2-adapter-proxy@1.8.0] Unescape single quotes of action URL parameters for request body conversion
- [cds-odata-v2-adapter-proxy@1.8.0] Fix action/function return type representation for `cds.LargeString`
- [cds-odata-v2-adapter-proxy@1.8.0] Improve formatting of README and CHANGELOG
- [cds-odata-v2-adapter-proxy@1.8.0] Adjust repository url
- [cds-odata-v2-adapter-proxy@1.7.16] `Content-Disposition` header filename is now url encoded
- [cds-odata-v2-adapter-proxy@1.7.16] Annotation `@Core.ContentDisposition.Type` to specify content disposition type (for example, inline (default), attachment, etc.)
- [cds-odata-v2-adapter-proxy@1.7.15] Quote key parts of type `cds.LargeString` for uri generation
- [cds-odata-v2-adapter-proxy@1.7.14] Decode url key values before conversion
- [cds-mtx@2.4.0] APIs `mtx.getEdmx(tenantId, service, language, odataVersion)` and the endpoint `/mtx/v1/metadata/edmx/?name=&language=&odataVersion=` now reuse the pre-build EDMX if `odataVersion` equals configured version (`cds.odata.version`)
- [cds-mtx@2.4.1] Additional HDI_DEPLOY_OPTIONS do no longer affect the stability of the meta tenant creation
- [cds-mtx@2.4.1] Reduction of redundant file system operations to improve stability of tenant upgrade
- [cds-mtx@2.4.0] Job list returned by diagnose API now contains correct results
- [cds-mtx@2.4.0] Offboarding via CDS transactions is now working without an explicit `where` clause, i.e. you can simplifyjs

```
await transaction.delete('tenant', tenantId).where({ subscribedTenantId: tenantId })
```

intojs

```
await transaction.delete('tenant', tenantId)
```

## October 2021 ​

### Added ​

- [eslint-plugin-cds@2.2.0] Added typings to javascript for all exposed APIs
- [cds-compiler@2.10.2] Support arbitrary paths after `$user` - similar to `$session`.
- [cds-compiler@2.10.2] Support scale `floating` and `variable` for `cds.Decimal` in CDL and CSN. Backend specific handling is described in their sections.
- [cds-compiler@2.10.2] Allow select item wildcard (`*`) in a `select`/`projection` at any position, not just the first.
- [cds-compiler@2.10.2] to.edm(x):In OData V4 generate transitive navigation property binding paths along containment hierarchies and terminate on the first non-containment association. The association target is either an explicit Edm.EntitySet in the same EntityContainer or in a referred EntityContainer (cross service references) or an implicit EntitySet identified by the containment path originating from an explicit EntitySet. This enhancement has an observable effect only in structured format with containment turned on.
- Support for scales `variable` and `floating`: V4: `variable` and `floating` are rendered as `Scale="variable"`. Since V4 does not support `floating`, it is approximated as `variable`.
- V2: `variable` and `floating` are announced via property annotation `sap:variable-scale="true"`

- [cds-compiler@2.10.2] to.sql/hdi/hdbcds:Reject scale `floating` and `variable`.
- Reject arbitrary `$user` or `$session` paths that cannot be translated to valid SQL.
- Following a valid `exists`, further `exists` can be used inside of the filter-expression: `exists assoc[exists another[1=1]]`
- `exists` can now be followed by more than one association step. `exists assoc.anotherassoc.moreassoc` is semantically equivalent to `exists assoc[exists anotherassoc[exists moreassoc]]`

- [cds-compiler@2.10.2] Allow defining unmanaged associations in anonymous aspects of compositions.
- [cds-compiler@2.10.2] Enable extensions of anonymous aspects for managed compositions of aspects.
- [cds-compiler@2.10.2] When the option `addTextsLanguageAssoc` is set to true and the model contains an entity `sap.common.Languages` with an element `code`, all generated texts entities additionally contain an element `language`, which is an association to `sap.common.Languages` using element `local`.
- [cds-compiler@2.10.2] for.odata:In `--odata-format=flat`, structured view parameters are flattened like elements.

- [cds-compiler@2.10.2] to.hdbcdsUse "smart quotes" for naming mode "plain" - automatically quote identifier, which are reserved keywords or non-regular.

- [cds4j@1.24.0] Allow to use refs with path prefix with anyMatch/allMatch
- [cds4j@1.24.0] Support `byParams` to simplify updates and deletes by parameters
- [cds4j@1.24.0] ORDER BYnew `CQL.sort` method to create a `CqnSortSpecification`
- new `Modifier.sort` method to modify a single `CqnSortSpecification`

- [cds4j@1.24.0] Support paths to extract data from nested rows
- [cds@5.6.0] New REST protocol adapter BetaMakes use of the beta OData URL to CQN parser. Hence, almost all OData requests are supported (see the following limitations).
- Activate via `cds.env.features.rest_new_adapter = true`
- Out of scope (compared to OData protocol adapter): OData query option `$apply`
- Batch requests (with or without atomicity groups)
- Draft handling

- [cds@5.6.0] New GraphQL protocol adapter (alpha)Serves single endpoint for all services based on `served` event at `/graphql` (subject to change).
- Activate via `cds.env.features.graphql = true`
- Required additional dependencies: `@graphql-tools/schema`, `express-graphql`, and `graphql`
- Not meant for productive use! For example, authentication and authorization are out of scope.

- [cds@5.6.0] Support of the following features when using beta OData URL to CQN parser (`cds.env.features.odata_new_parser`):REST-style URLs (example: `GET /Foo/1`)
- `$expand=*` query option on different nested expand levels (`$levels` is not yet supported)
- draft handling
- structured keys
- streaming
- navigation to primitive properties without `$value` query option

- [cds@5.6.0] Optimized Search: Support `$filter` query option in combination with optimize `$search` and localized data (when the environment variable `cds.env.features.optimized_search` is set to `true`)
- [cds@5.6.0] `GET` requests support static values in ON-conditions of composition parents when using unmanaged backlinks
- [cds@5.6.0] `destinationOptions` can be configured for Remote ServicesExample:json

```
  {"cds":{"requires":{
    "S4": {
      "destinationOptions": {
        "selectionStrategy": "subscriberFirst",
        ...
      }
    }
  }}}
```

- [cds@5.6.0] `forwardAuthToken` can be configured for Remote ServicesExample:json

```
  {"cds":{"requires":{
    "credentials": {
      "url": "...",
      "forwardAuthToken": true
      }
    }
  }}}
```

- [cds@5.6.0] File to store private project settings .cdsrc-private.json (should not be checked in source code management)
- [cds@5.6.0] Read additional configuration from JSON files or directory structures using `CDS_CONFIG` env variable
- [cds@5.6.0] Missing typescript definitions for services' `.send` shortcuts `get`, `put`, `post`, `patch`, and `delete`
- [cds@5.6.0] Build VCAP_SERVICES env variable dynamically for compatibility (`cds.env.features.emulate_vcap_services`)
- [cds@5.6.0] GET requests to Remote OData Service are automatically sent as `$batch` if the generated URL is too longCan be configured via `cds.env.remote.max_get_url_length` (beta, default: 1028).

- [cds@5.6.0] Provide ETag in response headers in case of `prefer: return=minimal`
- [cds@5.6.0] Kibana formatter: log the user's id via `cds.env.log.user = true` BetaConsider the data privacy implications!

- [cds@5.6.0] Experimental support for uiflex running locally on sqlite by setting `cds.requires.extensibility.kind = uiflex`
- [cds@5.6.0] Minified `cds.model` (deactivate via `cds.env.features.skip_unused = false`)
- [cds-mtx@2.3.2] Additional user-provided services are now accessible for the deployment

### Changed ​

- [eslint-plugin-cds@2.2.0] Aligned rule creation and tester api with ESLint
- [eslint-plugin-cds@2.1.2] Allow not only .js but also other file types (i.e..ts, etc) to bypass plugin rules
- [eslint-plugin-cds@2.1.1] Added preprocessor to avoid (other plugins) parsing errors on CDS files
- [cds-compiler@2.10.2] to.odata: Inform when overwriting draft action annotations like `@Common.DraftRoot.ActivationAction`.
- [cds-compiler@2.10.2] to.edm(x): Raise `odata-spec-violation-type` to a downgradable error.
- [cds-compiler@2.10.2] for.odata: In `--data-format=structured`, anonymous sub elements of primary keys and parameters are set to `notNull:true`, an existing `notNull` attribute is not overwritten. Referred named types are not modified.

- [cds-compiler@2.10.2] to.edm(x): Improve specification violation checks of (nested) keys: All (sub-)elements must be `Nullable: false` (error).
- Must represent a single value (error).
- In V4 must be a specification-compliant Edm.PrimitiveType (warning).

- [cds-compiler@2.10.2] to.hdi/hdbcds/sql: `$user.\` now has `\` added as alias - `$user.\ as \`
- [cds4j@1.24.0] the `com.sap.cds:cds4j-multitenant` module is replaced by `com.sap.cloud.mt:cds-mtx`
- [cds4j@1.24.0] the execution order of the individual statements of a deep insert is now guaranteed to be parent first
- [cds4j@1.24.0] GROUP BY - groups is now represented as a `List`. This affects: the return type of the `CqnSelect.groupBy()` method
- the parameter types of the `Select.groupBy` methods

- [cds4j@1.24.0] ORDER BY - the sort item is now represented as a `CqnValue`
- [cds@5.6.0] Query API: Specified keys are now part of the target path, for example, `SELECT.from('Books', 1)` will move the key condition into `SELECT.from.ref`. Deactivate during two month grace period via compat feature flag `cds.env.features.keys_into_where = true`

- [cds@5.6.0] Removed duplicate integrity checks
- [cds@5.6.0] Optimized search: Optimize queries for non-localized elements
- [cds@5.6.0] OData to CQN parsing changed to enable remote service consumption. As a side effect, application code in `srv.on('READ', handler)` custom handlers relaying on CQN might need to be adapted. The following has changed: Previously, columns in `req.query.SELECT.columns` were always defined. Now, in case there is no `$select` and `$expand` query options in the OData query, `req.query.SELECT.columns` is `undefined`.
- Previously, if the `$expand` query option was specified in the OData query, all elements of the expanded navigation property were listed explicitly in the CQN query. Now, an `*` (asterisk) is listed instead.

- [cds@5.6.0] Non-specified columns are resolved at database layer
- [cds@5.6.0] `cds deploy` no longer enforces the presence of SAP CommonCryptoLib (checked with env variable `SECUDIR`) on Windows since it uses now the built-in security libraries
- [cds@5.6.0] Target keys are not included into a body when sending `PATCH` requests to external services

### Fixed ​

- [cds-dk@4.5.4] `cds watch` no longer fails if started with `--ext`, `--livereload`, or `--open` arguments
- [cds-dk@4.5.3] `cds import` fix for `--dry` shortcut `-`
- [cds-dk@4.5.3] `cds import` fix for missing type properties in CSN for unbounded action and function in OData V4.
- [cds-dk@4.5.3] A bug with `cds init` when called in SAP Business Application Studio project wizard
- [cds-compiler@2.10.2] to.sql/hdi/hdbcds: Correctly handle `exists` in conjunction with mixin-associations
- [cds-compiler@2.10.2] to.edm(x): Fix a bug in annotation propagation to foreign keys.
- Don't render annotations for not rendered stream element in V2.

- [cds-compiler@2.10.2] to.hdi: for naming mode "hdbcds" and "quoted" parameter definitions are not quoted anymore.

- [cds-compiler@2.10.2] to.hdi/sql/hdbcds: Correctly handle explicit and implicit alias during flattening.
- Raise an error for `@odata.draft.enabled` artifacts with elements without types - instead of crashing with internal assertions.

- [cds-compiler@2.10.2] Properly generate auto-exposed entities for associations in parameters.
- [cds-compiler@2.10.2] Correctly apply extensions to anonymous array item types.
- [cds-compiler@2.10.2] Correctly apply/render annotations to anonymous action return types.
- [cds-compiler@2.10.2] With CSN flavor `plain` (`gensrc`), correctly render annotations on elements of referred structure types as `annotate` statements in the CSN's `extensions` property.
- [cds-compiler@2.10.2] to.cdl: Correctly render extensions on array item types
- Correctly render annotations on action return types

- [cds-compiler@2.10.2] to/for: Correctly handle CSN input where the prototype of objects is not the "default"
- [cds-compiler@2.10.2] to.hdi: for naming mode "hdbcds" and "quoted" parameter definitions are now quoted.
- for naming mode "plain", smart quotation is applied to parameter definitions if they are reserved words.

- [cds-compiler@2.10.2] to.hdi/hdbcds/sql: Ensure that cdl-style casts to localized types do not lose their localized property
- Fix a small memory leak during rendering of SQL/HDBCDS.

- [cds-compiler@2.10.2] to.edm(x): Remove ambiguous `Partner` attribute from `NavigationProperty`. A forward association referred to by multiple backlinks (`$self` comparisons) is no longer partner to an arbitrary backlink.
- [cds4j@1.24.0] Fix support for associations in ON condition
- [cds@5.6.0] Audit logging of non-string values
- [cds@5.6.0] Query API compilation error when keys start with `{`
- [cds@5.6.0] Handling of wrong `Edm.DateTimeOffset` values
- [cds@5.6.0] Using UUIDs in search with beta OData URL to CQN parser (`cds.env.features.odata_new_parser`)
- [cds@5.6.0] Runtime exception for READ requests with deeply nested navigation and structured keys, for example: `GET foo/Bar/b708ad6c-2dd4-40d5-91c0-2e3eacf306d2/Info/sales(a='1010',b='10',c='00')/functions(functionName='error')`
- [cds@5.6.0] The check for the minimum Node.js version now properly enforces version 12.18, i.e. aborts server startup.
- [cds@5.6.0] `cds.test` fails with a clearer error message if the server wasn't started at all
- [cds@5.6.0] Audit logging for modification of personal or sensitive data when using same entity as a composition child in different parent entities
- [cds@5.6.0] Deleting an entity defined with managed composition of one, whereas a dependent entity is defined having an independent managed association to its composition parent no longer crashes the application
- [cds@5.6.0] Audit logging for entities having arrayed elements
- [cds@5.6.0] Filtering for `cds.Date` on Remote OData V2 services
- [cds@5.6.0] Crash when `rollup` function was used in groupBy in OData requests
- [cds@5.6.0] Or for $filter with IsActiveEntity=true for access to active entities
- [cds@5.6.0] Reading draft-enabled entity with `$expand` targeting non-draft associations
- [cds@5.6.0] Delete with sub-select
- [cds@5.6.0] Runtime exception when streaming property annotated with `@Core.MediaType: 'application/json'`
- [cds@5.6.0] Reading streams via navigation when entity containing large data is a part of a draft-enabled composition tree
- [cds@5.6.0] Read draft entity with nested exists restriction
- [cds@5.6.0] Activate draft of entity having `to-one` and `to-many` compositions
- [cds@5.6.0] Caching issue that causes the OData `omit-values` preference in `Prefer` HTTP headers to misbehaves
- [cds@5.6.0] Deletion of draft instances if multiple draft enabled entities are used within one service
- [cds@5.6.0] Queries with `contains` filter targeting a remote OData V2 service
- [cds@5.6.0] Schema evolution support for nested CDS entities in `cds build`
- [cds@5.6.0] i18n texts with quotes and other special characters get escaped correctly if they appear in XML and JSON documents
- [cds@5.6.0] Execution of plain SQL statements on SQLite
- [cds@5.6.0] `Content-Disposition` header is now URL encoded
- [cds@5.5.5] Action parameters set to null
- [cds@5.5.5] Restrictions with "where exists" clause and filter on ambiguous fields
- [cds@5.5.5] Nulled user attribute in restrictions with "where exists" clause
- [cds@5.5.5] Wait for all queries to settle during deep operation
- [cds@5.5.4] Backwards compatibility for `cds.tx({ user: new User ({ tenant, locale }) })`
- [cds@5.5.4] Transaction API fix: `cds.tx ({ tenant }, tx => { ... })` instead of `cds.tx (tx => { ... }, { tenant })`
- [cds@5.5.4] Writable and reliable `query._target`
- [cds@5.5.4] `req.target` in REST with navigations in URL
- [cds@5.5.3] Resolving of views for view definitions using aliases
- [cds@5.5.3] `cds.test` in `cds repl` no longer yields an error with the beforeEach function not found
- [cds@5.5.3] Aliasing in case of draft union when expanding more than one `to-one` association
- [cds@5.5.3] Resolving of views if intermediate views are defined in database namespace
- [cds-mtx@2.3.4] Fixed full build logs not being part of the jobs logs.
- [cds-mtx@2.3.3] Job status reports for asynchronous tenant base model updates now contain the correct build and deployment logs.
- [cds-mtx@2.3.3] With SAP HANA build task configurations having subfolders, for example, `sap/db` instead of `db`, native SAP HANA artifacts and CSV files are now deployed correctly.
- [cds-mtx@2.3.3] API `mtx/v1/model/content` now also works with tenant from URL as specified
- [cds-mtx@2.3.3] Update of tenant metadata containers on SAP HANA Cloud no longer fails
- [cds-mtx@2.3.2] The `mtx/v1/diagnose/jobs` API will now correctly deliver job information about jobs in memory.
- [cds-mtx@2.3.2] Compatibility with cds < `@sap/cds@5.5.0` when running onboarding, upgrade, or extend on java projects has been fixed.
- [sap/ux-cds-odata-language-server-extension@1.3.5] Unjustified error "path does not exist" for paths pointing to entity elements defined as structured type.
- [cds-odata-v2-adapter-proxy@1.7.13] Escape quotes in search string before quoting
- [cds-odata-v2-adapter-proxy@1.7.12] Proxy option `propagateMessageToDetails` to always propagate root error or message to details section
- [cds-odata-v2-adapter-proxy@1.7.12] Support for fetching EDMX metadata locally via `cds.mtx.getEdmx`
- [cds-odata-v2-adapter-proxy@1.7.12] Support for fetching EDMX metadata remotely via MTX service URL

### Removed ​

- [cds@5.6.0] Usage of `@sap/xsenv` is superseded with `cds.env` in Node.js cds-runtime
- [cds@5.6.0] `@odata.on.insert/update` and `#user/now` are deprecated and will be removed in the next major version. Use `@cds.on.insert/update` and `$user/now` instead.

## September 2021 ​

### Added ​

- [cds-dk@4.5.1] `cds import` introduced option `--as` which converts EDMX file to different file formats such as CDS, CSN, and JSON.
- [cds-dk@4.5.1] `cds import` introduced flag `--f`, which forcefully overwrite the content of existing cds file when specified with `--as` option.
- [cds-dk@4.5.0] `cds import` supports import of functions, action, functionimport, and actionimport from both OData v2 and v4 edmx files.
- [vscode-cds@4.3.0] doc comments are automatically aligned
- [vscode-cds@4.3.0] new command: Restart CDS Language Support
- [cds-compiler@2.7.0] to.hdi.migration: Support changes to HANA comments.
- [cds-compiler@2.7.0] Support managed associations without foreign keys. Associations targeting a definition without primary keys or with an explicit empty foreign key tuple or with empty structured elements as foreign keys and their corresponding `$self` comparisons do not describe the relationship between the source and the target entity. These associations can be used to establish API navigations but cannot be used to access elements in the target entity as they cannot be transformed into a valid JOIN expression. Consequently, these associations are not added to the `WITH ASSOCIATIONS` clause or forwarded to SAP HANA CDS.
- [cds-compiler@2.7.0] to.sql/hdi/hdbcds/edm(x)/for.odata: Structure/managed association comparisons (tuple comparisons) are now also expanded in infix filters, all expressions, and all on-conditions.
- [cds-compiler@2.7.0] to.hdbcds: Better locations for messages - mostly concerning keywords and duplicates
- [cds.java@1.19.0] The CSV import is now more robust, for example simply ignoring files with empty content.
- [cds.java@1.19.0] The Correlation ID is now stored in the Request Context and propagated in outgoing HTTP requests using header `X-CorrelationID`. On incoming requests the correlation ID is obtained from the SLF4j MDC (ensuring compatibility with cf-java-logging-support) or from headers `X-CorrelationID` or `X-Correlation-Id`. If no correlation ID is present when a new Request Context is opened an ID will be generated automatically and also placed in the SLF4j MDC.
- [cds.java@1.19.0] The tenant ID is obtained from the `UserInfo` and placed in the SLF4j MDC on incoming requests (ensuring compatibility with cf-java-logging-support).
- [cds.java@1.19.0] The destination name of a Remote Service now defaults to the name of the Remote Service.
- [cds.java@1.19.0] The initial version of the logical messaging layer has been added, enabling applications to receive events on Remote Services and emit events from their Application Services from/to an external message broker.
- [cds.java@1.19.0] Improved resilience of JMS connections, by additional reconnect attempts if the built-in JMS reconnect eventually fails. The default amount of JMS reconnect attempts was lowered from `17280` to `10` as part of this change. To increase the reconnect attempts again set `cds.messaging.services..connection.properties.MaxReconnectAttempts`
- [cds.java@1.19.0] The AMQP Idle-Timeout is now configurable for Enterprise Messaging services, by setting `cds.messaging.services..connection.properties.AmqpIdleTimeout`. The default has changed from `60000` to `-1` (infinite), which is in line with the new default of the updated Enterprise Messaging library.
- [cds.java@1.19.0] SAP Event Mesh service bindings can now be detected in the environment based on the `enterprise-messaging` tag.
- [cds.java@1.19.0] Support $user values as function parameters in `where`-conditions of `@restrictions`. Make sure that the `$user`attribute has a single value only (`$user.` could be empty or a list of values, in general). Otherwise, the authorization check fails with error code 403.
- [cds.java@1.19.0] The `Message` and `ServiceException` API has been extended by the following:`Message#target(String, Function)`
- `Message#target(String, Class, Function)]`
- `ServiceException#messageTarget(String, Function)`
- `ServiceException#messageTarget(String, Class, Function)` These newly added methods allow the generation of message targets with a target parameter. The target parameter defines to which event context parameter the message refers to. Based on this information the OData v4 adapter can automatically add the binding parameter in case of actions or functions to the target, if required.

- [cds.java@1.19.0] Testability improvements for the `MessageTarget` by having added `MessageTarget#getRef()` to the interface. The new method `getRef()` returns a `CqnReference`, which provides `toJson()` to return it as a `Json` string. You can now, for example, use `target1.getRef().toJson()` and `target2.getRef().toJson()` of `MessageTarget` `target1` and `target2`, and compare the respective string values.
- [cds.java@1.19.0] The `cds-maven-plugin` provides the new goal `version`, which prints detailed version information about a CAP Java project on the console.
- [cds.java@1.19.0] Added support for `exists` predicate in `where`-conditions of instance-based authorizations. The new predicate `exists` conveniently allows to define authorization rules that are derived from associated entities (1:n). For instance, the `where`-clause `exists members[userId = $user and role = ''Editor'']'` filters all instances, which have an associated entity in `members` with matching `userId` and `role`.
- [cds4j@1.23.0] Support batch selects Beta
- [cds4j@1.23.0] Support deep bulk updates
- [cds4j@1.23.0] Support deep searched updates
- [cds4j@1.23.0] Support bulk updates with heterogeneous entries
- [cds4j@1.23.0] Support updates on structured elements
- [cds4j@1.23.0] Optimize execution of to-one expand all expands
- [cds4j@1.23.0] Optimize execution of nested to-one expands
- [cds4j@1.23.0] Make max batch size configurable via `cds.sql.max-batch-size`
- [cds4j@1.23.0] Support `any/allMatch()` to apply filters on associated collections in update and delete statements
- [cds4j@1.23.0] Add processing modes for the `CdsDataProcessor` validator
- [cds4j@1.23.0] Use 100 ns precision for timestamps on HANA and MySQL
- [cds4j@1.23.0] Support Java String datatype for `@Core.isURL`
- [cds@5.5.1] Support for casting SQL function input
- [cds@5.5.0] Support for minified models
- [cds@5.5.0] Messaging: Webhooks use 'application/json' as the default content type
- [cds@5.5.0] Messaging: If senders don't use `data` as a property of the payload, then the whole payload is interpreted as `data`
- [cds@5.5.0] Messaging: Support for `$namespace` placeholder in queue name
- [cds@5.5.0] Support for deletable singletons with `@odata.singleton.nullable`
- [cds@5.5.0] Remote requests set the `accept-language` header according to the original request or the user's locale
- [cds@5.5.0] Support for choosing data source names different from names of respective service definitions. Example:json

```
  {"cds":{"requires":{
    "S4": {
      "model": "...", "service": "API_BUSINESS_PARTNER"
    }
  }}}
```
- [cds@5.5.0] When calling `cds.tx()` to create new transactions, this now automatically inherits the current event context from `cds.context`. In case that creates issues set `cds.env.features.cds_tx_inheritance = false` to restore the former behaviour. You can still overwrite individual context settings, for example:js

```
const tx = cds.tx() // inherits tenant and user
const tx = cds.tx({ // inherits tenant
  user: new cds.User.Privileged
})
```
- [cds@5.5.0] Method `cds.tx()` now allows to pass a function, which will be executed within a new managed transaction, with `tx.commit/rollback()` handled automatically. For example:js

```
await cds.tx (tx => {
  await tx.insert (...)
  await tx.read (...)
})
```

is equivalent to:js

```
const tx = cds.tx ()
try {
  await tx.insert (...)
  await tx.read (...)
  await tx.commit()
} catch {
  await tx.rollback()
}
```
- [cds@5.5.0] Method `cds.tx({user})` now allows specifying a user as a plain string, for example:js

```
cds.tx ({ user:'me' })
```

is equivalent to:js

```
cds.tx ({ user: new cds.User('me') })
```
- [cds@5.5.0] Newly introduced method `cds.spawn()` allows correctly and conveniently spawning background jobs from within event handlers. Thereby ensuring a detached fully managed ACID transaction set as `cds.context` for each execution of the background job, inheriting the current event context from the outer `cds.context` by default. Usage options:js

```
cds.spawn (async ()=>{
  await INSERT.into ('Ticker') ...
})
```

js

```
cds.spawn (async ()=>{
  await INSERT.into ('Ticker') ...
},{ after: 111 /* ms */ })
```

js

```
let n=0, handle = cds.spawn (async ()=>{
  await INSERT.into ('Ticker') ...
  if (++n>9) clearTimeout (handle)
},{ every: 111 /* ms */ })
```

js

```
cds.spawn (async ()=>{
  await INSERT.into ('Ticker') ...
},{ // inherits tenant
  every: 111 /* ms */,
  user: new cds.User.Privileged
})
```
- [cds@5.5.0] Default server is CORS-enabled for all origins if not in production
- [cds@5.5.0] Default lock acquire timeout for `SELECT FOR UPDATE` via `cds.env.sql.lock_acquire_timeout`
- [cds@5.5.0] Optimized search: Support `groupby` for localized data (when the environment variable `cds.env.features.optimized_search` is set to `true` on SAP HANA)
- [cds@5.5.0] Out-of-the-box audit logging for deep structures without own association to data subject limited to one data subject per role per composition tree
- [cds@5.5.0] Support for reading streams via `GET /()/$value`
- [cds@5.5.0] Draft choreography: support of navigation with `SiblingEntity`
- [cds@5.5.0] Support for where exists with infix filters in `@restrict`
- [cds@5.5.0] Support annotation `@Capabilities.ExpandRestrictions.NonExpandableProperties`
- [cds@5.5.0] `@Core.ContentID` added to OData error responses if `content-id` header is specified
- [cds@5.5.0] New OData URL to CQN parser (`cds.env.features.odata_new_parser`):support of navigation to primitive properties using `$value`
- support of `not` operator with string functions (`contains`, `startswith`, `endswith`)

- [cds@5.5.0] Support for default values for virtual fields
- [cds@5.5.0] Payload for non-writable navigation targets removed from `req.data`
- [cds@5.5.0] `cds build` supports i18n message bundles for Java and Nodejs apps and a default CSN format option for Java
- [cds@5.5.0] View resolving considers renaming of foreign keys and `excluding` names when `columns` are explicitly provided in CQN
- [cds@5.5.0] Resilient acquire for SAP HANA via `cds.env.requires.db.connection_attempts = ` (alpha; hard max of 3 enforced)
- [cds@5.4.6] Support for nested where exists in `@restrict` (CRUD-only; beta)
- [cds-mtx@2.3.0] Tenant upgrade is now internally called via CDS service `TenantPersistenceService` that applications can add handlers for:cds

```
@protocol:'rest'
service TenantPersistenceService {
    type JSON {
        // any json
    }
    ...
    action upgradeTenant(tenantId: UUID, instanceData: JSON, deploymentOptions: JSON) returns JSON;
}
```

Please note that this API is not meant to be called by applications but has been introduced to allow applications to create handlers for custom logic to be executed with the tenant upgrade.

- [cds-mtx@2.3.0] Beta It is now possible to get the EDMX for services with a different OData version than the version configured for the build. API `mtx.getEdmx(tenantId, service, language, odataVersion)` and the endpoint `/mtx/v1/metadata/edmx/?name=&language=&odataVersion=` now supports a parameter `odataVersion`. Please note that the output is compiled on-the-fly if `odataVersion` is specified which has potential impact on the performance. You will also have to run a tenant upgrade for existing tenants (`/mtx/v1/model/upgrade`) to get a correct result.
- [cds-mtx@2.3.0] Extensions can now be reset via API `/mtx/v1/model/reset` and `/mtx/v1/model/asyncReset`.
- [cds-mtx@2.3.0] The job removal timeout is now configurable using `cds.mtx.jobs.removalTimeout`.
- [cds-mtx@2.3.0] `mtx.jobs.maxParallelExecutions` can now be used to parallelize asynchronous jobs. The default is `2`.

### Changed ​

- [cds-dk@4.5.2] `cds init` uses latest `Maven Java archetype` version `1.19.0` for creating Java projects.
- [cds-dk@4.5.1] Marked `cds lint` as beta again to further investigate issues from 'extends' via prettier plugin.
- [cds-dk@4.5.0] `cds init` uses latest `Maven Java archetype` version `1.18.1` for creating Java projects.
- [eslint-plugin-cds@2.1.0] Source code is now Javascript only
- [eslint-plugin-cds@2.1.0] Rule API simplified to only include report and cds
- [eslint-plugin-cds@2.1.0] Added new rules `no-db-keywords` and `require-2many-oncond`
- [eslint-plugin-cds@2.1.0] Filter out lint messages when run from command line with custom formatter
- [vscode-cds@4.3.0] consume `cds-lsp 5.3.0`
- [vscode-cds@4.3.0] consume `cds-compiler 2.7.0`
- [vscode-cds@4.3.0] translation support is now lazy
- [vscode-cds@4.3.0] performance improvements when translation files changed
- [vscode-cds@4.3.0] last workspace/symbols are cached now to speed up CAP explorer
- [vscode-cds@4.3.0] user setting `cds.workspace.scanCsn` has now three modes: Off, ByFileExtension (new default) and InspectJson
- [cds-compiler@2.7.0] Updated OData vocabularies 'Common', 'Core'
- [cds-compiler@2.7.0] to.sql/hdi/hdbcds: Invalid (i.e. not expandable) usage of structures is now checked - an error is raised
- [cds.java@1.19.0] The technical messaging layer no longer replaces `.` with `/` in topic names that match the qualified name of an event definition in the CDS model.
- [cds.java@1.19.0] Methods for message target generation in the `Message` and `ServiceException` API that accept a target prefix have been deprecated. Instead, methods are provided that enable to specify a target parameter of the event context that the message refers to.
- [cds.java@1.19.0] In both `Message` and `ServiceException` the API to pass a prefix and an entity name has been deprecated: `Message#target(String, String, Function)`
- `ServiceException#messageTarget(String, String, Function)` Instead, paths can now also be built with arbitrary parameters (for example, entity-typed action input parameters) using:
- `Message#target(Function)`
- `ServiceException#messageTarget(Function)` Specifying a prefix is no longer necessary as it is added automatically if required.

- [cds.java@1.19.0] `TenantProviderService#readTenants()` resp. `TenantProviderService#readTenantsInfo()` return a `List` with a single `null` entry resp. a `TenantInfo` with `null` indicating the default provider tenant in case of a single tenant(ST) application. In previous versions the returned lists was empty. There is no change for multitenant(MT) applications.
- [cds.java@1.19.0] When switching to privileged user with `RequestContextRunner#privilegedUser()`, not only the tenant, but also additional user attributes from the current user are propagated which contain more detailed tenant information.
- [cds@5.5.1] Support for casting SQL function input
- [cds@5.5.0] Messaging: Webhooks will always generate tokens
- [cds@5.5.0] Messaging: In multitenancy mode, messaging artifacts are only deployed to subscribers (unless the service option `deployForProvider` is set to `true`)
- [cds@5.5.0] Messaging: Incoming messages without corresponding handlers are not acknowledged
- [cds@5.5.0] If a service executes a query targeting a projection on one of its entities, the query is resolved along with projections to an entity known by the executing service. The result is post-processed to reflect the expected result of the incoming query. The reason is that no handlers of the executing service were executed as they did not know the query target. Deactivate during two month grace period via compact feature flag `cds.env.features.resolve_views = false`

- [cds@5.5.0] Use `@sap/cds-compiler`'s `smartId` function to determine whether a reference needs to be quoted. Allows the use of non-word characters in column names, for example `entity Foo { ![bar/bz]: String; }`.
- Support for columns with spaces with feature flag `cds.env.features.spaced_columns`.
- Note: Restrictions in other layers (example: OData's simple identifier schema) still apply.
- Note: Expressions in references (example: `ref: ['foo as bar']`) currently works but was never intended to and will be removed in future versions.

- [cds@5.5.0] Clear draft data based on their draft UUID instead of via deep delete
- [cds@5.5.0] Support `@sap/cds-compiler`'s changes for DB constraints: managed and unmanaged compositions of one behave like associations. This means that only `$self`-managed composition of one gets `DELETE CASCADE` constraint. Since all other "2one" cases require extra `DELETE` handled by the runtime, that constraint is ignored.
- [cds@5.5.0] Value with regards to date and time functions are not converted to strings in the OData protocol adapter
- [cds@5.5.0] No placeholders for `LIMIT` to enable statement caching during pagination
- [cds@5.5.0] Arrayed elements stringified in DB layer
- [cds@5.5.0] Return values of handlers will have precedence over database reads
- [cds@5.5.0] Error of a failed request to a Remote Service contains now the response payload if available
- [cds@5.5.0] Configuring ad-hoc destinations via `credentials.url` is now allowed in `NODE_ENV=production`
- [cds@5.5.0] New OData URL to CQN parser (`cds.env.features.odata_new_parser`): CQN for `$select` and `$expand` columns

- [cds@5.4.6] Support for nested where exists in `@restrict` (CRUD-only; beta)
- [cds-mtx@2.3.0] Tenant updates are now parallelized. You can set the pool size using `mtx.jobs.parallelUpgradeLimit`. The default is `4`.
- [cds-mtx@2.3.0] `mtx.jobs.intervalTimeout` is now deprecated, as the job queue does not require polling any more.
- [cds-mtx@2.3.0] The default queue size for asynchronous jobs has been increased to `1000`.
- [cds-mtx@2.3.0] In case of errors, the full `hdi-deploy` logs are now also printed for the default logging level.
- [cds-sidecar-client@1.2.0] This package is no longer maintained. Use `@sap/cds-dk` instead.

### Fixed ​

- [cds-dk@4.5.2] `cds deploy --to sqlite` now writes `credentials.database` again to package.json
- [cds-dk@4.5.0] `cds watch` additional CLI args were not passed to launched process, e.g. `--odata x4`.
- [cds-dk@4.5.0] `cds import` fix for TypeError issue during OData v4 edmx conversion to csn.
- [cds-dk@4.5.0] `cds import` fix for multi-line documentation text in OData v2 edmx file.
- [cds-dk@4.5.0] `cds import` fix for v4 csn generation when non standard OData vocabularies are referred.
- [cds-dk@4.5.0] `cds add data`no longer fails for entities without keys
- no longer creates csv files for synthetic draft entities
- no longer creates entries for virtual fields
- no longer skips over entities marked with `@cds.persistence.skip`, which is true for 'external' entities created by `cds import`.

- [cds-dk@4.5.0] `cds init --add` handles comma list correctly.
- [cds-dk@4.4.2] Use latest `cds-sidecar-client` to fix file upload in `cds activate`
- [cds-dk@3.5.3] Use latest `cds-sidecar-client` to fix file upload in `cds activate`
- [vscode-cds@4.3.0] certain localized elements were still indexed
- [vscode-cds@4.3.0] new i18n entry in properties file has corrupted existing last entry
- [vscode-cds@4.3.0] inconsistency in dependency calculation could have led to incorrect re-validations after a change
- [cds-compiler@2.7.0] Fix memory issue: do not keep reference to last-compiled model.
- [cds-compiler@2.7.0] Fix dump, which occurred when trying to report that the user has defined an element to be both `key` and `localized` if `localized` was inherited via the provided type, or in the generated entity for a managed composition of aspect.
- [cds-compiler@2.7.0] Properly auto-expose targets of associations in parameters and `many`.
- [cds-compiler@2.7.0] for.Odata:Fix handling of annotation `@cds.odata.valuelist` in conjunction with associations in structures using flat-mode and sqlMapping set to plain.
- Set correctly the $localized property in the OData backend resulting CSN for artifacts that have localized convenience views.

- [cds-compiler@2.7.0] to.edm(x):Fix rendering of structured referential constraints and nested partnerships in combination with `$self` comparisons.
- Fix merging of `@Capabilities` annotations while transforming them into `NavigationCapabilities` from the containee into the container.

- [cds-compiler@2.7.0] to.sql/hdi/hdbcds:Fix a bug in Association to Join translation in multi-level association redirection in combination with `$self`.
- Correctly flatten paths with filters or parameters.
- Improve error message in case of invalid `exists`.

- [cds-compiler@2.7.0] to.sql/hdi/hdbcds/edm(x)/for.odata: Correctly handle tuple expansion in subqueries of Unions.
- [cds-compiler@2.7.0] Make `;` optional before `}` in all circumstances (was not the case with `many`).
- [cds-compiler@2.7.0] to.sql/hdi/hdbcds/edm(x): More graceful handling of CSN input where associations do not have `keys` or an `on`-condition
- [cds.java@1.19.0] Fixed a bug causing element paths (e.g. `details.filename`) to be handled incorrectly in `@Core.MediaType` or `@Core.ContentDisposition.Filename` annotations.
- [cds.java@1.19.0] Fixed a bug causing synchronous tenant subscription to fail with the exception message "Only asynchronous SaaS subscription is supported when using enterprise-messaging with multitenancy" but messaging is actually configured with single tenant mode.
- [cds.java@1.19.0] Fixed a bug causing a draft child entity to have the wrong `DraftUuid` if it was created through a cqn path expression via an association.
- [cds.java@1.19.0] Fixed a bug that caused invalid OData aggregation requests with `$apply` when defined on target entities with instance-based authorizations.
- [cds.java@1.19.0] Fixed a bug where the `LastChangeDateTime` of a draft was not changed if a child entity was deleted or added.
- [cds.java@1.19.0] Fixed a bug in `cds-maven-plugin`, where it incorrectly determines the working directory with maven 3.8.x and a remote parent pom.
- [cds.java@1.18.3] Fixed a bug in OData V4 adapter, which caused a `BufferOverflowException` when processing batch requests with exact size of 16376 characters.
- [cds.java@1.18.2] Fixed a bug causing the Multitenancy HealthCheck to run into a `NullPointerException` resulting in the database being considered as `DOWN`.
- [cds.java@1.18.2] Fixed a bug causing issues in decoding Base64 Strings in responses from remote OData services.
- [cds.java@1.18.1] Fixed a bug causing `401 Unauthorized` errors when accessing the SaaS Registry due to the usage of expired JWT tokens.
- [cds.java@1.18.1] Fixed a bug causing the `MtUnsubscriptionClearDatasourceHandler` to not be loaded in a valid multi-tenant scenario.
- [cds.java@1.18.1] Adopted fixes of cds4j `1.22.1`
- [cds4j@1.23.0] Code generator:Fix case of inherited interface name
- Fix return type of inline defined arrayed type for EventContext interfaces
- Support structured elements as parameter of action/function

- [cds4j@1.23.0] Apply @cds.on.insert also for excluded elements
- [cds4j@1.23.0] Use 1 ms precision for timestamps on Mongo DB
- [cds4j@1.23.0] Fix NotNullConstraintException for temporal aspects
- [cds4j@1.23.0] Non-matching single updates now return a result with a single empty row to be consistent with the result of bulk updates
- [cds4j@1.22.1] Code generator: Fix of return type of inline structured type
- [cds@5.5.2] `$expand` requests with virtual fields with the same name in root and child
- [cds@5.5.2] Requests expanding `DraftAdministrativeData` when compound keys are used
- [cds@5.5.2] `SELECT.columns` with an empty array as argument
- [cds@5.5.2] Queries with complex lambda filters
- [cds@5.5.1] Typo in `DELETE` method of `cds.test`
- [cds@5.5.1] View resolving for intermediate queries
- [cds@5.5.1] Result post processing for renamed expands
- [cds@5.5.1] Don't use placeholder values for `null`
- [cds@5.5.0] `SELECT.from (Foo, f => f.bar('*').where(...))` resulted in a runtime exception
- [cds@5.5.0] Preserved locales are now considered when accessing database tables
- [cds@5.5.0] Integrity checks for compositions by draft enabled entities
- [cds@5.5.0] Constant columns must not be quoted anymore, i.e. `{ val: "'myValue'", as: "myColumn"}` must be changed to `{ val: "myValue", as: "myColumn" }`
- [cds@5.5.0] Accidental `tx.run()` after prior `tx.commit/rollback()` lead to acquired connections not returned to pool. This is detected and disallowed now. In case that creates issues set `cds.env.features.cds_tx_protection = false` to restore the former behaviour.
- [cds@5.5.0] Structured keys are correctly resolved with pegjs-based parser
- [cds@5.5.0] Template processing for columns with spaces in their name
- [cds@5.5.0] Deep delete with recursions in composition tree (with limited recursion depth)
- [cds@5.5.0] Draft edit with recursions in composition tree (with limited recursion depth)
- [cds@5.5.0] `emit` for messaging services now also works in custom express middlewares
- [cds@5.5.0] `req.query` is a CQN object (previously array with one entry) in case of batch insert in REST adapter
- [cds@5.5.0] HasActiveEntity flag with expand
- [cds@5.5.0] `compile.to.serviceinfo` now honors default Java endpoint paths if none are configured in application.yaml
- [cds@5.5.0] `PATCH` request to a non-existent entity annotated with the `@PersonalData` annotation
- [cds@5.5.0] `req.diff()` while deep updating via composition
- [cds@5.5.0] Convert data type of elements in sub-entities (to one association) when forwarding responses to external services
- [cds@5.5.0] Update children of a composition of many (`INSERT > DELETE`) with `PATCH/PUT` having at the same time another association to one composition child respects foreign key constraints.
- [cds@5.5.0] Handling of virtual fields used in the `$filter` query option of navigation requests
- [cds@5.5.0] Copy texts in default language from active to draft table on draft edit
- [cds@5.5.0] Optimized search: Escape double quotation marks and backslashes (when the environment variable `cds.env.features.optimized_search` is set to `true`)
- [cds@5.5.0] Update for multiple rows
- [cds@5.5.0] Expand during draft union
- [cds@5.5.0] Validate content type for `$batch` requests
- [cds@5.5.0] Support for `SELECT` statements in `where` clauses when resolving views
- [cds@5.5.0] `INSERT.rows()` does not silently fill in `INSERT.entries` anymore → use `INSERT.entries()` to do so instead.
- [cds@5.5.0] `UPDATE(Foo).with({foo:{'=':'bar'})` erroneously produced:js

```
{UPDATE:{..., with:{foo:{ref:['bar']}}}} //> wrong
```

instead of:js

```
{UPDATE:{..., data:{foo:'bar'}}} // correct
```

→ to produce the ref, use one of:js

```
UPDATE(Foo).with ({foo:{ref:['bar']}})
UPDATE(Foo).with `foo=bar`
```
- [cds@5.5.0] `UPDATE.with` property stays undefined until actually filled with data
- [cds@5.5.0] Differentiate between require and initialize error of audit logging client
- [cds@5.5.0] The built-in model tree-shaking erroneously deleted explicitly modeled `.texts` entities
- [cds@5.5.0] Actions and functions with `Integer` response type in REST services
- [cds@5.5.0] Occasional drop of conditions in `WHERE` depending on the value when using structured types
- [cds@5.5.0] `PATCH` fixed for singletons and when having a keyless, for example, managed to-one navigation path
- [cds@5.5.0] Internal server error when forwarding a query to an external service whose target entity does not contain keys
- [cds@5.5.0] Nested where exists in `@restrict` via navigation (CRUD-only; beta)
- [cds@5.5.0] Expand to one in draft union
- [cds@5.5.0] Patch to autoexposed entity through composition of aspect from Fiori Elements
- [cds@5.5.0] Diff for delete in draft
- [cds@5.5.0] Streaming requests on views with joins no longer crash the application
- [cds@5.4.6] Inverse transition mapping calculation
- [cds@5.4.6] Skip empty structures during deep update
- [cds@5.4.5] Processing of null elements during deep update
- [cds@5.4.5] Performance issue during template processing
- [cds@5.4.4] For drafts, the query parameter `$top=0` in combination with `$count=true` now returns the correct `@odata.count` value
- [cds@5.4.4] Deep delete with composition of one with structured key in target
- [cds@5.4.4] Implicit delete of child with structured key
- [cds@5.4.4] Update of deeply nested entity with structured key
- [cds@5.4.4] Order by join column during draft union
- [cds@5.4.4] Skip calculated properties while following projections
- [cds@5.4.4] The `with parameters` clause is now correctly handled in sub selects if the locale parameter exceeds 3 characters
- [cds@5.4.4] Statement already finalized error on SQLite
- [cds-mtx@2.3.1] Configuration `mtx.jobs.parallelUpgradeLimit` is now correctly limiting the number of parallel tenant upgrades.
- [cds-mtx@2.3.0] The maximum filename length of sources files that are stored with the tenant metadata has been increased from 200 to 500. The tenant metadata store will be updated accordingly with any tenant operation (extend, upgrade).
- [cds-mtx@2.3.0] Exceptions from asynchronous jobs are now visible in the application log again
- [cds-sidecar-client@1.1.23] Re-enabled compatibility with CDS Compiler v1
- [cds-odata-v2-adapter-proxy@1.7.11] Convert ContentID for warning messages and error body and propagate to details
- [cds-odata-v2-adapter-proxy@1.7.11] Fix batch boundary parsing from content type with charset definition
- [cds-odata-v2-adapter-proxy@1.7.11] Functions `startswith` and `endswith` respect proxy option `caseInsensitive`
- [cds-odata-v2-adapter-proxy@1.7.10] Fix query options not part of action parameters
- [cds-odata-v2-adapter-proxy@1.7.10] Proxy option `caseInsensitive` to transform search function for example, `substringof` to case insensitive variant
- [cds-odata-v2-adapter-proxy@1.7.9] Add metadata type of inline return type for actions and functions
- [cds-odata-v2-adapter-proxy@1.7.9] Proxy option `messageTargetDefault` to specify default message target, if undefined
- [cds-odata-v2-adapter-proxy@1.7.9] Empty proxy option `messageTargetDefault` leaves message target untouched

### Removed ​

- [cds-compiler@2.7.0] The internal non-enumerable CSN property `$env` has been removed from the compiled CSN.
- [cds@5.5.0] Direct usage of body-parser
- [cds@5.5.0] Queries constructed from `cds.ql` do not have the internal property `cqn` anymore
- [cds@5.5.0] Unofficial variant `SELECT({'expand(foo)':['a','b']})` is not supported anymore → use one of these official APIs for expands instead:js

```
SELECT(x => { x.a, x.foo (f =>{ f.b, f.c }) })
SELECT(['a',{ref:['foo'], expand:['b','c']}])
```
- [cds@5.5.0] Unofficial variant `SELECT.orderBy('foo','desc')` is not supported anymore → use one of these official APIs instead:js

```
SELECT.from(Foo).orderBy({foo:'desc'})
SELECT.from(Foo).orderBy('foo desc')
```
- [cds@5.5.0] Unofficial variant `SELECT.orderBy('foo, bar desc')` is not supported anymore → use one of these official APIs instead:js

```
SELECT.from(Foo).orderBy({foo:1,bar:-1})
SELECT.from(Foo).orderBy('foo','bar desc')
SELECT.from(Foo).orderBy `foo, bar desc`
```
- [cds@5.5.0] Unofficial variant `SELECT.where({ or: [{ foo: 'bar' }, { foo: 'baz' }] })` is not supported anymore → use one of these official APIs instead:js

```
SELECT.from(Foo).where({ foo: 'bar', or: { foo: 'baz' } })
SELECT.from(Foo).where `foo='bar' or foo='baz'`
```
- [cds@5.5.0] Usage of SQL window functions during expand on HANA
- [cds@5.5.0] Hidden symbol for where clause elements originating from `@restrict`
- [cds@5.5.0] Error masking gate keeper for `cds.env.log.levels.cli`

## August 2021 ​

### Added ​

- [cds.java@1.18.0] If the new property `cds.errors.combined` is set to `true` (default setting) CAP's default validations are gathered using the `Messages` API. This allows multiple validation errors to be returned at once to the client. At the end of the Before handler phase `Messages.throwIfError()` is automatically called to abort the event processing in case of errors. Applications are encouraged to replace places where they use `ServiceException` for validations with calls to the `Messages` API to contribute to the set of validation errors and remove explicit calls of `Messages.throwIfError()` and rather rely on the framework for this.
- [cds.java@1.18.0] Multitenant Enterprise Messaging Services now support receiving events through webhooks. They integrate with the tenant onboarding process to create webhooks, queues and subscriptions for each tenant in the enterprise-messaging service instance.
- [cds.java@1.18.0] Added initial version of the `AuditLogService` with a default handler using a logger as target.
- [cds.java@1.18.0] Added new feature `cds-feature-auditlog-v2` providing a handler to send auditlog messages to AuditLog Service V2.
- [cds.java@1.18.0] Added Spring Boot logger groups to group multiple CAP loggers under a well-defined stable name.
- [cds.java@1.18.0] Added the possibility to explicitly load a default-env.json file from classpath resources, by prefixing the path passed to the property `cds.environment.local.defaultEnvPath` with `classpath:`
- [cds4j@1.23.0] prefixing the path passed to the property `cds.environment.local.defaultEnvPath` with `classpath:`
- [cds4j@1.23.0] Support resolving views with literals in the projections
- [cds4j@1.23.0] Support session context variables ($user.id, $user.locale, $at, $now) in on-conditions of associations
- [cds4j@1.23.0] Support simple insert and select on structured elements
- [cds4j@1.23.0] Anonymize literals when logging CQN select statements (configurable via cds.ql.logging.log-values)
- [cds4j@1.23.0] Static evaluation and optimization of predicate expressions
- [cds4j@1.22.0] Support resolving views with literals in the projections
- [cds4j@1.22.0] Support session context variables ($user.id, $user.locale, $at, $now) in on-conditions of associations
- [cds4j@1.22.0] Support simple insert and select on structured elements
- [cds4j@1.22.0] Anonymize literals when logging CQN select statements (configurable via cds.ql.logging.log-values)
- [cds4j@1.22.0] Static evaluation and optimization of predicate expressions
- [cds-compiler@2.5.0] Allow to extend existing array annotation values via the ellipsis operator `...`. An ellipsis may appear exactly once at an arbitrary position in the top level array of an `annotate` directive. Only array values can be merged into arrays and unapplied ellipses are removed from the final array value. Annotation layering rules remain unaffected.
- [cds-compiler@2.5.0] to.sql/hdi/hdbcds:Doc comments are translated into HANA comments (or into `@Comment` annotation for `to.hdbcds`). Such comments are possible on entities, views, elements of entities and `to.hdbcds` also supports comments on view columns. Generation can be disabled via option `disableHanaComments`. Entities/views (and their elements/columns) annotated with `@cds.persistence.journal` for `to.hdi`/`to.sql` will not have comments rendered.
- Generation of temporal `WHERE` clause can be suppressed by annotating the `validFrom`/`validTo` elements of the projection with `false` or `null`.

- [cds-compiler@2.5.0] to.sql/hdi/hdbcds/edm(x)/for.odata: Structure/managed association comparisons (tuple comparisons) are now also expanded in `WHERE` and `HAVING` - this was previously only supported in on-conditions.
- [cds-compiler@2.5.0] `cdsc` now internally uses SNAPI.
- [cds-compiler@2.5.0] to.hdi.migration:Validate that the two supplied CSNs are compatible.
- Improve delta-mechanism to not render superfluous `[ALTER|DROP|ADD]` statements for unchanged SQL.

- [cds@5.4.0] Messaging: Support for format `cloudevents`
- [cds@5.4.0] Messaging: Support for `@topic`
- [cds@5.4.0] Messaging: Support for `subscribePrefix` and `publishPrefix`
- [cds@5.4.0] Support for `ReadByKeyRestrictions` annotations
- [cds@5.4.0] Support for OData `omit-values` preference in `Prefer` HTTP header
- [cds@5.4.0] Object variant of service methods
- [cds@5.4.0] Brazilian portuguese (`pt_BR`) is now in the list of normalized locales
- [cds@5.4.0] Support for actions and functions on Remote Service
- [cds-mtx@2.2.2] There are new APIs for diagnosing memory, asynchronous jobs, and HDI containers. They can be called via`/mtx/v1/diagnose/memory`
- `/mtx/v1/diagnose/jobs`
- `/mtx/v1/diagnose/container/` Note that with this change, the `/mtx/v1/model/diagnose` API is not available any more. The new API will work out of the box with `@sap/cds >= 5.5.0`, but you have to opt-in with earlier versions by setting:

json

```
"mtx": {
  "api": {
    "diagnose": true
  }
}
```

in your package.json.

- [cds-mtx@2.2.1] `working_set` and `exclude_filter` can now be used as `HDI_DEPLOY_OPTIONS`
- [cds-mtx@2.2.1] Job log is now cleaned up with each startup to avoid garbage after application shutdowns or crashes. Maximum age of entries can be configured via cds configuration `mtx.jobs.cleanup.regular` and `mtx.jobs.cleanup.stale` (in milliseconds). "Regular" refers to finished or failed jobs (default is 30 min), "Stale" refers to queued or running jobs (default is 7 days).
- [cds-mtx@2.2.1] Beta The tenant specific URL returned to the `saas-registry` can now be specified via two environment variables `SUBSCRIPTION_URL` and `SUBSCRIPTION_URL_REPLACEMENT_RULES`. The following example uses the MTX application URL and turns it into the UI application URL by replacing the application name suffix:yaml

```
SUBSCRIPTION_URL: ${protocol}://\${tenant_subdomain}-${default-uri}
SUBSCRIPTION_URL_REPLACEMENT_RULES: [['srv', 'app']]
```

`\${tenant_subomain}` will be replaced by the domain of the subscribed tenant.

### Changed ​

- [cds-dk@4.4.0] `cds init` uses latest `Maven Java archetype` version `1.17.0` for creating Java projects.
- [cds.java@1.18.0] The cds-maven-plugin now installs `@sap/cds-dk` in version `^4` by default.
- [cds.java@1.18.0] The archetype now generates a project that uses H2 instead of SQLite as in-memory database.
- [cds.java@1.18.0] Remote Services and Application Services now both try to project queries targeting entities defined outside of their service's namespace onto entities inside of their service's namespace, before dispatching the event to event handlers.
- [cds.java@1.18.0] Environment information such as service bindings, application information or properties are no longer statically available through `Properties` or `PlatformEnvironment` classes, but can now be accessed through the `CdsRuntime` via `CdsRuntime.getEnvironment()`. This enables to create multiple CDS runtimes with different service bindings or properties in a single process. This is especially useful for Spring Boot tests in which multiple different ApplicationContext instances are launched, which is now finally supported with CAP Java.
- [cds.java@1.18.0] Service bindings or application information can now be contributed by `ServiceBindingProvider` or `ApplicationInfoProvider` implementations, which are registered on the `CdsRuntime` through the `CdsRuntimeConfigurer`. They can be registered on the `CdsRuntimeConfigurer` using an implementation of `CdsRuntimeConfiguration` during the `environment` phase. With this change the internal `PlatformEnvironment` approach has been removed.
- [cds.java@1.18.0] The events on the `MtSubscriptionService`, which are triggered by a callback from the `mtx-sidecar` (e.g. `EVENT_ASYNC_SUBSCRIBE_FINISHED`), are now asynchronous to the sidecar's request. This allows long-running tasks to be implemented during the processing of these events and before the SaaS Registry is updated with the new subscription state.
- [cds-compiler@2.5.0] - If the first source provided to the compile command has a `$sources` property (whether enumerable or not) which is an array of strings, use that instead of calculating one.
- [cds-compiler@2.5.0] Updated OData vocabularies 'Aggregation', 'Analytics', 'Authorization', 'Capabilities', 'CodeList', 'Common', 'Communication', 'Core', 'Graph', 'HTML5', 'Measures', 'ODM', 'PersonalData', 'Repeatability', 'Session', 'UI', 'Validation'
- [cds@5.4.0] In multitenant `enterprise-messaging`: If a tenant subscribes, the messaging artifact generation is awaited. In your provisioning service configuration, make sure to set `onSubscriptionAsync` to `true` and `callbackTimeoutMillis` to more than 10 minutes.
- [cds@5.4.0] In `enterprise-messaging`: Messages are sent via HTTP
- [cds@5.4.0] Computed values are preserved during draft activate
- [cds@5.4.0] Messaging: No more topic manipulation per default
- [cds@5.4.0] For consistency reasons `cds build` now determines the default model path using cds resolve
- [cds@5.4.0] Match XSUAA's user attribute value `$UNRESTRICTED` case insensitive
- [cds-mtx@2.2.2] Fixed a regression where the `ExtendCDSdelete` scope was required for extension activations even without `undeployExtension` set to `false`.
- [cds-mtx@2.2.2] Fixed an application crash at startup when `MTX_DISABLE_META_TENANT_CREATION` is set and no Instance/Service Manager credentials are available.
- [cds-mtx@2.2.1] Native HANA table data properties files are now supported.
- [cds-mtx@2.2.1] `MT_LIB_TENANT-*`-prefixed tenants are now ignored when requesting `mtx/v1/provisioning/tenant`. This fixes a compatibility problem when using the `CDS_MULTITENANCY_DATASOURCE_HANADATABASEIDS` environment variable.
- [cds-mtx@2.2.1] To reduce the number of logs, the HDI deployment output is now only logged in debug mode.
- [cds-mtx@2.2.1] Tenant metadata request via `mtx/v1/provisioning/tenant/` are now cached.
- [cds-mtx@2.2.1] `/mtx/v1/metadata/edmx/` will now throw `ServiceMissingError` if no `name` query parameter is passed, instead of defaulting to `CatalogService`.

### Fixed ​

- [cds-dk@4.4.1] Use `@sap/eslint-plugin-cds@2.0.4`
- [cds-dk@4.4.0] Fixed bug when logging in Business Application Studio during `New Project from Template` wizard.
- [cds-dk@4.4.0] `cds import` fix for `` tag in Odata V2 for EntityType and ComplexType.
- [cds-dk@4.4.0] `cds help` does not crash with `this.load is not a function` in exotic installations
- [cds.java@1.18.1] Fixed a bug causing element paths (for example, `details.filename`) to be handled incorrectly in `@Core.MediaType` or `@Core.ContentDisposition.Filename` annotations.
- [cds.java@1.18.1] Fixed a bug causing the Multitenancy HealthCheck to run into a `NullPointerException` resulting in the database being considered as `DOWN`.
- [cds.java@1.18.1] Fixed a bug causing issues in decoding Base64 Strings in respones from remote OData services.
- [cds.java@1.18.0] Fixed a bug causing incorrectly serialized errors from remote OData requests in log lines.
- [cds.java@1.18.0] Fixed a bug causing aliases in projections used in expands of to many associations on remote OData V2 services to be incorrectly handled.
- [cds.java@1.18.0] Fixed a bug causing an explicitly configured_default-env.jso_ file to be ignored in case a default-env.json file was available as classpath resource.
- [cds.java@1.18.0] Fixed a bug that caused a `NullPointerException` because `featureTogglesInfo` is `null` when trying to access the `RequestContext` in an async thread where no `RequextContext` exists, yet.
- [cds.java@1.18.0] Adopted fixes of cds4j 1.21.1
- [cds4j@1.23.0] Remove unrecognized warning for 'doc' property in simple CDS types
- [cds4j@1.22.0] Remove unrecognized warning for 'doc' property in simple CDS types
- [cds-compiler@2.5.2] to.hdbcds: Fixed a bug introduced with 2.5.0 that caused virtual elements to be rendered in views.
- [cds-compiler@2.5.0] Remove warnings 'Ignoring annotation “@odata.draft.enabled” as the artifact is not part of a service' and 'Ignoring draft node for composition target ... because it is not part of a service'
- [cds-compiler@2.5.0] Doc comments are no longer ignored after enum values and on view columns in parseCdl mode.
- [cds-compiler@2.5.0] to.cdl: Doc comments for enum values are correctly rendered.
- Enum value and doc comments are now correctly rendered if the enum is called `doc`.
- Doc comments at type references are correctly rendered.
- Empty doc comments are correctly rendered and not left out.
- Doc comments on view columns are correctly rendered.

- [cds-compiler@2.5.0] to.edm(x): OData V2: Ignore `@odata.singleton`.
- OData V4: Do not render an `edm:NavigationPropertyBinding` to a singleton if the association has cardinality 'to-many'.

- [cds-compiler@2.5.0] forOData: Fix automatic renaming of shortcut annotation (eg. `@label`) with value `null`.

- [cds-compiler@2.5.0] CSN parser: Empty doc comments are correctly parsed and not complained about.

- [cds@5.4.3] Skip calculated properties while following projections
- [cds@5.4.3] Unrestricted subclauses in `@restrict.where`
- [cds@5.4.2] Where condition in draft union in case of multiple keys
- [cds@5.4.2] Handling of nulled properties in Service Consumption
- [cds@5.4.2] Requests to Remote Services returning `text/html` result in an error
- [cds@5.4.2] View resolving is more robust for path expressions
- [cds@5.4.2] Skip foreign properties (e.g., mixins via associations) while following projections
- [cds@5.4.2] UPDATE entity with composition to aspect with structure type property
- [cds@5.4.1] Erroneously added Brazilian portuguese (`pt_BR`) removed from the list of normalized locales
- [cds@5.4.0] Disable persistency check for requests without a target
- [cds@5.4.0] Expand at draft edit
- [cds@5.4.0] Remove restriction for `$search` queries not accepting brackets
- [cds@5.4.0] Select query with infix filter in custom handler
- [cds@5.4.0] Order by on same named properties of different associations in draft
- [cds@5.4.0] Allow to call bound actions and functions of read-only entities
- [cds@5.4.0] Writing draft-enabled entities with composition of aspects (a.k.a. managed compositions)
- [cds@5.4.0] Expand to autoexposed association/composition in draft case
- [cds@5.4.0] `cds.parse.xpr()` always returns an array
- [cds@5.4.0] Allow boolean options in `cds build` CLI
- [cds@5.4.0] Integrity check in case of bulk query execution
- [cds-mtx@2.2.1] Access to metadata API (edmx, csn, languages, services) is now restricted to owner or provider tenant again
- [cds-mtx@2.2.1] Allowed `HDI_DEPLOY_OPTIONS` are now filtered correctly
- [cds-mtx@2.2.1] Correlation ids of requests are now forwarded correctly to asynchronous jobs for better supportability of MTX tenant operations.

### Removed ​

- [cds-compiler@2.5.0] Removed internal property `$viaTransform` from CSN produced by OData/SAP HANA transformation
- [cds@5.4.0] Messaging: The topic prefix `topic:` is deprecated
- [cds@5.4.0] Messaging: No default headers for format not equal to `cloudevents`

## July 2021 ​

### Added ​

- [cds-dk@4.3.0] `cds import` now supports OData V4 edmx files.
- [cds-dk@4.3.0] `cds-ts` executable starts `cds` CLI with ts-node to allow JIT compilation of Typescript
- [cds-dk@4.3.0] `cds` CLI will give you a best guess if a command cannot be found, e.g. in case of a typing mistake.
- [cds-dk@4.3.0] `cds.import` as API alternative to `cds import` command to convert edmx files to csn [beta]
- [cds-dk@4.3.0] `cds.compile.to.openapi` as API alternative to `cds compile --to openapi` to convert CDS models to OpenAPI definitions
- [cds-dk@4.2.0] `cds add data` creates csv files with basic header lines for the entities in the project. `--for` option allows for selecting individual entities or namespaces.
- [vscode-cds@4.2.0] validation mode ActiveEditorOnly (new default). The new mode reduces number of compilations during editing and thus improves responsiveness.
- [vscode-cds@4.2.0] new command Visualize CDS file dependencies to analyze using dependencies of CDS model files. Getting an overview of file dependencies can help to keep your project architecture clean. Requires the 3rd party extension Graphviz (dot) language support for Visual Studio Code (joaompinto), which can be installed with a single click.
- [vscode-cds@4.1.1] This is a quality release focusing on performance for large models. There are new user settings and some have changed their defaults. Best performance is achieved with default settings, except `cds.contributions.enablement.odata` which should be switched `off` to speed up compilation, unless feature is needed.Additional hints to increase performance:Within SAP Business Application Studio: close `CAP Data Models and Services` view. Otherwise it will ask for all workspace symbols at every change.
- Settings: `Cds › Contributions › Enablement: Odata`: switch off as already mentioned above
- Settings: `Editor › Goto Location: Alternative Definition Command`: do not select `goToReferences`. Otherwise being already on a definition will trigger find references which requires all dirty models to be recompiled.
- Settings: `Workbench › Editor › Limit: Enabled`: switch on
- Settings: `Workbench › Editor › Limit: Value`: lower the number. If open editors have `using` dependencies, a change in one editor will lead to a recompile of related editors.
- Commands `Go to References` / `Find All References` will recompile all models that might have changed due to a change in a depending model. If there are index models it often means the complete workspace is being recompiled. Until a further change, reference calculation is reasonably fast.
- Command `Go to Symbol in Workspace` will recompile the complete workspace once, then it is reasonable fast.
- Changing settings in `CDS` section will currently perform a complete workspace invalidation, i.e. required indexes will lead to recompilations on-demand as described above.
- Changing certain `cds.env` settings, for example, folder configurations will invalidate the workspace as well.

- [cds-compiler@2.4.4] to.edm(x):Warn if an `edm:Property` has no `Type` attribute.
- Warn about using the protected names 'Edm', 'odata', 'System', 'Transient' as `edm:Schema` `Namespace` values.
- Allow `$edmJson` inline annotations in `edm:Collection` and nested annotations.

- [cds-compiler@2.4.4] to.hdi/sql/hdbcds: Transform a `exists ` into a `exists `, where the subselect selects from the target of `` and establishes the same relation as `` would via the WHERE clause. Infix-filters of `` are added to the WHERE clause.
- [cds-compiler@2.4.4] `cdsc` got a new option `--fallback-parser ` that is used if an unknown or no file extension is used.
- [cds-compiler@2.4.4] to.hdi/sql: Allow association publishing in UNIONs - this was previously forbidden, but this limitation only applies to HANA CDS.
- [cds-compiler@2.4.4] to.edm(x): Support dynamic expressions as $edmJson inline code
- [cds@5.3.2] `enterprise-messaging`: Experimental support to send messages via HTTP (`emitPerHTTP: true`)
- [cds@5.3.0] `cds serve` and `cds deploy` now also load `.ts` Typescript files if started with ts-node
- [cds@5.3.0] Log formatter for Kibana Beta via `cds.env.features.kibana_formatter`
- [cds@5.3.0] First version of the `AuditLogService` BetaSupported events: `dataAccessLog`, `dataModificationLog`, `configChangeLog`, and `securityLog`
- Usage: `const AuditLogService = await cds.connect.to('audit-log'); await AuditLogService.emit/send('', )`
- Out-of-the-box audit logging for modification of personal data and access to sensitive personal data via `cds.env.features.audit_personal_data`

- [cds@5.3.0] Support for deep updates with compositions of one in `UPDATE(...).with(...)`
- [cds@5.3.0] Support for logical events in `composite-messaging`
- [cds@5.3.0] Initial support for generating OData V2 queries
- [cds@5.3.0] Preserve `DraftAdministrativeData_DraftUUID` if OData v2 client (indicated by `@sap/cds-odata-v2-adapter-proxy`)
- [cds@5.3.0] Use placeholder values for numbers with `cds.env.features.parameterized_numbers` (alpha)
- [cds@5.3.0] Support for argument-less SQL functions (for example, `current_date`)
- [cds@5.3.0] Performance optimization: Resolve localized texts for `$search` queries at runtime (alternative to localized views resolution) to avoid the performance overhead of the SQL `coalesce` function in filter operations. To enable this experimental feature for SAP HANA, you can set the `cds.env.features.optimized_search` environment variable to `true`.
- [cds@5.3.0] Performance optimization: Optimize `$search` queries using the `CONTAINS` predicate instead of the `LIKE` predicate in the `WHERE` clause of a `SELECT` statement. To enable this experimental feature for SAP HANA, you can set the `cds.env.features.optimized_search` environment variable to `true`.
- [cds@5.3.0] OData lambda expressions in `$filter`:Basic support of structured types (`cds.env.odata.flavor = x4`) on SAP HANA
- Support of navigation paths on SAP HANA, for example, `GET /Books?$filter=author/books/all(d:d/stock gt 10)`

- [cds@5.3.0] Automatic topic manipulation for non-declared events
- [cds@5.3.0] Support for events which are declared outside of service
- [cds@5.3.0] Prefer headers `return=minimal` and `return=representation`Default value is configurable at `cds.env.odata.prefer.return`
- If not configured, the default is `representation`

- [cds@5.3.0] Support for annotation `@Core.ContentDisposition`
- [cds@5.3.0] Include `x-correlation-id` in headers of outbound message
- [cds@5.3.0] Service consumption supports `search` property and arbitrary functions in CQN
- [cds@5.3.0] Support for temporal requests with different data types
- [cds@5.3.0] Support for reading single draft-enabled entities via service API (`srv.read(, { ..., IsActiveEntity: true/false })`)
- [cds@5.3.0] Support for feature toggles via `@cds/mtx`'s `ModelProviderService` based on DwC's product configuration header (alpha)Activate via `cds.env.features.alpha_toggles`

- [cds@5.3.0] Support for structured keys used in composition of aspects Beta Support for AMQP options in AQMP-based message brokers
- [cds.java@1.17.0] OData V4 now supports `GET`, `POST`, `PUT` and `DELETE` requests on primitive and complex collections.
- [cds.java@1.17.0] OData V4 analytical queries now support filtering grouped data by aggregated values.
- [cds.java@1.17.0] The values `AVG` and `COUNT` are now supported in `@Aggregation.default` annotations.
- [cds.java@1.17.0] The `@Core.ContentDisposition.Filename` annotation is now supported in OData V4 to provide media data as an attachment download.
- [cds.java@1.17.0] Queries that use `group by` are now implicitly sorted by all `group by` elements. Earlier these queries were never implicitly sorted, as they couldn't be sorted implicitly by keys.
- [cds.java@1.17.0] Aliases in projections used for remote OData queries are now supported.
- [cds.java@1.17.0] The IN operator is now supported in remote OData queries. It is transformed into multiple comparisons concatenated by OR.
- [cds.java@1.17.0] Requests to remote OData services now forward the `X-Correlation-Id` header, if it is present in the `ParameterInfo` of the currently active `RequestContext`.
- [cds.java@1.17.0] Added initial alpha support for feature toggles.
- [cds.java@1.17.0] Messaging Services now leverage the outbox by default when emitting events. To disable the usage of the outbox set `outbox.enabled: false` on the messaging service's configuration.
- [cds.java@1.17.0] Enhanced interface `EventContext` with method `keySet()` to expose a set with all parameter keys.
- [cds.java@1.17.0] The `TenantProviderService` can now also handle SaaS registry service bindings of plan `service`.
- [cds.java@1.17.0] `CdsLockTimeoutException`s are now transformed into `ServiceException`s and mapped to error code `409007`.
- [cds.java@1.17.0] As part of the update to Spring Boot 2.5 the archetype now uses `spring.sql.init.mode` instead of `spring.datasource.initialization-mode`.
- [cds.java@1.17.0] The `cds-maven-plugin` provides the new goal `build`, which performs the goals `cds` and `generate` on the current project together in one execution.
- [cds.java@1.17.0] The `cds-maven-plugin` provides the new goal `watch`, which starts the CAP Java SDK Spring Boot application and watches for changes in the CDS model. When changes are detected, the `build` goal is executed and the application is restarted.
- [cds.java@1.17.0] The `cds-maven-plugin` now enables JavaDoc generation based on comments in the CDS model by default when generating accessor interfaces.
- [cds.java@1.17.0] The SAP proprietary locale `3Q` (`en-US-x-saprigi`) is now handled correctly.
- [cds4j@1.21.0] Allow to use path expressions based on `$outer` references in an EXISTS subquery
- [cds4j@1.21.0] Support CDS doc comments in code generation
- [cds4j@1.21.0] Allow to modify `CqnContainmentTest` (contains, startsWith, endsWith) via `Modifier.containment`
- [cds-mtx@2.1.2] Tenant creation and deletion is now called via CDS service `TenantPersistenceService` that applications can add handlers for:

cds

```
@protocol:'rest'
service TenantPersistenceService {
    type JSON {
        // any json
    }

    action createTenant(tenantId: UUID, subscriptionData: JSON) returns String;
    action deleteTenant(tenantId: UUID);
}
```

- [cds-mtx@2.1.2] The global meta tenant creation in `cds.mtx.in` can now be disabled by setting the `MTX_DISABLE_META_TENANT_CREATION` environment variable
- [cds-mtx@2.1.2] Allow array as configuration for mandatory scopes for subscription and update

json

```
mtx: {
    security: {
        "subscription-scope": ["myApp.subscription","myApp.superadmin"],
        "deployment-scope": ["myApp.deployment", "myApp.superadmin"]
    }
}
```

- [cds-mtx@2.1.2] Internal on- and offboarding API for sidecar use case: POST /mtx/v1/internal/provisioning/subscribe and POST /mtx/v1/internal/provisioning/unsubscribe with payload

json

```
{
  "subscribedTenantId": ,
  "async":
}
```

- [cds-mtx@2.0.2] Internal on- and offboarding API for sidecar use case: POST `/mtx/v1/internal/provisioning/subscribe` and POST `/mtx/v1/internal/provisioning/unsubscribe` with payload:

json

```
{
  "subscribedTenantId": ,
  "async":
}
```

- [cds-mtx@2.0.1] It's now possible to provide BTP dependencies in the `mtx` settings in your .cdsrc.json instead of implementing a custom handler, by setting `mtx.dependencies` accordingly.
- [sap/ux-cds-odata-language-server-extension@1.2.3] code completion, diagnostic, and go to definition for string properties `CollectionPath` and `ValueListProperty` in `@Common.ValueList` annotation defined on the service level
- [sap/ux-cds-odata-language-server-extension@1.2.3] semantic highlighting in OData annotations

### Changed ​

- [cds-dk@4.3.2] Bumped version of `@sap/cds` to 5.3.2
- [cds-dk@4.3.1] New version of `@sap/eslint-plugin-cds`
- [cds-dk@4.3.0] `cds init` uses latest `Maven Java archetype` version `1.16.3` for creating Java projects.
- [cds-dk@4.3.0] `cds init` generates dependency entry for `hdb` instead of `@sap/hana-client`.
- [cds-dk@4.3.0] Reworked templates for cds linter.
- [cds-dk@3.5.2] Bump to latest versions
- [cds-dk@3.5.2] Use latest `cds-sidecar-client` to fix CVE-2021-33502
- [vscode-cds@4.2.0] consume `cds-lsp 5.2.0`
- [vscode-cds@4.2.0] consume `cds-compiler 2.5.0`
- [vscode-cds@4.1.1] consume `cds-lsp 5.1.1`
- [vscode-cds@4.1.1] consume `cds-compiler 2.4.4`
- [vscode-cds@4.1.1] new performance relevant user settings`cds.workspace.debounceFastChanges`: skip intermediate compilations when typing - enabled by default
- `cds.workspace.scanDependentModules`: skip scanning of node_modules - enabled by default, speeds up start-up timeNote:When using code completion for global identifiers (see `cds.completion.workspaceSymbols.minPrefixLength`) this option needs to be enabled.
- For code completion of import paths in `using` statements this option needs to be enabled.
- To include definitions from nodejs dependent modules in workspace symbols this option needs to be enabled.

- [vscode-cds@4.1.0] consume `cds-lsp 5.1.0`
- [vscode-cds@4.1.0] consume `cds-compiler 2.3.2`
- [vscode-cds@4.1.0] user settingscds.workspaceValidationMode new default: OpenEditorsOnly
- cds.workspace.scanCsn new settings with default switch off (before implicitly on)
- cds.quickfix.importArtifact new setting with default off (before implicitly on)

- [vscode-cds@4.1.0] command `Install CDS Development Kit (@sap/cds-dk) globally` will now show a progress dialog as long as it is running
- [vscode-cds@4.0.4] uses `@sap/cds-lsp@5.0.5`
- [vscode-cds@4.0.4] new user option `cds.env.fetch` to dynamically fetch cds.env when using non-default i18n file/folder names
- [vscode-cds@4.0.2] uses `@sap/cds-lsp@5.0.3`
- [vscode-cds@4.0.2] uses `@sap/cds-compiler@2.2.4`
- [cds-compiler@2.4.4] Do not inherit `@cds.persistence.skip` when `@cds.persistence.table` is set on entity.
- [cds-compiler@2.4.4] to.cdl: Opening and closing braces of empty services and contexts are now on the same line.
- [cds-compiler@2.4.4] Type `DecimalFloat` is no longer proposed for code-completion.
- [cds-compiler@2.4.4] Non-string enums without values for their enum elements are warned about.
- [cds-compiler@2.4.4] OData CSN is no longer sorted by definition names
- [cds-compiler@2.4.4] to.edm(x): Update OData vocabularies 'Aggregation', 'Analytics', 'CodeList', 'Common', 'Measures', 'Session', 'UI'
- [cds@5.3.2] Aligned Node.js and Java auditlog APIs
- [cds@5.3.2] `enterprise-messaging`: No topic manipulation for outbound events beginning with a different namespace
- [cds@5.3.1] Task `@sap/cds-runtime/lib/messaging/deploy.js` moved to `@sap/cds/tasks/enterprise-messaging-deploy.js` after module merge
- [cds@5.3.1] Parse OData lambda expression on collection of scalars with equals operator (i.e., `.../any(d:d = "")`) to CQN with `contains` (pegjs-based parser only)
- [cds@5.3.0] Custom build tasks are no longer restricted to `@SAP` namespace.
- [cds@5.3.0] CDS build tasks of type `fiori` are no longer copying files located in the UI module folder into the deployment staging folder.
- [cds@5.3.0] Leaner error messages for unsuccessful remote service call
- [cds@5.3.0] Incoming messages now contain a privileged user
- [cds@5.3.0] `SELECT.where(...)` generates CQN with list of values for `in` operator
- [cds@5.3.0] Always use flag `u` during input validation via `@assert.format`
- [cds@5.3.0] Intermediate CQN format for lambda expressions with preceding navigation path
- [cds@5.3.0] Emit logs promoted to `info`
- [cds@5.3.0] Simpler topic names for `local`, `file-based-messaging` and `message-queuing`
- [cds@5.3.0] `messaging.emit(...)` also uses outbox
- [cds@5.3.0] Messaging will start listening to events once the `listening` event was fired on the `cds` object
- [cds@5.3.0] Cascade delete order reversed from leaves to root
- [cds@5.3.0] Intermediate cqn format for lambda expressions in odata
- [cds@5.3.0] OData function names and structure are kept unchanged after parsing a URL to CQN in the adapter layer, corresponding "CQN-to-SQL" logic is moved to the DB layer. The changes affect the following functions: `contains`, `startswith`, `endswith`, `toupper`, `tolower`, `indexof`, `day`, `date` and `time`.
- [cds@5.3.0] Template cache at prototype of `RootTransaction`
- [cds@5.3.0] Both strings and numbers are accepted as decimalsStrict numbers handling can be re-enabled via `cds.env.features.strict_numbers`

- [cds.java@1.17.0] Solely virtual elements are not considered readonly anymore. By default the CDS Compiler adds `@Core.Computed: true` to virtual elements, which makes them readonly by default. By adding explicitly to the virtual element, you can now create a virtual element that is not readonly.
- [cds.java@1.17.0] Interfaces for features contributing SQL DataSources have been refined and moved to public API. It is now possible to either implement a `DataSourceDescriptorFactory`, which can provide standard JDBC connection information, or for more flexibility a `DataSourceFactory`, which can directly create `DataSource` instances.
- [cds.java@1.17.0] Interface implementations loaded via Java's ServiceLoader (e.g. `ServletAdapterFactory` or `DataSourceFactory`) can now get access to the `CdsRuntime` directly after construction by implementing the `CdsRuntimeAware` interface. The `CdsRuntime` is no longer explicitly passed in methods of these interfaces.
- [cds.java@1.17.0] Centralized factories required to separate API from implementation into a `CoreFactory` interface. Application code should use existing static `create` methods on the respective interfaces (e.g. `UserInfo`, `EventContext`, etc.) instead of directly using the `CoreFactory` instance.
- [cds.java@1.17.0] Using autowired `Messages` in a Spring bean outside of a `RequestContext` now results in an error. Earlier `Messages` written like this were unnoticeably lost immediately.
- [cds.java@1.17.0] Queries that don't use a limit (top/skip) are not implicitly sorted anymore to improve performance of these queries. By default OData V2 or V4 requests always either define an explicit limit by the client or an implicit limit through server-driven paging.
- [cds.java@1.17.0] The enterprise-messaging feature can now auto-detect multitenancy-capable service bindings through the `instancetype` `reuse`. The previously used kind `enterprise-messaging-mt` has been removed.
- [cds4j@1.20.0] Improve performance of to-many expands
- [cds4j@1.20.0] Improve performance of upserts in deep updates
- [cds-mtx@2.1.2] File system APIs are now asynchronous
- [cds-mtx@2.1.2] A failed offboarding will now throw a `TenantOffboardingError`, instead of just logging the error.
- [cds-sidecar-client@1.1.21] Replace vulnerable 'Got' dependency with 'Axios'.
- [cds-sidecar-client@1.1.21] To facilitate debugging, display a few start and end characters of certain secrets in DEBUG output (applies to params that are not user-generated, i.e. short-lived and/or comprising many characters).
- [cds-sidecar-client@1.1.21] On SAP Business Application Studio, disable keyring storage as it is unsupported (switch to plain-text automatically)
- [cds-sidecar-client@1.1.21] Hide secret data in token-request URL from log output
- [sap/ux-cds-odata-language-server-extension@1.2.3] updated comprised OData vocabularies to include HTML5 vocabulary server

### Fixed ​

- [cds-dk@4.3.3] Removed internal links in npm-shrinkwrap.json
- [cds-dk@4.3.0] `cds import` fix for `` tag in OData V2 and `` tag in OData v4
- [cds-dk@4.3.0] `cds import` now sets the `kind` attribute in_package.jso_ to the correct `odata-v2` value for OData v2 services.
- [cds-dk@4.3.0] `cds import` now maps edm.DateTime to cds.DateTime for OData V2.
- [cds-dk@4.3.0] `cds compile --to edmx-v2/edmx-v4` now uses correct file naming when compiling a single CDS service.
- [cds-dk@4.2.1] `cds deploy` w/o any file arguments now works again and no longer fails with `No cds models found at/in ''`.
- [cds-dk@4.2.0] `cds deploy` called with multiple sources ignored all but the first one
- [cds-dk@4.2.0] `cdd add mta` now sets a buildpack for the server modules (Node.js or Java). This improves deploy performance and avoids issues with buildpack priorities, leading to potentially wrong build packs selected.
- [cds-dk@4.2.0] On drag and drop of an edmx file, `cds watch` now imports it in the proper working dir
- [cds-dk@4.2.0] `cds import` now moves the edmx file again to `srv/external` instead of copying it.
- [vscode-cds@4.2.0] validation mode ActiveEditorOnly (new default). The new mode reduces number of compilations during editing and thus improves responsiveness.
- [vscode-cds@4.2.0] new command Visualize CDS file dependencies to analyze using dependencies of CDS model files. Getting an overview of file dependencies can help to keep your project architecture clean. Requires the 3rd party extension Graphviz (dot) language support for Visual Studio Code (joaompinto), which can be installed with a single click.
- [vscode-cds@4.0.4] asynchronous scanning of workspace blocked and led to high cpu usage (mostly on Linux/macOS)
- [cds-compiler@2.4.4] Do not remove parentheses around single literals and references on the right-hand side of an `in` and `not in` operator.
- [cds-compiler@2.4.4] `cdsc`: Option `--direct-backend` can now be combined with `toCsn`'s option `--with-localized`
- [cds-compiler@2.4.4] The option `testSortCsn` was erroneously ignored in some compiler backends.
- [cds-compiler@2.4.4] for.odata: Propagate the `virtual` attribute correctly while flattening structures.
- [cds-compiler@2.4.4] If internal relational types are used directly in CDL (e.g. `cds.Association`), an error is emitted. In CSN, all artifacts of relational types need a `target` (/`targetAspect`) as well.
- [cds-compiler@2.4.4] In Association to Join translation don't produce a JOIN node for exposed (transitive) associations in combination with their exposed foreign keys. Also resolve foreign keys correctly against the target entity allowing to expose renamed foreign keys when aliased.
- [cds-compiler@2.4.4] The option `testSortCsn` (`--test-sort-csn` in `cdsc`) can be used to sort CSN definitions alphabetically. This option is only intended for tests. This will restore the pre-v2.3.0 ordering in EDMX.
- [cds-compiler@2.4.4] to.sql: for SQL-dialect `sqlite`, render the string-format-time function (`strftime()`) `$at.from` with date-format: `'%Y-%m-%dT%H:%M:%S.000Z'`
- `$at.to` with date-format: `'%Y-%m-%dT%H:%M:%S.001Z'` (+1ms compared to `$at.from`)

- for SQL-dialect `hana` wrap `SESSION_CONTEXT('VALID-TO')` and `SESSION_CONTEXT('VALID-FROM')` in `TO_TIMESTAMP(..)` function

- [cds-compiler@2.4.4] to.hdbcds: Wrap `SESSION_CONTEXT('VALID-TO')` and `SESSION_CONTEXT('VALID-FROM')` in `TO_TIMESTAMP(..)` function

- [cds-compiler@2.4.4] Correct auto-exposure in model with unscoped projection on deep scoped entity (from managed aspect compositions: component in component, like they are common in ODM).
- [cds-compiler@2.4.4] Internal types `cds.Association` and `cds.Composition` are no longer proposed for code-completion.
- [cds-compiler@2.4.4] Fix various issues with Association to Join translation: Substitute `$self.alias` expressions and respect prefix paths in foreign key accesses.

- [cds-compiler@2.4.4] to.hdbcds: In naming mode "hdbcds", correctly resolve $self backlinks with aliased foreign keys.
- [cds-compiler@2.4.4] to.cdl: Correctly traverse subelements when rendering annotations for them.
- Quote element names (if required) in `annotate with` statements.

- [cds-compiler@2.4.4] for.odata: Fix regression with detecting collision when generating foreign keys.
- [cds-compiler@2.4.4] to.edmx: Correctly render final base types in EDMX V2 when called with transformed OData CSN for V4.
- [cds-compiler@2.4.4] Fix regression: also for associations defined in a service, try to implicitly redirect the provided model target.
- [cds-compiler@2.4.4] to.edmx(x): The reverted change "`array of` elements are now allowed for OData V2, too." introduced with v2.2.0 has caused regressions in various scenarios that used OData V4 processed CSN for OData V2 EDMX rendering. Therefore the error has been lowered to a 'odata-spec-violation-array-of' warning.
- The fix 'Render constraints only if all principal keys are used in association' introduced with v2.2.2 has caused regressions in mocking scenarios. With option `--odata-v2-partial-constr` partial constraint generation can be reactivated. A 'odata-spec-violation-constraints' warning is raised.

- [cds-compiler@1.50.8] to.hdi.migration: Don't generate `ALTER` for type change from association to composition or vice versa (if the rest stays the same), as the resulting SQL is identical.
- [cds.java@1.17.0] Fixed a bug causing incorrect deserialization of request payloads with content-type `application/json` and `text/plain` for file upload requests on media type properties in OData V4.
- [cds.java@1.17.0] Fixed a bug causing the OData V2 artificial ID field `ID__` of aggregated entities to appear in CQN statements in case it was explicitly selected in `$select`.
- [cds.java@1.17.0] Fixed a bug causing multi-segment service paths to be handled incorrectly in OData V2.
- [cds.java@1.17.0] Expanded elements in remote OData V2 queries are now explicitly listed in `$select` in addition, if `$select` is used to reduce the selection set. This is due to the OData V2 behaviour that `$select` takes precedence over `$expand`.
- [cds.java@1.17.0] Fixed a bug causing incorrect authorization configurations in case base paths of different protocol adapter overlapped.
- [cds.java@1.17.0] Fixed a bug causing HTTP requests to SaaS Registry or Message Brokers to fail with `premature close` errors.
- [cds4j@1.21.1] Fix startsWith, endsWith with caseInsensitive flag
- [cds4j@1.21.0] Resolve naming conflict in generated interfaces
- [cds4j@1.21.0] Fix setting references for forward mapped to-one associations in insert/upsert
- [cds4j@1.21.0] Fix search for aliased localized elements behind associations
- [cds4j@1.21.0] Make `CqnBoolLiteral` immutable
- [cds4j@1.21.0] Fix exception on to-many expands with parameters in where clause
- [cds4j@1.21.0] Fix code generation for types with structured elements
- [cds4j@1.21.0] Fix code generation for compositions of aspects with structured elements
- [cds4j@1.21.0] Remove unrecognized warning for doc property in simple types
- [cds4j@1.20.5] Fix 'is' comparison with where exists subqueries in infix filters
- [cds4j@1.20.5] Fix exception on to-many expands with parameters in where clause
- [cds4j@1.20.5] Add `cds.java.expand` annotation for expand hints
- [cds@5.3.3] Validation of arrayed parameters of actions and functions
- [cds@5.3.3] Skip not-to-be-audited entities in composition tree
- [cds@5.3.3] In draft, `.texts` can be used without explicit exposure
- [cds@5.3.2] Call `init()` and register custom handlers for every new `cds.ApplicationService` created in extensibility scenarios
- [cds@5.3.2] Structured keys for deep operations in OData flavor `x4`
- _[cds@5.3.2]_Wrong user in messaging requests coming from webhooks
- [cds@5.3.2] Improvements in log formatter for Kibana: Remove redundant metadata information
- Add information from `req.headers`
- Treat error-like objects like errors
- Custom fields (alpha)

- [cds@5.3.2] Minor fix for optimized search on SAP HANA
- [cds@5.3.1] Improved error message in case custom `server.js` doesn't export a function
- [cds@5.3.1] Kibana formatter: `stacktrace` as array of strings
- [cds@5.3.1] Improved error message in case custom `server.js` doesn't export a function
- [cds@5.3.1] Bootstrapping for feature toggles
- [cds@5.3.1] Deep operations for certain composition constellations
- [cds@5.3.1] Aliasing on SQL layer for OData `ne` operator
- [cds@5.3.1] Fixed scope issues in manual deployment for messaging
- [cds@5.3.1] Projections with infix filters and cardinality changes are safely ignored during `CREATE`/`UPDATE`
- [cds@5.3.1] Resolving of views if underlying projection has explicit aliases
- [cds@5.3.0] Deep operations for certain composition constellations
- [cds@5.3.0] Projecting data works also for projections where one field maps to multiple entries
- [cds@5.3.0] `SELECT` queries without user-specified columns only modify draft columns if the entity is draft-enabled.
- [cds@5.3.0] Generated `index.html` erroneously showed entries for `contained` entities from managed compositions.
- [cds@5.3.0] Use OData simple identifier format for links to entity sets in generated `index.html`.
- [cds@5.3.0] `cds build` logged duplicate compilation errors for the identical .cds file, but with different relative path names.
- [cds@5.3.0] `cds serve` no longer tries to redirect SAP Fiori URLs starting with `$` to service URLs.
- [cds@5.3.0] `cds build` now supports `HANA Table data properties files` in SaaS applications. These files have not been copied into the sidecar folder.
- [cds@5.3.0] `cds deploy --dry` generates DROP/CREATE DDL statements with an order that also H2 can handle, i.e. with dependent views dropped before basic views.
- [cds@5.3.0] `cds build` now correctly handles symbolic links for nodejs projects on Windows.
- [cds@5.3.0] `cds build` now correctly filters CDS source files when building SaaS applications.
- [cds@5.3.0] Deploy endpoint for messaging artifacts includes the needed roles
- [cds@5.3.0] Detection of mocked services and forced resolving of views
- [cds@5.3.0] `POST/PATCH/PUT` requests on `Composition of many` with association as key and custom `on` conditions
- [cds@5.3.0] `$expand` on entities with `.` in name
- [cds@5.3.0] Filter on external service when using `ne null`
- [cds@5.3.0] Primitive property access of Singletons defined without keys via URL like `/Singleton/name`
- [cds@5.3.0] Expand and navigation in draft-enabled entity with composition of aspects
- [cds@5.3.0] `@Core.ContentDisposition.Filename` instead of `@Core.ContentDisposition`
- [cds@5.3.0] Select query with `$count` with combination with `$search`
- [cds@5.3.0] Parsing of `Timestamp`, `DateTime` and `Date` values in OData request when using beta URL to CQN parser (`cds.env.features.odata_new_parser`)
- [cds@5.3.0] Reset temporal session contexts
- [cds@5.3.0] Caching of runtime aspects
- [cds@5.3.0] Handling of foreign keys as well as an input validation when using nested associations as keys
- [cds@5.3.0] Transaction handling in case of multiple changesets
- [cds@5.3.0] SAP HANA procedure call with output parameter
- [cds@5.3.0] Skip foreign key propagation if target is annotated with `@cds.persistence.skip`
- [cds@5.3.0] Values misidentified as operators in `$search`
- [cds@5.3.0] Ensure UTC values are written to database
- [cds@5.3.0] ETag handling in case of action with `$select`
- [cds@5.3.0] Fix draft-related issues in `odata2cqn`
- [cds@5.3.0] Where clause in `@restrict` gets duplicated if `$search` query option is used
- [cds@5.3.0] Virtual fields are not filtered out before application service handlers
- [cds@5.3.0] Clarification: the minimum required Node.js version is 12.18. Versions < 12.18 might not work.
- [cds@5.3.0] `cds build` supports validation of `extension-allowlist`, which is replacing `entity-whitelist` or `service-whitelist` with cds-mtx 2.0. Warnings are no longer returned if neither entity-whitelist nor service-whitelist is defined.
- [cds@5.3.0] `cds compile -2 sql/edmx` erroneously wrote excessive compiler output to stderr
- [cds@5.3.0] Resolve the correct `enterprise-messaging-shared` credentials from `VCAP_SERVICES` by default
- [cds@5.3.0] `cds compile --to sql` now completes the last SQL statement with a proper semicolon
- [cds@5.3.0] - Binary keys handling in $filter
- [cds@5.3.0] - `odata.metadata` accept header fragment ignored during deserializer lookup in odata-server
- [cds@5.3.0] - Don't overwrite manual error code in case of data-server error
- [cds@5.3.0] - MTX enabled check
- [cds@5.3.0] - Invoke custom error handler (`srv.on('error')`) for each error and preserve modifications in case of changesets
- [cds@5.3.0] - Evaluation of restrictions for custom requests to the same `ApplicationService`
- [cds@5.3.0] - Misinterpreted SQL keyword as argument in QL's fluid usage
- [cds@5.3.0] - odata2cqn select=* syntax
- [cds@5.3.0] Requests using lambda operators in `$filter` in combination with instance based authorization
- [cds@5.3.0] Star columns can be written as `'*'` or `{ref: ['*']}`
- [cds@5.3.0] Arrayed and structured elements in draft mode
- [cds@5.3.0] Cascade delete where child entity has more than one parent
- [cds@5.3.0] Ignore `@restrict` conditions when reading `DraftAdministrativeData` of drafts
- [cds@5.3.0] Navigation to one composition via association in `containment` mode (`cds.odata.containment = true`)
- [cds@5.3.0] Create, update and delete requests to entity projections annotated with the annotation `@cds.persistence.table` are not resolved correctly
- [cds@5.3.0] Using inline `$filter` query option in deeply nested expands on SAP HANA
- [cds@5.3.0] Runtime exception when PATCH or PUT request methods are used for non-existing IDs. For example, → `PUT /api/v1/CustomerOrder('non-existing Id')/items(id='')/product`
- [cds@5.3.0] Drafts: read active children of active or draft entities using deeply nested navigation or `$expand` query option
- [cds@5.3.0] Select media type and content disposition information from base entity
- [cds@5.3.0] Attempt to calculate time delta with unresolved target crashes server
- [cds@5.3.0] OData string functions `contains`, `startswith` and `endswith` find records with `null` attributes when used with `not` operator
- [cds@5.3.0] Deep deletion of sensitive data (annotated with `@PersonalData.IsPotentiallyPersonal` or `@PersonalData.IsPotentiallySensitive`) during update is properly considered in audit logging
- [cds@5.3.0] Pseudo-variables as default value in draft-enabled entities
- [cds@5.3.0] Escape CDL keywords when used in URL path
- [cds-mtx@2.1.2] More error types and semantic HTTP status codes have been added
- [cds-mtx@2.1.2] Setting `MTX_ROLLBACK_CORRUPTED_CONTAINER` to `true` will now also delete and recreate an HDI container if its bindings are missing
- [cds-mtx@2.1.2] MTX Bootstrap has been adapted so that application service handlers can access MTX services again
- [cds-mtx@2.1.2] Logging is now consistently using cds.log
- [cds-mtx@2.1.2] A caching problem with the metadata persistence factory is fixed
- [cds-mtx@2.0.2] A failed offboarding will now throw a `TenantOffboardingError`, instead of just logging the error.
- [cds-sidecar-client@1.1.21] Fix subdomain determination with CF-CLI v7
- [cds-sidecar-client@1.1.21] Fix sending username and password for basic auth
- [cds-sidecar-client@1.1.21] Fix various requests
- [cds-sidecar-client@1.1.21] Interpret various HTTP responses properly.
- [cds-sidecar-client@1.1.21] Token is now correctly obtained.
- [cds-sidecar-client@1.1.21] Include compiled sources in published cds-sidecar-client package.
- [cds-sidecar-client@1.1.21] Compatibility with CF-CLI v7: automatic determination of running apps and relevant CF space for `login`
- [cds-sidecar-client@1.1.21] Error on login with username and password (basic auth)
- [cds-sidecar-client@1.1.21] Error due to npm binary not being found on Windows
- [sap/ux-cds-odata-language-server-extension@1.2.5] Unjustified warning for the `assert.integrity` term when applied to the service.
- [cds-odata-v2-adapter-proxy@1.7.8] Support for verb tunneling, i.e., POST with `X-HTTP-Method` header
- [cds-odata-v2-adapter-proxy@1.7.7] Support inline return type for actions and functions
- [cds-odata-v2-adapter-proxy@1.7.7] Default undefined message target to `/#TRANSIENT#`
- [cds-odata-v2-adapter-proxy@1.7.7] Return `404` for unknown service name during model compilation
- [cds-odata-v2-adapter-proxy@1.7.7] Enhance logging to contain service name for service lookup from request
- [cds-odata-v2-adapter-proxy@1.7.6] Prevent exception on handling entities without keys

### Removed ​

- [cds-compiler@2.4.4] to.hdbcds: Association publishing in subqueries is not supported by SAP HANA CDS - an error is raised during compile time, instead of waiting for a deployment error.

## May 2021 ​

### Added ​

- [cds-dk@4.1.0] `cds watch --open` opens the app in the browser with a given URL (part)
- [cds-compiler@2.2.0] The compiler now takes the "definition scope" of associations and compositions into account when implicitly redirecting the target and auto-exposing entities.
- [cds-compiler@2.2.0] OData: The warning `enum-value-ref` is no longer reclassified to an error. However, references to other enum values are still not supported.
- [cds@5.1.5] `cds build` adds `engines.node` version to package.json if not present, in order to match the minimum required node version of CDS.
- [cds@5.1.5] Generate an invocation context identifier (`cds.context.id`) if none can be derived
- [cds@5.1.0] Custom error handler via `srv.on('error', function (err, req) { ... })` BetaSynchronous modification of passed error only

- [cds@5.1.0] `cds.log.format()` for custom log formatting
- [cds.java@1.16.0] The OData V4 adapter now supports reading stream properties.
- [cds.java@1.16.0] Uploading streamed content to `@Core.MediaType` annotated properties is now supported in OData V4.
- [cds.java@1.16.0] The OData V2 adapter now provides all query parameters in the `ParameterInfo` interface.
- [cds.java@1.16.0] CSV files with locale ending are now supported for text tables of localized entities (for example, `Books.texts_de.csv`) when initializing in-memory databases.
- [cds.java@1.16.0] H2 databases are now automatically detected as embedded databases, ensuring that CSV files are automatically initialized.
- [cds.java@1.16.0] The datasource auto-configuration based on service bindings can now be disabled explicitly by using `cds.dataSource.autoConfig.enabled: false`.
- [cds.java@1.16.0] Added new property section `cds.sql` to configure the CQN to SQL transformation provided by CDS4j.
- [cds.java@1.16.0] Added a new `ExtensibilityService`, which allows to register on an event triggered when the CDS model is changed. The metadata caches listen to this event and proactively refresh their cache entry.
- [cds.java@1.16.0] Improved the error handling behaviour of the `Deploy` main class in case the deployment fails for a single tenant. The command now returns an error in that case.
- [cds4j@1.20.0] - Deprecate CQL.literal() and add CQL.constant() and CQL.val() for constant and non-constant values
- [cds4j@1.20.0] Allow using the SQL functions current_date, current_time and current_timestamp
- [cds4j@1.20.0] Allow to specify max age in meta data access to bypass cache
- [cds4j@1.20.0] Reflection API: Support type references
- [cds4j@1.20.0] Add `CqnAnalyzer.isCountQuery(cqn)` to check if a CQN statement is a count query
- [cds-runtime@3.1.1] Downport of "Support for reading single draft-enabled entities via service API (`srv.read(, { ..., IsActiveEntity: true/false })`)"
- [cds-runtime@3.1.1] Computed values are preserved during draft activate with `cds.env.features.preserve_computed = true`Preserving computed values will be the default behavior in @sap/cds^5.4

- [cds-runtime@3.1.0] Support for declared events with annotations `@topic`, `@source`, and `@type`
- [cds-runtime@3.1.0] Support for declared events in composite messaging
- [cds-runtime@3.1.0] Extended managed data (`@cds.on.insert`, `@cds.on.update`): Pseudo variable `$uuid`
- Pseudo variable `$user.`
- Static values, for example `@cds.on.insert: 'foo'`

- [cds-runtime@3.1.0] READ support for associations with custom on condition with form `. = $self and . = ''`
- [cds-runtime@3.1.0] Support for default values in views with more than one parameter
- [cds-runtime@3.1.0] Support of input validation for arrayed elements
- [cds-runtime@3.1.0] QL fluent API `orderBy()` convenience options `orderBy(' ')`, `orderBy('...', ...)`, `orderBy('..., ...')`, and `orderBy([...])`
- [cds-runtime@3.1.0] Use new, beta URL to CQN parser during read requests when serving to OData via `cds.env.features.odata_new_parser`
- [cds-runtime@3.1.0] beta version of new CQN to URL parser Use during service consumption via `cds.env.features.remote_new_parser`

- [cds-runtime@3.1.0] Draft-specific columns are considered in `$select` if OData validation is skipped
- [cds-runtime@3.1.0] Support for `cardinality` in `ref`
- [cds-runtime@3.1.0] Support for nested expressions in where conditions
- [cds-runtime@3.1.0] Invoke custom error handler Beta in OData and REST adapters if necessary
- [cds-runtime@3.0.9] Downport of "Private `._dependents` made non-enumerable to avoid circular references"
- [cds-runtime@3.0.7] CSRF-token handling in service consumption via `@sap-cloud-sdk/core` with `cds.env.features.fetch_csrf = true` files.
- [cds-mtx@2.0.1] Internal on- and offboarding API for sidecar use case: POST `/mtx/v1/internal/provisioning/subscribe` and POST `/mtx/v1/internal/provisioning/unsubscribe` with payload Beta

json

```
{
  "subscribedTenantId": ,
  "async":
}
```

- [cds-mtx@2.0.1] It's now possible to provide SAP BTP dependencies in the `mtx` settings in your .cdsrc.json instead of implementing a custom handler, by setting `mtx.dependencies` accordingly.
- [cds-mtx@2.0.0] SaaS provisioning operations GET, PUT, and DELETE on API `/mtx/v1/provisioning/tenant/` now require scope `mtcallback`. Upgrade calls on API `/mtx/v1/model/upgrade/` and `/mtx/v1/model/upgradeAsync/` now require scope `mtdeployment`. This is now aligned with the mandatory scope check required for the java runtime. To adapt the scope names to the java runtime scope configuration, the scope names can be changed using the following cds configuration:

json

```
mtx: {
    security: {
        "subscription-scope": "myApp.subscription",
        "deployment-scope": "myApp.deployment"
    }
}
```

- [cds-mtx@2.0.0] Support cds build API throwing BuildError instead of CompilationError.
- [cds-mtx@2.0.0] Undeployment of extensions can now be done using a simplified API: `/mtx/v1/model/deactivate` with payload containing the extension sources to be removed.

json

```
{
  "extension_files": [
    "db/ext3.cds"
  ],
  "tenant": ""
}
```

- [cds-mtx@2.0.0] Support automatic roll-back for corrupted tenants when `MTX_ROLLBACK_CORRUPTED_CONTAINER` is set to `true`. This should never be used in production, but only for integration tests.
- [cds-mtx@1.2.1] - Size of job queue can now be configured via `cds env`:

json

```
mtx: {
  jobqueue: {
    size: 10
  }
```

or parameter `CDS_MTX_JOBQUEUE_SIZE=10`

### Changed ​

- [cds-dk@4.1.0] If `cds watch` encounters a port that is already in use, it now just runs on an arbitrary port instead of a trying to search the next port available.
- [cds-dk@4.1.0] `cds init` uses latest `Maven Java archetype` version `1.15.3` for creating Java projects.
- [cds-dk@4.0.7] Bumped versions of `@sap/cds`, `@sap/cds-compiler`
- [cds-dk@4.0.6] Bumped versions of `@sap/cds`, `@sap/cds-runtime`, `@sap/cds-compiler`
- [cds-dk@4.0.5] Bumped version of `@sap/eslint-plugin-cds`
- [cds-dk@4.0.4] `cds init` uses latest `Maven Java archetype` version `1.15.0` for creating Java projects.
- [vscode-cds@4.0.2] uses `@sap/cds-lsp@5.0.2`
- [vscode-cds@4.0.2] uses `@sap/cds-compiler@2.2.2`
- [vscode-cds@4.0.1] now requires Visual Studio Code `>=1.54`
- [vscode-cds@4.0.1] entry `Preview as hdbtable` replaces `Preview as hana` in `CDS Preview` menu
- [vscode-cds@4.0.1] uses `@sap/cds-lsp@5.0.1`, which includes fixes for namespace handling
- [cds-compiler@2.2.4] Remove special handling for implicit redirection to auto-exposed entity; consistently do not overwrite user-specified target in a service anymore, also in this special case.
- [cds-compiler@2.2.4] Structured/Arrayed types for enums are now an error and not just a warning.
- [cds-compiler@2.2.4] to.cdl: Keywords in annotation paths are no longer escaped
- [cds@5.1.5] Better support for UI tools to get metadata for projects with both a Node.js and Java server
- [cds@5.1.0] Clean up obsolete compiler option `snapi`.
- [cds@5.1.0] `cds build` is no longer validating Node.js custom service handlers that have been registered using service `@impl` annotation.
- [cds@5.0.5] Internal errors are no longer decorated with `Please report this`. People interpreted the text as to only include the stack trace in error reports and to omit other valuable context information.
- [cds.java@1.16.0] OData V4 PUT requests on properties of non-existing entities now properly return a `404` response, instead of upserting the entity.
- [cds.java@1.16.0] Messages written during ETag validations on OData actions are now discarded.
- [cds.java@1.16.0] All requests or changesets are now executed in an OData V2 $batch request, even if one of the requests or changesets fails. This is in accordance with the OData V2 specification and the expectation of SAPUI5.
- [cds.java@1.16.0] The CloudFoundry platform feature is now enabled in case either `VCAP_SERVICES` or `VCAP_APPLICATION` is present. Earlier both environment variables had to be present.
- [cds.java@1.16.0] The statically available `LocalizedMessageProvider` has been moved into the `CdsRuntime`. In Spring Boot this allows to configure custom `LocalizedMessageProvider` implementations as Spring beans.
- [cds4j@1.20.0] Improve performance of to-many expands
- [cds4j@1.20.0] Improve performance of upserts in deep updates
- [cds4j@1.19.2] Improve performance of upserts in deep updates
- [cds-runtime@3.1.0] Model-based processing instruction cache attached to service for SaaS extensibility
- [cds-runtime@3.1.0] Removed compatibility feature flag `cds.env.features.skip_expand_assoc`
- [cds-runtime@3.1.0] Input-related details of assertion error added to error message, for example `Value 4 is not in specified range [1,3]`
- [cds-runtime@3.1.0] `$search` query option is parsed into `.search` instead of like expressions in `.where`
- [cds-runtime@3.1.0] Integrity checks are skipped if `@sap/cds-compiler`'s foreign key generation (beta!) is active
- [cds-runtime@3.1.0] Private `._dependents` made non-enumerable to avoid circular references
- [cds-runtime@3.1.0] `null` values for virtual properties added during post processing (previously done during serialization in odata-server)
- [cds-runtime@3.0.9] Downport of "Private `._dependents` made non-enumerable to avoid circular references"
- [cds-mtx@2.0.0] The global data meta tenant (`GLOBAL_DATA_META_TENANT`) is now created on the first application startup, instead of the first onboarding
- [cds-mtx@2.0.0] `@sap/hdi-deploy` and `@sap/instance-manager` are now directly required by `@sap/cds-mtx`. Therefore, they can be left out of your `_`dependencies`
- [cds-mtx@2.0.0] Job IDs are now generated using the `uuid` package
- [cds-mtx@2.0.0] The default behavior of the `extension-allowlist` has changed. If `extension-allowlist` is not configured, it is not allowed to apply any extension. Extensions can be easily enabled for all entities and services by adding the following to the configuration.

json

```
mtx: {
  "extension-allowlist" = [
      {
          "for": ["*"]
      }
  ]
```

### Fixed ​

- [cds-dk@4.1.5] An issue with opening URLs on Windows
- [cds-dk@4.1.5] `cds` CLI no longer adds `cds.compile.to.openapi` generically into all commands. This turned out to load cds configuration from wrong folders, introducing subtle side effects. Now, only the `cds compile` command adds `cds.compile.to.openapi`. If you use `cds.compile.to.openapi` in other flows, like at runtime, use `cds compile --to openapi` instead.
- [cds-dk@4.1.5] Include `@sap/cds` 5.1.5
- [cds-dk@4.1.5] Include `@sap/cds-runtime` 3.1.1
- [cds-dk@4.1.5] Include `@sap/cds-compiler` 2.2.8
- [cds-dk@4.1.5] Include `@sap/eslint-plugin-cds` 1.1.4
- [cds-dk@4.1.4] Include `@sap/cds` 5.1.4
- [cds-dk@4.1.4] Include `@sap/cds-compiler` 2.2.6
- [cds-dk@4.1.4] Include `@sap/eslint-plugin-cds` 1.1.3
- [cds-dk@4.1.3] Include `@sap/cds` 5.1.3
- [cds-dk@4.1.2] Include `@sap/cds` 5.1.2
- [cds-dk@4.1.1] Include `@sap/cds` 5.1.1
- [cds-dk@4.1.0] `cds compile --to hdbtable, hdbcds` no longer creates duplicate file extensions.
- [cds-dk@4.0.7] Lookup for `eslint` during `cds add lint`
- [cds-compiler@2.2.8] Fix regression: also for associations defined in a service, try to implicitly redirect the provided model target.
- [cds-compiler@2.2.6] to.edmx(x): The reverted change "`array of` elements are now allowed for OData V2, too." introduced with v2.2.0 has caused regressions in various scenarios that used OData V4 processed CSN for OData V2 EDMX rendering. Therefore, the error has been lowered to a 'odata-spec-violation-array-of' warning.
- The fix 'Render constraints only if all principal keys are used in association' introduced with v2.2.2 has caused regressions in mocking scenarios. With option `--odata-v2-partial-constr` partial constraint generation can be reactivated. A 'odata-spec-violation-constraints' warning is raised.

- [cds-compiler@2.2.6] Usually reserved names like `in` in references used as annotation values can now really be provided without delimited identifiers (if the name is not `true`, `false`, or `null`).
- [cds-compiler@2.2.6] Fixed the implicit redirection of associations to scoped targets (like texts entities).
- [cds-compiler@2.2.6] Fix regression: Allow virtual structured elements.
- [cds-compiler@2.2.6] to.edm(x): OData V2: Remove warning about scalar return types.
- Render constraints only if all principal keys are used in association.

- OData V4: Don't remove `@Capabilities` annotations from containee.
- Allow `@Core.MediaType` on all types and raise a warning for those (scalar) types that can't be mapped to `Edm.String` or `Edm.Binary`.

- [cds-compiler@2.2.4] to.cdl: Also handle subelement-annotations by rendering a `annotate X with Y`.
- [cds-compiler@2.2.4] to.hdi/sql/hdbcds: Fixed the database name (with naming mode `quoted`/`hdbcds`) and the `to.hdi` file name of scoped definitions (like `texts` entities) in services.
- [cds-compiler@2.2.4] Empty enums no longer result in a syntax error.
- [cds-compiler@2.2.4] Do not omit indirectly annotated or redirected sub elements during propagation of expanded sub elements.
- [cds-compiler@2.2.4] Also auto-expose composition targets of projected compositions, not just those targets, which were used at the original definition of the composition.
- [cds-compiler@2.2.4] Improve checks for keys, which are `array of` or of SAP HANA spatial type (`ST_POINT` & `ST_GEOMETRY`) with checking also inside of used user-defined structured type.
- [cds-compiler@2.2.4] to.edm(x): V2: `OnDelete=Cascade` was set on dependent instead on principal role.
- V4: ReferentialConstraints Property and ReferencedProperty for managed composition to one were swapped.

- [cds-compiler@2.1.6] Do not unjustified complain about `$self` comparisons.
- [cds-compiler@2.1.6] Auto-exposed entities are represented as projections in the CSN.
- [cds-compiler@2.1.6] to.sql/to.hdi: Revert change "Default values are no longer propagated from the principal to the generated foreign key element." from version 2.1.0
- Fix regression where localized convenience views for temporal entities used keys in the from clause that did not exist on the texts-entity
- Mixin associations are properly removed and are not rendered into views anymore

- [cds-compiler@2.1.6] to.hdi(.migration): Ensure filenames for `.hdbindex` files stay compatible to V1
- [cds-compiler@2.1.6] for.odata: An association as a type of action's parameter or return type now signals an error
- [cds-compiler@2.1.6] to.edm(x): `@Capabilities` annotations remain on the containees entity type
- In containment mode, don't render foreign keys of the containment constituting 'up' association in the containee as primary key refs.
- Revert change "Default values are no longer propagated from the principal to the generated foreign key element." from version 2.1.0
- Allow `--odata-proxies` and/or `--odata-x-service-refs` in combination with `--odata-format=flat` and `--version=v4`

- [cds-compiler@1.50.6] to.edm(x): OData V2: Render constraints only if all principal keys are used in association.
- OData V4: Don't remove `@Capabilities` annotations from containee.
- Allow `@Core.MediaType` on all types and raise a warning for those (scalar) types that can't be mapped to `Edm.String` or `Edm.Binary`.

- [cds@5.1.5] Match locales in all upper-case (for example `ZH-CN` instead of `zh-CN`)
- [cds@5.1.5] Key elements got lost in `cds.linked` when using type refs referring to other key elements
- [cds@5.1.5] Tree shaking erroneously removed types `Foo` when only referred to by type refs like `bar : Foo:bar`
- [cds@5.1.5] Fixed an error in transaction handling, that lead to database connections not released in rare cases
- [cds@5.1.5] SQL names option gets properly propagated
- [cds@5.1.5] No longer erroneously exclude entities explicitly marked with `cds.persistence:{table, skip:false}`, as in cap/samples/suppliers
- [cds@5.1.4] - Error when using complex type references, as in:

cds

```
entity Foo { bar: Tic:tac.toe; }
entity Tic { tac: Composition of { toe:String } }
```

- [cds@5.1.3] `cds` does not check for the min. required Node.js on SAP Business Application Studio, for now
- [cds@5.1.2] `cds compile --for odata` now honors the OData version again
- [cds@5.1.2] `cds compile --for odata` now honors the SQL naming mode (`sql.names`) again
- [cds@5.1.2] `cds serve` does not run in an infinite bootstrap loop if `cds.server()` is called in `server.js`
- [cds@5.1.1] `cds build` is now always adding `.hdbview, .hdbtable, .hdbconstraint or .hdbindex` plugin mappings to `.hdiconfig` to avoid that deployment is failing in case such files exist in an already deployed container, but are no longer generated.
- [cds@5.1.1] `cds compile --dest ` no longer crashes creating the destination folder
- [cds@5.1.0] `cds build` now correctly handles `message.properties` files used for Nodejs runtime messages if these files have been defined in an i18n content folder located at project root.
- [cds@5.1.0] Nodejs custom handlers are now correctly resolved if a dedicated destination folder has been configured for the build task.
- [cds@5.1.0] Now, the `.csv` file reader correctly closes open file descriptors to avoid memory leaks during `cds build`.
- [cds@5.0.7] Internal test stabilizations
- [cds@5.0.6] `cds build` no longer fails with `TypeError: x.startsWith is not a function` in some situations
- [cds@5.0.5] `cds build` now correctly creates the deployment layout for multitenant applications (sdc folder contents) that have dedicated folder paths configured for `db`, `srv`, and `app` modules.
- [cds@5.0.5] `cds deploy --to sqlite` now ignores a `_texts.csv` file again if there is a language-specific file like `_texts_en.csv` present
- [cds@5.0.5] `cds env` no longer fails to parse `.env` files with JSON values containing `=` characters
- [cds@4.6.6] Now, the `.csv` file reader correctly closes open file descriptors to avoid memory leaks during `cds build`.
- [cds@4.6.6] Fixed i18n handling causing `cds build` to fail with error message `bundle is not iterable`.
- [cds@4.6.6] Node.js custom handlers are now correctly resolved if a dedicated destination folder has been configured for the build task.
- [cds.java@1.16.0] Fixed a bug that caused issues when using the `PersistenceService` Spring bean during application startup, for example in a `@PostConstruct` initialization method.
- [cds.java@1.16.0] Fixed a bug that caused issues when using associations as keys in draft-enabled entities.
- [cds.java@1.16.0] Fixed a bug causing incorrect values for the `OData-Version` header in a parent `$batch` response.
- [cds.java@1.16.0] Fixed a bug causing incorporation of an empty JWT into the authorization header of a rest call to `mtx-sidecar`
- [cds.java@1.16.0] Fixed a bug concerning missing fields in the payload of subscribe and unsubscribe endpoints
- [cds.java@1.15.4] Adopted fixes of cds4j 1.9.3
- [cds.java@1.15.3] Fixed a bug that caused a `CdsDataStoreException` when trying to create a draft via a path `A()/B()/C` where entity `A` has an association `B` to a draft-enabled entity, which in turn has a composition `C`.
- [cds.java@1.15.3] Fixed a bug that caused a `CQNValidationException` when defining associations as keys in draft-enabled entities
- [cds.java@1.15.3] Fixed a bug causing a `SQLException` due to invalid SQL generated for aggregating OData v2 requests when properties were neither values nor dimensions.
- [cds.java@1.15.3] Adopted fixes of cds4j 1.9.2
- [cds.java@1.15.2] Fixed a bug that caused `$metadata` requests with `Accept-Language` header or `sap-language` query parameter to fail, in case the `mtx-sidecar` was used.
- [cds.java@1.15.1] Fixed a bug that caused modifying statements to fail on draft-enabled entities on the Persistence Service, in case the data included values for draft elements such as `IsActiveEntity`, `HasActiveEntity`, or `HasDraftEntity`.
- [cds.java@1.15.1] Fixed a bug that caused literal `0` or `1` in OData V2 filter expressions to be handled as String instead of Integer.
- [cds.java@1.15.1] Fixed a bug that caused invalid SQL statements for OData V2 queries, when the result was ordered by an aggregated measure.
- [cds4j@1.20.0] Fix upserts with uppercase UUID keys
- [cds4j@1.19.2] Support update via association with custom mapping
- [cds4j@1.19.2] Remove json-path (CVE-2021-27568)
- [cds4j@1.19.2] Use LIKE instead of CONTAINS when searching over views with calculated fields
- [cds4j@1.19.1] Fix exception during interface generation for inner definitions without namespace
- [cds-runtime@3.1.2] Downport of "Escape CDL keywords when used in URL path"
- [cds-runtime@3.1.1] Downport of "Attempt to calculate time delta with unresolved target crashes server"
- [cds-runtime@3.1.0] Ambiguous columns in having clause
- [cds-runtime@3.1.0] The generic read handler for drafts now correctly returns an object if the key of the entity is provided, before it was an array
- [cds-runtime@3.1.0] Improved handling of unique constraint violation error during create and update
- [cds-runtime@3.1.0] Better error logs for integrity checks
- [cds-runtime@3.1.0] Leading and trailing whitespaces are allowed in OData expressions
- [cds-runtime@3.1.0] Release database client if begin fails
- [cds-runtime@3.1.0] `auto-expand` of generated foreign keys in OData x4 flavor (`cds.env.odata.flavor = x4`) when actions return entities
- [cds-runtime@3.1.0] Consider `not null` annotations on inline structured types in OData x4 flavor (`cds.env.odata.flavor = x4`)
- [cds-runtime@3.1.0] Temporal data in OData batch requests
- [cds-runtime@3.1.0] Deep update/delete with static on conditions by composition to many
- [cds-runtime@3.1.0] Draft: Alias of entity projection is incorrectly considered as key.
- [cds-runtime@3.1.0] Support of arbitrary requests in service consumption if no external service model is provided
- [cds-runtime@3.1.0] Use unfolded model if transaction was initiated in messaging
- [cds-runtime@3.1.0] Infinite loop in restriction processing when user attribute is `null`
- [cds-runtime@3.0.9] Downport of "Use unfolded model if transaction was initiated in messaging"
- [cds-runtime@3.0.8] Timeout issues in `enterprise-messaging-shared` in reconnect
- [cds-runtime@3.0.8] Queries with a simultaneous use of `$expand` and `$orderby`, when the latter is using functions
- [cds-runtime@3.0.8] Preserve non-error messages to client during failing draft activation
- [cds-runtime@3.0.7] Timeout issues in `enterprise-messaging-shared`
- [cds-runtime@3.0.6] Allow to return primitive properties instead of entities in REST adapter
- [cds-runtime@3.0.6] Normalize time data on SQLite to support data type `TIMESTAMP_TEXT` files.
- [cds-mtx@2.0.0] No more duplicate log entries in model upgrade result.
- [cds-mtx@2.0.0] Scope check for extension undeployment (ExtendCDSDelete) is enabled again
- [cds-mtx@1.2.1] - Undeployment for model upgrade via `advancedOptions` working again files.
- [cds-mtx@1.2.1] - Undeployment of base model artifacts via undeploy.json is working again files.
- [cds-mtx@1.2.1] - Unallowed `@cds.persistence.journal` annotations in extensions are now checked
- [cds-sidecar-client@1.1.16] Bug where `keytar` module path was not correctly determined
- [cds-sidecar-client@1.1.15] Compatibility with CF-CLI v7
- [cds-odata-v2-adapter-proxy@1.6.2] Merge headers and body of POST and PUT media entity upload calls
- [cds-odata-v2-adapter-proxy@1.6.2] Handle error case in PUT media entity upload call
- [cds-odata-v2-adapter-proxy@1.6.1] Handle authorization header correctly in media upload

### Removed ​

- [cds-compiler@2.2.4] Consistently reject references to auto-exposed entities except for `annotate` (it might have worked before, depending on the sequence of definitions); expose an entity manually if you want to refer to it.
- [cds-compiler@2.2.4] to.edm(x): Revert change "`array of` elements are now allowed for OData V2, too" made in `cds-compiler@2.1.0`. Array of elements are not allowed for OData V2. Supporting this was an error, because this is forbidden by the OData V2 specification.

## March 2021 ​

### Added ​

- [cds-dk@4.0.0] `cds watch` is now a live reload server, allowing for automatic page refreshes in browsers whenever a file has changed.
- [vscode-cds@4.0.0] semantic highlighting - to be enabled via user setting `cds.semanticHighlighting.enabled`
- [vscode-cds@4.0.0] new API for annotation handler to support semantic highlighting
- [vscode-cds@3.4.0] preliminary support for cds-compiler 2.x
- [cds-compiler@2.1.0] Inferred sub elements of a referred structure type can be individually annotated.
- [cds-compiler@2.1.0] All primitive types except for binary are now allowed as enum value types.
- [cds-compiler@2.1.0] Allow users to define `A.B` even if there is a definition `A`, which is not a context or service.
- [cds-compiler@2.1.0] You can now provide almost all annotation assignments without delimited identifiers: the use of `.`, `@`, and `#` is fine for annotation names, property names of structures, and in references used as annotation values.
- [cds-compiler@2.1.0] for.odata: All the artifacts that have localized fields get a `$localized: true` property.
- Allow the user to define draft actions for annotation purposes `draftPrepare(SideEffectsQualifier: String) returns `,
- `draftActivate() returns `,
- `draftEdit(PreserveChanges: Boolean) returns `

- [cds-compiler@2.1.0] to.edm(x): Warn about nonapplicable annotations.
- Render property default values (only OData V4).
- Option `odataProxies` exposes association targets outside of the current service. These `EntityType`s do only expose their primary keys have no accompanying `EntitySet`. The added navigation targets are exposed under their namespace or if not available under namespace `root`. `odataProxies` is only available with `--format=structured`.
- Option `odataXServiceRefs` renders an `edm:Reference` to the service for those navigation targets that are defined in another service. `odataXServiceRefs` is only available with `--format=structured`.
- Duplicate EntityContainer entries with same name will raise an error.
- `array of` elements are now allowed for OData V2, too. Addendum this change is reverted in `cds-compiler@2.2.4`, as it violates the OData v2 specification.

- [cds-compiler@2.1.0] to.sql/hdi/hdbcds: Explicitly render the implicit alias for functions without arguments, e.g. `current_date`.
- [cds-compiler@2.1.0] to.sql: Sort the SQL statements according to the deployment order.
- New sql dialect `plain`, which now is the default. synchronously.

- [cds-compiler@2.1.0] API: `compileSync()` is now compatible to `compile()`: the function can also receive a file cache and will resolve all `using`s
- New API functions `parse.cql` (prefer it to deprecated `parseToCqn`) and `parse.expr` (prefer it to deprecated `parseToExpr`)
- function `getArtifactCdsPersistenceName` now accepts a CSN as a third parameter (used to be a namespace). With a CSN provided, the name can be correctly constructed for naming modes `quoted` and `hdbcds`. Without a CSN, the name is possibly wrong if it contains dots. If the CSN is not provided or the third parameter is not a CSN, the old, deprecated, implementation is used.

- [cds-compiler@2.1.0] `cdsc` and other client tools: Added `--with-localized` to the command `toCsn`, which adds convenience views for localized entities to the output.
- A script `bin/cds_update_identifiers.js` was added. You can use it to update the delimited identifier style in your CDS sources.
- A script `bin/cdscv2m.js` was added. It's command `ria` adds `@cds.redirection.target: false` annotate statements for all ambiguous redirection errors.

- [cds-compiler@2.1.0] Added `deprecated` options; setting any of them disables all `beta` options.
- [cds@5.0.2] Ensure correlation ID and set intermediate `cds.context` in default `server.js`
- [cds@5.0.1] `cds.load.properties` and `cds.parse.properties` to load and parse content in .properties format
- [cds@5.0.1] `cds.load.csv` and `cds.parse.csv` to load and parse csv content
- [cds@5.0.1] `CDL`, `CQL`, and `CXL` as new global methods for tagged template strings generating CSN, CQN, or CXN objects
- [cds@5.0.1] Fluent API classes provided through `cds.ql` also support tagged template strings now in these methods: `SELECT`, `SELECT.from`, `SELECT.where`, `UPDATE`, `UPDATE.with`, `UPDATE.where`, `INSERT.into`, `DELETE.from`, `DELETE.where` Example:

js

```
let Authors = SELECT `ID` .from `Authors` .where `name like ${'%Brontë%'}`
let Books = SELECT `ID,title` .from `Books` .where `author_ID in ${Authors}`
```

- [cds@5.0.0] MTX APIs are now automatically served when `cds.requires.multitenancy` exists. This renders an application-level server start script for multitenancy unnecessary.
- [cds@5.0.0] Auto-connect to a live reload server started by `cds watch`.
- [cds@5.0.0] `cds.parse` now offers tagged template strings. For example, const {CDL,CQL,CXL} = cds.parse; CQL`SELECT from Books where stock > 111`.
- [cds@5.0.0] `cds.log` now supports config options for Loggers and log levels via `cds.env.log`.
- [cds@5.0.0] `cds.entity.draft` as a stable way to read from draft data
- [cds@5.0.0] `cds.linked` now correctly links, events, action params and results, which were not linked before
- [cds@5.0.0] `cds.env.features.skip_unused = 'all'` removes all definitions from CSN, which are not reachable by defined services. Especially, when using comprehensive reuse models, like One Domain Model, this significantly reduces both, memory consumption as well as excess tables and views in databases.
- [cds.java@1.15.0] The method `throwIfError()` has been added to the `Messages` interface. You can use this method to throw a `ServiceException` based on the error messages collected in the `Messages` container. With this API, you can avoid duplicating errors or to define a general top-level error message.
- [cds.java@1.15.0] OData V2 and V4 adapters now support entity names that contain a dot in their CDS definition, for example `Books.texts`.
- [cds.java@1.15.0] Direct modifications on primitive properties using `PUT` or `DELETE` are now supported in OData V4, for example `PUT /Books(4711)/title`.
- [cds.java@1.15.0] CQN Select queries on remote OData services now support `excluding`.
- [cds.java@1.15.0] Simple projections reducing the select list (without aliases) can now be used with queries on remote OData services.
- [cds.java@1.15.0] The `TenantProviderService` is now capable of retrieving subscribed tenants from the SaaS registry, if a corresponding service binding is available. If not, it still falls back to retrieving subscribed tenants from the service manager.
- [cds.java@1.15.0] Added sending of event messages to multitenant-aware SAP Event Mesh services.
- [cds4j@1.19.0] Reflection API: Support aspects with compositions of aspects
- Support dots in events, aspects, structured types, actions, and functions

- [cds4j@1.19.0] Generator: Support dots in entity names, events, structured types, aspects, actions, and functions
- Support composition of aspects

- [cds-runtime@3.0.3] Support for `application/*+json` when parsing events through webhooks
- [cds-runtime@3.0.2] Support for `{xpr:...}` as argument of a function in SQL Builder
- [cds-runtime@3.0.2] Aliased parameters of a function call using an OData inline parameter syntax are provided as a request payload in `req.data`.
- [cds-runtime@3.0.2] Skip conversion to UTC on SAP HANA during insert via `.rows()`, `.values()`, or `.as()` with `cds.env.features.preserve_timestamps = true`.
- [cds-runtime@3.0.2] beta version of new URL to CQN parser Use during read requests when serving to REST via `cds.env.features.rest_new_parser`
- Known limitations: Falsy key path segments in navigations, for example, `GET /Books/0/author`
- `ne` operator in `$filter` does not match `NULL`
- Nested functions, for example, `contains(toupper(...))`
- `$select` not filtered for duplicates, for example, `$select=ID,*` -> `columns: ['ID', 'ID', ...]`

- Not supported when serving to REST: Deep navigations, for example, `GET /Books/1/author/books`
- `/$count`
- `$apply`

- [cds-runtime@3.0.1] `PUT` primitive properties via OData
- [cds-runtime@3.0.1] Optimistic concurrency control for primitive properties
- [cds-runtime@3.0.1] Data for virtual properties filtered out on write to draft tables
- [cds-runtime@3.0.1] Annotation `@odata.draft.enclosed`
- [cds-runtime@3.0.0] SAP Event Mesh: Webhook support
- [cds-runtime@3.0.0] SAP Event Mesh: Webhook support in multitenancy
- [cds-runtime@3.0.0] Messaging: Remove obsolete topics on queue creation
- [cds-runtime@3.0.0] Additional convenience look-ups of `messages.properties` files next to models
- [cds-runtime@3.0.0] Support for the `@cds.search` annotation to allow a different set of searchable elements in the `$search` OData query option and to extend the search to associated entities (currently not supported)
- [cds-runtime@3.0.0] Additional credentials look-up with label `service-manager` in SAP HANA pool
- [cds-runtime@3.0.0] Support for new "Locked by Another User" request of draft choreography
- [cds-runtime@2.9.8] Database pool teardown in case of failed db connection attempt
- [cds-runtime@2.9.6] Pass `tcpKeepAliveIdle` to `hdb` (available with `hdb^18`) via environment variable `HDB_TCP_KEEP_ALIVE_IDLE`
- [cds-runtime@2.9.6] Database pool teardown in case of credentials become invalid scenario extended by unreachable database
- [cds-mtx@2.0.0] No more duplicate log entries in model upgrade result.
- [cds-mtx@1.2.0] Multitenant applications now support extensions of entities using schema evolution based on `.hdbmigrationtable` files.
- [cds-mtx@1.2.0] It is now possible to specify limits for the number of extension fields per entity. If no limit is specified, the number of extension fields is not limited. If this list exists, only entities and services contained in this list can be extended.

json

```
"mtx" : {
  "extension-allowlist": [
    {
        'for': ['my.bookshop.Authors', 'my.bookshop.Books'],
        'new-fields': 2
    },
    {
        'for': ['CatalogService']
    }
  ]
}
```

- [cds-sidecar-client@1.1.14] Compatibility with CDS Compiler v2.
- [cds-odata-annotations@1.1.7] Go To References /Peek References / Show All References for the aggregated properties defined with the `@Analytics.AggregatedProperties` annotation. You can now navigate to the place where the aggregated property is referenced.
- [cds-odata-annotations@1.1.5] Code completion, diagnostics, and quick info for applying selected client-side OData functions: `odata.concat`
- `odata.fillUriTemplate`
- `odata.uriEncode`

- [cds-odata-annotations@1.1.5] Peek References/ Go To References for annotations referenced in other annotations. You can now see if and where the annotation is referenced. Limitation: references in propagated annotations might be not included.

### Changed ​

- [cds-dk@4.0.3] `cds compile --to xsuaa`, `edmx-v2`, and `edmx-v4` have moved from `@sap/cds` to `@sap/cds-dk`.
- [cds-dk@4.0.2] `cds init` uses latest `Maven Java archetype` version `1.14.3` for creating Java projects.
- [cds-dk@4.0.2] npm-shrinkwrap.json format version 2 is now used, produced by `npm` 7
- [cds-dk@4.0.2] npm-shrinkwrap.json now contains integrity hashes
- [cds-dk@4.0.0] `cds init` uses latest `Maven Java archetype` version `1.14.0` for creating Java projects.
- [cds-dk@4.0.0] `cds watch` has dropped its fallback support for `nodemon` through the `CDS_USE_NODEMON` configuration.
- [cds-dk@4.0.0] `cds add hana` now sets `hdbtable` as deployment format for SAP HANA
- [cds-dk@3.5.1] Bump version of `@sap/cds` to 4.6.5
- [vscode-cds@4.0.0] consume cds-compiler 2.1.4
- [vscode-cds@3.4.0] now requires Visual Studio Code `>=1.53`
- [vscode-cds@3.4.0] uses `@sap/cds-lsp@4.4.1`
- [vscode-cds@3.4.0] uses `@sap/cds-compiler@1.50.0`
- [cds-compiler@2.1.0] CSN representation: CSN Version is set to `2.0`
- CSN `definitions` are not sorted anymore
- `$syntax` is non-enumerable
- increase the use of JS numbers in the CSN for numbers in CDL, especially noticeable in annotation values
- Annotation definitions are to be found in the top-level property `vocabularies`.
- Introduce `kind: 'aspect'` to replace `kind: 'type', $syntax: 'aspect'` and `kind: 'entity', abstract: true` (the deprecated variants are still accepted as input).
- Projections are rendered via `projection` instead of `query.SELECT`.
- Parentheses are represented structurally and unnecessary parentheses are omitted.
- Use `.` instead of `_` for the name suffix of generated texts entities and the calculated entity for managed compositions.
- The CSN returned by `compile()` does not include localized convenience views anymore.

- [cds-compiler@2.1.0] Core engine (function `compile`): An assignment `@Foo.Bar` is always `@Foo.Bar`, we do not try to search anymore for a local definition of `Foo` probably having a different full name.
- Localized convenience views are no longer generated by the core compiler but added by the `for.odata` and `to.sql/hdi/hdbcds` processing on demand.
- Minimize name clashes when calculating names for autoexposed entities, extends the v1 option `dependentAutoexposed` to sub artifacts of entities (see “Added”).
- Ambiguities when redirecting associations now always lead to compile errors; you might want to use the new annotation `@cds.redirection.target` to solve them.
- The association `up_` in the calculated entity for managed compositions is now managed. Limitation: Nested managed compositions are not activatable via `to.hdbcds --names=hdbcds`.
- Bound actions and functions are no longer propagated from the main query source to the resulting view or projection.
- Remove annotation `@cds.autoexpose` from generated `.texts` entity
- Require `order by` references to start with a table alias when referring to source elements.
- Infer the type of a `select` item from the type of a top-level `cast`.

- [cds-compiler@2.1.0] Localized convenience views now also contain `masked` elements of the original artifact.
- [cds-compiler@2.1.0] for.odata: Even with `--format: structured`, (flat) foreign keys for managed associations are generated.
- An `entity` or an `aspect` defined outside the current service cannot be used as action parameter or return types.
- Structured elements are expanded in-place.
- Foreign keys for managed associations are created in-place.

- [cds-compiler@2.1.0] to.edm(x): An `Edm.TypeDefinition` is rendered for a derived scalar type and used as type reference instead of rendering the final scalar type, including the `array of`/`many` predicates.
- `enum` type definition as service member is rendered as `edm:TypeDefinition` instead of `edm:EnumType`.
- Set default source cardinality of compositions to exact one. This is observable in V2 EDM only.
- Key must not be `nullable=true`, this includes all sub elements of used structured types.
- Default values are no longer propagated from the principal to the generated foreign key element.
- `array of array` is rejected, nested Collections `Collection(Collection(...))` are illegal.
- Temporal rendering: `@cds.valid.from` is not `Edm.KeyRef` anymore.
- `@cds.valid.key` is rendered as `@Core.AlternateKeys`.

- Downgrade message "`` is not applied" from warning to info.
- Update Vocabularies 'Aggregation', 'Capabilities', 'Core', 'Validation'.

- [cds-compiler@2.1.0] to.sql/to.hdi/to.hdbcds: Reject using associations or compositions in query elements starting with `$self` or `$projection`.
- Virtual elements are not rendered.
- Structured elements are expanded in-place.
- Foreign keys for managed associations are created in-place.
- Implicit/CDL-style casts are not rendered as SQL CASTs.
- All association usages in queries are always translated into JOIN expressions (except for to.hdbcds `--names=hdbcds`).

- [cds-compiler@2.1.0] to.sql/to.hdi: Downgrade message `to-many-no-on` from error to warning.
- Default values are no longer propagated from the principal to the generated foreign key element.

- [cds-compiler@2.1.0] to.sql: Changed type mappings for `--dialect=sqlite`: `cds.Date` --› `DATE_TEXT`
- `cds.Time` --› `TIME_TEXT`
- `cds.Timestamp` --› `TIMESTAMP_TEXT`
- `cds.DateTime` --› `TIMESTAMP_TEXT`
- `cds.Binary` --› `BINARY_BLOB`
- `cds.hana.Binary` --› `BINARY_BLOB`

- Don't check missing type facets.

- [cds-compiler@2.1.0] to.hdbcds: References to derived, primitive types are replaced by their final type. The derived type definitions are not rendered anymore for hdbcds naming mode.
- Don't check missing type facets in views.

- [cds-compiler@2.1.0] to.cdl: Render maximum cardinality as 'to one' or 'to many'.
- Return at most two files. The first one (named model.cds) contains all definitions, rendered in order, without namespaces or using. Contexts and services are NOT nested. The second file (named <namespace>.cds) represents the CSN `namespace` property, simply defining such a namespace and requiring the first file.

- [cds-compiler@2.1.0] API changes: The API functions `compile()` and `compileSync()` return a CSN and not an XSN, `compactModel()` returns the first argument.
- If `options` does not provide a `messages` property, all messages are printed to standard error.
- The `options.messages` is kept throughout the compiler and contains all messages from the compiler and all backends.
- Messages are not sorted anymore; use the API function `sortMessages` to have it sorted.

- [cds@5.0.1] Minimum required Node.js version is now 12. Support for Node.js v10 is dropped.
- [cds@5.0.0] Upgraded major version of dependency `@sap/cds-compiler`
- [cds@5.0.0] `cds.requires.db.multiTenant` is deprecated. Multitenancy can now be enabled by adding a `cds.requires.multitenancy` configuration.
- [cds@5.0.0] `cds deploy --to hana` no longer adds a driver for SAP HANA to package.json. This can be done with `cds add hana`.
- [cds@5.0.0] `cds deploy --to hana` no longer adds configuration for SAP HANA to package.json. This can be done with `cds add hana`.
- [cds@5.0.0] `cds deploy --to hana` drops support for the classic CAP Java runtime, that means, longer writes credentials for SAP HANA to `connection.properties`.
- [cds@5.0.0] Fiori preview now loads and shows data initially in its list page
- [cds@5.0.0] i18n template strings now are replaced in EDMX documents such that they retain their surrounding string. For example, the `"{i18n>key1} - {i18n>key2}"` template results in `"value1 - value2"`, while previously the first match replaced the entire string, leading to `"value1"`. This is helpful for the `Template` strings of `UI.ConnectedFields`.
- [cds@5.0.0] CDS drops compiler v2 support for classic CAP Java runtime projects. `cds build` returns an error if compiler version 2 is used. For further details regarding migration to CAP Java SDK runtime, see Migration.
- [cds@5.0.0] `req.timestamp` is a Date object now; was a UNIX epoch integer before, i.e., Date.now()
- [cds.java@1.15.0] Added the new interface `CqnService`, which will gradually replace `CdsService`. The benefits of the new interface will be that it avoids name clashes with `CdsService` from the Reflection API and captures the intent of the interface better. In a future release `CdsService` might be deprecated. To avoid warnings in your code, consider renaming usages of `CdsService` to `CqnService`.
- [cds.java@1.15.0] When switching to the privileged user in a new Request Context using `privilegedUser()`, the current tenant context is automatically propagated to the privileged user.
- [cds.java@1.15.0] Unknown topic events are no longer auto-completed in Messaging Services.
- [cds.java@1.15.0] The goals `clean` and `generate` of the `cds-maven-plugin` adopting the naming convention for properties and add prefix `cds.` to all their properties.
- [cds.java@1.15.0] The `cds-services-archetype` doesn't set a Node.js version in pom.xml anymore, which means that the default version provided by the `cds-maven-plugin` is used. If required it is still possible to set the Node.js version property in a project.
- [cds-runtime@3.0.2] Minimum required Node.js version is now 12. Support for Node.js v10 is dropped.
- [cds-runtime@3.0.2] Draft handlers registered via `cds.ApplicationService.registerFioriHandlers()`, which gets called in `cds.ApplicationService.init()`
- [cds-runtime@3.0.2] OData validation is skipped by default. It can be explicitly turned on by setting `cds.odata.skipValidation` config to `false`
- [cds-runtime@3.0.1] Grants of `@restrict` in draft are derived from the CRUD vocabulary
- [cds-runtime@3.0.1] Unnecessary `@restrict` checks for actions on drafts are skipped ("in process by user" check remains)
- [cds-runtime@3.0.1] Drafts are deleted after the active version was created/ updated
- [cds-runtime@3.0.1] Skip "with parameters" clause if no order by clause or all columns in the order by clause are not strings
- [cds-runtime@3.0.0] By default, only elements typed as `string` are searchable via the `$search` OData query option to improve performance
- [cds-runtime@3.0.0] Deprecate `@Search.defaultSearchElement` annotation in favor of the `@cds.search` annotation
- [cds-runtime@3.0.0] Ignore `not null` annotation on nested structured types in OData x4 flavor (`cds.env.odata.flavor = x4`) if its parent structure is optional
- [cds-runtime@3.0.0] Smart quoting based on database-specific keywords exported by `@sap/cds-compiler`Deactivate during two-month grace period via compatible feature flag `cds.env.features.compiler_keywords = false`

- [cds-odata-annotations@1.1.7] Vocabulary description and long description for restricted `String` values are now displayed in Quick Info window of the completion lists.

### Fixed ​

- [cds-dk@4.0.3] `cds init` now works if started in file paths with spaces
- [cds-dk@4.0.2] Allow blanks in cds-dk installation path when running `cds init`.
- [cds-dk@4.0.1] Many things in linter
- [cds-dk@4.0.0] `cds watch` no longer runs in an endless restart loop if started in the user's home dir.
- [cds-compiler@2.1.4] The postinstall step now never fails with an exit code != 0. As the postinstall step is optional, it should not break any `npm install` steps.
- [cds-compiler@2.1.2] ensure `postinstall` script is part of the shipped package.json
- [cds-compiler@2.1.0] Core engine (function `compile`): Managed compositions in sub elements are now properly redirected, even if the sub structure comes from a referred type.
- Do not dump with sub queries in the `on` condition of `join`s.
- Properly report that managed aspect composition inside types and as sub elements are not supported yet.
- Make sure that including elements with managed aspect compositions only use the provided target aspect, but not the generated target entity.
- Properly handle the extra keywords in the third argument of the SAP HANA SQL function `round`.

- [cds-compiler@2.1.0] to.edm(x): Return all warnings to the user.
- Don't render references and annotations for unexposed associations.
- Rendering of `@Validation.AllowedValue` for elements of type enum annotated with `@assert.range`: Add `@Core.Description`, if the enum symbol has a `@Core.Description`, `@description` or document comments.

- Primary key aliases are now the path base names, colliding aliases are numbered.
- Fix a bug in constraint calculation if principal has no primary keys.
- Illegal OData identifiers, which are not exposed in the generated edmx schema are not causing errors anymore.
- Improve non-enum value handling on term definitions based on an enum type by raising a warning and rendering the value with appropriate scalar EDM type.
- Render annotation qualifier in JSON format.

- [cds-compiler@2.1.0] to.sql/hdi/hdbcds: Reject structured view parameters for SAP HANA.
- Types are not rendered anymore for SAP HANA in quoted mode.
- Structured elements in subqueries are now properly expanded.
- Actions, functions, annotations, and events do not have database specific checks run on them, as they will not be part of the resulting artifacts anyways
- With `--names=quoted` or `hdbcds`, some `.` in artifact names are turned into `_`. In general, this happens when part of the name prefix is "shadowed" by a non-context/service; any `.` after that point is turned into `_`. This change also affects the filenames and the `@cds.persistence.name` annotation in the CSN returned by `to.hdi.migration` and `for.odata`.

- [cds-compiler@2.1.0] to.sql/hdi: Fixed a bug, which led to an exception if elements were referenced as types.
- For the SQLite dialect, date, time, and timestamp are rendered as simple string literals instead of function calls.
- For naming mode "plain", date, time, and timestamps are rendered as SQL-compliant literals.

- [cds-compiler@2.1.0] to.sql/hdbcds: Fix issue, which led to wrong ON conditions for naming mode `hdbcds`.
- [cds-compiler@2.1.0] to.sql: SRID of SAP HANA spatial type (`ST_POINT` & `ST_GEOMETRY`) is not rendered as the length of `CHAR` for SQL-dialects other than `hana`. The resulting `CHAR` has a default length of 2,000.

- [cds-compiler@2.1.0] to.hdbcds: Nullability constraints on view parameters are not rendered anymore.
- CDS and SAP HANA CDS types inside cast expressions are mapped to their SQL-counterparts, as the CDS types can't be used in a cast.

- [cds-compiler@2.1.0] to.cdl: Correctly render `event` typed as `projection`.
- [cds-compiler@2.1.0] to.hdi.migration: Don't generate `ALTER` for type change from association to composition or vice versa (if the rest stays the same), as the resulting SQL is identical.
- [cds-compiler@1.50.4] to.hdbcds: CDS and SAP HANA CDS types inside cast expressions are mapped to their SQL-counterparts, as the CDS types can't be used in a cast.
- [cds-compiler@1.50.2] Correct calculation of dependent autoexposed entity name (fixing a potential regression with v1.50.0)
- [cds-compiler@1.50.2] to.hdi.migration: Correctly handle "temporal" and other cases when rendering expressions
- [cds-compiler@1.50.2] to.edm(x): Improve non-enum value handling on Oasis enum term definitions by raising a warning and rendering the value with appropriate scalar EDM type.
- Render annotation qualifier in JSON format.

- [cds-compiler@1.50.2] Update OData vocabularies 'Aggregation', 'Analytics', 'Capabilities', 'CodeList', 'Common', 'Communication', 'Core', 'Graph', 'HTML5', 'ODM', 'PersonalData', 'Session', 'UI'
- [cds@5.0.4] `cds build` no longer fails with a `task.apply is not a function` error when used in an npm script.
- [cds@5.0.3] `cds.compile` got thoroughly cleaned up and enhanced as the single API to compile models
- [cds@5.0.3] `cds.compile.to.cdl` was missing in 5.0.2
- [cds@5.0.3] `cds build` no longer uses reflected CSN which caused odata and EDMX transformation to fail. As a consequence language specific EDMX files were missing.
- [cds@5.0.2] `cds build` no longer aborts for CAP Java SDK based projects with compiler v2 not supported message.
- [cds@5.0.1] Fixed race conditions in `cds.serve` leading to broken services
- [cds@5.0.1] Fixed typos in API type definitions
- [cds@5.0.1] Fixed `cds.reflect.forall` for CSN extensions
- [cds@5.0.1] Fixed orphaned `_texts` proxies, causing init from CSV to fail with "no such table" errors
- [cds@5.0.0] `cds.connect.to` no longer returns `undefined` in concurrent cases where `connect` is called again while a datasource is about to be connected.
- [cds@5.0.0] `cds.log` formerly wrote log and debug output to stderr, now writes that to stdout
- [cds@5.0.0] `cds.server` now accepts port `0` as a number
- [cds@5.0.0] Race conditions in `cds.serve` and `cds.connect` lead to wrong Service instances to lost handler registrations
- [cds@4.6.5] `cds build` now correctly parses `.hdbtablemigration` files on Windows
- [cds@4.6.5] `compile --to serviceinfo` no longer crashes for Spring configuration in multi-root `yaml` files
- [cds.java@1.15.0] Fixed a bug, that could create a mismatch between the tenant in the Request Context and the tenant used by the database transaction. This bug could only occur, when explicitly changing the tenant context in the Request Context after already starting a database transaction. This situation is now detected with an exception and dedicated database transactions or ChangeSet Contexts must be opened for each tenant.
- [cds.java@1.15.0] Fixed a bug that caused issues with associations as keys in draft-enabled entities.
- [cds.java@1.15.0] Fixed a bug that caused the creation date instead of the last changed date of a draft entity to be considered during the draft garbage collection.
- [cds.java@1.15.0] Fixed a bug that caused `getDefinition()` of `ApplicationService` and `RemoteService` to return the service definition from the tenant-independent model.
- [cds.java@1.15.0] Fixed a bug that caused serialization issues in OData V4 when directly reading a `Edm.Decimal` property (for example, `/browse/Books(4711)/price`).
- [cds.java@1.15.0] Fixed a bug that caused invalid OData V4 EDMX files to be loaded due to external references defined in the EDMX.
- [cds.java@1.15.0] Fixed a bug that caused message targets to miss on the OData V2 error response.
- [cds.java@1.15.0] Fixed a bug that caused guid keys in message targets to be rendered incorrectly in OData V2.
- [cds.java@1.15.0] Fixed a bug that rejected requests (HTTP return code 403 Forbidden) to public actions and functions, which accept parameters.
- [cds.java@1.15.0] Fixed a bug that caused an incorrect authentication auto-configuration in case the base path of an adapter was configured to `/`.
- [cds.java@1.15.0] Fixed a bug, that caused no CSV data to be initialized during startup, in case an error was present in one of the CSVs. Every CSV file is now inserted in a dedicated transaction.
- [cds.java@1.15.0] Fixed a bug in `cds-maven-plugin`, where using command line argument `-Dskip=true` skips the goals `install-node`, `install-cdsdk`, `cds`, and `npm` at once. Now, each of these goals has it's own skip property: `cds.cds.skip`, `cds.install-cdsdk.skip`, `cds.install-node.skip`, and `cds.npm.skip`.
- [cds.java@1.14.1] Fixed a bug that prevented authorized users to read draft metadata or texts of a draft entity (for example, `//DraftAdministrativeData` or `//texts`). The requests were rejected with HTTP response code 403 (Forbidden) in case the entity is protected with a `@restrict`-clause that has a `where`-condition.
- [cds.java@1.13.2] Fixed a bug that prevented mock user configuration in case there was an XSUAA-binding in default-env.json but XSUAA-configuration has been turned off explicitly.
- [cds.java@1.13.2] Fixed a bug that caused the field length validation to fail on arrayed string elements (for example, `many String(10)`).
- [cds4j@1.19.0] Fix bulk upsert with empty list
- [cds4j@1.19.0] Support inline/anonymous defined type as return type for actions/functions
- [cds4j@1.19.0] Fix cascading delete fallback for path with infix filters
- [cds4j@1.18.1] Fix bulk upsert with empty list
- [cds4j@1.18.1] Fix cascading delete fallback for path with infix filters
- [cds4j@1.18.1] Render all LIMIT clauses as literal values
- [cds.java@1.13.2] Updated CDS4j to `1.17.2`
- [cds-runtime@3.0.5] Side effects on `@sap/hana-client`'s streaming extension
- [cds-runtime@3.0.4] Empty inserts for nested composition of one
- [cds-runtime@3.0.4] Preserve children if multiple compositions to same target
- [cds-runtime@3.0.3] Navigation properties in `$select` inside of `$expand` query option
- [cds-runtime@3.0.2] Accept header matching during media stream
- [cds-runtime@3.0.2] Time delta for Date type in temporals
- [cds-runtime@3.0.2] Function calls using an OData inline parameter syntax with aliased parameters of primitive types
- [cds-runtime@3.0.2] Path navigation in `$orderby` expressions when using SAP HANA functions
- [cds-runtime@3.0.1] Reading `SiblingEntity` via navigation of a draft enabled entity
- [cds-runtime@3.0.1] Inline defined return types of custom actions/functions in REST
- [cds-runtime@3.0.1] Multiple integrity errors in one changeset
- [cds-runtime@3.0.1] `@Capabilities.NavigationRestrictions` considers "deep" navigation paths
- [cds-runtime@3.0.1] Add ETags to result based on `@odata.etag` in CSN alone
- [cds-runtime@3.0.1] Reading media stream with accept header
- [cds-runtime@3.0.0] Using path navigations in `$filter` for SAP HANA-based services configured with `cds.odata.flavor = x4`
- [cds-runtime@3.0.0] Only `messaging` will deal with domain-level events
- [cds-runtime@3.0.0] Read access using nondraft enabled projections on draft children
- [cds-runtime@3.0.0] Debug message when metadata size exceeds cache limit
- [cds-runtime@3.0.0] Order by using functions in combination with group by
- [cds-runtime@3.0.0] Streaming by navigation
- [cds-runtime@3.0.0] Alignment of temporal data with compiler v2 format
- [cds-runtime@3.0.0] Calculate `DraftIsCreatedByMe` and `DraftIsProcessedByMe` properties of `DraftAdministrativeData` by reading drafts
- [cds-runtime@2.9.7] Reserved keywords for smart quoting
- [cds-runtime@2.9.7] Datetime conversion for SAP HANA in case of `INSERT...as(SELECT...)`
- [cds-runtime@2.9.5] Relative error target on draft activation for SAP Fiori Elements with OData V2
- [cds-runtime@2.9.4] Support for version 2 of the `@sap/xssec` package, as it is deprecated. Now, only version 3 of the package is supported.
- [cds-runtime@2.9.3] Check whether current request is a bound action
- [cds-runtime@2.9.2] Result payload by expand of grandchild entity, when the child data that is null
- [cds-runtime@2.9.2] Delete composition of one via navigation
- [cds-runtime@2.9.2] Use extended model in structured processing
- [cds-mtx@1.1.5] Connection handling has been improved. Errors of type `TimeoutError: Acquiring client from pool timed out` are reduced.
- [cds-mtx@1.1.5] The extension API `/mtx/v1/content` now returns a correct JSON if a collection is requested with any version of `@sap/cds` used by the application. The `cds extend` command was returning `(intermediate result)` is `not iterable` because of an incorrect server response.
- [cds-mtx@1.1.3] `mtx/v1/model/status` now returns the job status again
- [cds-odata-v2-adapter-proxy@1.6.0] Final CDS v5 compatibility version
- [cds-odata-v2-adapter-proxy@1.5.11] CDS 5 compatibility (>= 1.6.0 needed for CDS v5)
- [cds-odata-v2-adapter-proxy@1.5.11] Support `content-disposition` header in media entity upload
- [cds-odata-v2-adapter-proxy@1.5.11] Introduction of element annotation `@cov2ap.headerDecode` to decode header values
- [cds-odata-v2-adapter-proxy@1.5.10] Fix crash for bound action without return type
- [cds-odata-v2-adapter-proxy@1.5.10] Consider bound action binding parameter for messages targets

### Removed ​

- [cds-compiler@2.1.0] Core engine (function `compile`): Referential integrity issues now always lead to compile errors.
- The `type of` operator (without `:` in the reference) cannot be used for parameters and inside queries anymore.
- Using `"…"` for delimited identifiers leads to a compile error.
- Issue an error for “smart artifact references”, that means, when using `Definition.elem` instead of `Definition:elem`
- The definition of annotations is no longer allowed in `context`s and `service`s.
- Providing an alias name without `as` leads to a compile error or warning.
- Providing unexpected kind of definitions for `type` or other references lead to a compile error.
- The ancient CSN 0.1.0 format generation has been removed.
- The compiler does no longer look for modules whose file extension is .csn.json, both .csn and .json is still checked.

- [cds-compiler@2.1.0] for.odata: With `--format: structured`, the property `$generatedFieldName` in keys of managed associations has been removed.
- Artificially exposed types that are required to make a service self contained are removed from the OData processed CSN.
- Localized convenience views are no longer part of the OData CSN.

- [cds-compiler@2.1.0] API changes: The deprecated XSN based transformers `forHana`, `forOdata`, `toSwagger`, `toSql`, `toCsn`, `toCdl` have now been removed from the code base.
- Remove `collectSources()` as well as `options.collectSources`.
- A `CompilationError` usually does not have the property `model` anymore, to avoid potential memory issues.
- CSN compiler messages no longer have a `location` property. Use `$location` instead.

- [cds-compiler@2.1.0] The following `cdsc` options have been removed: `--old-transformers`.
- `--hana-flavor` with all corresponding rudimentary implemented language constructs.
- `--new-resolve` (the new resolver is now the default).

The following undocumented, internal functions have been removed. In case you spotted and used them, replace as given below.

- [cds@5.0.3] `cds.compile.cdl` → use `cds.compile` instead
- [cds@5.0.3] `cds.compile.to.parsed.csn` → use `cds.parse` instead
- [cds@5.0.3] `cds.compile.to.xtended.csn` → use `cds.compile` instead
- [cds@5.0.3] `cds.compile.to.inferred.csn` → use `cds.compile` instead
- [cds@5.0.3] `cds.compile.to.hdi` → use `cds.compile.to.hdbtable` instead
- [cds@5.0.3] `cds.compile.to.hana` → use `cds.compile.to.hdbcds` instead
- [cds@5.0.3] `cds.compile.to.xsuaa` → still available in CLI thru `cds compile -2 xsuaa`
- [cds@5.0.3] `cds.compile.to.serviceinfo` → still available in CLI thru `cds compile -2 serviceinfo`
- [cds@5.0.3] `cds.compile.to['edmx-v2']` → still available in CLI thru `cds compile -2 edmx-v2`
- [cds@5.0.3] `cds.compile.to['edmx-v4']` → still available in CLI thru `cds compile -2 edmx-v4`
- [cds@5.0.3] `cds.compile.to['edmx-w4']` → still available in CLI thru `cds compile -2 edmx-w4`
- [cds@5.0.3] `cds.compile.to['edmx-x4']` → still available in CLI thru `cds compile -2 edmx-x4`
- [cds@5.0.0] Compiler non-snapi support → see `cds.env.features.snapi` option
- [cds@5.0.0] In recent releases we added methods `cds.compile.to.hdbtabledata` and `cds.compile.to.hdbmigration`, intentionally undocumented, as they were meant to be private. Nobody should ever have used these methods, hence nobody should be affected by their removal.
- [cds-runtime@3.0.2] Blind path-level logs by odata-server
- [cds-runtime@3.0.0] Support for version 2 of the `@sap/xssec` package, as it is deprecated. Now, only version 3 of the package is supported.

## February 2021 ​

### Added ​

- [cds-compiler@1.50.0] Introduce annotation `@cds.redirection.target`. With value `false`, the projection isn't considered an implicit redirection target; with value `true`, is considered a “preferred” redirection target.
- [cds@4.6.3] [beta] `cds build` for SAP HANA now provides schema evolution support for multitenant application extensions.
- [cds@4.6.1] [beta] `cds build` for SAP HANA now supports the generation of `hdbmigrationtable` design-time artifacts for large volume tables allowing for schema evolution capabilities. Model entities annotated with `@cds.persistence.journal` will be deployed as `hdbmigrationtable` artifacts instead of `hdbtable`.
- [cds.java@1.14.0] Enhanced the index page to list both OData V4 and OData V2 endpoints, in case one or both adapters are present. As part of this change the properties to configure the index page were moved from `cds.odataV4.indexPage` to `cds.indexPage`.
- [cds.java@1.14.0] OData V4 `$expand` now supports using inner `$top` and `$skip` query options.
- [cds.java@1.14.0] Improved the changeset and error handling in the OData V2 adapter to align the behaviour more closely to OData V4.
- [cds.java@1.14.0] The privileged user is now allowed to read the drafts of all entities and users.
- [cds.java@1.14.0] Action and function calls returning a structured type can now be executed on remote OData services.
- [cds4j@1.18.0] `CQL.matching` to build a Query-by-Example style predicate
- [cds4j@1.18.0] Support path expressions in Update and Delete
- [cds4j@1.18.0] Introduce a global switch to disable WITH PARAMETERS in SQL statements on SAP HANA
- [cds4j@1.18.0] Support removing values in CDS data through `CdsDataProcessor` converters
- [cds4j@1.18.0] Reflection API: Support composition of Aspects
- Support dots in entity names

- [cds-runtime@2.9.0] Support for `cds.LargeString` in queries for remote services
- [cds-runtime@2.9.0] Support for tenant-aware emit in AMQP messaging
- [cds-runtime@2.9.0] Metadata (for example, `__count` or `@odata.count` for OData V2 and OData V4, correspondingly) of an external service result are uniformly normalized (for example, to `$count`) and propagated with the result by the rest-client
- [cds-runtime@2.9.0] Improved support for managed composition of one
- [cds-runtime@2.9.0] Support for cascade DELETE for composition of one
- [cds-runtime@2.9.0] Smart quoting in SQL statements
- [cds-runtime@2.9.0] Improved memory consumption of integrity checks
- [cds-runtime@2.9.0] Result payload includes ETag values of composition targets
- [cds-runtime@2.9.0] Custom metadata in OData result (alpha)
- [cds-runtime@2.9.0] Support for canonical URL to `$metadata` in `@odata.context` of a response: use `cds.env.odata.contextAbsoluteUrl = true` to get a service URL (default) or `cds.env.odata.contextAbsoluteUrl = 'http://example.com/yourService/'` to set your own URL
- [cds-runtime@2.8.4] Database pool teardown in case credentials becomes invalid
- [cds-runtime@2.8.4] Idle timeout added to default database pool configuration
- [cds-mtx@1.1.2] Multitenant applications without tenant-specific extensions now support schema evolution based on `.hdbmigrationtable` files.
- [cds-mtx@1.1.2] Provisioning parameters for the container creation can now also be set through cds environment `mtx.provisioning.container` or environment variable `CDS_MTX_PROVISIONING_CONTAINER`.\ Provisioning parameters that are set in the subscription request to `mtx/v1/provisioning/tenant` override the values from the environment.
- [cds-mtx@1.1.2] Dedicated hdi deployment options can now be set through environment variable `HDI_DEPLOY_OPTIONS`, for example, `HDI_DEPLOY_OPTIONS="{\"trace\": true }"`. See section Deployment Options in HDI for more details.
- [cds-mtx@1.0.28] It's now possible to pass hdi deployment parameters `undeploy` and `path-parameter` with the model upgrade (`mtx/v1/model/upgrade` and `mtx/v1/model/asyncUpgrade`)
- [cds-sidecar-client@1.1.13] Include original server error message in case of HTTP errors.

### Changed ​

- [cds-dk@3.5.0] `cds init` creates projects with latest version of `sqlite3` again.
- [cds-dk@3.5.0] `cds add mta` now creates a mta.yaml file that correctly handles spring boot .jar and .war archives.
- [cds-dk@3.4.2] `cds init` uses latest `Maven Java archetype` version `1.13.1` for creating Java projects.
- [cds-dk@3.4.2] Bump version of `@sap/cds` to 4.5.3
- [cds-dk@3.4.1] Bump version of `@sap/cds` to 4.5.2
- [cds-dk@3.4.1] Bump version of `@sap/cds-runtime` to 2.8.6
- [cds-dk@3.4.1] Bump version of `@sap/cds-compiler` to 1.49.2
- [cds.java@1.14.0] The cds-maven-plugin now enforces a minimum `@sap/cds-dk` version of `3.0.0`.
- [cds.java@1.14.0] Service entity `DraftAdministrativeData` is read-only now. Direct requests are rejected (for example, `/Service/DraftAdministrativeData`). Read requests via navigation to this entity (for example, `/Service/Entity(id)/DraftAdministrativeData`) are allowed for authorized users.
- [cds.java@1.14.0] In case property `cds.security.openUnrestrictedEndpoints` isn't configured explicitly, the Spring security configuration in the runtime authenticates all endpoints in multitenant scenario. In single tenant mode, the endpoints are still authenticated according to the restrictions in the CDS model.
- [cds.java@1.14.0] The signature of the error messages 400002, 400012, 400015, 400018, 400019, 409006 and 428002 was changed to not expose request data in error messages.
- [cds4j@1.18.0] Elements with type UUID are not searched by default any longer
- [cds4j@1.18.0] Improve Performance of cascading delete for acyclic delete graphs
- [cds4j@1.18.0] Use batch delete in upserts
- [cds4j@1.18.0] Suppress WITH PARAMETERS for simple CQL statements on SAP HANA
- [cds-runtime@2.9.0] The default implementation of SAP Event Mesh (`enterprise-messaging`) is now multitenant aware. Currently only emit is implemented. The old, shared variant is available through `enterprise-messaging-shared`.
- [cds-runtime@2.9.0] Skip localization on pure count queries
- [cds-runtime@2.9.0] Managed properties of base entity are updated if any composition target is updated
- [cds-runtime@2.9.0] Deactivate during two-month grace period via compatible feature flag `cds.env.features.update_header_item = false`
- [cds-runtime@2.9.0] Default text templates for element assertions don't contain an element name as a parameter anymore
- [cds-runtime@2.9.0] Custom authorization header can now be set in service consumption
- [cds-runtime@2.9.0] Managed associations-to-one aren't expanded in the result of a POST request in case of `cds.odata.flavor = v4`
- [cds-runtime@2.9.0] Deactivate during two-month grace period via compatible feature flag `cds.env.features.skip_expand_assoc = false`
- [cds-runtime@2.9.0] Implicit auto exposed entities inherit authorization restrictions from parent
- [cds-runtime@2.9.0] Modifying an entity without authorization results in HTTP code `403` instead of `404`
- [cds-runtime@2.9.0] Instance-based `@restrict.where` clauses are ignored during `CREATE` (instead of rejecting the request)
- [cds-runtime@2.9.0] Deactivate during two-month grace period through compatible feature flag `cds.env.features.skip_restrict_where = false`

### Fixed ​

- [cds-dk@3.5.0] `cds env` does not longer fail with an exception for unknown commands
- [cds-dk@3.4.2] `cds init` now refers to the latest HDI deployer, which supports Node.js v14
- [cds-dk@3.4.1] `cds watch` now shuts down its child process properly, so that `EADDRINUSE` errors in SAP Business Application Studio are gone
- [cds-compiler@1.50.0] to.edm(x): Illegal OData identifiers, which aren't exposed in the generated edmx schema aren't causing errors anymore.
- [cds-compiler@1.50.0] to.cdl: Annotations are now rendered with the new delimited Identifier syntax
- [cds-compiler@1.50.0] to.sql/hdi: Fixed a bug, which led to an exception if elements were referenced as types.
- For the SQLite dialect, date, time, and timestamp are rendered as simple string literals instead of function calls.
- For naming mode "plain", date, time, and timestamps are rendered as SQL-compliant literals.

- [cds@4.6.4] Fix call to `to.hdi.migration` compiler API
- [cds@4.6.4] `cds build` for SAP HANA now correctly passes `sql_mapping` options to new hdimigration compiler API.
- [cds@4.6.3] `cds compile --to serviceinfo` returns better results for Java projects
- [cds@4.6.3] `cds.connect.to('srv-missing')` called twice with `srv-missing` not configured, would have failed with an error on the first call, but got stuck in the Promise chain for all subsequent calls.
- [cds@4.6.3] `.after` handlers are called with result based on request, e.g., array for collection and object for entity, instead of always array Deactivate during two-month grace period via compatible feature flag `cds.env.features.arrayed_after = true`

- [cds@4.5.3] `cds deploy` and `build` now refer to the latest HDI deployer, which supports Node.js v14
- [cds@4.5.2] `cds serve --with-mocks` now also works in `production` environment if `cds.features.mocked_bindings` is true. Previously, mocks were always disabled in `production`.
- [cds@4.5.2] `cds serve` now only fires the `listening` event once
- [cds@4.5.2] `cds build` redacts cds configuration data in log messages
- [cds.java@1.14.0] Fixed a bug that caused `null` values to miss in expanded entities in OData V2 responses.
- [cds.java@1.14.0] Fixed a bug that caused `null` values in remote OData V2 function parameters to be handled incorrectly.
- [cds.java@1.14.0] Fixed a bug that caused results of remote OData V2 actions or functions calls returning a single entity response to be handled incorrectly.
- [cds.java@1.14.0] Fixed a bug that caused the `cds-maven-plugin` to try to use an invalid Node.js installation.
- [cds.java@1.14.0] Fixed a bug that caused the `cds-maven-plugin` to omit the execution of cds commands.
- [cds.java@1.14.0] Fixed a bug that prevented mock user configuration in case there was an XSUAA-binding in default-env.json but XSUAA-configuration has been turned off explicitly.
- [cds4j@1.18.0] Support handling `null` as a default value
- [cds4j@1.18.0] Fix search in draft entities on SAP HANA
- [cds4j@1.18.0] Fix return types in FLUENT style `EventContext` interfaces
- [cds4j@1.18.0] Fix SQL exception on SAP HANA when using FALSE as predicate
- [cds4j@1.18.0] Draft: Remove cascade annotations from draft entities
- [cds-runtime@2.9.1] Namespace lookup in EDM for OData configuration
- [cds-runtime@2.9.1] Find previous entity for inherited authorization restrictions
- [cds-runtime@2.9.1] Use extended model in generic CRUD post-processing
- [cds-runtime@2.9.1] Clone headers before sanitizing for logs
- [cds-runtime@2.9.0] `req.diff` for deep hierarchies
- [cds-runtime@2.9.0] DateTime conversion for `INSERT` statements using `.columns` and `.values/.rows` on SAP HANA
- [cds-runtime@2.9.0] OData V4 error response target for bound actions
- [cds-runtime@2.9.0] Requests using `$search` query option on draft enabled active entities
- [cds-runtime@2.9.0] Path navigations in `$filter` aren't considered as aggregated away when used in combination with `$apply`
- [cds-runtime@2.9.0] Draft: Entities with expired draft can now be deleted
- [cds-runtime@2.9.0] `Edm.Time`, `Edm.DateTime`, and `Edm.DateTimeOffset` serialization issues when using external OData V2 service
- [cds-runtime@2.9.0] Primitive property access of Singletons via URL like `/Singleton/name`
- [cds-runtime@2.9.0] Path navigation in `$orderby` expressions for draft-enabled services on SAP HANA
- [cds-runtime@2.8.6] Handling of OData query option `$skiptoken` when URL is encoded (that is, `%24skiptoken`)
- [cds-runtime@2.8.5] Handling of OData query option `$skiptoken`
- [cds-runtime@2.8.4] Crash on bad remote service credentials
- [cds-runtime@2.8.4] Wrong case order during query generation in service consumption
- [cds-mtx@1.1.2] Fix job-status handling.
- [cds-mtx@1.1.2] Persist job errors, so they can be revealed even after MTX restart.
- [cds-odata-v2-adapter-proxy@1.5.9] Improve TypeScript typings
- [cds-odata-v2-adapter-proxy@1.5.8] Update `@sap/logging` dependency
- [cds-odata-v2-adapter-proxy@1.5.7] Restore backwards compatibility with CDS v3
- [cds-odata-v2-adapter-proxy@1.5.6] Convert response message targets

### Removed ​

- [cds-runtime@2.9.0] Redundant key generation

## January 2021 ​

### Added ​

- [cds-lsp@4.3.0] asynchronous initialization for annotation plugins
- [cds-lsp@4.3.0] find references for annotation plugins
- [cds-lsp@4.3.0] revalidates workspace after an initial annotation plugin installation
- [cds-compiler@1.49.0] to.hdi/sql:Updated the list of reserved keywords for SAP HANA and SQLite
- Use "smart quoting" for naming mode "plain" - automatically quote reserved keywords

- [cds-compiler@1.49.0] to.hdi.migration:Supports various kinds of entity changes: entity addition/deletion/change (the latter including element additions/deletions/type changes).
- Provides option to render any element type change as `ALTER TABLE DROP` to prevent deployment issues due to incompatible data (default for length reductions or association/composition changes).

- [cds-compiler@1.49.0] to.cdl: Smart artifact references are now rendered explicitly via `:` notation
- [cds@4.5.0] `cds.server` provides an option to switch off automatically generated `index.html` served at `/`: Do that in a custom `server.js`:js

```
const cds = require('@sap/cds')
// ...
module.exports = (o) => cds.server({ ...o, index:false })
```
- [cds@4.5.0] The default `index.html` now honors the system's setting for dark mode.
- [cds@4.5.0] Former package `@sap/cds-reflect` is now embedded in `@sap/cds`
- [cds.java@1.13.0] The serve configuration of application services now allows to explicitly configure which services are served by which protocol and even allows to use different service paths for different protocols. This is enabled by the new annotations `@protocols` and `@endpoints`, which adds to the already existing `@path` annotation. The same can now also be configured in configuration files in the `cds.application.services..serve` section.
- [cds.java@1.13.0] Added a new artifact `cds-feature-k8s`, which implements service binding support for Kubernetes & Kyma. By default service bindings are expected as secrets under `/etc/secrets/sapcp//`, using key-value based secrets files. Additional service bindings with arbitrary secrets paths can be specified under the `cds.environment.k8s.serviceBindings` property.
- [cds.java@1.13.0] OData V2/V4 PATCH or PUT requests now put key values from the URL into the data map. This ensures that keys are immutable and makes key values available directly in POJO arguments of event handlers.
- [cds.java@1.13.0] OData V2 now provides `__deferred` links for unexpanded navigation properties.
- [cds.java@1.13.0] OData V2 now supports reading parameterized views.
- [cds.java@1.13.0] Added the possibility to create and configure remote services. Going forward, these services are used to represent local CQN-based service clients to remote OData APIs. They can be configured by using the property `cds.remote.services`.
- [cds.java@1.13.0] CQN Selects on remote OData services now support inline count.
- [cds.java@1.13.0] Pseudo variables like `$user.locale` are now handled in CQN statements to remote OData services.
- [cds.java@1.13.0] CQN statements using `byId()` can now be executed on remote OData services.
- [cds.java@1.13.0] CQN statements using `contains` are now using `substringof` when executing them against remote OData V2 services.
- [cds.java@1.13.0] CQN statements using parameters can now be executed on remote OData services.
- [cds.java@1.13.0] CQN statements using batched updates or batched deletes can now be executed on remote OData services.
- [cds.java@1.13.0] Batched or parameterized CQN statements that result in multiple OData requests are now executed as a `$batch` request on remote OData services. All those requests are combined into a single changeset to ensure atomicity.
- [cds.java@1.13.0] Action and function calls can now be executed on remote OData services.
- [cds.java@1.13.0] Added a first draft of an Outbox Service API.
- [cds.java@1.13.0] Simplified the $batch access log line to omit host, port and service path, which is the same in every request of the batch.
- [cds.java@1.13.0] Added a new API to retrieve authentication information, for example the JWT token of the current user. It can be accessed from the `CdsRuntime` using `getProvidedAuthenticationInfo`. The new API replaces the former internal `AuthenticatedUserClaimProvider`.
- [cds.java@1.13.0] The `cds-services-archetype` now supports the creation of new CAP Java projects with OData V2 support. Add command line argument `-DodataVersion=v2` to choose OData V2 support.
- [cds.java@1.13.0] The goal `addIntegrationTest` of the `cds-maven-plugin` automatically detects the OData version of the CAP Java project and adds the corresponding integration test class.
- [cds.java@1.13.0] The goal `install-cdsdk` of the `cds-maven-plugin` provides a new command line argument `cds.install-cdsdk.force=true` to force a new installation of `@sap/cds-dk`.
- [cds.java@1.13.0] The goal `cds` of the `cds-maven-plugin` validates the version of the installed `@sap/cds-dk` against a minimum required version. If the required version isn't fulfilled the build fails.
- [cds4j@1.18.0] Add CDS Data Processor API Beta to validate, convert, and generate CDS data
- [cds4j@1.18.0] Add Indexed parameters as replacement for deprecated positional parameters
- [cds4j@1.18.0] Add `@cds.java.name` annotation to define custom names for elements when generating Java interfaces
- [cds4j@1.18.0] Add `UniqueConstraintException`
- [cds4j@1.18.0] Add `NotNullConstraintException`
- [cds4j@1.18.0] Reflection API: Support for Events referencing other Events, Entities, and Structured Types
- [cds4j@1.18.0] Reflection API: Support for Aspects
- [cds4j@1.18.0] Reflection API: Add `setCqn` method in the generated EventContext Interface & overload `create` method
- [cds-runtime@2.8.0] Support for OData proxies Beta
- [cds-runtime@2.8.0] Support for OData cross-service references Beta
- [cds-runtime@2.8.0] Support upsert for to-one containment with foreign key in parent
- [cds-runtime@2.8.0] Support for case-insensitive `bearer` prefix when forwarding token in service consumption
- [cds-runtime@2.8.0] Support for filter on `null` values in service consumption
- [cds-runtime@2.8.0] Server-side pagination for REST services
- [cds-runtime@2.8.0] Input validation for typed parameters of actions/functions
- [cds-runtime@2.8.0] Format assertion exception for UUIDs in MTX's `ProvisioningService.tenant` (old SAP Cloud Platform subaccount IDs aren't UUIDs)
- [cds-runtime@2.8.0] Draft scenario all active is extended
- [cds-runtime@2.8.0] Skip integrity checks via:`@assert.integrity: false` on entity and service level (was only on association level)
- `cds.env.features.assert_integrity = false` as global config (private `cds.runtime.skipIntegrity` will be removed)

- [cds-runtime@2.8.0] Skip SAP HANA's localization feature (`WITH PARAMETERS ('LOCALE' = '')`) via `cds.env.features.with_parameters = false`
- [cds-runtime@2.8.0] Deprecation warning for `req.run`
- [vscode-cds@3.3.0] finds references for annotations

### Changed ​

- [cds-dk@3.4.0] `cds init` uses latest `Maven Java archetype` version `1.12.1` for creating Java projects.
- [cds-dk@3.4.0] `cds init` allows `_` in project name and leaves conversion to `Maven Java archetype`.
- [cds-dk@3.4.0] `cds init --add notebook` and `cds add notebook` now use a Python venv and offer a default Jupyter Notebook viewer.
- [cds-dk@3.4.0] Multitarget Node.js applications can now be initialized with multitenancy support by running `cds init --add mta,mtx`. Beta
- [cds-dk@3.3.5] Bump versions of `@sap/cds`
- [cds-dk@3.3.4] Bump versions of `@sap/cds` and `axios`
- [vscode-cds@3.3.0] extension is now called `SAP CDS language support`
- [vscode-cds@3.3.0] uses `axios@0.21.1`
- [vscode-cds@3.3.0] uses `@sap/cds-lsp@4.3.0` (see corresponding changelog for details)
- [vscode-cds@3.3.0] uses `@sap/cds-compiler@1.49.0`
- [vscode-cds@3.3.0] new user options for where-used requests until now this functionality was enabled by default and now needs to be enabled via user options: generic annotations - where a certain annotation `class` or `namespace` is used
- strings literals - where same string literals are used

- [cds-lsp@4.3.0] new user options for where-used request until now this functionality was enabled by default and now needs to be enabled via user options generic annotations - where a certain annotation `class` or `namespace` is used
- strings literals - where same string literals are used

- [cds-lsp@4.3.0] consumes `cds-compiler` 1.49.0
- [cds-lsp@4.3.0] compatibility with early versions of `cds-compiler` 2.x
- [cds-lsp@4.3.0] simplified consumption of CDS textmate grammar for Jetbrain IDEs
- [cds-compiler@1.49.0] OData/EDMX: Change the `EntityType` precedence of the OData term definition `AppliesTo=` attribute. If `AppliesTo` contains both `EntityType` and `EntitySet`, the annotation was assigned to the entity type. Extending an `AppliesTo=[EntitySet]` with `EntityType` would be OData compliant but incompatible for clients, which still expect the annotation at the set and don't perform the full lookup. With this change, `EntitySet` and `EntityType` are treated individually, effectively annotating the type and (if available) the set. This fixes both extendability and client behavior.
- [cds-compiler@1.49.0] to.hdbcds/hdi/sql: Reject using associations or compositions in query elements starting with `$self` or `$projection`.
- [cds-compiler@1.49.0] OData: Update vocabularies `Common`, `PersonalData`, `UI`.
- [cds-compiler@1.49.0] Update vocabularies `Aggregation`,``Common`
- [cds@4.5.0] SAP Fiori preview is now disabled if `NODE_ENV` is `production`, to avoid any runtime overhead there. You can enable it with configuration `cds.features.fiori_preview: true`.
- [cds@4.4.10] `cds build` for SAP HANA now only filters CSV files if it's needed, for example, if they contain comment lines.
- [cds.java@1.13.0] Entities annotated with `@cds.autoexpose` are now read-only, if they're auto-exposed by the CDS compiler (`@cds.autoexposed`), regardless if they're accessed directly or through a path navigation. Composition children of such entities inherit the read-only attributes of their parents now. This ensures that auto-exposed value helps (and, for example, their localized texts) are protected from write operations.
- [cds.java@1.13.0] Composition child entities (`@cds.autoexposed`, but not `@cds.autoexpose`) are now forbidden as the root of a path, regardless if they're also the target of the path or not. They should always be accessed through a path navigation starting from their parent entity. Draft-enabled entities continue to be an exception to this rule.
- [cds.java@1.13.0] The `DraftAdministrativeData` structure is only created once for a single draft document (root draft entity with all of its composition children). Earlier a dedicated `DraftAdministrativeData` structure was created for each entity in the draft document. This fixes issues where the user, who changed the draft last, or the last changed timestamp weren't consistent across the draft document.
- [cds.java@1.13.0] Temporal timestamps from `sap-valid-at`, `sap-valid-from`, and `sap-valid-to` query parameters are now truncated to microseconds, as this is the general granularity of timestamps in CDS.
- [cds.java@1.13.0] The error messages for Constraint Violation errors have been improved, by distinguishing not null constraint violations from unique constraint violations. With that the previous general error code `409001` (`CONSTRAINT_VIOLATED`) has been deprecated and is replaced by the more specific error codes `409003` (`VALUE_REQUIRED`) and `409006` (`UNIQUE_CONSTRAINT_VIOLATED`).
- [cds.java@1.13.0] Renamed `send` methods in `MessagingService` to `emit` to avoid confusions with function names in Node.js.
- [cds.java@1.13.0] Renamed property `cds.datasource.serviceName` to `cds.datasource.binding` (previous name is deprecated, but still available)
- [cds.java@1.13.0] Renamed property `cds.security.xsuaa.serviceName` to `cds.security.xsuaa.binding` (previous name is deprecated, but still available)
- [cds4j@1.18.0] Fix projection resolvement of aliased to-many associations
- [cds4j@1.18.0] Fix SQL exception on updates having only key values as data
- [cds4j@1.18.0] Fix `NoSuchElementException` when using binary elements in where condition
- [cds-reflect@2.13.5] Sunset. Code is now in `@sap/cds` package.
- [cds-runtime@2.8.0] ETag added for expanded entities
- [cds-runtime@2.8.0] Use `cds.log()` throughout (incl. odata-server)
- [cds-runtime@2.8.0] Replace text keys with default text (that is, w/o locale) before logging error
- [cds-runtime@2.8.0] Read after write on draft activate doesn't read deep
- [cds-runtime@2.8.0] On HTTP error (status >= 400) during remote service consumption: log details and throw gateway error
- [cds-runtime@2.8.0] `accept=application/json,text/plain` is used as default `accept` header for remote service calls
- [cds-runtime@2.8.0] Improved custom error message in case acquiring a client from the pool timed out
- [cds-runtime@2.8.0] Metadata endpoints are protected by default if respective service is protected. Deactivate metadata endpoint protection via `cds.env.odata.protectMetadata = false`.
- [cds-runtime@2.8.0] Streamlined module names used in logging

### Fixed ​

- [vscode-cds@3.3.0] temporary folder for `CDS Preview` commands is no longer part of project to avoid files being checked in
- [vscode-cds@3.3.0] re-validates workspace after an initial annotation plugin installation to show annotation errors w/o the need of manual code edit
- [cds-lsp@4.3.0] dependency analysis for compilation: if a changed file has dependencies to the roots, but the root models don't cover it, no longer it will compile multiple times
- [cds-lsp@4.3.0] translation code action wasn't shown in the context of annotations
- [cds-lsp@4.3.0] code completion for annotations had a trailing @
- [cds-lsp@4.3.0] annotation assignment spanned beyond semantical end
- [cds-lsp@4.3.0] code formatting of brackets enclosing multiple elements in annotations had wrong indentation
- [cds-lsp@4.3.0] indexing of on condition for elements was broken
- [cds-lsp@4.3.0] update regex to highlight one and many keywords properly
- [cds-compiler@1.49.0] Structured foreign key and forward association reference paths used in ON condition definitions are now translatable into the correct short form ON condition paths in Association to Join translation.
- [cds-compiler@1.49.0] to.hdbcds: Aliased mixin-associations are now handled correctly
- [cds-compiler@1.49.0] Using a hex literal like `x'D028'` (in a CSN input) could lead to an error.
- [cds-compiler@1.49.0] for.odata: Fix a bug in constraint calculation if principal has no primary keys.
- Don't overwrite user-defined `@Core.Computed` annotation.

- [cds-compiler@1.49.0] to.hdi/sql/hdbcds: Fixed a bug during processing of skipped/otherwise not db-relevant artifacts.
- [cds-compiler@1.49.0] to.hdbcds/hdi/sql: Types aren't rendered anymore for SAP HANA in quoted mode.
- Aliases are now respected when resolving $self
- Association clones are now prepended with three underscores (`_`) instead of two to prevent shadowing of context names or usages

- [cds@4.5.1] Update `@sap/cds-runtime` dependency
- [cds@4.5.0] `cds build` now correctly supports multitenant applications defining multiple database modules, for example, one database for tenant-related data and one for shared data.
- [cds@4.5.0] `cds deploy --to hana` does no longer fail with an invalid service name error if `.` is used in the MTA ID.
- [cds@4.4.9] `cds build` for SAP HANA no longer fails sporadically with ENOENT when writing CSV files.
- [cds@4.4.8] Add missing setter for `user.locale`.
- [cds.java@1.13.0] Fixed a bug that caused OData V4 to handle results of `min` functions on date elements incorrectly.
- [cds.java@1.13.0] Fixed a bug that caused properties mapped to `null` to miss in JSON responses to OData V4 requests using `$apply`
- [cds.java@1.13.0] Fixed a bug that caused multiple OData V2 expands with common navigation properties to be handled incorrectly.
- [cds.java@1.13.0] Fixed a bug that caused OData V2 function imports returning empty result sets to fail with an error.
- [cds.java@1.13.0] Fixed a bug that prevented element values to be changed to `null`, when saving an edited draft.
- [cds.java@1.13.0] Fixed a bug that could cause inconsistent states after a draft GC. The draft GC is now only triggered on the root entity of a draft-document, which ensures that either the whole document or nothing is garbage-collected. This aligns with the change around `DraftAdministrativeData`.
- [cds.java@1.13.0] Improved the logged error message in case deletion of a draft during the draft GC failed.
- [cds.java@1.13.0] Fixed a bug that caused frequent `Missing type information` warnings in the log, when accessing draft-enabled entities.
- [cds.java@1.13.0] Fixed a bug that caused immutable fields of draft-enabled entities to be handled incorrectly when new child entities are created.
- [cds.java@1.13.0] Fixed a bug that caused errors, when Microsoft JavaScript Dates with offsets (for example, `/Date(1601359314168-0100)/`) were returned from a remote OData V2 API.
- [cds.java@1.13.0] Fixed a bug that caused incorrect result structures when a remote OData V2 API returned `__deferred` links.
- [cds.java@1.13.0] Fixed a bug that caused `404` errors received from requests on remote OData collection endpoints to be silently ignored.
- [cds.java@1.13.0] Fixed a bug that caused precision loss in floating point numbers returned from remote OData services.
- [cds.java@1.13.0] Fixed a bug that caused the DataSource pool to be initialized multiple times in case the DataSource is configured based on service bindings.
- [cds.java@1.13.0] Removed the misleading term "secondary" from log lines, indicating which database services have been auto-configured.
- [cds.java@1.13.0] Fixed a bug that caused project URLs in the pom.xml to be invalid.
- [cds.java@1.13.0] Fixed a bug that caused issues with loading EDMX files in Maven test executions on Windows.
- [cds.java@1.12.1] Fixed a bug that caused the ETag header to miss in a OData V4 response, when the request header `Prefer: return=minimal` was set.
- [cds.java@1.12.1] Fixed a bug that caused tenant-specific extensions (MTX) to be ignored in the OData V2 adapter.
- [cds.java@1.12.1] Fixed a bug that caused the asynchronous tenant unsubscription to be incomplete, if the tenant HDI container was explicitly not deleted.
- [cds4j@1.18.0] Deprecate positional parameters in favor of indexed and named parameters
- [cds4j@1.18.0] Draft: Deletion isn't cascaded anymore to the `DraftAdministrativeData` of a non-root draft entity, because one deep draft document shares a single `DraftAdministrativeData` entity now.
- [cds4j@1.18.0] Reflection API: Refactor `CdsEvent` to inherit `CdsStructuredType`
- [cds4j@1.18.0] Deprecate `ConstraintViolationException`
- [cds4j@1.18.0] Improve performance of Deep Update: execute update statements in batches
- [cds4j@1.18.0] Search: The SQL rendering for search on SQL backends has been changed for localized elements: besides in the user's language texts are now additionally searched in the default language. On SAP HANA the performance of search over large data sets has been improved. This optimization is requires the association `localized` to the texts entity.
- [cds-runtime@2.8.3] No pagination while reading single entity
- [cds-runtime@2.8.3] `SELECT.limit.offset.val` should be a number
- [cds-runtime@2.8.2] `@mandatory` annotation of typed parameters of actions/functions
- [cds-runtime@2.8.1] Skip input validation for arrayed types as parameter of actions/functions
- [cds-runtime@2.8.1] Log error stack when serving to REST
- [cds-runtime@2.8.1] `@assert.range` doesn't imply `@mandatory`
- [cds-runtime@2.8.0] Aggregated-away properties in `$select`, `$expand`, and `$filter` now behave correctly
- [cds-runtime@2.8.0] Exception when accessing texts for a renamed localized draft entity
- [cds-runtime@2.8.0] Deep Update wrongly tried to create entries in case of nested `to-one` compositions
- [cds-runtime@2.8.0] Navigation on singleton
- [cds-runtime@2.8.0] Localized error messages if no authentication used
- [cds-runtime@2.8.0] Fix draft with expand when ordering by draft-specific columns
- [cds-runtime@2.8.0] Incorrect content type in batch response if no `Accept` header is provided
- [cds-runtime@2.8.0] Input validation for enums using `falsy` values
- [cds-runtime@2.8.0] Insert via navigation throws an error if the root of navigation doesn't exist
- [cds-runtime@2.8.0] Filter virtual fields from columns and expand by READ
- [cds-runtime@2.8.0] `auto-expand` of generated foreign keys when functions/actions return entities
- [cds-runtime@2.8.0] Custom headers are normalized to lower case
- [cds-runtime@2.8.0] Post-processing of arrayed elements in Database Service
- [cds-runtime@2.8.0] Duplicated key condition in DELETE CQN
- [cds-runtime@2.8.0] To be checked data for DELETE integrity checks in actions was wrong
- [cds-runtime@2.8.0] Fixed missing != comparator for query generation of remote services
- [cds-runtime@2.8.0] CSN modification during resolve view
- [cds-runtime@2.8.0] Clash of language-code-like namespaces (for example, `de.` or `fr.`) with localized entities
- [cds-runtime@2.8.0] `hdb`'s error event invalidates client
- [cds-runtime@2.7.10] Downport of fix "CSN modification during resolve view".
- [cds-runtime@2.7.9] Don't crash if release called without client.
- [cds-runtime@2.6.11] Downport of fix "CSN modification during resolve view".
- [cds-mtx@1.0.27] Extensions via `extend projection` are now checked correctly by the linter.
- [cds-mtx@1.0.27] Cross HDI container access is now supported properly. See section Deployment Options in HDI in SAP HANA Platform documentation for more details.
- [cds-mtx@1.0.27] When using`hdb` as driver for the database, the tenant updates are now logged properly
- [cds-odata-v2-adapter-proxy@1.5.5] Align determination of locale including sub tags (for example, `zh-TW`)
- [cds-odata-v2-adapter-proxy@1.5.4] Support action/function array parameter types
- [cds-odata-v2-adapter-proxy@1.5.4] Introduce proxy option for body parser size limit
- [cds-odata-v2-adapter-proxy@1.5.3] Improve TypeScript typings
- [cds-odata-v2-adapter-proxy@1.5.2] Add TypeScript typings for proxy constructor
- [cds-odata-v2-adapter-proxy@1.5.1] Normalize service root path in service root xml to include trailing slash
- [cds-odata-v2-adapter-proxy@1.5.0] Update minor version
- [cds-odata-v2-adapter-proxy@1.4.63] Fix that file upload error message doesn't return with 500 status code
- [cds-odata-v2-adapter-proxy@1.4.61] Fix accept header for binary data retrieval to include `application/json`
- [cds-odata-v2-adapter-proxy@1.4.60] Respect offset for Edm.DateTimeOffset, and default to UTC offset (+0000)
- [cds-odata-v2-adapter-proxy@1.4.60] Fix ticks and offset calculation for type DateTimeOffset to handle offset as minutes
- [cds-odata-v2-adapter-proxy@1.4.60] Update README for custom bootstrap to give proxy() priority over `cds.serve` (as with cds run)
- [cds-odata-v2-adapter-proxy@1.4.60] Make authorization header parsing more robust
- [cds-odata-v2-adapter-proxy@1.4.60] Provide __metadata type information for function/action result
- [cds-odata-v2-adapter-proxy@1.4.60] Data format of type `cds.Time` (`Edm.Time`) is switchable to ISO 8601 with proxy option `isoTime` or entity annotation `@cov2ap.isoTime`
- [cds-odata-v2-adapter-proxy@1.4.60] Data format of type `cds.Date` (`Edm.DateTime`) is switchable to ISO 8601 with proxy option `isoDate` or entity annotation `@cov2ap.isoDate`
- [cds-odata-v2-adapter-proxy@1.4.60] Data format of type `cds.DateTime` / `Edm.DateTimeOffset` is switchable to ISO 8601 with proxy option `isoDateTime` or entity annotation `@cov2ap.isoDateTime`
- [cds-odata-v2-adapter-proxy@1.4.60] Data format of type `cds.Timestamp` / `Edm.DateTimeOffset` is switchable to ISO 8601 with proxy option `isoTimestamp` or entity annotation `@cov2ap.isoTimestamp`
- [cds-odata-v2-adapter-proxy@1.4.60] Process `DateTimeOffset` always as UTC information (with `Z`)

### Removed ​

- [cds-runtime@2.8.1] Reconnect for `hdb`
- [cds-runtime@2.8.0] Usage of deprecated `req.run`
- [cds-runtime@2.8.0] Support for deprecated config `cds.auth.passport`. Use `cds.requires.auth` instead.
- [cds-runtime@2.8.0] Default `$format` query option in case of `GET` requests to remote OData services
