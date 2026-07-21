<!-- mirror: https://cap.cloud.sap/docs/releases/2021/aug21 -->
<!-- fetched: 2026-05-09T02:26:24.966Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# August 2021 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtx?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Multitenancy ​

### Handlers for Asynchronous Subscription ​

Tenant creation and deletion are now called via CDS service `TenantPersistenceService`, that applications can add handlers for:

cds

```
@protocol:'rest'
service TenantPersistenceService {
    type JSON {
        // any json
    }

    action createTenant(tenantId: UUID, subscriptionData: JSON) returns String;
    action deleteTenant(tenantId: UUID);
}
```

[Learn more about the handler for asynchronous provisioning.](/docs/guides/multitenancy/old-mtx-apis#event-handlers-for-cds-mtx-provisioning)

### Correlation IDs for Tenant Operations ​

The propagation of correlation IDs to asynchronous tenant operations is now fixed. The correlation IDs in the log entries of asynchronous tenant operations now correctly match the correlation IDs of the request that triggered the operation.

## New Capire Docs ​

- CAP Release Schedule → This schedule gives a reliable basis for planning adoption accordingly.New major versions of CAP will be released every 12 months, in April 2021, 2022, and so forth. Active CAP-based projects are strongly recommended to adopt new majors as soon as possible, as former releases will receive critical bug fixes only.

- Minimalistic Logging Facade Beta for Node.js → Learn more about out-of-the-box log formatting.
- Best Practices for Node.js - Error Handling → This section gives a brief overview of common best practices.
- Media Type Processing for CAP Java → This section describes how to process media streams in a custom event handler.
- Testing CAP Java applications → This section describes some best practices and recommendations for testing CAP Java applications.
- Observability for CAP Java → Presents a set of recommended tools that help to understand the current status of running CAP services.

## Node.js Runtime ​

This release focuses on quality and incremental steps towards larger feature packages.

### Important Changes ❗️ ​

You should take notice of the following changes, which **may** affect your project:

- Computed values are preserved during draft activate. That is, the values of properties that are annotated with `@Core.Computed` do not need to be recalculated when activating a draft, but are copied from the draft persistence to the active persistence. This change can be deactivated during a two-month grace period through compatibility feature flag `cds.env.features.preserve_computed = false`.

### Minor Additions ​

- Support for passing arguments for action and function implementations as objects.
- Support for OData's omit-values preference in `prefer` header.
- Support for OData's ReadByKeyRestrictions annotation.

## CDS Editors Speedup ​

The following applies to CDS editors in SAP Business Application Studio and Visual Studio Code.

### New Default Validation Mode: ActiveEditorOnly ​

SAP Business Application Studio and VS Code have a new default CDS validation mode, *ActiveEditorsOnly*.

It further reduces necessary compilations to improve responsiveness. The new mode only keeps track of the active editor in focus. Other files, even open visible ones (split tabs), are first revalidated once they get focus again.

The new mode needs special client support, thus for other IDEs the default remains *OpenEditorsOnly*.

[Learn more about this and other editor settings.](/docs/tools/cds-editors#settings)

### Graphical Dependency Analysis ​

A new command *Visualize CDS file dependencies* is available in SAP Business Application Studio and VS Code to get a better understanding of large models, for example, with hundreds of model files. Hovering over a node will show the number of files involved and the combined size of all involved files to get a rough understanding about the complexity and the compilation speed.

Use the command from the context menu on a folder or CDS file.

[Learn more about this and other commands from the editor.](/docs/tools/cds-editors#commands)

## CDS Language & Compiler ​

### Extend Array-Like Annotation Values ​

Usually annotations in an `extend` overwrite already existing annotation values. If an existing annotation has an array-like value, use the new ellipsis syntax to **add** values into the array:

cds

```
extend Books with @UI.LineItem: [
  ...,  //> represents the existing array entires
  { Value: ISBN },
  { Value: pages }
] {
  ISBN : String;
  pages : Integer;
}
```

[Learn more about Extend Array Annotations.](/docs/cds/cdl#extend-array-annotations)

### Doc Comments Are Translated to SAP HANA COMMENT ​

When generating output for deployment to SAP HANA, any entity's doc comments

cds

```
/**
 * I am the description for "Employee"
 */
entity Employees { ... }
```

are now translated to the HANA `COMMENT` feature:

sql

```
CREATE TABLE Employees (...) COMMENT 'I am the description for "Employee"'
```

[Learn more about Doc Comments.](/docs/cds/cdl#doc-comments)

## Java SDK ​

### Important Changes ❗️ ​

#### CDS Compiler v2 Enabled by Default ​

As of version 1.18.0, the CAP Java SDK uses the *cds-dk 4* and the *CDS Compiler v2*. This applies for newly generated projects but also for existing projects that do not use a fixed version of the *cds-dk* in their *pom.xml*.

[Learn more about using a specific cds-dk version.](/docs/java/developing-applications/building#cds-maven-plugin)

[Learn more about upgrading to Compiler v2.](/docs/cds/compiler/v2)

### Convenient Debug Logging with Spring Log Groups ​

The CAP Java SDK now defines [Spring Boot Log Groups](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.logging.log-groups) with logical names that you can use to turn on debug logging for certain areas of the CAP runtime. For example, to turn all logs regarding generated SQL statements, configure:

yaml

```
logging.level.com.sap.cds.persistence.sql: DEBUG
```

in your application configuration.

[Learn more about the available logger groups and how to toggle loggers dynamically in Java Observability.](/docs/java/operating-applications/observability)

### H2 Database by Default ​

Newly created projects now use the [H2 database](/docs/java/cqn-services/persistence-services#h2) by default. H2 is the default database used in Spring Boot and thus requires very little configuration.

### Returning Multiple Error Messages ​

The CAP Java SDK now collects all error messages for automatic [input validation](/docs/guides/services/constraints) using the Messages API and does no longer abort the request processing on the first validation error. Applications can contribute additional errors using the [Messages API](/docs/java/event-handlers/indicating-errors#messages) in the `Before` phase and are no longer required to explicitly call [`throwIfError()`](/docs/java/event-handlers/indicating-errors#throwing-a-serviceexception-from-messages) in that case.

### Session Context Variables in ON-conditions ​

You can now use session context variables such as `$user.id`, `$user.locale`, and `$now` in ON-conditions of associations.

### Updatable Views ​

Insert and update operations now also work on views having literals in the projection.

### Structured Elements ​

Simple insert and select operations are now supported on structured elements.
