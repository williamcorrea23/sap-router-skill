# Smart Form SSFO XML Node Mapping

Mapping matrix from document layout elements to SSFO XML nodes:

| Document Element | FormSpec Node Type | SSFO XML Node | SAP Smart Form Target |
|---|---|---|---|
| Page Header / Title | `TEXT` | `<NODE><TYPE>TEXT</TYPE></NODE>` | Header Secondary Window |
| Body Paragraph | `TEXT` | `<NODE><TYPE>TEXT</TYPE></NODE>` | Main / Secondary Window |
| Table Grid | `TABLE` | `<NODE><TYPE>TABLE</TYPE></NODE>` | Main Window Table Node |
| Repeating Line Item | `LOOP` | `<NODE><TYPE>LOOP</TYPE></NODE>` | Table Item Loop (`INTO GS_ITEM`) |
| Page Break | `COMMAND` | `<NODE><TYPE>COMMAND</TYPE></NODE>` | Page Break Command |
| Conditional Block | `ALTERNATIVE` | `<NODE><TYPE>ALTERNATIVE</TYPE></NODE>` | IF/ELSE Alternative Node |
| Company Logo / Graphic | `GRAPHIC` | `<NODE><TYPE>GRAPHIC</TYPE></NODE>` | Graphic Node (`GRAPHICS/BMAP`) |
| Address Block | `ADDRESS` | `<NODE><TYPE>ADDRESS</TYPE></NODE>` | SADR / Central Address Node |
