import { describe, it, expect } from "vitest";
import {
  assertSelectOnly,
  assertCustomerNamespace,
  assertPackageAllowed,
  assertWriteEnabled,
  assertDeleteEnabled,
  assertRoleAllows,
} from "../src/safety.js";

describe("assertSelectOnly", () => {
  it("allows a plain SELECT", () => {
    expect(() => assertSelectOnly("SELECT * FROM mara")).not.toThrow();
  });

  it("allows a WITH common table expression", () => {
    expect(() => assertSelectOnly("WITH +c AS ( SELECT a FROM t ) SELECT * FROM +c")).not.toThrow();
  });

  it("allows identifiers that merely contain a DML word (e.g. delete_flag)", () => {
    expect(() => assertSelectOnly("SELECT mandt FROM t WHERE delete_flag = 'X'")).not.toThrow();
  });

  it("rejects a statement that does not start with SELECT/WITH", () => {
    expect(() => assertSelectOnly("UPDATE mara SET x = 1")).toThrow(/read-only/i);
  });

  it("rejects DML keywords appearing as standalone words", () => {
    expect(() => assertSelectOnly("SELECT * FROM t; DELETE FROM t")).toThrow(/read-only/i);
    expect(() => assertSelectOnly("SELECT * FROM t UPSERT t")).toThrow(/read-only/i);
  });
});

describe("assertCustomerNamespace", () => {
  it("accepts names in the customer namespace", () => {
    expect(() => assertCustomerNamespace("ZFOO", ["Z", "Y"])).not.toThrow();
    expect(() => assertCustomerNamespace("yfoo", ["Z", "Y"])).not.toThrow(); // case-insensitive
  });

  it("rejects names outside the customer namespace", () => {
    expect(() => assertCustomerNamespace("AFOO", ["Z", "Y"])).toThrow(/customer namespace/i);
  });
});

describe("assertPackageAllowed", () => {
  it("allows customer packages", () => {
    expect(() => assertPackageAllowed("ZCUST")).not.toThrow();
  });

  it("blocks SAP-owned package prefixes (default BLOCKED_PACKAGES=SAP,SHD)", () => {
    expect(() => assertPackageAllowed("SAP_BASIS")).toThrow(/blocked/i);
    expect(() => assertPackageAllowed("shd0")).toThrow(/blocked/i); // case-insensitive
  });
});

describe("write/delete guards (default env: both disabled)", () => {
  it("assertWriteEnabled throws when ALLOW_WRITE is not set", () => {
    expect(() => assertWriteEnabled()).toThrow(/ALLOW_WRITE=true/);
  });

  it("assertDeleteEnabled throws when ALLOW_DELETE is not set", () => {
    expect(() => assertDeleteEnabled()).toThrow(/ALLOW_DELETE=true/);
  });
});

describe("assertRoleAllows (default role: admin)", () => {
  it("permits all capabilities for the default admin role", () => {
    expect(() => assertRoleAllows("write")).not.toThrow();
    expect(() => assertRoleAllows("delete")).not.toThrow();
    expect(() => assertRoleAllows("execute")).not.toThrow();
  });
});
