# `cds add test`

> Local mirror of the `cds add test` facet from `@sap/cds-dk`.
> Source: <https://cap.cloud.sap/docs/tools/cds-cli> (feature matrix lists
> `test` for both Node.js and Java) and the `cds add --help` output of a
> recent `@sap/cds-dk`.

## Purpose

`cds add test` scaffolds the project's test layout: a `test/` directory
(by default) with one starter test file per service/entity that the
generator decides to cover, plus any needed devDependencies declared in
`package.json`.

**Always run this first.** It is the toolchain's idiomatic test layout,
and it stays in sync with the project's CAP version.

## Invocation

```sh
npx cds add test
```

With options:

```sh
npx cds add test --out test --filter '^.*Service$'
```

## Options

| Flag | Meaning |
|---|---|
| `-o <dir>` / `--out <dir>` | Custom output directory. Default on Node.js is `test`. |
| `-f <pattern>` / `--filter <pattern>` | Restrict scaffolding to services/entities matching the pattern. Treated as a regex if it contains meta-characters like `^` or `*`, otherwise as a substring include. |

## Availability

`cds add test` is provided by `@sap/cds-dk`. The exact version that
introduced it is not pinned in the official docs, but if the user's
`@sap/cds-dk` is older than ~7.x, the command may not exist.

The skill handles this gracefully: if `cds add test` is unavailable or
exits non-zero, it falls back to writing from local `templates/`. The
fallback is recorded in `CAP-TEST-REPORT.md` under "Scaffold attempts".

## Detecting availability

```sh
npx cds add --help 2>&1 | grep -F 'test'
```

If the output contains a `test` facet line, the command is available.

## What the skill is allowed to forward

Only `--out` and `--filter`. Other flags surfaced by future versions
must be passed unchanged from the user's invocation, but the skill
does not guess them.

## What the skill must NOT do

- Pass arbitrary flags it did not see in the user message.
- Use `--force` (or any equivalent) to overwrite existing test files.
- Run `npm install` if `cds add test` declares a new devDependency —
  it surfaces the requirement and waits for the user.
