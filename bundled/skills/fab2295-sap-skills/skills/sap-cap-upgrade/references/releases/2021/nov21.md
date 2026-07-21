<!-- mirror: https://cap.cloud.sap/docs/releases/2021/nov21 -->
<!-- fetched: 2026-05-09T02:26:28.365Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# November 2021 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtx?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Events & Messaging General Available ​

We finalized our messaging implementations now and can hereby declare first general availability. In course of this, we also documented key concepts and usage scenarios in the new comprehensive [Events & Messaging Cookbook Guide](/docs/guides/events/):

[](/docs/guides/events/)

## Schema Evolution General Available ​

[Schema Evolution on SAP HANA Cloud](/docs/guides/databases/hana#schema-evolution-native-db-clauses) is finally released for productive usage now.

CAP supports schema evolution based on [migration tables](https://help.sap.com/docs/HANA_CLOUD_DATABASE/c2cc2e43458d4abda6788049c58143dc/52d1f5acfa754a7887e21226641eb261.html) for the SAP HANA database. Compatible changes including column rename can be applied to the database without any data loss and without the cost of an internal table-copy operation.

## Hybrid Tests with cds bind ​

With [hybrid testing](/docs/tools/cds-bind), you stay in your local development environment and use services from the cloud. With the new `cds bind`, you connect your CAP Node.js application to Cloud Foundry services. The `cds watch` gets the service credentials from Cloud Foundry and keeps it until exit. There is no need to save service credentials on your hard drive anymore.

[](/docs/tools/cds-bind)

## Exists Predicates in CQL Beta ​

This release adds thorough support for `exists` predicates with path expressions, to CDS compiler, as well as Node.js and Java runtimes. Exists path predicates allow to express complex relationships while hiding the complexity of nested subselects. For example:

sql

```
SELECT FROM Authors WHERE exists books.pages[wordcount > 1000]
```

[Learn more about the Exists Predicates in CQL.](/docs/cds/cql#exists-predicate)

Exists predicates can also be nested; for example, the above is equivalent to this:

sql

```
SELECT FROM Authors WHERE exists books [
  where exists pages [
    where wordcount > 1000
  ]
]
```

### Support in CDS Compiler ​

The CDS compiler translates this into plain SQL like that:

sql

```
SELECT FROM sap_capire_bookshop_Authors a
WHERE EXISTS (
  SELECT 1 from sap_capire_bookshop_Books b
  WHERE b.author_ID = a.ID and EXISTS (
    SELECT 1 from sap_capire_bookshop_BookPages p
    WHERE p.book_ID = b.ID
  )
)
```

### Support in Runtimes ​

Node.js and Java Runtimes care for the same, especially when enforcing instance-based access control:

cds

```
@restrict: [{ grant: 'READ',
  where: 'exists teams.members [userId = $user and role = `Editor`]'
}]
entity Projects {
  // ...
  teams : Association to many Teams;
}
```

[Learn more about Exists Predicate in the Authorization guide.](/docs/guides/security/authorization#exists-predicate)

In the example, only those users may read projects' data which are associated members with role *Editor*.

Warning

**Status: Experimental** --- Consider status of this features as experimental, which means behaviors might change in details. Always ensure functional correctness for your project when making changes with regards to authorization! Support for draft-enabled entities may be limited.

## Java Runtime ​

### Important Changes ❗️ ​

- The `CdsModelProvider` is now also triggered when using `CdsRuntime.getCdsModel(UserInfo, FeatureTogglesInfo)` with a `UserInfo` object, where the tenant is set to `null`. Earlier, the method always returned the default CDS model directly.
- CQL API cleanup GROUP BY - groups are now represented as a `List`
- ORDER BY - the sort item is now represented as a `CqnValue`
- `CqnLimit` - Using the CQL tree node `CqnLimit` is deprecated in favor of the new `Select.top()` and -`.skip()` methods.
- Some legacy methods are deprecated in favor of cleaner substitutes. Check the build log for deprecation warnings.

### Observability ​

Most features described in the [Java Observability guide](/docs/java/operating-applications/observability) are now demonstrated in the [Java Bookshop sample](https://github.com/SAP-samples/cloud-cap-samples-java).

### Error Messages ​

Built-in handlers, for example for `@assert.range` validation, now set the corresponding target in error messages. This ensures that error messages in SAP Fiori are shown directly at the relevant field, instead of in a generic popup.

### Remote OData ​

- It's now possible to build a destination for a Remote Service declaratively in the configuration. All destination properties supported by SAP Cloud SDK can be used under the new section `cds.remote.services..destination.properties`. For a full list of supported destination properties, look at SAP Cloud SDK's `com.sap.cloud.sdk.cloudplatform.connectivity.DestinationProperty` class.
- New configuration options `cds.remote.services..destination.headers` and `cds.remote.services..destination.queries` have been added and allow to configure key-value pairs of headers / queries to be added to every outgoing request of the Remote Service.

### anyMatch/allMatch Predicates ​

The [anyMatch/allMatch predicates](/docs/java/working-with-cql/query-api#any-match) can now be applied to paths with multiple segments:

java

```
Select.from(BOOKS)
     .where(b -> b.author().books().anyMatch(b -> b.title().eq("Capire")));
```

### Path Access to Data ​

The `Row`'s `get` method now supports paths, to simplify extracting values from nested maps:

java

```
CqnSelect select = Select.from(BOOKS).columns(
     b -> b.title(), b -> b.author().expand()).byId(101);
Row book = dataStore.execute(select).single();

Object author = book.get("author.name"); // path access
```

### Enhanced QL Support for Parameters ​

`byParams` is now also supported for `Update` and `Delete` statements, simplifying filtering by parameters as an alternative to `where` and `CQL.param`:

java

```
// using where
Delete.from(BOOKS)
  .where(b -> b.title().eq(param("title"))
         .and(b.author().name().eq(param("author.name"))));

// using byParams
Delete.from(BOOKS).byParams("title", "author.name");
```

### Enhanced QL Support for ORDER BY ​

Use the new `CQL.sort` method to create a sort specification in tree style:

java

```
CqnElementRef authorName = CQL.get("author.name");
CqnSortSpecification sort = CQL.sort(authorName, CqnSortSpecification.Order.ASC);
CqnSelect query = Select.from("bookshop.Books").orderBy(authorName);
```

Modify an existing sort specification using `Modifier.sort`:

java

```
CqnSelect sel = Select.from("Book").orderBy("title");

CqnSelect modified = copy(sel, new Modifier() {
    @Override
    public CqnSortSpecification sort(Value value, Order order) {
        return value.desc();
    }
});
```

### Simplified Representation of top/skip ​

Use the `top()` and `skip()` methods to get the values of `top` and `skip` of `Select` statements and expands:

java

```
CqnSelect query = Select.from(BOOKS).orderBy(b -> b.ID()).limit(10, 50);
assertThat(query.top()).isEqualTo(10);
assertThat(query.skip()).isEqualTo(50);
```

## Node.js Runtime ​

### Important Changes ❗️ ​

- `@sap/xsenv` is no longer used for credentials look-up and can be removed from projects.
- `cds.ql`: Keys passed as arguments into SELECT.from() are put into the target path (`SELECT.from.ref`) instead of adding a where expression at root level. This change is necessary in order to distinguish between resource paths and filters/ restrictions.js

```
SELECT.from('Books', 1)
```

Result now:js

```
SELECT: {
  from: {
    ref: [{
      id: 'Books',
      where: [{ ref: ['ID'] }, '=', { val: 1 }]
    }]
  },
  one: true
}
```

Result previously:js

```
SELECT: {
  from: { ref: ['Books'] },
  where: [{ ref: ['ID'] }, '=', { val: 1 }] },
  one: true
}
```

The change can be deactivated during two-month grace period via compatibility feature flag `cds.env.features.keys_into_where = true`.

### Service Consumption ​

There are two new configuration options for remote services:

- SAP Cloud SDK's destination options destination options can be passed via configuration `destinationOptions`. See Use Destinations with Node.js for more details. This enables you to configure if destinations should be loaded from provider or subscriber accounts of a multitenant application using destination options.
- With `forwardAuthToken`, the incoming JWT is forwarded to the remote service (instead of the standard token switch). See Forward Authorization Token with Node.js for more details.

Further, `GET` requests to Remote OData Services are automatically sent as `$batch` if the generated URL is too long.

[Learn more in the enhanced Consuming Services Cookbook.]((/guides/services/consuming-services)

### Project-Specific Configuration ​

- You can put your local and private project settings in a .cdsrc-private.json file in your project directory.
- The `CDS_CONFIG` environment variable allows to load configuration from JSON files and from the file system now.

### New REST Adapter Beta ​

The November release includes the beta version of the new REST adapter.

The new implementation uses the CAP-native OData URL to CQN parser. Hence, almost all OData requests are supported. For example, you can use query options like `$filter` and `$expand`, request deep resources such as `GET /Foo/1/bars/2/baz`, as well as (un)bound actions and functions.

Limitations/ out of scope (compared to OData protocol adapter):

- OData query option `$apply`
- OData batch requests (`/$batch`; with or without atomicity groups)
- Draft handling

The new REST adapter can be activated via `cds.env.features.rest_new_adapter = true`. Don't forget that you need to serve to `rest`, either via the `cds.serve()` API or the `@protocol` annotation.

## GraphQL Adapter for Node.js (experimental) ​

The November release includes a first experimental implementation of a generic [GraphQL](https://graphql.org/) adapter, which turns each CAP service into a GraphQL server.

The GraphQL adapter can be activated by setting config option:

- `cds.env.features.graphql = true`

Further, you need to install the following additional dependencies:

- `@graphql-tools/schema`
- `express-graphql`
- `graphql`

The adapter serves a single endpoint for all services based on the `served` event at `/graphql`. At that path, you'll find a generated UI (via third party library) that allows you to interact with your application.

Follow these steps to run [@capire/bookshop](https://github.com/SAP-samples/cloud-cap-samples) with `graphql`:

- `npm add graphql express-graphql @graphql-tools/schema`
- `cds_features_graphql=true cds watch bookshop`
- Open GraphiQL client at http://localhost:4004/graphql.
- Browse schema and enter queries in the GraphiQL client.

For example, you can execute queries like the following:

graphql

```
{
  CatalogService {
    Books {
      ID
      title
      genre {
        name
      }
    }
  }
}
```

The equivalent query in OData:

http

```
GET /browse/Books?$select=ID,title&$expand=genre($select=name)
```

Various limitations apply. For example, authentication and authorization are out of scope, and annotations aren't considered during schema generation.

Warning

Note that the GraphQL adapter isn't supported for productive usage!
