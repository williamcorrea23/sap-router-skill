import { defineConfig } from "vitest/config";
import * as fs from "fs";
import * as path from "path";

/**
 * The source uses NodeNext module resolution, so every relative import carries
 * a `.js` extension even though the file on disk is `.ts` (e.g.
 * `import { cfg } from "./config.js"`). Vite/esbuild treats the `.js` as an
 * explicit extension and does not try `.ts`, so we remap it here for tests.
 */
const jsToTsResolver = {
  name: "js-to-ts-resolver",
  enforce: "pre" as const,
  resolveId(source: string, importer?: string) {
    if (importer && source.startsWith(".") && source.endsWith(".js")) {
      const candidate = path.resolve(path.dirname(importer), source.replace(/\.js$/, ".ts"));
      if (fs.existsSync(candidate)) return candidate;
    }
    return null;
  },
};

export default defineConfig({
  plugins: [jsToTsResolver],
  test: {
    include: ["test/**/*.test.ts"],
    // Pin the environment config.ts reads so tests are deterministic regardless
    // of the developer's local `.env` (dotenv does not override already-set
    // vars, so these win). Dummy credentials keep config.ts from exiting on the
    // missing-SAP_URL/USER/PASSWORD check; the safety flags lock the guards to
    // their default-off state.
    env: {
      SAP_URL: "https://test-system.example.com:44300",
      SAP_USER: "TESTUSER",
      SAP_PASSWORD: "test-password",
      ALLOW_WRITE: "false",
      ALLOW_DELETE: "false",
      ALLOW_EXECUTE: "false",
      BLOCKED_PACKAGES: "SAP,SHD",
    },
  },
});
