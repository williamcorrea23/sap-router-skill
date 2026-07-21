# Security Audit — sap-cap-nodejs-dev

> Snapshot date: 2026-05-13
> Audited against the AI-agent / supply-chain attack surface that matters for a Claude Code
> skill (skill files = read-only docs an agent ingests + code samples the agent may produce).
> This file is part of the skill on purpose: it documents the rules the skill enforces so
> reviewers don't have to re-derive them.

## Scope of audit

A skill can fail in two ways:
1. **The skill itself** contains hostile content (prompt injection, hidden Unicode, malicious
   package refs, tool-poisoning instructions). Threat to *every* user of the skill.
2. **The skill teaches the agent unsafe patterns** (eval, raw SQL, dynamic require, weak
   auth, hardcoded secrets, overpermissive grants). Threat to projects built with the skill.

Both are checked below.

## Results matrix

| # | Vector | Status | Evidence / note |
|---|--------|--------|-----------------|
| 1 | Prompt Injection | clean | No "ignore previous / system prompt / you are now / jailbreak" phrases anywhere. |
| 2 | Indirect Prompt Injection | clean | No untrusted content embedded; all examples are static SAP/CAP content. |
| 3 | Tool Poisoning | clean | No tool redefinitions or override instructions. |
| 4 | MCP Poisoning | clean | Only references the **official** `@cap-js/mcp-server` (github.com/cap-js/mcp-server, announced on SAP community blog). |
| 5 | Context Poisoning | clean | All linked docs go to `cap.cloud.sap`, `github.com/cap-js`, `community.sap.com`. |
| 6 | Prompt Leakage | clean | No "reveal / print / dump prompt" patterns. |
| 7 | Jailbreak | clean | No bypass instructions. |
| 8 | Agent Hijacking | clean | No second-agent instructions, no role swaps. |
| 9 | Rogue Tool Execution | clean | Skill defines no tools; doesn't instruct calling arbitrary tools. |
| 10 | Unsafe Auto-Execution | clean | No `--unsafe-perm`, no `rejectUnauthorized: false`, no `trust-all`, no auto-run flags. |
| 11 | Unsafe Code Generation | hardened | Postgres example credentials now labeled **dev-only**; mocked-auth section now has explicit DEV-ONLY banner; `cds.User.Privileged` carries strong warning. Sample search handler uses CQL builder (`{ like: \`%${q}%\` }`) — value is parameterized by CAP, not concatenated into SQL. |
| 12 | Secret Exfiltration | clean | Zero real secrets. All `password`/`apiKey` values are placeholders (`"..."`) or mocked dev defaults (alice/bob). |
| 13 | Token Leakage | clean | No Bearer tokens, no JWTs (`eyJ…`), no `aws_access_*` patterns. |
| 14 | Credential Leakage | hardened | Mocked auth + Postgres example explicitly scoped to `[development]` profile with DEV-ONLY banners. CI samples use `${{ secrets.CF_* }}` (correct cofre pattern). |
| 15 | Overpermission | hardened | `grant: '*'` patterns are scoped to admin role or `where: 'parent.customer.userId = $user'` (row-level). `cds.User.Privileged` documented with a strong warning. |
| 16 | Excessive Privileges | hardened | Same as 15. No `chmod 777`, no global writes, no `sudo`. |
| 17 | Supply Chain Attack | clean | All npm packages are under official scopes: `@sap/*`, `@cap-js/*`, `@cap-js-community/*`, plus `express`, `jest`, `mbt`. No unscoped names that could be hijacked. |
| 18 | Dependency Confusion | clean | No internal-looking unscoped names. Scoped packages can't be confused with public unscoped ones. |
| 19 | Malicious Package Injection | clean | No third-party unverified packages. |
| 20 | Insecure Plugin Loading | clean | No dynamic `require()`/`import()` with user input. CAP plugin loading goes through the documented `cds.plugin` mechanism. |
| 21 | Arbitrary Command Execution | clean | No `execSync`, `child_process`, `spawn`, `os.system`, `shelljs`. |
| 22 | Command Injection | clean | No shell construction from request data. |
| 23 | Path Traversal | clean | No `fs.read*` / `fs.write*` / `path.join` with `req.*` inputs. |
| 24 | Arbitrary File Read | clean | Same as 23. |
| 25 | Arbitrary File Write | clean | Same as 23. |
| 26 | SSRF | clean | No `fetch(req.X)` / `axios(req.X)` / `new URL(req.X)` patterns. Remote service calls go through documented `cds.connect.to(<name>)` with pre-configured destinations. |
| 27 | Unsafe Deserialization | clean | No `JSON.parse(req.body)` of attacker-shaped input; no `yaml.load`; no `node-serialize`. |
| 28 | Eval Injection | clean | No `eval()`, `new Function()`, `vm.runInContext()`, `vm.runInNewContext()`. |
| 29 | Sandbox Escape | n/a | Skill has no sandbox layer. |
| 30 | Retrieval Poisoning | clean | The MCP `search_docs` tool ships with the official, locally-cached SAP docs. No user-controlled corpus. |
| 31 | Vector Database Poisoning | clean | No external vector DB. HANA `Vector(1536)` mentioned is a column type, not a DB. |
| 32 | Embedding Poisoning | clean | No code ingests embeddings from untrusted sources. |
| 33 | Training Data Poisoning | n/a | Skill does not train anything. |
| 34 | Fine-Tuning Poisoning | n/a | Same. |
| 35 | Backdoored Model Injection | n/a | No model loading. |
| 36 | Malicious MCP Server | clean | The only MCP server referenced is `@cap-js/mcp-server` from the official `cap-js` GitHub org. |
| 37 | Unauthorized Deploy | clean | `cf push` / `cf deploy` / `mbt build` snippets are user-driven examples; CI snippets gate everything behind `${{ secrets.CF_* }}`. Skill never tells the agent to auto-deploy. |
| 38 | Configuration Injection | clean | No untrusted-string interpolation into config. |
| 39 | Environment Variable Injection | clean | No `$VAR` interpolation into shell commands from user input. |
| 40 | Telemetry Leakage | clean | `@cap-js/telemetry` is referenced as OpenTelemetry config; no examples emit PII/credentials to traces. |
| 41 | Observability Data Exposure | clean | No `console.log(req.body)` / `cds.log(...password...)` patterns. |

