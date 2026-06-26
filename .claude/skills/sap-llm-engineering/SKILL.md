---
name: sap-llm-engineering
description: >-
  LLM engineering patterns adapted for SAP AI contexts — prompt optimization
  for BAPI code generation, evaluation loops for ABAP code quality, RAG
  pipeline patterns for SAP knowledge bases, training data curation for
  ABAP-specific models, agent evaluation harnesses. Emulates andrej-karpathy
  LLM engineering methodology applied to SAP domains. Use when optimizing
  prompts for ABAP generation, building SAP GenAI evaluations, constructing
  SAP RAG pipelines, fine-tuning code generation models, or measuring LLM
  output quality in SAP contexts. Triggers on: "prompt engineering ABAP",
  "evaluate ABAP generation", "LLM for SAP", "fine-tune ABAP model",
  "RAG pipeline SAP", "GenAI evaluation", "Karpathy pattern SAP".
---

# SAP LLM Engineering — Karpathy Patterns for SAP AI

Adapts Andrej Karpathy's LLM engineering methodology (evaluation loops,
prompt optimization, training data curation, RAG construction) for SAP
ABAP/BTP/CPI contexts.

## Philosophy (Karpathy-isms Applied to SAP)

| Karpathy Principle | SAP Application |
|---|---|
| "Build evaluation first, not last" | Create ABAP code quality eval harness before prompt engineering |
| "The model is not the product — the eval is" | ABAP generation quality measured by abaplint + unit test pass rate |
| "Synthetic data beats scraping" | Generate ABAP training pairs from existing SAP code + test suites |
| "Prompt engineering = the new programming" | BAPI code generation prompt IS the program specification |
| "LLMs are a tool, not a solution" | Use LLM for ABAP boilerplate, human review for business logic |
| "Iterate on evals, not prompts" | Measure eval metric improvement, not subjective prompt quality |

## Evaluation Harness for ABAP Code Generation

```python
# eval_abap_llm.py — Karpathy-style evaluation loop
"""
Measures ABAP code generation quality across dimensions.
Run BEFORE writing prompts — eval defines what "good" means.
"""

class AbapEvalHarness:
    def __init__(self):
        self.metrics = {
            'abaplint_pass': 0,       # abaplint --format json → pass/fail
            'syntax_ok': 0,           # ADT syntax check pass
            'unit_test_pass': 0,      # ABAP Unit test pass rate
            'clean_abap_score': 0,    # Clean ABAP compliance %
            'bapi_correctness': 0,    # BAPI import/export params match spec
            'security_ok': 0,         # No SQL injection, auth gaps
            'performance_ok': 0,      # No SELECT in loop, SELECT *, etc.
        }

    def evaluate(self, generated_code: str, spec: dict) -> dict:
        """Run full evaluation pipeline on generated ABAP code."""
        results = {}

        # 1. Static analysis (deterministic)
        results['abaplint'] = self.run_abaplint(generated_code)
        results['syntax'] = self.run_adt_syntax_check(generated_code)

        # 2. Semantic analysis (AI-augmented)
        results['clean_abap'] = self.score_clean_abap(generated_code)
        results['security'] = self.audit_security(generated_code)
        results['performance'] = self.audit_performance(generated_code)

        # 3. Correctness (spec-driven)
        if spec.get('bapi_name'):
            results['bapi_params'] = self.verify_bapi_signature(
                generated_code, spec['bapi_name']
            )

        # 4. Tests
        results['unit_tests'] = self.run_abap_unit_tests(
            generated_code, spec.get('test_cases', [])
        )

        return {
            'pass': all(v.get('pass', False) for v in results.values()),
            'score': sum(v.get('score', 0) for v in results.values()) / len(results),
            'details': results
        }

# Usage:
# harness = AbapEvalHarness()
# result = harness.evaluate(llm_output, spec={"bapi_name": "BAPI_MATERIAL_SAVEDATA"})
# print(f"Score: {result['score']:.2f}")
# if not result['pass']:
#     for dim, detail in result['details'].items():
#         if not detail['pass']:
#             print(f"FAIL {dim}: {detail.get('errors', [])}")
```

## Prompt Optimization Loop

