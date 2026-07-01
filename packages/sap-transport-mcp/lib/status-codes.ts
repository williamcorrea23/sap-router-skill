/** SAP TRSTATUS field → business label */
export const TRANSPORT_STATUS: Record<string, string> = {
  D: "Modifiable",
  L: "Released",
  R: "Release Started",
  N: "Locked",
  A: "Actively being released",
};

/** SAP CATEGORY / TRFUNCTION field → transport type label */
export const TRANSPORT_TYPE: Record<string, string> = {
  K: "Workbench",
  W: "Customizing",
  C: "Transport of Copies",
  T: "Tasks",
  G: "Workbench (for repairs)",
  R: "Repair",
  X: "Unclassified",
};

/** SAP PGMID field → human-readable program ID */
export const PROGRAM_ID: Record<string, string> = {
  R3TR: "Repository Object",
  LIMU: "Include Object",
  CORR: "Correction",
};

export function mapStatus(code: string): string {
  return TRANSPORT_STATUS[code] ?? `Unknown (${code})`;
}

export function mapType(code: string): string {
  return TRANSPORT_TYPE[code] ?? `Unknown (${code})`;
}

export function mapProgramId(code: string): string {
  return PROGRAM_ID[code] ?? code;
}
