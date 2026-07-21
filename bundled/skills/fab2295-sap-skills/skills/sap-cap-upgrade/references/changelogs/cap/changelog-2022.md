<!-- mirror: https://cap.cloud.sap/docs/releases/2022/changelog -->
<!-- fetched: 2026-05-09T02:26:15.335Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# Changelog 2022 ​

## December 2022 ​

### Added ​

- [cds-dk@6.4.0] `cds add helm` now supports App Router.
- [cds-dk@6.4.0] `cds subscribe --local` starts `@sap/cds-mtxs` locally instead of contacting a running instance via URL.
- [cds-dk@6.4.0] `cds unsubscribe` removes the subscription of a tenant from a SaaS app.
- [vscode-cds@6.4.0] CAP notebooks:possibility to declare variables and use them in magic commands, shell cells and terminal cells
- magic command `%%systeminfo` to render system information into the notebook
- magic command `%%writefile` with append option `-a`

- [vscode-cds@6.4.0] formatter: new options `whitespaceBeforeColonInAnnotation` and `whitespaceAfterColonInAnnotation` for specific configuration in annotations
- [cds-compiler@3.5.0] grammar: `localized` is now allowed in select items as well, to force the creation of convenience views.
- [cds-compiler@3.5.0] to.edm(x):Validate annotation values of OASIS/SAP vocabulary term definitions against `@Validation.AllowedValues`.
- Reveal dangling type references in produced EDM.
- `@Capabilities` 'pull up' introduced with 3.3.0 must now be switched on with option `odataCapabilitiesPullup`.

- [cds-compiler@3.5.0] If option `addTextsLanguageAssoc` is set but ignored by the compiler, an info message is emitted. This can happen if, e.g., the `sap.common.Languages` entity is missing.
- [cds-compiler@3.5.0] Add OData vocabularies 'Offline' and 'PDF'.
- [cds.java@1.30.0] A ChangeSet Context now allows registering multiple ChangeSet members. This enables independent transactions to share the same transactional boundaries. Note that independent transaction are not committed together atomically.
- [cds.java@1.30.0] A Persistence Service is now automatically created for every database service binding, not just the primary one. You can also explicitly configure additional Persistence Services with the new `cds.persistence.services` configuration. This allows to create Persistence Services for arbitrary DataSource beans present in the Spring Boot application.
- [cds.java@1.30.0] A `MessagingService` can now force a queue subscription, even if no topics are explicitly subscribed by setting `cds.messaging.services..queue.forceListening` to `true`. This is useful for scenarios where messages directly published to the queue should be received (e.g. dead-letter queues).
- [cds.java@1.30.0] A `MessagingService` now emits a `MESSAGING_ERROR` event, when processing of a message fails. This event can be used to decide if the message should be acknowledged nevertheless or if it should be redelivered by the messaging broker.
- [cds.java@1.30.0] The `cds-maven-plugin` now supports adding `@Generated` to classes generated based on the application's CDS model.
- [cds.java@1.30.0] Introduced a new experimental OData V4 response JSON serializer to improve performance. It can be enabled by setting `cds.odataV4.serializer.enabled` to `true`.
- [cds.java@1.30.0] OData v4 delta collections in deep updates (`PATCH` single entity) can now be used by adding the `@delta` suffix to the name of the collection data. Entities that shall be removed/deleted need to be marked with `@removed: {reason: 'changed'|'deleted'}`.
- [cds.java@1.30.0] The new option `cds.security.authorization.enabled: false` disables the generic authorization handler. This option must be used only for local testing where authorization checks are not required.
- [cds.java@1.30.0] The `cds-services-archetype` generates new CAP Java projects with the Spring Boot DevTools dependency included.
- [cds.java@1.30.0] Added an initial version of a Kafka implementation for the MessagingService APIs with `cds-feature-kafka`.
- [cds4j@1.34.0] Delta List support in Deep Updates and Upserts
- [cds4j@1.34.0] Type propagation for functions (min, max, toupper, count, ...)
- [cds4j@1.34.0] CDS annotation cache to reduce overall memory usage of the CDS model
- [cds4j@1.34.0] `CdsModelReader.Config` that allows UI annotation inclusion (excluded by default)
- [cds4j@1.34.0] Annotate generated accessor and builder interfaces with `@Generated`
- [cds4j@1.34.0] Add `CDS_NAME` constant to generated builder interfaces of CDS events
- [cds@6.4.0] Signatures for `ql.UPSERT`
- [cds@6.4.0] Runtime support for flat database UPSERTs
- [cds@6.4.0] `enterprise-messaging`: Support for `@sap/cds-mtxs`
- [cds@6.4.0] `persistent-outbox`: Support for parallel processing with option `parallel: true` as well as pluggable processor functions through `service.outbox.process` Beta
- [cds@6.4.0] `cds version` now also lists packages with `@cap-js/` prefix from dependencies
- [cds@6.4.0] `cds.context.http` is now available for webhook-based requests
- [cds@6.4.0] `cds build` for SAP HANA migration tables now only saves model entities annotated with `@cds.persistence.journal` as `last-dev` version.
- [cds@6.4.0] `cds deploy` now uses the `VCAP_SERVICES` environment variable (if set), and skips `cf` operations in this case
- [cap-js/graphql@0.1.0] To-many relationships are now represented by an additional nesting level which contains the fields `totalCount` and `nodes`. `totalCount` is similar to OData `$count`. `nodes` contains the fields belonging to the entity. This is similar to the GraphQL cursor connection specification, but without an additional second `edges` nesting level. The following shows an example query using the new schema structure:graphql

```
{
  AdminService {
    Books {
      totalCount
      nodes {
        title
      }
    }
  }
}
```
- [cap-js/graphql@0.1.0] Support for aliases on fields returned by mutations
- [cap-js/graphql@0.1.0] Improved support for aliases on fields that represent compositions and associations (some limitations still apply)
- [cap-js/graphql@0.1.0] Include localized `texts` fields of entities in schema generation
- [cap-js/graphql@0.1.0] Improve check to skip field `localized` during schema generation
- [cds-mtxs@1.3.3] The built-in Service Manager client now supports X.509 (mTLS) certificates in addition to the client-credentials authentication flow.
- [cds-mtxs@1.3.3] `cds-mtx` commands now exit the process correctly on SAP HANA when there's an error in the command.
- [cds-mtxs@1.3.3] SAP HANA encryption parameters are now correctly forwarded to the service-manager on subscription

### Changed ​

- [cds-dk@6.4.0] `cds add multitenancy` will not compile internal roles into the `xs-security.json` any more.
- [cds-dk@6.4.0] `cds add hana` does not create a `hdi-service-name: ${service-name}` for the database resource properties any more.
- [cds-dk@6.4.0] MTX-related commands now print usage help in case of known errors.
- [cds-dk@6.4.0] `cds import` now adds the annotation `@open` for all the Entities and ComplexTypes with attribute `Abstract` or `OpenType` and adds the same for those referred by the attribute `BaseType`.
- [cds-dk@6.4.0] `cds import` now adds default value in the CSN for the optional parameters in action/function for OData V4 files.
- [cds-dk@6.4.0] `cds init` uses latest Maven Java archetype version 1.30.0 for creating Java projects.
- [vscode-cds@6.4.0] minimum VS Code version is now 1.72.0
- [vscode-cds@6.4.0] uses classic `cds-lsp` for compiler versions < 3
- [vscode-cds@6.4.0] formatter: non-inline pre-annotations are now prefixed with an empty line to separate them from preceding elements
- [cds-compiler@3.5.0] to.edm(x):Vocabulary references to `Common` and `Core` are added to the generated EDM by default to allow usage of these vocabularies in HTTP messages even if the terms are not being used in the EDM itself.
- API representation of enum types as `@Validation.AllowedValues` has been shifted from `for.odata` to `to.edm(x)`. This allows to reuse imported enum types in new APIs.
- Messages raised from the EDM annotation renderer have been reworked with message id and enhanced message position including the annotation under investigation.
- `@Validation.AllowedValues` annotation as introduced for enum elements with 1.44.2 are now always rendered into the API regardless of `@assert.range`.

- [cds-compiler@3.5.0] to.cdl: The input CSN is no longer cloned for client-CSN and parseCdl-CSN, as the renderer does not modify it.
- [cds-compiler@3.5.0] A new warning is emitted if compositions of anonymous aspects are used with the `Association` keyword instead of `Composition`. Replace the former with the latter to fix the warning.
- [cds.java@1.30.0] The default Node.js version in goal `install-node` of the `cds-maven-plugin` is bumped to version `v16.18.1`.
- [cds.java@1.30.0] The minimum required `@sap/cds-dk` version in goal `cds` of the `cds-maven-plugin` is changed from `3.0.0` to `4.0.0`.
- [cds.java@1.30.0] The property `cds.deploy.component-scan` is superseded by documented property `cds.multitenancy.deploy.component-scan`.
- [cds.java@1.30.0] The `sap-language` query parameter now has lower priority than the `Accept-Language` header. If you require a query parameter to specify the locale use `sap-locale`, which follows BCP 47 specification.
- [cds.java@1.30.0] The `DataSource` beans created by the CAP Java SDK based on service bindings are now named `ds-` instead of earlier ``. This is to make room for a Persistence Service bean, that is now auto-configured with name ``.
- [cds.java@1.30.0] When setting `cds.datasource.csvInitializationMode` to `always` an Upsert instead of an Insert statement is executed. This enables using CSV initialization with PostgreSQL or file-based SQLite and H2.
- [cds.java@1.30.0] Annotations starting with `UI.` are no longer provided in the `CdsModel` reflection API to save memory resources. Those annotations are expected to be relevant only for Fiori UIs. In case access to these annotations is required through the reflection API, set `cds.model.includeUiAnnotations` to `true`.
- [cds.java@1.30.0] The `max-failed-attempts` property for a messaging queue configuration has been deprecated because in this case the error handler can be used for more custom scenarios.
- [cds4j@1.34.0] Optimize memory footprint of CDS Model
- [cds4j@1.34.0] Optimize memory footprint of `ResultBuilder`
- [cds4j@1.34.0] Optimize execution of to-one expands with nested to-many expands
- [cds4j@1.34.0] Optimize instantiation of `CdsDataProcessor`
- [cds@6.4.0] `.columns(…)` of both `cql.SELECT` and `cql.INSERT` give improved code completion when paired when appropriate type definitions are present
- [cds@6.4.0] Status code of error messages caused by empty `not null` fields is changed from `400` to `500` on database layer. Note that as result the error message `Value is required` in production will be replaced by `Internal server error` in the HTTP response.
- [cds@6.4.0] Underscores in environment variables can now be escaped by two `__` to set keys in `cds.env`. For example, use `CDS_FEATURES_WITH__MOCKS=...` to set `features.with_mocks`. Note that previously, this ended up as `features: { with_: { mocks:... }}`, so in rare cases, it might yield unexpected results.
- [cds@6.4.0] `persistent-outbox`: Only programming errors lead to `process.exit()`, unrecoverable ones are only logged and their `attempts` are updated to `options.maxAttempts`
- [cds@6.4.0] Global configuration of CSRF-token handling for remote services `cds.env.features.fetch_csrf` is deprecated. Instead, please use `csrf: true/false` and `csrfInBatch: true/false` in the configuration of your remote services. These options will allow to configure CSRF-token handling for each remote service separately.
- [cds@6.4.0] `cds build` no longer creates `engines` entry in package.json in case none has been defined. The Node.js version matched the minimal supported version of the CDS runtime and might therefore already be outdated.
- [cds@6.4.0] For streamlined MTX, `@sap/cds` now uses the custom SAP Service Manager client built into `@sap/cds-mtxs`
- [cds@6.4.0] Require new package `@cap-js/graphql` for `cds compile -2 graphql`
- [cap-js/graphql@0.1.0] The GraphQL protocol adapter now uses a new middlewares mechanism instead of `cds.plugins` which requires `@sap/cds` version 6.3 to run. Enable the `cds.requires.middlewares` flag and register the GraphQL protocol adapter in `cds.env.protocols` to get started.
- [cap-js/graphql@0.1.0] Replaced `debug` level query and mutation logging with improved `info` level request logging
- [cds-mtxs@1.4.0] Async API calls now have a `x-job-id` header.
- [cds-mtxs@1.4.0] Improved error handling for the Service Manager client.
- [cds-mtxs@1.4.0] When doing asynchronous updates for multiple tenants, you can now poll the status for each individual tenant. Continue using the `Location` response header to poll the status for all tenants.This is what a sample response body for an asynchronous request to `/-/cds/saas-provisioning/upgrade` looks like:

json

```
{
  "ID": "",
  "createdAt": "2022-12-12T13:07:15.817Z",
  "op": "upgrade",
  "tenants": {
      "t1": {
          "ID": ""
      }
  }
}
```

- [cds-mtxs@1.3.3] The built-in Service Manager client now supports pagination tokens. This allows for more than 1250 tenants.

### Fixed ​

- [cds-dk@6.4.0] `cds init` no longer creates `engines` entry in package.json to avoid `unsupported engine` warnings.
- [cds-dk@6.4.0] `cds subscribe` correctly exits the process after deploying to a HANA database.
- [cds-dk@6.4.0] `cds add multitenancy` doesn't create a duplicate `saas-registry` resource if there's one with `service-plan: service` any more.
- [cds-dk@6.4.0] `cds bind` now correctly maps the `hana-mt` and `sql-mt` shortcuts to the `cds.requires.db` entry.
- [cds-dk@6.4.0] `cds add mtx` no longer fails if the `mtx/sidecar` folder doesn't exist.
- [cds-dk@6.4.0] `cds compile --to xsuaa` now rejects expressions leading to invalid XSUAA attributes like `$user.foo-bar`, `$user.foo/bar`, `$user.foo.bar`
- [cds-dk@6.4.0] `cds compile --to xsuaa -o ` now sets `.json` as file ending instead of `.xsuaa`
- [cds-compiler@3.5.2] to.sql/hdi/hdbcds: Don't process references in actions, as they have no impact on the database - avoids internal errors
- [cds-compiler@3.5.0] Enums with a structured base type were accidentally not warned about if used in annotation definitions.
- [cds-compiler@3.5.0] for.odata/for.hana: Instead of parenthesising tuple expansion with `()`, put newly created expression in a `xpr` expression, if the term has more than one expansion.
- [cds-compiler@3.5.0] Annotation on indirect or inferred enum values were sometimes lost
- [cds-compiler@3.5.0] to.cdl:Certain keywords of special functions no longer add superfluous parentheses.
- Extension rendering now supports type extensions as well as `key` for elements.
- Builtins that clashed names with implicit contexts were not rendered with `cds.` prefix.
- Unknown artifacts (as can happen in parseCdl-style CSN) are now rendered as `USING` statements.
- Type extensions in `csn.extensions` (e.g. for `length`) are now rendered.

- [cds-compiler@3.5.0] to.edm(x):Fix a bug in type exposure when using `@cds.external` complex types.
- Don't remove empty `Edm.EntityContainer`.
- Aspects with actions outside of services are no longer warned about.

- [cds-compiler@3.5.0] for.hana: Fix a foreign key replacement bug during association to join translation.
- [cds.java@1.30.1] Fixed a bug that caused messages to be redelivered when using Event Mesh with webhooks, even if the error handler acknowledged the message.
- [cds.java@1.30.1] Fixed a bug that caused incompatibilities with `@sap/cds-mtxs@1.4.0` or greater.
- [cds.java@1.30.0] Fixed a bug that caused unacknowledged JMS messages to be never redelivered, except after an application restart.
- [cds.java@1.30.0] Fixed a bug that caused test classes to be included in the main compile step, when generating interfaces to `src/test`.
- [cds.java@1.30.0] Fixed a bug that caused incorrect responses when following OData next links, where `$skiptoken` had a larger value than `$top`.
- [cds4j@1.34.0] Include properties with `null` values in `toJson()` serialization
- [cds4j@1.34.0] Fix duplicate key error in deep updates/upserts
- [cds4j@1.34.0] Fixed SQlite generation for CQN select statements using `lock()`
- [cds@6.4.0] Type `expr` of CQN can now describe function calls
- [cds@6.4.0] Added missing optional `options` parameter in signature of `cds.serve`
- [cds@6.4.0] `cds deploy` handles empty result from `cf` call correctly
- [cds@6.4.0] When using CQL projections with array types, the type of the projection variable will now be correctly inferred as a single element of that array
- [cds@6.4.0] `cds deploy` logs without label
- [cds@6.4.0] Localized draft requests with nested expand in the case of `to many` now return localized data
- [cds@6.4.0] Protected service root for REST adapter
- [cds@6.4.0] `cds build` logs tar error message
- [cds@6.4.0] Resolve view only with renamed fields in orderBy case
- [cds@6.4.0] In case of `$apply` no default values for `top` or `skip` are set in subselects
- [cds@6.4.0] Environment variables like `cds.requires..kind...` now consistently override services set in e.g. `package.json`
- [cds@6.4.0] Expand of composition backlink now accesses draft instance instead of active
- [cds@6.4.0] Performance of server bootstrap for services with lots of entities
- [cds@6.4.0] Error with virtual properties in expand combined with draft
- [cds@6.4.0] req.tenant is properly propagated by custom authentication in odata and rest
- [cds@6.4.0] Error with `SiblingEntity` in draft
- [cds@6.4.0] Quoting of keys typed as `cds.String` in error targets. Error targets are a relative resource path to correlate error messages with the corresponding text input filed in the UI in an OData HTTP error response body for errors, warnings, and info messages. For example:diff

```
HTTP/1.1 400 Bad Request
OData-Version: 4.0
content-type: application/json;odata.metadata=minimal
Connection: close
Content-Length: 145
{
  "error": {
    "code": "400",
    "message": "Value is required",
-    "target": "items(ID=string-key-1)/text",
+    "target": "items(ID='string-key-1')/text",
    "@Common.numericSeverity": 4
  }
}
```
- [cds@6.4.0] Application crash if batched Uri uses invalid percent encoding
- [cds@6.4.0] `cds build` for SAP HANA no longer produces `hdbtabledata` for csv files that refer to non-existing entities. This can be the case for imported content packages that bring csv files for entities that are not used in the application model.
- [cds@6.4.0] `cds build` for SAP HANA now gives precedence for csv files from application layer. This is important for imported content packages that bring csv files that shall be overwritten in the application layer.
- [cds@6.4.0] `cds build` for Java no longer adds the service `cds.xt.MTXServices` to the application model.
- [cds@6.4.0] `cds build` no longer fails when creating large resource TAR archives for MTXS projects.
- [cds-mtxs@1.4.3] Asynchronous jobs now return a directly-consumable URL for Cloud Foundry deployments in the `Location` header.
- [cds-mtxs@1.4.3] Some incorrect status reports for the job and task polling have been fixed.
- [cds-mtxs@1.4.3] Stability improvements for SAP HANA tenant lifecycle operations, most notably unhandled promise rejections exiting the process have been fixed.
- [cds-mtxs@1.4.2] `/-/cds/jobs/pollTask` now correctly fetches the task status.
- [cds-mtxs@1.4.2] Jobs now have the correct default `RUNNING` status.
- [cds-mtxs@1.4.1] Fixed an error during parsing tenant metadata that occurs when the tenant metadata is empty.
- [cds-mtxs@1.4.1] Async upgrade parallelization via database clustering now works correctly with the new jobs service.
- [cds-mtxs@1.4.1] Improved `tenant_id` correlation for Kibana logging.
- [cds-mtxs@1.3.3] Improved error handling for the built-in Service Manager client.
- [cds-mtxs@1.3.3] Tenant metadata can now be retrieved programmatically for all tenants viajs

```
const sps = await cds.connect.to('cds.xt.SaasProvisioningService')
const tenants = await sps.get('/tenant')
```
- [cds-mtxs@1.3.3] `UPDATE`, `DELETE` and `upgrade` APIs of `cds.xt.SaasProvisioningService` can now also be called programmatically.
- [cds-odata-v2-adapter-proxy@1.9.16] Reject proxy processing of non OData services
- [cds-odata-v2-adapter-proxy@1.9.16] Use stream pipeline for result streaming
- [cds-odata-v2-adapter-proxy@1.9.16] Proxy does not end request to target anymore after writing body
- [cds-odata-v2-adapter-proxy@1.9.16] Document that managed compositions will not work correctly in Fiori Elements V2

### Removed ​

- [vscode-cds@6.4.0] OS specific CAP notebook cell types `Windows Bat (bat)`, `PowerShell`, `Shell Script (Bash)` are now replaced by cross-platform `Native Shell (shell)`
- [cds-compiler@3.5.0] to.edm(x): 'Empty Schema' warning has been removed.
- [cds@6.4.0] Removed `PreconditionFailedError` when sending a request with an `if-match` header on an entity without an etag
- [cds@6.4.0] Check for forbidden deep operations for associations on database layer. All non key fields for associations provided by request are ignored. Check https://cap.cloud.sap/docs/guides/services/providing-services#associations-vs-compositions for more information. Note that this is a breaking change for applications that rely on checks for forbidden deep operations by runtime.

## November 2022 ​

### Added ​

- [cds-dk@6.3.0] `cds deploy --to h2 --dry` to create drop/create DDL for H2. Full deployment (w/o `--dry`) is not yet supported, though.
- [cds-dk@6.3.0] `cds push |` to specify a custom extension archive by local path or download URL.
- [vscode-cds@6.3.0] CAP notebook magic command '%%extendjson' can be used to extend and overwrite existing JSON files
- [vscode-cds@6.3.0] CAP notebook now supports working directory for terminal cells
- [vscode-cds@6.3.0] formatting of artifact and type extensions
- [vscode-cds@6.3.0] syntax highlighting of element extensions
- [vscode-cds@6.3.0] syntax highlighting of numbers and some known types
- [cds.java@1.29.0] The goal `install-node` of the `cds-maven-plugin` supports basic authentication to download a Node.js distribution.
- [cds4j@1.33.0] Support comparing structured elements in where, byId and matching
- [cds4j@1.33.0] Add entity-level annotation `@cds.search.mode: 'localized-view'` to use `LIKE` on the entity or localized view in the generated SQL query.
- [cds-mtxs@1.3.2] `cds.requires['cds.xt.SaasProvisioningService'].jobs.clusterPoolSize` allows you to specify the number of concurrent HANA Cloud cluster tenant upgrades.
- [cds-mtxs@1.3.2] `cds.requires['cds.xt.DeploymentService'].hdi.create.binding_parameters` now also works with the built-in Service Manager client.

### Changed ​

- [cds-dk@6.3.1] `cds init` uses latest Maven Java archetype version 1.29.0 for creating Java projects.
- [cds-dk@6.3.1] Use `@sap/cds` 6.3.1
- [cds-dk@6.3.1] Use `@sap/cds-mtxs` 1.3.1
- [cds-dk@6.3.0] `cds add` support for classic Java projects is now removed.
- [cds-dk@6.3.0] `cds import` now adds the annotation `@cds.external` for all the definitions in the CSN along with the service.
- [cds-dk@6.3.0] `cds import` now adds `notNull` entry for all the parameters and properties in the CSN.
- [cds-dk@6.3.0] MTX Client now trims a passcode entered via prompt for convenience when pasting
- [cds.java@1.29.0] The `cds-services-archetype` generates a new CAP Java projects with a configured `@sap/cds-dk` version `6.3.0` which provides H2 support for version 2.x.
- [cds.java@1.29.0] The goal `install-cdsdk` of the `cds-maven-plugin` requires a `@sap/cds-dk` version configured, the parameter `version` is mandatory now. A default value is not provided anymore and the Maven build will fail without this parameter.
- [cds-mtxs@1.3.2] Error handling for the built-in Service Manager client is improved.
- [cds-mtxs@1.3.1] `cds.requires.multitenancy.for` settings have been moved to `cds.requires['cds.xt.DeploymentService'].for`.

### Fixed ​

