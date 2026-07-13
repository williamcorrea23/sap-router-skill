#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";

const command = process.argv[2] || "model";

function run(cmd, args) {
  const result = spawnSync(cmd, args, { stdio: "inherit", shell: process.platform === "win32" });
  return result.status ?? 1;
}

if (!existsSync("package.json")) {
  console.error("No package.json in current directory.");
  process.exit(2);
}

if (command === "model" || command === "compile") {
  process.exit(run("npx", ["cds", "compile", "srv", "--to", "json"]));
}

if (command === "build") {
  process.exit(run("npx", ["cds", "build"]));
}

if (command === "test") {
  process.exit(run("npm", ["test", "--if-present"]));
}

console.error(`Unknown command: ${command}`);
process.exit(2);
