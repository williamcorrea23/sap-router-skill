<!-- mirror: https://cap.cloud.sap/docs/releases/2021/oct21 -->
<!-- fetched: 2026-05-09T02:26:28.949Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# October 2021 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtx?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Best Practices for Testing ​

We provide best practices and recommendations for testing [in Node.js](/docs/node.js/cds-test#best-practices) and [in Java](/docs/java/developing-applications/testing#testing-cap-java-applications).

With the [cds.test](/docs/node.js/cds-test) toolkit, you can now easily write tests for your CAP Node.js application:

js

```
const {GET, expect} = cds.test('@capire/bookshop') // starts the server
const {data} = await GET `/browse/Books` // sends a request
expect (data.value).to.eql(...) // checks the response
```

## Consuming Services General Available ​

Consuming OData V2 and V4 services from CAP applications is now general available.

### Consuming OData V2 Services in Node.js ​

You can consume OData V2 services with Node.js, by setting `kind` to `odata-v2`.

*package.json:*

json

```
"cds": {
    "requires": {
        "API_BUSINESS_PARTNER": {
            "kind": "odata-v2",
            "model": "srv/external/API_BUSINESS_PARTNER",
            "credentials": {
                /* ... */
            }
        }
    }
}
```

Tip

The `cds import` command [automatically adds a section](/docs/guides/integration/calesi#importing-apis) with the right value.

### Import External Service Definitions as CDL ​

You can [import external service definitions as CDL file](/docs/guides/integration/calesi#importing-apis) (**.cds*) for better readability.

sh

```
cds import ~/Downloads/API_BUSINESS_PARTNER.edmx --keep-namespace --as cds
```

This new option will become the default in a future release.

### Notable Changes From the Beta Version ​

- With the new version of `cds import`, associations are declared without keys explicitly to solve runtime issues.

## Command Line & Tools ​

### Linting CDS Models ​

[CDS Lint](/docs/tools/cds-lint/) helps you to catch issues in your CDS models early. It is built on top of the standard ESLint framework and integrates with many popular IDEs.

With this release, we provide an initial set of rules. In future releases, we will add more rules and provide APIs, that help you to write your own rules.

### Improved Support for Doc Comments ​

The editor now automatically adds end marker and when line breaking starts the new line with a `*` vertically aligned.

### CDS Editors Speedup: Additional Options ​

The following applies to CDS editors in SAP Business Application Studio and Visual Studio Code.

- We improved the calculation of workspace symbols. Give it a try.
- The translation support was optimized with regards to indexing and revalidation.
- The workspace scanning for CSN files has changed. The user setting `cds.workspace.scanCsn` has now three options:OptionsDescription`Off`CSN files won't be scanned.`ByFileExtension`Default. Only CSN files with file extensions .csn or .csn.json will be scanned.`InspectJson`Additionally all .json files will be inspected if they contain CSN.With the new default, most CSN files are included in a fast way in workspace symbols.

### Merged @sap/cds-sidecar-client Package ​

We merged the former package `@sap/cds-sidecar-client` into `@sap/cds-dk`.

As `@sap/cds-sidecar-client` was always an internal package, this should not affect you. Yet, if, for any reason, you had `@sap/cds-sidecar-client` in your list of dependencies, you should remove it.

## Node.js Runtime ​

### Important Changes ❗️ ​

- In Improved Transaction Handling we had to make two changes that may affect your project → see the warning below.
- We Cleaned up `cds.ql` including a few undocumented API variants.
- The data returned by custom handlers now has precedence over the values in the database, which are - as required by the OData specification - retrieved in the OData protocol adapter after a write operation. This allows to control exactly which data gets returned to the client.

### Improved srv.tx() ​

Transaction handling was thoroughly cleaned up and improved in this release, and at last also documented end-to-end in [Node.js > srv.tx — Transactions](/docs/node.js/cds-tx).

[](/docs/node.js/cds-tx)

To highlight only a few fixes and additions you should take notice of:

- Method `srv.tx()` now allows specifying tenants and users as plain strings:
- Method `srv.tx()` now allows running functions in managed transactions:
- New method `cds.spawn()` guarantees properly isolated background jobs:
- Properties `cds.User.tenant` and `cds.User.locale` are deprecated.
- Fully Managed Transactions → method `srv.tx(req)` is deprecated.
- Automatic Context Propagation: calling `srv.tx({...})` now inherits from `cds.context` by default. This shortcuts the 99% cases.
- Protection against dangling connections: calling `tx.commit` or `tx.rollback` now disallows subsequent queries by default. Before, any accidential subsequent query began a new transaction, but this time without automatic `commit`/`rollback`. This in turn lead to hard-to-detect dangling connections, drained connection pools, and servers not responding anymore.

Warning

The last two fixes changed existing behavior, yet is very unlikely to affect your project. Nevertheless if it does, you can restore the former (rather erroneous) behavior by setting `cds.env.features.cds_tx_inheritance = false` or `cds.env.features.cds_tx_protection = false` respectively.

### Cleaned up cds.ql ​

After merging the runtime packages in the [July Release](./july21#changes-in-node-js), we merged various sources of the QL implementation and, in the process, removed the following *unofficial* variants:

- Unofficial variant `SELECT({'expand(foo)':['a','b']})` is not supported anymore → use one of these official APIs for expands instead:js

```
SELECT(x => { x.a, x.foo (f =>{ f.b, f.c }) })
SELECT(['a',{ref:['foo'], expand:['b','c']}])
```
- Unofficial variant `SELECT.orderBy('foo','desc')` is not supported anymore → use one of these official APIs instead:js

```
SELECT.from(Foo).orderBy({foo:'desc'})
SELECT.from(Foo).orderBy('foo desc')
```
- Unofficial variant `SELECT.orderBy('foo, bar desc')` is not supported anymore → use one of these official APIs instead:js

```
SELECT.from(Foo).orderBy({foo:1,bar:-1})
SELECT.from(Foo).orderBy('foo','bar desc')
SELECT.from(Foo).orderBy `foo, bar desc`
```
- Unofficial variant `SELECT.where({ or: [{ foo: 'bar' }, { foo: 'baz' }] })` is not supported anymore → use one of these official APIs instead:js

```
SELECT.from(Foo).where({ foo: 'bar', or: { foo: 'baz' } })
SELECT.from(Foo).where `foo='bar' or foo='baz'`
```

Further, the following bugs were fixed:

- `INSERT.rows()` does not silently fill in `INSERT.entries` anymore → use `INSERT.entries()` to do so instead.Note: `INSERT.rows()` is meant for bulk operations that do not require generic functionality, such as, for example, managed data.

- `UPDATE(Foo).with({foo:{'=':'bar'})` erroneously produced:js

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
- `UPDATE.with` property stays undefined until actually filled with data.

### CORS Out of the Box ​

If not in production, the default server is now CORS-enabled for all origins. This shall ease development with multiple apps, especially when a different app is serving the UI static content.

### Additions to Generic Providers ​

- Annotation `@Capabilities.ExpandRestrictions.NonExpandableProperties` allows to specify which navigation properties may not be expanded, in order to, for example, limit expensive queries.
- Default values for virtual fields are now supported.
- Singletons can be made deletable with annotation `@odata.singleton.nullable` (in contrast to `@odata.singleton`).
- Support for reading streams implicitly via `GET /()/$value`.

## Java SDK ​

### Important Changes ❗️ ​

- The methods `Message#target(String, String, Function)` and `ServiceException#messageTarget(String, String, Function)` are now deprecated in favor of the new `Message` and `ServiceException` API.
- When switching to privileged user with `RequestContextRunner#privilegedUser()`, not only the tenant, but also additional user attributes from the current user are propagated, which contain more detailed tenant information.

### Improvements in cds.ql ​

- Bulk updates now support deep and heterogeneous (flat and deep) update data.
- The any/allMatch predicate is now also supported in update and delete statements.
- The to-one expand optimization now also works for expand all and nested to-one expands. If all conditions are met, select statements with to-one expands are executed in a single query using joins.
- The max batch size for JDBC batch update can now be configured via `cds.sql.max-batch-size`.
- `byParams` simplifies filtering by parameters as an alternative to `where` and `CQL.param`:java

```
import static bookshop.Bookshop_.BOOKS;
// using where
Select.from(BOOKS)
    .where(b -> b.title().eq(param("title"))
           .and(b.author().name().eq(param("author.name"))));

// using byParams
Select.from(BOOKS).byParams("title", "author.name");
```

### Observability ​

Ensuring compatibility with [cf-java-logging-support](https://github.com/SAP/cf-java-logging-support) in respect to handling [correlation ids](/docs/java/operating-applications/observability#correlation-ids) for application logging.

### Maven Plugin version Goal ​

The `cds-maven-plugin` provides the new goal `version`, which prints detailed version information about a CAP Java project on the console.

### Testing with JSON Comparison ​

For easier comparison of JSON, we added the `getRef()` method to the `MessageTarget` interface. The new method `getRef()` returns a `CqnReference` which provides `toJson()` to return it as a `Json` string.

Example:

java

```
MessageTarget expectedTarget;
MessageTarget actualTarget;

// ...

assertEquals(expectedTarget.getRef().toJson(), actualTarget.getRef().toJson());
```

### Validator Processing Modes Beta ​

The `CdsDataProcessor` [validator](/docs/java/cds-data#data-validators) now comes with different processing modes. This allows to register validators that check for missing values.

## Multitenancy ​

### Handlers for Asynchronous Upgrade ​

To enhance your application with custom code for the upgrade of a tenant (see also [Tenant Upgrade API](/docs/guides/multitenancy/old-mtx-apis)), you can add handlers for the upgrade API that is called by `cds-mtx`. This API is called for the synchronous as well as for the asynchronous upgrade for each tenant.

The following API is called by `cds-mtx`:

cds

```
@protocol:'rest'
service TenantPersistenceService {
    type JSON {
        // any json
    }

    action upgradeTenant(tenantId: UUID, instanceData: JSON, deploymentOptions: JSON) returns JSON;
}
```

Note that this API is not meant to be called by applications but has been introduced to allow applications to create handlers for custom logic to be executed with the tenant upgrade.

[Learn more about the handler for tenant upgrade.](/docs/guides/multitenancy/old-mtx-apis#event-handlers-for-cds-mtx-upgrade)

### Extension Reset API ​

The API allows to remove all extensions for a tenant:

http

```
POST /mtx/v1/model/reset
```

Request body (example):

json

```
{
    "tenant": "tenant-extended"
}
```
