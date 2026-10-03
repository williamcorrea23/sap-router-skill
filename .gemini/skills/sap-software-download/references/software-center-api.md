# SAP for Me Software Center — service reference

Everything here was **verified live against the service during authoring**, signed in as an S-user with an
active download profile. Marked **[V]**. Where behaviour may vary by entitlement, that is stated.

Service root:

```
https://launchpad.support.sap.com/services/odata/svt/swdcuisrv/
```

OData v2, namespace `SVT_SWDC_UI_SRV`. `$metadata` is reachable unauthenticated-ish (it redirects to SSO if
you have no session) and is the fastest way to re-derive this file if SAP changes the model. **[V]**

> **Origin matters.** `me.sap.com/softwarecenter` embeds `launchpad.support.sap.com` in an **iframe**.
> Scripts, network logs and accessibility trees scoped to the top frame see the shell only. Issue these
> calls from a tab whose top document is on `launchpad.support.sap.com` so they are same-origin and the
> session cookie is sent. **[V]**

---

## Entity sets

Twenty-one sets exist. The ones that matter for operations: **[V]**

| Entity set | Use |
|---|---|
| `SearchResultSet` | Free-text search — the main entry point |
| `ObjectSet` | Full metadata for one downloadable object (by key) |
| `ObjectAttributeSet` | Attributes incl. `EQUIVALENT` cross-release mapping |
| `ObjectConditionSet` | Import conditions SPAM enforces |
| `ObjectPropertySet` | Additional properties |
| `DownloadItemSet` | Download items |
| `DownloadBasketItemSet` | Current Download Basket contents |
| `DownloadAuthProfileSet` | Your download authorization |
| `HierarchyItemSet` | The browse tree (Installations & Upgrades / by category) |
| `ObjectListItemSet` | Object lists within a node |
| `DownloadContentSet` | Content info |
| `SAPNotes`, `SideEffects` | Notes / side effects attached to an object |
| `SourcePackageSet` | Source packages |
| `ExportBasketItemSet`, `ExportActionLogSet` | Basket export + action log |
| `DownloadBasketITCMRefreshSet` | Basket refresh |
| `SAPNotesPriorityFilter`, `SAPNotesCategoryFilter`, `SAPNotesCountryFilter`, `SAPNotesComponentFilter` | Note filter value help |

Corresponding entity types drop the `Set` suffix and singularise (`SearchResult`, `Object`, `DownloadItem`, …).

---

## Search

```
GET /services/odata/svt/swdcuisrv/SearchResultSet
      ?SEARCH_STRING=<what you'd type in the UI>
      &SEARCH_MAX_RESULT=200
      &RESULT_PER_PAGE=200
      &$format=json
Accept: application/json
```

`$format=json` **works on this service** — unlike the SAP Notes `CorrInsSet` service, where it silently
returns zero rows. **[V]**

`SearchResult` fields: **[V]**

| Field | Notes |
|---|---|
| `Id` | Result index (`000004`) — positional, not stable |
| `Title` | **The filename**, e.g. `SAPK-74035INSTPI` |
| `Description` | Human text, e.g. `ST-PI 740: SP 0035` |
| `Infotype` | `Support Package`, `Installation Software Component`, `Maintenance Software Component`, … |
| `Fastkey` | **The 19-digit object key** — the identifier that matters |
| `DownloadDirectLink` | `https://softwaredownloads.sap.com/file/<Fastkey>` |
| `ContentInfoLink` | `https://me.sap.com/softwarecenter/object/<Fastkey>` |
| `ApplicationLink`, `PackApplicationLink`, `InfoObjectLink`, `SideEffectsLink`, `DependenciesLink` | Often empty |
| `SubtreeEvent`, `SearchResultDescr` | UI plumbing |

**Result sets mix families.** `SEARCH_STRING=ST-PI 740` returned 60 rows: 58 `Support Package`, 1
`Installation Software Component`, 1 `Maintenance Software Component`. Of the 58, only **35** matched the
mainline `^SAPK-740\d+INSTPI$` pattern. Always filter on the filename pattern for the delivery you want. **[V]**

---

## Navigating the add-on tree (nodes, not files)

`SearchResultSet` returns **navigation nodes** as well as files. A node has an **empty `Fastkey`** and a
populated **`SubtreeEvent`**. For add-ons this is the norm, not the exception: `ST-A/PI` returned 57 rows of
which only 3 were downloadable. **[V]**

Two discriminators live in those event strings: **[V]**

| Parameter | Values | Meaning |
|---|---|---|
| `V` | `INST` / `MAINT` | `Infotype` — Installation vs Maintenance Software Component |
| `SWTYPSC` | `N` / `X` | delivery type — **INSTALLATION** (SAINT) vs **EXCHANGE-UPGRADE** |
| `ENR` | 20-digit | software component release number |
| `TA` | `ACTUAL` | current vs archive view |

