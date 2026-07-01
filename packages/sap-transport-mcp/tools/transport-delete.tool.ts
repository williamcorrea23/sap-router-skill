import { z } from "zod";
import { getSystem } from "../config/systems.js";
import { adtDelete, adtGet, debugLog } from "../lib/adt-client.js";
import { enforceWritePolicy, auditLog } from "../config/policy.js";
import { transportGetTool } from "./transport-get.tool.js";

export const TransportDeleteInputSchema = z.object({
  transportNumber: z
    .string()
    .regex(/^[A-Z][A-Z0-9]{2}K\d{6}$/, "Transport number format: 3-char system ID + K + 6 digits (e.g. GW1K900528)")
    .describe(
      "SAP transport request number to delete (e.g. DEVK900123). " +
        "Only Modifiable (unreleased) transports can be deleted."
    ),
  systemId: z
    .string()
    .optional()
    .describe("Logical SAP system ID. Omit to use the default system."),
});

export type TransportDeleteInput = z.infer<typeof TransportDeleteInputSchema>;

export interface TransportDeleteResult {
  success: boolean;
  transportNumber: string;
  message: string;
  verification: {
    exists: boolean;
  };
}

export const transportDeleteTool = {
  name: "transport_delete_request",
  description:
    "Deletes an unreleased SAP transport request. " +
    "Blocked if the transport has already been released. " +
    "Always call transport_get_request first to confirm the transport is empty or unwanted " +
    "before deleting. This action is permanent.",

  async handler(rawInput: unknown): Promise<TransportDeleteResult> {
    const input = TransportDeleteInputSchema.parse(rawInput);
    const system = getSystem(input.systemId);
    const trkorr = input.transportNumber.toUpperCase();

    // 1. Read current state — needed for policy check on status
    const current = await transportGetTool.handler({
      transportNumber: trkorr,
      systemId: input.systemId,
    });

    // 2. Governance — blocks delete of released transports
    enforceWritePolicy({
      toolName: "transport_delete_request",
      systemId: system.id,
      transportNumber: trkorr,
      transportStatus: current.status,
    });

    let result: TransportDeleteResult;

    try {
      debugLog(`deleting transport ${trkorr} on ${system.id} (status: ${current.status})`);

      await adtDelete(system, `/sap/bc/adt/cts/transportrequests/${trkorr}`);

      // 3. Verify: confirm record no longer exists (expect 404)
      let stillExists = false;
      try {
        await adtGet(system, `/sap/bc/adt/cts/transportrequests/${trkorr}`);
        stillExists = true; // if this succeeds, delete did not work
      } catch {
        stillExists = false; // 404 = successfully deleted
      }

      if (stillExists) {
        throw new Error(
          `Transport ${trkorr} still exists after delete — SAP may have rejected the deletion. ` +
            "Check SE09 or contact your Basis team."
        );
      }

      result = {
        success: true,
        transportNumber: trkorr,
        message: `Transport ${trkorr} deleted from ${system.id}.`,
        verification: { exists: false },
      };
    } catch (error) {
      auditLog({
        toolName: "transport_delete_request",
        systemId: system.id,
        transportNumber: trkorr,
        input,
        result: "error",
        detail: error instanceof Error ? error.message : String(error),
      });
      throw error;
    }

    auditLog({
      toolName: "transport_delete_request",
      systemId: system.id,
      transportNumber: trkorr,
      input,
      result: "success",
      detail: result.message,
    });

    return result;
  },
};
