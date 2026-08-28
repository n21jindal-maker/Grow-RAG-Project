# Central configuration (model names, thresholds, paths)

import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
MANIFEST_PATH = os.path.join(DATA_DIR, "corpus_manifest.json")
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")
BM25_INDEX_PATH = os.path.join(BASE_DIR, "bm25_index.pkl")

# --- Phase 2: Chunking configuration ---
# Small table threshold: tables with <= this many data rows are kept as a single atomic chunk.
# Tables exceeding this are batched into TABLE_BATCH_SIZE-row sub-chunks.
TABLE_SMALL_THRESHOLD = 30
TABLE_BATCH_SIZE = 25  # rows per sub-chunk for large tables (header repeated per batch)

# --- Retrieval configuration ---
# NOTE: BAAI/bge-large-en-v1.5 cannot be used because sentence-transformers requires
# scikit-learn/scipy whose DLLs are blocked by Application Control policy on this machine.
# We use ChromaDB's built-in ONNXMiniLM_L6_V2 embedding function (all-MiniLM-L6-v2)
# which is ONNX-based and has no sklearn/scipy dependency.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # ONNX model used via chromadb.utils.embedding_functions.ONNXMiniLM_L6_V2
EMBEDDING_BACKEND = "onnx"  # 'onnx' = ChromaDB ONNXMiniLM_L6_V2 | 'st' = sentence-transformers (blocked)
CROSS_ENCODER_MODEL = "BAAI/bge-reranker-base"
TOP_K_RETRIEVAL = 10  # top-k for both vector search and BM25 (reduced from 20 per plan)
RRF_K = 60
TOP_K_RERANK = 3

# Legacy -- kept for backward compatibility but not used in Phase 2
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# LLM Configurations
PRIMARY_MODEL = "openai/gpt-oss-120b"
FALLBACK_MODEL = "llama-3.3-70b-versatile" # Groq
TEMPERATURE = 0.0
MAX_OUTPUT_TOKENS = 2000
RPM_LIMIT = 30
RPD_LIMIT = 1000
TPM_LIMIT = 8000
TPD_LIMIT = 200000
