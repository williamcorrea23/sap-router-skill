import { env } from "./env.js";

export interface SapSystem {
  id: string;         // logical name: "DEV", "QA", "PRD"
  hostname: string;
  sysnr: string;      // 2-digit: "00"
  client: string;     // 3-digit: "100"
  language: string;   // 2-char ISO: "EN"
  isDefault: boolean;
}

let _systems: SapSystem[] | null = null;

function buildSystems(): SapSystem[] {
  // Multi-system mode: SYSTEMS_CONFIG overrides all individual SAP_* vars
  if (env.SYSTEMS_CONFIG) {
    try {
      const parsed = JSON.parse(env.SYSTEMS_CONFIG) as unknown[];
      if (!Array.isArray(parsed) || parsed.length === 0) {
        throw new Error("SYSTEMS_CONFIG must be a non-empty JSON array");
      }
      return parsed.map((s, i) => {
        const sys = s as Record<string, unknown>;
        return {
          id: String(sys["id"] ?? `SYSTEM_${i}`),
          hostname: String(sys["hostname"] ?? ""),
          sysnr: String(sys["sysnr"] ?? "00"),
          client: String(sys["client"] ?? "100"),
          language: String(sys["language"] ?? "EN"),
          isDefault: Boolean(sys["isDefault"] ?? i === 0),
        };
      });
    } catch (e) {
      throw new Error(`Failed to parse SYSTEMS_CONFIG: ${e instanceof Error ? e.message : String(e)}`);
    }
  }

  // Single-system mode: use individual SAP_* env vars
  return [
    {
      id: env.SAP_SYSTEM_ID,
      hostname: env.SAP_HOSTNAME,
      sysnr: env.SAP_SYSNR,
      client: env.SAP_CLIENT,
      language: env.SAP_LANGUAGE,
      isDefault: true,
    },
  ];
}

export function getSystems(): SapSystem[] {
  if (!_systems) _systems = buildSystems();
  return _systems;
}

export function getSystem(systemId?: string): SapSystem {
  const systems = getSystems();
  if (!systemId) {
    const def = systems.find((s) => s.isDefault) ?? systems[0];
    if (!def) throw new Error("No SAP systems configured");
    return def;
  }
  const found = systems.find((s) => s.id.toUpperCase() === systemId.toUpperCase());
  if (!found) {
    const known = systems.map((s) => s.id).join(", ");
    throw new Error(`Unknown systemId "${systemId}". Configured systems: ${known}`);
  }
  return found;
}

/**
 * Builds the base HTTPS URL for a given system.
 * On-prem: port = 8000 + parseInt(sysnr)  (e.g. sysnr=00 → port 8000)
 * Cloud/BTP: override with SAP_HTTPS_PORT=443
 */
export function systemBaseUrl(system: SapSystem): string {
  const port = env.SAP_HTTPS_PORT ?? (8000 + parseInt(system.sysnr, 10));
  return `https://${system.hostname}:${port}`;
}
