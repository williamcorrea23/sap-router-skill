# `cds test` CLI

> Local mirror of the relevant sections of <https://cap.cloud.sap/docs/node.js/cds-test>.
> Source of truth: the URL above. This file exists so the skill can cite an
> anchor for every behavior.

`cds test` is a thin wrapper that delegates to Node's built-in test runner.

## Options

| Flag | Meaning |
|---|---|
| `-?` / `--help` | Print usage |
| `-l` / `--list` | List discovered test files. Does NOT execute. |
| `-s` / `--silent` | Suppress test output that goes through `console.log` |
| `-q` / `--quiet` | Suppress *all* output to stdout |

Examples:

```sh
cds test            # discover + run
cds test -l         # only list discovered files
cds test -s         # quiet console.log output from tests
```

## Discovery

The runner discovers files inside the project's test directory. Common
locations:

- `test/` — default produced by `cds add test --out` (the default of `-o`
  on Node.js is `test`)
- `tests/`
- `__tests__/`

Test file naming follows the underlying runner (Node's `node:test`):
`*.test.js`, `*.test.mjs`, `*.test.ts`, or `test-*.js`.

## Runner compatibility

`cds test` works with the Node built-in runner out of the box. The same
test files written against `cds.test()` (see `cds-test-api.md`) also run
under:

```sh
node --test
npx vitest --silent
npx jest --silent       # caveats — see test-frameworks.md
npx mocha --parallel
```

## Skill usage

The skill always prefers `npx cds test` for the default run. If the
project has an `npm test` script and the user did not pass runner-
specific flags, the skill MAY use `npm test` instead — this keeps
the project's existing convention.

## Exit codes

- `0` — all tests passed
- non-zero — at least one test failed, or the runner aborted

The skill maps any non-zero exit code to "failure" and emits
`CAP-TEST-FAILURE.md` in addition to `CAP-TEST-REPORT.md`.
