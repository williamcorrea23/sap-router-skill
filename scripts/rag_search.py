#!/usr/bin/env python3
"""
SAP RAG Search — Pinecone vector search for ABAP/SAP knowledge.

Usage:
  python scripts/rag_search.py "BAPI_MATERIAL_SAVEDATA example"
  python scripts/rag_search.py "how to create CDS view with parameters"
  python scripts/rag_search.py --top 5 "SELECT FOR ALL ENTRIES performance"

Requires:
  pip install requests python-dotenv
  .env with PINECONE_API_KEY, PINECONE_INDEX, PINECONE_ENVIRONMENT
  DEEPSEEK_API_KEY or GEMINI_API_KEY for embeddings
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent

# --- Load .env ---
try:
    from dotenv import load_dotenv
    load_dotenv(SKILL_DIR / ".env")
except ImportError:
    pass  # dotenv not installed, assume vars are already set

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX", "abap-hub-sap-rag")
PINECONE_ENV = os.environ.get("PINECONE_ENVIRONMENT", "aped-4627-b74a")
PINECONE_HOST = f"https://{PINECONE_INDEX}-bbrber0.svc.{PINECONE_ENV}.pinecone.io"

# --- Embedding provider ---
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")


def _embed_deepseek(texts, model="deepseek-chat"):
    """DeepSeek chat model — use as fallback with basic keyword extraction.
    DeepSeek v4 doesn't have a dedicated embedding endpoint.
    We use a lightweight local fallback instead."""
    return None  # DeepSeek has no embedding API


def _embed_gemini(text, model="gemini-embedding-001"):
    """Google Gemini embedding (1536 dim via outputDimensionality)."""
    import urllib.request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent?key={GEMINI_KEY}"
    body = json.dumps({
        "model": f"models/{model}",
        "content": {"parts": [{"text": text}]},
        "outputDimensionality": 1536
    }).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data["embedding"]["values"]
    except Exception as e:
        print(f"  Gemini embedding error: {e}", file=sys.stderr)
        return None


def _embed_simple(text, dim=1536):
    """Simple hash-based embedding for testing. NOT semantically meaningful.
    Only use when no real embedding API is available."""
    # Deterministic pseudo-embedding from text hash
    h = hashlib.sha256(text.encode()).digest()
    vec = []
    for i in range(dim):
        byte_idx = i % len(h)
        vec.append(((h[byte_idx] / 255.0) * 2) - 1)
    return vec


def embed(texts):
    """Embed text(s). Returns list of vectors or None."""
    if isinstance(texts, str):
        texts = [texts]

    # Try Gemini first
    if GEMINI_KEY:
        results = []
        for t in texts:
            vec = _embed_gemini(t)
            if vec is None:
                return None
            results.append(vec)
        return results

    # Fallback: simple hash embedding (works but lower quality)
    print("  WARNING: No embedding API key. Using hash-based embedding (low quality).",
          file=sys.stderr)
    return [_embed_simple(t) for t in texts]


def query_pinecone(vector, top_k=5, namespace="", filter_dict=None):
    """Query Pinecone index with a vector."""
    import urllib.request
    url = f"{PINECONE_HOST}/query"
    body = {
        "vector": vector,
        "topK": top_k,
        "includeMetadata": True,
        "includeValues": False,
        "namespace": namespace,
    }
    if filter_dict:
        body["filter"] = filter_dict

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={
            "Api-Key": PINECONE_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  Pinecone query error: {e}", file=sys.stderr)
        return None


def search(query_text, top_k=5, namespace=""):
    """Full RAG search: embed query -> search Pinecone -> return results."""
    if not PINECONE_API_KEY:
        print("ERROR: PINECONE_API_KEY not set in .env", file=sys.stderr)
        return None

    print(f"  Embedding query: {query_text[:60]}...")
    vectors = embed(query_text)
    if vectors is None:
        return None

    print(f"  Searching Pinecone index={PINECONE_INDEX}, top_k={top_k}...")
    result = query_pinecone(vectors[0], top_k=top_k, namespace=namespace)
    return result


def format_results(results, show_metadata=True):
    """Pretty-print search results."""
    if results is None:
        print("No results.")
        return

    matches = results.get("matches", [])
    namespace = results.get("namespace", "")

    print(f"\n{'='*70}")
    print(f"Results: {len(matches)} matches (namespace: '{namespace}')")
    print(f"{'='*70}")

    for i, m in enumerate(matches):
        score = m.get("score", 0)
        vid = m.get("id", "?")
        meta = m.get("metadata", {})

        print(f"\n--- Match {i+1} (score={score:.4f}) ---")
        print(f"  ID: {vid}")

        if show_metadata and meta:
            for key in ["title", "type", "module", "description", "topic"]:
                if key in meta:
                    print(f"  {key}: {meta[key]}")

            # Show text snippet
            text = meta.get("text", meta.get("content", meta.get("chunk", "")))
            if text:
                text_short = str(text)[:300]
                print(f"  text: {text_short}...")

            # Show other metadata keys
            other = [k for k in meta if k not in
                     ("title", "type", "module", "description", "topic", "text", "content", "chunk")]
            if other:
                print(f"  meta keys: {', '.join(other)}")

    print(f"\n{'='*70}")
    print(f"Use in prompt: concatenate top matches as context for LLM.")
    print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(
        description="SAP RAG Search — query Pinecone for ABAP/SAP knowledge"
    )
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--top", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--namespace", default="", help="Pinecone namespace")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--test", action="store_true", help="Test Pinecone connection only")
    args = parser.parse_args()

    if not PINECONE_API_KEY:
        print("ERROR: PINECONE_API_KEY not set.", file=sys.stderr)
        print("Run: cp .env.template .env  and fill PINECONE_API_KEY", file=sys.stderr)
        sys.exit(1)

    if args.test:
        import urllib.request
        url = f"{PINECONE_HOST}/describe_index_stats"
        req = urllib.request.Request(url, data=b"{}", headers={
            "Api-Key": PINECONE_API_KEY,
            "Content-Type": "application/json",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            stats = json.loads(resp.read())
        print(json.dumps(stats, indent=2))
        return

    if not args.query:
        parser.print_help()
        sys.exit(1)

    results = search(args.query, top_k=args.top, namespace=args.namespace)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        format_results(results)


if __name__ == "__main__":
    main()
