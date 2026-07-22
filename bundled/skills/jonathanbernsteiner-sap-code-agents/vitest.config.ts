// Vitest configuration — runs the unit suite under tests/.
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["tests/**/*.test.ts"],
    exclude: ["node_modules/**", ".seed-cache/**", ".next/**", "design-guidance/**"],
  },
});
