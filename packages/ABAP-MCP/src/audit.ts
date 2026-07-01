/**
 * ABAP MCP Server — Structured Audit Log
 *
 * Every state-changing action (write, create, delete, activate, execute, git
 * pull) is recorded as a single JSON line. This gives a tamper-evident trail of
 * "who changed what" — the baseline governance control for multi-user or shared
 * deployments.
 *
 * Output goes to STDERR, never STDOUT: stdout is the MCP stdio protocol channel
 * and any stray bytes there corrupt the client connection. When AUDIT_LOG_FILE
 * is set, lines are additionally appended to that file.
 */

import * as fs from "fs";
import { cfg } from "./config.js";

export interface AuditEvent {
  /** Tool that triggered the action, e.g. "write_abap_source". */
  tool: string;
  /** Coarse capability exercised: write | delete | execute. */
  action: "write" | "delete" | "execute";
  /** Target object URL / name where applicable. */
  target?: string;
  /** Outcome of the action. */
  outcome: "attempt" | "success" | "denied" | "error";
  /** Optional free-text detail (error message, transport, etc.). */
  detail?: string;
}

export function audit(event: AuditEvent): void {
  const line = JSON.stringify({
    ts: new Date().toISOString(),
    instance: cfg.instanceId,
    user: cfg.user,
    role: cfg.role,
    ...event,
  });
  // Prefix marks audit lines for easy grep/extraction from the stderr stream.
  process.stderr.write(`AUDIT ${line}\n`);
  if (cfg.auditLogFile) {
    try {
      fs.appendFileSync(cfg.auditLogFile, line + "\n");
    } catch (e) {
      process.stderr.write(`AUDIT_WRITE_FAILED ${e instanceof Error ? e.message : String(e)}\n`);
    }
  }
}
