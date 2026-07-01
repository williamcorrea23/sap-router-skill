import { z } from "zod";
import { getSystem } from "../config/systems.js";
import { adtGet, debugLog } from "../lib/adt-client.js";
import {
  extractTransportRequestsFromXml,
  extractTasksFromXml,
  extractObjectsFromXml,
  type TransportDetail,
} from "../lib/transport-mapper.js";

export const TransportGetInputSchema = z.object({
  transportNumber: z
    .string()
    .regex(/^[A-Z][A-Z0-9]{2}K\d{6}$/, "Transport number format: 3-char system ID + K + 6 digits (e.g. GW1K900528)")
    .describe("SAP transport request number (e.g. DEVK900123)."),
  systemId: z
    .string()
    .optional()
    .describe("Logical SAP system ID (e.g. DEV, QA, PRD). Omit to use the default system."),
});

export type TransportGetInput = z.infer<typeof TransportGetInputSchema>;

export const transportGetTool = {
  name: "transport_get_request",
  description:
    "Fetches full details of a SAP transport request: description, status, owner, target system, " +
    "all tasks, and all included ABAP objects. " +
    "Call this before releasing to confirm the transport contains the expected objects. " +
    "Safe to call any time — read only.",

  async handler(rawInput: unknown): Promise<TransportDetail> {
    const input = TransportGetInputSchema.parse(rawInput);
    const system = getSystem(input.systemId);
    const trkorr = input.transportNumber.toUpperCase();

    debugLog(`fetching transport ${trkorr} on ${system.id}`);

    // Single call returns header + tasks in the XML response
    const raw = await adtGet<unknown>(system, `/sap/bc/adt/cts/transportrequests/${trkorr}`);

    const allTransports = extractTransportRequestsFromXml(raw);
    const summary = allTransports[0] ?? {
      transportNumber: trkorr,
      description: "",
      type: "Workbench",
      status: "Unknown",
      owner: "",
      targetSystem: "",
      createdAt: "",
    };

    const tasks = extractTasksFromXml(raw);
    const objects = extractObjectsFromXml(raw);

    return {
      ...summary,
      tasks,
      objects,
      objectCount: objects.length,
    };
  },
};
