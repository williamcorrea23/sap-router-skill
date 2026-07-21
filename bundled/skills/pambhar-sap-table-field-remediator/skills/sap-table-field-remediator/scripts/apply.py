#!/usr/bin/env python3
"""apply.py — deterministic writer for the T1 `auto_apply` mechanical fixes.

The "auto-write" half of remediation. It takes the guard-blessed `auto_apply` findings
from a `remediation-report.json` and writes their mechanical, whole-word token swaps
(e.g. `KONV` -> `PRCD_ELEMENTS`) into the LOCAL `.abap` source files, emits a unified
diff, and records an audit log (`apply-log.json`). Nothing else is touched.

SCOPE / BOUNDARIES (read before trusting this):
  - LOCAL FILES ONLY. This edits files on disk. It does NOT push, transport, or activate
    anything in a SAP system — that requires system access the tool does not have and is
    the client's step. There is no ADT/RFC/transport here.
  - T1 ONLY. Only `action == "auto_apply"` findings are written. T2 (`propose`) and T3
    (`escalate`) fixes are variant-dependent and are authored by Claude interactively via
    its editor on human approval — never mechanically here. `verify`, `route_to_sibling`
    and `escalate` are ignored.
  - TRUSTS THE GUARD. guard.py already downgraded anything unsafe before it could reach
    `auto_apply`, so `auto_apply` IS the safe set. We do not re-run the guard here.
  - GIT IS THE BACKSTOP. The repo is version-controlled, so we write no backup files;
    `git checkout`/`git diff` is the revert/audit path.

Idempotent: after a real apply the `object` token is gone from the line, so a second run
drift-guards it out (SKIP) — that is correct, not an error.

Usage:
  python3 apply.py --report <remediation-report.json> --src <src-root> \
                   [--ledger <ledger.json>] [--log <apply-log.json>] [--dry-run]

`--src` is the root the findings' repo-relative `file` paths resolve against (findings use
`src/...`, so `--src /path/to/repo` reads `/path/to/repo/src/...`).
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import sys

GENERATOR = "apply.py"
SCHEMA_VERSION = "1.0"

# A replacement we can mechanically write must be a single bare identifier token
# (an ABAP object name, optionally namespaced with `/`). Anything with spaces/newlines
# is a phrase ("transparent tables per cluster ID") -> needs a human, so we skip it.
BARE_TOKEN = re.compile(r"^[A-Za-z_][A-Za-z0-9_/]*$")

# detect.js reports the STATEMENT-START line; on a multi-line SELECT the target table
# lives a few physical lines below (e.g. `SELECT ...` on line N, `FROM konv` on N+1). So
# we search from the finding line forward, bounded by this many lines or the ABAP
# statement terminator `.`, whichever comes first. This keeps the drift guard's intent
# (the object must still be present in THIS statement) while tolerating line wrapping.
STMT_WINDOW = 25


def finding_ref(file: str, object_: str, line) -> str:
    return f"{file}::{object_}::{line}"


def fingerprint(report: dict) -> str:
    """Byte-for-byte replica of worklist.py.fingerprint() so the ledger's stored
    fingerprint and this log's fingerprint compare equal for the same report."""
    blob = json.dumps(report.get("findings", []), sort_keys=True)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def word_re(token: str) -> re.Pattern:
    """Whole-word matcher for an ABAP object token.

    Case-INSENSITIVE: ABAP is case-insensitive and the source conventionally spells table
    names lowercase (`from konv`), while the catalog/finding spells them uppercase (`KONV`).
    Boundaries exclude identifier chars AND `/` so `gt_konv`, `konvx` and `/bi0/konv` do
    NOT partial-match, but a bare `konv` does.
    """
    return re.compile(
        r"(?<![A-Za-z0-9_/])" + re.escape(token) + r"(?![A-Za-z0-9_/])",
        re.IGNORECASE,
    )


def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def ledger_status_map(path: str) -> dict:
    """finding_ref -> status, from a worklist.py ledger. Empty if unreadable."""
    try:
        ledger = load_json(path)
    except (OSError, ValueError):
        sys.stderr.write(f"[apply] WARNING: could not read ledger {path}; ignoring it\n")
        return {}
    return {d.get("finding_ref"): d.get("status") for d in ledger.get("decisions", [])}


