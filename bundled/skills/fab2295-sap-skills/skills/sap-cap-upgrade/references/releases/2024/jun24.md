<!-- mirror: https://cap.cloud.sap/docs/releases/2024/jun24 -->
<!-- fetched: 2026-05-09T02:26:44.236Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# June 2024 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## New Majors: cds8 & CAP Java 3 ​

The June 2024 release includes updates to the major versions, version 8 for Node.js (`@sap/cds` and `@sap/cds-dk`) and version 3 for Java. Along with these changes, we're also updating the minimum required dependencies. These include:

| Dependency | Required Version | Recommended |
| --- | --- | --- |
| **Node.js** | 18 | [20 (LTS)](https://nodejs.org) |
| **Maven** | 3.6.3 |  |

### (No) Breaking Changes ​

No breaking changes to public APIs

As usual, we've aimed to minimize breaking changes with the major updates as much as we could. In fact, we've succeeded in making **no breaking changes to public APIs**. However, there are a few changes to Node.js package dependencies that you should be aware of. These include changes to [Typescript declarations](#cds-types-dependency) and [the new database services](#new-database-services-ga). Also, [some features are deprecated](#deprecated-features) with cds8, and some previously [deprecated ones finally got removed](#removed-features).

Warning

There are changes to the internal implementation, of course. These might affect your applications if you used any undocumented features (**which you never should**). We tried to anticipate such situations and bring these to your attention in their respective sections below.

## Tools / CLI ​

### Mermaid Preview in VS Code ​

You can now visualize your CDS model as a diagram in VS Code. Use the dropdown in the title area of the CDS editor, or the command *CDS: Preview as diagram*:

[Learn more about the new Mermaid exporter that is used under the hoods.](/docs/tools/cds-cli#mermaid)

### New cds add Commands ​

#### Automate Containerization of Modules ​

To deployment of CAP applications to the SAP BTP Kyma Runtime or to a Kubernetes cluster, you have to containerize your modules can now be automated using the [CTZ cli](https://www.npmjs.com/package/ctz).

The new `cds add containerize` command generates a `containerize.yaml` file with all the configuration required to containerize your modules, according to the CTZ tool. After configuring your repository in the `containerize.yaml` file, you can use the below command to containerize all your modules:

sh

```
ctz containerize.yaml
```

[Learn more about the `ctz` command.](https://www.npmjs.com/package/ctz)

#### Add Audit Log and Attachments Configuration ​

You can now easily add the deployment configuration for `@cap-js/audit-logging` using:

sh

```
cds add audit-logging
```

Similarly, add the deployment configuration for `@cap-js/attachments` using:

sh

```
cds add attachments
```

#### Add Typescript Configuration ​

Add the typescript configuration to your CAP project using the command:

sh

```
cds add typescript
```

### Drafts in .http Scripts ​

Support for draft entities has been added to the `cds add http` and the `Generate HTTP Requests` VS Code command. If an entity is annotated with `@odata.draft.enabled`, then the commands generate requests that can display, edit and activate the drafts.

http

```
GET {{server}}/admin/Books?$filter=(IsActiveEntity eq false) HTTP/1.1
Content-Type: application/json
Authorization: Basic alice:
```

[Learn more about request generation](/docs/tools/cds-cli#http)

### cds deploy with --profile ​

If you use `--profile` when calling `cds deploy`, it now also resolves additionally binding information based on that profile's settings. If a corresponding binding exists its service name and service key will be used. The development profile is used by default.

### Miscellaneous ​

#### @sap/cds-dk 8 Requires @sap/cds 7 at the Minimum ​

This means that if you still use `@sap/cds` 6 or lower, you will get an error from `cds` CLI commands. To resolve this, upgrade to `@sap/cds` 8.

Only as a fallback, downgrade `@sap/cds-dk`.

Run this to globally install `@sap/cds-dk` in the previous version:

sh

```
npm install -g @sap/cds-dk@7
```

## CDS Language & Compiler ​

### Transitive Localized Views Removed ​

As explained in the [Localized Data guide](/docs/guides/uis/localized-data#localized-helper-views), localized views are created for entities with localized data, recursively. In previous releases this included also entities which don't have localized elements on their own, but only associations to such. This is what we call a *transitive* localized view.

With the [New Database Services](#new-database-services-ga) the Node.js runtime doesn't need these transitive localized views any longer (the Java runtime has been able to do without them already for quite a while). They have become obsolete and are no longer generated. This reduces the total number of database objects in your application and thus reduces (re-)deployment times.

Example: Entity `Authors` has no own localized data, but only an association to an entity with localized data. No localized view is generated for `Authors` any more.

cds

```
entity Books { ...
  title : localized String; // has own localized data
}
entity Authors { ...  // has no own localized data
  books : Association to many Books;
}
```

In case you should want to switch transitive localized views back on, use the configuration shown in [Deprecated Features](#deprecated-features) in the Node.js section below.

### Native HANA Associations ​

For SAP HANA, CDS associations are by default reflected in the respective database tables and views by *Native HANA Associations* (HANA SQL clause `WITH ASSOCIATIONS`).

These native associations are no longer needed for CAP:

- The CAP JAVA runtime used native associations only in very early versions.
- The new HANA database service in the CAP Node.js runtime doesn't need native associations, either.

Unless you explicitly use them in other native HANA objects, we recommend switching off the generation of native HANA associations, as they increase deploy times: They need to be validated in the HDI deployment, and they can introduce indirect dependencies between other objects, which can trigger other unnecessary revalidations or even unnecessary drop/create of indexes. By switching them off, all this effort is saved.

json

```
{
  "cds": {
    "sql": {
      "native_hana_associations": false
    }
  }
}
```

Note that the first deployment after this configuration change may take longer, as for each entity with associations the respective database object will be touched (DROP/CREATE for views, full table migration via shadow table and data copy for tables). This is also the reason why we haven't changed the default so far. Subsequent deployments will benefit, however.

### Association-like Calculated Elements ​

In previous releases we have introduced [Publishing Association With Filter](/docs/cds/cdl#publish-associations-with-filter) and [Association-Valued Calculated Elements](/docs/cds/cdl#association-like-calculated-elements) as beta features. They are now generally available without restriction.

In views or projections, you can publish an association with a filter. The ON condition of the resulting association is the ON condition of the original association plus the filter condition, combined with `and`. In this example, projection `P_Authors` has a new association `availableBooks` that points only to those books where `stock > 0`:

cds

```
entity P_Authors as projection on Authors {
  *,
  books[stock > 0] as availableBooks
}
```

Alternatively, you can define a filtered association already as a calculated element in the base entity:

cds

```
entity Authors : managed {
  key ID       : Integer;
  name         : String;
  books        : Association to many Books on books.author = $self;
  unavailableBooks = books[stock = 0];
}
```

### Deprecated --to hdbtable ​

Use the `cds compile --to hana` command instead of the deprecated command `cds compile --to hdbtable`. The CLI command uses the corresponding compiler method [`cds.compile.to.hana()`](/docs/node.js/cds-compile#hana). The produced `.hdbtable/.hdbview` output is identical.

### Miscellaneous ​

#### Deprecation of Deploy Format hdbcds ​

The deploy format `hdbcds` for SAP HANA is deprecated. Switch to the default deploy format `hdbtable` instead. This is not relevant for SAP HANA Cloud, where deploy format `hdbcds` could never be used.

[Learn more about Moving From .hdbcds To .hdbtable](/docs/cds/compiler/hdbcds-to-hdbtable)

#### Reject Non-assignable Annotations ​

Annotations can only be assigned to a definition (entity, type, ...) or its elements. Annotations in other locations have so far resulted in a warning and are now rejected with an error like "Annotations can't be used in a column with ‘.{ ‹inline› }’".

Example:

cds

```
entity PAuthors as projection on Authors {
    @Anno: 'I am misplaced'
    books.{*},
}
```

You can safely remove these annotations, as they didn't have any effect before.

#### No $self in ON Condition of join ​

In the *ON* condition of a *join*, references starting with `$self` are no longer allowed and will result in a compiler error:

"Referring to the query's own elements here might lead to invalid SQL references; use source elements only".

Use table aliases instead. With `$self` it was too easy to create invalid SQL.

Example:

cds

```
entity V as select from A join
  ( B join C on C.c = B.b + $self.a ) // error, use A.a instead
  on A.a = B.b;
```

#### No Definition Named $self ​

Defining an object (entity, type, ...) named `$self` is no longer allowed and will result in the compiler error "Do not use “$self” as name for an artifact definition". Reason: such an object causes conflicts with the special variable `$self` in some places.

cds

```
entity $self {  // error
  // …
}
```

#### OData: Entities Must Have a Key ​

Entities without key are illegal in OData and can lead to runtime errors that are hard to detect. The OData backend now raises the error "Expected entity to have a primary key" for such an entity, so that problems can be detected already at compile time.

You should fix your model accordingly. If this is not possible, you can downgrade the error to a warning or an info message:

package.jsonjson

```
{
  "cds": {
    "cdsc" {
      "severities": {
        "odata-spec-violation-no-key": "Warning"
      }
    }
  }
}
```

#### OData: Collections are Nullable by Default ​

When defining an array element without explicitly specifying `null` or `not null`, the resulting collection in OData now by default has `Nullable=true`. The reason for this change is to have a consistent default within CAP.

CDS:

cds

```
foo : Array of String;
```

EDMX:

xml

```

```

#### Localized Entities and @cds.persistence.exists ​

If you annotate an entity `ExistingEntity` containing localized elements with `@cds.persistence.exists`, then the compiler will now also generate the "localized" view `localized_ExistingEntity` on the database. If you have already defined this view yourself as a native database object, either remove your definition, or tell the compiler not to generate the view with

cds

```
annotate localized.ExistingEntity with @cds.persistence.exists: true;
```

#### Session Variables $at.from and $at.to are Deprecated ​

The session variables `$at.from` and `$at.to`, used in the context of [Temporal Data](/docs/guides/domain/temporal-data#serving-temporal-data), have been deprecated, as the names are misleading. Replace them by `$valid.from` and `$valid.to`, respectively.

## Node.js ​

### Important Changes❗️ ​

Please take notice of the following changes to internal APIs, which may break your code in case you relied on such undocumented behavior, or tests that compare result snapshots which include undocumented data.

- Optimizations in New Protocol Adapter
- Changed: VCAP filters are AND-ed now
- Disabled `index.html` in production
- Removed`cds.ql` 'quirks' mode
- Standalone `@cap-js/cds-types` package
- Improved Error Responses
- See also: Deprecated Features
- See also: Removed Features

### New Database Services (GA) ​

With *cds7* we started our journey to re-implement our database services based on a new database service architecture, which we conclude with cds8 with all currently supported databases (`@cap-js/sqlite`, `@cap-js/postgres`, `@cap-js/hana`) being **generally available** (GA) and the defaults.

For example, when creating new projects with `cds init` or when preparing for production with `cds add hana --for production`, the new database service packages are added, with the outcome looking like that in your package.json:

json

```
  "dependencies": {
    "@cap-js/hana": "^1"
  },
  "devDependencies": {
    "@cap-js/sqlite": "^1"
  },
```

There are many benefits of the new database services; highlights are:

- Various optimizations like using database-native JSON functions for deep queries in single roundtrips, user-defined functions and more, to push data-processing tasks down to the database (→ improves utilization).
- Maximized feature parity & consistency such that tests running with SQLite will run similar with SAP HANA. Learn more about this in the respective database guide: CQL Compiles to SQL, and Consistent Timestamps for SQLite.
- Full support for eliminating transitive localized views (see above), reducing number of views by ~50%, which in turn results in significant speedup of SAP HANA upgrades.
- Support for search on associated entities.

Open Source – contribution welcome!

All new database services are open source at [https://github.com/cap-js/cds-dbs](https://github.com/cap-js/cds-dbs). Feel free and be invited to file features requests, bug reports, fixes, pull requests there → **contributions are welcome**.

Former database implementations are deprecated...

While they are still supported with *cds8*, they will not receive new features anymore. For example, the [elimination of transitive localized views](#transitive-localized-views-removed) is not possible with the old implementations, as well as all the other improvements mentioned above.

Also expect the old implementations to be **less tested** over time, and be removed with *cds9* latest. → We strongly recommend to **use the new database services as soon as possible.**

#### Plug & Play – Don't Add Driver Packages ​

The new database service packages are implemented as *[cds-plugins](/docs/node.js/cds-plugins)* which makes them plug & playable. In particular that means you don't have to add any additional configuration like `cds.requires.db` (you still can of course).

More importantly: you don't have to add additional dependencies to database driver packages like `sqlite3`, `hdb` or `@sap/hana-client` → and we strongly recommend you to not do so, but leave the choice of the most suitable one to us, please. This especially applies to the choice of `hdb` vs `@sap/hana-client`.

Don't add driver packages yourself!

... but leave the choice of the most suitable one to us, please.

#### New Option cds.features.ieee754compatible ​

Set this option to `true` to force all `Decimal` and `Int64` data read from databases to be read as strings. For example given that model definition:

cds

```
entity Foo {
   dec : Decimal;
   i64 : Int64;
}
```

You can write data either by providing strings or numbers, including JavaScript bigints:

js

```
await INSERT.into('Foo').entries(
  { dec:  123.45,  i64:  12345  }, // plain numbers
  { dec:  123.45,  i64:  12345n }, // w/ bigints
  { dec: '123.45', i64: '12345' }, // w/ strings
)
```

When you read data as follows, it will always return strings:

js

```
let foos = await SELECT.from('Foo') //>
[
  { dec: '123.45', i64: '12345' },
  { dec: '123.45', i64: '12345' },
  { dec: '123.45', i64: '12345' },
]
```

Without this flag set to `true` the behavior is database-driver-dependent, as before: SAP HANA drivers return strings, SQLite returns numbers.

CAP doesn't *cause* precision loss, but cannot *avoid* it completely

Note that this flag merely consolidates the behavior across different databases. It does not *avoid* precision loss, because that requires databases with suitable native types. This is the case for SAP HANA and PostgreSQL, but not for SQLite. For SAP HANA and PostgreSQL you can avoid precision loss by sending strings for data input, and already today get back strings, when reading data through CAP, even without this flag set to `true`. CAP never *causes* precision loss, as we never convert given data to JavaScript numbers.

#### New Option cds.features.sql_simple_queries ​

Use this flag to opt out from always using json functions with the new database services as follows:

jsonc

```
{ "cds": {
  "features": {
   "sql_simple_queries": 0, // always use json functions (the default)
   "sql_simple_queries": 1, // use json functions only for expands and booleans
   "sql_simple_queries": 2, // use json functions only for expands
  }
}
```

Note: when choosing level 2, values for booleans read from the database are returned as `1` and `0` instead of `true` and `false`. So ensure to always use truthy / falsy checks or `==` instead of strict checks like `===` when using that option. In all cases, the responses to HTTP requests will have the correct `true` and `false` values, of course.

#### Removed cds.ql 'quirks' Mode ​

From now on, `cds.ql` as well as all protocol adapters, generate spec-compliant [`ref` paths](/docs/cds/cxn#references) in `INSERT`/`UPDATE`/`DELETE` [CQN](/docs/cds/cqn) objects. For example:

js

```
INSERT.into('Books')
```

... always returns spec-compliant CQN objects now:

js

```
{ INSERT: { into: { ref: ['Books']}}}
```

... instead of 'quirked' ones like that:

js

```
{ INSERT: { into: 'Books' }}
```

With this, all framework components and generic handlers can expect all CQN objects to be in spec-compliant, non-quirked shape.

### New Protocol Adapters (GA) ​

The new protocol adapters comprise completely re-implemented adapters for OData and REST. Main benefits are:

- Code base of `@sap/cds` is reduced by a factor of 2
- Model-related memory consumption reduced by more than a factor of 2
- Per-request overhead reduced drastically
- Requests / sec throughput expected to improve drastically

APIs and behavior relevant for CAP-based applications stay the same.

Former adapter implementations are deprecated...

While they are still supported with *cds8*. And you can keep using them instead of the new ones by setting config option

js

```
cds.features.odata_new_adapter = false
```

Note though, that the old implementations will not receive new features anymore. Also expect them to be **less tested** over time, and be removed with *cds9* latest. → We strongly recommend to **use the new adapters as soon as possible.**

#### Noteworthy Changes❗️ ​

- `@odata.context` in responses where optimized to only contain the mandatory minimum information required by the OData specification. For example it does not include which columns were selected.
- `$batch` requests are processed sequentially to avoid peak loads and thereby heating up all pool connections. We might introduce a configuration to allow some parallelization in future.
- `$search` arguments are captured as plain `val` in CQN objects and optimized for SAP HANA features and syntax. OData grammar compliance is not validated anymore.
- HTTP `401 - Unauthorized` responses for basic authentication don't contain a JSON `{error}` body anymore.

#### New Input Validation ​

As part of the new protocol adapters we also provide a complete reimplementation of our generic input validation, which provides the following improvements and changes over the former one:

- All input validation happen in one place now — type checks and input validations are done by `cds.validate()` in the service layer now. Before type checks were done in the old OData library, while `@assert` checks were done in the service layer, and returned in different partial responses.
- UUIDs are not checked for hyphens by default. This allows to easily work data from ABAP, without any workarounds like `@odata.Type:'Edm.String'` required any longer.
- Fixed `@mandatory` checks — `undefined` as a value is rejected now; it passed before.

Note: `not null` is a database constraint!

As before the CDS `not null` declaration is a database constraint, not an application-level one. It is ***not*** checked in `cds.validate()` but only on the database, with database-specific errors. Use [`@mandatory`](/docs/guides/services/constraints#mandatory) if you want application-level checks instead. Reason for that is that quite frequently applications want to fill in missing values in custom code before an INSERT or UPDATE, which would not be possible, if `cds.validate()` would reject such input before.

#### Improved Error Responses ​

The new protocol adapters come with new error middlewares which improve error analysis in development or in tests. This comprises better error messages, more error details, and included error stacks.

May break tests

If you tested error responses using `.to.equal({...})` these tests may break and have to be adjusted.

More to come... → adhere to the principle of minimal assumptions

Please expect more of such improvements of error details in upcoming minor releases. To avoid these to break your tests again and again, Please adhere to the recommended in the [Best Practices section of the `cds.test()` guide](/docs/node.js/cds-test#minimal-assumptions), to always test only a minimal set of significant properties.

### Fiori Drafts ​

#### Lean Draft as the Sole Implementation ​

Lean draft is now the only draft implementation, the old draft implementation, which was deprecated since cds7, is removed in cds8.

Deprecated `cds.fiori.draft_compat`

Compatibility for old-style handler registrations through the [`cds.fiori.draft_compat`](/docs/node.js/fiori#draft-support) flag is still available in cds8, but will be removed in upcoming releases.

#### Automatic Draft Garbage Collection ​

Outdated drafts are automatically deleted now after a no-touch period of **30 days**, which can be overridden thru the `cds.fiori.draft_deletion_timeout` config option like that:

package.jsonjson

```
{"cds":{
  "fiori": {
    "draft_deletion_timeout": "15d"
  }
}}
```

Values can be strings as in the example above, with suffixes `w`, `d`, `h`, `hrs`, `min`, or numbers specifying milliseconds.

### ESLint v9 ​

[ESLint 9](https://eslint.org/blog/2024/04/eslint-v9.0.0-released/) was released recently and introduced the new [flat config system](https://eslint.org/blog/2022/08/new-config-system-part-2/), which is incompatible to the former one. With cds8 we migrated to eslint9, which also allows us to simplify eslint configurations for all CAP-based projects as follows.

Simply add a file named `eslint.config.mjs` to the root of your project with the following content:

eslint.config.mjsjs

```
import cds from '@sap/cds/eslint.config.mjs'
export default [ ...cds.recommended ]
```

This enables the recommended rules for CAP-based projects and also includes recommended rules and settings for Node.js, and browsers. The browser settings are particularly useful for UI5 content enclosed in your CAP project. You can also add additional rules or override existing ones in this file as needed, of course, following standard eslint9 ways.

`cds init` does that by default

When starting new projects using `cds init`, this file will be created for you automatically. The additional package dependency to `@sap/eslint-plugin-cds` that was required in the past for this purpose is no longer needed.

### TypeScript ​

Following are changes in cds8 in our ongoing endeavor to enhance and improve support for CAP-based TypeScript projects...

#### Standalone @cap-js/cds-types Package ​

In December 2023 we introduced the [open-source `@cap-js/cds-types` package](./../2023/dec23#type-definitions-are-open-source), which contains all TypeScript declarations for `@sap/cds` APIs. While so far, we still had a hard package dependency from `@sap/cds` to `@cap-js/cds-types` — which also created unwanted overhead for pure JavaScript projects — we found a better loosely-coupled way now to achieve the same without that hard dependency.

All you have to do is to add an explicit dev dependency to your TypeScript project now:

sh

```
npm add -D @cap-js/cds-types
```

With that in place, both the TypeScript compiler, as well as VS Code editors will find the type declarations for the `@sap/cds` APIs.

Imports from `@sap/cds/apis/...` are no longer supported!

As a consequence of the above, always only import `@sap/cds` APIs, while imports from `@sap/cds/apis/...` were always wrong and don't work any longer with cds8:

ts

```
import { Service } from '@sap/cds'
import { Service } from '@sap/cds/apis/services' // WRONG!
```

Deprecated since December 23...

As already rolled out in [December 23](./../2023/dec23#type-definitions-are-open-source), imports references to undocumented `.d.ts` files, as in line 2 above, was never documented, hence always wrong. While we still supported them for a grace period since then, this grace period ends with *cds8*.

Contributions welcome!

The main reason we open-sourced `@cap-js/cds-types` was to allow you to easily contribute to that together with us and improve the TypeScript declarations. So, please be invited again to use all opportunities in that regard.

### Fixed req.user/tenant ​

We detected and fixed several erroneous usages of `express.Request.user` and `.tenant` in express middlewares. Please note: There's only one public and documented way to access user and tenant information through instances of `cds.EventContext`, which in turn includes all subclasses of which like `cds.Request` instances passed to event handlers, as well as `cds.context`.

For example, try this in `cds repl`:

js

```
srv = (new cds.Service).on('*', req => req.user)
srv.read(Foo) //> Anonymous {}
cds.context = {user:'me'}
srv.read(Foo) //> User { id: 'me' }
```

Alternatively, this would work as well, of course:

js

```
srv = (new cds.Service).on('*', req => cds.context.user)
```

NEVER use `express.req.user/tenant`!

Note that in contrast to the above, `.user` or `.tenant` properties you might detect in your debugger on instances of [`express.Request`](https://expressjs.com/de/api.html#req) are *internal* properties of some authentication strategy implementations. These are not documented and not public and should **NEVER** be used anywhere!

`cds.User.default` is now an *instance* of `cds.User`, not a class anymore.

It is thus of same nature as `cds.User.anonymous` and `cds.User.privileged` singleton instances, by default it is an alias to the former. Note that this was always only used in (our own) tests to skip all access control checks, and should never be used in production code.

### Deprecated Features ​

As the new database services, the new protocol adapters, the new input validation are the default in *cds8*, the former implementation variants are officially deprecated from now on, and will be removed in upcoming releases. Yet for a grace period until removal, you can re-enable them through these configuration flags:

| Config Flag | Description |
| --- | --- |
| `cds.features.odata_new_adapter` | Set to `false` to keep using the former, deprecated OData adapter |
| `cds.features.cds_validate` | Set to `false` to keep using the former, deprecated input validation |
| `cds.fiori.draft_compat` | Set to `true` to keep using legacy style draft handlers |
| `cds.sql.transitive_localized_views` | Set to `true` to keep creating transitive localized views |

New `attic` profile

A new `cds.env` profile `attic` has been added, which allows to easily switch on all deprecated features as listed above, in single server starts or test runs. For example, you can use that like that:

sh

```
CDS_ENV=attic cds watch
CDS_ENV=attic jest
```

Requires `@sap/cds-attic`

Whenever using these deprecated options, make sure to [install `@sap/cds-attic` as explained below](#cds-attic).

#### Introducing @sap/cds-attic ​

To optimize package sizes, we will gradually move outdated and deprecated features out of our main code base into the new package `@sap/cds-attic`. This means, whenever you use deprecated features, you need to install this package:

sh

```
npm add @sap/cds-attic
```

Note that while in the beginning this package is actually empty, and deprecated features might still work without it being present, that'll change over time, as we gradually cleanup our code base and move outdated code in there.

#### Old Database Services ​

Also deprecated are the old database services. If you need to switch back to them, you can do so by ***not*** having the new ones in the package dependencies, and have old ones installed instead:

json

```
  "dependencies": {
    "@sap/cds": "^8",
    "@sap/cds-hana": "^2"
  },
```

Note that in contrast to the new database services, the old ones don't come with plug & play defaults for the configuration, so you would add these as before, for example:

json

```
  "cds": {
    "requires": {
      "db": {
        "kind": "sql",
        "[production]": {
          "kind": "hana"
        }
      }
    }
  }
```

In the transition phase to `cds8`, you may want to install both, variants, and switch between them using process env variables like that:

json

```
  "dependencies": {
    "@sap/cds": "^8",
    "@sap/cds-hana": "^2",
    "@cap-js/hana": "^1"
  },
  "devDependencies": {
    "@cap-js/sqlite": "^1",
    "sqlite3": "^5"
  },
```

### Removed Features ​

The following features were deprecated since *cds7*, or longer, and have been removed in *cds8*:

- CSN proxy objects `_texts` → use `.texts` instead
- Legacy API `srv.stream` → use `SELECT` with a single `LargeBinary` column instead
- Legacy API `req.user.locale` → use `req.locale` instead.
- Legacy API `req.user.tenant` → use `req.tenant` instead.
- Annotation `@assert.enum` → use `@assert.range` instead.
- Annotations `@Common.FieldControl.Mandatory` and `@FieldControl.Mandatory` → use `@mandatory` instead.
- Annotations `@Common.FieldControl.Readonly` and `@FieldControl.Readonly` → use `@readonly` instead.
- Undocumented properties of `cds.Request`: `.tokenInfo`
- `._.shared`
- `.attr`
- `._query`
- `._path`

- Undocumented header `x-correlationid` → use `x-correlation-id` instead
- Old middlewares, hence config option `cds.requires.middlewares = false`.
- Old draft implementation, hence config option `cds.fiori.lean_draft = false`.
- Config option `cds.features.serve_on_root = true` → use the new path scheme, or use an absolute `@path` annotation as announced in the release notes of cds 7.
- Config option `cds.drafts.cancellationTimeout` → use `cds.fiori.draft_lock_timeout` instead.

### Miscellaneous ​

#### VCAP Filters are AND-ed Now ​

For example, given a configuration like that:

jsonc

```
{"cds":{
  "requires": {
    "whatever": {
      "vcap": { "label": "foo", "tag": "bar" }
    }
  }
}}
```

In the past, this matched the first `VCAP_SERVICES` entry, with *either* a property `label` matching the value `"foo"` ***or*** property `tag` matching the value `"bar"` , which lead to unexpected, hard-to-resolve behaviors. This has been fixed in *cds8* by always only matching entries that match **all** specified filters.

#### No Generated index.html in Production ​

The default `index.html` page generated by the CAP runtime was always meant for development only. We added a specific check to *cds8* to avoid accidental shipment of an application to production with this page still served, by just not doing so if `NODE_ENV` is set to `production`. For demonstration purposes, you can set `cds.server.index = true` to enable this feature explicitly.

#### Destination Cache Turned On by Default ​

On the outbound protocol adapters side, we now switch on the destination cache by default.

## Java ​

### Important Changes❗️ ​

This release brings the new major version CAP Java `3.0`. In addition to advanced security features and latest dependency versions, there are also some incompatible changes that optimize runtime behavior. Most of the changes can be consumed in the previous version `2.10.x` already which guarantees a smooth transition.

[Learn more in migration guide.](/docs/java/migration#two-to-three)

The following changes are particularly worth mentioning:

New **minimum versions** apply:

| Dependency | Minimum Version |
| --- | --- |
| Cloud SDK | `5.9.0` |
| cds-dk | `^7` and `^8` |
| Maven | `3.6.3` |

Removed some **deprecated features**:

| Feature | Replacement |
| --- | --- |
| MTX Classic | [Streamlined MTX](/docs/java/multitenancy) |
| [`MtSubscriptionService`](https://www.javadoc.io/doc/com.sap.cds/cds-feature-mt/latest/com/sap/cds/services/mt/MtSubscriptionService.html) | [`DeploymentService`](https://www.javadoc.io/doc/com.sap.cds/cds-services-api/latest/com/sap/cds/services/mt/DeploymentService.html) |
| `cds-feature-xsuaa` | [`cds-feature-identity`](/docs/java/security#xsuaa-ias) |

Some **default behavior** has changed, most notably:

- The production profile is `cloud` matching Java buildpack behavior (cds.environment.production.profile: cloud).
- EDMX V4 is localized on the fly for all applications (cds.odataV4.lazyI18n.enabled: true).
- SQL is optimized for SAP HANA HEX engine (cds.sql.hana.optimizationMode: hex).
- Remote service calls have no activated CSRF protection (cds.remote.services.<key>.http.csrf.enabled: false).

**New features** are active by default:

- Actions and functions have support for instance-based authorization.

Stay up to date and benefit from latest and greatest features by migrating to `3.0`! Find a step-by-step instruction to upgrade in the [migration guide](/docs/java/migration#two-to-three).

Warning

- cds-services `2.10.x` is now in maintenance mode and only receives critical bugfixes.
- All versions < `2.10.x` have reached end of live and won't be patched anymore.

### IAS Service Consumption ​

CAP Java now supports consumption of [SAP Cloud Identity Services Identity Authentication (IAS)](https://help.sap.com/docs/cloud-identity-services)-based services of various kinds:

- Services bound to the IAS application.
- IAS BTP reuse services consumed via service binding.
- External IAS applications consumed via destination.

Regardless the kind of service, CAP provides a unified integration as Remote Service as described in the [documentation](/docs/java/cqn-services/remote-services#remote-odata-services). Basic communication setup and user propagation is done under the hood, for example, an mTLS handshake is performed in case of service-2-service communication.

Tip

CAP Java now requires AppRouter to be configured with mTLS in case of IAS authentication (`forwardAuthCertificates: true`).

By default, mTLS protection is activated for IAS endpoints. You can deactivate with property `sap.spring.security.identity.prooftoken: false`.

[Learn more about IAS authentication in CAP Java](/docs/java/security#xsuaa-ias)

#### IAS Reuse Service With CAP ​

You now can also easily create an IAS-based BTP reuse service on basis of CAP Java.

The CAP reuse service (server) needs to:

- Configure IAS authentication.
- Bind an IAS instance that exposes services and service plans.Sample configurationyaml

```
- name: server-identity
    type: org.cloudfoundry.managed-service
    parameters:
      service: identity
      service-plan: application
      config:
        multi-tenant: true
        catalog:
          services:
            - id: "1d5c23ee-1ce6-6130-4af4-26461bc6ef79"
              name: "review-service"
              plans:
                - id: "2d5c23ee-1ce6-6130-4af4-26461bc6ef78"
                  name: "standard"
```

The CAP consumer application (client) needs to:

- Create and bind the provided service from the marketplace.
- Create an IAS instance that consumes the required service.Sample SAP Cloud Identity Services Identity Authentication (IAS) instance for clientyaml

```
  - name: client-identity
    type: org.cloudfoundry.managed-service
    parameters:
      service: identity
      service-plan: application
      config:
        multi-tenant: true
        "consumed-services": [ {
          "service-instance-name": "review-service-instance"
        } ]
```
- Create a Remote Service based on the binding (optional).Sample Remote Service configurationyaml

```
cds:
  remote.services:
    Reviews:
      binding:
        name: review-service-binding
        onBehalfOf: currentUser
```
- Use CQN queries to consume the reuse service (optional)

[Learn more about simplified Remote Service configuration with bindings](/docs/java/cqn-services/remote-services#service-binding-based-scenarios)

#### App to App Communication With IAS ​

CAP Java now also supports streamlined [communication with applications](https://help.sap.com/docs/cloud-identity-services/cloud-identity-services/consume-apis-from-other-applications), that are not necessarily deployed to SAP BTP, leveraging SAP Cloud Identity Services Identity Authentication (IAS) communication.

The IAS server application needs to

- Configure IAS authentication.
- Expose an API in the IAS service instance.Sample IAS instance of serveryaml

```
- name: server-identity
    type: org.cloudfoundry.managed-service
    parameters:
      service: identity
      service-plan: application
      config:
        multi-tenant: true
        provided-apis:
          - name: "review-api"
```
- Prepare a CDS service endpoint for the exposed API.Sample CDS Service for the APIcds

```
service ReviewService @(requires: 'review-api') {
  [...]
}
```

To setup a connection to such a system, the client requires to do:

- Create an IAS instance that consumes the required API.Sample IAS instance for clientyaml

```
- name: client-identity
    type: org.cloudfoundry.managed-service
    parameters:
      service: identity
      service-plan: application
      config:
        multi-tenant: true
        oauth2-configuration:
          token-policy:
            grant_types:
              - "urn:ietf:params:oauth:grant-type:jwt-bearer"
```
- Create a Remote Service based on the destination (optional).Sample Remote Service configurationyaml

```
cds:
  remote.services:
    Reviews:
      destination:
        name: review-service-destination
```

To activate the app-2-app connection as subscriber, you need to

- Create an IAS application dependency in the IAS tenant pointing to the server's exposed API (Cloud Identity Service UI: Application APIs / Dependencies).
- Create a dedicated destination provided by the subscriber that points to the application. The prepared destination needs to haveThe URL pointing to the IAS-endpoint of the application.
- Authentication type `NoAuthentication`.
- Attribute `cloudsdk.ias-dependency-name` with the name of the created IAS application dependency.

[Learn more about how to consume external application APIs with IAS](https://help.sap.com/docs/cloud-identity-services/cloud-identity-services/consume-apis-from-other-applications)

[Learn more about simplified Remote Service configuration with destinations](/docs/java/cqn-services/remote-services#destination-based-scenarios)

### Auth Filters for Actions and Functions ​

`CqnSelect` statements propagated with the context of bound actions and functions now respect filter conditions of [restrictions](/docs/guides/security/authorization#instance-based-auth):

cds

```
service CustomerService @(requires: 'authenticated-user') {
  entity Orders @(restrict: [
    { grant: 'cancel', to: 'Customer', where: ($user.limit > invoiceAmount)}
  ]) {
    invoiceAmount: Integer;
  }
  actions {
     action cancel ();
  }
}
```

The custom handler code uses the query to locate the entities that the action or function is authorized for. In other words, it includes an extra filter: `$user.limit > invoiceAmount`:

java

```
@On(service = CustomerService_.CDS_NAME, entity = Orders_.CDS_NAME)
public void onCancelOder(OrdersCancelContext context) {
    CqnSelect restrictedOrders = context.getCqn(); // selects authorized entities only
    Result orders = persistenceService.run(restrictedOrders);
    /* process filteredOrders here */
}
```

Tip

Note that the **runtime does not reject the action or function** in case entities are excluded from the query due to an authorization condition.

Filters for actions and functions can be deactivated by setting cds.security.authorization.instance-based.custom-events.enabled: false.

### Outbox Observability ​

The persistent Outbox now periodically sends statistic data to [Open Telemetry](/docs/java/operating-applications/observability#open-telemetry) and [CDS actuator](/docs/java/operating-applications/observability#cds-actuator):

- `coldEntries`: Number of entries that reached the maximum number of retries.
- `remainingEntries`: Number of entries stored in the Outbox.
- `{min|max}StorageTimeSeconds`: Minimum and maximum time an entry is stored in the Outbox.

The data sent is labeled with the Outbox instance and tenant.

### Miscellaneous ​

- Java projects can now be generated without configured persistency: `cds init --add java --java:mvn persistence=false,archetypeVersion=3.0.0`.
- `cds add audit-logging` is supported now.
- mTLS support for connections to PostgreSQL.

## MTX ​

Adapt health check endpoint

As the generic *index.html* is [not served any more](#index-html) in cds8 you might have to change the health check endpoint in your deployment descriptor from `/` to `/health`.

### SAP HANA Driver Required ​

With `@sap/hdi-deploy` version 5 used by `@sap/cds-mtxs` 2 , you now need to have a dependency to an SAP HANA driver in your MTX sidecar project.

If not already done, install package [`@cap-js/hana`](https://www.npmjs.com/package/@cap-js/hana) for this. In `mtx/sidecar`, run:

sh

```
npm add @cap-js/hana
npm rm hdb @sap/hana-client @sap/cds-hana  # removes explicit and legacy adapters
```

`@cap-js/hana` installs the `hdb` driver for SAP HANA.

The `hdb` driver is recommended by CAP for example because of its small install size. Check the [feature comparison chart](https://www.npmjs.com/package/hdb) for `hdb` and `@sap/hana-client` to make sure that your app doesn't use features not supported by the `hdb` driver.

### Simplified SaaS Dependency Management ​

Instead of overwriting the `dependencies` handler in the MTX sidecar you can specify SaaS registry dependencies using the `subscriptionDependency` property. It points to the relevant key path in the service credentials (usually `xsappname`).

mtx/sidecar/package.jsonjson

```
"cds": {
 "requires": {
    "my-service": {
      "vcap": { "label": "my-label" },
      "subscriptionDependency": "xsappname"
    }
  }
}
```

[See the detailed section on SaaS registry dependencies](/docs/guides/multitenancy/#saas-dependencies)

For convenience, `@sap/cds-mtxs` provides defaults for commonly used dependent services out of the box, such as for the SAP BTP Audit Logging, SAP BTP Connectivity, SAP BTP Destination, and SAP BTP Portal services. Simply setting to `true` is enough:

mtx/sidecar/package.jsonjsonc

```
"cds": {
  "requires": {
    "audit-log": true,
    "connectivity": true,
    "destinations": true,
    "html5-repo": true,
    "portal": true
  }
}
```

### New Extension Project Structure ​

`cds pull` now updates the structure of extension projects to a structure using `npm workspaces`. It downloads the base model into an NPM workspace folder `.base` as a package. To make the downloaded base model ready for use in your extension project, install it as a package:

sh

```
npm install
```

This will link the base model in the workspace folder to the subdirectory `node_modules/`.

For existing projects, you might need to adapt the references (`using from '...'`).

New project structure for extension projects

So far, extension project had the following structure.

zsh

```
extension
├── db
│   ├── ext.cds
├── node_modules
│   └── _base
│       └── index.csn
├── package.json
└── srv
```

When running `cds pull`, the base model was stored inside the `node_modules` folder. In case `npm install` was called, the base model was deleted by npm again.

With the new structure, this is fixed by using the [npm workspaces](https://docs.npmjs.com/cli/v10/using-npm/workspaces). This will link the base model in the workspace folder to the subdirectory node_modules/ but at the same time removes the risk of loosing the base model through npm actions.

zsh

```
extension
├── .base
│   ├── index.csn
│   └── package.json
├── db
│   └── ext.cds
├── node_modules
│   ├── ...
│   ├── bookshop -> ../.base
│   ├── ...
├── package.json
└── srv
```

The `package.json` now contains the section

json

```
"cds": {
  "extends": "bookshop"
},
"workspaces": [
    ".base"
  ]
```

Since the folder for base model has changed, your extension sources might have to be adapted like

`using sap.capire.bookshop from '_base';`

to

`using sap.capire.bookshop from 'bookshop';`

The name of the reference is derived from the label specified by `extends` in the `package.json` file.

### More Extension Linter Restrictions ​

The extension linter that checks extensions before they can be activated now always checks critical annotations, even if no [extension linter configuration](/docs/guides/multitenancy/mtxs#extensibility-config) exists.

The following annotations are blocked:

Security annotations as extensions

cds

```
@requires
@restrict
```

Persistence annotations as extensions

cds

```
@cds.persistence.exists
@cds.persistence.skip
@cds.autoexpose
@cds.external
@cds.persistence.journal
@sql.append
@sql.prepend
```

Validation annotations as extensions

cds

```
@readonly
@mandatory        // allowed if default is specified
@assert.unique
@assert.integrity
@assert.target
@assert.format
@assert.range    // allowed if default is specified
@assert.notNull  // allowed if default is specified
```

Service annotations as extensions

cds

```
@path
@impl
@cds.autoexpose
@cds.api.ignore
@odata.etag
@cds.query.limit
@cds.localized
@cds.valid.from
@cds.valid.to
@cds.search
```

Annotations on new entities

cds

```
@cds.persistence.journal
@cds.persistence.exists
@sql.append
@sql.prepend
```

### Miscellaneous ​

#### Removed UIFlex Support From Extensibility API ​

The undocumented API for UIFlex extensions has been removed.

#### Removed cds.Subscriber Role From Build-in Mock Users ​

As non-technical users usually cannot trigger subscriptions and unsubscriptions, role `cds.Subscriber` has been removed from the [build-in mock users](/docs/node.js/authentication#mock-users).

#### Classic Multitenancy Package has Reached End of Life ​

Package `@sap/cds-mtx` has reached [end of life](./../schedule#end-of-life-status) and is no longer supported.
 If you still use it, [migrate to `@sap/cds-mtxs`](/docs/guides/multitenancy/old-mtx-migration) now.

## CAP Plugins ​

### Attachments w/ Malware Scans ​

The Attachments plugin [@cap-js/attachments](https://www.npmjs.com/package/@cap-js/attachments/) now supports automatic malware scanning for uploaded files, using [SAP Malware Scanning Service](https://discovery-center.cloud.sap/serviceCatalog/malware-scanning-service). This addition provides an extra layer of security, ensuring that all uploads are checked for malicious content seamlessly in the background.

- A new status feature shows the current state of each scan, including `Unscanned`, `Scanning`, `Infected`, `Clean`, and `Failed`.
- Scanning is enabled by default but is disabled in the development profile to streamline the testing process. You can disable malware scanning by setting cds.requires.attachments.scan: false.

### New SAP Document Management Service Plugin Beta ​

The new CDS plugin [@cap-js/sdm](https://www.npmjs.com/package/@cap-js/sdm/) is now available as [open source on GitHub](https://github.com/cap-js/sdm). You can easily add the package to your application's dependencies and use the `Attachments` type in your model.

sh

```
npm add @cap-js/sdm
```

[Find more details about the SAP Document Management Service Plugin.](https://github.com/cap-js/sdm#readme)

### New Open Resource Discovery Plugin ​

A new CDS plugin package for [Open Resource Discovery (ORD)](https://sap.github.io/open-resource-discovery/) is now available and [open source](https://github.com/cap-js/ord). Simply add package `@cap-js/ord` to your application's dependencies to generate an ORD document for your CAP Application.

[Find more details about the ORD Plugin.](/docs/plugins/index#ord-open-resource-discovery)

## CAP on Kyma/K8s ​

### Interactive Helm Chart Prompts ​

`cds add helm` will now ask prompts at the first execution to fill data in *values.yaml*.

log

```
[…]
Adding feature 'helm'...
domain: (abc.com)
imagePullSecret: (docker-registry)
registry: (registry-name)

Successfully added features to your project.
```

You can use `--y` flag with `cds add helm` command if you want to use defaults.

### Changes in the Helm Chart ​

With this release, the structure of the *values.yaml*, added by [`cds add helm`](/docs/guides/deploy/to-kyma#deploy-to-kyma), has changed:

values.yamlyaml

```
global:
  domain:
  imagePullSecret:
    name:
  image:
    registry:
    tag: latest
srv:
  ...
  image:
    repository: /bookshop-srv
    tag: latest
    repository: bookshop-srv
...
approuter:
  ...
  image:
    repository: /bookshop-approuter
    tag: latest
    repository: bookshop-approuter
...
hana-deployer:
  ...
  image:
    repository: /bookshop-hana-deployer
    tag: latest
    repository: bookshop-hana-deployer
...
```

You no longer have to specify registry name and tag with all the images. You can just specify it once in the global property. You can still specify tags at workload level if your tags are different.

#### Removal of mtxs-configmap ​

Earlier `configmaps` were used to provide environment variables required in multitenant application. Now, env variables are directly added to *values.yaml*.

Node application with App Router:

values.yamlyaml

```
sidecar:
  ...
  env:
    SUBSCRIPTION_URL: https://${tenant_subdomain}-{{ .Release.Name }}-approuter-{{ .Release.Namespace }}.{{ .Values.global.domain }}
  envFrom:
  - configMapRef:
      name: "{{ .Release.Name }}-mtxs-configmap"
  ...
```

Java application with App Router:

values.yamlyaml

```
srv:
  ...
  env:
      CDS_MULTITENANCY_APPUI_TENANTSEPARATOR: "-"
      CDS_MULTITENANCY_APPUI_URL: https://{{ .Release.Name }}-approuter-{{ .Release.Namespace }}.{{ .Values.global.domain }}
      CDS_MULTITENANCY_SIDECAR_URL: http://{{ .Release.Name }}-sidecar.{{ .Release.Namespace }}.svc.cluster.local:8080
  envFrom:
  - configMapRef:
      name: "{{ .Release.Name }}-mtxs-configmap"
  ...
```

In the *values.yaml*, these environment variables may be overwritten by `cds add` commands. If you want to provide your own value and don't want `cds add` commands to overwrite the value of any particular variable, add `#cds.noOverwrite` comment next to that value.

#### Removal of saasRegistryParameters Key ​

Previously, a separate key `saasRegistryParameters` was used to specify parameters of `saas-registry` service. Now, this key is removed and the parameters are mentioned in the `saas-registry` key directly.

values.yamlyaml

```
saas-registry:
  serviceOfferingName: saas-registry
  servicePlanName: application
  parameters:
    displayName: bookshop
    description: A simple CAP project.
    category: "CAP Application"
    appUrls:
      onSubscriptionAsync: true
      onUnSubscriptionAsync: true
      onUpdateDependenciesAsync: true
      callbackTimeoutMillis: 300000
      getDependencies: https://{{ .Release.Name }}-approuter-{{ .Release.Namespace }}.{{ .Values.global.domain }}/-/cds/saas-provisioning/dependencies
      onSubscription: https://{{ .Release.Name }}-approuter-{{ .Release.Namespace }}.{{ .Values.global.domain }}/-/cds/saas-provisioning/tenant/{tenantId}
    xsappname: bookshop-{{ .Release.Namespace }}
    appName: bookshop-{{ .Release.Namespace }}
  parametersFrom:
    - secretKeyRef:
        name: "RELEASE-NAME-saas-registry-secret"
        key: parameters
saasRegistryParameters:
  xsappname: bookshop
  appName: bookshop
  displayName: bookshop
  description: A simple self-contained bookshop service.
  category: "CAP Application"
  appUrls:
    getDependencies: "/-/cds/saas-provisioning/dependencies"
    onSubscription: "/-/cds/saas-provisioning/tenant/{tenantId}"
    onSubscriptionAsync: true
    onUnSubscriptionAsync: true
    onUpdateDependenciesAsync: true
    callbackTimeoutMillis: 300000
```

#### Support for External Destinations ​

The `backendDestinations` key now supports adding external destinations.

yaml

```
...
backendDestinations:
  srv-api:
    service: srv
  ui5:
    external: true
    name: ui5
    Type: HTTP
    proxyType: Internet
    url: https://ui5.sap.com
    Authentication: NoAuthentication
```

### Generated Chart ​

`cds add helm` command won't generate static files (subcharts and templates) when `cds add helm` is executed. Instead, `cds build` generates the `chart` folder containing all the static data in the `gen` folder.
