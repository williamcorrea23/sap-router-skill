/**
 * METHOD-LEVEL SURGERY handlers: read_abap_method, edit_abap_method
 *
 * Read or rewrite a single METHOD…ENDMETHOD block of a class without the agent
 * having to handle the whole class source. read_abap_method returns just the one
 * block; edit_abap_method splices a new body into the full source and routes it
 * through the standard write workflow (lock → DDIC → syntax → activate → unlock),
 * so all existing safety/locking/activation guarantees still apply.
 */

import type { ADTClient } from "abap-adt-api";
import type { ToolResult } from "../../types.js";
import { S_ReadMethod, S_EditMethod } from "../../schemas.js";
import { cfg } from "../../config.js";
import { assertWriteEnabled } from "../../safety.js";
import { writeWorkflow } from "../../write-workflow.js";
import { getObjectSourceCached, invalidateSource } from "../../cache.js";
import { extractMethod, replaceMethodBody, listMethodNames, MethodNotFoundError } from "../../helpers/method-splice.js";
import { audit } from "../../audit.js";

function ok(text: string): ToolResult { return { content: [{ type: "text", text }] }; }
function err(text: string): ToolResult { return { content: [{ type: "text", text }], isError: true }; }

export async function handleReadAbapMethod(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  const p = S_ReadMethod.parse(args);
  const baseUrl = p.objectUrl.replace(/\/source\/main$/, "");
  const source = await getObjectSourceCached(client, `${baseUrl}/source/main`);
  try {
    const block = extractMethod(source, p.methodName);
    return ok(
      `Method ${block.name} (of ${baseUrl}):\n\n${block.block}\n\n` +
      `── ${listMethodNames(source).length} method(s) in this source: ${listMethodNames(source).join(", ")}`
    );
  } catch (e) {
    if (e instanceof MethodNotFoundError) return err(e.message);
    throw e;
  }
}

export async function handleEditAbapMethod(client: ADTClient, args: Record<string, unknown>, extra?: any): Promise<ToolResult> {
  assertWriteEnabled();
  const p = S_EditMethod.parse(args);
  const baseUrl = p.objectUrl.replace(/\/source\/main$/, "");

  // Read current full source (bypass cache to avoid editing a stale copy).
  invalidateSource(baseUrl);
  const current = await getObjectSourceCached(client, `${baseUrl}/source/main`);

  let updated: string;
  try {
    updated = replaceMethodBody(current, p.methodName, p.source);
  } catch (e) {
    if (e instanceof MethodNotFoundError) return err(e.message);
    throw e;
  }
  if (updated === current) {
    return ok(`No change — the new body for '${p.methodName}' is identical to the current source.`);
  }

  const progressToken = (extra as { _meta?: { progressToken?: string | number } })?._meta?.progressToken;
  let step = 0;
  async function reportProgress(message: string) {
    if (progressToken === undefined) return;
    step++;
    await (extra as { sendNotification: (n: object) => Promise<void> }).sendNotification({
      method: "notifications/progress",
      params: { progressToken, progress: step, total: 4, message },
    });
  }

  const r = await writeWorkflow(
    client, baseUrl, updated,
    p.transport ?? cfg.defaultTransport,
    p.activateAfterWrite ?? true,
    p.skipSyntaxCheck ?? false,
    undefined,
    reportProgress,
  );
  const body = r.log.join("\n") + (r.syntaxErrors ? "\n\nSyntax errors:\n" + r.syntaxErrors.join("\n") : "");
  audit({ tool: "edit_abap_method", action: "write", target: `${baseUrl}#${p.methodName}`, outcome: r.success ? "success" : "error" });
  if (r.success) {
    return ok(`✅ Method '${p.methodName}' updated and activated\n\n${body}`);
  }
  return err(`❌ Method '${p.methodName}' NOT activated!\n\n${body}\n\n⚠️ ACTION REQUIRED: Fix the method body and call edit_abap_method again. Repeat until activation succeeds.`);
}
