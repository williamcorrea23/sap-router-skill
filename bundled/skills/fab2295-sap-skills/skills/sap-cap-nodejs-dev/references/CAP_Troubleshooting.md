# CAP Node.js Troubleshooting Reference

> Source: https://cap.cloud.sap/docs/get-started/get-help#node-js
> 
> Style reference based on the user's provided file.

## Environment & Version Checks

### Check the Node.js version

Use the latest LTS version of Node.js. The CAP documentation recommends even-numbered LTS releases such as 20, 22, and 24. Avoid odd-numbered versions because some native modules may fail to install.

```sh
node -v
```

If startup shows an error like `Node.js v1... or higher is required for @sap/cds`, upgrade to at least the minimum required version. For Cloud Foundry deployments, define the Node.js version in the `engines` field of `package.json`.

### Check access permissions on macOS or Linux

If global installs fail with errors like:

```txt
Error: EACCES: permission denied, mkdir '/usr/local/...'
```

configure `npm` to use a user directory for global modules:

```sh
mkdir ~/.npm-global ; npm set prefix '~/.npm-global'
export PATH=~/.npm-global/bin:$PATH
```

Also add the `export PATH=...` line to your shell profile, for example `~/.profile`.

### Check environment variables on Windows

Global npm installations are usually stored in:

```txt
C:\Users\<your-username>\AppData\Roaming\npm
```

Make sure this path is included in `PATH`.

Also set `NODE_PATH` to:

```txt
C:\Users\<your-username>\AppData\Roaming\npm\node_modules
```

### Updating CDS versions

**Design-time tools** such as `cds init` should be updated globally:

```sh
npm i -g @sap/cds-dk
```

**Node.js runtime** projects should keep `@sap/cds` updated in the top-level `package.json` under `dependencies`.

---

## Runtime Troubleshooting

### How can I start Node.js apps on different ports?

By default, CAP Node.js apps run on port `4004`. If another process is already using that port, `cds watch` may prompt you to restart on a different port.

```sh
cds watch
```

You can also define a custom port explicitly using one of these options:

- `PORT` environment variable
- `cds.server.port = 4005` configuration
- `cds serve --port 4005`
- `cds watch --port 4005`

### Why do I lose registered event handlers?

A common issue happens when event handlers are registered in `cds.on('served', ...)` using asynchronous code.

**Recommended:**

```js
cds.on('served', ()=>{
  const { db } = cds.services
  db.on('before',(req)=> console.log(req.event, req.path))
})
```

**Avoid this pattern:**

```js
cds.on('served', async ()=>{
  const db = await cds.connect.to('db') // DANGER: race condition
  db.on('before',(req)=> console.log(req.event, req.path))
})
```

Reason: Node.js `emit` operations are synchronous. Using `await` inside `cds.on('served', ...)` can introduce race conditions and cause hard-to-diagnose handler registration issues.

### Why does my app not show up in Dynatrace?

Check these two requirements:

- The application start script must be `cds-serve`, not `npx cds run`
- `@dynatrace/oneagent-sdk` must be present in `package.json`

### Why are requests rejected with HANA timeout errors?

Typical errors include:

- `Acquiring client from pool timed out`
- `ResourceRequest timed out`

These usually point to connectivity issues rather than CAP logic issues. Verify that:

- The SAP HANA instance is accessible from the application environment
- The database is correctly mapped to the Cloud Foundry space or Kyma cluster
- Required IP ranges are allowed

If these errors happen during startup, infrastructure or connectivity is the most likely root cause.

### Why are requests rejected with `431`?

A `431` error means the HTTP request headers are too large for the Node.js HTTP server.

Root cause:

- The request is rejected by Node.js during header parsing
- The request never reaches CAP
- The application may not log the request at all

Recommended action:

- Inspect request headers
- Reduce header size if possible
- If large headers are unavoidable, increase the Node.js header limit:

```sh
NODE_OPTIONS="--max-http-header-size=65536"
```

### Why are requests rejected with `502`?

If the request does not seem to reach the CAP application, but platform router logs show a `502`, the problem may be related to long-running requests and TCP connection reuse by the platform load balancer.

The CAP documentation suggests adjusting the Node.js server `keepAliveTimeout`:

```js
const cds = require('@sap/cds')
cds.once('listening', ({ server }) => {
  server.keepAliveTimeout = 3 * 60 * 1000 // > 3 mins
})
module.exports = cds.server
```

This helps when the platform still believes a connection is open while the server has already closed it.

---

## Quick Troubleshooting Checklist

### Setup & Tooling

- Confirm you are using an even-numbered Node.js LTS release
- Update `@sap/cds-dk` globally
- Keep `@sap/cds` current in project dependencies
- Check npm permissions and PATH/NODE_PATH issues

### CAP Runtime

- Check whether port `4004` is already in use
- Avoid `await` inside `cds.on('served', ...)`
- Use `cds-serve` when integrating with Dynatrace

### Connectivity & Infrastructure

- Verify SAP HANA reachability from the runtime environment
- Validate CF or Kyma service mappings
- Check allowed IP ranges and service bindings

### HTTP Errors

- `431`: inspect or reduce headers, or raise Node.js header limit
- `502`: review long-running requests and server `keepAliveTimeout`

---

## Recommended Diagnostic Order

1. Verify Node.js and CDS versions
2. Check local environment variables and npm permissions
3. Confirm CAP server startup command and port usage
4. Review handler registration patterns for race conditions
5. Validate database connectivity and service mappings
6. Inspect request headers for `431` issues
7. Inspect long-running request behavior for `502` issues

---

## Notes

This reference is intentionally focused on the CAP Node.js troubleshooting topics explicitly documented in the official CAP “Getting Help” page for Node.js.
