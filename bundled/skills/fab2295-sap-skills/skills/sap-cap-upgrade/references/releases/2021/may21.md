<!-- mirror: https://cap.cloud.sap/docs/releases/2021/may21 -->
<!-- fetched: 2026-05-09T02:26:27.749Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# May 2021 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtx?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Important Changes❗️ ​

### Minimum Node.js Version Enforced ​

Node.js v12.18 as minimum version ([announced in March](./mar21#noteworthy-changes)) is now checked on server startup, to prevent further errors due to older Node.js versions. If startup errors occur, see the [Troubleshooting guide](/docs/get-started/get-help#node-version) for more details.

### Multitenancy Changes ​

##### Default Scope Checks for SaaS Provisioning and Upgrade Requests ​

SaaS provisioning operations *GET*, *PUT*, and *DELETE* on API `/mtx/v1/provisioning/tenant/` now require scope `mtcallback`. Upgrade calls on API `/mtx/v1/model/upgrade/` and `/mtx/v1/model/upgradeAsync/` now require scope `mtdeployment`. With that, it is no longer required to provide own scope checks in a provisioning handler implementation to ensure security.
 This is now aligned with the mandatory scope check required for the CAP Java SDK.
 To adapt the scope names to the CAP Java SDK scope configuration, the scope names can be changed using the following CDS configuration:

json

```
"mtx": {
    "security": {
        "subscription-scope": "myApp.subscription",
        "deployment-scope": "myApp.deployment"
    }
}
```

##### Enhanced extension-allowlist and Changed Default for Allowlist ​

The default behavior of the `extension-allowlist` has changed. If `extension-allowlist` is not configured, it is not allowed to apply any extension.
 Extensions can be easily enabled for all entities and services by adding the following to the configuration.

json

```
"mtx": {
  "extension-allowlist": [
      { "for": ["*"] }
  ]
}
```

##### Dependencies Included with MTX ​

`@sap/hdi-deploy` and `@sap/instance-manager` are now directly required by `@sap/cds-mtx`. Therefore, they can be left out of your *package.json* `dependencies`.

## Capire Docs & Samples ​

##### New Guide Managing Data Privacy ​

A new cookbook related to data-privacy requirements is available. We give a general introduction to the topic and showcase how to use a CAP application with the SAP Personal Data Manager service of SAP BTP. You can use our [cap/samples](https://github.com/sap-samples/cloud-cap-samples) to follow along and try it hands-on in your enterprise account (entitlement required).

##### Revised Guide for Authorization ​

Two new sections have been added to the cookbook Authorization. In section [Events to Auto-Exposed Entities](/docs/guides/security/authorization#events-and-auto-expose), we demonstrate in a small example which events can be sent to auto-exposed entities. [Restrictions of Auto-Exposed and Generated Entities](/docs/guides/security/authorization#autoexposed-restrictions) explains the authorization rules that apply for request to auto-exposed or generated entities that have no explicit restrictions.

##### Anchor Links ​

You can now share direct links to sections by copying its anchor link. The anchor icon appears when hovering a section heading.

## Command Line / Toolkit ​

### Automatically Open Application URL ​

`cds watch --open` automatically opens the application's URL in the browser. You can also specify a custom URL like `cds watch --open browse/Books`.

This also works in SAP Business Application Studio, where a separate browser tab is opened.

## Node.js Runtime ​

### Observability Improvements ​

##### Logging Facade Beta ​

`cds.log()` is a minimalistic logging framework and is used throughout the Node.js runtime, including the inherited `@sap/odata-server`. By default, it logs to `console`. However, it allows to plug in other logging modules such as Winston, Bunyan, or Morgan. See section [cds.log()](/docs/node.js/cds-log) for more details.

##### Custom Error Handler Beta ​

Stakeholders can now register a custom error handler that is invoked whenever an error will be returned to the client. See section [srv.on('error', (err, req) => {})](/docs/node.js/core-services#srv-on-error) for more details.

### Generic Providers ​

##### Improved Input Validation ​

The input validation framework was extended to support arrayed elements.

Example:

cds

```
entity MyEntity {
  // …
  emails: array of {
    to: String not null @assert.format: '.+\@.+\..+';
    subject: String not null;
    body: String;
  };
};
```

Further, the relevant input- and modeling-related information of assertion errors was added to the error message. For example, for input `4` and modeling `@assert.range: [0, 3]`, the message now reads `Value 4 is not in specified range [1,3]` instead of only `Value is not in specified range.`.

##### Additions to Managed Data ​

The Node.js runtime now supports pseudo variables `$uuid` and `$user.` in managed data. Further, static values can be specified, for example `@cds.on.insert: 'foo'`. See section [Managed Data](/docs/guides/domain/index#managed-data) for more details.

##### Draft Handling ​

Finally, the generic read handler for drafts-enabled entities now correctly returns a single object if the key of the entity is provided. Before, it erroneously returned an array with a single entry.

### CSRF-Token Handling in Service Consumption ​

If the remote system you want to consume requires it, you can enable the new CSRF-token handling of `@sap-cloud-sdk/core` via `cds.env.features.fetch_csrf = true`.

## Java SDK ​

### Streaming Support ​

The CAP Java SDK now supports [streaming of media data](/docs/guides/services/media-data). You can leverage this feature by annotating entity properties with `@Core.MediaType`.

### Improved H2 Database Support ​

H2 databases are now automatically detected as embedded databases, ensuring that CSV files are automatically initialized.

### Improved CSV File Handling ​

CSV files with locale ending are now supported for text tables of localized entities (for example, `Books.texts_de.csv`) when initializing in-memory databases.

### Support for Type References ​

The CDS Reflection API and code generator now support type references:

cds

```
entity Person {
  key ID : UUID;
}
entity Author {
  key ID : Person:ID;  // type ref
}
```

The Reflection API resolves type references, so that they can be accessed in the same way as standard types:

java

```
CdsModel model = CdsModel.read(csn);
CdsType type = model.getEntity("Author").getElement("ID").getType();
```

### Check if a CQN Statement Is a Count Query ​

`CqnAnalyzer.isCountQuery(cqn)` allows to check if a CQN statement only returns a single count.

### CQL API ​

`CQL.literal(val)` has been deprecated and replaced by `CQL.constant(val)` and `CQL.val(val)` for defining constant and non-constant values.

### Performance Improvements ​

The performance of to-many expands and deep updates has been improved.
