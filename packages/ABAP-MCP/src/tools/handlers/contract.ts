/**
 * CONTRACT handler: get_abap_contract
 *
 * Returns the compressed public interface (signatures, no bodies) of a class or
 * interface — the part an agent needs to *call* a dependency. Typically 5–10% of
 * the full source, so it is the token-efficient way to give the model context on
 * surrounding objects before it writes code against them.
 */

import type { ADTClient } from "abap-adt-api";
import type { ToolResult } from "../../types.js";
import { S_GetContract } from "../../schemas.js";
import { getObjectSourceCached } from "../../cache.js";
import { buildContract, renderContract } from "../../helpers/contract.js";

function ok(text: string): ToolResult { return { content: [{ type: "text", text }] }; }

export async function handleGetAbapContract(client: ADTClient, args: Record<string, unknown>): Promise<ToolResult> {
  const p = S_GetContract.parse(args);
  const baseUrl = p.objectUrl.replace(/\/source\/main$/, "");
  const source = await getObjectSourceCached(client, `${baseUrl}/source/main`);
  const fallbackName = baseUrl.split("/").filter(Boolean).pop() ?? "";
  const contract = buildContract(source, fallbackName);
  const savings = source.length > 0
    ? ` (≈${Math.max(1, Math.round((1 - renderContract(contract).length / source.length) * 100))}% smaller than full source)`
    : "";
  return ok(`${renderContract(contract)}\n\n── contract derived from ${baseUrl}${savings}`);
}
