/**
 * Public surface of the SAP BTP Connectivity Proxy integration.
 *
 * The implementation is split into three cohesive layers:
 *
 *   credentials.ts  — resolve XSUAA client credentials from env, a CAP
 *                     `.cdsrc-private.json` binding, or a service-key JSON file
 *   token.ts        — fetch / cache / refresh XSUAA JWTs (client_credentials)
 *   agent.ts        — build an HttpProxyAgent or HttpsProxyAgent that signs
 *                     every request with the live JWT + Cloud Connector
 *                     location-ID
 *
 * Consumers should import from this barrel, not the individual files, so
 * internal refactors don't ripple outward.
 */

export type { BtpConnectivityCreds } from "./credentials.js";
export { loadBtpConnectivityCreds } from "./credentials.js";

export { BtpConnectivityTokenSource } from "./token.js";

export type {
  BtpConnectivityAgentConfig,
  BtpConnectivityAgentBundle,
} from "./agent.js";
export { createBtpConnectivityAgentBundle } from "./agent.js";
