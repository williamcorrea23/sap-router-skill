<!-- mirror: https://cap.cloud.sap/docs/releases/2024/feb24 -->
<!-- fetched: 2026-05-09T02:26:42.197Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# February 2024 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Support and Feature Requests for CAP Plugins ​

For Node.js plugins, to open issues and also add contributions, use the open source repositories. This is the place where all relevant content comes together.

For Java plugins we're using the SAP Community for all kinds of issues and requests.

[Learn more about support for Plugins](/docs/plugins/index#support-for-plugins)

## Timezone Definition and Data ​

There is now a [common CDS definition for time zones](/docs/cds/common#entity-timezones), useful as a code list:

cds

```
entity sap.common.Timezones : CodeList {
  key code : String; //> for example, Europe/Berlin
}
```

Package [`@sap/cds-common-content` 1.4.0](https://www.npmjs.com/package/@sap/cds-common-content) provides a list of commonly used time zones. Translations aren't covered yet, but are planned.

## Audit Logging Plugin (GA) ​

The open source CDS plugin [@cap-js/audit-logging](https://www.npmjs.com/package/@cap-js/audit-logging) is generally available. Simply add the package to your application's dependencies and get automatic audit logging, for personal data in a plug and play fashion:

sh

```
npm add @cap-js/audit-logging
```

[Learn more about setting up and using audit logging in the Data Privacy guide.](/docs/guides/security/data-privacy)

## Java ​

### Optimistic Locking API ​

So far, CAP Java supported optimistic locking only via the OData protocol. This release now introduces an API to use optimistic locking programmatically from custom code.

#### ETag Predicate ​

The new ETag predicate allows to specify expected ETag values for conflict detection in update or delete statements. Use the `CQL.eTag()` and `StructuredType.eTag()` methods to create an ETag predicate:

java

```
Instant expectedLastModification = ...;
Update.entity(ORDER)
      .entry(newData)
      .where(o -> o.id().eq(85).and(o.eTag(expectedLastModification)));
```

#### Runtime Managed Versions Beta ​

Use the new `@cds.java.version` annotation to advise the runtime to manage a *version* value that is used for optimistic conflict detection:

cds

```
entity Order : cuid {
  @odata.etag
  @cds.java.version
  version : Int32;
  product : Association to Product;
}
```

If a version element is additionally annotated with `@odata.etag` it's also used as [ETag by OData](/docs/guides/services/served-ootb#etag).

A version element can have the `Timestamp` and `UUID`, or any integral type like `Uint8`, ... `Int64`.

If the update data contains a value for a version element this value is used as the *expected* value for the version. This enables the very convenient use of version elements in the program flow:

java

```
PersistenceService db = ...
CqnSelect select = Select.from(ORDER).byId(85);
Order order = db.run(select).single(Order.class);
order.setAmount(5000);
CqnUpdate update = Update.entity(ORDER).entry(order);
Result rs = db.execute(update);
if (rs.rowCount() == 0) {
  // order 85 does not exist or was modified concurrently
}
```

[Learn more about Optimistic Concurrency Control in CAP Java.](/docs/java/working-with-cql/query-execution#optimistic)

### Change Tracking Beta ​

CAP Java now provides out-of-the box support for automatic tracking of of changes in the business domain. The Node.js equivalent is offered as [@cap-js/change-tracking](https://github.com/cap-js/change-tracking) plugin.

To enhance your application with change tracking, add `cds-feature-change-tracking` as runtime dependency in the `pom.xml` of the service:

xml

```

 com.sap.cds
 cds-feature-change-tracking
 runtime

```

In the CDS model, you can specify which parts of the model should be subject to change tracking:

- The domain level entity needs to be extended with the `changeTracked` aspect to provide basic support.
- On service level, the annotation `@changelog` defines a human-readable identifier for an entity.
- On field level of a service entity, elements subject to change tracking are annotated with `@changelog`.

In the UI, the change history view can be added as a facet.

The following example shows how to track changes of `Orders.total` (human readable identifier containing`orderNo` and `buyer`):

cds

```
using {sap.changelog as changelog} from 'com.sap.cds/change-tracking';

// domain entity level (basic support):
extend my.Orders with changelog.changeTracked;

// service entity level (identifier):
annotate AdminService.Orders with @changelog: [
  orderNo,
  buyer
];

// service entity field level (tracked values):
annotate AdminService.Orders {
  total @changelog;
};
```

Configure the UI to present a change history view:

cds

```
// UI level:
annotate AdminService.Orders with @(
  UI : { ...
    Facets : [ ...
       {
          $Type               : 'UI.ReferenceFacet',
          ID                  : 'ChangeHistoryFacet',
          Label               : '{i18n>ChangeHistory}',
          Target              : 'changes/@UI.PresentationVariant',
          ![@UI.PartOfPreview]: false
        } ...
   ] ...
  } ...);
```

Resulting change history view:

[Learn more about change tracking](/docs/java/change-tracking)

### Generic Outbox ​

CAP Java now allows to configure custom instances of type [OutboxService](https://www.javadoc.io/doc/com.sap.cds/cds-services-api/latest/com/sap/cds/services/outbox/OutboxService.html):

yaml

```
cds:
  outbox:
    services:
      MyCustomOutbox:
        maxAttempts: 10
        storeLastError: true
```

They can be used to emit an event of an *arbitrary* service `MyService`:

java

```
@Autowired
@Qualifier("MyService")
MyService myService;

@Autowired
@Qualifier("MyCustomOutbox")
OutboxService myCustomOutbox;

Service myServiceOutboxed = myCustomOutbox.outboxed(myService);
myServiceOutboxed.send(...);
```

The messages stored in `MyCustomOutbox` are processed independently from messages in other outbox instances.

[Learn more about Custom Outbox Instances for Generic Service Usage.](/docs/java/outbox#persistent)

## Tools ​

### New Snippet for annotate Statements ​

The new `elements…` snippet for `annotate` statements inserts all possible elements of the annotated artifact.

For example, if you want to annotate an entity, the snippet inserts all elements of the entity:

You can now add annotations to the elements as required and remove the ones you don't need:

cds

```
annotate Publisher with {
  name    @title;
  address @assert.unique;
}
```

### cds add html5-repo for Cloud Foundry (Beta) ​

We support a Beta version for a new command in the `cds add` toolchain:

sh

```
cds add html5-repo
```

This sets up the [HTML5 Application Repository](https://help.sap.com/docs/btp/sap-business-technology-platform/html5-application-repository) service. Under the hood, this command also runs `cds add destination` to fulfil all prerequisites.

See what this adds to your project...
- In `cds.requires`, entries for `destinations` and `html5-repo` are set to `true`:js

```
"cds": {
 "requires": {
   "destinations": true,
   "html5-repo": true
 }
}
```
- In your `mta.yaml`......the required services are created:yaml

```
resources:
- name: bookshop-destination
  type: org.cloudfoundry.managed-service
  parameters:
    service: destination
    service-plan: lite
    config:
      HTML5Runtime_enabled: true
      init_data:
        instance:
          existing_destinations_policy: update
          destinations:
            - Name: bookshop-srv
              URL: ~{srv-api/srv-url}
              Authentication: NoAuthentication
              Type: HTTP
              ProxyType: Internet
              HTML5.ForwardAuthToken: true
              HTML5.DynamicDestination: true
  requires:
    - name: srv-api
      group: destinations
      properties:
        name: srv-api # must be used in xs-app.json as well
        url: ~{srv-url}
        forwardAuthToken: true
- name: bookshop-html5-repo-host
  type: org.cloudfoundry.managed-service
  parameters:
    service: html5-apps-repo
    service-plan: app-host
- name: bookshop-html5-runtime
  type: org.cloudfoundry.managed-service
  parameters:
    service: html5-apps-repo
    service-plan: app-runtime
```

...a module is created for hosting the application content:yaml

```
- name: bookshop-app-content
  type: com.sap.application.content
  path: app/
  requires:
    - name: bookshop-destination
    - name: bookshop-html5-repo-host
      parameters:
        content-target: true
  build-parameters:
    build-result: resources
    requires:
      - name: bookshop-app-admin-books
        artifacts:
          - admin-books.zip
        target-path: resources/
      - ...
```

...modules are created for each `html5` application:yaml

```
  - name: bookshop-app-admin-books
    type: html5
    path: app/admin-books
    build-parameters:
      build-result: dist
      builder: custom
      commands:
        - npm ci
        - npm run build

  - name: bookshop-app-browse
    type: html5
    path: app/browse
    build-parameters:
      build-result: dist
      builder: custom
      commands:
        - npm ci
        - npm run build
- ...
```
- If the App Router was set up via `cds add approuter`, we create an `xs-app.json` in each submodule.json

```
{
  "welcomeFile": "/index.html",
  "authenticationMethod": "route",
  "routes": [{
    "source": "^/{{app}}/(.*)$",
    "target": "/{{app}}/$1",
    "destination": "srv-api",
    "authenticationType": "xsuaa",
    "csrfProtection": false
  }, {
    "source": "^(.*)$",
    "target": "$1",
    "service": "html5-apps-repo-rt",
    "authenticationType": "xsuaa"
  }]
}
```

### Convenience Options for cds bind ​

`cds bind -2 ` brings additional convenience in Cloud Foundry. If there isn't a service key, such a **service key is automatically created** with the name `-key`. Custom settings are still possible by creating the service key manually beforehand with the `-c` option.

In addition, `cds bind` comes with a new `--to-app-services` option that **binds to all services of a given CF application**.

Taken together, this reduces the flow to create, build, deploy, and bind a multitenant application with multiple platform services like this:

sh

```
cds init bookshop --add tiny-sample && cd bookshop
cds add xsuaa,hana,mtx,mta --for production
npm install
mbt build -t gen/mta.tar
cf deploy gen/mta.tar
cds bind --to-app-services bookshop-srv
cf create-service-key bookshop-auth bookshop-auth-key
cds bind -2 bookshop-auth
cf create-service-key bookshop-db bookshop-db-key
cds bind -2 bookshop-db
cf create-service-key bookshop-registry bookshop-registry-key
cds bind -2 bookshop-registry
```

1
2
3
4
5
6
7
8
9
10
11
12

### Upgrade all tenants via the cds-mtx CLI ​

In addition to upgrading individual tenants, `cds-mtx upgrade *` now allows batch upgrading of all tenants.

[Learn more about tools and CLI support.](/docs/get-started/feature-matrix#cli-tools-support)

### Configuration Schema Contributions by CAP Plugins Beta ​

Starting with `@sap/cds` and `@sap/cds-dk` version `7.6.0`, CAP plugins can now contribute a schema for their configuration. This allows VS Code to offer code completion in files like `package.json` or `.cdsrc.json`.

As an example, plugin [`cds-swagger-ui-express`](https://github.com/chgeo/cds-swagger-ui-express/blob/6b96e0f3fb105deab1a5613c81912604cc872424/package.json#L60-L93) contributes such a schema, so that you get assisted when adding configuration:

[Learn more about schema contributions here.](/docs/node.js/cds-plugins#configuration-schema)

### Implementing Your own Build Plugins Beta ​

CDS build now allows the implementation of custom build plugins.
