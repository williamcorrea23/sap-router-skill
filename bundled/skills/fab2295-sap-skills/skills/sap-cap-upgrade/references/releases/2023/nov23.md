<!-- mirror: https://cap.cloud.sap/docs/releases/2023/nov23 -->
<!-- fetched: 2026-05-09T02:26:38.752Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# November 2023 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## New Learning Sources Page ​

We created a new page that collects selected learning resources for you. We aim to maintain and curate the best learning content for you here, so please feel free to nominate blog posts, tutorials, etc in our [capire/docs](https://github.com/capire/docs/issues/new) repository, which helped you and should get more attention.

[](/docs/get-started/learn-more)

[Find here the new Learning Sources page.](/docs/get-started/learn-more)

## CAP Plugins ​

### New Overview Page in capire ​

There's a new page showing you a curated list of plugins that are available for the SAP Cloud Application Programming Model (CAP) which provide integration with BTP services and technologies, or other SAP products. For example, you'll find there the well known GraphQL adapter or the OData V2 proxy.

[](/docs/plugins/)

Maintained by CAP and SAP

These plugins are created and maintained in close collaboration and shared ownership of CAP development teams and other SAP and BTP development teams.

[Have a look at the new CAP plugins page.](/docs/plugins/)

### New Change Tracking Plugin ​

A new CDS plugin package [@cap-js/change-tracking](https://www.npmjs.com/package/@cap-js/change-tracking) is now available and [open source](https://github.com/cap-js/change-tracking). Simply add the package to your application's dependencies and get out-of-the box support for automatic capturing, storing, and viewing of the change records of modeled entities:

sh

```
npm add @cap-js/change-tracking
```

Warning

Please note that `@cap-js/change-tracking` is currently released as an early adopter version and, hence, minor breaking changes are possible in the general availability version.

[Find more details about the Change Tracking Plugin.](https://github.com/cap-js/change-tracking)

### Notifications Plugin for Business Notifications ​

A new CDS plugin package [@cap-js/notifications](https://www.npmjs.com/package/@cap-js/notifications/) is now available and [open source](https://github.com/cap-js/notifications). Simply add the package to your application's dependencies and publish the business notifications:

sh

```
npm add @cap-js/notifications
```

Warning

Please note that `@cap-js/notifications` currently supports single tenant application scenarios with notification types lifecycle management.

[Find more details about the Notifications Plugin.](https://github.com/cap-js/notifications)

[Find here more CAP plugins with a short description and all relevant links.](/docs/plugins/)

## CDS Language & Compiler ​

### Annotating Draft Entities ​

If an entity is draft related, additional entities and elements are generated for the database model or for the OData API, respectively. These additional entities and elements can now be annotated.

Example:

cds

```
annotate AdminService.Books.drafts with @cds.persistence.journal;
annotate AdminService.Books:DraftAdministrativeData with @UI.Hidden: false;
```

## Node.js ​

### Inferring Query Elements ​

A new API `req.query.elements` has been added to conveniently infer and reflect a query's result set. For example:

js

```
let q = SELECT.from(Books, b=>{ b.ID, b.title })
q.elements //> will return a CSN struct object like that:
{
  ID: { key: true, type: 'cds.Integer' },
  title: { type: 'cds.String', length: 111, localized: true }
}
```

The returned object contains the selected column names as key and the CSN definitions as value. This comes in very handy if custom implementation must be triggered on selection of certain elements, for example, *virtuals*.

js

```
if ('foo' in req.query.elements) doSomething()
```

[Find more details about the new API.](/docs/node.js/cds-ql#elements)

### Persistent Outbox by Default ​

The default [outbox](/docs/node.js/queue) configuration has been changed to `persistent-outbox`. As a result, once `cds.requires.outbox` is set to `true`, all messaging services and the audit-logging service now first store outgoing messages in a database table before sending them to the respective platform service.

Configuration to use the default, that is, persistent outbox:

json

```
{
  "cds": {
    "requires": {
      "outbox": true
    }
  }
}
```

To use the former default, the behavior can be restored with:

json

```
{
  "cds": {
    "requires": {
      "outbox": "in-memory-outbox"
    }
  }
}
```

[Learn more about the Transactional Outbox.](/docs/node.js/queue)

### Miscellaneous ​

- In order to comply with the specific error format of SAP Fiori Elements, we've implemented a feature flag `cds.fiori.wrap_multiple_errors = false`. With this, the first error is used as top level error instead of a generic wrapper error. This will become the default in the next major version.
- On SAP BTP Cloud Foundry Runtime, the default keep alive timeout of the server is set to 91s in order to exceed the 90s of Cloud Foundry gorouter. This was frequently the reason for intermittently failing requests with status code 502.

## Java ​

### JDK 21 Support ​

CAP Java 2 now officially supports [JDK 21](https://openjdk.org/projects/jdk/21/) which has been released as new LTS version recently.

We recommend configuring [SapMachine](https://sap.github.io/SapMachine/) 21 JDK (respective JRE) with the [SAP Java buildpack](https://help.sap.com/docs/btp/sap-business-technology-platform/developing-java-in-cloud-foundry-environment) as shown in the example (`mta.yaml`):

yaml

```
modules:
  - name: MyCAPJavaApp
    type: java
    path: srv
    parameters:
      ...
      buildpack: sap_java_buildpack
    properties:
      JBP_CONFIG_COMPONENTS: "jres: ['com.sap.xs.java.buildpack.jre.SAPMachineJRE']"
      JBP_CONFIG_SAP_MACHINE_JRE: '{ use_offline_repository: false, version: 21.+ }'
      JBP_CONFIG_JAVA_OPTS: '[from_environment: false, java_opts: ''-XX:+IgnoreUnrecognizedVMOptions'']'
```

Current `sap_java_buildpack` does not yet officially support JDK 21 and therefore has some limitations:

- Public Internet access is required to download the JDK (no offline mode).
- Only Java Main deliveries are supported (no restriction for Spring Boot apps).

Warning

The default parameter [`UseContainerCpuShares`](https://bugs.openjdk.org/browse/JDK-8281571), set by the SAP Java buildpack, is now removed. The sizing of JVM with respect to fork join pool, number of GC and compiler threads might change with JDK 21 in contrast to older JVM releases. If required, apply appropriate JVM sizing parameters according to your needs.

### Reading Drafts ​

#### New Draft Read Events ​

Upon [read of draft-enabled entities](/docs/java/fiori-drafts#reading-drafts), the standard `READ` event of a `CqnService` now spawns new `ACTIVE_READ` and `DRAFT_READ` events. These events allow to register event handlers to selectively handle the read of active entity data and draft data.

#### Split Persistence ​

Active entity data and draft data is usually co-located in the same database schema. By default, query execution of draft-enabled entities is optimized for performance and may leverage the option to join data of active entities and drafts.

However, it's now also possible to enforce a *split* persistence, which strictly separates active entity data and draft data. This allows, for example, to enable remote entities or entities stored in a different persistence for drafts. In that case set the property `cds.drafts.persistence` to `split`. You can then delegate reading of active entities to a remote system:

java

```
@On(entity = MyRemoteDraftEnabledEntity_.CDS_NAME)
public Result delegateToS4(ActiveReadEventContext context) {
    return remoteS4.run(context.getCqn());
}
```

[Learn more about Reading Drafts.](/docs/java/fiori-drafts#reading-drafts)

### Typed Service Interfaces ​

Besides the [model & data accessor interfaces](/docs/java/cqn-services/persistence-services#staticmodel) for CDS entities and CDS service metadata, the CDS code generator ([cds:generate](../../java/assets/cds-maven-plugin-site/generate-mojo.html)) now creates Java interfaces that reflect the API of the CDS service itself. In particular, the interfaces contain type-safe methods for bound and unbound actions and functions, as alternative to the generic `emit` method:

Given the CDS service definition:

cds

```
service CatalogService {
    entity Books as projection on db.Books {
    } actions {
        action addReview(rating : Integer, title : String, text : String)
          returns Reviews;
    };
    action submitOrder(book : String, quantity : Integer) returns {
        stock : Integer
    };
}
```

The following Java interface is generated:

java

```
@Generated(...)
public interface CatalogService extends CqnService {
  Reviews addReview(Books_ ref, Integer rating, String title, String text);

  SubmitOrderContext.ReturnType submitOrder(String book, Integer quantity);
}
```

The interface allows a simplified handler code:

java

```
@Autowired
CatalogService catalogService;

int stock = catalogService.submitOrder(bookID, 5).getStock();
```

To turn off the generation of typed service interfaces, use the flag `cqnService` of the `generate` goal:

xml

```

 cds.gen

  generate


  false


```

### Technical User Switch ​

Processing business requests frequently requires switching to the technical user of the tenant or technical user of the provider. One example is calling a platform or sidecar service on a technical level. To cover most common scenarios, the `RequestContextRunner` now allows to explicitly switch to a technical user:

- `systemUserProvider()`: Execute code as technical user on behalf of a provider tenant.
- `systemUser()`: Execute code as technical user on behalf of the current tenant.
- `systemUser(tenantId)`: Execute code as technical user on behalf of a specific tenant.

To execute code on behalf of the provider tenant, open a Request Context as follows:

java

```
@Autowired
CdsRuntime runtime;

runtime.requestContext().systemUserProvider().run(reqContext -> {
    ...  // running as provider user (tenant == null)
});
```

The user context is prepared appropriately.

[Learn more about Defining New Request Contexts.](/docs/java/event-handlers/request-contexts#defining-requestcontext)

### Custom EDMX Provider ​

Now, the OData V4 adapter makes use of the new `EdmxV4Provider` interface, which you can use to customize or even override the EDMX metadata being requested:

java

```
@Component
public class CustomEdmxV4Provider implements EdmxV4Provider {

    private EdmxV4Provider standardProvider;

    @Override
 public InputStream getEdmx(String serviceName) {
  return wrapped(standardProvider.getEdmx(serviceName));
 }

 private InputStream wrapped(InputStream edmxStream) {
  ... // adapt stream
 }

    @Override
    public void setPrevious(EdmxV4Provider prev) {
        this.standardProvider = prev;
    }
 ...
}
```

The default provider generates an EDMX stream according to the underlying CDS model of the current tenant. Don't miss to adjust the Etag of the customized EDMX data as well as clients. For example, SAP Fiori relies on it to implement a proper caching.

### SQL Optimization Mode for SAP HANA Cloud ​

The SAP HANA adapter in CAP Java now can generate SQL that is optimized for the new [HEX engine](https://help.sap.com/docs/SAP_HANA_PLATFORM/9de0171a6027400bb3b9bee385222eff/3861d0908ef14e8bbec1d76ea871ac0f.html#sap-hana-execution-engine-(hex)) in SAP HANA Cloud.

[Learn more about the SAP HANA Cloud Mode](/docs/java/cqn-services/persistence-services#sql-optimization-mode)

### Runtime Views Beta ​

When you define a projection on an entity that is mapped to a database table, the CDS compiler creates a corresponding view definition for the database schema. To activate the view definition, a database deployment is required. To avoid *unwanted* schema changes, you can now define a projection as a *runtime view* by annotating it with `@cds.persistence.skip`:

cds

```
entity Books {
  key id    : UUID;
      title : String;
      year  : Int16;
}

@cds.persistence.skip
entity BooksFromYear2000 as projection on Books {
   id, title as name
} where year = 2000;
```

At runtime, CAP Java dynamically resolves queries against this projection without requiring a corresponding view on the database.

[Learn more about Runtime Views.](/docs/java/working-with-cql/query-execution#runtimeviews)

Warning

**IMPORTANT:** This is a beta feature, which is available already now to get early feedback from you. All the [Important Disclaimers and Legal Information](https://help.sap.com/viewer/disclaimer) apply!

### Typed Entity References ​

Use the new `CQL.entity(Class)` method to create *typed* [entity refs](/docs/java/working-with-cql/query-api#entity-refs), which can be used as source in `CqnStatement`s or when calling actions or functions via [service interfaces](#typed-service-interfaces):

java

```
Book_ books = CQL.entity(Book_.class);
Book_ booksFromYear2000 = books.filter(b -> b.year().eq(2000));

// get author names of books from year 2000
Select.from(booksFromYear2000.author()).columns(a -> a.name());

// delete all books from year 2000
Delete.from(booksFromYear2000);
```

[Learn more about Entity References.](/docs/java/working-with-cql/query-api#entity-refs)

### Use CDS Watch with Test Containers ​

The `watch` goal of the `cds-maven-plugin` supports starting applications with test containers. Therefore it uses the [`test-run`](https://docs.spring.io/spring-boot/docs/current/maven-plugin/reference/htmlsingle/#run.test-run-goal) goal of the `spring-boot-maven-plugin`. To enable this feature, add the `-DtestRun` property to the Maven command line: `mvn cds:watch -DtestRun`. In the test environment the Spring Boot application can provide a setup for test-containers as explained in this [guide](https://spring.io/blog/2023/06/23/improved-testcontainers-support-in-spring-boot-3-1).

### Add PostgreSQL and Liquibase support ​

The [`add`](../../java/assets/cds-maven-plugin-site/add-mojo.html) goal of the `cds-maven-plugin` supports adding PostgreSQL and Liquibase features to a CAP Java project.

To add the PostgreSQL feature use the CDS client:

bash

```
cds add postgresql --for postgresql
```

To add the Liquibase feature use the `add` goal of the `cds-maven-plugin`:

bash

```
mvn com.sap.cds:cds-maven-plugin:add -Dfeature=LIQUIBASE -Dprofile=postgresql
```

## Multitenancy ​

### Job Queuing for Subscribe/Unsubscribe/Upgrade ​

The built-in job orchestrator now has an in-memory queuing mechanism. It can be configured using `cds.requires.multitenancy.jobs.queueSize`.

For non-scaled sidecar instances, this avoids tasks being run for the same tenant at the same time.

[Learn more about configuring the SaaSProvisioningService.](/docs/guides/multitenancy/mtxs#saasprovisioningservice)

### Timestamps for Tenant Metadata ​

[Tenant metadata](/docs/guides/multitenancy/mtxs#example-get-tenant-metadata) will now contain the `createdAt` and `modifiedAt` properties. Note, that the `createdAt` field is only filled for newly onboarded tenants.

[Learn more about getting tenant-specific metadata.](/docs/guides/multitenancy/mtxs#get-tenant)
