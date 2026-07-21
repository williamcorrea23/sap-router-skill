<!-- mirror: https://cap.cloud.sap/docs/releases/2021/mar21 -->
<!-- fetched: 2026-05-09T02:26:27.351Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# March 2021 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtx?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Important Changes ​

##### CDS Compiler v2 ​

[CDS compiler version 2](#cds) (cv2) brings numerous improvements, which allow us to greatly streamline model processing and memory consumption going forward. All projects are recommended to **upgrade as soon as possible**, as the former version will only receive critical fixes after v2 is released. Find a guide on how to upgrade at [CDS > Compiler v2](/docs/cds/compiler/v2).

##### Consolidated Node.js APIs ​

In the course of finishing compiler v2 we also consolidated a few Node.js APIs for model processing. Those changes mostly affect private, undocumented APIs, so you should not encounter any adoption efforts if you sticked to the public APIs, Nevertheless find some things mentioned in the following [Node.js](#cds-js) section.

## Capire Docs & Samples ​

##### New and Overhauled docs for cds.compile and cds.reflect APIs ​

In the course of finishing compiler v2, we also consolidated the APIs for parsing, compiling, and reflecting models. In response to feedback received, we also returned these docs back to the [Node.js API reference docs](//node.js#toc). Find the updated docs at [Node.js > cds.compile](/docs/node.js/cds-compile) and [> cds.reflect](/docs/node.js/cds-reflect).

##### New and Overhauled docs for cds.ql APIs ​

We filled in many gaps in the Node.js `cds.ql` reference docs. This also includes docs for the newly introduced [tagged template string support](#node-tts). Find the updated docs at [Node.js > cds.ql](/docs/node.js/cds-ql).

##### Guide re Publishing to OpenAPI ​

Moved the formerly hidden information on CAP support for OpenAPI to a top-level guide at [Advanced > OpenAPI](/docs/guides/protocols/openapi).

##### Guided Tour in cap/samples for Java ​

Take a guided tour in VS Code through our [CAP Java samples](https://github.com/SAP-samples/cloud-cap-samples-java) and learn which CAP features are showcased by the different parts of the repository. Just install the [CodeTour](https://marketplace.visualstudio.com/items?itemName=vsls-contrib.codetour) extension for VS Code.

## Command Line / Toolkit ​

### Live Reload with cds watch ​

In addition to restarting the server, `cds watch` now automatically reloads your browser page after a change in a CAP project. You can stay focused in the editor while the effect of your change is visible immediately.

### Adding SAP HANA Support with cds add hana ​

To prepare your project for SAP HANA, it is no longer necessary to modify your *package.json*. Instead, use `cds add hana` to enhance your project configuration. See section [Enhance Project Configuration for SAP HANA Cloud](/docs/guides/databases/hana) for more details.

### Adding Cloud Foundry Native Deployment Support with cds add cf-manifest ​

As an alternative to MTA-based deployment, you can now easily create the manifest files with `cds add cf-manifest`. This replaces the CDS build base approach, but is currently limited to single tenant applications. See section [Deploy Using Manifest Files](/docs/guides/deploy/to-cf) for more details.

### Linting CDS Models with cds lint Beta ​

You can now use [CDS Linter](/docs/tools/cds-lint/) in your CAP project. See section [Setup & Usage](/docs/tools/cds-lint/#usage-lint-cli) for more details how to enable and use it.

## CDS Editors & Tools ​

The following features are available for all editors based on our language server implementation for CDS in SAP Business Application Studio, Visual Studio Code, and Eclipse. The plugins are available for download for Visual Studio Code at [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=SAPSE.vscode-cds#overview) and for Eclipse at [SAP Development Tools](https://tools.hana.ondemand.com/#cloud-vscodecds).

### Support for CDS Compiler v2 ​

The latest version of the editor supports both, CDS compiler v1 and v2.

As before, the editor picks up the compiler installed in the workspace if available, else from a globally installed `@sap/cds-dk` if available, else the embedded compiler, which now is CDS compiler v2.

### Support for Semantic Highlighting ​

Semantic highlighting adds additional coloring/styling on top of the existing syntax highlighting. It visualizes semantic information like the type of identifiers, for example, (namespace/context/service, entity/view/aspect, type, element, annotation) or modifiers, for example, if types are definitions, built-in, delivered with `@sap/cds/common.cds`, or abstract.

Standard syntax highlighting:

Additional semantic highlighting (see following example configuration):

Semantic highlighting is disabled by default. It requires extra calculation. For large models, there might be a noticeable delay between typing and updated highlighting.

#### Enablement ​

Enable semantic highlighting for CDS source files:

- Open Settings.
- Restrict selection to `semantic`.
- Ensure that `Editor > Semantic Highlighting: Enabled` is set to `true` or `configuredByTheme`.
- Enable specific CDS semantic highlighting by setting `Cds > Semantic Highlighting: Enabled` to `true`.

#### Configuration ​

Configure colors and font styles based on the additional information from semantic highlighting.

- Open Settings.
- Navigate to `Editor: Semantic Token Color Customizations`.
- Follow the link `Edit in settings.json`.

Tip

If you have `Editor > Semantic Highlighting: Enabled` set to `configuredByTheme`, add the theme name as an extra node between `editor.semanticTokenColorCustomizations` and `rules` (use code completion support)

The underlying language server protocol defines a set of predefined constants for token types and modifiers. As there are no specific constants for entity-relation languages, use the following mapping:

Token types:

- `namespace/context/service` → `"namespace"`
- `entity/view/aspect` → `"class"`
- `element` → `"property"`
- `type` → `"type"`
- `annotation` → `"typeParameter"`

Modifiers:

- built-in types → `"*.static"`
- types from `@sap/cds/common.cds` → `"*.defaultLibrary"`
- aspects/abstract entities → `"*.abstract"`
- definitions → `"*.definition"`

Tip

Some themes in the Marketplace already contain specific configuration for semantic highlighting information.

## CDS Language & Compiler ​

### Compiler v2 — A Major Step Forward ​

[CDS compiler version 2](#cds) (cv2) brings numerous improvements, many of which behind the scenes, which allow us to greatly streamline model processing and memory consumption going forward.

We recommend **upgrading as soon as possible**, as the former version will only receive critical fixes after v2 is released.

*Minimized Breaking Changes* — Even though this is a major version update – actually the first in life for [@sap/cds-compiler](https://www.npmjs.com/package/@sap/cds-compiler) – we tried to minimize breaking changes to a minimum. Most changes should not affect you at all, as long as you sticked to public and documented APIs (which you always should!).

Nevertheless, we prepared a dedicated guide for you to ease upgrading at:
 [CDS > Upgrade to Compiler v2](/docs/cds/compiler/v2).

### Fixed Temporal Data ​

Former releases had a major glitch, which made it literaly impossible to send *as-of-now* queries or *time-travel* queries; for example:

http

```
GET .../Books(ID=201) HTTP/1.1
```

... would be rejected by OData libs, asking you to specify the full compound key.

Reason for that was, we erroneously included `validFrom` in the OData `

`. But frequently you would not know the value of that. We've fixed that now by omitting `validFrom` from the OData primary key, as documented in a [corrected version of the Temporal Data guide](/docs/guides/domain/temporal-data#primary-keys-of-time-slices).

Consequences:

- As-of-now and time-travel queries work now as they were thought to. In the unlikely case, you did own workarounds, adding `validFrom` to single-object requests as above, you'd need to remove that.
- Time-series queries with `sap-valid-from/sap-valid-to` also continue to work, even though result sets may now have entries with duplicate keys, that is, same `ID` with different `validFrom` → OData specification disallows that, but most OData libs fortunately don't care.

In case you encounter issues, for example, using an OData library, that rejects duplicate keys, reach out to us. We do have a solution also for that, which we would share then.

### Compiler Messages Explained ​

We added a guide to explain selected `cds` compiler messages, with information how to fix them to [CDS > Compiler Messages](/docs/cds/compiler/messages).

### Scoped Definitions ​

You can now define an object `Foo.Bar` even if there is a definition for `Foo` that is not a context or a service. You can, for example, define entities `Orders` and `Orders.Items`.

[Learn more in the CDS Definition Language Reference.](/docs/cds/cdl#scoped-names)

The compiler internally makes use of this, for example, for localized entities: the text entity for entity `Foo` is now called `Foo.texts`. See section [Fix refs to Foo_texts](/docs/cds/compiler/v2#fix-refs-to-foo-texts) for more details.

### Simplified Syntax for Annotated OData Annotations ​

Almost all annotation assignments can now be written without delimited identifiers: the use of `.`, `@`, and `#` is fine for annotation names, property names of structures, and in references used as annotation values. For example, you can now write:

cds

```
@Common.Text: {
  @UI.TextArrangement: #TextOnly,
  ...
}
```

### Sorting SQL Statements ​

The compiler now sorts SQL statements in the order in which they have to be executed for deploying the model to a database.

## Node.js Runtime ​

### Major Version Update to v5 ​

As a consequence of the major version upgrade of `@sap/cds-compiler^2`, also the Node.js runtime package `@sap/cds` received a major version update to **v5** → *npm update* your project to receive that.

##### No Breaking Changes ​

- There are no breaking changes to public APIs.

##### Noteworthy Changes ​

You should take notice of the following changes, which **may** affect your project:

- Dropped support for Node.js v10 --› v12 is minimum required now; recommended: v14 (LTS).
- `@sap/cds^5` requires `@sap/cds-compiler^2`.
- `cds.features.snapi = false` has been removed now
- `req.timestamp` now returns `Date` objects, before it was a `Date.now()` integer. Although a public API, this change should be transparent for custom code.

##### Changes to Implementation ​

Following are changes to undocumented internal implementations, hence **shouldn't** affect CAP-based projects. Nevertheless, they're listed here for your reference:

- Removed methods `cds.compile.to.hdbtabledata` and `.to.hdbmigration` .
- Removed support for deprecated `@sap/xssec^2` --› use `xssec^3` instead.

### Tagged Template Strings for CDL, CQL, and CXL ​

We enhanced `cds.parse` with new functions `CDL`, `CQL`, and `CXL` accepting [tagged template string literals](https://developer.mozilla.org/docs/Web/JavaScript/Reference/Template_literals). These are made available by the `cds` facade as global functions, so you can easily use them as follows:

### Tagged Template Strings with cds.ql ​

We also extended this support of tagged template strings to `cds.ql`, as well as the Querying API functions of `cds.Service`, with great effects on readability of code:

### Performance Optimizations ​

`@sap/cds` version 5 comes with several performance optimizations, many happened on a detailed implementation level. A few stand out however, and should be understood and taken into account by you:

- Outbound payload validation switched off by default — In former releases the OData library always validated outgoing data; we switched that off now by default, as it comes with a high overhead and minimal value. You can re-enable it with `cds.env.odata.skipValidation = false`, for example for debugging reasons during development.
- Locale-specific sorting is skipped if there is no order by clause if there's no `String` column in it. Background: on SAP HANA this requires using the SAP HANA-specific `with parameters` clause, which has certain performance issues today.
- Streamlined authorization checks — Authorization for draft-enabled entities via `@restrict` was streamlined in accordance to the Authorization cookbook. First, grants of `@restrict` are now restricted to CRUD (former redundant support for NEW and EDIT got removed). Second, redundant checks for bound actions are skipped, as they are anyways covered by the "locked by user" check.

### Tailored Search with @cds.search ​

Node.js runtime now supports entity-level annotation `@cds.search` to control deep generic search capability: Just annotate those elements, which shall be searched, and which not. All elements typed `String` are searchable by default. Reduce these to increase performance.

[Learn more in Cookbook > Generic Providers > Search Capabilities.](/docs/guides/services/served-ootb#searching-data)

Note 1: In previous versions, we also included all `UUID`-typed elements by default, which we don't do anymore, due to performance reasons.

Note 2: Deep search still remains unsupported at the moment. Hence, path expressions in `@cds.search` are currently ignored.

Note 3: The element-level annotation `@Search.defaultSearchElement` is deprecated and will be removed in future versions. In the meantime, `@cds.search` supersedes those, that is, if both are defined, `@cds.search` wins.

### Scalable Multitenant Messaging Using Webhooks Beta ​

The Node.js runtime now ships with full out-of-the-box support for outbound and inbound messaging in multitenant SaaS scenarios. To ensure scalability we avoid open connections.

On the inbound side, we use [webhooks](https://wikipedia.org/wiki/Webhook) to achieve that. Instead of transferring incoming messages through a permanent AMQP connection, they are delivered through HTTP using webhooks.

[Learn more in Node.js > Messaging reference docs.](/docs/node.js/messaging#sap-event-mesh)

## Java SDK ​

### Important Changes ❗️ ​

#### Virtual Elements ​

The behaviour of virtual elements has been changed to align it with how virtual elements are [treated by the CDS Compiler v2](/docs/cds/compiler/v2#removed-virtual-elements-as-calculated-fields). Although virtual elements are present in the domain model, they are no longer reflected in the generated database view. They still can be used in queries but with some limitations. They are:

- ignored on the select list, order by and group by
- not returned by select *
- ignored in input data of insert, update, and upsert
- rejected when used in filters, where or having

### Support for H2 Database ​

With CDS Compiler v2, SQL statements are [sorted properly](#sorting-sql-statements) so that a generated [`schema.sql`](/docs/java/cqn-services/persistence-services#in-memory-storage) file can be deployed without post-processing. This allows to smoothly use [H2](/docs/java/cqn-services/persistence-services#h2-database) for local development and Continuous Integration. In order to generate SQL for H2, the sql dialect in *.cdsrc.json* has to be set to "plain":

json

```
"sql": {
    "dialect": "plain"
}
```

### Compiler v2 Support ​

The new `@sap/cds-dk@^4` including `@sap/cds-compiler@^2` is supported by the CAP Java SDK. This release also maintains compatibility with `@sap/cds-dk@^3` including `@sap/cds-compiler@^1`.

See section [Upgrade to Compiler v2](/docs/cds/compiler/v2#impact-on-java-code) for more details on the new compiler version and how it might affect your CAP Java project.

To use the new major version, you can update the `@sap/cds-dk` version in your `pom.xml` file, by setting the `version` property of the `cds:install-cdsdk` Maven goal.

[Learn more about the `cds:install-cdsdk` Maven goal.](../../java/assets/cds-maven-plugin-site/install-cdsdk-mojo.html)

### Indicating Errors ​

The method `throwIfError()` has been added to the Messages interface. It simplifies throwing a ServiceException and aborting the request after collecting multiple error messages.

[Learn more about `throwIfError()` and Messages.](/docs/java/event-handlers/indicating-errors#messages)

### Updated Java Samples ​

We have revamped our [CAP Java Sample application](https://github.com/sap-samples/cloud-cap-samples-java). Some highlights include:

- Updated SAP Fiori UIs and improved Vue.js UI
- Added ability to add reviews to books
- Showcased instance-based authorizations

You can now also take a guided tour in VS Code through our [CAP Java sample application](https://github.com/sap-samples/cloud-cap-samples-java) and learn which CAP features are showcased by the different parts of the repository. Just install the [CodeTour](https://marketplace.visualstudio.com/items?itemName=vsls-contrib.codetour) extension for VS Code.

### Support for Simple Projections in Remote Services Beta ​

You can now use CQN queries targeting your own projections on entities from external services with Remote Services. Currently only simple projections are supported, which reduce the list of selected items without renaming them:

cds

```
entity SimpleBooks as projection on Books { ID, title, descr };
entity SimpleAuthors as projection on Authors excluding { placeOfBirth, placeOfDeath };
```

[Learn more about Remote Services.](/docs/java/cqn-services/remote-services)

### Services Accepting CQN Queries ​

The interfaces `ApplicationService`, `PersistenceService`, and `RemoteService` now all implement the common interface `CqnService`, which will gradually replace the former `CdsService` interface. Consider adapting your code to use `CqnService` over `CdsService`, as it captures the intent better and avoids name clashes with `CdsService` from the [Model Reflection API](/docs/java/reflection-api).

[Learn more about these three service types and their differences.](/docs/java/cqn-services/#cdsservices)

### Compositions of Aspects ​

Using [compositions of aspects](/docs/cds/cdl#managed-compositions) is now fully supported in CAP Java. Also accessor and model interfaces are generated accordingly. For example:

cds

```
entity Orders {
  key ID: Integer; //...
  Items : Composition of many OrderItems;
}

aspect OrderItems {
  key pos : Integer;
  product : Association to Products;
  quantity : Integer;
}
```

_

Upgrading from CDS Compiler v1 to v2 will cause accessor and model interfaces for compositions of aspects to change. It is therefore recommended to firstly upgrade to CDS Compiler v2 before starting to use compositions of aspects.

## Databases Beta ​

Support for [Schema Evolution](/docs/guides/databases/hana#schema-evolution-native-db-clauses) on SAP HANA Cloud has been added as beta feature for non-productive usage and trial.
