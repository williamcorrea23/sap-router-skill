<!-- mirror: https://cap.cloud.sap/docs/releases/2023/jul23 -->
<!-- fetched: 2026-05-09T02:26:37.529Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# July 2023 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Better Documentation Search ​

The search function in Capire got several improvements that lead to **more accurate results**.

- Java or Node.js pages get prioritized in the result list depending on the language toggle. For example, results for Fiori draft now show either Java or Node.js pages, but not a mixture of both.TipIf you haven't set the toggle to Node.js or Java, you can do so now at the top of this page. This toggle applies to all pages, so you only need to set it once.
- You can use more search terms to refine your search. They're now combined with AND to allow this. Note that exact searches (with terms in quotes for example) aren't possible at the moment.
- Ambiguity got reduced. For example, cds watch doesn't find patch or batch anymore.

## CDS Language & Compiler ​

### Calculated Elements ​

We closed a gap in the implementation of calculated elements: a calculated element "on-read" can now refer to a localized element.

Example:

cds

```
entity Product {
  // ...
  description : localized String;
  descr_len : Integer = length(description);
}
```

[Learn more about Calculated Elements.](/docs/cds/cdl#calculated-elements)

### Aspects Without Elements ​

If you define an aspect solely for the purpose of carrying annotations and you don't intend to add elements to it, you can now define it without an elements list, that is, without curly braces.

Example:

cds

```
@restrict: [ /*...*/ ]
aspect AuthorizationAnnotations;
```

We plan to enable applying such aspects to services and other objects without elements in the coming releases.

### Simplified Subqueries ​

Until now, each select item needed to have a name, even if it was inside a subquery and the name was never used. You can now omit these unnecessary aliases in most cases.

Before:

cds

```
select from Products {
  // …
} where price

After:

cds

```
select from Products {
  // …
} where price

## Node.js ​

After the major release in June, we have a smaller maintenance release in July. However, there are the two following noteworthy additions.

### cds.Service.endpoints (Beta) ​

The new property `.endpoints` of a served [cds.Service](/docs/node.js/core-services#cds-service) instance is an array containing the information for all endpoints.

Consider the service definition:

cds

```
@protocol: ['odata-v4', 'rest']
@path: 'browse'
service CatalogService { ... }
```

This exposes services via OData and REST with the schema `

/

` and therefore the following value for `CatalogService.endpoints`:

js

```
[
  { kind: 'odata-v4', path: '/odata/v4/browse' },
  { kind: 'rest', path: '/rest/browse' }
]
```

See [cds.protocols](/docs/node.js/cds-serve#cds-protocols) for more details on how to configure exposures.

### @restrict for Services ​

The Node.js runtime now supports `@restrict` annotations on service level. As described in the [authorization guide](/docs/guides/security/authorization#restrict-annotation), the properties `grant` and `where` aren't applicable to services so it's ignored. [Learn more about `@restrict`.](/docs/guides/security/authorization#supported-combinations-with-cds-resources)

## Java ​

### Important Changes ❗️ ​

#### Changed Search Behaviour ​

To achieve stable search performance, the default search behaviour has been changed. Now, only elements of the type String that *aren't computed* are searched. This can lead to observable differences in the search results. Example:

cds

```
entity Persons : cuid {
  firstName : String;
  lastName : String;
  fullName : String = firstName || ' ' || lastName; // not searched by default
}
```

Here, only elements `firstName` and `lastName` will be in the scope of a search by default, but the element `fullName` will not be included anymore.

Tip

If required, use the [@cds.search](/docs/guides/services/served-ootb#cds-search) annotation to include computed String elements.

#### Localized Data ​

CAP Java by default now leverages session context variables for localized and temporal data on all databases [including H2](#h2-session-context-vars). Consequently, the property `cds.sql.supportedLocales` now defaults to an empty list indicating that session variables should be used.

Warning

- H2 needs to be updated to v2.2.220 or later
- SQLite requires the compiler configuration `{"cdsc": { "betterSqliteSessionVariables": true }}` in .cdsrc.json

### Spring Boot 3.1 ​

CAP Java now supports [Spring Boot 3.1](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.1-Release-Notes).

### Better PostgreSQL Config ​

To facilitate running CAP Java with PostgreSQL on BTP a new feature `cds-feature-postgresql` is available. The feature auto-configures the service bindings for PostgreSQL on BTP. Find detailed information in the [documentation](/docs/guides/databases/postgres?impl-variant=java#using-postgresql).

### Order by Alias ​

You may now use an alias of a select list item in [Order By](/docs/java/working-with-cql/query-api#order-by) to sort by the corresponding items. This is useful if you need to sort by a complex expression:

java

```
Select.from("bookshop.Person")
    .columns(p -> p.get("name").toUpper().as("aliasForName"))
    .orderBy(p -> p.get("aliasForName").asc());
```

### H2 Session Context Vars ​

The H2 dialect now uses session context variables for localized and temporal data. These features can now be used without restrictions.

Warning

This feature requires cds-dk 7.1 (cds-compiler 4.1) and H2 v2.2.220 or later

### Improved Maven Plugin ​

This release brings some improvements for the [CDS Maven Plugin](/docs/java/developing-applications/building#cds-maven-plugin):

- The `watch` goal of the CDS Maven Plugin can now be executed from the root directory of the CAP Java application.
- The new `add` goal allows you to add different features to the CAP Java project. Supported features are `SQLITE`, `H2`, and `MTXS`.

#### Fine-Tuned @Generated Annotation ​

The `generate` goal of the [CDS Maven Plugin](/docs/java/developing-applications/building#cds-maven-plugin) allows you to fine-tune the verbosity of the `@Generated` annotation the generated java sources with the parameter `annotationDetailLevel`. You can choose to include full information (`FULL`), omit the generation timestamp (`MINIMAL`), or suppress the `@Generated` annotation (`NONE`).

### Native Executables Beta ​

CAP Java now supports GraalVM Native Image, which enables you to compile a CAP Java application to a native executable. Native Image applications have faster startup times and require less memory.

[Learn more about using GraalVM Native Image with CAP Java.](/docs/java/operating-applications/optimizing#graalvm-native-image-support-beta)

## cds-typer: Enums, Arrays ​

We've added [documentation for `cds-typer`](/docs/tools/cds-typer) to Capire. It features a [quick start guide](/docs/tools/cds-typer#cds-typer-vscode) and has detailed explanations on how to use the generated types.

The package has also gone open source and is available on [npm](https://www.npmjs.com/package/@cap-js/cds-typer) and [GitHub](https://github.com/cap-js/cds-typer).
**Feedback, bug reports, and contributions are welcome!**

Now `cds-typer` also supports the [`array of` / `many` syntax](/docs/cds/cdl#arrayed-types), as well as [enums](/docs/cds/cdl#enums). For your convenience, the Enum values are available at runtime .

For Example, if this is your source:

schema.cdscds

```
namespace issuetracker;

type Priority: String enum {
  LOW = 'Low';
  MED = 'Medium';
  HIGH = 'High';
}

entity Issues {
  priority: Priority;
  tags: array of String;
  categories: many String;
}
```

The cds-typer will generate:

@cds-models/issuetracker/index.ts (generated by cds-typer)ts

```
const Priority = {
  LOW: "Low",
  MED: "Medium",
  HIGH: "High",
}

class Issue {
  priority: Priority
  tags: Array
  categories: Array
}
```

Finally, this is how it can be used:

srv/service.jsjs

```
const { Priority, Issue } = require('#cds-models/issuetracker')

service.before('CREATE', Issue, ({data}) => {
  data.priority = Priority.LOW
})
```
