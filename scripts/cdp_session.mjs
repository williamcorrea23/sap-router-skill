#!/usr/bin/env node
// Zero-dependency Chrome DevTools Protocol client.
//
// Calls run inside a tab the user already logged in to, so session cookies stay
// in the browser and are never read, exported or forwarded by this process.
import { setTimeout as delay } from "node:timers/promises";

export const RESPONSE_BODY_LIMIT = 25_000;
const EVAL_TIMEOUT_MS = 45_000;

export function cdpBaseUrl() {
  if (process.env.BROWSER_CDP_URL) {
    return process.env.BROWSER_CDP_URL.replace(/\/$/, "");
  }
  return `http://127.0.0.1:${process.env.CHROME_DEBUGGING_PORT || "9222"}`;
}

export function originOf(url) {
  try {
    return new URL(url).origin;
  } catch {
    return "";
  }
}

export function websocketAvailable() {
  return typeof globalThis.WebSocket === "function";
}

async function getJson(path, timeoutMs = 4000) {
  const response = await fetch(cdpBaseUrl() + path, { signal: AbortSignal.timeout(timeoutMs) });
  if (!response.ok) {
    throw new Error(`CDP ${path} returned HTTP ${response.status}`);
  }
  return response.json();
}

export async function browserVersion() {
  return getJson("/json/version");
}

export async function listTargets() {
  const targets = await getJson("/json/list");
  return Array.isArray(targets) ? targets.filter((t) => t.type === "page") : [];
}

/** Find the logged-in tab for `expectedOrigin`, preferring deeper tenant paths. */
export async function findTab(expectedOrigin) {
  const pages = await listTargets();
  const matches = pages.filter((page) => originOf(page.url) === expectedOrigin);
  if (matches.length === 0) {
    return null;
  }
  matches.sort((a, b) => (b.url?.length || 0) - (a.url?.length || 0));
  return matches[0];
}

class CdpSession {
  constructor(target) {
    this.target = target;
    this.socket = null;
    this.nextId = 1;
    this.pending = new Map();
  }

  async connect() {
    if (!websocketAvailable()) {
      throw new Error("global WebSocket unavailable; Node 22+ required for the CDP session channel");
    }
    const socket = new globalThis.WebSocket(this.target.webSocketDebuggerUrl);
    socket.addEventListener("message", (event) => {
      let message;
      try {
        message = JSON.parse(typeof event.data === "string" ? event.data : String(event.data));
      } catch {
        return;
      }
      const waiter = this.pending.get(message.id);
      if (!waiter) {
        return;
      }
      this.pending.delete(message.id);
      if (message.error) {
        waiter.reject(new Error(message.error.message || "CDP error"));
      } else {
        waiter.resolve(message.result);
      }
    });
    socket.addEventListener("close", () => {
      for (const waiter of this.pending.values()) {
        waiter.reject(new Error("CDP connection closed"));
      }
      this.pending.clear();
    });
    await new Promise((resolve, reject) => {
      const onOpen = () => {
        socket.removeEventListener("error", onError);
        resolve();
      };
      const onError = () => {
        socket.removeEventListener("open", onOpen);
        reject(new Error(`Cannot open CDP WebSocket for ${this.target.url}`));
      };
      socket.addEventListener("open", onOpen, { once: true });
      socket.addEventListener("error", onError, { once: true });
    });
    this.socket = socket;
    return this;
  }

  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.socket.send(JSON.stringify({ id, method, params }));
      delay(EVAL_TIMEOUT_MS).then(() => {
        if (this.pending.delete(id)) {
          reject(new Error(`CDP ${method} timed out after ${EVAL_TIMEOUT_MS}ms`));
        }
      });
    });
  }

  async evaluate(expression) {
    const result = await this.send("Runtime.evaluate", {
      expression,
      awaitPromise: true,
      returnByValue: true,
      userGesture: false,
    });
    if (result.exceptionDetails) {
      const text = result.exceptionDetails.exception?.description || result.exceptionDetails.text;
      throw new Error(`page evaluation failed: ${text}`);
    }
    return result.result?.value;
  }

  close() {
    try {
      this.socket?.close();
    } catch {
      // socket already gone
    }
  }
}

export async function openSession(expectedOrigin) {
  let target;
  try {
    target = await findTab(expectedOrigin);
  } catch (err) {
    // An unreachable CDP endpoint is an ordinary "no session" case, not a crash.
    return { error: `Chrome/CDP not reachable at ${cdpBaseUrl()}: ${err?.message || String(err)}` };
  }
  if (!target) {
    return { error: `no logged-in tab found for ${expectedOrigin}` };
  }
  if (!target.webSocketDebuggerUrl) {
    return { error: `tab for ${expectedOrigin} exposes no WebSocket debugger URL` };
  }
  const session = await new CdpSession(target).connect();
  return { session, target };
}

/**
 * Run fetch() inside the logged-in page. The browser attaches session cookies
 * itself; nothing about them crosses back into this process.
 */
export async function apiFetch(session, path, { method = "GET", body = null, headers = {} } = {}) {
  const request = JSON.stringify({ path, method: method.toUpperCase(), body, headers, limit: RESPONSE_BODY_LIMIT });
  const expression = `(async (req) => {
    const target = new URL(req.path, location.origin);
    if (target.origin !== location.origin) {
      return { status: "BLOCKED", reason: "cross-origin request refused", origin: location.origin };
    }
    const init = { method: req.method, credentials: "same-origin", headers: req.headers || {} };
    if (req.body !== null && req.body !== undefined && req.method !== "GET" && req.method !== "HEAD") {
      init.body = req.body;
    }
    let response;
    try {
      response = await fetch(target.toString(), init);
    } catch (err) {
      return { status: "ERROR", url: target.toString(), reason: String(err && err.message ? err.message : err) };
    }
    const text = await response.text();
    const headerPairs = {};
    response.headers.forEach((value, key) => { headerPairs[key] = value; });
    return {
      status: response.ok ? "OK" : "ERROR",
      http_status: response.status,
      url: target.toString(),
      headers: headerPairs,
      truncated: text.length > req.limit,
      body: text.slice(0, req.limit),
    };
  })(${request})`;
  return session.evaluate(expression);
}

/** Fetch the API portal CSRF token from inside the page, for gated mutations. */
export async function fetchCsrfToken(session, path = "/apiportal/api/1.0/Management.svc/") {
  const result = await apiFetch(session, path, { headers: { "X-CSRF-Token": "Fetch" } });
  if (result?.status === "BLOCKED") {
    return result;
  }
  const token = result?.headers?.["x-csrf-token"] || "";
  return { status: token ? "OK" : "ERROR", token, http_status: result?.http_status };
}

export async function withSession(expectedOrigin, handler) {
  const attached = await openSession(expectedOrigin);
  if (attached.error) {
    return { status: "DEGRADED", reason: attached.error, cdp_url: cdpBaseUrl() };
  }
  try {
    return await handler(attached.session, attached.target);
  } finally {
    attached.session.close();
  }
}
