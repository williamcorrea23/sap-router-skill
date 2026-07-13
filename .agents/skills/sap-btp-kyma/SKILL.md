---
name: sap-btp-kyma
description: SAP BTP Kyma runtime — Kubernetes-native runtime on BTP with Istio service mesh, API Rules, serverless functions, eventing, and BTP service bindings. Use when deploying containerized apps to BTP Kyma, configuring API Rules, building serverless functions, or deciding between Kyma and Cloud Foundry.
trigger:
  - kyma runtime BTP setup
  - API rule kyma expose service
  - serverless function kyma
  - kyma eventing subscription
  - kyma vs cloud foundry decision
  - istio mTLS kyma
  - BTP service binding kubernetes
---

# SAP BTP Kyma Runtime

Kubernetes-native runtime on SAP BTP — containers, Istio service mesh, serverless functions, eventing, native BTP service integration.

**Kyma vs CF:** Kyma for event-driven, microservices, custom stacks, Istio, serverless, any Docker image. CF for standard CAP/ABAP apps, simpler ops.

## Prerequisites

- SAP BTP subaccount with Kyma entitlement enabled
- `kubectl` installed (≥ v1.28), `kyma` CLI installed
- Docker or container runtime for building images
- Cluster admin access to the Kyma cluster

## 1. Connect to Your Kyma Cluster

```bash
# Install Kyma CLI
curl -Lo kyma https://github.com/kyma-project/cli/releases/latest/download/kyma_linux_amd64
chmod +x kyma && sudo mv kyma /usr/local/bin/

# Get kubeconfig from BTP Cockpit: Subaccount → Kyma → Cluster → Download Kubeconfig
export KUBECONFIG=~/.kube/kyma-config
kubectl get nodes
# → All nodes should show Ready status
```

## 2. Expose a Service with API Rules

```yaml
apiVersion: gateway.kyma-project.io/v1beta1
kind: APIRule
metadata:
  name: my-api
  namespace: default
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

```bash
kubectl apply -f api-rule.yaml
kubectl get apirule my-api -n default
# → STATUS: OK when active. Use handler: noop for public endpoints (no auth).
```

## 3. Deploy a Serverless Function

```yaml
apiVersion: serverless.kyma-project.io/v1alpha2
kind: Function
metadata:
  name: process-order
  namespace: default
spec:
  runtime: nodejs20
  source: |
    module.exports = {
      main: async function (event, context) {
        const order = JSON.parse(Buffer.from(event.data, 'base64').toString());
        return { status: 'OK', orderId: order.id };
      }
    }
  env:
    - name: S4_DESTINATION
      value: "S4HANA_DEV"
```

```bash
kubectl apply -f function.yaml
kubectl get function process-order -n default -w
# → STATUS: RUNNING when build and deploy complete
kyma logs -f process-order -n default
```

## 4. Subscribe to Events (CloudEvents)

```yaml
apiVersion: eventing.kyma-project.io/v1alpha2
kind: Subscription
metadata:
  name: order-subscription
  namespace: default
spec:
  sink: http://process-order.default.svc.cluster.local
  types:
    - sap.kyma.order.created
    - sap.kyma.order.updated
  source: sap-s4hana
```

```bash
kubectl apply -f subscription.yaml
kubectl get subscription order-subscription -n default
# → READY: True when subscription active
```

## 5. Bind BTP Services in Kyma

```yaml
apiVersion: services.cloud.sap.com/v1
kind: ServiceInstance
metadata: { name: my-hdi, namespace: default }
spec:
  serviceOfferingName: hana-cloud
  servicePlanName: hdi-shared
---
apiVersion: services.cloud.sap.com/v1
kind: ServiceBinding
metadata: { name: my-hdi-binding, namespace: default }
spec:
  serviceInstanceName: my-hdi
  secretName: my-hdi-secret
```

```bash
kubectl apply -f service-binding.yaml
kubectl get servicebinding my-hdi-binding -n default
# → Creates a Kubernetes secret with service credentials
kubectl get secret my-hdi-secret -n default
```

## 6. Enable Istio mTLS

```bash
kubectl apply -f - <<'EOF'
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata: { name: default, namespace: default }
spec:
  mtls:
    mode: STRICT
EOF
# Use mode: PERMISSIVE during migration, STRICT only when all services in mesh
```

## Pitfalls

- **Pitfall: API Rule returns 403 on every request**
  - Cause: `oauth2_introspection` handler requires valid JWT with matching scopes. Token missing or scope mismatch.
  - Solution: Set `handler: noop` for public endpoints. For protected endpoints, ensure client sends valid XSUAA token with matching scopes.

- **Pitfall: Serverless function cold start delays**
  - Cause: Functions scale to zero when idle. First request triggers pod startup (5–15s).
  - Solution: Set `minReplicas: 1` in function spec to keep one warm pod. Use for event-driven workloads, not synchronous user-facing APIs.

- **Pitfall: Istio mTLS breaks inter-service calls**
  - Cause: STRICT mTLS requires all clients to present TLS certs. Non-mesh clients fail.
  - Solution: Use `mode: PERMISSIVE` during migration. Switch to STRICT only after all services are in the mesh. Test with `kubectl exec` + curl between pods.

- **Pitfall: Cluster provisioning takes very long**
  - Cause: Initial Kyma cluster provisioning takes 30–60 minutes via Gardener.
  - Solution: Plan provisioning ahead. Check status in BTP Cockpit → Kyma → Cluster. Do not re-trigger; provisioning is idempotent.

- **Pitfall: Service binding secret not created**
  - Cause: BTP Service Operator not installed or ServiceInstance still provisioning.
  - Solution: Verify operator: `kubectl get deployment btp-service-operator -n kyma-system`. Wait for ServiceInstance STATUS Ready before creating ServiceBinding.

## Verification

```bash
kubectl get nodes
kubectl get apirule -n default   # STATUS: OK
kubectl get function -n default  # STATUS: RUNNING
kubectl get secret my-hdi-secret -n default  # Type: Opaque
kubectl get subscription -n default  # READY: True
# Dashboard: https://dashboard.<cluster-domain>
```
