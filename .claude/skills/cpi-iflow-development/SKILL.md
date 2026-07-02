---
name: cpi-iflow-development
description: >-
  SAP CPI iFlow development — integration flow design, Groovy scripting, XSLT/Message
  mappings, content modifier, router, ZIP packaging, deploy via MCP. Use when creating
  CPI iFlows, writing Groovy scripts for CPI, packaging iFlows as ZIP, deploying to
  SAP CPI tenant, or debugging CPI message processing failures.
trigger:
  - CPI iFlow development
  - Groovy script CPI
  - integration flow design
  - XSLT mapping
  - message mapping
  - content modifier
  - router pattern
  - iFlow ZIP packaging
  - deploy iFlow
  - CPI message processing
  - XmlSlurper
  - value mapping API
  - exception subprocess
---

# SAP CPI iFlow Development

Full development lifecycle for SAP Cloud Integration (CPI) iFlows — from source code to deployed integration.

## Prerequisites

- SAP BTP subaccount with Integration Suite enabled
- Service Key for Process Integration Runtime (OAuth2 client_credentials)
- Environment vars set: `CPI_TENANT_URL`, `CPI_TOKEN_URL`, `CPI_CLIENT_ID`, `CPI_CLIENT_SECRET`
- Groovy 2.4+ syntax knowledge (CPI uses Nashorn engine, ECMAScript 5.1 dialect)
- Access to CPI Web UI for monitoring and trace

## iFlow ZIP Structure

```
my-iflow.zip/
├── META-INF/MANIFEST.MF
└── src/main/resources/
    ├── flow.xml                  ← Main integration flow definition
    ├── script/*.groovy           ← Groovy scripts
    ├── mapping/*.xslt            ← XSLT transformations
    ├── mapping/*.mmap            ← Message mappings
    ├── resources/*.xsd           ← EDI/XML schemas
    └── parameters.prop           ← Externalized parameters
```

## Step 1 — Create iFlow Source Files

Create the project directory and core files:

```bash
mkdir -p /opt/data/iflows/my-integration-flow/{src/main/resources/script,src/main/resources/mapping}
```

Write the `MANIFEST.MF`:

```
Manifest-Version: 1.0
Bundle-SymbolicName: my_integration_flow
Bundle-Version: 1.0.0
Bundle-Name: My Integration Flow
```

## Step 2 — Write flow.xml

Define sender channel, integration process steps, and receiver channel:

```xml
<IntegrationFlow id="my_integration_flow" version="1.0">
  <Sender id="sender_1" type="HTTPS" direction="Inbound">
    <Address>/process/order</Address>
    <Authentication>Basic</Authentication>
  </Sender>
  <IntegrationProcess id="process_1" name="Process Order">
    <ContentModifier id="cm_1" name="Set Headers">
      <Property name="OrderId" source="body" sourceField="orderId"/>
    </ContentModifier>
    <GroovyScript id="script_1" name="Transform Payload"
                  scriptPath="script/process-data.groovy"/>
    <RequestReply id="rr_1" name="Call S/4HANA">
      <Receiver ref="receiver_1"/>
      <Timeout>60000</Timeout>
    </RequestReply>
    <Router id="router_1" name="Route by Status">
      <Condition expression="${property.Status} = 'OK'" targetStep="end_ok"/>
      <Condition expression="${property.Status} = 'ERROR'" targetStep="end_error"/>
    </Router>
  </IntegrationProcess>
  <Receiver id="receiver_1" type="ODataV2" direction="Outbound">
    <Address>${destination.S4HANA}/sap/opu/odata/sap/Z_ORDER_SRV</Address>
  </Receiver>
</IntegrationFlow>
```

## Step 3 — Write Groovy Scripts

**XML-to-JSON transform with error handling:**

```groovy
import com.sap.gateway.ip.core.customdev.util.Message
import com.sap.it.api.ITApiFactory
import com.sap.it.api.msglog.MessageLog

def Message processData(Message message) {
    def log = message.getMessageLog()
    try {
        def body = message.getBody(java.lang.String)
        if (!body?.trim()) throw new IllegalArgumentException("Empty body")
        def xml = new XmlSlurper().parseText(body)
        message.setBody("""{"orderId":"${xml.orderId.text()}","customer":"${xml.customer.text()}"}""")
        message.setHeader("Content-Type", "application/json")
        log.setStringProperty("Status", "COMPLETED")
    } catch (Exception e) {
        log.setStringProperty("Status", "FAILED")
        log.addAttachmentAsString("error.txt", e.getMessage(), "text/plain")
        throw e
    }
    return message
}
```

