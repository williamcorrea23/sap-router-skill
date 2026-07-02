---
name: sap-llm-engineering
description: LLM engineering patterns for SAP AI — eval harnesses, prompt optimization, RAG pipelines, training data curation, agent quality measurement
trigger:
  keywords: [prompt engineering abap, evaluate abap generation, llm for sap, fine-tune abap model, rag pipeline sap, genai evaluation, agent eval sap]
  intent: Building eval-first LLM workflows for SAP ABAP/BTP/CPI code generation
---
# SAP LLM Engineering — Eval-First Patterns for SAP AI

Adapts Karpathy's LLM engineering methodology (build eval first, iterate on
metrics not vibes) to SAP ABAP/BTP/CPI contexts. The eval IS the product —
prompts are just configuration.

## Prerequisites

- `abaplint` installed and pinned to a specific version (rule sets evolve)
- SAP ADT or abaplint CLI for syntax validation
- LLM API access (for generation + optional embedding)
- `sap-crew-analysis` skill loaded (companion for code-quality scoring)
- 20% of training data held out as eval set — never evaluate on training prompts

## Core Principle

```
Build eval → Measure baseline → Improve prompt → Re-measure → Repeat
  (NOT: Write prompt → Hope it works → Manual review)
```

## Steps

### 1. Build Evaluation Harness (Before Any Prompt Work)

Define what "good ABAP" means across 7 dimensions:

```python
EVAL_DIMENSIONS = {
    'abaplint_pass':    'abaplint --format json → zero errors',
    'syntax_ok':        'ADT syntax check passes',
    'unit_test_pass':   'ABAP Unit test methods all green',
    'clean_abap_score': 'Clean ABAP compliance ≥ 70/100',
    'bapi_correctness': 'Import/export params match BAPI signature',
    'security_ok':      'No SQL injection, no auth-check gaps',
    'performance_ok':   'No SELECT *, no SELECT-in-loop',
}
```

Run eval on every LLM output:

```python
def evaluate(generated_code: str, spec: dict) -> dict:
    results = {
        'abaplint': run_abaplint(generated_code),
        'syntax': run_adt_syntax_check(generated_code),
        'security': audit_security(generated_code),
        'performance': audit_performance(generated_code),
    }
    if spec.get('bapi_name'):
        results['bapi'] = verify_bapi_signature(generated_code, spec['bapi_name'])
    return {
        'pass': all(r['pass'] for r in results.values()),
        'score': sum(r['score'] for r in results.values()) / len(results),
        'details': results,
    }
```

### 2. Establish Baseline

```bash
# Run current prompt against eval set, record scores
python eval_abap_llm.py --prompt baseline.json --eval-set holdout_20pct.json
# Output: baseline_score=0.42 — security dimension failing 80% of cases
```

### 3. Optimize Prompt (Iterate on Failures)

```python
# prompt_optimizer.py — fix prompt, not output
PROMPT_BAPI = """
You are an expert ABAP developer. Write a method calling {bapi_name}.
Requirements:
- Modern ABAP (inline declarations, NEW constructor)
- Always call BAPI_TRANSACTION_COMMIT with WAIT = 'X'
- Check BAPIRET2 tables, not just RETURN
- Handle errors with CX_STATIC_CHECK
- Include ABAP Unit test class with {min_tests} methods
ABAP version: {version}  Package: {package}
"""

def optimize(template, spec, eval_fn, max_iter=10):
    best_score, best_prompt = 0, None
    for i in range(max_iter):
        code = call_llm(template.format(**spec))
        result = eval_fn(code, spec)
        if result['score'] > best_score:
            best_score, best_prompt = result['score'], template
        if result['pass']:
            break
        spec = inject_failure_feedback(spec, result)  # feed failures back
    return best_prompt, best_score
```

### 4. Curate Training Data (For Fine-Tuning)

Extract `(instruction, signature, body)` triples from existing ABAP repos:

```python
QUALITY_FILTERS = [
    'abaplint_pass',           # must pass static analysis
    'syntax_check_pass',        # must compile
    'unit_test_pass',           # tests must pass
    'not_generated_code',       # exclude SAP standard generated code
    'clean_abap_score >= 70',   # quality threshold
]
# Sources: method implementations, BAPI wrappers, RAP behaviors, CDS views, unit tests
```

### 5. Build RAG Pipeline for SAP Knowledge

Chunk SAP docs by entity type for better retrieval:

```python
CHUNK_STRATEGIES = {
    'bapi':       {'split_on': 'FUNCTION ',    'max': 4000, 'meta': ['BAPI_NAME', 'MODULE']},
    'cds_view':   {'split_on': 'DEFINE VIEW ', 'max': 2000, 'meta': ['ENTITY_NAME']},
    'sap_note':   {'split_on': '## Solution',  'max': 8000, 'meta': ['NOTE_NUMBER', 'VERSION']},
    'abap_class': {'split_on': 'METHOD ',      'max': 1500, 'meta': ['CLASS_NAME', 'METHOD_NAME']},
}
```

Query with context:

```python
def generate_with_rag(question: str) -> str:
    context = vector_store.similarity_search(question, k=5)
    return call_llm(build_rag_prompt(question, context))
```

### 6. Evaluate Agent (Not Just Code)

```python
AGENT_EVAL_CASES = [
    {'task': 'Create ZCL_MATERIAL_HELPER with BAPI_MATERIAL_SAVEDATA wrapper',
     'criteria': ['syntax_valid', 'abaplint_pass', 'bapi_params_correct',
                  'has_error_handling', 'has_unit_test', 'clean_abap_70plus']},
    {'task': 'Debug ST22 dump SYNTAX_ERROR in ZREPORT_MM line 245',
     'criteria': ['reads_dump', 'identifies_root_cause', 'proposes_fix']},
]
# Run 3× per case, average scores, compute weighted total
```

### 7. Integration with sap-crew-analysis

`sap-llm-engineering` optimizes the PROMPT; `sap-crew-analysis` evaluates the CODE.
Loop: optimize prompt → generate → evaluate code → feed back → iterate.

## Pitfalls

- **Eval data leakage inflates scores**
  - Cause: Eval prompts overlap with training/few-shot examples in the prompt.
  - Solution: Hold out 20% of cases in a separate file. Never include them in few-shot examples.

- **LLM hallucinates non-existent BAPI names**
  - Cause: Generic LLMs trained on web data invent plausible-sounding BAPI names.
  - Solution: Validate every BAPI name against the SAP system via `mcp_sap_bapi_call` or `RFC_FUNCTION_SEARCH` before accepting generated code.

- **abaplint rule changes break eval reproducibility**
  - Cause: abaplint updates change rule severity between versions.
  - Solution: Pin abaplint version in `requirements.txt`. Re-baseline when upgrading.

- **Security dimension silently skipped**
  - Cause: Security checks are slower and teams deprioritize them.
  - Solution: Make `security_ok` a hard gate — eval fails if security check doesn't run. LLMs can introduce SQL injection in ABAP via dynamic WHERE clauses.

- **Token budget exhausted before convergence**
  - Cause: Full eval harness burns ~50K tokens per iteration × 10+ iterations.
  - Solution: Budget 15-20 iterations. Use cheaper model for initial screening, expensive model for final candidates.

- **Generic code LLMs score poorly on ABAP**
  - Cause: ABAP syntax is underrepresented in general training data.
  - Solution: Use extensive few-shot examples (5+ ABAP snippets). Consider fine-tuned models or RAG-augmented generation.

## Verification

- [ ] Eval harness covers all 7 dimensions (abaplint, syntax, unit test, clean ABAP, BAPI, security, performance)
- [ ] Baseline score recorded before any prompt optimization
- [ ] Eval set is separate from training/few-shot data (20% holdout)
- [ ] abaplint version pinned in project dependencies
- [ ] Every generated BAPI name validated against live SAP system
- [ ] Security dimension is a hard gate (not optional)
- [ ] Agent eval run 3× per case with averaged scores
- [ ] Prompt revision history tracked (iteration, score, failures)
- [ ] RAG chunks tagged with entity-type metadata for filtering
