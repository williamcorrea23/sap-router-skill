# Connection and Credentials

This file documents how the `sap-adt-commands` client resolves connection
details and credentials at runtime. Load this file when configuring a new SAP
destination, when a connection error mentions a missing environment variable,
or when an agent needs to confirm the credential resolution order.

## Destination Naming Convention

The recommended way to connect is the `--dest` flag with the format:

```text
SID_CLIENT_USER_LANG
```

- `SID` — three or four character SAP system ID, uppercase.
- `CLIENT` — logon client number (for example `100`).
- `USER` — logon user, uppercase.
- `LANG` — logon language (for example `EN`, `DE`, `VI`).

Generic example:

```text
DEV_100_DEVELOPER_EN
```

The client splits on underscores and expects exactly four parts. Names that do
not follow this format are rejected with an explanatory JSON error.

## Environment Variable Resolution

For a destination `SID_CLIENT_USER_LANG`, the client resolves values in this
order and takes the first hit:

| Value  | Resolution order                                                                 |
| ------ | -------------------------------------------------------------------------------- |
| url    | `--url` flag, then `SAP_<SID>_URL` env var                                       |
| user   | `--user` flag, then `SAP_<SID>_<USER>_USER` env var, then the `USER` part        |
| pwd    | `--pwd` flag, then `SAP_<SID>_<USER>_PWD` env var (**required**)                 |
| client | `--client` flag, else the `CLIENT` part of the destination                       |
| lang   | `--lang` flag, else the `LANG` part of the destination                           |

Environment variable resolution reads process environment first and then falls
back to `HKCU\Environment` in the Windows registry. This means values set with
`setx` become usable immediately in a fresh child process without an
interactive re-login.

Example resolution for `--dest DEV_100_DEVELOPER_EN`:

- `url` — `SAP_DEV_URL`
- `user` — `SAP_DEV_DEVELOPER_USER`, else `DEVELOPER`
- `pwd` — `SAP_DEV_DEVELOPER_PWD`
- `client` — `100`
- `lang` — `EN`

## Explicit Flags

The following explicit flags always override environment variables:

- `--url`
- `--user`
- `--pwd`
- `--client`
- `--lang`
- `--ca-bundle`
- `--insecure`

Explicit flags can also be used entirely without `--dest` for backward
compatibility with scripts that predate destination-based resolution.

The `--user` value is also used as the `adtcore:responsible` field when the
client creates ABAP objects. A separate responsible flag is not required.

## Human-Only Password Setup

Agents must never:

- Ask a user to paste a password into an AI conversation.
- Type a password into `setx`, `export`, or any other command the agent runs.
- Include a plaintext password on a generated command line.

The one-time setup below is performed by the human developer only. The base
URL is not a secret and can be set by the agent when the URL is known, but
the password variable must be set by the human:

```powershell
# URL — may be scripted by the agent when known
setx SAP_DEV_URL "https://sap.example.com:44300"

# Password — set by the human only
setx SAP_DEV_DEVELOPER_PWD "<password>"
```

The `SAP_<SID>_URL` value is shared across all users of that SID. The
`SAP_<SID>_<USER>_PWD` value is per user and never shared.

## Missing-Variable Behavior

When required values are missing, the client exits with a JSON error naming
exactly which variables to set:

```json
{
  "error": "Missing connection values for --dest DEV_100_DEVELOPER_EN",
  "set_once_with": [
    "setx SAP_DEV_URL \"<value>\"",
    "setx SAP_DEV_DEVELOPER_PWD \"<value>\""
  ]
}
```

The agent should treat this as a configuration issue and not a network
failure. After the human sets the missing values, retry the original command
as-is. No shell restart or session refresh is required, because the client
also reads directly from the registry.

## Client and Language Handling

- `sap-client` is sent as an HTTP header on every ADT request.
- `sap-language` is sent as an HTTP header on every ADT request.
- If neither the destination nor an explicit flag provides these values, the
  client falls back to `100` and `EN`.

## URL Handling

- The base URL should include the scheme and port, for example
  `https://sap.example.com:44300`.
- The URL should not include a trailing slash.
- Only HTTPS URLs should be used in production. HTTP is not blocked at the
  client level, but SAP ADT normally requires HTTPS.

## TLS Considerations

The client verifies the SAP server certificate against the system CA trust
store by default. This matches the standard `requests` behavior and is a
deliberate choice for a public, security-conscious project.

