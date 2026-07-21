<!-- mirror: https://cap.cloud.sap/docs/releases/2022/sep22 -->
<!-- fetched: 2026-05-09T02:26:33.900Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# September 2022 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Streamlined MTX ​

### New Extensibility Guide ​

Following the streamlined [multitenancy guide](/docs/guides/multitenancy/), there is now a [new guide for extending SaaS apps](/docs/guides/extensibility/customization). It features

- Easier setup of extension projects
- Local development roundtrips with SQLite
- More examples for extending CDS models

## CDS Language & Compiler ​

### Reuse Type sap.common.Locale ​

[The reuse types `@sap/cds/common`](/docs/cds/common) now contain a new type definition for `Locale`:

cds

```
type sap.common.Locale : String(14) @title : '{i18n>LanguageCode}';
```

This type is used for the `locale` field of generated text entities.

### Extending Scalar Types ​

The `extend` directive has been enhanced to allow for enlarging the `length` property of strings and the properties `precision` and `scale` of decimals.

Example:

cds

```
using { User, Locale } from '@sap/cds/common';
extend Locale with (length:16);
extend User with (length:200);
```

[Learn more about Extend.](/docs/cds/cdl#extend)

### New Integer Types ​

We have introduced the built-in types `UInt8` and `Int16`. They are supported by both, the Node.js and the Java runtime.

| CDS Type | Example Value | SQL | EDMX |
| --- | --- | --- | --- |
| `UInt8` | `133` | *TINYINT* | *Edm.Byte* |
| `Int16` | `1337` | *SMALLINT* | *Edm.Int16* |

Example:

cds

```
type Rating : UInt8;
type Stock : Int16;
```

[Learn more about Built-in Types.](/docs/cds/types)

## Node.js ​

### Important Changes ❗️ ​

- All MTX related services have been moved to `@sap/cds-mtxs`. Make sure that you update both modules, `@sap/cds` and `@sap/cds-mtxs`, together.
- The Node.js runtime doesn't interpret the SAP-specific query option `sap-language`. Fiori Elements always sends a BCP47 compliant `accept-language` header that is interpreted correctly. If you have used the query option in your tests, please use the header instead.
- If you use the new 1.0.0 version of `axios`, this might raise errors with missing response headers. In this case, stay with `axios 0.x` for the time being.
- 14.18 is now the minimum required Node.js version. Previously, this was 14.15. Check your version with `node -v`.

### Default Suffix for SQLite Files is now .sqlite ​

The default file endings of SQLite databases has been changed to `.sqlite` in order to integrate seamlessly with VS Code plugins. Make sure to adapt your *.gitignore* file.

If you are using `.db` as file ending within your project, it will work as before.

### Messaging via Redis Beta ​

Warning

This is a beta feature. Beta features aren't part of the officially delivered scope that SAP guarantees for future releases.

There's a new `Messaging Service` based on Redis PubSub, which is suitable for asynchronous communication between tightly-coupled microservices. To configure this messaging service, bind your CAP application to an appropriate platform service, for example of type `redis-cache` and install the latest version of npm package `redis`.

In the `package.json`, you can configure a Redis messaging service explicitly:

json

```
{
  "requires": {
    "messaging": {
      "kind": "redis-messaging"
    }
  }
}
```

### Improved cds.log() ​

- Added out-of-the-box support for winston loggers. For example, creation and usage of winston loggers is as simple as that now:js

```
cds.log.Logger = cds.log.winstonLogger()
```

Learn more in the documentation of `cds.log()`.
- Improved loading custom `server.js` files during bootstrapping so that setting custom loggers via `cds.log.Loggers = ...` has immediate effect on all subsequent log output.
- Finally, documentation for `cds.log()` received a major overhaul, including additional, formerly missing information as well as some formerly undocumented features.

### Improved cds.d.ts Typings ​

Together with our community, we have done various improvements in our [TypeScript typings](/docs/node.js/typescript#typescript-apis-in-sap-cds):

- Typings for using tagged template variants of several CQL constructs
- Typings for calling shortcut versions of CQL constructs (`SELECT(...)` in addition to `SELECT.from(...)`, etc.)
- Typings for wildcard expansion `*` of properties in CQL
- Typings for cds.log, cds.test, cds.utils, req.entity
- More specific signatures for CQL operations

If you observe gaps in any of the typings, we appreciate your help.

## Java ​

### Important Changes ❗️ ​

#### New Behavior for Upsert ​

The semantics, behavior and implementation of [Upsert](#upsert) has been redesigned. This might [affect your application](/docs/java/migration#legacy-upsert) if you use the Upsert statement in custom code.

#### Parameters of Actions and Functions ​

Values for parameters of actions and functions are now validated as described [here](#validation-function).

### Native UPSERT ​

The semantics, behavior and implementation of [upsert](/docs/java/working-with-cql/query-api#upsert) has been redesigned and aligned with the stakeholders' expectations. Upsert now leverages UPSERT (UPdate or inSERT) operations on the database where possible.

#### Behavior ​

- The Upsert statement is primarily intended for efficient data replication scenarios.
- The Upsert statement updates existing data or inserts new data if not yet existing.
- It is now possible to supply partial data ("PATCH semantics").
- The entities that are upserted are identified by the key values given in the data.
- Generic handlers are not executed upon upsert, and no ID generation happens.

#### Usage ​

The following code performs a [bulk upsert](/docs/java/working-with-cql/query-api#bulk-upsert) that upserts two books in a batch leveraging UPSERT on the DB:

java

```
Books b1 = Books.create(101);
b1.setTitle("Odyssey");

Books b2 = Books.create(103);
b2.put("title", "Ulysses");

CqnUpsert upsert = Upsert.into(BOOKS).entries(asList(b1, b2));
```

You can also upsert [deeply structured data](/docs/java/working-with-cql/query-api#deep-upsert). Here, we upsert an order with an associated order item:

java

```
Orders order = Orders.create(1000);

OrderItems item = OrderItems.create(1);
item.setBookId(101);
item.setQuantity(2);
order.setItems(asList(item));

CqnUpsert upsert = Upsert.into(ORDERS).entry(order);
```

#### Implications on Custom Code ​

Up to cds-services 1.27, upsert always completely *replaced* pre-existing data with the given data: it was implemented as cascading delete followed by a deep *insert*. Since this release the upsert is implemented as a deep *update* that creates data if not existing.

While generic code is not affected by this change application developers that use upsert in custom code need to be aware of the [implications](/docs/java/migration#legacy-upsert) and might have to adapt their code.

If an application can't immediately adjust to the new upsert behavior when upgrading to this version of cds-services, *it's possible to switch back* to the old upsert behavior: set the configuration parameter `cds.sql.upsert.strategy` to `replace`.

[Learn more about Upsert.](/docs/java/working-with-cql/query-api#upsert)

### Input Validation for Actions ​

[Input validation](/docs/guides/services/constraints) is now performed for action and function parameters. The annotations `@mandatory` as well as `@assert.format`, `@assert.range` and `not null` are evaluated to verify the parameter values:

cds

```
type Contact {
    @assert.format: '^\p{Lu}.*' name : String(30);
    @assert.range: [1, 10] priority: Integer;
    address: Address not null;
}
action addContact(contact: Contact not null);
function hasContact(@mandatory name: String) returns Boolean;
```

The validation is applied deeply to nested input data. Note that annotated parameters in your model are effectively validated when updating to this version. To switch off parameter validation temporarily, set `cds.query.validation.parameters.enabled` to `false`.

### Local Support for Streamlined MTX ​

You can now run and test your application locally with the [Streamlined MTX](/docs/guides/multitenancy/) sidecar (`@sap/cds-mtxs`) and a [file-based SQLite](/docs/java/cqn-services/persistence-services#file-based-storage) database in multitenant mode. In addition to the common [MTX configuration](/docs/guides/multitenancy/#enable-multitenancy) you need to set the following configuration in your `application.yaml`:

yaml

```
cds:
  multi-tenancy:
    mtxs:
      enabled: true
    sidecar:
      url: http://localhost:4004
```

Then start the sidecar locally (default port 4004) as described [in the multitenancy guide](/docs/guides/multitenancy/index#test-drive-locally). [Mock users with tenants](/docs/java/security#mock-tenants) can be used to run your tests. [Local Development and Testing](/docs/guides/multitenancy/index#test-drive-locally) explains the steps in detail.

### Improvements for PostgreSQL ​

You can now use the new SQL [dialect `postgres`](/docs/java/cqn-services/persistence-services#postgresql) of the CDS Compiler to generate DDL, which is specific for PostgreSQL. Before this release you had to manually adapt the DDL generated for the dialect `plain`.

sh

```
cds deploy --to postgres --dry
```

On [PostgreSQL](/docs/java/cqn-services/persistence-services#postgresql-1), localized and temporal data can now be used without restrictions.

### Miscellaneous ​

- CSV file import now also supports string values that contain escaped characters, delimiter tabs or are quoted with ".
- CloudSDK 4 is now supported. The integration automatically propagates CDS request contexts to CloudSDK's async callables (`ThreadContextExecutorService`).