The events are **raw query strings, not OData**. Pass them verbatim; `$filter=Id eq '<event>'` returns 0
rows, as does `HierarchyItemSet?Id='<event>'`. **[V]**

```
# node -> child nodes (INSTALLATION / EXCHANGE-UPGRADE)
GET .../HierarchyItemSet?_EVENT=DISPHIER&EVENT=TREE&NE=NAVIGATE&ENR=<ENR>&V=INST&TA=ACTUAL&$format=json

# child node -> files.  This is DownloadItemSet, NOT ObjectListItemSet (which returns 0).
GET .../DownloadItemSet?_EVENT=LIST&EVENT=LIST&ENR=<ENR>&SWTYPSC=N&PECCLSC=NONE&V=INST&TA=ACTUAL&$format=json
```

`DownloadItemSet` rows carry `Fastkey`, `Title`, `Description`, `Filesize` and a path-style `Filename`
(e.g. `001/2025/0000000010/000000096533/003/KITABCA.SAR`). Feed `Fastkey` to `ObjectSet` for the checksum
and SPAM level, and to the download URL.

Verified on **ST-A/PI 01X_731**, `ENR=73555000100200023403`: **[V]**

| `SWTYPSC` | Node | Title | Fastkey | Bytes |
|---|---|---|---|---|
| `N` | INSTALLATION | `SAPKITABCA` | `0010000000965332025` | 77,646,332 |
| `X` | EXCHANGE-UPGRADE | `SAPK-01XCAINSSA` | `0010000001017592025` | 77,643,960 |

The two differ by **0.003 %** in size and are both valid `CAR 2.01` archives — size, type and checksum
cannot tell you that you took the wrong branch. Only the node can.

---

## Object metadata

```
GET /services/odata/svt/swdcuisrv/ObjectSet('<ObjectKey>')?$format=json
```

Live response for ST-PI 740 SP 0035, trimmed: **[V]**

```json
{
  "ObjectKey": "0010000000343432026",
  "Title": "ST-PI 740: SP 0035",
  "Status": "AVAILABLE",
  "StatusDescr": "The File is available to download",
  "FileType": "SAR",
  "FileSize": "11645 ",
  "FileName": "SAPK-74035INSTPI",
  "FileVersion": "002",
  "Checksum": "f414bf416b70649d43d5615db004688a80a4427e04a36f937ee9afa8e3cd3636",
  "PatchType": "CSP",
  "EpsFileName": "I710020751258_0179285.PAT",
  "PackageLevel": "0035",
  "ComponentRelease": "ST-PI 740",
  "MinimalBasisRelease": "740",
  "RequiredSpamVersion": "0081",
  "IsAbapObject": true,
  "CreatedOn": "/Date(1779350832000)/",
  "ChangedOn": "/Date(1782108443000)/"
}
```

Field notes:

- **`FileSize` is in KB and carries a trailing space** — trim before arithmetic. **[V]**
- **`Checksum` is SHA-256**, lowercase hex. **[V]**
- **`RequiredSpamVersion`** — take the **maximum across the whole queue**, not the last package.
- **`EpsFileName`** — the `.PAT` produced by `SAPCAR -xvf`; this is the name SPAM lists, not `FileName`.
- **`IsSupportPackage` was `false`** on a component SP whose `PatchType` is `CSP`. Do **not** branch on this
  flag — use `Infotype` from the search result or `PatchType`. **[V]**
- Dates are OData v2 `/Date(epoch_ms)/`.

### Navigation properties

```
GET /services/odata/svt/swdcuisrv/ObjectSet('<key>')/ObjectAttributes?$format=json
GET /services/odata/svt/swdcuisrv/ObjectSet('<key>')/ObjectConditions?$format=json
```

- **`ObjectAttributes`** — returned 3 rows for SP35, including an `EQUIVALENT` attribute whose value encoded
  `ST-PI,758:SAPK-75802INSTPI,0002` — i.e. **the same correction on ST-PI 758 SP02**. Use this to keep a
  mixed-release landscape consistent. Key shape:
  `ObjectAttributeSet(ObjectKey='…',AttributeId='EQUIVALENT',AttributeValue='…')` **[V]**
- **`ObjectConditions`** — returned 1 row keyed
  `ObjectConditionSet(ObjectKey='…',ConditionSet='01',ComponentCategory='01',SoftwareComponent='ST-PI',AlternativeSet='00',Release='740',PackageCategory='01')`.
  These are the conditions SPAM evaluates when building a queue. **[V]**