def split_comment(line: str) -> tuple[str, str]:
    """Split an ABAP source line into (code, comment) with `code + comment == line`.

    A full-line comment (first non-blank char is `*`) is entirely comment. Otherwise the
    first unquoted `"` starts an inline comment (single-quote `'...'` literals are honoured,
    so a `"` inside a string is code, not a comment marker). No comment -> comment is "".
    The token search and the `.` terminator scan run on the code half only, so tokens and
    `.`s that live in comments or string literals can't trigger a match or an early break.
    """
    if line.lstrip().startswith("*"):
        return "", line
    in_str = False
    for i, ch in enumerate(line):
        if ch == "'":
            in_str = not in_str
        elif ch == '"' and not in_str:
            return line[:i], line[i:]
    return line, ""


def stmt_terminates(code: str) -> bool:
    """True if the (already comment-stripped) code contains a `.` statement terminator
    outside a single-quote string literal — a `.` in `'3.14'` does NOT end the statement."""
    in_str = False
    for ch in code:
        if ch == "'":
            in_str = not in_str
        elif ch == "." and not in_str:
            return True
    return False


def find_token_line(lines: list[str], start_idx: int, pat: re.Pattern) -> int | None:
    """Return the 0-based index of the first physical line (from start_idx, within the
    statement window) whose CODE (comment/string stripped) contains the whole-word token,
    or None. Stops after the line that ends the statement (a real, unquoted `.`), which is
    still checked for the token first."""
    end = min(len(lines), start_idx + STMT_WINDOW)
    for i in range(start_idx, end):
        code, _comment = split_comment(lines[i])
        if pat.search(code):
            return i
        if stmt_terminates(code):  # ABAP statement terminator — don't wander past it
            break
    return None


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Write T1 auto_apply mechanical fixes into local ABAP source (diffs "
                    "+ audit log). Local files only — never pushes to a SAP system.")
    ap.add_argument("--report", required=True, help="path to remediation-report.json")
    ap.add_argument("--src", required=True,
                    help="root the findings' repo-relative file paths resolve against")
    ap.add_argument("--ledger", default=None,
                    help="optional ledger; skip findings a human rejected/deferred")
    ap.add_argument("--log", default=None,
                    help="apply-log.json path (default: alongside the report)")
    ap.add_argument("--dry-run", action="store_true",
                    help="preview only: no source/log writes; log JSON printed to stdout")
    args = ap.parse_args()

    # --- fatal preconditions ------------------------------------------------ #
    try:
        report = load_json(args.report)
    except FileNotFoundError:
        sys.stderr.write(f"FATAL: report not found: {args.report}\n")
        return 2
    except ValueError as e:
        sys.stderr.write(f"FATAL: report is not valid JSON: {e}\n")
        return 2
    if not os.path.isdir(args.src):
        sys.stderr.write(f"FATAL: --src root not found or not a directory: {args.src}\n")
        return 2

    led_status = ledger_status_map(args.ledger) if args.ledger else {}

    log_path = args.log or os.path.join(
        os.path.dirname(os.path.abspath(args.report)), "apply-log.json")

    applied: list[dict] = []
    skipped: list[dict] = []
    # Per-file working state: path -> {"orig": <text>, "lines": [physical lines]}.
    files: dict[str, dict] = {}

    for f in report.get("findings", []):
        if f.get("action") != "auto_apply":
            continue  # T2/T3/verify/route/escalate are not ours to write

        obj = f.get("object", "")
        repl = f.get("replacement")
        ref = finding_ref(f.get("file"), obj, f.get("line"))

        # 1) respect a human rejection/deferral recorded in the ledger
        st = led_status.get(ref)
        if st in ("rejected", "deferred"):
            skipped.append({"finding_ref": ref, "reason": f"ledger status '{st}' — respecting human decision"})
            continue

        # 2) replacement must be a single bare token we can swap
        if not isinstance(repl, str) or not BARE_TOKEN.match(repl):
            skipped.append({"finding_ref": ref, "reason": "replacement not a bare token — needs manual apply"})
            continue

        # 3) in-place field changes (MATNR->MATNR) carry replacement == object: there is
        #    no token to swap; the real fix is a length/declaration change a human makes.
        if repl.upper() == obj.upper():
            skipped.append({"finding_ref": ref, "reason": "replacement equals object — no token swap (in-place field change; manual apply)"})
            continue

        # 4) resolve the file under --src
        abspath = os.path.join(args.src, f.get("file", ""))
        if not os.path.isfile(abspath):
            skipped.append({"finding_ref": ref, "reason": f"source file not found under --src: {f.get('file')}"})
            continue

        if abspath not in files:
            with open(abspath, "r", newline="") as fh:
                text = fh.read()
            files[abspath] = {"orig": text, "lines": text.splitlines(keepends=True)}
        lines = files[abspath]["lines"]

        line_no = f.get("line", 0)
        start_idx = line_no - 1  # 1-indexed -> 0-indexed
        if start_idx < 0 or start_idx >= len(lines):
            skipped.append({"finding_ref": ref, "reason": f"line {line_no} out of range for file"})
            continue

        # 5) drift guard: the object token must still be present in this statement
        pat = word_re(obj)
        idx = find_token_line(lines, start_idx, pat)
        if idx is None:
            skipped.append({"finding_ref": ref, "reason": f"drift — object token not found at line {line_no}"})
            continue

        before = lines[idx]
        code, comment = split_comment(before)  # never rewrite a trailing comment
        # Case polish: mirror the matched token's case so demo diffs blend with the
        # surrounding SQL (ABAP is case-insensitive, so this is cosmetic only).
        def _sub(m: re.Match) -> str:
            return repl.lower() if m.group(0).islower() else repl
        after = pat.sub(_sub, code) + comment  # swap ALL whole-word occurrences in code
        if after == before:  # defensive: nothing actually changed
            skipped.append({"finding_ref": ref, "reason": f"drift — object token not found at line {line_no}"})
            continue
        lines[idx] = after
        applied.append({
            "finding_ref": ref,
            "file": f.get("file"),
            "line": line_no,
            "object": obj,
            "replacement": repl,
            "before_line": before.rstrip("\n"),
            "after_line": after.rstrip("\n"),
        })

    # --- unified diff (per file, only files that changed) ------------------- #
    diff_lines: list[str] = []
    for abspath, st in files.items():
        new_text = "".join(st["lines"])
        if new_text == st["orig"]:
            continue
        rel = os.path.relpath(abspath, args.src)
        diff_lines.extend(difflib.unified_diff(
            st["orig"].splitlines(), new_text.splitlines(),
            fromfile=f"a/{rel}", tofile=f"b/{rel}", lineterm=""))
    diff_text = "\n".join(diff_lines)

    changed_files = sum(1 for st in files.values() if "".join(st["lines"]) != st["orig"])

    log = {
        "schema_version": SCHEMA_VERSION,
        "generator": GENERATOR,
        "report_ref": args.report,
        "report_fingerprint": fingerprint(report),
        "applied": applied,
        "skipped": skipped,
        "applied_count": len(applied),
        "skipped_count": len(skipped),
        "dry_run": bool(args.dry_run),
    }

    if args.dry_run:
        # Preview: diff + summary to stderr, would-be log to stdout. No writes.
        if diff_text:
            sys.stderr.write(diff_text + "\n")
        else:
            sys.stderr.write("[apply] (dry-run) no changes to preview\n")
        sys.stderr.write(
            f"[apply] DRY-RUN would write {len(applied)} fix(es) to {changed_files} file(s), "
            f"skip {len(skipped)}\n")
        print(json.dumps(log, indent=2))
        return 0

    # Real run: diff to stdout, write files, write log.
    if diff_text:
        print(diff_text)
    for abspath, st in files.items():
        new_text = "".join(st["lines"])
        if new_text == st["orig"]:
            continue
        with open(abspath, "w", newline="") as fh:
            fh.write(new_text)

    with open(log_path, "w") as fh:
        json.dump(log, fh, indent=2)
        fh.write("\n")

    if applied:
        sys.stderr.write(
            f"[apply] wrote {len(applied)} fix(es) to {changed_files} file(s), "
            f"skipped {len(skipped)} (dry_run=False). Log: {log_path}\n")
    else:
        sys.stderr.write(
            f"[apply] nothing applied (0 fixes); skipped {len(skipped)}. "
            f"Log: {log_path} (dry_run=False)\n")
    sys.stderr.write(
        "[apply] NOTE: local files only — not pushed/activated in any SAP system "
        "(that is the client's step).\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
