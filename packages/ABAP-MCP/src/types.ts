/**
 * ABAP MCP Server — Shared Type Definitions
 */

import type { z } from "zod";
import type { ADTClient } from "abap-adt-api";

export interface ToolDef {
  name: string;
  description: string;
  schema: z.ZodTypeAny;
  /**
   * Set to `false` for tools that never touch the SAP system (pure web/local
   * tools). The server then skips the ADT connection for this call and the
   * handler receives no usable client. Omitted = `true`.
   */
  requiresAdt?: boolean;
}

export type ToolResult = {
  content: { type: "text"; text: string }[];
  isError?: boolean;
};

export type ToolHandler = (
  client: ADTClient,
  args: Record<string, unknown>,
  extra?: any,
) => Promise<ToolResult>;
