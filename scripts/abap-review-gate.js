#!/usr/bin/env node
/**
 * ABAP Peer Review Gate — processes abaplint JSON output and enforces
 * severity-based pass/fail thresholds for CI/CD pipelines.
 *
 * Usage:
 *   cat abaplint-report.json | node scripts/abap-review-gate.js --mode security
 *   cat abaplint-report.json | node scripts/abap-review-gate.js --mode clean
 *
 * Modes:
 *   security — CRITICAL findings only (SQL injection, dangerous stmts, auth gaps)
 *   clean     — All findings (style + security + performance)
 *   transport — Pre-release gate (blocks transport on CRITICAL + HIGH)
 *
 * Exit codes: 0 = pass, 1 = findings above threshold, 2 = invalid input
 */

const { argv, stdin, exit } = require('process');

// Parse mode from CLI
const modeIdx = argv.indexOf('--mode');
const mode = modeIdx !== -1 ? argv[modeIdx + 1] : 'clean';

// Severity thresholds per mode
const THRESHOLDS = {
  security:  { CRITICAL: 0, HIGH: 1, MEDIUM: 5, LOW: 20 },
  clean:     { CRITICAL: 0, HIGH: 3, MEDIUM: 20, LOW: 100 },
  transport: { CRITICAL: 0, HIGH: 0, MEDIUM: 10, LOW: 50 },
};

// Security-critical rule categories
const SECURITY_RULES = new Set([
  'sql_escape_host_variables',
  'db_operation_in_loop',
  'select_performance',
  'rfc_error_handling',
  'obsolete_statement',
  'function_pool',
  'release_idoc',
]);

const threshold = THRESHOLDS[mode] || THRESHOLDS.clean;

let buffer = '';
stdin.setEncoding('utf-8');
stdin.on('data', (chunk) => { buffer += chunk; });

stdin.on('end', () => {
  try {
    const findings = JSON.parse(buffer);

    if (!Array.isArray(findings) && !findings.issues) {
      console.error('ERROR: Expected JSON array of abaplint findings or {issues: [...]}');
      exit(2);
    }

    const issues = Array.isArray(findings) ? findings : (findings.issues || []);

    // Map severity: abaplint uses "error", "warning", "info"
    const severityMap = {
      error: 'HIGH',
      warning: 'MEDIUM',
      info: 'LOW',
    };

    // Count findings by severity
    const counts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0, TOTAL: issues.length };
    const failures = [];

    for (const issue of issues) {
      // Determine severity
      let sev = severityMap[issue.severity] || 'LOW';

      // Elevate security rules to CRITICAL
      if (mode === 'security' && SECURITY_RULES.has(issue.key)) {
        sev = 'CRITICAL';
      }

      counts[sev]++;

      if (counts[sev] <= 5) {
        failures.push({
          file: issue.file || issue.filename || 'unknown',
          line: issue.line || issue.start?.row || 0,
          severity: sev,
          rule: issue.key || 'unknown',
          message: issue.message || issue.description || '',
        });
      }
    }

    // Print summary
    console.log(`\nABAP Peer Review — ${mode.toUpperCase()} MODE`);
    console.log('═'.repeat(50));
    console.log(`Total findings: ${counts.TOTAL}`);
    console.log(`  CRITICAL: ${counts.CRITICAL}  (threshold: ${threshold.CRITICAL})`);
    console.log(`  HIGH:     ${counts.HIGH}  (threshold: ${threshold.HIGH})`);
    console.log(`  MEDIUM:   ${counts.MEDIUM}  (threshold: ${threshold.MEDIUM})`);
    console.log(`  LOW:      ${counts.LOW}  (threshold: ${threshold.LOW})`);
    console.log('');

    if (failures.length > 0) {
      console.log('Top findings:');
      for (const f of failures) {
        const flag = f.severity === 'CRITICAL' ? '🔴' : f.severity === 'HIGH' ? '🟠' : f.severity === 'MEDIUM' ? '🟡' : '⚪';
        console.log(`  ${flag} ${f.file}:${f.line} [${f.rule}] ${f.message}`);
      }
      console.log('');
    }

    // Gate check
    if (counts.CRITICAL > threshold.CRITICAL) {
      console.log(`❌ BLOCKED: ${counts.CRITICAL} CRITICAL findings exceed threshold ${threshold.CRITICAL}`);
      exit(1);
    }
    if (counts.HIGH > threshold.HIGH) {
      console.log(`❌ BLOCKED: ${counts.HIGH} HIGH findings exceed threshold ${threshold.HIGH}`);
      exit(1);
    }
    if (counts.MEDIUM > threshold.MEDIUM) {
      console.log(`⚠️  WARNING: ${counts.MEDIUM} MEDIUM findings exceed threshold ${threshold.MEDIUM}`);
      if (mode === 'transport') {
        console.log('   Transport release BLOCKED.');
        exit(1);
      }
    }

    console.log(`✅ PASS: All findings within ${mode} thresholds.`);
    exit(0);

  } catch (e) {
    console.error(`ERROR: ${e.message}`);
    exit(2);
  }
});
