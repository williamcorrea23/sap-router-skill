/**
 * Pure helpers for the web tools (fetch_url, search_sap_web).
 * No network, no config — unit-testable in isolation.
 */

/**
 * Truncate extracted page content to `maxLen` characters, appending a
 * German marker so the model knows the content was cut.
 */
export function truncateContent(content: string, maxLen: number): string {
  if (content.length <= maxLen) return content;
  return content.slice(0, maxLen) +
    `\n\n--- [Inhalt gekürzt: ${content.length} → ${maxLen} Zeichen] ---`;
}

/**
 * Normalize a URL for fuzzy equality: ignore protocol (http/https redirects),
 * `www.` prefix, trailing slashes, query string and fragment.
 * Returns the raw input lowercased if it is not a parseable URL.
 */
export function normalizeUrlForMatch(raw: string): string {
  try {
    const u = new URL(raw);
    const host = u.hostname.toLowerCase().replace(/^www\./, "");
    const path = u.pathname.replace(/\/+$/, "");
    return `${host}${path}`;
  } catch {
    return raw.trim().toLowerCase().replace(/\/+$/, "");
  }
}

/**
 * Pick the search result that best matches the requested URL:
 * exact normalized match first, otherwise the first result.
 */
export function pickBestResult<T extends { url: string }>(
  requestedUrl: string,
  results: T[] | undefined,
): T | undefined {
  if (!results || results.length === 0) return undefined;
  const wanted = normalizeUrlForMatch(requestedUrl);
  return results.find((r) => normalizeUrlForMatch(r.url) === wanted) ?? results[0];
}
