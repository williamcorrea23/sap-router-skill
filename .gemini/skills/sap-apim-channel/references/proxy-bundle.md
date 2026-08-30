# Creating proxies and the bundle format

Read this when creating an API proxy, building or validating a bundle ZIP offline, or diagnosing a
rejected import.

## Four creation paths in the portal

`Configure → APIs → Create`, role `APIPortal.Administrator`:

| Path | When |
|---|---|
| **API Provider** | Backend is a configured system — SAP Gateway, S/4, PI, Open Connectors, Cloud Integration. Create the provider first (`Internet`, `On Premise` via Cloud Connector, `Open Connectors`, or `Cloud Integration`). |
| **URL** | Any REST/OData/SOAP target URL |
| **API Proxy** | Clone an existing proxy |
| **API Designer** | Model from an OpenAPI/Swagger spec |

A proxy is unique per **virtual host + base path**, and holds one mandatory Proxy Endpoint plus zero
or more Target Endpoints.

Lifecycle: *Save* leaves the proxy `Not Deployed` — editable, but not eligible for a product.
*Deploy* makes it `Deployed`, testable, and eligible. *Undeploy* removes it from the Developer Hub
without deleting it.

Sources: [Different Methods of Creating an API Proxy](https://help.sap.com/docs/integration-suite/sap-integration-suite/different-methods-of-creating-an-api-proxy-4ac0431),
[Create an API Provider](https://help.sap.com/docs/integration-suite/sap-integration-suite/create-an-api-provider-6b263e2).

## Bundle layout

Per [API Proxy Structure](https://help.sap.com/docs/integration-suite/sap-integration-suite/api-proxy-structure-4dfd54a):

```
APIProxy/<name>.xml            proxy header: endpoints, policies, file resources
APIProxyEndPoint/<name>.xml    base path, route rules, pre/post flows
APITargetEndPoint/<name>.xml   backend URL
Policy/<PolicyName>.xml        one per policy
APIResource/ FileResource/ Documentation/    optional, omitted when empty
```

`FileResource/` holds the `.js`, `.py` and `.xsl` files that script policies reference.

### Verify against a tenant export

The tenant's own export is the authoritative layout. Before relying on a generated bundle for a
production import, export an existing proxy and diff against it:

```bash
# via apim_execute_action: proxies.export --name <existing proxy>
python scripts/apim_proxy_packager.py extract --input export.zip --output ref/
```

### ProxyEndpoint skeleton

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ProxyEndPoint default="true">
    <name>default</name>
    <base_path>/router-echo</base_path>
    <properties/>
    <routeRules>
        <routeRule>
            <name>default</name>
            <targetEndPointName>default</targetEndPointName>
            <sequence>1</sequence>
            <faultRules/>
        </routeRule>
    </routeRules>
    <faultRules/>
    <preFlow><name>PreFlow</name></preFlow>
    <postFlow><name>PostFlow</name></postFlow>
    <conditionalFlows/>
</ProxyEndPoint>
```

Policies attach as `<step><name>Policy-Name</name></step>` inside a flow's `<request>` or
`<response>`. Each referenced name must have a matching `Policy/<name>.xml`.

### Endpoint transport properties

Settable on either endpoint: `api.timeout`, `request.streaming.enabled`,
`response.streaming.enabled`, `compression.algorithm` (`gzip`/`deflate`/`none`), `X-Forwarded-For`.

Source: [Proxy Endpoint Properties](https://help.sap.com/docs/integration-suite/sap-integration-suite/proxy-endpoint-properties-1705a92).

## Policy templates

Reusable policy bundles import and export independently of proxies, with their own layout:
`PolicyTemplateContainer/<name>.xml`, `PolicyTemplateContainer/Policy/<Policy>.xml`, and
`PolicyTemplateContainer/FileResource/`.
