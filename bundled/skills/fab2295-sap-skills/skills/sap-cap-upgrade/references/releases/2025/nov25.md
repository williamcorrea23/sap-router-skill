<!-- mirror: https://cap.cloud.sap/docs/releases/2025/nov25 -->
<!-- fetched: 2026-05-09T02:26:54.209Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# November 2025 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Status-Transition Flows Beta ​

Status-transition flows enable you to implement simple state-based workflows without writing a single line of code. Define flows (statuses and transitions) directly in your CDS model using annotations.

Add a flow declaration like this:

cds

```
annotate Travels with @flow.status: Status actions {
  rejectTravel    @from: #Open  @to: #Canceled;
  acceptTravel    @from: #Open  @to: #Accepted;
  deductDiscount  @from: #Open;
};
```

Handlers for validating entry conditions (`@from`) and setting target states (`@to`) are automatically generated and registered. When you define a target state as `$flow.previous`, CAP automatically adds the necessary data structures to track transitions and restore previous states. You can override the generated logic when needed, providing flexibility for complex scenarios.

CAP also generates UI annotations to make actions triggerable from Fiori Elements Object Pages, including automatic button disabling when the entry state is invalid.

[Learn more about Status-Transition Flows.](/docs/guides/services/status-flows)

## CDS Language & Compiler ​

### Security Annotations ​

The compiler typically emits a warning when an annotation cannot be applied because its target is invalid. For example:

cds

```
entity Books {
    // ...
    genre : Association to Genres;
}

annotate Books:genres with @title: 'Genre'; // typo: should be Books:genre
```

For security-related annotations (`@restrict`, `@requires`, and `@ams`), invalid annotate statements now result in an error instead of a warning:

cds

```
annotate Books:genres with @ams.attributes: {
  Genre: (genre.name)
};
```

This results in the following error:

log

```
Error[ext-undefined-element-sec]: Element "genres" has not been found
```

We strongly recommend to fix these errors. But you can also downgrade the error to a warning with cds.cdsc.severities.ext-undefined-element-sec:Warning.

## Node.js ​

### $compute in OData V4 Beta ​

