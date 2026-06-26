---
name: sap-ai-core
description: SAP AI Core — ML model deployment, AI workflows, AI API, model serving (vLLM, Triton), scenario management, execution scheduling, resource groups, artifact management, SAP AI Launchpad, integration with CAP/Fiori. Use when deploying ML models on SAP BTP, creating AI workflows, or integrating AI inference into SAP applications.
---

# SAP AI Core

ML platform on SAP BTP — deploy, serve, and manage AI models at scale.

## Architecture

```
SAP AI Core (BTP)
├── Resource Group (GPU/CPU quota)
├── Scenario → Workflow → Execution
├── Model → Deployment → Serving endpoint
└── Artifact storage (S3-compatible)
```

## AI API

```bash
# Create deployment
curl -X POST https://api.ai.core.prod.<region>.aws.cloud.sap/v2/lm/deployments \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "deploymentId": "my-model",
    "modelId": "risk-predictor-v1",
    "scenarioId": "risk-analysis",
    "executableId": "serve-risk-model",
    "targetStatus": "RUNNING"
  }'

# Call inference
curl -X POST https://api.ai.core.prod.<region>.aws.cloud.sap/v2/inference/deployments/my-model/v1/predict \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [[1.2, 3.4, 5.6, 7.8, 9.0, 1.1, 2.2, 3.3,
                   4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 1.0, 2.0,
                   3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 1.5]]
  }'
```

## Scenario and Workflow

```yaml
# scenario.yaml
apiVersion: ai.sap.com/v1alpha1
kind: Scenario
metadata:
  name: risk-analysis
spec:
  executables:
    - name: serve-risk-model
      image: docker.io/myorg/risk-predictor:latest
      ports: [{ port: 8080, protocol: HTTP }]
      resources:
        limits: { cpu: "1", memory: "4Gi", "nvidia.com/gpu": "1" }
```

## CAP Integration

```javascript
// CAP service calling AI Core inference
const cds = require('@sap/cds')
const axios = require('axios')

module.exports = class RiskService extends cds.ApplicationService {
  async init() {
    this.on('analyzeRisks', async (req) => {
      const risks = await cds.run(SELECT.from('Risks'))
      const features = risks.map(r => extractFeatures(r))
      const result = await axios.post(
        process.env.AI_CORE_ENDPOINT + '/v2/inference/deployments/risk-model/v1/predict',
        { features },
        { headers: { Authorization: `Bearer ${await getToken()}` } }
      )
      return result.data.predictions.map((p, i) => ({ ...risks[i], riskScore: p }))
    })
    await super.init()
  }
}
```

## AI Launchpad

SAP AI Launchpad (Fiori): manage scenarios, deploy models, monitor executions, view inference logs.

## Gotchas
- GPU quotas limited per subaccount — request increase through SAP
- Model size max: 6GB per deployment (standard plan)
- Inference timeout: 60s for sync, 10min for async (batch)
- AI Core is AWS-based in most regions (not CF-based like other BTP services)
