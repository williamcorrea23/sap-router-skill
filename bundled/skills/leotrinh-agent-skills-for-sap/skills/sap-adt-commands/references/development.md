# Development

This file documents how to run the Python source, how to install runtime
dependencies, and how contributors can optionally build a local executable
for their own use. Load this file when setting up a workstation or when
troubleshooting a runtime problem.

The default distribution model of this repository is **source-only**. The
Python source at `scripts/adt-client.py` is the reference implementation and
the only supported entry point on the default branch. No prebuilt executable
ships with the repository. A user who wants a single-file entry point can
build one locally with PyInstaller using the steps below; that build is the
responsibility of the person who built it.

Future official releases, if introduced later, would be published through
GitHub Releases with a controlled build process, not committed to the
default branch.

## Python Runtime Requirements

- Python 3.10 or newer. The source uses `X | None` PEP 604 union types and
  modern typing syntax, so Python 3.9 is not supported.
- Python 3.13 is known to work on Windows 11.

Verify with:

```powershell
python --version
```

Use the `py` launcher (`py --version`) on Windows if the `python` alias is
not present.

## Python Dependencies

`scripts/adt-client.py` imports:

- `requests` — HTTP client.
- `urllib3` — used to selectively suppress the expected insecure-request
  warning only when the user explicitly opted in with `--insecure`.

Standard-library modules used: `argparse`, `difflib`, `json`, `os`, `re`,
`sys`, `time`, `urllib.parse`, and (on Windows) `winreg`.

Third-party packages are pinned in `requirements.txt` at the skill root.

### Installation

Create a virtual environment and install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\skills\sap-adt-commands\requirements.txt
```

Or run without a venv when the packages are already available in the
active Python environment.

## Running the Python Source

Once the dependencies are installed:

```powershell
python .\skills\sap-adt-commands\scripts\adt-client.py --help
python .\skills\sap-adt-commands\scripts\adt-client.py --dest DEV_100_DEVELOPER_EN discovery
```

The `--help` output lists every supported subcommand. It is authoritative
for command names and flag spellings when the documentation and the
implementation disagree.

## Optional Local Build (Contributors)

The repository ships `scripts/adt-client.spec` as a PyInstaller build
configuration for contributors who want to package the client as a
single-file executable for their own use. The `.spec` file is a build hint
only; it is not run at install time and it does not produce any artifact
that is committed back to the repository.

If you choose to build a local executable, do so at your own risk. Locally
built binaries are not code-signed, not independently audited, and not
reproducibly built by this project. Users who prefer not to run prebuilt
executables should keep running the Python source instead.

### Build Command

Reproduce a local single-file executable with:

```powershell
python -m pip install pyinstaller
python -m PyInstaller `
  --onefile --console --name "adt-client" `
  --distpath ".\dist" `
  --workpath "$env:TEMP\pyinstaller-adt-client\build" `
  --specpath "$env:TEMP\pyinstaller-adt-client" `
  ".\skills\sap-adt-commands\scripts\adt-client.py"
```

The resulting file lands under `.\dist\adt-client.exe`. Do **not** commit
that file to the repository.

### Verifying a Locally Built Executable

If you want to record the hash of a local build for your own tracking, use:

```powershell
Get-FileHash .\dist\adt-client.exe -Algorithm SHA256
```

This is a personal integrity check and has no relationship with any
official checksum, because no official binary is distributed here.

## Source-Vs-Binary Relationship

- The Python source is authoritative.
- Any local executable produced by a contributor is a rebuilt artifact of a
  specific commit of `scripts/adt-client.py`.
- After any change to `scripts/adt-client.py`, previously built local
  executables are stale until they are rebuilt.

## Why the Python Source Is the Default

- Full transparency: every line can be read before running.
- Easier to patch, especially for corporate CA bundles or proxy settings.
- Smaller download for CI environments that already provide Python.
- Independent of Windows and PyInstaller build tooling.
- Portable to Linux and macOS without a separate build.

## Limitations of Local Executables

- Windows only when built with the recommended PyInstaller command; Linux
  and macOS users must use the Python source.
- Not code-signed. Depending on your endpoint security posture, running an
  unsigned executable may require additional approval.
- Startup is slower than direct Python execution because PyInstaller
  extracts the bundle at launch.
- No installer. Users copy the file into place manually.
