<!-- mirror: https://cap.cloud.sap/docs/releases/2022/oct22 -->
<!-- fetched: 2026-05-09T02:26:33.302Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# October 2022 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## CAP Sessions at SAP TechEd ​

**Date**: November 15/16, 2022
[Register now!](https://www.sap.com/about/events/teched.html)

We are about to pack our bags for this year's SAP TechEd. Here is what we have planned as sessions around CAP:

- Discover the Latest Innovations in CAP: New and noteworthy things in CAP
- Boost Verticalization, Customization, and Composition: Learn about multitenancy, extensibility, and feature toggles
- Bringing Service Integration to Your Fingertips: See service integration with integration packages in action
- Compose Full-Stack Apps in Business Application Studio: Build and deploy CAP applications in minutes using only visual editors

## Localization Support in Extensions ​

Within an extension, it's now possible to include i18n files, using the same approach as for standard applications

i18n/i18n.propertiesproperties

```
SalesRegion_name_col = Sales Region
Orders_priority_col = Priority
...
```

[Learn more about localized extensions.](/docs/guides/extensibility/customization#localizable-texts)

## SAP Fiori Analytical List Page for SFlight ​

We have added an SAP Fiori [Analytical List Page](https://ui5.sap.com/#/topic/3d33684b08ca4490b26a844b6ce19b83) (ALP) to our [CAP SFlight](https://github.com/SAP-samples/cap-sflight) sample.

The ALP runs with the Node.js and the Java version of CAP SFlight. Both runtimes support the relevant queries out of the box. That means, you just have to set the required annotations without the need of custom handler implementations.

Warning

Within the SFlight repository, to enable all features for the ALP in the Node.js runtime, we've switched on the new OData parser (`odata_new_parser: true`), which is still **experimental**. If you use the ALP with the standard OData parser, some features like grouping in the analytical table are not available.

## CDS Language & Compiler ​

### Reusing Annotations ​

Now, it is possible to extend a view or a projection with an aspect that only contains annotations. Use this to write lengthy annotations like for instance-based authorization only once and reuse them for several entities:

cds

```
@restrict: [{ grant: ['READ', 'WRITE'], where: 'CreatedBy = $user' }]
aspect RestrictToOwner {};

extend Orders with RestrictToOwner;
extend Vendors with RestrictToOwner;
```

Extending an entity with an aspect is the same as including the aspect. Thus, applying an annotation directly to the entity overwrites the same annotation coming from an aspect.

[Learn more about Named Aspects.](/docs/cds/cdl#named-aspects)

## Node.js ​

### Consumption of Dead Letter Queue ​

In messaging, to receive all messages without creating subscriptions, you can register on `*`.

### Simplified Usage of Correlated Sub-Queries ​

In the fluent query API, we have eased the construction of where exists clauses.

js

```
SELECT.from(Authors).where({exists:'books'})
SELECT.from(Authors).where({'not exists':'books'})
SELECT.from(Authors).alias('a').where({ exists:
  SELECT.from(Books).where({author_ID:{ref:['a','ID']}})
})
```

To support those clauses, we've introduced a dedicated method `.alias()` to choose table aliases.

js

```
SELECT.from(Authors).alias(a)
```

[Learn more about Constructing Queries.](/docs/node.js/cds-ql#constructing-queries)

### SAP-Specific EDMX Annotations Respected in Service Consumption ​

SAP-specific properties like `sap:display-format="Date"` are respected in EDMX importer and runtime.

js

```
service.insert({ name: 'Edgar Allan Poe', birthdate: '1809-01-19' }).into(Authors)
```

The payload of this query will be automatically transformed to match the expected EDM format of the remote system, in this case `1809-01-19T00:00:00`.

## Java ​

### Important Changes ❗️ ​

Starting with this release, property `cds.install-cdsdk.version` of goal `install-cdsdk` in the `cds-maven-plugin` is **mandatory and needs to be explicitly maintained by the application**. This property specifies the `@sap/cds-dk` version used for CDS build. Previously it was optional and had the default value `^4`. Note that the build stops if this property is missing. If your configuration is not prepared yet, find a detailed description how to set this property in [Using a specific cds-dk Version](/docs/java/developing-applications/building#cds-maven-plugin).

### Significant Performance Optimizations ​

Recently, there has been a focus on eliminating performance hotspots in the CAP Java runtime. According to measurements of basic OData requests such as fetching a full entity set (`GET /Travel`) in [SFlight](https://github.com/SAP-samples/cap-sflight) application, CPU usage has been significantly reduced. The following table shows some examples (CPU consumption compared to version 1.26.0):

| OData Request1 | CAP Java 1.29.0 |
| --- | --- |
| `GET /Travel?$top=1000` | down to 31% |
| `GET /Travel?$expand=to_Agency` | down to 39% |
| `GET /Travel?$expand=to_Booking($expand=to_Carrier)` | down to 21% |
| `GET /Travel?$search=Japan` | down to 46% |

1 No authorization and in-memory DB H2

Performance optimizations are still ongoing, so stay tuned for more improvements.

### H2 2.x as Default Database ​

CAP Java now supports H2 version 2.x. In Spring, H2 is automatically initialized as in-memory database when the H2 JDBC driver is present on the classpath.

For H2, you need to configure the CDS Compiler to use the new SQL [dialect `h2`](/docs/java/cqn-services/persistence-services#h2), which is specific for H2 2.x.

sh

```
cds deploy --to h2 --dry
```

The `cds-services-archetype` now generates a new CAP Java project with H2 2.x as in-memory database.

### Support for Download Repositories with Authentication ​

The goal `install-node` of the `cds-maven-plugin` triggers the download of a Node.js contribution from a remote repository. To support repositories that require authentication (for example, internet facing location), the goal has been enhanced with a new optional property `cds.install-node.serverId`, which refers to a server configuration in maven's `settings.xml` file. When setting up a connection to the remote repository to download Node.js, `install-node` now uses provided credentials from this server configuration.

### Create CDS QL Statements from Results ​

[Entity References](/docs/java/working-with-cql/query-execution#entity-refs) can now also be obtained from the result rows of insert and update operations. The references address the entity via the key values from the result row and can be used in CDS QL statements:

java

```
CqnUpdate update = Update.entity(AUTHOR).data("name", "James Joyce").byId(101);
Author joyce = service.run(update).single(Author.class);

CqnSelect q = Select.from(joyce.ref().books());
```
