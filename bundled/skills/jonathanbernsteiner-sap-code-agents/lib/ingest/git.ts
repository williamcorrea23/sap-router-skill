/**
 * B1/B2 — public-repo cloning for in-app ingestion.
 *
 * Uses isomorphic-git (pure JS smart-HTTP client) because Vercel functions
 * have no git binary. Guardrails: HTTPS URLs only, no embedded credentials,
 * a hard byte cap on the downloaded pack (so a pasted monorepo cannot fill
 * the function's disk), and a clone timeout.
 */
import * as git from "isomorphic-git";
import gitHttp from "isomorphic-git/http/node";
import * as fs from "node:fs";
import { join } from "node:path";

/** hard cap on bytes downloaded during clone (pack + refs) */
const MAX_CLONE_BYTES = 200 * 1024 * 1024;
const CLONE_TIMEOUT_MS = 180_000;

export function validateGitUrl(raw: string): { ok: true; url: string } | { ok: false; error: string } {
  let url: URL;
  try {
    url = new URL(raw.trim());
  } catch {
    return { ok: false, error: "Not a valid URL." };
  }
  if (url.protocol !== "https:") {
    return { ok: false, error: "Only public https:// git URLs are supported (no ssh, no http)." };
  }
  if (url.username || url.password) {
    return { ok: false, error: "URLs with embedded credentials are not accepted — public repositories only." };
  }
  if (!url.hostname.includes(".")) {
    return { ok: false, error: "Unrecognized host." };
  }
  return { ok: true, url: url.toString().replace(/\/+$/, "") };
}

/** Derive a workspace name from the repo URL, e.g. …/abap2xlsx.git → abap2xlsx */
export function workspaceNameForUrl(url: string): string {
  const base = url.replace(/\/+$/, "").replace(/\.git$/, "").split("/").pop() ?? "repo";
  const clean = base.toLowerCase().replace(/[^a-z0-9-_]/g, "-").replace(/^-+|-+$/g, "");
  return clean || "repo";
}

/**
 * Normalize a user-chosen workspace name to the same slug alphabet the
 * URL-derived names use (names are URL path segments under /w/…).
 */
export function normalizeWorkspaceName(
  raw: string
): { ok: true; name: string } | { ok: false; error: string } {
  const name = raw.trim().toLowerCase().replace(/[^a-z0-9-_]+/g, "-").replace(/^-+|-+$/g, "");
  if (!name) return { ok: false, error: "System name must contain letters or numbers." };
  if (name.length > 40) return { ok: false, error: "System name is limited to 40 characters." };
  return { ok: true, name };
}

/** Branch the (single-branch) clone in `dir` is on — recorded on the
 *  workspace so file citations can deep-link to blob/<branch>/… */
export async function clonedBranch(dir: string): Promise<string | null> {
  try {
    return (await git.currentBranch({ fs, dir, fullname: false })) ?? null;
  } catch {
    return null;
  }
}

class CloneCapError extends Error {}

/** http client wrapper that aborts once the byte cap is exceeded */
function cappedHttp(maxBytes: number): typeof gitHttp {
  let received = 0;
  return {
    async request(args: Parameters<typeof gitHttp.request>[0]) {
      const res = await gitHttp.request(args);
      if (!res.body) return res;
      const body = res.body as AsyncIterable<Uint8Array>;
      async function* counted() {
        for await (const chunk of body) {
          received += chunk.length;
          if (received > maxBytes) {
            throw new CloneCapError(
              `Repository too large: clone exceeded the ${Math.round(maxBytes / 1024 / 1024)} MB download cap.`
            );
          }
          yield chunk;
        }
      }
      return { ...res, body: counted() };
    },
  } as typeof gitHttp;
}

/**
 * Shallow single-branch clone of a public repository into `dir`.
 * Throws Error with a user-presentable message on failure.
 */
export async function cloneRepo(url: string, dir: string): Promise<void> {
  fs.mkdirSync(dir, { recursive: true });
  const timeout = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error("Clone timed out — the repository may be too large or the host unreachable.")), CLONE_TIMEOUT_MS)
  );
  try {
    await Promise.race([
      git.clone({
        fs,
        http: cappedHttp(MAX_CLONE_BYTES),
        dir,
        url,
        depth: 1,
        singleBranch: true,
        noTags: true,
      }),
      timeout,
    ]);
  } catch (e) {
    if (e instanceof CloneCapError) throw new Error(e.message);
    const msg = (e as Error).message ?? String(e);
    if (/404|not found/i.test(msg)) throw new Error("Repository not found — is the URL correct and the repository public?");
    if (/401|403|auth/i.test(msg)) throw new Error("Repository requires authentication — only public repositories are supported.");
    throw new Error(`Clone failed: ${msg.slice(0, 300)}`);
  }
}

/** Recursively list ABAP source files (.abap, .tabl.xml), skipping .git. */
export function listSourceFiles(dir: string): { abap: string[]; tabl: string[] } {
  const abap: string[] = [];
  const tabl: string[] = [];
  const entries = fs.readdirSync(dir, { recursive: true, withFileTypes: true });
  for (const e of entries) {
    if (!e.isFile()) continue;
    const full = join(e.parentPath, e.name);
    if (full.includes(`${dir}/.git/`) || full.includes("/.git/")) continue;
    if (e.name.endsWith(".abap")) abap.push(full);
    else if (e.name.endsWith(".tabl.xml")) tabl.push(full);
  }
  abap.sort();
  tabl.sort();
  return { abap, tabl };
}
