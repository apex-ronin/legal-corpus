r"""
Build legal_corpus.faiss from corpus/*.json via a local LM Studio embedder.

Standalone equivalent of data-arsenal/pipeline/build_local_indexes.py
(--only legal), reading from THIS repo's corpus/ directory. Output goes to
G:\AI-Models\indexes (override with INDEX_DIR env var) — index artifacts
stay out of git.

Requires: faiss-cpu, numpy, requests; LM Studio serving
text-embedding-nomic-embed-text-v1.5 on localhost:1234.
"""

import datetime
import json
import os
import sys
from pathlib import Path

import faiss
import numpy as np
import requests

EMBED_URL = os.environ.get("LOCAL_LLM_BASE_URL", "http://localhost:1234/v1").rstrip("/") + "/embeddings"
EMBED_MODEL = "text-embedding-nomic-embed-text-v1.5"
EMBED_DIMS = 768
DOC_PREFIX = "search_document: "    # nomic v1.5 task prefixes — required
QUERY_PREFIX = "search_query: "
BATCH_SIZE = 64

CORPUS_DIR = Path(__file__).resolve().parents[1] / "corpus"
INDEX_DIR = Path(os.environ.get("INDEX_DIR", r"G:\AI-Models\indexes"))


def load_corpus() -> list[dict]:
    records = []
    for path in sorted(CORPUS_DIR.glob("*.json")):
        for c in json.loads(path.read_text(encoding="utf-8")):
            records.append({
                "id": c["id"],
                "source_file": path.name,
                "title": c.get("title", ""),
                "clause_text": c.get("clause_text", ""),
                "embed_text": f"{c['id']} {c.get('title', '')}. "
                              f"Keywords: {c.get('vector', '')}. {c.get('clause_text', '')}",
            })
    return records


def embed(texts: list[str]) -> np.ndarray:
    resp = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "input": texts}, timeout=300)
    resp.raise_for_status()
    data = sorted(resp.json()["data"], key=lambda d: d["index"])
    return np.array([d["embedding"] for d in data], dtype=np.float32)


def main() -> int:
    records = load_corpus()
    if not records:
        print(f"FAIL: no clauses found in {CORPUS_DIR}")
        return 1
    print(f"Embedding {len(records)} clauses via {EMBED_MODEL}...")

    chunks = []
    for b in range(0, len(records), BATCH_SIZE):
        batch = records[b:b + BATCH_SIZE]
        chunks.append(embed([DOC_PREFIX + r["embed_text"] for r in batch]))
    vectors = np.vstack(chunks)
    assert vectors.shape == (len(records), EMBED_DIMS), vectors.shape

    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(EMBED_DIMS)
    index.add(vectors)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_DIR / "legal_corpus.faiss"))
    with open(INDEX_DIR / "legal_corpus_meta.jsonl", "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps({k: v for k, v in r.items() if k != "embed_text"},
                               ensure_ascii=False) + "\n")

    manifest_path = INDEX_DIR / "index_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    manifest["legal_corpus"] = {
        "embedder": EMBED_MODEL,
        "embedder_serving": "LM Studio /v1/embeddings (localhost:1234)",
        "dimensions": EMBED_DIMS,
        "metric": "cosine (L2-normalized IndexFlatIP)",
        "doc_prefix": DOC_PREFIX,
        "query_prefix": QUERY_PREFIX,
        "record_count": len(records),
        "source": "jsnnlsn-prog/legal-corpus corpus/*.json",
        "index_file": "legal_corpus.faiss",
        "metadata_sidecar": "legal_corpus_meta.jsonl",
        "built_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"OK: {index.ntotal} vectors -> {INDEX_DIR / 'legal_corpus.faiss'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
