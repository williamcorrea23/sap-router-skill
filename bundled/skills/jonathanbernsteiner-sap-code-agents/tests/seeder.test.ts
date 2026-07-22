/**
 * Seeder smoke test: parses the shipped fixtures exactly like scripts/seed.ts
 * does (same extractWorkspace call) and checks the invariants the seed run
 * depends on. No database required.
 */
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { extractWorkspace } from "../lib/parser/extract";
import { RULES, runValidator } from "../lib/validators";

const FIXTURES = join(__dirname, "..", "fixtures");

function loadFixtures() {
  const paths = execFileSync("find", [join(FIXTURES, "src"), "-type", "f"], { encoding: "utf8" })
    .split("\n")
    .filter(Boolean)
    .sort();
  return extractWorkspace(
    paths.map((p) => ({ path: p.replace(`${FIXTURES}/src/`, ""), contents: readFileSync(p, "utf8") }))
  );
}

describe("fixture seeding smoke test", () => {
  const result = loadFixtures();
  const manifest = JSON.parse(readFileSync(join(FIXTURES, "manifest.json"), "utf8"));

  it("parses all fixture objects without failures", () => {
    expect(result.objects).toHaveLength(13);
    expect(result.objects.filter((o) => o.parseStatus !== "ok")).toEqual([]);
    expect(result.unattachedFiles).toEqual([]);
  });

  it("covers every manifest object exactly", () => {
    const parsed = new Set(result.objects.map((o) => o.name));
    const listed = new Set<string>(manifest.objects.map((o: { name: string }) => o.name));
    expect(parsed).toEqual(listed);
  });

  it("extracts the goods-movement call chain (RFC stub → service → BAPI)", () => {
    const stub = result.objects.find((o) => o.name === "ZCL_GM_SCALE_RFC_STUB")!;
    expect(stub.calls.some((c) => c.kind === "class" && c.target === "ZCL_GM_MOVEMENT_SERVICE")).toBe(true);
    const service = result.objects.find((o) => o.name === "ZCL_GM_MOVEMENT_SERVICE")!;
    expect(service.calls.some((c) => c.kind === "function" && c.target === "BAPI_GOODSMVT_CREATE")).toBe(true);
  });

  it("extracts table accesses with evidence lines for the planted incompatibilities", () => {
    const byObject = new Map(result.objects.map((o) => [o.name, o.tableAccesses]));
    const daily = byObject.get("ZGM_DAILY_MOVEMENT_REPORT")!;
    expect(daily.some((t) => t.op === "select" && t.table === "MKPF")).toBe(true);
    expect(daily.some((t) => t.op === "select" && t.table === "MSEG")).toBe(true);
    const pricing = byObject.get("ZGM_PRICING_MARGIN_REPORT")!;
    expect(pricing.some((t) => t.table === "KONV")).toBe(true);
    expect(pricing.some((t) => t.table === "VBUK")).toBe(true);
    const aging = byObject.get("ZFI_OPEN_ITEMS_AGING")!;
    expect(aging.map((t) => t.table).sort()).toEqual(["BSAD", "BSID"]);
    for (const t of [...daily, ...pricing, ...aging]) {
      expect(t.evidence.length).toBeGreaterThan(0);
      expect(t.line).toBeGreaterThan(0);
    }
  });

  it("the planted MB01 batch program trips the mb-transactions-migo validator", () => {
    const legacy = result.objects.find((o) => o.name === "ZGM_LEGACY_MB01_BATCH")!;
    const rule = RULES.find((r) => r.id === "mb-transactions-migo")!;
    const matches = runValidator(rule, legacy.source);
    expect(matches.map((m) => m.detail).sort()).toEqual(["transaction MB01", "transaction MB31"]);
  });

  it("usage.csv is deterministic: dead objects 0, live objects positive, no unknown names", () => {
    const lines = readFileSync(join(FIXTURES, "usage.csv"), "utf8").trim().split("\n").slice(1);
    const byName = new Map(lines.map((l) => [l.split(",")[0], Number(l.split(",")[1])]));
    const dead = manifest.objects.filter((o: { dead: boolean }) => o.dead).map((o: { name: string }) => o.name);
    expect(dead.length).toBeGreaterThanOrEqual(2);
    for (const d of dead) expect(byName.get(d)).toBe(0);
    const objectNames = new Set(result.objects.map((o) => o.name));
    for (const [name, count] of byName) {
      expect(objectNames.has(name)).toBe(true);
      if (!dead.includes(name)) expect(count).toBeGreaterThan(0);
    }
  });
});
