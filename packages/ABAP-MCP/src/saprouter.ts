/**
 * SAP NI / NI_ROUTE tunnel implementation.
 *
 * Speaks just enough of the SAP NI binary protocol to ask a SAProuter to
 * forward TCP traffic to a target host:port. After the handshake completes
 * successfully, the returned socket is a transparent passthrough to the
 * target, suitable for layering TLS on top (i.e. ADT HTTPS over SAProuter).
 *
 * Wire format (NI_ROUTE request), big-endian. Field layout matches the pysap
 * SAPRouter packet (which is the working open-source reference) and the
 * publicly documented SAP NI protocol. Values verified against a live
 * SAProuter 40.x using the saprouter-probe.ts script.
 *
 *   offset  size   field
 *   0       4      ni_msg_len           total length of everything that follows
 *   4       9      eyecatcher           ASCII "NI_ROUTE" + 0x00
 *   13      1      version              0x02
 *   14      1      route_ni_version     0x28 (40 — default for modern routers)
 *   15      1      route_entries        number of hops (router + target = 2)
 *   16      1      route_talk_mode      0x01 (NI_RAW_IO — required for raw HTTPS)
 *   17      2      route_padd           0x0000
 *   19      1      route_rest_nodes     entries - 1 (hops AFTER the router itself)
 *   20      4      route_length         length of route_string
 *   24      4      route_offset         byte length of first hop entry
 *                                       (so the SAProuter advances past itself
 *                                        to the target entry on its own)
 *   28      N      route_string         concatenated entries:
 *                                       host\0 port\0 password\0 ...
 *
 * Response on success: an NI message whose body begins with "NI_PONG".
 * After the success message the socket is a passthrough.
 * On failure the body begins with "NI_RTERR" / "NIRTERR" / similar and
 * contains a human-readable error string.
 *
 * Format derived from public references (pysap, SAP Note 35435, OSS commentary)
 * — not from any proprietary SAP material.
 */

import net from "net";

export interface SAProuterHop {
  host: string;
  port: number | string;
  password?: string;
}

export interface SAProuterTunnelOptions {
  router: SAProuterHop;
  target: SAProuterHop;
  /** Optional connect+handshake timeout in ms. Default 15000. */
  timeoutMs?: number;
  /** If true, log NI frames to stderr for debugging. */
  debug?: boolean;
}

const ROUTE_NI_VERSION = 0x28;     // 40 — SAPROUTER_DEFAULT_VERSION in pysap
const ROUTE_REQUEST_VERSION = 0x02; // packet version
const TALK_MODE_NI_RAW_IO = 0x01;   // raw bytes after NI_PONG — required for HTTPS
const NI_ROUTE_EYECATCHER = Buffer.from("NI_ROUTE\x00", "ascii"); // 9 bytes
const DEFAULT_TIMEOUT_MS = 15000;

function encodeRouteString(hops: SAProuterHop[]): Buffer {
  const parts: Buffer[] = [];
  for (const hop of hops) {
    parts.push(Buffer.from(hop.host, "ascii"), Buffer.from([0]));
    parts.push(Buffer.from(String(hop.port), "ascii"), Buffer.from([0]));
    parts.push(Buffer.from(hop.password ?? "", "ascii"), Buffer.from([0]));
  }
  return Buffer.concat(parts);
}

function buildRouteRequest(hops: SAProuterHop[]): Buffer {
  const routeString = encodeRouteString(hops);
  // Byte length of the first hop's serialized form. The SAProuter expects
  // route_offset to point to the *next* hop after itself, so we hand it the
  // length of its own entry.
  const firstHopLen = encodeRouteString([hops[0]]).length;
  const HEADER_LEN = 24;
  const body = Buffer.alloc(HEADER_LEN + routeString.length);
  NI_ROUTE_EYECATCHER.copy(body, 0);
  body.writeUInt8(ROUTE_REQUEST_VERSION, 9);
  body.writeUInt8(ROUTE_NI_VERSION, 10);
  body.writeUInt8(hops.length, 11);
  body.writeUInt8(TALK_MODE_NI_RAW_IO, 12);
  body.writeUInt16BE(0, 13); // padding
  body.writeUInt8(hops.length - 1, 15); // rest_nodes = hops after this router
  body.writeUInt32BE(routeString.length, 16);
  body.writeUInt32BE(firstHopLen, 20);
  routeString.copy(body, HEADER_LEN);

  const prefix = Buffer.alloc(4);
  prefix.writeUInt32BE(body.length, 0);
  return Buffer.concat([prefix, body]);
}

/**
 * Reads exactly one NI frame: 4-byte BE length prefix, then `length` bytes.
 * Returns the body. Times out if not received within `timeoutMs`.
 *
 * Important: this function consumes precisely one frame and leaves any
 * subsequent bytes intact on the socket buffer, so further bytes received
 * after a successful handshake remain available to higher layers (TLS).
 */
function readOneNiFrame(socket: net.Socket, timeoutMs: number): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    let buf: Buffer = Buffer.alloc(0);
    let needed = -1;
    const onData = (chunk: Buffer) => {
      buf = Buffer.concat([buf, chunk]);
      if (needed < 0 && buf.length >= 4) {
        needed = buf.readUInt32BE(0);
      }
      if (needed >= 0 && buf.length >= 4 + needed) {
        cleanup();
        const body = buf.subarray(4, 4 + needed);
        const leftover = buf.subarray(4 + needed);
        if (leftover.length > 0) socket.unshift(leftover);
        resolve(body);
      }
    };
    const onError = (err: Error) => { cleanup(); reject(err); };
    const onClose = () => { cleanup(); reject(new Error("socket closed before NI response")); };
    const timer = setTimeout(() => { cleanup(); reject(new Error(`NI handshake timed out after ${timeoutMs}ms`)); }, timeoutMs);
    function cleanup() {
      clearTimeout(timer);
      socket.off("data", onData);
      socket.off("error", onError);
      socket.off("close", onClose);
    }
    socket.on("data", onData);
    socket.once("error", onError);
    socket.once("close", onClose);
  });
}