## Hardened items applied during audit

- **Postgres credential example** ([databases.md](databases.md)): added explicit dev-only banner; default
  password no longer matches the credential field name (anti-pattern that triggers some scanners).
- **Mocked authentication** ([nodejs-runtime.md](nodejs-runtime.md), [templates/package.json](../templates/package.json)): clarified DEV-ONLY scope; profile `[development]` reaffirmed as the only place it appears.
- **`cds.User.Privileged`** ([nodejs-runtime.md](nodejs-runtime.md)): strong warning added — never derive from `req.*`.
- **Java content** removed across the corpus (skill scope is Node.js-only); reduces surface a reviewer has to validate.
- **`SKILL.md`** scope guardrails + Public-API rule already forbid: internal `@sap/cds/lib/*` paths, deprecated/experimental APIs, raw SQL strings, custom OData/REST/GraphQL providers, role checks in JS where annotations would do, frontend/other-stack work.

## Standing rules the skill must enforce on agent output

The skill itself codifies these — they are not just audit notes:

1. **Never** import from `@sap/cds/lib/...`, `_private`, `__internal`, or any undocumented path.
2. **Never** use methods/options flagged `@deprecated`, `@experimental`, `@internal`, `@protected`.
3. **Never** concatenate SQL strings; use the CQL builder. Drop to `cds.db.run('SELECT …')` only when CQL cannot express it.
4. **Never** hardcode credentials in `package.json` / `.cdsrc.json` for non-`[development]` profiles. Use service bindings / env / `cds bind`.
5. **Never** check roles in JS when `@requires` / `@restrict` can express it.
6. **Never** call `cds.User.Privileged` based on anything in `req.*` or external input.
7. **Never** write UI code or non-CAP-Node.js backend code from this skill.
8. **Never** spawn child processes from a handler.
9. **Never** `require()` / `import()` a path derived from request data.
10. **Never** disable TLS verification, mark `rejectUnauthorized: false`, or pass `--unsafe-perm`.

## Reviewer quick-check (for `skills.sh` audit)

```sh
# from inside the skill dir:
grep -rniE "ignore (previous|prior|above|all)|jailbreak|system prompt|you are now" . | grep -v 'security-audit.md'        # PI
python3 -c "import re,os,sys; bad=re.compile(r'[​-‏‪-‮⁠-⁯﻿]'); [print(p,i) for r,_,fs in os.walk('.') if '/.git' not in r for f in fs if f.endswith(('.md','.json','.cds','.js','.ts','.yaml')) for p in [os.path.join(r,f)] for i,l in enumerate(open(p,errors='replace'),1) if bad.search(l)]"  # hidden unicode
grep -rniE 'eval\(|new Function\(|execSync|child_process|spawn|os\.system' --include='*.md' --include='*.js' --include='*.ts'                                                                       # code exec
grep -rniE '"(password|secret|api[_-]?key|token)"\s*:\s*"[^"$\{][^"]{3,}"' .                                                                                                                       # credentials
grep -rEho 'https?://[^ )\"\\\\]+' . | sort -u | grep -vE 'cap\.cloud\.sap|cap-js|sap\.com|ui5\.sap\.com|npmjs\.com|cloudfoundry|example\.com|your-org|localhost|ondemand\.com'                       # untrusted URLs
```

Each command must return zero hits (after excluding `security-audit.md`) for the skill to
pass.
