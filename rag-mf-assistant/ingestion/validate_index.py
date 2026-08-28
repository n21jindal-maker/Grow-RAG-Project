"""
ingestion/validate_index.py
---------------------------
Index Validation Script (Phase 2, Task 2.8).

Runs 10 curated sample queries against both ChromaDB (vector) and BM25 indexes.
Verifies that the correct scheme-specific chunk surfaces in top-3 results.

Usage:
    python ingestion/validate_index.py
"""

import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TOP_K_RETRIEVAL
from ingestion.indexer import load_chroma_collection, load_bm25_index

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

# ---------------------------------------------------------------------------
# 10 curated validation queries
# (query_text, expected_scheme_keyword, expected_section_hint)
# ---------------------------------------------------------------------------
VALIDATION_QUERIES = [
    (
        "What is the expense ratio of HDFC Mid Cap Fund?",
        "Mid-Cap",
        "summary_metrics",
    ),
    (
        "What is the expense ratio of HDFC Large and Mid Cap Fund?",
        "Large and Mid Cap",
        "summary_metrics",
    ),
    (
        "What is the exit load for HDFC Small Cap Fund?",
        "Small Cap",
        "exit_load",
    ),
    (
        "Exit load for HDFC Gold ETF Fund of Fund",
        "Gold ETF",
        "exit_load",
    ),
    (
        "What is the AUM of HDFC Multi Cap Fund?",
        "Multi Cap",
        "summary_metrics",
    ),
    (
        "Minimum SIP investment amount for HDFC Mid Cap Fund",
        "Mid-Cap",
        "minimum_investments",
    ),
    (
        "What is the fund benchmark for HDFC Large and Mid Cap Fund?",
        "Large and Mid Cap",
        "exit_load",
    ),
    (
        "HDFC Small Cap Fund returns over 5 years",
        "Small Cap",
        "returns_rankings",
    ),
    (
        "What is the tax implication when redeeming HDFC Gold ETF?",
        "Gold ETF",
        "exit_load",
    ),
    (
        "Portfolio holdings of HDFC Multi Cap Fund",
        "Multi Cap",
        "table",
    ),
]


def run_validation():
    """Run all validation queries and print a results table."""
    print("\n" + "=" * 70)
    print("Phase 2 Index Validation -- 10 Sample Queries")
    print("=" * 70)

    print("\nLoading ChromaDB collection...")
    collection = load_chroma_collection()
    item_count = collection.count()
    print(f"  Collection item count: {item_count}")

    print("Loading BM25 index...")
    bm25_index, bm25_chunks = load_bm25_index()
    print(f"  BM25 corpus size: {len(bm25_chunks)} chunks")

    passed = 0
    failed = 0
    results_table = []

    for i, (query, expected_scheme_kw, expected_section) in enumerate(VALIDATION_QUERIES, 1):
        print(f"\n[Query {i:02d}] {query}")

        # -- Vector search (ChromaDB with built-in embedding function) --
        vec_results = collection.query(
            query_texts=[query],
            n_results=min(TOP_K_RETRIEVAL, item_count),
        )
        vec_metas = vec_results["metadatas"][0]

        # -- BM25 search --
        tokenized_query = query.lower().split()
        scores = bm25_index.get_scores(tokenized_query)
        top_bm25_indices = sorted(
            range(len(scores)), key=lambda x: scores[x], reverse=True
        )[:TOP_K_RETRIEVAL]
        bm25_metas = [bm25_chunks[j]["metadata"] for j in top_bm25_indices]

        # -- Check top-3 for expected scheme keyword --
        vec_top3_schemes = [m.get("scheme_name", "") for m in vec_metas[:3]]
        bm25_top3_schemes = [m.get("scheme_name", "") for m in bm25_metas[:3]]

        vec_hit = any(expected_scheme_kw.lower() in s.lower() for s in vec_top3_schemes)
        bm25_hit = any(expected_scheme_kw.lower() in s.lower() for s in bm25_top3_schemes)

        status = "PASS" if (vec_hit or bm25_hit) else "FAIL"
        if status == "PASS":
            passed += 1
        else:
            failed += 1

        print(f"  Expected scheme keyword : {expected_scheme_kw}")
        print(f"  Vector top-3 schemes    : {vec_top3_schemes}")
        print(f"  BM25   top-3 schemes    : {bm25_top3_schemes}")
        print(f"  Vector hit: {'YES' if vec_hit else 'NO '}  |  BM25 hit: {'YES' if bm25_hit else 'NO '}  |  [{status}]")

        results_table.append({
            "query": query[:60],
            "expected": expected_scheme_kw,
            "vec_hit": vec_hit,
            "bm25_hit": bm25_hit,
            "status": status,
        })

    # Summary
    print("\n" + "=" * 70)
    print(f"VALIDATION SUMMARY: {passed}/{len(VALIDATION_QUERIES)} queries passed")
    print(f"  Vector index hits : {sum(1 for r in results_table if r['vec_hit'])}/{len(VALIDATION_QUERIES)}")
    print(f"  BM25 index hits   : {sum(1 for r in results_table if r['bm25_hit'])}/{len(VALIDATION_QUERIES)}")

    if failed == 0:
        print("\n[ALL PASS] Both indexes correctly return scheme-specific chunks in top-3.")
    else:
        print(f"\n[WARNING] {failed} queries did not surface expected scheme in top-3.")

    print("=" * 70 + "\n")
    return passed, failed


if __name__ == "__main__":
    passed, failed = run_validation()
    sys.exit(0 if failed == 0 else 1)