```python
# prompt_optimizer.py — Systematic prompt improvement
"""
Karpathy method: fix prompt, not output.
Track eval metrics across prompt revisions.
"""

PROMPT_TEMPLATES = {
    'bapi_create': """
You are an expert ABAP developer. Write a method that calls {bapi_name}
to create a {entity_type} with these fields: {fields}.

Requirements:
- Use modern ABAP (inline declarations, NEW constructor)
- Always call BAPI_TRANSACTION_COMMIT with WAIT = 'X'
- Check BAPIRET2 tables, not just IMPORTING RETURN
- Handle errors with CX_STATIC_CHECK exception
- Add BAL logging for audit trail
- Include ABAP Unit test class with {min_tests} test methods

ABAP version: {version}
Package prefix: {package}
""",
    'rap_behavior': """
You are an expert RAP developer. Write behavior implementation for entity
{entity_name} with these operations: {operations}.

Requirements:
- Use managed scenario with {persist_table}
- Implement {determinations} determinations
- Implement {validations} validations
- Implement {actions} actions
- Use EML (Entity Manipulation Language) for internal calls
- Add draft handling for {draft_operations} operations
- Include ABAP Unit with CDS Test Double Framework

ABAP version: {version}
""",
}

class PromptOptimizer:
    def __init__(self, eval_harness):
        self.harness = eval_harness
        self.revisions = []  # Track prompt → eval score history

    def optimize(self, template_name, spec, max_iterations=5):
        """Iteratively improve prompt until eval passes or max iterations."""
        best_score = 0
        best_prompt = None

        for i in range(max_iterations):
            prompt = self.build_prompt(template_name, spec)

            # Generate code with LLM
            code = self.call_llm(prompt)

            # Evaluate
            result = self.harness.evaluate(code, spec)

            # Track
            self.revisions.append({
                'iteration': i,
                'prompt_hash': hash(prompt),
                'score': result['score'],
                'failures': [
                    dim for dim, d in result['details'].items()
                    if not d.get('pass', False)
                ]
            })

            if result['score'] > best_score:
                best_score = result['score']
                best_prompt = prompt

            if result['pass']:
                break

            # Update spec with failure feedback for next iteration
            spec = self.update_spec_from_failures(spec, result)

        return best_prompt, best_score
```

## Training Data Curation for ABAP Models

```python
# abap_data_curator.py
"""
Curate training data from existing ABAP codebases.
Pattern: (problem_description, context, solution_code) triples.
"""

def extract_training_pairs(repo_path: str) -> list[dict]:
    """
    Extract (instruction, input, output) triples from ABAP repos.

    Sources:
    - Method implementation → method signature + doc → body
    - BAPI call → calling method signature → BAPI wrapper method
    - RAP behavior → BDEF definition → behavior class implementation
    - CDS view → annotation requirement → DDL source
    - Unit test → requirement doc → test class

    Quality filters:
    - abaplint pass required
    - Syntax check pass required
    - Unit test pass required
    - Non-generated code only (not SAP standard)
    - Clean ABAP score ≥ 70/100
    """
    pairs = []

    for abap_file in find_abap_files(repo_path):
        source = read_abap_source(abap_file)

        # Extract method-level pairs
        for method in parse_methods(source):
            if not is_generated(method):
                spec = extract_spec_from_docs(method)
                if spec and passes_quality_gate(method):
                    pairs.append({
                        'instruction': spec['instruction'],
                        'input': spec['signature'],
                        'output': method['body'],
                        'metadata': {
                            'module': detect_module(method),
                            'bapi': extract_bapi_usage(method),
                            'clean_score': score_clean_abap(method['body']),
                        }
                    })

    return pairs
```

## RAG Pipeline for SAP Knowledge Bases

