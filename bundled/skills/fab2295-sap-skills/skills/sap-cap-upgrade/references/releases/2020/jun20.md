<!-- mirror: https://cap.cloud.sap/docs/releases/2020/jun20 -->
<!-- fetched: 2026-05-09T02:26:21.767Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# June 2020 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Important Changes❗️ ​

### Move from npm.sap.com to npmjs.org ​

`@sap` Node.js packages have moved from `https://npm.sap.com` to the default registry `https://registry.npmjs.org`.

As future versions are going to be published only there, make sure to adjust your registry with:

sh

```
npm config delete "@sap:registry"
```

## Docs and Samples ​

### Search Results in Browser History ​

When you search through the documentation (the little magnifying glass), the search is now stored in the browser history. This way, you can come back to the search list after you have navigated to the results. Also, you can now bookmark and share your search. Just copy the `.../search?q=...` URL from your browser address bar.

### New and Revised Sections and Guides ​

New Guides and Sections:

- Node.js > Best Practices > Securing Your Application
- Java > Executing CQN Queries > Querying Views with Parameters
- Java > Development > Spring Boot Integration
- Java > Development > Databases > H2 Database
- Java > Development > CDS Maven Plugin
- Support → Use our support channel or ask a question in the CAP community

Revised Guides and Sections:

- About → Major Improvements
- About > Features Overview
- CDS > OData Annotations
- Node.js > Authentication

## Java Runtime ​

### Implicit Paging and Sorting ​

By default, the generic handlers for READ requests automatically truncate result sets to a size of 1,000 records max ([implicit pagination](/docs/guides/services/served-ootb#implicit-pagination)). The default page size can be controlled by means of the CDS annotation `@cds.query.limit.default` per service or application configuration property `cds.query.limit.default`. The maximum value can be controlled by means of the CDS annotation `@cds.query.limit.max` per service or the global application configuration property `cds.query.limit.max`.

In addition, the result is [implicitly sorted](/docs/guides/services/served-ootb#implicit-sorting). By default the entity's primary key is used as sort criterion. This feature can be turned off by means of the application configuration property `cds.query.implicitSorting.enabled: false`.

### OData Singletons ​

Read requests on entities annotated with `@odata.singleton` are now supported.

### Asynchronous Tenant Subscription API ​

The Java runtime now supports asynchronous tenant subscription requests on the SAP Cloud Platform. This is useful if tenant onboarding takes much time and would hit the timeout of a synchronous tenant subscription.

### Fiori Drafts ​

Added support for `$orderby`, `$top`, and `$skip` for [draft enabled entities](/docs/guides/services/served-ootb#implicit-sorting).

### Input Validation ​

You can now validate enums by means of the annotation [@assert.range](/docs/guides/services/constraints#assert-range).

### Clean Project Setup ​

Projects created with the [CAP Java archetype](/docs/java/getting-started#run-the-cap-java-maven-archetype) now use the [CDS Maven Plugin](/docs/java/developing-applications/building#cds-maven-plugin) during build. This plugin replaces a bunch of 3rd party plugins and boiler plate *pom.xml* code, making newly created projects much cleaner.

### Improved ETag Support ​

- ETag conditions on `$metadata` endpoints are now evaluated. OData responses also now contain the `@metadataEtag` field.
- ETag conditions on OData bound actions or function requests are now evaluated. ETag conditions evaluated through selection now lock the affected row for update.
- The OData entity response field `@etag` (>= 4.01) or `@odata.etag` (4.0) is now set when returning collections of entities or expanded entities that have an ETag.

### CDS.QL ​

- Limit and offset of select statements can be modified.
- Limit and offset are now also supported in expands.
- Queries on parameterized views are supported on SAP HANA. See also Java > Executing CQN Queries for more details.
- `$now` is supported as default value for inserts.
- Lock statements on SQLite are silently ignored and executed as select queries instead of throwing an exception.

### Bug Fixes ​

- Fixed a bug where exception messages of non-framework exceptions were displayed to the end user, despite non-custom error messages being disabled.
- Fixed a bug where a null OData function argument value caused a NullPointerException.
- Fixed a bug where multiple Spring contexts caused prevented the app from being started.
- UUIDs in OData requests are now normalized by converting them to lowercase.
- An UnsupportedOperationException is thrown on deep updates with more than one entry.
