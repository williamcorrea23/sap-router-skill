/**
 * ABAP MCP Server — Write Workflow
 * Orchestrates: lock → write → DDIC check → syntax check → activate → unlock
 */

import type { ADTClient, ActivationResultMessage } from "abap-adt-api";
import { isAdtError } from "abap-adt-api";
import { withWriteLock, withStatefulSession } from "./concurrency.js";
import { resolveMainProgram, resolveSyntaxContext } from "./helpers/resolve.js";
import { validateDdicReferencesInternal } from "./helpers/ddic-validation.js";
import { invalidateSource } from "./cache.js";

export function formatActivationMessages(messages: ActivationResultMessage[]): string[] {
  return messages.map(m =>
    `  [${m.type}] ${m.shortText}${m.line ? ` (line ${m.line})` : ""}${m.objDescr ? ` — ${m.objDescr}` : ""}`
  );
}

/** For ABAP class includes (e.g. /includes/definitions), the lock must be on the parent class.
 *  Returns the URL that should be used for lock/unlock operations. */
function getLockUrl(objectUrl: string): string {
  const includesIdx = objectUrl.indexOf("/includes/");
  if (includesIdx !== -1) return objectUrl.substring(0, includesIdx);
  return objectUrl;
}

/** For ABAP class includes, the source is written directly to the include URL (no /source/main suffix).
 *  For all other objects, append /source/main if not already present. */
function getSourceUrl(objectUrl: string): string {
  if (objectUrl.includes("/includes/")) return objectUrl;
  return objectUrl.endsWith("/source/main") ? objectUrl : `${objectUrl}/source/main`;
}

