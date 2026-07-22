/**
 * Custom workspace names (connect-a-source): user input is normalized to the
 * same slug alphabet as URL-derived names — names are URL path segments
 * under /w/… and must stay globally addressable.
 */
import { describe, expect, it } from "vitest";
import { normalizeWorkspaceName, workspaceNameForUrl } from "../lib/ingest/git";

describe("normalizeWorkspaceName", () => {
  it("lowercases and slugifies free-form input", () => {
    expect(normalizeWorkspaceName("My SAP Landscape (Prod)")).toEqual({
      ok: true,
      name: "my-sap-landscape-prod",
    });
  });

  it("keeps already-valid slugs unchanged", () => {
    expect(normalizeWorkspaceName("erp_core-2024")).toEqual({ ok: true, name: "erp_core-2024" });
  });

  it("trims leading/trailing separators", () => {
    expect(normalizeWorkspaceName("  --team-a--  ")).toEqual({ ok: true, name: "team-a" });
  });

  it("rejects input without letters or numbers", () => {
    expect(normalizeWorkspaceName("///---")).toMatchObject({ ok: false });
    expect(normalizeWorkspaceName("   ")).toMatchObject({ ok: false });
  });

  it("rejects names over 40 characters", () => {
    expect(normalizeWorkspaceName("x".repeat(41))).toMatchObject({ ok: false });
    expect(normalizeWorkspaceName("x".repeat(40))).toEqual({ ok: true, name: "x".repeat(40) });
  });

  it("normalizes to the same alphabet as URL-derived names", () => {
    const derived = workspaceNameForUrl("https://github.com/abap2xlsx/abap2xlsx.git");
    expect(derived).toBe("abap2xlsx");
    expect(normalizeWorkspaceName(derived)).toEqual({ ok: true, name: derived });
  });
});
