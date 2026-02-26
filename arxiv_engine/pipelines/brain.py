#!/usr/bin/env python3
"""Local semantic search for arxiv knowledge base."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sqlite3
from pathlib import Path
from typing import Iterable, TypedDict

from arxiv_engine.core.utils import get_arxiv_root, read_text_safe

DB_NAME = ".brain.sqlite"
HASH_VECTOR_DIM = 256
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SENTENCE_BACKEND = "sentence-transformers"
CHUNK_CHARS = 1200
CHUNK_OVERLAP = 200
TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")

_BACKEND: "EmbeddingBackend | None" = None
_WARNED_MISSING = False


class SearchResult(TypedDict):
    score: float
    source: str
    path: str
    chunk_index: int
    content: str


class EmbeddingBackend:
    name: str
    dim: int

    def encode(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class HashEmbedding(EmbeddingBackend):
    name = "hash"

    def __init__(self, dim: int = HASH_VECTOR_DIM) -> None:
        self.dim = dim

    def encode(self, texts: list[str]) -> list[list[float]]:
        return [hash_vector(text, self.dim) for text in texts]


class SentenceTransformerEmbedding(EmbeddingBackend):
    name = SENTENCE_BACKEND

    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]

        self.model_name = model_name
        self._model = SentenceTransformer(model_name)
        self.dim = int(self._model.get_sentence_embedding_dimension())

    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        )
        return [list(vector) for vector in vectors]


def chunk_text(
    text: str, max_chars: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP
) -> list[str]:
    if not text:
        return []
    if max_chars <= overlap:
        overlap = 0
    chunks: list[str] = []
    step = max_chars - overlap
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(text_len, start + max_chars)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= text_len:
            break
        start += step
    return chunks


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def warn_fallback_to_hash(reason: str) -> None:
    global _WARNED_MISSING
    if _WARNED_MISSING:
        return
    _WARNED_MISSING = True
    print(
        f"Warning: {reason}. Falling back to hash embeddings. "
        "Install with: pip install -r requirements.txt"
    )


def load_sentence_backend(model_name: str) -> EmbeddingBackend | None:
    try:
        return SentenceTransformerEmbedding(model_name)
    except Exception as exc:
        print(f"Warning: failed to load sentence-transformers ({exc}).")
        return None


def get_embedding_backend() -> EmbeddingBackend:
    global _BACKEND
    if _BACKEND is not None:
        return _BACKEND
    backend = load_sentence_backend(EMBEDDING_MODEL)
    if backend is None:
        warn_fallback_to_hash("sentence-transformers unavailable")
        backend = HashEmbedding()
    _BACKEND = backend
    return backend


def select_backend_for_query(meta: dict[str, str]) -> EmbeddingBackend | None:
    backend_name = meta.get("embedding_backend", HashEmbedding.name)
    if backend_name == HashEmbedding.name:
        return HashEmbedding()
    if backend_name == SENTENCE_BACKEND:
        model_name = meta.get("embedding_model", EMBEDDING_MODEL)
        backend = load_sentence_backend(model_name)
        if backend is None:
            print(
                "Index built with sentence-transformers. Install dependencies and retry."
            )
        return backend
    print(f"Unknown embedding backend: {backend_name}")
    return None


def hash_vector(text: str, dim: int = HASH_VECTOR_DIM) -> list[float]:
    tokens = tokenize(text)
    if not tokens:
        return [0.0] * dim
    vector = [0.0] * dim
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        idx = int.from_bytes(digest, "big") % dim
        vector[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0.0:
        return vector
    return [v / norm for v in vector]


def ensure_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS chunks ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "source TEXT NOT NULL,"
        "path TEXT NOT NULL,"
        "chunk_index INTEGER NOT NULL,"
        "content TEXT NOT NULL,"
        "vector TEXT NOT NULL"
        ")"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
    )


def iter_source_files(root: Path) -> Iterable[tuple[Path, str]]:
    if not root.exists():
        return
    try:
        category_dirs = list(root.iterdir())
    except OSError:
        return

    for category_dir in category_dirs:
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue
        try:
            project_dirs = list(category_dir.iterdir())
        except OSError:
            continue
        for project_dir in project_dirs:
            if not project_dir.is_dir() or project_dir.name.startswith("."):
                continue
            summary = project_dir / "SUMMARY.md"
            if summary.exists():
                yield summary, "summary"
            info = project_dir / "info.yaml"
            if info.exists():
                yield info, "info"
            playground_dir = project_dir / "playground"
            if playground_dir.exists():
                for py_file in playground_dir.rglob("*.py"):
                    yield py_file, "code"


def get_db_path(root: Path) -> Path:
    return root / DB_NAME


def build_index() -> int:
    root = get_arxiv_root()
    if not root.exists():
        print(f"Knowledge root not found: {root}")
        return 0

    db_path = get_db_path(root)
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as exc:
        print(f"Failed to open index db: {exc}")
        return 0

    count = 0
    try:
        backend = get_embedding_backend()
        ensure_tables(conn)
        conn.execute("DELETE FROM chunks")
        conn.execute("DELETE FROM meta")
        conn.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?)",
            ("vector_dim", str(backend.dim)),
        )
        conn.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?)",
            ("chunk_chars", str(CHUNK_CHARS)),
        )
        conn.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?)",
            ("chunk_overlap", str(CHUNK_OVERLAP)),
        )
        conn.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?)",
            ("embedding_backend", backend.name),
        )
        if isinstance(backend, SentenceTransformerEmbedding):
            conn.execute(
                "INSERT INTO meta (key, value) VALUES (?, ?)",
                ("embedding_model", backend.model_name),
            )

        for path, source in iter_source_files(root):
            text = read_text_safe(path)
            if not text:
                continue
            chunks = chunk_text(text)
            if not chunks:
                continue
            try:
                vectors = backend.encode(chunks)
            except Exception as exc:
                print(f"Warning: embedding failed for {path}: {exc}")
                continue
            if len(vectors) != len(chunks):
                print(f"Warning: embedding mismatch for {path}")
                continue
            for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
                conn.execute(
                    "INSERT INTO chunks (source, path, chunk_index, content, vector) VALUES (?, ?, ?, ?, ?)",
                    (source, str(path), idx, chunk, json.dumps(vector)),
                )
                count += 1
        conn.commit()
    except sqlite3.Error as exc:
        print(f"Index build failed: {exc}")
    finally:
        conn.close()

    print(f"Indexed {count} chunks into {db_path}")
    return count


def load_meta(conn: sqlite3.Connection) -> dict[str, str]:
    meta: dict[str, str] = {}
    try:
        for key, value in conn.execute("SELECT key, value FROM meta"):
            meta[str(key)] = str(value)
    except sqlite3.Error:
        return {}
    return meta


def query_brain(text: str, top_k: int = 5) -> list[SearchResult]:
    root = get_arxiv_root()
    db_path = get_db_path(root)
    if not db_path.exists():
        print("Index not found. Run: arxiv brain index")
        return []

    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as exc:
        print(f"Failed to open index db: {exc}")
        return []

    results: list[SearchResult] = []
    try:
        meta = load_meta(conn)
        backend = select_backend_for_query(meta)
        if backend is None:
            return []
        if meta.get("vector_dim") and int(meta["vector_dim"]) != backend.dim:
            print("Index vector dimension mismatch. Rebuild index.")
            return []

        query_vectors = backend.encode([text])
        if not query_vectors:
            print("Query is empty after tokenization.")
            return []
        query_vec = query_vectors[0]
        if not any(query_vec):
            print("Query is empty after tokenization.")
            return []

        cursor = conn.execute(
            "SELECT source, path, chunk_index, content, vector FROM chunks"
        )
        for source, path, chunk_index, content, vector_json in cursor:
            try:
                vector = json.loads(vector_json)
            except json.JSONDecodeError:
                continue
            if not vector or len(vector) != len(query_vec):
                continue
            score = sum(a * b for a, b in zip(query_vec, vector))
            if score <= 0.0:
                continue
            results.append(
                {
                    "score": float(score),
                    "source": str(source),
                    "path": str(path),
                    "chunk_index": int(chunk_index),
                    "content": str(content),
                }
            )
    except sqlite3.Error as exc:
        print(f"Query failed: {exc}")
        return []
    finally:
        conn.close()

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


def format_preview(text: str, limit: int = 240) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def main() -> None:
    parser = argparse.ArgumentParser(description="Local arxiv knowledge search")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("index", help="Build local index")

    ask_parser = subparsers.add_parser("ask", help="Query the local index")
    ask_parser.add_argument("text", help="Query text")
    ask_parser.add_argument("--top-k", type=int, default=5, dest="top_k")

    args = parser.parse_args()

    if args.command == "index":
        build_index()
        return

    if args.command == "ask":
        results = query_brain(args.text, top_k=args.top_k)
        if not results:
            print("No matches found.")
            return
        for item in results:
            print(
                f"[{item['score']:.3f}] {item['path']} "
                f"(source={item['source']}, chunk={item['chunk_index']})"
            )
            print(format_preview(item["content"]))
            print()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
