<!-- mirror: https://cap.cloud.sap/docs/releases/2020/nov20 -->
<!-- fetched: 2026-05-09T02:26:23.361Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# November 2020 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtx?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

### Revamped cap/samples ​

Our **[cap/samples](https://github.com/sap-samples/cloud-cap-samples)** received another cleanup and overhaul. Things added include:

- Authorization enabled by default now, also showcased in @capire/reviews
- Additional Fiori app in @capire/orders (moved there from @capire/fiori)
- Additional Vue.js apps in @capire/orders and @capire/reviews
- Messaging between @capire/bookshop, @capire/orders, and @capire/reviews
- Reuse & Compose / mashups showcased in @capire/fiori

[Learn more in the new Reuse & Compose guide](/docs/guides/integration/reuse-and-compose)

### New and Revised Guides ​

- The guide Domain Modeling with CDS received a major overhaul with several additions, also about things added in latest releases. → worthwhile a revisit, in particular the sections about aspects, which were missing before.
- New guide Providing & Consuming Services has been created from merged, revised, and complemented content of the former separate guides on Providing Services and Consuming Services.
- The guide Using Generic Providers was taken out from the former Providing Services guide and promoted to a top-level cookbook guide.
- New guide Reuse & Compose introduces how to compose enhanced, verticalized solutions by reusing content from other projects, and adapt it to your needs by adding extensions or projections.
- The guide on Managing Dependencies moved from the Getting Started sections to Node.js Best Practices.

### Provide Feedback for the Documentation ​

You can now provide feedback or report issues regarding the documentation directly from capire. Just click on the envelope icon on the right-hand side and follow the link to SAP Q&A. Give us as much information as possible in the pre-filled SAP Q&A form to enable better processing of your feedback.

## Command Line / Toolkit ​

### Export to OpenAPI ​

You can now convert CDS models to the [OpenAPI Specification](https://www.openapis.org), a widely adopted API description standard. For example, this is how you convert all services in `srv/` and store the API files in the `docs/` folder:

sh

```
cds compile srv --service all -o docs --to openapi
```

[Learn more about the export to OpenAPI.](/docs/guides/protocols/openapi)

### CAP Jupyter Notebooks ​

You can now add a **CAP Jupyter Notebook** to your CAP project.

A **CAP Jupyter Notebook** is a [Jupyter Notebook](https://jupyter.org) that serves as a guide on how to create, navigate and monitor CAP projects.

With this, we want to encourage the CAP community to work with CAP in the same explorative manner that scientists work with their data by:

- Visually interacting with their code
- Playing with REPL-type inputs (notebook input cells)
- Storing persistent code (notebook output cells)

The cell inputs/outputs are especially useful at later points in time when the project's details have long been forgotten. In addition, notebooks are a good way to share, compare and also reproduce projects.

*Opening and interacting with a **CAP Jupyter Notebook** in Visual Studio Code*

### Start with Different Ports on Node.js ​

By default, Node.js apps started with `cds run` or `cds watch` use port 4004, which might be occupied if other app instances are still running. In this case, `cds watch` now asks you if it should pick a different port.

```
$ cds watch
...
[cds] - serving CatalogService ...

EADDRINUSE - port 4004 is already in use. Restart with new port? (Y/n)
> y
restart
...
[cds] - server listening on { url: 'http://localhost:4005' }

```

Ports can be explicitly set with the `PORT` environment variable or the `--port` argument. See `cds help run` for more.

## CDS Editors & Tools ​

The following features are available for all editors based on our language server implementation for CDS in SAP Business Application Studio, Visual Studio Code, and Eclipse. The plugins are available for download for Visual Studio Code at [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=SAPSE.vscode-cds#overview) and for Eclipse at [https://tools.hana.ondemand.com](https://tools.hana.ondemand.com/#cloud-vscodecds).

### Native Submenus (Visual Studio Code only) ​

With VS Code 1.50, the editor supports native submenus. The CDS preview commands can now be accessed directly in the editor for an open CDS file.

In SAP Business Application Studio you can access the submenu entries by using menu `View` / `Find Command...` and then type `cds preview` to narrow the search to the applicable commands.

### Quickfixes for Deprecated Identifiers ​

Compiler warnings for deprecated identifiers wrapped in double quotes now show a quickfix to convert those into the modern form wrapped in `![...]`.

### Framework Support for Quickfixes in Annotation Handler ​

Annotation handler can now contribute quickfixes.

## Node.js Runtime ​

### Important Changes ❗️ ​

- CREATE and UPDATE requests that aren't allowed due to `@restrict.where` are rejected with `403` instead of `404`
- Internal `req.run()` is deprecated and will be removed. Use `cds.db.tx(req).run()` instead.
- Internal `req._model` is deprecated and will be removed. Use `tx.model` instead.
- Internal `req.statements` was removed. Use `cds.ql` instead.

 The following features, marked with *Experimental:* are brand new, more comprehensive documentation will follow:

### Experimental: cds.context Beta ​

- `cds.context` always allows access to the current request context when running in Node v12.18 and higher. It uses Node.js' `async_hooks` API for so-called continuation-local storage, and supercedes the need for `srv.tx(req)` in custom handlers (can be used with Node.js 12.18 or later).

### Experimental: cds.log Beta ​

- `cds.log` is a minimalistic logging framework, by default using `console`, which we'll use in all parts of CAP runtime, and which allows to plug in other logging framework like Winston, Bunyan, Morgan or other.

### Experimental: Convenience API on cds.Service ​

For actions and functions (unbound and bound), a convenience function is added to the respective instance of `cds.Service` / `cds.Service` subclass (if the name doesn't clash).

For example, if you have a remote service with an unbound action `cancelOrder(ID: UUID)`, you can invoke it like this:

js

```
const remote = await cds.connect.to('remote')
await remote.cancelOrder('')
```

Note The implementation has to take care of returning the correct response format, for example, an integer, an array of a type, etc.

### Tracing Database Statements with Dynatrace ​

The Node.js runtime supports tracing database statements with Dynatrace (n/a for SQLite).

### Custom Aggregates in OData ​

[Custom aggregates](/docs/guides/protocols/odata#custom-aggregates) can be used in `$apply`.

### Correlation ID Header Are Propagated to Subrequests ​

If an incoming HTTP request has header `x-correlation-id`, all resulting subrequests provide access to the ID via `req.headers['x-correlation-id']`.

### Miscellaneous ​

- New helper function `cds.utils.uuid()` to generate UUIDs
- Service consumption: Cloud SDK logs are only printed in debug mode
- Draft: Lock active entity on edit action to prevent duplicate drafts

## Java SDK ​

### Important Changes ❗️ ​

The OData comparison operators `eq` and `ne` are now mapped to the CQL [comparison operators](/docs/java/working-with-cql/query-api#comparison-operators) `CqnComparisonPredicate.IS` and `IS_NOT`, respectively, providing two-valued comparison semantics. If a query is [introspected](/docs/java/working-with-cql/query-introspection) with the `CqnAnalyzer`, this change is automatically taken into account.

### OData V2 (RC1) ​

The [OData V2 adapter](/docs/java/migration#v2adapter) is now available as a first release candidate. Features that were added in this version are:

- You're now able to return messages that are shown in Fiori UIs by means of the CDS Messages interface as already available for OData V4, see Indicating Errors for more details.
- You can now use actions, so called "Service Operations", with complex return types.

### OData V4 Analytics ​

We made large progress with adding more analytics features for OData V4:

- OData V4 $apply now supports the transformations skip, top, and orderby.
- OData V4 $apply now supports the transformation concat (not to be combined with other system query options).
- OData V4 $apply now supports custom aggregates with aggregation methods declared by `@Aggregation.default`.

### Logging and Tracing ​

The CAP Java SDK now logs single queries contained in an OData batch request separately. This feature enables fine-grained debugging but could cause increased log output. Therefore, you can disable this feature by setting the log level to "Warning" on the following log components:

yaml

```
com.sap.cds.adapter.odata.v2.BatchAccess=WARN
com.sap.cds.adapter.odata.v4.BatchAccess=WARN
```

### Datasource and Environment Configuration ​

You can now configure the connection pools of datasources, which are auto-configured by CAP Java SDK based for bound services using the following property in *application.yaml*:

yaml

```
cds.dataSource..hikari.=...
```

In addition, you can configure a dedicated *default-env.json* file for each Spring profile with:

yaml

```
cds.environment.local.defaultEnvPath=...
```

This enables using different service bindings / credentials for services for each Spring profile.

### Multitenancy: Fast Unsubscribe and Resubscribe ​

It's now possible to unsubscribe a tenant and resubscribe without delay. This feature enables stress testing of your tenant subscription logic.

### CDS.ql ​

- The comparison operators `IS` and `IS NOT` now allow to compare any two values for [in]equality. NULL values are treated as any other value in the comparison, in contrast to the `EQ` and `NE` operators, where NULL values might be treated as unknown depending on the underlying datastore. Corresponding builder methods `is(Value other)` and `isNot(Value other)` are added to the Value interface.
- Initial support for arrayed elements with simple and structured types.

### Bug Fixes ​

- Projection Resolvement: Support aliased elements in infix filters and filtered updates
- Fix `isPredicate` and `asPredicate` methods of `CqnPredicate`
- Fix using `isNull` on elements of associated entities
