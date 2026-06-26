---
name: cpi-iflow-development
description: SAP CPI iFlow development — integration flow design, Groovy scripting, XSLT/Message mappings, content modifier, router, ZIP packaging, deploy via MCP, iFlow structure, CPI best practices. Use when creating CPI iFlows, writing Groovy scripts for CPI, packaging iFlows as ZIP, deploying to SAP CPI tenant, or debugging CPI message processing failures.
---

# SAP CPI iFlow Development

Full development lifecycle for SAP Cloud Integration (CPI) iFlows — from source code to deployed integration.

## iFlow ZIP Structure

```
my-iflow.zip/
├── META-INF/
│   └── MANIFEST.MF                         ← Bundle metadata
├── src/
│   └── main/
│       └── resources/
│           ├── flow.xml                     ← Main integration flow
│           ├── script/
│           │   ├── process-data.groovy      ← Groovy scripts
│           │   └── validate-input.groovy
│           ├── mapping/
│           │   ├── field-mapping.xslt       ← XSLT transformations
│           │   └── order-to-invoice.mmap    ← Message mappings
│           ├── resources/
│           │   ├── edifact-schema.xsd       ← EDI schemas
│           │   └── wsdl/
│           │       └── partner-service.wsdl ← WSDL files
│           ├── value-mapping/
│           │   └── country-codes.vmap       ← Value mappings
│           ├── parameters.prop              ← Externalized parameters
│           └── security/
│               └── keystore.jks             ← (if bundled)
```

## MANIFEST.MF

```
Manifest-Version: 1.0
Created-By: SAP Router Orchestrator CPI Packager
Bundle-SymbolicName: my_integration_flow
Bundle-Version: 1.0.0
Bundle-Name: My Integration Flow
Bundle-Vendor: company.com
```

## flow.xml Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<IntegrationFlow
  xmlns="http://xmlns.sap.com/CPI/IntegrationFlow"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  id="my_integration_flow"
  version="1.0"
  senderId="sender_1"
  receiverId="receiver_1">

  <!-- Sender channel -->
  <Sender id="sender_1" type="HTTPS" direction="Inbound">
    <Address>/process/order</Address>
    <Authentication>Basic</Authentication>
    <CSRFProtected>true</CSRFProtected>
  </Sender>

  <!-- Integration Process -->
  <IntegrationProcess id="process_1" name="Process Order">
    <!-- Steps execute in order -->

    <ContentModifier id="cm_1" name="Set Headers">
      <Header name="Content-Type">application/json</Header>
      <Property name="OrderId" source="body" sourceField="orderId"/>
    </ContentModifier>

    <GroovyScript id="script_1" name="Transform Payload"
                  scriptPath="script/process-data.groovy"/>

    <RequestReply id="rr_1" name="Call SAP S/4HANA">
      <Receiver ref="receiver_1"/>
      <Timeout>60000</Timeout>
    </RequestReply>

    <Router id="router_1" name="Route by Status">
      <Condition expression="${property.Status} = 'OK'"
                 targetStep="end_ok"/>
      <Condition expression="${property.Status} = 'ERROR'"
                 targetStep="end_error"/>
    </Router>
  </IntegrationProcess>

  <!-- Receiver channel -->
  <Receiver id="receiver_1" type="ODataV2" direction="Outbound">
    <Address>${destination.S4HANA}/sap/opu/odata/sap/Z_ORDER_SRV</Address>
    <Authentication>Basic</Authentication>
  </Receiver>
</IntegrationFlow>
```

## Groovy Scripts for CPI

### Basic Script Template

```groovy
import com.sap.gateway.ip.core.customdev.util.Message
import java.util.HashMap

def Message processData(Message message) {
    // Get message body
    def body = message.getBody(java.lang.String) as String

    // Get headers and properties
    def headers = message.getHeaders()
    def properties = message.getProperties()
    def orderId = properties.get("OrderId")

    // Transform payload
    def xml = new XmlSlurper().parseText(body)
    def result = """{
        "orderId": "${orderId}",
        "customer": "${xml.customer.text()}",
        "items": ${xml.items.item.size()}
    }"""

    // Set transformed body
    message.setBody(result)

    // Set response headers
    message.setHeader("Content-Type", "application/json")
    message.setProperty("ProcessedAt", new Date().format("yyyy-MM-dd'T'HH:mm:ss"))

    return message
}
```

### XML Parsing (XmlSlurper)

```groovy
import com.sap.gateway.ip.core.customdev.util.Message

