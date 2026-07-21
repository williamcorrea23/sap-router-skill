<!-- mirror: https://cap.cloud.sap/docs/releases/2020/sep20 -->
<!-- fetched: 2026-05-09T02:26:24.359Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# September 2020 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtx?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Command Line / Toolkit ​

### Interactive Commands in cds watch ​

After `cds watch` has started, you can type commands like:

- `` or `rs` to restart the application
- `ps` to show a simple list of the involved processes with their IDs
- `debug` to enter debug mode (see below)
- `bye` or Ctrl + C to stop watching

### Debug Handler Code with cds watch ​

Start `cds watch` and enter `debug`. This restarts the application in debug mode. Similarly, `debug-brk` will start debug mode, but pause the application at the first line, so that you can debug bootstrap code.

If you do this in VS Code's integrated terminal with the 'Auto Attach' feature enabled, debugging starts right away:

If you executed `cds watch` on a standalone terminal, you can still attach a Node.js debugger to the process.

For example:

- In VS Code, use the Debug: Attach to Node Process command.
- In Chrome browser, just open chrome://inspect and click Inspect.

## CDS Editors & Tools ​

### Editing OData Annotations ​

There is a new plugin for the editor, which helps you add and edit OData annotations in CDS syntax. The OData annotation plugin supports the following features:

