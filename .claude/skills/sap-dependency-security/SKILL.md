---
name: sap-dependency-security
description: >
  SAP dependency security — MCP executable trust verification, supply-chain safeguards,
  cooldown policies for sensitive operations, lockfile hardening, npm/pip dependency audit,
  SAP security note tracking. Use when auditing project dependencies, verifying MCP server
  executables, or implementing supply-chain security policies for SAP tools.
trigger:
  keywords:
    - dependency security SAP
    - MCP executable trust
    - npm audit SAP
    - pip audit
    - supply chain security
    - SAP security notes
    - lockfile hardening
  intent: User needs to audit, verify, or harden dependencies and executables in an SAP development environment.
---

# SAP Dependency Security

Supply-chain security for SAP development tooling and MCP servers.

## Prerequisites

- `npm` and/or `pip` available in the project environment
- `sha256sum` utility (standard on Linux/macOS)
- Access to SAP support portal for security notes (S-user)
- Project under version control (Git)

## 1. Verify MCP Executable Signatures

```bash
# Generate checksum of the downloaded MCP executable
sha256sum aibap-mcp > checksum.txt

# Compare against the published checksum from the repo releases page
# If they differ → do NOT run the executable
diff <(echo "<published-sha256>  aibap-mcp") checksum.txt

# First run in sandbox — read-only, no network writes
./aibap-mcp --dry-run --read-only 2>&1 | tee first-run.log

# Review: does it connect to unexpected hosts? Does it write files?
grep -iE 'http|write|create|socket' first-run.log
```

## 2. Configure Cooldown Policies for Sensitive Operations

| Operation             | Cooldown     | Reason                        |
|-----------------------|--------------|-------------------------------|
| SAPWrite              | 5 seconds    | Prevent bulk code changes     |
| Transport release     | 30 minutes   | Production safety             |
| SAP system delete     | 24 hours     | Irreversible                  |
| User creation         | 1 hour       | IAM audit trail               |
| BAPI_POST_DOCUMENT    | 10 seconds   | Financial posting safety      |

Configure in your MCP server settings or Hermes agent config file.

## 3. Run npm Dependency Audit

```bash
# Full audit report
npm audit

# Auto-fix what is safely fixable
npm audit fix

# Fail build on HIGH or CRITICAL only
npm audit --audit-level=high
```

## 4. Run pip Dependency Audit

```bash
pip install pip-audit
pip-audit

# Audit a specific requirements file
pip-audit -r requirements.txt
```

## 5. Check SAP Security Notes

```bash
# Query SAP security notes API for relevant components
curl "https://api.sap.com/v1/security/notes?search=nodejs"

# For ABAP components, search SAP support portal:
# https://launchpad.support.sap.com/#/notes
# Filter: Priority = "Correction with high priority", Category = "Security"
```

## 6. Harden Lockfiles

```bash
# npm: install exact versions from lockfile (no mutations)
npm ci

# pip: enforce hash checking (add hashes to requirements.txt)
pip install -r requirements.txt --require-hashes

# Generate pip hashes
pip hash requests==2.31.0
# Output: --hash=sha256:abc123...
```

## 7. Enforce in CI/CD

```yaml
# .github/workflows/security-check.yml
name: Dependency Security
on: [pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm audit --audit-level=high
      - run: pip install pip-audit && pip-audit
      - name: Block merge on failure
        if: ${{ failure() }}
        run: exit 1
```

## Supply-Chain Checklist

- [ ] All MCP executables verified against published checksums
- [ ] Cooldown policies configured for write operations
- [ ] `npm audit` / `pip-audit` pass with no HIGH/CRITICAL vulnerabilities
- [ ] SAP security notes for relevant components reviewed
- [ ] Lockfiles committed to version control
- [ ] CI/CD pipeline blocks merge on audit failures

## Pitfalls

- **Cause:** MCP server runs with same OS privileges as the agent → **Solution:** Sandbox untrusted MCPs in a container or restricted user account; never run unverified MCPs as root.
- **Cause:** `npm audit fix` introduces breaking changes → **Solution:** Review the diff after `npm audit fix --dry-run` before applying; pin major versions with `package.json` ranges.
- **Cause:** `pip-audit` misses SAP-specific CVEs → **Solution:** Standard tools don't know SAP security notes; check the SAP support portal separately for component-specific patches.
- **Cause:** `npm install` (not `npm ci`) silently updates lockfile → **Solution:** Always use `npm ci` in CI; it installs exact versions and fails if lockfile is out of sync.
- **Cause:** `--require-hashes` fails because hashes are missing → **Solution:** Run `pip hash <package>==<version>` for every dependency and append the hash line to `requirements.txt`.
- **Cause:** HSECNOTE notes auto-assigned by SAP are missed → **Solution:** Subscribe to SAP security note notifications for your installed components via the support portal.

## Verification

```bash
# 1. Verify MCP checksum matches published value
sha256sum aibap-mcp
# Compare output with the published SHA-256 on the release page

# 2. Verify npm audit is clean (no HIGH/CRITICAL)
npm audit --audit-level=high && echo "npm audit PASS" || echo "npm audit FAIL"

# 3. Verify pip-audit is clean
pip-audit && echo "pip audit PASS" || echo "pip audit FAIL"

# 4. Verify lockfile is in sync
npm ci --dry-run && echo "Lockfile OK" || echo "Lockfile out of sync"

# 5. Verify CI security workflow exists
test -f .github/workflows/security-check.yml && echo "CI check exists" || echo "MISSING CI check"
```
