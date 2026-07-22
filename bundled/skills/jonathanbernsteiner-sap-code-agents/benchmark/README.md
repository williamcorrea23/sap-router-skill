# /benchmark

The acceptance benchmark: a fixed set of questions run through the real
agent loop and machine-checked, so agent behaviour is a pass/fail gate rather
than an impression.

## Contents

- `questions.json` — the question set. Each entry has an `id`, the `workspace`
  it runs against (`abapGit` or `example-manufacturer`), the `question` text,
  and an `expected_behavior` block:
  - `must_use_tools` — tools that must appear in the tool calls the agent made
  - `answer_matches` — regexes that must all match the final answer
    (case-insensitive)
  - `answer_not_matches` — regexes that must not match

The nine questions (`a*` on abapGit, `b*` on example-manufacturer) cover
per-object documentation, where-used lookups, table-access evidence, the "no
usage data" state, the simulated-usage labelling, retirement candidates,
S/4HANA table findings with citations, and an object whose target is outside
the codebase (`BAPI_GOODSMVT_CREATE`) and must not be described as if it were
in it.

## Commands

```bash
npm run benchmark          # run every question
```

The runner is `scripts/benchmark.ts`; it calls `lib/agent/loop.ts` against the
live Anthropic API and the configured database, so `ANTHROPIC_API_KEY` and
`DATABASE_URL` must be set in `.env.local`. It accepts an id-prefix argument to
run a subset, e.g. `npx tsx --env-file=.env.local scripts/benchmark.ts b3`.
