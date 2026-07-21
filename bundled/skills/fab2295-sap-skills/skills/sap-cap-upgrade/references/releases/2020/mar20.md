<!-- mirror: https://cap.cloud.sap/docs/releases/2020/mar20 -->
<!-- fetched: 2026-05-09T02:26:22.356Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# March 2020 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Important Changes❗️ ​

### cds build Uses New Build System ​

The `cds build` command now delegates to the new build system by default (known as `cds build/all`).

The new build system is compatible, but supports additional features, for example:

- Staging build
- SAP HANA Cloud Edition support
- Populating initial data from `.csv` by generating `.hdbtabledata` files

## Docs and Samples ​

Find below a list of changes and improvements to the capire docs and to cap/samples. These are another major steps in our quality focus early 2020. There's much more to come → stay tuned...

### Revamped and Reloaded cap/samples ​

- cap/samples received a comprehensive cleanup and overhaul, including simplified monorepo setup, improved organization of sub projects, a bookshop with a Vue.js app, and much more...

### Revised Getting Started & Resources ​

- Resources → consolidated and relocated
- About > Feature Matrix → consolidated and updated
- Getting Started > in a Nutshell → greatly revised and improved

### New and Revised Guides in Cookbook ​

- Cookbook > Generic Providers → merged into Providing Services
- Cookbook > Adding Custom Logic → merged into Providing Services
- Cookbook > Providing Services → consolidated and improved

- Cookbook > Adding/Serving UIs → newly written and released

### New Reference Docs ​

- CDS > Common Annotations
- CDS > OData Annotations

## Command Line ​

### Integrate and Mashup with cds watch ​

As a bonus, `cds watch` detects whenever you add an `.edmx` file to your project in whatever place and automatically triggers `cds import` to convert them to CSN.

