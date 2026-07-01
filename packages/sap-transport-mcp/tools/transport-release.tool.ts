import { z } from "zod";
import { getSystem } from "../config/systems.js";
import { adtPost, debugLog } from "../lib/adt-client.js";
import { enforceWritePolicy, auditLog } from "../config/policy.js";
import { transportGetTool } from "./transport-get.tool.js";

export const TransportReleaseInputSchema = z.object({
  transportNumber: z
    .string()
    .regex(/^[A-Z][A-Z0-9]{2}K\d{6}$/, "Transport number format: 3-char system ID + K + 6 digits (e.g. GW1K900528)")
    .describe("SAP transport request number to release (e.g. DEVK900123)."),
  systemId: z
    .string()
    .optional()
    .describe("Logical SAP system ID. Omit to use the default system."),
});

export type TransportReleaseInput = z.infer<typeof TransportReleaseInputSchema>;

export interface TransportReleaseResult {
  success: boolean;
  transportNumber: string;
  message: string;
  verification: {
    status: string;
    objectCount: number;
    targetSystem: string;
    releasedAt: string;
  };
}

export const transportReleaseTool = {
  name: "transport_release_request",
  description:
    "Releases a SAP transport request, making it available for import into the target system. " +
    "IMPORTANT: Release is irreversible. " +
    "Always call transport_get_request first to review the object list, " +
    "and confirm with the user before calling this tool. " +
    "Blocked if the transport contains zero objects.",

  async handler(rawInput: unknown): Promise<TransportReleaseResult> {
    const input = TransportReleaseInputSchema.parse(rawInput);
    const system = getSystem(input.systemId);
    const trkorr = input.transportNumber.toUpperCase();

    // 1. Read current state — needed for policy checks
    const current = await transportGetTool.handler({
      transportNumber: trkorr,
      systemId: input.systemId,
    });

    // 2. Governance — checks DRY_RUN, empty transport, released status
    enforceWritePolicy({
      toolName: "transport_release_request",
      systemId: system.id,
      transportNumber: trkorr,
      objectCount: current.objectCount,
      transportStatus: current.status,
    });

    let result: TransportReleaseResult;

    try {
      debugLog(`releasing transport ${trkorr} on ${system.id} (${current.objectCount} objects)`);

      await adtPost(
        system,
        `/sap/bc/adt/cts/transportrequests/${trkorr}/releasejobs`,
        undefined
      );

      // 3. Verify release succeeded
      const verified = await transportGetTool.handler({
        transportNumber: trkorr,
        systemId: input.systemId,
      });

      result = {
        success: true,
        transportNumber: trkorr,
        message:
          `Transport ${trkorr} released successfully on ${system.id}. ` +
          `${current.objectCount} object(s) exported to ${current.targetSystem}.`,
        verification: {
          status: verified.status,
          objectCount: verified.objectCount,
          targetSystem: verified.targetSystem,
          releasedAt: new Date().toISOString(),
        },
      };
    } catch (error) {
      auditLog({
        toolName: "transport_release_request",
        systemId: system.id,
        transportNumber: trkorr,
        objectCount: current.objectCount,
        targetSystem: current.targetSystem,
        input,
        result: "error",
        detail: error instanceof Error ? error.message : String(error),
      });
      throw error;
    }

    auditLog({
      toolName: "transport_release_request",
      systemId: system.id,
      transportNumber: trkorr,
      objectCount: current.objectCount,
      targetSystem: current.targetSystem,
      input,
      result: "success",
      detail: result.message,
    });

    return result;
  },
};
