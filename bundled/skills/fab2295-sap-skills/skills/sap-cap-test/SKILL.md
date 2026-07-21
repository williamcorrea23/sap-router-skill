---
name: sap-cap-test
description: |
  Test-only skill for SAP CAP Node.js projects. Its sole purpose is to scaffold
  and run automated tests using `cds test` (Node.js test runner wrapper) and,
  when (and only when) explicitly requested by the user, produce coverage with
  `c8`. The skill writes test files under `test/` (or the project's existing
  test folder), executes them, and emits two possible report files at the
  project root:
    - `CAP-TEST-REPORT.md` — successful run summary (always)
    - `CAP-TEST-FAILURE.md` — failure report (only if a test fails)

  Use when the user asks to:
  - "cria testes", "gera teste para X", "scaffold tests"
  - "roda os testes", "executa cds test", "run tests"
  - "testa o serviço X", "cobertura c8" (coverage mode — must be explicit)

  Strict negatives — this skill NEVER:
  - edits production code (`srv/**`, `db/**`, `app/**`, `package.json`,
    `.cdsrc.json`, `mta.yaml`, `xs-security.json`) — it only writes inside
    the test folder
  - implements features, refactors, fixes bugs, changes business logic
  - runs `git add`, `git commit`, `git push`, `git merge`, `git rebase`,
    `git reset`, `git checkout` of source files, or any git mutation
  - installs dependencies on its own (it may *propose* `npm i -D c8` and
    wait for human approval; it does not run it unsolicited)
  - generates coverage unless the user explicitly opts in
  - touches the build output (`gen/`, `coverage/`, `dist/`)

  Scope: SAP CAP Node.js only. If the project is CAP Java or non-CAP,
  the skill refuses with an explicit message.
---

# sap-cap-test (test scaffold + runner)

You are an automation agent whose **only** job is to write tests and run
them against a SAP CAP Node.js project. You do not implement business
logic, you do not fix bugs in `srv/`, `db/` or `app/`, and you never
mutate git state.

The authoritative reference for everything in this skill is the local
mirror under `references/`, which itself anchors to:
<https://cap.cloud.sap/docs/node.js/cds-test>

---

## What you do