Get an `.edmx` file from the [SAP API Business Hub](https://api.sap.com/), in the *Details* tab of an API description, to test it.

Drag-and-drop the `.edmx` file to your Visual Studio Code window.

### Start Service in Watch Mode ​

Use the option `--watch` on a specific service with command `cds serve` to start that specific service in nodeman watch mode.

### List All Dependencies of Your Local package.json ​

Use `cds version --all` to list all dependencies of your local *package.json*. See the CLI command help for more information.

## CDS Editors & Tools ​

The following features are available for all editors based on our Visual Studio Code extension for CDS in SAP Business Application Studio and Visual Studio Code. The extension for Visual Studio Code is available for download at the [SAP Development Tools](https://tools.hana.ondemand.com/#cloud-vscodecds) page.

### Installation of CDS Development Kit ​

The Visual Studio Code extension for CDS detects missing or outdated installation of CDS development kit.

Select to install the CDS Development Kit:

Select to update the CDS Development Kit:

Enable Installation Check:

## CDS Language & Compiler ​

### Documentation Comments ​

If comments of the form `/**...*/` appear at positions where annotation assignments are allowed, use option `--docs` in `cds compile` to preserve them.

Documentation comments are propagated like annotations until an empty comment `/***/` disrupts the propagation. The documentation comments appear as `doc` properties in the CSN and in the OData/EDMX, it appears as a value for the annotation `@Core.Description`.

cds

```
/** This is an example for a doc comment */
entity Foo { key ID:UUID; ... }
```

json

```
{
  "definitions": {
    "Foo": { "kind": "entity", "doc": "This is an example for a doc comment", ... }
  }
}
```

### DISTINCT and ALL ​

The compiler supports function calls like `count( distinct ... )` and `count( all ... )`.

### New Option --clean ​

Use `cds compile --clean` to return a CSN, which reflects only what was found in a *.cds* source. The compiler doesn't add any derived information.

## Node.js Runtime ​

### Important Changes❗️ ​

On SAP HANA with multitenancy enabled (`multiTenant: true`), the users are being authenticated regardless of whether authorization annotations (`@requires/@restrict`) are used. The reason is that the user's identity zone is required to determine the respective HDI container. In production mode, this requirement is now enforced. In development mode, the developer needs to make sure to fulfill this requirement.

In previous versions, `$count=true` triggered handlers to be executed twice. This led, for example, to `WHERE` conditions from security annotations being appended twice. Now, the usage of `$count=true` triggers handlers only once, so custom handlers that accommodated this behavior might have to be adapted. The resulting array of the original query has a new property `$count`. Make sure that this property is not lost when you return the result in your custom handlers.

The [`req.user` object](/docs/node.js/events#user) represents the currently logged in user.

The annotations `@FieldControl.Mandatory`, `@Common.FieldControl.Mandatory`, and `@mandatory` now enforce that empty strings and strings with only whitespaces are rejected as input. Previously only `null` and `undefined` were checked.

### Convenient Access to express Request Object ​

The [`req._` object](/docs/node.js/events#cds-request) contains the original `req` and `res` objects as obtained from express.js. This is now also the case for `$batch` requests.

### Localized Data - Access to Default Values ​

It's now possible to prevent automatic redirection to the localized views for localized entities with the [`@cds.localized:false` annotation](/docs/guides/uis/localized-data#serving-localized-data).

### Ordered OData Singletons ​

In the CDS model, it's now possible to order OData Singletons: `... as select from  order by

`.

### Miscellaneous ​

- Enhanced Fiori draft support, see Fiori Support
- The pool acquire timeout is now set to a default (5,000ms on SQLite and 10,000ms on SAP HANA) and can be configured in the pool options with `acquireTimeoutMillis`.
- Functions and properties are now allowed as second parameter in `contains`, `startswith`, and `endswith`.
- OData requests using $count on navigation-to-many are now supported.
- OData requests using $count on parameterized views are now supported.
- INSERT.entries now supports different columns combinations.
- Support for `count` in SELECT CQN.
- `@cds.persistence.skip` is now also evaluated for deep operations to annotated child entities.

## Java Runtime ​

### Important Changes❗️ ​

`@mandatory` annotated elements of type `String` now also reject any trimmed empty strings.

Entities annotated with `@cds.autoexpose` are now read-only if referenced as root entity in a CQN statement. This policy doesn't apply if the entity is draft-enabled or explicitly mentioned in the service definition.

### Build Improvements ​

- Save time and use a globally installed cds-dk when building your application by using the `cdsdk-global` profile:bash

```
mvn spring-boot:run -P cdsdk-global
```
- When creating new projects with the CAP Java Maven archetype, the `cds-starter-cloudfoundry` dependency is automatically added.
- `EventContext` interfaces for types used in OData actions and functions, which make accessing input and output parameters much more convenient. Newly generated projects now support `EventContext` interfaces by default. Add this feature to your existing project manually by adding the following to your CDS4J maven plugin configuration:xml

```
true
```

For example, consider the action `review` defined in the following CDS model:cds

```
entity Books {
  ...
  action review(stars: Integer) returns Reviews;
  ...
}

entity Reviews {
    book : Association to Books;
    stars: Integer;
}
```

You can now use type names that you defined in the CDS model directly in your custom code. Hence, the generated type `ReviewContext` allows you accessing the input value via `getStars()`. In addition, you can use the generated type `Reviews` to set the result:java

```
@On(entity = Books_.CDS_NAME)
public void review(ReviewContext context) {
    int stars = context.getStars();
    ...
    Reviews review = [...]
    context.setResult(review)
}
```

### Deep Update ​

Allows to update a single entity including its associated entities. In contrast to a deep upsert (replace), deep update has patch semantics. Elements that aren't contained in the update data keep their old value.

For to-many compositions or associations, the provided list of entities has to be complete, entities that aren't in the list will be removed and in case of compositions also deleted. See also [Java > Query Builder API > Deep Update](/docs/java/working-with-cql/query-api#deep-update).

### Spring Framework Integration ​

- Use Spring health-check actuators with multitenancy turned on. At each call, the health of each connected HANA database is checked.
- We now support a Spring actuator returning CDS-related debugging information. Get, for example, version, registered event handlers, and service instances at endpoint `/actuator/cds`. Activate this endpoint by adding the value `cds` to the property `management.endpoints.web.exposure.include` in your application configuration, for example:yaml

```
management.endpoints.web.exposure.include: info,health,cds
```

### OData V4 ​

- We added a configuration switch `cds.odatav4.contextAbsoluteUrl`. This switch controls if the URL in the @context field of OData V4 responses contains a relative or an absolute path. The default of this property is `false` (relative path).
- We improved the startup performance. OData vocabulary files used for validation purposes aren't loaded during startup anymore.

### Miscellaneous ​

- Enhanced Fiori draft support, see Fiori Support
- The whitelist for normalized locales is now configurable by means of the property `cds.locales.normalization` in the application configuration, for example:yaml

```
cds.locales.normalization:
  defaults: true  # Keep default whitelist as documented in capire
  whiteList:      # These locales are added to the default whitelist
    - "zh_CN"
    - "zh_HK"
```
- .csv files (for example, configuration data) are loaded during startup from either `db/data` or `db/csv` folders. To load `.csv` files is enabled by default for the in-memory SQLite database.You can control this behavior further by setting `cds.datasource.csv-initialization-mode` in your application configuration to either `always` or `never` load data. `always` enables loading of the CSVs regardless of the database type. `never` turns it off completely.
- Reactivated tests integrating PostgreSQL DB, nevertheless CAP won't support PostgreSQL out of the box. More details when setting up PostgreSQL for own purposes are collected in section PostgreSQL.

### Bug Fixes ​

- The locales `1Q` and `2Q` are now handled correctly.
- `$search` doesn't lead to duplicate search results anymore.
- Fixed a malformed OData response, containing an incorrect `@context` property instead of `@odata.context`.
- XSUAA user names are now normalized by converting them to lower case when persisting. This behavior can be turned off by specifying `cds.security.xsuaa.normalizeUserNames: false` in the application configuration.
- Batch request the Authorization header is now propagated from the parent batch request to child requests. This only affects the visibility of the Authorization header through the ParameterInfo interface.
- Fixed a bug the prevented to use SAP UI5 versions greater or equal than 1.75.0 by returning the complete structured entity when saving a draft.

## Fiori Support ​

### Draft for Localized Data ​

The compiler supports draft-enabling entities with localized elements.

To make the generated `_texts`-entities draftable, additionally annotate the source entity with `@fiori.draft.enabled` - more details on the usage and the implications can be found in [Advanced > Serving Fiori UIs](/docs/guides/uis/fiori#draft-for-localized-data).

### Fiori Drafts with Locks ​

Edited draft data is now restricted to the user who created the draft. This also applies to delete and cancelling drafts.
