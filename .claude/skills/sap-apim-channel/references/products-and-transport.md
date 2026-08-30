# Products, applications, key value maps and transport

Read this when publishing proxies for consumption, managing API keys, storing configuration in a
key value map, or moving API content between tenants.

## Products

A **Product** bundles deployed proxies — saved-only proxies are not eligible — plus quota metadata,
an OAuth scope (≤4K chars total) and up to 18 custom attributes. It starts as `Draft`; *Publish*
makes it consumable.

The product's quota fields are **values the Quota policy references**, not enforcement in
themselves. Publishing a product with a quota does nothing unless a Quota policy reads it, typically
through `verifyapikey.<policy>.apiproduct.developer.quota.limit`.

Source: [Create a Product](https://help.sap.com/docs/integration-suite/sap-integration-suite/create-a-product-d769622).

## Applications and API keys

Developers subscribe in the **Developer Hub** (formerly API Business Hub Enterprise): open the
product → *Subscribe* → new or existing application → the application receives a key and secret
valid for every product it subscribes to.

App keys and secrets are never returned by list or read calls — treat their absence from a response
as by design, not as a failed call.

Programmatic application management uses the Developer Hub OData surface at
`/odata/1.0/data.svc/APIMgmt.Applications`. With monetization enabled, prefer the `Subscriptions`
entity over the legacy `Applications` one.

Source: [Subscribe to a Product](https://help.sap.com/docs/integration-suite/sap-integration-suite/subscribe-to-a-product-to-consume-apis-and-events-in-an-application-f74f47d).

## Key Value Maps

`Configure → APIs → Key Value Maps → Create`. Keys may not contain `//` or trailing spaces.

- **Encrypted KVMs can only be created through the UI or the management API.** The
  `KeyValueMapOperations` policy can update one but never create it.
- Scope is `apiproxy` (default) or environment. Concurrent writes to an environment-scoped KVM can
  lose data — prefer proxy scope wherever anything writes concurrently.
- Never use a KVM for logging. Use the Message Logging policy pointed at an external endpoint.

Source: [Create a Key Value Map](https://help.sap.com/docs/integration-suite/sap-integration-suite/create-a-key-value-map-90d8d41).

## Transport between tenants

Four documented options, in order of preference:

| Option | For |
|---|---|
| **Cloud Transport Management (TMS)** | Cloud-native landscapes — SAP's recommended default |
| **CTS+** | Landscapes already transporting ABAP through CTS+ |
| **MTAR download** | Semi-automated fallback when the transport connection is down |
| **Manual export/import** | Urgent fixes only — no logging, no governance |

TMS routes content through the Content Assembly Service and the Deploy Service: it is a service
chain, not a single REST endpoint. Draft-version artifacts and access-policy-protected artifacts
cannot be transported — resolve those conflicts before starting.

> `Transport.mgmt` appears in older standalone/Neo material as a flat REST surface. It is **not**
> part of the current Integration Suite doc set. Treat any reference to it as legacy and use the
> TMS chain instead.

Source: [Content Transport](https://help.sap.com/docs/integration-suite/sap-integration-suite/content-transport-e3c79d6).

## CI/CD

Project "Piper" wraps the same `apiportal-apiaccess` API with ready-made steps: `apiProxyUpload`,
`apiProxyDownload`, `apiProviderUpload`, `apiProviderDownload`, `apiProviderList`. All take the
service key through `apimApiServiceKeyCredentialsId` in `.pipeline/config.yaml`.

API providers are create-only through Piper — updating one means deleting and recreating it.

Source: [apiProxyUpload](https://www.project-piper.io/steps/apiProxyUpload/).