**Value mapping lookup:** `ITApiFactory.getApi(ValueMappingApi).getMappedValue('COUNTRY_CODES', 'SAP_Internal', 'ISO', countryCode)`

## Step 4 — Package as ZIP

```bash
python /opt/data/scripts/cpi_iflow_packager.py create \
  --name my-integration-flow \
  --flow /opt/data/iflows/my-integration-flow/src/main/resources/flow.xml \
  --scripts /opt/data/iflows/my-integration-flow/src/main/resources/script/process-data.groovy \
  --output /opt/data/iflows/my-iflow.zip
```

Validate the ZIP structure:

```bash
python /opt/data/scripts/cpi_iflow_packager.py validate --input /opt/data/iflows/my-iflow.zip
```

## Step 5 — Lint Before Deploy

```bash
# Lint Groovy script
cpi_lint --code "$(cat /opt/data/iflows/my-integration-flow/src/main/resources/script/process-data.groovy)"

# Lint flow.xml
cpi_lint --code "$(cat /opt/data/iflows/my-integration-flow/src/main/resources/flow.xml)"
```

Key lint rules: hardcoded passwords → error, no exception subprocess → warning,
`new File()` in Groovy → error, `println()` → info (use MessageLog).

## Step 6 — Deploy to CPI Tenant

```bash
# List existing packages
cpi_mcp --tool list_integration_flows

# Deploy iFlow from source ZIP
cpi_mcp --tool deploy_artifact --params '{"artifactId":"my_iflow","artifactType":"IntegrationFlow"}'

# Check failed messages
cpi_mcp --tool get_runtime_stats --params '{"artifactName":"my_iflow"}'
```

## Integration Patterns

- **Sync Request-Reply**: HTTPS → Groovy (transform) → RequestReply (OData) → Groovy (response) → HTTPS response
- **Async with Retry**: SFTP → ContentModifier (correlation ID) → Router → Groovy → RequestReply (IDoc) → Retry (3x/5min) → SFTP archive
- **Splitter-Gather**: HTTPS (batch) → Splitter → RequestReply (BAPI per record) → Gather → Groovy (aggregate) → HTTPS response

## CPI Constraints

- iFlow design-time size: ~10 MB
- Message size: 100 MB max
- Groovy execution timeout: 5 min
- External call timeout: 10 min
- Max parallel branches: 50

## Pitfalls

- **Groovy Sandbox blocks file I/O** — Cause: CPI runs Groovy in Nashorn sandbox, `new File()` is blocked. Solution: Use Data Store or Header/Property for persistence.
- **XmlSlurper vs XPath** — Cause: javax XPath is restricted in sandbox. Solution: Use `new XmlSlurper().parseText(body)` for XML navigation.
- **Content Modifier expression syntax** — Cause: Wrong variable syntax causes silent failures. Solution: Use `${in.body}` not `${message.body}`; use `${property.X}` for properties.
- **Body type mismatch** — Cause: Body can be String, InputStream, or byte[]. Solution: Always cast explicitly: `message.getBody(java.lang.String)`.
- **Content-Type header lost after transform** — Cause: Setting body overrides headers. Solution: Set `Content-Type` header AFTER calling `message.setBody()`.
- **Groovy timeout on large payloads** — Cause: 5-min script timeout. Solution: Split long operations across multiple iFlow steps; use Splitter for batch processing.
- **Hardcoded credentials** — Cause: Passwords in Groovy scripts. Solution: Use Secure Parameters or OAuth2 credentials from Security Material.

## Verification

1. **Lint passes**: `cpi_lint` returns zero errors on all scripts and flow.xml
2. **ZIP validates**: Packager `validate` command exits 0
3. **Deploy succeeds**: `cpi_mcp get_runtime_stats` shows artifact in "Started" state
4. **Test message flows**: Send test payload via HTTPS endpoint, check CPI Web UI → Monitor → Messages for successful processing
5. **Trace enabled**: CPI Web UI → Monitor → Trace shows input/output payloads at each step
6. **Error subprocess works**: Inject invalid payload, verify exception subprocess triggers and MessageLog shows "FAILED" status
