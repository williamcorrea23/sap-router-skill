#!/usr/bin/env python3
"""Synchronize, index, and search external SAP skills and MCP candidates.

The catalog is deliberately fail-closed: synchronization and discovery never
make an MCP executable. Reviewed servers remain governed by mcps.json.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import stat
import tempfile
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REGISTRIES = ROOT / ".agents" / "registries"
SOURCES_FILE = REGISTRIES / "bundled-sources.json"
LOCK_FILE = REGISTRIES / "bundled-sources.lock.json"
INDEX_FILE = REGISTRIES / "bundled-assets.json"
MCP_CANDIDATES_FILE = REGISTRIES / "mcp-candidates.json"
SKILLS_DIR = ROOT / ".agents" / "skills"

CAPABILITY_TERMS = {
    "sap.adt.source.read": ("abap", "adt", "source code", "abap development"),
    "sap.adt.source.write": ("abap", "adt", "activate", "create class", "modify source"),
    "sap.gui.transaction.execute": ("sap gui", "sapgui", "transaction", "scripting", "com automation"),
    "sap.cap.model.search": ("sap cap", "cap cds", "cap-js", "cloud application programming"),
    "sap.cap.project.build": ("sap cap", "cap cds", "cap-js", "cap project"),
    "sap.ui5.project.validate": ("ui5", "sapui5", "fiori"),
    "sap.cpi.artifact.read": ("cpi", "integration suite", "iflow", "integration flow"),
    "sap.apim.proxy.read": ("apim", "api management", "api proxy"),
    "sap.transport.read": ("transport", "trkorr", "cts", "charm"),
    "sap.transport.modify": ("release transport", "transport gate", "deploy transport"),
    "sap.successfactors.data.read": ("successfactors", "sfapi", "employee central", "odata v2"),
    "sap.documentation.search": ("documentation", "docs", "wiki", "knowledge base"),
    "sap.finance.implementation.guide": ("finance", "fico", "s/4hana finance", "accounting"),
    "sap.logistics.process.guide": ("logistics", "warehouse", "material", "supply chain"),
    "sap.btp.operations.read": ("btp", "cloud foundry", "kyma", "sre", "automation pilot"),
    "agent.context.execute": ("context mode", "ctx_execute", "sandboxed execution"),
    "agent.context.fetch": ("ctx_fetch", "fetch and index", "context mode"),
    "agent.context.memory": ("ctx_checkpoint", "ctx_restore", "session memory"),
    "agent.output.optimize": ("rtk", "token optimizer", "output compression", "token savings"),
}

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_.+/-]{1,}", re.I)


def load(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, encoding="utf-8", errors="replace")


def remove_tree(path: Path) -> None:
    def make_writable(function: Any, name: str, _error: Any) -> None:
        target = Path(name)
        target.chmod(target.stat().st_mode | stat.S_IWRITE)
        function(name)
    shutil.rmtree(path, onexc=make_writable)


def source_root(config: dict[str, Any]) -> Path:
    return ROOT / config.get("default_checkout_root", "sources")


def sync(one: str | None = None, update: bool = False) -> int:
    config = load(SOURCES_FILE, {})
    root = source_root(config)
    root.mkdir(parents=True, exist_ok=True)
    old_lock = {item["id"]: item for item in load(LOCK_FILE, {}).get("sources", [])}
    locked: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    selected = [s for s in config.get("sources", []) if not one or s["id"] == one]
    if one and not selected:
        raise SystemExit(f"unknown source: {one}")
    for spec in selected:
        if spec.get("repository") == "bundled":
            existing = old_lock.get(spec["id"])
            if existing and (ROOT / existing.get("path", "")).is_dir():
                locked.append(existing)
                print(f"BUNDLED {spec['id']} {existing.get('revision', 'unpinned')[:12]}")
                continue
            failures.append({"id": spec["id"], "error": "bundled source is missing from the repository"})
            continue
        category = "mcps" if spec.get("kind") == "mcp" else ("tools" if spec.get("kind") == "tool" else "skills")
        target = root / category / spec["id"]
        previous = old_lock.get(spec["id"], {})
        if target.exists() and any(target.iterdir()) and not update:
            revision = previous.get("revision")
            if not revision:
                remote_head = run(["git", "ls-remote", spec["repository"], "HEAD"])
                revision = remote_head.stdout.split()[0] if remote_head.returncode == 0 and remote_head.stdout.split() else "bundled-unpinned"
            branch = previous.get("branch")
        else:
            temp_parent = ROOT / "scratch" / "source-import"
            temp_parent.mkdir(parents=True, exist_ok=True)
            temp_dir = Path(tempfile.mkdtemp(prefix=f"{spec['id']}-", dir=temp_parent))
            checkout = temp_dir / "checkout"
            result = run(["git", "clone", "--depth", "1", "--filter=blob:none", spec["repository"], str(checkout)])
            if result.returncode:
                shutil.rmtree(temp_dir, ignore_errors=True)
                failures.append({"id": spec["id"], "error": result.stderr.strip()})
                continue
            revision = run(["git", "rev-parse", "HEAD"], checkout).stdout.strip()
            branch = run(["git", "branch", "--show-current"], checkout).stdout.strip()
            for git_meta in sorted(checkout.rglob(".git"), key=lambda p: len(p.parts), reverse=True):
                if git_meta.is_dir():
                    remove_tree(git_meta)
                else:
                    git_meta.unlink()
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                remove_tree(target)
            shutil.move(str(checkout), str(target))
            shutil.rmtree(temp_dir, ignore_errors=True)
        license_names = sorted(p.name for p in target.glob("LICEN[CS]E*") if p.is_file())
        locked.append({**spec, "repository": "bundled", "origin": spec["repository"],
                       "path": target.relative_to(ROOT).as_posix(), "revision": revision,
                       "branch": branch or None, "license_files": license_names})
        print(f"SYNCED {spec['id']} {revision[:12]}")
        merged = {item["id"]: item for item in old_lock.values()}
        merged.update({item["id"]: item for item in locked})
        write_json(LOCK_FILE, {"schema_version": 1, "generated_at": now(),
                              "sources": sorted(merged.values(), key=lambda x: x["id"]), "failures": failures})
    if one:
        locked_ids = {item["id"] for item in locked}
        locked.extend(item for key, item in old_lock.items() if key not in locked_ids)
    write_json(LOCK_FILE, {"schema_version": 1, "generated_at": now(), "sources": sorted(locked, key=lambda x: x["id"]), "failures": failures})
    return 1 if failures else 0


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_text(path: Path, limit: int = 30000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except OSError:
        return ""


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    result: dict[str, str] = {}
    lines = text[3:end].splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            value = value.strip().strip("'\"")
            if value in (">", ">-", "|", "|-"):
                chunks = []
                index += 1
                while index < len(lines) and (not lines[index].strip() or lines[index].startswith((" ", "\t"))):
                    chunks.append(lines[index].strip())
                    index += 1
                result[key.strip()] = " ".join(chunk for chunk in chunks if chunk)
                continue
            result[key.strip()] = value
        index += 1
    return result


def infer_capabilities(text: str) -> list[str]:
    normalized = text.lower()
    return sorted(
        cap for cap, terms in CAPABILITY_TERMS.items()
        if any(re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", normalized) for term in terms)
    )


def tokens(text: str) -> list[str]:
    return sorted(set(match.group(0).lower() for match in TOKEN_RE.finditer(text)))


def skill_asset(source: dict[str, Any], root: Path, path: Path) -> dict[str, Any]:
    body = safe_text(path)
    meta = frontmatter(body)
    rel = path.relative_to(root).as_posix()
    title = meta.get("name") or path.parent.name
    description = meta.get("description") or next((line.strip("# ") for line in body.splitlines() if line.startswith("#")), title)
    corpus = f"{title} {description}"
    return {"id": f"{source['id']}:{rel}", "kind": "skill", "name": title,
            "description": description[:1000], "source_id": source["id"],
            "repository": source["repository"], "revision": source.get("revision"),
            "path": (Path(source["path"]) / rel).as_posix(), "capabilities": infer_capabilities(corpus),
            "title_keywords": tokens(f"{title} {description}"), "keywords": tokens(corpus),
            "trust": "bundled_unreviewed", "status": "searchable"}


def repository_asset(source: dict[str, Any], root: Path, kind: str) -> dict[str, Any]:
    readme = next(iter(sorted(root.glob("README*"))), None)
    body = safe_text(readme) if readme else ""
    package_fragments = []
    for name in ("package.json", "pyproject.toml", "setup.py", "requirements.txt", "mcp.json"):
        path = root / name
        if path.exists():
            package_fragments.append(safe_text(path, 10000))
    corpus = f"{source['id']} {body} {' '.join(package_fragments)}"
    description = next((line.strip("# ") for line in body.splitlines() if line.startswith("#")), source["id"])
    default_status = "disabled_candidate" if kind == "mcp" else "searchable"
    return {"id": f"{source['id']}:repository", "kind": kind, "name": source["id"],
            "description": description[:1000], "source_id": source["id"], "repository": source["repository"],
            "revision": source.get("revision"), "path": source["path"], "capabilities": infer_capabilities(corpus),
            "title_keywords": tokens(f"{source['id']} {description}"), "keywords": tokens(corpus),
            "trust": source.get("trust", "bundled_unreviewed"), "status": source.get("status", default_status)}


def canonical_assets() -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    for path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        body = safe_text(path)
        meta = frontmatter(body)
        name = meta.get("name") or path.parent.name
        description = meta.get("description", name)
        corpus = f"{name} {description}"
        assets.append({"id": f"canonical:{name}", "kind": "skill", "name": name,
                       "description": description[:1000], "source_id": "canonical", "repository": "local",
                       "revision": None, "path": path.relative_to(ROOT).as_posix(),
                       "capabilities": infer_capabilities(corpus), "title_keywords": tokens(f"{name} {description}"), "keywords": tokens(corpus),
                       "trust": "canonical", "status": "enabled"})
    mcps = load(REGISTRIES / "mcps.json", {}).get("servers", [])
    for server in mcps:
        corpus = json.dumps(server, ensure_ascii=False)
        assets.append({"id": f"registered-mcp:{server['id']}", "kind": "mcp", "name": server["id"],
                       "description": server.get("display_name", server["id"]), "source_id": "registered",
                       "repository": server.get("source", {}).get("repository"), "revision": server.get("source", {}).get("version"),
                       "path": ".agents/registries/mcps.json", "capabilities": server.get("capabilities", infer_capabilities(corpus)),
                       "title_keywords": tokens(f"{server['id']} {server.get('display_name', '')}"), "keywords": tokens(corpus),
                       "trust": "reviewed", "status": server.get("status", "disabled"),
                       "priority": server.get("routing", {}).get("priority", 999)})
    for candidate in load(MCP_CANDIDATES_FILE, {}).get("candidates", []):
        corpus = json.dumps(candidate, ensure_ascii=False)
        assets.append({"id": f"fallback-mcp:{candidate['id']}", "kind": "mcp", "name": candidate["id"],
                       "description": candidate.get("description", candidate["id"]), "source_id": "fallback",
                       "repository": "local .mcp.json", "revision": None, "path": ".mcp.json",
                       "capabilities": infer_capabilities(corpus), "title_keywords": tokens(f"{candidate['id']} {candidate.get('description', '')}"),
                       "keywords": tokens(corpus), "trust": "fallback", "status": "disabled_candidate"})
    return assets


def build_index() -> int:
    config = load(SOURCES_FILE, {})
    lock = {item["id"]: item for item in load(LOCK_FILE, {}).get("sources", [])}
    assets = canonical_assets()
    missing = []
    for declared in config.get("sources", []):
        source = lock.get(declared["id"])
        if not source:
            missing.append(declared["id"])
            continue
        root = ROOT / source["path"]
        skill_paths = sorted({*root.rglob("SKILL.md"), *root.rglob("skill.md")})
        assets.extend(skill_asset(source, root, path) for path in skill_paths if ".git" not in path.parts)
        kind = declared.get("kind", "auto")
        mcp_markers = list(root.rglob("*mcp*server*"))[:1] or ([root / "mcp.json"] if (root / "mcp.json").exists() else [])
        if kind == "mcp" or (kind == "auto" and mcp_markers):
            assets.append(repository_asset(source, root, "mcp"))
        if kind == "tool":
            assets.append(repository_asset(source, root, "tool"))
        if kind == "skills" and not skill_paths:
            assets.append(repository_asset(source, root, "knowledge"))
    write_json(INDEX_FILE, {"schema_version": 1, "generated_at": now(), "policy": "fail_closed",
                            "asset_count": len(assets), "missing_sources": missing, "assets": assets})
    print(f"INDEXED {len(assets)} assets; missing sources: {len(missing)}")
    return 0


def score_asset(asset: dict[str, Any], query: str, kind: str | None, capability: str | None) -> float:
    if kind and asset.get("kind") != kind:
        return -1
    if capability and capability not in asset.get("capabilities", []):
        return -1
    query_tokens = tokens(query)
    haystack = set(asset.get("keywords", []))
    title = set(asset.get("title_keywords", []))
    overlap = sum(1 for token in query_tokens if token in haystack)
    title_overlap = sum(1 for token in query_tokens if token in title) * 2
    phrase = 4 if query.lower() in f"{asset.get('name','')} {asset.get('description','')}".lower() else 0
    capability_bonus = 3 * sum(1 for cap in infer_capabilities(query) if cap in asset.get("capabilities", []))
    trust_bonus = {"canonical": 3, "reviewed": 2, "bundled_unreviewed": 0, "fallback": -1}.get(asset.get("trust"), 0)
    ready_bonus = 2 if asset.get("status") == "enabled" else 0
    priority_bonus = max(0, (100 - int(asset.get("priority", 100))) / 100)
    return round(overlap + title_overlap + phrase + capability_bonus + trust_bonus + ready_bonus + priority_bonus, 3)


def search(query: str, kind: str | None, capability: str | None, limit: int) -> int:
    if not INDEX_FILE.exists():
        build_index()
    data = load(INDEX_FILE, {})
    ranked = []
    for asset in data.get("assets", []):
        score = score_asset(asset, query, kind, capability)
        if score > 0:
            ranked.append({"score": score, **{k: asset.get(k) for k in ("id", "kind", "name", "description", "capabilities", "status", "trust", "path", "repository")}})
    ranked.sort(key=lambda item: (-item["score"], item["id"]))
    print(json.dumps({"query": query, "policy": "bundled MCPs remain disabled until reviewed", "results": ranked[:limit]}, indent=2, ensure_ascii=True))
    return 0 if ranked else 1


def status() -> int:
    config = load(SOURCES_FILE, {})
    lock = load(LOCK_FILE, {})
    index = load(INDEX_FILE, {})
    print(json.dumps({"declared_sources": len(config.get("sources", [])), "synced_sources": len(lock.get("sources", [])),
                      "sync_failures": lock.get("failures", []), "indexed_assets": index.get("asset_count", 0),
                      "missing_sources": index.get("missing_sources", [])}, indent=2, ensure_ascii=False))
    return 1 if lock.get("failures") else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Repository-owned SAP skill/MCP catalog")
    sub = parser.add_subparsers(dest="command", required=True)
    sync_p = sub.add_parser("sync")
    sync_p.add_argument("--source")
    sync_p.add_argument("--update", action="store_true")
    sub.add_parser("index")
    search_p = sub.add_parser("search")
    search_p.add_argument("query")
    search_p.add_argument("--kind", choices=("skill", "mcp", "tool", "knowledge"))
    search_p.add_argument("--capability")
    search_p.add_argument("--limit", type=int, default=10)
    sub.add_parser("status")
    args = parser.parse_args()
    if args.command == "sync":
        return sync(args.source, args.update)
    if args.command == "index":
        return build_index()
    if args.command == "search":
        return search(args.query, args.kind, args.capability, args.limit)
    return status()


if __name__ == "__main__":
    raise SystemExit(main())
