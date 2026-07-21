<!-- mirror: https://cap.cloud.sap/docs/releases/2022/apr22 -->
<!-- fetched: 2026-05-09T02:26:29.552Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# April 2022 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtx?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

*The April 2022 release only contains updates for the CAP Service SDK for Java.*

## Java SDK ​

### Important Changes ❗️ ​

- Path access via the get method is deprecated. See Convenience for Struct Data.
- The CDS model is no longer reloaded every time when opening a new Request Context. See Optimized Model Propagation.

### Spring Boot Developer Tools ​

CAP Java SDK now provides full support for [Spring Boot Developer Tools](https://docs.spring.io/spring-boot/docs/current/reference/html/using.html#using.devtools). The tools contain a bunch of handy development-time features that help you to reduce roundtrip times in local but also remote development scenarios:

- Automatic application update on CDS model, configuration, or code changes.
- Benefit from `cds-maven-plugin` integration (goal `watch`).
- Benefit from IDE integrations (Eclipse, IntelliJ IDEA, VS Code).
- LiveReload support to trigger an instantaneous browser refresh.
- Remote Update: deploy once and upload changes done locally at runtime.

To activate the developer tools, add the following in your development profile:

xml

```


        org.springframework.boot
        spring-boot-devtools
        true


```

### Optimized Model Propagation ​

The CDS model is no longer reloaded every time when opening a new [Request Context](/docs/java/event-handlers/request-contexts#defining-requestcontext). Only the outmost Request Context initially loads the CDS model and propagates it to all inner Request Contexts.

The only scenario where the model is still reloaded is when the new Request Context uses a different tenant. This scenario also requires a new [ChangeSet Context](/docs/java/event-handlers/changeset-contexts) to be opened in addition. If a ChangeSet Context is opened without an existing Request Context the latter is opened implicitly as well.

### Optimized $metadata Requests ​

The `$metadata` endpoints now stream the original EDMX directly, without serializing the internal Olingo EDMX representation. This results in a much better performance. It also allows you to use [OData dynamic expressions](/docs/guides/protocols/odata#dynamic-expressions).

### Enhanced $user.<attr> Usages ​

Now, user attribute values `$user.` can be automatically assigned to elements annotated with `@cds.on.insert` or `@cds.on.update`:

cds

```
entity UserData {
  @cds.on.insert : '$user.organization'
  organization : String;

  @cds.on.insert : '$user.departments'
  departments: array of String;
}
```

As [user attributes](/docs/guides/security/authorization#user-attrs) in general have a list of values, you can also fill an element of arrayed `String` type.

### Improved Deep Updates ​

Deep Update now supports changing to-one associations to different target entities.

- associations can be set to either new (nonexisting) or existing target entities
- compositions can only be set to new target entities that are created by the deep update

If a deep update contains data for a to-one association, the data for this association is ignored instead of throwing an exception, when the following applies:

- Doesn't cascade the update operation (default).
- Data doesn't set the association to another target entity.

Deep Updates over associations cascading both the insert and update operation now support creating new target entities with data containing an `InputStream` for a `LargeString` or `LargeBinary` element. In this case, an additional query is executed to determine if the target entity already exists.

Inserting target entities with key elements of type `String` and `@cds.on.insert: $uuid` annotation are now also supported.

### Convenience for Struct Data ​

If you access a `Map` via an [accessor interface](/docs/java/cds-data#typed-access) facade, you can use the [`*Path` methods](/docs/java/cds-data#nested-structures-and-associations) to manipulate nested maps:

java

```
CdsData data = Struct.create(CdsData.class);
data.putPath("deeply.nested.key", "value");
```

This results in a deeply nested data structure: `{ "deeply" : { "nested" : { "key" : "value" } } }`.

Read access to deeply nested data is supported via [getPath](https://javadoc.io/doc/com.sap.cds/cds4j-api/latest/com/sap/cds/CdsData.html#getPath-java.lang.String-). Path access via the [get](https://javadoc.io/doc/com.sap.cds/cds4j-api/latest/com/sap/cds/CdsData.html#get-java.lang.Object-) method is deprecated.

java

```
String v = data.getPath("deeply.nested.key");
```

To check if the data contains a nested map with a specific key use `containsPath`:

java

```
boolean b = data.containsPath("deeply.nested.key");
```

To do a deep remove use `removePath`:

java

```
String oldValue = data.removePath("deeply.nested.key");
```

### Miscellaneous ​

- Spring's `@Order` annotation on event handler classes is now respected and event handlers are registered in that order.
- Enhanced UserInfo in case of IAS authentication:UserInfo.getName() represents the token subject (`sub`) identifying the request user (`$user`).
- UserInfo.getAdditionalAttributes() contains all token claims such as `email` or `aud`.

- The persistent outbox can now store the last error message for an outbox entry if it failed to process it.
- Pessimistic locking via `Select.lock` with a timeout of 0 (NOWAIT) is now also supported on PostgreSQL.
