import { mapStatus, mapType, mapProgramId } from "./status-codes.js";

/**
 * Business-facing transport summary (list view).
 */
export interface TransportSummary {
  transportNumber: string;   // TRKORR
  description: string;       // AS4TEXT
  type: string;              // CATEGORY (mapped)
  status: string;            // TRSTATUS (mapped)
  owner: string;             // AS4USER
  targetSystem: string;      // TARSYSTEM
  createdAt: string;         // AS4DATE + AS4TIME → ISO 8601
}

/**
 * Business-facing transport detail (includes tasks and objects).
 */
export interface TransportDetail extends TransportSummary {
  tasks: TransportTask[];
  objects: TransportObject[];
  objectCount: number;
}

export interface TransportTask {
  taskNumber: string;
  description: string;
  owner: string;
  status: string;
}

export interface TransportObject {
  objectType: string;   // OBJECT (e.g. PROG, TABL, FUGR)
  objectName: string;   // OBJ_NAME
  programId: string;    // PGMID (mapped)
}

export interface ImportQueueEntry {
  transportNumber: string;
  description: string;
  owner: string;
  targetSystem: string;
  queuedAt: string;
}

/**
 * Maps a raw SAP ADT transport record to a business-friendly summary.
 * Handles both OData JSON (d.results) and XML-parsed objects (tm: namespace attributes).
 */
export function mapTransportSummary(raw: Record<string, unknown>): TransportSummary {
  // XML format from /sap/bc/adt/cts/transportrequests (tm: namespace attributes)
  if ("tm:number" in raw || "tm:desc" in raw) {
    const status = String(raw["tm:status"] ?? "");
    return {
      transportNumber: String(raw["tm:number"] ?? ""),
      description: String(raw["tm:desc"] ?? ""),
      type: String(raw["_category"] ?? "Workbench"),
      status: status === "D" ? "Modifiable" : status === "L" ? "Released" : status,
      owner: String(raw["tm:owner"] ?? ""),
      targetSystem: String(raw["tm:target"] ?? raw["adtcore:responsible"] ?? ""),
      createdAt: String(raw["adtcore:changedAt"] ?? ""),
    };
  }
  // OData JSON fallback (legacy)
  const date = String(raw["AS4DATE"] ?? raw["as4date"] ?? "");
  const time = String(raw["AS4TIME"] ?? raw["as4time"] ?? "");
  return {
    transportNumber: String(raw["TRKORR"] ?? raw["trkorr"] ?? raw["Name"] ?? ""),
    description: String(raw["AS4TEXT"] ?? raw["as4text"] ?? raw["Description"] ?? ""),
    type: mapType(String(raw["CATEGORY"] ?? raw["category"] ?? raw["Category"] ?? "")),
    status: mapStatus(String(raw["TRSTATUS"] ?? raw["trstatus"] ?? raw["Status"] ?? "")),
    owner: String(raw["AS4USER"] ?? raw["as4user"] ?? raw["Owner"] ?? ""),
    targetSystem: String(raw["TARSYSTEM"] ?? raw["tarsystem"] ?? raw["TargetSystem"] ?? ""),
    createdAt: parseSapDateTime(date, time),
  };
}

/**
 * Extracts all transport requests from the parsed XML of
 * GET /sap/bc/adt/cts/transportrequests response.
 */
export function extractTransportRequestsFromXml(
  parsed: unknown,
  ownerFilter?: string,
  statusFilter?: string
): TransportSummary[] {
  const root = (parsed as Record<string, unknown>)?.["tm:root"];
  if (!root || typeof root !== "object") return [];

  const results: TransportSummary[] = [];

  for (const sectionKey of ["tm:workbench", "tm:customizing"]) {
    const section = (root as Record<string, unknown>)[sectionKey];
    if (!section || typeof section !== "object") continue;
    const category = sectionKey === "tm:workbench" ? "Workbench" : "Customizing";

    for (const statusKey of ["tm:modifiable", "tm:released"]) {
      if (statusFilter === "Modifiable" && statusKey !== "tm:modifiable") continue;
      if (statusFilter === "Released" && statusKey !== "tm:released") continue;

      const statusSection = (section as Record<string, unknown>)[statusKey];
      if (!statusSection || typeof statusSection !== "object") continue;

      const requests = (statusSection as Record<string, unknown>)["tm:request"];
      const reqArray = Array.isArray(requests) ? requests : requests ? [requests] : [];

      for (const req of reqArray) {
        const r = req as Record<string, unknown>;
        if (ownerFilter && String(r["tm:owner"] ?? "").toUpperCase() !== ownerFilter.toUpperCase()) continue;
        results.push(mapTransportSummary({ ...r, _category: category }));
      }
    }
  }

  return results;
}

/**
 * Extracts tasks from a single transport's XML response.
 */
