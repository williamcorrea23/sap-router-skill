<!-- mirror: https://cap.cloud.sap/docs/releases/2026/changelog -->
<!-- fetched: 2026-05-09T02:26:19.769Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# Changelog 2026 ​

Open Source Changelogs

For repositories and plugins that are open source, please check out the respective changelogs in the [cap-js organization](https://github.com/cap-js) and the [CAP Community](https://github.com/cap-js-community).

## April 2026 ​

### Added ​

- [cds-dk@9.9.0] `cds build` routes `.hdbsynonymconfig` files with `*.configure` properties to the `cfg/` folder for HDI template substitution.
- [cds-dk@9.9.0] `cds deploy` also supports `-b` as a shortcut for `--resolve-bindings`.
- [cds-dk@9.9.0] `cds import` now supports `--resolve-bindings`.
- [vscode-cds@9.9.0] WorkspaceSymbols API: `/x` to get index flags
- [vscode-cds@9.9.0] WorkspaceSymbols: also include models defined in build tasks
- [cds-compiler@6.9.0] compiler:add support for extending views/projections with several SQL clauses: `where`, `group by`, `having`, `order by`, `limit`
- allow extending derived enum types/elements by adding enum symbols
- inside `extend … with enum {…}`, it is now possible to use `extend existingEnumSymbol with @Anno`, like it is already possible inside `extend … with {…}`
- when the new options `v7KeyPropagation` is set, the propagation of the `key` property in queries is simplified, and the `key` property is not propagated when including structures into types

- [cds-compiler@6.9.0] odata: set `meta.compilerCsnFlavor` in the OData transformed CSN
- [cds-compiler@6.9.0] seal: set `meta.compilerCsnFlavor` in the SEAL transformed CSN
- [cds-compiler@6.9.0] effective: set `meta.compilerCsnFlavor` in the effective CSN
- [cds-compiler@6.9.0] sql:set `meta.compilerCsnFlavor` in SQL transformed CSN
- allow single-leafed structures within a `list` on the left-hand side of the `IN` operator. For example `(author, struct) in (...)` becomes `(author_ID, struct_leaf) in (...)`.
- support `cds.Vector` on Postgres and H2

- [cds.java@4.9.0] The i18n message key used with `@assert` is now also used as error code on resulting validation errors.
- [cds.java@4.9.0] Support OData v4 Date and Time functions: `date`, `time`.
- [cds.java@4.9.0] Protocol annotations like `@odata`, `@hcql`, etc. now also support specifying the path for that protocol, e.g. `@odata: 'browse'`.
- [cds.java@4.9.0] The property `cds.protocols.defaults` now lets you specify the list of default protocols each ApplicationService is serving. By default an ApplicationService serves protocols "odata-v2" and "odata-v4". Value "*" adds all available protocols as default.
- [cds.java@4.9.0] Enabled to opt-in for RFC BAPI transaction commit work & wait, instead of commit work that is executed after each RFC call.
- [cds.java@4.9.0] Added new OpenRewrite recipes for deprecated apis that will be removed with CAP 5.0.
- [cds.java@4.9.0] H2/SQLite: Support vector functions in DDL (beta).
- [cds4j@4.9.0] Support functions to extract date and time components from temporal: `date`, `time`.
- [cds4j@4.9.0] Introduce caching for builder proxies.
- [cds4j@4.9.0] Support for the SAP HANA functions `years_between`, `months_between`, `days_between`, `seconds_between`, and `nano100_between`. The functions are emulated on non-SAP HANA databases.
- [cds4j@4.9.0] SAP HANA: support fallback to non-hex SQL on "HEX enforced but cannot be selected" errors on SAP HANA QRC 1/2026.
- use native JDBC/ngdbc support for `cds.Vector` in `String` and `float[]` format.

- [cds4j@4.9.0] Support `cds.Vector` on H2, SQLite and PostgreSQL.
- [cds4j@4.9.0] Support `CQL.vector_embedding` on SAP HANA, H2 and SQLite.
- [cds4j@4.9.0] Support `CQL.l2Normalize` on SAP HANA, PostgreSQL, H2 and SQLite. (beta)
- [cds4j@4.9.0] Support selects from pseudo table. (beta)
- [cds@9.9.0] Event Queue Scheduling: Support for `srv.schedule.task(event, data)` to create so-called "singleton tasks" that exist only once as well as `srv.unschedule.task(event)` to remove them again
- Support for cron expressions as argument for `.every()`, e.g., `.every('*/5 * * * 2')` for "Every 5 minutes, only on Tuesday"
- Support for `cds.appid` for isolating microservices in shared HDI scenarios The experimental option `targetPrefix` is temporarily kept to allow flushing tasks that rely on it, but will be removed soon

- Streamlined aggregation of `queued` service effective configuration

- [cds@9.9.0] Advanced Event Queue Scheduling via Scheduling Service (Beta; enable via `cds.requires.scheduling = true`) Efficient leftover processing by maintaining a schedule in `t0` (requires `@sap/cds-mtxs^3.9`)
- Revised event processing (ongoing)
- Only applicable with queue kind `persistent-queue` (which is the default)

- [cds@9.9.0] In addition to `.csv` files, and `.json` files, initial data can now also be provided via `.yaml` files Limitation: Only supported in Node.js runtimes, so far, not yet by `cds build` for Java, and for production deployments to HANA

- [cds@9.9.0] Support `$select` and `$expand` from draft actions: `draftNew`, `draftPrepare`, `draftActivate`, and `draftEdit`
- [cds@9.9.0] Enable referencing action request responses in `dependsOn` of subsequent requests in the same batch
- [cds@9.9.0] Import files the ESM way in ESM projects, e.g. to support mocking in Vitest
- [cds@9.9.0] Node.js-native `fetch`-based HTTP client for remote service consumption (beta) Used automatically when `@sap-cloud-sdk/http-client` is not installed or forced via `cds.remote.native_fetch = true`
- Known limitations: Resolving destinations via the BTP Destination Service is not supported
- Only basic authentication is supported

- [cds@9.9.0] `cds.infer.elements` now also supports SQL-style casts, wildcard overrides and `excluding` clauses
- [cds@9.9.0] Support for restricting the levels of `$expand` (beta) `@Capabilities.ExpandRestrictions.MaxLevels` defines the maximum allowed depth of an `$expand` starting from the annotated entity
- Additionally, `@Capabilities.ExpandRestrictions.Expandable: false` is interpreted as `@Capabilities.ExpandRestrictions.MaxLevels: 0`
- Finally, there is global config option `cds.query.restrictions.expand.maxLevels`

- [cds@9.9.0] Kafka: `cds.requires.messaging.config = { ... }` allows custom Kafka client config for development scenarios
- [cds-mtxs@3.9.0] It is now possible to create additional instances of the internal Service Manager Client or HANA TMS v2 client to access alternative services. Instances can be created using `cds.xt.containerManager.newInstance(serviceCredentials)`.
- [cds-mtxs@3.9.0] Environment variables `APPLICATION_ID`, `APPLICATION_VERSION_INFO`, and `DEPLOY_ID` are now forwarded to the HDI deploy environment.
- [cds-mtxs@3.9.0] Database deployment can be individually disabled for `cds.xt.SmsProvisioningService` or `cds.xt.SaasProvisioningService` for hybrid scenarios. It can be confiured by e. g. `cds.requires['cds.xt.SmsProvisioningService'] = { "subscribe": { "skip-db": true } }`. This is only available for synchronous subscription.
- [cds-mtxs@3.9.0] `cds.outbox.Messages` to model of `t0`.
- [cds-mtxs@3.9.0] Subscription payloads may now include a `custom_label` in the `_.hdi.create` options to attach additional labels to HANA containers and, for the service-manager, also to bindings. Example: `_.hdi.create.custom_label = 'my_key=my_value'`.

### Changed ​

- [cds-dk@9.9.0] `cds add html5-repo` creates destinations as part of the app deployer module instead of initial destinations in the destination service.
- [cds-dk@9.9.0] `axios` is removed from `dependencies`.
- [cds-dk@9.9.0] `cds init` no longer generates database-specific extensions (`db/hana/`, `db/sqlite/`) and their profile-based configuration in the sample template.
- [vscode-cds@9.9.0] removed `https-proxy-agent` in favour of native VS Code / fetch proxy handling.
- [vscode-cds@9.9.0] `CAP Release Notes` page shows a lightning bolt logo as dimmed background when loading fails.
- [vscode-cds@9.9.0] Zoom direction in Analyze Dependencies was flipped on macOS to have a more natural UX
- [cds-compiler@6.9.0] compiler:add `compilerVersion` to CSN meta
- issue a warning if a structure in an annotation value would have the same CSN representation as an expression
- issue warnings for extends on built-in types
- warn on duplicate members from includes via extend

- [cds-compiler@6.9.0] odata:update OData vocabularies: Common, Core, UI
- using `@readonly` with an expression value on entities or aspects is no longer silently accepted and now produces an error

- [cds.java@4.9.0] `cds-feature-bdc` enforces an allow-list for Formation Type Ids (e.g. `cds.bdc.formationTypeIds`) in production profiles from now on.
- [cds.java@4.9.0] The MTX sidecar health check now uses a configurable timeout instead of a hard-coded 1s limit. Set `cds.multitenancy.health-check.timeout` (type: `Duration`, default: `1s`) to adjust the threshold for your environment.
- [cds.java@4.9.0] The switch `cds.draft.post-active` now defaults to `true`. In case it is set to `false` or not set all POST requests to entities with draftNew action will create a new active instance.
- [cds.java@4.9.0] Improved error handling in `cds-adapter-mcp` to prevent stack traces and internal details from leaking in error responses.
- [cds4j@4.9.0] Path segments for to-one associations no longer contain a filter.
- [cds@9.9.0] I18n keys in `@assert` error messages are now used as error codes. The generic `ASSERT` error key is no longer used if the `message` is not an i18n key.

### Fixed ​

- [cds-dk@9.9.0] `cds add xsuaa --plan broker` does not use plan `application` in approuter scenarios.
- [cds-dk@9.9.0] `cds add postgres` for Kyma no longer adds an invalid `values.yaml` entry for `postgres-db-deployer`.
- [cds-dk@9.9.0] `cds init/add esm` now also fills `package.json` with proper content.
- [cds-dk@9.9.0] `cds deploy --to hana --resolve-bindings` no longer overwrites credentials of all hana-tagged `VCAP_SERVICES` entries with the target container's service key when multiple HDI bindings are present.
- [cds-dk@9.9.0] `cds add data` now adds a newline character at the end of csv files to make appending content easier.
- [cds-dk@9.8.3] Dependency updates, e.g. for CVE-2026-33937.
- [cds-dk@9.8.3] `cds add xsuaa --plan broker` does not use plan `application` in approuter scenarios.
- [cds-dk@8.9.13] CVE-2025-15284: update `express` to fix vulnerability with `qs` <6.14.1
- [vscode-cds@9.9.0] Prevent error when scanning for LSP-restart settings in configuration.
- [vscode-cds@9.9.0] support CDS lookup dirs defined in subfolders e.g. pom.xml (resolve cds env per project root instead of workspace root)
- [vscode-cds@9.9.0] WorkspaceSymbols: NodeJS V8 crashed for very large workspaces
- [vscode-cds@9.9.0] WorkspaceSymbols: filter out symbols from ignored files
- [vscode-cds@9.9.0] add quotes around the binary in the default cds-typer command to support paths with non-alphanumeric characters
- [cds-compiler@6.9.0] compiler:don't introduce a strange `cast` property in the CSN for a column with an expand on a to-many association
- while crawling tokens for LSP, allow extensions without name

- [cds-compiler@6.9.0] effective: don't absolutify paths in filters in annotations
- [cds-compiler@6.9.0] sql: properly resolve references in annotation values and `on` conditions for a column inside an expand without base reference
- [cds.java@4.9.0] HCQL V2: placeholder `$key` is no longer added to the HCQL request.
- [cds.java@4.9.0] Further improved performance of inactive draft delete during save.
- [cds.java@4.9.0] Fixed a bug, causing tenant-related properties (iss, subDomain) not getting propagated to the new `RequestContext` when calling `systemUser()`.
- [cds.java@4.9.0] `cds-feature-change-tracking` performance is improved when large number of entities are inserted.
- [cds.java@4.9.0] Fixed a bug, causing DraftMessages for composition of one to return invalid message targets.
- [cds.java@4.9.0] Fixed a bug, causing `@Core.MediaType` and `@Core.ContentDisposition.Filename` annotations with expression syntax (e.g., `@Core.MediaType: (mimeType)`) to not resolve correctly after type flattening.
- [cds4j@4.9.0] Fixed constant timestamp values in SQL statements. They are now set in UTC independently of the JVM's time zone.
- [cds4j@4.9.0] Fixed broken SQL if a hierarchy view has a sort order specified by order by.
- [cds4j@4.9.0] Fixed SQL error on SAP HANA when using `CASE WHEN` with a constant boolean condition on the select list.
- [cds@9.9.0] Calculation of `nextLink` based on `$skipToken` for requests with `$top` and/or `$skip`
- [cds@9.9.0] Stale entries in `.cds-services.json` are removed reliably, so that `cds mock/watch` no longer try to connect to dead servers
- [cds@9.9.0] Configuration shortcuts like `cds.requires[service] = true` always preserve object configuration from other sources
- [cds@9.9.0] `cds-serve --project  --service ` now honors the explicit service instead of defaulting to `all`
- [cds@9.9.0] Handle expression values for `@Core.MediaType`, like `@Core.MediaType: (mimeType)`
- [cds@9.9.0] Will not add a default target to `MULTIPLE_ERRORS`-type error
- [cds@9.9.0] Enabled creating active composition children using `direct_crud` requests via navigation
- [cds@9.9.0] Removed artifacts of draft metadata from active entity data
- [cds@9.9.0] Prevent type error when encountering an unexpected symbol key in `cds.ApplicationService`
- [cds@9.9.0] Reject requests with `$filter` on operations with primitive return types
- [cds@9.8.5] `compile.for.direct_crud` is resilient against draft-enablement on non-service entities
- [cds@9.8.5] Requests targeting a view with parameters are now correctly send to remote OData services
- [cds@9.8.5] `TypeError` due to unchecked access when handling `PUT` on collection via navigation
- [cds@9.8.5] Null value sorting in draft-enabled scenarios now matches database behavior (NULLS FIRST for ASC, NULLS LAST for DESC)

### Removed ​

- [vscode-cds@9.9.0] Unsupported `play` button for CDS queries in the `CAP Release Notes` page.

## March 2026 ​

### Added ​

- [cds-dk@9.8.2] `cds init` now removes the `.vscode` folder when creating projects in SAP Business Application Studio in order to restore compatibility with other project generators. This is a temporary solution likely to be reverted in cds-dk 10.
- [cds-dk@9.8.0] `cds up --overlay  (Cloud Foundry) now resolves MTA extension descriptors (.mtaext) from the project root.`
- [cds-dk@9.8.0] `cds add postgres` now supports Kyma with automatic database provisioning and IP whitelisting.
- [cds-dk@9.8.0] `cds deploy --to hana --store-credentials` now warns about the deprecated option `--store-credentials`.
- [cds-dk@9.8.0] `cds import` now uses the default options defined via `cds.import.options[] = {option: 'value'}`
- [cds-dk@9.8.0] `cds version` now shows version of `@sap/eslint-plugin-cds`.
- [cds-dk@9.8.0] `cds version --json` returns a stable output format as JSON.
- [cds-compiler@6.8.0] api: basic experimental support for code completion in `cds repl`
- [cds-compiler@6.8.0] compiler:retain original meta property in CSN
- add compilerCsnFlavor to meta property

- [cds-compiler@6.8.0] sql:Add support for `cds.Vector`
- Allow migration from cds.String to cds.LargeString
- Fiori Tree Views in the database backend
- For postgres: warning for identifiers that exceed the databases length limit

- [cds.java@4.8.0] Support aggregate functions in `@assert`.
- [cds.java@4.8.0] Setting `cds.messaging.services..queue.config.channel: null` for a Kafka channel-based messaging service now disables the default channel. If no channel is explicitly configured for an event using `@kafka.channel` the topic itself is used as channel.
- [cds.java@4.8.0] Improved performance of queries merging active and inactive data (e.g. "All" Fiori list-report filter), when reading draft-enabled entities for a user with a lot of drafts.
- [cds.java@4.8.0] Improved performance of inactive draft delete during draft save.
- [cds.java@4.8.0] The `add` goal of the `cds-maven-plugin` now adds a dependency to `cf-java-logging-support-servlet` for feature APPLICATION_LOGGING.
- [cds.java@4.8.0] HCQL adapter and HCQL client for remote services now support HCQL V2.
- [cds.java@4.8.0] Actions annotated with `@Common.DraftRoot.NewAction` now have a default `@On` handler.
- [cds.java@4.8.0] Setting `cds.drafts.postActive` causes plain POST requests to a draft-enabled entity (without explicit `IsActiveEntity`) to create an active instance, in case the entity has a draft new action.
- [cds.java@4.8.0] Support OData v4/v2 Date and Time functions: `year`, `month`, `day`, `hour`, `minute`, `second`.
- [cds.java@4.8.0] Improved layout of change tracking UI on mobile devices.
- [cds.java@4.8.0] Setting `cds.environment.deployment.appid` allows to define an identifier for the applications using the persistent outbox on shared databases.
- [cds4j@4.8.0] Support aggregate functions on associations in expressions of calculated elements, by moving them into a subquery.
- [cds4j@4.8.0] Support functions to extract date and time components: `year`, `month`, `day`, `hour`, `minute`, `second`.
- [cds@9.8.0] Calculated elements are now properly calculated in draft state. So far, the elements have been treated as regular elements ignoring the calculation. In case this causes issues, you can opt-out with `cds.fiori.calc_elements = false` until cds10

- [cds@9.8.0] $compute supports decimal constants
- [cds@9.8.0] Support `/$metadata` requests in OData batch
- [cds@9.8.0] Support for `@odata.bind` parameters in collection bound actions
- [cds@9.8.0] Support for renaming of foreign keys of managed associations while resolving views
- [cds@9.8.0] Support for `Prefer: return=minimal` header in generic draft actions
- [cds@9.8.0] OData batch: Parallel processing of atomicity groups via `cds.odata.max_batch_parallelization=` (default: `1`) Only applicable if `$batch` request exclusively contains `GET` requests
- Note: Parallel processing of atomicity groups is in conflict with OData specification for `multipart/mixed`!
- Additional experimental feature: Bundle independent `GET` requests into single transaction via `cds.odata.group_parallel_gets=true`

- [cds@9.8.0] `hcql`: request raw stream via http header `Accept: application/octet-stream`
- [cds-mtxs@3.8.0] If not needed, CSV data deployment with extensions can be disabled with `cds.requires['cds.xt.ExtensibilityService'].activate['skip-csv'] = true`. This improves the performance when pushing extensions if many extensions already exist.

### Changed ​

- [cds-dk@9.8.0] `cds add multitenancy` does not add an explicit `java` profile to the main app any more.
- [cds-dk@9.8.0] `cds deploy` and `cds bind` support Kyma-by-default for projects with Kyma-only deployment descriptors.
- [cds-dk@9.8.0] `cds deploy --to hana --on k8s` now supports deploying to SAP HANA using an existing Kubernetes service binding, allowing non-default Kyma naming conventions.
- [cds-dk@9.8.0] `cds import` now correctly imports Views with Parameters from a given OData EDMX service definition.
- [cds-dk@9.8.0] `cds import` now interprets empty navigation path references as if it would be a null value.
- [cds-compiler@6.8.0] compiler:improve warning in case of invalid type for key
- simplify syntax error text when expecting Comparison and Operator tokens
- improve support for code completion with `case` expressions, queries, and subqueries

- [cds.java@4.8.0] Generated `package.json` for new projects no longer contains a `description`, `repository` and `license`.
- [cds4j@4.8.0] Changed the fallback mode of expand to `parent-keys`.
- [cds4j@4.8.0] A query that uses a ref as substring|prefix|suffix in `contains`|`startWith`|`endsWith` is now rejected. Only literals or parameters may be used.
- [cds@9.8.0] Destination caching is no longer modified at runtime. Caching configuration is now managed by the Cloud SDK.
- [cds@9.8.0] `cds.env` now supports for credentials lookup Kubernetes secrets with a structure like `${SERVICE_BINDING_ROOT}/${SERVICE}/${INSTANCE}/${BINDING}`. Previously only one level between the root and the binding was possible.
- [cds@9.8.0] Allow using ESlint 10 by opening version range `^9 || ^10` for `@eslint/js`
- [cds@9.8.0] Outbound `hcql` requests always via `POST`

### Fixed ​

- [cds-dk@9.8.2] `cds add workzone` for Kyma correctly adds the `html5-apps-repo-runtime` to its `Chart.yaml`.
- [cds-dk@9.8.2] `cds add app-front` in combination with `cds add ias` correctly includes all `IASDependencyName` settings.
- [cds-dk@9.8.2] `cds build` has improved performance in some scenarios.
- [cds-dk@9.8.1] `cds build` plugins correctly formats a thrown `BuildError` in the logs.
- [cds-dk@9.8.1] `cds version` also reports a cds-dk installation in Java projects that don't have such a dependency in their `package.json`.
- [cds-dk@9.8.0] `cds bind` reports additional error information while accessing Cloud Foundry services.
- [cds-dk@9.8.0] `cds version` now works again if executed in subfolders of Java projects without a `pom.xml` file.
- [cds-dk@9.8.0] `cds add workzone` in combination with `cds add ias` adds the `HTML5.IASDependencyName` for the `srv-api`.
- [cds-dk@9.8.0] `cds add lint` now creates an ESLint config file again.
- [cds-dk@9.8.0] `cds import` now correctly handles enum types as keys in EDMX v4 import.
- [cds-dk@9.8.0] `cds push` now shows the correct passcode URL when the subdomain changes between logins.
- [vscode-cds@9.8.0] running CDS Typer in WSL projects
- [vscode-cds@9.8.0] formatter: indentation of annotations to entities with annotated actions
- [cds-compiler@6.8.0] sql:do not report validation errors on entities marked as `@cds.persistence.skip`
- normalize named arguments for portable functions
- properly flatten associations for temporal unique constraints

- [cds.java@4.8.0] Fixed a bug, causing the IAS tenant host not getting propagated to Cloud SDK if the issuer does not include a protocol scheme.
- [cds.java@4.8.0] Fixed a bug, causing incorrect predicates in remote OData adapter for expressions with `false` literals.
- [cds.java@4.8.0] Fixed a bug, causing errors in case custom `EventContext` interfaces were (package) private.
- [cds.java@4.8.0] Fixed a bug, causing draft data created from a deep update to have `IsActiveEntity` and `HasDraftEntity` set to `null`.
- [cds.java@4.8.0] Fixed a bug, causing incorrect executions of cds-maven-plugin `build` and `resolve` goals, when executed from the root directory.
- [cds.java@4.8.0] Fixed a bug, causing drafts to be created in OData V4, even if `IsActiveEntity` was explicitly set to `true` in a preceeding URL segment.
- [cds.java@4.8.0] Fixed a bug, causing TenantProviderService.readTenantInfos to throw an exception with TMSv2.
- [cds4j@4.8.0] Fixed parsing of calculated elements with value `null`.
- [cds4j@4.8.0] Fixed SQL error due to missing CTEs when using `exits` on runtime views in infix filters.
- [cds4j@4.8.0] Fixed SQL error when using `exists` predicates in calculation expressions.
- [cds4j@4.8.0] Fixed a bug forcing runtime view mode `resolve` for queries using `lock(null)` (incl. queries parsed from cqn).
- [cds4j@4.8.0] `matchesPattern` is correctly parsed from and to JSON when the flags are omitted.
- [cds4j@4.8.0] Hierarchical selects now optimize the select list, resulting in simpler queries.
- [cds@9.8.4] `res.statusCode` of batch sub-requests did not consider potential modifications during `srv.on('error')`
- [cds@9.8.4] Restore login challenge for late `401` with mocked authentication in `$batch`
- [cds@9.8.4] Batched request fails when depended upon atomicity group fails
- [cds@9.8.3] OData batch parallel processing: Drain remaining queue when aborting
- [cds@9.8.2] Compatibility with `@eslint/js^10`
- [cds@9.8.1] OData batch parallel processing: Preserve request sequence for OData v2
- [cds@9.8.1] In inbound messaging, only load the extended model if there is a tenant
- [cds@9.8.1] Ensure `cds.fiori.direct_crud` is considered during `cds build`
- [cds@9.8.0] OData JSON batch: Response value formatting and escaping for non `application/json` responses
- Setting correct `content-type` header value for all content types

- [cds@9.8.0] `content-length` is now set for OData multipart/mixed batch subrequest responses
- [cds@9.8.0] Connection issues when a Kafka cluster has been created with public endpoints
- [cds@9.8.0] Fix duplicated columns in case of `$expand=*`
- [cds@9.8.0] Unhandled promise rejection in `cds.spawn` if extended model could not be loaded
- [cds@9.8.0] Set `msg.tenant` & `msg.event` of messages received from Kafka, based on the stringified header values
- [cds@9.8.0] `$expand=*` expands only the exposed associations
- [cds@9.8.0] Broken `odata-v2` formatting for values used in `beween- and`, `in` and `lambda` type expressions
- [cds@9.8.0] Appending `/$value` to an entity that is not a media entity returns `400 Bad Request`
- [cds@9.8.0] In Jest test runs in ESM projects, files are now loaded properly
- [cds@9.8.0] Correctly resolve dependencies in workspace setups where the CAP project is not at the root
- [cds@8.9.9] Requests targeting a view with parameters are now correctly send to remote OData services
- [cds-mtxs@3.8.1] More accurate exception handling if the extension table `cds.xt.Extensions` cannot be read.
- [cds-mtxs@3.8.1] For HANA, tenant subscription now stores the tenant database `schema` in `cds.xt.Tenants`.
- [cds-mtxs@3.8.1] The annotation allowlist correctly handles allowed parent annotations.
- [cds-mtxs@3.8.0] The extension linter for annotations on structured types does not throw a `TypeError`.
- [cds-mtxs@3.8.0] The response when getting extensions using `/-/cds/Extensions/` now also contains the `status`.

## February 2026 ​

### Added ​

- [cds-dk@9.7.0] `cds debug` is now supported for Kubernetes/Kyma deployments.
- [cds-dk@9.7.0] `cds init --nodejs` as a shortcut for `cds init --add nodejs`.
- [cds-dk@9.7.0] Support for express 5 (in addition to express 4).
- [cds-dk@9.7.0] `cds deploy --to hana` now supports `--out` to specify the output directory for generated files.
- [cds-dk@9.7.0] `cds mock ` as a shortcut for `cds serve --mocked --project  --in-memory? --port 0`.
- [cds-dk@9.7.0] `cds add ias` adds a URL for local approuter testing to `redirect-uris` if approuter is configured.
- [cds.java@4.7.0] Added resilient connection handling in `cds-feature-kafka` for the case that the Kafka cluster is not available when a microservice starts.
- [cds.java@4.7.0] Improved handling of `@assert` and dynamic `@mandatory`/`@inapplicable` on managed associations.
- [cds.java@4.7.0] Added support for `publishPrefix` and `subscribePrefix` in configuration for `cds-feature-kafka`.
- [cds.java@4.7.0] Added support for Event Hub integration via `mvn cds:add -Dfeature=EVENT_HUB`
- [cds.java@4.7.0] Reduced database lock conflicts when processing messages of unordered outboxes by skipping locked entries.
- [cds4j@4.7.0] Allow using `$now` as default value for elements of type `Date`.
- [cds4j@4.7.0] Support function `ceil` as synonymn for `ceiling`.
- [cds4j@4.7.0] Allow supplying foreign-key values for path-based inserts via the data entries.
- [cds4j@4.7.0] Draft-enclosed associations now retain `@cascade` annotations.
- [cds4j@4.7.0] SAP HANA, PostgreSQL and H2: Support `Select.lock(mode, CqnLock.Wait.SKIP_LOCKED)`, which returns immediately and yields only rows that are not currently locked (non-blocking).
- [cds@9.7.0] Support for express 5 (in addition to express 4)
- [cds@9.7.0] New config option `cds.requires.db.data` to configure source folders for initial data and test data CSV files
- [cds@9.7.0] Enterprise Messaging now caches access tokens to support high-throughput message processing from Event Mesh
- [cds@9.7.0] Automatically add `@Common.DraftRoot.NewAction` for each draft-enabled entity during `compile.for.odata` via `cds.fiori.direct_crud=true`
- [cds@9.7.0] Support for `null` value in `@odata.bind`
- [cds@9.7.0] Validation of flow annotations at compile step

### Changed ​

- [cds-dk@9.7.0] `cds version` received major enhancements: It's now fully based on the `npm ls` command and always prints a tabular output. Also some new flags were added; check `cds version --help` for details.
- [cds-dk@9.7.0] `cds deploy --to k8s` increased the timeout to wait for the HDI container creation from 120 to 180 seconds.
- [cds-dk@9.7.0] `cds add` facets now abort when executed in a folder that is neither a Node.js nor a Java project.
- [cds-dk@9.7.0] `cds add lint` now also adds the .java extension to the files that are linted within VSCode.
- [cds-dk@9.7.0] `cds init` now restricts project names to 64 characters maximum, requiring them to start with an alphanumeric character or `_`, and contain only alphanumeric characters, `_`, and `-`.
- [cds-dk@9.7.0] `cds import` now generates an on condition for associations if the navigation property in an imported OData v4 service has a referential constraint.
- [cds-dk@9.7.0] `cds build` does not ignore wildcarded folders like `app/*` any more.
- [cds-dk@9.7.0] `cds env --resolve-bindings/-b` also considers local service bindings.
- [cds.java@4.7.0] `Update` statements triggered from `draftActivate` now include a key filter in the statement's `ref`.
- [cds.java@4.7.0] `cds-feature-flow` now rejects the statements for flow-annotated actions without full key in the infix filter.
- [cds@9.7.0] Colors are enabled by default in GitHub Actions workflows
- [cds@9.7.0] `queue`: Manually update `lastAttemptTimestamp` of outbox messages (instead of relying on `@cds.on.update: $now`)
- [cds@9.7.0] `express` is no longer a peer dependency of `@sap/cds` but a regular one. Applications that want to pin it or require it in their custom code, should declare the dependency on their own.
- [cds@9.7.0] `hcql` response format: `{ data: [], errors: [] }`
- [cds-mtxs@3.7.1] Provisioning service calls now skip `cds.xt.DeploymentService` operations if it is disabled, logging only a warning.

### Fixed ​

- [cds-dk@9.7.2] `cds build --for mtx-sidecar` correctly resolves `@source` in custom MTX sidecar services.
- [cds-dk@9.7.2] `cds build` now utilises caching for workspace resolution, which will speed up build times for projects with many workspaces.
- [cds-dk@9.7.2] `cds add` commands don't augment Helm Charts if not managed by CAP.
- [cds-dk@9.7.2] `cds add approuter` for Kyma configures token exchange for managed approuter scenarios.
- [cds-dk@9.7.2] `cds bind` reports additional error information while accessing Cloud Foundry services.
- [cds-dk@9.7.1] `cds add completion` now works without specifying the project runtime.
- [cds-dk@9.7.1] `cds add xsuaa` correctly adds the the binding for the `html5-apps-deployer` on Kyma.
- [cds-dk@9.7.1] `cds version` prints an older format in a legacy situation.
- [cds-dk@9.7.1] `cds add nodejs` is automatically added in BAS scenarios for compatibility if no other runtime is specified.
- [cds-dk@9.7.1] `cds add data -n` works correctly for `Composition of one` scenarios.
- [cds-dk@9.7.0] `cds add sqlite --for production` adds `@cap-js/sqlite` to `dependencies`.
- [cds-dk@9.7.0] `cds build --ws` fixes a race condition.
- [cds-dk@9.7.0] `cds build` now places the `i18n` folder in the generated output in nested locations.
- [cds-dk@9.7.0] `cds build --for mtx-sidecar` loads CAP plugins from the MTX sidecar instead of the main app for generating the sidecar CSN.
- [cds-dk@9.7.0] `cds add ias` uses a matching `IASDependencyName` for the application content deployer.
- [cds-dk@9.7.0] `cds add ias` uses a more generic `redirect-uris` pattern.
- [cds-dk@9.7.0] `cds import` no longer generates a managed association for navigation properties of imported OData v4 services if the foreign key, the managed association would generate, already exists.
- [cds-dk@9.7.0] `cds add multitenancy` for Java correctly creates a `package-lock.json` in mtx/sidecar.
- [cds-dk@9.7.0] `cds add xsuaa` works properly when executed after `cds add workzone`.
- [cds-dk@8.9.14] CVE-2026-25639: Update `axios` version to 1.13.5
- [eslint-plugin-cds@4.2.1] Removed usage of deprecated API in `lib/utils/rules.js`
- [eslint-plugin-cds@4.2.0] Use ESLint API supported by versions `9` and `10`.
- [eslint-plugin-cds@4.1.2] No longer crash on .java files larger than 32 kB.
- [eslint-plugin-cds@4.1.2] Weaken `java/cql-class-targets` to only warn when a string literal is passed as parameter.
- [eslint-plugin-cds@4.1.2] `assoc2many-ambiguous-key` no longer falsely warns about 1-n joins when an infix filter reduces the joined relation to a single row.
- [cds-compiler@6.7.3] sql: do not resolve path navigations to virtual elements which resulted in an internal error.
- [cds-compiler@6.7.2] compiler: Just issue warning for `using` declaration referring to nothing (fixes regression introduced with v6.7.0 if there is a file containing a `namespace` declaration, but no definitions)
- [cds-compiler@6.7.2] effective: clean up internal Symbols from meta section
- [cds-compiler@6.7.2] sql: clean up internal Symbols from meta section
- [cds.java@4.7.0] Avoid extra parenthesis in `filter` predicate of `$apply` in remote OData.
- [cds.java@4.7.0] Reduced the number of database calls to set session variables (on Postgres)
- [cds.java@4.7.0] Fixed a bug, that caused skipping CQN Predicate `FALSE` in remote OData.
- [cds.java@4.7.0] Fixed a bug, causing duplicated draft messages in case of entities with compound keys.
- [cds.java@4.7.0] Fixed a bug, causing duplicated draft messages in case of String-based targets.
- [cds.java@4.7.0] Fixed a bug, causing HTTP status `500` instead of `400` (not supported) when setting the `Content-Type: application/pdf` header for OData v4 action.
- [cds4j@4.7.0] Fixed exception on averaging over associations when using the static query builder API.
- [cds4j@4.7.0] Fixed refs with `$self` in exists predicates.
- [cds4j@4.7.0] Fixed "No element found" exception on statements using match predicates (exists, any, all) in subqueries.
- [cds4j@4.7.0] Fixed projection resolution in results: for null values when paths are aliased by the first segment.
- for paths whose last segment equals another element in the projection.

- [cds4j@4.7.0] Fixed a bug in recursive hierarchy on HANA, causing sporadic incorrect sort order of elements.
- [cds4j@4.7.0] Fixed an exception when using `exists` predicates in runtime views.
- [cds@9.7.1] `DELETE` requests nulling a `@mandatory` property
- [cds@9.7.1] Correctly call remote collection bound action for `odata-v4` services
- [cds@9.7.1] Flow annotation validation at compile time strictly follows the documentation: only enum status values are allowed Status value validation can be disabled via `cds.features.skip_flows_validation=true`

- [cds@9.7.0] Correctly respond with status `404` when `@cds.api.ignore` annotated action is requested
- [cds@9.7.0] Ensure plugin debug emitted with `DEBUG=all`
- [cds@9.7.0] Prevent app crash when `JSON.parse` of operation parameters fails
- [cds@9.7.0] Generate correct UI annotations for Status Transition Flows when building and compiling
- [cds@9.7.0] Remote services: Prefer `cds.context.user?.authInfo?.token?.jwt` over JWT in HTTP header of incoming request
- [cds@9.7.0] References to child elements in `@Common.Text` annotations will now be checked. The reference will not be included in `@cds.search`, in case ... ... the reference can not be found in the annotated entity's associations
- ... the referenced entity is annotated with `@cds.persistence.skip`
- ... the referenced field does not exist in the referenced entity
- References to children of children will be ignored.

- [cds@9.7.0] OData parser: Ignore superfluous brackets
- [cds@9.7.0] Prevent app crash in case of `req.reject()` during draft activate triggered via OData batch
- [cds@9.7.0] `cds minify` no longer removes services if their actions are kept
- [cds@9.7.0] Better error when subquery can't be resolved for the current service
- [cds@9.7.0] Flows: Record transition to default value on `INSERT`/ `UPSERT`
- [cds@9.7.0] Error response properties of OData batch subrequests are now formatted identically to properties in single OData error responses
- [cds@9.7.0] Prevent `@Common.numericSeverity` from appearing in persistent draft messages (in addition to the correct property `numericSeverity`)
- [cds-mtxs@3.7.1] HANA deployment parameters set via the `HDI_DEPLOY_OPTIONS` environment are now correctly evaluated.

### Removed ​

- [cds@9.7.0] `@cds.on.update: $now` from `cds.outbox.Messages.lastAttemptTimestamp`

## January 2026 ​

### Added ​

- [vscode-cds@9.7.0] Multi-Cursor support for range selection
- [vscode-cds@9.7.0] Folding range for consecutive `using` statements
- [vscode-cds@9.6.3] Progress reporting for persistency
- [vscode-cds@9.6.0] (Experimental) persistency of where-used index This feature allows to persist/restore where-used indexes on a per-file basis to speed up indexing of large projects with many root models. It is currently experimental and must be enabled via user setting `cds.workspace.persistency.enabled`. There are a couple of user settings to fine tune the behavior `cds.workspace.persistency.enabled`: general enablement. All other settings have no effect if this is disabled.
- `cds.workspace.persistency.persistAfterSave`: when a file is saved its index is persisted.
- `cds.workspace.persistency.persistAfterCompile`: when (closed) CDS files are compiled (also as part of another model compilation) their index gets persisted.
- `cds.workspace.persistency.restoreBeforeCompile`: when CDS files are part of a compilation their persisted index is used if matching
- `cds.workspace.persistency.restoreAfterStartup`: restore all persisted indexes after start-up
- `cds.workspace.persistency.indexAllAfterStartup`: index all files not yet persisted
- `cds.workspace.persistency.garbageCollectOrphanedIndexesAfterStartup`: index files are written per content. Delete index files with outdated content after start-up
- `cds.workspace.persistency.garbageCollectOrphanedIndexesAfterNSaves`: Delete index files with outdated content after specified number of `Save` requests
- `cds.workspace.persistency.reindexAfterCompileIfRestored`: If files are part of a compilation and a matching index exist, still index again.

- [cds-compiler@6.7.0] to.hdi: Support .hdbprojectionview for Data Product Production
- [cds-mtxs@3.7.0] Immediate deletion of TMS HANA tenants can be enabled with configuration `cds.requires['cds.xt.DeploymentService'].hdi.create.immediate_deletion = true` (combined with `cds.requires['cds.xt.DeploymentService'].hdi.create.cleanup_hana_tenants = true`)
- [cds-mtxs@3.7.0] Container credential determination with TMS v2 is accelerated by using `$top=1` for the container query.

### Changed ​

- [cds-dk@9.6.1] All commands use colored logs in GitHub Actions workflows by default.
- [vscode-cds@9.7.0] Persistency of where-used index is now beta
- [vscode-cds@9.7.0] User setting categories in settings UI
- [cds-compiler@6.7.0] compiler: Change internal processing sequence (extensions and entity generation) for potentially upcoming compiler features; messages for erroneous models might differ slightly
- [cds-compiler@6.7.0] for.odata/to.edm(x): Enhancements for Fiori Tree Views: support managed associations with explicit foreign keys, raise messages when the `@hierarchy` annotation cannot be applied.
- [cds-mtxs@3.7.0] MTXS is now using fewer requests when getting container credentials from HANA TMS v2.
- [cds-mtxs@3.6.2] Maximum chunk size when retrieving container bindings from service-manager is reduced to 1000.

### Fixed ​

- [cds-dk@9.6.1] CVE-2025-15284: update `express` to fix vulnerability with `qs` <6.14.1.
- [cds-dk@9.6.1] `cds watch` is more efficient on Linux with respect to `inotify` events. This fixes some crash and stall situations on Linux, especially in SAP Business Application Studio where resources are shared.
- [cds-dk@9.6.1] `cds build --production` correctly includes `message.properties` from i18n files provided by CAP plugins.
- [cds-dk@9.6.1] `cds add sample` fixes a warning about unused imports in app/common.cds.
- [cds-dk@9.6.1] `cds init` fixes some rare argument parsing errors.
- [vscode-cds@9.7.0] Show `CAP Release Notes` automatically only if timestamp of page changed.
- [vscode-cds@9.7.0] Formatter: align element names after `key` keyword only
- [vscode-cds@9.6.3] Some minor fixes
- [vscode-cds@9.6.0] Syntax highlighting in bracketed expressions
- [cds-compiler@6.7.1] compiler: Properly accept aspects as composition targets in an `extend` (fixes regression introduced with v6.7.0)
- [cds-compiler@6.7.0] to.sql: portable hana functions `*_between` with dates
- [cds-compiler@6.6.2] for.effective: Don't resolve backlinks in aspects
- [cds@9.6.4] `queue`: Too eager removal of control data from deserialized task
- [cds@9.6.4] Stop overriding existing `cds.requires.[service].credentials` configurations using values from `.cds-services.json`
- [cds@9.6.3] `queue`: Exactly-once guarantee only with `legacyLocking: false`
- [cds@9.6.2] Consider `@mandatory.message` for the error message, when a mandatory action / function parameter is not provided
- [cds@9.6.2] Respond with error code `400` when receiving requests that use `any()` / `all()` filters on an association to one
- [cds@9.6.2] Error message of unknown property check will no longer include `undefined` to identify structs without a name
- [cds@9.6.2] `enterprise-messaging`: Type error in check for unofficial XSUAA fallback
- [cds@9.6.2] Status Transition Flows: Exclusions for multiple projections
- [cds-mtxs@3.7.0] More stable deletion of HDI container instances via SAP BTP Service Manager.
- [cds-mtxs@3.7.0] Extension validation no longer counts field type changes as new fields.
- [cds-mtxs@3.7.0] Getting a task from the job service no returns `404` for non-existing tasks.
- [cds-mtxs@3.7.0] In combination with `@cap-js/hana` version 2.6.0 pool connection errors with invalid database credentials are handled more gracefully.
- [cds-mtxs@3.6.2] Command `cds-mtx` now correctly passes the services when triggering the 'served' event.
- [cds-mtxs@3.6.2] HDI deployment log files are now safely written in case of process terminations.
- [cds-mtxs@3.6.2] Etag returned by `/-/cds/model-provider/getCsn` now properly reflects model changes again.
- [cds-mtxs@3.6.2] Reading extensions using `/-/cds/extensibility/Extensions` now also works with an outdated schema of the extension table.

### Removed ​

- [vscode-cds@9.6.0] User setting `cds.workspace.debounceFastChanges`, now always enabled
