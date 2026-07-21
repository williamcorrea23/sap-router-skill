<!-- mirror: https://cap.cloud.sap/docs/releases/2023/apr23 -->
<!-- fetched: 2026-05-09T02:26:34.698Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# April 2023 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## All-new Documentation ​

The **CAP documentation pages (aka *CAPire*) got an all-new look and feel** with major improvements like dark-mode support, better accessibility and responsiveness on smaller devices. Here are some of the noteworthy features:

- The button on the upper right corner allows toggling dark or light mode. By default, it uses your operating system's preference.
- The sidebar on the left side now supports nested levels. Because it expands automatically to the current page, you now know exactly where that page is located.
- With the On this page outline on the right side, you now get an overview of the current page's content. It is available on smaller screen sizes as well
- The CDS language is now supported in code blocks, providing more accurate syntax highlighting.
- Code blocks with focused lines give more guidance in larger code snippets on which lines are relevant.

## Unrestricted XSUAA Attributes ​

`$user` attributes can be compared with *null* in `@restrict` annotations.

- `$user. is null` matches null and an empty array
- `$user. is not null` matches arrays != null and an array with at least one entry

Note that XSUAA attributes with `valueRequired:false` might need model adaption such as `$user.code = code or $user.code is null` to support unrestricted access. There is no effect on default XSUAA attributes with `valueRequired:true`.