export async function writeWorkflow(
  client: ADTClient,
  objectUrl: string,
  source: string,
  transport: string,
  activate: boolean,
  skipCheck: boolean,
  mainProgram?: string,
  onProgress?: (msg: string) => Promise<void>,
): Promise<{ success: boolean; log: string[]; syntaxErrors?: string[] }> {
  const lockUrl = getLockUrl(objectUrl);
  return withWriteLock(() => withStatefulSession(client, async () => {
    const log: string[] = [];
    let lockHandle: string | undefined;
    try {
      // Phase 1: lock → write → unlock (stateful session needed for lock/write)
      log.push(`🔒 Locking: ${lockUrl}`);
      // Direct lock — withStatefulSession already manages the session
      let lockResult: { LOCK_HANDLE?: string } | undefined;
      try {
        lockResult = await client.lock(lockUrl);
      } catch (lockErr) {
        const errMsg = lockErr instanceof Error ? lockErr.message : String(lockErr);
        // CTS_WBO_API/19 or /20 = "Object already locked in request X of user Y"
        // The T100 key is stored in AdtErrorException.properties, NOT in .message.
        // Check both the message text and the ADT properties for the lock error.
        const isLockConflict = errMsg.includes("already locked") ||
          (isAdtError(lockErr) && (
            lockErr.properties["T100KEY-ID"] === "CTS_WBO_API" ||
            errMsg.includes("CTS_WBO_API")
          ));
        if (isLockConflict) {
          // Extract the transport that actually holds the lock from the error message
          // e.g. "already locked in request S4PK912551 of user ..."
          const lockedInMatch = errMsg.match(/locked in request (\w+)/i);
          const corrNrFromErr = lockedInMatch?.[1] ?? transport;
          if (!corrNrFromErr) { throw lockErr; }

          // Helper: attempt a single lock POST with a given corrNr
          const tryLockWithCorrNr = async (corrNr: string): Promise<string | undefined> => {
            const lockResp = await client.httpClient.request(lockUrl, {
              method: "POST",
              headers: {
                Accept: "application/*,application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.lock.result",
              },
              qs: { _action: "LOCK", accessMode: "MODIFY", corrNr },
            });
            const bodyStr = typeof lockResp.body === "string" ? lockResp.body : JSON.stringify(lockResp.body);
            const m = bodyStr.match(/<LOCK_HANDLE>(.*?)<\/LOCK_HANDLE>/);
            return m?.[1];
          };

          // Attempt 1: use the transport extracted from the error message (workbench request)
          log.push(`⚠️ Lock failed (object in transport ${corrNrFromErr}), retrying with corrNr=${corrNrFromErr}...`);
          let handle: string | undefined;
          let lastRetryErr: unknown;
          try {
            handle = await tryLockWithCorrNr(corrNrFromErr);
          } catch (e1) {
            lastRetryErr = e1;
          }

          // Attempt 2: if attempt 1 failed, look up the transport task via transportInfo
          // (ADT sometimes requires the task number, not the workbench request number)
          if (!handle) {
            try {
              const info = await client.transportInfo(lockUrl, "");
              const tasks: Array<{ TRKORR: string }> = (info as { LOCKS?: { TASKS?: Array<{ TRKORR: string }> } })?.LOCKS?.TASKS ?? [];
              for (const task of tasks) {
                try {
                  handle = await tryLockWithCorrNr(task.TRKORR);
                  if (handle) {
                    log.push(`✅ Lock acquired (corrNr retry with task ${task.TRKORR})`);
                    break;
                  }
                } catch (e2) {
                  lastRetryErr = e2;
                }
              }
            } catch {
              // transportInfo failed — ignore, will throw original error below
            }
          } else {
            log.push(`✅ Lock acquired (corrNr retry)`);
          }

          if (!handle) {
            throw new Error(
              `Lock failed: ${errMsg}. corrNr retry also failed: ${lastRetryErr instanceof Error ? lastRetryErr.message : String(lastRetryErr)}`
            );
          }
          lockResult = { LOCK_HANDLE: handle };
        } else {
          throw lockErr;
        }
      }
      lockHandle = lockResult?.LOCK_HANDLE;
      if (!lockHandle) throw new Error("Lock failed — no lock handle received");
      log.push(`✅ Lock acquired`);
      await onProgress?.("🔒 Lock acquired");

      log.push(`✏️  Writing source code (${source.length} characters)...`);
      const sourceUrl = getSourceUrl(objectUrl);
      // setObjectSource may fail if the lock was acquired without corrNr (same-user re-lock)
      // but the object is actually in a different transport than the one passed by the caller.
      // In that case, extract the correct transport from the error and retry.
      try {
        await client.setObjectSource(sourceUrl, source, lockHandle, transport || undefined);
        // Server copy changed — drop any cached source so subsequent reads revalidate.
        invalidateSource(objectUrl);
        log.push("✅ Source code saved");
      } catch (e) {
        const writeErrMsg = e instanceof Error ? e.message : String(e);
        const isWriteLockConflict = writeErrMsg.includes("already locked") ||
          (isAdtError(e) && (
            e.properties["T100KEY-ID"] === "CTS_WBO_API" ||
            writeErrMsg.includes("CTS_WBO_API")
          ));
        if (isWriteLockConflict) {
          // Extract the transport that actually holds the lock
          // e.g. "already locked in request S4PK912551 of user ..."
          const lockedInMatch = writeErrMsg.match(/locked in request (\w+)/i);
          const correctTransport = lockedInMatch?.[1];
          if (correctTransport && correctTransport !== transport) {
            log.push(`⚠️ Write failed (lock in ${correctTransport}), retrying with corrNr=${correctTransport}...`);
            await client.setObjectSource(sourceUrl, source, lockHandle, correctTransport);
            invalidateSource(objectUrl);
            log.push(`✅ Source code saved (corrNr retry with ${correctTransport})`);
          } else {
            throw e;
          }
        } else {
          throw e;
        }
      }
      await onProgress?.("✏️ Source code saved");

      // Early DDIC validation prevents typical infinite loops caused by field name errors
      const ddicCheck = await validateDdicReferencesInternal(client, source);
      if (ddicCheck.tableCount > 0) {
        log.push(`🔎 DDIC validation: ${ddicCheck.tableCount} tables/structures checked`);
      }
      if (ddicCheck.invalid.length > 0) {
        log.push("❌ DDIC validation failed — code NOT activated.");
        log.push(...ddicCheck.invalid.slice(0, 50));
        if (ddicCheck.invalid.length > 50) {
          log.push(`... and ${ddicCheck.invalid.length - 50} more DDIC errors`);
        }
        log.push("👉 Please fix the invalid field names and call write_abap_source again.");
        return { success: false, log, syntaxErrors: ddicCheck.invalid };
      }

      // Phase 2: unlock + syntaxCheck in parallel (no lock needed for check)
      log.push("🔓 Releasing lock + 🔍 Syntax check (parallel)...");
      const syntaxContext = await resolveSyntaxContext(client, objectUrl, mainProgram, log);
      const [, syntaxRes] = await Promise.all([
        client.unLock(lockUrl, lockHandle).catch((e) => {
          log.push(`⚠️ Unlock failed: ${e instanceof Error ? e.message : String(e)}`);
        }),
        !skipCheck
          ? client.syntaxCheck(objectUrl, syntaxContext, source).catch((e) => {
              log.push(`⚠️ Syntax check failed: ${e instanceof Error ? e.message : String(e)}`);
              return null; // null = check failed
            })
          : Promise.resolve(undefined),
      ]);
      lockHandle = undefined;
      log.push("✅ Lock released");

      // Process syntaxRes (undefined = skipped, null = error, array = result)
      if (!skipCheck && syntaxRes !== undefined) {
        if (syntaxRes === null) {
          log.push("👉 Syntax check skipped — code was saved. Please check manually.");
          return { success: false, log };
        }
        const errs = (Array.isArray(syntaxRes) ? syntaxRes : []).filter(
          (m: { severity: string }) => ["E", "A"].includes(m.severity));
        if (errs.length > 0) {
          const msgs = errs.map((e: { text: string; line?: number }) => `  Line ${e.line ?? "?"}: ${e.text}`);
          log.push(`❌ ${errs.length} syntax error(s) — code NOT activated.`);
          log.push("👉 Please fix the errors and call write_abap_source again!");
          return { success: false, log, syntaxErrors: msgs };
        }
        log.push("✅ Syntax check OK");
        await onProgress?.("🔍 Syntax check OK — activating...");
      }

      if (activate) {
        log.push("🚀 Activating...");
        const segments = objectUrl.replace(/[?#].*$/, "").split("/").filter(Boolean);
        const name = segments[segments.length - 1] ?? objectUrl;

        // Include programs need the main program as context for activation,
        // because they cannot be activated alone (they reference variables of the main program).
        let activationContext: string | undefined;
        const isInclude = objectUrl.includes("/programs/includes/");
        if (isInclude) {
          const resolvedMain = resolveMainProgram(mainProgram);
          if (resolvedMain) {
            activationContext = resolvedMain;
            log.push(`📎 Include — activating in context of: ${mainProgram}`);
          } else {
            // Automatically determine main program
            try {
              const mains = await client.mainPrograms(objectUrl);
              if (mains.length > 0) {
                activationContext = mains[0]["adtcore:uri"];
                log.push(`📎 Include — main program automatically determined: ${mains[0]["adtcore:name"]}`);
              }
            } catch (mpErr) {
              log.push(`⚠️  Main program could not be determined: ${String(mpErr instanceof Error ? mpErr.message : mpErr)}`);
            }
          }
        }

        const activationResult = await client.activate(name, objectUrl, activationContext);
        if (!activationResult.success) {
          const msgs = formatActivationMessages(activationResult.messages);
          log.push(`❌ Activation failed — code was saved but NOT activated.`);
          if (msgs.length > 0) log.push(...msgs);
          log.push("👉 Please analyze the errors, fix the code and call write_abap_source again!");
          return { success: false, log };
        }
        if (activationResult.messages.length > 0) {
          log.push("✅ Activated (with notices):");
          log.push(...formatActivationMessages(activationResult.messages));
        } else {
          log.push("✅ Activated");
        }
        await onProgress?.("✅ Activated");
      }

      return { success: true, log };
    } catch (err) {
      if (lockHandle) {
        try { await client.unLock(lockUrl, lockHandle); log.push("🔓 Lock released after error"); }
        catch { log.push("⚠️  Lock could not be released — dropSession in finally will clean up"); }
        lockHandle = undefined;
      }
      throw err;
    }
  }));
}
