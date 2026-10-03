# `sapevt`, `sapxpg`, `sapinst` — extended reference

Companion to the parent skill. **[G]** throughout — confirm against your version.

---

## 1. sapevt in practice

```bash
# by SID + instance number
sapevt <EVENTID> name=<SID> nr=<nr>

# by profile
sapevt <EVENTID> pf=/usr/sap/<SID>/SYS/profile/<SID>_<INSTANCE>_<host>

# with a parameter, and tracing on
sapevt Z_LOAD_DONE -p REGION_APAC -t name=PRD nr=00
```

### When "nothing happened"

Work the chain in this order — the failure is rarely `sapevt` itself:

1. **Did the event get raised?** Add `-t` and read `dev_evt` in the working directory.
2. **Is the event defined?** **SM62** — events must exist (customer events start with `Z`/`Y`).
3. **Is a job actually waiting on it?** **SM37**, start condition *After event*. A raised event with
   no waiting job is a no-op, not an error.
4. **Parameter mismatch?** A job waiting on event + parameter will not fire on the bare event.
5. **Right system?** `name=`/`nr=` or `pf=` may be addressing a different instance than you think.

> **Events are not queued for later job definitions.** Raising an event before the job is scheduled
> to wait for it accomplishes nothing — the ordering matters.

### Operational notes

- Run as **`<sid>adm`** so the environment resolves.
- **No SAP authentication is involved** — OS access is the only control. This is why `<sid>adm` shell
  access is effectively production job-control access.
- Safe to call repeatedly; each call raises the event again.

---

## 2. sapxpg / external commands

### Defining a command (SM69)

| Field | Guidance |
|---|---|
| **Command name** | Must start with **`Y`** or **`Z`** for customer commands |
| **Operating system** | The command is keyed by name **+ OS** — define per platform |
| **Operating system command** | Full path to the executable, **no arguments** |
| **Parameters** | Arguments go here |
| **Additional parameters allowed** | ⚠️ **Consider this argument injection** — see below |

### Security review checklist

Treat SM69 like a sudoers file. For each defined command ask:

- [ ] Does it need to exist at all, or is it a leftover from a project?
- [ ] Is **"additional parameters allowed"** switched on? If so, can a caller append arguments that
      change what runs (`;`, backticks, `--option=…`, a different target path)?
- [ ] Does the command point at a script in a **writable** directory? Whoever can write the script
      controls what runs as the SAP service user.
- [ ] Who holds **`S_LOG_COM`** for it, and for which host?
- [ ] Is it restricted to specific hosts, or open to any?

> This checklist is an operational judgement drawn from how the mechanism works, not a quoted SAP
> recommendation — but "external command definitions" is a standard audit finding, and worth folding
> into the periodic security work in `sap-security-patch`.

### Failure decoding

| Message | Look at |
|---|---|
| `Starting external program SAPXPG failed` | Target host's `sapstartsrv` / SAP Host Agent — running? reachable? correct host in the command? |
| `Can't exec external program (No such file or directory)` | Path; arguments wrongly in the command field; missing shebang/interpreter |
| Runs from the shell, fails from SAP | Environment: `sapxpg` does not inherit your interactive profile. Use absolute paths and set what you need inside a wrapper script |
| Wildcard/pattern errors | Restricted by design — see SAP KBA **1891781** |

**ABAP entry point:** `SXPG_COMMAND_EXECUTE`. Failures surface there with the same underlying causes.

---

## 3. sapinst / SWPM

### Unattended run

```bash
./sapinst \
  SAPINST_INPUT_PARAMETERS_URL=/path/inifile.xml \
  SAPINST_EXECUTE_PRODUCT_ID=<product_id> \
  SAPINST_SKIP_DIALOGS=true
```

### Artefacts and where they go

| Artefact | Note |
|---|---|
| `inifile.xml` | The reproducible record of every answer. **Copy it out of the install directory.** |
| `sapinst.log` | Human-readable progress |
| `sapinst_dev.log` | **The one with the real error** |
| `/tmp/sapinst_instdir/...` | Default install directory — **on `/tmp`; may not survive a reboot** |

### Practical guidance

- **Always use current SWPM.** It carries product definitions; an old copy cannot install a newer
  product. See `sap-software-download`.
- **The browser UI** (default port **4237**) replaced X11 — you need a browser reaching that port,
  not a `DISPLAY`.
- **Retry from the failed step** rather than restarting; sapinst keeps state in the install directory.
- **Treat `inifile.xml` as sensitive** — archive deliberately, never commit it, redact before sharing.
- If a run fails oddly on an HA system, check whether something moved underneath it — e.g. a SQL
  Server AlwaysOn failover triggered by sapinst's own service restart (see
  `sap-sqlserver-alwayson` §7).
