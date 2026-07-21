# Secret Redaction Rules (mandatory for every Evidence block)

> **Why this exists.** The skill reads config files that routinely carry
> credentials — `xs-security.json`, `manifest.yaml`, `.cdsrc.json`,
> `mta.yaml`, and JS/TS files that may inline secrets in dev defaults.
> The Evidence section of each finding embeds **verbatim file excerpts**.
> Without redaction, a finding can leak the very secret it is reporting.
>
> **Contract.** Every excerpt the skill emits into `CAP-CODE-REVIEW.md`
> — including the Suggested-fix illustrative snippets — MUST be passed
> through the redaction filter below. The filter is allow-list-by-shape:
> when in doubt, redact.

---

## Trigger A — Key-name match (redact the value)

If a captured line contains a key (in JSON/YAML/JS object form) whose
name matches any pattern below (case-insensitive, with optional
hyphens/underscores), replace the value with the redaction placeholder.

```
client[-_]?secret      | client_secret, clientSecret, client-secret
secret                 | secret, app_secret, SECRET
password               | password, passwd, pwd, db_password
token                  | token, accessToken, refresh_token, api_token, bearer_token, idToken
api[-_]?key            | apiKey, api_key, API-KEY
auth(orization)?       | auth, Authorization (header values)
credentials            | credentials, cred, creds (entire object value, see below)
certificate            | certificate, cert
private[-_]?key        | privateKey, private_key, RSA_PRIVATE_KEY
signing[-_]?key        | signingKey, signing_key
encryption[-_]?key     | encryptionKey
session[-_]?secret     | sessionSecret, session_secret
cookie[-_]?secret      | cookieSecret
master[-_]?key         | masterKey
hmac[-_]?(key|secret)  | hmacKey, hmac_secret
sas[-_]?token          | sasToken (Azure shared access signature)
connection[-_]?string  | connectionString — only when the value contains `://...:.*@`
dsn                    | DSN — only when the value contains `://...:.*@`
```

**Replacement format**: `[REDACTED:<key-kind>]` where `<key-kind>` is the
matched class (`client_secret`, `password`, `token`, etc.).

When the key's value is itself an object (e.g. `"credentials": { ... }`),
**redact the entire object body** with a single line:

```json
"credentials": { /* [REDACTED:credentials-block] */ }
```

---

## Trigger B — Value-shape match (redact regardless of key)

These patterns are redacted even when the surrounding key name is
unknown or innocuous. Match against the captured line:

| Pattern | What it likely is | Placeholder |
|---|---|---|
| `eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}` | JWT | `[REDACTED:jwt]` |
| `Bearer\s+[A-Za-z0-9._\-]{20,}` | OAuth bearer token | `[REDACTED:bearer]` |
| `Basic\s+[A-Za-z0-9+/=]{20,}` | HTTP Basic auth | `[REDACTED:basic-auth]` |
| `AKIA[0-9A-Z]{16}` | AWS access key ID | `[REDACTED:aws-akid]` |
| `ASIA[0-9A-Z]{16}` | AWS temp access key ID | `[REDACTED:aws-akid]` |
| `xox[abprs]-[A-Za-z0-9-]{10,}` | Slack token | `[REDACTED:slack-token]` |
| `gh[opsu]_[A-Za-z0-9]{36,}` | GitHub token | `[REDACTED:gh-token]` |
| `sk-[A-Za-z0-9]{20,}` | OpenAI-style API key | `[REDACTED:openai-key]` |
| `[a-f0-9]{32,}` | Hex string ≥ 32 chars | `[REDACTED:hex]` |
| `[A-Za-z0-9+/]{40,}={0,2}` (long b64) | Base64 secret ≥ 40 chars | `[REDACTED:base64]` |
| `[a-z]+://[^:@\s]+:[^@\s]+@[^\s]+` | URL with embedded `user:password@` | `[REDACTED:url-with-creds]` |
| Line containing `-----BEGIN ([A-Z ]+)?PRIVATE KEY-----` | PEM private key block | drop **every** subsequent line until `-----END ...PRIVATE KEY-----` inclusive and replace the whole block with `[REDACTED:pem-private-key]` |
| Line containing `-----BEGIN CERTIFICATE-----` followed by `-----END CERTIFICATE-----` block | Cert block (less sensitive than private key, but still PII-adjacent) | `[REDACTED:pem-certificate]` |

