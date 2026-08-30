// Minimal .env loader mirroring load_dotenv() in scripts/apim_client.py:
// existing environment variables always win, so shell exports override the file.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

export function loadDotEnv(file = path.join(ROOT, ".env")) {
  if (!fs.existsSync(file)) {
    return 0;
  }
  let loaded = 0;
  for (const rawLine of fs.readFileSync(file, "utf8").split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#") || !line.includes("=")) {
      continue;
    }
    const index = line.indexOf("=");
    const key = line.slice(0, index).trim();
    const value = line.slice(index + 1).trim().replace(/^["']|["']$/g, "");
    if (key && process.env[key] === undefined) {
      process.env[key] = value;
      loaded += 1;
    }
  }
  return loaded;
}
