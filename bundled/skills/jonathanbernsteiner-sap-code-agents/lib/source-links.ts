/**
 * Source provenance links — pure, client-safe helpers shared by the UI and
 * the report renderers. A workspace's `source` is a public https git URL
 * where the upstream repo is known (repo-ingested systems, and the abapGit
 * example seeded from its canonical repo); fixture systems carry a non-URL
 * marker ("fixtures"). Repo-level links render wherever the URL is known;
 * file:line deep links stay ingested-only (they need the recorded branch).
 */

/** True when the workspace source is a public https repo URL. */
export function isRepoUrl(source: string | null | undefined): boolean {
  return !!source && /^https:\/\//i.test(source.trim());
}

/** Repo base URL without trailing slash or .git — link target for the repo itself. */
export function repoBaseUrl(source: string): string {
  return source.trim().replace(/\/+$/, "").replace(/\.git$/, "");
}

/** Compact display text for a repo URL: "github.com/abap2xlsx/abap2xlsx". */
export function repoDisplayName(source: string): string {
  return repoBaseUrl(source).replace(/^https:\/\//i, "");
}

/**
 * Deep link to a file (and line) inside the repo on its web host, e.g.
 * https://github.com/o/r/blob/main/src/x.abap#L42. Uses the branch recorded
 * at ingestion; HEAD (the host resolves it to the default branch) when the
 * branch is unknown. Returns null when the source is not a repo URL —
 * fixture systems never link.
 */
export function buildRepoFileUrl(
  repoUrl: string | null | undefined,
  branch: string | null | undefined,
  path: string,
  line?: number | null
): string | null {
  if (!isRepoUrl(repoUrl)) return null;
  const base = repoBaseUrl(repoUrl!);
  const ref = encodeURIComponent(branch?.trim() || "HEAD");
  const cleanPath = path
    .replace(/^\/+/, "")
    .split("/")
    .map(encodeURIComponent)
    .join("/");
  return `${base}/blob/${ref}/${cleanPath}${line ? `#L${line}` : ""}`;
}