- [cds-dk@6.3.0] MTX Client now ignores a username potentially saved for the current project, if a passcode is given
- [cds-dk@6.3.0] MTX Client now treats keytar as optional unless explicitly running `cds login`
- [cds-dk@6.3.0] `cds import` now captures the documentation properly for all the EntitySet referring to same EntityType.
- [cds-dk@6.3.0] `cds deploy --to sql` now produces 'plain' SQL again, suitable for e.g. H2. In 6.2 it produced 'sqlite' dialect, erroneously.
- [cds-dk@6.3.0] `cds compile --to openapi` now fixes the duplication of fields in `required` section.
- [cds-dk@6.3.0] `cds lint` now recognizes ESLint configurations from package.json.
- [vscode-cds@6.3.0] fix various axios related bugs
- [vscode-cds@6.3.0] formatting of extensions with selectItems
- [vscode-cds@6.3.0] format-cds script didn't find .cdsprettier.json
- [cds-compiler@3.4.4] compiler: CSN flavor `gensrc` (known as `xtended` in `@sap/cds`) lost annotations on enum values and projection columns.
- [cds-compiler@3.4.2] Don't propagate `@cds.external` (The CDS Importer adds `@cds.external` for all imported definitions beginning with cds-dk@6.3.0, see CAP release log).
- [cds-compiler@3.4.2] for.odata: Ignore all `@cds.external` definitions.
- [cds-compiler@3.4.2] to.sql: For sql dialect `h2`, don't turn a Decimal with length 0 into a Decfloat.
- [cds-compiler@3.4.2] Extending a projection with an aspect could result in incorrect auto-redirection.
- [cds-compiler@3.4.2] Annotations of aspects were not properly propagated to projections under some order-specific circumstances.
- [cds.java@1.29.1] The tenant's token issuer URL used to obtain tokens for auditing, is now correctly determined by the Audit Log Client library, avoiding NullPointerExceptions.
- [cds.java@1.29.1] Fixed a bug that caused Deploy main method to return with an error in case several tenants are updated and streamlined MTX is configured.
- [cds.java@1.29.1] Fixed a bug that caused the drafts of entities with etags not to be canceled when the active entity was deleted.
- [cds.java@1.29.1] Fixed a bug that caused access to a recycled HttpServletRequest, when accessing the Request Context in an asynchronous thread.
- [cds.java@1.29.0] Fixed a bug causing `not null` validation errors on action and function parameters to directly throw a `ServiceException` instead of being collected into the list of error messages.
- [cds4j@1.33.0] Fixed handling of an unrecognized query definition, when modeling an unmanaged association in a service entity.
- [cds4j@1.33.0] Fixed handling of values of type `java.lang.Short` mapped to `cds.UInt8` and `cds.Int16` in `CdsTypeUtils`.
- [cds4j@1.33.0] Fixed a bug that triggered exception `CdsElementNotFoundException` during search on entities that are projections or views on entities annotated with `@cds.search` with searchable elements excluded.
- [cds@6.3.2] `cds deploy` reports errors correctly
- [cds@6.3.2] Reference resolution in QL API
- [cds@6.3.2] `cds.parse.path` to correctly handle special characters
- [cds@6.3.2] `cds build` issues on Windows: build with large number of files and build on Git Bash.
- [cds@6.3.2] `odata` as default protocol for enabled middlewares feature
- [cds@6.3.1] `cds build` no longer reports false positive validation errors for built-in MTX models like `@sap/cds/srv/mtx` or `@sap/cds-mtxs/srv/bootstrap`
- [cds@6.3.1] `cds deploy` handles empty result from `cf` call correctly
- [cds@6.3.1] `$search` fails on columns composed by a CQL expression that uses the SAP HANA `coalesce` predicate
- [cds@6.3.1] Draft ownership was erroneously checked for bound actions on active instances
- [cds@6.3.1] `cds watch/run/serve --with-mocks` no longer start randomly with missing mocked services. This could happen if previous runs crashed with errors and left bad state in the local service registry.
- [cds-mtx@2.6.4] Full tenant metadata is stored again when running the subscription from CAP java
- [cds-mtx@2.6.4] APIs can now be run without express app
- [cds-mtx@2.6.4] Improved filter for technical tenants when getting all tenant ids
- [cds-mtxs@1.3.2] `cds-mtx` commands now exit the process correctly.
- [cds-odata-v2-adapter-proxy@1.9.15] Keep `ID__` parameter as query option for bound action/function on analytical entities
- [cds-odata-v2-adapter-proxy@1.9.15] Remove introduced query option `select` for bound action calls on analytical entities again
- [cds-odata-v2-adapter-proxy@1.9.14] Provide `value` section of `ID__` aggregation key as query option `select` to bound action handler
- [cds-odata-v2-adapter-proxy@1.9.14] Accept aggregation annotations in lowercase and uppercase writing
- [cds-odata-v2-adapter-proxy@1.9.14] Support `@Aggregation.ReferenceElement` and `@Aggregation.Reference` annotations to perform aggregation on different element
- [cds-odata-v2-adapter-proxy@1.9.14] Only a single aggregation reference element is supported, specified as array with single element, e.g. `['element']`
- [cds-odata-v2-adapter-proxy@1.9.14] Cast aggregation values of `#COUNT_DISTINCT` to `Integer` type to be represented as number (not as string), if typed accordingly
- [cds-odata-v2-adapter-proxy@1.9.14] Map default aggregation `#COUNT` to virtual property `$count` of `$apply`
- [cds-odata-v2-adapter-proxy@1.9.14] Remove unneeded temporary aggregation `$COUNT`. Use `#COUNT` instead.
- [cds-odata-v2-adapter-proxy@1.9.13] Escape entity key value for bound action key parameter mapping
- [cds-odata-v2-adapter-proxy@1.9.13] Support action parameters that overload bound entity key names
- [cds-odata-v2-adapter-proxy@1.9.13] Support action/function on analytical entities via `ID__` aggregation key
- [cds-odata-v2-adapter-proxy@1.9.12] Fix `$metadata` lookup with query options
- [cds-odata-v2-adapter-proxy@1.9.11] Support new CDS integer types
- [cds-odata-v2-adapter-proxy@1.9.11] Fallback target `auto` to `default` target until dynamic `target/port` assignment is available
- [cds-odata-v2-adapter-proxy@1.9.11] Prevent loading OData V4 `$metadata` when OData V2 `$metadata` is requested
- [cds-odata-v2-adapter-proxy@1.9.11] Fix draft requests re-write for `$filter`
- [cds-odata-v2-adapter-proxy@1.9.11] Proxy option to disable `x-forwarded` header processing (`processForwardedHeaders: false`)

## October 2022 ​

### Added ​

- [cds-dk@6.2.2] `cds deploy --to postgres --dry` to create drop/create DDL for PostgreSQL. Full deployment (w/o `--dry`) is not yet supported, though.
- [cds-dk@6.2.0] `cds import` now imports Singleton entities for OData V4 files.
- [cds-dk@6.2.0] `cds deploy` now supports the new default`.sqlite` file ending
- [cds-dk@6.2.0] `cds add mta` no longer creates a `before-all` custom build command for Java single and multi tenant applications. Custom build commands are defined for `db-deployer` and `mtx/sidecar` modules instead.
- [cds-dk@6.2.0] `cds import` now supports enum types for OData V4
- [cds-dk@6.2.0] `cds add enterprise-messaging` can be now be used to set up configuration and deployment descriptors for SAP Event Mesh.
- [cds-dk@6.2.0] `cds add` now throws an error if no facet is passed.
- [cds-dk@6.2.0] `cds watch` now also considers more files from SAP Fiori (`change,variant,ctrl_variant,ctrl_variant_change,ctrl_variant_management_change`)
- [cds-compiler@3.4.0] to.sql: Add support for sql dialect `h2`, which renders SQL for H2 2.x
- [cds.java@1.28.0] CSV files with strings quoted with `"`, escaped characters and tabs as the delimiters are now supported.
- [cds.java@1.28.0] The `UserInfo` resulting from IAS-based authentication now contains all (custom) attributes from the ID token.
- [cds.java@1.28.0] Using streamlined MTX (configured multitenancy sidecar with `@sap/cds-mtxs`) it is now possible to use the SQLite files created by it as a tenant databases when your CAP application is executed locally.
- [cds.java@1.28.0] Validation annotations `@mandatory`, `@assert.format` and `@assert.range` and the `not null` constraint are verified on parameters of actions and functions. The validations can be disabled with configuration option `cds.query.validation.parameters.enabled` set to `false`.
- [cds.java@1.28.0] `CdsThreadContextDecorator` that ensures CDS request context propagation to async callables executed by CloudSDK's `ThreadContextExecutorService` with CloudSDK 4.
- [cds4j@1.32.0] PostgreSQL: use session config variables to support localized views and temporal data
- [cds@6.3.0] Additional type signatures for service methods in the query API
- [cds@6.3.0] In case of error in a batch request, the @Core.ContentID is added to the details of the error message
- [cds@6.3.0] Extensibility: Use i18n files from extensions in edmx calculation
- [cds@6.3.0] In messaging, you can listen to all messages in a queue by subscribing to `'*'`
- [cds@6.3.0] Improved Log formatting for Cloud Foundry
- [cds@6.3.0] In remote services: Correct OData type conversion when using an imported csn
- [cds@6.3.0] Types for `SELECT.forUpdate({wait})`
- [cds@6.3.0] `cds.ql` now provides a dedicated method `.alias()` to choose table aliases, e.g.:js

```
SELECT.from(Authors).alias(a)
```

Note: unfortunately we can't use method `.as()` instead of `.alias()` for compatibility reasons
- [cds@6.3.0] `cds.ql` now supports constructing queries with `where exists` clauses, e.g.:js

```
SELECT.from(Authors).where({exists:'books'})
SELECT.from(Authors).where({'not exists':'books'})
SELECT.from(Authors).alias('a').where({ exists: // or 'not exists'
  SELECT.from(Books).where({author_ID:{ref:['a','ID']}})
})
```

Note: last query is equivalent to first
- [cds@6.3.0] `cds compile` and `cds deploy` now also support dialect `h2`
- [cds@6.3.0] New (easier) `jwt` and `xsuaa` authentication middleware for pluggable middlewares
- [cds@6.2.0] Types for using tagged template variants of several CQL constructs
- [cds@6.2.0] Types for calling shortcut versions of CQL constructs (`SELECT(...)` in addition to `SELECT.from(...)`, etc.)
- [cds@6.2.0] Types for `cds.test`
- [cds@6.2.0] Types for `cds.log().setFormat()`
- [cds@6.2.0] Support for `redis-messaging` Beta
- [cds@6.2.0] Log the cds version when starting the server
- [cds@6.2.0] Support for non-root entities as the main draft entity
- [cds@6.2.0] Support for IAS authentication using kind `ias-auth`
- [cds@6.2.0] Warning if multiple installations of `@sap/cds` were found when serving requests
- [cds@6.2.0] Wildcard expansion `('*')` of properties in QL is now typed
- [cds@6.2.0] Support for extended models in custom transactions and background processes
- [cds@6.2.0] `cds build` logs detailed error messages if required service models cannot be resolved or aren't defined in custom build tasks.
- [cds@6.2.0] Support for additional data types `cds.UInt8`, `cds.Int16`, `cds.Int32`, `cds.Int64`
- [cds@6.2.0] Typings for `cds.utils`, `req.entity`
- [cds@6.2.0] Optimized server startup for projects with large models and high numbers of services. Can be switched off by setting config `cds.features.precompile_edms = false` in case of problems.
- [cds@6.2.0] Set default header to `application/octet-stream` while sending binary to remote
- [cds@6.2.0] OData temporal query params `$at`, `$from`, `$to`, `$toInclusive` can be used in custom handlers
- [cds@6.2.0] Reserved keywords from compiler api available at `cds.compile.to.[cdl, sql.sqlite]`
- [cds@6.2.0] Improved `winston` integration in `cds.log`
- [cds-graphql@1.2.0] Support for CDS types `cds.UInt8`, `cds.Int16`, `cds.Int32` and `cds.Int64`
- [cds-graphql@1.2.0] Map `cds.Binary` and `cds.LargeBinary` to new custom `Binary` scalar type that uses strings to represent base64url encoded binary values
- [cds-graphql@1.2.0] Map `cds.Date` to new custom `Date` scalar type that uses strings to represent date values in the ISO 8601 format `YYYY-MM-DD`
- [cds-graphql@1.2.0] Map `cds.DateTime` to new custom `DateTime` scalar type that uses strings to represents datetime values in the ISO 8601 format `YYYY-MM-DDThh-mm-ssTZD`
- [cds-graphql@1.2.0] Map `cds.Decimal` to new custom `Decimal` scalar type that uses strings to represent exacted signed decimal values
- [cds-graphql@1.2.0] Map `cds.Int16` to new custom `Int16` scalar type that represents 16-bit signed integer values
- [cds-graphql@1.2.0] Map `cds.Int32` to the GraphQL built-in scalar type `Int`
- [cds-graphql@1.2.0] Map `cds.Integer64` and `cds.Int64` to new custom `Int64` scalar type that uses strings to represent 64-bit signed integer values
- [cds-graphql@1.2.0] Map `cds.Time` to new custom `Time` scalar type that uses strings to represent time values in the ISO 8601 format `hh:mm:ss`
- [cds-graphql@1.2.0] Map `cds.Timestamp` to new custom `Timestamp` scalar type that uses strings to represents timestamp values in the ISO 8601 format `YYYY-MM-DDThh-mm-ss.sTZD` with up to 7 digits of fractional seconds
- [cds-graphql@1.2.0] Map `cds.UInt8` to new custom `UInt8` scalar type that represents 8-bit unsigned integer values
- [cds-mtxs@1.3.0] `cds.requires.multitenancy.for` lets you define tenant-specific creation and deployment configuration.For example: parameters for `t0` onboarding can be specified via `cds.requires.multitenancy.for.t0`. Analogous to the configuration in `cds.xt.DeploymentService` you can specify options for `create` and `deploy`.

- [cds-mtxs@1.3.0] `cds.xt.DeploymentService`: The `t0` tenant is now onboarded on startup.
- [cds-mtxs@1.3.0] `POST /-/cds/deployment/subscribe` saves onboarding metadata in `t0`.
- [cds-mtxs@1.3.0] `POST /-/cds/deployment/unsubscribe` removes onboarding metadata for `t0`.
- [cds-mtxs@1.3.0] [BETA] Command line tool `cds-mtx` now also allows to run `upgrade` in an application environment, e. g. `npx cds-mtx upgrade tenant1` or `cds-mtx upgrade tenant1` if you have installed `@sap/cds-mtxs` globally. This redeploys the current application model. Potential service handlers can be registered in `cli.js` (`server.js` is not loaded)
- [cds-mtxs@1.2.0] `cds.xt.DeploymentService`: Additional parameters for HDI deployment (`@sap/hdi-deploy`) can now be added via the subscription request or the `cds` environment. Via additional parameter in the subscription payload:

json

```
{
  "tenant": "tenant",
  "_": {
    "hdi": {
      "deploy": {
        "auto_undeploy": "true"
      }
    }
  }
}
```

Via `cds` environment:

json

```
...
"cds": {
  "requires": {
    "cds.xt.DeploymentService": {
      "hdi": {
        "deploy": {
          "auto_undeploy": "true"
        }
      }
    }
  }
}
```

- [cds-mtxs@1.2.0] `PUT /-/cds/saas-provisioning/tenant/` saves subscription metadata.
- [cds-mtxs@1.2.0] `GET /-/cds/saas-provisioning/tenant/` returns the saved tenant metadata for ``.
- [cds-mtxs@1.2.0] `GET /-/cds/saas-provisioning/tenant` returns the saved tenant metadata for all tenants.
- [cds-mtxs@1.2.0] `GET /-/cds/deployment/getTables(tenant=')` returns all deployed tables for a tenant.
- [cds-mtxs@1.2.0] [BETA] Command line tool `cds-mtx` allows to run `subscribe and unsubscribe` in an application environment, e. g. `npx cds-mtx subscribe tenant1` or `cds-mtx subscribe tenant1` if you have installed `@sap/cds-mtxs` globally

### Changed ​

- [cds-dk@6.2.3] Use `@sap/cds` 6.2.3
- [cds-dk@6.2.3] Use `@sap/hdi-deploy` 4.5.0, which brings support for Node 18
- [cds-dk@6.2.0] `cds add data` no longer creates CSV headers in UPPERCASE, but keeps the original case of the declared element. Both styles work, but the latter is preferred.
- [cds-dk@6.2.0] `cds pull` requires `@sap/cds` 6.2 or higher
- [cds.java@1.28.0] UUID keys and `@cds.on.insert` values are not generated for `Upsert` anymore. Key values need to be included in the upsert data, otherwise use `Insert`. `@cds.on.insert` values can be given in the upsert data, but are not added automatically anymore, to not overwrite them in case the entity already exists on the database. The legacy behavior can be enabled with configuration option `cds.sql.upsert.strategy` set to `replace`.
- [cds4j@1.32.0] Removed any normalization of incoming locales. In standard CAP Java use cases (cds4j is called by cds-services) the locales are normalized by inbound adapters e.g. the OData adapters as defined here. Other components consuming CDS4j must handle locale normalization as part of the client code.
- [cds4j@1.32.0] Upsert: Use DB upserts instead of delete & insert and execute deep to-one upserts w/o selecting the target entity. Note that this optimization leads to orphans if the key value of an entity in a to-one composition is changed. The legacy behavior can be enabled with configuration option `cds.sql.upsert.strategy` set to `replace`.
- [cds4j@1.32.0] use ILIKE operator for search on H2 and PostgreSQL
- [cds@6.3.0] In `enterprise-messaging`, emitting CloudEvents messages sets the HTTP header `Content-Type: application/cloudevents+json`
- [cds@6.3.0] Added type definition for `cds.User`
- [cds@6.2.0] `cds.debug()` now returns undefined instead of falsy if debug is switched off. This allows usages like that:js

```
const DEBUG = cds.debug('whatever')
DEBUG?.(...)
```
- [cds@6.2.0] All MTX-related modules have been refactored and moved to `@sap/cds-mtxs`. Ensure to also upgrade to latest version of `@sap/cds-mtxs` when upgrading `@sap/cds` to avoid any breaking change effects.
- [cds@6.2.0] SQLite database file endings have been changed to `.sqlite`, so third-party tools (e.g. VS Code extensions) can deduce the file type.
- [cds@6.2.0] Method `disconnect()` in db services empties db pool w/o removing db services. In special cases (like tests) cleaning-up db service should be done manually while deleting `cds.services.db` and `cds.db`.
- [cds@6.2.0] Prefer HANA driver that is required in package.json of project root
- [cds-mtx@2.6.3] `polling_interval_millis` set for `@sap/instance-manager` has been increased to `3000`
- [cds-graphql@1.2.0] Don't generate fields that represent compositions of aspects within types that represent services
- [cds-graphql@1.2.0] Map `cds.Double` to GraphQL `Float` scalar type as it is capable of signed double‐precision
- [cds-mtxs@1.3.0] `@sap/instance-manager` has been replaced by a custom Service Manager client, which is now the default. You can switch back to the `@sap/instance-manager`-based client by setting `cds.requires['cds.xt.DeploymentService']['old-instance-manager']` to `true`.
- [cds-mtxs@1.2.0] `@sap/cds-mtxs@1.2.0` requires `@sap/cds@6.2`
- [cds-mtxs@1.2.0] `POST /-/cds/saas-provisioning/upgrade` accepts a list of tenants like `upgrade(['t1', 't2'])`.`upgrade(['*'])` upgrades all tenants.

- [cds-mtxs@1.2.0] `POST /-/cds/saas-provisioning/upgrade` gets its tenants from the `t0` cache instead of the `saas-registry` service.
- [cds-mtxs@1.2.0] `POST /-/cds/saas-provisioning/upgradeAll` has been deprecated and will be removed.
- [cds-mtxs@1.2.0] `POST /-/cds/deployment/unsubscribe` is now idempotent for HANA as well.
- [cds-mtxs@1.2.0] Polling interval to service-manager in `@sap/instance-manager` options has been increased to reduce rate-limiting problems.

### Fixed ​

- [cds-dk@6.2.3] `cds mock` now prefers a local `@sap/cds` installation, like other `cds` commands as well.
- [cds-dk@6.2.2] `cds deploy --to sql` now honors the `cds.sql.dialect` configuration to specify SQL dialects like `postgres`.
- [cds-dk@6.2.1] Installation errors with unresolvable `@sap/hdi` 4.4.0 are fixed.
- [cds-dk@6.2.0] `cds import` now imports csn for OData V2 file even if the `association set` is missing and throws error if the corresponding `association` is missing.
- [cds-dk@6.2.0] `cds import` now adds the annotation `@odata.Precision` entry only if precision > 0 for Edm.DateTime and Edm.DateTimeOffset.
- [cds-dk@6.2.0] `cds compile --to openapi` now has schema Objects for `-create` and `-update` to only advertise "deep" insert/update for containment navigation properties. Non-containment navigation properties are no longer mentioned.
- [cds-dk@6.2.0] `.sqlite` files are now git-ignored in new projects created with `cds init`
- [cds-dk@6.2.0] `cds compile --to openapi` now fixes the issue of failing range assertions for an element having undefined maximum and minimum range values.
- [cds-dk@6.2.0] `cds import` now for OData V2 files doesn't throw warning for `EntityType` being referred as type in complex types, functions and actions, provided it is present in the file.
- [vscode-cds@6.2.1] syntax highlighting of comments
- [cds-compiler@3.4.0] Properly report an error for bare `$self` references, except in the `on` condition of unmanaged associations.
- [cds-compiler@3.4.0] Do not dump with references to CDS variables like `$now` in `expand`/`inline`.
- [cds-compiler@3.4.0] Properly report an error when trying to `cast` a column to an association.
- [cds-compiler@3.4.0] to.cdl: Identifiers that are always keywords in special functions are now escaped.
- [cds-compiler@3.4.0] to.edm(x): Nested annotation was not applied if outer annotation has value zero.
- Fix `AppliesTo=ComplexType, TypeDefinition` term definition directive.

- [cds-compiler@3.4.0] to.sql/hdi/hdbcds: Properly report an error for `exists` with `$self.managed-association`
- For sql dialect `hana`, add an implicit alias when using `:param` in the select list
- Handle `$self` and magic variables during expansion of nested projections

- [cds.java@1.28.1] Fixed a bug in draft handling which could prevent insertion of child entity instances via an unmanaged composition in case the parent entity has multiple compositions to the child entity.
- [cds.java@1.28.1] Fixed a bug that caused the Java CAP application not to find a service binding via its service name property in case it also bears custom tags.
- [cds.java@1.28.1] Fixed a bug that caused the results of a `Select` statement for draft-enabled entities with an ordering condition to be ordered by wrong field, for example, by own field instead of a field of the association.
- [cds.java@1.28.1] SQLite filenames `db-[tenant].sqlite` generated by configured multitenancy sidecar with `@sap/cds-mtxs` are recognized when your CAP application is executed locally.
- [cds.java@1.28.1] Fixed a bug that caused `URISyntaxException` to be thrown during access to an entities with keys that must be encoded in the URL, for example, dates and times.
- [cds.java@1.28.0] Fixed a bug, causing properties passed to `@Transactional` to be ignored when using propagation `REQUIRED`, even though a new transaction is started.
- [cds.java@1.28.0] Fixed a bug, causing data loss for OData v2 `Edm.DateTime` properties without `sap:display-format: 'Date'`.
- [cds.java@1.28.0] Draft GC will no longer display full stack of an exception if it executed for the offboarded tenant.
- [cds.java@1.28.0] Fixed a gap in OData V2 which caused search texts with non-ascii-characters to be rejected.
- [cds.java@1.28.0] Fixed a bug in the CDS Maven plugin letting the build fail in case of a missing node.js installation even if the CDS build should be skipped by configuration.
- [cds.java@1.28.0] Fixed a bug in OData V2, causing error messages to display the name of the exception class and generic text instead of the actual error message.
- [cds.java@1.28.0] Fixed a bug in OData V2, that produces an error message about "content-type `text/plain` not being acceptable" whenever a request using `count` or `value` parameter runs into an error
- [cds.java@1.28.0] Fixed a bug that caused to omit custom HANA service instance options during onboarding of new SaaS tenants.
- [cds.java@1.28.0] Fixed a bug that the health check reported that no DB schema for a test is available
- [cds.java@1.28.0] Fixed a bug that caused the OData V2 adapter to return internal error messages with technical details on JSON deserialization issues. The details will only appear in the application log now.
- [cds.java@1.28.0] Fixed a bug that prevented to shutdown the JVM gracefully due to a hanging background thread in case of MT scenario.
- [cds4j@1.32.1] Fixed performance issue caused by subqueries in to-many expands, make `INNER JOIN` the default expand method.
- [cds4j@1.32.0] Code generator: Fix handling of entities with dots in their name outside of a CDS context
- [cds4j@1.32.0] Fixed unrelated exception when searching, if `cds.sql.search.use-localized-view` is enabled and no locale is given.
- [cds@6.3.0] Change signature of cqn `SELECT.limit.offset` and `SELECT.limit.rows` to `val` instead of `number`
- [cds@6.3.0] Parsing of store procedure SQL calls including the schema name. For example, `CALL "SCHEMA"."PROC"(?)` and `CALL SCHEMA.PROC(?)`
- [cds@6.3.0] Add property name in the error message on validation of the value
- [cds@6.3.0] Kibana and Cloud Foundry formatter: do not log cookie header value
- [cds@6.3.0] Missing SQL aliases for `$search` queries combined with `$orderBy` query option
- [cds@6.3.0] The return value of `cds.connect` is now correctly typed as a `Promise`
- [cds@6.3.0] `req.data` is no longer modified for remote services in the case of `odata-v2` inserts
- [cds@6.3.0] `cds.localize` no longer ignores i18n files defined within CDS model scope and outside project scope
- [cds@6.3.0] Don't modify query in `fioriGenericRead` handler
- [cds@6.2.3] New continuation for incoming messages
- [cds@6.2.3] `cds.test` no longer fails if used in ESM modules with `mocha` (`ERR_REQUIRE_ESM` error)
- [cds@6.2.3] Collection-bound actions/functions don't need draft ownership check
- [cds@6.2.2] Fix environment variable `OLD_MTX`, allowing `cds build` to create artifacts for classic `@sap/cds-mtx` library
- [cds@6.2.1] In the CDS configuration, custom profiles now have precedence over the (implicit) default `[development]` profile, irrespective of insertion order.
- [cds@6.2.1] `cds test` is now compatible with new `axios` 1.x
- [cds@6.2.0] Queries like `SELECT.from(Foo).where({a:1}).or({b:2}).and({c:3})` erroneously resulted in `SELECT from Foo where (a=1 or b=2) and c=3`
- [cds@6.2.0] Signatures for QN `order_by` expressions are now in line with the capire doc
- [cds@6.2.0] Signatures for QL operations are now more specific
- [cds@6.2.0] `basic-auth` does not inherit users of `mocked-auth`
- [cds@6.2.0] `cds.localize` now ignores i18n files defined outside project scope.
- [cds@6.2.0] Allow `@Capabilities.NavigationRestrictions.RestrictedProperties` to be specified in the format `{ InsertRestrictions.Insertable: false }`
- [cds@6.2.0] Bound actions/functions while calling remote service
- [cds@6.2.0] `$search`: Search on localized projections/views does not always return the localized data
- [cds@6.2.0] `cds push` now shows better output for failed extension validations
- [cds@6.2.0] Aliased parameters in REST parser
- [cds@6.2.0] `cds.deploy` now logs the correct filename for multitenant SQLite
- [cds@6.2.0] HDI configuration data (e.g. `./cfg`, `.hdiignore`) and HANA native artifacts have not always been copied into the `sdc` folder of a MTX sidecar module
- [cds@6.2.0] OData URL to CQN parser (`cds.env.features.odata_new_parser`) now supports functions with no arguments
- [cds@6.2.0] Runtime exception for `PATCH` HTTP request with an empty payload body and read-only field
- [cds@6.2.0] Streams in draft caused SQL error
- [cds@6.2.0] Better response state handling during `cds deploy` to Cloud Foundry.
- [cds@6.2.0] Draft: patch on draft enabled entity with a composition of one
- [cds@6.2.0] Maximum stack trace exceeded in generic audit logging implementation
- [cds@6.2.0] The protocol adapter logs the decoded URI or the original one, if it is invalid
- [cds@6.2.0] REST: reject action calls with round brackets (parentheses). For example, the request `/Books(1)/bookShelf.CatalogService.rate()` is now rejected.
- [cds@6.2.0] `cds deploy` and `cds run/serve/watch` no longer print terminal escape sequences (`x1b...`) if they run non-interactively.
- [cds@6.2.0] Some fields in entities like `path` generated invalid sql
- [cds-mtx@2.6.3] `.hdinamespace` files provided as native HANA content are now included for deployment
- [cds-mtx@2.6.3] EDMX files are only generated for the default language if ad-hoc edmx compilation is enabled (`mtx.edmx.compile: true`)
- [cds-graphql@1.2.0] Omit `filter` and `orderBy` for entities which don't contain fields
- [cds-graphql@1.2.0] Don't generate fields for associations and compositions in `orderBy` input types
- [cds-mtxs@1.3.0] `/-/cds/saas-provisioning/upgrade` now also runs with DwC
- [cds-odata-v2-adapter-proxy@1.9.10] Atom format fixes
- [cds-odata-v2-adapter-proxy@1.9.10] Trim spaces for filter function parameter transformations
- [cds-odata-v2-adapter-proxy@1.9.10] Allow passing proxy options as command line env (`camelCase` to `snake_case`, escape `_` by doubling)

