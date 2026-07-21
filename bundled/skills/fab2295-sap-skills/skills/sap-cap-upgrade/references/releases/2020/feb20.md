<!-- mirror: https://cap.cloud.sap/docs/releases/2020/feb20 -->
<!-- fetched: 2026-05-09T02:26:21.357Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# February 2020 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

This release is primarily a quality and consolidation release. We invested much in improving our tests to minimize regressions as well as introducing [new release procedures](#new-release-procedure) and [new release notes](#new-release-notes).

With this release, it's the first time we formally document, and therefore officially release things that have been around before, without being announced. Hence, in the following you find an unusual comprehensive list of news.

## Important Changes❗️ ​

### Open SemVer Ranges in Node Dependencies ​

- From now on, our package dependencies use open ranges.We finally live up to our own guidelines as documented in Managing Dependencies. Besides other benefits, in the future we can publish new patch versions and minor versions of Node.js packages independently and more frequently.You can reliably use `npm outdated` and `npm update` to easily stay up-to-date.
- You don't have to react in your projects.Nevertheless, we strongly recommend paying attention to the guidelines about using open SemVer ranges, `npm-shrinkwrap`, and package-lock.json as documented in Managing Dependencies.

### Node.js Version ​

CDS no longer supports Node.js 8.x, as this version is now out of maintenance.

Check with `node --version` that you don't use Node.js 8.x. If you still have Node.js 8.x installed, uninstall it and install a newer version, preferably Node.js 12.x.

### New Release Procedure ​

Starting with this release, we adjust our release process as follows:

- We do monthly releases labeled as 'February 2020', 'March 2020', and so forth.
- A release is marked by published release notes, which also marks the official availability of the features documented in these release notes.
- At the same time, we may publish new versions of Node.js and Java packages. The packages can be published individually within the four-weeks cycle to npm, for example, to deliver hotfixes.

### New Release Notes ​

Also starting with this release, we introduce new release notes as in this format, which we hope gives you a better overview of what's new, structured by logical packages. You should always pay attention to the [Important Changes](#important-changes) sections in there.

### New Changelogs ​

Finally, from now on you always find a combined up-to-date changelog for all CAP packages. The first page contains all changes of all releases of the current year. Older changelogs are available through appended links.

### See also ​

- Important Changes in CDS
- Important Changes in Java
- Important Changes in Node.js

## Enterprise Features ​

### Localized Data ​

The CDL keyword `localized` allows to mark entity elements that require translated texts. See [Cookbook > Localized Data](/docs/guides/uis/localized-data) for more details.

### Temporal Data ​

The new aspect `temporal` allows marking an entity as *logical* records of information for which changes are tracked over time as *time slices* with from/to boundaries. See [Cookbook > Temporal Data](/docs/guides/domain/temporal-data) for more details.

### Managed Data ​

Use the annotations `@cds.on.insert` and `@cds.on.update` to signify elements to be auto-filled by the generic handlers. See [Cookbook > Generic Providers > Managed Data](/docs/guides/domain/index#managed-data) for more details.

## Command Line ​

Update your cds-dk: `npm i -g @sap/cds-dk`.

### Jumpstart with cds init ​

Use `cds init` to start new projects. The command's implementation has been cleaned up and streamlined to only do the most necessary setup. For example, there's no automatic `npm install` anymore, Java projects anyways should never need that.

`cds init` has been moved to `@sap/cds-dk` now.

Legacy: The former implementation had numerous other options, which we removed, yet you can restore them if needed short term. Just invoke `cds init` with one of these removed options to get instructions how.

### Grow as you go with cds add ​

The newly added command `cds add` allows to add new features to an existing project gradually, only when you need them. Currently supported are:

sh

```
cds add hana      # adds configuration for SAP HANA deployment
cds add mta       # adds an mta.yaml file out of CDS models and config
cds add pipeline  # adds files for CI/CD
```

### Accelerate with cds watch ​

Use `cds watch` to start a cds server, even in a newly created and yet empty project. Whenever you feed your project with new content, for example, by adding or modifying *.cds*, *.json*, or *.js* files, the server automatically restarts to serve the new content. --- Happy feeding.

### Use cds compile with --log-level Option ​

The newly added option `--log-level` allows to choose which messages to see. For example, use it as follows:

sh

```
cds compile srv --to sql --log-level warning #> also the default
cds compile srv --to sql --log-level error
cds compile srv --to sql --log-level info
```

## CDS Editors & Tools ​

The following features are available for all editors based on our language server implementation for CDS in SAP Business Application Studio, Visual Studio Code, and Eclipse. The plugins for Visual Studio Code and Eclipse are available for download at [https://tools.hana.ondemand.com](https://tools.hana.ondemand.com/#cloud-vscodecds).

### Code Formatting ​

Use the code formatting options, to beautify your code during the whole process or after you finished writing your code. This helps you and other contributors to have clean and consistent code throughout your project.

- How can I format code?You can format a whole file.Select the code you want to format. Enable Format On Type, to format a single statement immediately when you end a statement.Enable Format On Save, to have a pretty format each time you save your file.Enable Format On Paste, to format the pasted code.
- What are my options and how can I configure them?Get to know your configurable options.Use the .cdsprettier.json file to edit your projects preferences.Use the configuration UI to edit your projects preferences. This also edits the .cdsprettier.json file. You can access the configuration UI on three ways.Command: `CDS: Show Formatting Options Configuration`
- .cdsprettier.json file; right-click in explorer pane
- .cds source file, right-click in explorer paneUse comments in source code to override settings from your projects .cdsprettier.json file

- Where can I define my preferences? Is there a hierarchy?Comments overlay settings in .cdsprettier.json.cdsprettier.json in most specific source folder (least specific is project root).cdsprettier.json in User Home if none available in project

### Code Snippets ​

We added additional Code Snippets for `entity` and `extend` to the code completion. You get suggestions, reflecting the recent syntax and can add them using the code completion of your IDE.

### i18n Support ​

You can explicitly enable design-time support for translation.

Translation support includes quick fixes and direct navigation to translation.

Supported Files: *.properties*, *.json*, *.csv*

For translation support at design-time, use your settings from the *.cdsrc.json* file. This file can contain information on the basename, folder, default language, fallback language.

## CDS Language & Compiler ​

### Important Changes❗️ ​

- Timestamp precision for `createdAt` and `modifiedAt` --- Managed fields `modifiedAt` and `createdAt` defined in the `managed` aspect in `@sap/cds/common` changed from `DateTime` to `Timestamp`. While this is fully compatible to existing uses, it might break tests comparing ISO string representations. For example:

js

```
expect(x.modifiedAt).to.equal('2020-03-01T12:21:34Z')     // would break
expect(x.modifiedAt).to.equal('2020-03-01T12:21:34.000Z') // correct
```

### SAP HANA-Specific Data Types Beta ​

You can now specify native SAP HANA data types in CDL. For example:

cds

```
entity Foo {
    coord : hana.ST_POINT;
}
```

This isn't yet supported by the Node.js and Java runtimes.

### Preview: Streamlined Compiler Implementation ​

We streamlined the implementation of several compiler functions, especially compiler backends such as `2sql` and `2edmx`, which significantly improves performance, for example, up to factor 10 in several scenarios. As this improvement isn't yet the default, you can check it out by prepending `CDS_FEATURES_SNAPI=y` to your `cds` commands. For example:

sh

```
CDS_FEATURES_SNAPI=y cds watch   # speed up dev turn-around times
CDS_FEATURES_SNAPI=y npm test    # speed up your tests
```

### Auto-Exposed Association Targets ​

If a service exposes an entity and uses an association to refer to another entity, use `@cds.autoexpose` to automatically expose this entity. This is especially valuable for code list entities to be used in Fiori value helps.

[Learn more in CDS - Definition Language > Auto-Exposed Targets](/docs/cds/cdl#auto-expose)[See also `@sap/cds/common` > Code Lists](/docs/cds/common#code-lists)

### Auto-Redirection ​

When exposing related entities, associations are automatically redirected. If there's no clear redirection target, `redirected to` can be used to explicitly define one.

When associations are redirected, the `on` condition (and foreign key specification) is automatically adopted to reflect renamed element in the new association target. For complex cases, it's also possible to explicitly provide an `on` condition.

[Learn more in CDS - Definition Language - (Auto-) Redirected Associations](/docs/cds/cdl#auto-redirect)

### extend projection ​

Use `extend projection` to extend the projection of a view entity to include more elements existing in the underlying entity.

cds

```
extend projection Foo with {
  foo as bar @car
}
```

[Learn more in the CDL Reference documentation](/docs/cds/cdl#extend-view)

### extend with <named aspect> ​

`extend` can now be used to extend an entity with a named aspect instead of anonymous inline aspects only as before.

cds

```
extend Foo with Bar;
```

[Learn more in the CDL Reference documentation](/docs/cds/cdl#aspects)

### Association Filters ​

The compiler now supports `association filters`. An association filter is an 'ad hoc' extension to the defined ON condition of the association. This allows, for example, to express join-like things in a simple and elegant way:

cds

```
entity E {
    key id: Integer;
};

entity F {
    key id: Integer;
    field1: Integer;
};

view V as select from E JOIN F on E.id = F.id and F.field1 > 3 {
    E.id,
    F.id as F3id
};
```

This can be expressed with filters like this:

cds

```
entity E {
    key id: Integer;
    toF: Association to F;
};

entity F {
    key id: Integer;
    field1: Integer;
};

view V as select from E {
    id,
    toF[field1 > 3].id as toF3id
};
```

## Node.js Runtime ​

### Important Changes❗️ ​

This version brings a major refactoring and streamlining of service runtime implementations, which stays fully compatible regarding all documented APIs but in case you used internal not documented (non-)APIs, you have to know these changes:

Removed undocumented features:

- Annotation `@source` from models loaded for runtime
- Property `cds.serve.app` → use `cds.app` instead
- Property `source` from CSN entity/view definition objects

It's unlikely that you ever used these undocumented internal features at all. In case you did use these features, you need to fix that immediately.

Deprecated features (→ might get removed in upcoming versions):

- Property `cds.session` → use `cds.db` instead
- Property `cds.options` → use `cds.db.options` instead
- Property `cds.unfold` → use `cds.compile` instead
- Property `cds.config` → use `cds.env` instead

These properties actually were duplicates to the mentioned alternatives.

Also take note of the following changes:

- Using OData $search or the CQN `contains` function in a custom handler and HANA as a database, doesn't use the HANA fuzzy search feature anymore. Search queries are now translated to use the `LIKE` predicate.
- Previously values given for the managed fields `modifiedAt`, `modifiedBy` at INSERT and values given for `createdAt` and `createdBy` at UPDATE were ignored. Now, the values given for these managed fields are propagated independent of the query operation.
- To support replication scenarios, `null` is now persisted if given as value for managed fields (`createdAt`, `createdBy`, `modifiedAt`, `modifiedBy`) or fields annotated with `@cds.on.insert` and `@cds.on.update`. `Null` was previously filled with the value resulting from the annotation.
- The application user for the HANA session context is now set via `SESSION_CONTEXT('APPLICATIONUSER')` instead of `SESSION_CONTEXT('XS_APPLICATIONUSER')`.
- HTTP error codes are now normalized as strings based on the OData v4 standard. For example, `null` is now `'null'`.
- All referential integrity checks (for example, foreign key constraint checks) are now executed before the database commit. Previously, the integrity checks were executed before each request.
- The namespace of a required service for messaging can no longer be set outside of the credentials block in the package.json respectively .cdsrc.json file.

### Streamlined and Optimized Bootstrapping ​

Both the implementation of bootstrapping functions like `cds.serve()` and `cds.connect()` as well as the corresponding CLI commands have been thoroughly refactored and optimized to avoid loading models redundantly, thereby drastically improving both, bootstrapping performance as well as memory consumption.

- `cds run` and `cds watch` have been reimplemented as convenience shortcuts to `cds serve`, which acts as the central orchestrator for bootstrapping now.
- `cds serve` now uses `cds.load('*')` to load a single effective model once, assigned to `cds.model`, and reused for db as well as all provided and required services .
- `cds.resolve/load('*')` resolves or loads all models in a project including those models for required services. It's controlled and configurable through `cds.env.folders` and `.roots￼`. Try this in `cds repl` launched from your project root to see that in action:js

```
cds.env.folders         // = folders db, srv, app by default
cds.env.roots           // + schema and services in cwd
cds.resolve('*',false)  // + models in cds.env.requires
cds.resolve('*')        // > the resolved existing files
```
- See also Streamlined Compiler Implementation

### Support for local ./server.js ​

`cds serve` now optionally bootstraps from project-local `./server.js` or `./srv/server.js`. This option gives you more control while you can still benefit from `cds serve` options like `--in-memory` or `--with-mocks`.

Within your local `./server.js`, you can delegate to the default server.js implementation shipped with `@sap/cds`. For example:

js

```
// local ./server.js
const cds = require('@sap/cds')

cds.on('bootstrap', (app)=>{
  // add your own middleware before any by cds are added
})

cds.on('listening', ()=>{
  // add more middleware ...
})

module.exports = cds.server // delegate to default server.js
```

### Support for .env files ​

In addition to providing process environment variables in *default-env.json*, your can now also provide them in *.env* files in .properties format. For example:

properties

```
# .env file
CDS_FOO_BAR = foobar
```

sh

```
cds env  #> prints:
foo.bar = foobar
```

### Mocking Required Services ​

- `cds run/serve --with-mocks` mock all required services registered in your package.json or .cdsrc.
- `cds deploy --with-mocks` adds tables and views for all required services to a SQLite database.
- `cds serve --mocked` allows mocking individual required services.

### Media Types & Streaming ​

Elements of an entity can be annotated to indicate that they contain media data. The runtime offers generic streaming support for reading and creating/updating/deleting such resources.

[For more details, see Generic Providers > Serving Media Data](/docs/guides/services/media-data)

### Deep Reads & Deep Updates / Upserts ​

Structured documents represent the concept of relationships between entities, which can be modeled using compositions and associations. The runtime provides generic handlers for structured documents, covering DEEP READ (using `$expand`) as well as DEEP INSERT, DEEP UPDATE, and DEEP DELETE for compositions.

[For more details, see Generic Providers > Serving Structured Data](/docs/guides/services/served-ootb#deep-reads-and-writes)

### ETag-based Conflict Detection ​

You can enable optimistic concurrency control using ETags by applying the `@odata.etag` annotation.

[For more details, see Cookbook > Providing Services > Concurrency Control](/docs/guides/services/served-ootb#etag)

### Miscellaneous ​

- Added `cds.debug()` as a convenient helper for debug output controlled by `process.env.DEBUG`. For example, use it as follows:js

```
const DEBUG = cds.debug('my-module')
DEBUG && DEBUG ('my debug info:', foo, ...)
```

sh

```
> DEBUG=my-module cds run
```
- Added `cds.error()` as a convenient helper for throwing errors whose stack traces start from the actual point of invocation. For example, use it as follows:js

```
const {error} = cds
if (...) throw error `Something's wrong with ${whatever}`
const foo = bar || error `Bar is missing!` // short circuit exits
```
- Support setting of journal mode for SQLite through credentials.journalMode. This makes it possible to enable nonblocking queries by using write-ahead logs (WAL mode) and setting the maximum connection pool size to > 1 (default).
- Added support for OData Singletons.
- Enabled support for streaming with draft.
- Support for navigation in OData aggregate expressions. For example: `/Orders?$apply=aggregate(items/quantity with sum as TotalQuantity)`

## Java Runtime ​

### Important Changes❗️ ​

Timestamps are now persisted in UTC instead of the timezone of the application!

### OData V4 Support ​

We support OData V4 by default. Recently, we added the following features:

#### Filtering ​

We extended the support for filter capabilities (functions like `in`, `add`, `sub`, `mul`, and `div`), including support for null and path expressions in filters. In addition, `$filter` now supports the `contains`, `startsWith`, `endsWith`, and `substring` functions. You can also make use of the functions `tolower` and `toupper` in `$filter` expressions. For more details, see [Query Builder API - Expressions](/docs/java/working-with-cql/query-api#expressions).

#### Searching ​

We also support searching entities by means of the OData V4 `$search` parameter (including search expressions `AND`, `OR`, and `NOT`), see [Query Builder API - Filtering](/docs/java/working-with-cql/query-api#filtering).

### Authentication and Authorization ​

We support authentication and authorization using `@require` and `@restrict` annotations. For more details, see [Java - Security](/docs/java/security).

### Fiori Draft Support ​

You can now use associations to other draft-enabled entities. This enables path expressions to the inactive entity via the active entity and vice versa. Also in draft, compositions of second grade or higher for draft-enabled entities are supported.

### Service Consumption API ​

With the [Service Consumption API](/docs/java/services), we provide a facade around services and their events.

### CAP Java and Spring Boot ​

We have native Spring Boot integration in place, and in fact, this is now our default. See [Java > Getting Started](/docs/java/getting-started) and [Java - Stack Architecture](/docs/java/developing-applications/building). This enables you to make use of Springs autowiring and Spring Boots autoconfiguration features. In addition, if you want to make use of Spring's transaction management, this is integrated as well.

### Response Messages ​

You can make use of the `Messages` interface to return localized response messages. By modifying the `sap-message` header, you can influence the way error and info messages are shown in a Fiori UI. It's also possible to return multiple messages in a single response.

### Model Reflection API ​

Using the Model Reflection API, you can introspect the CDS model of an application and retrieve details on the services, types, entities, and their elements. See [Model Reflection API](/docs/java/reflection-api) for more details. Additionally, supported are: events, bound and unbound actions and functions, and Arrayed Types.

### Query Builder API ​

Using the Query Builder API, you can fluently construct [CDS Query Language (CQL)] statements, which can be handled by the persistence service or, on a lower level, be executed by the data store. See [Query Builder API](/docs/java/working-with-cql/query-api) for more details.

- The Query Builder API supports a list of predicates, such as: equals, not equals, greater, less, in, between, is null, isn't null, contains, starts with, ends with, and, or, and not. For more details, see Query Builder API > Expressions.
- The Query Builder API supports scalar functions, such as func, toLower, toUpper, plus, minus, substring, times, and dividedBy. See Query Builder API - Expressions for more details.

Support for mocking application users to use authorization in local development.

### Deep Reads & Deep Updates / Upserts ​

We started to make deep upserts available. To start using deep upserts. For more details, see [Query Builder API > Upsert](/docs/java/working-with-cql/query-api#upsert). Feel free to make an update with key values in data instead of where condition. See [Query Builder API > Update](/docs/java/working-with-cql/query-api#update) for more details.

### Miscellaneous ​

- Support for localized Data, see Cookbook > Localized Data
- Support for Actions and Functions, see Application Services > Actions
- Support `@path` to specify custom URL paths for CDS services
- Enable application configuration through `application.yaml` file
- Starter package `cds-starter-cloudfoundry` to bootstrap applications deployed on Cloud Foundry

## Fiori Support ​

### Fiori Preview ​

Add annotations to your model and quickly visualize the outcome.

This is only a preview and not a toolset from SAP Fiori.

## Database Support ​

### Streamlined cds deploy ​

- `cds deploy` does not (have to) register the default models to package.json anymore. For example, unlike before, `cds deploy -2 sqlite` will merely add an entry: `db:{kind:'sqlite'}`, without an additional `model` property anymore.

### cds deploy --to hana ​

- `cds deploy` - Deploy your data model to either SAP HANA or SQLite.

### cds deploy --dry ​

- `cds deploy --dry` prints DDL statements to stdout instead of executing them.

### cds deploy --with-mocks ​

- `cds deploy --with-mocks` adds tables for required services.

( → learn more about these things using `cds help ...` )

### Auto-Generated .hdbtabledata ​

The effort of adding an `.hdbtabledata` manually to your imported data (`.csv` files) is now taken care of by the build and deployment process, for example, in `cds deploy --to hana`.
