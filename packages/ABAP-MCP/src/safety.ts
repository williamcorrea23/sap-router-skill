/**
 * ABAP MCP Server — Safety Guards
 * Inline checks that protect against unintended writes/deletes.
 */

import { ErrorCode, McpError } from "@modelcontextprotocol/sdk/types.js";
import { cfg } from "./config.js";

/**
 * Capabilities each role is permitted to exercise. Roles can only *restrict*
 * relative to the ALLOW_* flags — the flags remain a hard prerequisite, this
 * matrix is an additional gate on top. "admin" (the default) permits all three,
 * so legacy setups that never set SAP_ROLE behave exactly as before.
 */
const ROLE_CAPABILITIES: Record<typeof cfg.role, ReadonlySet<"write" | "delete" | "execute">> = {
  viewer: new Set(),
  developer: new Set(["write", "execute"] as const),
  admin: new Set(["write", "delete", "execute"] as const),
};

/** Throw unless the configured role may exercise `capability`. */
export function assertRoleAllows(capability: "write" | "delete" | "execute"): void {
  if (!ROLE_CAPABILITIES[cfg.role].has(capability))
    throw new McpError(ErrorCode.InvalidRequest,
      `Role '${cfg.role}' is not permitted to ${capability}. ` +
      `Set SAP_ROLE to a role that allows it (developer = write/execute, admin = all).`);
}

export function assertWriteEnabled(action = "Write"): void {
  assertRoleAllows("write");
  if (!cfg.allowWrite)
    throw new McpError(ErrorCode.InvalidRequest,
      `${action} is disabled. Set ALLOW_WRITE=true in .env. ` +
      "⚠️  Only enable on DEV systems!");
}

export function assertDeleteEnabled(): void {
  assertRoleAllows("delete");
  if (!cfg.allowDelete)
    throw new McpError(ErrorCode.InvalidRequest,
      "Delete is disabled. Set ALLOW_DELETE=true in .env. ⚠️  This action cannot be undone!");
}

export function assertPackageAllowed(devClass: string): void {
  const upper = devClass.toUpperCase();
  const blocked = cfg.blockedPackages.find(p => upper.startsWith(p));
  if (blocked)
    throw new McpError(ErrorCode.InvalidRequest,
      `Package '${devClass}' is blocked (prefix '${blocked}' in BLOCKED_PACKAGES).`);
}

export function assertCustomerNamespace(name: string, prefix: string[]): void {
  const upper = name.toUpperCase();
  if (!prefix.some(p => upper.startsWith(p)))
    throw new McpError(ErrorCode.InvalidRequest,
      `Name '${name}' must start with ${prefix.join(" or ")} (customer namespace).`);
}

/**
 * Reject anything that is not a read-only query before it reaches `runQuery`.
 *
 * This is defense-in-depth, not the primary barrier: the real protection is
 * that the query runs in ADT's read-only data-preview context, which the
 * backend will not let mutate. The check here gives a clear, early error
 * instead of a confusing backend failure.
 *
 * A statement is accepted only if it begins with SELECT or WITH (common table
 * expression) and contains no data-modifying keyword as a standalone word.
 * The `\b...\b` boundaries mean identifiers like `delete_flag` do not trip it.
 */
export function assertSelectOnly(query: string): void {
  const trimmed = query.trim();
  const isRead = /^(SELECT|WITH)\b/i.test(trimmed);
  const hasDml = /\b(INSERT|UPDATE|DELETE|MODIFY|UPSERT|COMMIT|ROLLBACK)\b/i.test(trimmed);
  if (!isRead || hasDml)
    throw new McpError(ErrorCode.InvalidRequest,
      "Only read-only queries are allowed: the statement must start with SELECT or WITH " +
      "and must not contain INSERT/UPDATE/DELETE/MODIFY/UPSERT/COMMIT/ROLLBACK.");
}
