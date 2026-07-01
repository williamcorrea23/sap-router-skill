import { z } from "zod";
import { getSystem } from "../config/systems.js";
import { adtGet, debugLog } from "../lib/adt-client.js";
import { extractObjectsFromXml, type TransportObject } from "../lib/transport-mapper.js";

export const TransportObjectsInputSchema = z.object({
  transportNumber: z
    .string()
    .regex(/^[A-Z][A-Z0-9]{2}K\d{6}$/, "Transport number format: 3-char system ID + K + 6 digits (e.g. GW1K900528)")
    .describe("SAP transport request number (e.g. DEVK900123)."),
  systemId: z
    .string()
    .optional()
    .describe("Logical SAP system ID. Omit to use the default system."),
});

export type TransportObjectsInput = z.infer<typeof TransportObjectsInputSchema>;

export interface TransportObjectsResult {
  transportNumber: string;
  system: string;
  objectCount: number;
  objects: TransportObject[];
}

export const transportObjectsTool = {
  name: "transport_list_objects",
  description:
    "Lists all ABAP objects included in a SAP transport request. " +
    "Use this to verify the expected programs, tables, function groups, and configurations " +
    "are present before releasing. Safe to call any time — read only.",

  async handler(rawInput: unknown): Promise<TransportObjectsResult> {
    const input = TransportObjectsInputSchema.parse(rawInput);
    const system = getSystem(input.systemId);
    const trkorr = input.transportNumber.toUpperCase();

    debugLog(`listing objects in ${trkorr} on ${system.id}`);

    const raw = await adtGet<unknown>(system, `/sap/bc/adt/cts/transportrequests/${trkorr}`);
    const objects = extractObjectsFromXml(raw);

    return {
      transportNumber: trkorr,
      system: system.id,
      objectCount: objects.length,
      objects,
    };
  },
};