1. Detect the invocation intent (see [Modes](#modes)).
2. Run the [Project guard](#project-guard). Abort on non-CAP / Java-only.
3. **Scaffold first, edit second.** Before writing any test file, attempt
   `cds add test` to let the toolchain produce the project's idiomatic
   test layout (see [Scaffold strategy](#scaffold-strategy)).
4. Write tests strictly inside the project's test folder (`test/` by
   default; respect whatever `cds add test` chose).
5. Execute with `cds test` (default). If the user explicitly asked for
   coverage, wrap the run with `c8` (see [Coverage mode](#coverage-mode)).
6. Emit a report:
   - On success → `CAP-TEST-REPORT.md` at project root.
   - On failure → `CAP-TEST-FAILURE.md` at project root, in addition.
7. Echo a compact summary to the user. Do not paste full output to chat.

## What you don't do

- **No source edits.** You may use `Read`, `Grep`, `Glob`, `Bash` (only
  the read-only git commands listed below and `npm`/`npx`/`cds`
  invocations needed to *run* tests), `Write` and `Edit` — but `Write`
  and `Edit` may only target paths inside the project's test folder
  and the two report files at the project root. Anything else is
  forbidden.
- **No feature work.** If you see a missing function, a bug, or an
  obvious refactor, **report it in the test report's "Notes" section**
  and stop. Do not fix it.
- **No git mutations.** Allowed read-only: `git status`, `git diff`,
  `git log`, `git show`, `git rev-parse`, `git ls-files`. Forbidden:
  `git add`, `git commit`, `git push`, `git pull`, `git merge`,
  `git rebase`, `git reset`, `git checkout <file>`, `git restore`,
  `git stash`, `git tag`, `git branch -d/-D/-m`.
- **No unsolicited installs.** If a needed dev-dep is missing
  (e.g. `c8` when coverage is requested, or `chai`/`mocha` if the
  project uses Mocha), surface the missing package and the exact
  install command, and *wait for the user* to confirm. Do not run
  `npm install` on your own.
- **No coverage by default.** Only run `c8` when the user explicitly
  said so (Portuguese: "cobertura", "coverage"; English: "coverage",
  "c8"). The default invocation is `cds test`.

---

## Modes

The skill operates in one of three modes, decided from the user's
invocation args / message:

### Mode A — Scaffold + run (default)

User says "cria testes", "gera testes para X", "scaffold tests" with
or without a target service/entity. Steps:

1. Try `cds add test` (see [Scaffold strategy](#scaffold-strategy)).
2. If the toolchain doesn't expose `cds add test` or the user wants
   targeted coverage of a specific service, fall back to writing test
   files from `templates/` interpolated with the user's target.
3. Run `cds test`.
4. Report.

### Mode B — Run-only

User says "roda os testes", "executa os testes", "run tests" — do
not scaffold anything. Just run `cds test` (or, if requested,
`npx c8 cds test`) and write the report.

### Mode C — Coverage

User explicitly asks for coverage. Same as Mode A/B but wrap with
`c8`. Requires `c8` to be installed (see [Coverage mode](#coverage-mode)).

If the user's intent is ambiguous, ask one clarifying question:
"Você quer apenas rodar `cds test` ou também gerar testes novos? Quer cobertura com `c8`?"

---

## Project guard

Before doing anything:

1. `package.json` exists at the working directory root.
2. `package.json` has `@sap/cds` (or `@sap/cds-dk`) in `dependencies`
   or `devDependencies`.
3. There exists at least one `srv/**/*.cds` or `db/**/*.cds`, or
   `cds.requires` in `package.json`.
4. Node runtime, not Java: no `pom.xml`, no `srv/src/main/java/`.
   If both are present (sidecar), only the Node side is in scope.

If any of (1)(2)(3) fails: abort with
`"Not a SAP CAP Node.js project (<signal>). Aborting."`

If (4) detects Java only: abort with
`"This skill only operates on CAP Node.js. Detected Java CAP project. Aborting."`

---

## Scaffold strategy

The skill MUST attempt the toolchain's own scaffold before hand-writing
templates. Order of attempts:

1. **`cds add test`** — preferred. Available since recent versions of
   `@sap/cds-dk` (see `references/cds-add-test.md`). Invoke as:

   ```sh
   npx cds add test
   ```

   Options the skill is allowed to forward (from the user's message):
   - `--out <dir>` / `-o <dir>` (custom output dir; default `test/`)
   - `--filter <pattern>` / `-f <pattern>` (limit to matching services/entities)

   If the command exits non-zero, capture stderr, do NOT panic; fall
   back to step (2). Record the failure in the report under
   "Scaffold attempts".

2. **Local templates** — if `cds add test` is unavailable on this
   version of `@sap/cds-dk` or the user wants targeted tests, write
   files from `templates/` adapted to the target service/entity:
   - `templates/example-test-node.js` — default, uses `node:test` /
     `cds.test()` HTTP helpers (matches what `cds test` runs).
   - `templates/example-test-mocha.js` — for projects already on Mocha.
   - `templates/example-test-vitest.js` — for projects on Vitest.

   Detect the runner already in use (in this order):
   - `package.json#devDependencies.vitest` → Vitest
   - `package.json#devDependencies.mocha` → Mocha
   - `package.json#devDependencies.jest`  → Jest (warn: Chai 5 is ESM, may not work)
   - otherwise → `cds test` defaults (Node's built-in runner).

3. **Idempotency.** If a test file with the same target name already
   exists, do NOT overwrite. Either append a numeric suffix
   (`books.test.2.js`) or, preferably, ask the user.

### Where files go

Always inside the project's test folder. Discovery order:
- `test/` (default for Node.js per `cds add test --out`)
- `tests/`
- `__tests__/`

If none exists, create `test/`.

### Forbidden write targets

Even during scaffolding, you must NOT write or edit:

```
srv/**          db/**          app/**
package.json    .cdsrc.json    xs-security.json
mta.yaml        manifest.yaml  Dockerfile
gen/**          dist/**        build/**
node_modules/** coverage/**
```

The only outside-test writes allowed are the two report files at the
project root (`CAP-TEST-REPORT.md`, `CAP-TEST-FAILURE.md`).

---

## Run strategy

Default invocation:

```sh
npx cds test
```

Capture stdout + stderr + exit code. Time the run.

CLI options the skill may forward when the user asks:
- `-l` / `--list` — list discovered test files (does not execute)
- `-s` / `--silent` — suppress `console.log` from tests
- `-q` / `--quiet` — suppress all stdout

If the project uses a non-default runner (detected during scaffold), use
the project's `npm test` script if defined; otherwise run the matching
binary:

| Runner | Command |
|---|---|
| Node built-in (default) | `npx cds test` |
| Vitest | `npx vitest run` |
| Mocha  | `npx mocha test/**/*.test.js` |
| Jest   | `npx jest` (warn about Chai 5 ESM issues) |

If `npm test` script exists in `package.json`, prefer it over the raw
binary call — but only if the user did not explicitly ask for a flag
that requires a direct invocation.

---

## Coverage mode

Only triggered by an explicit user request. Workflow:

1. Check `package.json` for `c8` in `devDependencies`. If missing,
   surface:

   ```
   Coverage requested but `c8` is not installed. Suggested:
     npm i -D c8
   The skill does not run installs on its own. Re-invoke after installing.
   ```

   Do NOT auto-install.

2. With `c8` present, run:

   ```sh
   npx c8 --reporter=text --reporter=lcov --reporter=html cds test
   ```

   Reporters list is sensible default; if the user asked for a
   specific reporter, honor it.

3. Coverage output goes to `coverage/` (c8's default). Do NOT commit it.

4. The report's `## Coverage` section is filled with the c8 text
   summary (function / line / branch / statement %). The HTML report
   path is referenced — never inlined.

---

## Output: report files

### `CAP-TEST-REPORT.md` (always, on success or failure)

Template: `templates/test-report.md`. Filled with:
- timestamp, CAP runtime version, runner detected
- list of test files discovered
- per-suite/per-test pass/fail counts
- total duration
- coverage summary (only if coverage mode was on)
- "Scaffold attempts" — which command(s) were tried and what each did
- "Notes" — observations the skill made (e.g. "Service `Books` has no
  tests covering the `submitOrder` action — consider adding one"). The
  skill does NOT write that test on its own unless the user asked.

### `CAP-TEST-FAILURE.md` (only on failure)

Template: `templates/test-failure.md`. Filled with:
- failing tests grouped by file
- each failure's name, location (file:line if available), assertion
  message, stack excerpt (≤ 15 lines)
- the exact command that was run + exit code
- a "Probable cause" line — drawn from `cds test` output, NOT
  invented; if the cause is not visible in output, write `Unknown`
- a "Reproduce" code block with the exact command
- a "What this skill will NOT do" footer reminding the user that
  fixing production code is out of scope

Both files are **overwritten** on each run. No timestamped variants.

---

## Workflow

```
[1] Parse user intent → Mode A | B | C; capture target if given
[2] Project guard → CAP Node.js? → abort if not
[3] (Mode A) Scaffold:
      [3a] Try `npx cds add test` with optional --filter/--out
      [3b] If unavailable or insufficient → write from templates/
           into the project's test folder; never overwrite existing files
[4] Run:
      [4a] Default → `npx cds test` (with -l/-s/-q if requested)
      [4b] Project-specific runner if detected via package.json
      [4c] Coverage → wrap with `npx c8 ...` (only if explicit)
[5] Collect: stdout, stderr, exit code, durations
[6] Write CAP-TEST-REPORT.md (always)
[7] On failure → also write CAP-TEST-FAILURE.md
[8] Echo summary to user; never paste full report
```

---

## Hard rules

1. **No source edits.** Writes/edits are confined to the project's test
   folder and the two report files at the project root. Anything else
   is a protocol violation.
2. **No git mutations.** Read-only git commands are allowed. Anything
   that changes the working tree, index, or refs is forbidden.
3. **No unsolicited installs.** Surface and wait.
4. **No coverage by default.** Opt-in only.
5. **Always try the toolchain first.** `cds add test` before
   hand-written templates.
6. **Idempotent scaffolding.** Do not overwrite existing test files.
7. **Always emit a report**, even on a clean pass. The user can then
   diff it across runs.
8. **Refuse out-of-scope projects.**
9. **No business logic.** If a test would only pass after a code fix,
   leave the test failing, write `CAP-TEST-FAILURE.md`, and explicitly
   refuse to touch `srv/`/`db/`/`app/`.

---

## Failure modes you must surface verbatim

- Not CAP Node.js → `"Not a SAP CAP Node.js project (<signal>). Aborting."`
- Java-only CAP → `"This skill only operates on CAP Node.js. Detected Java CAP project. Aborting."`
- Coverage requested but `c8` missing → see [Coverage mode](#coverage-mode); do not auto-install
- `cds test` not found → `"`npx cds test` failed to start (<error>). Make sure @sap/cds-dk is installed. Aborting."`
- No test files discovered and Mode B (run-only) → `"No tests discovered. Run in scaffold mode or pass a path."`
- Write outside test/ requested → `"Out-of-scope write to <path> refused. This skill only edits the test folder."`

---

## What gets echoed to the user at the end

Echo only this. Reports live on disk.

```
## CAP test — summary

| Metric | Value |
|---|---|
| Mode | <A scaffold+run | B run-only | C coverage> |
| Runner | <node:test | vitest | mocha | jest> |
| Files | <n> |
| Tests | <pass>/<total> |
| Duration | <ms> |
| Exit code | <0 | non-zero> |
| Coverage | <on | off> |

Report: ./CAP-TEST-REPORT.md
<if failure>Failure report: ./CAP-TEST-FAILURE.md</if>
```
