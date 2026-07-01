import { describe, it, expect } from "vitest";
import {
  parseMethods,
  findMethod,
  listMethodNames,
  replaceMethodBody,
  extractMethod,
  MethodNotFoundError,
} from "../src/helpers/method-splice.js";

const CLASS_SOURCE = `CLASS zcl_demo DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    METHODS greet IMPORTING iv_name TYPE string RETURNING VALUE(rv) TYPE string.
    METHODS add IMPORTING a TYPE i b TYPE i RETURNING VALUE(r) TYPE i.
ENDCLASS.

CLASS zcl_demo IMPLEMENTATION.
  METHOD greet.
    rv = |Hello { iv_name }|.
  ENDMETHOD.

  METHOD add.
    r = a + b.
  ENDMETHOD.
ENDCLASS.`;

describe("parseMethods", () => {
  it("finds all implementation methods (not declarations)", () => {
    const blocks = parseMethods(CLASS_SOURCE);
    expect(blocks.map((b) => b.name)).toEqual(["greet", "add"]);
  });

  it("does not match METHODS / CLASS-METHODS declarations", () => {
    expect(listMethodNames("    METHODS foo.\n    CLASS-METHODS bar.")).toEqual([]);
  });

  it("captures the body between header and ENDMETHOD", () => {
    const greet = findMethod(CLASS_SOURCE, "greet")!;
    expect(greet.body).toContain("rv = |Hello { iv_name }|.");
    expect(greet.body).not.toContain("ENDMETHOD");
  });
});

describe("findMethod / extractMethod", () => {
  it("is case-insensitive", () => {
    expect(findMethod(CLASS_SOURCE, "GREET")?.name).toBe("greet");
  });

  it("extractMethod throws MethodNotFoundError with available names", () => {
    expect(() => extractMethod(CLASS_SOURCE, "nope")).toThrow(MethodNotFoundError);
    try {
      extractMethod(CLASS_SOURCE, "nope");
    } catch (e) {
      expect((e as Error).message).toContain("greet");
      expect((e as Error).message).toContain("add");
    }
  });
});

describe("replaceMethodBody", () => {
  it("replaces only the target method body and preserves the rest", () => {
    const out = replaceMethodBody(CLASS_SOURCE, "add", "    r = a * b.");
    expect(out).toContain("r = a * b.");
    expect(out).not.toContain("r = a + b.");
    // greet untouched
    expect(out).toContain("rv = |Hello { iv_name }|.");
    // structure intact: still two ENDMETHOD and the declaration section
    expect((out.match(/ENDMETHOD\./g) ?? []).length).toBe(2);
    expect(out).toContain("CLASS zcl_demo DEFINITION");
  });

  it("tolerates a body that includes METHOD/ENDMETHOD keywords", () => {
    const out = replaceMethodBody(CLASS_SOURCE, "add", "METHOD add.\n    r = a - b.\n  ENDMETHOD.");
    expect(out).toContain("r = a - b.");
    // no double-wrapping
    expect((out.match(/METHOD add\./g) ?? []).length).toBe(1);
    expect((out.match(/ENDMETHOD\./g) ?? []).length).toBe(2);
  });

  it("throws when the method does not exist", () => {
    expect(() => replaceMethodBody(CLASS_SOURCE, "missing", "x = 1.")).toThrow(MethodNotFoundError);
  });

  it("keeps the result re-parseable", () => {
    const out = replaceMethodBody(CLASS_SOURCE, "greet", "    rv = iv_name.");
    expect(listMethodNames(out)).toEqual(["greet", "add"]);
  });
});
