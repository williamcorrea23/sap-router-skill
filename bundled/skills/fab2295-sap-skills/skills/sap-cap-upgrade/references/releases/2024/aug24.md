<!-- mirror: https://cap.cloud.sap/docs/releases/2024/aug24 -->
<!-- fetched: 2026-05-09T02:26:40.764Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# August 2024 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Native HANA Associations ​

For SAP HANA, CDS associations are by default reflected in the respective database tables and views by *Native HANA Associations* (HANA SQL clause `WITH ASSOCIATIONS`).

These native associations are no longer needed for CAP:

- The CAP JAVA runtime used native associations only in very early versions.
- The new HANA database service in the CAP Node.js runtime doesn't need native associations, either.

Generation of native HANA associations increase deploy times: They need to be validated in the HDI deployment, and they can introduce indirect dependencies between other objects, which can trigger other unnecessary revalidations or even unnecessary drop/create of indexes. By switching them off, all this effort is saved.

Tip

Unless you explicitly use them in other native HANA objects, we recommend switching off their generation. For new projects, `cds add hana` automatically adds this configuration.

package.jsoncdsrc.jsonjson

```
{
  "cds": {
    "sql": {
      "native_hana_associations": false
    }
  }
}
```

json

```
{
  "sql": {
    "native_hana_associations": false
  }
}
```

Note that the first deployment after this configuration change may take longer, as for each entity with associations the respective database object will be touched (DROP/CREATE for views, full table migration via shadow table and data copy for tables). This is also the reason why we haven't changed the default so far. Subsequent deployments will benefit, however.

[Learn more in the Database Guide.](/docs/guides/databases/hana#native-associations)

## CDS Language & Compiler ​

### Generating Scripts for Postgres Schema Migration ​

You can use `cds deploy --script ...` to generate a SQL script as a starting point for a manual schema migration. In contrast to option `--dry`, it accepts and produces DDL statements for changes that potentially lead to data loss and therefore are [not supported](/docs/guides/databases/postgres#limitations) in automatic schema migration.

In the resulting script, dangerous statements are accompanied by a warning:

sql

```
-- [WARNING] this statement is lossy
ALTER TABLE sap_capire_bookshop_Books DROP price;
```

Warning

Always check and, if necessary, adapt the generated script before you apply it to your database!

[Learn more about Generating Scripts for Schema Evolution.](/docs/guides/databases/postgres#generate-scripts)

## Node.js ​

### Important Changes ❗️ ​

- Removed array methods `forEach`, `filter`, `find`, `map`, `some`, `every` from `LinkedDefinitions`. Convert linked definitions into arrays before using these methods, for example:js

```
[...linked.definitions].map(d => d.name)
```

### Dynamic cds.debug() ​

The `cds.debug()` convenient helper used in CAP implementation now supports dynamic debug output activation at runtime. In effect, you can now programmatically enable debug output for CAP modules, for example, like that:

js

```
cds.log('sql','debug') // dynamically enable SQL debug output for database modules
```

## Java ​

### Recursive Hierarchies and Fiori Tree Table Support Beta ​

CAP Java now comes with basic support for [Recursive Hierarchies](https://sap.github.io/odata-vocabularies/vocabularies/Hierarchy.html) with OData v4 on SAP HANA Cloud, allowing to serve read requests for the SAP Fiori [Tree Table](https://experience.sap.com/fiori-design-web/tree-table/), including sort, filter and search on hierarchical data.

### Control Interface Names ​

Using the new `@cds.java.this.name` annotation, you can now define the name of the generated Java interfaces for entities and structured types:

cds

```
@cds.java.this.name: 'MyJavaClass'
entity Class {
  key ID: String;

  @cds.java.name : 'clazz'
  class : String;
}
```

java

```
@CdsName("Class")
public interface MyJavaClass extends CdsData {
  String ID = "ID";
  String CLAZZ = "class";

  @CdsName(ID)
  MyJavaClass id(String id);

  @CdsName(CLAZZ)
  String getClazz();

  // [...]
}
```

Info

In contrast to `@cds.java.name`, the `@cds.java.this.name` annotation does **not** rename projections on the annotated entity when using cds-dk 8.2 or later.

[Learn more about Renaming Types in Java.](/docs/java/cds-data#renaming-types-in-java)

### Miscellaneous ​

- `cds add application-logging` now adds a configuration to your CAP Java project to enhance it with SAP Application Logging support.
- `TenantProviderService.readTenants()` is now optimized for large sets of tenants and consumes significantly less memory.

## MTX ​

### Asynchronous Extension Activation ​

The activation of extensions via the Extensibility Service API can now be run asynchronously.

If you're using the [`PUT Extension/ID` API](/docs/guides/multitenancy/mtxs#put-extensions) just set the `Prefer: respond-async` header in your request:

http

```
PUT /-/cds/extensibility/Extensions/isbn-extension HTTP/1.1
Content-Type: application/json
Prefer: respond-async

{
  "csn": ["using my.bookshop.Books from '_base/db/data-model';
           extend my.bookshop.Books with { Z_ISBN: String };"],
  "i18n": [{ "name": "i18n.properties", "content": "Books_stock=Stock" },
           { "name": "i18n_de.properties", "content": "Books_stock=Bestand" }]
}
```

A URL to the job to be polled can be found in the `Location` response header.

## Tools ​

### CDS IntelliJ Plugin on JetBrains Marketplace ​

The [SAP CDS Language Support plugin for IntelliJ](https://github.com/cap-js/cds-intellij) is now available on the [JetBrains Marketplace](https://plugins.jetbrains.com/plugin/25209-sap-cds-language-support?noRedirect=true) and thus directly installable from within IntelliJ:

[](https://plugins.jetbrains.com/plugin/25209-sap-cds-language-support?noRedirect=true)

It is available for commercial IntelliJ products including IntelliJ IDEA Ultimate and WebStorm and adds features like syntax highlighting, code completion, formatting, diagnostics, and more.

If you installed the plugin manually before from GitHub, please uninstall it first.

### Faster TypeScript Development with cds-tsx Beta ​

Use the `cds-tsx` CLI command as an alternative to `cds-ts`:

sh

```
cds-tsx watch
# or
cds-tsx serve
```

The [`tsx`](https://tsx.is/) engine used by `cds-tsx` is much faster as it omits the type checks.

[Learn more about developing with `cds-tsx`.](/docs/node.js/typescript#cds-tsx)

### Add Logging and Telemetry ​

If you want to use the [SAP Cloud Logging](https://discovery-center.cloud.sap/serviceCatalog/cloud-logging) service as an alternative to [SAP Application Logging](https://discovery-center.cloud.sap/serviceCatalog/application-logging-service), this is how you can configure it in your project:

sh

```
cds add cloud-logging
```

In case telemetry configuration is required, add it like so:

sh

```
cds add telemetry
```

This is equivalent to `cds add cloud-logging --with-telemetry`

Alternatively, you can run this command if you prefer telemetry using Dynatrace:

sh

```
cds add dynatrace
```

[See our telemetry plugins for more.](/docs/plugins/index#telemetry)
