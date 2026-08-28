"""
ingestion/indexer.py
--------------------
Embedding Generation + ChromaDB Indexing + BM25 Index (Phase 2, Tasks 2.5-2.7).

Uses ChromaDB's built-in SentenceTransformerEmbeddingFunction to avoid scipy/sklearn
DLL dependency issues. The embedding function internally uses the `transformers` library
directly, bypassing scikit-learn entirely.

Pipeline:
  1. Chunk all documents via chunker.chunk_all_documents()
  2. Embed + persist to ChromaDB using SentenceTransformerEmbeddingFunction
  3. Build and serialize a BM25 index (rank_bm25) over the same corpus
"""

import os
import sys
import pickle
import logging
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    PROCESSED_DATA_DIR,
    CHROMA_DB_DIR,
    BM25_INDEX_PATH,
    EMBEDDING_MODEL,
    TOP_K_RETRIEVAL,
)

logger = logging.getLogger(__name__)

# Module-level singletons
_embedding_fn = None
_chroma_client = None
_chroma_collection = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_index(chunks=None, reset=False):
    """
    Build or rebuild the full index (ChromaDB + BM25) from the given chunks.

    Args:
        chunks: Pre-computed chunks list. If None, chunk_all_documents() is called.
        reset:  If True, wipe and recreate the ChromaDB collection before indexing.

    Returns:
        dict with keys: 'chroma_collection', 'bm25_index', 'chunk_count'
    """
    if chunks is None:
        from ingestion.chunker import chunk_all_documents
        chunks = chunk_all_documents()

    if not chunks:
        raise ValueError("No chunks produced -- check processed data directory.")

    logger.info("Building index from %d chunks...", len(chunks))

    # 1. Build ChromaDB index (embedding handled internally by the EF)
    logger.info("Persisting to ChromaDB at: %s", CHROMA_DB_DIR)
    collection = _build_chroma_index(chunks, reset=reset)

    # 2. Build BM25 index
    logger.info("Building BM25 index...")
    bm25_index, bm25_chunks = _build_bm25_index(chunks)
    _save_bm25_index(bm25_index, bm25_chunks)
    logger.info("BM25 index saved to: %s", BM25_INDEX_PATH)

    logger.info("Index build complete. %d chunks indexed.", len(chunks))
    return {
        "chroma_collection": collection,
        "bm25_index": bm25_index,
        "chunk_count": len(chunks),
    }


def load_chroma_collection(collection_name="mf_chunks"):
    """Load (or create) the ChromaDB persistent collection with the embedding function."""
    global _chroma_client, _chroma_collection
    if _chroma_collection is not None:
        return _chroma_collection

    import chromadb

    ef = get_embedding_function()
    Path(CHROMA_DB_DIR).mkdir(parents=True, exist_ok=True)
    _chroma_client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    _chroma_collection = _chroma_client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return _chroma_collection


def load_bm25_index():
    """
    Load the serialized BM25 index from disk.
    Returns: (bm25_index, chunks_list)
    """
    bm25_path = Path(BM25_INDEX_PATH)
    if not bm25_path.exists():
        raise FileNotFoundError(
            f"BM25 index not found at {BM25_INDEX_PATH}. Run build_index() first."
        )
    with open(bm25_path, "rb") as f:
        data = pickle.load(f)
    return data["bm25"], data["chunks"]


def get_embedding_function():
    """
    Lazy-load ChromaDB's ONNXMiniLM_L6_V2 embedding function (singleton).
    This is a pure-ONNX runtime embedding -- no sklearn/scipy dependency.
    The ONNX model (all-MiniLM-L6-v2) is auto-downloaded to ~/.cache/chroma/onnx_models/.
    """
    global _embedding_fn
    if _embedding_fn is None:
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
        logger.info("Loading ONNX embedding function (all-MiniLM-L6-v2)...")
        _embedding_fn = ONNXMiniLM_L6_V2()
    return _embedding_fn


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_chroma_index(chunks, reset=False):
    """
    Insert chunks into ChromaDB. The SentenceTransformerEmbeddingFunction
    handles embedding generation internally during upsert.
    """
    import chromadb

    ef = get_embedding_function()
    Path(CHROMA_DB_DIR).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))

    collection_name = "mf_chunks"
    if reset:
        try:
            client.delete_collection(collection_name)
            logger.info("Deleted existing ChromaDB collection '%s'", collection_name)
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    # Upsert in batches of 50 (ChromaDB limit per call)
    batch_size = 50
    total_batches = (len(chunks) - 1) // batch_size + 1
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i: i + batch_size]
        ids = [c["chunk_id"] for c in batch]
        documents = [c["text"] for c in batch]
        metadatas = [_flatten_metadata(c) for c in batch]

        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        logger.info(
            "  ChromaDB upsert batch %d/%d (%d chunks)",
            i // batch_size + 1,
            total_batches,
            len(batch),
        )

    global _chroma_client, _chroma_collection
    _chroma_client = client
    _chroma_collection = collection
    return collection


def _build_bm25_index(chunks):
    """Build a BM25 index over all chunk texts."""
    from rank_bm25 import BM25Okapi
    tokenized_corpus = [_tokenize(c["text"]) for c in chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    return bm25, chunks


def _save_bm25_index(bm25_index, chunks):
    """Pickle the BM25 index and aligned chunks list to disk."""
    bm25_path = Path(BM25_INDEX_PATH)
    bm25_path.parent.mkdir(parents=True, exist_ok=True)
    with open(bm25_path, "wb") as f:
        pickle.dump({"bm25": bm25_index, "chunks": chunks}, f)


def _tokenize(text):
    """Simple whitespace + lowercase tokenizer for BM25."""
    return text.lower().split()


def _flatten_metadata(chunk):
    """
    ChromaDB requires metadata values to be str/int/float/bool.
    Flatten the chunk dict into a single-level metadata dict.
    """
    meta = dict(chunk.get("metadata", {}))
    meta["chunk_type"] = chunk.get("chunk_type", "")
    meta["section_key"] = chunk.get("section_key", "")
    meta["table_index"] = chunk.get("table_index", -1)
    meta["batch_index"] = chunk.get("batch_index", -1)
    for k, v in list(meta.items()):
        if not isinstance(v, (str, int, float, bool)):
            meta[k] = str(v)
    return meta


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    result = build_index(reset=True)
    print(f"\nIndex build complete.")
    print(f"  Chunks indexed : {result['chunk_count']}")
    print(f"  ChromaDB path  : {CHROMA_DB_DIR}")
    print(f"  BM25 path      : {BM25_INDEX_PATH}")

    # Quick smoke test
    print("\nSmoke test -- querying ChromaDB for 'expense ratio'...")
    collection = result["chroma_collection"]
    q_results = collection.query(
        query_texts=["what is the expense ratio"],
        n_results=3,
    )
    for doc, meta in zip(q_results["documents"][0], q_results["metadatas"][0]):
        scheme = meta.get("scheme_name", "?")
        ctype = meta.get("chunk_type", "?")
        print(f"  [{scheme} | {ctype}] {doc[:120]}")