def Message parseXML(Message message) {
    def body = message.getBody(String)
    def order = new XmlSlurper().parseText(body)

    // Navigate XML
    def customerName = order.header.customerName.text()
    def lineItems = order.items.item

    def json = new groovy.json.JsonBuilder()
    json {
        customer customerName
        itemCount lineItems.size()
        items lineItems.collect { item ->
            [
                material: item.material.text(),
                quantity: item.quantity.text().toInteger(),
                price: item.price.text().toBigDecimal()
            ]
        }
    }

    message.setBody(json.toPrettyString())
    message.setHeader("Content-Type", "application/json")
    return message
}
```

### JSON Processing

```groovy
import com.sap.gateway.ip.core.customdev.util.Message
import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def Message enrichJSON(Message message) {
    def body = message.getBody(String)
    def json = new JsonSlurper().parseText(body)

    // Add enrichment fields
    json.processedAt = new Date().format("yyyy-MM-dd'T'HH:mm:ss.SSSZ")
    json.source = "CPI"

    // Add calculation
    json.items.each { item ->
        item.totalPrice = item.quantity * item.price
    }

    message.setBody(JsonOutput.toJson(json))
    return message
}
```

### HTTP Call from Groovy

```groovy
import com.sap.gateway.ip.core.customdev.util.Message
import groovy.json.JsonSlurper

def Message callExternalAPI(Message message) {
    // Read destination from CPI header
    def destUrl = message.getProperties().get("SAP_S4HANA_URL")

    // Make HTTP GET call
    def connection = new URL(destUrl + "/sap/opu/odata/sap/Z_MATERIAL_SRV/MaterialSet?\$top=10").openConnection()
    connection.setRequestMethod("GET")
    connection.setRequestProperty("Accept", "application/json")
    connection.setRequestProperty("Authorization", message.getHeaders().get("Authorization"))

    def responseCode = connection.getResponseCode()
    if (responseCode == 200) {
        def responseBody = connection.getInputStream().getText()
        message.setBody(responseBody)
    } else {
        throw new Exception("HTTP call failed with code: ${responseCode}")
    }

    return message
}
```

### Error Handling

```groovy
import com.sap.gateway.ip.core.customdev.util.Message
import com.sap.it.api.ITApiFactory
import com.sap.it.api.msglog.MessageLog

def Message processWithErrorHandling(Message message) {
    def messageLog = message.getMessageLog()

    try {
        def body = message.getBody(String)
        if (!body || body.trim().isEmpty()) {
            throw new IllegalArgumentException("Empty message body")
        }

        messageLog.setStringProperty("Status", "PROCESSING")
        // Process logic...
        messageLog.setStringProperty("Status", "COMPLETED")

    } catch (Exception e) {
        messageLog.setStringProperty("Status", "FAILED")
        messageLog.setStringProperty("Error", e.getMessage())
        messageLog.addAttachmentAsString("error-details.txt",
            "Error: ${e.getMessage()}\nStack: ${e.getStackTrace().join('\n')}",
            "text/plain")

        // Re-throw to trigger exception subprocess
        throw e
    }

    return message
}
```

### Value Mapping Lookup

```groovy
import com.sap.gateway.ip.core.customdev.util.Message
import com.sap.it.api.ITApiFactory
import com.sap.it.api.mapping.ValueMappingApi

def Message mapValues(Message message) {
    def valueMappingApi = ITApiFactory.getApi(ValueMappingApi)
    def body = message.getBody(String)
    def json = new groovy.json.JsonSlurper().parseText(body)

    // Lookup country code in value mapping
    def countryCode = json.country
    def isoCode = valueMappingApi.getMappedValue(
        'COUNTRY_CODES',    // Value Mapping Group
        'SAP_Internal',     // Source Agency
        'ISO',              // Target Agency
        countryCode         // Source Value
    )

    json.countryISO = isoCode ?: countryCode
    message.setBody(groovy.json.JsonOutput.toJson(json))
    return message
}
```

## Content Modifier Patterns

### Set Headers

```xml
<ContentModifier id="cm_1" name="Set Headers">
  <Header name="Content-Type">application/json</Header>
  <Header name="Accept">application/json</Header>
  <Property name="MessageID" source="header" sourceField="SAP_MessageProcessingLogID"/>
  <Property name="Tenant" value="${config.tenant}"/>
</ContentModifier>
```

### Modify Body with Expression

```xml
<ContentModifier id="cm_2" name="Wrap Body">
  <Body>
    <![CDATA[
    {
      "header": {"messageId": "${property.MessageID}", "timestamp": "${date:now:yyyy-MM-dd'T'HH:mm:ss}"},
      "payload": ${in.body}
    }
    ]]>
  </Body>
