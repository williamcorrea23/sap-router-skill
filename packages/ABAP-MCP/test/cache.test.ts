import { describe, it, expect, beforeEach } from "vitest";
import {
  getObjectSourceCached,
  invalidateSource,
  clearSourceCache,
  sourceCacheSize,
} from "../src/cache.js";

/** Minimal fake ADTClient that counts getObjectSource calls. */
function makeClient() {
  let calls = 0;
  return {
    calls: () => calls,
    getObjectSource: async (_url: string) => {
      calls++;
      return `SOURCE v${calls}`;
    },
  } as any;
}

const URL = "/sap/bc/adt/oo/classes/zcl_x";

describe("source cache", () => {
  beforeEach(() => clearSourceCache());

  it("serves the second read from cache (one backend call)", async () => {
    const client = makeClient();
    const a = await getObjectSourceCached(client, `${URL}/source/main`);
    const b = await getObjectSourceCached(client, `${URL}/source/main`);
    expect(a).toBe(b);
    expect(client.calls()).toBe(1);
    expect(sourceCacheSize()).toBe(1);
  });

  it("normalizes the key with/without /source/main suffix", async () => {
    const client = makeClient();
    await getObjectSourceCached(client, `${URL}/source/main`);
    await getObjectSourceCached(client, URL);
    expect(client.calls()).toBe(1);
  });

  it("re-fetches after invalidation (write/delete path)", async () => {
    const client = makeClient();
    await getObjectSourceCached(client, URL);
    invalidateSource(URL);
    const after = await getObjectSourceCached(client, URL);
    expect(client.calls()).toBe(2);
    expect(after).toBe("SOURCE v2");
  });

  it("clearSourceCache empties the store", async () => {
    const client = makeClient();
    await getObjectSourceCached(client, URL);
    expect(sourceCacheSize()).toBe(1);
    clearSourceCache();
    expect(sourceCacheSize()).toBe(0);
  });
});