- Code completion for annotations applied to entities and entity elements]
- Validation against the OData vocabularies and project metadata
- Navigation to the referenced annotations
- Quick view of vocabulary information
- Internationalization (i18n) support for language dependent strings

 The following features are available for all editors based on our language server implementation for CDS in SAP Business Application Studio, Visual Studio Code, and Eclipse. The plugins are available for download for Visual Studio Code at [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=SAPSE.vscode-cds#overview) and for Eclipse at [https://tools.hana.ondemand.com](https://tools.hana.ondemand.com/#cloud-vscodecds).

### Plugin Support for Domain-Specific Annotation Handlers ​

The editor now contains a plugin framework for semantical annotation editing. A first plugin for OData annotations will be available in the coming weeks and installed automatically.

All features are additional to the existing ones but provide semantical refinements. Among the features are:

- Diagnostics (semantical markers like errors, warning etc.)
- Code completion for the supported annotation domain, including details where available.
- Hover information
- Go to definition of certain annotation keys or values.
- Quickfix to convert a simple text value into a translation key and create a corresponding translation pair in the translation file.

Plugins to this framework are automatically installed. Updates to plugins will be fetched in the background and are in place after restart. Use a user setting, to override the default npm registry from which you get the plugins, for example in private cloud environments.

Inside annotation values code completion is also triggered using `/` character, next to `.`, and `@`.

### Formatting of Code Snippets ​

Snippets applied using code completion are now formatted according to the user defined formatting settings.

### Quickfixes in Problems View ​

Quickfixes are now accessible in diagnostic popups and in the *Problems* view.

Some quickfixes are now *preferred*, allowing an even quicker access using specific keyboard shortcut.

### More Code Navigations ​

Code navigation to go to the definition or find references are now available for `action`s, `function`s, and their parameters.

### Release Notes in VS Code ​

The release notes are now displayed when a new version is available on /releases/.

### Command to Check and Install @sap/cds-dk Globally in VS Code ​

The command **install CDS Development Kit (@sap/cds-dk) globally** is now available to check for updates and install **@sap/cds-dk** globally on your machine.

## CDS Language & Compiler ​

### Simplified type references ​

When referencing types of elements, the `type of` keyword was mandatory - this is no longer the case. Previously, only the following was valid:

cds

```
entity Foo {
  key id: Integer;
}

entity Bar {
  key id: type of Foo:id;
}
```

`Bar` can now be rewritten like this:

cds

```
entity Bar {
  key id: Foo:id;
}
```

See [CDL > Type References](/docs/cds/cdl#type-references) for more details.

### cast(element as Type) ​

The compiler now supports the `cast(element as Type)` function in queries. Using this function will also result in a `CAST` SQL function call. The `element as alias: Type` syntax is still supported, but will not result in SQL `CAST` calls.

In CDL, the cast looks like this:

cds

```
view V as select from E {
  cast( element as String ) as castedElement,
  element as cdlCastedElement: String
};
```

In CSN, it looks like this:

JSON

```
"columns": [
    {
      "xpr": [
        {
          "ref": [
            "element"
          ],
          "cast": {
            "type": "cds.String"
          }
        }
      ],
      "as": "castedElement"
    },
    {
      "ref": [
        "element"
      ],
      "as": "cdlCastedElement",
      "cast": {
        "type": "cds.String"
      }
    }
  ]
```

Which will ultimately result in the following SQL:

SQL

```
CREATE VIEW V AS SELECT
  CAST(E_0.element AS NVARCHAR(5000)) AS castedElement,
  E_0.element AS cdlCastedElement
FROM E AS E_0;
```

## Node.js Runtime ​

### Important Changes ❗️ ​

### Structured Elements in OData V4 for APIs ​

The Node.js runtime now offers native support for structured elements in OData. Entities modelled as structured in CDS can now be queried with OData without using the 'underscore notation' and the result returned will be a structured object instead of the previously flattened result. To enable structured mode the [`odata.flavor = x4` flag](/docs/node.js/cds-env#project-settings) needs to be set.

Structured:

http

```
GET /Books?$filter=author/ID eq 5
```

JSON

```
{
    author : {
      ID: 5
    },
    ...
}
```

Unstructured:

http

```
GET /Books?$filter=author_ID eq 5
```

JSON

```
{
    author_ID: 5,
    ...
}
```

Supported features included:

- Structured elements in `$orderby`, `$filter`, and `$select` queries
- Assertions in structured data
- Navigating to association to-one in structured

### Miscellaneous ​

- Generic input validation also apply to actions and functions.
- Support for `@assert.notNull: false`
- Support for annotation `@Capabilities.ReadRestrictions.Readable`
- Messaging: An ID is automatically generated for each message (`headers.id`).
- Support for custom timezone offset in OData queries (2020-09-27T22:07:00Z and 2020-09-27T21:07:00+01:00).

## Java Runtime ​

### Important Changes ❗️ ​

The module `cds-services-impl` isn't a compile time dependency anymore. This prevents application developers from using internal APIs. Applications that already use methods and classes from `cds-services-impl` will experience compile time errors like `error: cannot find symbol`. Thus, application developers need to switch to public APIs only provided by module `cds-services-api`.

### Native OData V2 Adapter (Beta) ​

The CAP Java runtime now supports OData V2 natively. Despite not yet GA, this feature is ready to be tested by early adopters. In order to use the OData V2 adapter, add the following dependency to your *pom.xml* file:

xml

```


        com.sap.cds
        cds-starter-spring-boot



        com.sap.cds
        cds-adapter-odata-v2


    ...

```

Note, that currently you can't use the OData V2 and OData V4 adapter at the same time. We'll support this in an upcoming CAP Java release. Therefore, remove the following dependency from your project:

xml

```

        com.sap.cds
        cds-starter-spring-boot-odata

```

In addition, make sure to change the OData version of your CDS build configuration to `v2` in *.cdsrc.json* or *package.json*, so that the correct EDMX is generated for the OData V2 adapter.

### SAP Fiori Drafts with Timeouts ​

By default, SAP Fiori drafts that aren't activated or updated are now automatically garbage collected after a timeout of 30 days. For example, this is useful when users that have created inactive draft entities don't exist anymore.

The timeout is configurable by application configuration. The following example extends the timeout to 8 weeks:

yaml

```
cds.drafts.deletionTimeout: 8w
```

This feature can be also turned off completely by setting the application configuration:

yaml

```
cds.drafts.gc.enabled: false
```

See [Java > Garbage Collecting Drafts](/docs/java/fiori-drafts#draft-gc) for more details.

### OData V4 Lambda Operators ​

The OData V4 adapter supports [OData Lambda operators](https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part2-url-conventions.html#_Toc31361024) `all` and `any`:

http

```
http://host/service/Authors?$filter=books/any(b:b/year eq 2000)
```

### Export Default Error Messages ​

It's now possible to export the default error messages thrown by the CAP Java runtime to a resource bundle file for further processing (for example, to customize or to translate error messages). See [Java > Indicating Errors](/docs/java/event-handlers/indicating-errors) for more details.

### AllMatch/anyMatch Predicates ​

Allow to [filter by values](/docs/java/working-with-cql/query-api#any-match) of elements in an associated collection through the Builder API methods `.anyMatch(

)` and `.allMatch(

)`. For example this query selects authors that have written *any* book in the year 2000:

java

```
Select.from(AUTHORS).where(a -> a.books().anyMatch(b -> b.year().eq(2000)));
```

### Entity References from Query Result ​

Simplify writing queries on the source entity of another query's result using [entity references](/docs/java/working-with-cql/query-execution#entity-refs) that can be obtained through the result row's `ref()` method:

java

```
CqnSelect query = Select.from(AUTHOR).byId(101);
Author authorData = service.run(query).single(Author.class);

// Author[101]
Author_ author = authorData.ref();

// SELECT from Author[101].books where year = 2000
Select.from(author.books()).where(b -> b.year().eq(2000));
```

### Updatable Views ​

Execute deep insert/upsert operations through [updatable views](/docs/java/working-with-cql/query-execution#updatable-views).

### Miscellaneous ​

- Support search by UUID
- The Reflection API now allows to check if a `CdsElement` is localized through the new `isLocalized` method.
