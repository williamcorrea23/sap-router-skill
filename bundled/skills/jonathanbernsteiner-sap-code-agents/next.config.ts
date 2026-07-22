// Next.js configuration (App Router).
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  outputFileTracingRoot: __dirname,
  // Let CI/gate builds run in an isolated dist dir so a concurrently running
  // `next dev` (same .next) can't corrupt trace collection.
  distDir: process.env.NEXT_DIST_DIR ?? ".next",
  // hide the floating Next.js dev-tools badge (bottom-left "N") in dev mode
  devIndicators: false,
  // @abaplint/core registers statement handlers in module-global state; if
  // webpack bundles it into more than one chunk the second copy throws
  // "duplicate statement syntax handler". Keep it external (ingest routes).
  serverExternalPackages: ["@abaplint/core", "pdfkit"],
  // pdfkit loads its built-in font metrics (.afm) from disk at runtime;
  // make sure they ship with the serverless bundle of the export route.
  outputFileTracingIncludes: {
    "/api/report/export": ["./node_modules/pdfkit/js/data/*.afm"],
  },
};

export default nextConfig;
