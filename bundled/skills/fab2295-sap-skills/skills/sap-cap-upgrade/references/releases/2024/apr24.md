<!-- mirror: https://cap.cloud.sap/docs/releases/2024/apr24 -->
<!-- fetched: 2026-05-09T02:26:40.158Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# April 2024 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Fewer Views in Database Beta ​

New option `cds.sql.transitive_localized_views: false` allows to skip generating *transitive* localized views. For example, use it like that in your *package.json* or in your *.cdsrc.json*:

package.jsonjson

```
{ "cds": {
  "sql": {
    "transitive_localized_views": false
  }
}}
```

Java: `false` as default

In CAP Java, transitive localized views are never used. Hence the default value is `false` and you automatically benefit from fewer views.

Node.js: Only with new database services

In CAP Node.js, transitive localized views can only be disabled when using *new* database services. For compatibility with old database services the default value is still `true`, but will be changed to `false` in the future.

What are transitive localized views?

As explained in the [Localized Data guide](/docs/guides/uis/localized-data#localized-helper-views), localized views are created for entities with localized data, recursively. This also includes entities which don't have localized elements on its own, but only associations to such. For example:

cds

```
entity Books { ...
  title : localized String; // has own localized data
}
entity Authors { ...
  books : Association to many Books;
}
```

Without `cds.sql.transitive_localized_views: false`, a localized view is created for `Authors` as well, because it has an association to `Books` which has localized data. This is what we call a *transitive* localized view.

Dry-run in your project...

For example when running this in *cap/sflight*:

macOS/LinuxWindowstxtsh

```
cds_sql_transitive__localized__views=true  cds \* -2 sql | grep -c VIEW
cds_sql_transitive__localized__views=false cds \* -2 sql | grep -c VIEW
```

cmd

```
set cds_sql_transitive__localized__views=true
cds * -2 sql | find /C "VIEW"
set cds_sql_transitive__localized__views=false
cds * -2 sql | find /C "VIEW"
```

This should print out some numbers, showing that the number of views created in the database is reduced from 80 to 55, like this:

txt

```
80
55
```

Speeds up database upgrades

This option can significantly reduce the number of views in your database, which can speed up database upgrades significantly, especially using SAP HANA.

## Expressions as Annotation Values Beta ​

The handling of [expressions as annotation values](/docs/cds/cdl#expressions-as-annotation-values) has been significantly enhanced.

### Propagation ​

When annotations are propagated in views/projections or along type references, the compiler now automatically adapts references in expression-like annotation values, if necessary.

Example:

cds

```
entity E {
  @Common.Text: (text)
  code : Integer;
  text : String;
}
entity P as projection on E {
  code,
  text as descr
}
```

When propagated to element `code` of projection `P`, the annotation is automatically rewritten to `@Common.Text: (descr)` due to the renaming of `text` to `descr`.

Note the syntax

Expression-like annotation values need to be enclosed in parentheses. It's still possible to provide a reference as an annotation value without parentheses, but such references are not adapted.

### References in OData Annotations ​

When the CDS model is flattened for OData generation, references in expression-like annotation values are automatically adapted.

Example:

cds

```
type Price {
  @Measures.ISOCurrency: (currency)
  amount : Decimal;
  currency : String(3);
}
service S {
  entity Product {
    key id : Integer;
    name : String;
    price : Price;
  }
}
```

The resulting annotation in EDMX correctly references the flattened element:

xml

```



```

Restrictions concerning the foreign key elements of managed associations

- Usually an annotation assigned to a managed association is copied to the foreign key elements of the association. This is not done for annotations with expression values. That means, it's currently not possible to use expression-valued annotations for annotating foreign keys of a managed association.
- In an expression-valued annotation, it's not possible to reference the foreign key element of a managed association.

### Expressions in OData Annotations ​

Expressions in OData annotations are automatically translated to the corresponding EDMX syntax. You can now simply write the following:

cds

```
service S {
  @UI.LineItem : [{
    Value: (status),
    Criticality: ( status = 'O' ? 2 : ( status = 'A' ? 3 : 0 ) )
  }]
  entity Order {
    key id : Integer;
    status : String;
  }
}
```

Previously, you'd have needed to write the following expression:

cds

```
Criticality : { $edmJson: { $If: [{$Eq: [{ $Path: 'status'}, 'O']}, 2,
                          { $If: [{$Eq: [{ $Path: 'status'}, 'A']}, 3, 0] }] } }
```

## Node.js ​

### INSERT w/ Streams and Subselects ​

With new database services (SAP HANA, PostgreSQL and SQLite) you can now specify streams and subselect queries as arguments to `INSERT.entries()`, for example:

Using a **stream** instead of reading and parsing full JSONs or alike into memory:

js

```
let streamed = fs.createReadStream('books.json')
await INSERT.into(Books) .entries (streamed)
```

Using a **subselect** query to copy *within* the database:

js

```
await INSERT.into(Books) .entries (SELECT.from(Products))
```

[Learn more about `INSERT.entries()`](/docs/node.js/cds-ql#insert-entries)

Recommendation

Prefer using streams and subselects whenever possible. Streams significantly reduce memory consumption and increase scalability. Subselects delegate all read/writes to the database.

## Java ​

### Enhanced Index Page ​

The [Index Page](/docs/get-started/bookshop#generic-index-html) has been enhanced in this release. It now lists links to all web applications contained in the `app` folder, which are now served automatically as well. In addition it comes with SAP Fiori preview links for entities with UI annotations and has a renewed stylesheet:

### Secure by Default ​

A bunch of CAP Java features are available for development scenarios only:

- Index Page
- Mock user authentication
- ...

To make sure these features are deactivated automatically in production mode, you can now tell the CAP runtime which Spring profile should be interpreted as productive:

yaml

```
cds.environment.production.profile: cloud
```

Note that the Java buildpack chooses the `cloud` profile by default.

### SAP Java Buildpack 2 ​

You can now choose to deploy CAP Java by means of SAP Java Buildpack version 2 (`sap_java_buildpack_jakarta`) which brings sapmachine 17 and 21 in offline mode:

yaml

```
parameters:
  buildpack: sap_java_buildpack_jakarta
properties:
  JBP_CONFIG_COMPONENTS: "jres: ['com.sap.xs.java.buildpack.jre.SAPMachineJRE']"
  JBP_CONFIG_SAP_MACHINE_JRE: '{ version: 21.+ }'
```

[Learn more about SAP Java buildpack usage](/docs/java/developing-applications/configuring#buildpack)

### Full-Fledged Sample Project ​

`cds add sample` now generates a full-fledged CAP Java application with bookshop entities that can be modified by mock users in a UI. In contrast, the result of `cds add tiny-sample` exposes the bookshop only as OData API.

## Tools ​

### Shell Completion for CDS Commands Beta ​

You can now easily enable shell completion in your shell for all `cds` commands like `build`, `compile`, and for `cds` itself.

Simply run the following command to install it once:

sh

```
cds add completion
```

After that, you have to source or restart your shell and you're good to go to use `tab` key for completion.

Currently, *bash*, *zsh*, *Git Bash* and *PowerShell* are supported.

### Test Data Generation Beta ​

In VS Code, test data for your application model is now available at your fingertips:

With the new commands *Generate Model Data as JSON / CSV*, select a CDS entity in the pick list, and then test data is inserted at the cursor position in the active text editor. This may include:

- plain `.csv` and `.json` files used for initial data deployment
- test `.js`/`.ts` files
- `.http` files used for manual tests with the REST Client

You can then modify the data as you wish potentially using AI tools.

Under the hood, this feature uses the `cds add data` CLI like this:

sh

```
cds add data --records 2 --content-type csv --filter Books
```

Which will create 2 CSV records with test data for all entities matching *Books* and store it in `db/data` by default. Run `cds add data --help` to see all options.

[Learn more about test data generation](/docs/tools/cds-cli#data)

### HTTP Requests Generation Beta ​

The new *Generate HTTP Requests* command in VS Code allows you to quickly generate sample HTTP requests for your services and entities, including sample data, authentication and endpoint information. You can execute the created request data with the [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) in `.http` files.

Under the hood, the extension uses the `cds add http` CLI command as follows:

sh

```
cds add http --filter Authors
```

This creates `.http` files with sample read and write requests for all services that include the `Authors` entity.

To add authentication and a CloudFoundry endpoint, use the `--for-app ` option.

[Learn more about request generation](/docs/tools/cds-cli#http)

### CDS Syntax Highlighting in VS Code Markdown Editor ​

The CDS language is now highlighted in `cds` code fences in the markdown editor of VS Code:

This is useful for all you authors that write about CAP and the CDS language.

The [markdown preview](https://code.visualstudio.com/docs/languages/markdown#_markdown-preview) in VS Code does not highlight CDS though. This remains to be tackled in a future release.

[Learn more about highlighting code in markdown](https://www.markdownguide.org/extended-syntax/#fenced-code-blocks)

### Playground for CDS ESLint Rules ​

You can now try each of the available [ESLint rules for CDS](/docs/tools/cds-lint/rules/) in a playground environment. This can help you better understand what the rule is supposed to do.

See this example from the [auth-valid-restrict-where](/docs/tools/cds-lint/rules/auth-valid-restrict-where/) rule with the *Open in Playground* link:

srv/cat-service.cdscds

```
service CatalogService {
  // invalid `where` expression, the equality operator is `=`
  @(restrict: [{ grant: 'READ', to: 'Viewer', where: 'CreatedBy === $user' }])
  entity ListOfBooks as projection on Books;
  ...
}
```

[Open In Playground](https://eslint-online-playground.netlify.app/#eNqNU21r2zAQ/iuHGaQdsdzAviwl0Ld9KAw2VtiXuSOqfHHU2pInyUm94P++k6y4a9qOgbGtu+eeu3vutEvQVlI5JrRayZLd22SeyLrRxoEoLKyMrmFyZnmT0TF7Dq7v7SRXT+ivVVtK9XfMgE+b4EgJQvhc4WOIKHDF28rBj1wBMMbIzQwKXdeoCiym3jyyxpyWKmS8qt5wHobv/AvAtBXa+f4EkCdjR7x163TDK1mkBq0zUrh0u0aDeTKnypItNypPpnli13qbJ7cDRe8/9KJjMk0aLh54iVSaViRfSJMniteBJI8Sp47408boexTOUwbUBo2VmlJ44IydsJPR5bomEtS6oA5GR4GNb1EJidYDYl9PXQ1RPz/mSahzDNtc/TPyxbQiz4eY2QMHzEGCXPUkQ3GXWbHGmvtJkg5eAEvaIBA5E7yRBtmd1g8kZXMaFkE56Tq48Lahlgfs4PoK5nCtHJZoCAZwVnNVcKdNB4SvEMhfaUFD+40F3NDQVHk0m82OD9F+uNoQ+txaLSR3pDQ4DefBbglOpY9lROv/FeKbI0HmL9KHBr3jICeF7jslQ0CxWN8C3lmsVr4cktGaTSa4Sy2ajRQYxWwtZYHda1ICt1B30MeLx1g2TmISZI5McMkdr3R5E4+hz7Oj/drTuu+gNFzR3+Tbp/OryZTqpv/vErdo6BTuBRkuDXKHxUUHiwXV3hL/BPrbY8+XZSBVuE+wDPgl0HWnHH7LiXCNgL9a8pPgukHj1QRpYblYhnKIutCq6iAO5bO07stq0I36jNfHa0rPYMZHUbXFIE+BVhjoT8H3/QrdG0R1x+ISwvu46sNsWJgz4Ydj2PZnCcVeiynQLZUrGXTpwyz7P/xO1Fc=)

### ESLint 9 Support ​

CAP's ESLint plugin `@sap/eslint-plugin-cds` has reached a new major version 3 which is now compatible with the new ESLint major version 9.

This means that you can do the following:

- Adjust your `@sap/eslint-plugin-cds` dependencies from `^2` to `^3`.
- Consult the ESLint 9 migration guide for more information. Especially the notes about the new 'flat' configuration format are helpful to migrate your ESLint config files.
- Use both, `cds lint` and `eslint`, clients for your project as before.

The [`cds add lint`](/docs/tools/cds-lint/#cds-add-lint) facet now creates ESLint 9 configuration for new projects.

In the upcoming major release of CAP Node.js, the [`cds lint`](/docs/tools/cds-lint/#usage-lint-cli) client will use ESLint 9 by default.

### Binding Shared Service Instances on Cloud Foundry ​

You can now bind to a shared service instance on Cloud Foundry just like any other service instance. For example, if you have access to a shared `redis-cache` service instance:

sh

```
cds bind messaging --to redis-cache
```

[Learn more about binding shared service instances](/docs/tools/cds-bind#binding-shared-service-instances)

### Overwrite Cloud Service Credentials ​

You can easily overwrite service credential values with local binding information. For example, you might need extra information to connect to a Cloud Foundry service via an SSH tunnel:

sh

```
cds bind service --to my-service --credentials '{ "proxy_host": "localhost" }'
```

Before, you had to use a `default-env.json` file with the *entire* credential details locally.

[Learn more about overwriting cloud service credentials](/docs/tools/cds-bind#overwriting-service-credentials)

## CAP Operator Plugin ​

The [CAP Operator](https://sap.github.io/cap-operator/) manages and automates the lifecycle operations involved in running multitenant CAP applications on Kubernetes (K8s) clusters. If you deploy an application using the CAP Operator, you must manually define the custom resources for the application in a helm chart, which needs time and deep knowledge of helm concepts.

This is where the CAP Operator **plugin** is very useful, as it provides an easy way to generate such a helm chart, which can be easily modified.

[Learn more about how to add and consume the CAP Operator plugin in our documentation](https://github.com/cap-js/cap-operator-plugin#readme).
