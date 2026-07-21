<!-- mirror: https://cap.cloud.sap/docs/releases/2025/feb25 -->
<!-- fetched: 2026-05-09T02:26:49.647Z -->
<!-- generator: cap-upgrade/scripts/refresh-references.js -->
# February 2025 ​

[](https://www.npmjs.com/package/@sap/cds?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-dk?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-compiler?activeTab=versions)[](https://www.npmjs.com/package/@sap/cds-mtxs?activeTab=versions)[](https://mvnrepository.com/artifact/com.sap.cds/cds-services-api)

## Prepare for CDS 9 ​

Along with new features, the next major release CDS 9 will contain some changes that you'll need to react on. For the items listed below, you can do this already **now**, which eases the transition. You can't use the mentioned **deprecated functions** with the CDS 9 release. The corresponding compatibility flags won't be respected any longer.

This section will be a regular part of all upcoming release notes and includes links to all changes relevant to the next major release.

### Migrate ESLint Configuration ​

ESLint v8 was [officially discontinued in October 2024](https://eslint.org/version-support/). To migrate your ESLint v8 configuration to ESLint v9, follow the [official migration guide](https://eslint.org/docs/latest/use/migrate-to-9.0.0).

Starting with CDS 9, [`cds lint`](/docs/tools/cds-lint/) will only support ESLint v9.

### Add Test Support Package ​

With CDS 9, package `@cap-js/cds-test` will be required for tests to run. You can use it already now with `npm add -D @cap-js/cds-test`.

[Learn more about the new package.](#cds-test)

### Remove Compat Flags and Enable @sap/cds 9 Features ​

- Switch on the new CDS parser.
- Upgrade to `@sap/xssec 4`. --> remove compat flag
- Switch on OData containment.
- Adapt to changed behavior when processing `@restrict.where` checks.
- Adopt @cap-js database services now.
- Switch on the new protocol adapters. --> remove compat flag
- Switch on lean draft. --> remove compat flag

## CDS Language & Compiler ​

### New Parser ​

The new CDS parser is now available, and you should start using it.

Switching to the new parser reduces installation times and speeds up parsing. It also enhances code completion. Additionally, some new features are only supported with the new parser.

Roadmap:

| Date | Status | Remarks |
| --- | --- | --- |
| Feb 25 | Released | opt-in usage; default still with old parser |
| May 25 | Used by default |  |

The new parser doesn't come with any breaking changes...

... and is fully compatible with the old parser. Enable it now as follows:

- Set option cds.cdsc.newparser: true in your private `~/.cdsrc.json` to switch on the new parser on your local machine.
- Switch it on in your project's development and test pipelines.
- If that's successful, use it in production.

#### New CDS Parser Support in VS Code ​

The new version of our [CDS plugin for VS Code](/docs/tools/cds-editors#vscode) is able to use the [new CDS parser](./jan25#reminder-new-parser). For the current minor release, though, the default remains to use the old parser. You can switch via the user setting [`cds.compiler.useOldParser`](vscode://settings/cds.compiler.useOldParser). Please report any issues.

### Type as Projection ​

Define a structured type as a projection on another structured type, entity, aspect, or event, where you pick only a subset of elements.

cds

```
entity Name {
  firstName  : String @label: '...';
  middleName : String @label: '...';
  lastName   : String @label: '...';
  initials   : String @label: '...';
  title      : String @label: '...';
}

type ShortName : projection on Name {
  firstName,
  lastName
};
```

TIP

Only available with the new parser via option cds.cdsc.newparser: true.

[Learn more about type projections.](/docs/cds/cdl#structured-types)

### Use Enums Like Constants ​

Instead of using literals, enum symbols defined in CDS can be used where the compiler can deduce the corresponding enum type. See the following example:

cds

```
type Status : String enum { open; closed; in_progress; };
entity Order {
  key id : Integer;
  status : Status default #open;
}
entity OpenOrder as projection on Order {
  id,
  (status = #in_progress ? 'is in progress' : 'is open')
    as status_txt : String,
} where status = #open or status = #in_progress;
```

[Learn more about Enums.](/docs/cds/cdl#enums)

### Annotating Managed Associations Beta ​

When you annotate a managed annotation with an [expression-valued annotation](/docs/cds/cdl#expressions-as-annotation-values), the annotation is now automatically copied to the respective foreign key elements in the OData API generation.

Previously, the copy mechanism has only been applied for non-expression annotations.

In the following example, the annotation is also applied to the generated foreign key element `author_ID` of `Books`:

cds

```
entity Authors { key ID : Integer; name : String; }
entity Books   { author : Association to Authors; }

annotate Books:author with @Common.Text: (author.name);
```

## Node.js ​

### Media Data in Actions and Functions ​

Media data like images, CSVs, and so on, can now also be used as a return type of actions and functions. The same set of [media data annotations](/docs/guides/services/media-data#annotating-media-elements) is supported.

cds

```
@(Core.MediaType: 'text/csv', Core.ContentDisposition.Filename: 'Books.csv')
type csv:  LargeBinary;
entity Books { ... } actions {
  function csvExport () returns csv;
}
```

js

```
this.on('csvExport', req => {
  return new Readable() // the csv stream
})
```

In addition, `req.reply` can be used to set the mime type and filename dynamically.

js

```
this.on('csvExport', req => {
  req.reply(new Readable(), { mimetype, filename })
})
```

[Learn more about media streaming in general.](/docs/guides/services/media-data)[Learn more about media streaming in custom handlers.](/docs/node.js/best-practices#custom-streaming-beta)

### Hints on SAP HANA ​

The new [`SELECT.hints`](/docs/node.js/cds-ql#hints) method of the [`cds.ql`](/docs/node.js/cds-ql) API passes hints to the database query optimizer that can influence the execution plan.

js

```
SELECT ... .hints('IGNORE_PLAN_CACHE', 'MAX_CONCURRENCY(1)')
```

SAP HANA only

Hints are only respected by the SAP HANA database service.

### New Package for cds.test ​

The [test support for CAP Node.js applications](/docs/node.js/cds-test) moves to its own package [`@cap-js/cds-test`](https://www.npmjs.com/package/@cap-js/cds-test). You can start using it now, so install it as follows:

sh

```
npm add -D @cap-js/cds-test
```

This package comes with dependencies you had to maintain separately until now. So get rid of the unnecessary dependencies and only maintain the `@cap-js/cds-test` package going forward.

sh

```
npm rm axios chai chai-subset chai-as-promised
```

With CDS 9, the new package will be required for the `cds.test` API to work.

## Java ​

### Important Change ❗️ ​

Before this release, the comparison operator `!=` was equivalent to the not equals operator (`<>`) and evaluated on a database with *three-valued* comparison logic. Now, the `!=` operator is treated as equivalent with the [is not](/docs/java/working-with-cql/query-api#comparison-operators) operator and is evaluated with *Boolean* logic.

The changed behavior might be observable in [instance-based authorization](/docs/guides/security/authorization#instance-based-auth) but only if a rule's `where` clause uses the `!=` operator. Then, you must check if Boolean or three-valued logic is appropriate. If you want to stick with three-valued logic, you need to use the `<>` operator.

### UI5 State Messages for Drafts Beta ​

CAP Java now supports persisting (error) messages for draft-enabled entities and providing *state messages* to the UI5 OData V4 model. To enable this feature, set the following properties in your `.cdsrc.json`:

.cdsrc.jsonjson

```
{
  "odata": {
    "containment": true
  },
  "cdsc": {
    "beta": {
      "draftMessages": true
    }
  }
}
```

Document-based URLs

The state messages feature relies on UI5 to use *document URLs*. Currently UI5 only uses the document URLs when containment is enabled in the OData metadata. Enabling containment narrows the API surface and only makes composition child entities accessible via their parent, which might be incompatible. It's planned to provide options to instruct UI5 to use document URLs, without enforcing containment on the server-side.

Setting this property adds additional elements to your draft-enabled entities and `DraftAdministrativeData`, which are required to store and serve state messages.

If this feature is activated, you can observe the following improvements, without changing the application code:

- Error messages for annotation-based validations (for example, `@mandatory` or `@assert...`) already appear while editing the draft.
- Custom validations can now be bound to the `DRAFT_PATCH` event and can write (error) messages. It's ensured that the invalid value is still persisted, as expected by the draft choreography.
- Messages no longer unexpectedly vanish from the UI after editing another field.
- Messages are automatically loaded when reopening a previously edited draft.

By default, side-effect annotations are generated in the EDMX that instruct UI5 to fetch state messages after every `PATCH` request. In case more precise side-effect annotations are required you can disable the default side-effect annotation per entity:

cds

```
annotate MyService.MyEntity with @Common.SideEffects #alwaysFetchMessages: null;
```

Requires Schema Update

Enabling draft messages requires a database schema update, as it adds an additional element to `DraftAdministrativeData`.

### Hierarchy Maintenance in Tree Table ​

In the UI5 tree table, on SAP HANA, CAP Java now supports *hierarchy maintenance* for [draft-enabled](/docs/guides/uis/fiori#draft-support) hierarchies. It's now possible to create new nodes and to add them as parent or child nodes to the hierarchy. You can also modify and delete nodes. In addition, one can change a parent of a child node (move a node).

If a node is deleted, its descendant nodes are only deleted if they are in a composition relationship with the deleted node.

#### Inline Editing ​

If a hierarchy appears on an object page, CAP Java now supports inline editing:

#### Order of Sibling Nodes ​

If a hierarchy is defined by a view *with a sort specification*, CAP Java uses this sort specification as the default sort order for sibling nodes in the hierarchy:

cds

```
entity Genre : cuid {
      name        : String;
      parent      : Association to Genre;
      siblingRank : Integer;
}

service GenreAdminService {
  entity GenreHierarchy as projection on Genre
                           order by siblingRank
    actions {
      action moveSiblingAction(NextSibling : cuid);
    };
}
```

In this example sibling nodes within the genre hierarchy are sorted by the value of the `siblingRank` property. You can use this property for a custom implementation of a [ChangeNextSiblingAction](https://github.com/SAP/odata-vocabularies/blob/main/vocabularies/Hierarchy.md#template_changenextsiblingaction-experimental), which allows to move a sibling node to an exact position between siblings.

### Expand on Subqueries ​

You can now expand to-one associations from [subqueries](/docs/java/working-with-cql/query-api#from-select) if the association is selected explicitly or implicitly via select all in the inner query:

java

```
CqnSelect booksOnCAP = Select.from(BOOKS).columns(
    b -> b.title(),
    b -> b.author())
   .search("CAP")
   .orderBy(b -> b.title())
   .limit(10);
Select.from(booksOnCAP).columns(
    b -> b.get("title"),
    b -> b.to("author").expand("name"));
```

### $expand on $apply in OData v4 ​

CAP Java now supports `$expand` of managed to-one associations in combination with non-aggregating [$apply](/docs/guides/protocols/odata#data-aggregation) transformations such as `filter`, `search`, `top`, `skip`, and `orderby`, as well as `hierarchy` transformations such as `TopLevels`, `ancestors`, and `descendants`:

http

```
GET /SalesOrganizations?$apply=
     ancestors($root/SalesOrganizations,SalesOrgHierarchy,ID
     /search(\"CAP\"),keep start)
     /com.sap.vocabularies.Hierarchy.v1.TopLevels(HierarchyNodes=$root/SalesOrganizations,HierarchyQualifier='SalesOrgHierarchy',NodeProperty='ID')
&$select=DistanceFromRoot,DrillState,LimitedDescendantCount,Name,ID&$top=10
&$expand=Superordinate($select=Name)
```

### SQL Window Functions ​

You can now use an [SQL window function](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-sql-reference-guide/windows-functions) to *partition* data and compute an aggregated value per partition without grouping the data. Use the new `over` method to turn an aggregate function into window function. The following example *partitions* the sales by region. For every partition the sum of sales are is computed but the raw amount is preserved:

java

```
Select.from(SALES)
      .columns(s -> s.region(),
               s -> s.saleId(),
               s -> s.amount(),
               s -> s.amount().sum().over(s.region()).as("sum"));
```

This query produces such a result:

| region | saleId | amount | sum |
| --- | --- | --- | --- |
| EU | eu1 | 10 | 60 |
| EU | eu2 | 30 | 60 |
| EU | eu3 | 20 | 60 |
| UK | uk1 | 90 | 90 |
| US | us1 | 5 | 20 |
| US | us2 | 15 | 20 |

### Expressions in Runtime Views ​

You can now use expressions in [runtime views](/docs/java/working-with-cql/query-execution#runtimeviews).

Runtime-view definition:

cds

```
@cds.persistence.skip
entity BooksView as projection on Books {
    id,
    toUpper(title) as title,
    author.forename || author.surname as author,
    (stock

Allowed query:

java

```
Select.from(BooksView).columns(
    b -> b.title(),
    b -> b.author(),
    b -> b.stock());
```

### Miscellaneous ​

- CAP Java now offers a typesafe API for the ChangeTracking Service which can be used to observe and customize detected changetracking entities.
- The `build` goal of the `cds-maven-plugin` can now be run from the root folder of the CAP Java project. It's no longer required to change into the `srv` folder to run this goal. It supports also the new parameter `goals` to let the user choose, which goals shall be executed to build the project.
- Event Handler methods can now take `CqnStatement` or one of its subtypes as argument. This works for events that operate on a `CqnStatement`, like all CRUD events or bound actions or functions. In addition, it's now also possible to use a `CqnStructuredTypeRef` as parameter type, which is useful, when handling a bound action.

## CAP Plugins ​

### Attachments: Multitenancy ​

[@cap-js/attachments](https://github.com/cap-js/attachments) now supports multitenancy with a shared object store instance. Within a shared object store instance, attachments are stored with tenant ID prefix to identify tenant-specific data.

## Tools ​

### Command-line formatter ​

The `format-cds` command-line formatter included in *@sap/cds-lsp* now considers ignore files (one of *.cdsignore* and *.gitignore*). Matching files will not be formatted.

[Learn more about the CDS Source Formatter.](/docs/tools/cds-editors#cds-formatter)

### CDS Plugin for Community IntelliJ IDEs ​

We got numerous feedback for our current [IntelliJ plugin](https://github.com/cap-js/cds-intellij) only supporting *commercial* versions of IntelliJ IDEs. Now, we publish a version 2 of the plugin as the first preview that supports the free *Community* editions of IntelliJ IDEs. It includes *all* features of our previous version.

This preview version is not available on the IntelliJ Marketplace. You need to install it manually from [Github](https://github.com/cap-js/cds-intellij/releases) via *Settings -> Plugins -> Config Wheel Icon (right to Marketplace and Installed) -> Install Plugin from Disk...*

Given the early stage, we would be happy if you try this out and give us [feedback](https://github.com/cap-js/cds-intellij/issues/new/choose). Please tag the issue with the new *2.x.x Community Edition* label.