### Removed ​

- [cds-dk@6.2.2] `cds add notebook` removed in favor of custom notebooks in VS Code (now part of the CDS Editor)

## September 2022 ​

### Added ​

- [eslint-plugin-cds@2.6.0] New `extension-restrictions` rule that validates extension projects' models against restrictions set by the extended SaaS app.
- [vscode-cds@6.2.0] document link resolution of 'folder' using paths to csn index files
- [vscode-cds@6.2.0] new formatting options `keepPreAnnotationsInOriginalLine` and `keepPostAnnotationsInOriginalLine`
- [vscode-cds@6.2.0] auto-exposed entities are now included in semantic Outline (user setting)
- [vscode-cds@6.2.0] code completion for annotations on auto-exposed entities
- [cds-compiler@3.3.0] Nested projections can be used without `beta` option:Support `expand`: columns can look like `assoc_or_struct_or_tabalias { col_expression1, … }`, `longer.ref as name { *, … } excluding { … }`, `{ col_expression1 as sub1, … } as name`, etc.
- Support `inline`: columns can look like `assoc_or_struct_or_tabalias.{ col_expression1, … }`, `longer.ref[filter = condition].{ *, … } excluding { … }`, `assoc_or_struct_or_tabalias.*`, etc.

- [cds-compiler@3.3.0] to.sql/hdi/hdbcds/edm(x)/for.odata: Allow to structure comparison against `is [not] null`.
- [cds-compiler@3.3.0] to.sql: Support dialect `postgres` - generates SQL intended for PostgreSQL. Not supported are `cds.hana` data types and views with parameters.
- [cds@6.1.3] Configuration to change maximum body size in bytes for remote requests: `cds.env.remote.max_body_length: 1000` sets it to 1 MB
- [cds-mtx@2.6.2] Retries can now be configured with a delay (in ms)json

```
"mtx": {
   "provisioning": { "retryDelay": 1000 }
}
```
- [cds-mtx@2.6.2] Clustering of upgrade jobs by database id can be disabled to reduce service-manager workloadjson

```
"mtx": {
    "jobs": {
      "clusterbydb": false
    },
    ...
}
```

### Changed ​

- [eslint-plugin-cds@2.6.0] Renamed rule `no-join-on-draft-enabled-entities` to `no-join-on-draft`.
- [eslint-plugin-cds@2.6.0] Expanded list of reserved keywords to check for in rule `no-db-keywords`.
- [vscode-cds@6.2.0] improved Java compatibility of TextMate grammar
- [cds-compiler@3.3.0] A valid redirection target does not depend on parameters anymore. This change could induce a redirection error, which could easily solved by assigning `@cds.redirection.target: false` to the entity with “non-matching” parameters.
- [cds-compiler@3.3.0] Properly issue an error when projecting associations with parameter references in the `on` condition. Before this change, the compiler dumped when projecting such an association in a view on top.
- [cds-compiler@3.3.0] Update OData vocabularies 'Capabilities', 'Common', 'UI'.
- [cds-compiler@3.3.0] to.cdl: Extensions are now always put into property `model` of `to.cdl()`s result.
- Actions on views and projections are now rendered as part of the definition, instead of an extension.

- [cds-compiler@3.3.0] to.edm(x): `@Capabilities` 'pull up' supports all counterpart properties of `@Capabilities.NavigationPropertyRestriction` except for properties `NavigationProperty` and `Navigability`.
- [cds-compiler@3.3.0] to.hdi: Updated list of `keywords` which must be quoted in naming mode `plain`.
- [cds-compiler@3.3.0] to.sql/hdi/hdbcds/edm(x)/for.odata: Reject structure comparison with operators `,=`. Message id `expr-unexpected-operator` is downgradable to a warning.
- [cds@6.1.3] For structured input, foreign keys are generated as non-enumerable properties on application-service layer

### Fixed ​

- [cds-dk@6.1.5] `cds build` no longer erroneously warns about old `@sap/cds` versions. Previously, it warned about `@sap/cds` 4 although a newer version was installed.
- [cds-dk@6.1.4] `cds build` now works again with `@sap/cds` version 4. Previously, this silently failed with no output. However, a warning is now emitted that strongly recommends an upgrade to version 6.
- [cds-dk@6.1.3] `cds import` now gives higher precedence to complex type in case of name collision with actions or functions.
- [cds-dk@6.1.3] `cds extend` and other commands no longer fail with `TypeError: Class constructor CliError cannot be invoked without 'new'`
- [eslint-plugin-cds@2.6.0] Errors from rules are shown again in the console output
- [vscode-cds@6.2.0] fixed syntax highlighting for `extend`, attribute names, type structs, and some keywords
- [vscode-cds@6.2.0] fixed formatting of bracketed expressions and annotations standing in their own lines
- [vscode-cds@6.2.0] fixed alignment of multiple annotations per line
- [cds-compiler@3.3.2] to.edm(x): Set `Scale` (V4) or `@sap:variable-scale` (V2) attributes correctly when overwriting `cds.Decimal` with `@odata.Scale`.
- [cds-compiler@3.3.2] to.sql: For dialect `postgres`, add braces around `$now`, `$at.from` and `$at.to`.
- [cds-compiler@3.3.0] Do not issue a warning anymore when adding elements via multiple `extend` statements in the same file.
- [cds-compiler@3.3.0] An info message for annotating builtins through `extend` statements is now reported, similar to `annotate`.
- [cds-compiler@3.3.0] Fix auto-redirection for target of new assoc in query entity
- [cds-compiler@3.3.0] for.odata: `@readonly/insertonly/mandatory: false` are not expanded.
- [cds.java@1.27.3] Fixed a bug, causing custom handlers of `MtSubscriptionService` not being called when running the application with the `Deploy` class.
- [cds.java@1.27.3] Fixed a bug, causing `The URI is malformed` Exception when applying alpha-numeric `$search` in `$expand`, e.g. `Books(1)?$expand=author($search=A3B)`.
- [cds.java@1.27.3] Fixed an exception when using an EXISTS predicate in infix filter of expand.
- [cds.java@1.27.2] Fixed a bug, causing OData V2 search queries including URL-encoded non-ASCII characters to fail.
- [cds.java@1.27.2] Automatic refresh of service manager cache in instance manager client lib.
- [cds4j@1.31.2] Fix exception when using an EXISTS predicate in infix filter of expand
- [cds4j@1.31.1] Fix NPE in deep insert with null valued structured elements
- [cds4j@1.31.1] Fix exception on updates with empty entries list
- [cds@6.1.3] Deep insert/update/upsert requests where the key of an association is provided in a structured format will not be rejected anymore if the target has default or mandatory fields
- [cds@6.1.3] For some configurations, mtxs services were bootstrapped twice
- [cds@6.1.2] Missing key insertion from where clauses in references for deep update statements
- [cds@6.1.2] Prevent duplicate entries for some `INSERT` statements
- [cds@6.1.2] Log details were not properly displayed in Kibana
- [cds@6.1.2] getCsn in model-provider if `cds.requires.toggles` is false
- [cds@6.1.2] HTTP calls in messaging have the correct content length
- [cds@6.1.2] Performance issue for OData `/$count` requests
- [cds@6.1.2] Typescript definition for SQL-native variant of `srv.run`, like `srv.run('SELECT * from Authors where name like ?',['%Poe%'])`
- [cds@6.1.2] Typescript definitions for `srv.run( [query] )` and `srv.send( {query, headers} )`
- [cds@6.1.2] Typescript definitions for `cds.log` are improved, level indicators like `cds.log()._debug` added
- [cds@6.1.2] Typescript definitions for `tx` now carry additional service methods
- [cds@6.1.2] `cds login` now returns errors with a better root cause messages
- [cds@6.1.2] `$expand` requests for to-one associations that do not select the foreign key
- [cds@6.1.2] `UPDATE` statement accepts empty objects: `UPDATE('Foo').with({ bar: {} })`
- [cds@6.1.2] URI encoding of parameters in remote service calls
- [cds-mtx@2.6.2] Debug logs do no longer contain any authentication details
- [cds-odata-v2-adapter-proxy@1.9.9] Fix logging layers and debug trace activation
- [cds-odata-v2-adapter-proxy@1.9.9] Connect `cds.log` with `http-proxy-middleware`
- [cds-odata-v2-adapter-proxy@1.9.8] Fix data type conversion for single attribute value responses (incl. $value)
- [cds-odata-v2-adapter-proxy@1.9.8] Fix response mapping of parameters for `Parameters` entity
- [cds-odata-v2-adapter-proxy@1.9.8] Respect `$format=json` for service root document
- [cds-odata-v2-adapter-proxy@1.9.8] Introduce proxy options to specify OData default format (default is `json`)
- [cds-odata-v2-adapter-proxy@1.9.8] `Atom (XML)` format support
- [cds-odata-v2-adapter-proxy@1.9.7] Respect `$select` filter for `deferreds` structure
- [cds-odata-v2-adapter-proxy@1.9.7] Fix definition lookup for service entities with scoped name
- [cds-odata-v2-adapter-proxy@1.9.7] Fix definition lookup for unbound service operations (actions, functions) with scoped name
- [cds-odata-v2-adapter-proxy@1.9.7] Improve Kibana logging even more
- [cds-odata-v2-adapter-proxy@1.9.7] Use project specific logger
- [cds-odata-v2-adapter-proxy@1.9.7] Document that option `fileUploadSizeLimit` only applies to uploads via `POST` using `multipart/form-data` requests
- [cds-odata-v2-adapter-proxy@1.9.6] Improve Kibana logging
- [cds-odata-v2-adapter-proxy@1.9.6] Improve error and warning logging messages
- [cds-odata-v2-adapter-proxy@1.9.6] Make log level of `Changeset order deviation` configurable via `changesetDeviationLogLevel`. Default is now `'info'`.

### Removed ​

- [vscode-cds@6.2.0] removed `cds watch` snippet
- [vscode-cds@6.2.0] removed formatting option `keepAnnotationsInOriginalLine` (will be migrated to the new options when set in .cdsrc.json)

## August 2022 ​

### Added ​

- [cds-dk@6.1.1] `cds import` now supports OData and SAP annotations for OData V4 imports.
- [cds-dk@6.1.1] `cds compile --to openapi` defines operation-specific HTTP error response status codes with descriptions via `ErrorResponses` property of certain annotations.
- [cds-dk@6.1.1] `cds compile --to openapi` now supports `--openapi:servers` option.
- [cds-dk@6.1.1] `cds add multitenancy` will add feature multitenancy-specific configuration, without extensibility.
- [cds-dk@6.1.1] `cds add toggles` will add feature toggle-specific configuration.
- [cds-dk@6.1.1] `cds add extensibility` will add configuration for project extensibility.
- [cds-dk@6.1.1] `cds add helm` now supports resource configuration for HANA deployment job and HTML5 app deployment job.
- [cds-dk@6.1.1] `cds add helm` added JSON Schema for values.yaml
- [cds-dk@6.1.1] `cds pull` will download the current CDS model of an extended SaaS app running with @sap/cds-mtxs.
- [cds-dk@6.1.1] `cds push` will upload an extension to a SaaS app running with @sap/cds-mtxs.
- [eslint-plugin-cds@2.5.0] Flavor in `model` property on `meta` object of rule
- [eslint-plugin-cds@2.5.0] Context function `getNode()` returns Node with proper location
- [vscode-cds@6.1.0] load cds based json schemas for `package.json`, `.cdsrc.json` and `.cdsrc-private.json` dynamically based on project's cds version
- [cds-compiler@3.2.0] New Integer types with these mappings:CDSODataSQLHANA CDScds.UInt8Edm.ByteTINYINThana.TINYINTcds.Int16Edm.Int16SMALLINThana.SMALLINTcds.Int32Edm.Int32INTEGERcds.Integercds.Int64Edm.Int64BIGINTcds.Integer64
- [cds-compiler@3.2.0] Properties of type definitions and types of direct elements can now be extended, e.g. `extend T with (length: 10);`
- [cds-compiler@3.2.0] CDL parser: support SQL function `substr_regexpr` with its special argument syntax.
- [cds-compiler@3.1.0] Extending an artifact with multiple includes in one extend statement is now possible: `extend SomeEntity with FirstInclude, SecondInclude;`
- [cds-compiler@3.1.0] Aspects can now have actions and functions, similar to entities. Aspects can be extended by actions as well.
- [cds-compiler@3.1.0] `cdsc`:`toCsn` now supports `--with-locations` which adds a `$location` property to artifacts
- `toHana`/`toSql` now supports `--disable-hana-comments`, which disables rendering of doc-comments for HANA.

- [cds-compiler@3.1.0] to.hdi/sql/hdbcds: Support FK-access in `ORDER BY` and `GROUP BY`
- [cds-compiler@3.1.0] to.hdi.migration: Detect an implicit change from `not null` to `null` and render corresponding `ALTER`
- [cds.java@1.27.0] The new open-source Service Binding Access library is now used as the default source to obtain service bindings. On K8s/Kyma this enables better integration with SAP BTP Service Operator, which uses a ServiceBinding.io-based format. This allows to read service bindings with the same set of metadata as in CloudFoundry automatically.
- [cds.java@1.27.0] A new property `cds.security.authentication.mode` has been introduced which can be set to `never` (disables authentication of CAP endpoints), `always` (authenticates all CAP endpoints), `model-relaxed` (authenticates endpoints based on `@requires`/`@restrict`, defaults to public endpoints) and `model-strict` (authenticates endpoints based on `@requires`/`@restrict`, defaults to authenticated endpoints). It is set to `model-strict` by default to comply with secure-by-default.
- [cds.java@1.27.0] The `cds-services-archetype` provides the new parameter `inMemoryDatabase` to choose the in-memory database configuration for local testing in the newly created CAP Java project. Supported values are `h2` (default) and `sqlite`.
- [cds.java@1.27.0] The property `cds.odataV2.caseSensitiveFilter` now controls, if functions `startsWith`, `endsWith` and `substringOf` are handled case-sensitive in OData V2. By default these functions are case sensitive.
- [cds.java@1.27.0] The `TenantProviderService` now offers a new `readProviderTenant()` method, which provides the tenant ID of the provider. It tries to retrieve this information from an existing XSUAA, Identity (IAS) or SaaS Registry service binding.
- [cds.java@1.27.0] Added the new `cds-feature-redis` artifact providing a Redis-based `MessagingService` using Redis PubSub.
- [cds.java@1.27.0] Annotations `@Capabilities.Readable` and `@Capabilities.ReadRestrictions.Readable` are now handled.
- [cds.java@1.27.0] `ApplicationLifecycleService` now offers new event `ERROR_RESPONSE` which is triggered by OData V2 and ODdata V4 protocol adapters to enable central exception handling.
- [cds4j@1.31.0] Improve key value detection of CqnAnalyzer
- [cds4j@1.31.0] Add factory method `create` w/ key value as parameter in generated data accessor interfaces
- [cds4j@1.31.0] Optimize `Select` statement execution with large result sets
- [cds4j@1.31.0] Optimize batch `Insert` and `Update` execution
- [cds@6.1.1] The configuration schema now includes `cds.extends` and `new-fields` (in `cds.xt.ExtensibilityService`)
- [cds@6.1.1] Ability to run extension validations as part of `cds lint`
- [cds@6.1.1] The `/-/cds/login` endpoint now also supports client credentials authentication
- [cds@6.1.1] `srv.run(fn)` now accepts a function as first argument, which will be run in an active outer transaction, if any, or in a newly created one. This is in contrast to `srv.tx(fn)` which always creates a new tx.js

```
cds.run (tx => { // nested operations are guaranteed to run in a tx
  await INSERT.into (Foo, ...)
  await INSERT.into (Bar, ...)
})
```
- [cds@6.1.0] Support for `@sap/cds-mtxs` in `enterprise-messaging`
- [cds@6.1.0] Detailed information about pool state: `borrowed`, `pending`, `size`, `available`, `max` to the timeout error
- [cds@6.1.0] Odata v2 payloads for `cds.Time` are converted from hh:mm:ss to PThhHmmMssS e.g. 12:34:56 to PT12H34M56S if provided in hh:mm:ss format
- [cds@6.1.0] Odata v2 payloads for `cds.Integer` are converted to String if not provided as String
- [cds@6.1.0] New OData parser supports aliased parameters e.g. `...function(ID=@p)?@p=5`
- [cds@6.1.0] Support for locale "en_US_x_saprigi"
- [cds@6.1.0] Parameter `rows` in ql API function `limit` can be omitted for remote services, e.g. `SELECT.limit(undefined, 5)`
- [cds@6.1.0] New OData parser supports $filter with "in" operator, e.g. `$filter=ID in (1,2,3)`
- [cds@6.1.0] `cds build` copies `package.json` and `.cdsrc.json` into _main folder of MTX sidecar app.
- [cds@6.1.0] New OData parser supports null parameter in function/action, e.g `/findBooks(author=1,title=null)`
- [cds@6.1.0] New environment variable `schemas` contains locations for json schemas validating `package.json`, `.cdsrc.json` and `.cdsrc-private.json` in VS Code
- [cds@6.1.0] `cds.test` can now listen on a fixed port by way of additional arguments '--port', '<PORT_NUMBER>
- [cds@6.1.0] `cds.requires.db.kind = 'sql-mt'` is introduced as a shorthand forjs

```
"db": {
  "kind": "sqlite",
  "[production]": {
    "kind": "hana-mt"
  }
}
```
- [cds@6.1.0] `cds build` support for Streamlined MTX extension projects based on build task `mtx-extension`
- [cds@6.1.0] TS definitions for `SELECT.forSharedLock` and `SELECT.forUpdate`
- [cds@6.1.0] TS definitions for `log`
- [cds@6.1.0] Support for new cds build task option `deploy-format`. Java apps may use this option instead of the corresponding global CDS config option.
- [cds@6.1.0] The `ExtensibilityService` serves an endpoint to retrieve a subdomain-specific JWT, which is used by `cds login`
- [cds@6.1.0] The endpoint `/-/cds/extensibility/push` now checks restrictions for new extensions. The configuration is added to the `cds.xt.ExtensibilityService`json

```
"requires": {
  "cds.xt.ExtensibilityService": {
    "element-prefix": ["Z_", "ZZ_"],
    "namespace-blocklist": ["com.sap.", "sap."],
    "extension-allowlist": [
      {
        "for": ["my.bookshop"],
        "kind": "entity",
        "new-fields": 2
      },
      {
        "for": ["CatalogService"],
        "new-entities": 2
      }
    ]
  }
}
```
- [cds@6.1.0] `cds build` validates required service models `@sap/**` for MTX sidecar app and logs an ERROR if some couldn't be resolved.
- [cds@6.1.0] Configuration schema for many properties of the `cds` configuration block in `package.json` or `.cdsrc.json`, especially for `cds.requires...`
- [cds-graphql@1.1.0] Parsing of input literal values specified inline inside of GraphQL queries
- [cds-mtxs@1.1.2] `cds.xt.DeploymentService` now lets you register a `deploy` handler, invoked right before the HDI deployment is triggered.
- [cds-mtxs@1.1.0] `cds.xt.DeploymentService` can now be added via the subscription request or `cds` environment (e. g. HANA via service-manager). Via an additional parameter in the subscription payload:json

```
{
  "subscribedTenantId": "tenant",
  "eventType": "CREATE",
  "_": {
    "hdi": {
      "create": {
        "provisioning_parameters": { "database_id" : "DB_ID" }
      }
    }
  }
}
```

Via the `cds` environment:json

```
"cds": {
  "requires": {
  "cds.xt.DeploymentService": {
    "hdi": {
      "create": {
        "provisioning_parameters": { "database_id" : "DB_ID" }
      }
    }
  }
}
```

### Changed ​

- [cds-dk@6.1.2] `cds init` uses latest Maven Java archetype version 1.27.1 for creating Java projects.
- [cds-dk@6.1.1] `cds add helm` updated default resource requirements for both `java` and `nodejs` projects.
- [cds-dk@6.1.1] `cds add helm` uses servicebinding.io bindings for CAP Java services, HANA and HTML5 app deployment jobs.
- [cds-dk@6.1.1] `cds compile --to openapi` creates only component schemas for schemas referenced in operations and in other schemas.
- [cds-dk@6.1.1] `cds import` switch from `@openapi.schema` to `@JSON.Schema`.
- [cds-dk@6.1.1] `cds add mtx` will now add configuration for streamlined MTX. It effectively acts as a shortcut for `cds add multitenancy,toggles,extensibility`
- [cds-dk@6.1.1] `cds add mtx` no longer includes `hana` and `xsuaa`. To achieve the same effect as before, run `cds add mtx && cds add hana,xsuaa --for production`.
- [cds-dk@6.1.1] `cds bind -2 ` binds the CDS `auth` service to the xsuaa instance. Previously `uaa` was used. This requires `@sap/cds` 6 or higher.
- [cds-dk@6.1.1] `cds add lint:dev` updated to adjust to new api structure of `@sap/eslint-plugin-cds` v2.5.0
- [cds-dk@6.1.1] `cds init` uses latest Maven Java archetype version 1.27.0 for creating Java projects.
- [cds-dk@6.1.1] `cds login localhost: -u ` now saves username (and empty password, if applicable) with project settings for convenience.
- [cds-dk@6.1.1] `cds add` error handling is improved and will give suggestions if you make a typo.
- [cds-dk@6.0.4] `cds init` uses latest Maven Java archetype version 1.26.1 for creating Java projects.
- [cds-dk@6.0.4] Use `@sap/cds` 6.0.4
- [cds-dk@6.0.4] `cds bind` handles orgs and spaces containing commas correctly.
- [eslint-plugin-cds@2.5.0] Model Validation rules use `parsed` flavor by default (`meta.model` property)
- [eslint-plugin-cds@2.5.0] Environment rules have
- [cds-compiler@3.1.0] compiler: If an unknown file extension is used but the file starts with an opening curly brace (`{`), it will be parsed as CSN.
- [cds-compiler@3.1.0] to.edm(x): In V4 containment mode, pull up `@Capabilities` annotations from the containers to the root container (set) and translate them into corresponding `@Capabilities.NavigationRestrictions`. If a `NavigationRestriction` is already available for that containment path, capabilities are merged into this path. Capability annotation value paths are prefixed with the navigation restriction path. The capability 'pull up' has an effect on entity annotations only. `@Capabilities` assignments on compositions are not pulled up but rendered to the association type which is important to enable dynamic capabilities on 'to-many' relations and to avoid ambiguities in entity set capabilities.
- [cds-compiler@3.1.0] Update OData vocabularies 'Analytics', 'Capabilities', 'Common', 'Core', 'DataIntegration', 'Graph', 'PersonalData', 'UI', 'Validation'.
- [cds.java@1.27.0] The minimum required version of Spring Boot is now `2.7.x`. Make sure to consider the upgrade instructions in the Spring Boot 2.7 Release Notes.
- [cds.java@1.27.0] The deprecated `WebSecurityConfigurerAdapter` are migrated to `SecurityFilterChain`. As both can't coexist custom security configurations in applications need to be migrated to `SecurityFilterChain` as well.
- [cds.java@1.27.0] Projects generated with the cds-services-archetype for now explicitly use H2 v1 to avoid incompatibilities with SQL generated by CDS Compiler.
- [cds.java@1.27.0] Authentication-related settings have been moved to a new `cds.security.authentication` configuration section. Within section `cds.security` property `authenticateUnknownEndpoints` has been replaced by `authentication.authenticateUnknownEndpoints` and `openMetadataEndpoints` has been replaced by `authentication.authenticateMetadataEndpoints`. The settings `openUnrestrictedEndpoints` and `defaultRestrictionLevel` have been subsumed under the new property `authentication.mode`. All previous properties are deprecated and can still be used for compatibility.
- [cds4j@1.31.0] Disable deprecated path access via `CdsData:get`, instead use `getPath`
- [cds@6.1.0] Streamlined calculation of the difference for `DELETE` queries using `req.diff()`
- [cds@6.1.0] Improved error messages for rest / new odata parser
- [cds@6.1.0] Adjust types for `SELECT.from` and `SELECT.one` to accept array classes as well
- [cds@6.1.0] No `"` added around search values in OData v2 e.g. Foo?search=name is passed through as is
- [cds@6.1.0] If an entity can not be read after write (e.g. insert only entity) no error is shown in the log
- [cds@6.1.0] Throw not supported error for pagination in `$expand`
- [cds-mtx@2.6.1] Retries for container creation and deployment have been disabled. Retries can be configured using via cds env:json

