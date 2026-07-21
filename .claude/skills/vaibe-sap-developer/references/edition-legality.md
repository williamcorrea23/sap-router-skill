# Environment Edition Legality Matrix
Parent skill: vaibe-sap-developer
Consulted by: Phase 1 Step 1 (question relevance + option filtering, using full cumulative answer context — not just the immediately preceding question) and Phase 3 validation.

Legend: ✅ legal / ⚠ allowed but discouraged (Clean Core preference, not a hard block) / ❌ not legal under strict Clean Core + ABAP Cloud compliance — drop the option from the question entirely, don't generate it and caveat afterward.

| Dimension | On-Premise | Cloud Private Edition | Cloud Public Edition | BTP ABAP Environment |
|---|---|---|---|---|
| Basis/release patch level exposed to developer | ✅ ask Q | ✅ ask Q | ❌ drop Q (continuous delivery) | ❌ drop Q (continuous delivery) |
| AMDP / native SQL | ✅ | ✅ | ❌ not a released API | ❌ not a released API |
| Standard OO class + classic ALV report | ✅ | ⚠ allowed, Clean Core prefers RAP | ❌ classic Dynpro/ALV UI unavailable | ❌ unavailable |
| RAP — Managed | ✅ | ✅ (preferred) | ✅ (only RAP option offered) | ✅ (only RAP option offered) |
| RAP — Unmanaged | ✅ | ⚠ allowed, discouraged | ❌ not exposed in key-user/developer extensibility | ❌ not exposed |
| Classic BAdI / user-exit / implicit enhancement | ✅ | ✅ (prefer released BAdIs) | ❌ only released BAdIs from extensibility catalog | ❌ no classic enhancement spots |
| OData V2 | ✅ | ✅ | ❌ V4-only via RAP | ⚠ rare, V4 is the default path |
| OData V4 (RAP-based) | ✅ | ✅ | ✅ default | ✅ default |
| IDoc processing / retrigger | ✅ | ✅ | ✅ via released APIs only, no custom enhancement spot | ❌ standalone BTP ABAP systems generally don't run classic IDoc infrastructure |
| ABAP Unit testing | ✅ | ✅ | ✅ | ✅ |
| New custom Function Module | ✅ | ✅ | ❌ not a released API — use Managed RAP/CDS instead | ❌ not a released API |
| Smart Forms / Adobe Forms / SAPscript | ✅ | ✅ | ❌ no classic form runtime | ❌ no classic form runtime |
| Classic Dynpro screen / WebDynpro ABAP | ✅ | ✅ | ❌ no classic UI runtime | ❌ no classic UI runtime |
| Flexible Workflow (standard scenarios, key-user adapted) | ✅ | ✅ | ✅ (event-trigger only, no custom ABAP step logic) | ❌ no workflow engine in standalone BTP ABAP systems |
| Classic Business Workflow (SWF, Workflow Builder) | ✅ | ✅ | ❌ Workflow Builder/BOR not available | ❌ not available |
| New custom authorization object (SU21) | ✅ | ✅ | ⚠ admin/Customizing activity, not key-user extensibility — confirm access | ⚠ same, confirm access |
| Custom Fields / Custom Logic key-user extensibility | ✅ available, rarely needed (direct dev access exists) | ✅ available, rarely needed | ✅ this is the primary legal customization route here | ✅ available via developer extensibility |
| Custom DDIC table/structure/lock object/number range | ✅ | ✅ | ✅ (as persistence behind a Custom Business Object) | ✅ |
| ALE config (WE20/WE21/BD64) / new IDoc type (WE30/31) | ✅ | ✅ | ⚠ prefer extending a released IDoc/message type over a new custom one | ❌ no ALE/IDoc infrastructure |
| ALV (classic FM-based or CL_SALV_TABLE/CL_GUI_ALV_GRID) | ✅ | ✅ | ❌ SAP GUI control framework unavailable — use Fiori List Report instead | ❌ unavailable |
| Background job scheduling (JOB_OPEN/SUBMIT/CLOSE) | ✅ | ✅ | ✅ | ✅ |
| Outbound HTTP via classic `cl_http_client` | ✅ | ✅ | ❌ not released — use `cl_web_http_client_manager` | ❌ not released |
| Outbound HTTP via `cl_web_http_client_manager` (released API) | ✅ | ✅ | ✅ | ✅ |
| SOAP proxy consumption (SE80 from WSDL) | ✅ | ✅ | ❌ REST/OData expected instead | ❌ unavailable |
| SAP Query / ABAP Query (SQ01/02/03) | ✅ | ✅ | ❌ classic SAP GUI tool unavailable | ❌ unavailable |
| BRFplus custom application development | ✅ | ✅ | ⚠ usually pre-built into specific scenarios only, confirm workbench access | ✅ |
| PFCG role assembly (classic single/composite role) | ✅ | ✅ | ❌ use Business Catalog/Business Role model instead | ✅ (still a real ABAP system) |
| Business Catalog / Business Role assignment | n/a (not the cloud model) | n/a | ✅ this is the role model here | n/a |

## How to apply this during queue-building (Phase 1, Step 1)
For every candidate question, check it against this table using **all answers collected so far**, not just the answer to the question immediately before it — environment edition is usually answered first (Q1) but keeps affecting relevance and option sets many questions later.

- If a dimension is ❌ for the current environment: remove that option from the question entirely (e.g. "Unmanaged RAP" never appears as a choice once environment = Cloud Public Edition); if removing options leaves only one legal choice, drop the question and treat that choice as resolved instead of asking it.
- If a dimension is ⚠: keep the option available, but Phase 3 validation should prefer/flag the Clean Core alternative in the generated code rather than silently using the discouraged pattern.
- If a whole artifact-category bucket collapses to no legal members under the current environment (e.g. "Data layer (CDS/AMDP)" bucket loses AMDP under Public Edition but CDS itself stays legal), filter the *exact type* options inside that bucket rather than dropping the bucket itself.
- If **every** option inside a bucket is ❌ for the current environment (e.g. the "Output/Legacy (Forms/Dynpro/WebDynpro)" bucket under Public Edition or BTP), don't silently drop the question or auto-resolve it — surface a blocking note that the whole category is unavailable there and point to the Clean Core-legal alternative (Fiori Elements on RAP/OData) before generating anything.

## Caveat
This matrix reflects general Clean Core / ABAP Cloud principles and may lag actual released-API catalog changes on a specific tenant. On a genuinely borderline case, generate the most conservative (most-likely-legal) pattern and say so explicitly — don't assert legality with more confidence than this table warrants.
