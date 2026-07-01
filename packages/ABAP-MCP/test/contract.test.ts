import { describe, it, expect } from "vitest";
import { buildContract, renderContract } from "../src/helpers/contract.js";

const CLASS_SOURCE = `CLASS zcl_demo DEFINITION PUBLIC INHERITING FROM zcl_base FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_serializable.
    METHODS greet IMPORTING iv_name TYPE string RETURNING VALUE(rv) TYPE string.
    CLASS-METHODS factory RETURNING VALUE(ro) TYPE REF TO zcl_demo.
    CONSTANTS c_max TYPE i VALUE 10.
  PROTECTED SECTION.
    METHODS hidden_protected.
  PRIVATE SECTION.
    DATA mv_secret TYPE string.
    METHODS hidden_private.
ENDCLASS.

CLASS zcl_demo IMPLEMENTATION.
  METHOD greet.
    rv = iv_name.
  ENDMETHOD.
ENDCLASS.`;

const INTERFACE_SOURCE = `INTERFACE zif_demo PUBLIC.
  METHODS run IMPORTING iv_x TYPE i.
  TYPES ty_tab TYPE STANDARD TABLE OF string WITH EMPTY KEY.
ENDINTERFACE.`;

describe("buildContract — class", () => {
  const c = buildContract(CLASS_SOURCE);

  it("identifies the class name and kind", () => {
    expect(c.kind).toBe("class");
    expect(c.name).toBe("zcl_demo");
  });

  it("includes only public-section members", () => {
    const joined = c.members.join(" | ");
    expect(joined).toMatch(/METHODS greet/i);
    expect(joined).toMatch(/CLASS-METHODS factory/i);
    expect(joined).toMatch(/CONSTANTS c_max/i);
    expect(joined).toMatch(/INTERFACES if_serializable/i);
  });

  it("omits protected and private members", () => {
    const joined = c.members.join(" | ");
    expect(joined).not.toMatch(/hidden_protected/i);
    expect(joined).not.toMatch(/hidden_private/i);
    expect(joined).not.toMatch(/mv_secret/i);
  });

  it("captures the superclass", () => {
    expect(c.members.join(" | ")).toMatch(/INHERITING FROM zcl_base/i);
  });

  it("renders much smaller than the full source", () => {
    expect(renderContract(c).length).toBeLessThan(CLASS_SOURCE.length);
  });
});

describe("buildContract — interface", () => {
  it("treats the whole interface body as public", () => {
    const c = buildContract(INTERFACE_SOURCE);
    expect(c.kind).toBe("interface");
    expect(c.name).toBe("zif_demo");
    const joined = c.members.join(" | ");
    expect(joined).toMatch(/METHODS run/i);
    expect(joined).toMatch(/TYPES ty_tab/i);
  });
});

describe("buildContract — fallback", () => {
  it("returns unknown kind for a plain report", () => {
    const c = buildContract("REPORT zdemo.\nWRITE 'hi'.", "zdemo");
    expect(c.kind).toBe("unknown");
    expect(c.name).toBe("zdemo");
    expect(renderContract(c)).toMatch(/no class\/interface contract/i);
  });
});
