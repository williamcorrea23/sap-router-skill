import { env } from "./env.js";

export class PolicyViolation extends Error {
  constructor(rule: string, detail: string) {
    super(`Policy violation [${rule}]: ${detail}`);
    this.name = "PolicyViolation";
  }
}

export interface WriteContext {
  toolName: string;
  systemId?: string;
  transportNumber?: string;
  objectCount?: number;
  transportStatus?: string;
  description?: string;
}

/**
 * Enforces governance rules before any write tool executes.
 * Throws PolicyViolation if the operation is not allowed.
 * Call this BEFORE any SAP API call in write tools.
 */
export function enforceWritePolicy(ctx: WriteContext): void {
  // 1. DRY_RUN blocks all writes
  if (env.DRY_RUN) {
    throw new PolicyViolation(
      "DRY_RUN",
      `Write blocked — DRY_RUN=true. Set DRY_RUN=false in .env to enable live writes. Tool: ${ctx.toolName}`
    );
  }

  // 2. Transport description must be meaningful
  if (ctx.description !== undefined && ctx.description.trim().length < 10) {
    throw new PolicyViolation(
      "DESCRIPTION_TOO_SHORT",
      `Transport description must be at least 10 characters. ` +
        `"${ctx.description}" is ${ctx.description.trim().length} characters. ` +
        `Provide a meaningful description (e.g. "Add plant 1000 config for Q2 cutover").`
    );
  }

  // 3. Cannot release a transport with zero objects
  if (ctx.toolName === "transport_release_request" && ctx.objectCount !== undefined) {
    if (ctx.objectCount === 0) {
      throw new PolicyViolation(
        "EMPTY_TRANSPORT",
        `Transport ${ctx.transportNumber ?? "(unknown)"} has no objects. ` +
          `Add ABAP objects before releasing. Releasing an empty transport wastes an import slot.`
      );
    }
  }

  // 4. Cannot delete a transport that has already been released
  if (ctx.toolName === "transport_delete_request" && ctx.transportStatus !== undefined) {
    if (ctx.transportStatus === "Released" || ctx.transportStatus === "Release Started") {
      throw new PolicyViolation(
        "DELETE_RELEASED",
        `Transport ${ctx.transportNumber ?? "(unknown)"} has status "${ctx.transportStatus}" ` +
          `and cannot be deleted. Released transports are immutable — contact your Basis team if rollback is needed.`
      );
    }
  }
}

/**
 * Audit log — call after every write (success or failure).
 * Replace console.error with your real sink: Splunk, CloudWatch, SAP audit trail, etc.
 */
export function auditLog(entry: {
  toolName: string;
  systemId?: string;
  transportNumber?: string;
  objectCount?: number;
  targetSystem?: string;
  input: unknown;
  result: "success" | "error";
  detail?: string;
}): void {
  const record = {
    timestamp: new Date().toISOString(),
    audit: true,
    ...entry,
  };
  // Always log audit entries regardless of LOG_LEVEL
  console.error(JSON.stringify(record));
}
