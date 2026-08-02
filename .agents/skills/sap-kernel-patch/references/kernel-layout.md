# Kernel directory layout, `sapcpe`, and the SAR file map

Reference detail for [../SKILL.md](../SKILL.md).

## Central vs instance exe, and `sapcpe`

| Location | Role |
|----------|------|
| **Central exe** — UNIX `/sapmnt/<SID>/exe/uc/<platform>` (= `/usr/sap/<SID>/SYS/exe/uc/<platform>` via symlink); Windows `\\<host>\sapmnt\<SID>\SYS\exe\uc\<platform>` | the master copy you **patch** |
| **Instance exe** — `/usr/sap/<SID>/<INST><nr>/exe` | per-instance local copy the instance actually runs |

On instance start, **`sapcpe`** compares the central exe against the instance exe and copies newer files
down (per the `sapcpeftlist`/`*.lst` file lists). So: **patch the central exe, then restart** — `sapcpe`
propagates. Don't hand-edit only the instance exe; it gets overwritten on the next start.

`<platform>` examples: `linuxx86_64` (Linux x86-64), `rs6000_64` (AIX/Power), `NTAMD64` (Windows x64),
`linuxppc64le` (Linux on Power).

## SAR file map (what to download & extract)

Extract order: DB-independent → DB-dependent → the rest.

| Archive | Contents | Notes |
|---------|----------|-------|
| `SAPEXE_<PL>-*.SAR` | **DB-independent** kernel (disp+work, sapstartsrv, sapcontrol, sappfpar, cleanipc, R3trans, tp, …) | always |
| `SAPEXEDB_<PL>-*.SAR` | **DB-dependent** kernel (the DB library / `dbsl`) | pick the one for your `dbms_type` |
| `dw_<PL>-*.sar` | updated `disp+work` (dw) | when a note calls for a newer dw only |
| `lib_dbsl_<PL>-*.sar` | DB interface library | targeted DBSL fixes |
| `igsexe_<PL>-*.sar` | Internet Graphics Service | if IGS is patched |
| `SAPHOSTAGENT<PL>.SAR` | SAP Host Agent | separate lifecycle — see SKILL §3 |
| `SAPCAR` | the extractor itself | standalone exe per platform |

Match **release** (e.g. 7.53 / 7.77 / 7.89), **patch level**, **platform**, **Unicode** (modern kernels are
Unicode-only), and for `SAPEXEDB` the **database**. Download per SAP Note 19466.

## After extraction (UNIX permissions)

`saproot.sh <SID>` sets the required ownership and setuid bits (root-owned binaries such as `icmbnd`,
`sapuxuserchk`). Run it from the exe directory as root after every extract, and after a rollback. Skipping
it is the classic "kernel patched but instance won't start / permission errors in dev_disp" cause.

## Sources

Same as [../SKILL.md](../SKILL.md) §Sources: SAP Note 19466 + kernel patching process [KP1], version
verification [KP2]. `sapcpe` / exe-list behaviour: SAP kernel documentation on help.sap.com.
