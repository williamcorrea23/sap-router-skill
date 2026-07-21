# Security Audit — sap-cap-nodejs-dev

**Skill version**: 3.1.0
**Audit date**: 2026-05-13
**Scope**: full content of [SKILL.md](SKILL.md), [README.md](README.md), every file under
[references/](references/) and [templates/](templates/).

This document records the threat-model checks applied to the skill. It is meant to be
reproducible by `skills.sh` (or any auditor) using the grep / Python heuristics described
below. The skill is **read-only documentation** that an LLM agent ingests; it does not run
its own code at install time, register tools, or load remote resources.

---

## Posture summary

| # | Threat | Verdict | Notes |
|---|--------|---------|-------|
| 1 | Prompt Injection | PASS | No override / role-swap / "ignore previous" patterns. |
| 2 | Indirect Prompt Injection | PASS | All embedded URLs are SAP / `cap-js` / npm registry — no untrusted instructions hosted there to be re-fetched. |
| 3 | Tool Poisoning | PASS | Skill exposes no tools. The only "tool" reference is `@cap-js/mcp-server` (official). |
| 4 | MCP Poisoning | PASS | Only the official `@cap-js/mcp-server` is configured; sources at `github.com/cap-js/mcp-server`. |
| 5 | Context Poisoning | PASS | No hidden/zero-width Unicode, no RTL overrides. |
| 6 | Prompt Leakage | PASS | No instructions that ask the agent to dump or reveal the system prompt. |
| 7 | Jailbreak | PASS | No DAN / "developer mode" / role-replacement copy. |
| 8 | Agent Hijacking | PASS | Skill content is descriptive; it does not redirect the agent to other instructions. |
| 9 | Rogue Tool Execution | PASS | No instructions to call undocumented tools or external endpoints. |
| 10 | Unsafe Auto-Execution | PASS | No `--no-verify`, no `--unsafe-perm`, no `rejectUnauthorized:false`, no auto-deploy. |
| 11 | Unsafe Code Generation | PASS | Anti-patterns (raw SQL with template literals, role checks in handlers) are explicitly listed as "DON'T". |
| 12 | Secret Exfiltration | PASS | No `console.log(req.headers)` / log-of-credentials patterns. |
| 13 | Token Leakage | PASS | No bearer/JWT literals; CI examples use `${{ secrets.* }}`. |
| 14 | Credential Leakage | PASS (with notes) | Only mocked dev credentials (`alice`/`bob`) and an example postgres password — both are `[development]`-profile gated and called out as dev-only. |
| 15 | Overpermission | PASS (with notes) | `cds.User.Privileged` is documented with an explicit warning to never derive from `req.*`. `grant: '*'` examples are scoped to `Admin` / owner row-filter (`where: 'parent.customer.userId = $user'`). |
| 16 | Excessive Privileges | PASS | Skill teaches `@requires` / `@restrict` and explicitly forbids `req.user.is(...)` role checks in handlers. |
| 17 | Supply Chain Attack | PASS | All recommended packages are `@sap/*`, `@cap-js/*`, `@cap-js-community/*`, plus widely-used `express`, `jest`, and the SAP MTA build tool `mbt`. |
| 18 | Dependency Confusion | PASS | All packages are scoped (`@sap/...`, `@cap-js/...`); no unscoped names that could be hijacked on public npm. |
| 19 | Malicious Package Injection | PASS | No `curl … \| sh`, no `wget … \| bash`, no postinstall script tricks, no `--registry` overrides. |
| 20 | Insecure Plugin Loading | PASS | No `require(<dynamic>)`, no `cds-plugin` loaded from user-controlled paths. |
| 21 | Arbitrary Command Execution | PASS | No `child_process`, `exec`, `execSync`, `spawn`, `shelljs` in any example. |
| 22 | Command Injection | PASS | No shell-string concatenation with input. |
| 23 | Path Traversal | PASS | No `fs.read*` / `path.join` with user input in samples. |
| 24 | Arbitrary File Read | PASS | No examples that read files based on request fields. |
| 25 | Arbitrary File Write | PASS | No examples that write files based on request fields. |
| 26 | SSRF | PASS | No `fetch(req.*)` / `axios(req.*)` / `new URL(req.*)` patterns. |
| 27 | Unsafe Deserialization | PASS | No `JSON.parse(req.body)` of untrusted input, no `yaml.load`, no `node-serialize`. |
| 28 | Eval Injection | PASS | No `eval`, `new Function`, `vm.runInNewContext`. |
| 29 | Sandbox Escape | N/A | Skill defines no sandbox. |
| 30 | Retrieval Poisoning | PASS | The skill does not stand up a RAG pipeline. The CAP MCP server is referenced but it is the official one. |
| 31 | Vector Database Poisoning | N/A | No vector-DB content authored by this skill (HANA `Vector(1536)` example is a column type, not data). |
| 32 | Embedding Poisoning | N/A | No embeddings produced by the skill. |
| 33 | Training Data Poisoning | N/A | Skill is not training data. |
| 34 | Fine-Tuning Poisoning | N/A | No fine-tuning. |
| 35 | Backdoored Model Injection | N/A | No model weights loaded. |
| 36 | Malicious MCP Server | PASS | Only `@cap-js/mcp-server` from `github.com/cap-js/mcp-server` (official SAP CAP org). |
| 37 | Unauthorized Deploy | PASS | All `cf deploy` / `mbt build` examples are user-driven; CI examples gate everything behind `${{ secrets.* }}`. The skill itself never invokes deploys. |
| 38 | Configuration Injection | PASS | No `${USER_INPUT}` interpolation into config files. |
| 39 | Environment Variable Injection | PASS | Env vars used (`NODE_ENV`, `POSTGRES_PASSWORD`) appear only in trusted local-dev / CI examples. |
| 40 | Telemetry Leakage | PASS | The only telemetry referenced is `@cap-js/telemetry` (OpenTelemetry); no code that pushes user PII to external endpoints. |
| 41 | Observability Data Exposure | PASS | No examples that log `req.user`, `req.headers`, or credentials. |

