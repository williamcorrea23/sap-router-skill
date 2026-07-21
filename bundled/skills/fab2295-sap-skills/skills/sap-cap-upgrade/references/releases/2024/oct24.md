<!-- mirror: https://cap.cloud.sap/docs/releases/2024/oct24 -->
<!-- fetched: 2026-05-09T02:26:46.274Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# October 2024 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Richer Configuration Properties in cap≽ire ​

In cap≽ire, configuration keys are now specially highlighted with a `` symbol. They also open a popover that shows how to set them in various ways.

Hover over the sample properties below and switch the different tabs in the popover. You can conveniently copy the configuration snippets using the copy button.

- cds.requires.db: sqlite (Node.js)
- cds.odata-v4.endpoint.path: /api (Java)

Let us know what you think of this feature and which configuration properties we have missed to adjust in cap≽ire.

## CDS Language & Compiler ​

### New Type: cds.Map ​

We have introduced the [built-in type](/docs/cds/types) `cds.Map` for representing an unspecified JSON Object structure.

cds

```
service People {
  entity Person {
    key ID      : UUID;
        name    : String;
        details : Map;
  }
}
```

In OData V4 EDMX, an element of type `cds.Map` is represented as an empty, open complex type. On SAP HANA, the `Map` type is mapped to `NCLOB`, on SQLite it is mapped to `JSON_TEXT`, on H2 to `JSON`, and on Postgres it is mapped to `JSONB`.

Currently restricted to CAP Java with OData V4

