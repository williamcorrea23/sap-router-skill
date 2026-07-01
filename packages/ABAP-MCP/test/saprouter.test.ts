import { describe, it, expect } from "vitest";
import { parseSapRouteString } from "../src/saprouter.js";

describe("parseSapRouteString", () => {
  it("parses a single router hop", () => {
    expect(parseSapRouteString("/H/saprout.example.com/S/3299")).toEqual([
      { host: "saprout.example.com", port: 3299, password: undefined },
    ]);
  });

  it("parses a router + target two-hop route", () => {
    const hops = parseSapRouteString(
      "/H/saprout.example.com/S/3299/H/target.example.com/S/44300",
    );
    expect(hops).toEqual([
      { host: "saprout.example.com", port: 3299, password: undefined },
      { host: "target.example.com", port: 44300, password: undefined },
    ]);
  });

  it("captures a hop password from the W token", () => {
    const [hop] = parseSapRouteString("/H/host/S/3299/W/secret");
    expect(hop.password).toBe("secret");
  });

  it("defaults the port to 3299 when S is omitted", () => {
    const [hop] = parseSapRouteString("/H/host");
    expect(hop.port).toBe(3299);
  });

  it("throws on an empty route string", () => {
    expect(() => parseSapRouteString("")).toThrow(/empty SAP route/i);
  });

  it("throws when a port (S) precedes any host (H)", () => {
    expect(() => parseSapRouteString("/S/3299")).toThrow(/'S' before 'H'/);
  });

  it("throws on an unknown token kind", () => {
    expect(() => parseSapRouteString("/X/foo/S/1")).toThrow(/unknown SAP route token/i);
  });
});
