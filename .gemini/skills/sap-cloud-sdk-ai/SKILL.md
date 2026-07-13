---
name: sap-cloud-sdk-ai
description: SAP Cloud SDK for AI — generative AI hub SDK, LLM orchestration, prompt templating, model selection, orchestration service for multi-step AI workflows, document grounding, retrieval augmented generation (RAG). Use when building AI agents with SAP Cloud SDK, calling LLMs via SAP BTP GenAI Hub, or implementing RAG patterns with SAP data.
trigger:
  keywords: [ai, sdk, generative, llm, orchestration, rag, prompt, btp, genai, models]
  intent: >-
    Build AI agents and orchestrate LLMs on SAP BTP using the Cloud SDK for AI, including prompt templating, RAG, and model selection.
---

# SAP Cloud SDK for AI

Generative AI development on SAP BTP — LLM orchestration, prompt management, RAG.

## Python SDK

```python
from gen_ai_hub.orchestration import OrchestrationService

# Orchestration with templating and grounding
service = OrchestrationService(
    api_url="https://api.ai.core.prod.<region>.aws.cloud.sap/v2",
    client_id="...", client_secret="..."
)

# Define a prompt template
template = '''
System: You are an SAP procurement expert. Answer using only provided context.

Context: {{?grounding_context}}

User: {{?user_input}}
'''

result = service.invoke(
    template=template,
    grounding={"type": "document", "source": "sap-procurement-docs"},
    model={"name": "gpt-4"},
    input={"user_input": "How do I create a purchase order?"}
)
print(result.content)
```

## Document Grounding

```python
# Upload SAP documents for RAG
service.upload_document(
    name="sap-procurement-docs",
    content=open("procurement_guide.pdf", "rb"),
    metadata={"category": "SAP_MM", "language": "EN"}
)

# Query with grounding
response = service.query_with_grounding(
    question="What BAPI creates a purchase order?",
    document_names=["sap-procurement-docs"],
    top_k=3
)
```

## Model Selection

| Model | Provider | Best For |
|---|---|---|
| GPT-4 / GPT-4o | OpenAI | Complex reasoning, code generation |
| Codex Opus / Sonnet | Anthropic | Analysis, structured output |
| Llama 3 | Meta (self-hosted) | Cost-sensitive, offline scenarios |
| Gemini Pro | Google | Multimodal, long context |

## Multi-Step Orchestration

```python
# Chain: classify → route → generate → validate
orchestrator = OrchestrationService()

steps = [
    {"name": "classify", "template": classify_template, "model": "gpt-4o-mini"},
    {"name": "generate", "template": generate_template, "model": "gpt-4"},
    {"name": "validate", "template": validate_template, "model": "gpt-4o-mini"}
]

result = orchestrator.run_pipeline(steps=steps, input={"question": user_input})
```

## Gotchas
- GenAI Hub requires AI Core entitlement on BTP subaccount
- Rate limits vary by model provider (OpenAI vs Anthropic vs Meta)
- Document grounding documents must be in supported format (PDF, TXT, MD)
- Always validate LLM output — hallucination risk with SAP technical content
