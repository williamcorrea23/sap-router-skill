<!-- mirror: https://cap.cloud.sap/docs/releases/2025/jun25 -->
<!-- fetched: 2026-05-09T02:26:51.821Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# June 2025 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Node.js ​

### Hierarchy Maintenance in Tree Views Beta ​

CAP Node.js now also supports hierarchy maintenance for [draft enabled](/docs/guides/uis/fiori#draft-support) entities. It's possible to create new nodes and to add them as root or child nodes to the hierarchy. You can also modify and delete nodes. In addition, one can change a parent of a child node (move a node).

If a node is deleted, its descendant nodes are only deleted if they are in a composition relationship with the deleted node.

The same set of modifications is supported on the Object Page as well.

Supported on all databases

This feature is supported on SQLite, Postgres and SAP HANA.

[Try it out yourself in our SAP Fiori bookshop sample app.](https://github.com/SAP-samples/cloud-cap-samples)[CAP Java supports this beta feature since February 2025.](./feb25#hierarchy-maintenance-in-tree-table)

### UI5 State Messages for Drafts Beta ​

CAP Node.js now also supports persisting (error) messages for draft-enabled entities and providing *state messages* to the UI5 OData V4 model.

The same precondition as for CAP Java applies:

- Enable the feature flag cds.cdsc.beta.draftMessages:true
- Enable OData containment mode with cds.odata.containment: true

We are working on a solution that does not require containment.

If activated, you can observe the following improvements, without changing the application code:

- Error messages for annotation-based validations (`@assert...`) already appear while editing the draft.
- Errors stemming from custom validations for the `PATCH` event are persisted as well. The invalid value is still persisted, as expected by the draft choreography.
- Messages no longer unexpectedly vanish from the UI after editing another field.
- Messages are automatically loaded when reopening a previously edited draft.

Setting this property adds additional elements to your draft-enabled entities and `DraftAdministrativeData`, which are required to store and serve state messages.

Requires Schema Update

Enabling draft messages requires a database schema update, as it adds an additional element to `DraftAdministrativeData`.

[CAP Java supports this beta feature since February 2025.](./feb25#ui5-state-messages-for-drafts)

## Java ​

### Important Changes ❗️ ​

#### Add DevDependency to @sap/cds-mtxs ​

`@sap/cds-mtxs` is now a [CAP plugin](/docs/plugins/). In order to pull the build configuration correctly, you have to add `@sap/cds-mtxs` to the root-level *package.json* `devDependencies`:

sh

```
npm add -D @sap/cds-mtxs
```

### Tree Views w/ H2 Database Beta ​

To simplify local development and testing with the [SAP Fiori Tree Table](https://www.sap.com/design-system/fiori-design-web/ui-elements/tree-table/?external), you can now also use a local H2 database, instead of connecting to SAP HANA.

### Event Handler Enhancements ​

We have made several enhancements, that allow for cleaner and more intuitive custom event handler implementations.

The below examples refer to the following example model:

cds

```
service Universe {
  entity World {
    name: String;
  } actions {
    function hello() returns String;
  }
}
```

#### Returning Arbitrary Types ​

You can now return objects of arbitrary types in your event handlers and the runtime takes care of putting them into the EventContext as `result`. Also, the runtime sets the context to completed.

Instead of setting the string as a context `result`:

java

```
@On(event = WorldHelloContext.CDS_NAME)
public void hello(WorldHelloContext context) {
  context.setResult("Hello World");
}
```

You can now return the string directly:

java

```
@On(event = WorldHelloContext.CDS_NAME)
public String hello() {
  return "Hello World";
}
```

#### Accessing the Service ​

You can now get the Service that is processing the event directly provided to your event handler, by defining a corresponding argument in the method signature.

This avoids manual casts, especially when having to access the `DraftService` interface or generated typed service interfaces:

Instead of obtaining the service from the context and casting it to a more specific sub-type:

java

```
@On(event = WorldHelloContext.CDS_NAME)
public void hello(WorldHelloContext context) {
  Universe service = (Universe) context.getService();
  service.run(...);
}
```

You can now define the specific service directly as an argument:

java

```
@On(event = WorldHelloContext.CDS_NAME)
public void hello(Universe service) {
  service.run(...);
}
```

#### Typed Entity References ​

You can now directly get a typed entity reference reflecting the reference of the currently processed CQN statement, by declaring a corresponding argument in your method signature.

You can directly use this reference to build type-safe queries:

java

```
@On(event = WorldHelloContext.CDS_NAME)
public void hello(World_ ref) {
  Select.from(ref).columns(w -> w.name());
}
```

CAP Java infers the entity for the event handler registration from the argument, so that it doesn't need to be explicitly defined in the annotation again.

#### Bringing It All Together ​

These features nicely play together like this:

java

```
@On(event = WorldHelloContext.CDS_NAME)
public String hello(Universe service, World_ ref) {
  Result result = service.run(Select.from(ref).columns(w -> w.name()));
  return "Hello " + result.single(World.class).getName();
}
```

### Media Data in Actions and Functions ​

Media data like images, CSVs, and so on, can now also be used as a return type of actions and functions. The return type annotated with `@Core.MediaType` has to be defined within the same service of the action or function.

**Example:**

cdscds

```
service OrderService {
  @(Core: {
     MediaType: 'application/pdf',
     ContentDisposition.Filename: 'order.pdf'
  })
  type pdf: LargeBinary;
  entity Orders { ... } actions {
    function exportAsPdf() returns pdf;
  }
}
```

javajava

```
@On (event = OrdersExportAsPdfContext.CDS_NAME)
public InputStream exportAsPdf(CqnElementRef order) {
    byte[] pdf = createPdf(order);
    return new ByteArrayInputStream(pdf);
}
```

[CAP Node.js supports this feature since February 2025.](./feb25#media-data-in-actions-and-functions)

### Media Elements in Remote OData ​

You can now read and write [media elements](/docs/guides/services/media-data#annotating-media-elements) annotated with `@Core.MediaType` from remote services with CQN statements.

If you want to read `image` of this entity, you need to create a statement like this:

java

```
Select.from(Media_.class, m -> m.filter(f -> f.ID().eq("..."))).columns(Media_::image);
```

You can also write the same property with an `Update` statement:

java

```
Media payload = Media.create();
payload.setId(...);
payload.setImage(...);

Update.entity(Media_.class).entry(payload);
```

[Learn more in Consuming Media Elements.](/docs/java/cqn-services/remote-services#consuming-media-elements)

## Tools ​

### IntelliJ Community Edition Supported by CDS Plugin ​

Triggered by your feedback, the [CDS plugin for the IntelliJ IDEs](https://github.com/cap-js/cds-intellij), version 2, now also runs on the *Community editions*, lifting the need for a commercial variant.

It will soon be availabe as an update on the [JetBreains Marketplace](https://plugins.jetbrains.com/plugin/25209-sap-cds-language-support).

[Join the discussions about the plugin on GitHub.](https://github.com/cap-js/cds-intellij)

### Faster Editor Feedback in VS Code ​

We have improved the responsiveness and CPU usage of the CDS editor, especially for larger models.

- During typing it will defer error indicators and other diagnostics until typing finished.
- Performance while typing has been improved by aborting compilations that are not needed anymore.

This behavior can be configured:

There is a new setting `cds.workspace.fastDiagnosticsMode` (default: `Clear`). With the option `Parse`, an immediate error feedback is provided that relies solely on the CDS grammar, which is less accurate but faster. The old behavior of updating diagnostics after (each intermediate) compilation is finished is still available with the option `Off`.
