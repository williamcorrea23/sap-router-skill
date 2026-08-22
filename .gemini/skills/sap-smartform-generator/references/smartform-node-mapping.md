# Native Smart Form mapping

Map document semantics onto a native XML export from the target SAP system. Node names, generated IDs, references, and ordering are release-specific; the generic mappings below are conceptual and are not a substitute for `CL_SSF_FB_SMART_FORM->XML_DOWNLOAD`.

| Document element | FormSpec intent | Native Smart Forms concept | Validation evidence |
|---|---|---|---|
| Page header/title | `TEXT` | Secondary window with text nodes | Position, first/subsequent-page condition, typography |
| Body paragraph | `TEXT` | Text node in MAIN or a secondary window | Text style, wrapping, dynamic symbols |
| Table grid | `TABLE` | Template/table section and cells | Widths, row heights, borders, header repetition |
| Repeating item | `LOOP` | Loop/table processing node | DDIC table/work area and overflow behavior |
| Page break | `COMMAND` | Command node | Page transition in rendered PDF |
| Conditional block | `ALTERNATIVE` | Alternative/condition node | Both branches tested with representative data |
| Logo/photo | `GRAPHIC` | Graphic node using SAP graphic/DMS content | Real image, resolution, scaling, alignment |
| Address | `ADDRESS` | Address node or explicit text mapping | Correct source and country formatting |
| Footer/page count | `TEXT` | Footer window with `SFSY` symbols | Current/total page verified in spool/PDF |

## Native artifact invariants

- Root local name: `SMARTFORM`.
- Smart Forms namespace: `urn:sap-com:SmartForms:2000:internal-structure`.
- Default IFR namespace normally present: `urn:sap-com:sdixml-ifr:2000`.
- Header `FORMNAME` and every repeated `FORMNAME` must match the canonical form name.
- At least one main window must have internal name `MAIN` and main-window type.
- Interface parameters, global data, symbols in text, loop work areas, and driver parameters must agree.
- SAP-generated node IDs and references must remain internally consistent.

Do not emit a generic `<NODE><TYPE>...</TYPE></NODE>` tree or an `<abapGit><SF>` wrapper as native SSFO. Use a real export as the structural baseline, then prove import and activation inside SAP.
