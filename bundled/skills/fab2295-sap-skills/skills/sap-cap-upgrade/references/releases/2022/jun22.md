<!-- mirror: https://cap.cloud.sap/docs/releases/2022/jun22 -->
<!-- fetched: 2026-05-09T02:26:32.279Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# June 2022 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Important Changes ❗ ​

### Authentication Enforced in Production ​

In a productive scenario with an authentication strategy configured, for example XSUAA, *all CAP service endpoints are now authenticated by default regardless of the authorization model*.

In Node.js this can be disabled via feature flag `cds.env.requires.auth.restrict_all_services: false` or by using mock authentication explicitly in production.

[For Java find details below](#security-java).

### Database-Level Constraints & @assert.target ​

With general availability of [database-level integrity constraints](/docs/guides/databases/cdl-to-ddl#database-constraints), service-level integrity checks as provided in the Node.js stack, are now deprecated and planned to be removed with the next major release. In essence, take notice of these changes:

Tip

**DB-level constraints** are the recommended way to ensure referential integrity.
Yet they are **not enabled by default** → do that explicitly by setting `cds.env.features.assert_integrity = 'db'`.

Warning

**Service-level referential integrity** checks are deprecated from now on, and [not enabled by default anymore](#changes-in-node-js). They will likely be removed with next major.

Warning

**Integrity Checks are not for end users** — Always keep in mind: Referential integrity checks are designed and meant for avoiding corruption of your database's integrity. The error messages that they produce are not suitable for end users of your apps. → [use `@assert.target` for that](#input-validation-for-associations-assert-target).

#### Input Validation for Associations — @assert.target ​

To address input validation on references suitable for end users, we introduced new annotation [`@assert.target`](/docs/guides/services/constraints#assert-target), which ensures, that the target of a managed to-one association exists.

cds

```
entity Books {
  ...
  author : Association to Authors @assert.target;
}
```

[Learn more about `@assert.target`](/docs/guides/services/constraints#assert-target)

### Improved Read After Write ​

OData `CREATE` and `UPDATE` requests, as well as draft-related `EDIT` and `SAVE` actions, are now followed by an additional `READ` request to the application service, instead of mixing the handler result with the database state.

##### As a Consequence ​

- It's only required to register `READ` handler to adjust the response, for example to handle virtual properties, instead of registering the same handler also for the above mentioned events.
- A user only sees the full response if authorized.
- If the subsequent `READ` results in an error, the response status is 204 without payload.

##### Formerly ​

js

```
  // Apply a discount for over-stocked books
  this.after ('READ','Books', each  => {
    if (each.stock > 111) each.title += ' -- 20% off'
  })
```

js

```
  // We additionally have to do that for responses after write
  this.on (['CREATE','UPDATE'], 'Books', async (_, next) => {
    const book = await next()
    // Results of write operations might be minimized
    if (!book.stock) {
      let {stock} = await SELECT `stock` .from (Books,book.ID)
      book.stock = stock
    }
    if (book.stock > 111) book.title += ' -- 20% off'
    return book
  })
```

##### Now ​

js

```
  // Apply a discount for over-stocked books
  this.after ('READ','Books', each  => {
    if (each.stock > 111) each.title += ' -- 20% off'
  })
```

### SAP Cloud SDK v2 (Node.js) ​

The usage of the SAP Cloud SDK dependency is now aligned with other dependencies. It is now an optional package that needs to be installed if required, similar to SAP HANA driver. To have it working as before, make sure to install the required packages as described in section [Mock Remote Service as OData Service (Node.js)](/docs/guides/services/consuming-services?impl-variant=node#mock-remote-service-as-odata-service-node-js).

### Dropped Support for Node.js v12 ​

Following the plans laid out in the [Release Schedule](./../schedule), please take notice of these changes and transitions:

Warning

**CAP cds 6 doesn't support Node v12** — Node.js v14.15 is now the minimum required Node.js version. You should better upgrade to Node.js v16 (current Active LTS version).

Warning

**CAP cds 5 goes into [Maintenance Status](./../schedule#maintenance-status)** — Essentially means that it will receive only emergency fixes from now on → plan to upgrade to cds 6 as soon as possible.

Danger!

**CAP cds 4 reached [End of Life Status](./../schedule#end-of-life-status)** — Essentially means that you urgently should upgrade to cds 6 now, unless your project reached end-of-life as well.

## Highlights ​

### Feature-Toggled Aspects ​

[Feature-Toggled Aspects](/docs/guides/extensibility/feature-toggles) complement the range of [CAP's extensibility offerings](/docs/guides/extensibility/) by one that allows SaaS providers to prepare prebuilt extensions, which can be toggled dynamically at runtime.

[Learn more about Features-Toggled Aspects in the Cookbook.](/docs/guides/extensibility/)

### Streamlined MT(X) ​

We thoroughly redesigned and refactored our MTX Services. The new package `@sap/cds-mtxs` (note the trailing `s`) provides a modular set of standard CAP services, which implement *[multitenancy](/docs/guides/multitenancy/)*, *[features toggles](/docs/guides/extensibility/feature-toggles)*, and *[extensibility](/docs/guides/extensibility/)* (*'MTX'* stands for these three functionalities).

#### Key Benefits ​

- Test-Drive Locally → While the 'old' MTX always required SAP HANA and an SAP BTP setup, you can now run fully MTX-enabled apps locally, with minimal complexity, using SQLite in-memory database, and so on.
- Grow as you go... → This also allows you to enable MTX only when required, as well as to simplify and speed up your test pipelines significantly; in turn accelerating development.
- MTX = CAP services → Being plain standard CAP services allows to benefit from all the flexibility CAP provides, such as customizing service definitions using CDS Aspects, adding custom event handlers, and so on. You can enhance and adapt MTX to your needs.
- Resource Consumption → The minimized and refactored implementations are the basis for some optimizations already applied, and much more to follow going forward

[Learn more about Streamlined MTX.](/docs/guides/multitenancy/mtxs)

#### Limitations → to Come Soon ​

Warning

**Extensibility** with streamlined MTX is not finalized and documented, hence not released yet → will follow soon with upcoming releases.

Warning

**Gaps in documentation** — there are still a few gaps in our documentation that we will fill in on the go, also between releases.

#### Migration from 'Old' MTX ​

The old MTX is still available through `@sap/cds-mtx` (without suffixed `s`). Means that you don't have to adopt the new, streamlined MTX in a hurry.

Tip

**Migration to New MTX** is very much straight forward. No content needs to be changed, configurations stay very much the same, only stored extensions need to be migrated, which we plan to support generically. We will document how to [migrate to new MTX](/docs/guides/multitenancy/old-mtx-migration) soon.

Warning

**No need to hurry, yet...** — you should plan to adopt new MTX as soon as possible within the next 12 months, as the old MTX goes into [Maintenance Status](./../schedule#maintenance-status) now (that means, will only receive emergency bug fixes from now on), and will reach [End of Life Status](./../schedule#end-of-life-status) with the next major release. :::

### Experimental Support for ECMAScript Modules (ESM) ​

You can now write CAP Node.js applications using ECMAScript Modules (ESM). Let's use, for example, the following handler code:

js

```
const cds = require('@sap/cds')
module.exports = function() { ... }
```

This is how you can turn it into an ES module:

js

```
import cds from '@sap/cds'
export default function() { ... }
```

[Learn more about ES modules](https://nodejs.org/docs/latest-v16.x/api/esm.html#modules-ecmascript-modules)

#### Enabling ESM support ​

The easiest to enable that, is to set type module in your package.json:

jsonc

```
  ...
  "type": "module",
  ...
```

[Find more information on this in the Node.js docs](https://nodejs.org/docs/latest-v16.x/api/esm.html#esm_enabling)

With ESM enabled, CAP will load all your JavaScript files (custom handlers, server.js) and asynchronously using [dynamic imports](https://javascript.info/modules-dynamic-imports).

#### Limitations ​

Some third party libraries still have issues with ESM modules. For example, [ESM support in Jest v28](https://jestjs.io/docs/28.0/ecmascript-modules) is still experimental, and we encountered lots of issues, so **we currently disable ESM support when running in Jest**.

Warning

**Note** that this feature is rated ***experimental*** so far.

### Import OpenAPI ​

The `cds import` command can now import OpenAPI documents into CSN file. It translates all operations into unbound actions and functions on service level.

To import OpenAPI documents, use:

sh

```
cds import ~/Downloads/OpenAPI_sample.json
```

Specify the `--from` option to import from EDMX, OpenAPI sources explicitly.

To import OpenAPI documents programmatically, use the [APIs](/docs/tools/apis/cds-import#cds-import-from-openapi).

### GraphQL GA ​

As a first step to a better package structure, the implementation of [the GraphQL protocol adapter](/docs/plugins/index#graphql-adapter) has moved to a separate package `@sap/cds-graphql`. The GraphQL adapter has reached an early general availability state and can be found on the [default npm registry](https://www.npmjs.com/package/@sap/cds-graphql), including instructions on how to get started.

### Shared Locks ​

Use *shared* locks in [pessimistic locking](/docs/guides/services/served-ootb#select-for-update) to prevent data from concurrent modification without blocking concurrent readers.

In CAP Java use [the `Select.lock()` method](/docs/java/working-with-cql/query-execution#pessimistic-locking) to obtain a shared lock:

java

```
import static com.sap.cds.ql.cqn.CqnLock.Mode.SHARED;
Select.from("bookshop.Books").byId(17).lock(SHARED);
```

In CAP Node.js use [the `forShareLock` method](/docs/node.js/cds-ql#forsharelock):

js

```
SELECT.from(Books,17).forShareLock()
```

### CAP on Kyma/K8s ​

You can now run CAP applications on SAP BTP, Kyma runtime.

You can add a [Helm chart](https://helm.sh/) containing the [Kubernetes deployment files](https://kubernetes.io/docs/reference/kubernetes-api/) to your CAP project with the [`cds add helm` command](/docs/guides/deploy/to-kyma#deploy-to-kyma). There is a new guide in the section [Deployment](/docs/guides/deploy/) that explains the [deployment to Kyma Runtime](/docs/guides/deploy/to-kyma):

Explore the many opportunities [Kyma](https://kyma-project.io/) and its underlying components, [Kubernetes](https://kubernetes.io/de/) and [Istio](https://istio.io/), gives you. For example, how to [easily secure communication between services](/docs/guides/services/consuming-services#connect-to-an-application-in-your-kyma-cluster).

For the deployment to SAP BTP, Kyma runtime, CAP supports reading service bindings from volume mounts in Java and in [Node.js](/docs/node.js/cds-connect#in-kubernetes-kyma).

[Learn more about the SAP BTP, Kyma Runtime](https://discovery-center.cloud.sap/serviceCatalog/kyma-runtime?region=all)

### CAP Notebooks in VS Code ​

Since [November 2021](https://code.visualstudio.com/blogs/2021/11/08/custom-notebooks#_notebook-support-in-vs-code), Notebooks have become part of the core functionality of VS Code. This allows to build VS Code extensions that support custom notebook extensions for *any* language or purpose, for example, [GitHub Issue Notebook](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-github-issue-notebooks) or [REST Book](https://marketplace.visualstudio.com/items?itemName=tanhakabir.rest-book).

Thus, we have substituted the formerly known CAP *Jupyter* Notebooks by the native [VS Code CAP Notebooks](/docs/tools/cds-editors#cap-vscode-notebook) within the [CDS Editor](/docs/tools/cds-editors). They are thus no longer isolated web views (Jupyter), but can actually interact with the rest of VS Code and any other extension enabling **syntax highlighting, indentation, code completion, and so on**.

Furthermore, we have **extended the number of CAP Notebooks** you can try out. These can be started using the command *CDS: Open CAP Notebooks Page*.

### CAP CDS on github.com ​

*CAP CDS* is now a publicly known language on [github.com](https://github.com).

You get syntax highlighting for [CAP CDS files](https://github.com/SAP-samples/cloud-cap-samples/blob/bcb6ffa20f96fc5d075153d9aa29494309053eb3/bookshop/db/schema.cds):

*CAP CDS* files are considered in language overview statistics:

### CAP Samples: Tree View ​

There is [new sample code](https://github.com/SAP-samples/cloud-cap-samples/pull/365) available that showcases hierarchical data using SAP UI5's `TreeTable`, the `@sap.hierarchy` annotations, OData V2, and the [CDS OData V2 adapter](https://www.npmjs.com/package/@sap/cds-odata-v2-adapter-proxy).

In addition, there is a [new, detailed blog post by Oliver Klemenz](https://blogs.sap.com/2022/07/01/display-of-hierarchical-data-in-sap-fiori-elements-using-sap-cloud-application-programming-model/) on this topic.

## CDS Language & Compiler ​

### Important Changes ❗️ ​

#### Removed "Compatibility" Options ​

In the step from Compiler v1 to v2 there had been a few incompatible changes. We had introduced some "compatibility" options to keep the old behavior for some time to ease the upgrade. These options have now been removed, using them leads to an error: "Deprecated flag ... has been removed in CDS compiler v3". If you see this error, you have to adapt your code to the v2 behavior.

[Learn more about Upgrade to Compiler v2.](/docs/cds/compiler/v2)

#### Remove Compiler v1 Options ​

Early versions of Compiler v1 used different options. Since Compiler v1.24, new options are available. With Compiler v3, support for old option names was removed. If you have a `"cdsc"` section in your `.cdsrc.json` or `package.json`, please ensure that the following options are replaced:

- `magicVars`: This option was replaced by `variableReplacements`.
- `toSql` / `toOdata` / `toHana` / `toCdl` / `toCsn`: These command specific options were removed. Command specific options are now top-level.
- `.names`: Use `sqlMapping` instead.
- `.dialect`: Use `sqlDialect` instead.
- `toOdata.version`: Use `odataVersion` instead.

Note that options such as `sqlMapping`, `sqlDialect`, as well as `odataVersion` are already set by `@sap/cds` and `@sap/cds-dk`. Usually you don't need these options in your `.cdsrc.json` at all.

#### Generated Objects and @cds.persistence.exists/skip ​

We made the behavior of the annotations `cds.persistence.skip` and `cds.persistence.exists` more consistent.

Now, no foreign key constraints on the database are generated for a managed association if the source entity or the target entity are annotated with `@cds.persistence.skip` or `@cds.persistence.exists`. With compiler v2, a foreign key constraint was generated even if the target entity is annotated with `@cds.persistence.exists`.

[Learn more about Database Constraints.](/docs/guides/databases/cdl-to-ddl#database-constraints)

If an entity with a localized element or a managed composition is annotated with `@cds.persistence.exists` or `@cds.persistence.skip`, this annotation is now also applied to the generated text or child entities, respectively. Thus, no database tables are generated for these text or child entities any more. With compiler v2, database tables were generated for the text or child entities.

If a different behavior is wanted, the generated text or child entities can be annotated explicitly with `@cds.persistence.exists/skip: false`.

[Learn more about unfolding text entities.](/docs/guides/uis/localized-data#behind-the-scenes) [Learn more about Managed Compositions.](/docs/cds/cdl#managed-compositions)

*Localized helper views* are no longer generated for entities annotated with `@cds.persistence.exists`, so that now the behavior is the same as for `@cds.persistence.skip`.

[Learn more about Localized Helper Views.](/docs/guides/uis/localized-data#localized-helper-views)

### Define Association in a Projection ​

An unmanaged association can now be defined directly in the select list of a view or projection:

cds

```
entity BookReviews as projection on Reviews {
  ...,
  subject as bookID,
  book : Association to Books on book.ID = bookID
};
```

The new association becomes part of the projection signature, but cannot be used in the query itself. In the ON condition you can, besides target elements, only reference fields of the select list. Elements of the query's data sources are not accessible. In comparison to mixins, this syntax is simpler and also available in projections.

[Learn more about Defining Associations in a select list.](/docs/cds/cql#select-list-associations)

With this syntax, it's now possible to add new, unmanaged associations to a projection or view in an extension:

cds

```
extend BookReviews with columns {
  subject as bookID,
  book : Association to Books on book.ID = bookID
};
```

[Learn more about Extending Views and Projections.](/docs/cds/cdl#extend-view)

### Annotating OData Annotations ​

Adding a nested annotation to a scalar or array valued OData annotation has been simplified: add a parallel annotation that has the nested annotation name appended to the outer annotation name:

cds

```
@UI.LineItem: [
    {Value: ApplicationName},
    {Value: Description}
]
@UI.LineItem.@UI.Criticality: #Positive
```

Generated EDMX:

xml

```

  ...


```

The old way of annotating a single value or a Collection by turning them into a structure with an artificial property `$value` is still possible, but deprecated.

Overwriting or extending annotated annotations via `annotate` now works as expected.

[Learn more about Annotating Annotations.](/docs/guides/protocols/odata#annotating-annotations)

### Arguments for Simple Custom Types ​

It is now possible to provide arguments when *using* a simple custom type.

cds

```
type NumericString : String;

entity Address {
  ...,
  zipCode : NumericString(5);
}
```

### Load On Demand ​

Requiring an API function of the compiler will no longer load the whole compiler, but only the necessary parts.

### Overriding OData Type Mapping ​

Overriding the OData type mapping with annotation `@odata.Type` can now be done with any EDM type.

cds

```
entity Foo {
  ...,
  @odata: { Type: 'Edm.GeometryPolygon', SRID: 0 }
  geoCollection : LargeBinary;
};
```

[Learn more about Overriding OData type mapping.](/docs/guides/protocols/odata#override-type-mapping)

## Node.js ​

### Important Changes ❗ ​

Warning

The following are changes in behavior, which you should take notice of.

- No referential integrity checks by default anymore.
- Non-Singleton `@sap/cds` anymore.
- Mandatory Login in Production.
- Improved Read after Write → triggers READ events which weren't there before.

##### Removed Support for Unofficial APIs ​

The following APIs were never documented or rolled out and therefore should never be used. As we remove those *unofficial* APIs, we give you a heads-up in case you used them anyway.

- Legacy CQN syntax for representation of values for `IN` operator `where: [..., 'IN', { val: [1,2,3] }]` isn't supported anymore → use:
- `where: [..., 'IN', { list: [{val:1},{val:2},{val:3}] }]` instead

- Legacy CQN syntax for aliases within ref: `{ ref: ['column as c'] }` isn't supported anymore → use:
- `{ ref: ['column'], as: 'c' }` instead

- Internal Feature Flags `cds.env.features.implicit_sorting`
- `cds.env.features.auto_fetch_expand_keys`
- `cds.env.features.throw_diff_error`
- `cds.env.features.delay_assert_deep_assoc`
- `cds.env.features.update_managed_properties`
- `cds.env.sql.spaced_columns`
- `cds.env.features.extract_vals`
- `cds.env.features.resolve_views`

- Annotations `@odata.contained` → use `cds.Composition` to use deep payloads instead
- `@odata.on.insert/update` → use `cds.on.insert/update` instead

- Sub-Selects in `@restrict` annotations → use the exists predicate instead
- As documented, `req.tenant` is `undefined` instead of `'anonymous'` for single tenant applications

### Optimized Search on SAP HANA as Default ​

We now translate `$search` requests into the SAP HANA native `contains` function instead of generic `LIKE` expressions whenever possible. In the previous major version, this was hidden behind the feature flag `cds.features.optimized_search`. It still can be disabled by setting the feature flag to `false`.

### Optimized Server Startup Times ​

OData transformation and corresponding checks are no longer applied to the whole model, but only to the relevant services. This reduces server start-up times and avoids OData related error messages for services which are not intended for OData exposure.

### New Rest Adapter as Default ​

The new REST adapter includes a more powerful request parser, that allows using associations and compositions as well. We already shipped this new implementation before, but hidden behind the feature flag `cds.features.rest_new_adapter`. With cds6, it completely replaces the old implementation.

### Added <Entity>.data(...) (experimental) ​

Linked definitions as obtained from `cds.linked()` models now provide proxy wrappers around raw data that provide canonic structured access to elements as defined in corresponding CDS models.

For example, raw data you get from Fiori clients, or from databases frequently contains flattened elements:

js

```
this.on ('UPDATE','Books', req => {
  let {author_ID} = req.data //> author_ID = 111
  // ...
})
this.after ('READ','Books', each => {
  let {author_ID} = each //> author_ID = 111
  // ...
})
```

If you prefer to access these things in their canonical, structured shape you can now do so like this:

js

```
let { Books } = this.entities
this.on ('UPDATE','Books', req => {
  let {author} = Books.data(req.data) //> author = {ID:111}
  // ...
})
this.after ('READ','Books', each => {
  let {author} = Books.data(each) //> author = {ID:111}
  // ...
})
```

Warning

**Note** that this feature is rated ***experimental*** so far.

### Added cds.context.http ​

It's now possible to reliably access the incoming Express.js request and response objects from anywhere within your implementation, if it was initiated by an HTTP request. For other inbound channels like messaging, `cds.context.http` isn't defined.

js

```
const { req, res } = cds.context.http
if (!req.headers.authentication)
  return res.status(403).send('Please login')
```

Previously, it was required to use `req._.req` or `req.context._.req` depending on the invocation context, which was quite fragile.

### Improved cds.tx() ​

When using the [function block variant of `cds.tx()`](/docs/node.js/cds-tx#srv-tx-fn), the new `tx` will be set as global root `tx` for the function body's continuation from now on. All nested service or database operations will be executed within this transaction automatically. In effect, this works now as intuitively expected:

js

```
cds.tx (()=>{
  // following are expected to run within the same transaction
  await INSERT.into (Authors). entries ({...})
  await INSERT.into (Books). entries ({...})
})
```

Before this improvement, this didn't work, but one of these was required:

js

```
cds.tx (tx => {
  cds.context = tx // ensure all subsequent cds.db calls are in this tx
  await INSERT.into (Authors). entries ({...})
  await INSERT.into (Books). entries ({...})
})
```

js

```
cds.tx (tx => {
  await tx.run( INSERT.into (Authors). entries ({...}) )
  await tx.run( INSERT.into (Books). entries ({...}) )
})
```

### Improved req.error() ​

To ease debugging, this release improves `req.error()` to always turn each recorded error in to an instance of `Error` with own stack trace.

For example:

js

```
req.error (`Somethings's wrong with your $data`)
req.error (`Failed to update some related record`)
```

→ These will now be reported with own stack traces, each.

Multiple errors are finally thrown as a wrapping Error object with `.message = 'MULTIPLE_ERRORS'` and `.details = the array of collected errors.

### Non-Singleton @sap/cds ​

With this release `@sap/cds` behaves like a regular Node.js module, so that `require('@sap/cds')` returns different objects for *different* install locations in the same process. Previously, `require('@sap/cds')` would return the *same* object even for different install locations.

While such install scenarios are rather exotic, code might need to be adjusted if you use [`jest.resetModules()`](https://jestjs.io/docs/jest-object#jestresetmodules) to wipe the module cache. You now really get a new `cds` object:

js

```
let cds = require('@sap/cds')
cds.foo = {}
func ()
function func() {
  jest.resetModules()
  cds = require('@sap/cds')
  cds.foo.bar // fails, as cds.foo is not available because `cds` is a fresh object
}
```

The fix is either to cope with the new object or to share the same `cds` variable:

js

```
let cds = require('@sap/cds')
cds.foo = {}
func (cds)
function func(cds) {
  jest.resetModules()
  cds.foo.bar // works because cds is passed on
}
```

### Further Changes ​

- The `file` option for file-based messaging moved from `credentials` to top level
- Remote Services now appended original errors as `reason` instead of `innererror`
- Property `innererror` of OData error responses is now propagated to client
- Boolean keys are properly parsed into JS boolean values

## Java ​

### Important Changes ❗ ​

##### Security by Default ​

The Spring security (auto-)configuration now authenticates all CAP endpoints that are not explicitly annotated with `@restrict` or `@requires`. Note that `cds.security.openUnrestrictedEndpoints = true` will only open endpoints that are explicitly exposed to `any`. To model open endpoints, you can either adapt your model accordingly or reactivate the former behavior with `cds.security.defaultRestrictionLevel = any`.

##### UUIDs in CSV Import ​

Values imported from the CSV files for fields having type UUID and annotated with `@odata.Type: 'Edm.String'` are not longer be normalized.

### Feature Toggles Configuration for Mock Users ​

If mock users are used, a default [FeatureToggleProvider](https://www.javadoc.io/doc/com.sap.cds/cds-services-api/latest/com/sap/cds/services/runtime/FeatureTogglesInfoProvider.html) is registered, which assigns feature toggles to users based on the [mock user configuration](/docs/java/security#mock-users).

#### Configuration per User ​

Feature toggles can be configured directly per mock *user*:

yaml

```
cds:
  security:
    mock:
      users:
        - name: Bob
          tenant: CrazyCars
          features:
            - wobble
        - name: Alice
          tenant: SmartCars
          features:
            - cruise
            - parking
```

For mock user `Bob` the feature `wobble` is enabled while for `Alice` the features `cruise` and `parking` are enabled.

#### Configuration per Tenant ​

Alternatively, feature toggles can be configured on mock *tenant* level:

yaml

```
cds:
  security:
    mock:
      users:
        - name: Bob
          tenant: CrazyCars
        - name: Alice
          tenant: SmartCars
      tenants:
        - name CrazyCars
          features:
            - wobble
        - name: SmartCars
          features:
            - cruise
            - parking
```

For the mock tenant `CrazyCars` the feature `wobble` is enabled while for tenant `SmartCars` the features `cruise` and `parking` are enabled.

### Create Active Version of Draft-Enabled Entity ​

OData V2 now also supports [directly creating active versions](/docs/java/fiori-drafts#bypassing-draft-flow) of draft-enabled entities through POST by passing `{"IsActiveEntity": true}` in the payload. In OData V4 this was already possible.

### Protocol Configuration ​

Use the new annotation `@protocol` as alias for `@protocols` to [configure](/docs/java/cqn-services/application-services#configure-path-and-protocol) by which protocol a service is served. Both annotations allow single and arrayed values. You can use `@protocol: 'none'` to completely disable serving a service.

### Auto-Build ​

The `cds-maven-plugin` is enhanced with new goal `auto-build`, which eases use of Spring Developer Tools. Once started, it reacts to changes in the CDS model and starts CDS builds automatically. In contrast to the `watch` goal it does not start the Java application and hence is suitable to enable development with IDEs.

## Tools ​

### Important Changes ❗️ ​

- Note the changes in the `cds build` area as they may affect the behaviour of your application in production environment
- `cds deploy --to hana` now stores connection information without credentials. This is the same behavior as cds bind and replaces the unsafe local default-env.json file which contained credentials in clear text. If you still need the old behavior, you can add the option `--store-credentials`.

### New CDS Lint Rules for Authorization ​

A series of new lint rules (with names `auth-*`) has been added to ensure that restrictions on CDS models enforce proper access control. Any models containing the `@restrict` / `@requires` annotations are now checked to catch empty restrictions, misspelled privileges, redundant events, and so on.

### Changes to cds build ​

#### Improved Initial Data Handling for SAP HANA Deployments ​

CSV files containing initial data are now found in *reuse modules* as well, which is the same bahavior as with SQLite. More specifically, they can be located in any *csv* or *data* subfolder, including *db/data* and *db/csv*, for which a CDS model file of your application exists. Previously, csv files would need to be manually copied from the reuse module into the application's deployment folder.

Use the following option to return to the former behaviour:

json

```
{ "for": "hana", "options": { "csvFileDetection": false } }
```

[Learn more about providing initial data.](/docs/guides/databases/initial-data)

#### More Configuration Files Available in Production ​

The files *.cdsrc.json*, *.npmrc* located in *root*, *srv* or *db* folders of your project are now copied into the deployment folder (usually *gen/srv*, *gen/db*) by default. Files including *package.json*, *package-lock.json* located in the *srv* folder have precedence over the corresponding files located in the project root directory. As these files are used in production environment, make sure that the folders do not contain one of these files by mistake. Consider using profiles `development` or `production` in order to distinguish environments. CDS configuration that should be kept locally can be defined in a file *.cdsrc-private.json*.

For security reasons the files *default-env.json* and *.env* are no longer copied into the deployment folder.

The contents of the *node_modules* folder is no longer copied into the deployment folder.

[Learn more about cds build configuration](/docs/guides/deploy/build)

#### New CDS Build Task Aliases ​

The new build task names `nodejs` and `java` should be used instead of the deprecated aliases `node-cf` and `java-cf`, which are still supported for compatibility reasons.

#### Cloud Foundry Manifest Files No Longer Auto-Generated ​

Manifest files for the *srv* and *db* modules are no longer created as default by `cds build`. If you prefer `cf push`-based deployment in contrast to MTA-based deployment, you can create *manifest.yml* and *services-manifest.yml* using the command `cds add cf-manifest`. Add them to your Git repo as regular source files.

[Learn more about Cloud Foundry native deployment.](/docs/guides/deploy/to-cf)

[Learn more about MTA deployment.](/docs/guides/deploy/to-cf#add-mta-yaml)
