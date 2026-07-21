# Bug Attribution Rules (strict)

The `sap-cap-upgrade` skill is forbidden from reporting any failure as version-caused unless **all three** criteria below hold simultaneously. When in doubt, **discard**. False negatives are acceptable; false positives are not.

The whole point of these rules is to make `version_caused_bugs[]` a list the operator (or any downstream consumer of the JSON) can trust without re-checking — and to keep the boundary "is this from the bump?" anchored in the official changelogs, not in the model's intuition.

---

## Criterion A — Baseline diff

The failure must appear in `post.failures[]` AND must NOT appear in `baseline.failures[]`.

Equality is by error signature: `(command, first 200 chars of stderr stripped of timestamps and absolute paths normalized to repo-relative)`. Anything that already failed before the bump is forever non-attributable.

## Criterion B — Regex hit in an official changelog entry

The captured error string (stderr or build output) must match a regex extracted from an entry in:
- `references/changelogs/cap/changelog-<YYYY>.md` (sections **Changed / Removed / Fixed / Breaking Changes / Migration**), for packages routed to CAP, OR
- `references/changelogs/cloud-sdk-js/changelog-v<N>.md` (section **Compatibility Notes**), for `@sap-cloud-sdk/*`.

The regex MUST be lifted from a concrete sentence in the changelog (e.g. an inline code reference, a "renamed X to Y" phrase, a removed API name). The skill does **not** invent regexes from common error patterns.

If a candidate failure produces a regex hit only against a section that is NOT in the lists above (e.g. matches against an "Added" or "Improvements" entry), it is **not** a breaking change and goes to `discarded[]` with `reason: "matched non-breaking section"`.

## Criterion C — Version crossing

The bumped package's `from→to` interval must include the version of the changelog entry that produced the regex hit.

Examples:
- `@sap/cds: 9.9.1 → 9.12.0` covers entries first published in 9.10.x, 9.11.x, 9.12.x ✓
- `@sap/cds: 9.9.1 → 9.10.0` does NOT cover an entry first published in 9.11.0 ✗
- `@sap-cloud-sdk/http-client: 3.18.0 → 4.0.0` crosses the v3→v4 boundary, so entries in `changelog-v4.md` "Compatibility Notes" apply ✓

If the entry's version cannot be determined from the changelog mirror (e.g. the section heading is malformed or version-less), discard with `reason: "version not extractable from rule"`.

---

## Mandatory blacklist — never reportable

The following are **always** discarded, regardless of A/B/C:

1. ESLint / Prettier / TSC / type-check warnings or errors **in user code** (anything under `app/`, `srv/`, `db/`, `test/`, etc., not produced by `cds build` itself).
2. Peer-dependency warnings emitted by `npm install`, even when about an in-scope package — these are advisories, not failures.
3. Network / registry errors (`ECONNRESET`, `ETIMEDOUT`, `E404` on registry, proxy errors).
4. SQLite / HANA / Postgres native binding rebuild failures (Node ABI mismatch). Reason logged: `native rebuild — out of scope`.
5. Permission errors (`EACCES`, `EPERM`).
6. Out-of-disk / OS-level errors (`ENOSPC`, `EMFILE`).
7. Failures from `npm test` whose stack trace points exclusively to user-authored test files when no in-scope package symbol appears in the trace.
8. Deprecation warnings printed to stderr (lines starting with `(node:NNNN) DeprecationWarning:` or `[DEP\d+]`) — listed in `notes` only, never as bugs.

---

## Tie-breaking & multi-source

If a single failure could be attributed to two changelog entries (e.g. one in CAP, one in Cloud SDK JS), pick the one whose package name appears in the captured error text. If neither package name appears explicitly, discard with `reason: "ambiguous source"`.

If two in-scope packages were bumped in the same run and both have a candidate matching entry, the bug is duplicated — once per `(rule_id, package)` pair — so the operator sees both refs in the report.

---

## Output discipline

`version_caused_bugs[]` must contain ONLY items that survived A ∧ B ∧ C and did not hit the blacklist. The skill returns the count of discarded entries (`discarded[].length`) so the user can audit, but never elevates a discarded entry to "maybe a bug".

When the discard list is large (≥ 5 entries) and `version_caused_bugs[]` is empty, append a `notes` entry: `"high discard count — consider running scripts/refresh-references.js to refresh changelogs"`.
