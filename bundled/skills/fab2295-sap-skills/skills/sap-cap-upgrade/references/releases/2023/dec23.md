<!-- mirror: https://cap.cloud.sap/docs/releases/2023/dec23 -->
<!-- fetched: 2026-05-09T02:26:36.084Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# December 2023 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Lazy Loading in Change Tracking Plugin ​

The CDS plugin for change tracking now comes with lazy loading of the *Change History* table:

## CDS Language & Compiler ​

### Association-Valued Calculated Elements Beta ​

You can now define a calculated element where the expression is an association with a filter ("association-like calculated element"). The calculated element effectively is an association, where the ON condition is the ON condition of the original association plus the filter condition, combined with `and`. The behavior is similar to [publishing an association with a filter](./sep23#publish-association-with-filter-beta).

Example:

cds

```
entity Authors : managed {
  key ID       : Integer;
  name         : String;
  books        : Association to many Books on books.author = $self;
  availableBooks = books[stock > 0];
}
```

[Learn more about Calculated Elements.](/docs/cds/cdl#calculated-elements)

### Expressions in Annotations Beta ​

We're working on a set of features with the goal to provide full support for [expressions](/docs/cds/cxn#expressions) as "first class" annotation values.

As a first step, you now can provide an expression as annotation value.

Example:

cds

```
entity Orders @(restrict: [
    { grant: 'READ', to: 'Auditor', where: (AuditBy = $user.id) }
  ]) {/*...*/}
```

The expression must be enclosed in parentheses. Supported expressions are the same as in calculated elements. You get code completion, and the compiler checks the syntax and the paths in the expression.

Warning

Runtime support in CAP is today only available for the `where` property of the `@restrict` annotation. Expressions are not supported in other [standard annotations](/docs/cds/annotations#common-annotations). The support will be extended in future releases.

Currently, paths are not rewritten in propagated annotations. In a projection, for example, all elements used in the expression must be propagated without renaming. Thus, for the time being we recommend using the feature mainly in top-level projections. Expressions in OData annotations are not yet handled properly, either.

In later releases we plan to extend the support for expressions in annotation values:

- Properly rewrite paths in propagated annotations.
- Support expressions in OData annotations with improved path handling.

This feature can of course also be used for your custom annotations:

cds

```
@MyCustomAnnotation : (a + b)
entity Foo {
  a : Integer;
  @MyCustomAnnotation : (a + b)
  b : Integer;
}
```

Warning

Expressions as annotation values are released as beta feature. We provide an early preview for the functionality to allow you to experiment with it and provide feedback. The behavior and the CSN representation of paths in propagated annotations will change. The behavior of expressions in OData annotations will change.

[Learn more about Expressions as Annotation Values.](/docs/cds/cdl#expressions-as-annotation-values)[Learn more about support in CAP Java](#support-for-expressions-in-annotations)

## Node.js ​

### Important Changes ❗️ ​

- In rare cases, it was required to oversteer the default VCAP lookup, for example, when multiple instances of the same service are bound to your application.From now on, it's required to explicitly deactivate the default lookup if a different mechanism should be used. Previously, `name` and the default `label` were used individually as lookup in sequential order, which led to erratic behavior.json

```
"cds": {
  "requires": {
    "messaging": {
      "kind": "enterprise-messaging-shared",
      "vcap": {
        "name": "",
        "label": false
      }
    }
  }
}
```

### Type Definitions Are Open Source ​

The [type definitions of the `@sap/cds` APIs](/docs/node.js/typescript#typescript-apis-in-sap-cds) are now maintained on github.com as package [`@cap-js/cds-types`](https://github.com/cap-js/cds-types). The new package allows us to provide fixes faster and in better quality with the help of the CAP community.

No additional dependency needed

You don't need to do anything to get the new package. It's shipped with `@sap/cds`.

However, please make sure to **import types through the [`cds` facade class](/docs/node.js/cds-facade) only**:

TypescriptJavaScriptts

```
import { Request } from '@sap/cds'
import { Request } from '@sap/cds/apis/events'

function myHandler(req: Request) { }
```

js

```
/** @param { import('@sap/cds').Request } req */
/** @param { import('@sap/cds/apis/events').Request } req */

function myHandler(req) { }
```

In this release, we've also fixed a number of type export issues that have forced you to reference the internal files from above.

### Log Formatting in Production ​

We reworked log formatting, especially with regards to naming and defaults. `cds.log` now exports two log formatters, namely `plain` and `json`. The JSON log formatter is the default log formatter in production. Hence, it's no longer necessary to set feature flag `kibana_formatter: true`. You can opt-out of this new default behavior via config `cds.log.format: 'plain'`.

Consequently, `cds add kibana-logging` was deprecated. Please use `cds add application-logging` going forward. Further, this initializer now adds an instance of SAP Application Logging Service with plan `standard` instead of `lite` to your *mty.yaml*. The *lite* service plan isn't meant for production as the quota is not sufficient to avoid dropped logs.

Additionally, we reworked the support for SAP Application Logging Service's custom fields and introduced configurable header value masking.

[For more details, see revised Logging in Production.](/docs/node.js/cds-log#logging-in-production)

### SAPUI5 Mass Edit ​

The ["Mass Edit" feature of SAPUI5](https://sapui5.hana.ondemand.com/sdk/#/topic/965ef5b2895641bc9b6cd44f1bd0eb4d.html) is now supported. It allows modifying multiple rows of a table at the same time without needing to create drafts for each row. The feature must be activated by setting `cds.fiori.bypass_draft = true`.

Warning

Be aware that this feature creates an additional entry point to your application. Custom handlers might require adaptations because the handlers are triggered with partial payloads instead of the complete business object.

### CSRF Token Configuration ​

Fetching CSRF tokens of remote services is configurable at a more fine granular level. If `method` and/or `url` are provided, those are used for fetching the token.

jsonc

```
"cds": {
  "requires": {
    "API_BUSINESS_PARTNER": {
      "kind": "odata-v2",
      "csrf": { // this configuration implies `csrf: true`
        "method": "get",
        "url": "..."
      }
    }
  }
}
```

[Learn more about the fetching CSRF tokens.](/docs/node.js/remote-services#csrf-token-handling)

### Eliminated passport Dependency ​

The generic authentication implementation doesn't rely on the 3rd party dependency `passport` anymore.

You can remove it running `npm uninstall passport` or delete it from the dependencies in the *package.json* by hand.

## Java ​

### Important Changes ❗️ ​

- The free OSS support for Spring Boot `2.7.x` has ended in November. Accordingly, the support for maintenance version CAP Java `1.34.x`, which is based on Spring Boot `2.7`, will be discontinued in May 2024. We strongly recommend migrating to CAP Java 2 as soon as possible. See also CAP Java release schedule.
- The execution order of the system query option `$apply`, with regards to other system query options, has been fixed. In accordance with the specification, the system query option `$apply` is now always evaluated first, then the other system query options are evaluated on the result of `$apply`. Before, it was possible that, for example, `$filter` or `$search` were evaluated before `$apply`.

### Support for Expressions in Annotations ​

With this release, the CDS compiler introduces [expressions in annotations](#expressions-in-annotations-beta).

Custom code can use the [reflection API](/docs/java/reflection-api#get-and-inspect-an-association-element-of-an-entity) to obtain the expression value from an annotation. This allows to use expressions as annotation values in *custom annotations* that are handled by custom code. This example defines a custom annotation `@my.check` to perform a consistency check after an update:

cds

```
annotate Authors with @my.check: (yearOfDeath is null or
                                  yearOfBirth  author.yearOfBirth);
```

Evaluate the annotation's expression value in a generic handler:

java

```
@After
public void checkAfterWrite(CdsUpdateEventContext ctx) {
   CdsEntity target = ctx.getTarget();

   CqnExpression xpr = target.getAnnotationValue("my.check", CQL.TRUE);
   ctx.getResult().stream().forEach(row -> {
      CqnSelect query = Select.from(row.ref()).where(xpr.asPredicate()).limit(1);
      if (db.run(query).first().isEmpty()) {
        throw new ServiceException(BAD_REQUEST, "check failed");
      }
   });
}
```

Warning

Besides in `@restrict`, CAP Java doesn't support using expressions in standard annotations.

[Learn more about expressions in annotations.](/docs/cds/cdl#expressions-as-annotation-values)

### Update with Expressions ​

The `Update` now supports expressions using the new `set` method, for example, to decrease the stock of Book 101 by 1:

java

```
Update.entity(BOOKS).byId(101).set("stock", CQL.get("stock").minus(1));
```

[Learn more about Update with Expressions.](/docs/java/working-with-cql/query-api#update-expressions)

### On-the-fly Localization of EDMX ​

Internationalization of an SAP Fiori elements UI requires that the server provides translated EDMX metadata documents. So far, localized EDMX files were created by `cds build` or retrieved from the MTX model provider API and served by the runtime as is.

This approach resulted in EDMX versions for multiple languages being cached by the runtime, which consumed significant memory.

Now, the `cds build` and MTX model provider API provide a nonlocalized EDMX template as well as a text bundle with the translated texts of each locale. If an OData `$metadata` request is served, the runtime mixes the translations into the EDMX on the fly and streams the response. For now, you need to enable this feature in the *application.yaml* with the configuration `cds.odata-v4.lazy-i18n.enabled: true`. It requires `@sap/cds-dk` >= `7.4.0` and `@sap/cds-mtxs` >= `1.12.0`.

The `cds build` currently creates localized and nonlocalized EDMX files as static resources by default. To save disk space, the creation of translated EDMX files can be disabled with the `cds build` option `--opts contentLocalizedEdmx=false`

Tip

On-the-fly localization of EDMX is only available with OData V4.

### RegEx Pattern Matching ​

Use the new `matchesPattern` predicate to test if a string value matches a given regular expression. The following query returns books with a title that starts with the letter "C" and ends with the letter "e":

java

```
Select.from(BOOKS).where(t -> t.title().matchesPattern("^C\\w*e$"));
```

You can also use `matchesPattern` with `CQL` in [tree-style](/docs/java/working-with-cql/query-api#cql-helper-interface):

java

```
Select.from("bookshop.Books").where(CQL.matchesPattern(CQL.get("title"), "^C\\w*e$"));
```

Furthermore, you can now use the `matchesPattern` function [in OData v4](https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part2-url-conventions.html#_Toc23836468):

txt

```
GET Books?$filter=matchesPattern(title, '^C\\w*e$')
```

Possible performance penalty

Pattern matching with regular expressions can result in significant performance degradation, if applied on large entity sets.

[Learn more about the matchesPattern predicate.](/docs/java/working-with-cql/query-api#matches-pattern)

### Auditlog Premium Plan ​

Feature `cds-feature-auditlog-v2` now supports public service plan `premium` of the Audit Log Service. External customers can consume it by binding the CAP application to the service instance of Audit Log and adding the following dependency to the service *pom.xml*:

xml

```

 com.sap.cds
 cds-feature-auditlog-v2

```

[Learn more in the Audit Log documentation](/docs/java/auditlog#handler-v2)

### Open Telemetry Support ​

CAP Java now provides end-to-end observability based on [Open Telemetry](https://opentelemetry.io/) format. Collected metrics, traces, and logs can be exported to [SAP Cloud Logging service](https://discovery-center.cloud.sap/index.html#/serviceCatalog/cloud-logging) and/or Dynatrace.

On SAP BTP, Cloud Foundry environment, configuration is simplified as shown as follows. Bind the application to a cloud logging service instance with Open Telemetry ingestion activated:

sh

```
cf create-service cloud-logging standard cls -c '{"ingest_otlp": {"enabled": "true"}}'
```

Don't forget to add the logging extension library for Open Telemetry in your service *pom.xml*:

xml

```

  com.sap.hcp.cf.logging
  cf-java-logging-support-opentelemetry-agent-extension
  ${logging.support.version}

```

Finally, configure the Open Telemetry Java agent from the buildpack as well as the logging extension library in the environment of the CAP application:

yaml

```
JBP_CONFIG_JAVA_OPTS:
  from_environment: false
  java_opts: >
    -javaagent:META-INF/.sap_java_buildpack/otel_agent/opentelemetry-javaagent.jar
    -Dotel.javaagent.extensions=BOOT-INF/lib/cf-java-logging-support-opentelemetry-agent-extension-.jar
```

Beside automatic instrumentations given by the Java agent, CAP Java additionally does the following:

- Adds nested spans for Request and ChangeSet contexts.
- Handles thread propagation of spans out of the box.

[Learn more about observability with Open Telemetry.](/docs/java/operating-applications/observability#open-telemetry)

### Miscellaneous ​

- The code generator supports annotating services with `@cds.java.name` to customize the name of the corresponding generated service interface.
- Draft garbage collector and outbox collector introduced model loading bursts in MTX sidecar as all subscriber tenants have been processed periodically. This has been improved so that such CPU overload situations are avoided.
