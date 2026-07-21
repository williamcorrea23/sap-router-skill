<!-- mirror: https://cap.cloud.sap/docs/releases/2025/may25 -->
<!-- fetched: 2026-05-09T02:26:53.410Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# May 2025 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

NOTE

This is a revision of the version published initially on June 5th with these corrections:

- CDS — Association to many w/o `ON` Conditions with fixed troubleshooting instructions.
- Node.js — Opt-in Replacement for Generic-Pool using a better config flag.
- Node.js — Improved Error Handling was missing in the initially published version.

## New Major Versions ​

### CAP Node.js v9 ​

The May 2025 release includes version 9 for CAP Node.js (`@sap/cds` and `@sap/cds-dk`). Along with these changes, we're also updating these minimum required dependencies:

| Dependency | Required Version | Recommended |
| --- | --- | --- |
| **Node.js** | 20 | [22 (LTS)](https://nodejs.org) |

End of Life for cds7

`@sap/cds` 7, `@sap/cds-dk` 7, and `@sap/cds-compiler` 4, which have been in [maintenance status](./../schedule#maintenance-status) so far, have reached [end of life](./../schedule#end-of-life-status) and won't be patched any longer.

If you still use `@sap/cds` 7 or lower, you get an error from `cds` CLI commands. To resolve this, upgrade to `@sap/cds` 9. Only as a fallback downgrade `@sap/cds-dk`.

### CAP Java v4 ​

The May 2025 releases also brings the new major version 4 for CAP Java. This version includes several enhancements and new features to improve the development experience.

End of Life for CAP Java 2.10

`cds-services` and `cds4j-api` version 2.10, which have been in [maintenance status](./../schedule#maintenance-status) so far, have reached [end of life](./../schedule#end-of-life-status) and won't be patched any longer.

### Migration ​

Following are the most important changes that you need to be aware of when upgrading to the new major versions:

- Transactional Event Queues — Enabled by default
- CDS Language — Association to many w/o ON Conditions
- CDS Language — `$now` is Transaction Time
- Databases — Skipped Native Associations for SAP HANA
- Databases — Consistent Operators
- Databases — Removed `hdbcds` Format
- Syntax Cleanup
- Changed Structure of `req.params`
- Service Level Restrictions
- Revised Handling of PUT Requests
- Open-Sourced `cds.test`
- New Database Services v2
- Node.js - Removed Features
- ESLint 9 Required
- Removed Legacy Build Configuration
- Java - Important Changes
- Multitenancy - Important Changes

### New License ​

All CAP Node.js packages starting with `@sap` as well as the CAP Java libraries now come with the [SAP Developer License 3.2 CAP](https://cap.cloud.sap/resources/license/developer-license-3_2_CAP.txt).

The formerly used *SAP Developer License 3.1 / 3.2* imposed strict rules on CAP users with respect to CAP usage and customer support. By shifting to the *SAP Developer License 3.2 CAP*, SAP allows customers of SAP Business Technology Platform (BTP) or any other SAP platform to use CAP applications productively and to request support in line with their existing licensing agreement with SAP.

[See more on our license page.](/docs/resources/cap-license)

## Hierarchical Tree Views, beta 2 Beta ​

The support for hierarchical tree view support is making progress. In this release, we consolidated the configuration between CAP Node.js and CAP Java, so that you can use the same configuration for both runtimes, following these step-by-step instructions, as well as adding support for SQLite and PostgreSQL (in Node.js).

### Consolidated Configuration ​

Given a domain model like this:

cds

```
entity Genres { //...
  parent : Association to Genres;
}
```

[As found in cap/samples/bookshop](https://github.com/capire/bookshop/blob/main/db/schema.cds#L26-L29)

#### 1. Configure the TreeTable in UI5's manifest.json, for example: ​

jsonc

```
  "sap.ui5": { ...
    "routing": { ...
      "targets": { ...
        "GenresList": { ...
          "options": {
            "settings": { ...
              "controlConfiguration": {
                "@com.sap.vocabularies.UI.v1.LineItem": {
                  "tableSettings": {
                    "hierarchyQualifier": "GenresHierarchy",
                    "type": "TreeTable"
                  }
                }
              }
            }
          }
        },
      },
    },
```

Note: `hierarchyQualifier` should be chosen as:
`"Hierarchy"`

#### 2. Annotate/extend the entity in the service as follows: ​

cds

```
// Tell Fiori about the structure of the hierarchy
annotate AdminService.Genres with @Aggregation.RecursiveHierarchy #GenresHierarchy : {
  ParentNavigationProperty : parent, // navigates to a node's parent
  NodeProperty             : ID, // identifies a node, usually the key
};

// Fiori expects the following to be defined explicitly, even though they're always the same
extend AdminService.Genres with @(
  // The columns expected by Fiori to be present in hierarchy entities
  Hierarchy.RecursiveHierarchy #GenresHierarchy : {
    LimitedDescendantCount : LimitedDescendantCount,
    DistanceFromRoot       : DistanceFromRoot,
    DrillState             : DrillState,
    LimitedRank            : LimitedRank
  },
  // Disallow filtering on these properties from Fiori UIs
  Capabilities.FilterRestrictions.NonFilterableProperties: [
    'LimitedDescendantCount',
    'DistanceFromRoot',
    'DrillState',
    'LimitedRank'
  ],
  // Disallow sorting on these properties from Fiori UIs
  Capabilities.SortRestrictions.NonSortableProperties    : [
    'LimitedDescendantCount',
    'DistanceFromRoot',
    'DrillState',
    'LimitedRank'
  ],
) columns { // Ensure we can query these fields from database
  null as LimitedDescendantCount : Int16,
  null as DistanceFromRoot       : Int16,
  null as DrillState             : String,
  null as LimitedRank            : Int16,
};
```

[As showcased in capire/bookstore](https://github.com/capire/bookstore/blob/main/app/genres/tree-view.cds)

That's it! You can now start the server with `cds watch` and see the hierarchical tree view in action in the [Browse Genres](http://localhost:4004/fiori-apps.html#Genres-display) app.

### Support for SQLite and PostgreSQL ​

In addition to the already supported SAP HANA, the hierarchical tree view is now also supported for SQLite and PostgreSQL with the new major versions of `@cap-js/sqlite` and `@cap-js/postgres` for the CAP Node.js stack.

[Learn more about that in the Node.js section below.](#cds-js)

The same is in progress for the CAP Java stack.

## Transactional Event Queues Beta ​

As an evolution of the *persistent outbox*, we have introduced CAP-native task queues to enhance the processing of events and requests to so-called *queued services*.

In a nutshell, queued events are ...

- written to the database within the current transaction and executed asynchronously after said transaction has been committed (→ atomicity).
- retried until they succeed, thereby adding resilience to the queued service - even beyond the current runtime.
- recoverable in case of unrecoverable errors (or if the maximum retry count was reached) via the dead letter queue.

[Learn more about CAP's Event Queues](/docs/guides/events/event-queues)

### In Node.js ​

Simply *queue* or *unqueue* a service via `cds.queued(srv)` or `cds.unqueued(srv)`, respectively, and the subsequent dispatch on the returned service is either executed as an asynchronous task or immediately.

[Learn more about CAP Node.js' cds.queued() API.](/docs/node.js/queue)

Additionally, the Node.js runtime added the following experimental features/ APIs:

#### Event Scheduling Alpha ​

New `.schedule()` as variant of [`cds.queued().send()`](/docs/node.js/core-services#srv-send-request) with fluent API options:

- `.after()`
- `.every()`

Allows you to schedule a background task to be executed after a delay or in a certain interval (as minimum value after completion of the previous task).

#### Event Callbacks Alpha ​

Register callbacks as follows:

- `.after('/#succeeded', (results, req))`
- `.after('/#failed', (error, req))`

Allows you to react to succeeded and failed asynchronous tasks, for example, replicating the full business object from a remote system once its creation was successful.

#### More Efficient Locking Alpha ​

We introduced an application-level event queue status management that avoids long-lasting database locks. That is - in a nutshell - instead of holding the lock during processing, the task runner only locks a message for maintaining its status.

The feature can be enabled via cds.requires.queue.legacyLocking = false.

Application-level task status management only works...

if all active task runners are on cds9.

### In Java ​

The technical outbox API allows to trigger asynchronous workloads.

[Learn more about CAP Java's Technical Outbox API](/docs/java/outbox#technical-outbox-api)

Furthermore, CAP Java already announced the [optimized outbox in last month's release](./apr25#optimized-outbox) as a first building block for more efficient task processing.

### Inbox ​

Utilizing the new event queues feature, inbound messages can be accepted as asynchronous tasks as well. Simply configure your messaging service for Node.js as cds.requires.messaging.inboxed = true and for CAP Java as cds.messaging.services

**Inboxing moves the dead letter queue into your CAP app.**

Enabling the inbox feature means that all messages are acknowledged towards the message broker - regardless of whether their processing was successful or not. Hence, any failures would need to be managed via the dead letter queue built on `cds.outbox.Messages`.

### Enabled By Default ​

Migrating from the outbox to general-purpose event queues is seamless. For example, the table name remains `cds.outbox.Messages` and `cds.outboxed(srv)` is kept as a synonym for the new `cds.queued(srv)`.

However, event queues are **enabled by default**. Hence, a database deployment is required when migrating to cds9/ CAP Java 4 in case the persistent outbox was not yet used in your project.

If this is an issue for your project, you can opt out of the event queues feature by adding cds.requires.queue = false (for Node.js and Java projects!) until you are ready for a database deployment.

## CDS Language & Compiler ​

### New Parser for CDL ​

In cds9 we switch over to the new CDS parser.

The new parser comes with the following:

- Reduced installation size of the compiler package by 40%
- Faster parsing
- Enhanced code completion

The new parser doesn't come with any breaking changes...

... and is fully compatible with the old parser.

### Agnostic Database Functions ​

The `@sap/cds-compiler`, the CAP Node.js database services, and the CAP Java runtime1 come with out-of-the-box support for a specified [set of standard functions](/docs/guides/databases/cap-level-dbs#portable-functions) inspired by OData and SAP HANA:

- `min`, `max`, `count`, `countdistinct`, `sum`, and `average`
- `concat`1
- `trim`
- `contains`, `startswith`, and `endswith`
- `matchespattern`
- `indexof`
- `substring`
- `length`
- `tolower` and `toupper`
- `ceiling`, `floor`, and `round`
- `year`, `month`, `day`, `hour`, `minute`, and `second`1
- `time` and `date`1
- `fractionalseconds`1
- `years_between`, `months_between`, `seconds_between`, and `nano100_between`1

Warning

1 not yet supported by CAP Java

These functions can be used reliably throughout CAP. The framework translates them to suitable native SQL functions.

Example: Function `startswith`

- used in OData queries as follows:http

```
GET /Books?$filter=startswith(title, 'Raven')
```
- used in CQL queries like in the following view:cds

```
entity V as select from Books {
  startswith(title, 'Raven') as found // mapped to native SQL equivalent
}
```

For SAP HANA, the resulting SQL is:sql

```
CREATE VIEW V AS SELECT
  CASE WHEN locate(title, 'Raven') = 1 THEN TRUE ELSE FALSE END AS found
FROM Books;
```

For SQLite, the resulting SQL is:sql

```
CREATE VIEW V AS SELECT
  coalesce((instr(Books.title, 'Raven') = 1), false) AS found
FROM Books;
```

Case sensitivity

The function mappings are case-sensitive. When written in lower case, they are recognized as a standard function call and rewritten. Otherwise, the function call is passed to SQL as is.

[Learn more about Standard Database Functions.](/docs/guides/databases/cap-level-dbs#portable-functions)

### Consistent Operators ​

CAP consistently supports the operators `==` and `!=` in CDS models (including [annotations with expression value](/docs/cds/cdl#expressions-as-annotation-values)) and in CQN. Like the standard SQL operators `IS [NOT] DISTINCT FROM`, they have two-valued Boolean logic and behave like in JAVA or Javascript.

Two-valued logic means, they always evaluate to `true` or `false`, but never to `null` or `unknown`. For example, the following expression evaluates to `true` also if `a` is `null`:

cds

```
  a != 42
```

In essence, `!=` changes from three-valued logic to two-valued logic

Operator `!=` has already been available in CAP before with three-valued logic and now has changed to two-valued logic. In case you really want and need three-valued logic, use operators `=` and `<>`, respectively.

### Miscellaneous ​

#### Nesting Definitions when Compiling to CDL ​

`cds compile --to cdl` now lexically nests definitions into services and contexts. This affects only the appearance of the resulting CDL files, their semantics are unchanged.

As an example, look at the following CSN, translated into CDL:

json

```
{
  "definitions": {
    "sap.com.Bookshop": {
      "kind": "service"
    },
    "sap.com.Bookshop.Books": {
      "kind": "entity",
      "elements": { /* ... */ }
    }
  }
}
```

cds

```
namespace sap.com;
service Bookshop {
  entity Books {
    // ...
  };
};
```

#### Generated Entities and @cds.persistence.journal ​

Using the annotation `@cds.persistence.journal` controls whether a CDS entity is deployed to SAP HANA using `.hdbmigrationtable` instead of `.hdbtable`.

In addition, this annotation is now copied from an entity to the corresponding compiler-generated `.texts` entity for [localized elements](/docs/guides/uis/localized-data#localized-data) and child entities for [Composition of aspects](/docs/cds/cdl#managed-compositions). This means these text tables are managed by `.hdbmigrationtable` instead of `.hdbtable`. This change requires a migration: undeploy the `.hdbtable` artifact and deploy the `.hdbmigrationtable` artifact in the same deployment.

Example:

cds

```
@cds.persistence.journal
entity Books {
  key id : Integer;
  title : localized String;
  chapters : Composition of many {
    key chapter : Integer;
    synopsis : String;
  }
}
```

In addition to entity `Books`, the compiler generates a text entity `Books.texts` for the localized element, and a child entity `Books.chapters` for the managed composition of aspect. Both generated entities now inherit the annotation `@cds.persistence.journal` from the `Books` entity.

If you don't want the generated entities to behave like the corresponding main entity, you can explicitly annotate the generated entities with `@cds.persistence.journal: false`.

Example:

cds

```
annotate Books.chapters with @cds.persistence.journal: false;
```

[Learn more about `@cds.persistence.journal`.](/docs/guides/databases/hana#schema-updates-with-sap-hana)

#### Syntax Cleanup ​

You may encounter syntax errors for definitions that are unclear.

- Providing default `null` for a not-nullable element or parameter is now an error:cds

```
entity E {
  foo : Integer not null default null;
}
```
- In CDS, it is not possible to provide a default for an array. A default for an array like parameter has been silently ignored so far and now is rejected. If you get this error, just remove the default. Example:cds

```
action A(par: array of Integer default 42);
```

### Important Changes ❗️ ​

#### Association to many w/o ON Conditions ​

Previously, a `to many` association or composition with missing an `ON` condition like that:

cds

```
entity Authors { // ...
  books: Association to many Books; // missing on condition
}
```

... was wrongly interpreted as a [managed association](/docs/cds/cdl#managed-associations) with `to one` cardinality, that is, as if you would have declared it like that:

cds

```
entity Authors { // ...
  books: Association to Books; // managed to-one association
}
```

And in effect the compiler *SQL* backends generated foreign keys for it *on the source side*. While this even might have silently worked in some cases, it was not the intended behavior and can only have been wrong.

This has been fixed in this release, such that an to-many association with missing `ON` condition is treated as an *unspecified* association. On one hand, this change allows for more flexible API modeling, which was not possible before. On the other hand, such *unspecified* associations cannot be generically served, but can be (have to be) handled through custom implementations.

In case you get compiler errors like that after upgrading to the May 25 release:

*[ERROR] Expected association with target cardinality ‘to many’ to have an ON-condition*

This can be resolved in one of the following ways:

- If you meant to declare an association to many, correct it like that:cds

```
books: Association to many Books;
books: Association to many Books on books.author = $self;
```
- If you meant to declare a managed association to one, correct it like that:cds

```
books: Association to many Books;
books: Association to Books;
```
- If that was correctly modelled and you indeed wanted to declare an unspecified association, ensure you don't deploy such entities to the database, and handle them with custom handlers.

#### Virtual Elements in Views ​

You can now define a virtual element in a view or projection without providing a value or an expression.

Example:

cds

```
entity P as projection on E {
  // ...,
  virtual v1 : String(11),  // new virtual element
  virtual v2                // new virtual element w/o type
}
```

This defines new virtual elements `v1` and `v2` in `P`. In previous releases this resulted in an error if entity `E` didn't have elements `v1` or `v2`.

Previous ways to define virtual elements in a view or projection are deprecated and may be removed in a future major release. We recommend replacing them with the new syntax.

cds

```
entity P as select from E {
  virtual null   as myV1,  // deprecated
  virtual a      as myV2   // deprecated
}
```

[Learn more about virtual elements in views.](/docs/cds/cdl#virtual-elements-in-views)

#### $now is Transaction Time ​

We have changed the semantics of `$now` in CDS models. When generating SQL, `$now` is now translated to `session_context($now)` and reflects the transaction time (in UTC) pinned by the CAP runtimes. If you need the old behavior, replace `$now` by `current_timestamp` in your models.

An exception is the `default` clause, where `$now` is still mapped to `current_timestamp` (databases don't support `session_context()` there). But for `default $now` the database default is less important, as already the runtimes provide the current server timestamp as default value.

#### Doc Comments are not Propagated ​

Doc comments are no longer propagated, as this is the expected behavior in most cases. For example, a doc comment defined on an entity isn't automatically copied to projections of this entity.

[Learn more about Doc Comments.](/docs/cds/cdl#doc-comments)

## Databases ​

### SAP HANA using ALTER TABLE ADD COLUMN ​

On SAP HANA, large tables can now get deployed faster. This is due to [HDI's new option `try_fast_table_migration`](https://help.sap.com/docs/SAP_HANA_PLATFORM/42668af650f84f9384a3337bcd373692/361b7a91488a4129aba2457bfc2a8520.html) that uses `ALTER` statements instead of expensively copying whole table content.

[CAP's multitenant library](/docs/guides/multitenancy/) has enabled this option by default, as well as most single-tenant projects. Existing single-tenant projects with a *custom db/package.json* need to set the option manually in their start script though:

db/package.jsonjsonc

```
"scripts": {
  "start": ".../deploy.js --parameter com.sap.hana.di.table/try_fast_table_migration=true ..."
}
```

### Skipped Native Associations for SAP HANA ​

On SAP HANA, CDS associations are no longer reflected in database tables and views by native HANA associations (HANA SQL clause `WITH ASSOCIATIONS`), as they are no longer needed by the CAP framework. This can significantly reduce database (re-)deployment times.

In the unlikely case that you need native HANA associations (for example, because you have defined native HANA objects that use them), you can switch them back on through cds.sql.native_hana_associations:true.

First deployment

Be aware that the first deployment after upgrading to cds9 may take longer: For each entity with associations, the respective database object is touched (DROP/CREATE for views, migration for tables). However, subsequent deployments will benefit.

To avoid full table migrations via shadow table and data copy, ensure that your project uses [faster table changes on SAP HANA](#sap-hana-using-alter-table-add-column).

[Learn more about Native HANA Associations.](/docs/guides/databases/hana#native-associations)

### Removed hdbcds Format ​

The deploy format `hdbcds` for SAP HANA has been deprecated with cds8 a year ago and can now no longer be used. If you haven't already done so, switch to the default deploy format `hdbtable` instead. This is not relevant for SAP HANA Cloud, where deploy format `hdbcds` was never available.

[Learn more about moving from .hdbcds to .hdbtable.](/docs/cds/compiler/hdbcds-to-hdbtable)

## Node.js ​

### Improved Error Handling ​

Error handling in CAP Node.js has received a major overhaul, mostly behind the scenes, but with some visible changes for you as a developer.

First, error responses now include reasonable `code` properties, for example `ASSERT_FORMAT`, which can be used in clients and tests to reliable identify the types of errors (before they were too aggressively replaced by status codes as strings).

http

```
Status: 400
Content-Type: application/json

{
  "error": {
    "code": "ASSERT_FORMAT",
    "message": "Input is not in the expected format.",
    "target": "emailAddress"
  }
}
```

Second, [error sanitation](/docs/node.js/events#error-responses), that is, removing error details in responses now is only done in production, instead of aggressively too early and always, which greatly improves testing in development profiles.

Third, input validation errors are now logged as *warnings* only, not as *errors*, as before. This is because input validation errors are not unexpected errors, but foreseen application behavior. In addition, duplicate logging of the same errors has been fixed.

Finally, we **publicly documented** now how errors are constructed using [`req.reject()`](/docs/node.js/events#req-reject) and [`req.error()`](/docs/node.js/events#req-error) and handled in the framework. Here's an excerpt of that:

[Learn more in the Node.js reference docs](/docs/node.js/events#req-reject)

(Non) Breaking Changes

These fixes and improvements required some changes to internal implementation details, and to private interfaces, such as:

- Property `code` property is now used correctly to identify the type of error, which was previously not done in the same way.
- Some error `message`s have changed to be more user-friendly and consistent.
- Some private technical properties like `numericSeverity` or `@Common.numericSeverity` have been removed from some error responses.

While these changes are not breaking any public APIs and hence shouldn't affect your productive applications, they may require adjustments in your tests in case you checked on error responses by deep object equality or similar. → Never do that, but always check on now stable `code` properties instead, as shown above.

### Tree Views w/ SQLite, Postgres Beta ​

cds9 simplifies the handling of OData hierarchies which are now also supported also in the new major versions of `@cap-js/sqlite` and `@cap-js/postgres`.

You can try it out in the [bookshop sample for SAP Fiori](https://github.com/capire/bookstore/blob/main/app). Run `cds watch`. The `Browse Genres` application and the value help for `Genres` in the `Manage Books` application use the SAP Fiori Tree Table.

### New Database Services v2 ​

With cds9 the new major version 2 of the `@cap-js` based database services is required.

#### Assumptions for Unique Constraints ​

Until version 2, the database services made these assumptions:

- A violated unique constraint on `INSERT` or `UPSERT` is always the key constraint and was reported as `ENTITY_ALREADY_EXISTS` to the end user.
- A violated unique constraint on `UPDATE` is always a custom constraint and was reported as `UNIQUE_CONSTRAINT_VIOLATION` to the end user.

These assumptions are now removed. The violated unique constraint is not interpreted and treated as any other error raised by the database. If the error should be reported to the client, the database-specific errors have to be inspected and enriched in custom code.

#### Opt-in Replacement for Generic-Pool Alpha ​

The configuration cds.requires.db.pool.builtin = true enables a built-in resource pool that improves error handling in multitenancy scenarios. Instead of a generic error `ResourceRequest timed out` the underlying error of the service manager is returned.

package.json.cdsrc.yamljson

```
{
  "cds": {
    "features": {
      "pool": "builtin"
    }
  }
}
```

yaml

```
cds:
  features:
    pool: builtin
```

### Open-Sourced cds.test ​

The [test support for CAP Node.js applications](/docs/node.js/cds-test) moved to [`@cap-js/cds-test`](https://www.npmjs.com/package/@cap-js/cds-test). Add it to your *devDependencies* with:

sh

```
npm add -D @cap-js/cds-test
```

This package comes with dependencies that you had to maintain separately until now. So, get rid of the unnecessary dependencies and only maintain the `@cap-js/cds-test` package going forward.

sh

```
npm rm axios chai chai-subset chai-as-promised
```

### Removed Features ​

The following features were deprecated since *cds8*, or longer, and have been removed:

| Removed Packages | Replacement |
| --- | --- |
| Legacy Protocol Adapters | The new, compatible protocol adapters are used automatically |
| Legacy Database Services | Use the new database services [from `@cap-js`](https://github.com/cap-js/cds-dbs?tab=readme-ov-file#readme) instead |
| Obsolete `@sap/cds-hana` | Use `@cap-js/hana` instead. |
| Support for Cloud SDK v3 | Use latest [`@sap-cloud-sdk` v4](https://github.com/SAP/cloud-sdk-js/blob/main/V4-Upgrade-Guide.md) |
| Support for `@sap/xssec` v3 | Use latest [`@sap/xssec` v4](https://www.npmjs.com/package/@sap/xssec) |
| `INSERT.as` | Use [`INSERT.entries` or `INSERT.from`](/docs/node.js/cds-ql#from) instead |
| `@odata.default.order` | Add an `order by` clause to the modeled view instead. |
| `@cds.default.order` | Add an `order by` clause to the modeled view instead. |
| `srv.impl()` and `.with()` | Use [`srv.prepend()`](/docs/node.js/core-services#srv-prepend) instead |
|  |  |

In addition the following compatibility options for features already deprecated in *cds8* or longer have been removed:

| Compatibility Options | Replacement |
| --- | --- |
| `cds.fiori.draft_compat` | Use the [stable registration](/docs/node.js/fiori#draft-support) for Draft handlers |
| `cds.features.compat_restrict_bound` | Restrict the bound action instead |
| `cds.features.compat_restrict_where` | Add a custom handler instead |
| `cds.features.stream_compat` | Adapt custom implementation to cope with streams |

### Important Changes ❗️ ​

#### Changed Structure of req.params ​

[`req.params`](/docs/node.js/events#params) now always returns an array of objects, also for entities with a single key `ID`. If you rely on the previous behavior, you can opt out with cds.features.consistent_params=false.

Assume the following HTTP request:

http

```
GET /catalog/Authors(101)/books(title='Eleonora',edition=2) HTTP/1.1
```

Then `req.params` looks as follows:

js

```
const [ author, book ] = req.params
// > author === { ID: 101}, was 101 before
// > book === { title: 'Eleonora', edition: 2 }
```

#### Service Level Restrictions ​

Local application service calls which do not satisfy the `@requires` annotation of a service are rejected. If you rely on the previous behavior, you can use the [privileged user](/docs/node.js/authentication#privileged-user) or opt out with cds.features.service_level_restrictions=false until the next major release.

#### No Fallback to Default Language for Technical APIs ​

`cds.context.locale` does not fall back to the default language if no locale is specified in the incoming request. This improves the performance of database statements for technical APIs for the following reasons:

- Data is not localized in the default language.
- Data is not sorted in the default language.

If you rely on the previous behavior, you can either request the data in the default language (for example, using the `Accept-Language` header) or opt out with cds.features.locale_fallback=true until the next major release.

[Find more details on Localization.](/docs/guides/uis/i18n)

#### Revised Handling of PUT Requests ​

In cds8 and lower PATCH and PUT requests triggered the creation of the resource if it did not yet exist. The often used but unofficial feature flag `cds.runtime.allow_upsert` suppressed this behavior.

With cds9, the unofficial feature flag is divided into separate flags with following defaults:

| Flag | Behavior | Default |
| --- | --- | --- |
| cds.runtime.patch_as_upsert | Create resource if it does not yet exist. | false |
| cds.runtime.put_as_upsert | Create resource if it does not yet exist. | true |
| cds.runtime.put_as_replace | Payload is enriched with default values. | false |

## Java ​

### Important Changes ❗️ ​

This release brings the new major version CAP Java `4.0`. In essence, it activates advanced security features by default and updates some minimum dependency versions.

Tip

All of the changes can be consumed in the previous version `3.10.x` already which guarantees a smooth transition.

[Learn more in the migration guide.](/docs/java/migration#three-to-four)

The following changes are particularly worth mentioning:

New [minimum versions](/docs/java/versions#dependencies-version-4) apply:

| Dependency | Minimum Version |
| --- | --- |
| cds-dk | `^8` |
| SAP Security | `3.1` |

Some **default behavior** has changed, most notably:

- Enabled advanced instance-based feature to check authorizations deeply (authorization.deep).

- Enabled advanced instance-based feature to reject entity selections with `forbidden` (`403`) accordingly (rejectSelectedUnauthorizedEntity).

- Enabled advanced instance-based feature to check input data (checkInputData).

- Translations from the framework's default language bundle are used (defaultTranslations).

Removed some **deprecated properties**:

| Feature | Removed Property | Recommendation |
| --- | --- | --- |
| Structured messages in Messaging API | `cds.messaging.services..structured` | [Use structured messages only](/docs/java/migration#removed-unstructured) |
| Unrestricted XSUAA attributes | emptyAttributeValuesAreRestricted | [Model unrestricted XSUAA attributes explicitly in the condition](/docs/guides/security/authorization#user-attrs) |
| Event Hub Plugin | module `cds-feature-event-hub` | Use [CDS Plugin for SAP Cloud Application Event Hub](https://github.com/cap-java/cds-feature-event-hub) (same artifact and group ID) |
| SMS certificate header | cds.multiTenancy...clientCertificateHeader | Use cds.security.authentication.clientCertificateHeader instead |
| Goal `cds-maven-plugin:generate` | `sharedInterfaces` and `uniqueEventContexts` | adapt custom code accordingly |

Stay up to date and benefit from latest and greatest features by migrating to `4.0`! Find a step-by-step instruction to upgrade in the [migration guide](/docs/java/migration#three-to-four).

Warning

- cds-services `3.10.x` is now in maintenance mode and only receives critical bugfixes.
- All versions < `3.10.x` have reached end of live and won't be patched anymore.

## Tools ​

### Richer Tooltips in CDS Editor ​

When hovering over a [CDS built-in type](/docs/cds/cdl#built-in-types), you get detailed documentation for it:

Likewise, for [specific compiler errors](/docs/cds/compiler/messages), extended documentation is shown on hover:

### Compact Formatting of case Expressions ​

To reduce vertical space, the CDS Code Formatter now omits line breaks after `when`, `then` or `else` in `case` expressions. It also aligns the `then` keyword with `when` arguments to improve visual structuring. Also, sub-expressions after `and` and `or` are now aligned with each other for better readability:

Compare old vs. new:

cds

```
... case
      when
        (
          metric_a     >  12
          or metric_b  >= 5000
          and metric_c = 4
        or quality_score >  8
      then
        'Standard priority'
      else
        'Low priority'
    end;
```

cds

```
... case
      when (
            metric_a     >  12
            or  metric_b >= 5000
            and metric_c = 4
          or  quality_score >  8
          then 'Standard priority'
      else 'Low priority'
    end;
```

The new formatting option `boolOpsAtLineEnd` enables you to position Boolean operators at the end of a line instead of at the start:

cds

```
when contract_renewal_status     = 'PENDING' and
      subscription_duration_days > 180 and
      (
        customer_satisfaction_score >= 8 or
        loyalty_program_tier        =  'GOLD'
      )
```

### Miscellaneous ​

#### ESLint 9 Required ​

Package `@sap/eslint-plugin-cds` 4 now requires ESLint 9. To migrate your ESLint 8 configuration to ESLint 9, follow the [official migration guide](https://eslint.org/docs/latest/use/migrate-to-9.0.0).

Also, `cds lint` now requires package `eslint` to be installed as an application dependency and is no longer bundled with `@sap/cds-dk`. Run `npm add -D eslint` to install it.

#### Removed Legacy Build Configuration ​

`cds build` no longer supports the undocumented legacy build configurations through cds.data and cds.service. To migrate, first check if the build defaults are ok by removing these properties. Otherwise, see the page on [build configuration](/docs/guides/deploy/build) for how to configure build tasks, especially the `model` property.

`--clean` is no longer a supported `cds build` argument. The build output folder is always cleaned anyway.

## Multitenancy ​

### Important Changes ❗️ ​

#### Configuration ​

- Configuration `cds.mtx` is no longer supported.  → Use the Extensibility Service Configuration instead.
- Legacy extensibility configuration (`entity-whitelist`, `service-whitelist`, `namespace-blacklist`) will cause an error.  → Use the Extensibility Service Configuration instead.
- Old `cds.xt.DeploymentService` configuration for HANA container creation `hdi.create.provisioning_parameters.` is no longer supported.  → Use `hdi.create.` instead.
- The MTX Sidecar now always uses the compiler settings (`cds.cdsc`) of the root project to ensure consistent compilation without the need to replicate the root compiler settings into the MTX Sidecar configuration. Configure this as a fallback in mtx/sidecar/package.json if you want to continue using the sidecar-local configuration:json

```
"requires": {
  "cds.xt.ModelProviderService": {
    "use-local-cdsc-config": true
  }
}
```

#### Java Setup ​

- If you get the message 'Invalid MTX sidecar configuration', you need to add the dependency to `@sap/cds-mtxs` also to the `package.json` in your project root. This is a known, temporary issue in `@sap/cds-mtxs@3`.

#### Extensibility ​

- The default for extension validation has been changed. The extension validation now always checks all existing extensions instead of only the extension with the ID to be uploaded.
- The application base model downloaded using `cds pull` will also contain all existing extensions except the one implemented in the current extension project.

## CAP Plugins ​

### SAP Cloud Application Event Hub ​

Distribute business events across the SAP cloud landscape by integrating your CAP application with [SAP Cloud Application Event Hub](https://help.sap.com/docs/sap-cloud-application-event-hub/sap-cloud-application-event-hub-service-guide/what-is).

The integration is provided by the open-source plugins [`@cap-js/event-broker`](https://github.com/cap-js/event-broker) for Node.js and [`com.sap.cds:cds-feature-event-hub`](https://github.com/cap-java/cds-feature-event-hub) for Java.

[Find more details in the Plugins page entry.](/docs/plugins/index#event-hub)

### SAP Integration Suite, Advanced Event Mesh Beta ​

[SAP Integration Suite, advanced event mesh](https://www.sap.com/products/technology-platform/integration-suite/advanced-event-mesh.html) enables applications to engage in real-time asynchronous communication across distributed environments using a fully managed cloud service designed for event-driven architectures.

The open-source plugins [`@cap-js/advanced-event-mesh`](https://github.com/cap-js/advanced-event-mesh) for Node.js and [`com.sap.cds:cds-feature-advanced-event-mesh`](https://github.com/cap-java/cds-feature-advanced-event-mesh) for Java provide out-of-the-box support.

[Find more details in the Plugins page entry.](/docs/plugins/index#advanced-event-mesh)

## Microservices with CAP ​

Here's a new [guide](/docs/guides/deploy/microservices) that shows how to deploy multiple Node.js CAP applications, which share one database schema. The guide is based on the collection of sample applications at [cap-samples](https://github.com/SAP-samples/cloud-cap-samples?tab=readme-ov-file#welcome-to-capsamples).
