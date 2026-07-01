import { execSync } from "child_process";
import { env } from "./env.js";
import type { SapSystem } from "./systems.js";

export type AuthHeaders = Record<string, string>;

/**
 * Returns HTTP headers for SAP ADT requests.
 * AUTH_METHOD=basic     → Authorization: Basic base64(user:pass)
 * AUTH_METHOD=certificate → Authorization: Basic with cert identity (mTLS via CERT_THUMBPRINT)
 *
 * Note: True mutual TLS (X.509) requires the HTTP agent to carry the client cert.
 * See docs/authentication.md for OS keychain setup. This function returns the
 * identity headers; the axios agent with pfx/cert is configured in adt-client.ts.
 */
export function getAuthHeaders(system: SapSystem): AuthHeaders {
  const base: AuthHeaders = {
    "sap-client": system.client,
    "Accept": "application/json",
    "Content-Type": "application/json",
    "sap-language": system.language,
  };

  switch (env.AUTH_METHOD) {
    case "basic": {
      if (!env.SAP_USERNAME || !env.SAP_PASSWORD) {
        throw new Error(
          "AUTH_METHOD=basic requires SAP_USERNAME and SAP_PASSWORD in .env"
        );
      }
      const encoded = Buffer.from(
        `${env.SAP_USERNAME}:${env.SAP_PASSWORD}`
      ).toString("base64");
      return { ...base, Authorization: `Basic ${encoded}` };
    }

    case "certificate": {
      if (!env.CERT_THUMBPRINT) {
        throw new Error(
          "AUTH_METHOD=certificate requires CERT_THUMBPRINT in .env\n" +
            "See docs/authentication.md for how to get your SHA-1 thumbprint."
        );
      }
      // The actual TLS client cert is loaded by adt-client.ts via the OS keychain.
      // We still send Basic auth headers as identity fallback for SAP ADT.
      // Most SAP ADT deployments use certificate for transport-level auth + Basic for ADT identity.
      if (!env.SAP_USERNAME || !env.SAP_PASSWORD) {
        throw new Error(
          "AUTH_METHOD=certificate also requires SAP_USERNAME and SAP_PASSWORD " +
            "for ADT identity headers (certificate covers transport-layer auth)."
        );
      }
      const encoded = Buffer.from(
        `${env.SAP_USERNAME}:${env.SAP_PASSWORD}`
      ).toString("base64");
      return { ...base, Authorization: `Basic ${encoded}` };
    }
  }
}

/**
 * Retrieves the PEM certificate from OS keychain by SHA-1 thumbprint.
 * Used by adt-client.ts to configure the axios mTLS agent.
 * Returns null if AUTH_METHOD is not "certificate".
 */
export function getCertificatePem(): string | null {
  if (env.AUTH_METHOD !== "certificate" || !env.CERT_THUMBPRINT) return null;

  const thumbprint = env.CERT_THUMBPRINT.replace(/:/g, "").toUpperCase();
  const platform = process.platform;

  try {
    if (platform === "darwin") {
      // macOS: extract cert from Keychain by SHA-1 hash
      const result = execSync(
        `security find-certificate -a -Z /Library/Keychains/System.keychain ` +
          `/Users/$USER/Library/Keychains/login.keychain-db 2>/dev/null | ` +
          `awk '/SHA-1/{h=$NF} /-----BEGIN/{found=(h=="${thumbprint}")} found{print} /-----END/{found=0}'`,
        { encoding: "utf8" }
      );
      if (!result.trim()) throw new Error("Certificate not found in macOS Keychain");
      return result.trim();
    } else if (platform === "win32") {
      // Windows: use PowerShell to export cert by thumbprint
      const result = execSync(
        `powershell -Command "` +
          `$cert = Get-ChildItem Cert:\\CurrentUser\\My | ` +
          `Where-Object {$_.Thumbprint -eq '${thumbprint}'}; ` +
          `if ($cert) { [Convert]::ToBase64String($cert.Export('Cert')) } else { exit 1 }"`,
        { encoding: "utf8" }
      );
      return `-----BEGIN CERTIFICATE-----\n${result.trim()}\n-----END CERTIFICATE-----`;
    } else {
      throw new Error(
        `Certificate auth not supported on platform "${platform}". Use AUTH_METHOD=basic.`
      );
    }
  } catch (e) {
    throw new Error(
      `Failed to load certificate (thumbprint: ${env.CERT_THUMBPRINT}): ${
        e instanceof Error ? e.message : String(e)
      }\nSee docs/authentication.md for setup instructions.`
    );
  }
}
