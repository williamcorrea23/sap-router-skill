#Context Video: https://customer-hzpubzwln1i257gg.cloudflarestream.com/55b893bcda8beb1dc9693f0b364ab5c3/watch


# SkillPilot — AI Learning Assistant for SAP SuccessFactors

> **Built to demonstrate how a Domain Lead thinks:** one focused AI use case,
> anchored to Hire-to-Retire, deployed on SAP BTP, designed to activate
> unused credits and drive renewal conversations.

**Live on SAP BTP Cloud Foundry:**
`https://skillpilot-hr.cfapps.us10-001.hana.ondemand.com/api/health`

---

## The Business Problem

60%+ of S/4HANA migrations exceed planned schedules. The failure mode is
rarely technical — it's adoption. Employees can't find the right training,
support tickets spike, and change management budgets run out before go-live.

Meanwhile, SAP customers approaching renewal are often sitting on pools of
unused BTP credits. The question every Customer Success team faces:
**what's the fastest path from committed capacity to demonstrated value?**

SkillPilot is the answer for the Hire-to-Retire process area.

---

## What SkillPilot Does

An AI-powered conversational assistant embedded in SAP SuccessFactors Learning
that helps employees discover courses, navigate learning paths, track
certifications, and prepare for S/4HANA migrations — in plain language,
not menu navigation.
```
Employee: "What do I need to learn before our S/4HANA go-live next quarter?"

SkillPilot: "Based on your role as a Functional Consultant, I recommend
starting with the S/4HANA Migration Fundamentals course (16 hours), then
moving to the S/4HANA Migration Specialist learning path (12 weeks).
Key topics: SAP Activate methodology, fit-to-standard workshops, and
LTMC data migration tooling..."
```

---

## Why This Use Case for BTP Consumption

One SkillPilot deployment drives consumption across multiple BTP services:

| BTP Service | Role in SkillPilot |
|---|---|
| SAP AI Core (Generative AI Hub) | Foundation model access (Claude Sonnet) |
| SAP HANA Cloud (Vector Engine) | Semantic search over learning content |
| Cloud Foundry Runtime | Application hosting |
| SAP AI Launchpad | Model monitoring and governance |

At enterprise scale (5,000 employees × 3 queries/week = 15,000 API calls/week),
this activates meaningful committed capacity — turning unused credits into
a renewal conversation anchor rather than a risk.

---

## Where It Sits in Hire-to-Retire
```
Hire → Onboard → [ LEARN ] → Perform → Reward → Retire
                      ▲
               SkillPilot lives here
               inside SuccessFactors Learning Management
               reading via released OData APIs
               never touching the core (Clean Core principle)
```

---

## FRE Maturity Ladder

SkillPilot is designed as a repeatable pattern, not a one-off demo.
It maps directly to SAP's Future Ready Enterprise maturity framework:

| Level | Capability | SkillPilot Stage |
|---|---|---|
| L1 | Static FAQ / keyword search | Baseline (pre-SkillPilot) |
| L2 | RAG with semantic search | **Current build** |
| L3 | Multi-module + analytics dashboard | Next: add SF Performance data |
| L4 | AI agents with auto-enrollment | Agents that act on recommendations |
| L5 | Cross-system intelligence | SF + S/4HANA + Ariba unified view |

---

## Technical Architecture
```
┌─────────────────────────────────────────────────┐
│              SAP Fiori / Chat UI                 │
└───────────────────┬─────────────────────────────┘
                    │ POST /api/chat
                    ▼
┌─────────────────────────────────────────────────┐
│         CAP Node.js RAG Service                  │
│                                                  │
│  Mock SF OData Data → TF-IDF Chunker             │
│  Query → Cosine Similarity → Top-3 Retrieval     │
│  Grounded Prompt Assembly                        │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│    Claude Sonnet (claude-sonnet-4-20250514)      │
│                                                  │
│  Dev:  Anthropic API (direct)                    │
│  Prod: SAP Generative AI Hub via AI Core         │
│        + XSUAA token exchange                    │
│        + SAP AI ethics guardrails                │
└─────────────────────────────────────────────────┘
                    │
                    ▼
         Answer + Source Citations
```

**Mock Data Layer** (mirrors SuccessFactors Learning OData API structure):
- 10 Courses (S/4HANA, BTP, AI/ML, Change Management, Fiori, Integration Suite)
- 3 Learning Paths (Functional Consultant, BTP Developer, Change Lead)
- 3 Certifications (S/4HANA, BTP Architect, SuccessFactors EC)
- 4 Skills with proficiency levels

---

## Live Demo
```bash
# Health check
curl https://skillpilot-hr.cfapps.us10-001.hana.ondemand.com/api/health

# Ask a question
curl -X POST https://skillpilot-hr.cfapps.us10-001.hana.ondemand.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What learning path should I take for S/4HANA migration?"}'

# Browse the knowledge base
curl https://skillpilot-hr.cfapps.us10-001.hana.ondemand.com/api/content
```

---

## Local Setup
```bash
git clone https://github.com/harsharao85/BTP_SkillPilot_Successfactors.git
cd BTP_SkillPilot_Successfactors
npm install
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
npm run start:rag
```

---

## Production Path (SAP BTP)

This build runs on BTP Cloud Foundry today. The production upgrade path:

1. **Swap AI layer**: Replace Anthropic API with SAP AI Core service binding + XSUAA
2. **Swap vector store**: Replace in-memory TF-IDF with HANA Cloud Vector Engine
3. **Swap data source**: Replace mock CSVs with live SuccessFactors Learning OData APIs
4. **Add auth**: Enable XSUAA for enterprise SSO
5. **Add UI**: Deploy Fiori Elements chat interface

Architecture is identical. Only the service bindings change.

---

## About This Build

Built by **Harsha Rao** as a proof-of-concept for the SAP BTP Customer Success
Domain Lead role. Prior work includes MentorForge — an AWS-native RAG learning
platform built on Bedrock, pgvector, and CDK. SkillPilot ports that pattern
into the SAP BTP ecosystem, demonstrating that the architectural judgment
transfers and the platform credibility is real.

**Stack**: CAP Node.js · SAP BTP Cloud Foundry · Claude Sonnet · TF-IDF RAG
**Deployed**: SAP BTP Trial (US East, AWS) · `cfapps.us10-001.hana.ondemand.com`
