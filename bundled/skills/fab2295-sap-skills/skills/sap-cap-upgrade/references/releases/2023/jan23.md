<!-- mirror: https://cap.cloud.sap/docs/releases/2023/jan23 -->
<!-- fetched: 2026-05-09T02:26:37.112Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# January 2023 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## CDS Language & Compiler ​

### Simplified Syntax for Binding Parameters ​

Bound actions or function have a so-called [binding parameter](https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#sec_BindinganOperationtoaResource) pointing to their bound entity — similar to `this` for Java or JavaScript methods — which usually is implicitly defined. In the following example, the bound action `CatalogService.Products.addReview` implicitly has a binding parameter `in` with type `Products`:

cds

```
service CatalogService {
  entity Products { ... }
    actions { // bound actions or functions
      action addReview (stars: Integer, comment: String);
    }
}
```

Sometimes however, you need to change the name or the type of this parameter, for example to bind the action or function to a *collection* of instances of the base entity rather than to a single instance. This is now possible by explicitly modelling the binding parameter: the *first* parameter of a bound action or function is treated as binding parameter, if it's typed by `[many] $self`. Use Explicit Binding to control the naming of the binding parameter. Use the keyword `many` to indicate that the action or function is bound to a collection of instances.

cds

```
service CatalogService {
  entity Products { ... }
    actions { // bound actions or functions
      action addReview (in: $self, stars: Integer, comment: String);
      action archiveOutOfStock (products: many $self, since: Date);
    }
}
```

Action `addReview` shows the equivalent of the action in the first example above but with an explicit binding parameter. Action `archiveOutOfStock` is bound to a collection of `Products` via a binding parameter called `products`.

Tip

In the past you had to use annotations `@cds.odata.bindingparameter.name` and `@cds.odata.bindingparameter.collection` to achieve the same, which are not required anymore, and deprecated from now on.

Explicit binding parameters are ignored in OData V2.

[Learn more about Bound Actions and Functions.](/docs/cds/cdl#bound-actions)

### Extending the Generated .texts Entities ​

If you have [localized data](/docs/guides/uis/localized-data), you can now collectively extend all generated *.texts* entities by extending the aspect [`sap.common.TextsAspect`](/docs/cds/common#texts-aspects), which is defined in file *common.cds*.

Use this to add an association targeting the `Languages` code list entity, or for adding flags that help you to control the translation process.

Example:

cds

```
extend sap.common.TextsAspect with {
  language : Association to sap.common.Languages on language.code = locale;
}
```

In the bookshop sample, this would result in the following *Books.texts* entity:

cds

```
entity Books.texts {
  key locale: sap.common.Locale;
  language : Association to sap.common.Languages on language.code = locale;
  key ID : UUID;
  title : String;
  descr : String;
}
```

[Learn more about Extending generated .texts entities.](/docs/guides/uis/localized-data#extending-texts-entities)

## Node.js ​

### Fixed Semantics of .where Function in Query API ​

In previous versions of the query API, the `where` method didn't consistently wrap the existing where clause in an `xpr`, resulting in situations where the provided expression wasn't always correctly evaluated.

Example:

js

```
const query = SELECT.from('Entity')
query.SELECT.where = [{ ref: [ 'a' ] }, '=', { val: 1 }, 'or', { ref: [ 'b' ] }, '=', { val: 2 }]
query.where({ c: 3 })
```

The generated SQL where clause would be `a = 1 or b = 2 and c = 3`, where the second expression might not be evaluated. This is now corrected and the expressions are correctly grouped, in SQL terms `(a = 1 or b = 2) and c = 3`.

### Continued Improvement of cds.d.ts Typings ​

Together with our community, we've done various improvements in our [TypeScript typings](/docs/node.js/typescript#typescript-apis-in-sap-cds):

- Typings for cds.test to allow additional arguments
- Typings for srv.send to support unbound actions
- Typings for cds.ql to return the correct CQN

If you observe gaps in any of the typings, we appreciate your help.

### Improved Implementation for search on SAP HANA ​

When searching on localized properties, it's now searched in the translation and the fallback for an entry matching the search term. Considering the [bookshop sample](https://github.com/SAP-samples/cloud-cap-samples/blob/main/bookshop) and a German user using the search terms **Wuthering** or **Sturmhöhe**, both would return a match.

## Java ​

### Important Changes ❗️ ​

#### Removed Support for Associations Between Unrelated Draft Entities ​

Associations from draft entities pointing outside the draft document no longer include entities in inactive state, that is, queries only return associated *active* data. In contrast, a corresponding composition from a draft entity always refers to an inactive entity as part of the hierarchical draft document.

In the following example

cds

```
service Bookshop {
  @odata.draft.enabled
  entity Books {
    author: Association to Authors;
    ...
  }

  @odata.draft.enabled
  entity Authors {
    ...
  }
}
```

the query `GET /Bookshop/Book(ID=,IsActiveEntity=false)/author` returns an associated entity (type `Authors`) with `IsActiveEntity=true` (or `null` if not existing), even if there's a draft version.

To restore the previous behaviour, you can configure `cds.drafts.associationsToInactiveEntities.enabled: true`.

Warning

This switch is deprecated and will be removed in future.

#### Changed HTTP Error Code on Missing Authentication ​

Unauthenticated requests are now rejected with HTTP error code 401 if they fail *authorization* (error code 403 previously). This can only happen in a misconfigured application where no authentication is active (for example, no Spring security added) but still authorization is performed by generic CAP handler. Productive usage shouldn't be affected but you might have to adjust test code.

### JDK 17 Support ​

JDK 17 is now fully supported and also the *recommended* runtime JDK. Until now, only JDK 8 and JDK 11 were supported. Due to the [Spring Boot support schedule](https://spring.io/projects/spring-boot#support), Spring Boot version 2.7 that is currently used will reach end of OSS support in November 23. The latest Spring Boot version 3 has minimum JDK version 17. Therefore, **we recommend a migration to JDK 17 in the near future** as preparation for the upcoming Spring Boot 3 migration.

We also recommend configuring [SapMachine](https://sap.github.io/SapMachine/) 17 JDK (respective JRE) with the [SAP Java buildpack](https://help.sap.com/docs/btp/sap-business-technology-platform/developing-java-in-cloud-foundry-environment) as shown in the example (`mta.yaml`):

yaml

```
modules:
  - name: MyCAPJavaApp
    type: java
    path: srv
    parameters:
      ...
      disk-quota: 512M
      buildpack: sap_java_buildpack
    properties:
      JBP_CONFIG_COMPONENTS: "jres: ['com.sap.xs.java.buildpack.jre.SAPMachineJRE']"
      JBP_CONFIG_SAP_MACHINE_JRE: '{ use_offline_repository: false, version: 17.+ }'
```

Current `sap_java_buildpack` has some limitations for JDK 17:

- Public Internet access is required to download the JDK (no offline mode).
- Only Java Main deliveries are supported (no restriction for Spring Boot apps).

### Reserved Database Keywords ​

You can now use identifier names in your CDS Models, which are [reserved words and keywords](/docs/guides/databases/cdl-to-ddl#reserved-words) on the target database. The runtime now uses delimited identifiers in the database's default case to avoid a clash with the keyword.

### Memory Consumption of CDS Models ​

The CAP Java runtime serves business requests on basis of CDS models that are cached in-memory for fastest possible processing. Especially for multi-tenancy, when different tenant-specific models are required, the CDS model cache can consume a substantial amount of memory.

CAP Java now stores CDS models in a more compact representation. Since 1.30, the model reader [strips UI annotations](./../2022/dec22#miscellaneous) from the in-memory representation.

With the model of the CAP SFlight [sample application](https://github.com/SAP-samples/cap-sflight), we observe the following improvements:

| CAP Java Version | file size | memory size | reduction |
| --- | --- | --- | --- |
| 1.29 | 222 kB | 1.30 MB |  |
| 1.30 w/ UI annotations | 222 kB | 735 kB | 43 % |
| 1.30 w/o UI annotations | 222 kB | 573 kB | 56 % |
| 1.31 w/o UI annotations | 222 kB | 171 kB | 87 % |

Moreover, some model artifacts, which are common to multiple tenants are now shared in memory. With *three* variants of the same Fiori Elements sample application model, which have only small differences, we observe:

| CAP Java Version | file size | memory size | reduction |
| --- | --- | --- | --- |
| 1.29 | 667 kB | 3.95 MB |  |
| 1.30 w/ UI annotations | 667 kB | 2.09 MB | 47 % |
| 1.30 w/o UI annotations | 667 kB | 1.69 MB | 57 % |
| 1.31 w/o UI annotations | 667 kB | 505 kB | 87 % |

### Security ​

- You can now limit the maximum number of requests that are accepted within a single OData `$batch` request. Settings `cds.odataV4.batch.maxRequests` resp. `cds.odataV2.batch.maxRequests` specify the corresponding limits. By default, no limit applies.
- Added a generic UserInfoProvider that recognizes requests on behalf of the provider tenant and normalizes the request tenant to `null`(that is, `UserInfo.getTenant() == null`). This helps to distinguish provider requests from subscriber requests, for instance when fetching the tenant-specific CDS model or when dispatching to the corresponding PersistenceService. Set `cds.security.authentication.normalizeProviderTenant` to `true` to activate the normalization.

### Modification of CQN Statements ​

Use the new `Modifier` methods `skip` and `top` to [modify](/docs/java/working-with-cql/query-api#copying-modifying-cql-statements) the pagination settings of a `CqnQuery`.

Warning

The subinterface `CqnModifier`, which does an expensive copy of values, is now deprecated and will be removed in a future release.

### OData: Update Related Entities Using Delta Payload ​

For OData PATCH requests that [update related entities](https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#sec_UpdateRelatedEntitiesWhenUpdatinganE) (deep updates) and specify the related entities as a nested [delta payload](https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#sec_DeltaPayloads), the key values of entities to be removed can now be given as properties instead of `@id` control information. The "reason" property of `@removed` is optional now.

json

```
{
    "ID": "o101",
    "Items@delta": [
        {
            "ID": "i01",
            "amount": 101
        },
        {
            "ID": "i02",
            "@removed": { }
        },
        {
            "@id": "OrderItems(i03)",
            "@removed": { "reason": "deleted" }
        }
    ]
}
```

The example update payload for `Order(o101)` contains a nested delta payload for the associated order items. Upon executing the PATCH request, order item `i01` is upserted (inserted or updated as needed), and items `i02` and `i03` are deleted. All other items of `Order(o101)` remain untouched.

## Tools ​

### Cloud Foundry User-Provided Services in Hybrid Testing ​

User-provided services can now be used for [hybrid testing](/docs/tools/cds-bind). The handling is fully transparent to users, e.g `cds bind --to my-user-provided-service` is sufficient.

`cds watch --profile hybrid` will automatically resolve bindings to user-provided service instances using the same technique as for any other managed services.

## Multitenancy ​

### Minimum Runtime Version Required ​

`@sap/cds-mtxs` version `>= 1.5.0` requires at least `@sap/cds@6.5.0`.

### Support of hdbmigrationtable in Extensible Projects ​

SaaS applications using extensibility can now use `@cds.persistence.journal` for base model entities to get `.hdbmigrationtable` support. Important: Extending migration table artifacts isn't supported.

### Cache Database Credentials from SAP Service Manager ​

The credentials fetched from the `service-manager` are now cached. This reduces the number of requests to the `service-manager`, mitigating errors caused by rate-limiting. Disable caching by setting `cds.requires.multitenancy.cacheBindings = false`.

### Simpler Deployment Service Configuration ​

You can now configure the deployment service in a simpler way:

jsonc

```
"hdi": {
  "create": {
    "database_id": ""
  },
  "bind": {
    "key": "value"
  }
}
```

Instead of:

jsonc

```
"hdi": {
  "create": {
    "provisioning_parameters": {
      "database_id": ""
    },
    "binding_parameters": {
      "key": "value"
    }
  }
}
```

The old configuration is still supported, but you're advised to migrate to the new configuration for improved readability.

### Improved Job Status Response ​

`/-/cds/jobs/pollJob` now also returns a `tenants` field, so tenant-specific tasks don't have to be polled individually. An example response format looks like this:

json

```
{
  "status": "FAILED",
  "op": "upgrade",
  "tenants": {
      "non-existing-tenant": {
         "status": "FAILED",
         "error": "Tenant 'non-existing-tenant' does not exist"
      },
      "existing-tenant": {
         "status": "FINISHED"
      }
   }
}
```

## CAP on Kyma/K8s ​

### SAP HANA Cloud HDI Containers on Kyma Runtime ​

With the December 2022 release of the SAP HANA Cloud tools, we can now create HANA HDI shared containers on the Kyma runtime. The CAP on Kyma tooling creates HANA HDI shared containers on the Kyma runtime itself.

### Support for Multitenancy and App Router ​

CAP on Kyma tooling now supports the deployment of Multitenant SaaS applications on Kyma along with App Router. The [Deploy to Kyma guide](/docs/guides/deploy/to-kyma) is updated with the multitenancy deployment instructions.

### Changes in the Helm Chart ​

With this release, the [Helm charts](/docs/guides/deploy/to-kyma#deploy-to-kyma) (`cds add helm`), the following keys have been renamed/moved:

| Old | New |
| --- | --- |
| `hana_deployer` | `hana-deployer` |
| `html5_apps_deployer` | `html5-apps-deployer` |
| → `bindings` → `html5_apps_repo` | → `bindings` → `html5-apps-repo` |
| → `cloudService` | → `env` → `SAP_CLOUD_SERVICE` |

In addition to these properties, `backendDestinations` is now moved from `html5_apps_deployer.backendDestinations` to root of `values.yaml`.

Earlier the `values.yaml` content for `HTML5 Apps Deployer` was:

yaml

```
html5_apps_deployer:
  cloudService: null
  backendDestinations: {}
  ...
```

Now, it's changed to:

yaml

```
backendDestinations: {}
html5-apps-deployer:
  env:
    SAP_CLOUD_SERVICE: null
  ...
```
