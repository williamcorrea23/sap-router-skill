<!-- mirror: https://cap.cloud.sap/docs/releases/2024/may24 -->
<!-- fetched: 2026-05-09T02:26:45.063Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# May 2024 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

*The May 2024 release only contains updates for the CAP Service SDK for Java.*

## Java ​

### Diff Processor ​

In business logic, there might be the need to compare two states of an entity, for example, before and after an operation. Usually, you want to react on changed values, for instance, to track changes accordingly. For this purpose you can now use the new `CdsDiffProcessor` API. It traverses through two states of the entity and reports differences to a `CdsDiffVisitor`, which can react on the changes according to the use case's needs:

java

```
CdsDiffProcessor diff = CdsDiffProcessor.create();
diff.add(new DiffVisitor() {
  @Override
  public void changed(Path newPath, Path oldPath, CdsElement element, Object newValue, Object oldValue) {
      // for example, log changes
  }

  @Override
  public void added(Path newPath, Path oldPath, CdsElement association, Map newValue) {
      // for example, send out event
  }

  @Override
  public void removed(Path newPath, Path oldPath, CdsElement association, Map oldValue) {
      // for example, delete related resources
  }
});

Result newImage = service.run(Select.from(...));
Result oldImage = service.run(Select.from(...));

diff.process(newImage, oldImage, newImage.rowType());
```

[Learn more about the Diff Processor.](/docs/java/cds-data#diff-processor)

### Change Tracking - Human-Readable Identifiers for Associations ​

You can now use the `@changelog` annotation to specify a human-readable identifier for an associated entity:

cds

```
annotate Orders {
  customer @changelog: [ customer.name ]
}
```

With this annotation, the change log will not log the (technical) customer ID if an associated customer changes but instead the customer's name is logged.

[Learn more about Identifiers for Associated Entities.](/docs/java/change-tracking#human-readable-values-for-associations)

### Fuzzy Search on SAP HANA Cloud Beta ​

If you run CAP Java in [`HEX` optimization mode](/docs/java/cqn-services/persistence-services#sql-optimization-mode) on SAP HANA Cloud, you can now enable [fuzzy search](/docs/guides/services/served-ootb#fuzzy-search) in your *application.yaml* and configure the default fuzziness (range [0.0, 1.0], 1.0 is exact).

yml

```
cds.sql.hana.search
   fuzzy: true
   fuzzinessThreshold: 0.9
```

Override the fuzziness for elements, using the `@Search.fuzzinessThreshold` annotation:

cds

```
entity Books {
  @Search.fuzzinessThreshold: 0.7
  title : String;
}
```

### Exact Wildcard Search ​

The wildcards '*' matching zero or more characters and '?' matching a single character are now supported in search terms. Using wildcards in [fuzzy search](/docs/guides/services/served-ootb#fuzzy-search) mode triggers a fallback to *exact pattern search*. You can escape wildcards using '\'.

### Control Max Age of HTTP Responses ​

Use the `@http.CacheControl: {maxAge: }` and CAP Java will set a corresponding `Cache-Control: max-age=` header in the response. The header allows to control the behavior of client-side caches, the `max-age` (in seconds) specifies the maximum age of the content before it becomes stale:

cds

```
entity Book : uuid {
  title : String;
  @http.CacheControl: { maxAge: 86400 }
  @Core.MediaType: 'image/png'
  cover : LargeBinary;
  price : Decimal(10,2);
}
```

The client may cache the cover image for 86400 s (1 day).

### OData v4 - Key-as-Segment Convention ​

For OData v4, CAP Java now supports the Key-as-Segment Convention in the URL.

You can now send:

http

```
GET https://host/service/OrderItems/1/2
```

Which is equivalent to:

http

```
GET https://host/service/OrderItems(OrderID=1,ItemNo=2)
```

[Learn more about the Key-as-Segment Convention](https://docs.oasis-open.org/odata/odata/v4.02/csd01/part2-url-conventions/odata-v4.02-csd01-part2-url-conventions.html#KeyasSegmentConvention)

### CAP Developer Dashboard Alpha ​

The CAP Developer Dashboard simplifies development by providing a centralized point where developers can efficiently manage and monitor their CAP applications. It offers tools and functions to support the development process and helps developers to quickly identify and resolve problems. Additionally, the dashboard facilitates better integration of CAP components, such as messaging, resilience and multitenancy, ensuring seamless functionality throughout CAP applications.

Add the `cds-feature-dev-dashboard` feature to your maven dependencies:

xml

```

    com.sap.cds
    cds-feature-dev-dashboard

```

Navigate to the dashboard using the "Dashboard UI" navigation link on the index page:

Only to be used in development

The dashboard is only intended for use in the development environment. It is strictly forbidden to use the dashboard in a production environment, as it allows access to sensitive data and presents a security risk.
