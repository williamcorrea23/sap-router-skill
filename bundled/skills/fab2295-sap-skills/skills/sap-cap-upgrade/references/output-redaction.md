# Output Redaction Rules (mandatory for every captured string)

> **Why this exists.** This skill captures stderr from `npm install`,
> stdout/stderr from `cds build`, response bodies from osv.dev and the
> npm advisory bulk endpoint, and the auth token from the user's
> `.npmrc`. Any of those can carry credentials. If the captured string
> reaches `notes[]` (or any other JSON field) un-redacted, the
> credential leaks the moment the JSON is pasted into a chat, posted
> to a PR, or shipped to CI logs.
>
> **Contract.** Every string the skill puts into its JSON output —
> `notes[]`, `discarded[].error_excerpt`, and any other free-form
> field — MUST pass through the redaction filter below first. The
> filter is fail-closed: when in doubt, redact.

---

## Trigger A — Auth-header / token-shaped patterns (redact value)

Match against any captured line. Case-insensitive.

| Pattern | What it likely is | Replacement |
|---|---|---|
| `Authorization:\s*Bearer\s+[A-Za-z0-9._\-]{8,}` | Bearer header (curl trace, 401 echo) | `Authorization: Bearer [REDACTED:bearer]` |
| `Authorization:\s*Basic\s+[A-Za-z0-9+/=]{12,}` | Basic auth header | `Authorization: Basic [REDACTED:basic]` |
| `Authorization:\s*[A-Za-z]+\s+[A-Za-z0-9._\-+/=]{8,}` | Any other auth scheme | `Authorization: <scheme> [REDACTED:auth-token]` |
| `//[^/\s]+/:_authToken\s*=\s*\S+` | `.npmrc` token line (registry-scoped) | `//<registry>/:_authToken=[REDACTED:npm-token]` |
| `_auth\s*=\s*\S+` | legacy `.npmrc` _auth | `_auth=[REDACTED:npm-legacy-auth]` |
| `_password\s*=\s*\S+` | `.npmrc` legacy password | `_password=[REDACTED:npm-legacy-password]` |
| `npm-auth-token[=:]\s*\S+` | env var dump | `npm-auth-token=[REDACTED:npm-token]` |
| `NPM_TOKEN\s*[=:]\s*\S+` | env var dump | `NPM_TOKEN=[REDACTED:npm-token]` |
| `GITHUB_TOKEN\s*[=:]\s*\S+` | env var dump | `GITHUB_TOKEN=[REDACTED:gh-token]` |
| `eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}` | JWT | `[REDACTED:jwt]` |
| `ghp_[A-Za-z0-9]{36,}` / `gho_…` / `ghs_…` / `ghu_…` | GitHub token | `[REDACTED:gh-token]` |
| `AKIA[0-9A-Z]{16}` | AWS access key ID | `[REDACTED:aws-akid]` |
| `[a-z]+://[^:@\s]+:[^@\s]+@[^\s]+` | URL with embedded `user:password@` | `<scheme>://[REDACTED:url-creds]@<host>` (keep host visible for triage) |

The hex / base64 broad-shape rules from the code-review skill's
`secret-redaction.md` are NOT applied here, because legitimate npm
package hashes (sha512 integrity strings) and tarball checksums
trip them constantly. The narrower auth-shape rules above are
sufficient for the strings this skill captures.

---

## Trigger B — Multi-line command echo

When the captured stderr contains the literal text of the curl
command that was run (Some shells / tracers echo `+ curl ... -H
"Authorization: Bearer xxx"` on failure), redact the whole line
matching `^[\+\$]\s+curl\s+` if any `-H 'Authorization:` or
`-H "Authorization:` is present on that line:

```
+ curl ... -H "Authorization: Bearer [REDACTED:bearer]" ...
```

Do NOT drop the whole line — keep the URL for triage. Only mask
the Authorization value.

---

## Trigger C — Whole-string drop (fallback)

If, after Triggers A and B, the resulting string still contains
any **20+ char run of [A-Za-z0-9._\-+/=]** immediately adjacent to
one of these keywords (case-insensitive), drop the whole line and
replace it with the comment placeholder:

`token | secret | password | credential | apikey | api_key | privatekey | private_key`

```
<!-- line redacted by skill: unclassified token-like content near credential keyword -->
```

---

## Filter algorithm (deterministic)

For each candidate string that is about to be assigned to `notes[i]`,
`discarded[i].error_excerpt`, or any other free-form JSON field:

1. **Run Trigger A** in regex order. Each match is replaced in place.
2. **Run Trigger B**. Each curl-trace line with an Authorization header
   is rewritten.
3. **Run Trigger C**. Each remaining line that still contains a
   token-shaped run adjacent to a credential keyword is dropped.
4. **Length cap.** Truncate to 4 KB AFTER redaction. The truncation
   pointer goes at the end: `... [truncated by skill at 4096 bytes]`.
5. **Emit.**

The filter MUST run **before** truncation. Truncation before
redaction is a bug — the secret could be in the first 4 KB and the
truncation would have left it intact.

---

## Special: npm auth token must never appear in any captured output

When the skill uses the npm advisory bulk endpoint (fallback in
`vulnerability-check.md`), it MUST:

1. Read the token into a process env variable, NOT into the command
   line. Use the form:

   ```sh
   NPM_AUTH_TOKEN=$(npm config get //registry.npmjs.org/:_authToken 2>/dev/null) \
   curl -sS --max-time 10 -X POST 'https://registry.npmjs.org/-/npm/v1/security/advisories/bulk' \
     -H 'Content-Type: application/json' \
     -H "Authorization: Bearer $NPM_AUTH_TOKEN" \
     -d '{"<pkg>":["<target>"]}'
   ```

   Even though the token is still in the rendered Authorization
   header at request time, this form keeps it out of `ps`-visible
   command line in most shells (the env var is set for the curl
   call only, not exported globally).

2. NOT echo the constructed `curl` command anywhere — not to stdout,
   not to a captured trace, not to `notes[]`. The skill records the
   URL, the response status, and the redacted response body. The
   request command stays internal.

3. If the response itself echoes the Authorization header back
   (the bulk endpoint does this in certain 401/403 error shapes),
   Trigger A redacts it before the response body is allowed into
   `notes[]`.

---

## What this is NOT

- It is NOT a complete DLP scanner. It only protects what the skill
  emits in its JSON output. It does not, and cannot, redact the
  contents of `package.json` (which the skill never quotes in
  `notes[]` anyway — only the names and versions of bumped packages
  go into `bumped[]`).
- It does NOT prevent the user's CI logs from showing the token if
  the user runs `npm install` themselves with `set -x` or
  `NPM_CONFIG_LOGLEVEL=verbose`. That is outside the skill's
  control.
- It does NOT rotate or revoke secrets it detects. Detection is the
  contract.

---

## Why narrow auth-shape over broad hex/base64

The code-review skill's `secret-redaction.md` is broad on purpose
because file-excerpt context is mostly human-readable code. This
skill's captured strings are mostly machine output from npm and
curl — full of legitimate sha256/sha512 hashes, tarball checksums,
integrity strings, and other hex/base64 blobs that are not secrets.
A broad filter here would either leave most error messages unreadable
or drop so many lines that the resulting `notes[0]` would be useless
for debugging the actual upgrade failure.

The auth-header / token-keyword approach narrows the filter to the
patterns that actually leak credentials in npm/curl output.
