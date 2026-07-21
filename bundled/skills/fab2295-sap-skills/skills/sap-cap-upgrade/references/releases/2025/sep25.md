<!-- mirror: https://cap.cloud.sap/docs/releases/2025/sep25 -->
<!-- fetched: 2026-05-09T02:26:54.807Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# September 2025 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Node.js ​

### Translated Error Messages ​

CAP Node.js now provides default translations for annotation-based validation errors in all CAP-supported languages. This enhancement allows the runtime to send more user-friendly message texts to the UI, streamlining the user experience for all CAP applications.

As part of this update, we streamlined the error codes, renaming `ASSERT_NOT_NULL` to `ASSERT_MANDATORY` to better reflect its purpose. For custom translations, use the previous error code `ASSERT_NOT_NULL`. Additionally, use the compatibility flag cds.features.compat_assert_not_null:true to restore compatibility until the next major version.

Impact on Tests

If your application's unit tests contain assertions about message texts, please update them to use error codes instead.

[Learn more about error handling in Node.js.](/docs/node.js/events#req-reject)[Learn more about internationalization in Node.js.](/docs/node.js/cds-i18n)

### Simplified Support for Streaming ​

The new QL API [`SELECT ... .stream ()`](/docs/node.js/cds-ql#stream) returns the data from the database as a raw stream. See the following snippet in the context of our new [`@capire/xtravels`](https://github.com/capire/xtravels) sample:

js

```
this.on ('exportJSON', async req => {
  let query = cds.ql (TravelsExport.query)
  let stream = await query.localized.stream()
  return req.reply (stream, { filename: 'Travels.json' })
})
```

### Revised Fiori Support ​

We have revised the implementation and documentation of our support for Fiori, specifically in the area of handler registration. The documentation now takes a use-case-based approach, enabling you to more quickly identify the hook you need to implement.

In summary, you can register handlers for the following draft-specific events:

js

```
srv.on('NEW',     MyEntity.drafts, /*...*/)
srv.on('PATCH',   MyEntity.drafts, /*...*/)
srv.on('SAVE',    MyEntity.drafts, /*...*/)
srv.on('EDIT',    MyEntity,        /*...*/)
srv.on('DISCARD', MyEntity.drafts, /*...*/)
```

[Learn more about serving Fiori UIs.](/docs/node.js/fiori)

### Combined Input Validation ​

Annotation-based input validation now runs together with custom validations executed in the `before` phase, so end users experience a single validation step. Previously, custom validations ran only after annotation-based validation passed successfully.

If the `@mandatory` annotation is violated, the input is still rejected immediately because type safety cannot be guaranteed.

Warning

If your validation depends on the input already being validated, for example, a string's format or a number's range, use an `on` handler to run your logic and then delegate to the generic handler via the `next` parameter.

[Learn more about annotation-based input validation.](/docs/guides/services/constraints)[Learn more about registering `on` handlers.](/docs/node.js/core-services#srv-on-request)

## Java ​

### JDK 25 Compliance ​

CAP Java is successfully tested with the brand new [JDK 25](https://openjdk.org/projects/jdk/25/) which is an LTS version.

We recommend configuring [SapMachine](https://sap.github.io/SapMachine/) 25 JDK (respective JRE) with the [SAP Java buildpack](https://help.sap.com/docs/btp/sap-business-technology-platform/developing-java-in-cloud-foundry-environment) as shown in the example (`mta.yaml`):

yaml

```
modules:
  - name: MyCAPJavaApp
    type: java
    path: srv
    parameters:
      ...
      buildpack: sap_java_buildpack_jakarta
    properties:
      JBP_CONFIG_COMPONENTS: "jres: ['com.sap.xs.java.buildpack.jre.SAPMachineJRE']"
      JBP_CONFIG_SAP_MACHINE_JRE: '{ version: 25.+, use_offline_repository: false }'
```

Current `sap_java_buildpack_jakarta` does not yet officially support JDK 25 and therefore has some limitations:

- Public Internet access is required to download the JDK (no offline mode).
- Only Java Main deliveries are supported (no restriction for Spring Boot apps).

Some highlights of the new JVM:

- Scoped values to safely share data within the methods calls in the same thread without resorting to method parameters.
- Flexible Constructor Bodies allow to write constructors in a more streamlined way.
- Compact Object Headers show 22% less heap space in SPECjbb2015 benchmark and JSON parser benchmark runs in 10% less time.

#### cds-services-archetype ​

The `cds-services-archetype` supports the creation of new CAP Java projects with JDK 25 as target runtime. This can be achieved with the command line option `-DjdkVersion=25`.

Currently create new projects with JDK 17 or 21

There is currently an issue with the official [`maven-archetype-plugin`](https://maven.apache.org/archetype/maven-archetype-plugin) itself, it doesn't work with JDK 25. Therefore, you need to use JDK 17 or 21 to create a CAP Java project. After the creation you have to switch the JDK to 25 as target runtime to build and run the newly created CAP Java project.

### Aggregating over Associations Beta ​

You can now aggregate values of associated entities directly in your CQL queries by using the aggregation methods `min`, `max`, `sum`, and `count` on associations with to-many relationships.

Example:

java

```
Select.from(ORDERS).columns(
      o -> o.orderNo(),
      o -> o.date(),
      o -> o.items().sum(i -> i.amount()).as("total"));
```

This query selects `orderNo` and `date` from Orders and additionally sums up the amounts of the associated items, which it returns as "total".

[Learn more about Aggregating over Associations.](/docs/java/working-with-cql/query-api#aggregating-associations)

### Streamlined CDS Models from Maven Dependencies ​

So far, CDS models imported from Maven dependencies were only available in the scope of the Maven module that declared the dependency to the reuse package. This prevented, for example, CDS files in the `db` directory from accessing models from dependencies defined in the `srv` module.

Now CDS models from reuse packages are available to the whole CAP project by default. They resolve to `target/cds` instead of `srv/target/cds`. This ensures that you can consistently import them from all CDS files in the project using proper `using` declarations.

Warning

If you have declared `using` statements, leveraging file paths like `using '../srv/target/cds//'`, make sure to switch to the correct syntax `using '/'`.

If you need to resolve reuse modules only within the scope of the declaring module, you can opt out of this new behavior. Configure the `to` property of the `resolve` goal:

xml

```

  com.sap.cds
  cds-maven-plugin
  ${cds.services.version}

    ...

      cds.resolve

        resolve


        ${project.build.directory}


    ...


```

### Miscellaneous ​

#### Streamlined Ordering of Security Configs ​

Spring Security configurations provided by CAP Java now correctly use the `@Order` annotation by placing it on the `SecurityFilterChain` bean method instead of the `Configuration` class:

java

```
@Configuration
@EnableWebSecurity
public class ActuatorSecurityConfig {

  @Bean
  @Order(1)
  public SecurityFilterChain appSecurityConfig(HttpSecurity http) {
    // ...
  }
}
```

Using a proper `@Order` makes it easier for you to configure custom security configurations that the system evaluates with the correct precedence.

Warning

As this was wrongly done in all our samples, documentation and framework code, please double-check any custom security configurations you have defined for the same mistake.

#### Setting Application UI URL Programmatically ​

Until now, configuration defined the *application UI URL* that the system returns upon a new tenant subscription.

Now, however, you can programmatically override the returned default *application UI URL* by implementing an `On` handler for the `APP_UI_URL` event of the `DeploymentService`.

The `AppUiUrlEventContext` interface encapsulates that event and gives you access to the `tenant`, `subdomain` and subscription `options` from the *SaaS registry* or *Subscription Manager* callback. You can use these to define the *application UI URL* you want to return to the subscriber as shown in the following example:

java

```
@ServiceName(DeploymentService.DEFAULT_NAME)
public class MyCustomDeploymentServiceHandler implements EventHandler {

  @On
  public String onAppUiUrl(AppUiUrlEventContext context) {

    String tenant = context.getTenant();                   // the tenant id
    String subdomain = context.getSubdomain();             // the subdomain
    Map options = context.getOptions();    // the subscription options

    return "https://" + tenant + "." + subdomain + "/" + options.get("subscriptionAppPlan");
  }

}
```

#### Disable Draft Garbage Collection for Entity ​

The new annotation `@odata.draft.gc: false` can be used to disable the Draft Garbage Collection for a particular entity.

cds

```
@odata.draft.gc: false
entity DraftEnabled {
  ...
}
```

[Learn more about garbage collection for Drafts.](/docs/java/fiori-drafts#draft-gc)

#### Simplified Bound Action Calls in OData ​

For convenience, the CAP Java runtime now allows to call bound actions/functions without prefixing them with the service name.

#### Performance ​

The CAP Java runtime now optimizes statement normalization to improve efficiency and reduce resource consumption.

## Tools ​

### Important Changes ❗️ ​

#### Edm.String now Becomes CDS String in cds import ​

`cds import` for EDMX files now maps `Edm.String` fields without length restriction to CDS's `String` (instead of `LargeString` as before). If you reimport and redeploy OData APIs, this leads to database type changes with [default lengths](/docs/cds/cdl#built-in-types). Make sure this still fits your data. In case of issues, change the type length or use `LargeString` again.

### cds add app-frontend ​

The new [SAP BTP Application Frontend](https://help.sap.com/docs/application-frontend-service) service is now easy to integrate:

sh

```
cds add app-frontend
```

**Note**: Support for the service is currently limited to single-tenant applications.

As the successor to the SAP BTP HTML5 Application Repository, it offers new features such as built-in versioning and delivers a simpler, more streamlined development experience for frontend applications.

[Read the blog post: “Introducing Application Frontend Service”](https://community.sap.com/t5/technology-blog-posts-by-sap/introducing-application-frontend-service/ba-p/14091408)

[Read the blog post about the `afctl` tool.](https://community.sap.com/t5/technology-blog-posts-by-sap/simple-ui-applications-with-application-frontend-service/ba-p/14096009)

### Annotations with Better Editor Support ​

The editor enhances code completion and diagnostics for annotating annotation values to follow [the latest guidelines](/docs/guides/protocols/odata#annotating-annotations). Here's a quick overview of the enhancements:

- Offers suggestions for annotations using shortcut syntax in code completion lists (previously only record properties were provided).
- No more suggestions with deprecated `$value` syntax in code completion lists.
- Diagnostics now show warning messages for the deprecated `$value` syntax.

## SAP Integration Suite, Advanced Event Mesh GA ​

[SAP Integration Suite, advanced event mesh](https://www.sap.com/products/technology-platform/integration-suite/advanced-event-mesh.html) enables applications to engage in real-time asynchronous communication across distributed environments using a fully managed cloud service designed for event-driven architectures.

After a successful test and evaluation phase, both open-source plugins, [`@cap-js/advanced-event-mesh`](https://github.com/cap-js/advanced-event-mesh) and [`com.sap.cds:cds-feature-advanced-event-mesh`](https://github.com/cap-java/cds-feature-advanced-event-mesh), are now **generally available** (GA). The most notable addition is the support for cross-subaccount broker validation.

[Find more details in the Plugins page entry.](/docs/plugins/index#advanced-event-mesh)

## capire Updates ​

### Java CQL Query API Enhancements ​

New `concat` function usage documentation for building more complex string concatenation operations in Java CQL queries, improving query composition capabilities.

[Learn more about Java CQL Query API.](/docs/java/working-with-cql/query-api#string-expressions)

### Java Security Configuration Improvements ​

Updated security configuration patterns with better guidance for custom Spring Security setups and improved IAS authentication flows documentation.

[Learn more about Java security.](/docs/java/security#custom-spring-security-config)

### Outbox Pattern with Shared Database ​

New documentation on implementing outbox pattern workarounds when using shared databases, providing solutions for distributed transaction challenges.

[Learn more about Java outbox pattern.](/docs/java/outbox#outbox-for-shared-databases)

### Extensibility and Composition Improvements ​

Enhanced Maven dependency resolution for CDS models, making reuse packages globally available across project modules and improving extensibility patterns.

[Learn more about extensibility and composition.](/docs/guides/integration/reuse-and-compose#importing-from-maven-dependencies)

### ...and more ​

- Improved multitenancy documentation with better deployment hints.
- Enhanced error handling documentation with security warnings.
- Updated Spring Boot integration samples and configurations.
- Fixed Node.js database connection pool configuration documentation.
- Improved cds.error() API documentation with HTTP status codes.
- Updated Java properties configuration examples.
- Enhanced Cloud Foundry deployment documentation.
- Updated about section with AI-related content.
