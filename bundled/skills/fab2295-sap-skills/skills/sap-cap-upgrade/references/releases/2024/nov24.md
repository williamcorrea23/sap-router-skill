<!-- mirror: https://cap.cloud.sap/docs/releases/2024/nov24 -->
<!-- fetched: 2026-05-09T02:26:45.865Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# November 2024 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Documentation (Capire) ​

Quite some time has passed, and many things happened, and were added, since we wrote the current versions of our central cookbook guides, so it was time to give them a thorough overhaul... We did that now...

### Revised Getting Started Guides ​

As so many things happened since we wrote our getting started and cookbook guides, many of them need major updates and thorough overhauls. We started that journey now with the Welcome page, and the guides in the Getting Started section:

- Welcome page → got a minor face lift; the bullets in the four boxes are adjusted
- Introduction - What is CAP? → 90% newly written; replaces former About CAP
- Best Practices → 100% new: key concepts and do's; was always missing
- Learn More → combines info formerly spread across several pages

### New: Aspect-oriented Modeling ​

We added a new guide for [Aspect-Oriented Modeling](/docs/cds/aspects) to the CDS reference. It explains how you can use aspects for separation of concerns, as well as to reuse and adapt definitions in your models.

### Improved CDL Reference ​

We improved the structure of the [Conceptual Definition Language (CDL)](/docs/cds/cdl) reference, mainly putting *[Language Preliminaries](/docs/cds/cdl#language-preliminaries)* sections to the top, introducing the basics for keywords, identifiers, built-in types, literals, and so on.

## CDS Language & Compiler ​

### New CDL Parser Alpha ​

The CDL Parser currently has an installation size of nearly 2 MB (runtime code and generated files). We plan to transition to a new parser with a significant size reduction (to around 200 kB installation size and having no package dependency) in three phases:

- Now: The new parser can be switched on via configuration for testing (see the following snippet).
- The new parser is switched on by default; the old parser is still installed and can be reactivated, if necessary (Jan/Feb 25).
- Completely remove the old parser including its dependency to the ANTLR4 runtime (next major release).

Set the following option in your private `~/.cdsrc.json` to switch on the new parser on your local machine:

~/.cdsrc.jsonjson

```
{
  "cdsc": {
    "newParser": true
  }
}
```

We appreciate any feedback that helps us to detect and fix issues before using the new parser by default.

### Enhanced @assert.range ​

We now support open intervals with `@assert.range` by wrapping *min* or *max* values in parentheses:

cds

```
@assert.range: [(0),100]    // 0

In addition an underscore `_` can be used as a stand-in for *infinity*:

cds

```
@assert.range: [(0),_]  // positive numbers only, _ means +Infinity here
@assert.range: [_,(0)]  // negative number only, _ means -Infinity here
```

[Learn more in the documentation of `@assert.range`](/docs/guides/services/constraints#assert-range)

## Node.js ​

### New Plugin for RFC ​

With the new [cds-rfc plugin](https://www.npmjs.com/package/@sap/cds-rfc) you can import the API of RFC-enabled function modules from an SAP S/4HANA system:

... and call the functions as if you're calling them from a local CAP service:

js

```
const S4 = await cds.connect.to('SYS')
const user = await S4.BAPI_USER_GET_DETAIL({
  USERNAME: 'display', ...
})
```

[Learn more about the new plugin](/docs/plugins/index#abap-rfc)

### New cds.i18n API ​

The new [`cds.i18n` API](/docs/node.js/cds-i18n) is used consistently for both serving localized SAP Fiori UIs, as well as for localized messages at runtime. You can also use it in your own Node.js applications to localize your own messages. Here are some examples:

js

```
const cds = require('@sap/cds')
cds.i18n.labels.at('CreatedAt','de')  // Erstellt am
cds.i18n.labels.at('CreatedAt')      // Created At
cds.i18n.messages.at('ASSERT_FORMAT',['wrong email',/\w+@\w+/])
```

You can also lookup translated UI labels for CSN definitions:

js

```
let {Books} = CatalogService.entities, {title} = Books.elements
cds.context = {locale:'fr'}  // as automatically set by protocol adapters
cds.i18n.labels.at(Books)    //> 'Livre'
cds.i18n.labels.at(title)    //> 'Titre'
```

[Learn more about that in the documentation of `bundle.at(key,...)`.](/docs/node.js/cds-i18n#at-key)

Fixes to former i18n for runtime messages

With this new implementation used consistently for all i18n, we also fixed some flaws of the former implementation for runtime messages.

- Bundles are always loaded from the neighborhood of .cds sources.
- Only files from the first match of `i18n.folders` are used, not all.
- Arguments for `{<>}` placeholders aren't recursively localized anymore.

While these changes are unlikely to affect any users or projects, take note of them, and take appropriate action if you relied on the former behavior.

### Fuzzy Search ​

The default fuzziness threshold used by CAP Node.js is 0.7 and is now configurable. If the default doesn't suite your needs, you can adapt it globally with cds.hana.fuzzy.

Besides the configurable default, now also the `@Search.fuzzinessThreshold`and `@Search.ranking` annotation is supported by the CAP Node.js runtime.

cds

```
entity Books {
      @Search.fuzzinessThreshold: 0.5
      @Search.ranking: HIGH
      title         : String;
      @Search.ranking: LOW
      description   : String;
}
```

In this example, the `title` is the important criteria while the search needs to be less exact compared to the default fuzziness.

If you don't want to use the fuzzy search, you can set cds.hana.fuzzy: false and `LIKE` expressions are used instead.

[Learn more about Fuzzy Search in CAP.](/docs/guides/services/served-ootb#fuzzy-search)

### cds debug Beta ​

The new CLI command `cds debug` lets you easily debug local or remote Node.js applications in Chrome DevTools.

For local applications, `cds debug` is simply a shortcut to `cds watch --debug`:

sh

```
cds debug
```

log

```
  Starting 'cds watch --debug'
  ...
  Debugger listening on ws://127.0.0.1:9229/...
  Opening Chrome DevTools at devtools://devtools/bundled/inspector.html?ws=...
```

For remote applications add the name of your application in the currently targeted Cloud Foundry space:

sh

```
cds debug bookshop-srv
```

log

```
  Opening SSH tunnel for CF app 'bookshop-srv'
  Opening Chrome DevTools at devtools://devtools/bundled/inspector.html?ws=...
```

This command opens an [SSH tunnel](https://docs.cloudfoundry.org/devguide/deploy-apps/ssh-apps.html), puts the application in debug mode, and connects and opens the debugger in [Chrome DevTools](https://developer.chrome.com/docs/devtools/javascript).

### cds add handler ​

You can now also have automatic handler stubs in Node.js projects for both JavaScript and TypeScript. In your project, run:

sh

```
cds add handler
```

This [facet](/docs/tools/cds-cli#cds-add) creates [event handlers](/docs/node.js/core-services#implementing-services) for service entities and actions like this:

JavaScriptTypeScriptjs

```
const cds = require('@sap/cds')
module.exports = class CatalogService extends cds.ApplicationService { init() {
  const { Books } = cds.entities('CatalogService')

  this.before (['CREATE', 'UPDATE'], Books, async (req) => {
    console.log('Before CREATE/UPDATE Books', req.data)
  })
  this.on ('submitOrder', async (req) => {... })

  return super.init()
}}
```

ts

```
import cds from '@sap/cds'
import { Books, submitOrder } from '#cds-models/CatalogService'

export class CatalogService extends cds.ApplicationService { init() {
  this.before (['CREATE', 'UPDATE'], Books, async (req) => {
    console.log('Before CREATE/UPDATE Books', req.data)
  })
  this.on (submitOrder, async (req) => {... })

  return super.init()
}}
```

For action stubs of *Java* projects, this feature has already been available since [September](./sep24#add-handler-stubs).

[Learn more about handler generation.](/docs/tools/cds-cli#handler)

### cds init --add esm Beta ​

You can now create [ECMAScript module projects (ESM)](https://nodejs.org/api/esm.html) with `cds init --add esm` or switch to ESM later with `cds add esm`. Sample code added with `cds add sample` or `cds add handler` honors the setting. However, it doesn't migrate existing code.

Should CAP projects use ESM?

The CAP Node.js runtime can be used in both CommonJS and ESM applications.

Our recommendation is to stay on CommonJS. Here are some guidelines to help you decide:

- The Jest test framework is known to only have experimental support for ESM.
- If you need to use ESM-only libraries like SAP Cloud SDK for AI now, switching to ESM is necessary. chai 5 is ESM-only as well, but version 4 on CommonJS is still supported.
- However, Node.js 23 already has experimental support for ESM imports into CommonJS applications. This approach improves ESM compatibility in CommonJS projects.

## Java ​

### Simpler Recursive Hierarchies ​

To create a recursive hierarchy for a UI5 tree table, applications so far had to define a [projection](/docs/cds/cdl#views-projections) to rename the `node` property and the foreign key to adhere to SAP HANA naming conventions.

CAP Java now automatically evaluates the `@Aggregation.RecursiveHierarchy` to identify the `node` property and the `parent` navigation property, and automatically does the renaming. It's now also possible to use a [managed association](/docs/cds/cdl#managed-associations) for the parent navigation.

cds

```
context db {
  entity SalesOrgs : cuid {
    name     : String;
    parentID : String(36);
    parent   : Association to SalesOrg
                on parent.ID = parentID;
  }
}

service S {
  @Aggregation.RecursiveHierarchy #SalesOrgHierarchy: {
    $Type                   : 'Aggregation.RecursiveHierarchyType',
    NodeProperty            : ID,
    ParentNavigationProperty: parent
  }
  entity SalesOrgHierarchy as projection on db.SalesOrgs {
      *,
      ID       as node_id,
      parentID as parent_id
    };
}
```

### Filter & Sort by Elements in cds.Map Beta ​

You can now filter and sort by sub-elements of `cds.Map` elements. Given the CDS model using the `Map` type for `Person.details`:

cds

```
entity Person {
  key ID      : UUID;
      name    : String;
      details : Map;
}
```

You can filter by sub-elements of `cds.Map` elements, for example, to select all persons named "Peter", which live in Walldorf:

java

```
Select.from(PERSON).where(p -> p.name().eq("Peter").and(
    p.get("details.address.city").eq("Walldorf")));
