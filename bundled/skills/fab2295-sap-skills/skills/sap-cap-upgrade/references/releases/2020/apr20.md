<!-- mirror: https://cap.cloud.sap/docs/releases/2020/apr20 -->
<!-- fetched: 2026-05-09T02:26:20.359Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# April 2020 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Docs and Samples ​

### Tests Added to cap/samples ​

We added a few tests to [cap/samples](https://github.com/SAP-samples/cloud-cap-samples/tree/master/test), which we use to qualify our content in there. In addition, you may take these as blueprints and best practices how to add tests to your projects, as well as samples in itself how to use certain CAP features, such as [`cds.ql` in Node.js](https://github.com/SAP-samples/cloud-cap-samples/tree/master/test/cds.ql.test.js). Just a few notes about these tests:

- They use `chai` as an assertions library.
- They run with both, Mocha and Jest as test runners.
- You can run the tests using the provided npm scripts:

sh

```
npm run jest  # or...
npm run mocha test/.js
```

Setup: We leave the choice of Mocha or Jest to you. Install them globally in order to run the tests, for example: `npm i -g mocha`. Note: In contrast to Jest, Mocha doesn't isolate tests, so you can't run them all at once but may need to run them individually.

### New and Revised Sections and Guides ​

New Guides and Sections:

- Cookbook > Providing Services > Implicit Pagination
- Cookbook > Providing Services > Input Validation
- CDS > Schema Notation > Imports
- Java > Executing CQN Queries > Pessimistic Locking
- Java > Query Builder API > Select > Ordering and Pagination > Write Lock
- Node.js > ETag
- Advanced > Deploying to Cloud > Deploy using MTA

## Command Line ​

New Node.js method `cds.compile.cdl()` allows compiling CDS sources in-process.

### cds watch <package name> ​

Use package names as arguments with `cds watch`/`run`/`serve`, for example:

sh

```
cds watch @capire/bookshop
```

### cds version -ls ​

Use `cds version --npm-list` (or `cds v -ls` for short) to print an `npm ls` subtree, for example:

```
$ cds version -ls
npm ls --depth 11 | grep @sap/cds
├─┬ @sap/cds 3.33.4 -> ~/cap/cds
│ ├── @sap/cds-compiler 1.26.1 -> ~/cap/compiler deduped
│ ├── @sap/cds-foss 1.2.0 -> ~/cap/foss deduped
│ ├── @sap/cds-reflect 2.10.2 -> ~/cap/core deduped
│ └── @sap/cds-runtime 1.0.5 -> ~/cap/runtime deduped
├─┬ @sap/cds-compiler 1.26.1 -> ~/cap/compiler
├─┬ @sap/cds-dk 1.8.1 -> ~/cap/cds-dk
│ ├── @sap/cds 3.33.4 -> ~/cap/cds deduped
│ ├── @sap/cds-foss 1.2.0 -> ~/cap/foss deduped
├─┬ @sap/cds-foss 1.2.0 -> ~/cap/foss
├─┬ @sap/cds-mtx 1.0.13 -> ~/cap/mtx/mtx-agent
├── @sap/cds-reflect 2.10.2 -> ~/cap/core
├─┬ @sap/cds-runtime 1.0.5 -> ~/cap/runtime
│ ├── @sap/cds-foss 1.2.0 -> ~/cap/foss deduped
├─┬ @sap/cds-test 0.0.2 -> ~/cap/tests
│ │ │ ├── @sap/cds 3.33.4 -> ~/cap/cds deduped
│ │ │ ├── @sap/cds 3.33.4 -> ~/cap/cds deduped
│ │ │ ├── @sap/cds 3.33.4 -> ~/cap/cds deduped
│ ├── @sap/cds 3.33.4 -> ~/cap/cds deduped

```

### cds build --log-level ​

With `cds build --log-level` and `cds compile --log-level`, you define which messages you want to see.

## CDS Language & Compiler ​

### Arrayed Types ​

Introduced keyword `many` as a substitute for `array of`. Furthermore, such arrayed types are now also supported on the database side - they're represented as elements of type `cds.LargeString`.

[Learn more in CDS > Definition Language > Arrayed Types](/docs/cds/cdl#arrayed-types)

### Parsed-only Output ​

The `cds compile` option `--parse` provides minimal, parsed-only CSN output. Minimal meaning as close to the CDL source as possible, that means no generation of fields or entities, no resolving of imports, no applying extensions, no annotation propagation, etc. Consequently, many integrity checks are also not run because they require one of the steps above.

The following example illustrates this nicely:

cds

```
using Bar from './bar';
namespace parsecdl;

entity Foo as select from Bar:toBar { *,
  unchecked
};

extend Bar with {
  add: Integer;
  not_expanded: localized String;
}
```

The CDL from above, compiled with `--parse` yields the following CSN:

json

```
{
  "namespace": "parsecdl",
  "requires": [ "./bar" ],
  "definitions": {
    "parsecdl.Foo": {
      "kind": "entity",
      "query": {
        "SELECT": {"from": {"ref":["Bar","toBar"]},
          "columns": [ "*", {"ref":["unchecked"]} ]
        }
      }
    }
  },
  "extensions": [
    { "extend": "Bar",
      "elements": {
        "add": { "type":"cds.Integer" },
        "not_expanded": { "localized":true, "type":"cds.String" }
      }
    }
  ]
}
```

As you've seen in the sample, `localized` isn't processed, imports aren't resolved, the view isn't validated (`Bar` might not have a field `unchecked`), and more.

### UI Annotations for Draft Administrative Data ​

All elements of `DraftAdministrativeData` are now annotated with `@Common.Label` and a translated text. In addition, the elements `DraftUUID`, `DraftIsCreatedByMe`, and `DraftIsProcessedByMe` are annotated with `@UI.Hidden`.

## Node.js Runtime ​

### Important Changes❗️ ​

If a [SELECT query](/docs/node.js/cds-ql#select-from) contains columns or column aliases with the same name, the query is rejected.

In a [SELECT query](/docs/node.js/cds-ql#select-from), that uses the object notation in `.where` statements, functions aren't allowed anymore.

The result of an OData `GET` request is now ordered by the keys of the returned entities by default if the client doesn't request a specific sorting (for example, through `$orderby`, `@cds.default.order`, or `@odata.default.order`).

### Value Range Annotations for OData ​

The [value range annotations](/docs/guides/services/constraints) [`@assert.format`](/docs/guides/services/constraints#assert-format) and [`@assert.range`](/docs/guides/services/constraints#assert-range) are now implemented for the OData protocol. The usage of `@assert.enum` is deprecated. Switch to `@assert.range enum`.

### @assert.integrity ​

Associations *to-one*, annotated with [`@assert.integrity: false`](/docs/guides/services/constraints#assert-target), are ignored on integrity checks.

### Implicit Pagination ​

The results of READ requests are automatically truncated at 1000 records. With server-side pagination, you can configure the default and max page size globally, on service, and on entity level.

[For more details, see Providing Services > Implicit Pagination.](/docs/guides/services/served-ootb#implicit-pagination)

### Changed Draft Locks Timeout ​

Draft locks now expire after a default timeout of 15 minutes. The locked entity can be reclaimed by other users after that timeout. The timeout duration is configurable via the application configuration property `cds.drafts.cancellationTimeout`.

### Miscellaneous ​

If there's no custom handler implemented for entities annotated with `@cds.persistence.skip` requests to it fail with HTTP code 501.

## Java Runtime ​

### Important Changes ❗️ ​

- Saving a draft now triggers an UPDATE event instead of an UPSERT event that was used in previous versions. Applications need to adopt this new behavior, see following section Fiori Drafts below for more information.
- OData system query parameter `$count` now generates a CQN query using the inlineCount option in CQL. Unlike before, a single `READ` event is now emitted. Previously, `$count` triggered invocation of two event handlers, as an additional CQL query was executed.

### Customizing Error Messages ​

Customize and translate error messages that are thrown by the CAP Java runtime in several ways:

- Use the following application configuration property to prevent that the technical error message is transferred to the application frontend:yaml

```
cds.errors.stackMessages.enabled: false
```

This setting doesn't affect application logging.
- Use the following application configuration property to log more details when the CAP Java runtime throws exceptions, such as parameters contained in the EventContext:yaml

```
cds.errors.extended: true
```
- Each error now has a dedicated error status, refer to the following enum to get a full list of possible errors:yaml

```
com.sap.cds.services.utils.CdsErrorStatuses
```
- Like with customer error messages, error messages thrown by the stack can be localized by means of so called message bundles. See Java > Indicating Errors > Formatting and Localization for more details. For example, to translate the text for the error message with error code 400002 (which is an invalid request) to German, you could define:txt

```
400002=Der Wert '{}' ist ungültig
```

### Concurrency Control Using ETags ​

Optimistic concurrency control is now supported by means of ETags. See [Cookbook > Providing Services > Concurrency Control](/docs/guides/services/served-ootb#etag) for more details.

### Fiori Drafts ​

#### Changes in Draft Orchestration ​

When saving a draft, this triggers now an UPDATE event. Previously, an UPSERT event was used that isn't able to perform sparse updates and maintain the `created-at` timestamp correctly. Applications need to adapt the new behavior as follows:

All event handlers reacting when a draft is saved and need to be registered on the UPDATE event, for example:

Before:

java

```
@Before(event = { CdsService.EVENT_CREATE, CdsService.EVENT_UPSERT })
public void validateOrders(Stream orders) {
   ...
}
```

After:

java

```
@Before(event = { CdsService.EVENT_CREATE, CdsService.EVENT_UPSERT, CdsService.EVENT_UPDATE })
public void validateOrders(Stream orders) {
    ...
}
```

If your event handler signature contains a `CdsUpsertEventContext` type signature, change that type to `CdsUpdateEventContext` or simply `EventContext`.

In addition, verify that no other event handlers are registered on the UPDATE event to make sure that they aren't triggered unintentionally. See [Java > Service Provisioning API > Implementing Event Handlers > Draft Event Flow](/docs/java/fiori-drafts#draftevents) for more details.

#### Changed Draft Locks Timeout ​

Draft locks now expire after a default timeout of 15 minutes. The locked entity can be reclaimed by other users after that timeout. The timeout duration is configurable via the application configuration property `cds.drafts.cancellationTimeout`.

#### New DRAFT_CREATE Event ​

Introduced a new DRAFT_CREATE event, which is triggered when creating either an empty draft or a draft from an existing entity. This way it's possible to step in and validate data before the draft entity is created.

### Accessing XSUAA JWT Token Properties ​

It's now possible to conveniently access properties of JWT tokens issued by XSUAA using `cds-feature-xsuaa`, for example:

java

```
import com.sap.cds.feature.xsuaa.XsuaaUserInfo;

@Autowired
private XsuaaUserInfo xsuaaToken;

@Before(...)
public void eventHandler(EventContext event) {
	logger.info("Request user: {} {} email: {}",
			xsuaaToken.getGivenName(),
			xsuaaToken.getFamilyName(),
			xsuaaToken.getEmail() );
}
```

### CDS Query Builder ​

- Inline counts are now supported when defining CQN queries. For example, `Result result = dataStore.execute(Select.from(BOOK).limit(2).inlineCount());` will deliver two book entries and additionally the number of all books. The `CqnSelect.hasInlineCount()` method indicates if an inline count will be returned.
- An `exists` subquery predicate can now be used `Select.from(EMPLOYEE).columns(c -> c.id(), c -> c.name()) .where(e -> e.exists(outer -> Select.from(CAR).where(c -> c.owner().id().eq(outer.id()).and(c.licensePlate().eq("XYZ123")))))` in filters of CQL queries. See Java > Query Builder API > Predicates, for more details.
- Write locks can be initiated by using pessimistic locking, for example, `Select.from("bookshop.Books").where(b -> b.get("ID").eq(1)).lock(5);` a lock timeout can be defined (otherwise DB specific). For more details, see Java > Query Builder API > Select > Ordering and Pagination > Write Lock and Java > Consumption API > Pessimistic Locking.

### Miscellaneous ​

- Support for `$select` and `$expand` on actions and functions in OData V4, ensuring compatibility with SAP UI5 >= 1.75.0
- A Spring property metadata file is now part of the `cds-framework-spring-boot` JAR. This enables code completion and suggestions of cds properties in Spring configuration files, if corresponding IDE plugins are installed. See Spring Tools for more details.
- Patterns in `.gitignore` generated by the archetype, now use `**/` as `glob` statement prefix, to ensure compatibility with other tools interpreting the `.gitignore` file (for example, npm publish). See glob (programming) (Wikipedia) for more details.
- Error messages listed in the details section of an error response now have the fields `@Common.numericSeverity` and optionally `@Common.longtextUrl`. This ensures that Fiori displays these messages correctly and also renders the target correctly.

### Bug Fixes ​

- Fixed handling of `CqnUpdate` statements with more than one data entry.
- Fixed handling of `CqnUpdate` statements with empty data entry.
- Fixed handling of mandatory associations to draft-enabled entities.
- Update data is only returned when amount of updated rows is higher than 0. Returned data is enriched by default values.
