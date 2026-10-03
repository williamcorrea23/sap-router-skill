# `sapgenpse` — command reference and troubleshooting

Companion to the parent skill. **[G]** throughout — assembled from SAP Help Portal pages and Notes;
`sapgenpse <command> -h` on the host is authoritative for your CommonCryptoLib version.

---

## 1. Environment first, always

```bash
echo $SECUDIR                      # PSE + credential location
echo $SNC_LIB                      # which crypto library
ls -l $SECUDIR                     # what is actually there
sapgenpse -v                       # CommonCryptoLib version
```

Typical `SECUDIR` values:

| Context | Path |
|---|---|
| AS ABAP instance | `/usr/sap/<SID>/<INSTANCE>/sec` |
| SAProuter | the saprouter working directory (often `/usr/sap/saprouter`) |
| Standalone client | wherever set; **must** be set explicitly |

> Running `sapgenpse` with the wrong (or unset) `SECUDIR` is the single most common way to "fix" a
> certificate and change nothing. It does not warn you.

---

## 2. Command summary

| Command | Purpose |
|---|---|
| `get_my_name -p <pse> [-x <PIN>]` | Show the PSE's own DN and validity — **best first diagnostic** |
| `get_my_name -v -n Issuer` | Show the issuer specifically |
| `gen_pse -p <pse> -x <PIN> "<DN>"` | Create a PSE with a self-signed certificate |
| `get_pse -p <pse> <snc_name>` | Create an SNC PSE for a given SNC name |
| `get_pse -r <csr_file> -p <pse> -x <PIN> "<DN>"` | Create PSE **and** emit a certificate signing request |
| `import_own_cert -c <cert> -p <pse> [-x <PIN>]` | Install the CA-signed reply into the **same** PSE |
| `export_own_cert -o <file> -p <pse> [-x <PIN>]` | Export the own certificate |
| `maintain_pk -p <pse> [-x <PIN>]` | **List** the trusted certificate list |
| `maintain_pk -a <cert> -p <pse> [-x <PIN>]` | **Add** a certificate to the trust list |
| `maintain_pk -d <n> -p <pse> [-x <PIN>]` | **Delete** trust-list entry number `<n>` |
| `seclogin -p <pse> -x <PIN> -O <os_user>` | Create the `cred_v2` credential for an OS user |
| `seclogin -p <pse> -l` | List credentials |
| `export_p12 / import_p12` | PKCS#12 exchange (where supported) |

**Common options:** `-p` PSE file, `-x` PIN, `-O` OS user, `-v` verbose, `-a` add, `-d` delete,
`-r` request file, `-c` certificate file, `-o` output file.

---

## 3. The two workflows that cover most work

### A. New certificate from a CA

```bash
# 1. request  (creates the PSE if it does not exist)
sapgenpse get_pse -v -r certreq -p SAPSSLS.pse -x <PIN> \
  "CN=host.example.com, OU=IT, O=Example, C=MY"

# 2. send certreq to the CA, receive the signed reply (plus any intermediates)

# 3. import the CA chain into the trust list FIRST, then the own certificate
sapgenpse maintain_pk -a <root_ca>.crt -p SAPSSLS.pse -x <PIN>
sapgenpse maintain_pk -a <intermediate>.crt -p SAPSSLS.pse -x <PIN>
sapgenpse import_own_cert -c <signed>.crt -p SAPSSLS.pse -x <PIN>

# 4. rebind credentials and verify
sapgenpse seclogin -p SAPSSLS.pse -x <PIN> -O <sid>adm
sapgenpse get_my_name -p SAPSSLS.pse -x <PIN>

# 5. restart the consumer (ICM, saprouter, …) — PSEs are read at start
```

> **Import the chain before the own certificate.** If the issuing chain is not trusted, the own
> certificate import can succeed while the resulting PSE still cannot present a valid chain.

### B. Renewal of an existing PSE

The safe pattern is **back up, then renew in place**:

```bash
cp $SECUDIR/SAPSSLS.pse $SECUDIR/SAPSSLS.pse.$(date +%Y%m%d)
# then follow workflow A against the same PSE
```

Keep the old PSE until the new certificate is confirmed working end-to-end — reverting is then a file
copy plus a `seclogin` plus a restart.

---

## 4. Troubleshooting

| Symptom | Likely cause |
|---|---|
| `GSS-API(maj): No credentials were supplied` | **`cred_v2` binding.** The process cannot open the PSE as its OS user. Re-run `seclogin -O <the actual runtime user>` |
| Works as `<sid>adm`, fails for the service | Same as above — different OS user |
| Certificate looks right, TLS still fails | Missing **intermediate** in the trust list, or the consumer was not restarted |
| `sapgenpse` changes have no effect | **`SECUDIR` wrong** — you edited a different PSE |
| STRUST and file system disagree | Both are views of the same store; refresh STRUST, and remember AS ABAP caches |
| Import fails with key mismatch | The CSR was generated in a **different PSE** than the one you are importing into |
| Everything expired at once | Common with SAProuter — the certificate has a fixed validity; **diary the expiry** |

**Diagnostic order:** `echo $SECUDIR` → `get_my_name` → `maintain_pk` (is the chain there?) →
`seclogin -l` (is the credential there, for the right user?) → restart.

---

## 5. Platform notes

| Platform | Notes |
|---|---|
| **Linux / AIX** | `sapgenpse` in the kernel directory (`/usr/sap/<SID>/SYS/exe/run` or the saprouter dir); `SNC_LIB` → `libsapcrypto.so` |
| **Windows** | `sapgenpse.exe`; `SNC_LIB` → `sapcrypto.dll`. `seclogin` binds to the **Windows account** running the service — commonly `SAPService<SID>`, **not** `<sid>adm`. This asymmetry is the usual Windows-specific failure |
| **AIX** | As Linux; watch that the environment is set for the right user in `.profile` |

> On Windows, remember there are **two** relevant accounts: `<sid>adm` (interactive/admin) and
> `SAPService<SID>` (the service). A credential created for the wrong one produces exactly the
> "works when I test it" symptom.

---

## 6. Relationship to STRUST

**STRUST** is the ABAP transaction over the same PSE store. Practical consequences:

- Changes made with `sapgenpse` may need STRUST refreshed (and sometimes an ICM restart) to take effect.
- STRUST is the right tool for AS ABAP's own SSL PSEs in day-to-day work; `sapgenpse` is the right
  tool when the system is down, for SAProuter, for standalone clients, and for scripting.
- **They are not independent** — do not treat "I did it in STRUST" and "I did it with sapgenpse" as
  two separate configurations.
