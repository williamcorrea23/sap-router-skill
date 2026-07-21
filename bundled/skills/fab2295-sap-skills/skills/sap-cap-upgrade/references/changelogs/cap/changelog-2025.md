<!-- mirror: https://cap.cloud.sap/docs/releases/2025/changelog -->
<!-- fetched: 2026-05-09T02:26:18.965Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# Changelog 2025 ​

Open Source Changelogs

For repositories and plugins that are open source, please check out the respective changelogs in the [cap-js organization](https://github.com/cap-js) and the [CAP Community](https://github.com/cap-js-community).

## December 2025 ​

### Added ​

- [cds-dk@9.5.0] `cds import` now accepts `--into-namespace ` to override the namespace entities are imported to, when importing OpenAPI definitions.
- [eslint-plugin-cds@4.1.1] Top level type definitions for package export
- [cds-mtxs@3.5.0] Deployment now evaluates Cloud Foundry environment variable `VCAP_SERVICES_FILE_PATH`.
- Added support for CDS defined request and response bodies for Spring `@RestController`s. The request and response bodies are validated against the CDS model.
- Support for protocol annotations `@odata`, `@hcql` and others as alternatives to explicit `@protocols` annotations.
- [cds.java@4.5.0] `cds-feature-flow` supports `$flow.previous` to define the transition to a previous state.
- [cds.java@4.5.0] `cds-feature-ucl` now supports SPII version 3.
- [cds.java@4.5.0] Added a check preventing the multiple registrations of destination data providers in JCo's `Environment`.
- [cds.java@4.5.0] The task-based outbox scheduler now supports a new lock strategy, that minimizes database locks. It can be enabled by setting `cds.outbox.persistent.statusLock.enabled` to `true`.
- [cds.java@4.5.0] Added a new outbox counter metric reporting failed message processing attempts.
- [cds.java@4.5.0] Select statements reading media streams are now enforcing a transaction, even if `cds.persistence.changeSet.enforceTransactional` is set to `false`.
- [cds.java@4.5.0] The W3C trace context is now stored with the outbox message and restored upon processing.

### Changed ​

- [cds-dk@9.5.0] `cds add portal` adds the correct service key configuration to the mta.yaml.
- [cds-dk@9.5.0] `cds add sample` creates sample files aligned with recent versions of bookshop and bookstore in https://github.com/capire.
- [cds-dk@9.5.0] `cds add sample` uses a matching ID in generated `manifest.json` and UI5 components.
- [cds-dk@9.5.0] `cds build` uses `hdblogicalschema` and `hdblogicalschemaconfig` plugins in its default `.hdiconfig`.
- [cds-dk@9.5.0] `cds add cloud-logging` adds required dependencies to pom.xml for Java projects.
- [cds-dk@9.5.0] `cds add kyma` is now the only suggested Kyma facet in `cds add help`.
- [cds-dk@9.5.0] `cds add helm-unified-runtime` option is now deprecated; use `cds add kyma --unified-runtime` instead.
- [cds-dk@9.5.0] `cds up --to k8s` now saves the checksum of buildpack images to determine if a rebuild is necessary.
- [cds-dk@9.5.0] `cds up --to k8s` will interactively ask for registry credentials if they don't exist on the remote cluster.
- [cds-dk@9.5.0] `cds build` automatically adds `contentLocalizedEdmx=true` to the java build task configuration if OData V2 is set.
- [cds-dk@9.5.0] `cds add github-actions` has out-of-the-box support for Java projects.
- [cds-dk@9.5.0] `cds add html5-repo` and `cds add app-frontend` do not create a separate ui5-deploy.yaml but use the default ui5.yaml.
- [cds-dk@9.5.0] `cds add` plugins allow merging into non-existing files with `cds.add.merge().into()`.
- [cds-dk@9.5.0] `cds build` tasks that produce `csn.json` now emit the `compile.for.runtime` event, in alignment with other runtime CSN producers like `cds serve`. Plugins can use such events to hook into CSN creation.
- [cds-dk@9.5.0] `cds add xsuaa` sets `credential-types: [ "binding-secret", "x509" ]` for XSUAA instances.
- [cds-dk@9.5.0] `cds add hana` does not create an explicit `.hdiconfig` file any more as `cds build` provides defaults.
- [cds-dk@9.5.0] `cds import` generates the on condition for a composition when the corresponding OData navigation property targets a collection, is contained (`$ContainsTarget` in OData EDM) and has a backlink (`$Partner` in OData EDM).
- [cds-dk@9.5.0] `cds import` now considers OData contained navigation properties as compositions instead of associations.
- [vscode-cds@9.5.0] Minimum VSCode version is now 1.103.1
- [cds-mtxs@3.5.0] Metadata is merged instead of overwritten for resubscriptions.
- [cds.java@4.5.0] `cds-feature-flow` now rejects state transitions when bound entity is in the draft state.
- [cds.java@4.5.0] Calls to the service manager are now performed directly from the current thread and not anymore from a forked cloud SDK thread context.
- [cds.java@4.5.0] Calls to the service manager for single tenant are now limited to one request per configured timeframe to prevent rate limits in service manager.
- [cds.java@4.5.0] Default refresh interval for Service Manager cache (`cds.multiTenancy.serviceManager.cacheRefreshInterval`) has been increased to 20 minutes (previously 2 minutes) to reduce load on Service Manager.
- [cds.java@4.5.0] The task-based outbox collector is now enabled by default.

### Fixed ​

- [cds-dk@9.5.0] `cds add ias` will always add a binding to the MTX sidecar or approuter if required.
- [cds-dk@9.5.0] `cds add ias` has improved support for multitenancy scenarios on Kyma.
- [cds-dk@9.5.0] `cds lint` no longer fails with error code 1 and no message when loading the config fails.
- [cds-dk@9.5.0] `cds version` no longer prints an `undefined` value for `@sap/cds-dk`.
- [cds-dk@9.5.0] `cds compile --flavor files` no longer crashes with a `TypeError`.
- [cds-dk@9.5.0] `cds add workzone` does not add superfluous `destinations` configuration to the `srv-api` import.
- [vscode-cds@9.5.0] Show compilation and other errors only once in status bar.
- [cds-compiler@6.5.2] to.sql|hdi: Don't add superfluous (and actually wrong) parentheses around `UNION`s
- Don't dump with a specific column expressions in the query after a `UNION`

- [cds@9.5.1] Draft child creation in case `cds.features.new_draft_via_action` is enabled
- [cds@9.5.1] Draft messages of declarative constraints
- [cds@9.5.1] Persisted draft messages in case of on-commit errors
- [cds@9.5.1] Async UCL tenant mapping for UCL SPII v2
- [cds@9.5.1] Quoting in `cds.compile.to.yaml`
- [cds-mtxs@3.5.0] `cds login` compatibility with recent `@sap/cds-dk` versions.
- [cds-mtxs@3.5.0] Event `compile.for.runtime` is also triggered when calling `POST/-/cds/extensibility/pull`.
- [cds-mtxs@3.5.0] Startup of MTX does no longer show `cdsc` configuration warning if only defaults are used.
- [cds-mtxs@3.5.0] Concurrency handling with HANA TMS v2 is now more stable.
- [cds.java@4.5.0] Fixed a bug causing an `HTTP 500 Internal Server Error`, when an OData function with a wrong (misspelled) parameter name is called.
- [cds.java@4.5.0] Fixed a bug causing draft-related readonly metadata to be writable through inactive entities.
- [cds.java@4.5.0] Fixed a bug causing an `UriParserSyntaxException`, when using both simplified bound action and key-as-segment syntax in URL for OData v4.
- [cds.java@4.5.0] Fixed a bug preventing custom events to be sent to AuditLogService via the outbox.
- [cds.java@4.5.0] Fixed a bug causing OpenTelemetry spans with unexpected error status in case outbox processors select locked messages.
- [cds.java@4.5.0] Fixed a bug that prevents audit logging for unauthorized request events for applications deployed to Kyma.
- [cds.java@4.5.0] Fixed a bug that prevents audit logging for unauthorized request events for applications deployed to Kyma.
- [cds.java@4.5.0] Fixed a bug causing outdated outbox metrics to be reported to OpenTelemtry.
- [cds.java@4.5.0] Fixed a bug causing POJO arguments being accepted for unsupported events.
- [cds.java@4.5.0] Fixed a bug that prevents correct transaction isolation in nested non-transactional changeset contexts.
- [cds.java@4.5.0] Fixed a bug in `cds-feature-change-tracking` causing changes of associations written in Update statements as, for example, `assoc.code` to generate changelogs of the wrong type.

## November 2025 ​

### Added ​

- [cds-compiler@6.5.0] compiler: remove all special restrictions for references after an `exists` predicate (backends might introduce restrictions relevant for them)
- support runtimes to improve draft handling (calc elements, column expressions)

- [cds-compiler@6.5.0] for.odata/to.edm(x): `is (not) null` operator is now supported in annotation expressions
- in OData version 2, all elements of the `DraftAdministrativeData` EntityType get the annotation `UI.HiddenFilter` with value `true`
- artifacts annotated with `@cds.external: 2` are now processed by the OData backend

- [cds-compiler@6.5.0] to.sql: the `exists` predicate can now be defined as a filter condition on the leaf of the `from` path i.e. `select from Books[exists author]` is equivalent to `select from Books where exists author`

- [cds.java@3.10.5] Deep authorizations now support conditions with paths for exists predicates in @restrict predicates.
- [cds.java@3.10.5] Calls to the service manager for single tenant can now be limited to one request per configured timeframe to prevent rate limits in service manager.
- [cds.java@3.10.5] Implemented maximum cache size and expiration time after access for `TenantAwareCache`, configurable via `cds.model.provider.cache` properties.
- [cds4j@4.5.0] Enable `$self` in subqueries, columns and where.
- [cds4j@4.5.0] Allow to use session context variables on the select list.
- [cds4j@4.5.0] Support search within elements of type `cds.Map`.
- [cds4j@4.5.0] Support calculated elements in `_drafts` entities.
- [cds4j@4.5.0] Support Fiori Tree Table (recursive hierarchy) requests on SQLite.
- [cds@9.5.0] Support for Declarative Constraints (`@assert`; beta)
- [cds@9.5.0] Status Transition Flows (`@flow`; beta): Aspect `sap.common.FlowHistory` automatically appended to entities with a `@to: $flow.previous`Deactivate via `cds.features.history_for_flows=false`
- Experimental: Via `cds.features.history_for_flows='all'`, all entities with a flow definition get appended
- Note: FlowHistory is not maintained within drafts

- Support for `@flow.status: ` on entity level
- UI annotation generation adds action to UI automatically (Object Page and List Report) but hidden in draft mode
- Experimental support for CRUD flows: Pseudo bound actions `CREATE` and `UPDATE` events can be flow-annotated Note: The `CREATE` event cannot have a `@from` condition

- Pseudo bound actions for drafts `NEW`, `EDIT`, `PATCH`, `DISCARD`, and `SAVE` can be flow-annotated Note: Flow annotations inside drafts (`@from`, `@to`) are processed as in standard flow transitions, with the following exceptions: The `NEW` event cannot have a `@from` condition
- The `DISCARD` event cannot have a `@to` condition

- [cds@9.5.0] Support for pseudo protocols
- [cds@9.5.0] Support for Async UCL tenant mapping notification flow
- [cds@9.5.0] `flush` on a queued service returns a Promise that resolves when immediate work (i.e., not scheduled for future) is processed
- [cds@9.5.0] For draft-enabled entities, IsActiveEntity=true can be omitted from url
- [cds@9.5.0] Support for `@Common.DraftRoot.NewAction` annotation with feature flag `cds.features.new_draft_via_action`Generic collection bound action `draftNew` will be added to draft enabled entities
- The action specified in the annotation will be rewritten into a draft `NEW` event
- Active instances of draft enabled entities can be created directly via `POST`

- [cds@9.5.0] Limited support for `$compute` query option: computed properties are only supported in `$select` at the root level, not in expanded entries or other query options. Only numeric operands and operators `add`, `sub`, `-`, `mul` and `div` are supported
- [cds@9.5.0] `ias-auth`: configurable name for XSUAA fallback's `cds.requires` entry
- [cds@9.5.0] `enterprise-messaging`: Support for scenario `ias-auth` with XSUAA fallback
- [cds@9.5.0] Service configuration through `VCAP_SERVICES` can now be supplied with `VCAP_SERVICES_FILE_PATH`. Note that this is an experimental CF feature.
- [cds-mtxs@3.4.4] [Pre-Alpha] Warning in case of multiple containers per BTP Tenant with HANA TMS v2.
- [cds-mtxs@3.4.4] Improved handling of `retry-after` header in case of rate limiting errors.
- [cds-mtxs@3.4.4] Maximum tolerated waiting time after a 429 response can be configured by setting `cds.requires.multitenancy.containerManager.maxRetryAfter` (in ms). Default is 5000.

### Changed ​

- [cds-compiler@6.5.0] compiler: report an error for an `annotate` on non-existent definitions with security-relevant annotations (`@restrict`, `@requires`, `@ams.…`)
- [cds-compiler@6.5.0] Update OData vocabularies: Capabilities, Common, Hierarchy
- [cds.java@4.4.2] Calls to the service manager are now performed directly from the current thread and not anymore from a forked cloud SDK thread context.
- [cds.java@4.4.2] HANA user switch logs "Reconnect connection for user" is now logged with level `DEBUG`.
- [cds.java@4.4.2] Introduces service manager parameter singleReadInterval to restrict the number of single credential reads to one call per tenant and interval.
- [cds4j@4.5.0] Optimized SQL for aggregations over associations.
- [cds4j@4.5.0] Externalized the converter methods that don't need a `CdsModel` from the `CdsJsonConverter` to `CdsCoreJsonConverter`.
- [cds4j@4.5.0] Annotations `@cds.java.name` or `@cds.java.this.name` on the service rename its wrapper interface accordingly.
- [cds4j@4.5.0] Resulting Java type of arithmetic expression is now determined by type propagation.
- [cds4j@4.5.0] Map elements in builder interfaces now have return type `StructuredType` to allow accessing subelements via `get`.
- [cds4j@4.5.0] The SQL for calculated elements CTEs now selects all non-virtual elements instead of a select `*`.
- [cds@9.5.0] Internal service `UCLService` moved into non-extensible namespace `cds.core`
- [cds@9.5.0] Status Transition Flows (`@flow`; beta): UI annotation generation is on by default. Switch off via `cds.features.annotate_for_flows=false`.
- Feature flag `cds.features.compile_for_flows` renamed to `cds.features.annotate_for_flows`

- [cds@9.5.0] `DELETE` requests during draft edit, that do not use containment will cause persisted draft messages to be cleared
- [cds-mtxs@3.4.4] [Pre-Alpha] Upgrade for list of tenants does no longer work with `cds.requires.multitenancy.jobs.clusterSize` > 1 (default is 3). Required TMS API has been disabled.
- [cds-mtxs@3.4.4] [Pre-Alpha] When setting `cds.requires['cds.xt.DeploymentService'].hdi.create.cleanup_hana_tenants = true`, the deletion will no longer throw an error if deletion fails because of other containers remaining.

### Fixed ​

- [cds-dk@8.9.11] Bump dependencies in shrinkwrap.
- [cds-compiler@6.5.0] compiler: make an annotation `@cds.autoexpose: false` on an aspect used as `Composition` target have the desired effect (similar on `cds.common.TextsAspect`)
- [cds.java@3.10.5] Fixed a bug causing `DRAFT_PATCH` events to fail with annotation validation errors, if update statements without key filters in the statement's ref are executed.
- [cds.java@3.10.5] Fixed a bug causing SQL exceptions when trying to write to the `DraftMessages` element of an entity. `DraftMessages` are considered readonly.
- [cds.java@3.10.5] Calls to the service manager are now performed directly from the current thread and not anymore from a forked cloud SDK thread context.
- [cds4j@4.5.0] Fixed nested aggregations over associations.
- [cds4j@4.5.0] Fixed conversion of predicates on select list to SQL.
- [cds4j@4.5.0] Fixed issue with duplicate column names when updating managed elements using setter methods.
- [cds4j@4.5.0] Fixed a `NullPointerException` in correlated subqueries using `$outer`.
- [cds4j@4.5.0] Fixed a `CdsElementNotFoundException` when resolving select statement with `Aggregate` transformation.
- [cds4j@4.5.0] Fixed a bug in CDS model reader, causing the entities to have wrong names when there are overlaps in naming between the entities and the services.
- [cds4j@4.5.0] Fixed superfluous nodes in hierarchy subsets with `keepStart = false`.
- [cds4j@4.5.0] Fixed exception when using inline within expand.
- [cds4j@3.10.5] Fixed deep update via views with path expressions.
- [cds4j@3.10.5] Support `byId()` in tenant discriminator mode.
- [cds@9.5.0] Correctly format values in a where clause send to an external OData service, when the expression order is: value, operator, reference
- [cds@9.5.0] cds.ql: tolerate extra spaces after in; parse RHS arrays of values as list
- [cds@9.5.0] CRUD-style API: `cds.read()` et al. used without `await` do not throw if there is no database connected
- [cds@9.5.0] Unnecessary compilation of model for edmx generation in multitenancy cases
- [cds@9.5.0] Using `req.notify`, `req.warn` and `req.info` in custom draft handlers by collecting validation errors in a dedicated collection
- [cds@9.5.0] `cds.auth` factory: passed options take precedence
- [cds@9.5.0] `cds deploy --dry` no longer produces broken SQL for DB functions like `days_between`.
- [cds@9.5.0] Read-after-write for create events during draft choreography will no longer include messages targeting siblings
- [cds@9.5.0] `before` and `after` handlers now really run in parallel. If that causes trouble, you can restore the previous behavior with `cds.features.async_handler_compat=true` until `@sap/cds@10`.
- [cds@9.5.0] Escaping of JSON escape sequences during localization
- [cds@9.5.0] Persisted draft messages in case of on-commit errors
- [cds@9.4.5] Custom error message for `@assert.range`
- [cds@9.4.5] For hierarchy requests with `$filter`, properly remove inner `where` clause
- [cds@9.4.5] Calling a parameterless function with parameter
- [cds@9.4.5] Aligned error handling for path navigation and `$expand`
- [cds@9.4.5] Input validation immediately rejects for `@mandatory`
- [cds@8.9.7] Reject navigations in `$expand` without parsing the navigation path
- [cds@8.9.7] Aligned error handling for path navigation and `$expand`
- [cds-mtxs@3.4.4] The `PUT` and `set` API of the Extensibility Service now work more stable with parallel requests handled by many application instances.
- [cds-mtxs@3.4.4] CDS Plugins are now loaded properly when running the `cds-mtx` command.

## October 2025 ​

### Added ​

- [cds-dk@9.4.1] `cds add app-frontend` is supported as an alias to `cds add app-front`.
- [cds-dk@9.4.1] `cds add attachments` is supported for Java projects.
- [cds-dk@9.4.0] `cds add app-front` adds configuration for the new SAP BTP Application Frontend service.
- [cds-dk@9.4.0] `cds add ias` has improved support for XSUAA hybrid projects.
- [cds-dk@9.4.0] `cds add multitenancy` automatically adds upgrade hooks for Node.js projects.
- [cds-dk@9.4.0] `cds deploy` support the generic `--resolve-bindings` option to resolve all bound services. This is helpful for use cases with multiple `hana`-tagged service bindings.
- [cds.java@4.4.0] New annotation `@odata.draft.gc: false` can be used to disable draft GC for an entity.
- [cds.java@4.4.0] `cds-feature-flow` now supports annotations `@from` and `@to` as synonyms to `@flow.from` and `@flow.to`. The status value can now also be specified as enum reference with a leading `#`.
- [cds.java@4.4.0] The `resolve` goal of the `cds-maven-plugin` now makes CDS reuse models available globally in the project. They can thus can be imported within all CDS files. Module-specific resolution can be achieved by setting the new configuration `to` to `${project.build.directory}`.
- [cds.java@4.4.0] Enabled programmatic definition of the application UI URL in multitenant applications that is returned upon a tenant subscription.
- [cds.java@4.4.0] Support calling OData bound actions and functions without service namespace prefix.
- [cds.java@4.4.0] `@readonly` processing can now be skipped for certain statements, by setting hint `@readonly` with value `false`.
- [cds.java@4.4.0] The goal `add` of the `cds-maven-plugin` supports adding the Attachments Plugin to a CAP Java project.
- [cds.java@4.4.0] Support string concatenation function `concat` in both OData V4 and V2, e.g. `$filter=concat(element,'string_value')`
- [cds.java@4.4.0] Deep authorizations now support conditions with paths for `exists` predicates in `@restrict` predicates.
- [cds.java@4.3.2] Implemented maximum cache size and expiration time after access for `TenantAwareCache`, configurable via `cds.model.provider.cache` properties.
- [cds4j@4.4.0] Support for the `@open` annotation in 'CdsJsonConverter'.
- [cds4j@4.4.0] Improved logging of search resolution.
- [cds4j@4.4.0] Added a new `CQL.in` method to simplify building `in` predicates from `CdsResult`.
- [cds4j@4.4.0] Added new methods to `CQL` to simplify building typed references.
- [cds4j@4.4.0] Support `concat` function and `||` operator in CQN for strings concatenation.
- [cds4j@4.4.0] Support aggregating over associations in columns and where clause.

### Changed ​

- [cds-dk@9.4.3] `cds add github-actions` will use the `cap-js/cf-setup` action from GitHub marketplace instead of creating a local copy.
- [cds-dk@9.4.3] `cds add containerize` omits the Unix-based `before_all` scripts in `containerize.yaml` in favor of a cross-platform compatible `cds up --to k8s` integration.
- [cds-dk@9.4.3] `cds up --to k8s` now uses built-in containerization, eliminating the hard dependency on the `ctz` library.
- [cds-dk@9.4.3] `cds up --to k8s` will interactively ask for a domain if it can't be determined from the current Kubernetes configuration.
- [cds-dk@9.4.3] `cds build --for hana` no longer requires `.hdbgrants` and `.hdbrevokes` to be specified as a plugin in the `.hdiconfig` file.
- [cds-dk@9.4.3] `cds import` no longer emits usage info when invoked with the dry option.
- [cds-dk@9.4.2] `cds add containerize` does not add app module installations scripts to its `containerize.yaml`. Use `cds up --to k8s` instead.
- [cds-dk@9.4.2] `cds add` is less eager with respect to changing unaffected configuration.
- [cds-dk@9.4.2] `cds add ias` adds less unnecessary configuration in combination with the HTML5 repository.
- [cds-dk@9.4.2] `cds add test` includes the service name in the test suite description.
- [cds-dk@9.4.0] `cds add typescript` and `cds add typer` will now add a `path` entry in the project's tsconfig.json or jsconfig.json respectively, which will mitigate resolution problems with `@cap-js/cds-types`.
- [cds-dk@9.4.0] `cds add multitenancy` adds the `with-mtx` profile to Java apps by default, simplifying local development.
- [cds-dk@9.4.0] `cds import` for EDMX files now maps `Edm.String` types to `cds.String` (before: `cds.LargeString`). Background is that some databases don't support the resulting `NCLOB` type in key fields.
- [cds-dk@9.4.0] `cds build` will now remove dev dependencies starting with `workspace:`, `file:`, as well as the entire `workspace:` block therein, and regenerate the package-lock.json if needed.
- [cds-dk@9.4.0] `cds import` for EDMX correctly imports multiline strings in `DefaultValue`.
- [cds-dk@9.4.0] `cds import` now writes annotations from EDMX files in a flat, i.e. non-structured manner, so that they can be processed by the application runtime.
- [cds-dk@9.4.0] `cds bind` does not fail when setting the profile via `CDS_ENV`.
- [cds-dk@9.4.0] `cds version` is more robust with respect to Java versions.
- [cds.java@4.4.0] The mock users security configuration is now also disabled when setting `cds.security.authentication.authConfig.enabled` to `false`.
- [cds4j@4.4.1] The log level for messages "Query in view ... is not supported by CDS model reader..." was changed from `WARN` to `DEBUG`.
- [cds4j@4.4.0] Optimized hierarchical queries for HANA with `level` > 0. The parameter `depth` is set to `level` + 1 to reduce calculation time.
- [cds4j@4.4.0] No deep data copy during statement normalization.
- [cds-mtxs@3.4.3] [Pre-Alpha] `hana_tenant_prefix` is now mandatory to ensure a unique HANA tenant for `t0`.

### Fixed ​

- [cds-dk@9.4.3] `cds add data` fixes an issue where randomly generated `Decimal` and `Integer` values could exceed their defined precision or scale.
- [cds-dk@9.4.3] `cds add pipeline` does not add UI5 template files in some cases.
- [cds-dk@9.4.3] `cds add ias` does not write to the `mta.yaml` for non-MTA projects.
- [cds-dk@9.4.3] `cds add ias` automatically adds the `authenticationType` to `xs-app.json` if required.
- [cds-dk@9.4.3] `cds add ias` adds a binding to the approuter component if required.
- [cds-dk@9.4.3] `cds import --from ...` yields a better error message for unknown import kinds.
- [cds-dk@9.4.2] `cds add ams` followed by `cds add mta` correctly generates the AMS deployer module.
- [cds-dk@9.4.2] `cds add hana` does not fail if there's no `.cdsrc.json`.
- [cds-dk@9.4.2] `cds up` doesn't try to create a symlink to the monorepo package-lock.json if a submodule-local one already exists.
- [cds-dk@9.4.2] `cds add test` creates correct OData URLs with unqualified entity names in service paths.
- [cds-dk@9.4.2] `cds add http` skips contained composition targets.
- [cds-dk@9.4.2] `cds add sample` no longer comes with an error when creating a Book through Fiori.
- [cds-dk@9.4.2] `cds build` now places the `i18n` folder in the generated output root directory instead of nested locations.
- [cds-dk@9.4.1] `cds import` adds latest version 4 of `@sap-cloud-sdk` packages.
- [cds-dk@9.4.1] `cds add sample` now uses Integer IDs for Books and Authors again, instead of UUIDs.
- [cds-dk@9.4.0] `cds add html5-repo` avoids some superfluous configuration combination with `cds add portal`.
- [cds-dk@9.4.0] `cds add handler` ignores external services.
- [cds-dk@9.4.0] `cds add audit-logging` correctly adds the dependency in the Chart.yaml for Helm deployments.
- [cds-dk@9.4.0] `cds deploy --to hana` works with user-provided HANA services.
- [cds-dk@9.4.0] `cds bind` doesn't add the `custom-service:` prefix for Node.js any more.
- [cds-compiler@6.4.6] compiler: a references to an element of the target in a filter for associations inside an annotation expression does not lead to a compiler message requesting users to provide the annotation themselves (regression with v6.4.4)
- [cds-compiler@6.4.4] compiler: properly rewrite references in arguments of associations in annotation expressions
- a references to a variable (`$user.id`, …) in a filter of an annotation expression does not lead to a compiler message requesting users to provide the annotation themselves
- improve code completion in annotation expressions: the editor can display valid names for references even if the expression does not properly end by `)`

- [cds-compiler@6.4.4] to.sql: reject `$self` in infix filter following exists predicate instead of just ignoring the filter expression
- properly add comparison for the `tenant` discriminator to the `join` condition of `localized` views if the non-published option for tenant support is set (regression with v6.4.0)

- [cds-compiler@6.4.2] parser: improve error recovery with empty expression as annotation value
- avoid clutter in message text for syntax errors: use `‹Value›` instead of listing value tokens

- [cds-compiler@6.4.2] compiler: fix suppression of warnings when annotating backend-generated things like draft entities or localized convenience views
- [cds-compiler@6.4.2] to.sql|hdi|hdbcds: don’t report unjustified errors when projecting structured elements and calculated elements had been used (regression with v6.4.0)
- [cds.java@4.4.1] Fixed a bug that no default ON handler was registered for the new `APP_UI_URL` event in `DeploymentService` without multi tenancy enabled.
- [cds.java@4.4.0] Fixed an issue causing an event to be acknowleged even if the processing failed in case of a custom outbox handler throwing an exception.
- [cds.java@4.4.0] Fixed a bug causing an Exception `Comparison Or Logical expression MUST have a left and right expression` when requesting `$metadata` with `$format=json` for expressions with constants.
- [cds.java@4.4.0] Fixed incorrectly placed `@Order` annotations on security configurations. Make sure to place `@Order` annotations on the `SecurityFilterChain` bean method, instead of on the configuration class.
- [cds.java@4.4.0] `cds-feature-change-tracking` performance is improved when large number of entities are inserted.
- [cds.java@4.4.0] Fixed a bug causing ETags validations to unexpectedly fail in combination with activated DraftMessages.
- [cds.java@4.3.2] Fixed a bug causing `CdsModel` instances to pile up in memory and cause out of memory errors.
- [cds4j@4.4.1] Fixed exception on aggregating over associations when using the static query builder API.
- [cds4j@4.4.0] Anonymous aspects used for composition of aspect, now get a proper `@CdsName` annotation and `CDS_NAME` constant generated during code generation.
- [cds4j@4.4.0] Fixed exception when using `exists` predicates on the select list.
- [cds4j@4.3.2] Fixed deep update via views with path expressions.
- [cds4j@4.3.2] Fixed usage of `byId` with models using tenant discriminator.
- [cds@9.4.4] Input validation of action parameters in action calls on draft state of draft enabled entities
- [cds@9.4.4] Input validation on `NEW` event of draft choreography
- [cds@9.4.4] Ignore outbox model on Windows
- [cds@9.4.4] `enterprise-messaging-shared`: preserve error listener during reconnect
- [cds@9.4.3] Don't continue validation user input if data type is wrong
- [cds@9.4.3] UI annotation generation for status transition flows for Java
- [cds@9.4.3] Increased minimium version of `@sap/cds-compiler` to 6.3.x
- [cds@9.4.3] Undefined error message for early access checks
- [cds@9.4.2] `DISCARD` as a synonym for `CANCEL`
- [cds@9.4.2] `cds.load()` called twice
- [cds@9.4.1] Default `kind` for unknown required service to `hcql`
- [cds@9.4.1] Consider and allow aliases from nesting during OData query validation
- [cds-mtxs@3.4.3] Deployment errors when activating extensions do no longer appear as base64 encoded text in the logs.
- [cds-mtxs@3.4.3] The `cds.cdsc.tenantDiscriminator` setting is ignored by the sidecar.
- [cds-mtxs@3.4.3] [Pre-Alpha] Upgrade for list of tenants now works properly again with `cds.requires.multitenancy.jobs.clusterSize` > 1 (default is 3).
- [cds-mtxs@3.4.3] [Pre-Alpha] Creation of tenant containers for a BTP tenant or `t0` for different applications now works more stable.
- [cds-mtxs@3.4.3] When pushing or adding extensions via API, the extension validation now checks the edmx for the configured odata version.
- [cds-mtxs@3.4.3] Update of the application URL via Subscription Management Dashboard now works correctly.
- [cds-mtxs@3.4.2] [Pre-Alpha] Subscription when using HANA TMS v2 now filters all options that are incompatible.
- [cds-mtxs@3.4.1] Annotation validation now works correctly when using `extend  with `.
- [cds-mtxs@3.4.1] [Pre-Alpha] Subscription triggered by BTP when using HANA TMS v2 works again.
- [cds-mtxs@3.4.1] The profile `[with-mtx]` doesn't override database configuration for non-MTX usage.
- [cds-mtxs@3.4.1] Improved resilience for SaaS registry and Subscription Manager callbacks.

## September 2025 ​

### Added ​

- [cds-dk@9.3.0] `cds bind -a` is now also supported for Kyma, where the app prefix can be passed for `-a`, e.g. `bookshop-srv`.
- [cds-dk@9.3.0] `cds build --for hana` now trims leading and trailing whitespaces in csv-Files if build option `trimCsvWhitespaces` is set.
- [cds-dk@9.3.0] `cds add github-actions` sets required `permissions`.
- [cds-dk@9.3.0] `cds up` supports a deployment layout where approuter or portal service configuration is in a top-level `.deploy` folder.
- [cds-dk@9.3.0] `cds add ias` sets the `access-token-format` to `jwt` by default.
- [cds-compiler@6.4.0] compiler: `annotate … with @extension.code: [..., 'additional code']` even works if no value for that annotation has been provided with the base definition.
- [cds-compiler@6.4.0] to.sql: Calculated elements can now be used next to (but not in) nested projections.
- [cds-compiler@6.4.0] to.edm(x): The `@cds.api.ignore` annotation can now be applied to actions, functions, and their parameters.
- [cds.java@4.3.0] Added new `run` methods to return typed results for typed queries.
- [cds.java@4.3.0] Spring Boot applications now show CAP Java banner.
- [cds.java@4.3.0] Spring Boot applications now print link to an index page when run locally.
- [cds.java@4.3.0] The SQL for to-one path expressions can now be optimized by avoiding joins if a FK column can be selected instead. Set `cds.sql.toOnePath.mode` to `optimize` to enable this optimization.
- [cds4j@4.3.0] Support `hana.` as prefix for SAP HANA specific SQL statement hints.
- [cds4j@4.3.0] The code generator avoids clashes with some methods from parent interfaces or classes by adding a suffix '_' to the method name.
- [cds4j@4.3.0] Support data modification via views with `where` condition.
- [cds4j@4.3.0] Optimized SQL for managed to-one paths by avoiding joins to the association target if possible and selecting the foreign key instead (`cds.sql.toOnePath.mode: optimize`).
- [cds4j@4.3.0] Support for deserializing arrays of simple types in 'CdsJsonConverter'.
- [cds@9.4.0] Status Transition Flows (`@flow`; alpha):Resolve enum references in `@from`/`@to` values
- Support for `@to: $flow.previous` (transition to the previous status in a flow) Use `cds.env.features.flows_history_stack=true` to switch from history (default) to stack-based behavior
- Requires adding aspect `sap.common.FlowHistory` to the respective entity

- [cds@9.4.0] `i18n` translations for `@assert` messages
- [cds@9.4.0] `SELECT ... .stream ()` returns the data from the database as a raw stream
- [cds@9.4.0] `cds.validate` treats `@insertonly` elements as immutable
- [cds@9.4.0] Vietnamese translations for texts from `@sap/cds/common`
- [cds@9.4.0] `ias`/`jwt`/`xsuaa`-auth: Add token payload (as `token_payload`) to warning log in case of an invalid tokenNote: Some invalid tokens are (for performance reasons) not fully validated and, hence, the payload may not be trusted!

- [cds-mtxs@3.3.1] [Pre-Alpha] By setting `cds.requires['cds.xt.DeploymentService'].hdi.create.cleanup_hana_tenants = true`, the unsubscribe operation will also try to remove the corresponding HANA tenant.
- [cds-mtxs@3.3.0] The number of unbound entities added via extensions can now be restricted via their namespace:jsonc

```
"extension-allowlist": [
 {
  "for": ["my.new"],
  "new-entities": 1
 }]
```
- [cds-mtxs@3.3.0] [Pre-Alpha] Support for HANA TMSv2.

### Changed ​

- [cds-dk@9.3.0] `cds add sample` provides more i18n translations.
- [cds-dk@9.3.0] `cds add ias` sets the `xsuaa-cross-consumption` field to `true` by default.
- [vscode-cds@9.3.0] Minimum VSCode version is now 1.101.2
- [cds-compiler@6.4.0] to.sql: generation of localized convenience views now use the ON-condition of the `localized` element to create the FROM clause.

- [cds.java@4.3.0] The `cds-services-archetype` now generates a `srv/pom.xml` with some useful default settings for the code generation.
- [cds4j@4.3.0] DiffProcessor: Throw exception on entries with non-unique key.
- [cds4j@4.3.0] Improved performance of the projection data resolver and element reference parsing.
- [cds@9.4.0] `SAVE` handlers for drafts are triggered when a draft is activated Opt-out until cds^10 with `cds.features.compat_save_drafts=true`

- [cds@9.4.0] Improved default error messages for input validation.
- [cds@9.4.0] Renamed error key for validation errors of `@mandatory` from `ASSERT_NOT_NULL` to `ASSERT_MANDATORY`For i18n message lookup, an automatic fallback is implemented.
- Opt-out until cds^10 with `cds.features.compat_assert_not_null=true`

- [cds@9.4.0] Errors are collected for `_initial` (internal!) and `before` phase

### Fixed ​

- [cds-dk@9.3.2] `cds add html5-repo` avoids some superfluous configuration combination with `cds add portal`.
- [cds-dk@9.3.2] `cds import` correctly imports OData v2 EDMX files with `Edm.Time` properties having a precision.
- [cds-dk@9.3.1] `cds add ias` correctly sets the `subscription-manager` dependencies endpoint for Node.js.
- [cds-dk@9.3.1] `cds add data --records` respects the max length of a string field when it is annotated with `@Communication.IsEmailAddress`
- [cds-dk@9.3.1] `cds add data --records --format csv` correctly escaping complex properties nested within structs.
- [cds-dk@9.3.1] `cds add data --records` correctly generates values for structs in cases when the entity and the struct, used by the entity, have both a property with the same name.
- [cds-dk@9.3.1] `cds add html5-repo` also binds the `html5-repo-host` service to the approuter.
- [cds-dk@9.3.1] `cds up` has improved support for setups with multiple microservices.
- [cds-dk@9.3.1] `cds add mta` will add no `role-collections` parameters if there are some specified in `xs-security.json`.
- [cds-dk@9.3.1] `cds add github-actions` correctly generates a release workflow.
- [cds-dk@9.3.1] `cds add github-actions` uses a simplified and more resilient Kyma setup script.
- [cds-dk@9.3.1] `cds import` now correctly imports EDMX files with empty NavigationPropertyPath tags.
- [cds-dk@9.3.1] `cds import` now correctly imports OData v2 EDMX files with `Edm.Time` properties, which have a precision.
- [cds-dk@9.3.0] `cds add workzone` with missing `sap.app` config in `manifest.json` does not throw a `TypeError`.
- [cds-dk@9.3.0] `cds add ias` adds a subdomain-less application URL in `redirect_uris`.
- [vscode-cds@9.4.0] Code completion for annotations: In certain cases proposals added a superfluous `@` character
- Entries in annotation expressions could be shown twice
- SQL functions could have been suggested in annotation expressions

- [vscode-cds@9.4.0] Semantic highlighting of annotations could not be enabled. User setting name is now changed to `cds.contributions.features.semanticHighlighting`
- [vscode-cds@9.3.0] Element names are now correctly highlighted even without type specification
- [cds-compiler@6.4.0] parser: minor improvements in error reporting and error recovery
- [cds-compiler@6.4.0] to.sql: columns selecting variables did not always get a column alias.
- when excluding a structure, the SQL backend incorrectly emits `wildcard-excluding-one`.

- [cds-compiler@6.3.6] to.sql: Topological ordering of views did not always account for subqueries (fixes regression from v5.9.0)
- [cds-compiler@6.3.4] parser: Keep parentheses around lists on the right side of an `in` operator.
- [cds-compiler@6.3.4] compiler: For calculated elements using associations with filters and cardinality, CSN recompilation could fail for `gensrc` CSN, as happens for MTX.
- [cds-compiler@6.3.2] to.sql: Fix internal inconsistency when handling nested projections.
- [cds-compiler@5.9.12] to.sql: Topological ordering of views did not always account for subqueries (fixes regression from v5.9.0)
- [cds-compiler@5.9.10] parser: Keep parentheses around lists on the right side of an `in` operator.
- [cds-compiler@5.9.10] compiler: For calculated elements using associations with filters and cardinality, CSN recompilation could fail for `gensrc` CSN, as happens for MTX.
- [cds.java@4.3.1] Fixed a bug causing `DRAFT_PATCH` events to fail with annotation validation errors, if update statements without key filters in the statement's ref are executed.
- [cds.java@4.3.1] Fixed a bug causing SQL exceptions when trying to write to the `DraftMessages` element of an entity. `DraftMessages` are considered readonly.
- [cds.java@4.3.1] Fixed a bug causing issues when returning `CdsResult` in an event handler method.
- [cds.java@4.3.1] Fixed a bug causing an event to be acknowledged even if the processing failed in case of a custom outbox handler throwing an exception.
- [cds.java@4.3.0] Enabling draft messages no longer breaks UI behaviour on UI5 versions before `1.135.0`.
- [cds.java@3.10.4] Fixed a bug in `cds-feature-change-tracking` causing duplicate changelog entries for association elements that are also keys.
- [cds.java@3.10.4] Fixed a bug, causing authorization predicate to appear in all `where` clauses of `Select` statements using `Select` statements in their `from` clauses.
- [cds4j@4.3.0] Fixed result structure of deep updates on projections.
- [cds4j@4.3.0] Fixed ClassCastException in CdsData.getPath, getPathOrDefault and containsPath on non-map values.
- [cds4j@4.3.0] Fixed SQL error due to missing CTE for queries with paths over runtime views.
- [cds4j@4.3.0] Fixed a regression from 4.1.0 where inserts on views with `null` values for aliased to-one paths incorrectly triggered deep inserts into the path target without data.
- [cds4j@4.3.0] Fixed FK propagation for deletes in deep update & upsert.
- [cds4j@4.3.0] Resolved a bytecode incompatibility issue in the `Result` interface that was introduced in version 4.2.0.
- [cds@9.4.0] Duplicate reconnects in AMQP
- [cds@9.4.0] `ASSERT_FORMAT` errors return correct regexp in message
- [cds@9.4.0] Crash by draft validation with (custom) error w/o target
- [cds@9.4.0] Fixed issue where `' $'` in payloads of batch requests would be prefixed with `'/'`
- [cds@9.4.0] Broken link `cds.auth`
- [cds@9.4.0] Persist original error message in draft validation messages
- [cds@9.4.0] Escaping of `\t` and `\f` in edmx during localization
- [cds@9.4.0] Escaping of JSON escape sequences other than `\"` during localization
- [cds@9.3.1] In messaging services, propagated headers (e.g. `x-correlation-id`) will not be automatically propagated for `format: 'cloudevents'`
- [cds@9.3.1] Avoid deprecation warning for `cds.context.user.tokenInfo`
- [cds@9.3.1] Consider `@Capabilities.ExpandRestrictions.NonExpandableProperties` annotation and ignore fields referenced by the annotation, when rewriting asterisk expand into columns
- [cds-mtxs@3.4.0] Extension validation now properly check unbound entities.
- [cds-mtxs@3.3.1] [Pre-Alpha] Container determination for HANA TMS v2 now fails correctly if no containers exist.
- [cds-mtxs@3.3.1] Subscription Manager and Saas Registry Service can now be used in parallel (hybrid use).
- [cds-mtxs@3.3.0] Better support for `readOnlyRootFilesystem` in Kubernetes.

### Removed ​

- [vscode-cds@9.4.0] Temporary user setting `cds.workspace.fastDiagnosticsMode`. The default so far `clear` is now the only mode.

## August 2025 ​

### Added ​

- [cds-compiler@6.3.0] compiler: Column casts can now use more modifiers such as `default` directly.
- [cds-compiler@6.3.0] for.odata/to.edm(x):New option `draftUserDescription` is now available. It adds the fields `CreatedByUserDescription`, `LastChangedByUserDescription`, `InProcessByUserDescription` to the `DraftAdministrativeData` entity.

- [cds-compiler@6.3.0] to.sql:Structures with only one element can now be compared to scalar values. This also applies to associations with only one foreign key.
- `cds.UInt8` can now be used in SQL dialects "h2" and "postgres".
- Managed associations can now be used in comparisons, e.g. `assoc = struct`.
- Structures and managed associations with only one element can be compared with scalars, e.g. `struct = 1`.
- In the draft use case, the `DRAFT.DraftAdministrativeData` entity now includes the following fields by default: `CreatedByUserDescription`, `LastChangedByUserDescription`, `InProcessByUserDescription`, and `DraftMessages`.

- [cds@9.3.0] New method `collect()` has been added to `LinkedCSN`, which can be used like that:js

```
const federated_entities = cds.linked(csn).collect (d => d.is_entity && d['@federated'])
```
- [cds@9.3.0] Remote services can now be configured without `kind`, for example:json

```
{ "cds": { "requires": { "SomeService": true }}}
```
- [cds@9.3.0] Automatic protocol selection is applied if a required service is configured as above and the remote services is served via multiple protocols. For example, if the above service would be declared like that, the best protocol would be chosen automatically (`hcql` in this case):cds

```
@hcql @rest @odata service SomeService {...}
```
- [cds@9.3.0] Method `cds.connect.to()` now allows to connect to remote services with just an http url. For example use that from `cds repl` like that:js

```
srv = await cds.connect.to ('http://localhost:4004/hcql/books')
await srv.read `ID, title, author.name from Books`
```
- [cds@9.3.0] Property `cds.User.authInfo` as generic container for authentication-related informationFor `@sap/xssec`-based authentication strategies, `cds.context.user.authInfo` is an instance of `@sap/xssec`'s `SecurityContext`

- [cds@9.3.0] Support for state transition flows (`@flow`):Generic handlers for validating entry (`@from`) and exit (`@to`) states
- Automatic addition of necessary annotations for Fiori UIs (`@Common.SideEffects` and `@Core.OperationAvailable`) during compile to EDMX with feature flag `cds.features.compile_for_flows = true`

- [cds@9.3.0] Experimental support for consuming remote HCQL services (`cds.requires..kind = 'hcql'`)
- [cds@9.3.0] Infrastructure for implementing the tenant mapping notification of Unified Customer Landscape's (UCL) Service Provider Integration Interface (SPII) APIBootstrap the `UCLService` via `cds.requires.ucl = true` and implement the assign and unassign operations like so:js

```
// custom server.js
cds.on('served', async () => {
  const ucl = await cds.connect.to('ucl')
  ucl.on('assign', async function(req) { ... })
  ucl.on('unassign', async function(req) { ... })
})
```
- Currently, only the synchronous interaction pattern is supported!

- [cds@9.3.0] The targets of `@Common.Text` are added to the default search targets
- [cds@9.3.0] Patch Level Validations are enabled by default. Opt-out with `cds.fiori.draft_messages=false`
- [cds@9.3.0] Enable custom aggregations for currency codes and units of measure
- [ux-cds-odata-language-server-extension@1.18.6] Added more code completion suggestions to improve adding annotations to annotations with scalar or array values
- [ux-cds-odata-language-server-extension@1.18.6] Added more code completion suggestions for annotations using shortcut syntax
- [ux-cds-odata-language-server-extension@1.18.6] Added a diagnostic message for the deprecated `$value` syntax

### Changed ​

- [cds-dk@9.2.1] `cds add github-actions` adds `if: always()` to the scripts retrieving Cloud Foundry logs.
- [cds-dk@9.2.1] `cds up` uses a default timeout of 10 minutes for Helm upgrades.
- [cds-dk@9.2.1] `cds bind` works out-of-the-box for PostgreSQL databases.
- [cds-dk@9.2.1] `cds bind -a` gives warning if no services are bound to the targeted app.
- [vscode-cds@9.2.1] OData Annotation Modeler's sub features can be enabled distinctively. For performance reasons, only code completion and hover information are enabled by default. Enable others via user settings: `cds.contributions.features.`
- [vscode-cds@9.2.1] Performance optimizations when updating dependency net of CDS file dependencies
- [cds-compiler@6.3.0] Update OData vocabularies: Common
- [cds-compiler@6.3.0] cdsc: EDMX output uses XML comments as service separators instead of `//`. If there is only one service, no header is printed, allowing piping the output to a file.
- [cds-compiler@6.3.0] to.sql: path expressions which end in a foreign key are now always optimized to use the element of the source side.
- [cds@9.3.0] `UCLService` only pushes the application template to UCL if `cds.requires.ucl.applicationTemplate` is present
- [cds@9.3.0] `cds.User.tokenInfo` is deprecated. Use `cds.context.user.authInfo.token` instead.
- [cds@9.3.0] Undocumented compat `cds.context.http.req.authInfo` is deprecated. Use `cds.context.user.authInfo` instead.
- [cds@9.3.0] Delete all persisted draft messages, when the first request targeting a draft child without containment is handled.
- [cds@9.3.0] cds build now trims leading or trailing whitespace characters for all values in CSV files deployed to SAP HANA.

### Fixed ​

- [cds-dk@9.2.1] `cds add github-actions` won't try to merge a `cf-info` action if there's an existing `mta.yaml`.
- [cds-dk@9.2.1] `cds add workzone` with missing `sap.app` config in `manifest.json` does not throw a `TypeError`.
- [cds-dk@9.2.1] `cds compile --to xsuaa` generates roles for `@requires` in bound actions.
- [cds-dk@9.2.1] `cds add lint` now adds proper configuration to enable linting of JavaScript and TypeScript files in VS Code.
- [cds-dk@9.2.1] `cds add mta` does no longer adds services in `mta.yaml` for plugins coming from `devDependencies`.
- [vscode-cds@9.2.1] Using paths which end with a folder name were not resolved correctly
- [vscode-cds@9.2.1] Formatter support for `==` operator
- [cds-compiler@6.3.0] compiler: Redirecting associations to non-query entities was fixed.
- [cds-compiler@6.3.0] to.sql/to.edm(x): References to associations can now be compared to other associations and structures.
- [cds-compiler@6.3.0] to.sql: Referencing a foreign key of an `@cds.persistence.skip` entity previously caused an error in queries. Now the foreign key in the source entity is resolved and rendered.
- [cds@9.3.0] Errors when reading complementary drafts
- [cds@9.3.0] Apply configurations in case `cds.env` was loaded before `cds.log` is initialized.
- [cds@9.3.0] `req.diff` resolves correctly deleted nested composition by deep update
- [cds@9.3.0] `cds-deploy` did not terminate correctly even though deployment was successful
- [cds@9.3.0] Requests to an unimplemented unbound action/ function are rejected
- [cds@9.3.0] Custom app-service implementations configured through `cds.requires.app-service.impl` is now correctly resolved (again)
- [cds@9.3.0] Validation of UUID format for navigation by key
- [cds@9.2.1] Check whether token validation was configured
- [cds@9.2.1] `UPDATE(Foo).with`foo=${'bar'}`erroneously constructed the equivalent of`UPDATE(Foo).with`foo=bar` instead of `UPDATE(Foo).with`foo='bar'`
- [cds@9.2.1] Errors in emits for file-based messaging are thrown
- [cds@9.2.1] Queue: Ensure `method`, `path`, `entity` and `params` are correctly taken over when creating tasks
- [cds@9.2.1] Reject navigations in `$expand` without parsing the navigation path

### Removed ​

- [cds-compiler@6.3.0] for.odata/to.edm(x): The `addAnnotationAddressViaNavigationPath` option has been removed. Its functionality is included in the `draftMessages` option.
- [cds@9.3.0] Internal property `cds.services._pending` was removed => use `cds.services` instead.
- [cds@9.3.0] Internal property `srv._is_dark` was removed => use `!srv.endpoints?.length` instead.
- [cds@9.3.0] Internal method `cds.env.requires._resolved` was removed => use `cds.requires` instead.
- [ux-cds-odata-language-server-extension@1.18.6] Removed code completion suggestions with the deprecated `$value` syntax

## July 2025 ​

### Added ​

- [cds-dk@9.1.1] shipping an `index.d.ts` file containing a subset of the dk types now.
- [cds-dk@9.1.0] `cds add test` to generate test files for CDS services [experimental]
- [cds-dk@9.1.0] `cds debug --no-devtools` allows to skip opening the developer tools.
- [vscode-cds@9.2.0] goto implementation for NodeJS services, entities, events, actions and functions, services and entities for Java
- [vscode-cds@9.1.3] Formatting options `whitespaceBeforeColonInParamList` and `whitespaceAfterColonInParamList` to control whitespace around colons in parameter lists
- [vscode-cds@9.1.0] Performance/Responsiveness: Reduce "lagging red underline" while typing - configurable via user setting `cds.workspace.fastDiagnosticsMode`
- Outdated compilations in background are aborted fast. This increases responsiveness and reduces CPU usage and is especially useful for large projects with many files.

- [vscode-cds@9.1.0] Formatter: New option `argsInNewLine` to put multiple arguments to e.g. function calls on a new line
- [vscode-cds@9.1.0] Outline/Workspace Symbols: use distinct icons for `Association` and `Composition` elements
- [cds-compiler@6.2.0] parser: CDL-casts in queries now support all type expressions, e.g. `field : many String not null`.
- [cds-compiler@6.2.0] compiler: Association paths in annotation expressions can now end with a filter, e.g. `@anno: (assoc[1=1])`.
- [cds.java@4.2.0] Added support for the `$apply` queries in Remote OData.
- [cds.java@4.2.0] Added support for filter restriction annotations `@Capabilities.FilterRestrictions.Filterable`, `@Capabilities.FilterRestrictions.RequiresFilter`, `@Capabilities.FilterRestrictions.RequiredProperties` and `@Capabilities.FilterRestrictions.NonFilterableProperties` by setting `cds.query.restrictions.enabled` to `true`.
- [cds.java@4.2.0] Added support for expand restriction annotations `@Capabilities.ExpandRestrictions.MaxLevels`, `@Capabilities.ExpandRestrictions.Expandable` and `@Capabilities.ExpandRestrictions.NonExpandableProperties` by setting `cds.query.restrictions.enabled` to `true`.
- [cds.java@4.2.0] Change-tracked root entities will now respect `@cascade: { delete }` on the `changes` association and no longer write changelogs in case the entity is deleted. All changelogs of that entity are removed together with the entity.
- [cds.java@4.2.0] The token issuer (e.g. the subscriber IAS tenant host) is now propagated for outboxed events by default.
- [cds.java@4.2.0] Validation annotations `@mandatory`, `@disabled`, `@assert.range` and `@assert.format` now support custom messages, by defining the annotation `.message` with an error text or message bundle key.
- [cds.java@4.2.0] The `DraftService.run` methods now delegate to their respective counter-parts for draft patch and cancel, when statements explicitly target inactive entities.
- [cds.java@4.2.0] The `Result.single()` method now throws a ServiceException with http status code 404, if no entity is available and `cds.errors.preferServiceException` is set to `true`.
- [cds.java@4.2.0] OData V4 adapter now supports ETags for Remote OData entities where ETag element is not known. Such entities must be annotated with the annotation `@odata.etag` on the entity level. The ETag value is stored in the metadata container and provided as plain ETag predicate.
- [cds.java@4.1.0] Event handlers can now return objects of arbitrary types. They are put into the EventContext as `result` and set the context as completed.
- [cds.java@4.1.0] Event handler methods can now use arguments of type `StructuredType` and its entity-specific subclasses in their signature. The given (typed) reference is the one of the event's CQN.
- [cds.java@4.1.0] Event handler methods can now use arguments of type `Service` and its subclasses in their signature. The provided service is the one the event is emitted on.
- [cds.java@4.1.0] Actions and functions in OData V4 now support returning media streams.
- [cds.java@4.1.0] Remote OData supports reading and writing streamed properties.
- [cds.java@4.1.0] Feature `cds-feature-change-tracking` creates correct change links for statements targeting items of compositions when these statements contain path from the root given that this path references keys.
- [cds.java@4.1.0] Introduced a new setting `cqnServiceGetters` for the `generate` goal of the CDS Maven Plugin. When enabled the method `getService()` in generated `EventContext` interfaces is overridden to return the typed service interface.
- [cds4j@4.2.0] Introduced `Optional returns()` for `CdsOperation` in reflection API reflecting `returns` parameter of actions and functions.
- [cds4j@4.2.0] Support Fiori Tree Table (recursive hierarchy) requests on PostgreSQL (beta).
- [cds4j@4.2.0] Introduced a new result supertype `CdsResult` that can be typed with the entity row type.
- [cds4j@4.2.0] Introduced a new `StructuredType` sub-interface which can link query builder interfaces with accessor interfaces.
- [cds4j@4.2.0] Option to disable runtime cascade delete via Delete statement hint `cascade.delete: false`.
- [cds4j@3.10.3] Support query hint `cds.sql.runtimeView.mode` to override the runtime view mode for a select statement.
- [cds@9.2.0] `srv.schedule` allows to specify the time in a more readable way, e.g. `srv.schedule(...).after('1min')`
- [cds@9.2.0] Support for `jwt`/`xsuaa`-auth on XSA
- [cds@9.2.0] Enable `@sap/xssec`'s caching mechanisms (requires `@sap/xssec^4.8`) The signature cache can be configured via `cds.requires.auth.config`, which is passed to `@sap/xssec`'s authentication services
- The token decode cache can be configured programmatically via `require('@sap/xssec').Token.enableDecodeCache(config?)` and deactivated via `require('@sap/xssec').Token.decodeCache = false`

- [cds@9.2.0] `cds.requires` correctly resolve service credentials on Kyma when its merged env configuration is only `true` and the service is found via its property name.
- [cds@9.2.0] `ias`-auth: Support for fallback XSUAA-based authentication meant to ease migration to IAS The fallback is automatically enabled if XSUAA credentials are available. To enable the credentials look-up, simply add `cds.requires.xsuaa = true` to your env.
- In case you need a custom config for the fallback (passed through to `@sap/xssec` as is!), configure it via `cds.requires.xsuaa = { config: { ... } }`

- [cds@9.2.0] Better error message if `cds.xt.Extensions` table is missing in extensibility scenarios.

### Changed ​

- [cds-dk@9.1.1] `cds add http` now generates auth headers with `:` separators again, as this is the only separator supporting empty passwords with the RestClient extension in VS Code. (For use with IntelliJ, separate username and password with a blank.)
- [cds-dk@9.1.0] `cds add helm` doesn't route the subscription callbacks through the app router any longer.
- [cds-dk@9.1.0] `cds lint` now uses local copy of `eslint` help content.
- [cds-dk@9.1.0] `cds add cloud-logging` will correctly add the Helm dependency to `Chart.yaml`.
- [vscode-cds@9.1.1] Maximum log-file size can now be increased to at most 1 GB (default limit unchanged at 10 MB)
- [vscode-cds@9.1.0] Minimum VSCode version is now 1.99.0
- [vscode-cds@9.1.0] Formatter: Chained method-like function calls are now broken into separate lines
- [cds-compiler@6.2.0] compiler: Annotation `@extension.code` is no longer propagated.
- [cds-compiler@6.2.0] Update OData vocabularies: Common
- [cds-compiler@6.2.0] The list of CDL keywords was updated for the latest CDL grammar.
- [cds-compiler@6.2.0] to.cdl: Foreign keys of managed associations are only rendered explicitly if the compiler can't infer them when recompiled.
- [cds-compiler@6.2.0] cdsc: The command `parseCdl` was renamed to `parse`, since it also supports CSN input.
- [cds.java@4.1.0] The SMS dependencies endpoint triggered during subscription now supports the hybrid mode with SaaS Registry and XSUAA. In that case it only returns the own XSUAA binding as a dependency.
- [cds.java@3.10.3] The SMS dependencies endpoint triggered during subscription now supports the hybrid mode with SaaS Registry and XSUAA. In that case it only returns the own XSUAA binding as a dependency.
- [cds4j@4.2.0] Constant temporal literals are now rendered as constants in SQL instead of as parameters.
- [cds4j@4.2.0] Select statements that only have virtual elements on the select list don't throw a `select * not expected` error anymore.
- [cds4j@4.1.1] Runtime Views: Only generate CTEs for association targets if required for join.
- [cds4j@3.10.3] Aligned runtime view mode annotation name with config property.
- [cds@9.2.0] Upgrade to Peggy 5 version
- [cds@9.2.0] Enabled conversion of `not exists where not` to OData `all`, integrating the inverse of the policy applied by the OData parser.
- [cds@9.2.0] Numeric values in `.csv` files are now returned as numbers instead of strings, e.g. `1` instead of `'1'`; when pre-padded with zeros, e.g., `0123`, they are returned as strings, e.g. `'0123'` instead of `123`.
- [cds-mtxs@3.2.0] The `metadata` field in t0's tenants table supports more than 5000 characters.
- [cds-mtxs@3.2.0] Improved resilience for subscriptions after incomplete unsubscriptions.
- [cds-mtxs@2.7.5] The `metadata` field in t0's tenants table supports more than 5000 characters.
- [ux-cds-odata-language-server-extension@1.18.2] Updated to support latest changes in OData annotation vocabularies

### Fixed ​

- [cds-dk@9.1.3] Fix installation issues with version 9.1.2.
- [cds-dk@9.1.2] CVE-2025-7783: vulnerability with `form-data` versions <4.0.4.
- [cds-dk@9.1.2] `cds build --for hana` no longer excludes external entities when not in mocking mode.
- [cds-dk@9.1.1] `cds deploy --to hana --no-build` now works correctly
- [cds-dk@9.1.1] fixed bug in call from SAP Business Application Studio wizard
- [cds-dk@9.1.0] `cds add hana` for Java correctly adds the HANA dependencies to `chart/Chart.yaml`.
- [cds-dk@9.1.0] `cds add xsuaa` for Java doesn't throw an error when the `.cdsrc.json` is not existing.
- [cds-dk@9.1.0] `cds build --for fiori` stores EDMX files again relative if `dataSources.mainService.settings.localUri` in UI5's `manifest.json` is a relative path.
- [cds-dk@9.1.0] `cds add ams/ias` add the `repository` in combination with `cds add helm-unified-runtime`.
- [cds-dk@9.1.0] `cds add xsuaa` adds a wildcard prefix to the domain name to allow for multitenancy use cases.
- [cds-dk@9.1.0] `cds add portal` for Java binds the HTML5 repo runtime and portal service to the Java server instead of the MTX sidecar, to allow for CAP Java built-in dependencies resolution.
- [cds-dk@9.1.0] `cds repl --run` can now run again w/o `@cap-js/cds-test` installed.
- [cds-dk@9.1.0] `cds push` and other commands now handle request errors more robustly
- [cds-dk@9.1.0] `cds debug` now also honors the `--host` parameter when it starts `cds watch`.
- [vscode-cds@9.1.3] Workspace symbols could have been incomplete due to a bug in the where-used index
- [vscode-cds@9.1.1] Colons in type paths are no longer aligned with other colons, nor are they padded with spaces
- [vscode-cds@9.1.0] Formatter: Original empty lines are now correctly preserved before single-lined blocks
- Separate alignment of annotations before resp. within projection-like entities

- [cds-compiler@6.2.2] compiler: `@extension.code` was accidentally restricted to non-expression values.
- [cds-compiler@6.2.0] compiler: Calculated elements can now have a localized type.
- Associations in sub-queries of an `order by` of a `UNION` are now redirected.

- [cds-compiler@5.9.8] compiler: Calculated elements can now have a localized type
- [cds.java@4.2.0] Fixed a bug causing message targets in OData V4's `sap-messages` header to miss the `$Parameter/` prefix when referring to action or function parameters.
- [cds.java@4.2.0] Fixed ClassCastException in DraftScenarioAnalyzer on pass-through search.
- [cds.java@4.2.0] Fixed a bug in the goal `cds` of the `cds-maven-plugin` that caused this goal to fail, if the version output of `cds version` contains an `undefined`.
- [cds.java@4.2.0] Fixed a bug that can cause connection leaks in remote OData batch requests.
- [cds.java@4.2.0] Fixed a bug causing `*` not to be recognized as "all-active" in a user's feature list.
- [cds.java@4.2.0] Fixed a bug causing typescript-based UI5 webapp links to miss on the index page.
- [cds.java@4.2.0] Fixed a bug in `cds-feature-change-tracking` causing duplicate changelog entries for association elements that are also keys.
- [cds.java@4.2.0] Fixed a bug, causing authorization predicate to appear in all `where` clauses of `Select` statements using `Select` statements in their `from` clauses.
- [cds.java@4.1.1] Update CDS4j to 4.1.1 with performance improvements for TreeTable on H2.
- [cds.java@4.1.0] Fixed a bug, causing UnauthorizedRequestEvent not to be logged with the AuditLogService.
- [cds.java@4.1.0] Fixed a bug, causing exceptions to be thrown in case errors were written to `Messages` in an `@After` handler.
- [cds.java@4.1.0] Fixed a bug, causing `Select` queries extended with conditions generated from `@restrict` annotations to be always false for drafts.
- [cds.java@4.1.0] Fixed a bug, causing the ETag header to miss on OData V4 responses, when targeting entity properties.
- [cds.java@4.1.0] Fixed a bug, causing a huge number of Service Manager calls, when it returned with a rate limit error code.
- [cds.java@3.10.3] Fixed a bug, causing exceptions to be thrown in case errors were written to `Messages` in an `@After` handler.
- [cds.java@3.10.3] Fixed a bug, causing `Select` queries extended with conditions generated from `@restrict` annotations to be always false for drafts.
- [cds.java@3.10.3] Fixed ClassCastException in DraftScenarioAnalyzer on pass-through search.
- [cds4j@4.2.0] Fixed upserts on projections w/ (forward-mapped) assocication paths
- [cds4j@4.2.0] Fixed a bug, enforcing UUID normalization on UUID keys with OData Type `Edm.String` in deep updates.
- [cds4j@4.2.0] Fixed unsupported method ProxyList.removeIf
- [cds4j@4.2.0] Fixed a bug in `CdsJsonConverter` causing an exception when parsing a JSON object with a Map type field.
- [cds4j@4.2.0] Fixed a bug causing exceptions in the methods `keys()` and `keyValues()` of the interface `Path` when underlying data use immutable maps.
- [cds4j@3.10.3] Gracefully handle forward mapped associations with unsupported on condition on the select list instead of throwing UnsupportedOperationException
- [cds@9.2.0] Runtime error in transaction handling in messaging services when used with outbox
- [cds@9.2.0] Always use `cds.context` middleware for `enterprise-messaging` endpoints
- [cds@9.2.0] Crash during Location header generation caused by custom response not matching the entity definition.
- [cds@9.2.0] Support for logging of correct error locations with `cds watch` and `cds run`.
- [cds@9.2.0] Double-unescaping of values in double quotes during OData URL parsing
- [cds@9.2.0] Throw explicit error if the result of a media data query is not an instance of `Readable`, rather than responding with `No Content`
- [cds@9.2.0] When loading `.csv` files quoted strings containing the separator (comma or semicolon) where erroneously parsed as two separate values instead of one.
- [cds@8.9.6] Batch insert using `INSERT.entries()` on draft enabled entities
- [cds@8.9.5] `req.diff` in case of draft entities using associations to joins/unions
- [cds@8.9.5] Locale detection does not enforce `.query` to be present. Some protocol adapters do not set it.
- [cds@8.9.5] View metadata for requests with $apply
- [cds@8.9.5] Handling of bad timestamps in URL ($filter and temporals)
- [cds-mtxs@3.2.0] `cds.requires.html5-host` and `cds.requires.html5-runtime` can be used as shortcuts to define SaaS dependencies with `cds-mtxs` version 3 again (using CAP plugin technique).
- [cds-mtxs@3.2.0] Job configuration is merged if specified both in `cds.requires.multitenancy` and `cds.requires['cds.xt.SaasProvisioningService']` or `cds.requires['cds.xt.SmsProvisioningService']`.
- [cds-mtxs@2.7.5] Initialization of `t0` tenant using `cds-mtx-migrate --init-tenant-list` now uses the database_id of any existing tenant.
- [ux-cds-odata-language-server-extension@1.18.2] False positive diagnostic for enum references in annotation expressions.
- [ux-cds-odata-language-server-extension@1.18.2] False positive diagnostic for a single path in expression

## June 2025 ​

### Added ​

- [cds-compiler@6.1.0] for.odata: Introduce a new option `addAnnotationAddressViaNavigationPath` to annotate services containing draft-enabled entities with `@Common.AddressViaNavigationPath`.
- Introduce a new option `draftMessages` that enhances the draft generation logic.

- [cds.java@4.0.0] Introduced a new setting `betterNames` for the `generate` goal of the CDS Maven Plugin. This enables technical conversions to better support CDS models with names with characters invalid for Java identifiers or clashing with Java keywords.
- [cds4j@4.1.0] Generated `EventContext` interfaces now provide an overriden `getService()` method which returns the generated service interface or `CqnService`.
- [cds4j@4.1.0] Support query hint `cds.sql.runtimeView.mode` to override the runtime view mode for a select statement.
- [cds4j@4.1.0] Support Fiori Tree Table (recursive hierarchy) requests on H2 (beta).
- [cds4j@4.0.0] Value.length() to determine the length of a String value
- [cds4j@4.0.0] Added new switch `betterNames` to the code generator configuration to introduce the following conversions: the names from CDS entities that match Java keywords are suffixed with `_`.
- the characters `/` and `$` are treated as `_` during conversion to camel case or screaming case.
- the leading `_` in elements remains in the resulting names.
- the characters that are not valid for Java identifiers are replaced with `_` in the resulting name.

- [cds4j@4.0.0] Added the public API `CdsJsonConverter` (beta) to convert JSON to `CdsData` and vice versa.
- [cds4j@4.0.0] Added support for calculated elements (`null as LimitedDescendantCount : Int16`, etc.) in hierarchical views (projected entities only).
- [cds4j@4.0.0] Added support for match predicates `anyMatch`/`allMatch` in filters of recursive Hierarchies.
- [cds@9.1.0] CDS config schema validations for `cds.requires.auth.tenants`, `cds.cdsc`, `cds.query`, `cds.log`, `cds.server`
- [cds@9.1.0] Queue option `targetPrefix` to prefix `target` value of `cds.outbox.Messages` entries for microservice isolation
- [cds@9.1.0] Basic support for CRUD for hierarchy entities

### Changed ​

- [cds-dk@9.0.6] `cds build` now adds an `engines.node = ">=20"` entry to the effective package.json iff it is missing from the project's package.json to avoid engine confusion when deploying to Cloud Foundry
- [cds-dk@9.0.6] `cds add` without any flag now shows the help (`cds add --help`) instead of throwing an error
- [cds-dk@9.0.5] `cds init` uses latest Maven Java archetype version 4.0.2 for creating Java projects.
- [vscode-cds@9.0.2] Telemetry now requires the user to install `SAP Business Application Studio Toolkit` extension
- [cds-compiler@6.1.0] Update OData vocabularies: Capabilities, Common
- [cds-compiler@6.0.12] Update OData vocabularies: 'Common', 'Hierarchy'
- [cds.java@4.0.0] Runtime views are now by default rendered via CTEs pushing the projection into the SQL. Set `cds.sql.runtimeView.mode: resolve` to use the previous mode, which resolved projections explicitly by transforming CQN statements.
- [cds.java@4.0.0] Renamed `cds.multiTenancy.subscriptionManager.clientCertificateHeader` to `cds.security.authentication.clientCertificateHeader`.
- [cds.java@4.0.0] Renamed `cds.multiTenancy.security.internalUserAccess.enabled` to `cds.security.authentication.internalUserAccess.enabled`.
- [cds.java@4.0.0] Security checks have been hardened by enabling the following properties by default: `cds.security.authorization.deep.enabled`, `cds.security.authorization.instanceBased.rejectSelectedUnauthorizedEntity.enabled` and `cds.security.authorization.instanceBased.checkInputData.enabled`.
- [cds.java@4.0.0] Translations for error messages for built-in input validation annotations are now enabled by default. You can disable these translations by setting `cds.errors.defaultTranslations.enabled` to `false`.
- [cds.java@4.0.0] Subscription hooks in `com.sap.cds.feature.mt.lib.subscription.exits` from former MT library have been deprecated. Use event handler for `DeploymentService` instead.
- [cds4j@4.1.0] Improved SQL for nested runtime views in CTE mode and calculated elements on read.
- [cds4j@4.0.0] Runtime views are now by default rendered via CTEs. Set `cds.sql.runtimeView.mode: resolve` to use the resolve mode.
- [cds4j@4.0.0] StructDataParser now rejects non-array nodes as value for to-many associations.
- [cds4j@4.0.0] With cds-compiler 6 (cds 9) `$now` in projections is replaced by the value of the session variable `now`.
- [cds4j@4.0.0] Removed deprecated function Xpr.length(), use Xpr.size() instead.
- [cds4j@4.0.0] Removed deprecated configuration parameters `sharedInterfaces` and `uniqueEventContexts` from code generator.
- [cds4j@4.0.0] Removed deprecated `Modifier.selectListValue(Value)`, use `selectListValue(SelectableValue)` instead.
- [cds4j@4.0.0] Removed deprecated `CqnSearchPredicate`, use CqnSearchTermPredicate instead.
- [cds4j@4.0.0] Removed deprecated `SelectableValue::withoutAlias()`.
- [cds4j@4.0.0] Removed deprecated `Modifier::search(String term)`, use `Modifier::searchTerm(CqnSearchTermPredicate)` instead.
- [cds@9.1.0] Reduced the amount of SELECT nesting the OData adapter does for `$apply` queries.
- [cds@9.1.0] Better error messages for unresolved parent associations in hierarchy requests
- [cds@9.1.0] Enabled updated behavior of `draftActivate` to move updates to fields of draft enabled entities with type `cds.LargeBinary` from draft to active table on the database level, with feature flag `cds.env.fiori.move_media_data_in_db`.
- [cds-mtxs@3.1.0] `cds.requires.multitenancy.jobs.clusterSize` is set to 3 by default.
- [cds-mtxs@3.1.0] `cds.requires.multitenancy.jobs.workerSize` is set to 4 by default.

### Fixed ​

- [cds-dk@9.0.5] `cds build` for extensions now filters built-in entities such as `cds.outbox.Messages` to fix the extension upload with `cds push`.
- [cds-dk@9.0.5] `cds add data` now correctly works for nested structured properties.
- [cds-dk@9.0.5] `cds add data/http` no longer create decimal numbers with too many precision places
- [cds-dk@8.9.5] Bump `tar-fs` to address CVE-2024-12905.
- [cds-dk@8.9.5] `cds add data` now correctly works for nested structured properties.
- [cds-dk@8.9.5] Help text of `cds debug`.
- [cds-compiler@6.1.0] compiler: The ternary condition operator `…?…:…` is now right-associative as usual (in v5, chaining it like in `…?…:…?…:…` was not possible without parentheses).
- [cds-compiler@6.0.14] to.sql: Fix error when calculated element refers to a localized element.
- [cds-compiler@6.0.14] to.edm(x): Correctly handle `PropertyPath` in a collection when using expressions as annotation values
- [cds-compiler@6.0.12] compiler: Fix artifact refs in annotated annotation expressions, i.e. the `Type` inside `annotate … with @SomeAnno: (cast( … as Type ))`.
- [cds-compiler@6.0.12] to.sql: Checks around managed associations for mocked entities have been relaxed.
- [cds-compiler@6.0.12] to.edm(x): Resolved a crash caused by references in annotation expressions that were not properly updated.
- [cds-compiler@5.9.6] to.sql: Fix error when calculated element refers to a localized element.
- [cds-compiler@5.9.6] to.edm(x):Fix errors for service entities containing multiple path steps (e.g. `Service.Prefix.MyEntity`).
- Support enum references in annotation expressions that were resolved by the compiler.

- [cds.java@4.0.1] Native HANA associations are no longer explicitly disabled in new projects, as this is the default behaviour in cds9
- [cds.java@4.0.1] Fixed a bug, causing the sample UI to trigger unsupported requests
- [cds.java@4.0.1] Fixed a bug, causing `draftActivate` to return error targets with `IsActiveEntity=true`, if there is exactly one error message.
- [cds.java@4.0.0] Fixed a bug in `cds-feature-flow`, causing exceptions when updating the status of a draft-enabled entity.
- [cds.java@4.0.0] Fixed a bug, causing `draftActivate` to return error targets with `IsActiveEntity=true`.
- [cds.java@4.0.0] Fixed an NPE in `cds-adapter-odata-v2` when media entity element is null.
- [cds.java@4.0.0] Fixed a bug causing concurrent modification issues with `ModifiableUserInfo` or `ModifiableParameterInfo` during parallel read access.
- [cds.java@3.10.2] Fixed a bug causing concurrent modification issues with `ModifiableUserInfo` or `ModifiableParameterInfo` during parallel read access.
- [cds4j@4.1.0] Fixed a bug, causing missing updates to `null` when writing to paths in a (runtime) view.
- [cds4j@4.1.0] Fixed rendering of non-refs on the select list of subqueries.
- [cds4j@4.1.0] Gracefully handle forward mapped associations with unsupported on condition on the select list instead of throwing UnsupportedOperationException.
- [cds4j@4.1.0] Fixed a bug in the code generator, causing compilation error if a service is empty and doesn't contain any operations or entities.
- [cds4j@4.0.1] Fixed search on entities using elements of `@cds.external` entities as `@Common.Text`
- [cds4j@4.0.1] Ignore to-one expands to virtual entities in Runtime View CTE mode.
- [cds4j@3.10.2] Fixed UnsupportedOperationException on `CqnAnalyzer.analyze(statement).targetKeys()` where no keys can be extracted due to the complexity of the statement.
- [cds4j@3.10.2] The exceptions that occur within methods of accessor interface proxies, for example `forEach`, are no longer wrapped in `InvocationTargetException`, but thrown directly.
- [cds4j@3.10.2] StructDataParser now rejects non-array nodes as value for to-many associations.
- [cds4j@3.10.2] SQLite: Fixed an issue where setting a new session variable inside a transaction unintentionally cleared other session variables.
- [cds4j@3.10.2] Don't ignore expands to `@cds.external` entities to support remote service mocks
- [cds4j@3.10.2] Fixed NPE in `FromClauseBuilder` on accessing on-condition of association
- [cds4j@3.10.2] Fixed search on entities using elements of `@cds.external` entities as `@Common.Text`
- [cds4j@3.10.2] Ignore to-one expands to virtual entities in Runtime View CTE mode
- [cds@9.1.0] Copies of `cds.context` with `locale`
- [cds@9.1.0] Support for relative paths in `@odata.bind`
- [cds@9.1.0] `cds build` on Windows OS - fixed cli tar usage for resources.tgz
- [cds@9.1.0] Actions and functions with scalar return types use same `@odata.context` calculation as other return types, fixing e.g. `cds.odata.contextAbsoluteUrl` not being respected
- [cds@9.1.0] Improve content-type and content-length handling in OData adapter
- [cds@9.1.0] Parsing incorrect function parameters
- [cds@9.1.0] `cds deploy --dry` no longer tries to load a DB adapter, so that it works w/o one installed.
- [cds@9.1.0] Fix `@mandatory` for actions and functions
- [cds@9.0.4] In some cases, the app crashed if an element was named like a reserved CSN key.
- [cds@9.0.4] Locale detection does not enforce `.query` to be present. Some protocol adapters do not set it.
- [cds@9.0.4] `between` operator for remote OData requests
- [cds@9.0.4] `cds serve/watch` and `cds.test()` no longer try to connect to an SQLite database if none is configured.
- [cds@9.0.4] `cds.connect.to` for required queueable services if no persistence is configured
- [cds@9.0.4] Persistent queue is not enabled if no persistence is configured
- [cds@9.0.3] Handling of bad timestamps in URL ($filter and temporals)
- [cds@9.0.3] View metadata for requests with $apply
- [cds@9.0.3] Server crash for some URLs
- [cds-mtxs@3.1.0] Properly catching errors in the `t0` cleanup intervals.
- [cds-mtxs@3.1.0] eTag determination for `ModelProviderService.getCsn()` only evaluates active extensions now if not explicitly requested differently.
- [cds-mtxs@2.7.4] Extension of aspects is now possible. It needs to be enabled usingjsonc

```
"requires": {
  "extensibility": {
    "enable-aspect-extension": true
  }
}
```

in the root project configuration.
- [cds-mtxs@2.7.3] More reliable detection of forbidden annotations in entity extensions
- [cds-mtxs@2.7.3] Event 'activated' now only available as internal event to avoid deadlocks.

### Removed ​

- [cds.java@4.0.0] Removed deprecated property `cds.security.authorization.emptyAttributeValuesAreRestricted`. Empty attributes are always considered restricted by default and explicit `is null` conditions must be used to treat empty attributes as unrestricted.
- [cds.java@4.0.0] Removed deprecated property `cds.odataV4.serializer.buffered`. OData V4 responses are now always streamed while serialized.
- [cds.java@4.0.0] Removed deprecated property `cds.messaging.services..structured` and deprecated plain String-based methods in `MessagingService` and `TopicMessageEventContext`. Messages are now structured by default and always represented as separated data and header maps.
- [cds.java@4.0.0] Removed deprecated custom K8s service binding handling via properties `cds.environment.k8s`.
- [cds.java@4.0.0] Removed deprecated classes `ClientCredentialJwtAccess`, `ClientCredentialsJwtReader` and `XsuaaParams`.
- [cds.java@4.0.0] Removed the resource bundle template `cds-messages-template.properties` in the `cds-services-utils` jar.

## May 2025 ​

### Added ​

- [cds-dk@9.0.1] `cds debug --force` automatically enables SSH for Cloud Foundry application instances.
- [cds-dk@9.0.1] Faster table deployments on SAP HANA using HDI param `com.sap.hana.di.table/try_fast_table_migration=true` in `cds build --for hana`, `cds deploy --to hana`, `cds add hana`.
- [eslint-plugin-cds@4.0.2] Add new rule sets for JS `js.all` and `js.recommended` to detect bad practice in service implementations.
- [eslint-plugin-cds@4.0.2] Add rule `no-shared-handler-variables` to detect when state is shared between handlers.
- [eslint-plugin-cds@4.0.2] Add rule `use-cql-select-template-strings` to mitigate potential for SQL injections.
- [eslint-plugin-cds@4.0.2] Add rule `no-cross-service-import` to detect when typer artifacts are imported in an unrelated service.
- [eslint-plugin-cds@4.0.2] Add rule `no-deep-sap-cds-import` to forbid importing from below the facade of `@sap/cds`.
- [vscode-cds@9.0.1] Support for telemetry - See `README.md` for details
- [cds-compiler@6.0.8] for.odata/to.edm(x): Annotating the generated `DraftAdministrativeData` artifacts and their elements is now supported.

- [cds.java@3.10.0] Support functions `round`, `floor`, `ceiling`, `length`, `indexof`, and `trim` in OData V4.
- [cds.java@3.10.0] Added expression validations with `@assert.constraint`.
- [cds.java@3.10.0] Added support for `@mandatory` with expressions.
- [cds.java@3.10.0] Added support for `@readonly` with expressions.
- [cds.java@3.10.0] Added support for Service Manager v2 API. Usage is disabled by default, but can be enabled with CDS property `cds.multiTenancy.serviceManager.v2.enabled: true`.
- [cds.java@3.10.0] The goal `add` of the `cds-maven-plugin` for feature AMS adds support for local testing of AMS policies to a CAP Java project.
- [cds.java@3.10.0] Authorizations now support conditions with paths involving associations in `@restrict` predicates for modifying statements.
- [cds.java@3.10.0] `@readonly` (and it's `@Common.FieldControl` variants) and `@Core.Computed` can now be evaluated already on draft instances by setting `cds.drafts.enforceReadonly` to `true`. During activation they are therefore no longer evaluated. With this change values that are computed on server-side in draft mode will be retained during activation.
- [cds4j@3.10.0] Support `Result:rowType` for insert, upsert and update results
- [cds4j@3.10.0] Added numeric rounding functions `round`, `floor` and `ceiling` on `Value` and on `CQL`
- [cds4j@3.10.0] Function `average` is synonym for `avg`
- [cds4j@3.10.0] Type propagation for the `avg`|`average` function
- [cds4j@3.10.0] Added String functions `length`, `indexOf` and `trim`
- [cds4j@3.10.0] Support expanding unmanaged associations in hierarchies
- [cds4j@3.10.0] Support expanding reverse-mapped associations on subqueries and hierarchies
- [cds4j@3.10.0] Support associations/compositions to entities with aliased keys
- [cds@9.0.0] CAP-native task queues (beta; replacing generic outbox -- see section Changed for additional details) Events and requests to a "queued service" are written to the database in the current transaction (with default kind `persistent-queue`) and processed as asynchronous tasks Programmatically queue or unqueue any service via `cds.queued(srv)`/ `cds.unqueued(srv)`
- Statically queue instances of `cds.MessagingService` or `AuditLogService` via config `cds.requires..queued = true`
- Disable the persistent task queue via `cds.requires.queue = false`

- Tasks are processed in dedicated transactions (except on SQLite, where there are no concurrent transactions)
- Tasks are retried until processed successfully or the max. retry count is reached, i.e., adding resiliency to the respective service Tasks that cause unrecoverable or programming errors will remain in the database table but will not be retried

- Experimental task scheduling API `.schedule()` as variant of `.send()` with fluent API options `.after()` and `.every()`
- Experimental task callback API `.after('/#succeeded', (results, req))`/ `.after('/#failed', (error, req))`
- Experimental task trigger API `.flush()`
- Experimental application-level task status management to avoid long-lasting database locks Enable via `cds.requires.queue.legacyLocking = false`
- Caution: Application-level task status management only works if all active app deployments are on cds^9!

- [cds@9.0.0] Inbox: Inbound messages can be accepted as asynchronous tasks via config `cds.requires.messaging.inboxed = true`
- [cds@9.0.0] Not null validations for actions and functions
- [cds@9.0.0] `cds.auth`: Provide custom configuration to `@sap/xssec`-based authentication via `cds.requires.auth.config`
- [cds@9.0.0] IAS: Token validation for requests to the app's "cert url" (with `.cert` segment in the domain)
- [cds@9.0.0] Support refs with longer path expressions like `ref: ['root', 'child', 'subchild', 'ID']` when resolving queries to the target entity
- [cds@9.0.0] `PATCH` as synonym for `UPDATE` during event handler registration
- [cds@9.0.0] `UPSERT` semantics for `PUT` requests can be deactivated via flag `cds.runtime.put_as_upsert=false`
- [cds-mtxs@3.0.1] `cds-mtx upgrade t0` can be used to (re)initialize the `t0` tenant, e. g. in a cf hook to avoid concurrency issues.
- [cds-mtxs@3.0.1] The `cds.xt.ExtensibilityService.activated` event now also sends the payload of the activation call. It also sends the tenant in the `x-tenant-id` header field now.

### Changed ​

- [cds-dk@9.0.4] `cds add typescript` adds a `tsx` dependency. It no longer adds a `watch` script pointing to `cds-tsx` because `cds watch` will run `tsx` automatically.
- [cds-dk@9.0.3] `DEBUG=build cds build` does not log the CDS env any more.
- [cds-dk@9.0.3] `cds init --java:mvn` does not prefix the `-D` to options any more to allow for options not starting with `-D`.
- [cds-dk@9.0.3] `cds add html5-repo` for Helm does not add XSUAA configuration for IAS-only projects.
- [cds-dk@9.0.3] `cds add html5-repo` for Helm has improved support for IAS.
- [cds-dk@9.0.3] `cds watch` with `tsx` will no longer be print notifications to `console.log` without environment variable `DEBUG` set.
- [cds-dk@9.0.3] `cds add html5-repo` will add missing `requires` for its `build-parameters` setting, even if ran with a preexisting `requires` key.
- [cds-dk@9.0.3] `cds unknown-command valid-file.cds` now fails due to the unknown command instead of compiling the cds file.
- [cds-dk@9.0.1] Change license from SAP DEVELOPER LICENSE AGREEMENT '3.1' to '3.2 CAP'. See https://cap.cloud.sap/resources/license/developer-license-3_2_CAP.txt.
- [cds-dk@9.0.1] The `CHANGELOG.md` file now only contains changes from 8.0.0 onwards.
- [cds-dk@9.0.1] cds-dk now requires `@sap/cds` version 8.3.0 or higher. An error is raised for older versions.
- [cds-dk@9.0.1] cds-dk now requires `@sap/cds-mtxs` version 2 or higher.
- [cds-dk@9.0.1] `cds add multitenancy` and `cds add xsuaa` use the `production` profile by default.
- [cds-dk@9.0.1] `cds add helm` uses a default for the Docker secret name (`docker-registry`), instead of asking for it in interactive mode.
- [cds-dk@9.0.1] `cds add helm` uses the pre-configured domain name for your Kyma cluster as a default, instead of asking for it.
- [cds-dk@9.0.1] `cds add workzone` uses the backend destination `srv-api` instead of `-srv-api` on Cloud Foundry.
- [cds-dk@9.0.1] `cds add approuter` in combination with `xsuaa` adds a `redirect-uris` to `mta.yaml` for Cloud Foundry projects.
- [cds-dk@9.0.1] `cds build --ws-pack` now recursively packs dependencies from workspaces. If the `workspaces` definition in the project root contains glob patterns with braces `{…}`, Node.js 22 or later will be required.
- [cds-dk@9.0.1] `cds add xsuaa` adds a `redirect_urls` to the `mta.yaml` for Cloud Foundry projects.
- [cds-dk@9.0.1] `cds deploy --to hana` throws an error if an unsupported option is passed.
- [cds-dk@9.0.1] The Node version in `gen/db/package.json` file generated by `cds build` is now `>=18`, matching to what `@sap/hdi-deploy` specifies.
- [cds-dk@9.0.1] `cds watch` only auto-resolves bindings if either `CDS_ENV` or `--profile` are set.
- [cds-dk@9.0.1] `cds compile --help` no longer mentions the `hdbcds` format.
- [cds-dk@9.0.1] `cds add pipeline` also creates UI5 resources if required.
- [cds-dk@9.0.1] `cds add hana` does not add `native_hana_associations` configuration any more.
- [cds-dk@9.0.1] `cds up` supports embedded multitenancy scenarios with no sidecar.
- [cds-dk@9.0.1] `cds lint` requires projects to install `eslint` locally (or system-wide), as `cds-dk` will no longer include `eslint` internally.
- [cds-dk@9.0.1] `cds add telemetry` adds limits the version of added `@opentelemetry` dependencies to `
- [cds-dk@9.0.1] `cds add cf-manifest` uses a 1 GB disk quota instead of 512 MB for Java apps.
- [cds-dk@8.9.4] `cds init` uses latest Maven Java archetype version 3.10.1 for creating Java projects.
- [eslint-plugin-cds@4.0.2] Bumped peer dependency to `@sap/cds` to 9.
- [vscode-cds@9.0.1] Change license from SAP DEVELOPER LICENSE AGREEMENT '3.1' to '3.2 CAP v2'
- [vscode-cds@9.0.1] Where-used functionality now based on new index
- [vscode-cds@9.0.1] Improved `cds json schema` retrieval
- [vscode-cds@9.0.1] Refactored CLI call handling to cds and other tools
- [vscode-cds@9.0.1] More compact formatting of `case` statements
- [vscode-cds@9.0.1] Refactoring when renaming/deleting CDS files is now disabled by default. Corresponding user settings are `cds.refactoring.files.rename.enabled` and `cds.refactoring.files.delete.enabled`
- [cds-compiler@6.0.8] License changed to "SAP DEVELOPER LICENSE AGREEMENT Version 3.2 CAP"
- [cds-compiler@6.0.8] Node 20 is now the minimum required version.
- [cds-compiler@6.0.8] Namespace `cds.core` is no longer reserved by the cds-compiler. It is used by the CAP runtimes.
- [cds-compiler@6.0.8] compiler:Providing a filter for a function call now is a syntax error (was a warning before). Example: `count(*)[ uncheckedFilterRef > 0 ]`.
- Providing a default value for an array-like action or function parameter is a syntax error now (was a warning before). Example: `action A( par: many Integer default 42 )`.
- Providing an annotation for an array-like element in the middle of a type expression is no longer allowed (was a warning before), as this leads to unexpected results. Example: `bar: many String null @anno enum { symbol };`. Fix this by moving the annotation out of the type expression, e.g. before the element name.
- A simple query inside parentheses (e.g. `entity V as (select from E)`) is no longer represented as `set` in CSN. Repeated `order by` or `limit` clauses are no longer allowed (e.g. `entity V as ( select from E order by id ) order by id;`).
- Defining an element or parameter as `not null default now` now is an error.
- A virtual element can be defined in a view without providing a value or reference.cds

```
entity V as select from E { virtual a } //defines new virtual element 'a'
```

In this example, the compiler no longer tries to resolve the name of the virtual element as reference to an element of the view's data source.
- If a select item selects an element of a virtual structure that itself is not explicitly marked as virtual, then the select item must be explicitly marked as virtual, too.
- To-many associations without ON-condition no longer get a `keys` property, i.e. `Association to many Foo;` does not get any foreign keys.
- Annotation `@cds.persistence.journal` is now propagated to generated entities, including `.texts` entities.
- Doc comments are no longer propagated; use option `propagateDocComments: true` to propagate them again.
- With CSN input, the compiler does not accept anymore type properties like `enum` in the `cast` property for the SQL function `cast` which were simply ignored by the SQL backend. Remark: inside a direct `cast` property for select columns (CDL-style `cast`), these type properties are still allowed.

- [cds-compiler@6.0.8] to.sql/to.hdi:Default for option `booleanEquality` is `true`, i.e. `!=` is rendered as `IS DISTINCT FROM` or a similar expression and therefore has boolean logic instead of three-valued logic.
- To-many associations with neither an explicit foreign key list (i.e. without `keys`) nor an ON-condition are reported as errors.
- For SAP HANA, CDS associations are by default no longer reflected in the respective database tables and views by native HANA Associations (HANA SQL clause `WITH ASSOCIATIONS`). They can be switched on via configuration `cds.sql.native_hana_associations: true`.
- A set of OData and SAP HANA functions are translated to database-specific variants.
- For SQL and HDI rendering, `$now` is no longer rendered as `CURRENT_TIMESTAMP`, but as a session variable `SESSION_CONTEXT('NOW')` for SAP HANA, `SESSION_CONTEXT('$now')` for SQLite, `@now` for H2, and `current_setting('cap.now')::timestamp` for Postgres. For `default` values, `CURRENT_TIMESTAMP` is kept, as `default` clauses only allow static expressions. To restore the old behavior, use option `dollarNowAsTimestamp: true`.
- `count(*)` inside nested projections is rejected, as there is no proper representation in SQL

- [cds-compiler@6.0.8] to.cdl:Nested definition rendering is now the default, i.e. definitions inside services are rendered in `service { … }`, instead of being rendered top-level using their absolute name.
- `to.cdl` no longer returns an entry `namespace`, only `model`.

- [cds-compiler@6.0.8] for.odata/to.edm(x):References to foreign keys in annotation expressions are now adjusted to directly reference the corresponding local foreign key element.
- Annotating the generated `DraftAdministrativeData` artifacts and their elements is now supported.

- [cds4j@3.10.0] New method `Xpr.size()` replaces (deprecated) method `Xpr.length()`
- [cds@9.0.2] REVERT: For drafts, read-only fields must be set in `CREATE` handlers (calculated values set in `NEW` handlers are cleansed). If children are added in draft `CREATE` handlers, the field `DraftAdministrativeData_DraftUUID` must be set.
- [cds@9.0.1] Lean draft handler is registered in a service only if a draft-enabled service entity exists
- [cds@9.0.0] Evolution of the generic outbox to CAP-native task queues:`cds.queued()`/ `cds.unqueued()` replace `cds.outboxed()`/ `cds.unboxed()` (temporary compat in place)
- Global configuration `cds.requires.queue` replaces `cds.requires.outbox` (temporary compat in place)
- New default `cds.requires.queue = true`. This change requires a database deployment (for table `cds.outbox.Messages`) if `cds.requires.outbox` was not manually set to `true` before.
- Default `chunkSize` reduced from `100` to `10`. If parallel processing is disabled (`parallel = false`), the `chunkSize` config is ignored and the effective `chunkSize` is `1`.

- [cds@9.0.0] Support for `@sap/cds-mtxs` version 1 is dropped
- [cds@9.0.0] Service level restrictions for application service calls are enforced by defaultOpt out with `cds.features.service_level_restrictions=false` until next major version

- [cds@9.0.0] `req.diff` uses a deep expand to fetch data for deep update comparison. Previously, it read each composition layer sequentially.
- [cds@9.0.0] `cds.test` now requires module `@cap-js/cds-test` to be installed. Test dependencies like `axios`, `chai`, `chai-as-promised`, and `chai-subset` can be usually removed in favor of `@cap-js/cds-test`.
- [cds@9.0.0] `cds.context.locale` is only set if initiated from an HTTP client specifying a locale
- [cds@9.0.0] Only new major version 4 of SAP Cloud SDK is supported from now on . Please make sure to upgrade. Detailed changes are documented in the migration guide.
- [cds@9.0.0] `cds-serve` now fails if `@sap/cds` would be loaded from different installation paths to prevent inconsistent server state. Such situations are always a setup issue, often caused by plugins that require diverging versions. Disable with `cds.server.exit_on_multi_install: false`.
- [cds@9.0.0] For drafts, read-only fields must be set in `CREATE` handlers (calculated values set in `NEW` handlers are cleansed). If children are added in draft `CREATE` handlers, the field `DraftAdministrativeData_DraftUUID` must be set.
- [cds@9.0.0] `hdbtabledata` files created by `cds compile/build` now instruct SAP HANA to decode base64 values in CSV files for `LargeBinary` elements. This aligns the behavior with SQLite and H2, avoiding manual base64 decoding. It can be disabled with `cds.hana.table_data.column_mapping.LargeBinary=false`.
- [cds@9.0.0] `PATCH` requests no longer create the target resource if it doesn't exist (`UPSERT` semantics)Re-enable via flag `cds.runtime.patch_as_upsert=true`

- [cds@9.0.0] `PUT` requests no longer set unprovided properties to their default values (`REPLACE` semantics)Re-enable via flag `cds.runtime.put_as_replace=true`
- If enabled, the defaulting is now done in the protocol adapter

- [cds@9.0.0] `req.params` is an array of objects (instead of plain values for single-keyed entities with key `ID`)Opt out with `cds.features.consistent_params=false` until next major version

- [cds-mtxs@3.0.2] `cds.requires.multitenancy.jobs.clusterSize` is set to 3 by default.
- [cds-mtxs@3.0.2] `cds.requires.multitenancy.jobs.workerSize` is set to 4 by default.
- [cds-mtxs@3.0.1] `@sap/cds-mtxs` now also conforms to the CAP plugin protocol.
- [cds-mtxs@3.0.1] `@sap/cds-mtxs` now declares a peer dependency to `@sap/cds` version 9. Lower versions will fail.
- [cds-mtxs@3.0.1] For the `java` profile, `cds.requires.auth` is set to `"kind": "dummy"` in the sidecar by default.
- [cds-mtxs@3.0.1] `com.sap.hana.di.table/try_fast_table_migration` deployment parameter is now enabled as default.
- [cds-mtxs@3.0.1] Outdated MTX configuration now throws an error.
- [cds-mtxs@3.0.1] Outdated provisioning parameter configuration now causes an error.
- [cds-mtxs@3.0.1] The extension validation (aka linting) now always checks extensions including existing extensions. This can be disabled usingjsonc

```
"requires": {
  "cds.xt.ExtensibilityService": {
    "check-existing-extensions": false
  }
}
```
- [cds-mtxs@3.0.1] The extension validation (aka linting) now also checks if the model can be compiled to EDMX. This also detects e.g. missing key fields of entities.
- [cds-mtxs@3.0.1] If the `subscription-manager` profile is used, IAS will be the default authentication kind for production.
- [cds-mtxs@3.0.1] The MTX sidecar now always uses the compiler configuration of the project root. To use a separate compiler configuration, you need to add the configurationjsonc

```
"requires": {
  "cds.xt.ModelProviderService": {
    "use-local-cdsc-config": true
  }
}
```

### Fixed ​

- [cds-dk@9.0.4] Bring shrinkwrap back.
- [cds-dk@9.0.4] `cds import --from edmx` no longer produces invalid CSN for function imports with return types of the same name.
- [cds-dk@9.0.4] `cds watch` no longer shows the outbox model for empty projects.
- [cds-dk@9.0.3] `cds up -2 k8s` fails for errors in `ctz` instead of only logging the messages.
- [cds-dk@9.0.3] `cds add helm` now correctly prompts for the registry server.
- [cds-dk@9.0.2] `cds add multitenancy` adds the `@sap/cds-mtxs` to `devDependencies` in for Java projects.
- [cds-dk@9.0.2] `cds add ias` rewrites the `url: ~{srv-url}` to `url: ~{srv-cert-url}` if required.
- [cds-dk@9.0.2] `cds add ias` adds `forwardAuthCertificates` and `strictSSL` settings to the app router if required.
- [cds-dk@9.0.1] `cds up` has improved support for monorepos.
- [cds-dk@9.0.1] `cds add html5-repo` works in combination with multitenancy when no app router or Work Zone is set up.
- [cds-dk@9.0.1] `cds add dynatrace` sets the `environment_name` property according to the specification.
- [cds-dk@9.0.1] `cds deploy --to hana` now supports `--with-mocks`.
- [cds-dk@9.0.1] `cds bind` gives better error messages if the Cloud Foundry org or space are not found.
- [cds-dk@9.0.1] `cds add enterprise-messaging` with xsuaa now adds `processed-after` in the `mta.yaml`.
- [cds-dk@9.0.1] `cds deploy --to hana` correctly hands over `--profile` to `cds build` when deploying.
- [cds-dk@9.0.1] `cds import` adds `@mandatory` annotations to properties marked as `required` in the schema.
- [cds-dk@9.0.1] `cds add ams` for Java adds a custom builder to the `mta.yaml` to circumvent the missing `srv/src/gen/policies`.
- [cds-dk@9.0.1] `cds add multitenancy` requires the `srv-api` instead of the `mtx-api` for Java projects.
- [vscode-cds@9.0.1] Avoid exception during json schema hover when no hover text is available
- [vscode-cds@9.0.1] Welcome page (`CAP Release Notes`) now show title of code block sections
- [vscode-cds@9.0.1] Formatter: Separate alignment of annotations to entity and select items
- [vscode-cds@9.0.1] Syntax highlighting of parenthesized annotations with strings containing a colon
- [vscode-cds@9.0.1] Syntax highlighting of comments in queries
- [cds-compiler@6.0.10] to.sql/to.hdi:Fixed internal error for to-many associations without ON-condition in entities with `@cds.persistence.skip`.

- [cds-compiler@6.0.10] for.odata/to.edm(x):In annotation expressions: enum references that have already been resolved by the compiler are correctly rendered to EDMX.

- [cds-compiler@6.0.8] to.edm(x): Fixed crash for rare case if annotation expressions were used.
- [cds-compiler@5.9.4] to.edm(x): Parameters are marked optional unless explicitly marked as `not null`. Annotation `Core.OptionalParameter` will be added to optional parameters.
- [cds.java@3.10.1] Fixed a bug in the Service Manager v2 API integration that leads to 400 Bad Request errors when service instances or service bindings are requested by ID.
- [cds.java@3.10.1] Fixed a bug in `cds-services-archetype` causing an invalid default package name.
- [cds.java@3.10.1] Fixed a bug in `cds-feature-change-tracking` causing the composition `changes` to be written when the entity itself is deleted.
- [cds.java@3.10.1] Fixed a bug causing instance-based authorization conditions to be executed on inactive draft-enabled instances during `draftActivate` or `draftEdit`. This fix requires `cds.security.authorization.instanceBased.checkInputData.enabled` to be set to `true`.
- [cds.java@3.10.1] Fixed a bug in `cds-feature-flow` causing server errors in case an action with `@flow` annotations was triggered on a non-existent entity instance.
- [cds.java@3.10.0] Fixed a bug, causing `com.sap.cloud.sdk.datamodel.odata.client.exception.ODataDeserializationException` when querying the `@odata.singleton` annotated entity via remote service.
- [cds.java@3.10.0] Fixed a bug, causing a JsonParsingException, when authenticating with a IAS based jwt token that contains non-string attributes.
- [cds.java@3.10.0] Fixed a bug, causing the Kafka client to loose connection in case of a certificate rotation.
- [cds.java@3.10.0] Fixed a bug, causing the original Correlation ID not propagated to custom Outbox handlers.
- [cds.java@3.10.0] Fixed a bug, causing the display of the undocumented properties in the developer dashboard.
- [cds.java@3.10.0] Fixed a bug, causing a messed up event context when receiving message from Event Mesh without data, dataMap or headersMap.
- [cds.java@3.10.0] Fixed a bug in `cds-feature-change-tracking` causing the links between the projections of the entities that exclude elements of aspect `changelog.changeTracked` and their changes to be lost. Links between entities and changes are now written using domain entities which is assumed to be extended with aspect `changelog.changeTracked`.
- [cds.java@3.10.0] Fixed a bug in `cds-feature-change-tracking` causing statement with wrong selection predicate being generated when `Update` statement uses CDS delta lists as payloads for compositions.
- [cds.java@3.10.0] Fixed a bug in `cds-feature-change-tracking` causing `Delete` statements to consider localized values for images.
- [cds.java@3.10.0] Fixed a bug in `cds-feature-change-tracking` causing parametrized `Update` statements to select more data than needed for changelogs.
- [cds4j@3.10.1] Fixed duplication issue due to left join in runtime view CTE mode on RT views with filtered to-many associations
- [cds4j@3.10.1] Support redirected associations, nested projections and structs in runtime view CTE mode
- [cds4j@3.10.0] Fixed serialization of statements with predicates on the select list
- [cds4j@3.10.0] Reduced memory consumption during bulk inserts
- [cds4j@3.10.0] Execute bulk inserts in partitions
- [cds4j@3.10.0] Fix search on entities using virtual elements as `@Common.Text`
- [cds@9.0.2] `cds.load()` ignores the outbox model if it's the only model source, helping `watch` to suppress it as well.
- [cds@9.0.1] `cqn2odata`: value formatting in OData v4 lambda expressions
- [cds@9.0.1] Processing in `filed-based-messaging` must be async
- [cds@9.0.1] `Location` response header for REST protocol
- [cds@9.0.1] `cds.log` is unwired from `cds.env` now, which allows to use `cds.log` in plugins, without risk of loading `cds.env` too early.
- [cds@9.0.1] Elements from `mixin` are now being considered by `minify`
- [cds@9.0.1] Lean draft: Insert.entries on draft enabled entity
- [cds@9.0.1] Remote call of action/function always forwards passed headers
- [cds@9.0.1] `cds serve` no longer fails with an duplicate install error if the shell's working directory differs in case (like `C:` vs `c:` on Windows).
- [cds@9.0.1] Erroneously skipped input validation for local service calls
- [cds@9.0.0] Webhook creation in `enterprise-messaging` is more resilient in case of multiple instances
- [cds@9.0.0] `cdsjsonschema` protocol in lower case for cds json schema
- [cds@9.0.0] In `CREATE` handlers for drafts, the original path is preserved
- [cds@9.0.0] `@sap/cds-mtxs` is now loaded before other plugins so that they can register handlers for mtx services.
- [cds@9.0.0] The default index page respects now `cds.odata.containment`
- [cds@9.0.0] Remove incorrect `Type` suffix from `@odata.context` for views with parameters
- [cds@9.0.0] Support where clauses in refs
- [cds@8.9.4] No longer require `@sap/cds-compiler` versions 6.x as these are not supported with CAP Java 3.
- [cds@8.9.4] Regression in view resolving with mixins
- [cds@8.9.4] View resolving for external service entities aborted too early
- [cds@8.9.4] `cds.Map` validation in action/function parameters
- [cds@8.9.3] OData: `$value` access of primitive properties returned by custom handler
- [cds@8.9.3] UCL: Add missing declaration of variable `$input` in mutation for creating an application template
- [cds@8.9.3] Purge of `servers` from `.cds-services.json` file
- [cds@8.9.3] Loading of relative service implementations in plugins
- [cds@8.9.3] `cds.compile.to.edmx` in case the model was manipulated in a plugin
- [cds-mtxs@3.0.2] Properly catching errors in the `t0` cleanup intervals.
- [cds-mtxs@3.0.1] Extension validation (aka linting) for new entities now works properly, also if no other extensions exist.
- [cds-mtxs@3.0.1] Extension validation now ignores internal definitions with namespace `cds.core`.
- [cds-mtxs@3.0.1] Base model pulled for extension projects using `cds pull` no longer contains internal definitions with namespace `cds.core`, `cds.outbox` or `cds.xt`.
- [cds-mtxs@3.0.1] [Beta] Extension of aspects is now possible. For now, it needs to be enabled usingjsonc

```
"requires": {
  "cds.xt.ExtensibilityService": {
    "allow-aspect-extension": true
  }
}
```

### Removed ​

- [cds-dk@9.0.1] `cds build --clean` is removed.
- [cds-dk@9.0.1] `cds build` no longer supports configuration with `cds.data` and `cds.service` in package.json.
- [cds-dk@9.0.1] `cds watch` still allows options `--include` and `--exclude`, but CDS configuration is ignored.
- [cds-dk@9.0.1] `cds deploy --to hana --store-credentials` is removed.
- [eslint-plugin-cds@4.0.2] Removed support for ESLint8
- [vscode-cds@9.0.1] User setting `cds.useOldParser`
- [vscode-cds@9.0.1] Official support for CDS < 8 and CDS compiler < 5 (a fallback to the latest compiler is done)
- [cds-compiler@6.0.8] compiler: The Antlr-based parser is removed.
- v5 deprecated flags are removed.
- Option `compositionIncludes` is removed, as its default is `true`; instead, a deprecated flag was added.

- [cds-compiler@6.0.8] to.hdbcds: The HDBCDS backend is deprecated and can no longer be invoked.
- [cds@9.0.0] Legacy OData adapter which was enabled with compat `cds.features.odata_new_adapter=false`
- [cds@9.0.0] Legacy Database services which were enabled with `@sap/cds-hana` or `sqlite3`
- [cds@9.0.0] `@cds.default.order` and `@odata.default.order` for implicit sorting
- [cds@9.0.0] `cds.auth`: Support for `@sap/xssec^3` (incl. compatibility mode of `@sap/xssec^4`)
- [cds@9.0.0] Undocumented compat flag `cds.features.odata_v2_result_conversion`
- [cds@9.0.0] Undocumented util `cds.utils.pool`
- [cds@9.0.0] Undocumented method `INSERT.as`. Use `INSERT.from` instead to insert sub `SELECT` queries.
- [cds@9.0.0] Undocumented method `req._queryOptions` of `cds.Request` belonging to the new OData adapter
- [cds@9.0.0] Undocumented method `_reset` of the `cds.ql` API
- [cds@9.0.0] Undocumented property `cmd` of the `cds.ql` `Query` class. Please use method `kind` instead.
- [cds@9.0.0] Undocumented method `protocol4` of the `Protocol` class. Please use property `def.protocols` instead.
- [cds@9.0.0] Undocumented methods `impl` and `with` of the `ApplicationService` class. Please use `prepend` instead.
- [cds@9.0.0] Undocumented compat flag `cds.features.rest_error_handler`
- [cds@9.0.0] Deprecated compat flags `cds.features.compat_restrict_bound` and `cds.env.features.compat_restrict_where`
- [cds@9.0.0] Deprecated compat flag `cds.features.stream_compat`
- [cds@9.0.0] Deprecated feature flag `cds.log.kibana_custom_fields`. Please use `cds.log.als_custom_fields` instead`.
- [cds@9.0.0] Deprecated compat flag `cds.features.keys_in_data_compat`
- [cds@9.0.0] Deprecated element-level annotation `@Search.defaultSearchElement`. Please use annotation `@cds.search` instead.
- [cds@9.0.0] Deprecated stripping of unnecessary topic prefix `topic:` in messaging
- [cds@9.0.0] Deprecated messaging `Outbox` class. Please use config or `cds.outboxed(srv)` to outbox your service.

## April 2025 ​

### Added ​

- [cds.java@3.9.0] Added support for the SAP Integration Suite, Advanced Event Mesh.
- [cds.java@3.9.0] Added `@Core.OptionalParameter` support for bound and unbound function parameters. Supported values are `true` and `false`.
- [cds.java@3.9.0] Subscription dependencies for `portal` and `html5-apps-repo` are automatically created if the corresponding service is bound to the CAP Java application.
- [cds.java@3.9.0] Log CDS Properties by setting the log level `logging.level.com.sap.cds.properties: DEBUG` in the application.yaml. Warnings are turned on by default.
- [cds.java@3.9.0] `cds-feature-auditlog-v2` now ignores auditlog service bindings relevant for the XSA platform.

### Changed ​

- [cds-dk@8.9.3] `cds add pipeline` also creates UI5 resources if required.
- [cds-dk@8.9.2] The Node version in `gen/db/package.json` file generated by `cds build` is now `>=18`, matching to what `@sap/hdi-deploy` specifies.
- [cds-dk@8.9.2] `cds` commands now fail if used in combination with the upcoming `@sap/cds` version 9.
- [vscode-cds@8.9.0] use new CDS parser by default

### Fixed ​

- [cds-dk@8.9.3] `cds add workzone` uses the backend destination `srv-api` instead of `-srv-api` on Cloud Foundry.
- [cds-dk@8.9.3] `cds init` uses latest Maven Java archetype version 3.9.1 for creating Java projects.
- [cds-dk@8.9.2] `cds bind` gives better error messages if the Cloud Foundry org or space are not found.
- [cds-dk@8.9.2] `cds add html5-repo` works in combination with multitenancy when no app router or Work Zone is set up.
- [cds-dk@8.9.1] `cds build` restores compatibility with `@sap/cds` 7, no more crashing there with `TypeError: Cannot read properties of undefined (reading 'enabled')`.
- [cds-dk@8.9.1] `cds add containerize` works if run before `cds add helm`.
- [cds-dk@8.9.1] `cds add http` no longer writes headers starting with a placeholder (IntelliJ compatibility)
- [cds-dk@8.9.1] `cds init --force` overwrites existing files.
- [vscode-cds@8.9.1] Formatting of annotations in parentheses with values containing spaces
- [vscode-cds@8.9.0] Auto update of Annotation Modeler plugin did not work
- [vscode-cds@8.9.0] Document highlights could show wrong ranges for namespaces
- [cds-compiler@5.9.2] to.edm(x): Revert addition of the attribute sap:filterable="false" to the NavigationProperty DraftAdministrativeData in OData V2
- [cds-compiler@4.9.10] Added option `allowMixinInProjectionExtension` which allows referring to mixins in `extend projection`. This was forbidden in cds-compiler v4, but re-introduced in v5.5. Users wanting to migrate from cds-compiler v3 to v4 can use this option for easier migration.
- [cds.java@3.9.1] Fixed a bug, causing wrapping services with typed service interfaces to fail when service interfaces are defined in a separate dependency.
- [cds.java@3.9.1] Fixed a bug, causing ORD EDMX metadata endpoints to fail, when services contain a dot.
- [cds.java@3.9.1] Fixed a bug, causing Kafka SSL configuration to access corrupted keystore files.
- [cds.java@3.9.1] Fixed a bug, causing Event Mesh multitenancy subscription or upgrades to fail silently.
- [cds.java@3.9.0] Fixed a bug, causing lost commits, when starting readonly transactions through Spring APIs inside of a ChangeSetContext.
- [cds.java@3.9.0] Fixed a bug in OData v4 adapter, causing duplicated entries in response payload for `@open` types.
- [cds4j@3.9.1] Fix queries with filtered path over runtime views
- [cds@8.9.2] `forUpdate` will not consider `wait` if `ignoreLocked` is set
- [cds@8.9.2] Do not crash in case of custom `DraftAdministrativeData` table
- [cds@8.9.1] `cds.env` merging for `null` values
- [cds@8.9.1] Best-effort mechanisms for lambda support on OData V2 remote services (usage of functions in lambda expressions)
- [cds@8.9.1] Use extended model in `enterprise-messaging` inbound handlers
- [cds@8.9.1] Compat flag `cds.features.draft_compat` for handler registration in draft scenarios
- [cds-mtxs@2.7.2] Inaccurate warnings about outdated configuration are removed.
- [cds-mtxs@2.7.2] Improved resilience in handling corrupted metadata entries stored in the tenant database table.
- [cds-mtxs@2.7.1] Input validation annotations (e. g. `@assert.range`) with default values in extensions are now correctly checked.
- [cds-mtxs@2.7.1] Event 'activated' is now only triggered for successfully completed extension activation.
- [cds-mtxs@2.7.1] Binding parameters configured for subscription are now correctly passed to the Service Manager.

## March 2025 ​

### Added ​

- [cds-dk@8.9.0] `cds import` now adds Cloud SDK dependencies to package.json if an OData service is imported.
- [cds-dk@8.9.0] `cds deploy --to hana --on k8s` is now supported.
- [cds-dk@8.9.0] `cds up` automates freezing dependencies, building, and deploying your application.
- [cds-dk@8.9.0] `cds pull` includes existing extensions if the server is configured accordingly.
- [cds-dk@8.8.0] `cds add xsuaa` lets you pass a `--plan` option, e.g. for `cds add xsuaa --plan broker`.
- [cds-dk@8.8.0] `cds add workzone` and `cds add workzone-standard` support for Kyma.
- [cds-dk@8.8.0] `cds add typer` now adds a `before:cds-watch` script to run cds-typer before starting `cds watch`.
- [cds-dk@8.8.0] `cds watch` supports a `before:cds-watch` npm script in your `package.json`, executed once before the initial `cds watch` startup.
- [cds-compiler@5.9.0] compiler:Generated entities for compositions of named aspects now have an `include` on the named aspect, inheriting actions from the aspect. This can be disabled via option `compositionIncludes: false`.
- A warning is emitted for selected elements that are explicitly `virtual`, whose behavior will change in cds-compiler v6.
- New warning for structures having a scalar default value.
- New warning for localized structures, as they are not fully supported by the compiler.
- The new parser (`newParser: true`) now supports operator `==`.

- [cds-compiler@5.9.0] to.cdl:Definitions can now be rendered nested in services. A common namespace can be extracted, too. To use it, enabled options `renderCdlDefinitionNesting` and `renderCdlCommonNamespace`.
- Annotation array values are pretty-printed to reduce whitespace.

- [cds-compiler@5.9.0] for.effective: Property `namespace` is no longer part of effective CSN.
- [cds-compiler@5.9.0] for.sql/hdi:[cds-compiler@5.9.0] The new operator `==` is rendered as `IS NOT DISTINCT FROM` or an equivalent expression.
- [cds-compiler@5.9.0] Using option `booleanEquality`, operator `!=` is rendered as `IS DISTINCT FROM` or an equivalent expression.

- [cds.java@3.8.0] Added support for async mode for Unified Customer Landscape´s (UCL) SPII Tenant Mapping API in `cds-feature-ucl`.
- [cds.java@3.8.0] Added parameter for token retrieval timeout for determination of service manager JWT token.
- [cds.java@3.8.0] Event handler signatures can now accept arguments of type `CqnStatement` or it's specific sub-interfaces and `CqnStructuredTypeRef`.
- [cds.java@3.8.0] The `build` goal of the `cds-maven-plugin` now supports execution from project root folder. It also takes a new property `goals` to specify a custom list of goals for execution.
- [cds.java@3.8.0] IAS App2App flows can now be configured for a remote service without creating a destination, by using the IAS binding and setting `binding.options.ias-dependency-name` to the respective IAS application dependency.
- [cds.java@3.8.0] Added support for UI5's State Messages concept to draft-enabled entities, when compiler flag `cdsc.beta.draftMessages` is set to `true`.
- [cds.java@3.8.0] When using State Messages annotation-based validations such as `@mandatory` or `@assert...` are now executed on draft entities.
- [cds.java@3.8.0] Event Handler methods now support `CqnStatement` or its subtypes and `CqnStructuredTypeRef` as arguments.
- [cds.java@3.8.0] Bound and unbound function parameters now support `@Core.OptionalParameter` annotations.
- [cds4j@3.9.0] Support referencing origin entity from upsert result: `Row.ref()`
- [cds4j@3.9.0] Elements that are the target of a `@Common.Text` annotation are now by default searchable
- [cds4j@3.8.0] Support for [SQL] Window Functions
- [cds4j@3.8.0] Support expressions & literals in runtime views
- [cds4j@3.8.0] Support match predicates `anyMatch`/`allMatch` in infix filters of element refs used in where conditions
- [cds4j@3.8.0] Support operator `==` in CQN with Boolean logic (same as IS)
- [cds@8.9.0] Support for parallel multi-instance processing of outbox entries
- [cds@8.9.0] Remote services: ensure request correlation by guaranteeing outgoing header `x-correlation-id`
- [cds@8.9.0] Support for `@odata.bind` to reference foreign keys
- [cds@8.9.0] Support for plugins in ESM format
- [cds@8.9.0] Dependency to `@eslint/js` so that `eslint` works w/o the application having to install it.
- [cds@8.9.0] IAS: In the `client_credentials` flow, the array of `ias_apis` (if present) is added to the technical user's roles
- [cds@8.9.0] Opt-in feature `cds.features.consistent_params` for `req.params` always being an array of objectsThat is, no more plain values for single-keyed entities with key `ID`
- Will become the default in `@sap/cds^9`

- [cds@8.8.0] `cds.ql` method `SELECT.hints()` which passes hints to the database query optimizer that can influence the execution plan
- [cds@8.8.0] Schema updates for MTX configuration
- [cds@8.8.0] Deprecate `cds.requires.db.database` in JSON schema
- [cds@8.8.0] Service level restrictions for application service calls can be enforced with `cds.features.service_level_restrictions=true`With `@sap/cds^9`, this becomes the new default.

- [cds@8.8.0] Support implicit function parameters calls with @prefix
- [cds@8.8.0] `cds.test` now uses package `@cap-js/cds-test` if installed, otherwise prints a hint to install it. With cds 9, this package will be required.
- [cds@8.8.0] Operation response streamingOData: Operations returning `cds.LargeBinary` annotated with `@Core.MediaType` may send stream responses.
- REST: Operations may send stream responses.
- Annotations `@Core.MediaType`, `@Core.ContentDisposition.Filename` and `@Core.ContentDisposition.Type` on operation return types will be considered.

- [cds-mtxs@2.7.0] Database deployment of extensions can now be suppressed by settingjsonc

```
  "requires": {
    "cds.xt.ExtensibilityService": {
      "activate": {
        "skip-db": true
      }
    }
  }
```
- [cds-mtxs@2.7.0] `cds.xt.ExtensibilityService.pull` now returns csn including existing extensions if `check-existing-extensions` is configured (see below)
- [cds-mtxs@2.7.0] Beta: Event `cds.xt.ExtensibilityService.activated` is sent if an asynchronous call of `cds.xt.ExtensibilityService.activate` is finished.
- [cds-mtxs@2.6.0] `html5-runtime: true` and `html5-host: true` are shortcuts in `cds.requires` to specify SAP BTP HTML5 Repository service SaaS dependencies.
- [cds-mtxs@2.6.0] `ExtensibilityService` now supports draft extensions, allowing to separately validate and activate extensions.
- [cds-mtxs@2.6.0] `ExtensibilityService.activate` now allows to pass HDI deployment parameters.
- [cds-mtxs@2.6.0] `cds.env.odata.containment` is respected when compiling to EDMX.

### Changed ​

- [cds-dk@8.9.0] `cds build` logging is simplified.
- [cds-dk@8.9.0] `cds add html5-repo` ignores folders in `app/` starting with `.`
- [cds-dk@8.8.0] Running `cds deploy` in dry mode with an output file specified will now only produce a warning in stderr and will not exit with an error code.
- [cds-dk@8.8.0] `cds deploy --out …` will not generate the specified output file if it would end up empty.
- [cds-dk@8.8.0] `cds add workzone` adds a transpilation task for UI5 deployment descriptors in TypeScript projects.
- [cds-dk@8.8.0] `cds add workzone` does not use the deprecated `webide-extension-task-updateManifestJson` task any more.
- [eslint-plugin-cds@3.2.0] Rules `@sap/cds/sql-null-comparison` and `@sap/cds/no-java-keywords` are moved from the `experimental` rule set to `all`.
- [vscode-cds@8.8.1] using native Node.js `fetch` for https requests
- [vscode-cds@8.8.0] preparation to use new CDS parser
- [vscode-cds@8.8.0] minimum VSCode version is now 1.96.0
- [cds-compiler@5.9.0] Update OData vocabularies: 'Common', 'Hierarchy'
- [cds4j@3.8.0] Changed operator `!=` in CQN to Boolean logic (same as IS NOT)
- [cds@8.9.0] Invalid draft requests now have status code 400
- [cds@8.9.0] Allow ESM loading of handler files (`.js`, `.ts`) in all situations, incl. test runs with Jest's `--experimental-vm-modules` option.
- [cds@8.9.0] Application and remote services now throw the error `Target  cannot be resolved for service ` when the query cannot be resolved to the service entity. Setting the feature flag `cds.env.features.restrict_service_scope` to false disables this.
- [cds@8.9.0] Accept 2xx status codes set in custom operation handlers
- [cds@8.9.0] Implicit orderby elements are marked as such and are no longer considered for requests to remote services
- [cds@8.8.0] The default index page now shows links to CDS functions with their parameter names but no default values anymore.

### Fixed ​

- [cds-dk@8.9.0] `cds add telemetry` is order-independent with other `cds add` commands for Java.
- [cds-dk@8.9.0] Build task `mtx-extension` now fails with exit code 1 in case of build errors.
- [cds-dk@8.8.2] Bump axios to 1.8.4, fixing CVE-2025-27152
- [cds-dk@8.8.1] `cds init` uses latest Maven Java archetype version 3.8.0 for creating Java projects.
- [cds-dk@8.8.1] `cds init --add lint` writes complete eslint.config.mjs.
- [cds-dk@8.8.1] `cds import` no longer fails with an `EXDEV` error in `docker` containers.
- [cds-dk@8.8.1] `cds import` json schema now contains correct references.
- [cds-dk@8.8.0] `cds add approuter` doesn't create entries for `app` and `appconfig` local directories any more.
- [cds-dk@8.8.0] `cds add telemetry` for Java doesn't erroneously add `cds` configuration or `dependencies` to the `package.json`.
- [cds-dk@8.8.0] `cds add sample` adds the workzone-specific configuration if `cds.requires.workzone` is `true`.
- [cds-dk@8.8.0] `cds compile -o` uses the correct file suffix if explicitly specified in the file name.
- [cds-dk@8.8.0] `cds bind` caches the promise of its `cf -v` call to prevent race conditions.
- [cds-dk@8.8.0] `cds import --out ` does not fail if executed in a folder with a `.`.
- [cds-dk@8.8.0] `cds add workzone` has improved support for multitenancy.
- [eslint-plugin-cds@3.2.0] Rules `@sap/cds/sql-null-comparison` will not warn about `!= null`, as it may be supported by future CDS compiler versions.
- [eslint-plugin-cds@3.2.0] Some rules had `docs` meta property `recommended: true`, but were not part of the recommended rules list.
- [eslint-plugin-cds@3.2.0] When determining a CDS project's root directory, we now consider package.json's with `@sap/cds` as `devDependency` or `peerDependency`
- [vscode-cds@8.8.2] Welcome Page was shown after each restart
- [vscode-cds@8.8.1] use lowercase `cdsjsonschema` as protocol for cds schema urls.
- [vscode-cds@8.8.1] user setting `cds.useOldParser` did not work correctly
- [vscode-cds@8.8.0] removed rendering issues in `CAP Release Notes` view
- [vscode-cds@8.8.0] `Generate data model` now also works for `schema.cds` files in subfolders.
- [cds-compiler@5.9.0] to.odata: Annotation expressions using `LabeledElement` were not correctly rendered into EDMX.
- [cds-compiler@5.8.2] for.odata: Generate foreign key elements for events again.
- [cds.java@3.8.1] Fixed a bug, causing Audit log implementation to generate redundant entries with empty attributes for the audit log when entity uses associations as the keys.
- [cds.java@3.8.1] Fixed a bug, causing Audit log implementation to generate messages with duplicated attributes when audited instances expanded multiple times in the same `Select` statement.
- [cds.java@3.8.1] Fixed a bug in Cloud SDK integration, causing the IAS app2app flow to accidentally request a token from the provider level IAS tenant in DwC scenarios.
- [cds.java@3.8.1] Fixed a bug, causing draft queries not being optimized and certain queries on runtime views to fail.
- [cds.java@3.8.0] Fixed a bug, causing non-unique "MT_LIB_TENANT-" service instances to be filtered out.
- [cds.java@3.8.0] Fixed a bug in OData V4 adapter, causing `NullPointerException` while processing payload containing complex type array initialized with `null`.
- [cds.java@3.8.0] Fixed a bug, causing localized error messages in logs and exception stack traces.
- [cds.java@3.8.0] Fixed a bug, causing invalid property suggestions in IDEs, when editing `application.yaml`.
- [cds4j@3.9.0] Fix SQL error on predicates using is (not) on the select list
- [cds4j@3.9.0] Fix exception on computing inline count for queries with a condition evaluating to false
- [cds4j@3.9.0] Fix NPE on expand with inline count for select statements using path expressions in where
- [cds4j@3.9.0] Fix 'Missing value for parameter' error on expand by parent-keys when the parent key is selected with a structuring alias
- [cds4j@3.8.1] Fix expand by 'parent-keys' of associations using literals in on-condition
- [cds4j@3.8.1] Runtime views: ignore expands of entities without persistence
- [cds4j@3.8.0] Consider type casts of refs in orderBy
- [cds@8.9.0] Lean draft: Proper navigation to the service entity of draft-administrative data
- [cds@8.9.0] Unprocessed foreign keys from expressions of semi join conditions in `UPDATE.data`
- [cds@8.9.0] Kafka: Each topic will have a dedicated consumer-group id (configurable with `consumerGroup`)
- [cds@8.9.0] Foreign-key calculation based on navigation path
- [cds@8.9.0] `cds.env` shortcuts like `cds.requires.db === 'hana'` are normalized to `cds.requires.db.kind === 'hana'` when combined from multiple sources
- [cds@8.9.0] Error handling for invalid access of an entity that does not have a key, by key, through REST
- [cds@8.9.0] `cds.validate` crashed with unknown target
- [cds@8.9.0] `cds.parse.expr` parsed SAP HANA native functions like `current_utctimestamp` erroneously as `ref`
- [cds@8.9.0] `null` values in logger if `custom_fields` are configured
- [cds@8.9.0] User-provided instances of SAP Cloud Logging should have either tag `cloud-logging` or `Cloud Logging`
- [cds@8.9.0] The `@odata.context` for entities and views with parameters should refer to the EntityType with `/Set` at the end e.g. `../$metadata#ViewWithParamType(1)/Set`
- [cds@8.8.3] Event Mesh: Reconnect in case of error in AMQP connection
- [cds@8.8.2] Consuming REST actions returning anonymous structures
- [cds@8.8.2] `i18n.labels/messages` were occasionally missing
- [cds@8.8.1] Requests violating `cds.odata.max_batch_header_size` are terminated with `431 Request Header Fields Too Large` instead of `400 - Bad Request`
- [cds@8.8.1] `cds.parse.` writing directly to `stdout`
- [cds@8.8.1] Instance-based authorization for programmatic action invocations
- [cds@8.8.1] Implicit function parameter calls with Array or Object values
- [cds@8.8.1] OData: Throw an error by `POST` with payload that contains array of entity representation
- [cds@8.8.1] `cds.validate` filters out annotations according to OData V4 spec
- [cds@8.8.1] Crash for requests with invalid time data format
- [cds@8.8.1] Add missing 'and' between conditions in object notation of QL
- [cds@8.8.1] Multiline payloads in `$batch` sub requests
- [cds@8.8.1] Instance-based authorization for modeling like `$user. is null`
- [cds@8.8.1] Respect `cds.odata.contextAbsoluteUrl` in new OData adapter
- [cds@8.8.1] `cds.odata.context_with_columns` also applies to singletons
- [cds@8.8.0] Order by virtual fields in draft-related requests
- [cds@8.8.0] Erroneous cleansing when draft activation is invoked programmatically
- [cds@8.8.0] Skip validation for mandatory fields in update scenarios for entities in draft activation
- [cds@8.8.0] Simplified default configuration: `cds.requires.messaging = true`
- [cds@8.8.0] `cds.connect` called with options erroneously filled in `cds.services`
- [cds@8.8.0] Mocked users won't have a tenant in single-tenant mode
- [cds@8.8.0] Allow usage of latest versions of `chai` and `chai-as-promised` on Node >= 23 with the built-in test runner and `mocha`. The `jest` runner is not able though to load these ESM modules.
- [cds@8.8.0] Reject navigations in expand
- [cds@8.8.0] Activation of drafts for entities using `@cds.api.ignore`
- [cds@8.8.0] Prevent uncaught type error during validation of composition entries
- [cds-mtxs@2.7.0] Synchronous calls to `/-/cds/saas-provisioning/upgrade` for non-existing tenants are now handled properly.
- [cds-mtxs@2.6.1] Compatibility with cds 7 is enabled again.
- [cds-mtxs@2.6.1] Asynchronous jobs now properly handle errors exceeding 5000 characters.
- [cds-mtxs@2.6.0] `cds.xt.SaasProvisioningService` is still served for Java projects with `subscription-manager` profile.

### Removed ​

- [cds-dk@8.9.0] Removed `before:cds-watch` script.

## February 2025 ​

### Added ​

- [cds-compiler@5.8.0] Type definitions can now be projections on other types, i.e. `type Proj : projection on OtherType { elem }`. Use it to create types based on other types, e.g. by selecting only certain elements. Only available with the new parser (`newParser: true`)
- [cds-compiler@5.8.0] Analyze enum symbols like `#ENUM_SYMB` in all (sub) expressions and conditions. It can be validated if the compiler can deduce its `enum` type from its use context: when the enum symbol is used as `default` value, `select` column expression, argument when navigating along an association to an entity with a parameter, or argument of a `cast` function call, or
- when the enum symbol is compared to a reference or `cast` function call; we consider the operators `=`, `<>`, `!=`, `in`, `not in` and also analyze enum symbols as `when` operands if the `case` operand is a reference/`cast`.
- We not only consider simple enum symbols, but also lists of enum symbols (on the right side of `in`/`not in`), and a `case … end` (sub) expression with enum symbols after the `then`s and/or the `else`.
- An enum symbol can be validated if the deduced type is a direct or indirect `enum` type, or an managed association with one foreign key having an `enum` type.
- For the effects in the compiler, IDE and backends, see the changelog entry for v5.7.0. Hint: the deprecated hdbcds backend does not support enum symbols.
- Remark: the support for enum symbols used as annotation values is still limited.

- [cds-compiler@5.8.0] to.sql.migration: Allow extending `precision` of `cds.Decimal` and allow extending `scale` if `precision` is increased by at least the same amount.
- [cds-compiler@5.8.0] to.edm(x): `@assert.range` now supports "exclusive" values by writing values in parentheses such as `[ (1), (2) ]`, as well as "infinite" by using `[ _, _ ]`.
- [cds-compiler@5.8.0] for.odata/to.edm(x)/for.seal: Propagate annotation expressions from managed associations to the foreign keys

### Changed ​

- [cds-compiler@5.8.0] Top-level CSN property `csnInteropEffective` is ignored and no longer warned about.
- [cds-compiler@5.8.0] Update OData vocabularies: 'Analytics', 'Common', 'Hierarchy', 'UI'

### Fixed ​

- [cds-dk@8.7.3] `cds compile -o` fixes the output file name in `-o .json`.
- [cds-dk@8.7.3] `cds lint` won't stumble over scalar config objects anymore.
- [cds-dk@8.7.3] `cds init` uses latest Maven Java archetype version 3.7.2 for creating Java projects.
- [cds-dk@8.7.3] `cds deploy --to hana --dry` doesn't exit with a `TypeError` if there are no models.
- [cds-dk@8.7.3] `cds add ias` fixes a few scenarios in combination with multitenancy.
- [cds-dk@8.7.2] `cds compile -o` with a file name such as `cds c srv/cat-service.cds -o srv/cat-service.json`.
- [cds-dk@8.7.2] `cds compile` without `-o` doesn't print the file name header for single services any more.
- [cds-dk@8.7.2] `cds add workzone` in combination with multitenancy doesn't throw an error any more.
- [cds-dk@8.7.2] `cds import --from rfc` stores the input file again in `srv/external//...` instead of `srv/external/...`.
- [cds-dk@8.7.2] `cds import --name` no longer crashes with a `TypeError`.
- [cds-dk@8.7.2] `cds import --out ` no longer crashes with a `Error: EEXIST`.
- [cds-dk@8.7.2] `BuildError` no longer cuts off its stack.
- [cds-dk@8.7.2] `cds bind -a` doesn't concurrently try to check the Cloud Foundry version or OAuth token.
- [cds-dk@8.7.2] `cds import` now resolves target of association/composition correctly for multiple schema files.
- [cds-dk@8.7.1] `cds add mta` now sets `parameters.instances` explicitly to `1` in Java projects, same as for Node.js projects.
- [cds-dk@8.7.1] `cds add mta` does not add the `readiness-health-check-type` and `readiness-health-check-http-endpoint` properties to the `mta.yaml` any more.
- [cds-dk@8.7.1] `cds add -p` correctly parses plugin-contributed options.
- [cds-dk@8.7.1] `cds watch` correctly escapes its default ignored directories on Windows.
- [cds-dk@8.7.1] `cds compile` correctly uses `--service=all` as its default.
- [cds-dk@8.7.1] `cds add ias` correctly writes MTX sidecar config in combination with `cds add multitenancy`.
- [cds-compiler@5.8.0] New CDL parser: parse all entity definitions using `projection on` without a terminating `;` if they had been accepted by the old parser, i.e. for compatibility, we gave up the idea of removing the existing special handling in this case.
- [cds-compiler@5.8.0] Old and new parser: issue a warning for an ignored filter on the result of a function or method call.
- [cds-compiler@5.8.0] CSN annotation expressions with value `true` for `=` were not checked.
- [cds-compiler@5.8.0] Annotation `@Core.Computed` was not set for select items that are paths into structured parameters.
- [cds-compiler@5.8.0] Annotation expression path rewriting has been improved. Paths on foreign keys are rewritten.

- [cds-compiler@5.8.0] for.seal: References into structured parameters were incorrectly flattened.
- Set `@cds.persistence.name` only on persistence-relevant things.

- [cds-compiler@5.7.4] New CDL Parser (option `newParser: true`) Improve code completion
- Fix further edge cases in error recovery

- [cds.java@3.7.2] Fixed performance problem in `cds-feature-change-tracking` when `Update` or `Upsert` statements are inspected for change-tracked elements.
- [cds.java@3.7.2] Fixed a bug, causing statements using paths in the source to fail when deep authorization is enabled.
- [cds.java@2.10.7] Fixed a bug in `cds-feature-change-tracking` causing the changed values for targets of associations not to be logged when the same type was referenced multiple times.
- [cds.java@2.10.7] Fixed performance problem in `cds-feature-change-tracking` when `Update` or `Upsert` statements are inspected for change-tracked elements.
- [cds4j@3.7.2] Fixed a bug, causing deep updates on projections with aliased keys to fail
- [cds4j@2.10.7] SAP HANA HEX mode: fixed fallback to non-hex SQL on "HEX enforced but cannot be selected" errors on HANA QRC 4/2024
- [cds4j@2.10.7] Fixed deep updates on projections with aliased keys
- [cds4j@2.10.7] Fixed missing foreign key propagation in deep updates and upserts
- [cds@8.7.2] Strip `Z` suffix of values of `cds.Timestamp` with OData type `Edm.DateTime`
- [cds@8.7.2] Skip validation for mandatory fields in update scenarios for entities in draft activation
- [cds@8.7.2] `cds.compile.to.yaml` escapes strings including colons if necessary
- [cds@8.7.1] Loading of CAP Plugins implemented in Typescript
- [cds@8.7.1] `Location` header if read after write returns empty result due to missing read authentication
- [cds@8.7.1] Enable accessing `req.params` when handling requests on parameterized views
- [cds@8.7.1] `cds.connect.to(class {...})` did not call the `init` function
- [cds@8.7.1] Generic Paging/Sorting was run twice for non-draft requests
- [cds@8.7.1] Service implementation loaded from `node_modules`

## January 2025 ​

### Added ​

- [cds-dk@8.7.0] `cds watch` supports `--exclude` and `--include` options to specify additional paths to include or exclude. Alternatively, set `cds.watch.[include|exclude]` in your CDS config.
- [cds-dk@8.7.0] `cds import` now updates configuration for Java projects (in `application.yaml` etc.)
- [cds-dk@8.7.0] `cds import --config` now also accepts a string with flat key-value pairs (like `--config "credentials.destination=foo"`), which is easier to write than the current JSON string (`--config "{\"credentials\": {\"destination\": \"foo\"}}"`).
- [cds-dk@8.7.0] `cds debug` now supports Java applications, both local and remote.
- [cds-dk@8.7.0] `cds import` can now import an odata-V4 file with external dependencies(odata-V4 file). Dependencies has to be provided with -d/--dependencies option and must not have any external dependencies.
- [cds-compiler@5.7.0] Analyze enum symbols like `#ENUM_SYMB`; support starts at the following places:used as sole `default` value or `select` column expression if the element/column has a specified enum type, or
- used as sole value (in parentheses) of an annotation assignment if there is a definition for that annotation having an enum type;
- effects in compiler: complain if enum symbol is undefined
- effects in the IDE with an upcoming version of cds-lsp when compiler option `newParser` is set: offer code completion and hover information,
- effects in backends like `to.sql` (and potentially runtimes): enum symbol is replaced by corresponding string/integer value when appropriate.

- [cds-compiler@5.7.0] for.seal: Process foreign key annotations similar to to.edm(x)
- [cds.java@3.7.1] Instance based authorization can now reject CREATE/UPDATE with 400 via option `cds.security.authorization.instance-based.check-input-data`
- [cds.java@3.7.0] Added possibility to enable default translations for validation error messages by setting `cds.errors.defaultTranslations.enabled` to `true`. These translated error messages avoid references to technical entity or element names and solely rely on the message's target.
- [cds.java@3.7.0] If `cds.security.authorization.instance-based.customEvents` is disabled, instance based authorization can now reject `draftEdit` events with 403 instead of filtering via option `cds.security.authorization.instance-based.reject-selected-unauthorized-entity` as well.
- [cds.java@3.7.0] Added debug logs when calculating object key for Kafka messages.
- [cds.java@3.7.0] The goal `add` of the `cds-maven-plugin` supports adding ORD integration to a CAP Java project.
- [cds.java@3.7.0] The exposed ORD endpoint of the CAP Java application is now also shown on the index page.
- [cds.java@3.7.0] The dev-dashboard can now list all registered event handlers for application services.
- [cds.java@3.7.0] Added capabilities to selectively remove messages from the current RequestContext's message container with the new method `Messages.removeIf(Predicate)`.
- [cds.java@3.7.0] OData V4 protocol adapter now supports implicit parameter aliases for function calls.
- [cds.java@3.7.0] The goal `add` of the `cds-maven-plugin` supports adding a CAP Java Plugin, a Maven dependency and a Remote Service configuration to a CAP Java project.
- [cds.java@3.7.0] Default outboxes can now be disabled per service by setting `cds.messaging.services..outbox.enabled` to `false`.
- [cds4j@3.7.0] Allow to use predicates in the select list
- [cds4j@3.7.0] Support typed refs via `CQL.entity(ENTITY, ref)`
- [cds4j@3.7.0] Model reader: Support `$enclosed` property of associations
- [cds4j@3.7.0] Support expanding filtered associations/compositions in runtime views
- [cds@8.7.0] Allow usage of tar library (https://www.npmjs.com/package/tar) as a workaround to solve remaining issues by extension build on Windows. The tar library should be installed by app developers.
- [cds@8.7.0] `cds.ql` supports limit with an optional offset, e.g. `limit(10, 5)`
- [cds@8.7.0] Basic support for new built-in type `cds.Map`
- [cds@8.7.0] Normalization of DateTime and Timestamp payloads in new OData adapter
- [cds-mtxs@2.5.0] Running jobs time out after 90 minutes by default. This is configurable using `cds.requires.multitenancy.jobs.heartbeatAge` and `cds.requires.multitenancy.jobs.heartbeatInterval`.
- [cds-mtxs@2.5.0] Extension linter now optionally checks extensions including existing extensions. This can be enabled usingjsonc

```
"requires": {
  "cds.xt.ExtensibilityService": {
    "check-existing-extensions": true
  }
}
```

This is not available for the extension project build.
- [cds-mtxs@2.5.0] Warning when using legacy options in `cds.mtx`.

### Changed ​

- [cds-dk@8.7.0] `cds add mta` sets backend and MTX `parameters.instances` to a default of `1` for improved discoverability.
- [cds-dk@8.7.0] `cds add sample` generates sample .ts files if the project is a TypeScript project
- [cds-dk@8.7.0] `cds import` now doesn't need beta flag to populate default value for optional action and function parameters as compiler now supports default value for @Core.OptionalParameters.
- [cds-dk@8.7.0] `cds add portal` now uses a more generic sample translated title instead of "Bookshop".
- [cds-compiler@5.7.0] CDL parser: it is now recommended to set the option `newParser` to make the compiler use a CDL parser with a significantly smaller footprint (among other things). New features might only work if this option is set, see above.
- [cds4j@3.7.0] `Modifier.selectListValue` (beta) now takes an `SelectableValue` instead of a `Value`
- [cds4j@3.7.0] In-Predicate (`Value.in`) now takes a `Collection` instead of a `List`
- [cds@8.7.0] Cleanse immutable values in draft modifications
- [cds@8.7.0] Do not use compatibility mode of @sap/xssec 4, can be reverted with `cds.env.features.xssec_compat = true`
- [cds@8.7.0] `cds.Float` is now correctly deprecated in `cds.builtin.types`.
- [cds@8.7.0] Input provided via protocol adapter for elements annotated with `@cds.api.ignore` are rejected. Previously, they were ignored.

### Fixed ​

- [cds-dk@8.7.0] `cds add mta` in combination with `cds add ias` correctly adds all routes to the backend module.
- [cds-dk@8.7.0] `cds add mta` adds the DB deployer module without prior installation of `@cap-js/hana`.
- [cds-dk@8.7.0] `cds add mta` adds the npm-ci builder for nodejs modules to use fixed package-lock versions for dependency vendoring.
- [cds-dk@8.7.0] `cds build --ws` will no longer require a `db/` folder in the root directory of the project.
- [cds-dk@8.7.0] `cds import` doesn't throw error while importing odata-V4 file with com.sap.vocabularies.
- [cds-compiler@5.7.2] Fix edge case in error recovery of the new CDL parser (option `newParser: true`)
- [cds-compiler@5.7.0] CDL parser: doc comment parser was susceptible to ReDos
- [cds-compiler@5.7.0] to.sql/hdi: Paths inside calculated elements that are simple functions were not properly rewritten.
- [cds-compiler@5.7.0] for.odata: Re-add foreign keys in property `targetAspect` in the OData CSN.
- [cds-compiler@5.7.0] to.edm(x): In annotation translation, by default map `SemanticObjectMappingAbstract` to `SemanticObjectMappingType` to avoid regressions.
- [cds-compiler@5.7.0] to.cdl: Fix quoting of identifier `many` in `Composition of`/`Association to`
- [cds-compiler@5.7.0] for.seal: Allow annotation paths to end in `many`-elements, not just scalar, like we allow in for.odata
- [cds.java@3.7.1] Fixed a bug in Event Mesh feature, causing a wrong webhook url registration when property `cds.messaging.webhooks.url` starts with `https://`
- [cds.java@3.7.1] Fixed a bug in Kafka feature, causing issues when a Kafka cluster has been created with public endpoints.
- [cds.java@3.7.1] Bound function calls with implicit parameter aliases now support arguments with names equal to the names of the system query options without the `$`. They must be prefixed with `@`.
- [cds.java@3.7.0] Fixed a bug in OData V4 adapter, causing `NullPointerException` when serializing complex types for requests containing `$select=*`.
- [cds.java@3.7.0] Fixed a bug in OData V2 adapter, causing incorrect statements generation for analytical view requests, containing measures in `$orderby()` not present in `$select`.
- [cds.java@3.7.0] Fixed a bug, causing a message's longTextUrl to be lost, when converting the message to an exception.
- [cds.java@3.7.0] Fixed a bug that caused a critical inconsistency to be accepted where tenants had multiple HDI containers.
- [cds.java@3.7.0] Fixed a bug with DB connection pools which caused connection errors when a tenant is moved to another HANA instance.
- [cds.java@3.7.0] Fixed a bug, causing handler annotations with type filters to prevent registration of the handler method if the type is not an interface and the service is outboxed.
- [cds.java@3.7.0] Fixed a bug, causing `ApplicationService` calls within `@Before` handlers (e.g. originating from `@assert.target`) to unexpectedly throw an exception, if error messages were written before.
- [cds.java@3.7.0] Fixed a bug in `cds-feature-change-tracking` causing the changed values for targets of associations not to be logged when the same type was referenced multiple times.
- [cds.java@3.7.0] Deep authorization checks are not performed on filtered compositions anymore
- [cds4j@3.7.0] SAP HANA HEX mode: fixed fallback to non-hex SQL on "HEX enforced but cannot be selected" errors on HANA QRC 4/2024
- [cds4j@3.7.0] Fixed missing foreign key propagation in deep updates and upserts
- [cds@8.7.0] Narrowed down peer dependency version of `express` to `^4`
- [cds@8.7.0] OData, REST: Responses are only written in case that the response object is not already closed, which allows responding to requests directly in custom handlers. Note: Responses sent directly are not transactionally safe! Further, subsequent errors can no longer be communicated to the client!
- Note: Only respond directly in non-`$batch` requests!

- [cds@8.6.2] Crash during requests to actions with parameter `array of `
- [cds@8.6.2] Instance based restriction using `is null`
- [cds@8.6.2] Filtering of grouped result on default aggregate
- [cds@8.6.2] Multipart batch response for failed changesets
- [cds@8.6.2] Handling of invalid parentheses in OData property access
- [cds@8.6.2] Resolve view: Mixins are not in elements of projection target
- [cds@8.6.2] Input provided via protocol adapter for elements annotated with `@cds.api.ignore` can be rejected with `cds.features.reject_ignored: true`.
- [cds@8.6.1] find draft root in authorization checks when entity has recursive compositions
- [cds@8.6.1] `default-env.json` was not loaded anymore when in production mode.
- [cds@8.6.1] i18n texts like `1` or `true` were returned as numbers, or booleans instead of strings
- [cds@8.6.1] CSN files produced by `cds build` now again contain information to resolve handler files. That was broken in case of reflected/linked models set by e.g. plugins.
- [cds@8.6.1] `average` aggregation used with draft enabled entities
- [cds-mtxs@2.5.1] Schema evolution for the `t0` tenant with `lazyT0: true`
- [cds-mtxs@2.5.1] Parallel extension requests for different tenants are now handled correctly.
- [cds-mtxs@2.5.0] Better resilience when deleting tenants.
- [cds-mtxs@2.5.0] HANA encryption parameters are now properly supported also for applications using Subscription Manager.
- [cds-mtxs@2.5.0] Limit check for field extensions now correctly sums up all separately added fields.
