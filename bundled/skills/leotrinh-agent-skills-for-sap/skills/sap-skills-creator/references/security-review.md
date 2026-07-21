# Security Review

Load this file during the Security Review phase and again for any Audit
run. Walk each category top to bottom. Do not skip categories.

Findings use the severity ladder:

- **Critical** — blocks release. The skill cannot ship.
- **High** — must be fixed before public release; internal use requires
  explicit acceptance.
- **Medium** — fix in this iteration when possible.
- **Low** — improvement backlog.
- **Informational** — noted for future maintainers.

## 1. Credentials and Secrets

### Reject

- Hardcoded passwords, PINs, or master keys.
- OAuth tokens (`Bearer`, `refresh_token`, `access_token`) in code, docs,
  templates, or logs.
- Session cookies (`SAP_SESSIONID`, `MYSAPSSO2`, `sap-appcontext`, etc.)
  embedded anywhere.
- Private keys or certificate material in any format.
- Real destination credentials from a customer or partner system.
- Real customer hostnames or SIDs in examples.
- `.env` files that contain values.
- Secrets embedded in binaries.
- Secrets in test fixtures.

### Require

- Environment variables or secret managers as the source of truth.
- Destination-based resolution when the target platform supports it.
- Redacted logs. Errors must never echo secret values.
- Placeholder-only examples (`<password>`, `<token>`, `<user>`,
  `<sid>`).
- Explicit "missing secret" errors that name the exact configuration
  step, without printing the value that would have been used.

### Never

- Instruct the user to paste a secret into an AI conversation.
- Instruct the agent to store a secret in memory across turns.
- Instruct the agent to write a secret to a file the user did not choose.

## 2. Network Behaviour

### Document

- External hosts contacted, including registries and update services.
- Protocols and TLS behaviour (verification enabled by default).
- Authentication mechanism per host.
- Timeouts and retry behaviour.
- Proxy behaviour and CA bundle handling.
- Offline capability when the network is unavailable.

### Reject

- TLS verification disabled by default.
- Automatic insecure fallback when TLS verification fails.
- Hidden telemetry or usage reporting.
- Undocumented network calls from scripts.
- Infinite retry loops on transient failures.
- Broad exception swallowing that masks connection errors.

### Require

- Explicit flags or environment variables for insecure behaviour.
- User-visible warnings whenever an insecure mode is active.
- Clear error messages when the CA bundle or proxy is misconfigured.

## 3. Filesystem Behaviour

### Review

- Which files the skill reads.
- Which files it writes or overwrites.
- Temporary files: names, locations, cleanup.
- Permission changes (chmod, ACL modifications).
- Path handling — reject relative traversal patterns (`..`).
- Absolute developer paths (`C:\\Users\\...`, `/home/<user>/`) in
  documentation and code.
- User-home assumptions that break on other operating systems.
- Overwrite policy — must be explicit, never silent.
- Deletion — must require confirmation.

### Require

- Explicit user confirmation for overwrites or destructive actions.
- Documented cleanup behaviour for temporary files.
- No writes outside the target project directory unless the user opted
  in.

## 4. Shell and Subprocess Behaviour

### Review

- Command injection risks in generated commands.
- Unsafe string interpolation into shell strings.
- Use of `shell=True` (Python), `bash -c` interpolation, or PowerShell
  `Invoke-Expression` with untrusted input.
- Unquoted paths, especially those that may contain spaces.
- Command lines that carry secrets in argv (visible in process
  listings).
- Platform assumptions (Windows vs Linux vs macOS).
- Exit-code handling — non-zero must not be silently ignored.
- Timeout handling for long-running subprocesses.

### Prefer

- Argument arrays over shell strings.
- Explicit quoting utilities (`shlex`, `--%` in PowerShell for
  stop-parsing tokens when required).
- Reading secrets from environment variables or files, not from argv.

## 5. SAP-Specific Operational Risks

Classify each operation the skill can trigger:

| Class | Examples | Required control |
|-------|----------|------------------|
| **Read-only informational** | GET metadata, list objects | None beyond authentication. |
| **Read-only operational** | Discovery, search, dry-run | Report exact endpoint used. |
| **Write-capable** | Source writes, object creation | Confirm target, transport, and human authorization. |
| **Destructive** | Deletion, transport release, unlock | Explicit contemporaneous authorization; no retry. |
| **Credential-sensitive** | Any operation resolving secrets | Redacted logs, no secret echo. |
| **Production-impacting** | Any operation against a production tenant | Explicit environment confirmation. |

### Required control sequence for destructive SAP operations

```text
Inspect
→ Confirm target (object, package, transport, system)
→ Preview planned operation
→ Obtain explicit authorization for the specific operation
→ Execute once
→ Verify response
→ Report exact outcome
```

Do not infer authorization from a broad request such as "clean up the
deployment", "finish the transport", or "fix everything".

## 6. Dependency and Supply-Chain Review

### Review

- Third-party packages introduced by the skill.
- Version constraints and pin strategy.
- Package provenance (official registry, vendored source).
- Install scripts that run during dependency installation.
- Binaries checked into the repository.
- Generated files that could hide unreviewed code.
- Downloaded artefacts fetched at runtime.
- GitHub Actions or other CI plugins the skill relies on.
- External skill dependencies (skills that require another skill to
  work).

### Prefer

- Python standard library over new dependencies.
- Small, well-known libraries when a dependency is truly needed.
- Explicit version pins.
- No install-time network calls beyond dependency resolution.

## 7. Public-Release Review

Before a skill goes public:

- Confirm license compatibility across every included file, including
  images and templates.
- Add a trademark disclaimer stating the project is not affiliated with
  SAP SE.
- Run the validator's security scan and re-scan for real hostnames.
- Remove customer data and sanitised examples that could still be
  identifiable.
- Review any embedded code for proprietary customer origins.
- Explain or remove any binary artefact.
- Provide clear security-reporting instructions (link to `SECURITY.md`).
- Ensure the human-readable `README.md` is complete and correct.

## Findings Log Template

Record findings in the review report template
(see [`../assets/skill-review-report-template.md`](../assets/skill-review-report-template.md)).
Each row should contain:

```text
Rule / Category
Severity
Location (file, optionally line)
Short description
Recommended fix
Status (open, fixed, accepted with reason)
```

Redact secret-looking values. Never quote a suspected secret verbatim in
the report; use the first few characters plus `...` and note the type.
