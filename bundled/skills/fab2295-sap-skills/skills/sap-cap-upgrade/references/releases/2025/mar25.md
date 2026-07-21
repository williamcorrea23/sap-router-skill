<!-- mirror: https://cap.cloud.sap/docs/releases/2025/mar25 -->
<!-- fetched: 2026-05-09T02:26:52.621Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# March 2025 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Prepare for Major Release ​

Along with new features, the next major release CDS 9 will contain some changes that you'll need to react on. For the items listed below, you can do this already **now**, which eases the transition. You can't use the mentioned **deprecated functions** with the CDS 9 release. The corresponding compatibility flags won't be respected any longer.

- Migrate ESLint Configuration
- Add Test Support Package
- Switch on the new CDS parser.
- Upgrade to `@sap/xssec 4`. --> remove compat flag
- Switch on OData containment.
- Adapt to changed behavior when processing `@restrict.where` checks.
- Adopt @cap-js database services now.
- Switch on the new protocol adapters. --> remove compat flag
- Switch on lean draft. --> remove compat flag

## CDS Language & Compiler ​

### New Parser ​

Switch over to the new parser already now. Set option cds.cdsc.newparser: true in your private `~/.cdsrc.json` to switch on the new parser on your local machine. Switch it on in your project's development and test pipelines. If that's successful, use it in production.

### Actions in Composition of Aspects ​

Actions and functions of a CDS aspect are now available in the generated child entity when defining a composition of aspect.

In this example, the compiler-generated child entity `Orders.items` has an action `close`:

cds

```
aspect Item {
  key id : String;
} actions {
  action close();
};

entity Orders {
  key id : String;
  items: Composition of Item;
};
```

