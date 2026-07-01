import { z } from "zod";
import { getSystem } from "../config/systems.js";
import { adtGet, debugLog } from "../lib/adt-client.js";
import { extractTransportRequestsFromXml, type ImportQueueEntry } from "../lib/transport-mapper.js";

export const ImportQueueInputSchema = z.object({
  targetSystemId: z
    .string()
    .describe(
      "SAP system ID of the target system to check (e.g. QA1, PRD). " +
        "This is the 3-character SID of the system you want to import into."
    ),
  systemId: z
    .string()
    .optional()
    .describe(
      "Logical SAP system ID to query FROM (usually DEV). " +
        "Omit to use the default configured system."
    ),
});

export type ImportQueueInput = z.infer<typeof ImportQueueInputSchema>;

export interface ImportQueueResult {
  targetSystem: string;
  queriedFrom: string;
  pendingCount: number;
  transports: ImportQueueEntry[];
}

export const importQueueTool = {
  name: "transport_check_import_queue",
  description:
    "Shows transport requests currently waiting to be imported into a target SAP system. " +
    "Use this before releasing to confirm the target system is not backlogged, " +
    "and after releasing to verify your transport entered the queue. " +
    "Safe to call any time — read only.",

  async handler(rawInput: unknown): Promise<ImportQueueResult> {
    const input = ImportQueueInputSchema.parse(rawInput);
    const system = getSystem(input.systemId);
    const targetSid = input.targetSystemId.toUpperCase();

    debugLog(`checking import queue for ${targetSid} from ${system.id}`);

    const raw = await adtGet<unknown>(
      system,
      `/sap/bc/adt/cts/transportrequests`,
      { targets: targetSid }
    );

    // Import queue = Released transports targeted for this system
    const all = extractTransportRequestsFromXml(raw, undefined, "Released");
    const transports: ImportQueueEntry[] = all.map((t) => ({
      transportNumber: t.transportNumber,
      description: t.description,
      owner: t.owner,
      targetSystem: targetSid,
      queuedAt: t.createdAt,
    }));

    return {
      targetSystem: targetSid,
      queriedFrom: system.id,
      pendingCount: transports.length,
      transports,
    };
  },
};
