import { describe, it, expect } from "vitest";
import { z } from "zod";
import { toJsonSchema } from "../src/helpers/json-schema.js";

describe("toJsonSchema", () => {
  it("keeps descriptions set after .optional()", () => {
    const schema = z.object({
      transport: z.string().optional().describe("Transport request"),
    });
    const json = toJsonSchema(schema) as any;
    expect(json.properties.transport).toEqual({ type: "string", description: "Transport request" });
    expect(json.required).toBeUndefined();
  });

  it("keeps descriptions set after .default().optional()", () => {
    const schema = z.object({
      activate: z.boolean().default(true).optional().describe("Activate after writing"),
    });
    const json = toJsonSchema(schema) as any;
    expect(json.properties.activate).toEqual({ type: "boolean", description: "Activate after writing" });
  });

  it("prefers the wrapper description over the inner one", () => {
    const schema = z.object({
      f: z.string().describe("inner").optional().describe("outer"),
    });
    const json = toJsonSchema(schema) as any;
    expect(json.properties.f.description).toBe("outer");
  });

  it("converts z.record to a plain object schema with description", () => {
    const schema = z.object({
      args: z.record(z.unknown()).describe("Tool arguments"),
    });
    const json = toJsonSchema(schema) as any;
    expect(json.properties.args).toEqual({ type: "object", description: "Tool arguments" });
    expect(json.required).toEqual(["args"]);
  });

  it("unwraps top-level .refine() (ZodEffects) to the object schema", () => {
    const schema = z.object({
      a: z.string().optional(),
      b: z.string().optional(),
    }).refine((d) => !!(d.a ?? d.b), { message: "either a or b" });
    const json = toJsonSchema(schema) as any;
    expect(json.type).toBe("object");
    expect(Object.keys(json.properties)).toEqual(["a", "b"]);
  });

  it("marks only non-optional, non-default fields as required", () => {
    const schema = z.object({
      must: z.string(),
      opt: z.number().optional(),
      def: z.boolean().default(false),
    });
    const json = toJsonSchema(schema) as any;
    expect(json.required).toEqual(["must"]);
  });
});