```
"mtx": {
   "provisioning": { "retries": 2 }
}
```

retries two times after a failure.
- [cds-mtxs@1.1.1] Log and debug output is improved.

### Fixed ​

- [cds-dk@6.1.2] `cds add helm` fixed JSON Schema for `srv` property in values.yaml
- [cds-dk@6.1.2] `cds add helm` fixed env property errors for `hana_deployer` and `html5_apps_deployer`
- [cds-dk@6.1.2] `cds add data` now creates proper data file names for entities in a `context`, i.e. `sap.common-Countries.csv` instead of `sap-common-Countries.csv`
- [cds-dk@6.1.2] `cds import` now captures the parameter/property of collection type differently and the associated annotations are pulled out of the `items` object of the parameter/property entry in the csn.
- [cds-dk@6.1.2] Remove redundant `console.log()` statement in `cds lint`
- [cds-dk@6.1.2] `cds push` now shows complete error messages from extension validation
- [cds-dk@6.1.2] `cds push` and related commands now show properly formatted error messages and also fail with a non-zero exit code in error situations
- [cds-dk@6.1.1] `cds add helm:connectivity`: `connectivity.configMapName` was not used for the `connectivity-proxy-info`.
- [cds-dk@6.1.1] `cds import` replaced occurrences of `\\` with `/` in the `package.json` for Linux platforms.
- [cds-dk@6.1.1] `cds import` fixed `@Core.Description` and `doc` property duplication.
- [cds-dk@6.1.1] `cds extend` and `cds activate` no longer save any data (this is reserved to `cds login`).
- [cds-dk@6.1.1] Extensibility commands now add http (not https) to local app URLs without schema.
- [cds-dk@6.1.1] Extensibility commands don't query CF any longer when run against local apps.
- [vscode-cds@6.1.1] fixed error when text editor is not found in CAP notebook decoration
- [cds-compiler@3.2.0] An internal dump could have occurred in certain situations for models with cyclic type definitions.
- [cds-compiler@3.2.0] Annotations on inferred enum elements of views were lost during recompilation.
- [cds-compiler@3.2.0] to.cdl: Annotations on enum value in query elements were lost.
- [cds-compiler@3.2.0] for.odata: Allow dynamic shortcut annotation values (`$edmJson`).
- [cds-compiler@3.2.0] to.edm(x):Don't overwrite annotations of input model.
- Ignore `null` values in `$edmJson` strings.

- [cds-compiler@3.2.0] to.hdi.migration: Don't interpret bound action changes as element changes.
- [cds-compiler@3.1.2] to.edm(x):`@Capabilities` 'pull up' for containment trees should not prefix the dynamic annotation paths of the root container.
- Remove service namespace prefix of a parameter type for function/action annotation targets in multi schema mode if the parameter type is defined in an alternative schema.

- [cds-compiler@3.1.0] Syntax of date/time literals are now checked against ISO 8601. If the format is invalid, a warning is emitted.
- [cds-compiler@3.1.0] The code completion directly after the `(` for functions with special syntax now suggests all valid keywords, like for `extract` or `locate_regexpr`.
- [cds-compiler@3.1.0] compiler:`cast(elem as EnumType)` crashed the compiler.
- Annotations on sub-elements in query entities were lost during re-compilation.
- An association's cardinality was lost for new associations published in projections.
- Annotations on indirect action parameters were lost in CSN flavor `gensrc`.
- Re-allow `annotate` statements referring to the same element twice, even if there are annotation assignments for sub elements.
- If a file's content starts with `{` and if neither file extension is known nor `fallbackParser` is set, assume the source is CSN.

- [cds-compiler@3.1.0] all backends: references in `order by` expressions are correctly resolved.
- [cds-compiler@3.1.0] to.edm(x):Allow cross service references for unmanaged associations and improve warning message for muted associations.
- Nested `@UI.TextArrangement` has precedence over `@TextArrangement` shortcut annotation for `@Common.Text`.

- [cds-compiler@3.1.0] to.hdi.migration:Doc comments rendered the full doc comment instead of only the first paragraph, as `to.hdi` does.
- Respect option `disableHanaComments` when rendering the `ALTER` statements

- [cds-compiler@3.1.0] to.hdi/sql/hdbcds:Check for invalid usages of `$self` and give helpful errors
- Correctly resolve association-steps in the from-clause in conjunction with `exists`

- [cds-compiler@2.15.8] to.edm(x): Nested `@UI.TextArrangement` has precedence over `@TextArrangement` shortcut annotation for `@Common.Text`.
- [cds-compiler@2.15.8] to.hdi.migration:Respect option `disableHanaComments` when rendering the `ALTER` statements
- Doc comments rendered the full doc comment instead of only the first paragraph, as `to.hdi` does.

- [cds-compiler@2.15.8] compiler: An association's cardinality was lost for associations published in projections.
- [cds.java@1.27.1] Fixed a bug, causing the audit log service to throw an exception, if the user name was empty when using the `oauth2` plan.
- [cds.java@1.27.1] Fixed a bug, causing the feature-dependent EDMX to be ignored in OData V2 and V4 in single-tenancy scenario.
- [cds.java@1.27.1] Fixed a regression, causing `$metadata` response in JSON format to no longer work.
- [cds.java@1.27.0] The `mvn cds:version` goal now is able to parse the version output generated by `@sap/cds-dk@6`.
- [cds.java@1.27.0] The passwords of mock users are now encoded using the Spring Security `{noop}` encoder. This drastically improves performance. Note that mock users are not intended for productive usage.
- [cds.java@1.27.0] Fixed a bug causing the partition collector thread of the persistent outbox to crash if a non-`Exception` `Throwable` was thrown by the processed event.
- [cds.java@1.27.0] Fixed a bug causing the JMS connection reestablishment to fail for Message Queueing.
- [cds.java@1.27.0] Fixed a bug causing UTF-8 BOM headers in csv files to fail the CSV-based database initialization.
- [cds.java@1.27.0] Fixed a bug that prevented errors in remote OData requests to be written to the application logs, when the error didn't match the OData error structure.
- [cds.java@1.27.0] Fixed a bug causing character-based media streams, represented by `Reader` instances, to be handled incorrectly in OData V4.
- [cds.java@1.27.0] Fixed a bug causing an explicit `@requires: 'any'` (public endpoint) on service-level to not propagate to the entity-level.
- [cds.java@1.27.0] Fixed a bug causing errors when special characters such as `&` are used in OData V4 search phrases.
- [cds@6.1.1] Erroneous checks for `join` in `SELECT.from(SELECT.from('xxx'))`
- [cds@6.1.1] Virtual fields with default values in draft context
- [cds@6.1.1] View resolving without model information doesn't crash
- [cds@6.1.1] Unable to upload large attachments. Uploading a large attachment (base64 encoded) caused a runtime exception.
- [cds@6.1.1] `cds.Query.then()` is using `AsyncResource.runInAsyncScope` from now on. → this avoids callstacks being cut off, e.g. in debuggers.
- [cds@6.1.1] `cds.tx()` and `cds.context` have been fixed to avoid accidental fallbacks to auto-commit mode.
- [cds@6.1.1] HDI configuration data (e.g. `./cfg`, `.hdiignore`) is now included in the `resources.tgz` file which is required for Streamlined MTX.
- [cds@6.1.1] `cds deploy` accepts in addition to `VCAP_SERVICES` also `TARGET_CONTAINER` and `SERVICE_REPLACEMENTS` from vcap file when using `--vcap-file` parameter.
- [cds@6.1.1] `cds build` doesn't duplicate CSV files that are contained in `db/src/**`.
- [cds@6.1.1] Typescript issues in `apis/log.d.ts`
- [cds@6.1.1] `cds build` adds OS agnostic base model path to generated feature CSN.
- [cds@6.1.1] Unhandled promise rejection in `expand` handling
- [cds@6.1.1] `cds.context.model` middleware is not mounted for not extensible services
- [cds@6.1.1] `cds.context` continuation was sometimes not reset in REST adapter
- [cds@6.1.0] Wrong context in `tx.run(query)` when `query` is an array
- [cds@6.1.0] We now detect and ignore erroneous attempts to re-register framework-generated stubs as handlers for custom actions/functions.
- [cds@6.1.0] Emits with `persistent-outbox` also work with manual transactions
- [cds@6.1.0] You can now use `cds.ql` fluent API to query tables not in the model, but in database. For example, within `cap/samples/bookshop` this works now:sql

```
await SELECT.from('sqlite_master')
await cds.read('sqlite_master')
```

Caveat: the following undocumented usage of unqualified names happened to work in the past. But this was very fragile and caused lots of issues, and therefore was removed:sql

```
await SELECT.from('Books')
await cds.read('Books')
```

Always use qualified names, or reflected definitions instead:sql

```
const Books = 'sap.capire.bookshop.Books'
await SELECT.from(Books)
await cds.read(Books)
```

sql

```
const {Books} = cds.entities ('sap.capire.bookshop')
await SELECT.from(Books)
await cds.read(Books)
```
- [cds@6.1.0] Wrong results for expand to many without `orderBy`
- [cds@6.1.0] `cds deploy` api endpoint regex for cli now ignores trailing version info in url
- [cds@6.1.0] Default values no longer overwrite payload values on fields of new drafts
- [cds@6.1.0] Unmanaged to-one navigation caused malformed SQL statement in draft
- [cds@6.1.0] `cds.compile.to.serviceinfo` fix failure to detect Java services if `odataV4.endpoint.path` or `odataV2.endpoint.path` missing in `cds` configuration in `application.yaml`
- [cds@6.1.0] Data type conversion did not work in some expand cases
- [cds@6.1.0] Failed connection to SAP HANA with no or malformed credentials was leading to credentials being written to the log
- [cds@6.1.0] `cds build` no longer fails with an error `no such file` if one of the following files has been defined in some `srv` subfolder - `package.json, package-lock.json, .cdsrc.json, .npmrc`
- [cds@6.1.0] Tar issue on Windows: 'The command line is too long'.
- [cds@6.1.0] `$search`: Lifecycle issue that causes an empty search result when the `$search` and `$expand` query options were combined
- [cds@6.1.0] Operator `IN` with Tagged Template String Literals e.g.:sql

```
SELECT.from(Object).where`userId IN ${aUserIDs}`
```
- [cds@6.1.0] `cds build` now uses a closed version range in the node engines version of the deployed application's `package.json`
- [cds@6.1.0] `cds build` no longer generates EDMX files for services that aren't odata protocol enabled
- [cds@6.1.0] `cds deploy` handles orgs and spaces containing commas correctly
- [cds@6.1.0] Incorrect decoding of special characters when reading data of type `cds.LargeString` from SAP HANA using `hdb@^0.19.5` driver
- [cds@6.1.0] The payload is added to the delete request in rest adapter as req.data
- [cds-mtx@2.6.1] Use of legacy APIs for scope checks has been removed
- [cds-mtx@2.6.1] Better compatibility for environments without vcap-environment, especially DwC
- [cds-mtx@2.6.1] Restored compatibility for Node.js 12. In version 2.6.0, this failed with an error like `SyntaxError: Unexpected token`.
- [cds-mtx@2.6.1] Extension linters now also check types and aspects
- [cds-mtx@2.6.1] I18n file collection now works correctly with @sap/cds@6
- [cds-mtx@2.6.1] Job status of asynchronous requests to scaled applications is now returned correctly again
- [cds-mtxs@1.1.1] `cds.xt.DeploymentService` can now also be called by users with role `cds.Subscriber`.
- [cds-odata-v2-adapter-proxy@1.9.5] Fix media upload via associations/compositions using POST
- [cds-odata-v2-adapter-proxy@1.9.5] Fix duplication of streaming request data for media entity (chunked)
- [cds-odata-v2-adapter-proxy@1.9.5] Fix result structure for parameterized entities entry addressed by key (object or not found)
- [cds-odata-v2-adapter-proxy@1.9.5] Update README on sample apps
- [cds-odata-v2-adapter-proxy@1.9.4] Remove logging library `@sap/logging`. Use `cds.log` instead.
- [cds-odata-v2-adapter-proxy@1.9.4] Remove obsolete proxy option `disableNetworkLog`
- [cds-odata-v2-adapter-proxy@1.9.4] Proxy option `fixDraftRequests` suppresses unsupported draft expand to `SiblingEntity` and injects `SiblingEntity: null`

## July 2022 ​

### Added ​

- [cds-dk@6.0.0] `cds import` now supports importing external openapi specification file into CSN.
- [cds-dk@6.0.0] `cds import` now supports the `--from` option to specify the protocol for importing an external file.
- [cds-dk@6.0.0] `cds import` can be programmatically accessed using APIs `cds.import()`, `cds.import.from.edmx()`, and `cds.import.from.openapi()`.
- [cds-dk@6.0.0] `cds compile --to openapi` allows describing custom headers and custom query options.
- [cds-dk@6.0.0] `cds import` now supports `HasStream="true"` for both OData V4 and V2.
- [cds-dk@6.0.0] `cds compile --to openapi` now adds properties with `@mandatory` to the required field.
- [cds-dk@6.0.0] Added a link to VS Code CAP Notebooks documentation to `cds init --add notebooks` and `cds add notebooks`.
- [vscode-cds@6.0.0] using native `notebook` support for `cap-notebook`
- [vscode-cds@6.0.0] support for new major cds-compiler 3.0.0
- [vscode-cds@6.0.0] new user setting `cds.workspaceSymbols.caseInsensitive` (default off) to search case insensitive
- [vscode-cds@6.0.0] new user setting `cds.outline.semantical` (default off) to show outline in a rather semantical structure as opposed to a flat list
- [vscode-cds@6.0.0] analyze dependencies now supports coloring of layers for monorepos
- [vscode-cds@6.0.0] `env.cdsc` is now also considered for code completion
- [vscode-cds@6.0.0] custom requests to format given content with given options (for example, for a formatting options config UI) and to get path of options file
- [cds.java@1.26.0] Support for the new `@sap/cds-mtxs` multitenancy sidecar can now be enabled by setting `cds.multitenancy.mtxs.enabled` to `true`.
- [cds.java@1.26.0] OData V2 now also supports directly creating active versions of draft-enabled entities through `POST` by passing `{"IsActiveEntity": true}` in the payload.
- [cds.java@1.26.0] Validations of `@assert.target` now use a shared database lock when reading the target entity instance.
- [cds.java@1.26.0] Annotation `@protocol` can now be used as alias for `@protocols`. Both annotation allow single and arrayed values. You can use `@protocol: 'none'` to avoid serving a service.
- [cds.java@1.26.0] The `cds-maven-plugin` now allows to set additional environment variables when executing the goals `install-cdsdk`, `cds`, `npm` and `npx`.
- [cds4j@1.30.0] Support `@cds.java.name` on action and function parameters
- [cds4j@1.30.0] Support shared locks for pessimistic locking
- [cds4j@1.30.0] Add `CdsData::create` to create new instances of CdsData
- [cds@6.0.1] Config option `cds.env.server.port` allows to configure the port to use (in addition to `process.env.PORT` and CLI option `--port`)
- [cds-mtx@2.6.0] Support for new build task aliases `java` and `nodejs`
- [cds-graphql@1.0.0] Extracted GraphQL protocol adapter from `@sap/cds` to `@sap/cds-graphql`
- [cds-graphql@1.0.0] Support for `@sap/cds` `cds.plugins`
- [cds-mtxs@1.0.1] `@sap/cds-mtxs` now has a `peerDependency` to `@sap/cds`.

### Changed ​

- [cds-dk@6.0.3] `cds init` uses latest Maven Java archetype version 1.26.0 for creating Java projects.
- [cds-dk@6.0.3] `cds init` now creates Node.js projects with version 6 of `@sap/cds`
- [cds-dk@6.0.2] Use `@sap/cds` 6.0.2
- [cds-dk@6.0.1] Deprecated the `--for ` parameter of `cds add data` in favor of the new `--data:for`. The former is still supported, but will eventually be removed, as it collides with the general `--for ` parameter of `cds add`.
- [cds-dk@6.0.0] `cds import` now uses `@odata.Type` and `@odata.Precision` for edm to cds type mapping.
- [cds-dk@6.0.0] `cds compile --to openapi` now has better description for `$expand` query option.
- [cds-dk@6.0.0] The original package `sqlite3` is now used again in its latest version.
- [cds-dk@6.0.0] `cds import` now deprecated `cds.DecimalFloat` type.
- [cds-dk@6.0.0] `cds import` now allows OData version 4.01 edmx files and supports `Scale="floating"`.
- [cds-dk@6.0.0] `cds import` now adds `@odata.Type` annotation for `Edm.Byte` and `Edm.SByte`.
- [cds-dk@6.0.0] `cds import` now has improved tests to check `--as`option with `force` flag file overwriting.
- [cds-dk@6.0.0] `cds init` uses latest Maven Java archetype version 1.25.0 for creating Java projects.
- [cds-dk@6.0.0] `cds import` now imports edmx file without any entities containing only unbounded action/function.
- [cds-dk@6.0.0] `cds import` API now supports includeNamespaces option.
- [cds-dk@6.0.0] `cds compile --to openapi` now adds `format`, `multipleOf`, `maximum` and `minimum` to anyOf.
- [cds-dk@6.0.0] `cds import` will now mark an association as a composition when `OnDelete Action="Cascade"` is present.
- [cds-dk@6.0.0] `cds import` has deprecated `--into` option.
- [cds-dk@6.0.0] `cds bind` reads Cloud Foundry file `config.json` to get org and space information.
- [cds-dk@6.0.0] `cds deploy` now stores connection information without credentials by default in `.cdsrc-private.json`.
- [cds-dk@6.0.0] `cds deploy` has a new option `--store-credentials` to enforce the former behavior of storing credentials in `default-env.json`.
- [cds-dk@6.0.0] If a `@sap/cds` is installed locally in a project, it must be version 4 or higher for CLI commands to run.
- [cds-dk@6.0.0] `cds import` now doesn't trim the bound action/function name in the csn if the format of the name is A_B.
- [cds-dk@6.0.0] `@sap/cds` version 6 is now required in new projects added by `cds init` and `cds add`.
- [vscode-cds@6.0.3] support latest release of cds-compiler 3.0.2
- [vscode-cds@6.0.3] added authentication and new build task names to cds schema
- [vscode-cds@6.0.0] now requires NodeJS `>=16.11` (included in recent VS Code)
- [vscode-cds@6.0.0] now requires Visual Studio Code `>=1.66`
- [vscode-cds@6.0.0] use `workspace.fs` for file IO during `cds preview`.
- [cds.java@1.26.0] The default value of `cds.security.defaultRestrictionLevel` is now `authenticated-user`. Endpoints that are not explicitly annotated with `@restrict` or `@requires` now require authentication by default. To model open endpoints, you need to explicitly expose services or entities to `any` in your model.
- [cds.java@1.26.0] In case multitenancy is enabled `cds.security.openUnrestrictedEndpoints` no longer defaults to `false`. In case you annotated any services or entities explicitly with `@requires: any` they are no longer authenticated and no tenant information is available therefore. Consider removing the annotation or changing it to `@requires: authenticated-user`.
- [cds.java@1.26.0] Updated default Node.js version used by CDS Maven Plugin to `v14.19.3`
- [cds4j@1.30.0] Deprecate `CdsAssociationType::keys`, instead use `CdsAssociationType::refs`
- [cds@6.0.3] On Business Application Studio, `@sap/cds` now rejects starting on Node 12, as it does locally. This avoids cryptic follow-up errors.
- [cds@6.0.1] Plugins cannot be loaded as ES modules, but need to remain CommonJS modules
- [cds-graphql@1.0.0] Refactor GraphQL schema generation to build schema using the `GraphQL.js` `GraphQLSchema` object rather than manually building an SDL string
- [cds-graphql@1.0.0] Let `cds.tx` handle setting `cds.context` instead of setting it manually
- [cds-graphql@1.0.0] Nest `create`, `update` and `delete` mutations within the entity that they mutate instead of naming mutations by prefixing the entity with the operation they perform:graphql

```
mutation {
  AdminService {
    Books {
      create(input: { title: "Moby-Dick" }) {
        title
      }
    }
  }
}
```
- [cds-graphql@1.0.0] Replace inequality operator `<>` with `!=` generated in `CQN` by `eq` filter to align with OData protocol adapter
- [cds-graphql@1.0.0] Logging level of `query on ${entity.name}` and `mutation on ${entity.name}` messages from `log` to `debug`

### Fixed ​

- [cds-dk@6.0.3] `--vap-file` parameter of `cds deploy` is available again (removed in 6.0.0)
- [cds-dk@6.0.3] `cds add helm:connectivity`: `connectivity.configMapName` was not used for the `connectivity-proxy-info`.
- [cds-dk@6.0.3] `--vcap-file` parameter of `cds deploy` is available again (removed in 6.0.0)
- [cds-dk@6.0.3] `cds add helm:connectivity`: `connectivity.configMapName` was not used for the `connectivity-proxy-info`.
- [cds-dk@6.0.3] `cds add helm:connectivity`: Environment variables added for connectivity service for Java.
- [cds-dk@6.0.3] `cds add helm`: Generation of `xs-security.json` file works on Windows now (`cds compile srv -2 xsuaa` command failed).
- [cds-dk@6.0.1] `cds bind` api endpoint regex for cli now ignores trailing version info in url
- [cds-dk@6.0.0] `cds compile --to openapi` fixes annotations on bound action overloads.
- [cds-dk@6.0.0] `cds add cf-manifest` now uses the correct `application` plan for the `xsuaa` service
- [cds-dk@6.0.0] A combination of `cds add approuter`, `cds add mtx`, and `cds add mta` will now use a safer approach to determine the subscription URL.
- [cds-dk@6.0.0] `cds init` and `cds add` output the feature names correctly in case the names contain a dash
- [cds-dk@6.0.0] `cds compile --to openapi` fix for type error when entity/action is not specified in the service definition.
- [cds-dk@6.0.0] `cds import` API fix for race condition issue.
- [cds-dk@6.0.0] `cds somecdsfile --profile ...` (without the `compile` command) no longer ignores the given profile
- [cds-dk@6.0.0] `cds watch` got more robust against unlucky timing and no longer runs into port conflicts
- [vscode-cds@6.0.4] show not-supported warning when opening CAP Notebook page in SAP Business Application Studio
- [vscode-cds@6.0.0] fixed glitches in cds schema support for `package.json`, `.cdsrc.json` and `.cdsrc-private.json`
- [vscode-cds@6.0.0] fixed highlighting for empty block comments `/**/`
- [cds-compiler@3.0.2] to.sql: For `sqlDialect` `plain`, `$now` is replaced by `CURRENT_TIMESTAMP` again.
- [cds-compiler@3.0.2] compiler: Don't crash if a USING filename is invalid on the operating system, for example, if `\0` is used.
- Info messages for annotations on localized convenience views are only emitted for unknown ones.
- Improve error message for an `extend` statement which had added a new element and tried to extend that element further. Similarly for a new action. (If you consider this really of any use, use two `extend` statements.)

- [cds-compiler@3.0.2] for.odata: expand `@readonly`/`@insertonly` on aspects as for entities into `@Capabilities`.
- [cds-compiler@3.0.2] to.edm(x): Exclude managed association as primary key on value list annotation preprocessing.
- Don't render annotations for aspects defined in a service.