export function extractTasksFromXml(parsed: unknown): TransportTask[] {
  const root = (parsed as Record<string, unknown>)?.["tm:root"];
  if (!root || typeof root !== "object") return [];

  const tasks: TransportTask[] = [];

  for (const sectionKey of ["tm:workbench", "tm:customizing"]) {
    const section = (root as Record<string, unknown>)[sectionKey];
    if (!section || typeof section !== "object") continue;

    for (const statusKey of ["tm:modifiable", "tm:released"]) {
      const statusSection = (section as Record<string, unknown>)[statusKey];
      if (!statusSection || typeof statusSection !== "object") continue;

      const requests = (statusSection as Record<string, unknown>)["tm:request"];
      const reqArray = Array.isArray(requests) ? requests : requests ? [requests] : [];

      for (const req of reqArray) {
        const r = req as Record<string, unknown>;
        const taskRaw = r["tm:task"];
        const taskArr = Array.isArray(taskRaw) ? taskRaw : taskRaw ? [taskRaw] : [];
        for (const t of taskArr) {
          const task = t as Record<string, unknown>;
          const status = String(task["tm:status"] ?? "");
          tasks.push({
            taskNumber: String(task["tm:number"] ?? ""),
            description: String(task["tm:desc"] ?? ""),
            owner: String(task["tm:owner"] ?? ""),
            status: status === "D" ? "Modifiable" : status === "L" ? "Released" : status,
          });
        }
      }
    }
  }

  return tasks;
}

export function mapTransportTask(raw: Record<string, unknown>): TransportTask {
  const date = String(raw["AS4DATE"] ?? "");
  const time = String(raw["AS4TIME"] ?? "");
  return {
    taskNumber: String(raw["TRKORR"] ?? raw["Name"] ?? ""),
    description: String(raw["AS4TEXT"] ?? raw["Description"] ?? ""),
    owner: String(raw["AS4USER"] ?? raw["Owner"] ?? ""),
    status: mapStatus(String(raw["TRSTATUS"] ?? raw["Status"] ?? "")),
  };
}

export function mapTransportObject(raw: Record<string, unknown>): TransportObject {
  return {
    objectType: String(raw["OBJECT"] ?? raw["Type"] ?? ""),
    objectName: String(raw["OBJ_NAME"] ?? raw["Name"] ?? ""),
    programId: mapProgramId(String(raw["PGMID"] ?? raw["ProgramId"] ?? "")),
  };
}

/**
 * Extracts ABAP objects from the parsed XML of a single transport request.
 * Objects appear as tm:abap_object elements nested under tm:task elements.
 */
export function extractObjectsFromXml(parsed: unknown): TransportObject[] {
  const root = (parsed as Record<string, unknown>)?.["tm:root"];
  if (!root || typeof root !== "object") return [];

  const objects: TransportObject[] = [];

  function collectObjects(node: unknown): void {
    if (!node || typeof node !== "object") return;
    const n = node as Record<string, unknown>;

    const abapObjects = n["tm:abap_object"];
    const arr = Array.isArray(abapObjects) ? abapObjects : abapObjects ? [abapObjects] : [];
    for (const obj of arr) {
      const o = obj as Record<string, unknown>;
      objects.push({
        objectType: String(o["tm:type"] ?? ""),
        objectName: String(o["tm:name"] ?? "").trim(),
        programId: mapProgramId(String(o["tm:pgmid"] ?? "")),
      });
    }

    for (const key of Object.keys(n)) {
      if (key !== "tm:abap_object") collectObjects(n[key]);
    }
  }

  collectObjects(root);
  return objects;
}

export function mapImportQueueEntry(raw: Record<string, unknown>): ImportQueueEntry {
  const date = String(raw["AS4DATE"] ?? "");
  const time = String(raw["AS4TIME"] ?? "");
  return {
    transportNumber: String(raw["TRKORR"] ?? raw["Name"] ?? ""),
    description: String(raw["AS4TEXT"] ?? raw["Description"] ?? ""),
    owner: String(raw["AS4USER"] ?? raw["Owner"] ?? ""),
    targetSystem: String(raw["TARSYSTEM"] ?? raw["TargetSystem"] ?? ""),
    queuedAt: parseSapDateTime(date, time),
  };
}

/**
 * Converts SAP date (YYYYMMDD) + time (HHMMSS) to ISO 8601.
 * Returns empty string if both are missing or zero-padded defaults.
 */
export function parseSapDateTime(date: string, time: string): string {
  if (!date || date === "00000000") return "";
  const y = date.slice(0, 4);
  const mo = date.slice(4, 6);
  const d = date.slice(6, 8);
  const hh = time.slice(0, 2) || "00";
  const mm = time.slice(2, 4) || "00";
  const ss = time.slice(4, 6) || "00";
  return `${y}-${mo}-${d}T${hh}:${mm}:${ss}Z`;
}
