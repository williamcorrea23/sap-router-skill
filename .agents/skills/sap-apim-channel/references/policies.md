# Policy catalogue and XML shapes

Read this when attaching, authoring or debugging a policy.

## The namespace rule

Every policy carries `enabled`, `continueOnError`, `async` and the namespace
`xmlns="http://www.sap.com/apimgmt"`. **A policy without that namespace will not load** — this is
the most common reason a hand-written policy is rejected.

## Available types

Access Control · Access Entity · Assign Message · Basic Authentication · Extract Variables ·
Invalidate/Lookup/Populate Cache · JavaScript/Python/XSL · JSON↔XML · Key Value Map Operations ·
OAuth v2.0 · Quota · Raise Fault · Reset Quota · Response Cache · Service Callout · Spike Arrest ·
SAML Assertion · SOAP Message Validation · Verify API Key · XML/JSON/Regex Threat Protection ·
Statistics Collector.

Source: [Policy Types](https://help.sap.com/docs/integration-suite/sap-integration-suite/policy-types-c918e28).

## Shapes

```xml
<VerifyAPIKey async="true" continueOnError="false" enabled="true" xmlns="http://www.sap.com/apimgmt">
    <APIKey ref="request.header.apikey"/>
</VerifyAPIKey>
```

```xml
<SpikeArrest async="true" continueOnError="false" enabled="true" xmlns="http://www.sap.com/apimgmt">
    <Identifier ref="client.ip"/>
    <Rate>30pm</Rate>
</SpikeArrest>
```

```xml
<!-- type: default | calendar | flexi | rollingwindow -->
<Quota type="calendar" async="true" continueOnError="true" enabled="true" xmlns="http://www.sap.com/apimgmt">
    <Identifier ref="verifyapikey.Verify-API-Key.client_id"/>
    <Allow count="10000"/>
    <Interval>1</Interval>
    <TimeUnit>month</TimeUnit>
    <Distributed>true</Distributed>
    <Synchronous>true</Synchronous>
</Quota>
```

```xml
<AssignMessage async="false" continueOnError="false" enabled="true" xmlns="http://www.sap.com/apimgmt">
    <Add><Headers><Header name="X-Trace">value</Header></Headers></Add>
    <AssignVariable><Name>var</Name><Ref>request.header.temp</Ref></AssignVariable>
    <AssignTo createNew="false" transport="http" type="request"/>
</AssignMessage>
```

```xml
<RaiseFault async="true" continueOnError="false" enabled="true" xmlns="http://www.sap.com/apimgmt">
    <FaultResponse><Set>
        <Payload contentType="text/plain">Server Error</Payload>
        <StatusCode>500</StatusCode>
        <ReasonPhrase>Server Error</ReasonPhrase>
    </Set></FaultResponse>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</RaiseFault>
```

```xml
<ServiceCallout async="true" continueOnError="false" enabled="true" xmlns="http://www.sap.com/apimgmt">
    <Request clearPayload="true" variable="myRequest"/>
    <Response>callOutResponse</Response>
    <Timeout>30000</Timeout>
    <HTTPTargetConnection><URL>https://api.example.com/API</URL></HTTPTargetConnection>
</ServiceCallout>
```

```xml
<ResponseCache async="true" continueOnError="false" enabled="true" xmlns="http://www.sap.com/apimgmt">
    <CacheKey><KeyFragment ref="request.uri" type="string"/></CacheKey>
    <ExpirySettings><TimeoutInSeconds>60</TimeoutInSeconds></ExpirySettings>
</ResponseCache>
```

```xml
<KeyValueMapOperations async="true" continueOnError="false" enabled="true"
    mapIdentifier="urlMapper" xmlns="http://www.sap.com/apimgmt">
    <Put override="false"><Key><Parameter>key1</Parameter></Key><Value ref="var_name"/></Put>
    <Get assignTo="target.var"><Key><Parameter ref="source.var"/></Key></Get>
    <Scope>apiproxy</Scope>
</KeyValueMapOperations>
```

## Notes that bite

- **ResponseCache attaches twice** — once in PreFlow, once in PostFlow. One attachment silently
  does nothing.
- **OAuthV2 is non-RFC-compliant in two fields**: it returns `"token_type":"BearerToken"` instead of
  `"Bearer"`, and `expires_in` as a string rather than a number. Wrap it with a JavaScript or
  AssignMessage policy when a client demands strict compliance.
  Source: [Non-RFC-Compliant Behavior](https://help.sap.com/docs/integration-suite/sap-integration-suite/non-rfc-compliant-behavior-oauthv2-policy-7a98cc9).
- **Concurrent Rate Limit is decommissioned** — no proxy can create or update it. Use Quota or
  Spike Arrest.
- **OAuth v2.0 needs three pieces**: a token-endpoint proxy with `Operation=GenerateAccessToken`,
  a `VerifyAccessToken` policy on the protected resources, and an API Product that resolves which
  proxies the token authorizes.
- Scripts (JavaScript/Python/XSL) live as FileResources and are referenced from a script policy —
  they are not inline in the policy XML.

## Further shapes

[SAP/apibusinesshub-api-recipes](https://github.com/SAP/apibusinesshub-api-recipes) (Apache-2.0) is
SAP's own collection of proxy bundles and policy templates, and is where this repo's bundled
templates take their patterns from.
