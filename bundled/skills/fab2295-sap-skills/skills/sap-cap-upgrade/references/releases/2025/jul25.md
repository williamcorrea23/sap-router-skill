<!-- mirror: https://cap.cloud.sap/docs/releases/2025/jul25 -->
<!-- fetched: 2026-05-09T02:26:51.038Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# July 2025 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Customize Validation Messages ​

Generic validation annotations, `@assert.range`, `@assert.format`, and `@mandatory`, now support custom messages. Use the annotation `@.message` with an error text or [i18n bundle key](/docs/guides/uis/i18n#externalizing-texts-bundles) like this:

cds

```
entity Person : cuid {
  @assert.format: '/^\S+@\S+\.\S+$/'
  @assert.format.message : 'Provide a valid email address'
  email : String;
}
```

Learn more about [input validation](/docs/guides/services/constraints) and [custom error messages](/docs/guides/services/constraints#custom-messages)

## Fiori Tree Views GA ​

CAP's tree view support is now generally available (GA) and no longer in beta, with the following features:

- Usage of standard OData/Fiori Annotations to define hierarchical entities
- Hierarchical queries from the underlying UI5 Tree Table component are served generically by CAP runtimes
- On top of SAP HANA, PostgreSQL, SQLite (CAP Node.js only), and H2 (CAP Java only).
- Read-only usage of hierarchical entities in List Views, Object Pages, and Value Helps
- Modification of hierarchies in draft enabled entities.

Not (yet) supported:

- Intercepting and modifying hierarchical queries in custom handlers
- Arbitrary OData query options other than the ones served today for UI5 Tree Table

Try it out in our bookshop sample apps for [CAP Java](https://github.com/SAP-samples/cloud-cap-samples-java) and [CAP Node.js](https://github.com/capire/bookstore).

## Node.js ​

### Improved Documentation ​

We improved the [CAP Node.js reference docs](/docs/node.js/) in these places:

- `req.subject`

### XSUAA Fallback in IAS Auth ​

To ease migration from XSUAA- to IAS-based authentication, the `ias` strategy automatically supports -- given the necessary bindings exist -- tokens issued by XSUAA.

Simply add `xsuaa` to the list of required services:

jsonc

```
"requires": {
  "auth": "ias", //> as before
  "xsuaa": true
}
```

[Learn more about IAS-based authentication](/docs/node.js/authentication#ias)

### Token Caching ​

`@sap/xssec^4.8`'s signature cache and token decode cache are enabled by default.

Configure or deactivate the signature cache via cds.requires.auth.config, which is passed to `@sap/xssec` as is.

Unlike the signature cache, configuring the token decode cache is done programmatically during bootstrapping.

For example a [custom `server.js`](/docs/node.js/cds-server#custom-server-js), is configured as follows:

js

```
require('@sap/xssec').Token.enableDecodeCache(config?)
```

To deactivate, set `decodeCache` to false instead:

js

```
require('@sap/xssec').Token.decodeCache = false
```

[Learn more about Token Caching.](/docs/node.js/authentication#cached-by-default)[Learn more about `@sap/xssec`](https://www.npmjs.com/package/@sap/xssec)

### Numeric Values in .csv Files ​

Numeric values in *.csv* files are now returned as numbers instead of strings.

For example, CSV data like this:

csv

```
id,name,age
1,John Doe,30
2,Jane Smith,25
3,Bob Johnson,40
```

... is now returned as:

js

```
[{ id: 1, name: 'John Doe', age: 30 }, ...]
```

When pre-padded with zeros, they're returned as strings, for example:

csv

```
id,name,age
01,John Doe,30
02,Jane Smith,25
03,Bob Johnson,40
```

... keeps being returned as:

js

```
[{ id: '01', name: 'John Doe', age: 30 }, ...]
```

You can also quote numeric values in the CSV file, to enforce them to be returned as strings:

csv

```
id,name,age
"1",John Doe,30
"2",Jane Smith,25
"3",Bob Johnson,40
```

## Java ​

### Generic Exception Handling for Result.single ​

By default, `Result.single` queries throw an `EmptyResultException` for cases where the result is empty. To avoid writing boilerplate exception handling code for these exceptions, you can now configure the runtime to generically handle them instead.

Tip

Set the configuration option cds.errors.preferServiceException: true to make `Result.single` methods automatically throw a `ServiceException` with an HTTP status code 404 (Not Found) for queries with no results.

### Simplified API of DraftService ​

To programmatically update or delete a draft via the `DraftService`, so far you had to use the dedicated `patchDraft(CqnUpdate, ...)` and `cancelDraft(CqnDelete, ...)` methods.

Now, when a statement exclusively targets inactive entities, you can alternatively use the `run(CqnUpdate, ...)` or `run(CqnDelete, ...)` methods. The `DraftService` will then automatically delegate to `patchDraft(CqnUpdate, ...)` and `cancelDraft(CqnDelete, ...)`.

Tip

This now allows to write handler code in a uniform way for draft-enabled and not draft-enabled entities.

[Learn more about Editing Drafts in CAP Java.](/docs/java/fiori-drafts#editing-drafts)

### Restrictions on $expand ​

Runtime now checks the following restrictions related to `$expand`:

- `@Capabilities.ExpandRestrictions.MaxLevels: ...` sets maximum allowed depth of an `$expand` from this entity.
- `@Capabilities.ExpandRestrictions.Expandable: false` prevents any expands from the entity.
- `@Capabilities.ExpandRestrictions.NonExpandableProperties: [...]` prevents expands for the specified properties.

This feature is enabled by cds.query.restrictions.enabled: true.

[Learn more about these restrictions in the Security guide.](/docs/guides/security/data-protection?impl-variant=java#http-server-and-cap-protocol-adapter)

## Tools ​

### Go to Implementations (Experimental) ​

The CDS text editor now supports "Go to Implementations" for CDS services and entities, for NodeJS and Java. On NodeJS, actions, functions and events are supported additionally. This feature is still experimental and might not cover all cases. Please report any issues you encounter.

### Formatting Parameter Lists ​

The new formatting options `whitespaceBeforeColonInParamList` and `whitespaceAfterColonInParamList` provide fine-grained control over spaces before and after colons in parameter lists for actions, functions, entities, and views.

### cds add github-actions ​

A new CLI command allows a quick setup for GitHub Actions:

sh

```
cds add github-actions
```

Use `cds add gha` as a shortcut.

We also added an [example workflow](https://github.com/capire/samples/blob/6ac5b81253e7f1c73d7633c7d2fe68c026864e0a/.github/workflows/cf.yaml) used in the Capire samples repository creating a Cloud Foundry deployment for an application with multiple microservices.
