# Repository implementation patterns

Use these repositories as bounded implementation references. Pin reviewed commits before adopting behavior, retain license notices where required, and do not vendor external source into the skill.

## Responsibility matrix

| Repository | Role in this skill | Required boundary |
|---|---|---|
| [abapGit/abapGit](https://github.com/abapGit/abapGit/tree/309bdca11519501509fd9e0737dceef362c1c91e) | Canonical SSFO serialization/deserialization behavior | Base native XML claims on a real SAP round-trip |
| [pokrakam/SAPlink-Git](https://github.com/pokrakam/SAPlink-Git/tree/1fdff157c067fd8cc965be2f42077d09b03d8d73) | Legacy independent confirmation of Smart Forms APIs | GPL reference only; do not copy into differently licensed code |
| [arc-mcp/arc-1](https://github.com/arc-mcp/arc-1/tree/7b6fc90b27412cf73613dc6eb1aece0cdbcce26d) | Governed SAP ADT inspection, ABAP driver edits, and transport evidence | SSFO import requires a reviewed custom tool or SAP fallback |
| [GoogleCloudPlatform/sap-genai-samples](https://github.com/GoogleCloudPlatform/sap-genai-samples/tree/d7c3fe6842bcd6019b897b00d43afb131fc5f0f9) | PDF/unstructured input to JSON-schema output | FormSpec remains schema-validated and human-reviewed |
| [abap-ai/llm_client](https://github.com/abap-ai/llm_client/tree/960b4a612c88ffec13e63e3ed8ca91adc2077818) | Optional in-ABAP structured output and tool calls | Apply provider/version/security limitations |
| [abap-ai/mcp](https://github.com/abap-ai/mcp/tree/423fa4cf30c09637e1772c196120c978c59b5cf2) | MCP tools, output schemas, tasks, and DDIC-derived schemas | Implement a real persistent protocol server, not a one-shot status print |

## abapGit SSFO lifecycle

Model the adapter on [`zcl_abapgit_object_ssfo`](https://github.com/abapGit/abapGit/blob/309bdca11519501509fd9e0737dceef362c1c91e/src/objects/zcl_abapgit_object_ssfo.clas.abap):

1. Serialize by loading the SAP form with `CL_SSF_FB_SMART_FORM`.
2. Call `XML_DOWNLOAD` into an iXML document.
3. Normalize volatile package/user/date/time metadata, stabilize IDs/IDREFs, sort captions/text metadata, and externalize ABAP code sections as abapGit does.
4. Preserve the Smart Forms and IFR namespaces.
5. Deserialize only after package/transport approval: create the TADIR entry, enqueue the form, call `XML_UPLOAD`, store it active, and dequeue it.
6. Verify existence in `STXFADM`, active state through `SSF_STATUS_INFO`, generated function-module resolution, and a test execution.

The XML returned by SAP is the source of truth. Offline parsing proves only structural plausibility.

## SAPlink cross-check

Use [`ZSAPLINK_SMARTFORM`](https://github.com/pokrakam/SAPlink-Git/blob/1fdff157c067fd8cc965be2f42077d09b03d8d73/src/zsaplink_smartform.clas.abap) to cross-check the classic topology:

- existence lookup in `STXFADM`;
- `CL_SSF_FB_SMART_FORM` load plus `XML_DOWNLOAD`;
- iXML DOM conversion and namespace handling;
- overwrite/delete safeguards followed by XML upload.

SAPlink is a legacy GPL implementation. Reference its behavior; do not copy its code without an explicit license review.

## AI-to-FormSpec extraction

Follow the structured-output pattern from Google Cloud SAP GenAI Samples:

1. Define the current FormSpec JSON schema first.
2. Submit PDF/text/image evidence with explicit page coordinates and allowed field types.
3. Parse only schema-conforming output; in ABAP, the sample uses `/UI2/CL_JSON=>DESERIALIZE`.
4. Retain the original evidence, confidence, and review decision for every inferred dynamic field.
5. Reject unknown top-level schemas instead of silently translating an obsolete FormSpec.

If inference runs inside ABAP, `abap-ai/llm_client` provides structured output and tool calls across supported providers. Add authorization, usage limits, secret handling through approved destinations/SM59, timeouts, and provider-specific fallbacks. Do not send business documents to an external model without data-governance approval.

## MCP and SAP orchestration

Use ARC-1 for capabilities it exposes through ADT. Keep writes opt-in, restrict allowed packages, and require separate transport-write permission. For SSFO, choose one reviewed path:

- custom ARC-1 tool that calls an approved ABAP wrapper around the abapGit lifecycle;
- abapGit import in SAP;
- controlled SAP GUI import when no API adapter exists.

An MCP implementation must remain alive and support initialization, tool discovery, tool calls, structured errors, and graceful shutdown. Use `abap-ai/mcp` patterns for tools, optional output schemas, DDIC schema generation, and long-running tasks. A Python module that prints “running” and exits is not an MCP server.

## Acceptance evidence

Do not claim completion until all evidence exists:

- validated FormSpec with zero unresolved review flags;
- native XML preflight and consistent canonical name;
- real DEV import result, lock/transport trace, and active status;
- ABAP driver syntax/activation and generated function-module resolution;
- rendered PDF from SAP with representative data;
- visual diff covering geometry, text, graphics, borders, wrapping, and pagination;
- human acceptance plus rollback instructions.
