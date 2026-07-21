# Coverage with `c8`

> The CAP testing docs at <https://cap.cloud.sap/docs/node.js/cds-test>
> do not prescribe a coverage tool. `c8` is the de-facto coverage tool
> for Node-based test runners because it uses V8's built-in coverage
> data — no source transformation, no Babel plugin.

## When to use

**Only when the user explicitly asks for coverage.** Triggers:

- Portuguese: "cobertura", "coverage", "cobertura c8"
- English: "coverage", "c8", "code coverage"

The default invocation is plain `cds test`. The skill never enables
coverage on its own — it costs more (HTML/lcov files, slower run) and
the user may not want the artifacts.

## Dependency check

`c8` must be installed as a devDependency:

```sh
npm i -D c8
```

The skill does NOT install it on its own. If missing, it surfaces:

```
Coverage requested but `c8` is not installed.
Suggested:
  npm i -D c8
The skill does not run installs unsolicited. Re-invoke after installing.
```

## Invocation

Default coverage run:

```sh
npx c8 --reporter=text --reporter=lcov --reporter=html cds test
```

- `text` — prints a coverage table to stdout (used to fill the report)
- `lcov` — produces `coverage/lcov.info` (CI uploads)
- `html` — produces `coverage/index.html` (local browsing)

Optional flags forwarded from the user:
- `--lines <n>` / `--functions <n>` / `--branches <n>` / `--statements <n>`
  — coverage thresholds. Non-zero exit if not met.
- `--exclude '<glob>'` — skip files (e.g. `--exclude 'test/**'`).
- `--include '<glob>'` — include only (e.g. `--include 'srv/**'`).

Sensible defaults if the user doesn't specify:

```sh
npx c8 \
  --reporter=text --reporter=lcov --reporter=html \
  --include 'srv/**' --include 'db/**' \
  --exclude 'test/**' --exclude 'gen/**' --exclude 'node_modules/**' \
  cds test
```

## Reading the result

`c8`'s text reporter prints a table:

```
-------------------|---------|----------|---------|---------|
File               | % Stmts | % Branch | % Funcs | % Lines |
-------------------|---------|----------|---------|---------|
All files          |   84.21 |    72.50 |   88.46 |   84.21 |
 srv/catalog.js    |   91.30 |    83.33 |  100.00 |   91.30 |
 srv/orders.js     |   76.92 |    60.00 |   75.00 |   76.92 |
-------------------|---------|----------|---------|---------|
```

The skill extracts the `All files` row and writes it to the `Coverage`
section of `CAP-TEST-REPORT.md`. The full HTML report path
(`./coverage/index.html`) is referenced — never inlined.

## What the skill must NOT do

- Run `c8` without an explicit user request.
- Auto-install `c8`.
- Edit `package.json` to add a `coverage` script. (That is a source
  edit; the skill is read-only outside the test folder.)
- Configure `.c8rc.json` on the user's behalf.
- Commit the `coverage/` directory.

If the user wants a permanent `coverage` script in `package.json`, the
skill surfaces the suggested JSON snippet and asks the user to add it.