```python
# sap_rag_pipeline.py
"""
RAG pipeline optimized for SAP technical documentation.
Chunk strategy: by BAPI method, by CDS entity, by SAP Note.
"""


SAP_CHUNK_STRATEGIES = {
    'bapi': {
        'split_on': 'FUNCTION ',
        'metadata_fields': ['BAPI_NAME', 'MODULE', 'RELEASE_VERSION'],
        'min_chunk_size': 200,
        'max_chunk_size': 4000,
    },
    'cds_view': {
        'split_on': 'DEFINE VIEW ',
        'metadata_fields': ['ENTITY_NAME', 'ANNOTATIONS', 'DATA_SOURCE'],
        'min_chunk_size': 100,
        'max_chunk_size': 2000,
    },
    'sap_note': {
        'split_on': '## Solution',
        'metadata_fields': ['NOTE_NUMBER', 'COMPONENT', 'VERSION', 'DATE'],
        'min_chunk_size': 300,
        'max_chunk_size': 8000,
    },
    'abap_class': {
        'split_on': 'METHOD ',
        'metadata_fields': ['CLASS_NAME', 'METHOD_NAME', 'VISIBILITY'],
        'min_chunk_size': 50,
        'max_chunk_size': 1500,
    },
    'btp_service': {
        'split_on': '## ',
        'metadata_fields': ['SERVICE_NAME', 'PLAN', 'REGION'],
        'min_chunk_size': 200,
        'max_chunk_size': 5000,
    },
}

class SapRagPipeline:
    def __init__(self, embedding_model='text-embedding-3-large'):
        self.embedding_model = embedding_model
        self.index = None  # Vector store index

    def ingest(self, source_type='all'):
        """Ingest SAP documentation into vector store."""
        sources = {
            'sap_help': self.scrape_help_portal(),
            'sap_notes': self.fetch_relevant_notes(),
            'community': self.scrape_blogs_wikis(),
            'internal': self.load_trench_knowledge_files(),
            'abap_skills': self.load_all_skill_mds(),
        }

        chunks = []
        for source_name, documents in sources.items():
            strategy = self.detect_strategy(source_name)
            for doc in documents:
                chunks.extend(self.chunk(doc, strategy))

        self.index = self.build_vector_index(chunks)

    def query(self, question: str, k: int = 5) -> list[dict]:
        """Retrieve relevant SAP knowledge for a question."""
        results = self.index.similarity_search(question, k=k)
        return [{
            'content': r.page_content,
            'metadata': r.metadata,
            'relevance': r.score,
        } for r in results]

    def generate_with_context(self, question: str) -> str:
        """Generate ABAP code/solution with RAG context."""
        context = self.query(question)
        prompt = self.build_rag_prompt(question, context)
        return self.call_llm(prompt)
```

## Agent Evaluation Harness

```python
# agent_eval.py
"""
Measure SAP agent quality across tasks.
Run before deploying agent to production.
"""

SAP_AGENT_EVAL_CASES = [
    {
        'task': 'Create ABAP class ZCL_MATERIAL_HELPER with BAPI_MATERIAL_SAVEDATA wrapper',
        'criteria': ['syntax_valid', 'abaplint_pass', 'bapi_params_correct',
                     'has_error_handling', 'has_unit_test', 'clean_abap_70plus'],
        'weight': 1.0,
    },
    {
        'task': 'Find all BAdIs related to purchase order processing and explain each',
        'criteria': ['finds_me_process_po', 'finds_me_define_pricing',
                     'explains_interface', 'suggests_use_case'],
        'weight': 0.8,
    },
    {
        'task': 'Debug ST22 dump SYNTAX_ERROR in ZREPORT_MM line 245',
        'criteria': ['reads_dump_correctly', 'identifies_root_cause',
                     'proposes_fix', 'checks_related_objects'],
        'weight': 0.9,
    },
]

def evaluate_agent(agent_fn, test_cases=SAP_AGENT_EVAL_CASES, runs=3):
    """Run agent through all test cases, average scores across runs."""
    results = []

    for case in test_cases:
        scores = []
        for run in range(runs):
            output = agent_fn(case['task'])
            score = score_output(output, case['criteria'])
            scores.append(score)

        avg_score = sum(scores) / len(scores)
        results.append({
            'task': case['task'][:60],
            'avg_score': avg_score,
            'min_score': min(scores),
            'max_score': max(scores),
            'weight': case['weight'],
        })

    weighted_total = sum(r['avg_score'] * r['weight'] for r in results)
    total_weight = sum(r['weight'] for r in results)
    overall = weighted_total / total_weight

    return {
        'overall_score': overall,
        'results': results,
        'summary': f"Agent score: {overall:.2f}/1.00"
    }
```

## Integration with sap-crew-analysis

```
sap-crew-analysis evaluates ABAP code quality.
sap-llm-engineering evaluates the AGENT that generates ABAP code.

Combined loop:
  1. sap-llm-engineering: optimize prompt for ABAP generation
  2. Generate code with optimized prompt
  3. sap-crew-analysis: evaluate code (9 dimensions)
  4. abaplint: static lint check
  5. Feed results back → iterate prompt (step 1)
  → Converge on highest-scoring prompt template
```

## Gotchas

- **Eval data leakage**: Never evaluate on training prompts. Hold out 20% for eval.
- **SAP API version drift**: BAPI signatures change across S/4HANA versions. Version-tag eval cases.
- **ABAplint rules evolve**: Rule severity changes between versions. Pin abaplint version in eval.
- **LLM ABAP hallucinations**: Models invent non-existent BAPI names. Always validate against SAP system.
- **Token costs**: Full eval harness runs ~50K tokens per iteration. Budget 10-20 iterations for convergence.
- **SAP-specific syntax**: Generic code LLMs score poorly on ABAP. Use ABAP-fine-tuned models or extensive few-shot.
- **Security evals are mandatory**: Never skip security dimension — LLMs can introduce SQL injection in ABAP.
