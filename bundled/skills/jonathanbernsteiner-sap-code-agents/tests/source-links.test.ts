import { describe, expect, it } from "vitest";
import { buildRepoFileUrl, isRepoUrl, repoDisplayName } from "../lib/source-links";

describe("source provenance links", () => {
  it("recognizes repo URLs vs fixture markers", () => {
    expect(isRepoUrl("https://github.com/abap2xlsx/abap2xlsx")).toBe(true);
    expect(isRepoUrl("fixtures")).toBe(false);
    expect(isRepoUrl("abapgit-cache")).toBe(false);
    expect(isRepoUrl(null)).toBe(false);
    expect(isRepoUrl("http://github.com/x/y")).toBe(false); // https only
  });

  it("renders compact display names without protocol or .git", () => {
    expect(repoDisplayName("https://github.com/abap2xlsx/abap2xlsx.git")).toBe(
      "github.com/abap2xlsx/abap2xlsx"
    );
    expect(repoDisplayName("https://github.com/abapGit/abapGit/")).toBe("github.com/abapGit/abapGit");
  });

  it("builds file links with branch and line anchor", () => {
    expect(
      buildRepoFileUrl("https://github.com/abap2xlsx/abap2xlsx", "main", "src/zcl_excel.clas.abap", 42)
    ).toBe("https://github.com/abap2xlsx/abap2xlsx/blob/main/src/zcl_excel.clas.abap#L42");
  });

  it("falls back to HEAD when the ingested branch is unknown", () => {
    expect(buildRepoFileUrl("https://github.com/o/r.git", null, "src/x.abap")).toBe(
      "https://github.com/o/r/blob/HEAD/src/x.abap"
    );
  });

  it("encodes branch and path segments", () => {
    expect(buildRepoFileUrl("https://github.com/o/r", "feature/x", "a b/c.abap", 7)).toBe(
      "https://github.com/o/r/blob/feature%2Fx/a%20b/c.abap#L7"
    );
  });

  it("never links fixture sources", () => {
    expect(buildRepoFileUrl("fixtures", "main", "src/x.abap", 1)).toBeNull();
    expect(buildRepoFileUrl("abapgit-cache", null, "src/x.abap", 1)).toBeNull();
    expect(buildRepoFileUrl(null, null, "src/x.abap", 1)).toBeNull();
  });
});
