import { config } from "dotenv";
import { z } from "zod";

config();

const EnvSchema = z.object({
  // Primary SAP system — used when SYSTEMS_CONFIG is not set
  SAP_HOSTNAME: z.string().min(1, "SAP_HOSTNAME is required"),
  SAP_SYSNR: z.string().regex(/^\d{2}$/, "SAP_SYSNR must be a 2-digit number (e.g. 00)").default("00"),
  SAP_CLIENT: z.string().regex(/^\d{3}$/, "SAP_CLIENT must be a 3-digit number (e.g. 100)").default("100"),
  SAP_LANGUAGE: z.string().length(2).default("EN"),
  SAP_SYSTEM_ID: z.string().default("DEV"), // logical name shown in tool output

  // Auth
  AUTH_METHOD: z.enum(["basic", "certificate"]).default("basic"),
  SAP_USERNAME: z.string().optional(),
  SAP_PASSWORD: z.string().optional(),
  CERT_THUMBPRINT: z.string().optional(), // SHA-1 thumbprint, AUTH_METHOD=certificate

  // Multi-system (optional — JSON array overrides individual SAP_* vars)
  // Format: [{"id":"DEV","hostname":"dev.sap.co","sysnr":"00","client":"100","language":"EN","isDefault":true}]
  SYSTEMS_CONFIG: z.string().optional(),

  // HTTPS port override — cloud systems use 443, on-prem uses 8000+sysnr
  SAP_HTTPS_PORT: z.coerce.number().optional(),

  // Operational
  LOG_LEVEL: z.enum(["debug", "info", "warn", "error"]).default("info"),
  DRY_RUN: z.preprocess((v) => v === "true" || v === true, z.boolean()).default(false),
});

function loadEnv() {
  const result = EnvSchema.safeParse(process.env);
  if (!result.success) {
    const issues = result.error.issues
      .map((i) => `  ${i.path.join(".")}: ${i.message}`)
      .join("\n");
    throw new Error(`Environment configuration invalid:\n${issues}`);
  }
  return result.data;
}

export const env = loadEnv();
export type Env = typeof env;
