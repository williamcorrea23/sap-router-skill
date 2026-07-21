<!-- mirror: https://cap.cloud.sap/docs/releases/2025/aug25 -->
<!-- fetched: 2026-05-09T02:26:48.447Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# August 2025 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## New capire docs & samples ​

We consolidated all our samples repos together with the one for the capire docs in one GitHub org ⇒ one location for you and us to bookmark and find them all at:

- https://github.com/capire

Among many other advantages, the new org gives us the freedom to have individual repos for each sample, instead of monorepos only.

### Continuous Deployments ​

For example, this enables real continuous [deployments](https://github.com/capire/bookshop/deployments) of individual projects to staging and production environments using respective [GitHub Actions workflows](#github-actions).

### GitHub Packages ​

It also allows us to use [GitHub Packages](https://github.com/orgs/capire/packages) for more realistic publishing and consuming reuse packages and reuse services.

Learn more about [using GitHub Packages](https://github.com/capire/xtravels?tab=readme-ov-file#using-github-packages) as well as [using local workspace setups](https://github.com/capire/xtravels?tab=readme-ov-file#using-workspaces) as an alternative in the readme of [capire/xtravels](https://github.com/capire/xtravels#readme).

### GitHub Discussions ​

In addition, we also enabled [GitHub Discussions](https://github.com/orgs/capire/discussions) in there:

NOTE

Previous locations like [https://github.com/sap-samples/cloud-cap-samples](https://github.com/sap-samples/cloud-cap-samples) are now archived.

## New & General Available ​

### Fiori Draft Messages ​

CAP's generic support for persistent Fiori draft messages, which we rolled out as beta before, is now generally available (GA), with the following features:

- Fast feedback to end users through running validations on PATCH requests.
- Seamless editing through persisted validation errors.
- Better UX through combining custom validations and annotation-based ones.

Not supported yet:

- OData V2 UIs because they don't enforce document URLs.
- OData V4 UIs using SAP UI5 version < 1.135.0.

Try it out in our [SFlight sample app](https://github.com/capire/xtravels).

NOTE

Fiori draft messages require a database schema update.

You can disable this feature with cds.fiori.draft_messages:false.

[Learn more about Draft Validations.](/docs/guides/uis/fiori#validating-drafts)

### CAP MCP Server ​

The new MCP server for CAP provides AI-powered development assistance for your CAP applications. It offers context-focused tools designed to help the AI agent better understand not only CAP APIs but also your specific project.

[`@cap-js/mcp-server`](https://github.com/cap-js/mcp-server)

Try it out to enhance your development workflow.

## CDS Language & Compiler ​

### Expressions in Annotations GA ​

CAP support for expressions as first-class annotation values is now **generally available** (GA).

Examples:

cds

```
annotate Orders with @restrict: [
  { grant:'READ', where: ( buyer = $user.id ) }
];
```

cds

```
annotate Foo with {
	bar @UI.Hidden: ( status != 'visible' );
}
```

[Learn more about Expressions as Annotation Values.](/docs/cds/cdl#expressions-as-annotation-values)

Noteworthy:

- You must enclose annotation expressions in parentheses.
- The compiler checks the validity of the expression, including the path expressions.
- The compiler rewrites propagated expressions when elements are renamed in views.
- Expressions are translated to OData annotations wherever possible.

NOTE

While the compiler supports expression values generically for all annotations, the consumer of an annotation of course also needs to understand expressions. Currently this is the case for CAP's `@restrict` annotation (support for further CAP annotations is to be expected in upcoming releases) and for several SAP Fiori annotations.

### Optimized Path Expressions ​

A path expression that addresses the foreign key of a ***managed*** to-one association is always rewritten to select the local foreign key column, instead of reading the target's equally named primary key with a join.

For example, this query:

sql

```
SELECT author.ID from Books
```

... was translated to the like of this **before**:

sql

```
SELECT author.ID from Books
LEFT JOIN Authors ON Authors.ID = author_ID
```

... while it's always translated to this **now**:

sql

```
SELECT author_ID from Books
```

This is the default behavior in the compiler and in the Node.js runtime. For Java, activate this behavior with the [cds.sql.toOnePath.mode: optimize](/docs/java/developing-applications/properties#cds-sql-toOnePath-mode) until it becomes the default.

NOTE

Both native SQL translations show identical behavior unless your data violates referential integrity. For example, if you had a foreign key without a matching target key, the new behavior returns the foreign key value, while the former one would have returned `NULL`.

### Auto-coerced Associations ​

A *managed* to-one association at a value position in a query or expression is automatically coerced to its single foreign key.

For example, while this was required **before**:

sql

```
SELECT from Books where author.ID = 150;
SELECT from Books where author.ID is not null;
```

This can be written **now** as:

sql

```
SELECT from Books where author = 150;
SELECT from Books where author is not null;
```

This works for all places where path expressions can show up, such as views and projections, or [expressions in annotations](#cxl) in CDS sources, as well as runtime queries in Node.js.

## Node.js ​

### Search by @Common.Text ​

The runtime's generic handlers for `$search` requests now automatically include elements referred to by `@Common.Text` annotations by default. For example:

cds

```
entity Books { //...
  @Common.Text : author.name
  author : Association to Authors;
}
```

[Learn more about searching data.](/docs/guides/services/served-ootb#searching-data)[CAP Java supports this feature since April 2025.](./apr25#enhanced-search)

### Streaming Query Results ​

Database services now let you stream query results for more efficient data handling. Instead of materializing the complete result set in memory, you can stream the result.

A raw stream can be obtained through [`SELECT.pipeline()`](/docs/node.js/cds-ql#pipeline) which, for example, can be piped directly to the HTTP response.

js

```
await SELECT.from(Books) .pipeline (req.res)
```

If modification at runtime is required, an object stream can be obtained through [`SELECT.foreach()`](/docs/node.js/cds-ql#foreach) or through using `for await`.

js

```
for await (let book of SELECT.from(Books)) { ... }
await SELECT.from(Books) .foreach (book => { ... })
```

[Learn more about querying data in CAP Node.js.](/docs/node.js/cds-ql#select)[Try it out in our SFlight sample application.](https://github.com/capire/xtravels)

### cds.requires w/o kind ​

You can now configure remote services without specifying `kind`, for example:

package.json.cdsrc.yamljson

```
{
  "cds": {
    "requires": {
      "SomeService": true
    }
  }
}
```

yaml

```
cds:
  requires:
    SomeService: true
```

Automatic protocol selection applies if a required service is configured without `kind` and the remote service supports multiple protocols. For example, if this service is declared like this, the best protocol is chosen automatically (`hcql` in this case):

cds

```
@hcql @rest @odata service SomeService {...}
```

[Learn more about required services.](/docs/node.js/core-services#required-services)

### cds.connect.to(<url>) ​

Method [`cds.connect.to()`](/docs/node.js/cds-connect#cds-connect-to-1) now lets you connect to remote services with just an HTTP URL. For example, use that from [`cds repl`](/docs/tools/cds-cli#cds-repl) like that:

js

```
srv = await cds.connect.to ('http://localhost:4004/hcql/books')
await srv.read `ID, title, author.name from Books`
```

The protocol is determined automatically based on occurrences of `hcql`, `rest`, or `odata` in the URL.

Note that the remote client has no model information about the remote service, so no type-specific transformations of sent queries are applied.

WARNING

This feature is **not to be used in production**!
 It's meant as a handy convenience shortcut for design-time tasks only.

### cds.linked(csn).collect() ​

New method `collect()` has been added to [`LinkedCSN`](/docs/node.js/cds-reflect#linked-csn), which can be used to filter and pick out properties of definitions, like that:

js

```
const federated_entities = cds.linked(csn).collect (
  d => d.is_entity && d['@federated'],
  d => d.name
)
```

### cds.User.authInfo ​

We introduced `cds.User.authInfo` as an optional generic container for authentication-related information. For `@sap/xssec`-based authentication strategies, such as `ias`, `jwt`, and `xsuaa`, it's an instance of `@sap/xssec`'s [`SecurityContext`](https://www.npmjs.com/package/@sap/xssec#securitycontext). This replaces the former undocumented `cds.User.tokenInfo`, which is now deprecated.

[Learn more about authentication in CAP Node.js.](/docs/node.js/authentication)

WARNING

The `cds.User.authInfo` property depends on your authentication library. CAP does not guarantee its content or existence. Use it with caution and always pin your dependencies as described in the best practices.

## Java ​

### Typed Query Results ​

You can now work more easily with query results using the generated [query builder interfaces](/docs/java/working-with-cql/query-api#concepts). For typed queries, the result is automatically typed with the corresponding [data accessor interface](/docs/java/cds-data#typed-access). You no longer need to provide the accessor interface when calling `single()`, and you can use `list()` and `stream()` to replace `listOf()` and `streamOf()`:

java

```
import static cds.gen.catalogservice.CatalogService_.BOOKS;

@Autowired
CatalogService service;

var select = Select.from(BOOKS).byId(4711);
Books book = service.run(select).single();
String title = book.getTitle();
```

To enable this feature, generate [query builder interfaces](/docs/java/working-with-cql/query-api#concepts) with the `linkedInterfaces` option:

srv/pom.xmlxml

```

  cds.generate

    generate



    - true


```

If you encounter compile errors, update your `Result` declarations to use `CdsResult`:java

```
var select = Select.from(BOOKS).byId(4711);
Result result = service.run(select);
Books book = result.single(Books.class);
CdsResult result = service.run(select);
Books book = result.single();
```

For generic results, assign to an untyped query by using `CqnSelect`:java

```
CqnSelect select = Select.from(BOOKS).byId(4711);
Result result = dataStore.execute(select);
Row book = result.single();
```

Tip`Result` now extends `CdsResult`. All methods in `Result` are also available in `CdsResult`.WarningWe've added new `run` method overloads to the `CqnService` interface. If you use Mockito to mock `run` methods in your tests and rely on argument matchers for `Select` or `Update` (for example, `any(Select.class)`) instead of `CqnSelect` or `CqnUpdate`, you may run into incompatibilities in tests. Similarly, not parameterized `Select` or `Update` declarations can cause compile-time errors.To simplify migration, use the OpenRewrite recipe to update argument matchers and parameterize untyped `Select` or `Update` declarations with `?`:sh

```
mvn org.openrewrite.maven:rewrite-maven-plugin:run \
  -Drewrite.recipeArtifactCoordinates=com.sap.cds:cds-services-recipes:4.3.0 \
  -Drewrite.activeRecipes=com.sap.cds.services.migrations.MigrateStatements \
  -DskipMavenParsing=true
```

### Attachments in Object Store Alpha ​

Version `1.2.0` of `cds-feature-attachments` now supports SAP BTP Object Store.When activated, attachments are stored in an Object Store instance instead of the default persistence. Add `cds-feature-attachments-oss` as Maven dependency in your `srv/pom.xml` to use this feature:xml

```

    com.sap.cds
    cds-feature-attachments-oss
    ${latest-version}

```

A valid Object Store service binding created for one of the supported backends is required:AWS S3
- Azure Blob Storage
- Google Cloud Storage

No support for multitenancy

The Object Store integration does only support single-tenant applications.

[Learn more about Object Store integration.](https://github.com/cap-java/cds-feature-attachments/tree/main/storage-targets/cds-feature-attachments-oss)

### Code Generator Documentation ​

To benefit from compile-time code checks, it's highly recommended to use type-safe APIs when working with CDS data in custom Java handlers. The goal `cds:generate` of the CDS Maven plugin automatically generates [accessor interfaces](/docs/java/cds-data#typed-access) for all structured CDS model types. This generator has evolved over time and offers a comprehensive feature set to control the resulting Java interfaces. Here are some example how you can use it:

- Influence the Java package names.
- Filter entities that are subject to code generation.
- Influence the style of the interfaces.
- Influence the name of the fields and methods.
- Influence API documentation of a package.

[Find here detailed documentation about the code generator.](/docs/java/developing-applications/building#codegen-config)

### Link to Index Page ​

When running CAP Java locally (development mode), the console now shows a clickable link to the index page for easy access.

## Tools ​

### IntelliJ Community Support ​

Version 2.0.0 of the [CDS IntelliJ Plugin](https://plugins.jetbrains.com/plugin/25209-sap-cds-language-support) marks a significant milestone – the plugin is now fully compatible with the free IntelliJ IDEA Community Edition, making CDS development accessible to all developers without requiring a paid license.

#### Comprehensive IDE Features ​

The plugin now supports a full range of IDE capabilities including:

- Navigation: Go to Definition, Go to Implementation, Find References, Document Links
- Code Intelligence: Hover documentation, workspace symbols, document highlights, structure tool window
- Code Quality: Range/Document formatting, quick fixes for diagnostics

#### Enhanced LSP Integration ​

The plugin leverages the *LSP4IJ* plugin for improved language server integration, providing more reliable and performant IDE features. *LSP4IJ* is automatically installed as a dependency when you install the CDS plugin.

#### Configuration & Settings ​

The new settings page allows you to configure the CDS language server under *Languages & Frameworks > CDS*:

Additional improvements include automatic Node.js interpreter detection and an `.http` file conversion *intention* for better compatibility with IntelliJ.

### ESLint Checks for JavaScript ​

We have added lint checks for JavaScript service implementations.

As an example, one of the checks can find wrongly used `SELECT` clauses that can lead to [SQL injection](/docs/node.js/cds-ql#avoiding-sql-injection) issues:

js

```
SELECT`ID`.from `Authors`.where(`name = ${name}`) // bad, ${name} is not validated
SELECT`ID`.from `Authors`.where `name = ${name}`  // OK, ${name} is validated
```

Enable all JS checks in your ESLint configuration like so:

js

```
import cdslint from '@sap/eslint-plugin-cds'
export default [ ..., cdslint.configs.js.all ]
```

[See the full list of checks.](/docs/tools/cds-lint/rules/#javascript)

## GitHub Actions Guides & Samples ​

We have added a new end-to-end guide on how to set up GitHub actions with recommended defaults.

[Read the new guide.](/docs/guides/deploy/cicd#github-actions)

In addition, the new [capire/samples](https://github.com/capire/samples) repository provides simple example workflows to [test, deploy, and release new versions](https://github.com/capire/samples/tree/main/.github/workflows).