The OData query option [`$compute`](https://docs.oasis-open.org/odata/odata/v4.02/csd01/part2-url-conventions/odata-v4.02-csd01-part2-url-conventions.html#SystemQueryOptioncompute) allows specifying arbitrary expressions, which are now partially supported.

The implemented feature set includes numeric operands, the operators `add`, `sub`, `mul`, `div`, and `divby`, and grouping with parentheses. Although the specification distinguishes between `div` and `divby` for result types, we currently treat them identically for simplicity.

http

```
GET /Travels
  ?$compute=BookingFee mul 100 divby TotalPrice as PctOfAdminCosts
  &$select=PctOfAdminCosts
```

[Learn more about OData in general.](/docs/guides/protocols/odata)

## Java ​

### Important Changes ❗️ ​

#### Numeric Type Promotion ​

Numeric type promotion is now handled in the CAP Java runtime, resulting in consistent behavior across different databases.

Arithmetic expressions no longer implicitly narrow to Integer types; division with non-approximate types yields Decimal.

In case your handler code relies on specific Java types resulting from arithmetic expressions, use `type(CdsBaseType)` to explicitly set the type.

[Learn more about Numeric Type Determination in Working with CDS Data.](/docs/java/cds-data#numeric-type-determination)

### Calculated Elements for Drafts ​

Requires `@sap/cds@^9.5.0`

This feature requires usage of `@sap/cds@^9.5.0` in the CAP Java project.

Previously, calculated elements of draft-enabled entities couldn't be reliably used for values shown on the UI or for influencing UI behavior. As a consequence, you likely used `virtual` elements with custom calculations in code instead.

Values of calculated elements are now properly calculated when querying drafts from the `_drafts` table. This works whether they are defined in the domain entity or in a view or projection. Calculated elements in the `_drafts` table are always calculated on read, even if the original calculated element is `stored`.

Call to action

Reconsider using calculated elements instead of `virtual` elements, to avoid custom code and to push calculations to the database.

[Learn more about calculated elements.](/docs/cds/cdl#calculated-elements)

### Outbox Improvements ​

#### Processing Strategy ​

Improved processing of outbox messages is now enabled [by default](./apr25#optimized-outbox). The improved processing avoids regularly iterating over all tenants. Instead, asynchronous outbox processing for specific tenants is initiated as part of the request that submits outbox messages.

Due to a temporary limitation that will be removed soon, if an application instance restarts, the processing strategy depends on future requests writing to a tenant's outbox table. If this is not acceptable for your application, you can schedule regular checks of all tenants' outbox tables at the cost of iterating over all tenants. To do this, set cds.outbox.persistent.scheduler.allTenantsTask.enabled: true.

With this new strategy, you can now specify the number of threads per outbox instance that should process messages in parallel within an application instance. Set cds.outbox.services.<key>.threads (default `2`) to the desired value. Note that this only works for outbox instances with out-of-order processing. For outbox instances with in-order processing, exactly one thread is used.

If you want to switch back to the old processing strategy, set cds.outbox.persistent.scheduler.enabled: false.

#### Locking ​

To ensure that an outbox message is processed only once, locking mechanisms are applied to the outbox table. Previously, this relied on database locks. If processing of an outbox message took a long time, database locks and connections were held for for a long time as well. You can now enable an optimized locking strategy that reduces database locks by introducing a status column.

This new locking strategy is opt-in by setting cds.outbox.persistent.statusLock.enabled: true and requires at least `@sap/cds` version `9`.

Update all app instances to CAP Java 4.5 or higher

Only enable the new locking strategy **after** all active application instances are **already** updated to CAP Java 4.5.0. This ensures proper in-order processing during the locking strategy switch.

#### Observability ​

CAP Java's outbox publishes metrics to OpenTelemetry. For multiple application instances, these metrics could have reported incorrect values. This behavior is now adapted to avoid reporting outdated metrics. You can visualize these metrics in a Cloud Logging dashboard.

Try the Dashboard

Import the dashboard into your Cloud Logging instance:

- Go to `Stack Management` -> `Saved Objects` -> `Import`
- Import cap-java-outbox-metrics.ndjson

- Choose `Check for existing objects` -> `Request action on conflict`
- Click on `Import` and choose `Skip` on every conflict
- Open the `CAP Java Outbox Metrics` dashboard

When submitting a message to the outbox, the W3C trace context is now stored together with the message. This ensures that asynchronously processed outbox messages are processed with the same W3C Trace ID as their originating request, providing an end-to-end view of a request's path.

### Support for CDS Data in Spring REST Controllers ​

You can now use CDS-defined objects in Spring REST controllers directly. CAP Java automatically parses the request payload and validates it against the CDS model:

java

```

@RestController
@RequestMapping("/rest")
public class BooksRestServiceController {

  @Autowired
  private AdminService srv;

  @GetMapping("/read/books")
  public List readBooks() {
    return srv.run(Select.from(BOOKS)).list();
  }

  @PatchMapping("/update/book")
  public Books updateBook(Books book) {
    return srv.run(Update.entity(BOOKS).data(book)).single();
  }

}
```

### CDS Map Enhancements ​

CAP Java now provides improved support for `cds.Map` elements. Given the following CDS entity with a map element `details`:

cds

```
entity Products : cuid {
  name     : String;
  category : String;
  details  : Map;
}
```

#### Search in Sub-Elements of Map Beta ​

You can now search for values of sub-elements within a [cds.Map](/docs/java/cds-data#cds-map) element by adding a path to the sub-element in the search scope:

Java

```
Select.from(PRODUCTS)
   .columns(p -> p.id(), p -> p.name())
   .search("blue", List.of("details.color"))
   .where(p -> p.category().eq("shirts"));
```

Expensive on large datasets

Searching by content of a map element can be expensive on large datasets. Use additional filters on non-map elements to reduce the dataset.

#### Static Builder Methods to Access Sub-Elements of Map ​

The static builder interface methods for cds.Map elements now allow you to access sub-elements of the map via `get`:

Java

```
Select.from(PRODUCTS).columns(p -> p.details().get("color"));
```

### Tree Views on SQLite ​

The OData requests of the UI5 tree table are now handled on all databases supported by CAP Java including SQLite.

[Learn more about Hierarchical Tree Views.](/docs/guides/uis/fiori#hierarchical-tree-views)

### Avoiding Transactions for Select ​

When reading media elements, a transaction is now always enforced to prevent any stream from being closed too early. You can now safely set cds.persistence.changeSet.enforceTransactional: false to avoid initiating transactions on `SELECT` queries. This can reduce contention within your application, as connections are returned to the connection pool faster.

[Learn more about avoiding transactions for select.](/docs/java/event-handlers/changeset-contexts#avoid-transactions)

### Protocol Annotations ​

CAP Java now supports protocol annotations like `@odata` as an alternative to the array-style `@protocols: [...]` syntax to determine how a service is exposed:

cds

```
@odata service CatalogService { ... }
```

[Learn more about configuring protocols.](/docs/java/cqn-services/application-services#configure-path-and-protocol)

## Plugins ​

### cap-js/attachments Enhancements ​

#### Important Fixes ​

- Fixed duplicate object store creation in multitenant scenarios with separate object stores per tenant when the tenant's subscription was updated via the SaaS Manager.
- Fixed a potential isolation issue where, in multitenant scenarios with separate object stores, simultaneous uploads from different tenants could break tenant isolation.
- Fixed an issue where the attachment handlers were not registered when the `attachments` composition was behind a feature toggle.

#### All Hyper-Scaler Object Stores Are Now Supported ​

In addition to the existing AWS S3 support for the [SAP BTP Object Store](https://discovery-center.cloud.sap/serviceCatalog/object-store) service, Google Cloud Storage and Azure Blob Storage are now supported as well.

package.jsonjson

```
"cds": {
  "requires": {
    "attachments": {
      "kind": "standard"
    }
  }
}
```

`kind: standard` automatically determines based on the bound object store which implementation to use.

Manually setting the hyper-scaler kindAWS S3 KindAzure Blob storage KindGCP Cloud Storage Kindjson

```
"cds": {
  "requires": {
    "attachments": {
      "kind": "s3"
    }
  }
}
```

json

```
"cds": {
  "requires": {
    "attachments": {
      "kind": "azure"
    }
  }
}
```

json

```
"cds": {
  "requires": {
    "attachments": {
      "kind": "gcp"
    }
  }
}
```

#### Malware Scanning Improvements ​

The included malware scanning feature now supports `mTLS` for the service binding to the [SAP Malware Scanning Service](https://discovery-center.cloud.sap/serviceCatalog/malware-scanning-service?service_plan=clamav&region=all&commercialModel=btpea).

Files larger than 400 MB can now be uploaded, but due to limitations of the Malware Scanning service, they remain in the status "Scanning failed".

Additionally, malware scanning now happens asynchronously and is more reliable, and the scan status now has a UI criticality.

#### Localization ​

The Attachments plugin now provides translations for all SAP-supported languages for its UI component and error messages.

#### Dynamically Hiding the UI Section ​

`@UI.Hidden` can now be used to hide the attachments section on the UI, with support for dynamic expressions.

cds

```
entity Incidents {
  // ...
  status : Integer enum {
    submitted =  1;
    fulfilled =  2;
    shipped   =  3;
    canceled  = -1;
  };
  @UI.Hidden : (status = #canceled ? true : false)
  attachments: Composition of many Attachments;
}
```

`@attachments.disable_facet` is now deprecated. Please switch over to `@UI.Hidden`.

## Tools ​

### Simplified Kyma Project Setup ​

Kyma project setup and deployment are now easier than ever:

- Simplified project setup: Start a Kyma project with a single command: `cds add kyma` as a shortcut for `cds add helm` and `cds add containerize`.
- Improved deployment experience: Kyma deployments via `cds up -2 k8s` use checksum-based buildpack artifact management for faster builds and fewer unnecessary rebuilds.
- Interactive registry credential prompts: The CLI detects missing registry credentials on your Kyma cluster and prompts you to provide them interactively, eliminating manual credential maintenance.
- Automated UI5 build: UI5/Fiori apps are built when you run `cds up -2 k8s`, streamlining the deployment workflow.
- No more hard dependency on `ctz`: You no longer need to install `ctz` locally to work with Kyma projects, reducing setup complexity.

`ctz` is discontinued

CAP does not further maintain the [`ctz`](https://github.com/SAP/ctz) package in favor of `cds up --to k8s`.

For more details, see the [updated documentation](/docs/guides/deploy/to-kyma).

### GitHub Actions for Java Projects ​

`cds add github-actions` is now available for Java projects. It adds a default set of workflows that build, test, and deploy Java applications.

[Learn more on GitHub Actions.](/docs/guides/deploy/cicd#github-actions)

### Command-Line Formatter Allows Piping ​

The CDS command-line formatter (`format-cds`), which is part of `@sap/cds-lsp`, now allows you to pass in sources from standard input. For example:

sh

```
cat myfile.cds | npx --package=@sap/cds-lsp format-cds - > myfile-formatted.cds
```

Or if you already installed `@sap/cds-lsp` globally:

sh

```
cat myfile.cds | format-cds - > myfile-formatted.cds
```

Formatting options will be picked up from `.cdsprettier.json` if present, searched from the current working directory up to the root directory or the user's home directory as a fallback. Additionally, you can pass formatting options as command-line arguments. For example:

sh

```
cat myfile.cds | format-cds --tabSize=2 - > myfile-formatted.cds
```

[Learn more about CDS formatter.](/docs/tools/cds-editors#cds-formatter)

## capire Updates ​

### Improved Localized Data Documentation ​

Enhanced documentation for working with localized data and internationalization, including updated CSV format examples using comma-separated values instead of semicolons.

[Learn more about Localized Data.](/docs/guides/uis/localized-data)

### Draft Protection Configuration Update ​

The configuration property for draft protection has been updated from `cds.security.draftProtection.enabled` to `cds.security.authorization.draftProtection.enabled` in CAP Java. Additionally, direct updates to active entities now respect the draft lock, preventing data loss when a draft is subsequently activated.

[Learn more about Draft Lock in Java.](/docs/java/fiori-drafts#draft-lock)

### OData Hierarchy Vocabulary Support ​

Added support for the `@Hierarchy` OData vocabulary, enabling hierarchical data structures in OData services. This vocabulary is now included in the list of supported SAP vocabularies for automatic translation.

[Learn more about OData Vocabularies](/docs/guides/protocols/odata#sap-vocabularies)

### Draft Aggregation Queries ​

Documentation now clarifies that aggregating over active and inactive draft entities isn't supported in CAP Java. Queries with aggregation functions implicitly add `IsActiveEntity` to the group-by clause, resulting in separate active and inactive rows instead of aggregated results.

[Learn more about Fiori Drafts in Java.](/docs/java/fiori-drafts#aggregation-queries)

### Misc ​

- Updated `cds bind` command to prefer `-a` flag instead of `--to-app-services`.
- Enhanced documentation for `UInt8` type support on H2 and PostgreSQL.
- Improved CI/CD documentation with better links after ad-hoc deployment.
- Fixed code fence languages and formatting in Temporal Data guide.
- Clarified that cds build is a separate step for `cds up -2 k8s`.