</ContentModifier>
```

## Router Patterns

```xml
<Router id="router_1" name="Route by Content">
  <Condition expression="${property.OrderType} = 'STANDARD'" targetStep="process_standard"/>
  <Condition expression="${property.OrderType} = 'RUSH'" targetStep="process_rush"/>
  <DefaultCondition targetStep="process_standard"/>
</Router>
```

## XSLT Mapping

```xslt
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template match="/">
    <ns0:SalesOrder xmlns:ns0="urn:sap-com:document:sap:so:functions:style">
      <SalesOrderHeader>
        <CustomerID><xsl:value-of select="/order/customer/id"/></CustomerID>
        <OrderDate><xsl:value-of select="/order/date"/></OrderDate>
      </SalesOrderHeader>
      <xsl:for-each select="/order/items/item">
        <SalesOrderItem>
          <ItemNumber><xsl:value-of select="position()"/></ItemNumber>
          <Material><xsl:value-of select="material"/></Material>
          <Quantity><xsl:value-of select="quantity"/></Quantity>
        </SalesOrderItem>
      </xsl:for-each>
    </ns0:SalesOrder>
  </xsl:template>

</xsl:stylesheet>
```

## Integration Pattern Library

### Pattern 1: Sync Request-Reply (SOAP → OData)

```
HTTPS Sender (SOAP)
  → Content Modifier (extract headers)
    → Groovy Script (SOAP→JSON transform)
      → Request-Reply (OData V2 to S/4HANA)
        → Groovy Script (JSON→SOAP transform)
          → HTTPS Response
```

### Pattern 2: Async with Retry

```
SFTP Sender (file poll)
  → Content Modifier (set correlation ID)
    → Router (validate → error subprocess)
      → Groovy Script (transform)
        → Request-Reply (IDoc to ECC)
          → Retry (3x with 5min delay)
            → SFTP Receiver (archive)
```

### Pattern 3: Splitter-Gather

```
HTTPS Sender (batch payload)
  → Groovy Script (split into individual records)
    → Splitter (iterate per record)
      → Request-Reply (BAPI call)
        → Gather (collect responses)
          → Groovy Script (aggregate)
            → HTTPS Response
```

## CPI Constraints

| Limit | Value |
|---|---|
| iFlow design-time size | ~10 MB |
| Message size | 100 MB |
| Groovy execution timeout | 5 min |
| Number of steps per iFlow | ~100 |
| External call timeout | 10 min |
| Parallel branches | 50 |

## Deploy via MCP

```bash
# Inspect current packages
sap_cpi_list_packages()

# List artifacts in package
sap_cpi_list_artifacts(packageId="my-package")

# Deploy iFlow from source ZIP
sap_cpi_deploy_artifact(artifactId="my_iflow", artifactType="IntegrationFlow")

# Check deployment status
sap_cpi_get_runtime_artifacts()

# Monitor failed messages
sap_cpi_get_failed_messages(top=20, artifactName="my_iflow")
```

## ZIP Packaging via Python

```bash
# Create iFlow ZIP from source files
python scripts/cpi_iflow_packager.py create \
  --name my-integration-flow \
  --flow flow.xml \
  --scripts script/process.groovy script/validate.groovy \
  --mappings mapping/order.xslt \
  --parameters parameters.prop \
  --output my-iflow.zip

# Validate existing iFlow ZIP structure
python scripts/cpi_iflow_packager.py validate --input my-iflow.zip

# Extract iFlow ZIP to source files
python scripts/cpi_iflow_packager.py extract --input my-iflow.zip --output src/

# Lint CPI artifacts (Groovy + XML)
cpi_lint --code "$(cat flow.xml)"
```

## Gotchas

- **Groovy Sandbox**: CPI runs Groovy in Nashorn sandbox — no `System.exit()`, no file I/O, restricted `Runtime`
- **XmlSlurper not XPath**: use Groovy's `XmlSlurper().parseText()` not javax XPath
- **Message body types**: can be String, InputStream, or byte[]. Always cast explicitly
- **Content Modifier expressions**: use `${in.body}` not `${message.body}`
- **Externalize parameters**: never hardcode URLs, credentials, or threshold values
- **CPI log**: `message.getMessageLog().setStringProperty()` appears in MPL dashboard
- **MIME type**: `message.setHeader("Content-Type", "application/json")` must be set after body transform
- **Timeout**: Groovy script timeout is 5 min — split long operations across multiple steps
