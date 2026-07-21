<!-- mirror: https://cap.cloud.sap/docs/releases/2023/sep23 -->
<!-- fetched: 2026-05-09T02:26:39.366Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# September 2023 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Share Your Ideas for CAP ​

We run a continuous influence session as an official channel for your feature requests. Get engaged and share your ideas.

[Find here the continuous influence session for CAP.](https://influence.sap.com/sap/ino/#/campaign/2280)

## PostgreSQL ​

### Native cds build Support ​

If your app is using `@cap-js/postgres`, `cds build` now auto-pulls a `postgres` build task generating deployment artifacts for PostgreSQL. This results in a folder structure like this in your `gen` folder:

zsh

```
bookshop/
├─ db/
├─ gen/
│ └─ pg/
│   ├─ package.json
│   └─ db/
│     ├─ csn.json
│     └─ data/
│       ├─ my.bookshop-Authors.csv
│       ├─ my.bookshop-Books.csv
│       └─ ...
└─ ...
```

Remove custom build scripts

As `cds build` is now doing all the work for you, build scripts shouldn't be required any more. If your scenario requires custom build scripts, make sure they do not interfere with the `cds build`-generated `gen` folder structure.

[Learn more about deployment with a deployer app.](/docs/guides/databases/postgres#with-a-deployer-app)

### Using cds add ​

For Node.js projects on Cloud Foundry, you can now easily add PostgreSQL configuration to your CAP project – simply run `cds add postgres`.

## CDS Language & Compiler ​

### Calculated Elements ​

In previous releases we have introduced [Calculated Elements On-read](./march23#calculated-elements-beta) with support in the [Node Runtime](./aug23#calculated-elements-in-node-js) and in the [Java Runtime](./jun23#java-support-for-calculated-elements-on-read), and [Calculated Elements On-write](./jun23#calculated-elements-on-write) as beta features. They are now generally available without restriction.

[Learn more about Calculated Elements.](/docs/cds/cdl#calculated-elements)

### Publish Association With Filter Beta ​

In views or projections, you can now publish an association with a filter. The ON condition of the resulting association is the ON condition of the original association plus the filter condition, combined with `and`.

In this example, in addition to `books` projection `P_Authors` has a new association `availableBooks` that points only to those books where `stock > 0`:

cds

```
entity P_Authors as projection on Authors {
  *,
  books[stock > 0] as availableBooks
};
```

[Learn more about Publishing Associations.](/docs/cds/cdl#publish-associations)

### Defaults for Managed Associations ​

If the association target has a single primary key, a default value can be provided for a managed association.

cds

```
entity Booking {
  // ...
  bookingStatus : Association to one BookingStatus default 'N';
}
```

This default applies to the generated foreign key element:

sql

```
CREATE TABLE Booking (
  ...
  bookingStatus_code NVARCHAR(1) DEFAULT 'N',
);
```

[Learn more about Managed Associations.](/docs/cds/cdl#managed-associations)

## Security ​

### Internal Users ​

Microservices of an application usually need to send requests on the technical provider level. For instance, multitenant CAP services fetch tenant-specific CDS models from their MTX sidecar. Obviously endpoints for intra-application communication need to be authorized properly, to exclude external clients.

Use the new pseudo-role `internal-user` to conveniently protect internal endpoints:

cds

```
@requires: 'internal-user'
service InternalService {
  // only open for the technical PaaS provider
  // ...
}
```

Defining custom CAP roles for this use case is no longer necessary and could lead to very dangerous privilege escalations.

Behind the scenes, a JWT token created on behalf of the technical user for the application's shared XSUAA or IAS instance results in granted pseudo-role `internal-user` in the receiving CAP service that is bound to the **same instance**.

[Find more details about internal communication in Pseudo Roles.](/docs/guides/security/cap-users#pseudo-roles)

## Node.js ​

### Important Changes ❗️ ​

- Node 16 is EOL (see Node.js announcement). Please upgrade to Node.js 18 or higher as the Node.js buildpack might drop the support soon.For more information, please see What's New for SAP BTP.

### Optimized cds.test ​

To work properly, [cds.test](/docs/node.js/cds-test) requires to be started from the application directory, to ensure that the correct [cds.env](/docs/node.js/cds-env) configuration is applied. If it's started from an incorrect directory, rather cryptic error messages appear or it even tests the application with an invalid configuration. To simplify the detection of these errors, we have implemented the flag [CDS_TEST_ENV_CHECK](/docs/node.js/cds-test#cds-test-env-check) that throws an error and explains the root cause:

sh

```
Detected cds.env loaded before running cds.test in different folder:
1. cds.env loaded from:  ./
2. cds.test running in:  cds/tests/bookshop

    at Test.in (node_modules/@sap/cds/lib/utils/cds-test.js:65:17)
    at test/cds.test.test.js:9:41
    at Object.describe (test/cds.test.test.js:5:1)

   5 | describe('cds.test', ()=>{
>  6 |   cds.env.fiori.lean_draft = true
     |       ^
   7 |   cds.test(__dirname)

  at env (test/cds.test.test.js:7:7)
  at Object.describe (test/cds.test.test.js:5:1)
```

To mitigate such issues, use [`cds.test.in(...)`](/docs/node.js/cds-test#test-in-folder) in the beginning of the file, which ensures that [cds.env](/docs/node.js/cds-env) is loaded correctly.

[Learn more about cds.test.](/docs/node.js/cds-test)

We plan to enable the flag by default in the next major release. Please prepare for it by enabling the flag already today.

## Java ​

### Important Changes ❗️ ​

- Cloud SDK `4.24.0` is the new minimum required version for CAP Java. Use dependency management to ensure your project consistently uses this or a later Cloud SDK version.
- For event brokers that don't provide an explicit unique message ID the ID is now determined from the cloudevents ID property, if available. Message IDs are no longer generated when receiving an event without any ID.
- Active instances of draft-enabled entities are now locked for deletion, if a locked draft exists, that is owned by a different user. The user owning the draft can always delete the active instance and with that also delete the corresponding draft.

### JDK21 Compliance ​

CAP Java can now be run on latest [SapMachine 21](https://sap.github.io/SapMachine/) (LTS) and [GraalVM 21](https://www.graalvm.org/). Integration tests covering transitive dependencies introduced by CAP Java extensions have been executed successfully.

We have started to investigate cool new JDK21 features such as [Virtual Threads](https://openjdk.org/jeps/444).

Stay tuned!

### Collating on SAP HANA ​

When using locale-specific comparison on SAP HANA, we replaced a *statement-wide* collation setting, which had negative impact on the performance in some situations. Now, only if locale-specific sorting is required, the `ORDER BY ... COLLATE` clause is used, which affects only the selected sort specification.

By default, all string elements are sorted locale specific. To fine-tune this, the new annotation [@cds.collate](/docs/java/cqn-services/persistence-services#sap-hana-cloud) allows to indicate that an element does not require locale-specific comparison:

cds

```
entity Books : cuid {
    title        : localized String(111);
    descr        : localized String(1111);
    @cds.collate : false
    isbn         : String(40);  // does not require locale-specific sorting
}
```

Warning

If string elements, which are not annotated with `@cds.collate:false`, are used in an ordering relation (`>`, `

[Learn more about support for SAP HANA Cloud.](/docs/java/cqn-services/persistence-services#sap-hana-cloud)

### Use List Values with IN ​

You can now compare list values in an `IN` predicate, which allows to efficiently filter by multiple value sets:

java

```
import static com.sap.cds.ql.CQL.*;

...

CqnListValue elements = list(get("AirlineID"), get("ConnectionID"));
CqnListValue lh454  = list(val("LH"), val(454));
CqnListValue ba119  = list(val("BA"), val(119));
List valueSets = List.of(lh454, ba119);

CqnSelect q = Select.from(FLIGHT_CONNECTION).where(in(elements, valueSets));
```

This is executed by this efficient SQL query:

sql

```
SELECT * FROM FlightConnection
  WHERE (AirlineID, ConnectionID) IN ((?, ?), (?, ?))
```

[Learn more about List Values.](/docs/java/working-with-cql/query-api#list-values)

### Optimized Expand ​

The expand strategy `parent-keys` is now executed as a bulk operation. Use the strategy `load-single` to expand the associated entity sets one by one.

cds

```
entity Person {
  key id   : Int16;
  name     : String;
  parent   : Association to Person;
  @cds.java.expand: {using: 'parent-keys'}
  children : Composition of many Person on children.parent = $self;
}
```

Sample query:

java

```
Select.from(PERSON)
  .where(p -> p.id().in(300, 400))
  .columns(p -> p.name(),
           p -> p.children().expand(c -> c.name()));
```

This query is executed as follows:

sql

```
SELECT * FROM Person T0 WHERE T0.id in (?, ?)
SELECT * FROM Person T0 INNER JOIN Person T1 ON (T1.parent_id = T0.id) and (T0.id in ((?), (?)))
```

Use `@cds.java.expand: {using: 'load-single'}` to enforce expanding with individual selects.

[Learn more about Expand Optimization.](/docs/java/working-with-cql/query-api#expand-optimization)

### Identity Management ​

#### Enhanced Identity Feature ​

Previously, feature `cds-feature-xsuaa` was mandatory for XSUAA authentication. Now feature `cds-feature-identity` is also supporting pure XSUAA-based scenarios and is positioned to fully replace `cds-feature-xsuaa` in a compatible way.

For compatibility reasons, the `cds-feature-xsuaa` feature still takes precedence over `cds-feature-identity` in the classpath. Remove the Maven dependency to `cds-feature-xsuaa` explicitly in order to switch to `cds-feature-identity` in general.

Warning

Note that `cds-feature-xsuaa` is based on [spring-xsuaa](https://github.com/SAP/cloud-security-services-integration-library/tree/main/spring-xsuaa) which is deprecated. Consequently, `cds-feature-xsuaa` is now deprecated as well and will be removed in a future release.

### Miscellaneous ​

- The `cds-feature-postgresql` adds support for SSL connections with host verification.
- Service Bindings from `default-env.json` are now provided through a plugin-in the Service Binding Library and are therefore visible to other libraries, for example Cloud SDK.

## Multitenancy ​

### Download Migrated Projects ​

After migrating an application to `@sap/cds-mtxs`, customers might want to continue working with the extensions they made with `@sap/cds-mtx`.
 As long as the metadata containers (`TENANT--META`) created by `@sap/cds-mtx` still exist, the customer extension projects can be downloaded using the CDS client. The user running the download command needs to have the scope `cds.ExtensionDeveloper` assigned.

sh

```
cds extend  --download-migrated-projects
```

The command downloads an archive named `migrated_projects.tgz` that contains the existing extensions that are ready to be used with `@sap/cds-mtxs`.

[Learn more about MTX migration and the download of migrated projects.](/docs/guides/multitenancy/old-mtx-migration#download-of-migrated-extension-projects)

## Miscellaneous ​

- CSV files with multiline values, that is line breaks, are supported with `cds deploy`.
