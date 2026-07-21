<!-- mirror: https://cap.cloud.sap/docs/releases/2026/apr26 -->
<!-- fetched: 2026-05-09T02:26:55.805Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# CAP Release April 26 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Preparing for cds 10 ​

The next major release of CAP, *cds 10*, is planned for June 26. You can get prepared for it by checking your project for compatibility issues and adjusting your code accordingly already now.

### CAP Node.js ​

**Node.js v22** becomes the *minimum* supported runtime. Recommended is Node 24 (LTS). [Learn more about the CAP Release Schedule](./../schedule#cap-node-js)

**Native `node:sqlite`** becomes the default SQLite driver. To keep using `better-sqlite3` or `sql.js`, add them as an explicit dependency. -> [See February 2026 Release Notes](./feb26#native-sqlite-support)

#### Flags with Changed Defaults ​

Following are flags to revert fixes of erroneous or legacy behaviors during a grace period. While these flags are still available, their default values are now set to the *fixed behavior*. That means you've to set it to the former default explicitly, if you need to do so, as you rely on the former behavior, and don't have the time to fix that now.

Fix your code asap, as the flag will be removed with the next major release.

| Flag | Fixed erroneous behavior | Was | Since |
| --- | --- | --- | --- |
| ieee754compatible1 | Inconsistency b/w SQLite (dev) and HANA (prod) with regard to *Decimal* and *Int64* values. | false | [Jun 24](./../2024/jun24#new-option-cds-features-ieee754compatible) |
| compat_srv_getters | Wrong ability to call [srv.entities](/docs/node.js/core-services#entities) with namespaces. | *true* | [Dec 25](./../2025/dec25#cleaned-up-model-reflection-apis) |
| compat_texts_entities | Generated [.texts](/docs/node.js/cds-reflect#texts) entries in [srv.entities](/docs/node.js/core-services#entities). | *true* | [Dec 25](./../2025/dec25#cleaned-up-model-reflection-apis) |
| legacyLocking | Outbox caused long-lived database locks. | *true* | [May 25](./../2025/may25#more-efficient-locking) |

1 On *SQLite* and *PostgreSQL* only; no change for *HANA*, which always worked the new way. => The new default ensures consistency across all databases, and prevents potential data loss or corruption due to the old erroneous behavior.

#### Flags Entirely Removed ​

The following flags already had the new behavior as default in cds 9, but you were still able to set the old value, to revert to the old behavior if needed. In cds 10, these flags are removed entirely, and if your project explicitly sets the legacy value, it will be ignored.

If you have any of these in your project, you must adjust now!

| Removed Flag | Fixed behavior | Was | Since |
| --- | --- | --- | --- |
| service_level_restrictions | Ignored `@requires` on local service calls | true | [May 25](./../2025/may25#service-level-restrictions) |
| consistent_params | Unclear `req.params` -> now always an array | true | [May 25](./../2025/may25#changed-structure-of-req-params) |
| compat_save_drafts | Draft `SAVE` handlers called on `PATCH` events | false | [Sep 25](./../2025/sep25#revised-fiori-support) |
| compat_assert_not_null | `ASSERT_MANDATORY` instead of `_NOT_NULL` | false | [Sep 25](./../2025/sep25#translated-error-messages) |
| calc_elements | Calculated elements not supported for drafts | false | [Feb 26](./feb26#calculated-elements-for-drafts) |

#### Are you affected? ​

Check the tables below for details on the relevant flags and their default values in *cds 10*, and whether your project is affected by any of these changes. If your project explicitly sets any of the flags listed in the "Flags Being Removed" table, you are affected and must adjust your code accordingly to avoid potential issues when upgrading to *cds 10*.

Run this in the root of your project to check for any of the flags listed below:

sh

```
grep -rn \
-e ieee754compatible \
-e compat_srv_getters \
-e compat_texts_entities \
-e legacyLocking \
-e service_level_restrictions \
-e consistent_params \
-e compat_save_drafts \
-e compat_assert_not_null \
-e calc_elements \
-e direct_crud \
package.json .cdsrc*.* .env 2> /dev/null
```

If that yields any results, check the relevant files and lines for the flags, and adjust them as needed, following the details in the tables above.

#### Try it now ​

To give you the chance to try out the new defaults and adjust your project accordingly, we already turned on the new defaults in *cds 9*, while keeping the old behavior available as opt-out via feature flags. This allows you to test your project with the new defaults and fix any issues before they become enforced with *cds 10*. Check the tables below for details on the relevant flags, and set them in your project configuration to opt in early:

.env file.cdsrc.yamlpackage.jsonproperties

```
# Flags with changed defaults
cds.features.ieee754compatible = true
cds.features.compat_srv_getters = false
cds.features.compat_texts_entities = false
cds.requires.queue.legacyLocking = false

# Flags entirely removed
cds.features.service_level_restrictions = true
cds.features.consistent_params = true
cds.features.compat_save_drafts = false
cds.features.compat_assert_not_null = false
cds.fiori.calc_elements = false
```

1
2
3
4
5
6
7
8
9
10
11
12
yaml

```
features:
  service_level_restrictions: true
  ieee754compatible: true
  consistent_params: true
  compat_srv_getters: false
  compat_texts_entities: false
  compat_assert_not_null: false
  compat_save_drafts: false
fiori:
  calc_elements: true
requires:
  queue:
    legacyLocking: false
```

1
2
3
4
5
6
7
8
9
10
11
12
13
jsonc

```
{
  "cds": {
    "features": {
      "service_level_restrictions": true,
      "ieee754compatible": true,
      "consistent_params": true,
      "compat_srv_getters": false,
      "compat_texts_entities": false,
      "compat_assert_not_null": false,
      "compat_save_drafts": false
    },
    "fiori": {
      "calc_elements": true
    },
    "requires": {
      "queue": {
        "legacyLocking": false
      }
    }
  }
}
```

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21

### CAP Java ​

Along with *cds 10*, CAP Java is planning to release the major version 5, which will support Spring Boot 4. To prepare for the next major version, please have a look at the preview of the [migration guide](/docs/java/migration#four-to-five). It lists deprecated APIs, which will be removed, and properties, for which default values will change. Please substitute your usage of deprecated APIs with the suggested replacements and adjust your properties to the future default values.

### CDS Language ​

#### Annotate with invalid target ​

The compiler typically emits a warning when an annotation cannot be applied because its target is invalid.

Starting with cds-compiler 6.5, an annotate statement for for one of the security related annotations `@restrict`, `@requires`, or `@ams` with an invalid (i.e. non-existing) target is an error.

cds

```
annotate com.sap.NotThere with @restrict: ...;
annotate com.sap.Books:notThere with @restrict: ...;
```

Compilation results in:

txt

```
Error: Artifact “com.sap.NotThere” has not been found
Error: Element “notThere” has not been found
```

Fix the error by providing the correct target, or by removing the `annotate` statement in case it has become obsolete.

## Vector Embeddings ​

The CAP Java runtime and the CDS compiler now come with enhanced support for [vector embeddings](/docs/guides/databases/vector-embeddings), ... CAP Node.js will follow soon.

### Now also for H2, SQLite, ... ​

You can now also use the built-in CDL [`Vector`](/docs/cds/types) type with [H2](/docs/guides/databases/h2) and [SQLite](/docs/guides/databases/sqlite) for local development, as well as with [PostgreSQL](/docs/guides/databases/postgres) (beta). In the past that was possible for SAP HANA only, which disallowed local development as soon you used `Vector` type in your models.

Along with the support for the type itself CAP Java now also supports related `CQL.cosineSimilarity` and `CQL.l2Distance` functions for similarity search and [Retrieval-augmented generation](https://en.wikipedia.org/wiki/Retrieval-augmented_generation) (RAG) with vector embeddings on all the four databases.

PostgreSQL Support in Beta

Using `Vector` types on PostgreSQL is currently in beta, and requires the [pgvector](https://github.com/pgvector/pgvector) extension installed with PostgreSQL.

### New Vector Embedding Function Beta ​

CAP Java now supports the [VECTOR_EMBEDDING](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-sql-reference-guide/vector-embedding-function-vector) function via `CQL.vectorEmbedding` to generate vector embeddings from text data directly in SAP HANA.

To generate vector embeddings on write in the database, you can define a calculated element [on-write](/docs/cds/cdl#on-write) using the `vector_embedding` function:

cds

```
extend Incidents with {
  @cds.api.ignore
  embedding : Vector(768) = vector_embedding(
    'Title: ' || title || ', Summary: ' || summary,
    'DOCUMENT', 'SAP_GXY.20250407'
  ) stored;
}
```

In Java queries, you can use `CQL.vectorEmbedding` to compute vector embeddings. For example, in a RAG scenario to enhance the context of a user query for the LLM, compute the vector embedding of the user query and use `CQL.cosineSimilarity` to find similar incidents based on their embeddings and add them to the request to the LLM.

Java

```
var userQuery = CQL.val("""
  Have we seen incidents with solar inverters this month,
  and how were they resolved?
  """);
var embedding = CQL.vectorEmbedding(userQuery, TextType.QUERY, "SAP_GXY.20250407");
var similarity = CQL.cosineSimilarity(CQL.get(Incidents.EMBEDDING), embedding);

Select.from(INCIDENTS).columns(
  i -> i.ID(), i -> i.title(), i -> i.summary(), i -> i.date(),
  i -> similarity.times(100).as("relevance")
).where(i -> similarity.gt(0.75))
.orderBy(i -> i.get("relevance").desc());
```

Local Testing with H2 and SQLite

On H2 and SQLite the `CQL.vectorEmbedding` function is emulated using local [ONNX](https://onnx.ai) embedding models, which can be added via [LangChain4j embeddings](https://github.com/langchain4j/langchain4j/tree/main/embeddings) for local testing.

[Learn more about vector functions in CAP Java.](/docs/java/working-with-cql/query-api#vector-functions)

## CDS Language ​

### Declarative Constraints GA ​

In [December 25](./../2025/dec25#declarative-constraints) we initially released [Declarative Constraints](/docs/guides/services/constraints#assert-constraint) – i.e., the new `@assert:` syntax – under Gamma status. With this release, they are generally available and production-ready. You can now use them in your projects with confidence, and fully rely on their stability and support.

As part of the GA release, we applied a minor fix to the way we handle error codes. For example, given the following constraint:

cds

```
@assert: (case
  when price is null then 'PRICE_MUST_BE_PROVIDED'
  when price

Before, the error code returned in case of violations was always `ASSERT`, regardless of the specific error. With the GA release, the error code is now correctly set to the value specified in the constraint definition, such as `PRICE_MUST_BE_PROVIDED` or `PRICE_MUST_BE_POSITIVE` in the example above.

### Extending Views with CQL Clauses ​

You can now extend view definitions with [CQL clauses](/docs/cds/cql) `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`, and `LIMIT`. For example, given the following view definition:

cds

```
entity BooksByGenre as select from Books {
  avg(stock) as avg_stock,
} group by genre.name;
```

... you could now extend it like that:

cds

```
extend BooksByGenre with
where title like '%of%'
group by author.name
having min(price) > 19.99;
```

If the base view already has a `GROUP BY` or `ORDER BY` clauses, the new elements specified in the extension will be appended to the existing clause.

If the base view already has a `WHERE` or `HAVING` clause, extending these clauses is currently not supported. We're thinking of supporting that by combinations with `AND` in an upcoming release.

### Extending Derived Enums ​

You can now add [enum](/docs/cds/cdl#enums) values to a derived enum type via [`extend`](/docs/cds/cdl#extend).

Example:

cds

```
type Colors : String enum { red; green; blue }
```

cds

```
type Colory : Colors;
extend Colory with enum { yellow }
```

The new color `yellow` is only available in `Colory`, but not in `Colors`.

## CAP Node.js ​

### New cds test Version 1.0 ​

The new version 1.0 of [`@cap-js/cds-test`](https://www.npmjs.com/package/@cap-js/cds-test) marks a sign of stability: it's here to stay and plays a major role in our portfilo of CAP products with long-term support. It comes with the following updates:

- Upgraded to latest Chai version 6.
- Added support for Vitest runner.
- Replaced Axios with Fetch API.

Check out the updated docs

Ensure to check out the [updated documentation](/docs/node.js/cds-test) to learn more about how to use the new version effectively in your testing strategy. Especially the [Getting Started](/docs/node.js/cds-test#getting-started) section has been significantly improved, as well as the [Best Practices](/docs/node.js/cds-test#best-practices) section.

(No) Breaking Changes

While we avoided any breaking changes, there are some edge cases with Jest, which is still widely used, but has unsolved issues, especially with ESM modules. => Ensure to check the [Deprecated APIs](/docs/node.js/cds-test#deprecated-apis) section – not only, but especially if you are using Jest.

### Upgraded to Chai 6 ​

The default assertion library is now the latest version 6 of [Chai](https://www.npmjs.com/package/chai). This version is used whenever you use the `expect` assertion function through [`cds.test.expect`](/docs/node.js/cds-test#expect):

js

```
const { expect } = cds.test
expect (42) .to.be.a ('number') .gt (41)
```

When used with Jest, [`cds.test.expect`](/docs/node.js/cds-test#expect) returns a built-in emulation of `chai.expect` that covers the most common matchers, but not all. This is because chai 6 is ESM based, and Jest still struggles with ESM modules. You can always install and use `chai` directly, of course, or use another assertion library of your choice.

### Featuring Vitest ​

You can now run tests with the [Vitest](https://vitest.dev/) framework, with [`cds.test`](/docs/node.js/cds-test) fully supporting it as a primary choice, while still maintaining compatibility with other test runners like [Jest](https://jestjs.io/), [Mocha](https://mochajs.org/), or [Node's built-in test runner](https://nodejs.org/api/test.html) – optionally through the `cds test` command, which provides a cleaner output.

For example, for the tests in [@capire/samples](http://github.com/capire/samples)...sh

```
git clone --recursive http://github.com/capire/samples
cd samples
npm install
```

These still work as before:

sh

```
node --test
cds test
npx mocha --parallel bookstore/test
npx jest --silent
```

sh

```
npx vitest --silent
```

sh

```
npx vitest --ui
```

Vitest as a primary choice

Vitest is a modern test runner built on top of Vite, designed for speed and developer experience, with a feature set comparable to Jest, and fully ESM compatible. If you're starting a new project, Vitest is a great choice; it also offers straightforward [migration paths](https://vitest.dev/guide/migration.html) for [Jest](https://vitest.dev/guide/migration.html#jest) and [Mocha](https://vitest.dev/guide/migration.html#mocha-chai-sinon) users.

[Learn more about Vitest's feature set.](https://vitest.dev/guide/features.html)

### Node-native Fetch API ​

We replaced all dependencies on 3rd party HTTP client libraries like [Axios](https://axios-http.com) in favor of using Node's native implementation of [Fetch API](https://developer.mozilla.org/docs/Web/API/Fetch_API) in all relevant packages and scenarios, including:

- Remote service proxies in `@sap/cds` -> reducing the need for Cloud SDK
- CLI commands in `@sap/cds-dk` that perform HTTP calls, e.g. `cds bind`
- HTTP shortcuts in `@cap-js/cds-test` (`GET`, `PUT`, `POST`, ...)

This change is **transparent to you** for all uses in remote service proxies and CLI commands, as these APIs are not directly exposed. Same applies to usages of the HTTP shortcut methods provided through [`cds.test`](/docs/node.js/cds-test#http-bound), which still have the same API and behavior as before, but are now implemented on top of the Fetch API instead of `axios`.

js

```
// Still works as before, but now implemented with Fetch API under the hood
const { GET, expect } = cds.test ('@capire/bookshop')
const { data } = await GET `/Books`
expect(data).to.have.length(5)
```

What about `cds.test.axios`?

Property [`cds.test.axios`](/docs/node.js/cds-test#axios) is still available, but deprecated, and with a subset of features only – mainly `axios.defaults`. Prefer using the new [`cds.test.defaults`](/docs/node.js/cds-test#defaults) property instead, which works in a similar way as `cds.test.axios.defaults` did:

js

```
const { defaults, axios } = cds.test
axios.defaults.auth = { username: 'alice' } // still works ...
defaults.auth = { username: 'alice' } // but prefer that
```

Stuck with `axios`?

Install `axios` explicitly as a project dependency if you need the full feature set of it. In that case, `cds.test.axios` will point to the installed `axios` instance, and HTTP shortcuts will automatically use `axios` instead of the emulation, as before.

Key Benefits

The removal of *Axios* is part of our ongoing efforts to minimize external dependencies and the associated security attack surface.

Fetch API is a modern, standard [Web API](https://developer.mozilla.org/docs/Web/API/), natively supported through the global [`fetch()`](https://nodejs.org/api/globals.html#fetch) function in Node.js since version 18. It offers a powerful and flexible feature set, including better support for streaming, consistent with browser environments.

### N/o Cloud SDK ​

( read this heading as: *"**Not only** Cloud SDK"* )

With the move to the [native Fetch API](#node-native-fetch-api), SAP Cloud SDK (which uses `axios` internally) is no longer a mandatory dependency for remote communication in development scenarios. Like in this example from the [Getting Started](/docs/get-started/bookshop#cap-level-integration) guide:

shell

```
cds watch bookshop
```

shell

```
cds repl
```

js

```
await cds.service.bindings
const CatalogService = await cds.connect.to ('CatalogService')
await CatalogService .read `ID, title, genre` .from `Books`
```

As long as given service bindings can be resolved from the process environment and use basic or no authentication, the CAP runtime's implementation of remote service proxies automatically uses Node's native [`fetch()`](https://nodejs.org/api/globals.html#fetch) function instead.

SAP Cloud SDK for Production and Hybrid Tests

Note though, that [`@sap-cloud-sdk/http-client`](https://www.npmjs.com/package/@sap-cloud-sdk/http-client) is still required for **production** or **hybrid** test scenarios that need to resolve service bindings via [BTP Destinations](hhttps://help.sap.com/docs/connectivity/sap-btp-connectivity-cf/destination-service) and/or use OAuth-based principle propagation. Hence, ensure to `npm add` it as a dependency to your project latest when [preparing for production](/docs/guides/deploy/to-cf#prepare-for-production).

## CAP Java ​

### Important Changes ❗️ ​

An Application Service no longer serves all protocols by default, but only `odata-v2` and `odata-v4`. To serve other protocols, or to serve all protocols as before, the new property `cds.protocols.defaults` can be used. Please check the [Protocol Configuration](#protocol-configuration) section below for details.

### New date/time Functions ​

CAP Java now also supports these [standard CQL date/time functions](/docs/guides/databases/cap-level-dbs#date-time-functions) to extract date and time components from a timestamp (in UTC), as well as functions to calculate durations:

- `date(x)` -> `yyyy-MM-dd` Date
- `time(x)` -> `HH:mm:ss` Time
- `years_between(x,y)` -> Int32
- `months_between(x,y)` -> Int32
- `days_between(x,y)` -> Int32
- `seconds_between(x,y)` -> Int64

The functions can be called via the `Value` interface, or via the `CQL` interface, like that:

java

```
Select.from("Travels").colums(
  t -> t.createdAt().date().as("date"),
  t -> t.createdAt().time().as("time"),
  t -> t.start().daysBetween(t.end()).as("days"),
  t -> CQL.monthsBetween(CQL.get("start"), CQL.get("end")).as("months")
);
```

These functions are guaranteed to be supported for all databases. The `*_between` functions are mapped to native SQL functions in SAP HANA and emulated for other databases.

### Protocol Configuration ​

Protocol annotations like `@odata`, `@hcql`, etc. now also support to specify the *path* for that protocol, which allows usages as shown in line 1 below, which is equivalent the more verbose variants 2 and 3 below:

cds

```
@odata: 'browse'
```

1
cds

```
@odata @path: 'browse'
```

2
cds

```
@protocols: ['odata'] @path: 'browse'
```

3

[Application Service](/docs/java/cqn-services/application-services)s serve only protocols `odata-v2`, `odata-v4` and `odata-x4` by default now, i.e. in case the protocol is not explicitly specified in the model via annotation. In previous versions, all available protocols have been served by default.

To restrict the list of protocols an Application Service is serving by default, use the new property `cds.protocols.defaults` and define a list of protocols:

application.yamlyaml

```
cds:
  protocols:
    defaults: ["odata-v4"]
```

To explicitly enable the previous behaviour of serving all protocols, the wildcard protocol `*` can be used as value in the new property `cds.protocols.defaults`.

Always specify protocols

Design [use-case specific services](/docs/guides/security/authorization#dedicated-services) and explicitly annotate the exposing protocols.

[Learn more about configuring protocols.](/docs/java/cqn-services/application-services#configure-path-and-protocol)

### 'Brownfield' Projects ​

The CAP Java documentation now has a [section](/docs/java/cap-plugins-in-spring-boot-apps) explaining how CAP Java's BTP integration features (aka. Calesi plugins) can be used in brownfield Spring Boot applications.

### Optimised Draft Deletion ​

After a Draft is activated the inactive version is deleted. So far, CAP Java used to perform a *cascading* delete of the inactive version. For deeply structured documents this cascading delete is an expensive operation. The implementation now performs a *flat*, non-cascading delete of all entities that are part of the draft document.

### Miscellaneous ​

- The MTX sidecar health check now uses a configurable timeout. Set cds.multitenancy.health-check.timeout to adjust the threshold for your environment. The default is 1s.

## CAP Plugins ​

### Change Tracking v2 ​

Version 2.0 of [@cap-js/change-tracking](https://github.com/cap-js/change-tracking) introduces a fundamentally new architecture for tracking changes. Instead of capturing changes at the service level, the plugin now tracks changes at the database level using **native database triggers** on *[SQLite](/docs/guides/databases/sqlite), [SAP HANA](/docs/guides/databases/hana), and [PostgreSQL](/docs/guides/databases/postgres)*.

This new approach delivers significant performance improvements and resolves long-standing issues with bulk operations, sorting, and change log consistency.

#### Performance Benefits ​

Median HTTP request duration measured on SAP HANA
(Logarithmic Scale)

| Scenario | Service Level (v1) | DB Triggers (v2) | Improvement |
| --- | --- | --- | --- |
| Simple column update | 328 ms | 136 ms | ~**2.4x** faster |
| Update with 1000 children | 54.900 ms | 1.090 ms | ~**50x** faster |

#### Tree Table Visualization ​

The change history is now displayed in a [Tree Table](/docs/guides/uis/fiori#hierarchical-tree-views) that provides a hierarchical view of changes across parent and child entities. The depth of displayed child changes can be configured via the cds.requires.change-tracking.maxDisplayHierarchyDepth. The default is `3`.

#### CDS Expression Language in Annotations ​

The `@changelog` annotation now supports [CDS Expression Language (CXL)](/docs/cds/cxl), enabling broader customization of object IDs and changelog labels.

cds

```
annotate Books {
  author @changelog: (author.firstName || ' ' || author.lastName)
}
```

#### Further Improvements ​

- Search now works on all columns of the change log table
- The `@Common.Timezone` annotation on properties is now considered in the change log
- Change values are now dynamically localized when pointing to localized properties from code list entities, meaning that if for example a status column is tracked and the status name is shown in the change log, the name will dynamically adjust based on the users language if the name is a localized property
- Large string field values are automatically truncated
- Decimal values are now formatted correctly
- The change history section is hidden in draft mode
- `disableCreateTracking`, `disableDeleteTracking` and `disableUpdateTracking` now apply correctly to composition entities, not just root entities

#### Schema Changes and Migration ​

Version 2 introduces breaking changes to the underlying schema. The `ChangeLog` table has been removed and its columns have been merged into `Changes`, which received further structural modifications as well. If you are upgrading from version 1, a database migration is required.

For SAP HANA deployments, a detailed migration plan including a HANA migration table is provided. Read the [migration guide](https://github.com/cap-js/change-tracking/blob/main/MIGRATION.md) in the @cap-js/change-tracking repository for more information.

[Learn more about the Change Tracking Plugin.](/docs/plugins/#change-tracking)

### Attachments ​

#### cds-feature-attachments (Java) ​

- The OSS variant of the plugin now supports multitenancy via shared S3 buckets.
- The size of uploads can now be restricted via `@Validation.Maximum`.
- The type of uploads can now be restricted via `@Core.AcceptableMediaTypes`.
- Attachments are now also checked for malware on downloads, in addition to uploads.
- Integration with Malware Scanning Service now supports mTLS authentication.
- New `ScanStates` entity enables enhanced display of scan status, including criticality.

#### @cap-js/attachments (Node.js) ​

- File names are now automatically deduplicated ensuring multiple uploads of the same file yield unique file names.
- If used in combination with `@cap-js/audit-logging`, security relevant events (attachment download rejected, attachment size exceeded, attachment upload rejected) are automatically emitted as audit logs.
- The attachment service now has a programatic API to copy attachments using native object storage APIs.

js

```
const AttachmentsSrv = await cds.connect.to("attachments")
await AttachmentsSrv.copy(
  sourceAttachmentsEntity,
  sourceKeys,
  targetAttachmentsEntity,
  (targetKeys = {}),
)
```

[Learn more about the Attachments Plugin.](/docs/plugins/#attachments)

### New: Print Service ​

The Node.js plugin `@cap-js/print` is released as an initial version. It provides print service features through integration with the [SAP Print Service](https://api.sap.com/api/PRINTAPI/overview).

[Learn more about the Print Plugin.](https://github.com/cap-js/print)

### New: Workflows / SBPA ​

The Node.js plugin `@cap-js/process` is released as a first beta release. It can be used to interact with SAP Build Process Automation. It can be used to manage the lifecycle of processes and to retrieve information on running and finished processes.

[Learn more about the Process Automation Plugin.](/docs/plugins/#sap-build-process-automation)
