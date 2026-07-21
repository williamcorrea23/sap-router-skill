<!-- mirror: https://cap.cloud.sap/docs/releases/2023/jun23 -->
<!-- fetched: 2026-05-09T02:26:38.145Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# June 2023 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Mandatory Prerequisites ❗️ ​

Major Release

The June 2023 release comprises **major release** updates of [CAP Java 2](#java), as well as [CAP Node.js 7](#node-js). While we kept breaking changes to a minimum as much as possible, please pay attention to the information in the subsections below, as well as to the *Important Changes* sections in the subsequent chapters!

#### Upgrade to Node.js 18 ​

Node.js 14 is out of maintenance and cds 7 requires Node.js 16 minimum. So, ensure to upgrade your Node.js installation. Recommended is Node.js 18, which is the latest LTS version currently. Node.js 16 is not recommended as it reaches end of life already in September 2023.

[Download Node.js LTS version](https://nodejs.org)[See also: CAP Release Schedule](./../schedule)

#### Upgrade to Java 17 ​

For Java projects using the new [CAP Java SDK 2](#java2), an update to Java 17 is mandatory.

Note: In SAP Business Application Studio, this needs to be triggered explicitly using the command *Java: Set Default JDK* (press F1 to find it).

#### Upgrade to cds-dk 7 ​

`@sap/cds` 7 requires `@sap/cds-dk` 7, so make sure to update it with

sh

```
npm i -g @sap/cds-dk
```

#### Use cds-serve as Start Script ​

Prior to cds 7 there was a conflict with the `cds` executables from `@sap/cds` and `@sap/cds-dk`. To resolve this, we renamed the executable provided by `@sap/cds`, which is mainly used in npm start scripts, into `cds-serve`. So, make sure to change `cds-serve` in your start scripts instead of `cds run` from now on, for example:

json

```
"scripts": {
  "start": "cds run"
  "start": "cds-serve"
}
```

Note: with `@sap/cds-dk` installed, you'd continue to use `cds run` or `cds serve` on your command line as the preferred way.

#### Upgrade VS Code plugins ​

Ensure your VS Code plugins are upgrade. In particular the [SAP CDS Language Support extension](/docs/tools/cds-editors#vscode) has to be on latest version. Usually that happens automatically, and you only need to confirm to restart.

#### Migrate to @sap/cds-mtxs ​

The old MTX package `@sap/cds-mtx` was deprecated with cds 6, and is no longer supported with cds 7. So, in order to use cds 7, you need to use the new MTX services package `@sap/cds-mtxs` for multitenant applications.

[Learn more about migrating to `@sap/cds-mtxs`.](/docs/guides/multitenancy/old-mtx-migration)

## Revamped Guides ​

#### New Database Guides ​

We thoroughly overhauled and updated our [database guide](/docs/guides/databases/index), adding content that was missing so far. Moreover, we added dedicated guides for SAP HANA Cloud, as well as the new SQLite Service and PostgreSQL Service.

#### Renovated Node.js Reference Docs ​

Several Node.js reference documentations have been renovated and complemented, such as:

- The cds Facade
- Class cds. Service
- Class cds. ApplicationService

## CDS Language ​

### Important Changes ​

Here we list only the most prominent changes. The full list can be found in the changelog.

#### Default String Length ​

The default length for type `cds.String` has been changed from `5000` to `255` for all database dialects except for `hana`.

Omitting the string length is meant for rapid prototyping. For production, the length should always be specified. The default of `5000` is the largest possible length for NVARCHAR fields in SAP HANA. On other (row-based) databases, this length might have detrimental effects on performance.

The default string length can be controlled with a configuration option:

package.json.cdsrc.jsonjson

```
{
  "cds": {
    "cdsc": {
      "defaultStringLength": 5000
    }
  }
}
```

json

```
{
  "cdsc": {
    "defaultStringLength": 5000
  }
}
```

#### Table Aliases in Extends ​

When extending a view or projection with new select items, it's no longer possible to use the table alias of the base entity.

Example:

cds

```
entity Base { key id: Integer; }
entity P as select from Base as b { id };
```

The table alias `b` is no longer visible in an extension:

cds

```
extend P with columns { b.id as bid }  // error
```

Prefixing elements with the table alias isn't necessary, just remove it:

cds

```
extend P with columns { id as bid }
```

This change was necessary as a table alias should be an implementation detail of the basic view definition and shouldn't be visible anywhere else. In addition, the change avoids potential name resolution ambiguities if `Base` is extended with a structured element `b`.

#### Identifiers with $ ​

Your identifiers should not start with `$`. This is now enforced for table aliases and mixin names. For them, you can simply choose a different name, as they're local to the respective view/projection definition. The reason for this change is to avoid unexpected name resolution effects in combination with built-in `$`-variables.

#### type of with Association Path ​

Element type references can no longer follow associations. For example, it is no longer possible to write the following:

cds

```
entity Books {
  // ...
  authorName : type of author.name;
}
```

You have to refer directly to the element in the target entity:

cds

```
entity Books {
  // ...
  authorName : Authors:name;
}
```

### Calculated Elements ​

Warning

Calculated elements are released as **beta** feature. They're brand new, and we want to keep the possibility to gather feedback and do some adjustments, if necessary. We don't expect major changes in the functionality, though, and plan to remove the beta tag in one of the next releases.

Calculated elements "on-read" were already introduced in the [March Release](./march23#calculated-elements-beta), so far to be used only in views or projections. With the current release, we add the following functionalities:

- usage in ad-hoc queries in the Java runtime
- "on write" variant of calculated elements (also called "stored" calculated elements)

#### Java Support for Calculated Elements (On-Read) ​

The Java runtime now supports using calculated elements in ad-hoc queries.

cds

```
service Register {
  entity People : cuid {
    lastName  : String(30);
    firstName : String(30);
    fullName  : String = firstName || ' ' || lastName;
    upperName : String = upper(fullName);
  }
}
```

Although the values of calculated elements aren't persisted, they can be used in ad-hoc queries at runtime in Java just like ordinary elements:

java

```
Select.from(PEOPLE).columns("fullName", "upperName");
```

The Java runtime substitutes them with their defining expression:

sql

```
SELECT firstName || ' ' || lastName as fullName,
       upper(firstName || ' ' || lastName) as upperName FROM People
```

Support in the Node.js runtime is on the roadmap.

Tip

Always specify the type of a calculated element as the type is not computed automatically.

#### Calculated Elements On-Write ​

In addition to the calculated elements "on-read" introduced in the March release, CDS now also supports calculated elements "on-write", so called "stored" calculated elements. The computed values are stored in the database and thus can improve performance, in particular when used for sorting or filtering.

Define a calculated element "on-write" with the keyword `stored`. Parentheses around the expression are optional, a type specification is mandatory:

cds

```
entity People {
  lastName : String;
  firstName : String;
  fullName : String = (firstName || ' ' || lastName) stored;
}
```

Calculated elements "on-write" are implemented by using the respective database feature. For SAP HANA, the following table is created:

sql

```
-- SAP HANA syntax --
CREATE TABLE Register_People (
  lastName NVARCHAR,
  firstName NVARCHAR,
  fullName NVARCHAR GENERATED ALWAYS AS (firstName || ' ' || lastName)
);
```

Using calculated elements "on write" in ad-hoc queries is possible both in the Java and in the Node.js runtime.

[Learn more about Calculated Elements.](/docs/cds/cdl#calculated-elements)

### Annotated Return Types ​

It's now possible to annotate the `returns` of an (bound or unbound) action or function. The annotation can be provided directly in the action/function definition:

cds

```
service SomeService {
  entity SomeEntity {
    key id: Integer;
  } actions {
    action boundAction() returns @Core.MediaType: 'application/json' LargeBinary;
  };
  action unboundAction() returns @Core.MediaType: 'application/json' LargeBinary;
};
```

Or it can be assigned via the `annotate` statement:

cds

```
annotate SomeService.SomeEntity actions {
  boundAction returns @Core.MediaType: 'application/json';
};
annotate SomeService.unboundAction with returns @Core.MediaType: 'application/json';
```

[Learn more about Annotations.](/docs/cds/cdl#annotations)

## Node.js ​

### Important Changes ​

Following are potentially breaking changes you should take notice of...

### Changed Default Service Path ​

By default, each service is served at an endpoint including a protocol prefix. The `AdminService` is now served at `/odata/v4/admin` instead of `admin`. Consumers of endpoints, like SAP Fiori Elements applications, might need to be adjusted.

[Learn more about the reason of this change.](#protocols)

#### Removed Service-Level Checks for Referential Integrity ​

This effects `cds.features.assert_integrity` = **`app`** . This feature had been [deprecated since cds6](./../2022/jun22#db-constraints), and announced to be removed with cds 7 → please use [database constraints](/docs/guides/databases/cdl-to-ddl#database-constraints) and/or [`@assert.target`](/docs/guides/services/constraints#assert-target) instead.

#### Removed Audit Logging ​

In the course of modularization, the audit logging implementation of `@sap/cds` has been factored out into a separate package `@sap/cds-audit-logging` (to be released soon).

#### Deprecated OData Flavor x4 ​

This affects usages of config settings `cds.odata.flavor` and `cds.odata.structs`. Don't use these anymore, and we'll likely remove them with the next major release. Reason: This feature is used very rarely, if at all, while creating lots of efforts and runtime overhead.

#### Removed Unofficial Features ​

- Method `req.run()` → use `cds/srv.run()` instead.
- Methods `req.getUriInfo()` and `req.getUrlObject()`
- Config option `cds.env.features.bigjs`
- Config option `cds.env.features.parameterized_numbers`
- Config option `cds.env.features.cds_tx_protection`

#### See Also ​

- Serving Multiple Protocols
- Simplified Handlers

### New Database Services ​

With cds 7, new database services for SQLite and PostgreSQL are released (new SAP HANA Service will follow soon), which are based on an entirely new database service architecture. The new services are implemented in new open source packages as follows:

| Database | Implemented In | Learn More |
| --- | --- | --- |
|  | [`@cap-js/sqlite`](https://npmjs.com/package/@cap-js/sqlite) | [New SQLite Service](/docs/guides/databases/sqlite) |
|  | [`@cap-js/postgres`](https://npmjs.com/package/@cap-js/postgres) | [New PostgreSQL Service](/docs/guides/databases/postgres) |

Maximized Portability

A main advantage of the new database architecture and the new services is maximized feature parity and portability. For example, we've extensive and equal support for **path expressions** with or without infix filters, for all databases. Similarly a set of standardized functions is now supported in a portable way.

This gives you enhanced test coverage with SQLite, as well as allowing to switch to other databases, for example from PostgreSQL to SAP HANA, when your project grows.

Warning

We strongly encourage you to start migrating to and using the new database services as soon as possible. We were able to keep breaking changes to a minimum, mostly affecting undocumented behaviour. We tested them thoroughly, also with customers' test suites. Nevertheless, they're in their very first release, of course... **carefully read the migration guides** for that reason.

### New Packages ​

To further modularize `@sap/cds`, as well as simplifying dependencies, new packages have been introduced:

- `@sap/cds-fiori` contains SAP Fiori-related code like the Fiori preview.
- `@sap/cds-hana` contains SAP HANA-related code, with dependency to the `hdb` driver.

Recommendation

While you don't need to act immediately, we strongly recommend adding both packages to your package dependencies and remove direct dependencies to the `hdb` driver, if you use SAP HANA or SAP Fiori. This likely will become mandatory in future versions.

### Lean Draft ​

With cds 7, draft handling for SAP Fiori Elements was reimplemented thoroughly.

The following improvements simplify the handling of draft entities drastically:

- All draft sibling entities are now fully compliant CSN entities. Previously, they were only an overlay of the original entity. This allows a clear separation of logic for drafts and active instances. If you used `req.query` or implemented against `$filter` patterns of SAP Fiori Elements to find out the targeted entity, using lean draft simplifies this drastically.js

```
// As an example, you can differentiate now which handlers are run for active and draft instances
srv.after("READ", MyEntity, () => {});
srv.after("READ", MyEntity.drafts, () => {});
```
- It also provides better performance as the new implementation doesn't generate expensive `UNION` SQL statements, which are hard to optimize by the databases.

For easier adoption, we also provide a compatibility mode `cds.fiori.draft_compat = true` that reduces adoption effort to a minimum. Be aware, that this is a compatibility mode that will be dropped in the next major release.

[Learn more about the new lean draft implementation.](/docs/node.js/fiori#draft-support)

Lean Draft is enabled by default...

If that creates problems, you can still disable it via `cds.fiori.lean_draft = false`, though. Yet, as the [New Database Services](#new-database-services) are cleaned up of any draft-related code, they require Lean Draft, or not using Draft at all.

### Plugins ​

The [new plugins technique](/docs/node.js/cds-plugins) allows to provide plugin packages, that automatically plug in to cds including auto-wiring required configurations. For example, the new database services auto-wire themselves, when you install them:

sh

```
npm add @cap-js/sqlite
```

[Blog post about reusable components for CAP with cds-plugin.](https://blogs.sap.com/2023/04/30/reusable-components-for-cap-with-cds-plugin/)[Blog post about reusable plugin components for CAP Java applications.](https://blogs.sap.com/2023/05/16/how-to-build-reusable-plugin-components-for-cap-java-applications/)

### Protocols ​

#### Serving Multiple Protocols ​

Prior to cds7 you already were able to specify the protocol, but each service was served through a *single* protocol only, at a *single* service endpoint mounted at `/`:

cds

```
@protocol: 'rest'
service AdminService { ... }
```

AdminService is served at `/admin`

With cds7, services can be served via multiple protocols, as follows:

cds

```
@protocol: ['odata-v4', 'rest']
service AdminService { ... }
```

AdminService is served at `/odata/v4/admin` as well as at `/rest/admin`.

#### New Protocol-Specific Service Endpoints ​

Serving services via multiple protocols, requires separate endpoints with protocol prefixes, for example, `/odata/v4/admin` and `/rest/admin` in the example above. Other advantages of that include avoiding conflicts with static resources served at `/` or `/admin/webapp/...`.

Breaking Change

The new service endpoints may pose a breaking change to your applications. For example this is the case if:

- When using OData v2 proxy version `

Prefer the new path scheme

While we provide the compat options as indicated above, you should prefer switching to the new endpoint scheme as soon as possible, as the old one should be regarded as **deprecated**, and will likely be removed in future.

#### Configuring Protocols ​

With the new major version, the framework does not need to bring the configuration for each protocol. Protocol adapters like [`@cap-js/graphql`](https://github.com/cap-js/graphql/blob/main/cds-plugin.js) register themselves using the [`cds-plugin` mechanism](/docs/node.js/cds-plugins).

cds-plugin.jsjs

```
const cds = require('@sap/cds')
const protocols = cds.env.protocols ??= {}
if (!protocols.graphql) protocols.graphql = {
  path: "/graphql", impl: "@cap-js/graphql"
}
```

Additional custom protocols can use the same mechanism to make the framework aware of itself. Applications can simply refer to these protocols using the `@protocol` annotation.

[Learn more about the new protocol configuration.](/docs/node.js/cds-serve#cds-protocols)

### Simplified Handlers ​

From now on, the `result` argument of after handlers is always an array.

**Before**, you always had to handle these three cases: no result, single object, and array of rows, frequently leading to code like that:

js

```
srv.after('READ', Books, result => {
  if (!result) return
  if (!Array) result = [result]
  for (let each of result) // ... do something with each
})
```

**Now**, as `result` is always an array, this reduces to:

js

```
srv.after('READ', Books, books => {
  for (let each of books) // ... do something with each
})
```

That change is mostly nonbreaking, as most anyways had to support all three cases.

In the very rare cases you may need to differentiate whether the incoming request was addressing a single entry or a collection. Use `req.query.SELECT.one` to do so.

### Miscellaneous ​

- With the major version, SAP Cloud SDK version 3 is required. Version 2 is out of maintenance. Be aware, that this requires adding an additional dependency `@sap-cloud-sdk/resilience`.
- By default, only primitive strings are searched when using `$search` query option. If columns using expressions should be searched, use the annotation `@cds.search`.
- If a custom handler implements `$search` itself, `req.query.SELECT.search = undefined` must be set to undefined instead of using the `delete` keyword.
- All requests for handling of stream metadata (data type, filename, etc.) is handled on application service level instead of protocol adapter level, as streaming is a generic application service feature.

## Java ​

### Important Changes ​

#### New Major 2.x ​

This release brings the new *major* version CAP Java 2.0. Find a step-by-step instruction to upgrade in the [migration guide](/docs/java/migration#one-to-two). Stay up to date and benefit from latest and greatest features by migrating to `2.0.x`.

The following changes are especially noteworthy:

- CAP Java 2.0 requires minimal Java 17
- API Cleanup: Some interfaces, methods, configuration properties and annotations, which had already been deprecated in 1.x, are now removed in version 2.0.
- In some areas the behavior has changed, which might be observable. For example refs are now immutable, and the handling of `NULL` values in results has changed.
- It's no longer possible to navigate from one draft document to a different draft document in inactive state.

Warning

Be aware that cds-services `1.34.x` and cds4j `1.38.x` are now in [maintenance](./../schedule#maintenance-status) mode and only receive critical bugfixes. All cds-services versions below `1.34.x` won't be fixed anymore.

### Spring Boot 3 ​

txt

```
. .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v3.0.7)
```

CAP Java now runs with Spring Boot 3, which brings a number of great benefits:

- Leveraging JDK 17 (baseline) and JDK 19 language features.
- Latest Spring Framework 6, Jakarta EE 9 and Tomcat 10.1 capabilities.
- New Observability API to provide metrics and traces for OpenTelemetry.
- GraalVM Native Image support that allows compiling applications to native executables.
- Experiment with virtual threads and gain initial experience.

Warning

Spring Boot 2.7 runs out of OSS support in November 2023.

### OData: $count in $expand ​

The OData V4 adapter now supports the [$count](https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358955) system query option in `$expand`.

http

```
GET http://host/service/Authors?$expand=Books($count=true;$top=3)
```

The `$count` query option ignores the `$top` and `$skip` options, and returns the total count of results across all pages including only those results matching any specified `$filter` and `$search`.

The count is added to the response under the name of the navigation property suffixed with [@count](https://docs.oasis-open.org/odata/odata-json-format/v4.01/odata-json-format-v4.01.html#sec_ExpandedNavigationProperty):

json

```
{
  "Name": "Victor Hugo",
  "Books@count": 42,
  "Books": [ ... ],
  ...
}
```

Use `Authors?$expand=Books/$count` to count without expanding the entity.

### Simplified @After-Handlers ​

The result of `CRUD` events now can be easily injected as POJO argument in `@After`-handlers:

java

```
@After(event = CqnService.EVENT_READ)
public void afterReadResult(Result result) {
 Stream rows = result.stream();
 // ...
}
```

### Structured Event Messages ​

Added a new configuration property `structured` to the messaging service configuration. The default is set to `false`. If set to `true`, it enforces that plain strings are transformed into a structured representation.

Tip

**Note:** Setting `structured` to `true` might have an effect on the representation of the message in the broker.

Configuration example:

yaml

```
cds:
  messaging.services:
    - name: "messaging"
      kind: "enterprise-messaging"
      structured: true
```

The interface `MessagingService` provides a new method for emitting events with a data map and a headers map:

java

```
void emit(String topic, Map data, Map headers);
```

Example:

java

```
String topic;
MessagingService messagingService;

messagingService.emit(topic, Map.of("firstname", "John", "lastname", "Doe"), Map.of("timestamp", Instant.now()));
```

[Learn more about Enhanced Message Representation.](/docs/java/messaging#messages-representation)

## MTX Services ​

### Renovated Guide for Multitenancy ​

The [guide for multitenancy](/docs/guides/multitenancy/) has bean greatly improved.

### Simplified Configuration ​

Multitenancy and Extensibility can now easily be added using `cds add multitenancy` and `cds add extensibility`.

Example:

sh

```
cds add multitenancy
```

Adds package `@sap/cds-mtxs` to your project:jsonc

```
{
   "dependencies": {
      "@sap/cds-mtxs": "^1"
   },
}
```

Adds these lines to *package.json* to enable multitenancy with sidecar:jsonc

```
{
  "cds": {
    "profile": "with-mtx-sidecar",
    "requires": {
      "multitenancy": true
    }
  }
}
```

Adds a sidecar subproject at `mtx/sidecar`:json

```
{
  "name": "-mtx",
  "dependencies": {
    "@sap/cds": "^7",
    "@sap/cds-hana": "^2",
    "@sap/cds-mtxs": "^1.9",
    "@sap/xssec": "^3",
    "express": "^4",
    "passport": ">=0.6.0"
  },
  "devDependencies": {
    "@cap-js/sqlite": ">=0"
  },
  "scripts": {
    "start": "cds-serve"
  },
  "cds": {
    "profile": "mtx-sidecar"
  }
}
```

[Learn more about these facets.](/docs/guides/multitenancy/#enable-multitenancy)

The configuration for multitenancy uses static profiles `mtx-sidecar` and `with-mtx-sidecar`. This keeps the **configuration compact**.

For example, profile `mtx-sidecar` contributes the following configuration:jsonc

```
"[mtx-sidecar]": {
    requires: {
      db: {
        "[development]": { ...sqlite_mt, credentials: { url: "../../db.sqlite" }},
        "[production]": hana_mt,
      },
      "cds.xt.ModelProviderService": {
        "[development]": { root: "../.." }, // sidecar is expected to reside in ./mtx/sidecar
        "[production]": { root: "_main" },
        "[prod]": { root: "_main" }, // for simulating production in local tests
        _in_sidecar: true,
      },
      "cds.xt.SaasProvisioningService": true,
      "cds.xt.DeploymentService": true,
      "cds.xt.ExtensibilityService": true,
    },
    "[development]": {
      // requires: { auth: "dummy" }, -> We need authentication for push and pull requests
      server: { port: 4005 }
    }
  }
```

### Sidecar Also Default for Node.js ​

If a project is switched to multitenancy using `cds add multitenancy`, cds now always creates a sidecar module in folder `mtx/sidecar`, also for Node.js based projects.

[Learn more about the sidecar setup.](/docs/guides/multitenancy/#about-sidecar-setups)

### Improved Local Tests ​

The tenant upgrade can now also be triggered using the CLI:

sh

```
cds upgrade t1 --at http://localhost:4005 -u alice:
```

### Migration from Old MTX ​

For multitenant applications using `@sap/cds-mtx`, a migration to `@sap/cds-mtxs` is mandatory. Package `@sap/cds-mtx` is no longer supported with cds 7.

[See our migration guide](/docs/guides/multitenancy/old-mtx-migration)

## Toolkit / CLI ​

### Important Changes ​

- `cds deploy --to sqlite` no longer modifies `package.json`. The `--no-save` argument is no longer needed.
- `cds build/all` is no longer available. Use `cds build` instead.
- `cds build --for java` no longer supports the CAP Java Classic runtime. Migrate to the current CAP Java runtime version.

### Deploy Format hdbtable ​

In cds 7, we say goodbye to `hdbcds` as default deploy format for SAP HANA and use `hdbtable` instead. `cds build` now creates `hdbtable` and `hdbview` files by default.

jsonc

```
"cds": {
  "requires": {
    "db": "hana"
  },
  "hana": {
    "deploy-format": "hdbtable"
  }
}
```

In case you still need `hdbcds`

... configure it like that:

json

```
"cds": {
  "requires": {
    "db": {
      "kind": "hana",
      "deploy-format": "hdbcds"
    }
  }
}
```

### Improved cds env ​

- `cds env ` allows for a simpler querying of Node.js configuration options. The additional `get` subcommand isn't required anymore.
- The new `--keys` option of `cds env` lists the configuration keys only. For example, this shows all required services of a Node.js app:sh

```
cds env requires --keys
```