```

You can also sort by sub-elements of `cds.Map` elements, for example, to sort by `address.city` in the `details` Map:

java

```
Select.from(PERSON).where(p -> p.name().eq("Peter"))
      .orderBy(p -> p.get("details.address.city")
                     .type(CdsBaseType.String).asc());
```

To ensure that type-specific sorting is applied, specify the expected type of the sub-element.

Warning

Avoid Filtering and sorting by elements within maps on large data sets as it's an expensive DB operation.

### Enhanced Instance-Based Authorization ​

Entities having an instance-based authorization condition, that is [`@restrict.where`](/docs/guides/security/authorization#restrict-annotation), are guarded by the CAP Java runtime by adding a filter condition to the DB query. Instances that don't match the filter condition are excluded from the result. If the user isn't authorized to query an entity, OData requests targeting a *single* entity return a *404 - Not Found* even though the entity exists.

To allow the UI to distinguish between *not found* and *forbidden*, CAP Java now introduces a new configuration option reject-selected-unauthorized-entity. If enabled, unauthorized `PATCH` and `DELETE` requests to single entities are rejected with *403 - Forbidden*. The additional authorization check may affect performance.

[Learn more about `@restrict.where` in the instance-based authorization guide.](/docs/guides/security/authorization#instance-based-auth)

Info

It isn't checked whether the user can read the targeted entity. The handler could disclose to unauthorized users that an entity under a given key exists.

## MTX ​

### Annotation Allowlist for Extensions ​

In June, we announced that [only a few annotations are allowed as extensions](./jun24#more-extension-linter-restrictions).

You can now add exceptions for these restrictions, at your own risk, using the `annotations` property as follows:

jsonc

```
"cds.xt.ExtensibilityService": {
  "extension-allowlist": [
    {
      "for": ["CatalogService"],
      // allow @readonly annotations in CatalogService
      "annotations": ["@readonly"]
    }
  ]
}
```
