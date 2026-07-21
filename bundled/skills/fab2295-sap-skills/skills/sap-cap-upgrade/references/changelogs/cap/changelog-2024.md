<!-- mirror: https://cap.cloud.sap/docs/releases/2024/changelog -->
<!-- fetched: 2026-05-09T02:26:17.961Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# Changelog 2024 ​

Open Source Changelogs

For repositories and plugins that are open source, please check out the respective changelogs in the [cap-js organization](https://github.com/cap-js) and the [CAP Community](https://github.com/cap-js-community).

## December 2024 ​

### Added ​

- [cds-dk@8.6.0] `cds repl` got new option `--run` to run a server; also available through `.run` command within the REPL.
- [cds-dk@8.6.0] `cds repl` got new option `--use` to make the features of a `cds` available as globals.
- [cds-dk@8.6.0] `cds repl` got new builtin `.inspect` command to inspect object with configurable depth, e.g. `.inspect cds .depth=1`.
- [cds-dk@8.6.0] `cds watch` now detects a TypeScript project and tries to run with `tsx` if this is installed locally or globally. Otherwise a warning message is emitted. `CDS_TYPESCRIPT=false` can be used to opt out of this behavior.
- [cds-dk@8.6.0] `cds import --group` to allow RFC importer to organize imported modules under a logical name.
- [cds-dk@8.6.0] `cds init/add` for Java projects automatically create a `package-lock.json`.
- [cds-dk@8.6.0] `cds add ias` adds IAS configuration (beta).
- [cds-dk@8.6.0] `cds add ams` adds AMS configuration (beta).
- [cds-compiler@5.6.0] Allow to refer to draft state element `HasActiveEntity` and `HasDraftEntity` via variable `$draft` in annotation path expressions.
- [cds-compiler@5.6.0] for.odata|to.edm(x): Introduce annotating the generated foreign keys
- [cds.java@3.6.0] Feature `cds-feature-ord` now also exposes EDMx metadata documents which are linked from ORD documents with the same authentication scheme as the ORD document.
- [cds.java@3.6.0] The goal `generate` of the `cds-maven-plugin` executed with option `-Dcds.generate.feature=EVENT_HANDLERS` can be executed from project root.
- [cds.java@3.6.0] Optimized HANA JDBC connection retrieval in MT applications with shared pool configured. In particular, recently used connections of the same tenant can be reused much more quickly if they are not taken by an other tenant already.
- [cds.java@3.6.0] Support for Apache Kafka messaging in CAP Java application running in a DwC environment, see util-cap-kafka for details.
- [cds.java@3.6.0] CAP integration for IAS now also supports SAP BTP, Kyma runtime.
- [cds.java@3.6.0] Events, for which registered handlers on Event Hub messaging services are available, will be automatically exposed as integration dependencies in the ORD document of the CAP application. For each topic one integration dependency will be created.
- [cds4j@3.6.0] Support match predicates `anyMatch`/`allMatch` in infix filters of element refs on the select list.
- [cds@8.6.0] `SELECT.from` now supports full-query tagged template literals, e.g.: `SELECT.from`Books where ID=${201}``
- [cds@8.6.0] `cds.ql` enhanced by functions to facilitate construction of CQN objects.
- [cds@8.6.0] `cds.ql` became a function to turn CQN objects, CQL strings, or tagged template literals into instances of the respective `cds.ql` class.
- [cds@8.6.0] New `cds` events to allow multitenant plugins: `compile.for.runtime`, `compile.to.dbx`, `compile.to.edmx`.
- [cds@8.6.0] `cds.env` now supports `.cdsrc.js` and `.cdsrc.yaml` files, also in plugins.
- [cds@8.6.0] `cds.env` now supports profile-specific `.env` files, e.g. `.hybrid.env` or `.attic.env`.
- [cds@8.6.0] Experimental OData parsing for hierarchy requests (`descendants`, `ancestors`, `TopLevels`)
- [cds@8.6.0] The new OData adapter now supports `cds.odata.containment`. Contained entities can only be accessed via their parents and do not show up as EntitySets in $metadata and the service document.

### Changed ​

- [cds-dk@8.6.0] Running `cds init` in the user's home dir w/o a project name now fails. This is to prevent creation of configuration that would act as global (user) configuration leading to follow-up problems with later projects.
- [vscode-cds@8.5.1] enabling `newParser` via `cds.env` will no longer interfere with CDS editor
- [cds-compiler@5.6.0] Update OData vocabularies: 'Common', 'EntityRelationship', 'UI'
- [cds.java@3.6.0] cds-feature-kafka now uses mTLS for authentication. OAuth authentication is deprecated by Kafka on BTP and will be removed starting February 2025.
- [cds.java@3.6.0] The goal `install-cdsdk` of the `cds-maven-plugin` has been deprecated.
- [cds.java@3.6.0] The `cds-services-archetype` generates new CAP Java projects with a `pacakge.json` and `package-lock.json` containing a devDependency to `@sap/cds-dk`. The `srv/pom.xml` is generated with the execution of `npm ci` instead of using goal `install-cdsdk`.
- [cds.java@2.10.6] cds-feature-kafka now uses mTLS for authentication. OAuth authentication is deprecated by Kafka on BTP and will be removed starting February 2025.
- [cds@8.6.0] `CDL`, `CQL`, and `CXL` globals are deprecated => use respective functions from `cds.ql` instead.
- [cds@8.6.0] `CREATE`, and `DROP` globals are deprecated => use respective functions from `cds.ql` instead.
- [cds@8.6.0] Zulu time zone information is stripped from `cds.DateTime` properties when querying Odata V2 remote services
- [cds@8.6.0] Processing of `@restrict.where` was aligned with CAP Java: Instance-based authorization on app service calls does not consider custom `WHERE` clauses of `UPDATE`/`DELETE` queries Until `@sap/cds^9`, this change can be deactivated via `cds.env.features.compat_restrict_where = true`

- Simple static clauses (e.g., `$user.level > 5`) are no longer evaluated by the server but added to the respective SQL regardless. As a result, requests may receive a response of `2xx` with an empty body instead of a `403`. Until `@sap/cds^9`, this change can be deactivated via `cds.env.features.compat_static_auth = true`

- Read restrictions on the entity are no longer taken into consideration when evaluating restrictions on bound actions/ functions Until `@sap/cds^9`, this change can be deactivated via `cds.env.features.compat_restrict_bound = true`

### Fixed ​

- [cds-dk@8.6.1] `cds add ams` now creates correct dependencies for Java projects.
- [cds-dk@8.6.0] `cds add html5-repo` adds an `index.html` as `welcomePage` to the `xs-app.json`, if available.
- [cds-dk@8.6.0] `cds bind` fixes the recursive call to `mergeCredentials`.
- [cds-dk@8.6.0] `cds add` won't add a duplicated `SUBSCRIPTION_URL` if it doesn't match the template specification.
- [cds-dk@8.6.0] `cds watch` gives a better error message for TypeScript projects started with if `tsx` isn't installed.
- [cds-dk@8.6.0] `cds build` no longer throws an undefined error when processing build plugin messages.
- [cds-dk@8.5.1] `cds build` now logs existing plugin build messages if a BuildError is thrown.
- [cds-compiler@5.5.2] to.hdi|sql|edm[x]: Correctly handle `cds.Map`, ensure that it does not have `.elements` yet.
- [cds.java@3.6.0] Fixed an issue in `add` goal of the `cds-maven-plugin` causing a wrong yaml syntax of mock user roles in `application.yaml`.
- [cds.java@3.6.0] Fixed a bug causing URL encoded client certificates being incorrectly rejected on Kyma when calling endpoints secured with mTLS (e.g. SMS and UCL).
- [cds.java@3.6.0] Fixed a bug causing the close of DB sessions when the outbox tries to process an outbox entry that shall be emitted using a Kafka messaging service.
- [cds.java@3.6.0] Fixed a bug that bound service manager instances where no plan could be determined on K8S are ignored.
- [cds.java@2.10.6] Values for key elements annotated with `@Core.Immutable` are no longer removed from the payload of updates.
- [cds.java@2.10.6] For ST applications, the request user name is written to Auditlog V2 instead of the technical provider user.
- [cds4j@3.6.1] Fixed a bug in handling case of `node_id` and `parent_id` for HANA hierarchies
- [cds4j@3.6.0] Fixed a bug, causing duplicate elements `node_id` and `parent_id` on the select list of a source of a hierarchy
- [cds4j@3.6.0] Fixed a bug, causing a wrong value for `IsActiveEntity` in a nested select from inactive drafts
- [cds4j@3.6.0] Reject write operations through projections using paths or infix filters
- [cds4j@3.6.0] Don't generate UUIDs for association key elements on insert
- [cds4j@2.10.6] Reject write operations through projections using paths or infix filters
- [cds4j@2.10.6] Don't generate UUIDs for association key elements on insert
- [cds@8.6.0] ETag calculation if column was provided as Javascript Date
- [cds@8.6.0] Forwarding of `/$count` queries while mocking the external service
- [cds@8.6.0] Resolving of implicit function parameters (e.g `GET .../test.foo?x='bar'`)
- [cds@8.6.0] Arrayed elements are not part of response unless explicitly selected with `$select`
- [cds@8.6.0] In case of nonexistent user attributes (`$user.X`), only the subclause gets substituted with `false`
- [cds@8.6.0] `@odata.context` in new OData adapter: Fixed crash for requests to actions/functions when `cds.env.odata.context_with_columns` is enabled
- Aggregation functions with `$apply` are now returned when `cds.env.odata.context_with_columns` is enabled
- `@odata.context` is now the first property in the response values of `concat` requests
- Binary key values are now properly encoded and formatted
- Fixed keys appearing as `(undefined)` for updates via navigation to-one
- Fixed key value pairs being returned as `undefined=undefined` for property access of aspects
- Backlinks no longer appear as keys for property access of aspects
- Non-anonymous structured types are now prefixed with the service name
- Structured types no longer end with `/$entity`

- [cds@8.5.1] `cds deploy --dry --model-only` no longer tries to load a SQLite database
- [cds@8.5.1] Requests with HTTP methods other than `POST` to the `/$batch` endpoint are now rejected when using the new OData adapter
- [cds-mtxs@2.4.2] The annotation check of the extension linter can now properly handle extensions like `extend service CatalogService with @cds.query.limit;`
- [cds-mtxs@2.4.1] `cds-mtx upgrade "*"` correctly parses metadata supplied by the `--body` parameter.

### Removed ​

- [vscode-cds@8.5.1] obsolete support for CAP Notebook urls

## November 2024 ​

### Added ​

- [cds-dk@8.5.0] `cds debug` lets you debug Node.js applications running locally or in Cloud Foundry.
- [cds-dk@8.5.0] `cds watch --inspect` and `cds watch --inspect-brk` activate the debugger in the same way as the standard Node.js CLI options, i.e. they accept a `host:port` combination and `0` as values.
- [cds-dk@8.5.0] The existing `cds watch --debug` is now an alias to `cds watch --inspect`.
- [cds-dk@8.5.0] `cds add cloud-logging` adds cloud-logging as an alternative for application logging in Kyma.
- [cds-dk@8.5.0] `cds add cloud-logging --with-telemetry` or `cds add telemetry` adds cloud-logging as well as support for `cap-js/telemetry` plugin in Kyma.
- [cds-dk@8.5.0] `cds add handler` now also works for Node.js projects. It creates an implementation file for each service with event handlers for all entities and actions.
- [cds-dk@8.5.0] `cds add esm` creates ESM-compatible Node.js projects. Sample code added by `add sample` and `add handler` will respect this setting if added afterwards. Existing code will not be adjusted by `cds add esm`, though.
- [cds-dk@8.4.1] `cds deploy --no-build` lets you skip the implicit `cds build`.
- [cds-dk@8.4.1] `cds add data/http` supports new type `cds.Map`.
- [vscode-cds@8.4.3] refactoring `using` statements when renaming/deleting files or folders now considers ignore files (.cdsignore or .gitignore) and will not refactor ignored files
- [vscode-cds@8.4.2] user setting to disable refactoring support when renaming/deleting CDS files (`cds.refactoring.files.rename.enabled` and `cds.refactoring.files.delete.enabled`)
- [vscode-cds@8.4.0] Rename or move of CDS files and folders will update all `using` statements to the renamed file
- [vscode-cds@8.4.0] Deletion of CDS files or folders will show all `using` statements to the renamed file with possibility to remove those. Note: The referencing files will likely have compilation errors afterward.
- [vscode-cds@8.4.0] Telemetry reporting in SAP Business Application Studio
- [cds-compiler@5.5.0] CDL parser: when the new experimental option `newParser` is used, the compiler uses a CDL parser with a significantly smaller footprint (among other things).
- [cds-compiler@5.5.0] to.sql|hdi.migration: For SAP HANA, render `ALTER` statements as one big statement to improve performance.
- [cds-compiler@5.5.0] to.sql.migration: Give more helpful comments when using option `script`.
- [cds.java@3.5.0] Added feature `cds-feature-ucl` which allows CAP applications to write custom event handlers for Unified Customer Landscape´s (UCL) SPII Tenant Mapping API.
- [cds.java@3.5.0] Added feature `cds-feature-ord` which allows CAP applications to serve Open Resource Discovery (ORD) documents.
- [cds.java@3.5.0] Added the option to validate semi-open intervals with `@assert.range`.
- [cds.java@3.5.0] Instance based authorization can now reject WRITE/DELETE/custom events with 403 instead of filtering via option `cds.security.authorization.instance-based.reject-selected-unauthorized-entity`
- [cds4j@3.5.0] Codegen: added an option to improve naming for CDS entities with upper case characters containing slashes.
- [cds4j@3.5.0] Support `Select.from(CqnTableFunction)` to use `HANA.hierarchy` as source of a query
- [cds4j@3.5.0] Automatically rename node_id/parent_id based on the @Aggregation.RecursiveHierarchy annotation
- [cds4j@3.5.0] Support `CqnAnalyzer.analyze()` for `CqnFilterableStatement` as convenience
- [cds4j@3.5.0] Add support for filters and orderBy of elements in cds.Map (beta)
- [cds@8.5.0] New `cds.i18n` module used consistently for both, UI labels and runtime messages.
- [cds@8.5.0] Enhanced `cds.validate` to support open intervals for: `@assert.range:[(0),(Infinity)]` -> `0
- [cds@8.5.0] `package.json` validation and suggestions for messaging services.
- [cds@8.5.0] `cds.log()`: Detect binding to SAP Cloud Logging via user provided service. The user provided service must have tag `cloud-logging`.
- [cds@8.5.0] Support for function parameters via query component (example: `GET /foo?bar=baz` instead of `GET /foo(bar='baz')`)
- [cds@8.5.0] Experimental support for programmatic draft actions `srv.new(MyEntity, data)`, `srv.cancel(MyEntity.drafts, keys)`, `srv.edit(MyEntity, data)` and `srv.save(MyEntity.drafts, keys)`
- [cds-mtxs@2.4.0] Deployment logs written by HDI to `stderr` are now attached to deployment error messages.
- [cds-mtxs@2.4.0] For HANA, the initial job status for asynchronous tenant upgrades is now `QUEUED`.
- [cds-mtxs@2.4.0] Annotation in extensions that are blocked by default can now be allow-listed:jsonc

```
"requires": {
  "cds.xt.ExtensibilityService": {
      "extension-allowlist": [
        {
          "for": ["my.bookshop.Books"],
          "annotations": ["@mandatory", "@cds.api.ignore"]
        }
      ]
  }
}
```
- [cds-mtxs@2.3.1] The `X-Correlation-ID` header is set for requests to Service Manager.
- [cds-mtxs@2.3.1] Extension projects can now be tested using `cds w` even if the application base model contains `@impl` annotations.

### Changed ​

- [cds-dk@8.5.0] `cds import` now generates generic action/function in case of bound action/function collision and unbound function collision with @cds.validate = false.
- [cds-dk@8.5.0] `cds add typescript` creates projects with `cds-tsx` to run apps instead of former `cds-ts`.
- [cds-dk@8.5.0] `cds deploy` writes error output to `stderr`.
- [cds-dk@8.5.0] `cds add http` now evaluates mocks users when creating `Authorization` headers
- [cds-dk@8.4.2] `cds init` uses latest Maven Java archetype version 3.4.1 for creating Java projects.
- [vscode-cds@8.4.3] (performance) expensive workspace scanning is only done during renaming/deleting files or folders if those contain CDS files
- [vscode-cds@8.4.2] performance improved when scanning the workspace and calculating refactorings when renaming/deleting CDS files
- [vscode-cds@8.4.0] Improve handling of fall back cds-lsp version 7.9.0
- [vscode-cds@8.4.0] Improve dynamic schema loading for `package.json` and `cds-rc.json`
- [vscode-cds@8.4.0] Improve size and start-up time by bundling
- [cds-compiler@5.5.0] Update OData vocabularies: 'Common', 'PersonalData', 'UI'.
- [cds.java@3.5.0] Property `cds.multiTenancy.subscriptionManager.clientCertificateHeader` has been deprecated. Use 'cds.security.authentication.clientCertificateHeader' instead.
- [cds.java@3.5.0] Property `cds.multiTenancy.security.internalUserAccess.enabled` has been deprecated. Use `cds.security.internalUserAccess.enabled` instead.
- [cds@8.5.0] `cds-deploy` script has a non-zero exit code on deployment failure
- [cds@8.5.0] Properties of type `cds.Binary` in URLs as well as request payload are converted to `Buffer`s. Properties of type `cds.LargeBinary` in request payload are converted to `Readable`s. Previously, both were provided as Base64-encoded strings. This change can be deactivated via `cds.env.features.base64_binaries = true`, which is set by default for profile `attic`.

### Fixed ​

- [cds-dk@8.5.0] `cds import` throws proper error message if Annotation element doesn't have Term attribute.
- [cds-dk@8.5.0] `cds add approuter` no longer enforces Node.js 22, which is not supporter by current `@sap/approuter` version 17. The previous Node.js version 20 is used again.
- [cds-dk@8.5.0] `cds add -p` with custom options now works if the entry was not in the `package.json` beforehand.
- [cds-dk@8.5.0] `cds add http` works for actions without parameters.
- [cds-dk@8.5.0] `cds add workzone` includes the `updateManifestJson` task on initial generation.
- [cds-dk@8.5.0] `cds build --ws` no longer creates migration tables in shared database or wrong workspace.
- [cds-dk@8.4.2] `cds add -p/--package` correctly parse plugin-contributed options.
- [cds-dk@8.4.2] `cds add side-by-side-extensibility` does not throw an error.
- [cds-dk@8.4.2] fix method name in `cds bind` credential handling.
- [cds-dk@8.4.2] `cds add --help` no longer has missing line breaks in help text.
- [cds-dk@8.4.2] `cds` commands no longer fail with an error `cds.extend is not a function` with very old versions of `@sap/cds`.
- [cds-dk@8.4.2] `cds add hana` adds the `requires.db` entry to `.cdsrc.json` for Java projects.
- [cds-dk@8.4.2] `cds add data` creates decimal values with correct scale `0` if only precision is given, like in `Decimal(15)`.
- [cds-dk@8.4.1] `cds compile --to ` shows a cleaner error message.
- [cds-dk@8.4.1] `cds add data` handles composition of one correctly.
- [cds-dk@8.4.1] `cds add http` creates payloads for unbound actions in services.
- [cds-dk@8.4.1] `cds compile --to xsuaa` can now handle annotation expressions in `where` clauses.
- [cds-dk@8.4.1] `cds add http` produces requests for all expected data and no longer relies on existing data on the side.
- [cds-dk@8.4.1] `cds add typer` creates `tsconfig.json` that works with `cds-tsx`.
- [vscode-cds@8.4.1] Deleting CDS files now also suggests to remove `using` statements without artifacts
- [vscode-cds@8.4.0] Preview uses text document listener for refreshing preview file
- [vscode-cds@8.4.0] highlighting of escaped identifiers and parameter lists
- [vscode-cds@8.4.0] `using` path proposals could have been suggesting JS files instead of CDS files in certain cases
- [vscode-cds@8.4.0] on Windows if client mixes upper- and lowercase drive letters some requests could have failed
- [vscode-cds@8.4.0] CDS Typer was called when deleting a file which led to a misleading error output
- [vscode-cds@8.4.0] Analysis of dependencies failed when handling non-npm `package.json` files (e.g. from `pnpm` lacking `name` property)
- [cds-compiler@5.4.4] Re-allow referring to mixins (and table aliases) in added columns
- [cds-compiler@5.4.4] Re-add foreign keys of named aspects to the OData CSN.
- [cds-compiler@5.4.2] to.sql: For SQLite, map `cds.Map` to `JSON_TEXT` to ensure text affinity.
- [cds.java@3.5.0] Fixed a bug in `cds-feature-mt`, causing data sources accidentally being initialized for service instances of `service-manager` which were meant for single tenancy use cases. Now data sources in multi-tenant environments are only created for service plan `container`.
- [cds.java@3.5.0] Fixed a bug causing an `HTTP 500 Internal Server Error` (`CdsDefinitionNotFoundException`) when a CDS service which is inactive due to a feature toggle is targeted in an OData V4 request.
- [cds.java@3.5.0] Fixed a bug in `cds-feature-change-tracking` causing the `StackOverflowError` exception being thrown, when change-tracking entities with references to self.
- [cds.java@3.5.0] Fixed a bug in the `version` goal of the `cds-maven-plugin` printing the version information of the wrong sub-module.
- [cds.java@3.5.0] Fixed a bug, causing client certificates not to be handled correctly on endpoints secured with mTLS (e.g. SMS and UCL).
- [cds.java@3.5.0] Values for key elements annotated with `@Core.Immutable` are no longer removed from the payload of updates.
- [cds.java@3.4.1] Fixed a bug causing an `HTTP 500 Internal Server Error` (`CdsDefinitionNotFoundException`) when a CDS service which is inactive due to a feature toggle is targeted in an OData V4 request.
- [cds.java@3.4.1] Fixed a bug in `cds-feature-change-tracking` causing the `StackOverflowError` exception being thrown, when change-tracking entities with references to self.
- [cds.java@3.4.1] Added filename support for annotation @Core.ContentDisposition.Type: 'inline' in cds-adapter-odata-v4. This ensures that the browser saves the content with the correct filename, if it can't be shown in browser window (e.g. zip archive).
- [cds.java@3.4.1] Fixed an issue in the `cds-services-archetype` causing to create initial CAP Java projects with a reference to a snapshot version of the `@sap/cds-dk`.
- [cds.java@2.10.5] Fixed a bug, causing redundant change log entries being generated for changed localized elements.
- [cds.java@2.10.5] Fixed a bug, causing translated values depending on user locale to appear in values for identifiers for change log entries.
- [cds.java@2.10.5] Fixed a bug, causing UI provided by `cds-feature-change-tracking` to omit text for attributes of the change tracked entities when the respective field is hidden from the UI.
- [cds.java@2.10.5] Fixed a bug in `cds-feature-change-tracking` causing the `StackOverflowError` exception being thrown, when change-tracking entities with references to self.
- [cds4j@3.5.0] Fix builder interface methods for structured elements by adding `@CdsName` annotations.
- [cds4j@3.5.0] `@cds.java.ignore` annotations on structured elements are respected
- [cds4j@2.10.5] Fixed a bug, causing database implementations to fail to load in ForkJoinPool threads
- [cds4j@2.10.5] SAP HANA HEX mode: fixed fallback to non-hex SQL on "HEX enforced but cannot be selected" errors on HANA QRC 3/2024
- [cds@8.5.0] `cds.validate` should not delete readonly keys from `req.data`
- [cds@8.5.0] `cds.validate` should not reject imported associations
- [cds@8.5.0] Readonly fields must not be set when creating draft entities
- [cds@8.5.0] Validation of mandatory properties caused streams to be rejected for new OData adapter
- [cds@8.5.0] `cds.log` with null parameters and JSON format
- [cds@8.5.0] `cds.compile.to.sql` proper replacement for sqlite session variables in java projects
- [cds@8.5.0] `cds.compile.to.serviceinfo` ignores only the `endpoints` property for unknown protocols
- [cds@8.5.0] `Preference-Applied` header is returned in OData adapter if requested
- [cds@8.5.0] No location header is returned on OData update requests if `minimal` preference is set
- [cds@8.5.0] Handling of invalid requests for views with parameters
- [cds@8.4.2] `cds.compile.to.edmx` if using the new builtin type `cds.Map`
- [cds@8.4.1] Validate request method for operations
- [cds@8.4.1] Correctly generate CQN for lambda expressions in new OData adapter
- [cds@8.4.1] `req.diff()` on old database with property transitions
- [cds-mtxs@2.4.0] Status codes for parallel async requests are always reported correctly.
- [cds-mtxs@2.3.1] The access token coming from Service Manager is redacted with `DEBUG` output on.
- [cds-mtxs@2.3.1] The Service Manager client will now poll the ongoing operation for containers which are on "in progress" if it can find an existing instance instead of erroring out.
- [cds-mtxs@2.3.1] `cds login --client` works correctly with client credentials from a service key.
- [cds-mtxs@2.3.1] Synchronous upgrades don't fail for all tenants when there's a tenant for which the upgrade fails.

## October 2024 ​

### Added ​

- [cds-dk@8.4.0] Added support for `import` and `export` for auto-completion in `package.json` and `.cdsrc.json`.
- [cds-dk@8.4.0] `cds add side-by-side-extensibility` adds configuration for logic extensibility via extension points (Java).
- [cds-dk@8.4.0] `cds init --java` can be used as an alias to `cds init --add java`.
- [cds-dk@8.4.0] Add cds schema for `helm` build plugin.
- [vscode-cds@8.3.0] Preview of `mta.yaml` via Mermaid diagram
- [vscode-cds@8.3.0] show absolute name and kind of artifact in hover and completion details
- [cds-compiler@5.4.0] to.edm(x): `cds.Map` as empty open complex type with name `cds_Map` or if the definition has been assigned `@open: false` as empty open complex type `cds_Map_closed` in OData V4.
- [cds.java@3.4.0] Added support for annotation `@Core.ContentDisposition.Type` in `cds-adapter-odata-v4`.
- [cds.java@3.4.0] Added support for Preference `omit-values=nulls` for OData V4. To omit `null` values in payload the header `Prefer` with value `omit-values=nulls` must be specified.
- [cds.java@3.4.0] The goal `add` of the `cds-maven-plugin` supports adding AMS integration to a CAP Java project.
- [cds4j@3.4.0] Support `where in ` predicates in Select, Update and Delete
- [cds4j@3.4.0] New case-when-then API to build case expressions
- [cds4j@3.4.0] SAP HANA: optimized search over to-many associations
- [cds4j@3.4.0] Add basic support for `cds.Map` type (beta)
- [cds@8.4.0] Set the maximum allowed size of HTTP headers in bytes for `$batch` subrequests via flag `cds.env.odata.max_batch_header_size` (default: 64 KiB)
- [cds@8.4.0] New OData flag `cds.env.odata.context_with_columns` that adds selected and expanded columns to `@odata.context`. Default is `false`
- [cds@8.4.0] New experimental option `--workers` to `cds watch/run/serve` that allows running a `cds.server` cluster (process env variable `WORKERS` or `CDS_WORKERS` can be used alternatively)
- [cds-mtxs@2.3.0] If extensibility is disabled, the upgrade operation now checks if extensions exist to avoid potential data loss. If intended the check can be disabled by setting `cds.requires['cds.xt.DeploymentService'].upgrade.skipExtensionCheck: true`.
- [cds-mtxs@2.3.0] Requests to Service Manager now forward the correlation ID.

### Changed ​

- [cds-dk@8.4.0] `cds init` does not put comments in JSON files within `.vscode/`.
- [cds-dk@8.4.0] `cds import --from asyncapi` now uses CloudEvents type in `@topic` annotation.
- [cds-dk@8.4.0] `cds deploy` does not fall back to the deprecated `hanatrial` service plan any more.
- [eslint-plugin-cds@3.1.1] `no-db-keywords` is no longer part of the 'recommended' rules, as the cds-compiler takes care of quoting SQL keywords, if they are used as identifiers.
- [vscode-cds@8.3.0] Visualize dependencies: no longer need to install 3rd party extension
- no longer need to show `.dot` text file first to render the graph i.e. less flickering
- removed clumsy zoom buttons. Use mouse wheel or touchpad gestures to zoom in/out, mouse drag to move

- [vscode-cds@8.3.0] Improved UI code formatter settings: better usage of horizontal space, number settings are now shown in same line
- [cds-compiler@5.4.0] Update OData vocabularies: 'Capabilities', 'Common', 'Core', 'PersonalData', 'PDF', 'UI'.
- [cds-compiler@5.4.0] to.cdl: Identifiers using non-ASCII unicode characters, as introduced in v4.4.0, are no longer quoted.
- [cds-compiler@5.4.0] For propagated expressions as annotation values, the `=` is changed as well, if it is a simple identifier.
- [cds.java@3.4.0] Removed deprecated goals `addTargetPlatform` and `addIntegrationTests` from the `cds-maven-plugin`. Both are replaced by goal `add` with corresponding feature parameter.
- [cds.java@3.4.0] Dependencies to modules with groupId `com.sap.cloud.mt` have been removed. Classes originating from these dependencies have been directly packaged into `cds-feature-mt` and other internal modules. Packages `com.sap.cloud.mt` and `com.sap.cds.mtx` have been renamed to `com.sap.cds.feature.mt` and `com.sap.cds.services.util.lib`.
- [cds.java@3.4.0] Classes `ClientCredentialJwtAccess` and `ClientCredentialJwtReader` have been deprecated.
- [cds.java@3.4.0] Minimum version of `com.sap.dwc:util-cap` library for DWC integration into CAP Java has been increased to `2.3.15`.
- [cds.java@3.4.0] Added property `cds.multiTenancy.security.internalUserAccess.enabled` to control authorization of MT lifecycle endpoints for internal users. In production profile, `internal-user` is not authorized by default anymore.
- [cds@8.4.0] For remote service calls to OData v2 services, less conversions are performed on the returned data
- [cds@8.4.0] Internal API `srv.endpoints` now always is an array of endpoint objects, an empty one if the service is not served to any protocol

### Fixed ​

- [cds-dk@8.4.0] `cds env` now colors is output honoring settings like `FORCE_COLOR`.
- [cds-dk@8.4.0] `cds add` commands correctly detect Java/Node in Microsoft PowerShell.
- [cds-dk@8.4.0] `cds add hana` doesn't add `dependencies` to `.cdsrc.json` any more.
- [cds-dk@8.4.0] `cds add cf-manifest` uses the new `sap_java_buildpack_jakarta` buildpack.
- [cds-dk@8.4.0] `cds build --production` now correctly formats console log output.
- [cds-dk@8.4.0] `cds add` correctly handles entries like `cds.requires.auth` if the following configuration is scoped in a profile.
- [cds-dk@8.4.0] `cds add` plugins can use a shortcut for their options.
- [cds-dk@8.4.0] `cds import` fix for no entity schema in OData V2.
- [eslint-plugin-cds@3.1.1] `auth-restrict-grant-service` can now handle invalid values for `@restrict`
- [eslint-plugin-cds@3.1.1] `auth-use-requires` now handles `null` values for `@restrict.grant.to`
- [eslint-plugin-cds@3.1.1] `auth-valid-restrict-to` is now more robust against invalid properties such as `__proto__` and reduces the number of false positives
- [eslint-plugin-cds@3.1.1] `auth-valid-restrict-where` now handles and reports invalid value `@restrict: [{where: null}]`
- [eslint-plugin-cds@3.1.1] `auth-no-empty-restrictions` now handles invalid value `@restrict: [null]`
- [vscode-cds@8.3.0] highlighting of CASE-statement keywords when put in their own line
- [vscode-cds@8.3.0] analysis of dependencies for certain cases
- [cds-compiler@5.4.0] compiler: Some invalid CDL snippets could crash the parser and compiler.
- [cds-compiler@5.4.0] to.edm(x): OData V2: `Core.Links` watermark annotation has a `xmlns` attribute now.
- [cds-compiler@5.4.0] for.seal: Remove unapplied extensions from CSN.
- [cds-compiler@5.4.0] to.sql.migration: Handle `ALTER COLUMN` for columns with `NOT NULL` and a default value.
- [cds-compiler@5.3.2] to.sql|hdi|hdbcds|effective: Handle subexpressions in conjunction with exists predicate.
- [cds.java@3.4.0] Fixed the messaging default error handler behaviour when receiving messages of not subscribed tenants. By default, such messages are now acknowledged (i.e. skipped) to avoid growing error queues in the messaging broker.
- [cds.java@3.3.1] Fixed a bug, causing an HTTP connection leak in health indicator `modelProvider`.
- [cds.java@3.3.1] Fixed a bug, causing `deploymentService` health indicator being enabled by default.
- [cds.java@3.3.1] Fixed a bug, causing UI provided by `cds-feature-change-tracking` to omit text for attributes of the change tracked entities when the respective field is hidden from the UI.
- [cds4j@3.4.0] Fixed a bug in code generator, causing builder interfaces to be generated with incorrect references when builders for nested inline structured types are generated.
- [cds4j@3.3.1] SAP HANA HEX mode: fixed fallback to non-hex SQL on "HEX enforced but cannot be selected" errors on HANA QRC 3/2024
- fixed SQL mode statement hints for hierarchy search queries

- [cds@8.4.0] Commands like `cds deploy` now fail with a clear error message if called with an invalid value for `cds.features.assert_integrity` (like `true`)
- [cds@8.4.0] Authentication validation errors (e.g., expired token, wrong audience) are logged as warning
- [cds@8.4.0] Requests using `$apply` will always apply implicit sorting on best effort mechanism
- [cds@8.4.0] Properly handle empty content-type in new OData adapter
- [cds@8.4.0] Error/crash with `cds.features.odata_new_parser` for requests containing `$expand=*` and `$select`, which selects individual columns and star, e.g. `$select=ID,*`
- [cds@8.4.0] Referencing new entities in `$batch` with new OData adapter did not work properly when using non integer content IDs in multipart/mixed
- [cds@8.4.0] `cds.compile.to.serviceinfo` to ignore unknown protocols
- [cds@8.4.0] New OData adapter and `cds.spawn` did not crash on programming errors (for example TypeError)
- [cds@8.3.1] Erroneous caching in `cds.validate`
- [cds@8.3.1] Precedence of request headers for `cds.context.id`
- [cds@8.3.1] For `quoted` names, overwrite `@cds.persistence.name` for drafts and localized views properly
- [cds@8.3.1] Do not use hana error code as http status code
- [cds-mtxs@2.3.0] Migration command `cds-mtx-migrate --syncTenantList` is now more robust.
- [cds-mtxs@2.3.0] `DEBUG=mtx` redacts Service Manager credentials.
- [cds-mtxs@2.3.0] When deleting a tenant HDI container, all of its service bindings are deleted – not just the ones labeled with the tenant ID.
- [cds-mtxs@2.3.0] Extension linter now checks `@mandatory` and `@readonly` more accurately.
- [cds-mtxs@2.3.0] `cds.xt.JobsService` inserts jobs and tasks in one transaction.

## September 2024 ​

### Added ​

- [cds-dk@8.3.0] `cds add mta`, `cds add helm` and `cds add cf-manifest` execute the `mvn cds:add -Dfeature CF/K8S` under the hood for Java projects.
- [cds-dk@8.3.0] `cds compile --to mermaid` now supports `mta.yaml` to generate a visualization of your deployment descriptor.
- [cds-dk@8.3.0] `cds add data` now also generates data for models imported with `cds import`.
- [cds-dk@8.3.0] `cds add data` now also supports structured types.
- [cds-dk@8.3.0] `cds deploy` now can also write its DDL statements to a separate log file with the `--out ` parameter.
- [cds-dk@8.3.0] `cds add dynatrace` is now supported for Kyma.
- [cds-dk@8.3.0] `cds import --name ...` to be used in RFC importer (`@sap/cds-rfc`).
- [cds-dk@8.3.0] `cds add cloud-logging --with-telemetry` and `cds add dynatrace` are added to the `production` profile by default and respect the `for` option.
- [cds-dk@8.2.0] `cds add dynatrace` adds configuration for Dynatrace.
- [cds-dk@8.2.0] `cds add cloud-logging` adds configuration for SAP Cloud Logging. Option `--with-telemetry` allows for configuration with telemetry.
- [cds-dk@8.2.0] `cds version` shows version information for `@cap-js/db-service`.
- [cds-dk@8.2.0] `cds add portal` now adds SAP Cloud Portal configuration for Kyma.
- [cds-dk@8.2.0] `cds add handler` allows to create handler stubs (for Java only, beta)
- [cds-dk@8.2.0] `cds init --add java --no-db` lets you create a Java project without persistent database.
- [cds-dk@8.2.0] `cds import` supports plugins.
- [cds-dk@8.2.0] `cds add containerize` now supports unified-runtime.
- [cds-dk@8.2.0] `cds add helm` now supports templating in the mountPath in the additionalVolumes.
- [cds-dk@8.2.0] Experimental support for `tsx` through `cds-tsx`.
- [cds-dk@8.2.0] `cds bind --to-app-services` now uses `vcap.name` to resolve multiple services with same type. A warning is issued in case of ambiguities.
- [cds-dk@8.2.0] `cds compile --to ord -o ` supports `.json` file extension.
- [cds-dk@8.2.0] `cds import --destination` applies destination credentials to existing service configurations.
- [eslint-plugin-cds@3.1.0] api:rules now have a `name` property, containing the rule name
- new exported property `parser`

- [eslint-plugin-cds@3.1.0] rules: there is now an `experimental` rule group, containing new rules that can be tested
- [eslint-plugin-cds@3.1.0] new experimental rules were added:`@sap/cds/sql-null-comparison`
- `@sap/cds/no-java-keywords`

- [eslint-plugin-cds@3.1.0] `auth-valid-restrict-grant` now proposes '*' when incorrect `@restrict.grant` value 'any' is used
- [vscode-cds@8.2.0] code completion for artifacts within `using` statements now also completes single name segments with complete name
- [cds-compiler@5.3.0] compiler:A warning is emitted if a string enum's values are longer than the specified length.
- ON-condition rewriting has been improved and now supports secondary associations.

- [cds-compiler@5.3.0] to.edm(x): Support optional action and function parameters in OData V4. The following rules apply:A parameter declared `not null` without default value is mandatory.
- A function parameter declared `null` without default value is mandatory.
- An action parameter declared `null` without default value is optional as it is equivalent to `@Core.OptionalParameter { DefaultValue: null }`.
- A parameter with a default value is optional and the default value is rendered as `@Core.OptionalParameter { DefaultValue:  }` regardless of its nullability.
- `@Core.OptionalParameter: true` can be used to turn a mandatory parameter into an optional parameter (especially function parameters) and to signal an unspecified default value in the API if the parameter has no default clause.
- `@Core.OptionalParameter: false` turns the creation of a `@Core.OptionalParameter: { Default: ... }` annotation off.
- A default clause or `@Core.OptionalParameter: ` have no effect on an explicit binding parameter.
- Mandatory and optional action parameters may appear in any order.
- Optional function parameters must not be followed by mandatory parameters.

- [cds-compiler@5.3.0] to.edm: Forward `@OpenAPI {...}` into EDM Json with option `--odata-openapi-hints`.
- [cds-compiler@5.3.0] cdsc: Option `--transitive-localized-views` was added.
- [cds.java@3.3.0] Introduced a new health indicator `modelProvider` to include the health status of MTX sidecar into the application's `/actuator/health` endpoint.
- [cds.java@3.3.0] Introduced a new setting `strictSetters` for the `generate` goal of the CDS Maven Plugin. This enables stricter type-safe setters for data access interfaces, instead of using a plain `Map` type.
- [cds.java@3.3.0] OData V4 protocol adapter now supports parameter aliases for entity keys.
- [cds.java@3.3.0] OData V4 protocol adapter now supports parameter aliases for function calls.
- [cds.java@3.3.0] New property `cds.odata-v4.fiori-preview.ui5.version` allows to configure the UI5 version used by the Fiori Preview.
- [cds.java@3.2.0] The goal `add` of the `cds-maven-plugin` supports adding CloudFoundry / Kubernetes support and health checks to a CAP Java project.
- [cds.java@3.2.0] The goal `generate` of the `cds-maven-plugin` supports generation of template handlers for actions and functions from the CDS models.
- [cds.java@3.2.0] `TenantProviderService.readTenantsInfo` now accepts a set of strings that filters the fields of the retrieved `TenantInfo` objects. This helps to reduce memory consumption when there is a large number of subscribed tenants.
- [cds.java@3.2.0] OData V4 PATCH or PUT requests now handle `If-Match: *` and `If-None-Match: *`, allowing to enforce a strict update respectively insert behaviour instead of the default upsert behaviour.
- [cds.java@3.2.0] The goal `add` of the `cds-maven-plugin` supports adding application logging to a CAP Java project.
- [cds.java@3.2.0] Deep authorizations now support conditions with paths involving associations in `@restrict` predicates.
- [cds.java@3.2.0] Support OData hierarchical requests, using `com.sap.vocabularies.Hierarchy.v1.TopLevels`, `ancestors`, `descendants` transformations. The feature is supported only on SAP HANA and needs to be enabled by setting `cds.query.hierarchy.enabled` to `true`.
- [cds.java@3.2.0] Support `null` values for collection-typed arguments for OData V4 as arguments for actions and functions.
- [cds4j@3.3.0] Support predicates comparing managed to-one associations with structured target key values
- [cds4j@3.3.0] `@cds.java.name` can be used as alias with lower priority in all places where `@cds.java.this.name` is supported
- [cds@8.3.0] `cds.deploy` can now also write its DDL statements to a separate log
- [cds@8.3.0] Symlinks are followed in `cds test`
- [cds-mtxs@2.2.0] `PUT /-/cds/saas-provisioning/tenant` and `POST /-/cds/saas-provisioning/subscribe` accept additional environment variables to the HDI deployment via the generic options `_`, e. g. additional `VCAP_SERVICES`:jsonc

```
"_": {
  "hdi": {
    "deployEnv": {
      "VCAP_SERVICES": { ... },
      "SOMETHING_ELSE": "something"
    },
    ...
  }
}
```

### Changed ​

- [cds-dk@8.3.0] `cds add sample` now uses `@ui5/cli` version 4.
- [cds-dk@8.3.0] `cds import` now throws a warning for OpenAPI files containing recursive data types.
- [cds-dk@8.2.0] `cds add hana` writes configuration for `cds build/compile` to no longer produce native SAP HANA associations. This improves deployment performance, but has a one-time performance penalty (in the next deployment).
- [cds-dk@8.2.0] `cds login` prints shorter messages about refresh tokens.
- [cds-dk@8.2.0] `cds init` uses latest Maven Java archetype version 3.2.0 for creating Java projects.
- [vscode-cds@8.2.0] hover and completion proposal details now show artifact kind
- [vscode-cds@8.2.0] Minimum VSCode version is now 1.90.2
- [cds.java@3.2.0] Reading inactive instances of draft-enabled entities no longer issues data access events to the audit log.
- [cds.java@2.10.4] Reading inactive instances of draft-enabled entities no longer issues data access events to the audit log.
- [cds4j@3.3.0] Copy Select w/ modifier: when replacing element refs on the select list with non-ref values, the ref's display name is now propagated as alias to `Modifier::selectListValue`
- [cds@8.3.0] Unknown protocols in `@protocol` annotations formerly prevented server starts; they are merely ignored now with a warning in the logs.
- [cds@8.3.0] Deprecated configuration flag `cds.env.features.keys_in_data_compat` because of incompatibility with data validation in new OData adapter.
- [cds@8.3.0] `@cds.api.ignore` doesn't suppress an association, the annotation is propagated to the (generated) foreign keys.
- [cds@8.3.0] Where clauses of restrictions for bound actions and functions defined by `@restrict` are now enforced and no longer ignored.
- [cds@8.3.0] `@cap-js/telemetry` is now loaded before other plugins to allow better instrumentation.
- [cds@8.2.3] All annotations in input data are skipped and removed from the input by `cds.validate()` - as we did in legacy OData adapter
- [cds-mtxs@2.2.0] HANA deployments without `resources.tgz` will now skip the deployment instead of failing with an error.
- [cds-mtxs@2.2.0] Debug logs for HANA deployments can be set using `DEBUG=deploy`.
- [cds-mtxs@2.2.0] The error about an invalid scope when fetching a token now contains the expected scope.
- [cds-mtxs@2.2.0] Logs for enqueued jobs are not colored in non-TTY environments any more.

### Fixed ​

- [cds-dk@8.3.0] `cds add workzone`-created apps can now directly be added via Content Manager in SAP Build Work Zone.
- [cds-dk@8.3.0] Less obtrusive warning about `cds` instead of `cds-ts` in Typescript projects.
- [cds-dk@8.2.3] In `cds.cli.command`, commands now show up in the correct case.
- [cds-dk@8.2.3] `cds add` plugins don't throw a `TypeError` if `cds.cli.options` is `undefined`.
- [cds-dk@8.2.3] `cds watch` no longer ignores `*git/` folders, but only `.git/`.
- [cds-dk@8.2.3] `cds import` updates `package.json` file in `srv` folder if existing. The `srv` folder name is determined by `cds.env.folders.srv` config or parameter `--out`.
- [cds-dk@8.2.3] `cds import` doesn't change existing service configuration data. Now, `destination` credentials are only saved for the `production` profile.
- [cds-dk@8.2.2] BDSA-2024-6188: vulnerability with express.js 4.19.2
- [cds-dk@8.2.2] `cds import --out` copies the given metadata file to the correct output folder. CLI options are propagated to the `cds.import` API.
- [cds-dk@8.2.2] `cds add sample` no longer creates a irregular whitespace in `admin-service.js`.
- [cds-dk@8.2.2] `cds login` now correctly fetches tokens again with client credentials (or hints at invalid credentials).
- [cds-dk@8.2.2] `cds add handler` can now also be called from the `srv` dir.
- [cds-dk@8.2.1] Update `@sap/hdi-deploy` to fix CVE-2024-4067 with `micromatch` 4.0.7
- [cds-dk@8.2.1] `cds add` plugins now correctly parse flags (options with `type: 'boolean'`) if not used as the last argument.
- [cds-dk@8.2.0] `cds import` fix for single entity schema in OData V2.
- [cds-dk@8.2.0] `cds add portal` correctly sets the `appId` in its `CommonDataModel.json` from the `manifest.json` app ID.
- [cds-dk@8.2.0] `cds add html5-repo` adds the SAP BTP Destination service as a hard dependency again for Kyma projects.
- [cds-dk@8.2.0] `cds build --ws-pack` correctly creates tarball archives for workspaces with nested `node_modules` folders.
- [cds-dk@8.2.0] `cds import` now shows proper error message in case of bound action collision.
- [cds-dk@8.2.0] `cds deploy --to hana` now runs an existing `hana` build task configuration instead of a default one.
- [cds-dk@7.9.8] BDSA-2024-6188: vulnerability with express.js 4.19.2
- [eslint-plugin-cds@3.1.0] cli: Running `eslint` on the command line now runs `inferred` rules again
- [eslint-plugin-cds@3.1.0] `start-entities-uppercase` no longer reports false positives for elements
- [eslint-plugin-cds@3.1.0] Typescript errors in `lib/types.d.ts` were fixed
- [eslint-plugin-cds@3.1.0] Rule property `hasSuggestions: true` was removed from rules that did not have suggestions
- [eslint-plugin-cds@3.1.0] Custom rule tests using `runRuleTester` did not catch errors in files inside `valid/`. Tests can now also be run with other test runners such as `mocha` and `node --test` instead of just `jest`
- [eslint-plugin-cds@3.1.0] `auth-` lint rules have been reworked to reduce the number of false positives and negatives `auth-valid-restrict-where` no longer runs in quadratic time and now handles "expressions as annotation values"
- `auth-no-empty-restrictions` now runs for actions and functions, too
- `auth-use-requires` will not propose `@requires` anymore, if the `@restrict` has a `where` condition
- `auth-valid-restrict-grants` incorrectly proposed to use `WRITE` instead of other events; it no longer crashes for invalid value types and now runs on all CSN artifacts
- `auth-valid-restrict-keys` has improved reporting about misspelled vs unknown properties; it now runs on all CSN artifacts

- [eslint-plugin-cds@3.0.5] Inferred rules did not run when executed via `eslint` or `cds lint`.
- [vscode-cds@8.2.0] highlighting of element names in annotate statements and of special element names `entity`, `type`, `event`
- [vscode-cds@8.2.0] completion: rename of source folders led to wrong using path proposals
- [vscode-cds@8.2.0] completion: using path proposals did not work in multi-line using statements
- [vscode-cds@8.2.0] maintain translation quickfix sent wrong document version
- [cds-compiler@5.3.0] CDL parser: Issue warning if annotation assignments have been written at an invalid position inside a type expressions.
- [cds-compiler@5.3.0] CDL parser: Issue warning for arrayed parameter with default value.
- [cds-compiler@5.3.0] to.cdl: Arrayed parameters with default values were not rendered correctly.
- [cds.java@3.3.0] Fixed a bug, causing excessive serialization of elements of complex type not present in the payload returned via OData action/function import.
- [cds.java@3.3.0] Fixed a bug, preventing OData V4 parser to correctly parse entities, actions or functions with the elements or the arguments of types defined within the CDS services.
- [cds.java@3.3.0] Fixed a bug, causing redundant change log entries being generated for changed localized elements.
- [cds.java@3.3.0] Fixed a bug, causing translated values depending on user locale to appear in values for identifiers for change log entries.
- [cds.java@3.2.0] Fixed a bug, causing audit log implementation to fail with `NullPointerException` when processing the associations with elements relevant to Audit Logging.
- [cds.java@3.2.0] Fixed a bug, causing failed unsubscriptions triggered by Subscription Manager Service in a Deploy with Confidence context.
- [cds.java@3.2.0] Fixed a bug, causing incorrect EDMX being returned by the `$metadata` endpoint when special characters are used in the I18N texts.
- [cds.java@3.2.0] Fixed a bug, causing `ErrorStatusException` being thrown when auditing accesses to inactive instances of draft-enabled entities.
- [cds.java@3.2.0] Fixed a bug, causing failing requests to `/cds` actuator when one of the internal contributors throws an exception.
- [cds.java@3.2.0] Fixed an incompatible change, causing applications with multiple xsuaa bindings to fail on startup due to missing XSUAA configuration for secondary bindings. These applications now can set `cds.security.xsuaa.allowMultipleBinding` to `true` so that all xsuaa bindings are available in custom spring auto-configurations. Note: CAP Java still does not process multiple bindings and requires a dedicated spring configuration. In general, applications should refrain from configuring several XSUAA bindings.
- [cds.java@2.10.4] Fixed a bug, causing audit log implementation to fail with `NullPointerException` when processing the associations with elements relevant to Audit Logging.
- [cds.java@2.10.4] Fixed a bug, causing incorrect EDMX being returned by the `$metadata` endpoint when special characters are used in the I18N texts.
- [cds.java@2.10.4] Fixed a bug, causing `ErrorStatusException` being thrown when auditing accesses to inactive instances of draft-enabled entities.
- [cds.java@2.10.4] Fixed a bug, causing failing requests to `/cds` actuator when one of the internal contributors throws an exception.
- [cds4j@3.3.0] Fixed a bug, causing SQL exceptions when processing deep updates from flattened runtime views
- [cds4j@3.3.0] Fixed a bug in code generator leading to missing annotations `@CdsName` on setters and getters in FLUENT mode.
- [cds4j@3.3.0] Fixed a bug causing database implementations to fail to load in ForkJoinPool threads
- [cds4j@3.3.0] Fixed a bug in $apply processing causing filter preceding a filter by grouped values to be ignored
- [cds4j@3.3.0] Fixed bugs in code generator: [cds4j@3.3.0] leading to incorrect interfaces being generated for entities annotated with the `@cds.java.extends` naming entities that contain inline types.
- [cds4j@3.3.0] causing builder interfaces for global structured types to be omitted.
- [cds4j@3.3.0] leading to missing annotations `@CdsName` on setters and getters in FLUENT mode.

- [cds4j@3.3.0] Fixed inline count for queries which use top 0
- [cds4j@2.10.4] Skip updates with empty entries
- [cds4j@2.10.4] Fixed a bug, causing `Cds4jServiceLoader` failing to load certain classes when used in asynchronous code
- [cds@8.3.0] When modifying active children of of draft-enabled entities directly (`bypass_draft`), the error message was misleading.
- [cds@8.3.0] Cleaning up drafts calls `CANCEL` handlers
- [cds@8.3.0] Allow to call `CANCEL` on draft entities programmatically
- [cds@8.3.0] Encoding of `@odata.nextLink` path
- [cds@8.3.0] Computed fields are ignored in projections
- [cds@8.3.0] Consider `id` in a `ref` step for mapping of service elements to their name on the db.
- [cds@8.3.0] Feature toggles with new OData adapter.
- [cds@8.3.0] Target entity was incorrectly calculated for some actions in new OData adapter.
- [cds@8.3.0] `req.diff()` does not manipulate existing queries anymore.
- [cds@8.3.0] New OData adapter: normalize on commit error in `/$batch`
- [cds@8.2.3] Unmanaged associations are excluded from `@mandatory` checks
- [cds@8.2.3] Properly reject direct requests to `DraftAdministrativeData`
- [cds@8.2.3] Virtual elements annotated with `@Core.MediaType`
- [cds@8.2.3] OData Requests targeting a specific instance and custom handler returns empty array
- [cds@8.2.3] `cds-serve` and `cds-deploy` now set `cds.cli` information
- [cds@8.2.2] Erroneous caching in `cds.validate`
- [cds@8.2.2] Properly check `$filter` element types across navigations
- [cds@8.2.1] Date validation of legacy OData protocol adapter
- [cds@8.2.1] Content-Length headers in multipart batch request body
- [cds@8.2.1] Streaming requests with virtual properties
- [cds@8.2.1] Bring back support for `x-correlationid`
- [cds@8.2.1] Validation of inlined elements
- [cds@8.2.1] multipart `$batch` parsing with -- as part of payload
- [cds-mtxs@2.2.0] `/-/cds/saas-provisioning/dependencies` show a better error message when it can't resolve its configured SaaS dependencies.
- [cds-mtxs@2.2.0] The Service Manager client re-fetches the authorization token on retries.
- [cds-mtxs@2.2.0] Better error handling in `cds.xt.JobsService`.

### Removed ​

- [cds-dk@8.2.0] Removed `build` and `build:ts` npm scripts that were generated into `package.json` when adding the `typescript` facet.
- [eslint-plugin-cds@3.1.0] api: `genDocs` was removed
- [cds@8.3.0] Alpha support for SAP Event Broker-based messaging (kind `event-broker`). Use CDS plugin `@cap-js/event-broker` instead.

## August 2024 ​

### Added ​

- [cds-dk@8.1.1] Add more features to CAP project creation wizard in SAP Business Application Studio.
- [cds-dk@8.1.1] `cds.add.merge` now you specify a `key` in its `deletions` semantics.
- [vscode-cds@8.0.2] Mermaid: add option for layout direction
- [cds-compiler@5.2.0] to.edm(x): Add `@Core.Links { rel: 'author', href: 'https://cap.cloud.sap' };` as watermark to lead schema.
- [cds-compiler@5.2.0] to.sql.migration: Introduce option `script` to aid in generation of manual migration scripts by not aborting when encountering lossy changes.
- [cds4j@3.2.0] SAP HANA: Support to resolve and normalize queries, that use hierarchy transformations: `CqnTopLevelsTransformation`, `CqnDescendantsTransformation`, `CqnAncestorsTransformation`
- Use `SCORE` function to search hierarchies in HEX mode

- [cds4j@3.2.0] Extended support for runtime views
- [cds@8.2.0] Allow `cds.connect.to (SomeService)` where `SomeService` is a class
- [cds@8.2.0] Lean draft: support CDS orderBy in `list status: all`
- [cds@8.2.0] Support where not in as object in `cds.ql` expressions like: `where({ID:{not:{in:[...]}}})`
- [cds@8.2.0] Unbound CDS functions now show up in the server's index page along with an exemplary call signature
- [cds@8.2.0] `cds.log`'s JSON formatter: Field `w3c_traceparent` is filled based on request header `traceparent` (cf. W3C Trace Context) for improved correlation
- Custom fields `cds.env.log.cls_custom_fields` are filled if bound to an instance of SAP Cloud Logging
- Default `cds.env.log.als_custom_fields` enhanced by `{ reason: 3 }` (project config takes precedence)

- [cds@8.2.0] Support for `cds.hana` types like `cds.hana.ST_POINT` in `cds.builtin`
- [cds@8.2.0] Internal `cds.debug()` API now always returns a logger instance, which allows switching on debugging subsequently, e.g. by the like of `cds.log('sql','debug')`
- [cds@8.2.0] New config flag `cds.server.shutdown_on_uncaught_errors` allows to control whether the server should shut down on uncaught errors. Default is `true`

### Changed ​

- [cds-dk@8.2.0] `cds add hana` writes configuration for `cds build/compile` to no longer produce native SAP HANA associations. This improves deployment performance, but has a one-time performance penalty (in the next deployment).
- [cds-dk@8.2.0] `cds login` prints shorter messages about refresh tokens.
- [cds-dk@8.2.0] `cds init` uses latest Maven Java archetype version 3.2.0 for creating Java projects.
- [cds-dk@8.1.1] `cds init` uses latest Maven Java archetype version 3.1.0 for creating Java projects.
- [cds-compiler@5.2.0] for.odata: No longer reject default values on action/function parameters.
- [cds-compiler@5.2.0] to.edm(x): Raise warning for default values on action/function parameters that they are ignored.
- [cds@8.2.0] Revert workaround from 8.1.0 for server startup message `WARNING: Package '@sap/cds' was loaded from different installations`. This is now addressed in `@sap/cds-mtxs` 2.0.5.
- [cds@8.2.0] When parsing CSV files, `cds.deploy` no longer doubles a literal `\` character (backslash) with a second backslash (`\\`), but retains it as-is. This caused unwanted data changes.
- [cds@8.2.0] Optimized handling of large binaries (BLOBs) in case of drafts. Unchanged BLOBs are not copied into the draft entity. If those BLOBs from draft entities are requested, the unchanged BLOBs will be fetched from the corresponding active entity. Note that this change may require adjustment of custom logic, if large binaries from draft entities are requested (for example, using `ql.SELECT` statement). To restore previous behavior use `cds.features.binary_draft_compat`.

### Fixed ​

- [cds-dk@8.2.0] `cds import` fix for single entity schema in OData V2.
- [cds-dk@8.2.0] `cds add portal` correctly sets the `appId` in its `CommonDataModel.json` from the `manifest.json` app ID.
- [cds-dk@8.2.0] `cds add html5-repo` adds the SAP BTP Destination service as a hard dependency again for Kyma projects.
- [cds-dk@8.2.0] `cds build --ws-pack` correctly creates tarball archives for workspaces with nested `node_modules` folders.
- [cds-dk@8.2.0] `cds import` now shows proper error message in case of bound action collision.
- [cds-dk@8.2.0] `cds deploy --to hana` now runs an existing `hana` build task configuration instead of a default one.
- [cds-dk@8.1.2] Dependency update for `axios` to fix CVE-2024-39338.
- [cds-dk@8.1.2] `cds login` now fetches the passcode URL for the subscriber tenant if the subdomain is given.
- [cds-dk@8.1.2] `cds build` now correctly generates migration tables for `CodeList` entities.
- [cds-dk@8.1.1] `cds import` now gives proper error message for OData import in case of invalid OData version or invalid encoding.
- [cds-dk@8.1.1] `cds import` now able to ignore invalid escape sequence in the description of properties for OData V2.
- [cds-dk@8.1.1] `cds add mta` does not error when the `app/router` folder was deleted.
- [cds-dk@8.1.1] `cds version -i` does not show a globally installed version when none is installed or linked.
- [cds-dk@8.1.1] `cds compile --to openapi` no longer fails with `Error: Unknown protocol: graphql`.
- [cds-dk@8.1.1] `cds add data` can now correctly handle circular dependencies in entities that point to themselves via associations and compositions.
- [cds-dk@8.1.1] `cds add` returns correct suggestions for shell completion.
- [cds-dk@8.1.1] `cds version` reports correct `@sap/cds-compiler` version.
- [cds-dk@8.1.1] `cds deploy` falls back correctly to `@sap/hana-client` when `HDI_DEPLOY_OPTIONS='{"use_hdb":false}'` is set.
- [cds-dk@7.9.7] Dependency update for `axios` to fix CVE-2024-39338
- [cds-dk@7.9.7] `cds build --for mtx-sidecar` now correctly supports different `srv` folder name.
- [cds-dk@7.9.7] `cds build --ws-pack` correctly creates tarball archives for workspaces with nested `node_modules` folders.
- [cds-dk@7.9.7] `cds version` now reports the correct version of `@sap/cds` if this one is installed locally along with a local `@sap/cds-dk` installation.
- [cds-dk@7.9.7] `cds version -i` does not show a globally installed version when none is installed or linked.
- [cds-dk@7.9.7] `cds version` reports correct `@sap/cds-compiler` version.
- [cds-dk@7.9.7] `cds version` can skip over check for Java version
- [cds-compiler@5.2.0] compiler: Fix extensions with bound actions using an explicit binding parameter in `parseCdl` CSN.
- [cds-compiler@5.2.0] for.odata, to.edm(x): Fix some issues with resolving annotation expressions in nested objects and reliably replace value of `=` attribute with `true` after processing.
- [cds-compiler@5.1.2] compiler: In parseCdl mode, bound actions specifying the binding parameter with `$self` did not work.
- [cds.java@3.2.0] Fixed a bug, causing audit log implementation to fail with `NullPointerException` when processing the associations with elements relevant to Audit Logging.
- [cds.java@3.2.0] Fixed a bug, causing failed unsubscriptions triggered by Subscription Manager Service in a Deploy with Confidence context.
- [cds.java@3.2.0] Fixed a bug, causing incorrect EDMX being returned by the `$metadata` endpoint when special characters are used in the I18N texts.
- [cds.java@3.2.0] Fixed a bug, causing `ErrorStatusException` being thrown when auditing accesses to inactive instances of draft-enabled entities.
- [cds.java@3.2.0] Fixed a bug, causing failing requests to `/cds` actuator when one of the internal contributors throws an exception.
- [cds.java@3.2.0] Fixed an incompatible change, causing applications with multiple XSUAA bindings to fail on startup due to missing XSUAA configuration for secondary bindings. These applications now can set `cds.security.xsuaa.allowMultipleBinding` to `true` so that all XSUAA bindings are available in custom spring auto-configurations. Note: CAP Java still does not process multiple bindings and requires a dedicated spring configuration. In general, applications should refrain from configuring several XSUAA bindings.
- [cds.java@3.1.1] Fixed a bug, causing runtime exceptions when loading I18n data from MTXS sidecar running with @sap/cds >= `8.1.0`.
- [cds.java@3.0.2] Fixed a bug, causing runtime exceptions when loading I18n data from MTXS sidecar running with @sap/cds >= `8.1.0`.
- [cds4j@3.2.0] Consider expand ref filter in optimized parent-key expands
- [cds4j@3.2.0] Fix usage of context variables in match predicates
- [cds4j@3.2.0] Fix handling of external imported draft entities when parsing the CDS model
- [cds4j@3.2.0] Fixed a bug, causing `Cds4jServiceLoader` to fail to load certain classes inside asynchronous code
- [cds4j@3.2.0] Consider `@cds.search` in select from subquery
- [cds@8.2.0] Resolving views with path expression renamings
- [cds@8.2.0] Set content-type-header in batch for actions with 204 No Content
- [cds@8.2.0] URI encoding of `@odata.nextLink` in OData response
- [cds@8.2.0] Requests reading media data streams did not provide `req.params`
- [cds@8.2.0] `cds.compile.to.hana` for legacy hana service with `@cap-js/sqlite` as dev dependency
- [cds@8.2.0] Better redaction of debug output
- [cds@8.2.0] Instance-based authorization using functions
- [cds@8.2.0] Fixed flaws in `cds.connect.to()` that lead to deadlocks in case of errors due to invalid service configurations or initializations.
- [cds@8.2.0] Navigation with backlink as key can now omit backlink keys for new OData adapter
- [cds@8.1.1] For `accept-language`, ignore additional options
- [cds@8.1.1] Global `describe`, `before`, `beforeAll`, `afterAll` hooks are now writable again. They were accidentally made read-only in 8.0.0.
- [cds@8.1.1] Expand to `DraftAdministrativeData` for active instances of draft-enabled entities over drafts
- [cds@8.1.1] Deduplication of columns for certain on conditions for the legacy database driver
- [cds@8.1.1] For legacy-sqlite/-hana: Add keys to expands with only non-key elements to ensure not returning null for expand.
- [cds@8.1.1] New parser was to restrictive regarding an empty line at the end of batch body.
- [cds@8.1.1] Error target for operations with complex parameters
- [cds@8.1.1] Remote services: JWT gets found in authorization header
- [cds@8.1.1] Search with invalid characters
- [cds@8.1.1] Invoke `srv.on('error')` for each failing batch subrequest
- [cds-mtxs@2.1.0] On-the-fly CSN calculations are only done with `extensibility: true` in the main app.
- [cds-mtxs@2.1.0] The request correlation ID is appended to generic HDI deployment error messages.
- [cds-mtxs@2.1.0] Asynchronous extension activation now reverts faulty extensions correctly.
- [cds-mtxs@2.1.0] Parallel extension activation calls do no longer create inconsistent extension states.
- [cds-mtxs@2.0.6] Subscription Manager service subscriptions are now working again.
- [cds-mtxs@2.0.6] The `cds.features.assertIntegrity` is correctly added to the compiler options for HANA builds.
- [cds-mtxs@2.0.6] The job status now always returns a non-null value also when using `@cap-js/hana`.
- [cds-mtxs@2.0.6] The passcode URL now reflects the subscriber subdomain, if such is received from the client.
- [cds-mtxs@2.0.5] The server startup no longer yields the `WARNING: Package '@sap/cds' was loaded from different installations:` message in PNPM setups with `--global-bin-dir` on. This happened in BAS, for example on `cds watch/serve` etc.
- [cds-mtxs@2.0.5] Setting `HDI_DEPLOY_OPTIONS` to `'{"use_hdb": false}'` now works correctly for `@sap/hana-client` fallbacks.

### Removed ​

- [cds-dk@8.2.0] Removed `build` and `build:ts` npm scripts that were generated into `package.json` when adding the `typescript` facet.
- [cds@8.2.0] Array methods `forEach`, `filter`, `find`, `map`, `some`, `every` from `LinkedDefinitions`. Convert linked definitions into arrays before using these methods, for example:js

```
[...linked.definitions].map(d => d.name)
```

## July 2024 ​

### Added ​

- [cds-dk@8.1.0] `cds compile --to mermaid` can be configured with a layout direction like `LR`.
- [cds-dk@8.1.0] `cds deploy --to hana` now shows the `hdi-deploy` version when running.
- [cds-compiler@5.1.0] cdsc: Option `--stdin` was added to support input via standard input, for example, `cat file.cds | cdsc --stdin`
- [cds-compiler@5.1.0] Allow to refer to draft state element `IsActiveEntity` via magic variable `$draft.IsActiveEntity` in annotation path expressions. for.odata: During draft augmentation, `$draft.IsActiveEntity` is rewritten to `$self.IsActiveEntity` for all draft-enabled entities (root and sub-nodes but not for named types or entity parameters).
- to.edm(x): (V4 only) Allow to refer to an entity element in a bound action via `$self` and not only via explicit binding parameter in an annotation path expression. The API generator will prefix the path with the actual binding parameter name (explicit, annotation or default).

- [cds.java@3.0.1] Added switch `cds.multiTenancy.serviceManager.acceptInstancesWithoutTenant.enabled` (default: false) to allow reading tenant labels also from HDI container bindings in case the underlying HDI service instance is missing the label due to a data inconsistency. You may use this switch to temporarily activate the work-around for the broken service instances, but you should manually patch the instances with the correct tenant label as soon as possible via the ServiceManager API.
- [cds.java@2.10.3] Added switch `cds.multiTenancy.serviceManager.acceptInstancesWithoutTenant.enabled` (default: false) to allow reading tenant labels also from HDI container bindings in case the underlying HDI service instance is missing the label due to a data inconsistency. You may use this switch to temporarily activate the work-around for the broken service instances, but you should manually patch the instances with the correct tenant label as soon as possible via the ServiceManager API.
- [cds4j@3.1.0] `@Search.ranking` annotation to define the ranking weight for an element ('HIGH' = 1.0, 'MEDIUM' = 0.7, 'LOW' = 0.5).
- [cds@8.1.0] Streaming of data with content type 'application/json'
- [cds@8.1.0] Service annotation `@cds.server.body_parser.limit` and global config option `cds.server.body_parser.limit` allow to configure the maximum request body size in bytes. The default value by express' body parser middleware is 100 kb. See express docs for details.
- [cds@8.1.0] Translations for new languages: bg (Bulgarian), el (Greek), he (Hebrew), hr (Croatian), kk (Kazakh), sk (Slovak), sl (Slovenian), sr (Serbian), uk (Ukrainian)

### Changed ​

- [cds-dk@8.1.0] Better generation of http files with `cds add http`, especially for draft requests.
- [cds-compiler@5.1.0] Update OData vocabularies: 'Common', 'Core', 'HTML5', 'UI'.
- [cds-compiler@5.1.0] to.cdl|hdbcds|hdi|sql: Remove `generated by` comment.
- [cds.java@3.0.1] Deep authorizations are not enabled by default (`cds.security.authorization.deep.enabled: false`)
- [cds@8.1.0] Event Broker: Standardize behavior for cloud events and header propagation

### Fixed ​

- [cds-dk@8.1.0] `cds add` recognizes `hasCfManifest` as inactive unless a `manifest.yml` file exists.
- [cds-dk@8.1.0] `cds add` help and suggestions are only shown when the `help` method is implemented.
- [cds-dk@8.1.0] `cds add sample` does not include the deprecated `synchronizationMode` property in `manifest.json` files anymore.
- [cds-dk@8.1.0] `cds compile --to mermaid` no longer produces empty `namespace` blocks that would lead to rendering errors.
- [cds-dk@8.1.0] `cds compile --to mermaid` no longer fails for complex queries like joins.
- [cds-dk@8.1.0] `cds build --for mtx-sidecar` now correctly supports different `srv` folder name.
- [cds-dk@8.1.0] `cds add audit-log` in combination with `cds add multitenancy` correctly adds the audit-log dependency to the MTX sidecar.
- [cds-dk@8.1.0] `cds build` adds the correct hdbtabledata file paths to the hana result set.
- [cds-dk@8.1.0] `cds add` plugins can now correctly interpret `cds.cli` properties.
- [cds-dk@8.1.0] `cds deploy --to hana --dry` now shows correct files with their content.
- [cds-dk@8.1.0] `cds version` now reports the correct version of `@sap/cds` if this one is installed locally along with a local `@sap/cds-dk` installation.
- [cds-dk@8.1.0] Shell completion now works correctly for `cds init --add`.
- [cds-dk@8.1.0] `cds build --for mtx-sidecar` no longer fails if the severity of a compilation error has been downgraded from `Error` to `Warning`.
- [cds-dk@8.0.3] `cds build --ws` no longer creates migration tables in shared db if already existing in a workspace.
- [cds-dk@8.0.3] `cds add destination` adds the destination service as an MTX SaaS dependency.
- [cds-dk@8.0.3] `cds add html5-repo` adds the HTML5 repo runtime as an MTX SaaS dependency.
- [cds-dk@8.0.3] `cds add html5-repo` does not add a destination service anymore if not required by other services.
- [cds-dk@8.0.3] `cds add workzone` runs `cds add destination` as a dependent facet.
- [cds-dk@8.0.3] `cds add` plugins don't fail if custom options are provided via the `options` API.
- [cds-dk@8.0.3] `cds add data` can now correctly handle circular associations. The maximum depth of associations is increased to 5.
- [cds-dk@8.0.3] `cds add redis` is separated from `cds add redis-messaging` to allow for separate consumption.
- [cds-dk@8.0.3] `cds add redis` uses the `standard` service plan by default.
- [cds-dk@8.0.3] `cds watch` no longer leads to a warning `'@sap/cds' was loaded from different installations` when local project dependencies are installed.
- [cds-dk@8.0.3] `cds init` uses latest Maven Java archetype version 3.0.0 for creating Java projects.
- [cds-dk@7.9.6] `cds add data` can now correctly handle circular associations. The maximum depth of associations is increased to 5.
- [cds-compiler@5.1.0] compiler: checks for associations now work for nested projections of the form `association.{ id }`
- [cds-compiler@5.1.0] to.edm(x): No `Nullable` attribute for `$ReturnType` of `Collection()` OData V4 CSDL, section 12.8 Return Type
- [cds-compiler@5.1.0] to.sql|hdi|hdbcds: Detect and error on "cross-eyed" backlinks, where we cannot construct a valid on-condition.
- [cds-compiler@5.1.0] to.sql|hdi.migration: Correctly detect that a view was dropped - this was previously just silently ignored.
- [cds-compiler@4.9.8] compiler: Fix extensions with bound actions using an explicit binding parameter in `parseCdl` CSN.
- [cds-compiler@4.9.8] to.edm(x): No `Nullable` attribute for `$ReturnType` of `Collection()` OData V4 CSDL, section 12.8 Return Type
- [cds.java@3.0.1] Fixed a bug in `cds-feature-postgresql` which caused a connection issue to a PostgreSQL database due to an invalid CA certificate.
- [cds.java@2.10.3] Fixed a bug in `cds-feature-postgresql` which caused a connection issue to a PostgreSQL database due to an invalid CA certificate.
- [cds4j@3.1.0] Support nested select with inline count
- [cds4j@3.1.0] Setting session context variables is no longer implicitly assumed to have a surrounding transaction
- [cds4j@3.1.0] Skip updates with empty entries
- [cds@8.1.0] Erroneous authentication of `enterprise-messaging`
- [cds@8.1.0] `@odata.context` for actions/functions returning an array of ``
- [cds@8.1.0] `cds-deploy` script terminates if deployment fails
- [cds@8.1.0] Allow backslashes, quotation marks and ampersands in search terms
- [cds@8.1.0] Search compatibility for new parser and old db
- [cds@8.1.0] The server startup no longer yields the `WARNING: Package '@sap/cds' was loaded from different installations:` message in PNPM setups using `--global-bin-dir`. This happened in BAS, for example on `cds watch/serve`
- [cds@8.0.4] Localized views like `localized_de_Books` where accidentally generated for new sqlite service.
- [cds@8.0.4] Atomicity group handling in `$batch`
- [cds@8.0.4] `$batch` in combination with `commit` hooks
- [cds@8.0.4] `continue-on-error` preference for JSON `$batch`
- [cds@7.9.4] View resolving for `cds.features.lean_draft`
- [cds@7.9.4] Error in the `enterprise-messaging` deploy script
- [cds@7.9.4] Properly forward path expression in front of lambda functions for `odata-v2` remote services
- [cds@7.9.4] OData queries selecting the same column with `$count=true`
- [cds@7.9.4] Closed higher end of version range for dependency on `cds-types`

## June 2024 ​

### Added ​

- [cds-dk@8.0.2] `cds add malware-scanner` adds configurations for `SAP Malware Scanning service`.
- [cds-dk@8.0.1] `cds add hana` and `cds build` now support the SAP HANA artifact type `.hdbeshconfig` required for enterprise search integration.
- [cds-dk@8.0.1] `cds init` adds simplistic `eslint.config.mjs` file to newly created projects.
- [cds-dk@8.0.1] Running any `cds` command in a TypeScript project will print a hint to `cds-ts`.
- [cds-dk@8.0.1] The `cds.build.Plugin` class now supports a `baseModel()` method that returns a CSN that doesn't include features when feature toggles are enabled.
- [cds-dk@8.0.1] `cds add workzone` adds support for SAP BTP Work Zone, Standard Edition.
- [cds-dk@8.0.1] `cds add helm` now supports using external destinations in `backendDestinations` key.
- [cds-dk@8.0.1] `cds add` supports the `--java:mvn` option.
- [cds-dk@8.0.0] `cds init --add` now also allows the shortcut `cds init -a`.
- [cds-dk@8.0.0] `cds add audit-logging` adds configuration for `@cap-js/audit-logging`.
- [cds-dk@8.0.0] `cds add typescript` initializes a bare CDS project with TypeScript nature.
- [cds-dk@8.0.0] `cds add containerize` generates `containerize.yaml` file with configuration required to build the container images by `ctz` CLI.
- [cds-dk@8.0.0] Setting `FORCE_COLOR=1` will now force colored log output.
- [cds-dk@8.0.0] `cds add --package/-p` allows you to specify remote packages (in `npm add` format).
- [cds-dk@8.0.0] `cds add helm` asks prompts to fill in data at first execution.
- [cds-dk@8.0.0] `cds add http` can now generate requests for entities annotated with `odata.draft.enabled`.
- [cds-dk@8.0.0] `cds import` will now support references in `requestBody` for OpenAPI files.
- [cds-dk@8.0.0] Multitenancy-related commands now always print the HTTP status on request errors.
- [cds-dk@8.0.0] `cds add helm` added `HorizontalPodAutoscaler` which can be enabled by `srv.hpa.enabled`.
- [cds-dk@8.0.0] `cds add attachments` adds configurations for `@cap-js/attachments`.
- [cds-dk@8.0.0] Shell completion now supports `fish` shell.
- [cds-dk@8.0.0] `cds add portal` creates configuration for the SAP Cloud Portal service.
- [cds-dk@8.0.0] `compile --to mermaid` exports a CDS model as a mermaid diagram.
- [cds-dk@7.9.5] `cds add hana` and `cds build` now support the HANA artifact type `.hdbeshconfig` required for enterprise search integration.
- [vscode-cds@8.0.1] Commands CDS: Preview as diagram to create a Mermaid class diagram. `@sap/cds-dk 8` is required.
- [vscode-cds@8.0.1] If trace is enabled via `cds.trace.level` the trace file location is shown in the `vscode-cds` Output view.
- [cds.java@3.0.0] Added support for @sap/cds-dk version `8`.
- [cds.java@3.0.0] Implemented instance-based authorization for bound actions & functions.
- [cds.java@3.0.0] Added properties `cds.odataV2.searchMode` and `cds.odataV4.searchMode` to configure how `$search` is handled.
- [cds.java@3.0.0] Correlation IDs are now propagated for messaging services running in structured mode (separating headers from data).
- [cds.java@3.0.0] Setting the new parameter `persistence` of the cds-maven-archetype to `false` generates an application without the JDBC persistence layer.
- [cds.java@3.0.0] The goal `add` of the `cds-maven-plugin` supports adding AuditLog V2 support to a CAP Java project.
- [cds.java@3.0.0] Introduced deep role-based and instance-based authorization checks for CQN statements.
- [cds.java@3.0.0] The goal `npm` of the `cds-maven-plugin` supports the new parameter `commands` to execute multiple npm commands in one execution block.
- [cds.java@3.0.0] Added OpenTelemetry instrumentation for Outbox Services.
- [cds.java@3.0.0] Added actuator end point `/actuator/cds/outboxes` to introspect outbox services.
- [cds.java@3.0.0] Properties `cds.model.provider.extensibility` and `cds.model.provider.toggles` can be used to disable tenant-specific extensions and/or feature toggles dimensions when loading models dynamically from MTX Sidecar.
- [cds.java@3.0.0] The switch `interfacesForAspects` in the `cds-maven-plugin` enables the generation of accessor interfaces for the entities representing targets of the compositions of aspects.
- [cds4j@3.0.0] `CqnPassThroughSearchPredicate` to pass-through search strings to the data store.
- [cds4j@3.0.0] Added new switch `interfacesForAspects` to the code generator configuration to enable the generation of accessor interfaces for targets of the compositions of aspects.
- [cds@8.0.3] Translations for the technical SAP language `1Q` used in support scenarios, for example for translation issues. See https://sapui5.hana.ondemand.com/sdk/#/topic/91f21f176f4d1014b6dd926db0e91070 for more.
- [cds@8.0.2] `express` is now an optional peer dependency, to indicate to applications to install it as part of their dependencies. It is needed for all runtime scenarios, but can be omitted for pure design-time cases like `cds compile` calls.
- [cds@8.0.0] Profile `[attic]` to quickly test with deprecated features like so `CDS_ENV=attic cds watch` or `CDS_ENV=attic jest`.
- [cds@8.0.0] New OData Adapter: Default location header for actions that return an entity (custom handler must set the response status code to 201)
- [cds@8.0.0] New `cds.utils` methods `.stack()` and `.location()` to get the stack trace and location of the caller (not publicly released yet).
- [cds@8.0.0] Protected the methods inherited from `LinkedDefinitions` prototype against accidental and undetected interpretation and usage as CSN element: An error is thrown, when trying to access one of the usual CSN properties, like `.name`, `.kind`, `.type`, ... on them.
- [cds@8.0.0] Escaping single quotes with doubled ones `''` in `.properties` files
- [cds@8.0.0] Support for `@sap/xssec^4`
- [cds@8.0.0] New OData and REST adapter pass error to next such that a custom error middleware added to `cds.middlewares.after` is called Note: The custom middleware must precede the default error middleware (if it remains), for example, by adding via `unshift()`

- [cds@8.0.0] Support for extensibility scenarios in RESTful protocol adapters
- [cds@8.0.0] The built-in CORS middleware can be enabled explicitly with `cds.server.cors = true`. By default, this is `false` if in production.
- [cds@8.0.0] Remote Service: `useCache` destination option is enabled by default
- [cds@8.0.0] New model processor `cds.compile.to.hana` to generate `.hdbtable`, `.hdbview` files including migration table support.
- [cds@8.0.0] Added `cds.requires.connectivity` indicating whether SAP BTP Connectivity service is required.
- [cds@8.0.0] Support inline where conditions in `@restrict` like `where: (prop = $user.id)`.
- [cds-mtxs@2.0.1] Added HANA build plugin mappings `.hdbeshconfig` and `.hdbcalculationview` required for enterprise search and embedded analytics integration.
- [cds-mtxs@2.0.1] The Service Manager client reports the container state on timeouts.
- [cds-mtxs@2.0.0] Additional end point to get the passcode URL.
- [cds-mtxs@2.0.0] Dependencies for the SAP BTP Connectivity, Audit Logging, and Destinations services are automatically added if `cds.requires.[connectivity|audit-log|destinations]` properties are set, respectively.

### Changed ​

- [cds-dk@8.0.2] `cds add http` stores `http` files in a folder `test/http/` by default. Previously, this was `http/`.
- [cds-dk@8.0.2] `cds add helm` removed `saasRegistryParameters` key and moved parameters to `saas-registry`.
- [cds-dk@8.0.2] `cds init` no longer creates a `.cdsrc.json` for Node.js projects.
- [cds-dk@8.0.2] `cds build` configuration cleanup for `data.model` and `service.model` to only support configuration of a single model folder.
- [cds-dk@8.0.1] `cds add multitenancy` now adds the `java` profile in the MTX sidecar config, in addition to `mtx-sidecar`.
- [cds-dk@8.0.1] `cds init` uses Maven Java archetype version 2.10.1 for creating Java projects.
- [cds-dk@8.0.1] `cds init --add java` and other `cds add` commands use Java 21 by default.
- [cds-dk@8.0.1] `cds add helm` now adds env variables directly in values.yaml file instead of mtxs-configmap ref.
- [cds-dk@8.0.1] `cds init` for a Node.js project adds `@cap-js/cds-types` to its `devDependencies`.
- [cds-dk@8.0.1] `cds login` now informs about command-line options ignored when fetching a token.
- [cds-dk@8.0.1] `cds login` now exits with an error in case of clashing parameters.
- [cds-dk@8.0.1] cds shell completion now suggests files/folders when called directly after cds command, for example, `cds pac` will return files/folders starting with `pac`.
- [cds-dk@8.0.0] `cds deploy --to hana` uses `@sap/hdi-deploy` version 5.
- [cds-dk@8.0.0] `cds deploy` resolves the existing binding for deployment.
- [cds-dk@8.0.0] `cds import` will not generate `ON condition` for association or composition.
- [cds-dk@8.0.0] `cds import` will not add the `@cds.ambiguous` annotation for association or composition.
- [cds-dk@8.0.0] `cds import` now supports OData V2 EDMX file with empty or missing `EntityContainer`.
- [cds-dk@8.0.0] `cds init` will now initialize a cds 8 project.
- [cds-dk@8.0.0] `cds add approuter` will not add XSUAA under the hood any longer.
- [cds-dk@8.0.0] `cds add hana` and `cds build` use `@sap/hdi-deploy` version 5.
- [cds-dk@8.0.0] `cds add hana` now uses `@cap/js-hana`.
- [cds-dk@8.0.0] `cds add multitenancy` uses `@sap/cds-mtxs` version 2.
- [cds-dk@8.0.0] `cds add multitenancy` does not add the `UIFlexDeveloper` role anymore.
- [cds-dk@8.0.0] `cds add helm` doesn't expose srv and sidecar workload in multi tenant mode if approuter is present.
- [cds-dk@8.0.0] `cds add helm` changed `values.yaml` structure.
- [cds-dk@8.0.0] `cds add helm` command doesn't generate static files (subcharts and templates) when `cds add` is executed. Instead, it generates the `chart` folder containing all the static data in the `gen` folder when `cds build` is executed.
- [cds-dk@8.0.0] `cds add xsuaa` now uses `@sap/xssec` version 4.
- [cds-dk@8.0.0] `cds add tiny-sample` uses the same `schema.cds` file name as `cds add sample`.
- [cds-dk@8.0.0] `cds add html5-repo` now adds the `deploy_mode: html5-repo` parameter to the mta.yaml.
- [cds-dk@8.0.0] `cds add html5-repo` uses `gen` (Node.js) or `.` (Java) for the app deployer `path`.
- [cds-dk@8.0.0] `cds add mta` now creates an mta.yaml with schema version 3.3.0.
- [cds-dk@8.0.0] `cds login` no longer falls back to a legacy URL or a GET request for tokens.
- [cds-dk@8.0.0] `cds login` now enforces HTTPS when contacting remote URLs.
- [cds-dk@8.0.0] `cds login` no longer saves Refresh Tokens by default for security reasons. (Use `--save-refresh-token` to enable this feature.)
- [cds-dk@8.0.0] `cds build` cleanup of build task property `use`.
- [cds-dk@8.0.0] `cds add helm` default value of `xsappname` will contain Release Namespace as well.
- [cds-dk@8.0.0] `cds build` allows custom plugins to be executed after the built-in plugins.
- [cds-dk@8.0.0] `cds login` eagerly fetches the passcode URL (if supported by `@sap/cds-mtxs`) and prints it on prompt.
- [cds-dk@8.0.0] `cds extend` and `cds activate` have been deprecated and are now removed. (You can still migrate and download projects, see `cds migrate --help` and `cds extend --help`.)
- [cds-dk@8.0.0] Remove obsolete classic MTX checks and enforce `@sap/cds` >= 7.
- [cds-dk@8.0.0] `cds build` uses cds.compile.to.hana API with `@sap/cds` 8.
- [cds-dk@8.0.0] `cds bind` and `cds deploy` use direct http requests instead of `cf curl`.
- [cds-dk@8.0.0] `cds build --for java` no longer generates localized EDMX files by default. It can be enabled using `contentLocalizedEdmx` build task option.
- [cds-dk@8.0.0] `@cap-js/sqlite`/`better-sqlite3` is used in dependencies instead of `sqlite3`.
- [cds-dk@8.0.0] `cds add sample` now generates comma-separated CSV files, instead of semicolon-separated, in order to be more consistent with `cds add data`.
- [cds-dk@8.0.0] `cds build` no longer supports the deprecated register API for custom plugins.
- [cds-dk@8.0.0] `cds init` no longer adds `devDependencies` for `eslint` and `@sap/eslint-plugin-cds` when creating a new project.
- [cds-dk@8.0.0] `cds init` now creates `eslint.config.mjs` file with reference to `@sap/cds/eslint.config.mjs`.
- [cds-dk@7.9.4] `cds init` uses latest Maven Java archetype version 2.10.1 for creating Java projects.
- [cds-dk@7.9.4] `cds bind` and `cds deploy` use direct http requests instead of `cf curl`.
- [eslint-plugin-cds@3.0.4] Internal refactorings
- [vscode-cds@8.0.1] Dropped official support for CDS compilers <4. The extension likely still works with older versions, but compatibility is not guaranteed.
- [vscode-cds@8.0.1] Minimum VSCode version is now 1.89.1
- [cds-compiler@5.0.2] Node 18 is now the minimum required version.
- [cds-compiler@5.0.2] API `CompilationError`s will no longer serialize all compiler messages into `e.message`. Use `e.messages[]` instead or `e.toString()` to serialize errors into a string.
- [cds-compiler@5.0.2] CDL parser: Annotations that can't be applied are now rejected.
- [cds-compiler@5.0.2] compiler: `extend` statements on "namespaces" (paths that are not definitions) are now always errors.
- non-structured events are rejected
- `$self` references in JOINs are rejected if they could lead to issues in SQL rendering.
- non-string enum definitions must have a value.
- A top-level definition `$self` is rejected. `$self` is considered a reserved name.
- `$at.from`/`$at.to` are deprecated; use `$valid.from`/`$valid.to` instead.

- [cds-compiler@5.0.2] to.hdbcds: The HDBCDS backend is now considered deprecated.
- [cds-compiler@5.0.2] to.edm(x): Set default nullability to `true` for collection like properties (was `false` before).
- Raise message ids `odata-spec-violation-namespace`, `odata-spec-violation-no-key` from warning to error.

- [cds-compiler@5.0.2] to.sql: `@cds.persistence.exists` is not propagated to generated localization views (`localized.*`)
- Option `fewerLocalizedViews` is now enabled by default.
- Option `betterSqliteSessionVariables` is now enabled by default.

- [cds.java@3.0.0] The minimum required @sap/cds-dk version is now `7`.
- [cds.java@3.0.0] The minimum required Cloud SDK version is now `5.9.0`.
- [cds.java@3.0.0] The minimum required Maven version for a CAP Java project is now `3.6.3`.
- [cds.java@3.0.0] The default Node.js version installed by the CDS Maven Plugin is updated to `v20.14.0`.
- [cds.java@3.0.0] Enabled parameters `sharedInterfaces` and `uniqueEventContext` by default in goal `generate`.
- [cds.java@3.0.0] The Spring Boot `cloud` profile is now set as production profile by default.
- [cds.java@3.0.0] CSRF Token Handling for Remote OData Services is now disabled by default. It can be enabled by setting `cds.remote.services..http.csrf.enabled` to `true`.
- [cds.java@3.0.0] The SQL optimization mode for SAP HANA is now set to `hex` by default.
- [cds.java@3.0.0] Setting the configuration property `cds.outbox.persistent.enabled` to `false` now disables all persistent outbox services.
- [cds.java@3.0.0] The lazy internationalization of OData V4 metadata is enabled by default. It can be disabled by setting `cds.odata-v4.lazy-i18n.enabled` to `false`.
- [cds.java@3.0.0] The `ModelChangedEventContext` now takes an `Instant` instead of a `Long` as timestamp. This timestamp is used to only refresh model caches where the model was cached before that time.
- [cds.java@3.0.0] The "proof of possession" check in the SAP Security Library is enabled by default for IAS scenarios. This requires clients to always send the client certificate in addition to the actual JWT token. It can disabled by setting the configuration property `sap.spring.security.identity.prooftoken` to `false`.
- [cds.java@3.0.0] The property `cds.auditLog.personalData.throwOnMissingDataSubject` now defaults to `true`, causing exceptions in case of incomplete personal data annotations.
- [cds.java@3.0.0] CQN queries on application services using expand or inline without specifying an association to expand resp. inline all associations are rejected now.
- [cds.java@3.0.0] The `cds-services-archetype` generates CAP Java projects using JDK 21 by default, if no JDK version is specified.
- [cds.java@3.0.0] MessagingServices now represent message and headers in a structured Map-based format by default. The old string-based format can be used by setting `cds.messaging.services..structured: false`
- [cds4j@3.0.0] Deprecated `CqnSearchPredicate`, instead use `CqnSearchTermPredicate`
- [cds4j@3.0.0] Deprecated `Modifier.search(String)`, instead use `Modifier.searchTerm(CqnSearchTermPredicate)`
- [cds4j@3.0.0] Deprecated session context variable `$user.tenant`, instead use `$tenant`
- [cds4j@3.0.0] Deprecated session context variables `$at.from` and `$at.to`, instead use `$valid.from` and `$valid.to`
- [cds4j@3.0.0] Removed deprecated option `supported_locales` for using locale-specific views on H2 and SQLite
- [cds4j@3.0.0] Removed deprecated `cqn(String)` methods in `Insert`, `Update` and `Upsert`
- [cds4j@3.0.0] Optimized SQL for to-many expands by parent-keys
- [cds@8.0.2] Creation via draft by association is forbidden with `403` response.
- [cds@8.0.2] New OData adapter captures input of `$search` as plain val without applying OData grammar.
- [cds@8.0.2] ´not null´ is not validated for action/function params. Use `@mandatory` instead.
- [cds@8.0.2] REST adapter rejects unknown input if not annotated with `@open`. Previously, it removed the unknown elements from the payload.
- [cds@8.0.0] Meant for tests only: `cds.User.default` points to a singleton instance of `cds.User` instead of a class now.
- [cds@8.0.0] Never public: `express.Request.user` or `.tenant` must not be used anywhere NOTE: that was never public nor guaranteed to exist at all! Always only use `cds.Request.user/tenant` or `cds.context.user/tenant`.
- [cds@8.0.0] Never public: `cds.Request.protocol` was 'odata-v4' and is now 'odata'.
- [cds@8.0.0] Errors sent to clients now include a stack trace in the `stack` property during development and in tests NEVER test with `.toEqual()` but always only with `.toMatchObject()`.
- [cds@8.0.0] Node.js 18 is now the minimum required Node.js version. Version 16 is no longer supported.
- [cds@8.0.0] `cds.fiori.draft_deletion_timeout` is enabled with default value `30d`
- [cds@8.0.0] `srv.on('error')` is only invoked for errors during `srv.dispatch()`, i.e., for errors that occur while the respective request is being processed by a service instance Specifically, `srv.on('error')` is no longer invoked for an error that occurs in the protocol adapter. Instead, use a custom middleware added to the beginning of `cds.middlewares.after`.
- This change does not affect the legacy OData adapter.

- [cds@8.0.0] In `bypass_draft`, direct active modifications now have event `CREATE` instead of `NEW`.
- [cds@8.0.0] `cds compile --to serviceinfo` returns the correct URL path for Java applications.
- [cds@8.0.0] The default index page is no longer served if `NODE_ENV` is set to `production`. Set `cds.server.index = true` to restore previous behavior.
- [cds@8.0.0] Delete deprecated cds build stub.
- [cds@8.0.0] Multiple entries in `cds.requires..vcap` are now ANDed instead of ORed, so that e.g. multiple bound services of the same kind can be filtered more easily. For example, `{ "vcap": { "label": "xsuaa", "tag": "broker" }}` can be used to only bind an XSUAA instance (out of many) with the `xsuaa` label AND the `broker` tag.
- [cds@8.0.0] Role `cds.Subscriber` removed from predefined mock users.
- [cds@8.0.0] REST adapter uses managed transactions
- [cds@8.0.0] The default index page got a new design.
- [cds@8.0.0] Syntax error in batch body is handled as bad request
- [cds-mtxs@2.0.2] Calls to Service Manager now include the `Client-ID` and `Client-Version` headers.
- [cds-mtxs@2.0.0] `@sap/cds-mtxs` now requires `@sap/hdi-deploy >= 4`.
- [cds-mtxs@2.0.0] Deprecated endpoint `upgradeAll` has been removed from `SaasProvisioningService`.
- [cds-mtxs@2.0.0] Use the `cds.compile.to.hana` API to support cds plugins such as embedded analytics.
- [cds-mtxs@2.0.0] When pushing an extension, the extension is blocked if it contains critical annotations.
- [cds-mtxs@1.18.2] All requests to Service Manager are now retried 3 times by default. This value can be modified by setting `cds.requires.mulitenancy.serviceManager.retries`.
- [ux-cds-odata-language-server-extension@1.14.1] Updated to support changes in annotation vocabularies
- [ux-cds-odata-language-server-extension@1.14.1] Enhanced code completion performance

### Fixed ​

- [cds-dk@8.0.1] `cds add` is failing if one of the `canRun` conditions in the plugin isn't satisfied.
- [cds-dk@8.0.1] `cds version` and other CLI commands no longer color their output if e.g. stdout is redirected.
- [cds-dk@8.0.1] `CHANGELOG.md` is part of npm package.
- [cds-dk@8.0.1] `cds build` determines the correct feature names if a `.cds` file path contains the name `fts`.
- [cds-dk@8.0.1] `cds watch` now ignores `.git/**`
- [cds-dk@8.0.0] `cds add mta` correctly adds the logging service with `@sap/cds >= 7.5`, if not explicitly disabled.
- [cds-dk@8.0.0] `cds add` doesn't fail for Java projects if `srv/pom.xml` doesn't exist.
- [cds-dk@8.0.0] `cds login` now prints the App URL, reports HTTP 404 errors correctly and gives better mitigation hints.
- [cds-dk@8.0.0] `cds deploy` consistently resolves configured service models, where previously the db model had priority.
- [cds-dk@8.0.0] `cds build` checks for the existence of a package.json file in the root folder of Node.js projects.
- [cds-dk@8.0.0] `cds add` sets `cds.cli` before plugins are loaded.
- [cds-dk@8.0.0] `cds add http` supports custom keys, including composite keys.
- [cds-dk@8.0.0] `cds add approuter` will not create a `router` subfolder if an `xs-app.json` is found in the `app` directory.
- [cds-dk@7.9.5] `cds add` is failing if one of the `canRun` conditions in the plugin isn't satisfied.
- [cds-dk@7.9.5] `cds watch` now ignores `.git/**`
- [cds-dk@7.9.4] Dependency update to fix CVE-2024-37890
- [cds-dk@7.9.3] `cds add data` now has a more precise foreign key type conversion from CSV data, covering edge cases.
- [cds-compiler@5.0.6] for.seal: Don't generate DRAFT artifacts.
- [cds-compiler@5.0.4] CDL parser: an `extend entity` and `extend aspect` with an extensions for the same element now correctly leads to an error, because it resulted in part of the extension being simply dropped. Remark: an `extend type` and the recommended plain `extend` led to an error in that situation already before.
- [cds-compiler@5.0.4] to.sql: Conditions inside filters in combination with foreign key aliases were not properly translated in rare cases.
- [cds-compiler@5.0.4] Update OData Vocabularies: 'PDF', 'UI'.
- [cds-compiler@5.0.2] for.odata: Propagate all `@odata { Type, MaxLength, Precision, Scale, SRID }` to generated foreign keys.
- [cds-compiler@4.9.6] for.seal: Don't generate DRAFT artifacts.
- [cds-compiler@4.9.6] for.odata: Propagate all `@odata { Type, MaxLength, Precision, Scale, SRID }` to generated foreign keys.
- [cds-compiler@4.9.6] to.edm(x): Respect `AppliesTo` specification in term definitions for actions and functions.
- [cds-compiler@4.9.6] to.sql: Conditions inside filters in combination with foreign key aliases were not properly translated in rare cases.
- [cds.java@3.0.0] Fixed a bug, causing draft fields to be generated for structured types and arrays of structured types.
- [cds.java@3.0.0] Fixed a bug, causing issues when using `@cds.java.version` on draft-enabled entities.
- [cds.java@3.0.0] Fixed a variable scale of `Decimal` used as action/function parameter.
- [cds.java@2.10.2] Fixed a bug, causing the SMS client to retrieve subscribed tenants from the Subscription Manager Service without pagination.
- [cds.java@2.10.1] Fixed a bug in MT applications, causing even more requests to ServiceManager in an overload situation (429 responses).
- [cds.java@2.10.1] Fixed a bug, causing unexpected transaction rollbacks during processing of outbox messages. This might have resulted in messages delivered with a delay.
- [cds.java@2.10.1] Fixed a bug in the developer dashboard which caused a crash when the application is reloaded by Spring Dev Tools in CDS watch mode.
- [cds.java@2.10.1] Fixed a bug, causing the developer dashboard to not be completely disabled in production.
- [cds4j@3.0.0] OData v4 - select list items of `$select` are not ignored any longer but correctly applied to the result of the `$apply`-pipeline, if a request contains both `$apply` and `$select`
- [cds4j@2.10.1] SAP HANA: Don't generate statement-level collation clause in subqueries
- [cds4j@2.10.1] Fix UnsupportedOperationException on deep updates with `@cds.java.version` elements
- [cds@8.0.3] Empty feature set by switched off feature toggles
- [cds@8.0.3] Allow deviating response types for `$batch`, e. g. input `multipart` and output `json`
- [cds@8.0.2] `cds.log(…, 0)` now properly changes log level to `SILENT` if called after the respective logger had already been created.
- [cds@8.0.2] `cds.test` recommends version 7 of `chai-as-promised`. Version 8 is ESM-only and does not work with `cds.test` at the moment.
- [cds@8.0.2] Loading of `cds.plugins` now respects the (internal!) property `cds.env.plugins` again.
- [cds@8.0.2] Proper error handling for invalid draft requests in combination with `$apply`
- [cds@8.0.2] Usage of `Date` values in `cds.ql` expressions
- [cds@8.0.2] Error in `enterprise-messaging` deploy script
- [cds@8.0.2] Error handling for bad navigation properties (like in `$orderby=prop1/prop2`) in new OData adapter
- [cds@8.0.2] Properly forward path expression in front of lambda functions for `odata-v2` remote services
- [cds@8.0.1] always enforce `attic` profile
- [cds@8.0.0] Failing logins with internal pre-release versions from git main branches.
- [cds@8.0.0] Prevent inconsistent ordering when selecting messages from outbox
- [cds@8.0.0] Creating child-nodes with `@Core.Immutable` fields
- [cds@8.0.0] ETag handling in draft cancel
- [cds@8.0.0] `if-none-match` with asterisk in update handler
- [cds@8.0.0] `odata.mediaContentType` for empty stream is always `null`
- [cds@8.0.0] `$select/$expand` large binaries by draft edit and activate does not return large binaries
- [cds@8.0.0] Error message for actions/functions with wrong path
- [cds@8.0.0] Direct `READ` of entities that are `@cds.autoexposed` when the `cds.env.features.odata_new_adapter` flag is set to `true`
- [cds@8.0.0] Reject `PATCH` requests where foreign keys cannot be determined statically or where multiple entities need to be updated
- [cds@8.0.0] actions / functions bound to a collection of entities in case `cds.features.odata_new_parser` is enabled
- [cds@8.0.0] `cds.compile.to.hana` generates `afterImage` only if migration tables exist.
- [cds@7.9.3] `cds compile --to serviceinfo` returns the correct URL path for Java applications.
- [cds@7.9.3] Prevent HANA deadlocks when processing outbox table
- [cds@7.9.3] Invalid cache for `SiblingEntity` requests
- [cds@7.9.3] `cds.test` recommends version 7 of `chai-as-promised`. Version 8 is ESM-only and does not work with `cds.test` at the moment.
- [cds@7.9.3] Loading of `cds.plugins` now respects the (internal!) property `cds.env.plugins` again.
- [cds@7.9.3] `req.data` and `req.INSERT.entries` were not pointing to same object if it contains more than one entry.
- [cds-mtxs@2.0.2] Reduced number of Service Manager requests to `service_instances` in the error case.
- [cds-mtxs@2.0.1] Improved robustness in case of temporary extension inconsistencies.
- [cds-mtxs@2.0.1] The Service Manager client now stores instance and binding locations used for async polling in-memory, allowing parallel subscriptions for single-instance applications.
- [cds-mtxs@2.0.1] The Service Manager client automatically recreates instances in "creation failed" state on subscription.
- [cds-mtxs@1.18.2] Certificate check for sms subscription now also compatible with kyma.
- [cds-mtxs@1.18.2] Feature toggles can contain `.` again.
- [cds-mtxs@1.18.2] Extension field limit check now correctly accepts `0` as no fields to be extended.

### Removed ​

- [cds-dk@8.0.0] `cds add notebook` is removed. CAP Jupyter Notebooks have been replaced by custom CAP Notebooks for VS Code which are now part of the CDS Editor. See https://cap.cloud.sap/docs/tools/#add-cds-editor for more.
- [cds-compiler@5.0.2] API: Deprecated functions `preparedCsnToEdmx` and `preparedCsnToEdm` were removed. Use `to.edm(x)` instead.
- [cds.java@3.0.0] Removed deprecated feature `cds-feature-xsuaa`. As a consequence, support for SAP's `spring-xsuaa` library has been removed as well. Use `cds-feature-identity` in combination with SAP's `spring-security` library instead.
- [cds.java@3.0.0] Removed support for the classic MTX Sidecar. The `cds.multitenancy.mtxs.enabled` property has been removed, as it is now obsolete.
- [cds.java@3.0.0] The deprecated `MtSubscriptionService` API and the corresponding compatibility mode `cds.multitenancy.compatibility.enabled` have been removed in favor of the `DeploymentService`.
- [cds.java@3.0.0] The deprecated HTTP-based tenant upgrade APIs `/mt/v1.0/subscriptions/deploy` and `PUT /messaging/v1.0/em/` have been removed in favor of the task-based upgrade approach.
- [cds.java@3.0.0] The goal `addSample` is removed from the `cds-maven-plugin` and replaced with goal `add` with parameter `-Dfeature=TINY_SAMPLE`.
- [cds.java@3.0.0] Removed various deprecated classes, methods and properties.
- [cds@8.0.2] Type information is no longer shipped as part of `@sap/cds`. Instead, the `@cap-js/cds-types` package has to be explicitly installed as devDependency for projects requiring type support. Installing the package is sufficient to add type support back in.
- [cds@8.0.2] Invalid annotations `@Common.FieldControl.Mandatory` and `@FieldControl.Mandatory` → use `@Common.FieldControl: #Mandatory` instead
- [cds@8.0.2] Invalid annotations `@Common.FieldControl.ReadOnly` and `@FieldControl.ReadOnly` → use `@Common.FieldControl: #ReadOnly` instead
- [cds@8.0.0] Legacy leftovers for old middlewares: `ExtensedModel:middleware4` (in combination with extensibility)
- [cds@8.0.0] Legacy request header `x-correlationid` which was always just a misspelled variant of `x-correlation-id`.
- [cds@8.0.0] Legacy configuration option `cds.requires.middlewares = false`
- [cds@8.0.0] Legacy configuration option `cds.features.serve_on_root = true`
- [cds@8.0.0] Legacy draft implementation `cds.fiori.lean_draft = false`
- [cds@8.0.0] Legacy API `req.user.locale`. Use `req.locale` instead.
- [cds@8.0.0] Legacy API `req.user.tenant`. Use `req.tenant` instead.
- [cds@8.0.0] Legacy configuration `cds.drafts.cancellationTimeout`. Use `cds.fiori.draft_lock_timeout` instead.
- [cds@8.0.0] Legacy annotation `@assert.enum`. Use `@assert.range` instead.
- [cds@8.0.0] Legacy properties of `cds.Request`: `req.tokenInfo`, `req._.shared`, and `req.attr`
- [cds@8.0.0] Legacy type facade files from `@sap/cds/apis/...`. Use `@sap/cds` as only type import.
- [cds@8.0.0] Legacy quirks mode. From now on, `cds.ql` generates spec compliant `ref` paths in INSERT/UPDATE/DELETE CQNs. The database services expect the same. Use `{ INSERT: { into: { ref: ['Authors']}}}` instead of `{ INSERT: { into: 'Authors' }}`
- Use `{ UPDATE: { entity: { ref: ['Authors']}}}` instead of `{ UPDATE: { entity: 'Authors' }}`
- Use `{ DELETE: { from: { ref: ['Authors']}}}` instead of `{ DELETE: { from: 'Authors' }}`

- [cds@8.0.0] Deprecated csn entity proxy `_texts`. Use `.texts` instead.
- [cds@8.0.0] Deprecated built-in `cds.compile.to.gql` and `cds.compile.to.graphql` compile targets. These are provided by `@cap-js/graphql` plugin versions >= 0.9.0.
- [cds@8.0.0] Deprecated API `srv.stream`. Use `SELECT` with a single `cds.LargeBinary` column instead.
- [cds-mtxs@2.0.1] `@sap/instance-manager` is not supported any longer as a fallback to the built-in Service Manager client.

## May 2024 ​

### Added ​

- [vscode-cds@7.9.0] Commands CDS: Generate Model Data as JSON/CSV to create a number of records with test data for a selected entity.
- [vscode-cds@7.9.0] Command CDS: Generate HTTP Requests to create HTTP requests for a selected service or entity.
- [vscode-cds@7.9.0] Syntax highlighting for the `cds` language to the markdown editor (not to the preview though).
- [cds.java@2.10.0] Option to set a `Cache-Control: max-age=` HTTP header via `@http.CacheControl: {maxAge: }` CDS annotation on stream properties. The header allows to control the behavior of caches, the `max-age` (in seconds) specifies the maximum age of the content before it becomes stale.
- [cds.java@2.10.0] Change Tracking: Annotation `@changelog` on compositions and to-one associations can be used to write human-readable values into the change log instead of technical keys of the target entity.
- [cds.java@2.10.0] Support OData V4 Key-as-Segment Convention
- [cds.java@2.10.0] Support filtering grouped data by aggregated values with `$these/aggregate` for OData V4 analytical queries.
- [cds.java@2.10.0] New Developer Dashboard (alpha) that provides a centralized point where developers can efficiently manage and monitor their CAP applications.
- [cds.java@2.10.0] Introduced Kafka consumer/producer configuration via messaging configuration (`cds.messaging.services.[my_kafka_service].queue.config.[consumer/producer].[property]: "value"`).
- [cds4j@2.10.0] Introduced `CdsDiffProcessor` API to compare images of the data between each other and observe differences in them.
- [cds4j@2.10.0] Support fuzzy search on SAP HANA via config option `cds.sql.hana.search.fuzzy: true`
- fuzziness threshold default `cds.sql.hana.search.fuzzinessThreshold` (default: 0.8)
- `@Search.fuzzinessThreshold` element annotation to override the default fuzziness threshold

- [cds4j@2.10.0] Support exact search with wildcards `*` and `?`.
- [cds4j@2.10.0] New `ContainmentTest` modes `MATCH` and `SEARCH` with wildcard support.

### Changed ​

- [cds-dk@7.9.1] `cds add mta` will now use the new `sap_java_buildpack_jakarta` buildpack configuration in the `mta.yaml`.
- [cds-mtxs@1.18.1] Extension linter can now be configured for extensions of existing fields.
- [cds-mtxs@1.18.1] With extensions, the deployment service now uses a separate folder for each deployment to improve parallel upgrade and extension operations.
- [cds-mtxs@1.18.1] Trailing parts of secrets are not logged in case of errors anymore.

### Fixed ​

- [cds-dk@7.9.2] `cds add data` now uses the correct JSON type for foreign keys from CSV data, e.g. number instead of string
- [cds-dk@7.9.2] `cds bind` now calls resolve in sequence to avoid file access exceptions
- [cds-dk@7.9.1] `eslint` 9 doesn't crash anymore if called in a project created with `cds init`
- [eslint-plugin-cds@3.0.3] Disabling ESLint for the next line via `eslint-disable-next-line` now works properly in cds files
- [vscode-cds@7.9.0] code completion for elements snippet now works when annotating artifacts using paths such as `MyService.SomeEntity` or when triggered at particular positions including line start
- [vscode-cds@7.9.0] maintain translation quickfix could have used an existing translation file of a reuse component
- [cds-compiler@4.9.4] to.sql: always include `tenant` column in foreign key references.
- reject `tenantDiscriminator` option only if sql dialect is `hana` and if `withHanaAssociations` option is set.

- [cds-compiler@4.9.2] compiler: Rewriting annotation expression paths in structures of projections has been improved.
- [cds-compiler@4.9.2] to.edm(x): Operator `/` represents `DivBy` operator, explicit `DivBy` is replaced with `Div` as integer division.

- [cds-compiler@4.9.2] to.sql: consider all associations in tenant dependent entity for referential constraint generation
- [cds.java@2.10.0] Fixed a bug, causing incorrect session context variables when processing database statements.
- [cds.java@2.9.2] Fixed a bug, causing connections to PostgreSQL databases on Google Cloud Platform (GCP) to fail because missing support for mutual TLS.
- [cds.java@2.9.1] Fixed a bug, causing the index page to fail to load in a Native Image application.
- [cds4j@2.10.0] Fixed "Cannot set reference. Reverse associations are not supported" exception on insert with data for to-many associations.
- [cds@7.9.2] Server crash in case of certain errors in Cloud SDK
- [cds@7.9.2] Bug in restriction of entities modeled as composition of aspects
- [cds@7.9.2] `$search`: resolve an exception accessing `req.query.elements`
- [cds@7.9.2] Ignore flattened associations in projection on remote entities
- [cds@7.9.2] Falsy keys in `cds.ql` were ignored in usage like `SELECT.from(Books, 0)`
- [cds@7.9.1] `cds.compile.to.sql` doesn't fail for older compiler versions if `postgres` keywords aren't defined
- [cds@7.9.1] `cds compile --to serviceinfo` no longer detects a Java project if there is a pom.xml file in a subfolder of `app/`
- [cds@7.9.1] `acquireTimeoutMillis` is ensured if custom pool config is provided
- [cds-mtxs@1.18.1] Callback to saas-registry now works properly with certificate-based binding.
- [cds-mtxs@1.18.1] The passcode URL returned by the token endpoint no longer contains a 'cert' subdomain.

### Removed ​

- [vscode-cds@7.9.0] Toolbar button Open with CDS Text Editor from graphical modeler, modeler now handles both directions to switch between graphical and textual editor.

## April 2024 ​

### Added ​

- [cds-dk@7.9.0] Shell completion in Linux, macOS, Windows for cds commands and parameters (beta)
- [cds-dk@7.9.0] `cds bind` supports shared service instances. Service keys are created in the space where a service instance was shared from.
- [cds-dk@7.9.0] `cds add data` now can generate actual data (not only a header line), both as `csv` and `json` structure.
- [cds-dk@7.9.0] `cds subscribe` now allows to pass tenant metadata and HDI parameters using parameter `--body `.
- [cds-dk@7.9.0] `cds add http` has a `--dry` flag to write the generated http requests to stdout.
- [cds-dk@7.9.0] `cds add hana` and `cds build` support undeploy of calculation views by default.
- [cds-dk@7.9.0] `cds bind` supports custom credentials to overwrite cloud service credentials.
- [cds-dk@7.9.0] Better support for `profiles` in cds schema for `package.json` and `.cdsrc.json`.
- [cds-dk@7.9.0] `cds bind` supports custom credentials to overwrite cloud credentials of multiple services.
- [cds-dk@7.8.2] `cds compile` to `openapi` now maps `@ODM.oidReference.entityName` annotation to generate `x-sap-odm-oid-reference-entity-name`.
- [cds-dk@7.8.1] `cds add` plugins now support custom flags.
- [cds-dk@7.8.1] `cds add kafka` is also enabled for Helm deployments.
- [cds-dk@7.8.1] `cds add enterprise-messaging` and `cds add enterprise-messaging-shared` now support a `--cloudevents` flag which automatically adds `cds.requires.messaging.format = 'cloudevents'`.
- [eslint-plugin-cds@3.0.0] Support ESLint flat configurations (`eslint@v9`) and make them available as recommended, all.
- [eslint-plugin-cds@2.7.0] Add `getRootPath()` method to `context` object to get the project rootPath.
- [cds-compiler@4.9.0] compiler: Annotations with expressions are now rewritten when propagated.
- [cds-compiler@4.9.0] for.seal: Added API function that produces a CSN for SEAL.
- [cds-compiler@4.9.0] for.odata/to.edm(x): Support annotation path expressions including path flattening.
- [cds.java@2.9.0] UI content from the `app` folder is now served automatically for local development.
- [cds.java@2.9.0] Links to web applications from `app` folder are now added automatically to the index page for local development.
- [cds.java@2.9.0] OData V4 index page content now provides a `Fiori Preview` link for each entity, loading a dynamically generated Fiori sample application.
- [cds.java@2.9.0] Added support for communicating with MTX sidecar based on a bound instance of identity service (IAS).
- [cds.java@2.9.0] CSRF token retrieval for Remote OData Services can now be disabled by setting `cds.remote.services..http.csrf.enabled` to `false`.
- [cds.java@2.9.0] The goal `add` of the `cds-maven-plugin` supports adding a complex and tiny sample to a CAP Java project.
- [cds.java@2.9.0] A set of property defaults recommended for production can now be set at once by setting `cds.environment.production.enabled` to `true` or marking a specific Spring profile as the production profile by setting `cds.environment.production.profile` to (for example) `cloud`. The properties set include strict disabling of mock users and the index page.
- [cds.java@2.9.0] The goal `generate` of the `cds-maven-plugin` provides the new switch `uniqueEventContexts` to prefix event context interfaces for bound actions / functions with the entity name. This avoids possible naming clashes for operations with the same name for different entities.
- [cds.java@2.9.0] Added a new property `cds.sql.inlineCount.mode` to configure how inline counts are calculated.
- [cds4j@2.9.0] Configuration option `cds.sql.inlineCount` to specify if inline-count is executed via `window-function` or an additional `query`.
- [cds@7.9.0] Option `cds.env.sql.transitive_localized_views: false` to skip generating transitive localized views for entities which don't have own localized elements, but only associations to such. Supported for Java and new database services in Node.js (ignored for old ones).
- [cds@7.9.0] Option `cds.env.sql.native_hana_associations: false` to skip generating native HANA associations.
- [cds@7.9.0] Running `cds compile --to sql` with `@cap-js/sqlite` installed now uses `session_context('$user.locale')` in generated DDL statements instead of generating static localized views for 'en', 'fr', and 'de' (same for `cds.deploy`).
- [cds@7.9.0] `api`: export reserved keywords for postgres via `cds.compiler.to.sql.keywords.postgres`
- [cds@7.9.0] Kind `legacy-hana` and profile `better-hana` for local testing scenarios.
- [cds@7.9.0] Support for PDF files (MIME type `application/pdf`) when the `cds.env.features.odata_new_adapter` flag is set to `true`
- [cds@7.9.0] Lean draft: Support for filtered compositions (remain in the document)
- [cds@7.9.0] Support for `COUNT_DISTINCT` as OData data aggregation default method
- [cds@7.9.0] Better support for `profiles` in cds schema for `package.json` and `.cdsrc.json`
- [cds@7.9.0] Performance improvement for generating `@odata.context` url if `cds.features.odata_new_parser` is enabled
- [cds@7.9.0] Alpha support for SAP Event Broker-based messaging (kind `event-broker`)
- [cds-mtxs@1.18.0] `cds-mtx subscribe  --body ` now allows to pass tenant metadata and HDI parameters.

### Changed ​

- [cds-dk@7.9.0] `cds deploy --to hana` warns about using custom service name, e.g `--to hana:myService` and `--vcap-file` at the same time.
- [cds-dk@7.9.0] `cds compile` to `openapi` now throws an error when `@protocol : 'none'` is given.
- [cds-dk@7.9.0] `--data:for` of `cds add data` is now deprecated in favor of `--filter`.
- [cds-dk@7.9.0] `cds add data` sorts columns with own elements first, assuming they are more significant than the inherited/included elements.
- [cds-dk@7.9.0] `cds add http --filter` accepts a service/entity/action name or a regex instead of a path.
- [cds-dk@7.9.0] `cds deploy` and `cds bind` both use Cloud Foundry client for backend communication.
- [cds-dk@7.9.0] Changes in the `package-lock.json` file don't restart the server e.g. during `cds watch`
- [cds-dk@7.9.0] `cds init --add java` uses the currently installed Java version for the `pom.xml`.
- [cds-dk@7.9.0] `cds add mta` derives the JDK version from the `pom.xml` version.
- [cds-dk@7.9.0] `cds add helm` update default gateway to `kyma-system/kyma-gateway`
- [cds-dk@7.9.0] `cds lint` supports both legacy (`@eslint@^8`) and flat (`@eslint@^9`) ESLint configurations.
- [cds-dk@7.9.0] `cds add lint` adds flat ESLint configurations with `@eslint@^9`, `@sap/eslint-plugin-cds@^3.0.0`.
- [cds-dk@7.9.0] `cds add lint` now requires `ESLint` version 8 or above.
- [cds-dk@7.8.2] New versions of `@sap/cds` and `@sap/eslint-plugin-cds`
- [cds-dk@7.8.2] `cds add helm` moved `TENANT_HOST_PATTERN` key from configmap to `values.yaml`.
- [cds-dk@7.8.2] `cds add helm` `web-application` subchart now supports controlling the health probe timings and updated default gateway to `kyma-system/kyma-gateway`
- [eslint-plugin-cds@3.0.2] requires `ESLint` version 8 or above
- [eslint-plugin-cds@3.0.0] Plugin configurations (recommended, all) for `eslint@- [cds-compiler@4.9.0] Update OData vocabularies: 'Aggregation', 'Capabilities', 'Common', 'Hierarchy', 'PersonalData', 'Session', 'UI'.
- [cds-compiler@4.9.0] to.edm(x): Exposed anonymous parameter types are now prefixed with `ap`, `bap` and `ep` for actions, bound actions and entities.
- [cds.java@2.9.0] Renamed property `cds.odataV4.apply.inCqn.enabled` to `cds.odataV4.apply.transformations.enabled` to align with `@odata.apply.transformations` annotation name.
- [cds.java@2.9.0] The CSV data importer shows a warning instead of stopping the application, if it finds a CSV file for a not existing entity.
- [cds.java@2.9.0] An empty quoted value in a CSV files (`""`) is no longer interpreted as `null`, but as an empty String value.
- [cds4j@2.9.0] SAP HANA HEX mode: fallback to non-hex SQL on "hex enforced but cannot be selected" errors.
- [cds4j@2.9.0] The inline-count of a query is now computed with an SQL window function if the query has a filter.
- [cds4j@2.9.0] Segments of structured types created from a Path no longer contain a filter, as they don't have an identity.
- [cds4j@2.8.2] `DeepUpdateSplitter` locks only entities annotated with `@cds.java.version` to calculate FKs.
- [cds@7.9.0] Deprecated INSERT.into(...) .as (SELECT...) → use INSERT.into(...) .entries (SELECT...) instead.
- [cds@7.9.0] Default value of `cds.env.log.mask_headers` changed to `['/authorization/i', '/cookie/i', '/cert/i', '/ssl/i']` (adding `'/cert/i'` and `'/ssl/i'`)
- [cds@7.9.0] Error messages for entities annotated with '@cds.autoexpose'
- [cds@7.9.0] For Java apps `cds.sql.transitive_localized_views` now defaults to `false` to create less database views.
- [cds@7.9.0] For Java apps `cdsc.betterSqliteSessionVariables` now defaults to `true` to enable session variables on H2 and SQLite by default.
- [cds-mtxs@1.18.0] Retries for failed upgrades are more resilient, using an exponential backoff mechanism and more retries.

### Fixed ​

- [cds-dk@7.9.0] Revert json schema for cds schemas to `draft-07` to prevent VS Code warnings about unsupported schema features.
- [cds-dk@7.9.0] `cds add` doesn't fail for projects with a minimal `package.json` w/o `name` and `version` fields
- [cds-dk@7.9.0] `cds add data` can be executed in projects w/o `package.json` and `.cdsrc.json` files.
- [cds-dk@7.9.0] `cds add sample` does not fail if the `srv` folder doesn't exist.
- [cds-dk@7.9.0] `cds add helm` fixed xsuaa tenant-mode not updating on adding `multitenancy`
- [cds-dk@7.9.0] `cds watched` cannot be called from command line anymore.
- [cds-dk@7.9.0] `cds login` now correctly handles the case of an expired refresh token and gives more information about token-request errors.
- [cds-dk@7.9.0] `cds login` now refreshes the token URL if it had previously reverted to a legacy URL.
- [cds-dk@7.9.0] Command retrieval during cds bootstrap is now more robust.
- [cds-dk@7.9.0] `cds watch` now ignores all `gen`-folder content to allow tenant subscription in hybrid mode.
- [cds-dk@7.9.0] `cds build` doesn't copy `.cdsrc-private.json` file into the deployment folder.
- [cds-dk@7.8.2] `cds run/serve --resolve-bindings` correctly work with the new runtime authentication middleware.
- [cds-dk@7.8.2] `cds add helm-unified-runtime` fixed backend destinations urls for deployments that aren't exposed.
- [cds-dk@7.8.1] `cds build` does no longer add the model @sap/cds-mtxs/srv/bootstrap for Java projects by mistake if the `--ws` option is set.
- [eslint-plugin-cds@3.0.2] Internal parser call now handles `ESLint` version 8 and 9
- [eslint-plugin-cds@3.0.1] Add namespace `@sap/cds` to plugin configuration
- [eslint-plugin-cds@3.0.0] In latest-cds-version, get output from `npm outdated` on exit code 1.
- [eslint-plugin-cds@2.7.0] In no-db-keywords, use `getRootPath()` instead of dirname, as wrong paths lead to missing db entries, disabling the rule.
- [vscode-cds@7.8.1] Revert json schema to `draft-07` due to unsupported features in `2020-12` and `2019-09`
- [vscode-cds@7.8.1] `workspace/symbols` request could have shown interactive popup if LSP plugins are slow
- [vscode-cds@7.8.1] Indexing of entities with enum elements that led to wrongly reported unused imports
- [vscode-cds@7.8.1] Indexing of namespaces after internal compiler changes
- [vscode-cds@7.8.1] Indexing of annotations was slow
- [cds-compiler@4.9.0] compiler: Deprecated `$parameters` is no longer proposed in code completion.
- Duplicate mixin definitions lead to failing name resolution.

- [cds-compiler@4.9.0] to.cdl: Types were always rendered for associations with filters, even if it would lead to a compilation failure.
- [cds-compiler@4.9.0] to.edm(x): Fix a recursion bug in entity parameter handling.
- Fix event exclusion in service preprocessing.

- [cds.java@2.9.0] Fixed a bug, causing a failure when upgrading webhooks in Enterprise Messaging for tenants subscribed using Subscription Management Service (SMS).
- [cds.java@2.9.0] Fixed a bug, causing `@mandatory` or `not null` validations to run on nested data of non-cascading associations.
- [cds.java@2.9.0] Fixed a bug, causing `ext_attr` XSUAA claim not to be available in `UserInfo.getAdditionalAttributes()`.
- [cds4j@2.9.0] Fixed deletes via to-one compositions with backlink association key.
- [cds4j@2.9.0] Fixed setting of structured foreign keys with nesting level greater than two.
- [cds4j@2.9.0] Fixed result of inserts on draft-enabled projections, containing projected data.
- [cds4j@2.8.2] Fixed type of `cds.Vector` elements in generated accessor interfaces.
- [cds@7.9.0] `cds.compile.to.yaml` produced invalid YAML for compacted lines
- [cds@7.9.0] Handling of If-None-Match header for non-existing entity
- [cds@7.9.0] Revert json schema for cds schemas to `draft-07` to prevent VS Code warnings about unsupported schema features.
- [cds@7.9.0] Remote services: JSON representation of error shall include `request` and `response`
- [cds@7.9.0] Aliasing of associated entity column in case of expand by CQN build with joins.
- [cds@7.9.0] `$apply` scenarios when used alongside `cds.env.features.odata_new_adapter = true` and the new database layer
- [cds@7.9.0] ETag handling combined with where restrictions
- [cds@7.9.0] `cds compile --to hdbtabledata` now correctly supports CSV files using format `.texts_.csv`. Before the `include_filter` wasn't set in the generated `.hdbtabledata` files.
- [cds@7.9.0] `cds` commands no longer crash when executed in the `@sap/cds` installation dir.
- [cds@7.9.0] `cds.infer`: exposed association of query is inferred as `cds.Association` and not as it's target
- [cds@7.8.2] `.find` and `.filter` in `linked.entities()` now returns values instead of names
- [cds@7.8.2] `cds.app.serve.from(pkg,folder)` did not consider `pkg` for serving static resources
- [cds@7.8.1] In some cases, `.drafts` erroneously pointed to a CSN entity stub.
- [cds@7.8.1] Feature vectors including falsy values like `{ ft1: true, ft2: true, ft3: false }`
- [cds-mtxs@1.18.0] Extension linter is now also called if extensions are created via API.
- [cds-mtxs@1.18.0] The Service Manager credentials cache is correctly invalidated following a resubscription.

## March 2024 ​

### Added ​

- [cds-dk@7.8.0] `cds add mta` configures readiness health checks via http to `/` for Java and `/health` for Node.js.
- [cds-dk@7.8.0] `cds add` facets can now also be space-separated, e.g. `cds add mta mtx pipeline`.
- [cds-dk@7.8.0] `cds add http` adds an `http` folder with `.http` files generated for all services.
- [cds-dk@7.8.0] `cds add http --filter [path to dir or file]` generates `.http` files only for the specified file or directory. The shortcut is `-f`.
- [cds-dk@7.8.0] `cds add http --for-app [app name]` uses the hostname and the auth of the specified deployed app.
- [cds-dk@7.8.0] `cds add http --out` allows to specify the output folder for the http files. The shortcut is `-o`.
- [cds-dk@7.8.0] `cds build` reclassifies compilation warnings as info messages for extension projects in case they are caused by the SaaS application base model. `cds build --log-level info` logs all messages. Reclassification of message IDs can be customized.
- [cds-dk@7.8.0] `cds version` now also prints the version of the CAP Java SDK as well as the Java and Maven versions
- [cds-dk@7.8.0] `cds build` now uses argument `--ws-pack` instead of `--ws` to enable tarball based packaging of npm workspace dependencies for Node.js apps (beta).
- [cds-dk@7.8.0] `cds import` can now import the Action/Function with binding parameter type of different schema in the scope of a document.
- [cds-dk@7.7.2] `cds import` now has `beta` flag which can be used to import beta functionality in the CSN/CDS.
- [vscode-cds@7.8.0] Add preview commands to editor title
- [cds-compiler@4.8.0] compiler: Type `cds.Vector` was added. It is mapped to `REAL_VECTOR` on SAP HANA.
- [cds-compiler@4.8.0] Support associations to/from entities with parameters for SAP HANA SQL (hdi/direct).
- [cds-compiler@4.8.0] to.sql/to.hdi: SAP HANA keywords `ABSOLUTE`, `REAL_VECTOR`, and `ST_ASESRIJSON` are now included for smart quoting. +PostgreSQL keyword `SYSTEM_USER` is now included for smart quoting.

- [cds-compiler@4.8.0] API: Added `to.sql.postgres.keywords` and `to.sql.h2.keywords`. They contain keywords for the respective SQL dialect.
- [cds.java@2.8.1] Added a new property `cds.multiTenancy.dependencies.destination.enabled` to automatically declare Destination service as a dependency during subscription.
- [cds.java@2.8.1] Remote Services can now be configured with a service binding, from which a destination is derived automatically, by configuring the new properties section `cds.remote.services..binding`.
- [cds.java@2.8.1] Remote OData services now support the `ETagPredicate` for update and delete queries. The `ETagPredicate` is translated into a corresponding `If-Match` header.
- [cds.java@2.8.1] Remote OData services now store values from `ETag` response headers in the `CdsData` metadata (`data.getMetadata("etag")`). When executing an update statement ETags are automatically set in `If-Match` if present in the metadata of the data provided for the update.
- [cds.java@2.8.1] The switch `sharedInterfaces` in the `cds-maven-plugin` allows to replace the inner interfaces for global types with inlined arrayed types in the event contexts for an actions and functions with global ones.
- [cds.java@2.8.1] The goal `watch` of the `cds-maven-plugin` can be executed from the project root folder.
- [cds.java@2.8.1] Introduced a new API `OutboxService.outboxed(Service, Class)` to wrap a service with an asynchronous suited API while outboxing it.
- [cds.java@2.8.1] Introduced the interface `AsyncCqnService` and the API `AsyncCqnService.of(CqnService, OutboxService)`, providing an asynchronous suited API for CqnServices wrapped by an outbox.
- [cds.java@2.8.1] Added a new property `cds.outbox.services..ordered` (default: `true`) to disable strict ordering of outbox messages, allowing for parallelized message processing.
- [cds.java@2.8.1] Improved parallelization of tenant processing across outbox processors in multiple application instances.
- [cds.java@2.8.1] The new `EventContext.proceed()` method allows to explicitly proceed with executing the next On event handler.
- [cds.java@2.8.1] The goal `add` of the `cds-maven-plugin` supports adding Kafka support to a CAP Java project.
- [cds.java@2.8.1] The mock user security configuration now allows loading iFrames, to support H2 console out-of-the-box for local development.
- [cds.java@2.8.1] The mock user security configuration now triggers authentication also for XMLHttpRequests, to fix authentication issues with local UIs running under a parallel path to the API endpoints in some browsers.
- [cds.java@2.7.1] CQN transformations for `$apply` can now be selectively enabled per service using annotation `odata.apply.transformations`
- [cds4j@2.8.1] Added new switch `uniqueEventContexts` to the code generator configuration to enable the generation of unique event context interfaces. This is an incompatible change, because the event context interfaces are generated with the prefix of bound entities.
- [cds4j@2.8.1] SAP HANA: added support for CDS type `cds.Vector`: the data type `com.sap.cds.Vector`
- similarity functions `CQL.cosineSimilarity` and `CQL.l2Distance`

- [cds4j@2.8.1] Support spaces in ref paths for structure preserving element selections.
- [cds@7.8.0] Health check endpoint `/health` in default server
- [cds@7.8.0] Class `cds.service` now provides getters for `entities`, `types`, `events` and `operations`. These return iterable objects, which can be used in `for...of` loops.
- [cds@7.8.0] Class `cds.entity` getters for `keys`, `associations`, `operations` also return `Iterable` objects now
- [cds@7.8.0] Method `compile.to.serviceinfo()` now lists all Node.js service endpoints in cases where multiple protocols are configured. For Java, the list is still limited to the first endpoint. This will be fixed in a future release.
- [cds@7.8.0] More warnings for deprecated features, functions and annotations.
- [cds-mtxs@1.17.0] Ignore non-existing container if running upgrade `*` by setting `cds.requires['cds.xt.SaasProvisioning'].upgrade.ignoreNonExistingContainers: true`.
- [cds-mtxs@1.17.0] `cds-mtx-migrate '*'|[,] --init-tenant-list [--force] [--dry]` now allows to fill the internal tenant list (e. g. for migration of Dynamic Deployer base applications).
- [cds-mtxs@1.17.0] `cds-mtx-migrate '*'|[,] --sync-tenant-list [--force] [--dry]` now allows to sync the internal tenant list with existing containers. Entries without a corresponding HDI container will be removed.

### Changed ​

- [cds-dk@7.8.0] `cds add helm` uses `/health` for liveness and readiness checks for Node.js.
- [cds-dk@7.7.1] `cds init` uses latest Maven Java archetype version 2.7.0 for creating Java projects.
- [eslint-plugin-cds@2.6.6] Removed `require-2many-oncond` rule, as it is now covered by the compiler.
- [vscode-cds@7.8.0] Move menu item `Preview as yaml` to the top of the menu items list indicating its default character
- [vscode-cds@7.8.0] Formatting logging now includes whitespace even if it may be reduced to empty string, relative alignment positions, and details on inserting delayed items
- [vscode-cds@7.8.0] Minimum supported VSCode version is now 1.86.0
- [cds-compiler@4.8.0] compiler: Overriding an included element must not change the type to an association if it wasn't an association before and vice versa.
- [cds-compiler@4.8.0] Update OData vocabularies: 'Authorization', 'Common', 'UI'.
- [cds.java@2.8.1] Moved property `cds.remote.services..destination.type` to `cds.remote.services..type`. Also moved properties `suffix`, `service`, `queries` and `headers` from section `cds.remote.services..destination` to section `cds.remote.services..http`. Backwards compatibility for the old properties remains.
- [cds.java@2.8.1] CQN statements are not added to Open Telemetry spans anymore by default for performance reasons, but only if logger `com.sap.cds.otel.spans.CQN` is set to `DEBUG`.
- [cds4j@2.8.1] SQL: only use localized helper views if necessary
- [cds4j@2.7.1] Code generator: Constant classes for an enums are not generated anymore if the enum is defined as inline type for the element.
- [cds-mtxs@1.17.0] `/-/cds/saas-provisioning/upgrade` sent as an async request with payload `"tenants": ["*"]` will now return job information even if no tenants are found.

### Fixed ​

- [cds-dk@7.8.0] `cds deploy` always included models from existing `fts/*` folders. Now, it only does so if `cds.requires.toggles` is switched on.
- [cds-dk@7.8.0] `cds build` now adds the correct HANA tenant database artifacts for a multitenant application in case a second shared database exists.
- [cds-dk@7.8.0] `cds bind --to-app-services` will throw a better error message if no app name is supplied.
- [cds-dk@7.7.2] `cds deploy --to hana` environment entries from `--vcap-file` option now overwrite environment entries.
- [cds-dk@7.7.2] `cds add helm` `web-application` subchart now allows annotations to be added to the K8s services and `content-deployment` subchart now allows to set `imagePullPolicy`.
- [cds-dk@7.7.1] `cds build` now allows the SaaS application base model to be located in a subfolder of the mtx extension project using npm workspace setup. Before, such a scenario caused duplicate model definitions.
- [cds-dk@7.7.1] `cds init` shows better error message if project name contains unsupported characters.
- [eslint-plugin-cds@2.6.7] Removed loading of previously removed rule.
- [vscode-cds@7.8.0] Code completion for annotations with ![] identifiers
- [cds-compiler@4.8.0] compiler: `cast()`s to structured types and associations are now rejected. They could lead to crashes before.
- [cds-compiler@4.8.0] to.edm(x): Reject action/function return types that are declared `many of many`.
- Render user defined annotation type `cds.Integer` as `Edm.Int`.

- [cds-compiler@4.8.0] to.sql|hdi|hdbcds: Correctly handle `.list` during flattening.
- Improve handling of `.items`.

- [cds-compiler@4.8.0] to.sql|hdi.migration: Turn types and aspects into dummies to reduce CSN size.
- Correctly detect a removed `.default` and forcefully set the default to `null`.

- [cds.java@2.8.1] Fixed a bug that prevents deactivating the draft gc as a side-effect of a draft activation.
- [cds.java@2.7.1] Fixed a bug, causing event-mesh tenant upgrades not to be executed.
- [cds4j@2.8.1] Fixed a bug in code generator causing the event context interfaces being generated for the operations that are renamed with `@cds.java.name`.
- [cds4j@2.8.1] Structured compound foreign keys have priority over flat foreign keys, even if only partially defined.
- [cds4j@2.8.1] Fixed write operations on elements of a projections that are referenced via an alias prefix in the CDS model.
- [cds4j@2.7.1] Fixed a bug causing `ClassCastException` for `BetweenPredicate` in the CQL Statement Builder
- [cds4j@2.7.1] Fixed a bug causing key values to be set to `null` when setting an association to `null` containing the source key in the ON condition
- [cds@7.8.0] Reverted `cds.Association` being derived from `cds.struct`; it's now derived from `cds.type` again.
- [cds@7.8.0] Entity definitions using joins were erroneously marked as `_unresolved`
- [cds@7.8.0] Consistent error messages for query options validation with new parser
- [cds@7.8.0] Validation for mandatory associations which target entities with defaulted keys
- [cds@7.8.0] Transaction handling for aborted streaming requests
- [cds@7.8.0] Create/Update over filtered managed compositions
- [cds@7.8.0] Templates are cached at the model (instead of the service)
- [cds@7.8.0] Deprecation warnings use `cds.log()` in production
- [cds@7.8.0] Single quote in a string in `.where` for remote service
- [cds@7.8.0] Escaped characters in double quoted search term when using `odata_new_parser`
- [cds@7.7.3] `cds.log`: preserve message property of details through stringification (it's non-enumerable if the detail entry is an error)
- [cds@7.7.3] Auto-exposed child entities with multiple restrictions
- [cds@7.7.3] Calculation of read-only values in custom code during creation of new drafts
- [cds@7.7.2] Requests to actions/functions on entities in draft state via navigation.
- [cds@7.7.2] PUT/PATCH with if-none-match: * forces insert
- [cds@7.7.1] JWT authentication for Event Mesh endpoints
- [cds@7.7.1] `cds.log`'s json formatter: ensure `type` is set (required on kubernetes until CLS defaults this)
- [cds@7.7.1] Erroneously generated foreign keys in `req.data` for UPDATE using path expressions
- [cds@7.7.1] `INSERT.columns.rows` for multiple nested composition of aspects
- [cds@7.7.1] Paths passed to `tar` on Windows are now normalized to use forward slashes.
- [cds-mtxs@1.17.0] The `dataEncryption` provisioning parameter is disabled for `t0` when using HANA native tenants.
- [cds-mtxs@1.17.0] Ignore non-existing container if running upgrade `*` by setting `cds.requires['cds.xt.SaasProvisioning'].upgrade.ignoreNonExistingContainers: true`.
- [cds-mtxs@1.17.0] The built-in Service Manager client filters bindings by `ready = true`.

## February 2024 ​

### Added ​

- [cds-dk@7.7.0] Schema support for declaring schema contributions in cds plugins.
- [cds-dk@7.7.0] `cds import` now supports `ref` in schema properties for AsyncAPI files.
- [cds-dk@7.7.0] `cds add html5-repo` is now supported for Cloud Foundry (Beta).
- [vscode-cds@7.6.1] Add preview commands to editor title
- [vscode-cds@7.6.0] Hover over import path of `using` statement shows `README.md` or `package.json#description` if absolute (i.e. module) import
- [cds-compiler@4.7.0] compiler: Virtual elements can now be referenced in expressions in annotation
- [cds.java@2.7.0] Introduced a new API `OutboxService.outboxed(Service)` to wrap services with outbox handling. Events triggered on the wrapper are stored in the outbox first, and executed asynchronously. Relevant information from the `RequestContext` is stored with the event data, however the user context is downgraded to a system user context.
- [cds.java@2.7.0] If the outbox is enabled for Messaging and AuditLog services the new outbox wrapper API is used. The outbox wrapper can be programmatically removed by using `OutboxService.unboxed(Service)`, returning a synchronously operating instance.
- [cds.java@2.7.0] Added properties section `cds.outbox.services` to configure additional outbox services. The previous properties `cds.outbox.persistent` still configure the default outbox services named `DefaultOutboxOrdered` and `DefaultOutboxUnordered`, if they are not configured explicitly within the new section.
- [cds.java@2.7.0] The default outbox used by a Messaging or AuditLog service can now be configured through properties `cds.messaging.services..outbox.name` and `cds.auditlog.outbox.name`.
- [cds.java@2.7.0] Added support for case insensitive contains CQN queries with the `cds-feature-remote-odata` to remote OData V2/V4 services.
- [cds.java@2.7.0] Added support for `CqnBetweenPredicate` in remote OData requests.
- [cds.java@2.7.0] Added OpenTelemetry spans for outbox and draft GC background activity.
- [cds.java@2.7.0] Improved Draft GC to request tenant-specific CDS models only if there is at least one stale draft in the tenant database.
- [cds.java@2.7.0] The goal `add` of the `cds-maven-plugin` supports adding Spring-Boot Security support to a CAP Java project with `-Dfeature=SECURITY`.
- [cds.java@2.7.0] Added beta version of change tracking feature `cds-feature-change-tracking` to capture changes in the database.
- [cds4j@2.7.0] Between predicate (`CqnBetweenPredicate`) using `CQL.between()`
- [cds4j@2.7.0] Code generator: For an enums defined in the CDS model, the constant classes are generated with the constants reflecting the values of the enum members
- [cds4j@2.7.0] Added support for parsing Base64 encoded binary data in a JSON document
- [cds4j@2.7.0] Support `cds.Vector` type on SAP HANA Beta
- [cds@7.7.0] Improved trace output for bootstrap phase. For example try that:js

```
DEBUG=trace cds w bookshop | grep trace
```
- [cds@7.7.0] Support for `@odata.draft.bypass` to allow direct modifications of active instances.
- [cds@7.7.0] `req.user.tokenInfo` for `@sap/xssec`-based authentication (`ias`, `jwt`, `xsuaa`)
- [cds@7.7.0] `cds.fiori.draft_lock_timeout` as successor of `cds.drafts.cancellationTimeout`.Possible values are /^([0-9]+)(h|hrs|min)$/ or a number in milliseconds.

- [cds@7.7.0] There is a new `sap.common.Timezones` entity with a basic time zone definition. There will be accompanying data in package `@sap/cds-common-content`.
- [cds@7.7.0] Deprecation warnings for configuration options `cds.drafts.cancellationTimeout`, `cds.features.serve_on_root`, `cds.features.stream_compat`, `cds.fiori.lean_draft` and `cds.requires.middlewares`, as well as for the properties `req.user.locale` and `req.user.tenant`. The deprecation warnings can be turned off by setting `cds.features.deprecated` to `off`.
- [cds-mtxs@1.16.0] `cds-mtx upgrade` now allows to pass `*` to upgrade all tenants.

### Changed ​

- [cds-dk@7.7.0] `cds add mta` will add `npm ci` to its `before-all` build scripts to make `mbt build` more self-contained.
- [cds-dk@7.6.1] `cds login` now automatically discards invalid refresh tokens and retries instead of exiting with an error.
- [cds-dk@7.6.1] `cds login` now saves the passcode URL received from a failing token request and prints it along with the error and any subsequent passcode prompt.
- [cds-dk@7.6.1] `cds login` now hints at missing user role as the cause of an error, if applicable.
- [vscode-cds@7.6.0] Formatting option `alignAfterKey` option now applies to views and projections as well
- [cds-compiler@4.7.0] Update OData vocabularies: 'Authorization', 'Common', 'Hierarchy', 'UI'.
- [cds-compiler@4.7.0] to.edm(x): `@cds.odata.valuelist` renders all non-key elements of the value help list as `ValueListProperty`.
- [cds.java@2.7.0] Properties section `cds.outbox.persistent` has been deprecated in favor of `cds.outbox.services`.
- [cds.java@2.7.0] Properties `cds.auditlog.outbox.persistent.enabled` and `cds.messaging.services..outbox.persistent.enabled` have been deprecated in favor of the existing `...outbox.enabled` and new `...outbox.name` property.
- [cds.java@2.7.0] System users now generally run with all feature toggles enabled by default. This aligns with the behaviour of the recently introduced `RequestContextRunner.systemUser(String)` methods.
- [cds4j@2.7.0] `CdsAssociationType::getTargetAspect` now returns `Optional` as aspects are always structured
- [cds@7.7.0] The index page now lists all service endpoints, which is important for services that are exposed through multiple protocols.
- [cds@7.7.0] `cds.deploy` improves error diagnostics with deeper `Query` object inspection.
- [cds@7.7.0] Slightly changed the default export for ESM compatibility. This fixed failing ESM imports in Vitest tests.
- [cds-mtxs@1.16.0] The Service Manager polling timeout is increased from 60 to 180 seconds.
- [cds-mtxs@1.16.0] On failing UAA token request, MTXS now responds to client with JSON to enable parsing the passcode URL.

### Fixed ​

- [cds-dk@7.7.0] `cds build` for MTX extensions no longer fails in case of duplicate model definitions.
- [cds-dk@7.7.0] `cds version -i` now prints the same versions in MD form as `cds version`
- [cds-dk@7.6.1] `cds import` now fixed the `AnnotationPath` attribute value import for Annotation in OData V4 EDMX correctly in the CSN.
- [cds-dk@7.6.1] `cds import` will now move the imported EDMX file to `srv/external` only if the import is successful.
- [cds-dk@7.6.1] `cds import` now captures the annotations present within EntityContainer for OData V4 EDMX in the CSN.
- [cds-dk@7.6.1] `cds deploy` allows usage of `SERVICE_REPLACEMENTS` without specifying `VCAP_SERVICES`.
- [cds-dk@7.6.1] `cds deploy` gives an error if its service key corresponds to a Service Manager instance.
- [vscode-cds@7.6.1] Elements snippet now works when annotating artifacts in namespaces and/or contexts or if the brace after the elements is still missing
- [vscode-cds@7.6.0] Removed padding after unary plus, minus or parameter colon
- [vscode-cds@7.6.0] Artifact-elements snippet in `annotate` statement now appears regardless of cursor position between braces (or logs reason for not appearing)
- [vscode-cds@7.6.0] Highlighting after semicolon in certain contexts
- [vscode-cds@7.6.0] On Windows editor potentially no longer updated diagnostics for sources with annotations
- [vscode-cds@7.6.0] Wrong diagnostics about unused imports
- [vscode-cds@7.6.0] First code completion could have been slow as workspace was scanned unnecessarily
- [vscode-cds@7.6.0] Code completion for annotations was not shown in certain cases
- [vscode-cds@7.6.0] `untitled` i.e. new not yet saved files no longer worked in VSCode
- [cds-compiler@4.7.6] OData: Restored compatibility with the Java runtime. Drafts generation was applied twice.
- [cds-compiler@4.7.4] OData: Fixed infinite recursion in draft handling for nested recursive compositions.
- [cds-compiler@4.7.2] Restored compatibility with `@sap/cds-dk` for Java runtime
- [cds-compiler@4.7.0] CDL parser: a `select` after two or more `(`s in an expression or condition could cause some constructs in that query, such as `virtual`, to be not properly parsed.
- [cds-compiler@4.7.0] compiler: published associations with filters sometimes had the filter applied twice if used in inline aspect compositions
- [cds-compiler@4.7.0] to.sql|hdi|hdbcds[.migration]: With `withHanaAssociations`: `false`, remove the association elements from the final CSN in order to correctly detect them during migration scenarios and with generated `hdbcds`.
- Skip expensive processing (for calculated elements and nested projections) if the model doesn't use it.
- Don't greedily set alias on subqueries if not required.
- Remove bound actions and turn all non-database relevant artifacts into dummies to simplify and shrink CSN.

- [cds-compiler@4.6.2] compiler: Fix incorrect error about type properties if deprecated flag `ignoreSpecifiedQueryElements` is set.
- [cds-compiler@4.6.2] Update OData vocabularies: 'Authorization', 'Common'.
- [cds.java@2.7.0] Fixed a bug, causing an `Internal Server Error` if an OData V2 request without `/$value` is sent to a stream entity with a field annotated with `@Core.MediaType`.
- [cds.java@2.7.0] Fixed a bug, causing `FeatureToggleInfoProvider` to be skipped, when using `RequestContextRunner.systemUser(String)` to set a system user context.
- [cds4j@2.7.0] Fixed a bug causing syntax errors in the consumption interfaces that used the global types with an inlined arrayed types
- [cds4j@2.7.0] Fixed a bug, causing wrong signatures being generated for the methods representing an actions and functions with the arrayed arguments or return types
- [cds4j@2.7.0] Fixed a bug, causing virtual structured elements not being ignored outside of filters and where conditions
- [cds4j@2.7.0] Fixed a bug in the Boolean comparison of row values with IS/IS NOT on H2 and SAP HANA
- [cds4j@2.6.1] SAP HANA: Fix "hex enforced but cannot be selected" for subqueries using `LIMIT/OFFSET` in optimizationMode `hex`
- [cds4j@2.6.1] Fixed a bug, causing unexpected manipulations of shared `Expand` objects
- [cds@7.7.0] Persistent outbox must not be used for `t0` tenant.
- [cds@7.7.0] Second `await cds.connect.to('X')`, where initialization of `X` results in an error, did not return.
- [cds@7.7.0] Support additional draft requests.
- [cds@7.7.0] `cds.log` with `null` as argument.
- [cds@7.6.4] Emitting multiple message with an in-memory outbox
- [cds@7.6.4] Occasional crash for invalid draft requests
- [cds@7.6.4] On the index page, additional links now show up again for non-OData services.
- [cds@7.6.4] Handling of thenables for queries
- [cds@7.6.3] Event Mesh webhooks now add standard `before` middlewares in case of custom authorization
- [cds@7.6.3] `compile.to.serviceinfo` no longer fails for services marked with `@protocol:'none'`. Such internal services are not shown in the output.
- [cds@7.6.2] Introduce i18n `BATCH_TOO_MANY_REQ` key for error message: "Batch request contains too many requests"
- [cds@7.6.2] Properly handle `$orderby` in lean draft
- [cds@7.6.2] View resolving in combination with `@cap-js/cds-db`
- [cds@7.6.2] Allow `cds.requires.someService.outbox` to be a string
- [cds@7.6.2] `cds.log`: errors, when not the first argument, were considered objects carrying custom fields
- [cds@7.6.2] `accept` header parsing for OData requests if quality factor `q` is included
- [cds@7.6.2] Broken links on index page if multiple protocols are configured
- [cds-mtx@2.6.7] `provisioning_parameters` set via `cds.mtx.provisioning.container` or `CDS_MTX_PROVISIONING_CONTAINER` are correctly merged into request options.
- [cds-mtxs@1.16.0] `upgrade` action is now also provided by `cds.xt.SmsProvisioningService`.
- [cds-mtxs@1.16.0] Cleanup option of MTXS Migration deletes old `__META__` tenant only if cleanup is triggered for `*` (all tenants).
- [cds-mtxs@1.16.0] Improved formatting of errors when fetching auth tokens.

## January 2024 ​

### Added ​

- [cds-dk@7.6.0] `cds add application-logging` is now supported for Java.
- [cds-dk@7.6.0] `cds add` and `cds init` help shows a more complete list of available commands.
- [cds-dk@7.6.0] `cds bind -2 ` automatically creates service key named `-key` on Cloud Foundry.
- [cds-dk@7.6.0] `cds bind --to-app-services ` binds to all services of a deployed app.
- [cds-dk@7.6.0] `cds build` requires feature toggles to be switched-on in order to get the corresponding features generated.
- [cds-dk@7.6.0] `cds build` supports npm workspace setups Beta.
- [cds-compiler@4.6.0] compiler: Events can now be projections on other structured events and types.
- [cds-compiler@4.6.0] to.cdl: `parseCdl` and `gensrc` style CSN (a.k.a. `inferred` and `xtended`) is now supported as input.
- [cds.java@2.6.0] Optionally handle `$apply` in custom code. Requires setting `cds.odataV4.apply.inCqn.enabled` to `true`.
- [cds.java@2.6.0] Support for calling actions and functions via HCQL has been added to `cds-adapter-hcql` and `cds-feature-remote-hcql`.
- [cds.java@2.6.0] Added Open Telemetry spans for individual requests of an OData $batch request.
- [cds.java@2.6.0] Added Open Telemetry spans for executed CQN statements.
- [cds.java@2.6.0] Support for Cloud SDK 5 (>= 5.2.0) in addition to Cloud SDK 4.
- [cds.java@2.6.0] Entities associated through composition and explicitly annotated with `@odata.draft.enabled: false` are now excluded from the draft tree (incl. `.texts` entities in case of missing `@fiori.draft.enabled` annotation).
- [cds4j@2.6.0] ETag predicate (`CqnEtagPredicate`) for optimistic verification with `CQL.eTag()` and `StructuredType.eTag()` factory methods.
- [cds4j@2.6.0] Add typed query builder API for Update::set
- [cds@7.6.0] `cds.upsert` as shortcut for `cds.db.upsert`
- [cds@7.6.0] Automatic deletion of stale drafts. Feature is enabled if `cds.env.fiori.deletionTimeout` is set to a value of `true`; `true` uses the default timeout of `30d` (30 days).
- [cds@7.6.0] Support for default exports (ESM/TS) in custom authentication
- [cds@7.6.0] Support for executing SAP HANA procedures from SYS schema
- [cds@7.6.0] Support for more complex on-conditions in case of READ requests
- [cds@7.6.0] Best effort mechanism for supporting lambda expressions targeting remote odata-v2 services
- [cds@7.6.0] Support for actions and functions which are bound to singletons
- [cds-mtxs@1.15.0] MTXS now supports subscription via Subscription Manager Service also for Node.js applications.
- [ux-cds-odata-language-server-extension@1.12.2] Enhanced code completion to restrict the suggestions for annotation terms, complex types and properties to more meaningful based on `Validation.ApplicableTerms` set in OData vocabulary definitions .
- [ux-cds-odata-language-server-extension@1.12.2] Enhanced validation to display warning if the usage of annotation terms, complex types and properties is restricted in OData vocabulary definitions with `Validation.ApplicableTerms`.

### Changed ​

- [cds-dk@7.6.0] Json schemas for `build` and `deploy` moved here from `@sap/cds`.
- [cds-dk@7.6.0] cds build plugins can provide additional json schemas, including root nodes Beta.
- [cds-dk@7.6.0] `cds add helm` doesn't expose srv workload in single tenant mode if App Router is present.
- [cds-dk@7.6.0] `cds add hana` also adds draft tables to the `undeploy.json`.
- [cds-dk@7.6.0] `cds build` uses existing `.npmrc` file from project root for the MTX sidecar build, precedence has `.npmrc` in sidecar folder.
- [cds-dk@7.6.0] `cds logout --clear-invalid` also deletes expired tokens.
- [cds-dk@7.5.1] Bump of dependencies
- [cds-dk@7.5.1] MTXS commands will now use a request timeout to avoid hanging on invalid URLs.
- [cds-dk@7.5.1] Error messages for invalid URLs have been improved.
- [cds-dk@7.5.1] Reverting the fix from `7.5.0`: `cds compile` to `openapi` now adds correct schema `$ref` for patch operation.
- [cds-compiler@4.6.0] Update OData vocabularies: 'Aggregation', 'Validation'
- [cds-compiler@4.6.0] to.sql/hdi/hdbcds: Removed warnings for number and type of keys in draft-enabled entities.
- [cds.java@2.6.0] Outbox messages are no longer stored with a `partition` number, but with a `target`, which identifies the outbox service and collector processing the message. The `OutboxService.PERSISTENT_NAME` instance (formerly managing two partitions) was replaced by two distinct outbox services (`OutboxService.PERSISTENT_UNORDERED_NAME` and `OutboxService.PERSISTENT_ORDERED_NAME`) each handling messages with a dedicated `target`. Compatibility with auditlog or messaging events stored in the old format is ensured.
- [cds.java@2.6.0] The OutboxService API has been changed from `enroll(String, String)` to `submit(String, Map)`. The `OutboxMessageEventContext.getMessage()` method now respectively returns `Map` as well.
- [cds.java@2.6.0] `cds.multiTenancy.serviceManager.timeout` has been removed.
- [cds4j@2.6.0] SQLite: `CQL.matchesPattern` now also throws an exception on unsupported patterns to align with H2
- [cds4j@2.6.0] To check for equality of `CdsElement`s obtained from the `CdsModel` they now need to be compared with `equals`
- [cds4j@2.6.0] Optimizations for SAP HANA HEX engine a subselect to search in active entities is avoided
- search can now search from a subquery
- search can now search computed elements
- search does not search the fallback text of localized elements
- enforce searching the fallback text with the annotation `@cds.sql.search.mode: 'localized-association'

- [cds4j@2.6.0] Rename config option `cds.sql.search.use-localized-view: true` to `cds.sql.search.mode: 'localized-view'`
- [cds@7.6.0] Draft: Standard Sorting Behavior for SAP Fiori List Report Floorplan
- [cds@7.6.0] Use new CDS schema for validation and code completion in `package.json` and `.cdsrc.json` files
- [cds@7.6.0] Media Data Streaming OData: Large binaries without `@Core.MediaType` annotation were previously returned as base64-encoded buffer. Starting from this `@sap/cds` version also not-annotated large binaries are ignored by OData. It is strongly recommended to annotate all large binary properties with `@Core.MediaType` and use it according to streaming scenarios.
- Custom Handlers: `SELECT` with explicitly listed `SELECT.columns` of type `cds.LargeBinary` returns them as Readable streams. Large binary columns requested implicitly by `SELECT` (for example, with `.columns('*')`) are ignored.
- Streaming API: `cds.stream()` and `srv.stream()` are deprecated and will be removed with the next major release. Use `SELECT` with a single `cds.LargeBinary` column instead. The resulting object will contain the name of the column and a stream value. For example, `SELECT.one.from(E).columns(['image']).where(...)` returns `{ image:  }`.
- Backward Compatibility: To restore previous behavior use `stream_compat`.

- [cds-mtxs@1.14.3] The temporary workaround for `cds.env.requires.['cds.xt.ModelProvideService'].loadSync = true` is removed. This setting won't have an effect for future versions.

### Fixed ​

- [cds-dk@7.6.0] `cds build` no longer throws `maximum call stack size exceeded` error when building SaaS extensions.
- [cds-dk@7.6.0] `cds add approuter` no longer adds `SUBSCRIPTION_URL` configuration to Java projects in some scenarios.
- [cds-dk@7.6.0] `cds add html5-repo` in combination with `cds add helm` or `cds add helm-unified-runtime` correctly adds HTML5 repo runtime configuration.
- [eslint-plugin-cds@2.6.5] Performance got improved significantly for projects with many non `.cds` files (like `.js` files)
- [vscode-cds@7.5.1] Retrieval of `@sap/cds-dk` global installation path is now more robust in SAP Business Application Studio
- [vscode-cds@7.5.1] Activate extension also for `jsonc` files
- [cds-compiler@4.6.0] compiler:ON-conditions of associations with filters in calculated elements were incorrectly rewritten when included in other entities, and the filter was applied twice in some scenarios.
- redirecting an association with filter did not rewrite paths relative to the redirection target.
- Unknown type references with an explicit named type argument such as `Unknown(length: 10)` crashed.

- [cds-compiler@4.6.0] to.edm(x):`@Core.IsURL` is not rendered in combination with `@Core.MediaType` (V4 only).
- No 'odata-navigation' warning for association targets annotated with `@cds.autoexpose: false`.
- No empty annotation in API, when a non-existent base annotation is annotated (eg. `@Common.Label.@Core.Description` without `@Common.Label`).
- Don't crash if value for `$Type` is not a string.
- Generated foreign keys of type `cds.UUID` that are also primary key are not annotated with `@Core.ComputedDefaultValue`. This is a follow up correction to 4.5.0.

- [cds.java@2.6.0] Fixed a bug, causing the `UnsupportedOperationException` being thrown during creation or an update of an entity with to-one compositions to other entities that are subject to the audit logging.
- [cds.java@2.6.0] The event contexts generated in the fluent style now autocomplete the event context when the method `result(...)` is called. An explicit call to `setCompleted()` is no longer necessary.
- [cds.java@2.6.0] Readded Cloud SDKs resilience implementation as a dependency to `cds-integration-cloudsdk`.
- [cds.java@2.6.0] Fixed a bug, preventing `;` to be used in OData V2 search words.
- [cds.java@2.6.0] Fixed a bug, causing `Number` types (e.g. `Integer`) to `BigDecimal` `ClassCastException` in OData v4 Serializer.
- [cds.java@2.6.0] Fixed a bug, causing `ClassCastException` when using typed service interfaces to call remote OData actions or functions.
- [cds.java@2.6.0] Fixed a bug, which prevents setting the correct tenant for the draft GC after draft activation.
- [cds4j@2.6.0] Fix UnsupportedOperationException on expand by parent-keys with orderBy on result sets > 100
- [cds4j@2.6.0] Fix upserts via projections using element ref paths
- [cds4j@2.6.0] Fix exception that occurs if the name of an element equals the qualified name of its entity
- [cds4j@2.6.0] Queries with inline count and the filters that are always false have inline count set to zero instead of a default value
- [cds@7.6.1] Garbage collection of draft is configured with `cds.fiori.draft_deletion_timeout`
- [cds@7.6.0] `cds.minify` returned a shallow clone. When callers like 2sql `cds.linked` that subsequently, this left the passed-in csn in a broken, partially linked state. Now, `cds.minify` doesn't clone anymore, but modifies the passed in csn.
- [cds@7.6.0] Handling of read-only fields in drafts
- [cds@7.6.0] Event Mesh: Better error message for incoming messages without a topic
- [cds@7.6.0] `cds build` now logs a better error message if an incompatible `@sap/cds` version is used.
- [cds@7.6.0] Better error message for runtime requests to non-existing tenants in extensibility scenario.
- [cds@7.6.0] Do not generate UUIDs for association key during `CREATE` operation.
- [cds@7.6.0] OData aggregation with lean draft
- [cds@7.6.0] Sorting in new odata parser with nested select statements. The default sort order is now added to the outer select statement.
- [cds@7.6.0] Server crash in case of misformatted `groupby` transformation in `$apply`
- [cds@7.6.0] Switched EM webhook endpoints to also use new authentication implementation
- [cds@7.6.0] `odata_new_parser`: better error message and code for expand on non-existing elements
- [cds@7.5.3] `cds.localize` and `cds build` produce `i18n.json` again with keys from all base languages
- [cds@7.5.3] `cds.compile.to.serviceinfo` now correctly parses SpringBoot config with nested objects, e.g. for `cds.odata-v4.endpoint.path`
- [cds@7.5.3] Recommend to use `chai` 4 for the time being, as `chai` 5 doesn't properly work yet (requires ESM, `chai-as-promised` not working)
- [cds@7.5.3] View resolving for entities using property names that are identical to entity names
- [cds@7.5.3] Direct modifications with `cds.fiori.bypass_draft` if `cds.fiori.draft_compat` is not enabled
- [cds@7.5.3] Draft: Field validation error message does not display the name of the field
- [cds@7.5.2] Service-level ETag handling in legacy OData server
- [cds@7.5.2] Only provide model to ModelProvider if extensibility or feature toggles are active
- [cds@7.5.2] OData server driven paging when using feature flags `cds.env.features.odata_new_parser` and `cds.env.features.okra_skip_query_options`
- [cds-mtxs@1.15.0] Additional services needed when using `SERVICE_REPLACEMENTS` for HDI deployment can now also be consumed in Kyma after adding them to the `cds` configuration likejson

```
"requires": {
      "myuserprovided": {
          "vcap": {
              "label": "user-provided",
              "name": "myuserprovided"
          }
      },
```

See also https://help.sap.com/docs/SAP_HANA_PLATFORM/4505d0bdaf4948449b7f7379d24d0f0d/a4bbc2dd8a20442387dc7b706e8d3070.html#environment-variables-for-hdi-configuration
- [cds-mtxs@1.15.0] Temporary files for build and deployment are created in the OS temp directory if file system permissions do not allow the creation in the cds root directory.
- [cds-mtxs@1.14.4] Fixed a `TypeError` in the credentials cache invalidation for HANA deployments.
- [cds-mtxs@1.14.3] i18n translations missing in some Java setups are now correctly resolved.
- [cds-mtxs@1.14.3] CSNs loaded in a worker thread are correctly linked. In earlier versions, this could lead to a stack overflow in projects having `cds.requires.db.schema_evolution: false` and cyclic actions such as this:cds

```
entity C_Books as projection on Books { * } actions {
  action returnSelf() returns C_Books;
}
```
- [cds-mtxs@1.14.3] Sync upgrades for `tenants = *` with `clusterSize > 1` are working correctly.
- [cds-mtxs@1.14.2] `POST /-/model-provider/getEdmx` correctly ad-hoc compiles EDMX files for extended or toggled models.
- [cds-mtxs@1.14.2] `POST /-/model-provider/getEdmx` re-compiles the EDMX if a `model` is passed.
- [cds-mtxs@1.14.2] More resilient retry handling for 'authentication failed' errors in SAP HANA deployments.

### Removed ​

- [cds@7.6.0] Experimental `STREAM` CQN is removed and cannot be used anymore