- [cds-compiler@2.15.6] Annotations on sub-elements were lost during re-compilation.
- [cds.java@1.26.1] Fixed a bug causing example tests generated by the `cds-services-archetype` to fail if `cds-starter-cloudfoundry` is present.
- [cds.java@1.26.1] Fixed a bug causing non-ASCII characters to be handled incorrectly in file-based messaging.
- [cds.java@1.26.0] Fixed a bug, causing errors produced by annotation `@assert.target` to have an incorrect target path in case of nested data.
- [cds.java@1.26.0] Fixed a bug, causing error `no target table or view available for FOR UPDATE clause` on SAP HANA when the target entity of an association annotated with `@assert.target` has localized fields.
- [cds.java@1.26.0] Fixed a bug, causing duplicate `ID__` values on OData V2 aggregation requests.
- [cds.java@1.26.0] Fixed a bug, causing CSV imports into an in-memory database to be missed for entities behind a feature flag.
- [cds.java@1.26.0] Fixed a bug, causing headers being incorrectly propagated from a `$batch` parent requests to its child requests.
- [cds.java@1.26.0] Fixed a bug, causing incorrect handling of OData nextlinks when using `$top`.
- [cds.java@1.26.0] Fixed a bug, causing incorrect results when querying OData v2 analytical views (`Aggregation.ApplySupported.PropertyRestrictions: true`) with `$count`.
- [cds@6.0.4] Local mocking of external services using `cds watch`
- [cds@6.0.3] Generic handlers for draft-related operations will trigger a READ event afterwards
- [cds@6.0.3] `file-based-messaging` only watches the file when at least one handler is registered
- [cds@6.0.3] `--vap-file` parameter of `cds deploy` is available again
- [cds@6.0.3] `cds build` no longer throws an error if `@sap/cds-mtx` library (classic MTX) isn't installed locally.
- [cds@6.0.3] `cds.spawn` no longer tries to reuse a transaction
- [cds@6.0.3] Custom query parameter caused bad request on certain characters in rest adapter
- [cds@6.0.3] `cds-ts` no longer fails with an `ERR_UNKNOWN_FILE_EXTENSION` error
- [cds@6.0.3] Timeouts when sending string payloads to remote services
- [cds@6.0.3] `cds.context.http` for `$batch` using atomicity groups
- [cds@6.0.2] Jest tests do not fail any longer because of logs during app shutdown
- [cds@6.0.2] `cds build` now uses correct `mtx/sidecar` context. This avoids redundant `cds-mtxs` npm dependency for Java projects.
- [cds@6.0.1] Removed debug log about shutdown from `cds serve`
- [cds@6.0.1] Hiding timeout error in production mode
- [cds-mtx@2.6.0] `@sap/cds-mtx` is now compatible with @sap/cds@^6.
- [cds-mtx@2.6.0] Kibana logs of asynchronous jobs now always have the correct correlation id.
- [cds-mtx@2.6.0] Upgrade of tenants with no meta tenant (for example, created by dynamic deployer) can now be upgraded again, including the creation of the missing meta tenant.
- [cds-mtx@2.6.0] Upgrade of tenants now consistently updates the base model files per tenant again.
- [cds-graphql@1.0.0] Only generate `eq` and `ne` comparison operations for boolean filters
- [cds-graphql@1.0.0] Queries on entities with names that contain underscores
- [cds-graphql@1.0.0] Only generate args for fields that represent elements with to-many relationships
- [cds-odata-v2-adapter-proxy@1.9.3] Fix batch handling of parameterized entities
- [cds-odata-v2-adapter-proxy@1.9.2] Check on `cds.mtx.eventEmitter` before access
- [cds-odata-v2-adapter-proxy@1.9.2] Restructure README
- [cds-odata-v2-adapter-proxy@1.9.1] Compile CSN for Node.js when loaded from CDS MTX services
- [cds-odata-v2-adapter-proxy@1.9.1] Check on `cds.requires.multitenancy` instead of deprecated `cds.requires.db.multiTenant` (compatible)
- [cds-odata-v2-adapter-proxy@1.9.1] Support `$count` with parameterized entities
- [cds-odata-v2-adapter-proxy@1.9.1] Make decoding of JWT token body more robust (error log in case of invalid JWT)
- [cds-odata-v2-adapter-proxy@1.9.1] Synchronize parallel loading of CSN and EDMX
- [cds-odata-v2-adapter-proxy@1.9.1] First (alpha) support for CDS Streamlined MTX (no extensibility support yet)
- [cds-odata-v2-adapter-proxy@1.9.1] Move `@types/express` to devDependencies
- [cds-odata-v2-adapter-proxy@1.9.0] CDS 6 compatible version
- [cds-odata-v2-adapter-proxy@1.9.0] Enhance proxy option `target` with mode `auto` to handle dynamic target/port assignment (for example, for unit-tests)
- [cds-odata-v2-adapter-proxy@1.9.0] Represent time component of `cds.Date/Edm.DateTime` with second precision (i.e. `00:00:00`)

### Removed ​

- [cds-graphql@1.0.0] Dependency on `@graphql-tools/schema` previously used to combine SDL string with resolvers

## June 2022 ​

### Added ​

- [eslint-plugin-cds@2.4.1] Authorization rules 'auth-*'.
- [cds-compiler@3.0.0] Instead of requiring all files on startup, they are required on an as-needed basis to reduce startup times.
- [cds-compiler@3.0.0] CDL parser: support SQL functions `locate_regexpr`, `occurrences_regexpr`, `replace_regexpr` and `substring_regexpr` with their special argument syntax.
- [cds-compiler@3.0.0] CDL parser: the names `trim` and `extract` are not reserved anymore.
- [cds.java@1.25.0] When setting the new property `cds.security.defaultRestrictionLevel = authenticated-user` the Spring security (auto-)configuration authenticates all CAP endpoints that are not explicitly annotated with `@restrict` or `@requires`. In that case `cds.security.openUnrestrictedEndpoints = true` will only open endpoints that are explicitly exposed to `any`. By default `cds.security.defaultRestrictionLevel` is set to `any`, making endpoints public by default.
- [cds.java@1.25.0] Annotation `@assert.target` can be used to ensure that target of managed to-one association is present. The target entity should be present prior to the creation of entity which require such assertion and cannot be created in same transaction. For compositions, to-many associations, unmanaged or managed to-one associations annotated with `@cascade` the `@assert.target` annotation will be ignored.
- [cds.java@1.25.0] Added a new `FeatureTogglesProvider` for mocked users, which reads array of enabled feature toggles from `cds.security.mock.tenants.features` or `cds.security.mock.users.features`.
- [cds.java@1.25.0] `cds-maven-plugin` is enhanced with new goal `auto-build` which eases use of Spring Developer Tools. Once started, it reacts to changes in the CDS model and starts CDS builds automatically. In contrast to the `watch` goal it does not start the Java application and hence is suitable to enable development with IDEs.
- [cds.java@1.25.0] The `cds-maven-plugin` provides the new goal `npx` which can be used to execute an `npx` command during the build.
- [cds.java@1.25.0] Improved debug logging of user information resolved by `UserInfoProvider` implementations.
- [cds4j@1.29.0] Reflection API: Support paths over associations and structured elements in `CdsStructuredType#getTargetOf`
- [cds4j@1.29.0] Support `@cds.java.name` on actions and functions
- [cds@6.0.0] Listeners for `commit` events on the request object are now awaited
- [cds@6.0.0] Experimental support for ECMAScript modules (ESM): You can now write your custom code, i.e., service implementations, `server.js`, `db/init.js` using ES6 `import` statements. Note though that this is experimental for now. Known limitation: jest doesn't support dynamic imports, which are required for that.
- [cds@6.0.0] Improved `cds.error` to allow these using variants:js

```
cds.error `Message with formatted: ${{foo:'bar'}}`
cds.error ({ message, code, ... })
cds.error (message, { code, ... })
let e = new cds.error(...) //> will not throw
```

Calling `cds.error()` with `new` returns the newly created Error, while calling it without `new` it throws immediately. The latter is useful for usages like that:
- [cds@6.0.0] Improved `req.error` to always turn each recorded error in to an instance of `Error` with own stack trace. Multiple errors are finally thrown as an array of these errors with `.message = 'MULTIPLE_ERRORS'` and `.details = this` (the latter is for compatibility to former releases).
- [cds@6.0.0] Public API for `cds.User.roles`: For example, this allows to construct new instances of `cds.User` like so:js

```
let user = new cds.User ({ id:'me', roles:['admin'] })
user.is('admin') //> true
```
- [cds@6.0.0] Public API for `cds.context.tx`: This provides access to the current global root `tx`, if any. (This replaces the former undocumented `req._tx`)
- [cds@6.0.0] Public API `cds.User.anonymous` and `cds.User.privileged`, which are sealed instances you can use directly instead of always passing `new cds.UserPrivileged`.
- [cds@6.0.0] Public API `cds.context.http` to reliably access inbound HTTP `req` and `res` objects.
- [cds@6.0.0] Persistent outbox now contains last error and timestamp of last attempt
- [cds@6.0.0] Enable PUT requests for UPDATE queries with CQN for remote services
- [cds@6.0.0] Support for new major version 2 of SAP Cloud SDK
- [cds@6.0.0] Support for the `@assert.target` annotation for managed-to-one associations
- [cds@6.0.0] Support for `FOR SHARE LOCK` on SAP HANA to acquire shared locks on the queried records so that the locked records stay intact until the transaction is committed or rolled back.
- [cds@6.0.0] Consistent error information for remote batch requests
- [cds@6.0.0] `cds.env` now supports expanding scalar `cds.requires` entries from `cds.requires.kinds` as follows:jsonc

```
{ "cds": {
  "requires": {
    "mtx-sidecar": true,
    "db": "sql",
    "kinds": {
      "sql": {/* detailed config for sql */},
      "mtx-sidecar": {/* detailed config */},
    }
  }
}}
```
- [cds@6.0.0] Support for mTLS in `enterprise-messaging-shared` and `message-queuing`
- [cds@6.0.0] Allow empty publish and subscribe prefixes for SAP Event Mesh when using the format `cloudevents`
- [cds@6.0.0] Custom type `sap.common.Locale` in common.cds
- [cds@6.0.0] Ordering by aggregated value for draft-enabled active entity
- [cds@6.0.0] `cds build` support for model provider service-based resource deployment.
- [cds@6.0.0] Remote service:Conversion of OData V2 (`"kind": "odata-v2"`) function and action results to OData V4 format
- Conversion of binary data in CQN queries to `base64url` in URL and payload
- Key predicate is omitted for single-key entities in resulting URL, for example, `GET /Foo(1)` instead of `GET /Foo(ID=1)`)
- Support of views with parameters

- [cds@6.0.0] Add `@odata.mediaContentType` if selecting stream property
- [cds@6.0.0] Kubernetes service bindings: Support for `servicebinding.io` and SAP BTP Service Operator based bindings
- [cds@6.0.0] `cds build` copies an existing `.npmrc` file located in the root or srv folder of your project into the deployment folder (usually `gen/srv`). This allows for dedicated npm configuration in cloud environments. Can be switched off by cds build option `contentNpmrc`.
- [cds@6.0.0] `cds build` copies an existing `.cdsrc.json` file located in the root or srv folder of your project into the deployment folder (usually `gen/srv`). The effective CDS configuration is created from the `.cdsrc.json` and CDS configuration defined in the `package.json` file. Can be switched off by cds build option `contentCdsrcJson`.
- [cds@6.0.0] Beta OData URL to CQN parser (`cds.env.features.odata_new_parser = true`):`@odata.context` is derived without using okra, not yet supported: `$expand=*` query option

- Support for actions and functions
- Further `$apply` transformations supported (nested) `concat` transformations
- `orderBy` transformation
- `top` & `skip` transformation
- `identity` transformation

- [cds@6.0.0] Log `BEGIN`/`COMMIT`/`ROLLBACK` commands when using SAP HANA as the underlying database
- [cds@6.0.0] Binary data in payload is validated to be RFC-4648 and OData ABNF conformed
- [cds@6.0.0] Support multiple media (streaming) properties in one entity
- [cds@6.0.0] Support for annotation `@protocol:'none'` to mark services as internal
- [cds@6.0.0] New build task aliases `java` and `nodejs` deprecating `java-cf`and `node-cf`, which are still supported for compatibility reasons.
- [cds@6.0.0] New shutdown event sent by `cds serve` Beta
- [cds@6.0.0] `$filter` in `$expand` for remote services
- [cds@6.0.0] Mapping of aliases in $expand for remote services

### Changed ​

- [cds-dk@4.9.7] Update `@sap/xsenv` to 3.3.1
- [cds-dk@4.9.6] Include `@sap/cds` 5.9.6
- [eslint-plugin-cds@2.4.1] Node.js 14 is now the minimum required Node.js version. Version 12 is no longer supported.
- [eslint-plugin-cds@2.4.1] Default CSN flavor in rules is `parsed`.
- [cds-compiler@3.0.0] cds-compiler now requires Node 14.
- [cds-compiler@3.0.0] `compile()` and its derivates now use `fs.realpath.native()` instead of `fs.realpath()`.
- [cds-compiler@3.0.0] CDL parser:Multi-line doc comments without leading `*` were inconsistently trimmed.
- As before, a structure value for an annotation assignment in a CDL source is flattened, i.e. `@Anno: { foo: 1, @bar: 2 }` becomes `@Anno.foo: 1 @Anno.@bar: 2`. Now, the structure property name `$value` is basically ignored: `@Anno: { $value: 1, @bar: 2 }` becomes `@Anno: 1 @Anno.@bar: 2`. The advantage is that overwriting or appending the annotation value works as expected.
- Keywords `not null` is only valid after `many String enum {...}` and no longer after `String`.

- [cds-compiler@3.0.0] `@cds.persistence.skip` and `@cds.persistence.exists` are both copied to generated child artifacts such as localized convenience views, texts entities and managed compositions.
- [cds-compiler@3.0.0] Update OData vocabularies 'Common', 'UI'.
- [cds-compiler@3.0.0] (Sub-)Elements of localized convenience views can now be annotated,for example,`annotate localized.E:elem`.
- [cds-compiler@3.0.0] `getArtifactCdsPersistenceName` now enforces the `csn` argument and can optionally have the `sqlDialect` passed in.
- [cds-compiler@3.0.0] `getElementCdsPersistenceName` can optionally have the `sqlDialect` passed in.
- [cds.java@1.25.0] By default, CDS Maven archetype now generates a CAP Java project for local development. To add dependencies required for production on CF, you can set the property `-DtargetPlatform=cloudfoundry`. Alternatively, you can enhance the project at any time with CDS Maven plugin goal `addTargetPlatform`.
- [cds.java@1.25.0] The parameter `cds.watch.noStart` is removed from the goal `watch` of the `cds-maven-plugin` and replaced with the new goal `auto-build`.
- [cds@6.0.0] `@sap/cds` can now be loaded from different install locations like any other module, i.e. `@require('@sap/cds')` will no longer return the same singleton instance.
- [cds@6.0.0] SAP Cloud SDK is now only an optional dependency and must be installed manually
- [cds@6.0.0] Improved `cds.context` implementation to use `AsyncLocalStorage` instead of plain `async_hooks` (-> see Node.js docs); APIs stay the same.
- [cds@6.0.0] Improved `cds.tx(tx=>{ ... })`: The new `tx` will be set as `cds.context.tx` for the function body's continuation, so all nested service or database operations will be executed within this transaction automatically.
- [cds@6.0.0] Node.js 14.15 is now the minimum required Node.js version. Version 12 is no longer supported.
- [cds@6.0.0] Node.js 14.15 is now enforced on loading of `@sap/cds`, for example, on server startup.
- [cds@6.0.0] Improve error messages in messaging management
- [cds@6.0.0] `cds.env.requires` formerly inherited from `cds.env.requires.kinds`. This is not the case anymore; hence things like this worked before but don't anymore:js

```
let sql = cds.requires.sql       //> is undefined now
let sql = cds.requires.kinds.sql //> use this instead
```

Alternatively you can add this to your cds config:json

```
{ "cds": { "requires": { "sql": true } }}
```
- [cds@6.0.0] Details of errors from remote services are now in property `reason` (before it was `innererror`)
- [cds@6.0.0] `innererror` is not removed from OData error response
- [cds@6.0.0] The `file` option of file-based messaging is now on top level (before it was in `credentials`)
- [cds@6.0.0] Optimized Search: `cds.env.features.optimized_search=true` is now the default behavior.
- [cds@6.0.0] `cds build` no longer generates CF manifest files for Nodejs and HANA db deployer modules.
- [cds@6.0.0] `cds build` no longer supports WebIDE Fullstack compatibility mode. Consequently HANA artifacts and service EDMX files for Fiori modules might no longer be correctly generated.
- [cds@6.0.0] Remote services: Batched `GET` requests will not fetch CSRF tokens
- [cds@6.0.0] CQN now uses `xpr` correctly instead of brackets in `where`
- [cds@6.0.0] `process.exit` is called again by `cds run/serve` and `watch`, to gain a reliable `exit` event for cleanup tasks. Before, this would be spoiled by apps that do not shut down the event loop properly.
- [cds@6.0.0] `cds build` no longer filters `./` file dependencies from package.json in the build output.
- [cds@6.0.0] Fiori preview no longer supports URL pattern with `service` and `entity` query parameters, for example, `$fiori-preview?service=...&entity=...`. These URLs were created back in `@sap/cds` 3.x.
- [cds@6.0.0] `cds build` no longer copies the `node_modules` folder into the deployment folder (usually `gen/db/**` and `gen/srv/**`).
- [cds@6.0.0] Set default tenant to `undefined` in single-tenant mode
- [cds@6.0.0] Handle foreign keys of to-one associations which should be set to `null` on db layer
- [cds@6.0.0] `cds build` uses the native `fs` functions instead of `fs-extra`.
- [cds@6.0.0] `cds build` supports initial data in CSV files that are located in any 'csv' or 'data' subfolder of some CDS model file. This also implies CSV files stored in reuse modules. Now, this behaviour is consistent with SQLite deployment. If the location of some CSV file has changed, a deployment error might be returned. In that case previously deployed `hdbtabledata` files have to be undeployed.
- [cds@6.0.0] `cds deploy` reads Cloud Foundry file `config.json` to get org and space information.
- [cds@6.0.0] New REST adapter replaced old (limited) implementation
- [cds@6.0.0] Default behaviour for runtime integrity checks. From now on no integrity checks will be done by default. Note that this is a breaking change for applications that rely on automatic integrity checks by runtime. We recommend to use `cds.env.features.assert_integrity`: `db` to switch on database integrity constraints. The value `app` can be used as fallback to previous behaviour.
- [cds@6.0.0] `cds build` no longer copies `.env` or `default-env.json` files into the deployment folder.
- [cds@6.0.0] OData `POST`, `PATCH` and `PUT` requests as well as draft-related `draftEdit` and `draftActivate` actions are now followed by an additional `READ` request to the application service. Consequently affected functionality:It is now sufficient to have a custom `READ` handler in order to adjust the response (for example, to handle virtual properties) of the modification request.
- A user is now required to be authorized to read updated data for example, a user having a role restricted with "INSERT-only" annotation pattern will get empty results in response to `POST` request.
- For compatibility reasons, `req._` of the modification request is uplinked to `req._` of the follow-up `READ` request so that one still can access original `req._.req/res` request objects of the modification request within the corresponding `READ` handlers.
- Modification logs are now followed by corresponding access logs.
- More details can be found in cds v6.0.0 release notes.

- [cds@6.0.0] Message for PreconditionFailedError is now configurable in messages.properties
- [cds@6.0.0] Remove circular references in Kibana logging
- [cds@6.0.0] Error sanitization in production is skipped for custom errors with HTTP code `5xx`. From now on, it's possible for an app developer to return any error message to the client. Note that this is a breaking change for applications that rely on error sanitization for custom errors in production. The behaviour of errors thrown by CAP framework is unchanged.

### Fixed ​

- [cds-dk@4.9.6] `cds login` (and `cds extend`, `cds activate` if previously logged in) now properly renew token URL
- [cds-dk@4.9.6] Improved logging during those commands
- [cds-compiler@2.15.4] for.odata: Fix derived type to scalar type resolution with intermediate `many`.

- [cds-compiler@2.15.4] to.edm(x): (V4 structured) Fix key paths in combination with `--odata-foreign-keys`.
- Add `Edm.PrimitiveType` to `@odata.Type`.
- (V4 JSON) Render constant expressions for `Edm.Stream` and `Edm.Untyped`.
- Fix a bug in target path calculation for `NavigationPropertyBinding`s to external references.
- Render inner annotations even if `$value` is missing.

- [cds-compiler@2.15.4] Update OData vocabularies 'Common', 'UI'.
- [cds-compiler@2.15.4] to.sql/to.hdbcds/to.hdi: "type of"s in `cast()`s could lead to type properties being lost.
- [cds.java@1.25.0] Fixed a bug, causing values imported from CSV files for fields having type `UUID` and annotated with `@odata.Type: 'Edm.String'` being normalized.
- [cds.java@1.25.0] Fixed a bug, causing issues when searching for strings containing backslashes in OData V2.
- [cds.java@1.25.0] Fixed a bug, causing the enterprise messaging tenants update failed when any broken tenant are in the tenant list.
- [cds4j@1.29.0] Fix generation of values for managed elements, when updating a projection without having the managed elements projected
- [cds4j@1.29.0] Code generator: Ensure static field names reflect @cds.java.name annotation
- [cds4j@1.29.0] Fix truncation of timestamps before epoch on Java 8 (JDK-8134928)
- [cds@6.0.0] We don't rely on `global.cds` anymore -> allows to load and correctly work with multiple versions of `cds`
- [cds@6.0.0] Improved shutdown for AMQP connections and file listeners
- [cds@6.0.0] Using `CQL` with a tagged template string `SELECT from Foo { null as boo }` threw an exception.
- [cds@6.0.0] In case of `MULTIPLE_ERRORS` throw an `Error` instead of an object
- [cds@6.0.0] `cds build` ensures correct precedence of feature annotations. Fixes `Duplicate assignment` compilation errors.
- [cds@6.0.0] Compatibility with former support to find service `@impl: 'relative/to/cdw'`.
- [cds@6.0.0] Views on views with parameters where erroneously inherited params through `cds.linked()`.
- [cds@6.0.0] Authentication: Return HTTP `404 Not Found` rather than `204 No Content` status code for invalid requests. For example, given the following request `/ReqAdmin(1)/toIntermediate/toa` and assuming that the `toIntermediate` instance does not exist, the runtime returned an HTTP `204 No Content` success status response code indicating that the request has succeeded. In such scenarios, now the HTTP `404 Not Found` status code is returned rather than `204 No Content`.
- [cds@6.0.0] Errors from HTTP requests sent via `cds.test.axios` now are the original Axios errors, i.e. including properties like `request` and `response`, with stack traces from caller.
- [cds@6.0.0] Errors constructed and thrown by `req.reject()` now have a stack starting at the code calling `req.reject()`.
- [cds@6.0.0] Auth annotations `@restrict` and `@requires` with empty array do not allow access anymore
- [cds@6.0.0] Delete on restricted singleton caused request to fail
- [cds@6.0.0] Add workaround of typescript not complete literal unions, specially when union strings.
- [cds@6.0.0] Accidental handling of non-proxy entities as they would have been proxies (`cds.env.odata.proxies`) in expands
- [cds@6.0.0] Boolean keys are properly parsed into JS boolean values
- [cds@6.0.0] Navigation path segments with aliased keys in structured mode (OData flavors `w4` and `x4`) when using beta OData URL to CQN parser (`cds.env.features.odata_new_parser`)
- [cds@6.0.0] All entities in `@sap/cds/common` have now proper CDS doc comments
- [cds@6.0.0] `cds build` uses `package.json` and `package-lock.json` files located in `srv` folder for deployment if existing. Before, `package.json` and `package-lock.json` files of the project root folder have always been taken.
- [cds@6.0.0] Pass options from `cds.parse.expr` to `cdsc.parse.expr`.
- [cds@6.0.0] Avoid error that is caused for example, in a streaming scenario when there is an issue while processing the stream. Trying to change/send the response object could cause a crash because the response was sent already.
- [cds@6.0.0] Correct URL generation for `Integer64` and `Decimal` for remote services
- [cds@6.0.0] Operation parameters from structured type and annotated with @open are not filtered from the input query
- [cds@6.0.0] Services are secured by default in production. Can be disabled via feature flag `cds.env.auth.restrict_all_services: false` or by using `mocked-auth`.
- [cds@6.0.0] Optimized Search: Exception when searching on views using built-in SQL SAP HANA functions
- [cds@6.0.0] In some cases, custom error handlers were not called for rest
- [cds@6.0.0] `cds build` adds newline at EOF for `hdbmigrationtable` files
- [cds@6.0.0] Static values in on condition were ignored when inserting on navigation
- [cds@6.0.0] Removed entity key validation by POST request in rest
- [cds@6.0.0] `$count=false` returned count
- [cds@6.0.0] `odata_new_parser`: `format=json` allowed as query parameter, other formats not supported and returning 501, trailing `?` allowed e.g. `/Employees?`
- [cds@6.0.0] `odata_new_parser`: Piped use of same transformations is now supported, like `/Students?$apply=filter(BIRTHYEAR ge 2000)/groupby((UNIVERSITY),aggregate(SUBJECT with countdistinct as distinctSubjects))/filter(UNIVERSITY eq 'Hamburg')`
- [cds@6.0.0] `odata_new_parser`: Behavior of piped transformations while using `topcount` or `bottomcount` is now correct
- [cds@6.0.0] Better error message for missing `exists` predicate in `@restrict.where`
- [cds@6.0.0] Reading raw Binary data provided as a `base64` (standard or url-safe) string by means of a `$value` query option
- [cds@6.0.0] Selecting a navigation with `$select` ended up in database error
- [cds@6.0.0] `cds.compile` no longer fails for cds sources that contain the `file:` pattern
- [cds@6.0.0] `$select=IsActiveEntity` did not work on draft enabled entity, when requesting active data via navigation
- [cds@6.0.0] not equal operator `<>` treated the same way as `!=`
- [cds@6.0.0] `cds.localize` now respects custom i18n file names (which is not recommended though)
- [cds@6.0.0] `cds version` now handles array-valued entries for `folders.db`and `folders.srv` gracefully when looking for MTX sidecar
- [cds@6.0.0] OData access of entities named `get` and `set`
- [cds@6.0.0] missing brackets for OR condition in `.where()` when requesting by navigation
- [cds@6.0.0] `cds build` now correctly supports nodejs apps that do not have a service module defined. In these cases the build task's src folder has to be configured as "."
- [cds@6.0.0] `cds build ` is now correctly executed if called by npm script or mta build.
- [cds@6.0.0] `cds deploy` now shows a better error message on INSERT errors (on SQLite).
- [cds@5.9.8] Application model is now again properly updated after extension activation
- [cds@5.9.8] Avoid crashes during `cds version` when `folders.db` or `folders.srv` are array-valued instead of strings
- [cds@5.9.8] `cds build` correctly validates MTX extension allow lists and doesn't log false positive warning messages
- [cds@5.9.7] Deleting a parent will delete all compositions, also texts
- [cds@5.9.7] Views with aliased elements in `orderBy`
- [cds-odata-v2-adapter-proxy@1.8.21] Add `Type` suffix to fix `__metadata.type` for parameterized entities (datajs did skip date type conversion)
- [cds-odata-v2-adapter-proxy@1.8.21] Fix parameterized entities navigation links
- [cds-odata-v2-adapter-proxy@1.8.21] Enhance Fiori Elements example apps
- [cds-odata-v2-adapter-proxy@1.8.20] Change README on App Router compression flag `compressResponseMixedTypeContent`
- [cds-odata-v2-adapter-proxy@1.8.20] Fill and process surrogate key `ID__` correctly in case of analytical queries
- [cds-odata-v2-adapter-proxy@1.8.20] Add an example Fiori Elements applications showcasing hierarchical `TreeTable` usage
- [cds-odata-v2-adapter-proxy@1.8.20] Rework UI application examples (basic, draft and hierarchy apps)

