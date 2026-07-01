import { z } from "zod";
import { getSystems } from "../config/systems.js";

export const SystemInfoInputSchema = z.object({});

export interface SystemInfoResult {
  configuredSystems: Array<{
    id: string;
    hostname: string;
    client: string;
    language: string;
    isDefault: boolean;
  }>;
  defaultSystem: string;
  totalCount: number;
}

export const systemInfoTool = {
  name: "transport_list_systems",
  description:
    "Lists all SAP systems configured for this MCP server. " +
    "Use this first to discover valid systemId values when working with multi-system setups. " +
    "Safe to call any time — reads from local config only, no SAP API call.",

  async handler(_rawInput: unknown): Promise<SystemInfoResult> {
    const systems = getSystems();
    const def = systems.find((s) => s.isDefault) ?? systems[0];

    return {
      configuredSystems: systems.map((s) => ({
        id: s.id,
        hostname: s.hostname,
        client: s.client,
        language: s.language,
        isDefault: s.isDefault,
      })),
      defaultSystem: def?.id ?? "(none)",
      totalCount: systems.length,
    };
  },
};
