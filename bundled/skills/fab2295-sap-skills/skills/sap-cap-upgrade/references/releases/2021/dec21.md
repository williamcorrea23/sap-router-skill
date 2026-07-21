<!-- mirror: https://cap.cloud.sap/docs/releases/2021/dec21 -->
<!-- fetched: 2026-05-09T02:26:25.552Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# December 2021 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtx?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Exists Predicates in CQL ​

This release adds thorough support for `exists` predicates with path expressions, to CDS compiler, as well as Node.js and Java runtimes. Exists path predicates allow to express complex relationships while hiding the complexity of nested subselects. For example:

sql

```
SELECT FROM Authors WHERE exists books.pages[wordcount > 1000]
```

[Learn more about the Exists Predicates in CQL.](/docs/cds/cql#exists-predicate)

Exists predicates can also be nested. The previous example is equivalent to:

sql

```
SELECT FROM Authors WHERE exists books [
  where exists pages [
    where wordcount > 1000
  ]
]
```

Warning

Paths *inside* infix filters aren't yet supported.

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

The `EXISTS` predicate is also supported by the CAP Node.js and CAP Java runtimes. In CAP Java `EXISTS` is expressed by the [`anyMatch` predicate](/docs/java/working-with-cql/query-api#any-match). In an OData request a [Lambda Operator](https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part2-url-conventions.html#_Toc31361024) is used.

### Instance-based Authorization ​

The `EXISTS` predicate is especially useful when enforcing instance-based access control:

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

In the example, only those users may read projects' data, which are associated members with role *Editor*.

## Persistent Outbox Beta ​

The persistent outbox combines asynchronism with resilience. It allows to defer the emit of messages until the success of the current transaction, to avoid that recipients falsely receive messages in case of a rollback.

In addition, the persistent outbox safely stores the messages in the used persistence, so that they are not lost in case an application crashes. The deferred emits will then be done asynchronously. In case the emit is currently not possible, for example because of a temporary unavailability of the targeted service, it will be retried with an exponentially growing waiting time.

Currently, the persistent outbox can be enabled to be used with messaging and audit logging services.

See [Java - Persistent Outbox](/docs/java/outbox#persistent) or [Node.js - Persistent Outbox](/docs/node.js/queue#persistent-queue) for more details.

## Resilient Audit Logging via Outbox Beta ​

The out-of-the-box audit logging makes use of the new persistent outbox, if enabled. See [Persistent Outbox](#persistent-outbox) for more details. That is, logs that shall be sent to the audit log sink are first written into the persistent outbox, which is transactionally safe, and only sent to the audit log sink once the original transaction was committed. This ensures that there are no "ghost" logs (for example, modifications that eventually were not committed) or lost logs (for example, modifications that were committed but not logged because there was an issue in between).

## Declarative Audit Logging in Java ​

Audit logs of type "Personal data access" and "Personal data modification" are now automatically created in case the model is annotated with `@PersonalData` and `@AuditLog` as described in section [Audit Logging](/docs/guides/security/dpp-audit-logging):

cds

```
annotate Authors with
@PersonalData : { EntitySemantics : 'DataSubject'}
@AuditLog.Operation : { Read : true, Update : true }
{
  ID @PersonalData.FieldSemantics : 'DataSubjectID';
  name @PersonalData.IsPotentiallyPersonal;
}
```

In the example, modifying the field `Authors.name` generates a log event of type `DataModificationLog`.

For more information, see the respective section for [Java](/docs/java/auditlog).

## Database Constraints Beta ​

CDS can now automatically generate database constraints for managed to-one Associations and Compositions:

cds

```
entity Books {
  ...
  author : Association to Authors;
}
entity Authors {
  key ID : Integer;
  ...
}
```

Association `author` triggers the generation of a constraint:

sql

```
CONSTRAINT Books_author ON Books
  FOREIGN KEY(author_ID) REFERENCES Authors(ID)
  ON UPDATE RESTRICT
  ON DELETE RESTRICT
  VALIDATED
  ENFORCED
  INITIALLY DEFERRED
```

Database constraints are available for SQL dialects `hana` and `sqlite`.

Switch them on with the configuration `cds.env.features.assert_integrity` that can have the values

- `'db'`: Database constraints
- `'app'`: Runtime checks (default, only effective in Node.js runtime)
- `false`: No database constraints and no runtime checks

The Node.js runtime features integrity checks in the application. We intend to replace these rather expensive checks in the application by database constraints with the next major release in 2022. For the migration period until then you can choose what kind of integrity checks are performed.

Generation of database constraints is of course also possible on the CAP Java stack, where no runtime checks are available.

[Learn more about Database Constraints.](/docs/guides/databases/cdl-to-ddl#database-constraints)

## SQL Window Functions ​

CQL now supports the syntax for SQL window functions:

sql

```
select from Foo {
  ...,
  sum(x) over (partition by a order by b
                 rows between unbounded preceding and current row) as s
}
```

No semantic checks are performed for the window functions, they are simply translated to SQL. Consult the documentation of your database for more information about the supported window functions.

[Learn more about representing SQL window functions in CXN.](/docs/cds/cxn#function-calls)

## GraphQL Schema Using CLI (experimental) ​

The GraphQL schema used in the experimental GraphQL Adapter can be generated stand-alone via `cds compile -2 gql`.

## Node.js Runtime ​

### Important Changes ❗️ ​

From this release on, debug logs of `cds.DatabaseService` and `cds.RemoteService` have sanitized values in production. The sanitization can be deactivated:

js

```
cds.env.log.sanitize_values = false
```

Tip

In production, it's strongly recommended to use log level `info` or higher.

### Generic Providers ​

The media type of a stream property is now updated based on the content type header of the `PUT .../` request. With this, only one request is needed to update both, the media data and the media type.

Further, the Node.js runtime now supports filtering based on the count of records in a collection. For example, you can get all hard-working authors via `GET /Author?$filter=books/$count gt 10`.

### Developer Experience ​

For the December release, we added some improvements with regard to developer experience.

- Typically, running with mocks in production isn't sensible and, hence, the command line option `--with-mocks` was ignored. However, there may be some scenarios during development that would benefit from this option.`cds.env.features.with_mocks = true` now allows `--with-mocks` in production.
- Authorization-related local development was tricky if the respective (mock) user had a tenant other than `anonymous`, as, by default, a new, empty SQLite database would have been created during `cds watch`. Now, in single tenant mode, the default SQLite database is used regardless of `context.tenant`.
- The npm module `passport` is no longer required for authentication strategies `dummy` and `mock`. See Authentication Strategies for more details.
- Requests to remote services are logged (similar to the debug logs for executed SQL statements) if the log level for module `remote` is set to `debug`. See Module Names Used by the Runtime for more details.

## Java SDK ​

### Important Changes ❗️ ​

#### Use Double Star (**) to Exclude Paths ​

To `exclude` *complete* namespaces from code generation with the [CDS Maven Plugin](/docs/java/developing-applications/building#cds-maven-plugin), now `**` placeholder must be used. Adjust the configuration in the `pom.xml` accordingly.

### Configure DB Connection Properties in MT Scenario ​

Pool configurations of multitenant database bindings now support map-based parameters. This enables additional connection properties to be specified. For Hikari connection pool, you can use `cds.datasource..hikari.data-source-properties.: `.

For instance, to configure the packet size of connections created by SAP HANA JDBC driver, add following configuration to your *application.yaml* file:

yaml

```
cds:
  datasource:
    :
      hikari:
        data-source-properties:
          packetSize: 300000
```

[Learn more about datasource configuration.](/docs/java/cqn-services/persistence-services#datasource-configuration)

### CSV Import of Array-Typed Elements ​

Values for elements with arrayed types can now be specified in CSV files for test data import. The values need to be presented as JSON arrays as shown in the following example:

cds

```
entity Samples : cuid {
    records : array of {
        index: Integer;
        flag: Boolean
    }
}
```

A CSV file `Samples.csv` in folder `db/data` containing a single entity instance to be imported could look like this:

csv

```
ID;records
08[...]15;[{"index": 1, "flag": true}, {"index": 2, "flag": false}]
```

[Learn more about providing initial data.](/docs/guides/databases/initial-data)

### OData ​

#### Expose a Service with OData V2 and V4 in Parallel ​

In CAP Java, you can expose a service with OData versions [V2 and V4 in parallel](/docs/java/migration#enabling-odata-v2-and-v4-in-parallel). Formerly this wasn't possible when using the MTX sidecar. This limitation has now been lifted.

### Remote Service Consumption ​

You can now configure Cloud SDK's [destination retrieval strategy](https://help.sap.com/doc/b579bf8578954412aea2b458e8452201/1.0/en-US/com/sap/cloud/sdk/cloudplatform/connectivity/ScpCfDestinationRetrievalStrategy.html) and the [token exchange strategy](https://help.sap.com/doc/b579bf8578954412aea2b458e8452201/1.0/en-US/com/sap/cloud/sdk/cloudplatform/connectivity/ScpCfDestinationTokenExchangeStrategy.html) for a Remote Service by setting `cds.remote.services..destination.retrievalStrategy` resp. `cds.remote.services..destination.tokenExchangeStrategy`.

### CQL Runtime ​

#### Null Values in Results ​

Clarification: The result row of a query execution [may contain `null` values](/docs/java/working-with-cql/query-execution#null-values). Therefore, the `containsKey` method is not appropriate to check if a value is present in a result row and isn't equal to `null`.

#### Aliased Expands ​

[Expands](/docs/java/working-with-cql/query-api#expand) in CQL `Select` statements can now have an alias:

java

```
CqnSelect select = Select.from(BOOKS).columns(
     b -> b.author().as("writer").expand()).byId(101);
Row book = dataStore.execute(select).single();

Object writer = book.get("writer.name"); // path access
```

#### Associations on the Select List ​

Managed to-one associations and compositions can now be [added to the select list](/docs/java/working-with-cql/query-api#managed-associations-on-the-select-list) of `Select` statements.

java

```
CqnSelect select = Select.from(BOOKS).columns(
     b -> b.author()).byId(101);
Row book = dataStore.execute(select).single();

Object authorId = book.get("author.Id"); // path access
```

### Reflection API: get/find Elements by Path ​

When using the [Reflection API](/docs/java/reflection-api), you can now specify a *path* to reflect on elements of a structured type or of an associated entity. Considering the following model:

cds

```
entity People {
     key id : UUID;
     name : { first : String; last : String; };
     car : Composition of one { brand : String; color : String; };
}
```

The following snippets are equivalent.

Long version:

java

```
@Autowired
CdsModel model;

CdsEntity people = model.getEntity("People");

CdsElement name = people.getElement("name");
CdsStructuredType nameType = name.getType().as(CdsStructuredType.class);
CdsElement firstName = nameType.getElement("first");

CdsElement car = people.getElement("car");
CdsStructuredType carType = car.getType(CdsAssociationType.class).getTarget();
Optional colorOfCar = carType.findElement("color");
```

New short version:

java

```
@Autowired
CdsModel model;

CdsEntity people = model.getEntity("People");
CdsElement firstName = people.getElement("name.first");
Optional colorOfCar = people.findElement("car.color");
```

### CDS Maven Plugin: Include/Exclude Definitions ​

The [CDS Maven Plugin](/docs/java/developing-applications/building#cds-maven-plugin) now allows to selectively *include* and *exclude* definitions during [code generation](/docs/java/cqn-services/persistence-services#staticmodel). With the following configuration of the `generate` goal, Java artifacts are generated for the definitions of the `CatalogService` but not for definitions of the namespace `localized`:

xml

```

    com.sap.cds
    cds-maven-plugin
    ${cds.services.version}



                generate



                    CatalogService.**


                    localized.**





```

## New Lint Rule for CSV Files ​

A [new CDS lint rule](/docs/tools/cds-lint/rules/valid-csv-header/) validates header lines of CSV files for whether the columns match to CDS entities. In addition, quick fixes suggest the correct names in VS Code:

To get the VS Code integration for this rule, run [`cds add lint`](/docs/tools/cds-lint/#cds-lint-vscode) once in your project.

[Learn more about CDS Lint.](/docs/tools/cds-lint/)

## Hybrid Testing: K8s and Java ​

You can [bind to Kubernetes service bindings and secrets](/docs/tools/cds-bind#services-on-kubernetes) and [run your CAP Java applications with bindings](/docs/tools/cds-bind#run-cap-java-apps-with-service-bindings) using [`cds bind --exec`](/docs/tools/cds-bind#cds-bind-exec) now. [Examples for important use cases](/docs/tools/cds-bind#use-cases) have been added to the [hybrid testing guide](/docs/tools/cds-bind).

## CDS Editor Performance Optimizations ​

The following applies to CDS editors in SAP Business Application Studio and Visual Studio Code.

The editor is now faster at startup and requires less memory.

Progress is now indicated when configuration was changed, and during references and workspace symbols.
