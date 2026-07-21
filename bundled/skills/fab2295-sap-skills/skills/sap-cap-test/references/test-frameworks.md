# Test framework selection

> Reference for picking the right runner for a given CAP Node.js project.
> Anchored to <https://cap.cloud.sap/docs/node.js/cds-test#runs-with-mocha-jest-other>.

`cds test` runs under Node's built-in test runner (`node:test`). The
same test files written against `cds.test()` HTTP helpers also work
under Vitest, Mocha and (with caveats) Jest.

## Detection order

The skill picks the runner by inspecting `package.json#devDependencies`:

1. `vitest` present → **Vitest**
2. `mocha` present  → **Mocha**
3. `jest` present   → **Jest** (with a warning, see below)
4. otherwise        → **`cds test`** (Node built-in)

If the project has an `npm test` script, the skill prefers it over
the raw runner binary — unless the user passed flags that require
a direct invocation (`-l`, `-s`, `-q` on `cds test`, for instance).

## Commands

| Runner | Run command | List command |
|---|---|---|
| `cds test` / Node built-in | `npx cds test` | `npx cds test -l` |
| Vitest | `npx vitest run` | `npx vitest list` |
| Mocha  | `npx mocha "test/**/*.test.js"` | (no built-in) |
| Jest   | `npx jest` | `npx jest --listTests` |

## Jest caveat

`cds.test()` exposes Chai's `expect`. **Chai 5+ is ESM**, which does
not play well with Jest's CommonJS-first transform pipeline. Symptoms:

- `SyntaxError: Cannot use import statement outside a module`
- `expect.to.deep.equal is not a function`

Workarounds the skill may suggest (but not apply unsolicited):

- Migrate to Vitest (CAP docs explicitly recommend Vitest).
- Use Jest's native `expect` instead of `cds.test()`'s Chai `expect`.
- Configure Jest with `--experimental-vm-modules` + ESM-compatible
  Chai imports.

The skill writes the warning into the test report's "Notes" section
when it detects Jest.

## Why Vitest is recommended

- Native ESM support → Chai 5 just works
- Drop-in `expect`, `describe`, `it` globals
- Faster than Mocha+Chai for the same test set
- Built-in coverage via `--coverage` (uses `c8` under the hood)

When the project already uses Vitest, coverage mode invokes
`vitest run --coverage` instead of wrapping with `c8` directly.

## Mocha note

Older CAP samples use Mocha. The skill detects Mocha but does NOT
migrate the project to anything else. Migration is a source-code
change, which the skill refuses.
