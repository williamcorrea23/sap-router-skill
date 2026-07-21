<!-- mirror: https://cap.cloud.sap/docs/releases/2020/may20 -->
<!-- fetched: 2026-05-09T02:26:22.967Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# May 2020 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Docs and Samples ​

### New cap/samples Based on Java ​

Find the new bookshop sample application based on CAP Java on [GitHub](https://github.com/SAP-samples/cloud-cap-samples-java).

### New Look and Feel for Code Blocks ​

For commands that are specific to bash, command prompt, and PowerShell, we introduced a new look and feel. Switch between these versions selecting the tab you need.

### Improvements for Mobile Usage of the Documentation ​

We take feedback seriously and therefore we've improved the mobile usage of our documentation.

### New and Revised Sections and Guides ​

New Guides and Sections:

- Cookbook > Using Databases
- Java > Getting Started > Sample Application→ new bookshop sample application based on CAP Java
- Java > Query Builder API > Copy & Modify CQL Statements
- Java > Query Introspection API
- Java > Development > Application Configuration > SQL Lite
- Java > Development > Database Support in Java > SQL Lite
- Java > Migration → steps how to migrate your classic Java Runtime to the new CAP Java SDK

Revised Guides and Sections:

- About → we've revised all figures
- Cookbook→ we have revised all figures
- CDS > Common Annotations
- Java > Security
- Node.js > APIs > `cds.connect.to`
- Node.js > APIs > `srv.on`
- Node.js > APIs > `SELECT.one`
- Advanced > Troubleshooting > Setup
- Advanced > Troubleshooting > SQLite

## Java Runtime ​

### Important Changes ❗️ ​

- The CDS Data Store automatically generates UUID values on input if no value is provided. UUIDs are lowercased on input.

### Model Reflection API ​

- CDS Model can be read from CSN InputStream or String, see Java > Reflection API > The CDS Model
- Support of Enum Types

### Query Builder / Service Consumption API ​

- API for modification of CQL statements available, see Java > Query Builder API > Copy & Modify CQL Statements.
- Streaming for LargeString and LargeBinary types annotated with `@Core.MediaType`, see Java > Executing CQN Queries > Using I/O Streams in Queries.
- Support collation on SAP HANA providing locale-specific comparison and sorting of strings, see Java > Development > Database Support in Java > SQLite.
- Provide case-insensitive comparison and sorting of strings on SQLite
- `@cds.search` annotation supported, see Java > Query Builder API > Select
- `count()` function supported, by using `CQL.count()`
- case-insensitive contains supported, for instance `Select.from("Books").where(b -> b.get("title").contains(CQL.literal("CAP"), true))`;

### Input Validation ​

Support for input validation on ordinal types (`@assert.range`) and string expressions (`@assert.format`) has been added. All valid constraints defined on entity elements of simple type are checked in an early BEFORE-handler of the CDS service. CUD-Requests, which don't match one of the constraints, are rejected.

- `@assert.range` (see Cookbook > Providing Services > Input Validation) validates the ranges on ordinal data types such as numbers, dates, and times (enums not yet supported):

cds

```
entity RangeEntity {
 key ID : UUID;
 @assert.range: [0, 23] hour: Integer;
 @assert.range: [0.001, 9.999] lessThan10: Double;
 @assert.range: ['2018-01-01', '2018-12-31'] in2018: Date;
 @assert.range: ['23:00:00', '23:59:59'] time: Time;
 @assert.range: ['2008-02-13T09:00:00Z', '2020-02-20T09:00:00Z'] datetime: DateTime;
}
```

```
{:.indent}

```

- `@assert.format` (see Cookbook > Providing Services > Input Validation) provides a powerful tool to make sure that input strings match a regular expression in ECMA 262 format:

cds

```
 entity FormatEntity {
 key ID : UUID;
 @assert.format: '^\p{Lu}.*' authorName : String(30);
 @assert.format: '[\\w|-]+@\\w[\\w|-]*\\.[a-z]{2,3}' email: String;
 @assert.format: '^\d+(\.\d+)?' chapter: String;
 @assert.format: '[a-zA-Z][a-zA-Z][a-zA-Z]' threeChars: String;
}
```

### CSV Import ​

CSV file import has been enhanced with some helpful features, which make it more flexible:

- File locations and file endings of the CSV files has been made configurable (example shows the default values):

yaml

```
cds:
  datasource:
    csvFileSuffix: .csv
    csvPaths:
      - db/data/**
      - db/csv/**
      - ../db/data/**
      - ../db/csv/**
```

All paths ending with `/**` are searched recursively.

- More flexible header line delimiters: either `;` or `,` is accepted.
- More detailed error messages on import data that is inconsistent with the CDS model.

### OData V4 Protocol Adapter ​

The OData adapter accepts `GET` requests with `$value` URI suffix on primitive entity properties. Whereas the path to a single property delivers a full OData JSON-response:

bash

```
$ curl http://acme/odata/v4/Catalog/Authors(01a4c48c-0dfc-4507-abc6-9b54a431b78a)/name
{"@context":"../$metadata#Authors%2801a4c48c-0dfc-4507-abc6-9b54a431b78a%29/name","value":"AnAuthor"}
```

`$value` picks the `value` property for the response only:

bash

```
$ curl http://acme/odata/v4/Catalog/Authors(01a4c48c-0dfc-4507-abc6-9b54a431b78a)/name/$value`
William Shakespeare
```

### Authorization ​

- Instance-based authorization is active by default, that means, `where` conditions of `@restrict`-annotated entities are evaluated for events `READ`, `UPDATE`, and `DELETE`. There are some limitations related to paths in the `where` expression, see Java > Security.
- Introduced enhanced expression parser for the `where` condition, which allows automatic type conversion of user attributes.
- Grants for draft-related events such as `draftEdit`, `DRAFT_CANCEL`, or `DRAFT_NEW` etc. are derived from grants of standard CQN events. For instance, granted event `CREATE` implies also `DRAFT_NEW`. Before that, draft events had to be listed in `@restrict` annotations in order to permit access.
- The `where` condition of `@restrict` won't apply anymore for draft entities on events `READ`, `DELETE`, and `UPDATE`. This allows to create and edit draft entities, which temporarily don't match the condition. The condition will be checked when activating the draft entity.
- Support for new keyword `$UNRESTRICTED` in user attribute value lists. Soon XSUAA will issue JWT tokens with potential `$UNRESTRICTED` string values in attribute lists of unrestricted users. Unrestricted attributes will be dropped by the runtime when evaluating where-conditions of `@restrict` annotated entities during instance-based authorization. The former logic - unrestricted access indicated by empty attribute value lists - will be removed in a later version after some transition period.

### Miscellaneous ​

- Enhanced temporal data support: Allow date only values (for example, `2020-04-24`) for `sap-valid-from`, `sap-valid-to`, and `sap-valid-at` request parameters.

### Bug Fixes ​

- Fixed server error on malformed OData requests that contain an unknown action or function.
- The default ON-handlers for `AuthorizationService` now have a proper default order number. This enables custom handlers to override them on demand.
- `$expand=*` isn't supported for draft enabled entities. This is reflected with an improved error message now.