[Learn more about the composition of aspects.](/docs/cds/cdl#managed-compositions)

## Node.js ​

### Recursive Hierarchies and Fiori Tree Table Support Beta ​

CAP Node.js now supports [Recursive Hierarchies](https://sap.github.io/odata-vocabularies/vocabularies/Hierarchy.html) with OData v4 on SAP HANA Cloud, allowing to serve read requests for the [SAP Fiori Tree Table](https://experience.sap.com/fiori-design-web/tree-table/), including sort, filter, and search on hierarchical data.

You can try it out in our [bookshop sample for SAP Fiori](https://github.com/capire/bookstore/blob/main/app). Simply run

- `cds deploy -2 hana --production`
- `cds watch --profile hybrid`

The `Browse Genres` app as well as the value help for `Genres` in the `Manage Books` app use the SAP Fiori Tree Table.

## Java ​

### Log CDS Configuration ​

Upon start-up, you can now get an overview of the configured [CDS properties](/docs/java/developing-applications/properties). Turn on by setting the log level for `com.sap.cds.properties` to `DEBUG` in the *application.yaml* file:

srv/src/main/resources/application.yamlyaml

```
logging:
  level:
    com.sap.cds.properties: DEBUG
```

Sample output:sh

```
... DEBUG ... com.sap.cds.properties : 'cds.dataSource.autoConfig.enabled': 'false' (default: 'true')
... DEBUG ... com.sap.cds.properties : 'cds.dataSource.embedded': 'true' (default: 'false')
...  WARN ... com.sap.cds.properties : 'cds.security.authorization.emptyAttributeValuesAreRestricted': 'false' (default: 'true', deprecated, not documented)
... DEBUG ... com.sap.cds.properties : 'cds.security.mock.users.admin.name': 'admin'
... DEBUG ... com.sap.cds.properties : 'cds.security.mock.users.admin.password': '***' (sensitive)
... DEBUG ... com.sap.cds.properties : 'cds.security.mock.users.admin.roles[0]': 'admin'
... DEBUG ... com.sap.cds.properties : 'cds.security.mock.users.admin.roles[1]': 'cds.Developer'
... DEBUG ... com.sap.cds.properties : 'cds.security.mock.users.admin.attributes.businessPartner[0]': '10401010'
... DEBUG ... com.sap.cds.properties : 'cds.odataV4.endpoint.path': '/api' (default: '/odata/v4')
... DEBUG ... com.sap.cds.properties : 'cds.errors.defaultTranslations.enabled': 'true' (default: 'false')
```

### Miscellaneous ​

- Subscription dependencies for portal and html5-apps-repo are automatically created if the corresponding service is bound to the CAP Java application.
- The result of the execution of a `CqnUpsert` statement now provides an entity reference to the upserted entity via the `Row.ref()` method.

## Multitenancy ​

### Extension Drafts Beta ​

The API [`PUT /-/cds/extensibility/Extensions/`](/docs/guides/multitenancy/mtxs#put-extensions) can now be used to upload extensions as drafts. This allows to trigger the upload, validation, and activation of extensions separately.

Example:

http

```
PUT /-/cds/extensibility/Extensions/isbn-extension HTTP/1.1
Content-Type: application/json

{
  "csn": ["using my.bookshop.Books from '_base/db/data-model';
           extend my.bookshop.Books with { Z_ISBN: String };"],
  "i18n": [{ "name": "i18n.properties", "content": "Books_stock=Stock" },
           { "name": "i18n_de.properties", "content": "Books_stock=Bestand" }],
  "status": 1 // draft = 1, activation = 2
}
```

This request adds an extension with `ID` `isbn-extension` as draft. It will not be publicly visible and necessary changes are not deployed to the database.

http

```
POST /-/cds/extensibility/validate HTTP/1.1
Content-Type: application/json

{
  "ID": "isbn-extension"
}
```

This request validates the extension with `ID` `isbn-extension`.

http

```
POST /-/cds/extensibility/Extensions/activate HTTP/1.1
Content-Type: application/json

{
  "ID": "isbn-extension",
  "status": 2 // target status 2 = activation
}
```

This request promotes the extension with `ID` `isbn-extension` to status `2`, making it visible to everyone and applying any necessary changes to the database. Note that `2` is the default value for `status`, so it can be omitted if the goal is to make extensions publicly visible.

Please note: `status` was `level` in the first version of the API.

## Tools ​

### Deployment With cds up Beta ​

Given you have fulfilled the prerequisites for [Cloud Foundry](/docs/guides/deploy/to-cf#prerequisites) or [Kyma](/docs/guides/deploy/to-kyma#prerequisites) deployments, a new command allows for a simpler way to build and deploy CAP applications:

sh

```
cds up
```

This deploys your CAP app to Cloud Foundry by default.

Essentially, this command automates the following steps...sh

```
# Depending on your deployment method...
cds add mta # Cloud Foundry
cds add helm,containerize # Kubernetes

# Installing app dependencies, e.g.
npm i app/browse
npm i app/admin-books

# If project is multitenant
npm i --package-lock-only mtx/sidecar

# If package-lock.json doesn't exist
npm i --package-lock-only

# Final assembly and deployment...

### Cloud Foundry
mbt build -t gen --mtar mta.tar
cf deploy gen/mta.tar -f

### Kyma/Kubernetes, e.g.
ctz containerize.yaml --log --push
helm upgrade --install bookshop ./gen/chart --wait --wait-for-jobs --set-file xsuaa.jsonParameters=xs-security.json
kubectl rollout status deployment bookshop-srv --timeout=8m
kubectl rollout status deployment bookshop-approuter --timeout=8m
kubectl rollout status deployment bookshop-sidecar --timeout=8m
```

For Kyma (Kubernetes), simply run:

sh

```
cds up --to k8s
```

### Initial Type Generation With cds watch ​

[`cds-typer`](/docs/tools/cds-typer) is now run once by `cds watch`. This is useful for newly cloned projects to generate the model types initially. For example, model imports like this no longer error out at startup:

srv/cat-service.jsjs

```
const { Books } = require('#cds-models/sap/capire/bookshop')
```

Manual invocations, like `npx cds-typer`, are no longer needed for this local scenario but still relevant for CI workflows, though.

### Ad-hoc SAP HANA Deployment on Kyma ​

[`cds deploy --to hana`](/docs/guides/databases/hana#cds-deploy-hana) is now also supported for Kubernetes:

sh

```
cds deploy --to hana: --on k8s
```

Omitting the binding or secret name creates a new HDI container and binding called `-db-binding`.
