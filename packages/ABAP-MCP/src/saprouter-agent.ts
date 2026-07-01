/**
 * `https.Agent` that tunnels every HTTPS connection through a SAProuter via
 * the SAP NI binary protocol (see `./saprouter.ts`).
 *
 * Each new HTTPS connection opens a fresh NI tunnel to the SAProuter and
 * asks it to forward TCP to the request's host:port. TLS is then negotiated
 * end-to-end with the target backend on top of the tunnel; the SAProuter
 * only sees opaque bytes, exactly as it would for a GUI / RFC connection.
 *
 * Usage:
 *
 *     const agent = new SAProuterHttpsAgent({ router, debug: true });
 *     const client = new ADTClient(url, user, pwd, client, lang, { httpsAgent: agent });
 */

import https from "https";
import type { RequestOptions } from "https";
import tls from "tls";
import type { TLSSocket } from "tls";
import type { Duplex } from "stream";
import { createSAProuterTunnel, SAProuterHop } from "./saprouter.js";

export interface SAProuterAgentOptions extends https.AgentOptions {
  /** First-hop SAProuter (host + port [+ password]). */
  router: SAProuterHop;
  /** Optional connect + NI handshake timeout in milliseconds. */
  tunnelTimeoutMs?: number;
  /** Emit NI frame trace lines to stderr. */
  debug?: boolean;
}

/** Shape of the extra TLS fields Node passes through `Agent#createConnection`. */
interface TlsConnectionOptions extends RequestOptions {
  servername?: string;
  rejectUnauthorized?: boolean;
  ca?: tls.SecureContextOptions["ca"];
  ALPNProtocols?: tls.ConnectionOptions["ALPNProtocols"];
}

type CreateConnectionCallback = (err: Error | null, stream: Duplex) => void;

export class SAProuterHttpsAgent extends https.Agent {
  private readonly router: SAProuterHop;
  private readonly tunnelTimeoutMs?: number;
  private readonly debug: boolean;

  constructor(opts: SAProuterAgentOptions) {
    super(opts);
    this.router = opts.router;
    this.tunnelTimeoutMs = opts.tunnelTimeoutMs;
    this.debug = !!opts.debug;
  }

  /**
   * Override Node's per-connection factory: return a TLS socket layered on
   * top of a fresh NI tunnel instead of a direct TCP connection.
   *
   * Node's typings declare a synchronous return value, but in practice an
   * async connection is reported via the callback and `undefined` is
   * returned synchronously. We match the typings shape and rely on the
   * callback contract.
   */
  createConnection(
    options: RequestOptions,
    callback?: CreateConnectionCallback,
  ): Duplex | null | undefined {
    const opts = options as TlsConnectionOptions;
    const cb = callback ?? ((): void => undefined);
    const host = typeof opts.host === "string" ? opts.host : undefined;
    const port = typeof opts.port === "number" ? opts.port : undefined;
    if (!host || !port) {
      cb(new Error("SAProuterHttpsAgent: missing host or port for createConnection"), undefined as unknown as Duplex);
      return undefined;
    }
    createSAProuterTunnel({
      router: this.router,
      target: { host, port },
      timeoutMs: this.tunnelTimeoutMs,
      debug: this.debug,
    })
      .then((rawSocket) => {
        const tlsSocket: TLSSocket = tls.connect({
          socket: rawSocket,
          servername: opts.servername ?? host,
          rejectUnauthorized: opts.rejectUnauthorized,
          ca: opts.ca,
          ALPNProtocols: opts.ALPNProtocols,
        });
        tlsSocket.once("secureConnect", () => cb(null, tlsSocket));
        tlsSocket.once("error", (err) => cb(err, undefined as unknown as Duplex));
      })
      .catch((err: Error) => cb(err, undefined as unknown as Duplex));
    return undefined;
  }
}
