<!-- mirror: https://cap.cloud.sap/docs/releases/2020/aug20 -->
<!-- fetched: 2026-05-09T02:26:20.769Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# August 2020 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtx?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## New and Revised Guides ​

- Java > Multitenancy

## CDS Editors & Tools ​

The following features are available for all editors based on our language server implementation for CDS in SAP Business Application Studio, Visual Studio Code, and Eclipse. The plugins are available for download for Visual Studio Code at [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=SAPSE.vscode-cds#overview) and for Eclipse at [https://tools.hana.ondemand.com](https://tools.hana.ondemand.com/#cloud-vscodecds).

### Preview Commands (currently not in Eclipse) ​

The VS Code extension for the core data services (CDS) language now features a set of commands to generate a quick preview for a given `cds` file. By using this preview, you can get a quick glance at the code the `cds compiler` will generate.

### Code Completion Proposes Global Identifiers ​

The editor includes proposals of identifiers found in the workspace that aren't yet imported in the current file.

Enable global proposals:

## CDS Language & Compiler ​

### Join Cardinality ​

CQL now allows to specify a join cardinality. Allowed are any combinations of `{ [ EXACT ] ONE | MANY } TO { [ EXACT ] ONE | MANY }` for `{ INNER | { LEFT | RIGHT | FULL } [ OUTER ] }` joins. The cardinality is added in for SAP HANA generated CREATE VIEW statements.

### Unique Constraints ​

Support the creation of unique constraints by assigning `@assert.unique.` to non-query entities or query entities annotated with `@cds.persistence.table`. The value of the annotation is an array of paths referring to elements in the entity. The path leaf may be an element of a scalar, structured or managed association type. Individual foreign keys or unmanaged associations can't be accessed. In case the path points to a structured element, the unique constraint will contain all columns stemming from the structured type. In case the path points to a managed association, the unique constraint will contain all foreign key columns stemming from this managed association.

### Extended Projection Support ​

Projections columns can now use expressions like select items, both for `entity … as projection on` and `extend projection … with`.

### OData V4: array of <structured> ​

`array of ` or `many ` is now allowed in OData V4, flat format.

### Foreign Key Access and Association to Join Translation ​

The association to join transformation treats foreign key accesses with priority. If a foreign key of a managed association can be accessed without joins, no joins are generated. The priority handling can be turned of with option `joinfk`.

Before:

sql

```
CREATE VIEW V AS SELECT
  managedAssociation_1.foreignKey
FROM (Source AS Source_0 LEFT JOIN Source AS managedAssociation_1 ON (Source_0.managedAssociation_foreignKey = managedAssociation_1.foreignKey));
```

After:

sql

```
CREATE VIEW V AS SELECT
  Source_0.managedAssociation_foreignKey AS foreignKey
FROM Source AS Source_0;
```

### Extended Event Support ​

An event payload type can now be defined with a type/entity reference or a projection (instead of providing the elements directly). Furthermore, aspects can now be included when specifying the elements of an event payload type, as it's known for type, entity and aspect definitions. The directly provided elements of an event payload are now represented as `elements` in the CSN.

## Node.js Runtime ​

### Setting Headers for Remote Services ​

Headers can be set with `tx.emit` on remote HTTP services:

js

```
const tx = service.transaction()
const resultUsingHeaders = await tx.emit({
    query: SELECT.from('Entity'),
    headers: { header1: 'content'}
})
```

See [Node.js > Core Service API](/docs/node.js/core-services#srv-emit-event) for more details.

### Support for Privileged Users ​

With `cds.User.Privileged`, it's possible to bypass authorization checks while [consuming a local service](/docs/node.js/core-services). See [Node.js > Authentication](/docs/node.js/authentication#privileged-user) for more details.

### Miscellaneous ​

- Support for `@sap/xssec^3`
- Support for `expand` with `*` in Query Language API

## Java Runtime ​

### Important Changes ❗️ ​

#### UPSERT event isn't used anymore! ​

Previously, OData V4 `PUT` requests triggered an `UPSERT` event on the corresponding CAP services. By default, the `UPSERT` event implements a `CqnUpsert` statement, which first triggers a cascading delete followed by a deep insert. This doesn't exactly match the semantics of a `PUT`.

Now, the OData V4 `PUT` follows the same pattern as `PATCH`, by:

- First triggering an `UPDATE` event
- Following a `CREATE` event if the entity didn't yet exist.

As the `UPDATE` event in CAP supports updating sparse data, the `PUT` operation also ensures to fill up unspecified values with `null` or their default values, as long as they can't be determined through a foreign key relation. In addition, a `PUT` request no longer affects the full composition tree of an entity, but only those parts of the entity that the `PUT` was sent to and those that are specified in the entity data.

**Action required:** If your application has been using `PUT` requests and therefore registering event handlers for `UPSERT`, you need to register event handlers for `CREATE` and `UPDATE` events instead! Note however, that an `UPSERT` event can still be triggered through the [local service consumption API](/docs/java/services).

#### System User ​

- The name of the XSUAA system user (JWT with client credential flow) is now set to `system`.

### SAP Fiori Drafts ​

You can now use OData V4 `PATCH` and `PUT` requests to update and create active entities by specifying the key property `IsActiveEntity=true` in your OData URI. This skips the need to create an inactive draft entity first, which is useful when updating or creating an entity through technical APIs instead of SAP Fiori UIs. See [Java > Bypassing Fiori Draft Flow](/docs/java/fiori-drafts#bypassing-draft-flow) for more details.

### SaaS Multitenancy ​

It's now possible to develop multitenant CAP Java applications with MTX Sidecar and Service Manager, see [Java > Multitenancy](/docs/java/multitenancy).

### OData V4 ​

The OData V4 protocol adapter now additionally supports applying a [compute](https://docs.oasis-open.org/odata/odata-data-aggregation-ext/v4.0/cs02/odata-data-aggregation-ext-v4.0-cs02.html#_Toc435016588) transformation on the result of the *groupby* or *aggregate* transformations of $apply. Note: navigation properties aren't supported when using compute.

### Privileged User ​

A new option `privilegedUser()` can be leveraged when [defining](/docs/java/event-handlers/request-contexts#defining-requestcontext) your own `RequestContext`. Adding this introduces a user, which passes all authorization restrictions. This is useful for scenarios, where a restricted service should be called through the [local service consumption API](/docs/java/services) either in a request thread regardless of the original user's authorizations or in a background thread.

### Remote OData V2 / V4 Service Consumption (alpha) ​

CAP's [service consumption APIs](/docs/java/services) are based on the protocol-agnostic CQN query language. So far, The CAP Java runtime only supported to run CQN queries against SQL databases out-of-the-box. By adding the newly introduced Maven dependency `cds-feature-remote-odata` to your CAP Java project, you can now enable CQN queries against remote OData V2 and V4 services. SAP Cloud SDK is used to execute the OData requests, which are compiled from the CQN query definition. In the current state only `CqnSelect` queries (`GET` requests) are supported.

You can enable a CDS service from your model as a local representation of a remote OData service, by simply adding a destination configuration to it:

yaml

```
cds:
  services:
  - name: API_BUSINESS_PARTNER # name of the service in the CDS model
    destination:
      name: "s4-business-partner-api" # the destination, retrieved from SAP Cloud SDKs DestinationAccessor
      suffix: "/sap/opu/odata/sap" # an optional suffix appended to the destination's URL
      type: "odata-v2" # or odata-v4
```

You can learn more about destinations in the [SAP Cloud SDK documentation](https://sap.github.io/cloud-sdk/docs/java/features/connectivity/sdk-connectivity-destination-service).

Afterwards, you can interact with the service like with any other database-backend service. See [Service Consumption API](/docs/java/services) documentation for more details.

### Reflection API ​

- Support parsing the query definition of views with joins

### CDS Data Store ​

- Support select from subquery. Note: expand isn't supported in subqueries

### Bug Fixes ​

- The `cds-maven-plugin` doesn't use npm/npx from local installation cache anymore, if goal `install-node` is skipped or not configured. In this case, a globally installed npm/npx is required and used.
- Fixed a bug that caused a `NullPointerException` when calling an action or function, which returned a contained entity. With this fix, the OData V4 context URL for actions or functions returning an entity is now built based on entity types instead of entity sets.
- Fixed a bug that caused the `cds-maven-plugin` to determine a null working directory, in case the Maven project used an "external" parent project, not part of it's own source tree.
- Fixed a bug that caused an incorrect encoding of non-ASCII characters in `sap-messages` header
- Generate builder interfaces for services containing only actions/functions
- Fixed typed data access for arrayed types
