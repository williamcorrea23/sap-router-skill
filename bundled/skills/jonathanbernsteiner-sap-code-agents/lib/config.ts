/**
 * Product identity — single source of truth.
 */
export const PRODUCT_NAME = "SAP Code Agents";
export const PRODUCT_DESCRIPTION =
  "Evidence-tiered analysis of custom ABAP codebases for SAP S/4HANA migration pre-studies";

/**
 * Absolute base URL of this deployment — invite links and auth-email
 * redirects. NEXT_PUBLIC_SITE_URL wins; on Vercel previews it falls back to
 * VERCEL_URL, locally to localhost.
 */
export function siteUrl(): string {
  const explicit = process.env.NEXT_PUBLIC_SITE_URL;
  if (explicit) return explicit.replace(/\/$/, "");
  if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}`;
  return "http://localhost:3000";
}
