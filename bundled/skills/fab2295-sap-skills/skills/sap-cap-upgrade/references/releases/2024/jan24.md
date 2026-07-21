<!-- mirror: https://cap.cloud.sap/docs/releases/2024/jan24 -->
<!-- fetched: 2026-05-09T02:26:42.808Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# January 2024 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Open Telemetry Plugin ​

The Telemetry plugin [@cap-js/telemetry](https://www.npmjs.com/package/@cap-js/telemetry) provides observability features such as tracing and metrics, including [automatic OpenTelemetry instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/automatic). Simply add the plugin to your project and you will find telemetry output written to the console as follows:

txt

```
[odata] - GET /odata/v4/processor/Incidents
[telemetry] - elapsed times:
  0.00 → 2.85 = 2.85 ms  GET /odata/v4/processor/Incidents
  0.47 → 1.24 = 0.76 ms    ProcessorService - READ ProcessorService.Incidents
  0.78 → 1.17 = 0.38 ms      db - READ ProcessorService.Incidents
  0.97 → 1.06 = 0.09 ms        @cap-js/sqlite - prepare SELECT json_object('ID',ID,'createdAt',createdAt,'creat…
  1.10 → 1.13 = 0.03 ms        @cap-js/sqlite - stmt.all SELECT json_object('ID',ID,'createdAt',createdAt,'crea…
  1.27 → 1.88 = 0.61 ms    ProcessorService - READ ProcessorService.Incidents.drafts
  1.54 → 1.86 = 0.32 ms      db - READ ProcessorService.Incidents.drafts
  1.74 → 1.78 = 0.04 ms        @cap-js/sqlite - prepare SELECT json_object('ID',ID,'DraftAdministrativeData_Dra…
  1.81 → 1.85 = 0.04 ms        @cap-js/sqlite - stmt.all SELECT json_object('ID',ID,'DraftAdministrativeData_Dr…
```

In addition to the default console output, there are predefined kinds for exporting telemetry data to [SAP Cloud Logging](https://help.sap.com/docs/cloud-logging), Dynatrace, and Jaeger.

[See the repository's `README` for more details.](https://github.com/cap-js/telemetry/blob/main/README.md)[Learn more about Java support.](/docs/java/operating-applications/observability#open-telemetry)

## CDS Language & Compiler ​

### Define Event by Projection ​

You can now define an event as projection on an entity, type, or another event. This is useful, for example, when importing services: it allows to define an event in CAP as projection on the "external" event.

Example:

cds

```
event CustomerChanged : projection on ImportedService.BusinessPartner.ChangedEvent {
  BusinessPartner as ID,
  BusinessPartnerFullName as name,
  // ...
}
```

Only the effective signature of the projection is relevant.

[Learn more about Events.](/docs/cds/cdl#events)

## Node.js ​

### Media Data and Large Binaries ​

Previously, the database services returned `cds.LargeBinary` without `@Core.MediaType` annotation as regular column with base64-encoded buffer as value which potentially causes problems in memory consumption.

As a consequence, from now on the database services will return large binaries only if requested explicitly and as a stream instead of the materialized buffer.

This has the following effect:

js

```
SELECT.from(Attachments) //> [{ ID, title, image: Buffer }]
SELECT(['image']).from(Attachments) //> [{ image: Buffer }]

SELECT.from(Attachments) //> does not include "image"
SELECT(['image']).from(Attachments) //> [{ image:  }]
```

This also has an effect for OData APIs. Large binaries have to be annotated with `@Core.MediaType` in order to be reachable via the [streaming choreography](/docs/guides/services/media-data). If not annotated, those properties are not reachable anymore, even if requested explicitely.

`cds.stream()` and `srv.stream()` are deprecated and will be removed with the next major release. `SELECT` with a single large binary column can be used instead as described above.

Compatibility to the previous behavior can be restored with

json

```
"cds": {
  "features": {
    "stream_compat": true
  }
}
```

Tip

It is strongly recommended to annotate all large binary properties with `@Core.MediaType` and use them according to streaming scenarios.

[Learn more about streaming.](/docs/guides/services/media-data)[Learn more about databases.](/docs/guides/databases/index)

### Programmatic Outboxing of Services ​

You can now use `cds.outboxed(srv)` to get the outboxed variant of a service: Each event first gets stored in an outbox before reaching the target service. For immediate emits of outboxed services, there's also the counterpart `cds.unboxed(srv)`.

js

```
const outboxed = cds.outboxed(srv)
await outboxed.emit('someEvent', { some: 'message' }) //> deferred emit via outbox
await cds.unboxed(outboxed).emit('someEvent', { some: 'message' }) //> immediate emit w/o outbox
```

[Learn more about the outbox in Node.js.](/docs/node.js/queue)

### Lean Draft Sorting on SAP Fiori List Report Floorplan ​

The sorting behavior for the lean draft has been aligned with the other runtimes in the SAP ecosystem, such as CAP Java and RAP for a consistent user experience.

Instead of positioning the drafts always on top of the list, they are now included at the respective position of the actual sorting order.

### Garbage Collection of Stale Drafts ​

Stale drafts can be deleted automatically after a configurable timeout. Simply set the timeout to `true` (enables default timeout of `30d`) or a value like `14d`.

json

```
{
  "cds": {
    "fiori": {
      "draft_deletion_timeout": "14d"
    }
  }
}
```

[Learn more about general draft handling in Node.js.](/docs/node.js/fiori)

## Java ​

### Important ❗️ ​

#### Support for Cloud SDK 5 ​

CAP Java supports [Cloud SDK 5](https://sap.github.io/cloud-sdk/docs/java/release-notes) now.

In case your application uses Cloud SDK integration (`cds-integration-cloud-sdk`), the migration is a matter of adapting Maven dependencies only.

Migrate to Cloud SDK 5 as soon as possible

We highly recommend to migrate to Cloud SDK 5 as soon as possible as Cloud SDK 4 runs out of maintenance end of May 24 according to the [release policy](https://sap.github.io/cloud-sdk/docs/java/release-policy).

[You can find detailed instructions in the dedicated migration guide.](/docs/java/migration#cloudsdk5)

#### Comparing CDS Elements ​

When comparing `CdsElement` instances obtained from the `CdsModel` the `equals` method must now be used.

### Support for Spring Boot 3.2 ​

CAP Java now supports latest [Spring Boot `3.2`](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.2-Release-Notes).

The most interesting feature is [virtual thread](https://dev.java/learn/new-features/virtual-threads/) support. To use virtual threads, you need to run with JDK 21 and set the property `spring.threads.virtual.enabled` to `true`.

Note that HANA JDBC driver processes Input/Output in `synchronized` blocks which can reduce the effect of virtual threads. Experiments are currently being carried out with an internal driver version optimized for virtual threads. Stay tuned!

### Enhanced Open Telemetry ​

When configured with a front end for Open Telemetry signals, CAP Java now additionally writes trace spans for the following:

- Individual OData V4 requests of a `$batch` request.
- CQN processing showing detailed statement information.

Moreover, Dynatrace as Open Telemetry front end is [integrated](/docs/java/operating-applications/observability#open-telemetry-configuration-dynatrace) smoothly now.

[Learn more about Open Telemetry in CAP Java.](/docs/java/operating-applications/observability#open-telemetry)

### Update with Expressions in Fluent Style ​

Use the model interfaces of the builder API to build update expressions in fluent style. The following statements converts a book's title to upper case and increases the stock by 1:

java

```
CqnUpdate update = Update.entity(BOOK).where(b -> b.title().eq("CAP"))
    .set(b -> b.title(), title -> title.toUpper())
    .set(b -> b.stock(), stock -> stock.plus(1));
```

[Learn more about building update expressions.](/docs/java/working-with-cql/query-api#update-expressions)

### Improvements in Search on SAP HANA Cloud HEX Engine ​

On SAP HANA Cloud, in SQL optimization mode `hex`, CAP Java uses the `SCORE` function instead of the `CONTAINS` predicate to execute a search.

Compared to `CONTAINS`, `SCORE` has more capabilities, listed in the following:

- can be executed by the SAP HANA HEX engine
- can search expressions
- can search subqueries

This allows to significantly simplify the generated SQL in `hex` mode, which brings performance improvements in many situations.

Annotate an entity with `@cds.sql.search.mode` to specify how an entity should be searched. Ths following list contains possible values:

- `generic` - search using `LIKE`
- `localized-associations` - for localized elements, the translation and the fallback text are searched
- `localized-view` - for localized elements, the translation is searched or the fallback text if no translation is available

[Learn more about SQL optimization mode.](/docs/java/cqn-services/persistence-services#sql-optimization-mode)