The hex / base64 shape rules are **deliberately broad**. A real-world
xsappname or service GUID will sometimes trip them — that is acceptable.
False positives in redaction are far cheaper than false negatives.

---

## Trigger C — File-name match (redact the entire excerpt if Trigger A or B hits)

Inside these files, the redaction is **strict**: if any Trigger-A or
Trigger-B match occurs anywhere in the captured excerpt, the entire
excerpt is replaced with a structural placeholder:

```
[REDACTED:excerpt from <filename> contained a potential secret —
 finding rendered without verbatim content]
```

Files in this strict category:

- `xs-security.json`
- `manifest.yaml`, `manifest.yml`
- `mta.yaml`, `mta.yml`
- `default-services.json`
- `default-env.json`
- `services-manifest.json`
- Anything under `secrets/`, `.secrets/`, `.env*`

The rationale: these files are credential-shaped end-to-end. A snippet
that "looks fine" three lines down may be one line away from a secret
the reader can extrapolate.

---

## Trigger D — SEC-007 (secrets inlined in source)

When the finding being emitted IS the SEC-007 "secrets inlined in
source" rule, the Evidence block MUST NOT include the secret value
under any circumstance — not even partially. The Evidence block for
SEC-007 uses this fixed format:

```
<key-or-variable-name>: [REDACTED:found-secret]
```

A SEC-007 finding's purpose is to point the human at the file:line so
they can fix it. The skill must NOT make the secret easier to harvest
from the report than from the original file.

---

## Filter algorithm (deterministic)

For each candidate Evidence excerpt:

1. **File-class check.** If the source file matches Trigger-C's strict
   category, scan the excerpt for any Trigger-A or Trigger-B hit. If
   any hit, replace the entire excerpt with the structural placeholder
   in Trigger C. Done.
2. **PEM block check.** If the excerpt overlaps a `-----BEGIN ... -----END`
   block, replace the whole block (including any in-block lines that
   the excerpt would have included) with `[REDACTED:pem-...]`.
3. **Line-by-line redaction.** For every line still in the excerpt:
   - Apply Trigger A: if the line is `<key>: <value>` or `"<key>": "<value>"`
     or `const <key> = <value>`, and `<key>` matches the key-name regex,
     replace `<value>` with the matching placeholder.
   - Apply Trigger B: for every value-shape regex, replace the match
     with the matching placeholder.
4. **Fail-closed.** If any line still contains a token that "looks
   secret" but the algorithm couldn't classify it (e.g. a 30-char
   alphanumeric blob next to no recognizable key), drop that single
   line and replace it with:

   ```
   <!-- line N redacted by skill: unclassified potential secret -->
   ```

5. **Emit the redacted excerpt.**

The skill MUST NOT emit a finding whose Evidence ends up empty after
redaction. In that case, render the finding without an Evidence code
block — instead, write one prose sentence: *"Evidence omitted: file
excerpt contained content that could not be safely redacted (see
<path>:<line> for the original)."*

---

## What this is NOT

- It is NOT a general DLP scanner. It only redacts what the skill is
  about to write into `CAP-CODE-REVIEW.md`. The original files on disk
  are untouched (the skill is read-only on source).
- It is NOT a substitute for the user removing the secret from the
  repo and rotating it. The skill reports the finding (SEC-007) so the
  human can act.
- It does NOT decrypt or transform secrets. Redaction is one-way and
  irreversible from the report's perspective.

---

## Why broad over precise

False positives in redaction (legitimate hex IDs masked unnecessarily)
make the report slightly less readable. False negatives (a real secret
left in the report) defeat the whole purpose of the audit and can be
disclosed to anyone with read access to `CAP-CODE-REVIEW.md`. The
report is often committed, pasted into chat, or shared with auditors —
treat every Evidence excerpt as if it will be posted publicly.
