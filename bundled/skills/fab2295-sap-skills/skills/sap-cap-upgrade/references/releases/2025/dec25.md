<!-- mirror: https://cap.cloud.sap/docs/releases/2025/dec25 -->
<!-- fetched: 2026-05-09T02:26:49.037Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# December 2025 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Status-Transition Flows Gamma ​

The Status Flows feature was rolled out as Beta [in November](./nov25#status-transition-flows) and is now promoted to Gamma level. This means it is finalized, ready to use, stable, and supported long term in the documented feature set.

cds

```
annotate TravelService.Travels with @flow.status: Status actions {
  acceptTravel    @from: [ #Open ] @to: #Accepted;
  rejectTravel    @from: [ #Open ] @to: #Rejected;
  deductDiscount  @from: [ #Open ]; // restricted to #Open travels
}
```

As part of this the documentation moved to [Cookbook > Status Flows](/docs/guides/services/status-flows), got overhauled and cleaned up of implementation details which are not considered public.

## Declarative Constraints Gamma ​

Use the new [`@assert`](/docs/guides/services/constraints#assert-constraint) annotation to express conditions using [CDS Expression Language (CXL)](/docs/cds/cxl). The system validates these conditions whenever you write data. For example, the following constraints are defined on the `TravelService.Travels` entity:

cds

```
using { TravelService } from './travel-service';
annotate TravelService.Travels with {

  Description @assert: (case
    when length(Description)  EndDate then 'ASSERT_BEGINDATE_BEFORE_ENDDATE'
    when exists Bookings [Flight.date

[Learn more about Declarative Constraints](/docs/guides/services/constraints)

## New @hierarchy Annotation ​

Annotations for hierarchical tree views have been greatly streamlined. Simply annotate a respective entity with the new `@hierarchy` annotation like this:

cds

```
annotate AdminService.Genres with @hierarchy;
```

Which replaces all of these elaborate OData annotations you had to add previously:

The rest stays as before, and as documented in [Serving Fiori UIs – Hierarchical Tree Views](/docs/guides/uis/fiori#hierarchical-tree-views). Find in the guide also additional details and usage options about the new `@hierarchy` annotation.

## New cds export Beta ​

Use `cds export` to create API client packages from CDS service definitions. For example, given a service definition like that:

srv/data-service.cdscds

```
service sap.capire.flights.data {
  @readonly entity Flights as projection on my.Flights;
  @readonly entity Airlines as projection on my.Airlines;
  @readonly entity Airports as projection on my.Airports;
}
```

[See the full source in @capire/xflights](https://github.com/capire/xflights/tree/main/srv/data-service.cds)

We can create an API client package using the following command:

sh

```
cds export srv/data-service.cds
```

The output is a full-featured CAP reuse package, which can be published to *npm* registries:

sh

```
npm publish ./apis/data-service
```

... and consumed by other CAP projects using standard `npm add` and `npm update`:

sh

```
npm add @capire/xflights-data
```

In addition `cds export` applies CAP plugin techniques to the generated package, so consumers benefit from plug & play, without any further configuration required.

Why use cds export?

Instead of exporting APIs to OData EDMX and `cds import`ing them to consuming apps, `cds export` creates ready-to-use API client packages, with **lossless** CDS API models.

[Learn more about cds export.](/docs/tools/cds-cli#cds-export)

## CDS Language & Compiler ​

### Loading from app/* subfolders ​

By default, `cds build` or `cds serve` now automatically fetch and load all `.cds` files not only from the `./app` folder itself but also from all `./app/*` subfolders in there. For example, if you have Fiori apps organized in subfolders like shown in the snapshot below, all the `.cds` files will be loaded automatically.

Thereby we eliminate the need to add an `./app/index.cds` with `using` directives for each file in subfolders like that:

cds

```
// Import all .cds files from common folder
using from './common/code-lists';
using from './common/common';
using from './common/labels';

// Import all .cds files from travels folder
using from './travels/capabilities';
using from './travels/field-control';
using from './travels/layouts';
```

You can disable this by setting cds.folders.apps: false. You can apply the same for other folders by e.g. cds.folders.srvs: srv/*.

### Enums in Annotation Expressions ​

Up to now, you could use enum symbols in annotation expressions only for enums defined in CDS. As value for an OData annotation, you had to provide the actual value and then explain the meaning of these funny numbers. Now, you can directly use the enum symbols:

cds

```
entity Travel {
  key TravelUUID : UUID;
  status : String(1) enum { Open = 'O'; Accepted = 'A'; Canceled = 'X'; };

  // 1 is ReadOnly, 7 is Mandatory
  @Common.FieldControl: (status = #Accepted ? 1 : 7)
  @Common.FieldControl: (status = #Accepted ? #ReadOnly : #Mandatory)
  bookingFee : Decimal(16,3) default 0;
}
```

[Learn more about Annotation Expressions.](/docs/cds/cdl#expressions-as-annotation-values)

## Node.js ​

### Direct CRUD on Draft-enabled Entities Beta ​

With cds.fiori.direct_crud:true, the Node.js runtime now allows direct CRUD requests to draft-enabled entities. For example, instead of having to follow the draft request sequence of `EDIT`, `PATCH`, and `SAVE`, you can send direct `UPDATE` requests to the so-called *active entity*.

[Learn more about draft-specific events.](/docs/node.js/fiori#draft-specific-events)

In such direct requests, the additional key `IsActiveEntity` defaults to `true`, which allows you to omit it:

http

```
POST {{server}}/odata/v4/travel/Travels
{ "ID": 4711 }
```

http

```
PUT {{server}}/odata/v4/travel/Travels(ID=4711)
{ "Description": "Fun times!" }
```

No code changes required

Note that with this feature, the `POST` request creates the active entity. Hence, even though the feature works seamlessly with existing implementations and also SAP Fiori elements adjusts on the fly, it may affect your tests.

[Learn more about direct CRUD on draft-enabled entities.](/docs/guides/uis/fiori#direct-crud)

### Improved Event Queue Processing ​

We consolidated event queue processing into a default queue and custom queues (if configured).

This change is transparent for projects except for minor content changes in the technical data structure (`cds.outbox.Messages`) that *may* show up in custom-built extensions for [managing the Dead Letter Queue](/docs/node.js/queue#managing-the-dead-letter-queue).

Further, we increased the db-related guarantee from *at least once* to *exactly once*. That is, the system only commits database changes from event processing if it successfully processes the event, and vice-versa.

[Learn more about Event Queues in Node.js](/docs/node.js/queue)

### Cleaned-up Model Reflection APIs ​

The following function usages are officially deprecated and will be removed in the next major version 10.

| Deprecated Usage | Official Usage |
| --- | --- |
| `srv.entities()` | [`srv.entities`/ `cds.entities()`](/docs/node.js/cds-reflect#cds-service) |
| `srv.types()` | [`srv.types`](/docs/node.js/cds-reflect#cds-service) |
| `srv.events()` | [`srv.events`](/docs/node.js/cds-reflect#cds-service) |
| `srv.actions()` | [`srv.actions`](/docs/node.js/cds-reflect#cds-service) |

Further from version 10 onwards, the `.texts` entities will not be included in the `srv.entities` variants anymore. Use the [`texts`](/docs/node.js/cds-reflect#texts) property of the respective entity instead.

| Deprecated Usage | Official Usage |
| --- | --- |
| `CatalogService['Books.texts']` | `CatalogService.Books.texts` |

You can enforce that behavior already today with cds.features.compat_texts_entities:false.

## Java ​

### Important Changes ❗️ ​

### Deep Updates for Draft ​

So far, for draft-enabled entities, [deep updates](/docs/java/working-with-cql/query-api#deep-update) were only supported for the *active* entities. Now, you may also execute deep updates on the *inactive* entities provided that the update statement includes the keys for entities to be updated. [Searched updates](/docs/java/working-with-cql/query-api#searched-update) will be rejected.

The following example shows the recommended way to do this:

java

```
DraftService draftService = ...
Orders entry = Orders.create();
entry.setId(123);
entry.setItems(...); // Some info about items

CqnUpdate deepUpdate =
  Update.entity(ORDERS, o -> o.filter(f -> f.IsActiveEntity().eq(false)))
        .entry(entry);
draftService.run(deepUpdate);
```

### Miscellaneous ​

#### API for Aliasing CqnValue ​

The `CqnValue` interface received a new `as(String alias)` method to create aliased values directly. This makes it easier to build queries with aliased values, such as predicate expressions on the select list:

java

```
CqnExpression xpr = cdsModel.getEntity(BOOKS.CDS_NAME).getAnnotationValue("@xpr", CQL.FALSE);

Select.from(BOOKS).columns(xpr.as("annotatedXpr"));
```

## Tools ​

### cds up Convenience for Kyma ​

If your project contains Helm deployment resources and no *mta.yaml* `cds up` will default to Kubernetes and you do not need to specify the `--to k8s` option anymore.

sh

```
cds up --to k8s
cds up
```

[Learn more about Kyma Deployment.](/docs/guides/deploy/to-kyma)

## Plugins ​

### @sap/cds-rfc ​

The Node.js plugin `@sap/cds-rfc` now supports multitenancy.

[Learn more about the ABAP RFC plugin.](/docs/plugins/index#abap-rfc)