The type `cds.Map` currently is [only supported by the CAP Java runtime](#basic-support-for-cds-map) with OData v4.

## Node.js ​

### Customizing OData $batch Request Limits ​

We introduced a new configuration option that enables you to specifically raise the limit for the individual requests in a `$batch` request with content-type `multipart/mixed` and not for the server in general. This limit can be set with the new configuration option cds.odata.max_batch_header_size which comes with a default value of 64 KiB.

To maximize performance, the [new OData protocol adapter](/docs/releases/2024/jun24#new-protocol-adapters-ga) utilizes Node.js' native HTTP parser when parsing the body of `$batch` requests. By default, the parser has a limit of 16 KiB as described in [`http.maxHeaderSize`](https://nodejs.org/api/http.html#httpmaxheadersize).

The limit for [`maxHeaderSize`](https://nodejs.org/api/http.html#httpmaxheadersize) applies to the headers but also to the [request line](https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages#request_line).

In OData requests where the filters in the request target become very long, the request line can exceed the default limit. The common workaround is to wrap GET requests with URLs exceeding the server's limit into `$batch` requests. Our new configuration option enables you to use this workaround while preserving a reasonable limit.

## Java ​

### Important Changes ❗️ ​

#### Removed Dependency to Deprecated Multitenant Library ​

To support multitenancy, CAP Java internally consumes APIs offered by SAP BTP [multitenant libraries](https://central.sonatype.com/namespace/com.sap.cloud.mt) (Maven group ID `com.sap.cloud.mt`). These libraries have been put into maintenance mode, so starting with this version, CAP Java has removed these dependencies and adopted the base implementation.

I used multitenancy APIs directly. What can I do?

If you made *explicitly* use of these multitenancy APIs, you can continue to offer most of them through new packages CAP Java offers. The new packages are `com.sap.cds.feature.mt.lib` and `com.sap.cds.services.utils.lib` respectively. You need to adapt package names in your custom code accordingly.

Warning

Direct usage of these multitenant APIs is deprecated and might be removed in future versions. Consume public APIs offered by CAP instead.

#### Hardened Authorization of Tenant Lifecycle Endpoints ​

By default, internal user access to tenant lifecycle endpoints, that is subscribe, unsubscribe or upgrade, is rejected in production profile now. You can control internal user access by property cds.multi-tenancy.security.internal-user-access.enabled.

Important Note for applications on DwC

Make sure to adopt at least version `2.3.15` of `utils-cap`.

### Basic Support for cds.Map Beta ​

You can now use the new [built-in `cds.Map` type](/docs/cds/types) for storing and retrieving arbitrary structured data. Values of elements with type `Map` are represented in CAP Java as `Map`.

- On write, the map data is serialized to a JSON object and stored on the database.
- On read, the JSON object is deserialized into a Java Map.

Since the map is serialized to a JSON object, the type of elements inside `Map` is limited to what is supported by JSON: strings, numbers, Boolean values and null, as well as nested maps and lists.

Given the CDS model using the new `Map` type for `Person.details`:

cds

```
entity Person {
  key ID      : UUID;
      name    : String;
      details : Map;
}
```

You can store arbitrary data in `details`:

java

```
Map person =
  Map.of("name", "Peter",
         "details", Map.of(
            "age", 40,
            "address", Map.of(
              "city", "Walldorf",
              "street", "Hauptstraße")));

Insert.into("Person").entry(person);
```

When you read the `Person` entity, `details` is deserialized into a Java map:

java

```
Person p = db.run(Select.from(PERSON).byId(1024)).single(Person.class);
CdsData details = p.getDetails();
Integer age = details.get("age"); // 40
String city = details.getPath("address.city"); // Walldorf
```

You can also extract data from within a map using paths:

java

```
Select.from("Person").byId(1024).columns("details.address");
// -> { address : { city : 'Walldorf', street: 'Hauptstraße' } }

Select.from("Person").byId(1024).columns("details.address.city");
// -> { city : 'Walldorf' }
```

Temporary Limitations

Filters on `cds.Map` elements, as well as partial updates and deletes are not yet supported.

### Enhancements for CDS QL ​

#### IN Subqueries ​

Use an in-subquery predicate to test if an element or a tuple of elements is contained in the result of a subquery. In the following, we select all authors, with the same name as a journalist:

java

```
import static bookshop.Bookshop_.AUTHORS;
import static socialmedia.Journalists_.JOURNALISTS;

// fluent style
Select.from(AUTHORS).where(author -> author.name().in(
  Select.from(JOURNALISTS).columns(journalist -> journalist.name())
));
```

You may also use `CQL.in` to create an in-subquery predicate. In the following, we search for matches of the element pair `(firstName, lastName)`:

java

```
// tree style
CqnListValue fullName = CQL.list(CQL.get("firstName"), CQL.get("lastName"));
CqnSelect subquery = Select.from("socialmedia.Journalists").columns("firstName", "lastName");
Select.from("bookshop.Authors").where(CQL.in(fullName, subquery));
```

[Learn more about `IN` subqueries.](/docs/java/working-with-cql/query-api#in-subquery-predicate)

#### Case-When-Then Expressions ​

You can now use a convenient API to compose case expressions:

java

```
Select.from(PERSONS).columns(
  p -> p.name(),
  p -> p.when(p.age().lt(25)).then("young")
        .when(p.age().ge(75)).then("elderly")
        .orElse("adult").as("ageTxt").type(CdsBaseType.String));
```

This query converts a person's numeric `age` value to a textual `ageTxt` representation.

### Enhancements for OData v4 ​

#### Content Disposition Type ​

For stream properties, you may now use the `@Core.ContentDisposition.Type` annotation to indicate whether the content is expected to be displayed *inline* in the browser, or as an attachment that is downloaded and saved locally.

cds

```
entity Books : uuid {
  ...
  @Core.MediaType: 'image/jpeg'
  @Core.ContentDisposition.Type: 'inline'
  coverImage : LargeBinary ;
}
```

When downloading the `coverImage` the runtime will set a `Content-Disposition: inline` header to advise the browser to display the cover image in the browser.

#### Omitting Null Values ​

In a GET request, the client may now specify a `Prefer: omit-values=nulls` header to indicate that the server may omit `null` value in the response.

### Tool Support for AMS ​

Use the [add](../../java/assets/cds-maven-plugin-site/add-mojo.html) goal of the [CDS Maven Plugin](/docs/java/developing-applications/building#cds-maven-plugin) to add [AMS](/docs/guides/security/cap-users#roles-assignment-ams) integration to a CAP Java project:

sh

```
mvn cds:add -Dfeature=AMS
```

## Tools ​

### Renaming CDS Files in VS Code ​

When you rename a *.cds* file or a folder which contains CDS files, this automatically updates usages in other *.cds* files.

If you delete a *.cds* file, the plugin shows you usages in other *.cds* files.

Note: Currently, Visual Studio Code asks for confirmation first, then shows the additional refactorings in other files. At that point, it is no longer possible to cancel the deletion. The refactorings are only for information. Applying them will likely lead to (other) compilation errors. Use (git) `Undo` in case.
