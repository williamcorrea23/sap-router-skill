<!-- mirror: https://cap.cloud.sap/docs/releases/2026/jan26 -->
<!-- fetched: 2026-05-09T02:26:56.619Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# January 2026 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Capire Renovations ​

We improved and streamlined structure across the documentation, making it easier to find relevant information quickly – especially in the existing [Get Started](/docs/get-started/), as well as the newly introduced [Develop](/docs/guides/), and [Deploy](/docs/guides/deploy/) sections. In addition, many guides have been thoroughly updated to reflect the latest best practices and features in CAP, as well as new guides added to cover new topics.

[](/docs/guides/)

Also, the styling includes some minor improvements, for example, adopted [GitHub Alerts-style callouts](/docs/get-started/learn-more#callouts-and-alerts), the *Scroll to Top* button that automatically appears when scrolling down a page, and the new/updated keyboard shortcuts . and , to quickly navigate through the guides. Press h to see all keyboard shortcuts.

### Getting Started Guides ​

The [Get Started](/docs/get-started/) section got a streamlined structure. These guides also received major content updates:

- Get Started > In a Nutshell – all new initial setup guides, emphasizing the need to Stay Up to Date.
- Bookshop Sample – significantly improved and enhanced our primer to promote latest best practices.
- Learn More – received a major cleanup, and got complemented with links to highly recommended learning sources, such as The qmacro Series.

[](/docs/get-started/)

### Databases Guides ​

The [Databases](/docs/guides/databases/) section received a major content overhaul and additions, especially in these new guides:

- CAP-Level Database Support
- CDL Compiled to DDL
- Adding Initial Data.

[](/docs/guides/databases/)

### Integration Guides ​

The [Integration](/docs/guides/integration/) section is a newly introduced section where we collected and added guides dedicated to:

- CAP-level Service Integration
- CAP-level Data Federation
- Inner-Loop Development

[](/docs/guides/integration/calesi)

NOTE

This replaces the former, now archived [Consuming (Remote) Services](/docs/guides/services/consuming-services) guide.

### Security & Data Privacy ​

Section [Security & Data Privacy](/docs/guides/security/) was completely restructured, and now consolidates all security and compliance aspects of CAP applications. Notable additions include a dedicated chapter about [Authentication](/docs/guides/security/authentication) with a focus on [IAS](/docs/guides/security/authentication#ias-auth). Another new section clarifies how assigned user claims such as [AMS](/docs/guides/security/cap-users#adding-ams-support-1)-Policies are represented in [CAP Users](/docs/guides/security/cap-users) and influence authorization checks at runtime. Finally, [Outbound Authentication](/docs/guides/security/remote-authentication) shows how CAP applications can establish HTTP connections to remote services without having to worry about authentication.

### CDS Expression Language ​

New reference docs for [CDS Expression Language (CXL)](/docs/cds/cxl) was added to provide an overview over the expression language which is used in [CDS Query Language (CQL)](/docs/cds/cql), [calculated elements](/docs/cds/cdl#calculated-elements), and in [annotation expressions](/docs/cds/cdl#expressions-as-annotation-values) like [`@assert`](/docs/guides/services/constraints).

[](/docs/cds/cxl)

## Node.js ​

### Support for express^5 ​

CAP Node.js now supports version 5 of [`express`](https://expressjs.com/) besides version 4, and we've made `express` a standard dependency.

If you don't require a specific version (for example, due to custom middleware), you can remove your own `express` dependency and automatically receive the latest version that is compatible with all your (transitive) dependencies.

Previously undefined `express` version

In case you so far didn't have an own dependency to `express` in your *package.json*, `express^4` was used, now `express^5` is used. This might break code of yours that worked with express APIs. In that case, add an explicit dependency to `express^4` to force that to be used – i.e.: `npm add express@4`.

[Learn more about `express` usage in CAP Node.js.](/docs/node.js/cds-facade#cds-app)

### Initial Data Folders Configuration ​

The new config option cds.requires.db.data lets you configure source folders for initial data and test data CSV files across different profiles, which allows you to more conveniently manage your initial data for production, development, as well as various test scenarios.

package.json.cdsrc.yamljson

```
"cds": {
  "requires": {
    "db": {
      "[development]": { "data": [ "db/data", "test/data" ] },
      "[production]": { "data": [ "db/data" ] }
    }
  }
}
```

yaml

```
cds:
  requires:
    db:
      '[development]': { data: [ db/data, test/data ] }
      '[production]': { data: [ db/data ] }
```

[Learn more about adding initial data.](/docs/guides/databases/initial-data)

`cds deploy --to hana` now includes test data

Ad-hoc deployments with [`cds deploy --to hana`](/docs/guides/databases/hana#cds-deploy-hana) previously omitted the *test/data/* folder, but include it now by default. To restore the original behavior, call it with `--production`.

### New cds.ql.clone() Method ​

The newly documented [`cds.ql.clone()`](/docs/node.js/cds-ql#cds-ql-clone) method allows you to create shallow clones of CQN query objects, to keep the original query intact. This is particularly useful when you need to modify queries programmatically before passing them along to execution.

Apply a *given -> clone -> modify -> forward* pattern to avoid unintended side effects:

js

```
// given
const q1 = SELECT.from`Books` .orderBy`genre.name`
```

js

```
// clone
let q2 = cds.ql.clone (q1)
```

js

```
// modify
q2.orderBy`title desc`
```

js

```
// forward
await cds.run (q2)
```

[Learn more about Modifying CQNs in the new Calesi guide.](/docs/guides/integration/calesi#modifying-cqns)

## Java ​

### Important Changes ❗️ ​

Note that SapMachine 17 will reach end of life (EOL) in [September 2026](https://sapmachine.io/docs/maintenance-and-support). Starting April 2nd, 2026 [SAP Java Buildpack](https://help.sap.com/whats-new/cf0cb2cb149647329b5d02aa96303f56?Component=SAP+Java+Buildpack) will default to Java 21.

Application deployments from this point onwards will be staged and started with JDK 21, unless the version is explicitly pinned to JDK 17:

yaml

```
---
applications:
- name:
  buildpacks:
  - sap_java_buildpack_jakarta
  ...
  env:
    TARGET_RUNTIME: tomcat
    JBP_CONFIG_COMPONENTS: "jres: ['com.sap.xs.java.buildpack.jre.SAPMachineJRE']"
    JBP_CONFIG_SAP_MACHINE_JRE: '{ version: 17.+ }'
```

Consider migrating to JDK 21 soon, or preferably directly to JDK 25.

### Relaxed Path-based Inserts ​

OData requests with intermediate to‑one segments which have no key filter like `header` in `POST /Order(123)/header/shipments` were not supported out of the box so far. Now the runtime accepts such a request in case an appropriate foreign key value (`header_ID` here) is provided in the request payload:

http

```
POST /Order(123)/header/shipments

{
   "ID": 1001,
   "trackingNo": "ABC123",
   "header_ID": 42
}
```

In general, foreign key values that can be derived from the path take precedence over conflicting payload values.

### Miscellaneous ​

- Support function `ceil` as synonym for `ceiling`.

## CDS Editor ​

###### tools ​

### Multi-cursor for Selection Ranges ​

Selection ranges now also work with VS Code's [multi-cursor mode](https://code.visualstudio.com/docs/editing/codebasics#_multiple-selections-multicursor).

Multi-cursor support is also available in IntelliJ through the CDS language server.

### Folding Ranges Improvements ​

The editor now treats consecutive `using` statements as one collapsible block.

Range folding is also available in IntelliJ through the CDS language server.

### Faster References Search and Workspace Symbols Beta ​

Tasks like `Find References` or `Workspace Symbols` now may run faster through a persisted index. Especially larger projects with multiple independent CDS files will benefit here.

In VS Code, enable the feature through setting [cds.workspace.persistency.enabled](vscode://settings/cds.workspace.persistency.enabled).

This feature is currently in beta. Please let us know about improvements or issues in your projects.

### User Settings with Category Groups ​

The editor now groups the user settings in categories, allowing easier navigation:

## Kyma ​

### Multitenancy Upgrades for Kyma ​

For multitenant Kyma applications, `cds add multitenancy` now adds the [mtx-upgrade](/docs/guides/multitenancy/#update-database-schema) Kubernetes job, automatically executed on each deployment.

[Learn more about Kyma Deployment.](/docs/guides/deploy/to-kyma)

### cds debug --k8s ​

`cds debug` is now also available for Kubernetes. Simply run this command to open a Chrome Node.js debugging session on your remote application running in Kyma:

sh

```
cds debug bookshop-srv --k8s
```

Use `kubectl get deployments` to see available applications.

## Capire Updates ​

Besides the renovations, mentioned at the top of the release notes this month, we had some more notable changes and additions.

### Exclude Elements with @cds.java.ignore ​

We documented how to exclude specific elements, actions, or functions from generated accessor interfaces using the `@cds.java.ignore` annotation.

[Learn more about excluding elements from accessor interfaces.](/docs/java/cds-data#excluding-elements)

### Enhanced cds deploy --to hana Documentation ​

The documentation for [`cds deploy --to hana`](/docs/guides/databases/hana#cds-deploy-hana) has been significantly improved with clearer explanations of how it works and better guidance on configuring deployments.

[Learn more about deploying to SAP HANA.](/docs/guides/databases/hana#cds-deploy-hana)

### Runtime Flag for Sample Projects ​

When adding sample files or data, you now need to use the `--nodejs` or `--java` flag. The flag clarifies the target runtime and ensures proper project setup.

sh

```
cds init --add sample --nodejs
```

[Learn more about `cds init` commands.](/docs/tools/cds-cli#cds-init)

### Enhanced Java Plugin Development Guide ​

The update includes additional guidance on:

- Proper versioning requirements for plugin compatibility
- Using Spring Boot auto-configuration correctly
- Recommended `cds-services` versions for plugin development

[Learn more about building CAP Java plugins.](/docs/java/building-plugins)
