<!-- mirror: https://cap.cloud.sap/docs/releases/2025/apr25 -->
<!-- fetched: 2026-05-09T02:26:47.850Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# April 2025 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Prepare for Major Release ​

Along with new features, the next major release CDS 9 will contain some changes that you'll need to react on. You can do this already **now**, which eases the transition. You can't use the mentioned **deprecated functions** with the CDS 9 release. The corresponding compatibility flags won't be respected any longer.

See [CDS Language & Compiler](#cds) and [Node.js](#cds-js).

## CDS Language & Compiler ​

In preparation for the upcoming major release, [switch on the new CDS parser.](./feb25#new-parser)

## Node.js ​

Use this month to get prepared for the upcoming major release. Here's are the things you can and should already enable and test:

- Upgrade to `@sap/xssec 4`. --> remove compat flag
- Adapt to changed behavior when processing `@restrict.where` checks.
- Adopt @cap-js database services now.
- Switch on the new protocol adapters. --> remove compat flag
- Switch on lean draft. --> remove compat flag
- Migrate ESLint Configuration
- Add Test Support Package

## Java ​

### Optimized Outbox ​

Technical [Outbox Service](/docs/java/outbox#persistent) offers CAP applications a generic API to emit events to (Remote) CDS Services in a resilient way. By default, CAP auditlog and messaging events are sent via the Outbox. The internal Outbox processing is now optimized to serve high-scale load profiles across many tenants using task queues internally. As a consequence, the persistence of a tenant's outbox only needs to be queried when needed, and resource consumption is significantly reduced due to the massively reduced DB connection usage.

To benefit from the task-based Outbox processing, you need to explicitly set cds.taskScheduler.enabled: true. In future versions of CAP Java, the optimized Outbox will be enabled by default.

### Remote OData Singletons ​

CAP Java now supports consuming *singleton* instances from remote OData services during remote service consumption. This is particularly useful for scenarios where a single, globally shared entity needs to be accessed. For example, `OverallStatus` could represent the health status of an entire system:

xml

```


















```

This EDMX model defines the singleton `OverallStatus`. It can now be accessed using remote service consumption as usual:

java

```
CqnSelect selectStatus = Select.from(OVERALL_STATUS);
OverallStatus status = remoteService.run(selectStatus).single(OverallStatus.class);
```

### Enhanced Search ​

The `@Common.Text` annotation allows you to specify a property that holds a text to be displayed on the UI instead of the value of the annotated property. To enhance the user experience, the property that holds the display text is now searched by default:

cds

```
entity Books : cuid {
title  : String;
@Common.Text : author.name
author : Association to Authors;
}
entity Authors : cuid {
name : String;
}
```

Here the value of the `name` property of the `Authors` entity is displayed instead of the `author` association and is now also searched automatically, without requiring additional configuration.

### To-many Expand on Subqueries ​

You can now expand to-many associations from [subqueries](/docs/java/working-with-cql/query-api#from-select) if the association is selected implicitly via select all in the inner query:

java

```
CqnSelect authorsUnder40 = Select.from(AUTHORS)
   .excluding(a -> a.placeOfBirth())
   .where(a -> a.age().lt(40));
Select.from(authorsUnder40).columns(
    a -> a.get("name"),
    a -> a.to("books").expand("title"));
```

### New Functions in CDS QL ​

The following new functions are now supported by CDS QL in CAP Java:

#### Arithmetic Functions ​

- round
- floor
- ceiling

#### String Functions ​

- length
- indexof (zero-based)
- trim

The functions are available on the `Value` interface as well as on the `CQL` helper class. Examples:

java

```
CqnSelect booksWithShortTitle = Select.from(BOOKS).where(b -> title().length().lt(10));
CqnSelect averagePriceRoundedByGenre = Select.from(BOOKS)
    .columns(b -> b.genre().name(), b.price().avg().round())
    .groupBy(b -> b.genre().name());
```

The functions are implemented in a database-agnostic way with semantics aligned with OData v4:

- Arithmetic Functions
- String Functions

### Miscellaneous ​

- The `Result.rowType()` method, which returns the structured type of each row of a query result, is now also supported for insert, upsert, and update results.
- Expands from and to entities with aliased keys are now also supported.

## CAP Plugins ​

### Attachments: Multitenancy ​

[@cap-js/attachments](https://github.com/cap-js/attachments) now supports multitenancy with both shared and tenant-specific object store instances. By default, the plugin uses a separate object store instance for each tenant to ensure complete data isolation.

The tenant-specific object store instance scenario is sketched in the following figure:

### Change Tracking: Multitenancy ​

[@cap-js/change-tracking](https://github.com/cap-js/change-tracking) now supports multitenancy and extensibility using MTX-S sidecar deployments.
