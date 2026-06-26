---
name: sap-btp-kyma
description: SAP BTP Kyma runtime — Kubernetes-native runtime on BTP, service mesh (Istio), API Rules, serverless functions, eventing, Kyma CLI, container workloads on BTP, Kyma vs Cloud Foundry decision guide. Use when deploying containerized apps to BTP, configuring Istio/API Rules, building serverless functions on BTP, or deciding between Kyma and CF runtimes.
---

# SAP BTP Kyma Runtime

Kubernetes-native runtime on SAP BTP — containers, Istio service mesh, serverless, eventing.

## Kyma Architecture

```
SAP BTP Kyma Runtime
├── Kubernetes Cluster (Gardener-managed)
│   ├── Istio Service Mesh (ingress/egress, mTLS)
│   ├── Serverless (Kubernetes functions)
│   │   ├── Node.js, Python, Go functions
│   │   └── Auto-scaling (KPA - Knative Pod Autoscaler)
│   ├── Eventing (CloudEvents)
│   ├── API Rules (expose services externally)
│   └── Service Catalog (BTP service bindings)
└── Kyma Dashboard (web UI)
```

## Kyma vs Cloud Foundry Decision

| Criterion | Kyma | Cloud Foundry |
|---|---|---|
| Container support | Any Docker image | Buildpack or Docker |
| Language support | Any | Java, Node.js, Python, Go, PHP, .NET |
| Scaling | KPA (Knative) + HPA | App Autoscaler |
| Service mesh | Istio (built-in) | None (custom) |
| Serverless | Yes (functions) | No |
| CAP support | Containerized | Native |
| Learning curve | Higher (Kubernetes) | Lower (cf push) |
| Use when | Event-driven, microservices, custom stacks | Standard CAP/ABAP apps |

## API Rules (Expose Services)

```yaml
apiVersion: gateway.kyma-project.io/v1beta1
kind: APIRule
metadata:
  name: my-api
spec:
  gateway: kyma-gateway.kyma-system.svc.cluster.local
  host: my-api.<cluster-domain>
  service:
    name: my-service
    port: 8080
  rules:
    - path: /.*
      methods: ["GET", "POST"]
      accessStrategies:
        - handler: oauth2_introspection
          config:
            requiredScopes: ["read"]
```

## Serverless Function

```yaml
apiVersion: serverless.kyma-project.io/v1alpha2
kind: Function
metadata:
  name: process-order
spec:
  runtime: nodejs20
  source: |
    module.exports = {
      main: async function (event, context) {
        const order = JSON.parse(Buffer.from(event.data, 'base64').toString());
        console.log('Processing order:', order.id);
        // Call SAP S/4HANA via destination
        return { status: 'OK', orderId: order.id };
      }
    }
  env:
    - name: S4_DESTINATION
      value: "S4HANA_DEV"
```

## Eventing (CloudEvents)

```yaml
apiVersion: eventing.kyma-project.io/v1alpha2
kind: Subscription
metadata:
  name: order-subscription
spec:
  sink: http://process-order.default.svc.cluster.local
  types:
    - sap.kyma.order.created
    - sap.kyma.order.updated
  source: sap-s4hana
```

## Kyma CLI

```bash
# Install Kyma CLI
curl -Lo kyma https://github.com/kyma-project/cli/releases/latest/download/kyma_linux_amd64
chmod +x kyma && sudo mv kyma /usr/local/bin/

# Connect to cluster
kyma alpha deploy

# Deploy function
kyma apply function -f function.yaml

# Check function status
kyma get function -n default

# Watch logs
kyma logs -f process-order -n default
```

## Istio Service Mesh

```yaml
# mTLS between services
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
spec:
  mtls:
    mode: STRICT
```

## BTP Service Binding in Kyma

```yaml
apiVersion: services.cloud.sap.com/v1
kind: ServiceInstance
metadata:
  name: my-hdi
spec:
  serviceOfferingName: hana-cloud
  servicePlanName: hdi-shared
---
apiVersion: services.cloud.sap.com/v1
kind: ServiceBinding
metadata:
  name: my-hdi-binding
spec:
  serviceInstanceName: my-hdi
  secretName: my-hdi-secret
```

## Gotchas

- Kyma cluster provisioning: 30-60 min for initial cluster
- API Rules use OAuth2 by default — configure `noop` for public endpoints
- Serverless functions scale to zero when idle → cold start on first request
- Istio mTLS is ON by default — inter-service calls need TLS config
- Kyma Dashboard URL: `https://dashboard.<cluster-domain>`
