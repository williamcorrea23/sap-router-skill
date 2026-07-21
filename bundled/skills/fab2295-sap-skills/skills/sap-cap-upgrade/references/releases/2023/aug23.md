<!-- mirror: https://cap.cloud.sap/docs/releases/2023/aug23 -->
<!-- fetched: 2026-05-09T02:26:35.293Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# August 2023 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## CDS Language & Compiler ​

### Constraints for .texts Entities ​

If you have enabled foreign key constraints on the database, you will now also get a constraint on the generated `.texts` entity for localized elements.

Example:

cds

```
entity Books {
  key ID : Integer;
  title : localized String;
}
```

A constraint is added to the `texts` table:

sql

```
ALTER TABLE Books_texts
  ADD CONSTRAINT Books_texts_texts
  FOREIGN KEY(ID) REFERENCES Books(ID)
  ON UPDATE RESTRICT
  ON DELETE CASCADE
  VALIDATED ENFORCED INITIALLY DEFERRED
```

[Learn more about Database Constraints.](/docs/guides/databases/cdl-to-ddl#database-constraints)[Learn more about Localized Data.](/docs/guides/uis/localized-data#localized-data)

## Node.js ​

### ‼️ Important Security Change ‼️ ​

For reasons of security by default, the startup of the application is now stopped if `jwt` or `ias` is configured but no service binding is found. Previously, only a warning was emitted and the startup continued without any authentication.

As a consequence, the authentication configuration for test deployments or deployments of demo applications needs to be adapted. For example, by configuring `dummy` or `mocked` authentication for production profile like that:

json

```
{
  "cds": {
    "requires": { "auth": "[production]": { "kind": "dummy" }}
  }
}
```

Danger!

Only use that for demo purposes, not in real productive scenarios!

[Learn more about Authentication Strategies.](/docs/node.js/authentication#strategies)

### Calculated Elements in Node.js ​

In recent releases we already introduced [calculated elements with support in views](./march23#calculated-elements-beta), followed by [on-write support](./jun23#calculated-elements-on-write), and [support in Java runtime](./jun23#java-support-for-calculated-elements-on-read). With this release, Node.js support is added by the new database services.

For example given this definition:

cds

```
service Register {
  entity People : cuid {
    lastName  : String(30);
    firstName : String(30);
    fullName  : String = firstName || ' ' || lastName;
    upperName : String = upper(fullName);
  }
}
```

Although the values of calculated elements aren't persisted, they can be used in ad-hoc queries at runtime in Node.js just like ordinary elements:

js

```
SELECT.from(People).columns('fullName', 'upperName');
```

The database service substitutes them with their defining expression:

sql

```
SELECT firstName || ' ' || lastName as fullName,
       upper(firstName || ' ' || lastName) as upperName FROM People
```

[Learn more about Calculated Elements on Read.](/docs/cds/cdl#on-read)

### Consistent Timestamps in SQLite ​

The support for `DateTime` and `Timestamp` values has been greatly improved in the new SQLite service, also to maximize feature parity with SAP HANA and PostgreSQL. All timestamp values are converted and stored in normalized values now, so they can be safely compared. For example, you can now safely insert any valid ISO string:

js

```
await INSERT.into(Books).entries([
  { createdAt: new Date },                       //> stored .toISOString()
  { createdAt: '2022-11-11T11:11:11Z' },         //> padded with .000Z
  { createdAt: '2022-11-11T11:11:11.123Z' },     //> stored as is
  { createdAt: '2022-11-11T11:11:11.1234563Z' }, //> truncated to .123Z
  { createdAt: '2022-11-11T11:11:11+02:00' },    //> converted to zulu time
])
```

### PostgreSQL Step-by-Step Guide ​

The PostgreSQL database guide was enhanced with [step-by-step instructions](/docs/guides/databases/postgres#with-a-deployer-app) describing how to add PostgreSQL to CAP projects. This greatly enhances the existing documentation which required advanced CAP expertise to succeed.

This is a community contribution to [https://github.com/capire/docs](https://github.com/capire/docs).
 Thanks so much for that!

### Fixed Typescript APIs ​

Our Typescript API declarations, that is `@sap/cds/apis/cds.d.ts`, had several bugs and flaws that broke usage in real Typescript projects. Usage for IntelliSense in JavaScript projects was not affected. In a first iteration we now fixed many of these flaws and filled in missing declarations so that usage of `@sap/cds` in true Typescript projects shouldn't run into showstoppers anymore.

Noteworthy in that context:

- You can use default import as well as individual imports now:ts

```
import cds from '@sap/cds';               // default import
import { Session, User } from '@sap/cds'; // individual imports

console.log (cds.Session === Session) //> true
console.log (cds.User === User) //> true
```

Note that functions like `cds.parse()` o`r cds.linked()` are not available through individual imports. Always access these functions using the `cds` facade object obtained via default import:ts

```
let csn = cds.parse(`entity Foo {}`)
let m = cds.linked(csn)
```
- Many missing exports have been added now, for example:ts

```
import {

  Service,
  ApplicationService,
  MessagingService,
  DatabaseService,
  RemoteService,

  EventContext,
  Request,
  Event,
  User,

  Association,
  Composition,
  entity,
  event,
  type,
  array,
  struct,
  service,

} from '@sap/cds'
```

ts

```
import cds from '@sap/cds'

cds.env
cds.requires
cds.version
cds.home
cds.root

cds.compile
cds.resolve
cds.load
cds.get
cds.parse
cds.reflect
cds.linked

cds.builtin
cds.Association
cds.Composition
cds.entity
cds.event
cds.type
cds.array
cds.struct
cds.service
cds.services
cds.server
cds.serve
cds.connect

cds.Service
cds.ApplicationService
cds.MessagingService
cds.DatabaseService
cds.RemoteService

cds.EventContext
cds.Request
cds.Event
cds.User

cds.debug
cds.log
cds.test
cds.utils
cds.lazify
cds.lazified
cds.exit

cds.ql
cds.entities
cds.context
cds.spawn
cds.tx
cds.run
cds.foreach
cds.stream
cds.read
cds.create
cds.insert
cds.update
cds.delete
```
- You are not required to use the `esModuleInterop` tsc compiler option anymore. You can use `@sap/cds` with or without that option now.

Going forward, we will add more improvements and also fix/add links to capire docs.

## Java ​

### CDS reuse models in Jars ​

CDS models and other content can now be shared through Maven dependencies in addition to npm packages. This means you can now provide CDS models, CSV files, i18n files and Java code (for example, event handlers) in a single Maven dependency.

Models are placed in the `resources/cds` folder of the reuse package under a unique module directory (for example, leveraging group ID and artifact ID): `src/main/resources/cds/com.sap.capire/bookshop/`.

Projects wanting to import the content simply add a Maven dependency to the reuse package to their `pom.xml`.

xml

```

  com.sap.capire
  bookshop
  1.0.0

```

Additionally the new `resolve` goal from the CDS Maven Plugin needs to be added, to extract the models into the `target/cds/` folder of the Maven project, in order to make them available to the CDS Compiler.

xml

```

  com.sap.cds
  cds-maven-plugin
  ${cds.services.version}

    ...

      cds.resolve

        resolve // [!code focus]


    ...


```

In CDS files the reuse models can then be referred to using the standard `using` directive:

cds

```
using { CatalogService } from 'com.sap.capire/bookshop';
```

Note that [CDS editor](/docs/tools/cds-editors) does not yet support this new location and hence shows an error marker for this line. This will be fixed soon.

[Learn more about providing and using reuse packages.](/docs/guides/integration/reuse-and-compose)

### Miscellaneous ​

- Platform starter bundles `cds-starter-cloudfoundry` and `cds-starter-k8s` now also comprise maven dependencies that are required to run with IAS-based authentication. In particular,`cds-feature-identity`
- Spring boot starter bundle for security (cloud-security-services-integration-library ) are included.

- Performance of accessor interfaces (generated POJOs) has been improved significantly.
- Public Java Bookshop sample now demonstrates how to consume Postgre SQL.

## New Audit Logging Plugin Beta ​

Last but not least, the new, open source CDS plugin [@cap-js/audit-logging](https://www.npmjs.com/package/@cap-js/audit-logging) is available for early adoption now. Simply add the package to your applications's dependencies and get automatic audit logging, for personal data in a plug and play fashion:

sh

```
npm add @cap-js/audit-logging
```

*Learn more about setting up and using audit logging in the [Data Privacy guide](/docs/guides/security/data-privacy), which got greatly revamped and rebased on the new [Incident Management](https://github.com/cap-js/incidents-app) reference sample*.

#### Migration from former implementation ​

If you were using the former audit logging support implemented in `@sap/cds@6,` here are your migration steps:

- Remove obsolete dependency `@sap/audit-logging`
- Remove obsolete configuration `cds.requires.audit-log`
- Remove obsolete feature flag `cds.env.features.audit_personal_data = true`.
- Remove obsolete `@AuditLog.Operation` annotations from your CDS models.
- Add the new plugin package, i.e.: `npm add @cap-js/audit-logging`.

`@cap-js/audit-logging` supports all plans of the SAP Audit Log Service.

Warning

Please note that `@cap-js/audit-logging` is currently released as an early adopter version and, hence, minor breaking changes are possible in the general availability version.

## VS Code Standard Theme in CDS Editor ​

The [SAP CDS Language Support extension for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=SAPSE.vscode-cds) now uses the standard theme instead of a custom built-in theme. This allows you to use one of the many excellent [themes](https://code.visualstudio.com/docs/getstarted/themes) included in Visual Studio Code by default, as well as in the extension marketplace.

Previously, a custom theme called *Vanilla* was used which in today's standard was quite outdated. For example it did not provide colors for all token classes. A similar, but more competent, theme is for example *Light Modern* included in Visual Studio Code as default light theme. In case you have specifically used *Vanilla*, you don't need to take action. Visual Studio Code will automatically switch to *Light Modern* after an update of the extension.
