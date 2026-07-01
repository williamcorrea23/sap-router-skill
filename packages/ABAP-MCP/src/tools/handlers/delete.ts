/**
 * DELETE tool handler: delete_abap_object
 */

import type { ADTClient } from "abap-adt-api";
import type { ToolResult } from "../../types.js";
import { S_DeleteObject } from "../../schemas.js";
import { assertWriteEnabled, assertDeleteEnabled } from "../../safety.js";
import { withWriteLock, withStatefulSession } from "../../concurrency.js";
import { invalidateSource } from "../../cache.js";
import { audit } from "../../audit.js";

function ok(text: string): ToolResult { return { content: [{ type: "text", text }] }; }

export async function handleDeleteAbapObject(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  assertWriteEnabled("Delete");
  assertDeleteEnabled();
  const p = S_DeleteObject.parse(args);
  audit({ tool: "delete_abap_object", action: "delete", target: p.objectUrl, outcome: "attempt" });
  try {
    await withWriteLock(() => withStatefulSession(client, async () => {
      const lock = await client.lock(p.objectUrl);
      try {
        await client.deleteObject(p.objectUrl, lock.LOCK_HANDLE, p.transport || undefined);
      } catch (e) {
        try { await client.unLock(p.objectUrl, lock.LOCK_HANDLE); } catch { /* ignore */ }
        throw e;
      }
    }));
  } catch (e) {
    audit({ tool: "delete_abap_object", action: "delete", target: p.objectUrl, outcome: "error", detail: e instanceof Error ? e.message : String(e) });
    throw e;
  }
  invalidateSource(p.objectUrl);
  audit({ tool: "delete_abap_object", action: "delete", target: p.objectUrl, outcome: "success" });
  return ok(`✅ Object '${p.objectName}' deleted.\n⚠️  This action cannot be undone.`);
}
