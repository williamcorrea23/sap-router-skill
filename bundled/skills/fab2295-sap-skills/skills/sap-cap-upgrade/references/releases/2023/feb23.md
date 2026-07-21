<!-- mirror: https://cap.cloud.sap/docs/releases/2023/feb23 -->
<!-- fetched: 2026-05-09T02:26:36.501Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# February 2023 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

Tip

We're focussing already on our [upcoming major release](./../schedule#yearly-major-releases) and therefore have fewer announcements than usual for you. Nevertheless we hope you enjoy the additions and fixes to our framework.

## CDS Language & Compiler ​

### Method-Style Syntax for Spatial Functions ​

CDS now supports the instance method call syntax and instantiation syntax for geospatial functions.

cds

```
entity Geo as select from Foo {
  geoColumn.ST_Area() as area : Decimal,
  new ST_Point(2.25, 3.41).ST_X() as x : Decimal
};
```

## Java ​

### Streamlined Deployment Service ​

The former [MtSubscriptionService](https://www.javadoc.io/doc/com.sap.cds/cds-feature-mt/latest/com/sap/cds/services/mt/MtSubscriptionService.html) has been deprecated in favour of the new [DeploymentService](https://www.javadoc.io/doc/com.sap.cds/cds-services-api/latest/com/sap/cds/services/mt/DeploymentService.html). It covers all tenant lifecycle events such as subscriptions or upgrades in a lean way:

| Event Name | Event Context | Use Case |
| --- | --- | --- |
| `DEPENDENCIES` | [DependenciesEventContext](https://www.javadoc.io/doc/com.sap.cds/cds-services-api/latest/com/sap/cds/services/mt/DependenciesEventContext.html) | MT Dependencies |
| `SUBSCRIBE` | [SubscribeEventContext](https://www.javadoc.io/doc/com.sap.cds/cds-services-api/latest/com/sap/cds/services/mt/SubscribeEventContext.html) | Add a tenant |
| `UNSUBSCRIBE` | [UnsubscribeEventContext](https://www.javadoc.io/doc/com.sap.cds/cds-services-api/latest/com/sap/cds/services/mt/UnsubscribeEventContext.html) | Remove a tenant |
| `UPGRADE` | [UpgradeEventContext](https://www.javadoc.io/doc/com.sap.cds/cds-services-api/latest/com/sap/cds/services/mt/UpgradeEventContext.html) | Upgrade tenant(s) |

By default, tenant-specific resources such as database containers are deleted during removal. Migration to the [new API](/docs/java/multitenancy#custom-logic) is recommended.

Tip

Event handlers on the `MtSubscriptionService` API are continued to be triggered in a compatibility mode `cds.multitenancy.compatibility.enabled` (activated by default).

### Miscellaneous ​

- The Maven archetype now has a new property `jdkVersion`, which can be used to determine the JDK version of the generated CAP Java project. Supported values are `11` and `17` (default).
- The built-in CDS actuator now contains a new section `dbpools` that shows database pool statistics (requires `registerMbeans: true` in Hikari pool configuration).
- The new OData V4 serializer now supports a mode in which it buffers the response before streaming it to the client. This can be enabled in case serialization errors after streaming to the client has already started must be avoided. To enable it set `cds.odataV4.serializer.buffered` to `true`.

## Tools ​

### CAP Notebooks From The Docs ​

[CAP Notebooks](/docs/tools/cds-editors#cap-vscode-notebook) are now available directly through our documentation.

A new *notebook button* on the right-hand-side of the screen directly opens a CAP Notebook in a new [workspace](https://code.visualstudio.com/docs/editor/workspaces) in the user's local [VS Code application](https://code.visualstudio.com/docs).

For this feature, the [SAP CDS Language Support](https://marketplace.visualstudio.com/items?itemName=SAPSE.vscode-cds) Visual Studio Code Extension version 6.6.0 or higher is required.

### New CAP Notebook Samples ​

As CAP Notebooks are now available through our documentation, we make a different kind of CAP Notebook available to you from the [CAP Notebooks Welcome page](/docs/tools/cds-editors#cap-notebooks-page).

These are shorter notebooks which serve to describe and demonstrate the different code/language cell types (*Native Shell*, *Native Terminal*, *CDS*, etc.) as well as different commands available within a CAP Notebook providing you simple examples to help you get started.

### AsyncAPI Export Tooling ​

[AsyncAPI Export](/docs/guides/protocols/asyncapi) tooling is now available to document events in the CAP project in AsyncAPI format. You can provide additional configuration for AsyncAPI exports with [presets](/docs/guides/protocols/asyncapi#presets) and [annotations](/docs/guides/protocols/asyncapi#annotations).

sh

```
cds compile srv --service all -o docs --to asyncapi
```

[](/docs/guides/protocols/asyncapi)

## CAP on Kyma/K8s ​

### Connectivity Service ​

Connectivity Service Instance is no longer created by `cds add helm`. Only volumes are added to the `srv` deployment. You need to create the service and bind it before deployment.

[Learn more about Connectivity service.](/docs/guides/deploy/to-kyma#arbitrary-btp-services)

### Changes in the Helm Chart ​

- Renamed keys
- New way to specify parameters as JSON for service instances
- Two keys for `saas-registry`

With this release the following keys have been renamed/moved:

| Old | New |
| --- | --- |
| `html5_apps_repo_host` | `html5-apps-repo-host` |
| `service_manager` | `service-manager` |
| `saas_registry` | `saas-registry` |
| `event_mesh` | `event-mesh` |

[Learn more about configuring SAP BTP services.](/docs/guides/deploy/to-kyma#sap-btp-services)

The `config` property of service instances is no longer supported. If you want to specify parameters using a JSON file then you need to use `--set-file` flag during installation.

[Learn more about configuration options for SAP BTP services.](/docs/guides/deploy/to-kyma#configuration-options-for-services)

The `saas-registry` key has been split into 2 different keys. Key 1: `saas-registry` is dedicated for the service instance properties. Key 2: `saasRegistryParameters` is dedicated for the parameters and these parameters can be modified by the user if required.

Earlier the *values.yaml* content for `saas-registry` was:

yaml

```
saas_registry:
  serviceOfferingName: saas-registry
  servicePlanName: application
  parameters:
    getDependencies: "/-/cds/saas-provisioning/dependencies"
    onSubscription: "/-/cds/saas-provisioning/tenant/{tenantId}"
  ...
```

Now it's changed to:

yaml

```
...
saas-registry:
  serviceOfferingName: saas-registry
  servicePlanName: application
  parametersFrom:
    - secretKeyRef:
        name: "RELEASE-NAME-saas-registry-secret"
        key: parameters
saasRegistryParameters:
  xsappname: bookshop
  appName: bookshop
  displayName: bookshop
  description: A simple self-contained bookshop service.
  category: "CAP Application"
  appUrls:
    getDependencies: "/-/cds/saas-provisioning/dependencies"
    onSubscription: "/-/cds/saas-provisioning/tenant/{tenantId}"
    onSubscriptionAsync: true
    onUnSubscriptionAsync: true
    onUpdateDependenciesAsync: true
    callbackTimeoutMillis: 300000
```
