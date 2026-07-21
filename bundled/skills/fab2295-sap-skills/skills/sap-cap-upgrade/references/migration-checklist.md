# Upgrade Checklist (canonical procedure)

The skill executes this exact sequence inside the project's working directory. Every step has an explicit purpose; the order matters because it isolates "version-caused" failures from pre-existing ones.

## Mode gate

The skill defaults to **plan** mode unless the invocation prompt explicitly authorizes apply mode (keywords listed in `SKILL.md` → "Modes"). Plan mode runs steps **0 → 2 → 7 (plan emit)** only — no edits, no install, no validation. Apply mode runs the full sequence below.

## 0. Preconditions

- `package.json` exists in `cwd`.
- `node` and `npm` resolvable in `PATH`.
- At least one in-scope package present (per `packages-catalog.md`). If not → emit `status:"no_changes"` and stop.

## 1. Capture baseline (BEFORE any bump) — apply mode only

Run, **without modifying anything**:

1. `npx --no-install cds build --production` (or `npx cds build` if `--production` not supported by the installed `@sap/cds-dk`).
2. If `package.json` has `scripts.test`, run `npm test -- --silent || true`.

Persist exit codes and stderr to memory as `baseline.failures[]` (one entry per non-zero command, with the captured stderr text **after** passing through `output-redaction.md`). Working memory is not the JSON output, but if the same string ever reaches `notes[]` later (e.g. via the `build_failed_unrelated` path), redaction MUST already have been applied at capture time — redacting only at emit time is a footgun. Do not write any files for this; it lives in memory.

If `cds build` is itself broken before any bump (baseline failure count > 0), all those errors are now part of `baseline.failures` and will **never** be reported as version-caused.

In **plan mode**, skip this step entirely — no commands run, no baseline captured.

## 2. Resolve target versions

For every dependency in `package.json` (under `dependencies`, `devDependencies`, `peerDependencies`, `optionalDependencies`) whose name matches the regex in `packages-catalog.md`:

```sh
npm view <pkg> dist-tags.latest
```

One call per package. Capture stdout. Aggregate into `{ "@sap/cds": "9.12.0", "@cap-js/sqlite": "2.6.0", ... }`.

## 2.5. Vulnerability gate (hard stop)

> **This step is mandatory in BOTH plan and apply modes.** It runs after every target version is resolved (step 2) and before anything is written or installed (step 3+). See `vulnerability-check.md` for the full contract.

For every `<pkg>@<target>` produced by step 2, query the advisory sources in this exact order:

1. **Primary — osv.dev** (no auth):

   ```sh
   curl -sS --max-time 10 -X POST 'https://api.osv.dev/v1/query' \
     -H 'Content-Type: application/json' \
     -d '{"package":{"name":"<pkg>","ecosystem":"npm"},"version":"<target>"}'
   ```

2. **Fallback — npm advisory bulk** (used ONLY when osv.dev returns 5xx, times out, or returns malformed JSON). Read the auth token via a one-shot env var so it does not appear on the visible command line; redact the Authorization echo from the response body before it reaches `notes[]`:

   ```sh
   NPM_AUTH_TOKEN=$(npm config get //registry.npmjs.org/:_authToken 2>/dev/null) \
   curl -sS --max-time 10 -X POST 'https://registry.npmjs.org/-/npm/v1/security/advisories/bulk' \
     -H 'Content-Type: application/json' \
     -H "Authorization: Bearer $NPM_AUTH_TOKEN" \
     -d '{"<pkg>":["<target>"]}'
   ```

   The skill MUST NOT echo this command, the env var value, or any HTTP request trace into stdout, stderr, or any captured string that may reach `notes[]`. Only the response body — already passed through `output-redaction.md` — may be referenced.

Normalize the response to severity ∈ {`critical`, `high`, `moderate`, `low`} per the mapping in `vulnerability-check.md`.

**Decision matrix:**

| Outcome | Action |
|---|---|
| No advisory | Keep bump in `bumped[]`. Continue. |
| Severity `low` | Keep bump in `bumped[]`. Add entry to `vulnerability_warnings[]`. Continue. |
| Severity `moderate \| high \| critical` | **Remove** bump from `bumped[]`. Add entry to `blocked_by_vulnerability[]`. After processing all targets, if `blocked_by_vulnerability[].length > 0`, set `status: "vulnerable_target"` and emit the JSON. **Stop.** Do not run step 3 or later. |
| Both sources failed (HTTP error / timeout / malformed JSON on both) | Set `status: "vuln_check_failed"`. Put both attempts' errors **redacted via `output-redaction.md`** in `notes[0]`. **Stop.** Fail-closed: do not proceed without a successful gate query. |

In **plan mode**, this is the last operational step. Build the JSON output and emit it. Do not proceed past this point.

In **apply mode**, only proceed to step 3 if `blocked_by_vulnerability[]` is empty AND the gate did not error. Otherwise emit the JSON and stop — same as plan mode for the gate-failure paths.

## 3. Apply bumps

Edit `package.json` in place. For each in-scope dep:
- Preserve the existing range operator (`^`, `~`, exact, or `>=`); replace only the numeric tail.
- If the current spec is a tag (`latest`, `next`) or a non-semver (URL, git+, file:), **skip** that dep and add a `notes` entry explaining why.
- Record `{name, from, to, major_jump: <bool>}` per bump.

Do **not** touch any other dependency, script, field, or formatting. Do not rewrite the file beyond the version strings.

## 4. Install

```sh
npm install --no-fund --no-audit
```

If exit code != 0 → emit `status:"install_failed"`. Put the captured stderr in `notes[0]` **after** passing it through `output-redaction.md` and **then** truncating to 4 KB (in that order — redacting after truncation can leave half a secret intact). Stop. Do not roll back: the user owns the lockfile.

## 5. Re-validate (AFTER bump)

Run the same commands as step 1 and capture `post.failures[]`.

## 6. Diff + attribute

Compute `new_failures = post.failures \ baseline.failures` (set difference by error signature: command + first 200 chars of stderr).

Apply `bug-attribution-rules.md` to every entry in `new_failures`. Each attempted attribution either:
- produces a `version_caused_bug` entry (regex hit + version-crossing match), or
- goes to `discarded[]` with `reason`.

## 7. Emit JSON

Last message of the skill is the strict JSON object documented in `SKILL.md` ("Output (contract com o agente)"). No additional prose after the JSON.

## Forbidden actions

- `git add`, `git commit`, `git push`, `git checkout`, `git restore`, `git stash` — never.
- Editing source files (anything outside `package.json` and `package-lock.json`/`npm-shrinkwrap.json`/`yarn.lock` as side-effect of `npm install`).
- Invoking any other skill or agent. The skill MUST NOT call `Skill`, `Agent`, or any equivalent tool. Acting on the report (applying source fixes for `version_caused_bugs[]`, regenerating CDS / docs, etc.) is the operator's call, made outside this skill.
- Running `npm publish`, `npm link`, `npm dedupe`, `npm prune --production`.