### Removed ​

- [cds-compiler@3.0.0] All v2 deprecated flags.
- [cds-compiler@3.0.0] Keyword `masked`.
- [cds-compiler@3.0.0] CDL parser: `*` is not parsed anymore as argument to all SQL functions; it is now only allowed for `count`, `min`, `max`, `sum`, `avg`, `stddev`, `var`.
- [cds-compiler@3.0.0] All non-SNAPI options.
- [cds@6.0.0] Deprecated option to send synchronous requests via `srv.emit()` -> use `srv.send()` for that
- [cds@6.0.0] Deprecated feature flag `cds.env.features.implicit_sorting`
- [cds@6.0.0] Deprecated feature flag `cds.env.features.update_managed_properties`
- [cds@6.0.0] Deprecated feature flag `cds.env.features.resolve_views`
- [cds@6.0.0] Deprecated feature flag `cds.env.features.spaced_columns`
- [cds@6.0.0] Deprecated feature flag `cds.env.features.throw_diff_error`
- [cds@6.0.0] Deprecated feature flag `cds.env.features.delay_assert_deep_assoc`
- [cds@6.0.0] Deprecated feature flag `cds.env.features.auto_fetch_expand_keys`
- [cds@6.0.0] Deprecation warning for query parameters `sap-valid-from` and `sap-valid-to`
- [cds@6.0.0] Built-in graphql support → moved to new `@sap/cds-graphql`
- [cds@6.0.0] Deprecated feature flag `cds.env.features.extract_vals`
- [cds@6.0.0] Support for CQN `where in` syntax `{ val: [1, 2, 3] }` without `list`. Use `{ list: [{ val: 1 }, { val: 2 }, { val: 3 }] }` instead.
- [cds@6.0.0] Support for selects in restrict entries, for example, `where : 'exists (select 1 from MyTable where a = b)'` is not allowed anymore
- [cds@6.0.0] Input validation for deep `INSERT`/`UPDATE` for associations in the service layer
- [cds@6.0.0] Support for `@odata.contained` annotation. Use Compositions instead.
- [cds@6.0.0] Support for `@odata.on.insert/update` annotation. Use `cds.on.insert/update` instead.
- [cds@6.0.0] Support for expressions in references, for example: `ref: ['foo as bar']`).
- [cds@6.0.0] Generic support of `$expand` and `$select` OData query options for custom actions and functions

## May 2022 ​

### Added ​

- [vscode-cds@4.5.6] file icon for CDS files
- [vscode-cds@4.5.5] support syntax highlighting for escape sequences in template strings
- [cds-compiler@2.15.0] A new warning is emitted if `excluding` is used without a wildcard, since this does not have any effect.
- [cds-compiler@2.15.0] All scalar types can now take named arguments, for example, `MyString(length: 10)`. For custom scalar types, one unnamed arguments is interpreted as length, two arguments are interpreted as precision and scale, for example, `MyDecimal(3,3)`.
- [cds-compiler@2.15.0] If the type `sap.common.Locale` exists, it will be used as type for the `locale` element of generated texts entities. The type must be a `cds.String`.
- [cds-compiler@2.15.0] to.cdl: Extend statements (from `extensions`) can now be rendered.
- [cds-compiler@2.15.0] Add OData vocabulary 'Hierarchy'.
- [cds-compiler@2.15.0] CDL: New associations can be published in queries, e.g. `assoc : Association to Target on assoc.id = id`
- [cds.java@1.24.0] Full support for the Spring Boot Developer Tools allowing much easier and faster development. This includes instant code replacement in test applications deployed to the cloud.
- [cds.java@1.24.0] The goal `watch` of the `cds-maven-plugin` supports the Spring-Boot Developer Tools for a quicker application restart after changes in the CDS model.
- [cds.java@1.24.0] The `$metadata` endpoints now stream the original EDMX directly, without serializing the internal Olingo EDMX representation. Beside much better performance this allows to make use of OData dynamic expressions now.
- [cds.java@1.24.0] Added a new event `ApplicationStopped` to the `ApplicationLifecycleService`, which can be used to stop background tasks. Note that this event is not guaranteed to be emitted, when the application terminates. It is first and foremost intended to stop background tasks when Spring closes its ApplicationContext.
- [cds.java@1.24.0] `UserInfo.getAdditionalAttributes()` now contains all token claims such as `email` or `aud` in case of IAS authentication.
- [cds.java@1.24.0] Spring's `@Order` annotation on event handler classes is now respected and event handlers are registered in that order.
- [cds.java@1.24.0] Enhanced annotations `@cds.on.insert` and `@cds.on.update` with following features: Static values can be assigned
- Arbitrary user context variables can be assigned, for example, `@cds.on.insert: $user.given_name`. The context variables must be mapped from the exposed SAML assertion attributes.

- [cds.java@1.24.0] Key elements of type `String` that are annotated with `@cds.on.insert: $uuid` now get a string representation of a UUID assigned.
- [cds.java@1.24.0] Full support for the Spring Boot Developer Tools allowing much easier and faster development. This includes instant code replacement in test applications deployed to the cloud.
- [cds.java@1.24.0] The goal `watch` of the `cds-maven-plugin` supports the Spring-Boot Developer Tools for a quicker application restart after changes in the CDS model.
- [cds.java@1.24.0] Added a new event `ApplicationStopped` to the `ApplicationLifecycleService`, which can be used to stop background tasks. Note that this event is not guaranteed to be emitted, when the application terminates. It is first and foremost intended to stop background tasks when Spring closes its ApplicationContext.
- [cds.java@1.24.0] `UserInfo.getAdditionalAttributes()` now contains all token claims such as `email` or `aud` in case of IAS authentication.
- [cds.java@1.24.0] Spring's `@Order` annotation on event handler classes is now respected and event handlers are registered in that order.
- [cds.java@1.24.0] Enhanced annotations `@cds.on.insert` and `@cds.on.update` with following features: Static values can be assigned
- Arbitrary user context variables can be assigned, e.g. `@cds.on.insert: $user.given_name`. The context variables must be mapped from the exposed SAML assertion attributes.

- [cds4j@1.28.0] Support key paths and auto cast in `CdsData`: `getPath`, `putPath`, `containsPath`, `removePath`
- [cds4j@1.28.0] PostgreSQL - support `Select` with `lock(0)` (`SELECT FOR UPDATE ... NOWAIT`)
- [cds4j@1.28.0] Support changing targets of to-one associations/compositions
- [cds4j@1.28.0] Draft: support draft associations to entities with compound keys
- [cds-mtx@2.5.6] Tenant upgrades can now scale beyond a single database.
- [cds-mtx@2.5.6] The tenant IDs are now exposed in the provisioning service (`/mtx/v1/provisioning/tenantIds`).
- [cds-mtx@2.5.6] The SaaS Provisioning Service `UPDATE` event type is now also supported.
- [cds-mtx@2.5.6] By setting cds environment `mtx.provisioning.lazymetadatacontainercreation: true`, the creation of the `__META__` container can be postponed to the first onboarding again. In case the onboarding request contains additional parameters for the container creation, these parameters will also be used for the creation of the `__META__` tenant, except if the parameters are also set via cds environment `mtx.provisioning.metadatacontainer`.

### Changed ​

- [cds-dk@4.9.5] Include `@sap/cds` 5.9.5
- [cds-dk@4.9.5] Include `@sap/cds-compiler` 2.15.2
- [cds-dk@4.9.4] Include `@sap/cds` 5.9.4
- [cds-dk@4.9.4] Bump `axios` to latest (CVE-2022-1214)
- [vscode-cds@4.5.6] updated included capire docs
- [cds-compiler@2.15.0] to.edm(x): perform inbound qualification and spec violation checks as well as most/feasible EDM preprocessing steps on requested services only.
- Open up `@odata { Type, MaxLength, Precision, Scale, SRID }` annotation. The annotations behavior is defined as follows: The element/parameter must have a scalar CDS type. The annotation is not applied on named types (With the V2 exception where derived type chains terminating in a scalar type are resolved).
- The value of `@odata.Type` must be a valid `EDM` type for the rendered protocol version.
- If `@odata.Type` can be applied, all canonic type facets (`MaxLength`, `Precision`, `Scale`, `SRID`) are removed from the Edm Node and the new facets `@odata { MaxLength, Precision, Scale, SRID }` are applied. Non Edm type conformant facets are ignored (eg. `@odata { Type: 'Edm.Decimal', MaxLength: 10, SRID: 0 }`).
- Type facet values are not evaluated.

- V2: Propagate `@Core.MediaType` annotation from stream element to entity type if not set.

- [cds-compiler@2.15.0] to.edm: Render constant expressions in short notation.
- [cds-compiler@2.15.0] Update OData Vocabularies: 'Common', 'Graph', 'Validation'.
- [cds.java@1.24.0] The CDS model is no longer reloaded every time when opening a new Request Context. Only the outmost Request Context initially loads the CDS model and propagates it to all inner Request Contexts. The only scenario where the model is still reloaded is when the new Request Context uses a different tenant. This scenario also requires a new ChangeSet Context to be opened in addition.
- [cds.java@1.24.0] If a ChangeSet Context is opened without an existing Request Context the latter is opened implicitly as well.
- [cds.java@1.24.0] HTTP Headers from the `$batch` request are now propagated to the inner requests, if they do not yet exist there. This means those headers are now available through the `context.getParameterInfo().getHeaders()` method, when processing a request defined in a `$batch` request.
- [cds.java@1.24.0] `UserInfo.getName()` now returns the subject of the token (property `sub`) in case of IAS authentication.
- [cds.java@1.24.0] When a new request context is opened with a modified `ParameterInfo`, null values and empty strings as correlation id in the `ParameterInfo` object are not interpreted as an intention to overwrite an existing correlation id in the MDC, anymore, and therefore are silently ignored
- [cds.java@1.24.0] The CDS model is no longer reloaded every time when opening a new Request Context. Only the outmost Request Context initially loads the CDS model and propagates it to all inner Request Contexts. The only scenario where the model is still reloaded is when the new Request Context uses a different tenant. This scenario also requires a new ChangeSet Context to be opened in addition.
- [cds.java@1.24.0] If a ChangeSet Context is opened without an existing Request Context the latter is opened implicitly as well.
- [cds.java@1.24.0] The `$metadata` endpoints now stream the original EDMX directly, without serializing the internal Olingo EDMX representation. Beside much better performance this allows to make use of OData dynamic expressions now.
- [cds.java@1.24.0] HTTP Headers from the `$batch` request are now propagated to the inner requests, if they do not yet exist there. This means those headers are now available through the `context.getParameterInfo().getHeaders()` method, when processing a request defined in a `$batch` request.
- [cds.java@1.24.0] `UserInfo.getName()` now returns the subject of the token (property `sub`) in case of IAS authentication.
- [cds.java@1.24.0] When a new request context is opened with a modified `ParameterInfo`, null values and empty strings as correlation id in the `ParameterInfo` object are not interpreted as an intention to overwrite an existing correlation id in the MDC, anymore, and therefore are silently ignored
- [cds4j@1.28.0] Deprecate path access via `CdsData:get`, instead use `getPath`
- [cds4j@1.28.0] Override flat FK values with structured ones, if both are present in payload of Insert statements
- [cds4j@1.28.0] Deep Update: Don't allow to set composition to existing target entity
- Ignore update data for non-cascading associations

### Fixed ​

- [cds-dk@4.9.5] `cds init` uses latest Maven Java archetype version 1.24.0 for creating Java projects.
- [vscode-cds@4.5.5] find references could have shown wrong entries from localized context
- [cds-compiler@2.15.2] Option `cdsHome` can be used instead of `global.cds.home` to specify the path to `@sap/cds/`.
- [cds-compiler@2.15.2] to.edm(x):Set anonymous nested proxy key elements to `Nullable:false` until first named type is reached.
- Enforce `odata-spec-violation-key-null` on explicit foreign keys of managed primary key associations.
- Proxies/service cross references are no longer created for associations with arbitrary ON conditions. Only managed or `$self` backlink association targets are proxy/service cross reference candidates.
- Explicit foreign keys of a managed association that are not a primary key in the target are exposed in the the proxy.
- If an association is primary key, the resulting navigation property is set to `Nullable:false` in structured mode.

- [cds-compiler@2.15.0] to.cdl:Annotations of elements of action `returns` are now rendered as `annotate` statements.
- Annotations on columns (query sub-elements) were not always rendered.
- Doc comments on bound actions were rendered twice.
- Unapplied annotations for action parameters were not rendered.
- Unions and joins are correctly put into parentheses.
- Add parentheses around certain expressions in function bodies that require it, such as `fct((1=1))`.

- [cds-compiler@2.15.0] to.edm(x):Fix a bug in top level and derived type `items` exposure leading to undefined type rendering.
- Fix a naming bug in type exposure leading to false reuse types, disguising individual type modifications (such as annotations, (auto-)redirections, element extensions).
- Ignore `@Aggregation.default`.
- Consolidate message texts and formatting.
- Fix navigation property binding in cross service rendering mode.
- Remove partner attribute in proxy/cross service navigations.

- [cds-compiler@2.15.0] Core engine (function `compile`):Annotations for new columns inside `extend projection` blocks were not used.
- Extending an unknown select item resulted in a crash.
- Extending a context/service with columns now correctly emits an error.
- Unmanaged `redirected to` in queries did not check whether the source is an association.

- [cds-compiler@2.15.0] parseCdl: `extend  with enum {...}` incorrectly threw a compiler error.
- [cds-compiler@2.15.0] API: `compile()` used a synchronous call `fs.realpathSync()` on the input filename array. Now the asynchronous `fs.realpath()` is used.
- [cds-compiler@2.15.0] On-conditions in localized convenience views may be incorrectly rewritten if an element has the same as a localized entity.
- [cds-compiler@2.15.0] to.sql/hdi/hdbcds:No referential constraint is generated for an association if its parent or target entity are annotated with `@cds.persistence.exists: true`.
- Fix rendering of virtual elements in subqueries
- Correctly process subqueries in JOINs

- [cds-compiler@2.15.0] to.sql/hdi: Queries with `UNION`, `INTERSECT` and similar in expressions are now enclosed in parentheses.
- [cds.java@1.24.0] Fixed a bug, causing the audit log service to send a message without a tenant, instead of properly using the provider tenant.
- [cds.java@1.24.0] Fixed a bug, causing issues with OData V4 URLs, which contained the service path also in other parts of the URL (e.g. the domain).
- [cds.java@1.24.0] Fixed a bug, causing issues with OData V4 URLs, which contained filters on properties that have reserved identifiers as prefix such as `INF`.
- [cds.java@1.24.0] Fixed a bug introduced with version `1.23.0`, causing connection issues with MTX sidecar in context of DwC.
- [cds.java@1.24.0] Fixed a bug, causing the tenant provider service to deliver only subscribed tenants but the update failed tenants are also expected.
- [cds.java@1.24.0] Fixed a bug, causing issues when receiving extended declared events via the messaging service.
- [cds.java@1.24.0] Fixed a bug, causing the audit log service to send a message without a tenant, instead of properly using the provider tenant.
- [cds.java@1.24.0] Fixed a bug, causing issues with OData V4 URLs, which contained the service path also in other parts of the URL (for example, the domain).
- [cds.java@1.24.0] Fixed a bug, causing issues with OData V4 URLs, which contained filters on properties that have reserved identifiers as prefix such as `INF`.
- [cds.java@1.24.0] Fixed a bug introduced with version `1.23.0`, causing connection issues with MTX sidecar in context of DwC.
- [cds.java@1.24.0] Key elements of type `String` that are annotated with `@cds.on.insert: $uuid` now get a string representation of a UUID assigned.
- [cds4j@1.28.0] Fix data duplication issue when to-many expand is applied to many-to-many associations
- [cds4j@1.28.0] Fix exceptions while serializing streaming elements to JSON
- [cds4j@1.28.0] Code generator:Ensure technical entities are identified correctly
- Don't generate interfaces for technical entities

- [cds4j@1.28.0] Move element default values from `CdsSimpleType:defaultValue` to `CdsElement:defaultValue`
- [cds4j@1.28.0] Fix deep update with InputStreams in target data
- [cds4j@1.28.0] PostgreSQL - fix handling of elements with type `cds.Binary`
- [cds@5.9.6] Ignored requests in batch requests
- [cds@5.9.6] `pool` module for logger facade is separated from `hana` database logger. Timeout error by acquiring client from pool is now enhanced with `_poolState` providing current pool attributes.
- [cds@5.9.6] Multiple errors did not have correct HTTP response status code
- [cds@5.9.6] `POST|PUT|PATCH` requests with `charset` directive in `Content-Type` header (for example, `Content-Type: application/json; charset=utf-8`) no longer issues an error "Invalid content type" in REST adapters
- [cds@5.9.6] Call hana procedure:accepted are any symbols in a procedure name if it is delimited with a double quotation (`"`)
- fixed results for table output parameters when using `@sap/hana-client`; limitation: output parameters in a `CALL` statement must follow the same order used in a stored procedure definition

- [cds@5.9.6] `@odata.context` considers `cds.env.odata.contextAbsoluteUrl` when requesting an OData Service
- [cds@5.9.5] `HDB_TCP_KEEP_ALIVE_IDLE` config
- [cds@5.9.5] A combination of `!=` operator and `or` in `where` clauses of `@restrict` annotations or when adjusting `req.query` in custom handlers (OData services only)
- [cds@5.9.5] Programmatic calls to bound actions/functions do have keys in `req.data` again if compat flag `cds.env.features.keys_in_data_compat` is set
- [cds@5.9.4] Error messages are improved if no `passport` module was found or if no `xsuaa` service binding is available
- [cds@5.9.4] Issue fixed for `srv.get()`. It was returning `TypeError` in plain REST usage for external services, for example, `srv.get('/some/arbitrary/path/111')`
- [cds@5.9.4] Allow unrestricted services to run unauthenticated, removing the `Unable to require required package/file "passport"` error. Totally not recommended in production. Note that though this restores pre 5.9.0 behavior, this will come again starting in 6.0.
- [cds@5.9.4] Audit logging of sensitive data in a composition child if its parent is annotated with `@PersonalData.EntitySemantics: 'Other'` and has no data privacy annotations other than `@PersonalData.FieldSemantics: 'DataSubjectID'` annotating a corresponding composition, for example:js

```
  annotate Customers with @PersonalData : {
    DataSubjectRole : 'Address',
    EntitySemantics : 'Other'
  } {
    addresses @PersonalData.FieldSemantics: 'DataSubjectID';
  }
  annotate CustomerPostalAddress with @PersonalData : {
    DataSubjectRole : 'Address',
    EntitySemantics : 'DataSubject'
  } {
    ID @PersonalData.FieldSemantics : 'DataSubjectID';
    street @PersonalData.IsPotentiallyPersonal;
    town @PersonalData.IsPotentiallySensitive;
  }
```
- [cds-mtx@2.5.6] When using a custom folder setup for native artifacts for HDI, the `cfg` folder is now correctly included for the HDI deployment
- [cds-odata-v2-adapter-proxy@1.8.19] Don't propagate `host` header to forwarded calls.
- [cds-odata-v2-adapter-proxy@1.8.18] Propagate all headers to forwarded calls.
- [cds-odata-v2-adapter-proxy@1.8.17] Filter out annotation elements in response data starting with `odata.` or including `@odata.`.
- [cds-odata-v2-adapter-proxy@1.8.17] Elements starting with `@` are excluded as before.
- [cds-odata-v2-adapter-proxy@1.8.17] Propagate special headers to forwarded calls (i.e. starting with `dwc`).

## April 2022 ​

### Added ​

- [eslint-plugin-cds@2.4.0] Rule report recycling ensures that rules are created/run only once for the root model
- [cds-compiler@2.14.0] cdsc: `--quiet` can now be used to suppress compiler output, including messages.
- `--options ` can be used to load compiler options. A JSON file is expected. Is compatible to CDS `package.json` and `.cdsrc.json` by first looking for `cdsc` key in `cds`, then for a `cdsc` key and otherwise uses the full JSON file.
- `--[error|warn|info|debug] id1,id2` can be used to reclassify specific messages.

- [cds-compiler@2.14.0] Add OData Vocabularies: 'DataIntegration', 'JSON'.

### Changed ​

- [cds-dk@4.9.3] `cds init` uses latest Maven Java archetype version 1.23.1 for creating Java projects.
- [cds-dk@4.9.3] Include `@sap/cds` 5.9.3
- [cds-dk@4.9.2] Include `moment` 2.29.2, fixing CVE-2022-24785
- [cds-dk@4.9.2] Include `@sap/cds` 5.9.2
- [cds-dk@4.9.2] Include `@sap/eslint-plugin` 2.3.5
- [cds-dk@4.9.1] `cds init` uses latest Maven Java archetype version 1.23.0 for creating Java projects.
- [cds-dk@4.9.1] Include `@sap/cds` 5.9.1
- [cds-dk@4.9.1] Include `@sap/cds-compiler` 2.13.8
- [cds-dk@4.9.1] Include `@sap/eslint-plugin` 2.3.4
- [eslint-plugin-cds@2.4.0] Rule `no-dollar-prefixed-names` no longer acts on compiler warning messages
- [eslint-plugin-cds@2.3.5] Catch root model compilation errors and do not try again on every file (-> long lint times for broken models)
- [eslint-plugin-cds@2.3.5] Add to lint reports with rules marked with '!'
- [vscode-cds@4.5.4] `CAP Release Notes` page now persists its state
- [cds-compiler@2.14.0] Update OData Vocabularies: 'UI'.
- [cds-mtx@2.5.5] Improved logging in the context of requesting tokens.
- [cds-mtx@2.5.4] If enabled via `cds.env.mtx.security.metadata-scope-checks`, the v2 CSN and EDMX APIs, as well as all metadata APIs are now scope-checked for `mtdeployment`.
- [cds-mtx@2.5.4] Tokens sent to the command-line client are now reduced in scope for security reasons.

### Fixed ​

- [cds-dk@4.9.3] `cds add cf-manifest` now uses the correct `application` plan for the `xsuaa` service
- [cds-dk@4.9.3] `cds login`, `cds activate`: correctly include response in auth errors
- [cds-dk@4.9.3] The SAP HANA and MTA options in the project wizard in BAS now work again
- [vscode-cds@4.5.4] Syntax highlighting in Business Application Studio
- [cds-compiler@2.14.0] to.cdl: Delimited identifiers as the last elements of arrays in annotation values are now rendered with spaces in between, to avoid accidentally escaping `]`.
- Identifiers in includes and redirection targets were not quoted if they are reserved keywords.

