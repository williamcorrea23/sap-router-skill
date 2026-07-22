/**
 * Object category derivation — GitHub-ingested systems have no fixture
 * manifest, so the category must come deterministically from the object
 * type/name already stored. Unknown types stay null (Uncategorized), never
 * guessed.
 */
import { describe, expect, it } from "vitest";
import { deriveCategory } from "../lib/ingest/pipeline";

describe("deriveCategory", () => {
  it("maps code objects to abap", () => {
    expect(deriveCategory("CLAS", "ZCL_GM_MOVEMENT_SERVICE")).toBe("abap");
    expect(deriveCategory("PROG", "ZGM_DAILY_MOVEMENT_REPORT")).toBe("abap");
    expect(deriveCategory("FUGR", "ZGM_API")).toBe("abap");
  });

  it("maps DDIC tables and interfaces", () => {
    expect(deriveCategory("TABL", "ZGM_SCALE_TICKET")).toBe("custom_table");
    expect(deriveCategory("INTF", "ZIF_GM_MOVEMENT_TYPES")).toBe("interface");
  });

  it("classifies user-exit includes (ZX*) and enhancement types as enhancement", () => {
    expect(deriveCategory("PROG", "ZXMBCU01")).toBe("enhancement");
    expect(deriveCategory("ENHO", "Z_ENH_IMPL")).toBe("enhancement");
    expect(deriveCategory("SMOD", "ZMOD01")).toBe("enhancement");
  });

  it("does not treat ordinary Z-programs as enhancements", () => {
    expect(deriveCategory("PROG", "ZGM_LEGACY_UPLOAD")).toBe("abap");
  });

  it("returns null for unknown types instead of guessing", () => {
    expect(deriveCategory("DTEL", "ZGM_TICKET_ID")).toBeNull();
    expect(deriveCategory("DOMA", "ZGM_DOMAIN")).toBeNull();
  });

  it("is case-insensitive on type and name", () => {
    expect(deriveCategory("prog", "zxmbcu01")).toBe("enhancement");
    expect(deriveCategory("tabl", "zgm_movement_log")).toBe("custom_table");
  });
});
