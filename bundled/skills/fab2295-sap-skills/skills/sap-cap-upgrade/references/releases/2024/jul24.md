<!-- mirror: https://cap.cloud.sap/docs/releases/2024/jul24 -->
<!-- fetched: 2026-05-09T02:26:43.420Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# July 2024 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## CDS Language & Compiler ​

### IsActiveEntity In Expression Annotations ​

If you have enabled draft for an entity, you can now use the generated element `IsActiveEntity` in expression-like annotation values by using the prefix `$draft`:

cds

```
@odata.draft.enabled
entity SomeEntity {
  key ID: UUID;
  @UI.Hidden: ( not $draft.IsActiveEntity )
  notVisibleInDraft: String;
  // ...
}
```

[Learn more about Expressions as Annotation Values.](/docs/cds/cdl#expressions-as-annotation-values)

## Node.js ​

### Request Body Limits ​

The global configuration cds.server.body_parser.limit restricts the accepted request body size for all endpoints of the server. If the payload exceeds the configured value, the request is rejected with *413 - Payload too large*.

jsonc

```
{
  "cds": {
    "server": {
      "body_parser": {
        "limit": "1mb" // also accepts b, kb, etc...
      }
    }
  }
}
```

The default limit is *100 kb*, as defined by the built-in [body parsers of the underlying express framework](https://expressjs.com/en/api.html#express.json).

In addition to the global configuration, there's a service-specific annotation `@cds.server.body_parser.limit` as the expected request body sizes might vary between different services within the application.

cds

```
annotate AdminService with @cds.server.body_parser.limit: '1mb';
```

[Learn more about configuring the Maximum Request Body Size.](/docs/node.js/cds-server#maximum-request-body-size)

## Java ​

### Avoiding Transactions for Select ​

By default, CAP Java automatically starts one transaction per ChangeSet Context when there is a first call. Started transactions consume a significant amount of system resources, such as a database connection from the connection pool. This can lead to a bottleneck in high-load situations. However, `READ` events actually don't require transactions in most cases and can be executed in JDBC auto commit mode instead. To further limit the transaction time, setting property cds.persistence.changeSet.enforceTransactional:false avoids initiating transactions for these Select queries in the ChangeSet Context. This significantly increases application throughput.

[Learn more about avoiding transactions for select.](/docs/java/event-handlers/changeset-contexts#avoid-transactions)

### Weighted Fuzzy Search on HANA ​

Use the [@Search.ranking](https://help.sap.com/doc/saphelp_nw75/7.5.5/en-US/38/baf2fc3a8e4ed887b29de738296fa9/content.htm) annotation to specify how relevant the value of an element is for the computation of the [fuzzy search](/docs/guides/services/served-ootb#fuzzy-search) score. The allowed values are `HIGH`, `MEDIUM` (default), and `LOW`:

cds

```
entity Books {
  key id            : UUID;

      @Search.ranking: HIGH
      title         : String;

      description   : String;

      @Search.ranking: LOW
      publisherName : String;
}
```

In this `Books` entity, the element `title` is most relevant, whereas `publisherName` contributes only little to the score of the search result.

## Tools ​

### Add Portal Configuration ​

A new command to set up [SAP Cloud Portal](https://discovery-center.cloud.sap/serviceCatalog/cloud-portal-service):

sh

```
cds add portal
```

### Add Work Zone Configuration Beta ​

Likewise, add configuration for [SAP BTP Work Zone, Standard Edition](https://discovery-center.cloud.sap/serviceCatalog/sap-build-work-zone-standard-edition):

sh

```
cds add workzone-standard
```
