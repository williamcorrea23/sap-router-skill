<!-- mirror: https://cap.cloud.sap/docs/releases/2021/feb21 -->
<!-- fetched: 2026-05-09T02:26:26.163Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# February 2021 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtx?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Docs and Samples ​

### Real-Time Search Improvements ​

The search ranking algorithm has been improved to show more accurate results. Additionally, capire can now be searched in real-time.

Full-text search results are automatically highlighted and the scroll position is adjusted to display the first result.

### Guided Tours in cap/samples ​

Take a guided tour in VS Code through our [CAP samples](https://github.com/SAP-samples/cloud-cap-samples) and learn which CAP features are showcased by the different parts of the repository. Just install the [CodeTour](https://marketplace.visualstudio.com/items?itemName=vsls-contrib.codetour) extension for VS Code.

We'll add more code tours in the future. Stay tuned!

### Using SQLite and SAP HANA Functions ​

CAP samples demonstrate how you can use [native database functions of SQLite and SAP HANA](https://github.com/SAP-samples/cloud-cap-samples/commit/65c8c82f745e0097fab6ca8164a2ede8400da803) in one code base. There is also a [code tour](https://github.com/SAP-samples/cloud-cap-samples#code-tours) available for it.

## CDS Language & Compiler ​

### Resolving Ambiguities for Auto-Redirection of Associations ​

If there are several equally suited potential targets for the auto-redirection of an association, you can now resolve the ambiguity with the annotation `@cds.redirection.target`. Use the value `true` to make an entity a preferred redirection target, or `false` to exclude an entity as target for auto-redirection. See section [Auto-Redirected Associations](/docs/guides/services/providing-services#redirected-associations) for a detailed example.

## Node.js Runtime ​

### Important Changes ❗️ ​

The following changes can affect your project. See the respective sections for details and potentially necessary actions.

- The default implementation of a messaging service with kind `enterprise-messaging` is now multitenant aware. The old, shared variant is available through kind `enterprise-messaging-shared`.
- `.after` handlers are consistently called with a result with a type based on the respective request.
- Managed properties of a containing entity are updated if any composition target is updated.

### Authorization Enhancements ​

If not explicitly contained in the service definition, composite entities that are auto-exposed by the CDS Compiler can't be accessed directly, and associated entities that are auto-exposed by means of `@cds.autoexpose` are read-only. Additionally, implicitly autoexposed entities inherit the authorization restrictions of their containing entity when accessed via navigation.

Instance-based `@restrict.where` clauses are ignored during `CREATE` requests. Previously, the respective requests were rejected as there are no `WHERE` clauses in `INSERT` statements. This change allows to specify instance-based restrictions with grant type `WRITE` (cf. [Control Access with @restrict](/docs/guides/security/authorization#restrict-annotation)). It can be deactivated during a two-month grace period through compatible feature flag `cds.env.features.skip_restrict_where = false`.

Finally, trying to modify an entity without the necessary authorization results in an error response with HTTP status code `403` (instead of previously `404`).

### Data in .after Handlers ​

[`.after` Handlers](/docs/node.js/core-services#srv-after-request) are consistently called with a result with a type based on the respective request, for example an array for a collection and an object for a single entity. Previously, after handler for read requests were always called with an arrayed result. This change can be deactivated during a two-month grace period through compatible feature flag `cds.env.features.arrayed_after = true`.

### Managed Properties in Composition Trees ​

Managed properties of a containing entity are updated if any composition target is updated. For example, on a deep update to `OrderHeaders` with payload `{ items: [...] }`, `OrderHeaders.modifiedAt` will be updated if `items` contains changes. This change can be deactivated during a two-month grace period through compatible feature flag `cds.env.features.update_header_item = false`.

### Error Response Targets ​

The target of error responses now adheres to the OData path syntax. This allows, for example, the UI to correctly highlight the respective input and display the i18n name of the respective property even in case of name clashes.

Example:

cds

```
POST /Headers
{
  ID: 1,
  items: [{
    ID: 1,
    description: null, //> a mandatory property
  }]
}

Error Response:
{
  code: '400',
  message: 'Value is required',
  target: 'items(ID=1)/description' //> fully qualified path
}
```

### OData Metadata ​

OData responses now contain ETags for nested entities, that is, on READs with $expand and on deep CREATEs/ UPDATEs. Only the ETag of the header item is compared to the `If-(None-)Match` header.

Further, the Node.js runtime now supports responding with absolute context URLs. See section [Absolute Context URL](/docs/guides/protocols/odata#absolute-context-url) for more details.

## Java SDK ​

### Important Changes ❗️ ​

#### Changed ​

- The Maven build now enforces a minimum `@sap/cds-dk` version of 3.0.0.
- In case property `cds.security.openUnrestrictedEndpoints` is not configured explicitly, the Spring security configuration in the runtime authenticates all endpoints in multitenant scenario. In single tenant mode, the endpoints are still authenticated according to the restrictions in the CDS model.
- Elements with type UUID aren't searched by default any longer.
- Entities that have associations annotated with cascade, don't cascade insert, update, and delete operations anymore when they're in draft mode.

#### Fixed ​

- Service entity `DraftAdministrativeData` is now read-only and can't be accessed directly any more. Read requests using navigation to this entity (for example, /<Service>/<Entity>(id)/DraftAdministrativeData) are allowed for authorized users.
- The signature of the error messages 400002, 400012, 400015, 400018, 400019, 409006 and 428002 was changed to not expose request data in error messages.

### OData V2 Endpoints on Index Page ​

The index page of CAP Java application now displays links to OData V2 endpoints as well.

### OData V4 Protocol Adapter Enhancements ​

OData V4 `$expand` now supports using **inner** `$top` and `$skip` query options. Restriction: The result for `$count` is not considered, yet, when using these options in combination.

[Learn more about OData features supported in CAP.](/docs/guides/protocols/odata#overview)

### Remote Services Beta ​

You can now configure Remote Services, which are CQN-based clients to remote OData V2/V4 APIs.

[Learn more about Remote Services.](/docs/java/cqn-services/remote-services)

### Performance Improvements ​

- The performance of cascading delete operations has been improved on acyclic delete graphs.
- The performance of upserts has been improved by using batch delete.

### CDS.ql ​

- CDS.ql update and delete statements support now path expressions in the entity resp. from clause.
- `CQL.matching` allows to build a query-by-example style predicate, which can be used in infix filters and where clauses.

### Remove Values From Data Maps ​

You can now also use the `CDSDataProcessor` [converters](/docs/java/cds-data#cds-data-processor) to remove values from data maps.