- [cds-compiler@2.14.0] to.edm(x): Correctly rewrite `@Capabilities.ReadRestrictions.ReadByKeyRestrictions` into `@Capabilities.NavigationPropertyRestriction` in containment mode.
- [cds.java@1.23.1] The `cds-feature-auditlog-v2` now sends audit logs to the audit server in the context of the provider tenant if the tenant in `UserInfo` is `null`.
- [cds.java@1.23.1] The runtime now returns a server error with a meaningful error message when a transaction unexpectedly fails to open.
- [cds.java@1.23.1] The `cds-feature-auditlog-v2` now sends audit logs to the audit server in the context of the provider tenant if the tenant in `UserInfo` is `null`.
- [cds.java@1.23.1] The runtime now returns a server error with a meaningful error message when a transaction unexpectedly fails to open.
- [cds@5.9.3] Since 5.8.2 `req.target` for requests like `srv.put('/MyService.entity')` is defined, but `req.query` undefined (before `req.target` was also undefined). This was leading to accessing undefined, which has been fixed.
- [cds@5.9.3] Custom actions with names conflicting with methods from service base classes, for example, `run()`, could lead to hard-to-detect errors. This is now detected and avoided with a warning.
- [cds@5.9.3] Typed methods for custom actions were erroneously applied to `cds.db` service, which led to server crashes, for example, when the action was named `deploy()`.
- [cds@5.9.3] Invalid batch requests were further processed after error response was already sent to client, leading to an InternalServerError
- [cds@5.9.3] Full support of `SELECT` queries with operator expressions (`xpr`)
- [cds@5.9.2] i18n translation for errors did not work correctly in some cases
- [cds@5.9.2] Normalization in custom `getRestrictions`
- [cds@5.9.2] Throw exception by `INSERT` into HANA queries if number of provided rows deviates from number of affected rows returned by hdb to prevent data losses
- [cds@5.9.2] Handler detection for extended services
- [cds@5.9.2] Speed-up in localization handling
- [cds@5.9.2] Draft: navigation via an association to many from a non-draft enabled entity to a draft-enabled entity
- [cds@5.9.2] Limited support of `SELECT` queries with operator expressions (`xpr`)
- [cds-mtx@2.5.4] `MT_LIB_TENANT-`-prefixed tenants used by the Java runtime are now correctly ignored by the `cds-mtx` sidecar.
- [ux-cds-odata-language-server-extension@1.5.4] Unjustified error for `LocalDataProperty` in `Common.ValueList` when the property is defined in the service using a `many` clause.
- [ux-cds-odata-language-server-extension@1.5.4] Unjustified error for `Action` in `UI.DataFieldForAction` if it contains the signatures (i.e. the parts in () ) .
- [ux-cds-odata-language-server-extension@1.5.4] Unjustified warning for CAP CDS native annotation `@mandatory` when applied to a parameter.
- [cds-odata-v2-adapter-proxy@1.8.16] Fix if elements are annotated with `@cds.api.ignore`
- [cds-odata-v2-adapter-proxy@1.8.16] Abort file upload when limit is reached
- [cds-odata-v2-adapter-proxy@1.8.15] Remove internal repository reference
- [cds-odata-v2-adapter-proxy@1.8.15] Document that Singletons are not available in OData V2
- [cds-odata-v2-adapter-proxy@1.8.15] Ignore omitted elements annotated with `@cds.api.ignore`
- [cds-odata-v2-adapter-proxy@1.8.15] Support validated for absolute context urls via `cds.odata.contextAbsoluteUrl`.
- [cds-odata-v2-adapter-proxy@1.8.15] Skip aggregation for measures with aggregation `#NONE` and `#NOP`
- [cds-odata-v2-adapter-proxy@1.8.15] Support `$count` aggregations for measures with aggregation `#$COUNT`
- [cds-odata-v2-adapter-proxy@1.8.15] Changed OData type mapping for `Edm.Byte` to `cds.Integer`
- [cds-odata-v2-adapter-proxy@1.8.14] Upgrade `@sap/logging` to fix vulnerability
- [cds-odata-v2-adapter-proxy@1.8.13] Remove peer dependency to prevent workspace failures
- [cds-odata-v2-adapter-proxy@1.8.12] Refactorings to support universal CSN
- [cds-odata-v2-adapter-proxy@1.8.12] Refactorings to support metadata prototype layering
- [cds-odata-v2-adapter-proxy@1.8.12] Include `search` in `$apply` aggregations

## March 2022 ​

### Added ​

- [cds-dk@4.9.0] `cds parse` as convenient shortcut to `cds compile --flavor parsed`.
- [cds-dk@4.9.0] `cds compile --to openapi` uses value of annotation `@Common.Label` on entities, actions, and functions for operation tags, diagram includes non-primitive action and function import parameters.
- [cds-dk@4.9.0] `cds add` now accepts `--for ` argument to create Node,js project configuration for a given profile
- [cds-dk@4.9.0] `cds add approuter` allows for serving your application's UI using SAP App Router.
- [cds-dk@4.9.0] `cds add kibana-logging` adds Kibana-friendly logging in a more convenient way than having to manually alter the package.json.
- [eslint-plugin-cds@2.3.3] Added new rule `no-dollar-prefixed-names`
- [eslint-plugin-cds@2.3.3] Lint reports with rules marked with '!' notify of rule compile errors
- [eslint-plugin-cds@2.3.3] Lint reports of any thrown errors can be exposed by `--debug` (includes stack)
- [vscode-cds@4.5.2] New code-formatting options for `action`s and `function`s: `alignActionNames` (aligns names)
- `alignActionReturns` (aligns `returns` keywords)

- [cds-compiler@2.13.0] CDL syntax: Allow to `extend E:elem` and `annotate E:elem` instead of having to write deeply nested statements.
- Enable `default` values as part of scalar type definitions.
- The following `extend` syntax variants are now possible:cds

```
extend … with elements { … }
extend … with definitions { … }
extend … with columns { … }
extend … with enum { … }
extend … with actions { … }
```

This syntax expresses how an artifact is extended instead of what is extended.
- Using `ORDER BY` in generic functions such as SAP HANA's `first_value` is now possible.

- [cds-compiler@2.13.0] Make API function `compileSources` accept CSN objects as file content
- [cds-compiler@2.13.0] to.edm(x): Annotate view parameters with `@sap.parameter: mandatory` (V2) and `@Common.FieldControl: #Mandatory` (V4).
- [cds-compiler@2.13.0] to.sql/hdi/hdbcds: Introduce the annotations `@sql.prepend` and `@sql.append` that allow inserting user-written SQL snippets into the compiler generated content. Changes in annotations `@sql.prepend` and `@sql.append` are now reflected in the output of `to.hdi.migration`. This enables CDS Build to produce `.hdbmigrationtable` files translating such model changes into schema changes.
- [cds-compiler@2.13.0] API: Lists of keywords for various backends are available as `to.[.].keywords`, for example, `to.sql.sqlite.keywords`.
- [cds-compiler@2.13.0] for.odata/to.edm(x): The draft composition hull is now also taking into account compositions in subelements.
- [cds.java@1.23.0] `@Core.ContentID` is now present on OData V4 error responses, allowing to correspond OData ChangeSet error messages with the request causing the error.
- [cds.java@1.23.0] Improved the `AuthenticationInfo` API to grant easier access to raw authentication information such as JWT tokens.
- [cds.java@1.23.0] The `AuthenticationInfo` can now be accessed from the `RequestContext` and `EventContext` and is provided as a Spring bean. It is also propagated to child threads when propagating the `RequestContext`.
- [cds.java@1.23.0] Introduced new pseudo-role `internal-user` which allows authorization for clients that share the same authentication secret as the server (for example, same XSUAA instance).
- [cds.java@1.23.0] Added default set of mock users reflecting the pseudo roles. They are named `authenticated`, `system`, `internal` and `privileged` and can be used with an empty password.
- [cds.java@1.23.0] Added integration with Cloud SDK's `RequestHeaderFacade` ensuring HTTP headers are propagated to Cloud SDK.
- [cds.java@1.23.0] The goal `install-cdsdk` of the `cds-maven-plugin` provides the new parameter `arguments` to pass additional arguments to the command line.
- [cds.java@1.23.0] Added properties `cds.auditlog.outbox` and `cds.messaging..outbox` that control the usage of the (persistent) Outbox in Auditlog resp. Messaging services.
- [cds.java@1.23.0] Added mTLS (x509 certificates) authentication support for XSUAA-based platform services: Service Manager, Enterprise Messaging, SaaS Provisioning and Auditlog.
- [cds.java@1.23.0] When using SAP HANA Cloud you can now enable a shared connection pool using property `cds.multiTenancy.dataSource.combinePools.enabled` without having to specify all database instances using property `cds.multiTenancy.dataSource.hanaDatabaseIds`.
- [cds.java@1.23.0] `@Core.ContentID` is now present on OData V4 error responses, allowing to correspond OData ChangeSet error messages with the request causing the error.
- [cds.java@1.23.0] Improved the `AuthenticationInfo` API to grant easier access to raw authentication information such as JWT tokens.
- [cds.java@1.23.0] The `AuthenticationInfo` can now be accessed from the `RequestContext` and `EventContext` and is provided as a Spring bean. It is also propagated to child threads when propagating the `RequestContext`.
- [cds.java@1.23.0] Introduced new pseudo-role `internal-user` which allows authorization for clients that share the same authentication secret as the server (e.g. same XSUAA instance).
- [cds.java@1.23.0] Added default set of mock users reflecting the pseudo roles. They are named `authenticated`, `system`, `internal` and `privileged` and can be used with an empty password.
- [cds.java@1.23.0] Added integration with Cloud SDK's `RequestHeaderFacade` ensuring HTTP headers are propagated to Cloud SDK.
- [cds.java@1.23.0] The goal `install-cdsdk` of the `cds-maven-plugin` provides the new parameter `arguments` to pass additional arguments to the command line.
- [cds.java@1.23.0] Added properties `cds.auditlog.outbox` and `cds.messaging..outbox` that control the usage of the (persistent) Outbox in Auditlog resp. Messaging services.
- [cds.java@1.23.0] Added mTLS (x509 certificates) authentication support for XSUAA-based platform services: Service Manager, Enterprise Messaging, SaaS Provisioning and Auditlog.
- [cds.java@1.23.0] When using SAP HANA Cloud you can now enable a shared connection pool using property `cds.multiTenancy.dataSource.combinePools.enabled` without having to specify all database instances using property `cds.multiTenancy.dataSource.hanaDatabaseIds`.
- [cds4j@1.27.0] Allow to explicitly turn off draft-enabled associations
- [cds4j@1.27.0] Support on condition resolution with Effective CSN
- [cds4j@1.27.0] Collectors to connect a stream of predicates with AND or OR
- [cds4j@1.27.0] Support new values for managed data (`@cds.on.insert` and `@cds.on.update`) [cds4j@1.27.0] `$user.locale` and `$user.tenant` to set data from the user info
- [cds4j@1.27.0] `$uuid` to automatically generate UUID values

- [cds@5.9.0] Enable custom audit logging implementation by subclassing or prepending `cds.AuditLogService`
- [cds@5.9.0] Log authentication/authorization traces, for example, authentication strategy, and access control decisions to facilitate troubleshooting in debug mode.
- [cds@5.9.0] Bound functions and actions calls with odata-v2 from remote service
- [cds@5.9.0] Beta support for procedure calls with table output data (SAP HANA only) Both hdb and `@sap/hana-client` currently do not support parameter metadata for table output. To provide the functionality anyways, CAP must fetch the metadata itself. As this is not CAP's expertise, the feature is only beta.
- All parameters must be named or unnamed, that is `CALL EXAMPLE_PROC(PARAM_1 => ?,PARAM_2 => ?)` or `CALL EXAMPLE_PROC(?,?)`

- [cds@5.9.0] Alpha `cds.ApplicationService.getRestrictions(definition, event, user)`, which returns the applicable restrictions for the current request as follows: `null`: unrestricted access
- `[]`: no applicable restrictions -> no access
- `[{ grant: '...', to: ['...'], where: '...' }, ...]`: applicable restrictions with grant normalized to strings That is, `grant: ['CREATE', 'UPDATE']` in model becomes `[{ grant: 'CREATE' }, { grant: 'UPDATE' }]`

- Promise resolving to any of the above (needed for CAS override)

- [cds@5.9.0] Internal model provider service can be used for obtaining dynamic csn, including features and key user extensions
- [cds@5.9.0] Support insert of SQL snippets for HANA migration tables using @sql.append and @sql.prepend annotations.
- [cds@5.9.0] Support for the `@odata.draft.enclosed` annotation on associations targeted via navigation — previously only supported for `$expand`
- [cds@5.9.0] Pseudo role `internal-user` for technical user tokens acquired from own XSUAA instance
- [cds@5.9.0] Include globally-installed cds-dk version in output of `cds version`.
- [cds@5.9.0] Include version of cds-mtx in output of `cds version`, if available.
- [cds@5.9.0] Feature toggle support in `cds build` for cloud deployments. Create language bundles and parsed CSN for all features.
- [cds@5.9.0] Support for `@Aggregation.default` in new OData parser (`cds.env.features.odata_new_parser = true`)

### Changed ​

- [cds-dk@4.9.0] `cds init` does not create `VS Code` file exclusions anymore, so that `.vscode/` and `.gitignore` are visible by default, allowing easier editing of these files.
- [cds-dk@4.9.0] `cds init` reports Maven archetype version in console if called with `--add java`.
- [cds-dk@4.9.0] `cds init` uses latest Maven Java archetype version 1.22.2 for creating Java projects.
- [cds-dk@4.9.0] `cds import` modified documentation for namespace option.
- [cds-dk@4.9.0] `cds import` does not create bound function imports key parameters in CSN for OData V2.
- [cds-dk@4.9.0] `cds import` now when `--keep-namespace` option is not given validates the file name and then converts it to complier supported format as service name .
- [cds-dk@4.9.0] add new methods from `FsUtil` to typescript interface.
- [cds-dk@4.8.2] `cds init` uses latest Maven Java archetype version 1.22.1 for creating Java projects.
- [eslint-plugin-cds@2.3.4] Only deduplicate model error messages when working within VS Code Editor
- [eslint-plugin-cds@2.3.4] Hide `no-dollar-prefixed-names` compiler warning message in VS Code Editor (already passed by lsp)
- [vscode-cds@4.5.3] Consume `package.json` and `.cdsrc.json` schemas from `@sap/cds-lsp`
- [vscode-cds@4.5.3] Better error message in case `cds preview` could not compile a source file
- [vscode-cds@4.5.2] Removed obsolete code-formatting option `alignAsInElements` (calculated fields use `=` now)
- [cds-compiler@2.13.0] In query entities inside services, only auto-redirect associations and compositions in the main query of the entity.
- [cds-compiler@2.13.0] An element now inherits the property `notNull` from its query source (as before) or its type (like it does for most other properties); `notNull` is then not further propagated to its sub elements anymore.
- [cds-compiler@2.13.0] A structure element inherits the property `virtual` from its query source (as before), but does not further propagate `virtual` to its sub elements (semantically of course, but the CSN is not cluttered with it); there is a new warning if a previously `virtual` query entity element is now considered to be non-virtual.
- [cds-compiler@2.13.0] Do not propagate annotation value `null`. The value `null` of an annotation (and `doc`) is used to stop the inheritance of an annotation value. This means than other than that, a value `null` should not be handled differently to not having set that annotation.
- [cds-compiler@2.13.0] In the effective CSN, the structure type is only expanded if something has changed for associations: the `target` (`keys` does not change if the `target` does not change) unmanaged associations as sub elements are not supported anyway.
- [cds-compiler@2.13.0] In the effective CSN, “simple” type properties like `length`, `precision`, `scale` and `srid` are propagated even for a propagation via type.
- [cds-compiler@2.13.0] Update OData Vocabularies: 'Capabilities', 'Common', 'Core', 'UI'.
- [cds-compiler@2.13.0] to.sql: For SQL dialect `hana` referential constraints are now appended as `ALTER TABLE ADD CONSTRAINT` clause to the end of `schema.sql`. With option `constraintsInCreateTable` constraints are rendered into the `CREATE TABLE` statement.
- Referential constraint names are now prefixed with `c__`.

- [cds.java@1.23.0] Removed `RequestContextRunner.recalculateFeatureToggles()` without substitution. `RequestContextRunner.featureToggles(FeatureTogglesInfo)` is only allowed when creating the initial `RequestContext` of a request. The method throws an exception otherwise.
- [cds.java@1.23.0] Removed `RequestContextRunner.recalculateFeatureToggles()` without substitution. `RequestContextRunner.featureToggles(FeatureTogglesInfo)` is only allowed when creating the initial `RequestContext` of a request. The method throws an exception otherwise.
- [cds4j@1.27.0] If the data of deep Insert or deep Update contains values of an associated entity but the (forward mapped) association does not cascade the Insert/Update operation, the relationship is established instead of throwing an exception
- [cds@5.9.0] Cleaned up `cds.env.requires` towards a consistent usage: Moved all entries of `cds.requires` to `cds.requires.kinds` → `cds.requires` is empty now by default, but has `cds.requires.kinds` as prototype, so for example, `cds.requires.sql` will still return a match.
- Added support for db-specific `cds.requires.db.deploy-format` → deprecating `cds.hana.deploy-format` (which is still supported for compatibility)
- Introduced `cds.requires.kinds.hana-cloud` as `{kind:hana, deploy-format:hdbtable}` → to be used by default for production
- Changed `cds.requires.audit-log` to be consistent to all other; also got moved to `cds.requires.kinds.audit-log`, so it is no longer activated by default.
- Added support for `cds.requires.foo: true` with `foo` being a preset/prototype entry in `cds.requires.kinds` → allows to more easily switch on pre-configured services.

- [cds@5.9.0] Update-managed properties (`@cds.on.update`) are always updated Example: `UPDATE('Books').set({}).where({ ID: 1 })` leads to new modifiedAt and modifiedBy
- Does not apply to nested entities that are only preserved by specifying their primary keys in the data
- Deactivate during two month grace period via compact feature flag `cds.env.features.update_managed_properties = false`

- [cds@5.9.0] Response no longer contains keys neither technical draft properties (for example, `HasDraftEntity` or `InProcessByUser`) in expanded data if they were not requested explicitly when using `cds.Service` API Example:js

```
> await srv.read('Authors', a => { a.name, a.books(b => { b.title }) }).where({ ID: 1 })
// -> "old behaviour" result
[{ name: 'Emily Brontë', books: [{ title: 'Wuthering Heights', ID: 201 }] }]
// -> "new behaviour" result
[{ name: 'Emily Brontë', books: [{ title: 'Wuthering Heights' }] }]
```
- Technical draft properties are not automatically fetched also on a root level
- Deactivate during two month grace period via compat feature flag `cds.env.features.auto_fetch_expand_keys = true`

- [cds@5.9.0] Access control is checked in generic handlers (rather than handlers materialized on app startup)
- [cds@5.9.0] Expand restriction check moved to pre-before phase
- [cds@5.9.0] The active state of an entity is read instead of the draft state when navigating from a draft entity to a draft-enabled entity via an association.
- [cds@5.9.0] Authentication middleware is always mounted (used to be only for restricted services)
- [cds@5.9.0] Fiori preview now uses the Horizon theme
- [cds@5.9.0] 'Preview' links in generic index.html page no longer get the word preview appended automatically, allowing for more flexible naming. Link providers should make sure to add the preview word if necessary.
- [cds@5.9.0] Don't throw error in GraphQL adapter if update mutation filter does not match any entries (to be consistent with delete mutations)
- [cds@5.9.0] Remote call of unbound action/function returns octet-stream instead of string by default
- [cds@5.9.0] Default pool's behavior has been changed from `FIFO` (queue) to `LIFO` (stack). Can be changed in pool configuration.
- [cds@5.9.0] `cds run/serve` now gracefully shuts down the HTTP server before exiting. Custom handlers for signals like `SIGTERM` or `SIGINT` can now be processed.
- [cds@5.9.0] `cds build` no longer creates `COMMENT` statements for HANA if doc comments are present in CDS models. The statements caused superfluous table migrations during HANA deployments.

### Fixed ​

- [cds-dk@4.9.0] `cds compile --to openapi` now correctly treats `null` and the empty string as function parameters.
- [cds-dk@4.9.0] `cds bind --exec` no command output (STDOUT) displayed on Windows.
- [cds-dk@4.9.0] `cds watch` now gracefully shuts down the live reload server before exiting
- [cds-dk@4.9.0] `cds import` now generates correct csn for both OData V2 and V4 EDMX files where the EntityType has a BaseType entry.
- [cds-dk@4.9.0] `cds import` now throws an error in case of missing Association Sets.
- [cds-dk@4.9.0] `cds import` bug fixed for `--force` flag. Now overwrites the correct file content.
- [cds-dk@4.9.0] `cds import` fix will no longer capture unwanted annotations in the CSN for OData V4.
- [cds-dk@4.9.0] `cds import` now support annotations for properties of type `Type Definition`
- [cds-dk@4.9.0] `cds import` fix for supporting valid datatypes in unbounded function imports for OData V4.
- [cds-dk@4.9.0] `cds import` bug fixed for missing data imports for parameters with entity type not mapped to an entity set.
- [cds-dk@4.9.0] `cds import` now supports properties with complex type for OData V4.
- [cds-dk@4.9.0] `cds import` fix will now throw error if the key property of an entity is of type `Collection` for both OData V2 and V4 edmx.
- [cds-dk@4.9.0] `cds bind --to hana` provides more comprehensive error message in case Cloud Foundry `org` or `space` are not set.
- [cds-dk@4.8.2] `cds import` can now capture the data for any given `EntityContainer Name` for OData V4. Earlier it only worked when the name was `EntityContainer`.
- [vscode-cds@4.5.3] No loner set NODE_ENV to production which resulted in `npm i` only installing prod dependencies
- [vscode-cds@4.5.2] Saving a `cds` file now automatically refreshes all open previews for this file
- [vscode-cds@4.5.2] Show Formatting Options ConfigurationShowed empty samples editor
- Editor no longer switches to typescript
- No longer save changes popup when closing samples editor
- When not opened on existing file (CDS source or .cdsprettier.json) and workspace has multiple workspace folders, user has now to pick the workspace folder

- [vscode-cds@4.5.2] Code formatting:Separate post-annotation with blank
- Remove erroneous newlines around cardinality and filter in `select`
- Separate projection items with newlines

- [vscode-cds@4.5.2] Code completion for annotations now correctly handle e.g: @aaa.| entity
- [cds-compiler@2.13.8] to.hdbcds/hdi/sql: Correctly handle `localized` in conjunction with `@cds.persistence.exists` and `@cds.persistence.skip`
- [cds-compiler@2.13.6] to.hdbcds/hdi/sql: Correctly handle `localized` in conjunction with `@cds.persistence.exists`
- [cds-compiler@2.13.0] Properly resolve references inside anonymous aspects:references starting with `$self.` made the compiler dump.
- a simple `$self` did not always work as expected (it represents the entity created via the anonymous aspect).
- other references inside deeply nested anonymous aspects induced a compilation error.

- [cds-compiler@2.13.0] compiler: `()` inside `ORDER BY` clause was not correctly set.
- [cds-compiler@2.13.0] parse.cdl: References in `ORDER BY` and filters are now correctly resolved.
- [cds-compiler@2.13.0] Issue error when trying to introduce managed compositions of aspects in `mixin`s
- [cds-compiler@2.13.0] Issue error in all cases for type references to unmanaged associations.
- [cds-compiler@2.13.0] Avoid dump when extending an illegal definition with a name starting with `cds.`.
- [cds-compiler@2.13.0] to.sql/to.cdl/to.hdbcds/to.hdi: Render `cast()` inside `ORDER BY`, `GROUP BY` and `HAVING` properly.
- [cds-compiler@2.13.0] to.sql/hdi/hdbcds:`$self` was incorrectly treated as a structured path step.
- Correctly handle table alias in on-condition of mixin in `exists` expansion.
- Correctly handle table `$self` references to aliased fields in on-condition of mixin association during `exists` expansion.

- [cds-compiler@2.13.0] to.edm: Don't escape `&` as `&`.
- [cds-compiler@2.13.0] to.edmx: Escaping compliant to XML specification:`&` and `` is not escaped, unless it appears in text values as `]]>`.
- `"` is escaped in attribute values only.
- Control characters are always escaped.

