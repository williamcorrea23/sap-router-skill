# Troubleshooting

Load this file when a command fails and the failure mode is not obvious.
The tables below map common symptoms to root causes and recommended next
steps. When a symptom is not listed, prefer inspection over retrying — most
ADT failures are configuration-level and will not resolve through retries.

## Missing Credentials

| Symptom                                                    | Cause                                                          | Fix                                                                                                        |
| ---------------------------------------------------------- | -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| JSON error `Missing connection values for --dest ...`      | `SAP_<SID>_URL` or `SAP_<SID>_<USER>_PWD` env var not set      | Show the exact `setx` command to the human with a `<password>` placeholder; wait for confirmation.         |
| `error: missing --pwd`                                     | Neither `--dest` nor `--pwd` provided                          | Use `--dest SID_CLIENT_USER_LANG` with env vars, or pass explicit flags in a shell the agent does not own. |

## Authentication and Authorization

| HTTP | Symptom                                                | Likely cause                                    | Fix                                                                                     |
| ---- | ------------------------------------------------------ | ----------------------------------------------- | --------------------------------------------------------------------------------------- |
| 401  | `Authentication failed (HTTP 401)`                     | Wrong user, password, or client                 | Verify `SAP_<SID>_<USER>_PWD` and the `USER` / `CLIENT` parts of `--dest`.              |
| 403  | Authentication failed on discovery, or 403 on a write  | Missing SAP authorizations, or lock by editor   | Confirm ADT authorizations; close SE38 / SE80 editor session; retry.                    |

Do not retry 401 or 403 in a loop. Retries with the same credentials will not
change the result and may lock the account.

## Endpoint Availability

| HTTP | Symptom                                                    | Meaning                                                                          | Fix                                                                                    |
| ---- | ---------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| 404  | On `transports`, `transport-contents`, `create-transport`  | CTS REST is not enabled                                                          | Use SE01/SE09/SE10 through SAP GUI or ADT in Eclipse.                                  |
| 404  | On `inactive-objects`                                      | Endpoint variant not exposed; client already falls back to `workarea/inactive`   | If the fallback also fails, the endpoint is not available on this release.             |
| 406  | On `atc-check` worklist                                    | System does not accept the ATC worklist content type                             | Run ATC through SCI or SE38.                                                           |
| 406  | On text elements or message class                          | Endpoint requires `Accept: */*`                                                  | Retry with the default settings; the client already handles this internally.           |

Not all SAP systems expose the same ADT endpoints. Endpoint absence is a
system configuration issue, not a bug in the client.

## Locks and Concurrency

| Symptom                                       | Meaning                                                                         | Fix                                                                                                              |
| --------------------------------------------- | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Cannot lock object for source write           | Another session holds the lock                                                  | Use `unlock NAME --type TYPE` if the lock is your own; otherwise ask an administrator to release it via SM12.    |
| HTTP 403 on `activate` immediately after write | The object is open in an interactive SE38 / SE80 session that owns the lock     | Close the editor and retry `activate`.                                                                           |
| `unlock` reports the lock is held by another user | Only SM12 can clear cross-user locks                                          | Ask an SAP administrator to clear the lock. Do not retry.                                                        |

## Activation and Related Errors

| Symptom                                                     | Meaning                                                                     | Fix                                                                                              |
| ----------------------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `activate` returns `inactive_remaining` values              | Some prerequisites are still inactive                                       | Activate the prerequisites first, or activate them together in the same call.                    |
| `activate` returns syntax or definition errors              | The written source has ABAP errors                                          | Fix the source and reactivate. Never suppress the error by re-running unchanged.                 |
| `write-source` reports the system is delivery-only          | `MODIFICATION_SUPPORT=false` in the target system                          | The system is locked for modifications. Use the intended development system instead.             |

## Transport Errors

| Symptom                                                              | Meaning                                                                | Fix                                                                                              |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `create-transport` returns SE01/SE09 hint                            | CTS REST not enabled                                                   | Create the transport through SAP GUI, then use its number in subsequent calls.                   |
| `release-transport` returns `released: false`                        | An open task refused to release                                        | Inspect the returned task-level result, fix the failing task, then retry.                        |
| `delete-transport` reports the transport is not empty                | The transport still contains objects                                   | Move objects with `move-object` first, then retry.                                               |
| `move-object` falls back to the direct task-objects PUT              | The re-lock approach did not succeed                                   | Confirm the object is not locked by another user; check the returned status.                     |

Never resolve a transport failure by deleting or force-releasing something
that is contested. Escalate to a human.

## Quality Check Anomalies

| Command      | Symptom                                                                | Meaning                                                             | Fix                                                                                                                 |
| ------------ | ---------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `atc-check`  | `gate: UNKNOWN_POLL_UNSUPPORTED`                                       | The worklist endpoint could not be polled                           | Run ATC via SCI or SE38 and report the result manually.                                                             |
| `atc-check`  | HTTP 406 on worklist                                                   | Endpoint not exposed in the expected content type                   | Run ATC through SAP GUI.                                                                                            |
| `abap-unit`  | HTTP 400 or empty result set                                           | The XML schema on this release differs from the expected shape      | Run ABAP Unit through SE80 or ADT in Eclipse and paste the result.                                                  |

Do not report `PASS` when the check did not complete.

## XML Parsing Errors

If the client emits an unexpected XML parsing error, the target endpoint may
have returned an HTML login page or an error page instead of ADT XML. Common
causes:

- The base URL is wrong.
- The SAP web dispatcher rewrote the URL.
- A load balancer terminated the session.
- Authentication actually failed but the server returned HTML instead of a
  JSON or XML error body.

Inspect the raw response by running the same request from a browser or
`curl` while authenticated, and adjust the base URL or path accordingly.

## TLS or Certificate Errors

The client verifies the SAP server certificate against the system CA trust
store by default. TLS errors are expected in corporate SAP environments that
issue certificates from a private certificate authority. The client does not
fall back to insecure mode automatically.

| Symptom                                                       | Fix                                                                                  |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `certificate verify failed: unable to get local issuer ...`   | Point the client at the corporate CA bundle: `--ca-bundle <path>` or `SAP_ADT_CA_BUNDLE`. |
| Any TLS handshake error on a system with a valid public cert  | Confirm the URL is `https://` with the correct port, and that the network path (VPN, proxy) is up. |
| Repeated TLS errors while triaging a lab or sandbox system    | Use `--insecure` for the specific invocation. Never make it a default.               |
| Both `--insecure` and `--ca-bundle` supplied                  | Configuration error — the client fails fast with a JSON validation message.          |

Prefer `--ca-bundle` or `SAP_ADT_CA_BUNDLE` for corporate SAP systems.
`--insecure` is intended only for controlled troubleshooting and
non-production environments and prints a warning on `stderr` when active.

## Safe Retry Guidance

Retry is safe only when the failure is transient and the operation is
idempotent. Examples:

- Network timeout while listing transports: safe to retry after a short
  delay.
- Read-only inspection commands: safe to retry.

Retry is **not** safe for:

- Authorization failures (`401`, `403`).
- Malformed requests (`400`).
- Missing endpoint (`404`).
- Anything that already had a side effect on the SAP system.

## When to Stop

Stop and ask the human when:

- The same command fails twice with the same authorization or endpoint
  error.
- A destructive operation returned a partial success (some tasks released,
  some not).
- A lock cannot be resolved without administrator help.
- A quality check is inconclusive but a downstream release is being
  proposed.

Stopping is always preferable to escalating a small failure into a
production incident.