> `DownloadItemSet?$filter=Fastkey eq '<key>'` returned **200 with an empty result set** — `DownloadItemSet`
> is not a substitute for `ObjectSet`. Use `ObjectSet` for metadata. **[V]**

---

## Authorization and basket

```
GET /services/odata/svt/swdcuisrv/DownloadAuthProfileSet?$format=json
GET /services/odata/svt/swdcuisrv/DownloadBasketItemSet?$format=json
```

`DownloadAuthProfileSet` returns your S-user with `Active: true` when downloads are permitted — a cheap
precheck that separates "not entitled" from "technically broken". `DownloadBasketItemSet` returns the
basket contents (empty array when the basket is empty). **[V]**

---

## Download

| | |
|---|---|
| Direct file | `https://softwaredownloads.sap.com/file/<ObjectKey>` |
| Object page | `https://me.sap.com/softwarecenter/object/<ObjectKey>` |

The direct link **redirects into SP-initiated SAML at `accounts.sap.com/saml2/idp/sso`**. Whether that
needs a human depends entirely on the **credential presented**: **[V]**

| Credential | Result |
|---|---|
| Browser session cookies | Interactive SAML. Stalls under browser automation (reproduced twice on a session whose `DownloadAuthProfileSet` showed `Active: true` — so it is the SSO flow, not entitlement). Account picker appears when one e-mail maps to several S-users. |
| **X.509 client certificate** | **Silent authentication; file returned.** Verified: 7 packages, 58,917,370 bytes, every SHA-256 matching the service. |

### The chain, hop by hop (cert auth) **[V]**

```
GET  https://softwaredownloads.sap.com/file/<key>
  → 302 https://origin-az.softwaredownloads.sap.com/tokengen/?file=<key>
       200 text/html  ~12.8 KB  — auto-POST form
       action = https://accounts.sap.com/saml2/idp/sso
       fields = RelayState (~126 B), SAMLRequest (~11.7 KB)

POST https://accounts.sap.com/saml2/idp/sso
       200 text/html  ~28.2 KB  — auto-POST form  (cert authenticated silently)
       action = https://origin-az.softwaredownloads.sap.com/tokengen/?file=<key>&downloadId=<uuid>
       fields = utf8, authenticity_token (~88 B), SAMLResponse (~6.9 KB), RelayState

POST <that action>
       200 application/octet-stream   ← the .SAR
       final url https://softwaredownloads.sap.com/?file=<key>&downloadId=<uuid>&v=
```

Notes for implementers:

- The `downloadId` UUID is **minted by the IdP hop** and appended to the form action — you cannot construct
  it in advance, which is why the chain must be walked rather than short-circuited.
- `curl -L` follows redirects but **does not submit forms**. Parse each response's `<form action>` and
  `<input name/value>`, HTML-unescape the action, and re-POST. Two form POSTs total.
- Carry a **cookie jar** across all hops (`-b`/`-c`).
- The page says *"Since your browser does not support JavaScript, you must press the Continue button"* —
  that is the no-JS fallback, and it is exactly what makes the flow scriptable.
- Keep the P12 passphrase out of the process list: put `cert-type`/`cert` in a `0600` curl config file and
  pass `-K`, rather than `--cert` on the command line.
- **The OData service above accepts the same certificate**, so the entire search → qualify → download →
  verify loop runs headless.

### Verifying the artefact

- SAPCAR magic: the file begins with `CAR 2.01`.
- It contains one or more `EPS/in/<name>.PAT` entries. **`EpsFileName` from `ObjectSet` names one of them,
  not necessarily the only one** — ST-PI 740 SP30 and SP33 each contain two PATs. **[V]**

> Contrast with the **TCI transport packages** in
> [sap-security-patch](../../sap-security-patch/SKILL.md), which were characterised as SSO-gated on the
> basis of browser behaviour only. That conclusion should be re-tested with certificate auth before being
> relied on — the mechanism here turned out to be scriptable once the credential changed.

---

## Re-deriving this file

If SAP changes the model, re-extract from a `launchpad.support.sap.com` tab:

```js
// entity sets + types
const t = await (await fetch('/services/odata/svt/swdcuisrv/$metadata')).text();
[...t.matchAll(/EntitySet Name="([A-Za-z0-9_]+)"/g)].map(m => m[1]);

// fields of one entity type
const seg = t.slice(t.indexOf('EntityType Name="Object"'), t.indexOf('</EntityType>', t.indexOf('EntityType Name="Object"')));
[...seg.matchAll(/Property Name="([A-Za-z0-9_]+)" Type="Edm\.([A-Za-z]+)"/g)].map(m => m[1] + ':' + m[2]);
```