Corporate SAP environments frequently use certificates issued by an internal
certificate authority that the default Python truststore does not know about.
For those cases the client offers three explicit options:

| Option                              | Effect                                                                |
| ----------------------------------- | --------------------------------------------------------------------- |
| ``--ca-bundle <path>``              | Verify against a specific PEM CA bundle for this invocation.          |
| ``SAP_ADT_CA_BUNDLE=<path>``        | Same as ``--ca-bundle`` but persistent across invocations.            |
| ``--insecure``                      | Disable verification for this invocation. Warns on stderr.            |
| ``SAP_ADT_INSECURE=1``              | Disable verification via environment. Still cannot combine with CA.   |

Resolution precedence, first match wins:

```text
--ca-bundle           (CLI wins over env)
--insecure            (CLI wins over env)
SAP_ADT_CA_BUNDLE     (env)
SAP_ADT_INSECURE      (env)
system CA trust store (default — verify=True)
```

Environment values interpreted as true: ``1``, ``true``, ``yes``, ``on``.

Rules and safety notes:

- The client never falls back from secure verification to insecure mode
  automatically. A TLS failure remains a failure unless the user explicitly
  chose ``--insecure`` or supplied a working CA bundle.
- Combining ``--insecure`` (or ``SAP_ADT_INSECURE``) with ``--ca-bundle``
  (or ``SAP_ADT_CA_BUNDLE``) is a configuration error. The client fails
  fast with a JSON validation error instead of silently choosing one.
- When ``--insecure`` is active the client prints a single warning to
  ``stderr`` and suppresses only the expected ``urllib3``
  ``InsecureRequestWarning``. It does not print credentials, cookies,
  tokens, or authorization headers, and it does not globally suppress
  unrelated warnings.
- Prefer ``--ca-bundle`` or ``SAP_ADT_CA_BUNDLE`` for corporate SAP
  systems. ``--insecure`` is intended only for controlled troubleshooting
  and non-production environments.

Example: verify against a corporate CA bundle stored per-user with `setx`:

```powershell
setx SAP_ADT_CA_BUNDLE "C:\certs\corporate-root-ca.pem"
python .\scripts\adt-client.py --dest DEV_100_DEVELOPER_EN discovery
```

Example: one-off troubleshooting against a lab system without a valid cert:

```powershell
python .\scripts\adt-client.py --dest DEV_100_DEVELOPER_EN --insecure discovery
```

## Credential Handling Rules for Agents

1. Never paste passwords into the chat or into a command.
2. Never generate a `setx` or `export` line that contains a real password.
3. Never log or echo values read from `SAP_*_PWD` environment variables.
4. When a password variable is missing, print the exact `setx` command with a
   `<password>` placeholder and wait for the human to run it.
5. When a URL variable is missing, either ask the human for the URL or, if the
   base URL is known from a non-secret source, generate the `setx` for the URL
   only.
6. After the human confirms, retry the original command unchanged.

## Troubleshooting Missing Values

| Symptom                                        | Likely cause                                | Fix                                                                                       |
| ---------------------------------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `Missing connection values for --dest ...`     | `SAP_<SID>_URL` or `SAP_<SID>_<USER>_PWD` not set | Ask the human to set the missing variables with `setx` and retry.                       |
| `Authentication failed (HTTP 401)`             | Wrong password, wrong user, or wrong client | Verify the `USER`, `CLIENT` parts of the destination and the `SAP_<SID>_<USER>_PWD` var. |
| `Authentication failed (HTTP 403)`             | Missing SAP authorizations                  | Confirm the user has the ADT authorization objects needed for the operation.             |
| Connection timeout                             | Wrong URL, network path, or firewall        | Verify the URL and that the SAP host and port are reachable from this machine.           |
| TLS certificate verify failed                  | Private CA not in system trust store        | Supply ``--ca-bundle`` or ``SAP_ADT_CA_BUNDLE``. Use ``--insecure`` only as a last resort.|

## Do Not Store SAP Credentials in the Repository

Under no circumstances should any file in this repository contain:

- Real SAP passwords, tokens, cookies, or client certificates.
- Real customer SAP URLs, SIDs, or usernames.
- Screenshots or logs that expose the above.

Fictional placeholders such as `sap.example.com`, `DEV`, `100`, `DEVELOPER`,
`EN`, `ZEXAMPLE_PACKAGE`, and `DEVK900001` are always safe.