function bodyLooksLike(body: Buffer, marker: string): boolean {
  return body.subarray(0, marker.length).toString("ascii") === marker;
}

function describeErrorBody(body: Buffer): string {
  // Pull printable ASCII for a useful error message
  const text = body.toString("latin1").replace(/[^\x20-\x7e\n\r\t]/g, " ").trim();
  return text.length > 0 ? text : `0x${body.toString("hex")}`;
}

/**
 * Open a TCP socket to `router`, ask SAProuter to route to `target`, and
 * resolve with the upgraded socket once the handshake succeeds.
 * The caller can wrap the returned socket in TLS to talk to the target.
 */
export function createSAProuterTunnel(opts: SAProuterTunnelOptions): Promise<net.Socket> {
  const timeoutMs = opts.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const dbg = opts.debug ? (msg: string) => console.error(`[saprouter] ${msg}`) : () => {};

  return new Promise((resolve, reject) => {
    const routerPort = typeof opts.router.port === "string" ? parseInt(opts.router.port, 10) : opts.router.port;
    if (!routerPort || Number.isNaN(routerPort)) return reject(new Error(`invalid SAProuter port: ${opts.router.port}`));

    const socket = net.createConnection({ host: opts.router.host, port: routerPort });
    socket.setNoDelay(true);

    const connectTimer = setTimeout(() => {
      socket.destroy(new Error(`TCP connect to SAProuter ${opts.router.host}:${routerPort} timed out after ${timeoutMs}ms`));
    }, timeoutMs);

    socket.once("error", (err) => {
      clearTimeout(connectTimer);
      reject(err);
    });

    socket.once("connect", async () => {
      clearTimeout(connectTimer);
      try {
        const req = buildRouteRequest([opts.router, opts.target]);
        dbg(`-> NI_ROUTE ${opts.router.host}:${routerPort} -> ${opts.target.host}:${opts.target.port} (${req.length} bytes)`);
        socket.write(req);

        const body = await readOneNiFrame(socket, timeoutMs);
        const head = body.subarray(0, Math.min(16, body.length)).toString("ascii").replace(/\0/g, ".");
        dbg(`<- ${body.length} bytes, head="${head}"`);

        if (bodyLooksLike(body, "NI_PONG")) {
          // Standard success acknowledgement; socket is now a transparent tunnel.
          resolve(socket);
          return;
        }
        if (bodyLooksLike(body, "NI_RTERR") || bodyLooksLike(body, "NIRTERR")) {
          socket.destroy();
          reject(new Error(`SAProuter rejected route: ${describeErrorBody(body)}`));
          return;
        }
        // Some SAProuter versions just start passing data after NI_ROUTE without
        // sending NI_PONG. If the body does not look like an error and we have
        // already consumed one frame, treat as success and unshift the body so
        // it becomes available to the TLS layer above.
        if (body.length > 0) socket.unshift(Buffer.concat([encodeFrameLength(body.length), body]));
        resolve(socket);
      } catch (e) {
        socket.destroy();
        reject(e instanceof Error ? e : new Error(String(e)));
      }
    });
  });
}

function encodeFrameLength(len: number): Buffer {
  const b = Buffer.alloc(4);
  b.writeUInt32BE(len, 0);
  return b;
}

/**
 * Parse a SAP-style route string like:
 *   /H/saproutprd.example.com/S/3299
 *   /H/saproutprd.example.com/S/3299/H/mdadneap1.example.com/S/44300
 *   /H/host/S/port/W/password
 *
 * Returns an ordered list of hops. The first hop is the SAProuter; subsequent
 * hops are intermediate or target nodes. If only one hop is given, the target
 * must be supplied separately.
 */
export function parseSapRouteString(s: string): SAProuterHop[] {
  const hops: SAProuterHop[] = [];
  let current: Partial<SAProuterHop> | null = null;
  const tokens = s.split("/").filter(Boolean);
  for (let i = 0; i < tokens.length; i += 2) {
    const kind = tokens[i]?.toUpperCase();
    const value = tokens[i + 1] ?? "";
    if (!kind || !value) throw new Error(`unexpected SAP route token at position ${i}: '${tokens[i] ?? ""}'`);
    if (kind === "H") {
      if (current && current.host) {
        hops.push({ host: current.host, port: current.port ?? 3299, password: current.password });
      }
      current = { host: value };
    } else if (kind === "S") {
      if (!current) throw new Error("SAP route 'S' before 'H'");
      current.port = parseInt(value, 10);
    } else if (kind === "W" || kind === "P") {
      if (!current) throw new Error("SAP route password before 'H'");
      current.password = value;
    } else {
      throw new Error(`unknown SAP route token '${kind}'`);
    }
  }
  if (current && current.host) {
    hops.push({ host: current.host, port: current.port ?? 3299, password: current.password });
  }
  if (hops.length === 0) throw new Error(`empty SAP route string: '${s}'`);
  return hops;
}
