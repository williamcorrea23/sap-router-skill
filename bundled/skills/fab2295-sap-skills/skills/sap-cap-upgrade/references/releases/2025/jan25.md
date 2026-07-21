<!-- mirror: https://cap.cloud.sap/docs/releases/2025/jan25 -->
<!-- fetched: 2026-05-09T02:26:50.242Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# January 2025 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Prepare for Major Release ​

We understand that you want to be well prepared for changes in our major releases. This section will be a regular part of all upcoming release notes and includes links to all changes relevant to the next major release. As the legacy variants will be removed after the major release, it's crucial that you start adopting and testing these changes now to ensure a smooth transition. Please provide feedback if you encounter any issues or if you're satisfied with the updates.

#### @sap/cds-compiler^6 ​

- New Parser

#### @sap/cds^9 ​

- Upgrade to `@sap/xssec 4`
- OData Containment
- Consolidated Authorization Checks
- @cap-js Database Services
- Protocol Adapters
- Draft Handler Compatibility

## AI-friendly Content in Capire ​

This documentation site now exposes two new files, [llms.txt](/docs/llms.txt) and [llms-full.txt](/docs/llms-full.txt), that help LLMs better understand the content of the pages. You can link it in your prompts, for example, to give more context.

[Learn more about llms.txt](https://towardsdatascience.com/llms-txt-414d5121bcb3)

## CDS Language & Compiler ​

### Reminder: New Parser ​

As already announced with the November '24 release, we're in full swing finalizing the new CDS parser. Replacing the old parser brings significantly reduced installations and faster parsing, as well as improved code completion. While we rolled it out as alpha last November, it's in a Release Candidate status now.

TIP

- The new parser doesn't come with any breaking changes.
- We already started using the new parser by default in all CAP development and tests.
- Current status is Release Candidate → you can, and should start using it.

Roadmap is as follows:

| Date | Status | Remarks |
| --- | --- | --- |
| Nov 24 | Alpha | opt-in usage; default still with old parser |
| Dec 24 | Beta | opt-in usage; default still with old parser |
| Jan 25 | Release Candidate | opt-in usage; default still with old parser |
| May 25 | Release | new parser by default; **w/o fallback to old parser** |

No fallback as of May '25

As there won't be a fallback to the old parser in May anymore, we **strongly recommend testing your projects** already now with the new parser to detect issues before it becomes the default. Set option cds.cdsc.newParser: true in your private `~/.cdsrc.json` to do so on your local machine. If that’s successful, start using it in development and test pipelines of your project.

### Use Enums for Defaults ​

It's now possible to use enum symbols when defining a default value.

cds

```
type Status : String enum { open = 'O'; closed = 'C' };

entity Orders {
  key id : Integer;
  status : Status default #open;
}
```

Enum symbols are going to be supported in more places, for example `where status = #open`, in one of the next releases.

## Node.js ​

### Basic Support for cds.Map ​

The [built-in `cds.Map` type](/docs/cds/types) for storing and retrieving arbitrary structured data is now available. Values of elements with type `Map` are represented as plain Javascript objects.

cds

```
entity Person {
  key ID      : UUID;
      name    : String;
      details : Map;
}
```

Given this CDS model using the new `Map` type for `Person.details`, you can store arbitrary data in `details`:

js

```
await INSERT.into(Person).entries({
  name: 'Peter',
  details: {
    age: 40,
    address: {
      city: 'Walldorf',
      street: 'Hauptstrasse'
    }
  }
})
await SELECT.from(Person).columns('name', 'details')
```

OData v4 only

This feature is available for OData v4 services only.

Temporary Limitations

In this version, `cds.Map` serves as a *dumb* object storage which can be retrieved/written as a whole. Filters as well as partial selects, updates, and deletes are not yet supported.

### Upgrade to @sap/xssec 4 ​

The [authentication strategies](/docs/node.js/authentication#strategies) migrated to the new API of [`@sap/xssec` version 4](https://www.npmjs.com/package/@sap/xssec). Even though there's no change in behavior, you can fall back to the previously used compatibility API of `@sap/xssec` in case of issues with cds.features.xssec_compat = true.

Compatibility as well as support for `@sap/xssec@3` will be dropped with the next major version of `@sap/cds`. **Please upgrade to `@sap/xssec@4` now** if not yet done.

## Java ​

### Predicates as Select List Items ​

Use predicates as select items to evaluate boolean expressions on the database.

java

```
Select.from(BOOKS).byId(17).columns(
  b -> b.year().gt(2000).as("isFrom21stCentury"),
  b -> b.author().name().eq("J.K. Rowling").as("byJKRowling"));
```

This query tests whether a given book was written in the 21st century by J.K. Rowling. The query result maps the aliases `isFrom21stCentury` and `byJKRowling` to boolean values indicating the result of the evaluation. The evaluation is performed on the database without transferring the underlying data to the client.

### Typed Entity References ​

With the new `CQL.entity(Class, ref)` method you can use a generic `CqnStructuredTypeRef` with generated [model interfaces](/docs/java/cqn-services/persistence-services#staticmodel) to build a query in fluent style:

java

```
import static bookshop.Bookshop_.BOOKS; // generated model type
import static com.sap.cds.ql.CQL.entity;

CqnStructuredTypeRef ref; // generic entity reference

Select.from(entity(BOOKS, ref)).where(b -> b.author().name().eq("J.K. Rowling"));
```

### Invoke Functions with Parameters Aliases ​

OData V4.01 allows you to invoke functions using [implicit parameter aliases](https://docs.oasis-open.org/odata/new-in-odata/v4.01/cn04/new-in-odata-v4.01-cn04.html#sec_NewInvokingFunctionswithImplicitPara). This invocation style is now also supported by the CAP Java runtime. The following example illustrates the usage:

http

```
GET sue/stock(id=2)         // traditional syntax
GET sue/stock(id=@ID)?@ID=2 // explicit parameter alias
GET sue/stock?id=2          // implicit parameter alias
```

[Learn more about functions in CAP Java](/docs/java/cqn-services/application-services#actions)

### Expand all Subnodes in Hierarchy ​

In the SAP Fiori Tree Table, you can now expand all children of a selected node:

### Default Runtime Messages Bundle ​

CAP Java has a built-in mechanism to [localize runtime messages](/docs/java/event-handlers/indicating-errors#formatting-and-localization) being sent to the UI, for example, resulting from input validation. Previously, applications had to [provide resource bundle files](/docs/java/event-handlers/indicating-errors) to provide the translations for such standard runtime messages. With this update, CAP Java retrieves translated text from a prepared resource bundle file containing all CAP-supported languages, streamlining the localization process. CAP Java now sends more user-friendly message texts to the UI. This enhancement is designed to improve the user experience, while still maintaining detailed technical information in the logs for debugging purposes. To benefit from this feature, you need to set property [cds.errors.defaultTranslations.enabled: true](/docs/java/developing-applications/properties#cds-errors-defaultTranslations-enabled).

Impact for unit tests

Rewrite unit tests in your application which contain assertions about message texts. Alternatively, use message codes instead.

[Learn more about messages in CAP Java](/docs/java/event-handlers/indicating-errors#messages)

### Authorization Checks On Input Data Beta ​

CAP Java now can also validate input data of `CREATE` and `UPDATE` events with regards to instance-based authorization conditions. Invalid input that does not meet the condition is rejected with response code `400`.

Let's assume an entity `Orders` which restricts access to users classified by assigned accounting areas:

cds

```
annotate Orders with @(restrict: [
  { grant: '*', where: 'accountingArea = $user.accountingAreas' } ]);
```

A user with accounting areas `[Development, Research]` is not able to send an `UPDATE` request, that changes `accountingArea` from `Research` or `Development` to `CarFleet`, for example. Note that the `UPDATE` on instances *not matching the request user's accounting areas* (for example, `CarFleet`) are rejected by standard instance-based authorization checks.

Activate this feature: cds.security.authorization.instanceBased.checkInputData: true.

### cds debug for Java Applications ​

We have extended [`cds debug`](./../2024/nov24#cds-debug) to Java, so that you can easily debug local and remote Java applications. Without an app name, `cds debug` starts Maven with debug arguments **locally**:

```
$ cds debug
Starting 'mvn spring-boot:run -Dspring-boot.run.jvmArguments="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=8000"'
...
Listening for transport dt_socket at address: 8000
...

```

If you add a **remote application** name from the currently targeted Cloud Foundry space, it opens an [SSH tunnel](https://docs.cloudfoundry.org/devguide/deploy-apps/ssh-apps.html) and puts the remote application into debug mode:

```
$ cds debug
...
Debugging has been started.
Address : 8000

Opening SSH tunnel on 8000:127.0.0.1:8000

> Keep this terminal open while debugging.

```

Then connect a debugger in your IDE at the given port.

[Learn more about `cds debug`](/docs/tools/cds-cli#cds-debug)

## Tools ​

### cds watch with Include and Exclude Paths ​

You can now specify which additional paths `cds watch` watches and ignores:

sh

```
cds watch --include ../other-app --exclude .idea/
```

[Learn more about `cds watch` and its options.](/docs/tools/cds-cli#cds-watch)

### Sample Code for TypeScript ​

When executed in a TypeScript project, `cds add sample` now creates proper TypeScript code for the service handlers instead of `.js` files.

This means you can now create a full-fledged TypeScript project with:

sh

```
cds init bookshop --add typescript,sample
```

[Also see the SFlight application on TypeScript.](https://github.com/SAP-samples/cap-sflight)

### Code Formatting in CDS IntelliJ Plugin ​

[SAP CDS Language Support for IntelliJ](https://plugins.jetbrains.com/plugin/25209-sap-cds-language-support) now provides all CDS formatting options for configuration under **Settings > Editor > Code Style > CDS**. The plugin adds any non-default settings to a *.cdsprettier.json* file in the root of a CDS project for consumption by the included LSP server.

Additionally, the most suitable Node.js runtime for the server is now automatically selected from the Node.js interpreters registered under **Settings > Languages & Frameworks > Node.js**.
