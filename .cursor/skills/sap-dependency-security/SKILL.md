---
name: sap-dependency-security
description: SAP dependency security — MCP executable trust verification, supply-chain safeguards, cooldown policies for sensitive operations, lockfile hardening, npm/pip dependency audit, SAP note security patches tracking. Use when auditing project dependencies, verifying MCP server executables, or implementing supply-chain security policies for SAP tools.
---

# SAP Dependency Security

Supply-chain security for SAP development tooling and MCP servers.

## MCP Executable Trust

```bash
# Verify MCP executable signature
sha256sum aibap-mcp > checksum.txt
# Compare with published checksum from repo releases page

# Run executable in sandbox first
./aibap-mcp --dry-run --read-only 2>&1 | tee first-run.log
# Review: does it connect to unexpected hosts? Does it write files?
```

## Cooldown Policies

```
Operation           Cooldown    Reason
─────────           ───────     ──────
SAPWrite            5 seconds   Prevent bulk code changes
Transport release   30 minutes  Production safety
SAP system delete   24 hours    Irreversible
User creation       1 hour      IAM audit trail
BAPI_POST_DOCUMENT  10 seconds  Financial safety
```

## npm/pip Dependency Audit

```bash
# npm audit
npm audit
npm audit fix

# pip audit
pip install pip-audit
pip-audit

# Check for SAP-specific CVEs
curl https://api.sap.com/v1/security/notes?search=nodejs
```

## SAP Note Security Patches

```bash
# Check relevant security notes
# Use mcp-sap-notes to fetch latest security notes for component BC-ABA
```

## Lockfile Hardening

```bash
# npm
npm ci  # use exact versions from package-lock.json

# pip
pip install -r requirements.txt --require-hashes
# requirements.txt with hashes:
# requests==2.31.0 --hash=sha256:abc123...
```

## Supply-Chain Checklist

- [ ] All MCP executables verified against published checksums
- [ ] Cooldown policies configured for write operations
- [ ] npm/pip audit pass with no HIGH/CRITICAL vulnerabilities
- [ ] SAP security notes for relevant components reviewed
- [ ] Lockfiles committed to version control
- [ ] CI/CD pipeline blocks merge on audit failures

## Gotchas
- MCP servers run with same OS privileges as Claude Code — sandbox untrusted MCPs
- Dependency audit tools may not catch SAP-specific vulnerabilities (check SAP notes separately)
- HSECNOTE security notes auto-assigned by SAP for transport-critical patches