---

## Reproducible audit checks

Run from the skill root.

```sh
# 1. Prompt-injection / jailbreak phrases
grep -rniE "ignore (previous|prior|above|all)|disregard|forget (everything|previous)|system prompt|you are now|new (role|instructions)|jailbreak|act as|override (instructions|prompt)|developer mode|dan mode|pretend (you|to)" \
  --include="*.md" --include="*.json" --include="*.yaml" --include="*.cds" --include="*.js" --include="*.ts"

# 2. Hidden Unicode (zero-width, RTL override, BOM)
python3 -c "
import os, re, sys
ranges = list(range(0x200B,0x200F+1))+list(range(0x202A,0x202E+1))+list(range(0x2060,0x206F+1))+[0xFEFF,0x061C]
bad = set(ranges)
hits = 0
for r,_,fs in os.walk('.'):
    if '/.git' in r: continue
    for f in fs:
        if not f.endswith(('.md','.json','.yaml','.cds','.js','.ts')): continue
        for i,line in enumerate(open(os.path.join(r,f),encoding='utf-8',errors='replace'),1):
            if any(ord(c) in bad for c in line):
                print(f'{r}/{f}:{i}'); hits += 1
sys.exit(1 if hits else 0)
"

# 3. Eval / dynamic code
grep -rEn 'eval\s*\(|new Function\s*\(|vm\.runInNew' --include='*.md' --include='*.js' --include='*.ts'

# 4. Command exec
grep -rEn 'execSync|spawn(Sync)?|child_process|cp\.exec|shelljs|os\.system' --include='*.md' --include='*.js' --include='*.ts'

# 5. SSRF / fetch with input
grep -rEn 'fetch\(\s*req\.|axios\.[a-z]+\(\s*req\.|http\.get\(\s*req\.|new URL\(\s*req\.' --include='*.md' --include='*.js' --include='*.ts'

# 6. Path traversal / arbitrary file ops
grep -rEn 'fs\.(read|write|append|unlink).*req\.|require\(\s*req\.|path\.join.*req\.' --include='*.md' --include='*.js' --include='*.ts'

# 7. Hardcoded secrets (excluding mocked-dev profile)
grep -rEn '"(password|secret|api[_-]?key|token|access[_-]?key)"\s*:\s*"[^"$\{<][^"]{3,}"' \
  | grep -v '\[development\]' | grep -v '"alice"\|"bob"\|"postgres"'

# 8. Bearer / JWT literals
grep -rEn 'Bearer [A-Za-z0-9._-]{20,}|eyJ[A-Za-z0-9_-]+\.eyJ'

# 9. TLS bypass
grep -rEn 'rejectUnauthorized\s*:\s*false|strict-ssl\s*=?\s*false|trustAll|SSL_VERIFY_NONE'

# 10. npm hardening bypass / untrusted install
grep -rEn 'unsafe-perm|--ignore-scripts\s*false|curl[^|]*\|\s*npm|--registry\s+http'

# 11. Hidden Unicode AND non-SAP package scopes (supply chain)
grep -rEho '"@?[a-z0-9][a-z0-9._/-]+":\s*"[\^~0-9]' --include='*.json' | sort -u

# 12. .env or secret files committed
find . -name '.env*' -not -path './.git/*' -o -name 'secrets.*' -not -path './.git/*'
```

All twelve checks return **no findings** for this skill version (modulo the documented
mocked-dev credentials, which are profile-gated and explicitly labeled).

---

## Trusted source list

The skill references only the following external sources:

- `https://cap.cloud.sap/docs/...` — official SAP CAP documentation
- `https://github.com/cap-js/...` — official `cap-js` GitHub org (CAP project)
- `https://github.com/cap-js-community/...` — official community org
- `https://github.com/SAP/cloud-security-xsuaa-integration/...` — official SAP repo
- `https://community.sap.com/...` — official SAP community
- `https://www.npmjs.com/package/...` — npm registry
- `https://ui5.sap.com` — official UI5 CDN
- `https://plugins.cloudfoundry.org` — official CF plugin index
- `https://github.com/cloudfoundry/cli/releases` — official CF CLI releases
- `https://bestofcapjs.org/` — community curated list

Placeholders (`api.example.com`, `myapp.example.com`, `your-org/...`, `localhost`,
`*.cfapps.eu10.hana.ondemand.com`) are explicit examples, not active references.

---

## Hardenings applied during this audit

- [references/databases.md](references/databases.md): postgres example moved into a
  `[development]`/`[production]` profile split, with an explicit warning that production
  credentials must come from `cds bind` / VCAP / env vars and never from `package.json`.
- [references/nodejs-runtime.md](references/nodejs-runtime.md): added an explicit warning
  on `cds.User.Privileged` ("Bypasses ALL authorization — never derive from `req.*`") and a
  "mocked is DEV-ONLY" callout above the alice/bob example.
- The `Senua` legacy name was retired; the skill is published as `sap-cap-nodejs-dev`
  with strict CAP-Node.js scope and a public-API-only rule (see SKILL.md §1, §2).

---

## Out of scope (by design)

- The skill **does not** generate, run, or schedule code on its own. All code samples are
  illustrative and must be reviewed by the operator.
- The skill **must refuse** any request outside SAP CAP Node.js (UI/frontend, other
  backend stacks, non-CAP architectures, or any use of internal/protected/deprecated CAP
  APIs). See SKILL.md §1.