- [cds-compiler@2.13.0] Ellipsis (`...`) in annotations in different layers but without base annotation now produces an error. The old but incorrect behavior can be re-enabled with option `anno-unexpected-ellipsis-layers`.
- [cds.java@1.23.0] Fixed a NPE in Auditlog v2 handler in case of single tenant scenario (ST) and OAuth2 plan.
- [cds.java@1.22.2] Fixed a bug causing changes on draft entities to be incorrectly handled when performed over a to-one navigation property.
- [cds.java@1.23.0] Fixed a NPE in Auditlog v2 handler in case of single tenant scenario (ST) and OAuth2 plan.
- [cds.java@1.22.2] Fixed a bug causing changes on draft entities to be incorrectly handled when performed over a to-one navigation property.
- [cds4j@1.27.0] Fix classloader issue with generated interfaces when using `spring-boot-devtools`
- [cds4j@1.27.0] Code generator: Fix use of '$' in doc comments
- [cds4j@1.27.0] Fix ClassCastException when selecting arrayed elements via static CDS QL builder
- [cds4j@1.26.2] HANA Search: In case a search operates on elements that are only supported with LIKE the search falls back to LIKE only for those elements and not for the whole statement. This can improve the scalability of a search operations significantly.
- [cds4j@1.26.2] HANA Search: Resolve search over elements in views with UNION to LIKE instead of CONTAINS.
- [cds4j@1.26.2] HANA Search: Resolve search over elements typed with LargeString (NClob) with LIKE instead of CONTAINS.
- [cds4j@1.26.2] HANA Search: Resolve search over elements in views annotated with @cds.persistence.exists: true with LIKE instead of CONTAINS.
- [cds@5.9.1] Function arguments might be escaped too often
- [cds@5.9.1] URL encoding for remote services for CQN queries
- [cds@5.9.1] `cds serve` during development again redirects URLs for UI apps in a folder with the same name as a service, so `/foo/webapp` would redirect to `/foo` again. This got broken in 5.8.3.
- [cds@5.9.1] Endless loop in localization handling
- [cds@5.9.1] Ensure service impl while extending entity from the service
- [cds@5.9.1] Post-processing of custom draft queries
- [cds@5.9.1] `cds build` no longer omits unused CDS type definitions, leading to Java compiler errors
- [cds@5.9.0] Logging of failed requests to remote services was incompatible to Elasticsearch
- [cds@5.9.0] `cds serve --project ` didn't serve static web resources from ``
- [cds@5.9.0] `cds serve -p ` was meant to be a shortcut for `cds serve --project `
- [cds@5.9.0] Messaging: Use correct kind for logging
- [cds@5.9.0] Incorrect return values for update-managed properties (`@cds.on.update`) of child entities that were not changed in request
- [cds@5.9.0] `$filter` with navigation to-one eq null
- [cds@5.9.0] Calculation of `DraftIsProcessedByMe` when navigating to `DraftAdministrativeData`
- [cds@5.9.0] Inbound streaming with media type annotated as `@Core.Computed`
- [cds@5.9.0] Pass column expression into `SELECT()` (example: `SELECT('SUBSTRING(locale,0,2) as loc').from()`)
- [cds@5.9.0] Annotation `@cds.api.ignore` ignores key in new parser
- [cds@5.9.0] Inconsistencies in actions and functions API
- [cds@5.9.0] Opening root transaction in `srv.run` if none exists
- [cds@5.9.0] Glitches in handling of `req.user.tenant` and `req.user.locale`
- [cds@5.9.0] Flattened keys in URL are resolved correctly if they are unique in new REST adapter
- [cds@5.9.0] Actions and functions in REST adapter
- [cds@5.9.0] Empty string as key does not work in new parser
- [cds@5.9.0] Requesting property of an entity caused error in new parser
- [cds@5.9.0] The SQLite CSV import now imports `"true"` and `"false"` as strings instead of Booleans
- [cds@5.9.0] Fixed loading mechanism for custom build task handlers
- [cds@5.9.0] `req.diff()` for `UPDATE` on a view with renamed property in `orderBy`
- [cds@5.9.0] `$user.` for managed properties (`@cds.on.insert`/`@cds.on.update`)
- [cds@5.9.0] GraphQL `__typename` meta field if it is the only selected field of an association/composition
- [cds@5.9.0] Command shortcuts like `cds c` are now handled properly if executed in an npm script
- [cds@5.9.0] ETag is not included in expanded entities using `$select`, for example: `Books(1)?$expand=author($select=ID)`
- [cds@5.9.0] `cds.compile.to...` no longer crashes if called with a CSN that has a dangling ref
- [cds@5.9.0] Requests to remote services via navigation path without explicit `$select`, but having `$expand` query option
- [cds@5.9.0] `cds.compile` correctly supports reserved namespaces like `cds.foundation`.
- [cds@5.9.0] `cds.compile.to.serviceinfo` now uses the correct configuration for the base URL paths for Java services
- [cds@5.9.0] `cds deploy --to sqlite` correctly localizes texts in deployed views. Before not all localized texts have been correctly resolved.
- [cds@5.9.0] `cds deploy --to hana` reports missing org or space info with a better message.
- [cds@5.9.0] Using combinations of `.` and `_` in CSN definition names
- [cds@5.8.4] `UPDATE` singleton entity does not require to provide singleton keys in a payload
- [cds@5.8.4] CQN queries with operator expressions (`xpr`) in ON-conditions of unmanaged associations and compositions
- [cds@5.8.3] `queries` property for application-defined destinations of remote services
- [cds@5.8.3] `cds serve --watch` no longer fails if `@sap/cds-dk` is installed only globally
- [cds@5.8.3] `cds serve` during development longer redirects URLs with similar path segments from different services, like `/service/one` and `/service`
- [cds@5.8.3] `cds deploy --to sqlite` now ignores a `_texts.csv` file again if there is a language-specific file like `_texts_en.csv` present
- [cds@5.8.3] Using logical blocks (surrounded with `(` and `)`) in ON-conditions of unmanaged associations and compositions
- [cds@5.8.3] Skip "with parameters" clause if no order by clause or all columns in the order by clause are not strings when using parametrized views on SAP HANA
- [cds@5.8.3] Limited support for binary data in OData[cds@5.8.3] Using of `base64` encoded string values in `WHERE IN` on SAP HANA
- [cds@5.8.3] `base64url` values in `@odata.context` annotation

- [cds@5.8.3] `cds.context` is set in GraphQL adapter
- [cds@5.8.3] Using payloads with `@odata.type` annotating primitive properties no longer crashes the application. `#` in type value may be omitted. Example:json

```
{
  "ID": 201,
  "title@odata.type": "#String",
  "title": "Wuthering Heights",
  "stock@odata.type": "Int32",
  "stock": 12
}
```
- [cds@5.8.3] Unicode support for i18n bundles
- [cds-mtx@2.5.3] Provisioning parameters for the container creation can now also be set exclusively for the `__META__` container via cds environment `mtx.provisioning.metadatacontainer` or environment variable `CDS_MTX_PROVISIONING_METADATACONTAINER`. Tenant containers are not affected by that cds environment.
- [cds-mtx@2.5.3] Configuration parameters for the `@sap/instance-manager` module can now be passes using cds environment `mtx.provisioning.instancemanageroptions` or environment variable `CDS_MTX_PROVISIONING_INSTANCEMANAGEROPTIONS`. See also @sap/instance-manager.
- [cds-mtx@2.5.3] Upgrade calls for non-existing tenants do no longer create orphan HDI containers
- [cds-mtx@2.5.3] More robust handling of inconsistent HDI container having no tenant id (error "TypeError: Cannot read property 'toLowerCase' of undefined")
- [cds-odata-v2-adapter-proxy@1.8.11] Fix for `falsy` values during data type conversion for functions and actions
- [cds-odata-v2-adapter-proxy@1.8.11] Add OData V2 links via link providers to HTML index page
- [cds-odata-v2-adapter-proxy@1.8.10] Refactor locale determination from CDS
- [cds-odata-v2-adapter-proxy@1.8.10] Serialize body to string in case of type `object` before calculating content length
- [cds-odata-v2-adapter-proxy@1.8.10] Support `AnalyticalContext` annotations in addition to deprecated `Analytics` annotations

### Removed ​

- [cds@5.9.0] Redundant locale implementation

## February 2022 ​

### Added ​

- [cds.java@1.22.1] The `cds-feature-auditlog-v2` automatically provides the dependency to the AuditLog v2 services during MT subscription, if it's using an `oauth2` plan.
- [cds.java@1.22.0] Added a local in-memory `MessagingService` implementation with kind `local-messaging` that can be used in JUnit tests. Its event publishing is synchronous to the event listeners, which frees test code from having to wait on the asynchronous execution of the listeners.
- [cds.java@1.22.0] The multitenancy library is now configured with a default resilience config, that attempts up to three retries with a wait time of 500ms in between in case requests to the MTX sidecar fail with unexpected errors.
- [cds.java@1.22.0] The OData V2 adapter now handles `@Aggregation.default: #COUNT`.
- [cds.java@1.22.0] The audit logging implementation now handles `@PersonalData.EntitySemantics: 'Other'`.
- [cds.java@1.22.0] `IN` predicates with user attributes are now supported in instance-based authorization conditions, e.g. `country in $user.countries`.
- [cds.java@1.22.0] To support deferred foreign key constraints in SQLite during the CSV data import, all CSV files can be imported in a single changeset. This behavior can be enabled by setting the new property `cds.dataSource.csvSingleChangeset` to `true`.
- [cds.java@1.22.0] Added a local in-memory `MessagingService` implementation with kind `local-messaging` that can be used in JUnit tests. Its event publishing is synchronous to the event listeners, which frees test code from having to wait on the asynchronous execution of the listeners.
- [cds.java@1.22.0] The multitenancy library is now configured with a default resilience config, that attempts up to three retries with a wait time of 500ms in between in case requests to the MTX sidecar fail with unexpected errors.
- [cds.java@1.22.0] The OData V2 adapter now handles `@Aggregation.default: #COUNT`.
- [cds.java@1.22.0] The audit logging implementation now handles `@PersonalData.EntitySemantics: 'Other'`.
- [cds.java@1.22.0] `IN` predicates with user attributes are now supported in instance-based authorization conditions, e.g. `country in $user.countries`.
- [cds.java@1.22.0] To support deferred foreign key constraints in SQLite during the CSV data import, all CSV files can be imported in a single changeset. This behavior can be enabled by setting the new property `cds.dataSource.csvSingleChangeset` to `true`.

### Changed ​

- [cds-dk@4.8.1] `cds init` uses latest Maven Java archetype version `1.22.0` for creating Java projects.
- [cds.java@1.22.0] Potentially sensitive values are now excluded from logged CQN statements by default. To enable logging of sensitive values again you can set `cds.security.logPotentiallySensitive` to `true`
- [cds.java@1.22.0] Potentially sensitive values are now excluded from logged CQN statements by default. To enable logging of sensitive values again you can set `cds.security.logPotentiallySensitive` to `true`

### Fixed ​

- [cds-dk@4.8.1] Bump `follow-redirects` package to 1.14.8 (CVE-2022-0536)
- [cds-dk@4.8.1] `cds bind --exec` no command output (STDOUT) displayed on Windows.
- [vscode-cds@4.5.1] extension did not start in Business Application Studio
- [cds.java@1.22.1] The `cds-feature-auditlog-v2` doesn't support plan `oauth2` in combination with persistent Outbox and the startup of the CAP Java application now fails with a corresponding error. If persistent Outbox is enabled, the plan `standard` of the Auditlog v2 service has to be used.
- [cds.java@1.22.0] Fixed a bug, that caused `NullPointerException`s when elements were present in a `Result` provided to the OData V2 adapter that were not part of the EDMX definition.
- [cds.java@1.22.1] The `cds-feature-auditlog-v2` doesn't support plan `oauth2` in combination with persistent Outbox and the startup of the CAP Java application now fails with a corresponding error. If persistent Outbox is enabled, the plan `standard` of the Auditlog v2 service has to be used.
- [cds.java@1.22.0] Fixed a bug, that caused `NullPointerException`s when elements were present in a `Result` provided to the OData V2 adapter that were not part of the EDMX definition.
- [cds4j@1.26.1] Navigating associations of draft-enabled entities with keys named other than 'ID'.
- [cds4j@1.26.1] Fix potential hash collisions in deep updates
- [cds4j@1.26.1] Elements with type UUID that are annotated with `@odata.Type:'Edm.String'` are not normalized anymore, comparison is case sensitive
- [cds@5.8.2] Crash if error does not have a stack in Kibana logging
- [cds@5.8.2] Allow short names for bound operations in odata-server
- [cds@5.8.2] Performance issue during deep operations
- [cds@5.8.2] Resolving views with parameters
- [cds@5.8.2] Expanding association-to-many within draft union scenario
- [cds@5.8.2] Erroneous invalidation of deep `INSERT|UPDATE|DELETE` operations if root entity has managed to-one association to non-writable view
- [cds@5.8.2] Handling of falsy results when sending requests to remote services
- [cds@5.8.2] Resolving foreign key propagations for views with union
- [cds@5.8.1] Use single transaction for update mutations in GraphQL adapter
- [cds@5.8.1] ODATA to CQN parser returned not selected keys in `@odata.context`
- [cds@5.8.1] Draft: `$expand` with special draft columns in `$orderBy` for active entities
- [cds@5.8.1] Reading distinct values of draft enabled entity
- [cds@5.8.1] Handling of LOB data on HANA
- [cds@5.8.1] Fix streaming draft by navigation
- [cds@5.8.1] Empty to-many arrays are not removed from req.data for inserts
- [cds@5.8.1] `$filter` query option in structured mode (OData flavors `w4` and `x4`) Using JSON-stringified objects no longer occasionally crashes an application
- Filtering on a structured element with `ne null` condition also selects data having some `null` properties within

- [cds@5.8.1] Rest: `Content-type` header is set to `text/plain` for primitive data types in response (except for `Boolean`)
- [cds@5.7.6] `draftActivate` action does not return children if not requested
- [cds-odata-v2-adapter-proxy@1.8.9] Stabilization fixes
- [cds-odata-v2-adapter-proxy@1.8.8] Proxy option `calcContentDisposition` to calculate `content-disposition` header even if already available
- [cds-odata-v2-adapter-proxy@1.8.7] Proxy option `fixDraftRequests` to convert unsupported draft request to a working version (default: false)
- [cds-odata-v2-adapter-proxy@1.8.6] Fix README for combined custom backend bootstrap
- [cds-odata-v2-adapter-proxy@1.8.6] Allow annotation `@odata.type` in lower case format
- [cds-odata-v2-adapter-proxy@1.8.6] Allow type prefix `datetime` in addition to `datetimeoffset`
- [cds-odata-v2-adapter-proxy@1.8.6] Add peer dependency @types/express

## January 2022 ​

### Added ​

- [cds-dk@4.8.0] `cds import` now reflects the entity set and entity container level annotations in the csn.
- [cds-dk@4.8.0] `cds activate --sync` allows to use the synchronous server API for extension upload.
- [vscode-cds@4.5.0] workspace symbols query now supports filters for kinds
- [cds-compiler@2.12.0] CDL parser: You can now use multiline string literals and text blocks. Use backticks (`) for string literals that can span multiple lines and can use JavaScript-like escape sequences such as `\u{0020}`. You can also use three backticks (```) for strings (a.k.a. text blocks) which are automatically indentation-stripped and can have an optional language identifier that is used for syntax highlighting, similar to markdown. In difference to the former, text blocks require the opening and closing backticks to be on separate lines. Example:cds

```
@annotation: `Multi
 line\u{0020}strings`
@textblock: ```xml

              The root tag has no indentation in this example

            ```
```
- [cds-compiler@2.12.0] Enhance the ellipsis operator `...` for array annotations by an `up to `: only values in the array of the base annotation up to (including) the first match of the specified `` are included at the specified place in the final array value. An array annotation can have more than on `... up to ` items and must also have a pure `...` item after them. A structured `` matches if the array item is also a structure and all property values in `` are equal to the corresponding property value in the array value; it is not necessary to specify all properties of the array value items in ``. Examplecds

```
@Anno: [{name: one, val: 1}, {name: two, val: 2}, {name: four, val: 4}]
type T: Integer;
@Anno: [{name: zero, val: 0}, ... up to {name: two}, {name: three, val: 3}, ...]
annotate T;
```
- [cds-compiler@2.12.0] for.odata: Support `@cds.on {update|insert}` as replacement for deprecated `@odata.on { update|insert }` to set `@Core.Computed`.
- [cds4j@1.26.0] Support nulls first|last in orderBy
- [cds4j@1.26.0] JavaDocs for CqnVisitor
- [cds@5.8.0] Custom `server.js` don't have to export `cds.server` anymore -> we use that by default now.
- [cds@5.8.0] In `cds.requires`: Support to replace primitive values with objects
- [cds@5.8.0] Support filter functions on renamed properties from external service
- [cds@5.8.0] Results of database queries use `big.js` for values of type `cds.Decimal` and `cds.Integer64` if enabled via `cds.env.features.bigjs`
- [cds@5.8.0] Support lambda in `$filter` in `$expand`
- [cds@5.8.0] Support for `GET` requests on service root in REST adapter (old and new)
- [cds@5.8.0] Support for `HEAD` requests in REST adapter (old and new)
- [cds@5.8.0] New hook `req.before('commit')`
- [cds@5.8.0] Draft (Access control for bound actions): Only the user that is the owner of the draft can execute its bound actions.
- [cds@5.8.0] Check that all keys are provided in REST adapter
- [cds@5.8.0] Restrict access to all services via `cds.env.requires.auth.restrict_all_services = true`That is, all unrestricted services (i.e., w/o own `@requires`) are treated as having `@requires: 'authenticated-user'`

- [cds@5.8.0] Threshold for automatically sending GET requests as `$batch` (beta, cf. @sap/cds@5.6.0) can be configured per remote service via `cds.env.requires..max_get_url_length` (if not configured on service, the global config applies)
- [cds@5.8.0] Limited support for binary data in ODataIn payloads, the binary data must be a base64 encoded string
- In URLs, the binary data must have the following format: `binary''`, for example, `$filter=ID eq binary'Q0FQIE5vZGUuanM='`
- The use of binary data in some advanced constructs like `$apply` and `/any()` may be limited
- On SQLite, the base64 encoded string is stored in the database
- It's strongly discouraged to use binary data as keys. See "Primary Keys — Best Practices" in the documentation.

- [cds@5.8.0] Support for OData annotation `@Core.ContentDisposition.Type` with `attachment` as the default value
- [cds@5.8.0] Support for returning custom stream objects in custom handlers Beta:Example:js

```
return {
  value: instanceof Readable || null,
  $mediaContentType : 'image/jpeg',
  $mediaContentDispositionFilename : 'foo.bar', // > optional
  $mediaContentDispositionType : 'inline' // > optional
}
```

- [cds-mtx@2.5.2] It is now checked if CDS annotations `@sql.append` and `@sql.prepend` are used in extensions. Using these annotations in extensions is currently not allowed.

### Changed ​

- [cds-dk@4.8.0] The forked package `@mendix/sqlite3` is now used instead of `sqlite3` to overcome CVE-2021-32804. No code changes in applications are needed, as the new package installed by `npm` with the same name `sqlite3`.
- [cds-dk@4.8.0] [beta] The templating for `cds init` and `cds add` has been rewritten from scratch. This will allow for some new, more complex commands, such as `cds add mtx` or `cds add xsuaa`.
- [cds-dk@4.8.0] Use `cds bind` during `cds deploy` to store connection information in file `.cdsrc-private.json`.
- [cds-dk@4.7.3] Bump `follow-redirects` package to 1.14.7 (CVE-2022-0155)
- [eslint-plugin-cds@2.3.2] Rule `require-2many-oncond` now also detect navigations of aspects for flavor 'parsed'
- [eslint-plugin-cds@2.3.2] Removed duplicates from rule results of category 'Environment'
- [vscode-cds@4.5.0] consume cds-compiler 2.12.0
- [vscode-cds@4.5.0] code completion for `index.cds` files will now render just the folder
- [vscode-cds@4.5.0] CDS language server is now bundled and minified to speed up initialization
- [vscode-cds@4.5.0] performance: revalidate file on focus got only if stale index
- [vscode-cds@4.5.0] memory consumption: indexes are now cached per file, no longer per compilation
- [cds-compiler@2.12.0] Update OData Vocabularies 'Aggregation', 'Capabilities', 'Common', 'Core', PersonalData, 'Session', 'UI'
- [cds4j@1.26.0] CqnStructuredTypeRef does not traverse the segments any longer
- [cds4j@1.26.0] visiting ref segments is deprecated: CqnReference.Segment.accept(CqnVisitor)
- CqnVisitor.visit(Segment) are deprecated

- [cds@5.8.0] `cds deploy --to hana` now uses `cf curl` instead of `cf` command natively
- [cds@5.8.0] Event Mesh: In multitenancy mode, messaging artifacts are also deployed for provider accounts (unless the service option `deployForProvider` is set to `false`)
- [cds@5.8.0] Status code in case of multiple errors (rules apply in order): If all errors have the same status code, that status code is used
- If there is at least one 5xx status code, the resulting status code is 500
- If there is at least one 4xx status code, the resulting status code is 400
- If none of the rules apply, the resulting status code is 500

- [cds@5.8.0] Ignore the `If-Match` HTTP request header for `UPDATE`/`DELETE` requests whose target entities are not annotated with the `@odata.etag` annotation.
- [cds@5.8.0] I18n template strings now are replaced in EDMX documents such that they can occur multiple times. For example, the `{i18n>key1} - {i18n>key2}` template results in `value1 - value2`, while previously only the first string was replaced, leading to `value1 - {i18n>key2}`. This is helpful for the `Template` strings of `UI.ConnectedFields`.

### Fixed ​

- [cds-dk@4.8.0] `cds import` now omits function imports with `put/delete` kind.
- [cds-dk@4.8.0] `cds import` has fixed the entity type to entity set mapping in OData V2.
- [cds-dk@4.8.0] `cds import` now supports collection type.
- [cds-dk@4.8.0] `cds watch` now picks a free livereload port if the standard port 35729 is already bound
- [cds-dk@4.8.0] `cds extend`, `cds activate`, `cds login`, and `cds logout` now prioritize command-line options over saved settings
- [cds-dk@4.8.0] MTX client now logs fewer characters of secrets in debug output
- [cds-dk@4.8.0] MTX client now handles incomplete error responses better
- [vscode-cds@4.5.0] `cds preview` is now refreshing the preview correctly when called after the underlying cds file has been changed
- [vscode-cds@4.5.0] `enum` was not indexed
- [vscode-cds@4.5.0] `composition` of aspect was not indexed
- [vscode-cds@4.5.0] symbols contained localized entries with recent compiler versions
- [vscode-cds@4.5.0] workspaces with many workspace folders could lead to stop lsp
- [vscode-cds@4.5.0] syntax highlighting is now better aligned with CDS grammar: multi-lined strings disabled
- backslash escaping disabled
- doubled quotes inside strings to reproduce single quotes
- element types now include scopes and length/size arguments

- [cds-compiler@2.12.0] to.sql/hdi/hdbcds: With `exists`, ensure that the precedence of the existing association-on-conditions and where-conditions is kept by adding braces.
- [cds-compiler@2.12.0] to.sql/hdi: Window function suffixes are now properly rendered.
- [cds-compiler@2.12.0] to.sql: `$self` comparisons inside aspects are not checked and won't result in an error anymore.
- [cds-compiler@2.12.0] to.hdbcds: Correctly apply the "."-to-"_"-translation algorithm to artifacts that are marked with `@cds.persistence.exists`.
- Message with ID `anno-hidden-exists` (former `anno-unstable-hdbcds`) is now only issued if the compiler generates a SAP HANA CDS artifact which would hide a native database object from being resolved in a SAP HANA CDS `using … as …`.

- [cds-compiler@2.12.0] to.cdl: Annotation paths containing special characters such as spaces or `@` are now quoted, e.g. `@![some@annotation]`.
- [cds-compiler@2.12.0] compiler: A warning is emitted for elements of views with localized keys as the localized property is ignored for them.
- [cds4j@1.26.0] Fix to-many expands using `or` in on condition
- [cds4j@1.26.0] Code generator: Allow expand and to select subelements of structured elements in builder interfaces
- [cds4j@1.26.0] Fix CqnValidation to avoid StackOverflowError
- [cds@5.8.0] At Node.js runtime, the `development` configuration profile is no longer active if `CDS_ENV` is set to `production` and `NODE_ENV` is undefined
- [cds@5.8.0] Enterprise Messaging: The user is now privileged for AMQP
- [cds@5.8.0] `cds.spawn` also works with synchronous functions
- [cds@5.8.0] Foreign keys in parent are set to `null` when deleting composition of one
- [cds@5.8.0] `cds version` now always prints the version of `@sap/cds-dk`, especially if `cds version` was called from within an npm script, i.e. not from `cds-dk`'s CLI.
- [cds@5.8.0] Better error message in case destination of Remote Service isn't found
- [cds@5.8.0] Differentiate between draft already exists and entity locked
- [cds@5.8.0] OData adapter: roll back transaction before re-throwing standard error in case of atomicity group
- [cds@5.8.0] Results of actions/functions do not ignore custom data when using `$expand` query option
- [cds@5.8.0] `req.data` is available in custom error handler in case of deserialization error thrown by legacy OData server
- [cds@5.8.0] Joining entities with renamed foreign keys (limited to single-level projections)
- [cds@5.8.0] Requests with draft and `$expand=*` caused problems in some cases
- [cds@5.8.0] `cds serve` during development longer redirects URLs with similar path segments like `/browse/123/browse/` to for example, `/browse/`
- [cds@5.8.0] Post-processing for renamed columns in expand
- [cds@5.8.0] Deploy to SAP HANA: passing of options to `hdi-deploy` via `HDI_DEPLOY_OPTIONS` now possible
- [cds@5.8.0] Keys as path segments in beta OData to CQN parser
- [cds@5.8.0] OData V2 Remote Service (`"kind": "odata-v2"`): Request data properties of types `cds.Date`, `cds.DateTime`, and `cds.Timestamp` are converted accordingly to OData V2 specification
- Response data properties of types `cds.Decimal`, `cds.DecimalFloat` (deprecated) and `cds.Integer64` are handled properly when using `Accept` header with `IEEE754Compatible=true/false` and `ExponentialDecimals=true/false` format parameters

- [cds@5.7.5] Instance-based restriction for activation of draft-enabled entities using `or` in restriction
- [cds@5.7.5] Messaging: Duplicate handler execution if application service registered events twice
- [cds@5.7.5] Post of a deeply nested sub-entity with structured parent keys
- [cds@5.7.5] Negating lambda expressions in OData using the `not` operator
- [cds@5.7.5] Event Mesh: Redelivery count when using AMQP
- [cds@5.7.5] OData requests using lambda expressions on localized data
- [cds@5.7.5] `cds.db.exists` wrongly generated a `SELECT * FROM ...` for OData flavor x4
- [cds@5.7.5] Return localized texts on draft activate
- [cds@5.7.5] Unicode characters in unquoted search terms in beta OData to CQN parser
- [cds-mtx@2.5.2] API `/mtx/v1/provisioning/tenant` does no longer return duplicate tenants in case of concurrent API calls.
- [cds-mtx@2.5.2] Dependencies to `VCAP_SERVICES` environment have been removed. Service dependencies can now be fully defined via `cds.env`, except for databases shared between tenants.
- [cds-odata-v2-adapter-proxy@1.8.5] Prevent additional call to fill `content-disposition`, in case header is already provided with stream
- [cds-odata-v2-adapter-proxy@1.8.5] Support OData V2 `binary` media upload via POST for entities with element of type `Binary` and without `@Core.MediaType` annotations
- [cds-odata-v2-adapter-proxy@1.8.5] Return server error as response, if OData V4 server does not support media upload without `@Core.MediaType` annotation, for example, `No payload deserializer available for resource kind 'PRIMITIVE' and mime type 'image/png'`
