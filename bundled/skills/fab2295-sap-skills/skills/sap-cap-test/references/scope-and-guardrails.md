# Scope and guardrails

> The non-negotiable rules. If the user pushes the skill outside these,
> the skill refuses verbatim.

## Allowed write targets

The skill may CREATE or EDIT files only inside:

```
<project>/test/**
<project>/tests/**
<project>/__tests__/**
<project>/CAP-TEST-REPORT.md       (project root, overwrite)
<project>/CAP-TEST-FAILURE.md      (project root, overwrite, only on failure)
```

Everything else — including `package.json`, `.cdsrc.json`,
`xs-security.json`, `mta.yaml`, `manifest.yaml`, anything under
`srv/`, `db/`, `app/`, build outputs, and `node_modules/` — is
**out of scope** for writes.

If `cds add test` adds a devDependency to `package.json` on its own,
that is the toolchain doing it, not the skill. The skill must NOT
hand-edit `package.json` to add deps.

## Allowed commands

Read-only (always allowed):

```sh
git status
git diff
git diff --name-only
git log
git show
git rev-parse
git ls-files
git branch --show-current
```

Test-related (allowed):

```sh
npx cds add test [--out X] [--filter Y]   # scaffolding
npx cds add --help                         # availability probe
npx cds test [-l|-s|-q]                    # the run
npx vitest run [--coverage]                # alt runner
npx mocha "test/**/*.test.js"              # alt runner
npx jest                                   # alt runner (with warning)
npx c8 ... cds test                        # coverage (opt-in only)
npm test                                   # if defined
```

Forbidden (always):

```sh
git add ...                  git commit ...               git push ...
git pull ...                 git merge ...                git rebase ...
git reset ...                git checkout <file>          git restore ...
git stash ...                git tag ...                  git branch -D
git remote add/remove/...    git fetch -p                 git clean ...
npm install / npm i (any)    yarn add / pnpm add          npm uninstall
sed -i ...                   rm -rf <anything>            mv / cp of source
```

If a forbidden command is needed to complete the user's request,
the skill MUST stop, explain why, and surface the command for the
user to run manually.

## Allowed reasoning, forbidden actions

The skill CAN say:
- "Service `Books` has no test for the `submitOrder` action."
- "There appears to be a bug in `srv/orders.js:42` — uncaught
  rejection on missing `book`."
- "Coverage for `srv/orders.js` is 22%; consider adding tests for
  the `submit` and `cancel` actions."

The skill MUST NOT:
- Open `srv/orders.js` to fix the bug.
- Add a missing `@assert.notNull` to `db/schema.cds`.
- Add a `coverage` script to `package.json`.
- Run `npm install c8` (or anything else).
- Commit anything.

## Refusal phrases

Use these exact strings when the user asks for an out-of-scope action:

- Asked to fix code: `"Fixing production code is out of scope for sap-cap-test. The skill only writes tests."`
- Asked to commit: `"sap-cap-test does not run git mutations. Please commit manually after reviewing the changes."`
- Asked to install: `"sap-cap-test does not install dependencies. Suggested: `<exact command>`."`
- Asked to scaffold a service: `"Scaffolding production code is out of scope. Use `cds add <facet>` directly."`

## The two-line summary the skill must print at the start of every run

```
sap-cap-test: tests only — no code edits, no commits, no installs.
Run mode: <A|B|C>   Coverage: <on|off>   Runner: <detected>
```

This makes the contract visible to the user at the top of every run.