[Learn more about unrestricted XSUAA attributes.](/docs/guides/security/authorization#unrestricted-xsuaa-attributes)

## Reliable Pagination ​

For [Server Side Paging](https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#sec_ServerDrivenPaging) CAP so far uses a numeric skip token that uses `$skip` and `$top` for pagination. This can result in duplicate or missing rows if the data is concurrently created or deleted. Alternatively, you can now use [reliable pagination](/docs/guides/services/served-ootb#reliable-pagination), which generates a skip token based on the values of the last row of a page and is therefore more robust.

You can enable *reliable paging* with the following configuration options:

- Java: `cds.query.limit.reliablePaging.enabled: true`
- Node.js: `cds.query.limit.reliablePaging: true`

[Learn more about reliable pagination.](/docs/guides/services/served-ootb#reliable-pagination)

## Enhanced Show All References in VS Code ​

*Show All References* for service elements such as entities, properties and actions now also shows the references to these elements in annotation values. You can use it before modifying a service element to understand if annotations will be affected by the change and avoid the related errors or easily fix them.

## CDS Language & Compiler ​

### Additional OData Annotation Vocabularies ​

By default, the compiler only generates the OData metadata for annotations listed in one of the OData vocabularies known to the compiler. Assuming you have a vocabulary `com.MyCompany.vocabularies.MyVocabulary.v1`, you can set the following configuration option:

package.json.cdsrc.jsonjson

```
{
  "cds": {
    "cdsc": {
      "odataVocabularies": {
        "MyVocabulary": {
          "Alias": "MyVocabulary",
          "Namespace": "com.MyCompany.vocabularies.MyVocabulary.v1",
          "Uri": "- "
        }
      }
    }
  }
}
```

json

```
{
  "cdsc": {
    "odataVocabularies": {
      "MyVocabulary": {
        "Alias": "MyVocabulary",
        "Namespace": "com.MyCompany.vocabularies.MyVocabulary.v1",
        "Uri": ""
      }
    }
  }
}
```

Assume you use the annotation assignments prefixed with `Alias`:cds

```
service S {
  @MyVocabulary.MyAnno: 'My new Annotation'
  entity E { /*...*/ };
};
```

This is added to the OData API, including the mandatory reference to the vocabulary definition:xml

```



...



```

The compiler neither evaluates the annotation values nor the URI. The values are translated generically and it's your responsibility to make the URI accessible if required.Learn more about OData Annotation Vocabularies.

## Node.js ​

### Important Changes ❗️ ​

A new `minorUnit` element in sap.common.Currencies holds the number of fractions that the minor unit takes (for example, 0 or 2). See @sap/cds-common-content for matching content.
- Texts for sap.common.Countries are changed from Country to Country/Region.

### Miscellaneous ​

- If custom authentication is enabled, it's now also used for the protection of enterprise-messaging webhooks.
- You can now limit the maximum number of requests that are accepted within a single OData $batch request. `cds.odata.batch_limit` specifies the corresponding limit. By default, no limit applies.

## Java ​

### Important Changes ❗️ ​

#### Optimized OData V4 Adapter ​

The optimized serializer is now enabled by default. It can be disabled by setting `cds.odatav4.serializer.enabled: false`.

#### XSUAA Attributes Restricted by Default ​

By default, undefined or empty attributes **restrict** expressions in where-conditions of instance-based authorization now. For instance, `$user.code = code` evaluates to `false` if the user attribute `code` is not defined or has no value.

#### Immutable References ​

In CDS QL, a [reference](/docs/cds/cxn#references) (*ref*) identifies an entity set or element of a structured type. References can have multiple segments and ref segments can have filter conditions.

The default implementations of references (`ElementRef` and `StructuredTypeRef`), as well as ref segments (`RefSegment`) are now immutable. This makes [copying & modifying CQL statements](/docs/java/working-with-cql/query-api#copying-modifying-cql-statements) much cheaper, which significantly improves the [performance](#performance).

Tip

Only code that modifies existing refs is affected by this change.

##### - Set alias or type ​

`CQL:entity:asRef`, `CQL:to:asRef` and `CQL:get` create immutable refs. Modifying the ref is not supported. Methods `as(alias)` and `type(cdsType)` now return a *new* (immutable) ref:

java

```
ElementRef authorName = CQL.get("name").as("Author");
ElementRef nombre = authorName.as("nombre");           // authorName is unchanged
ElementRef string = authorName.type("cds.String");     // authorName is unchanged
```

##### - Modify ref segments ​

Also the segments of an immutable ref can't be modified in-place any longer. To create an immutable ref segment with filter, use

java

```
Segment seg = CQL.refSegment("title", predicate);
```

The deprecated `RefSegment:id` and `RefSegment:filter` methods now throw an `UnsupportedOperationException`. For in-place modification of ref segments use the new [RefBuilder](#ref-builder).

### Modification of Ref Segments ​

Use `CQL.copy(ref)` to create a `RefBuilder`, which is a modifiable copy of the original ref. The `RefBuilder` allows to modify the segments in-place to change the segment id or set a filter. Finally call the `build` method to create an immutable ref.

To manipulate a ref in a `Modifier`, implementations should override the new `ref(CqnStructuredTypeRef ref)` and `ref(CqnElementRef ref)` methods. Only use `CQL.copy(ref)` if necessary.

java

```
Modifier modifier = new Modifier() {
 @Override
 public CqnStructuredTypeRef ref(CqnStructuredTypeRef ref) {
  RefBuilder copy = CQL.copy(ref); // try to avoid copy
  copy.targetSegment().filter(newFilter);
  return copy.build();
 }

 @Override
 public CqnValue ref(CqnElementRef ref) {
  List segments = new ArrayList<>(ref.segments());
  segments.add(0, CQL.refSegment(segments.get(0).id(), filter));
  return CQL.get(segments).as(alias);
 }
};
CqnStatement copy = CQL.copy(statement, modifier);
```

For compatibility, the legacy methods `ref(ElementRef ref)` and `ref(StructuredTypeRef ref)` are still supported. The runtime automatically creates *mutable* copies of refs as input for these methods during CQN modification.

Warning

The `Modifier` methods `ref(ElementRef ref)` and `ref(StructuredTypeRef ref)` are *deprecated* and will be removed with CAP Java 2.0.

### Performance Improvements ​

[Immutable references](#immutable-references) improve the performance of copy operations, resulting in a significant reduction in CPU usage, in particular for GET requests on single entities.

According to measurements of basic OData requests in the [SFlight](https://github.com/SAP-samples/cap-sflight) demo application, the average response time of requests on single entities is reduced by 20-30% compared to cds-services version `1.33.1`.

### Compare Row Values ​

The Query Builder API now allows to build queries that use row values in comparisons.

For example, to get all sales after Q2/2012 you may compose the following query:

java

```
import static com.sap.cds.ql.CQL.*;

...

CqnListValue props = list(get("year"), get("quarter"));
CqnListValue vals  = list(val(2012), val(2));
CqnSelect q = Select.from(SALES).where(comparison(props, GT, vals));
```

On databases that support comparing row value (SQLite, H2, Postgres) this feature is leveraged when converting to SQL:

sql

```
Select * from Sales where (year, quarter) > (2012, 2)
```

On SAP HANA, the comparison is unfolded as follows:

sql

```
Select * from Sales where year > 2012 or year = 2012 and quarter > 2
```

### Open Types in OData v4 ​

You may now annotate an entity or a structured type with [@open](/docs/guides/protocols/odata#open-types) to indicate that it is *open* and hence allows clients to add properties dynamically by specifying uniquely named property values in the payload. Likewise, the server may return additional properties:

cds

```
@open
entity Products {
    key productId : Int32;
}
```

The CDS build for OData v4 will render the entity type `Products` in `edmx` with the [`OpenType` attribute](https://docs.oasis-open.org/odata/odata-csdl-xml/v4.01/odata-csdl-xml-v4.01.html#sec_OpenEntityType) set to `true`.

Now the client may pass additional properties:

js

```
POST /CatalogService/Products
Content-Type: application/json

{
    "productId": 17,
    "description": "box",
    "details": {
        "length" : 17,
        "width"  : 4,
        "height" : 23
    }
}
```

Warning

Like virtual elements, additional properties are not automatically persisted by the runtime. They must be handled completely by custom code.

### Improved Kyma Support ​

A new starter module `cds-starter-k8s` has been introduced which bundles useful CAP dependencies for the Kubernetes/Kyma environment. The CDS Maven archetype now supports the `kubernetes` and `k8s` values as additional option in the `targetPlatform` parameter.

## Tools ​

### Important Changes ❗️ ​

`cds-ts watch` now considers configuration from `tsconfig.json` files in Typescript projects. This might expose compilation errors that were ignored before. Note that `cds-ts run` has always used `tsconfig.json`, so that these 'error' cases should be rare.

### mTLS (X.509) Authentication ​

You can now configure `@sap/cds-mtxs` to authenticate with X.509 (mTLS) against XSUAA when fetching a token for multitenancy and/or extensibility. In particular, `cds login -m [:]` can be run against an X.509-enabled application, supplying as `` the private key of its X.509 client certificate. This [configuration](https://help.sap.com/docs/btp/sap-business-technology-platform/enable-mtls-authentication-to-sap-authorization-and-trust-management-service-for-your-application) is usually made in the config parameters of the XSUAA resource in `mta.yaml`.

### EDMX Import ​

You can now import OData V4 EDMX files containing multiple `Schemas` with single `EntityContainer`.

### AsyncAPI Import ​

The `cds import` command can now import AsyncAPI documents. It translates events listed in an AsyncAPI document to CDS services and events in a CSN file.

To import an AsyncAPI document, use:

sh

```
cds import ~/Downloads/AsyncAPI_sample.json
```

You can specify the `--from` option to import from AsyncAPI sources explicitly.

To import AsyncAPI documents programmatically, use the [APIs](/docs/tools/apis/cds-import#cds-import-from-asyncapi).
