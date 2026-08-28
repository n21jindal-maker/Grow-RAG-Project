"""
ingestion/chunker.py
--------------------
Section-Keyed Chunker for RAG MF Assistant (Phase 2, Tasks 2.1-2.4).

Reads pre-structured processed JSON files from data/processed/ and emits chunks.

Chunk types produced:
  - 'section'     : One chunk per section key in the JSON `sections` dict
  - 'table'       : Small tables (<= TABLE_SMALL_THRESHOLD rows) as single atomic chunk
  - 'table_batch' : Large tables (> TABLE_SMALL_THRESHOLD rows) batched into
                    sub-chunks of TABLE_BATCH_SIZE rows, header row repeated in each

Exit load deduplication:
  The exit_load section contains historical dated entries. This chunker strips
  all historical rules and retains only the most-recent / current rule.
"""

import json
import re
import uuid
import logging
from pathlib import Path
from collections import Counter
from langchain_text_splitters import RecursiveCharacterTextSplitter

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    PROCESSED_DATA_DIR,
    TABLE_SMALL_THRESHOLD,
    TABLE_BATCH_SIZE,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Section keys guaranteed by the preprocessor
# ---------------------------------------------------------------------------
SECTION_KEYS = [
    "summary_metrics",
    "exit_load",
    "returns_rankings",
    "minimum_investments",
    "about",
    "full_content",
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def chunk_document(processed_json_path) -> list:
    """
    Load one processed JSON file and return a list of chunk dicts.

    Each chunk contains:
        chunk_id    : str  -- UUID4 hex
        text        : str  -- self-contained markdown text
        chunk_type  : str  -- 'section' | 'table' | 'table_batch'
        section_key : str  -- source section key (or 'table' for table chunks)
        table_index : int  -- index in JSON tables[] (-1 for section chunks)
        batch_index : int  -- sub-chunk index for table_batch (-1 otherwise)
        metadata    : dict -- full metadata from the JSON file
    """
    path = Path(processed_json_path)
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)

    if doc.get("status") != "success":
        logger.warning("Skipping %s -- status is not 'success'", path.name)
        return []

    metadata = doc.get("metadata", {})
    sections = doc.get("sections", {})
    tables = doc.get("tables", [])
    chunks = []

    # -- 1. Section chunks --------------------------------------------------
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    for key in SECTION_KEYS:
        raw_text = sections.get(key, "").strip()
        if not raw_text:
            logger.debug("Section '%s' empty in %s -- skipping", key, path.name)
            continue

        if key == "exit_load":
            raw_text = _deduplicate_exit_load(raw_text)

        header = _build_section_header(key, metadata)
        
        if len(raw_text) > 1500 or key == "full_content":
            sub_chunks = text_splitter.split_text(raw_text)
            for sub_idx, sub_text in enumerate(sub_chunks):
                chunk_text = header + f"(Part {sub_idx+1}/{len(sub_chunks)})\n" + sub_text
                chunks.append(_make_chunk(
                    text=chunk_text,
                    chunk_type="section",
                    section_key=key,
                    table_index=-1,
                    batch_index=-1,
                    metadata=metadata,
                ))
        else:
            chunk_text = header + raw_text
            chunks.append(_make_chunk(
                text=chunk_text,
                chunk_type="section",
                section_key=key,
                table_index=-1,
                batch_index=-1,
                metadata=metadata,
            ))

    # -- 2. Table chunks ----------------------------------------------------
    for t_idx, table_md in enumerate(tables):
        rows = _get_data_rows(table_md)
        row_count = len(rows)
        if row_count == 0:
            continue

        table_label = _infer_table_label(table_md, t_idx)
        context_prefix = _build_table_context(table_label, metadata)

        if row_count <= TABLE_SMALL_THRESHOLD:
            # Atomic chunk -- keep full table as-is
            chunks.append(_make_chunk(
                text=context_prefix + table_md.strip(),
                chunk_type="table",
                section_key="table",
                table_index=t_idx,
                batch_index=-1,
                metadata=metadata,
            ))
        else:
            # Large table: batch into sub-chunks of TABLE_BATCH_SIZE rows
            header_row, separator_row = _extract_header(table_md)
            batches = _batch_rows(rows, TABLE_BATCH_SIZE)
            for b_idx, batch in enumerate(batches):
                start_row = b_idx * TABLE_BATCH_SIZE + 1
                end_row = b_idx * TABLE_BATCH_SIZE + len(batch)
                batch_md = header_row + "\n" + separator_row + "\n" + "\n".join(batch)
                chunk_text = (
                    context_prefix
                    + f"(rows {start_row}-{end_row} of {row_count})\n\n"
                    + batch_md.strip()
                )
                chunks.append(_make_chunk(
                    text=chunk_text,
                    chunk_type="table_batch",
                    section_key="table",
                    table_index=t_idx,
                    batch_index=b_idx,
                    metadata=metadata,
                ))

    return chunks


def chunk_all_documents(processed_dir=None) -> list:
    """
    Chunk every processed JSON file in processed_dir.
    Returns a flat list of all chunks across all documents.
    """
    data_dir = Path(processed_dir) if processed_dir else Path(PROCESSED_DATA_DIR)
    all_chunks = []

    json_files = sorted(data_dir.glob("*_processed.json"))
    if not json_files:
        logger.warning("No processed JSON files found in %s", data_dir)
        return []

    for json_file in json_files:
        logger.info("Chunking: %s", json_file.name)
        doc_chunks = chunk_document(json_file)
        logger.info("  -> %d chunks produced", len(doc_chunks))
        all_chunks.extend(doc_chunks)

    logger.info("Total chunks across corpus: %d", len(all_chunks))
    return all_chunks


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _make_chunk(*, text, chunk_type, section_key, table_index, batch_index, metadata):
    """Construct a chunk dict with a fresh UUID."""
    return {
        "chunk_id": uuid.uuid4().hex,
        "text": text.strip(),
        "chunk_type": chunk_type,
        "section_key": section_key,
        "table_index": table_index,
        "batch_index": batch_index,
        "metadata": dict(metadata),
    }


def _build_section_header(section_key, metadata):
    """
    Prefix a section chunk with scheme context so the chunk is self-contained
    (critical for embedding quality -- embedding model sees full context).
    """
    scheme = metadata.get("scheme_name", "Unknown Scheme")
    last_updated = metadata.get("last_updated", "")
    key_label = section_key.replace("_", " ").title()
    return f"Scheme: {scheme}\nSection: {key_label}\nLast Updated: {last_updated}\n\n"


def _build_table_context(table_label, metadata):
    """Prefix a table chunk with scheme + table label."""
    scheme = metadata.get("scheme_name", "Unknown Scheme")
    last_updated = metadata.get("last_updated", "")
    return f"Scheme: {scheme}\nTable: {table_label}\nLast Updated: {last_updated}\n\n"


def _infer_table_label(table_md, table_index):
    """Infer a human-readable label from the table header row."""
    first_line = table_md.strip().split("\n")[0]
    if "Over the past" in first_line or "Total investment" in first_line:
        return "SIP Returns History"
    if "Sector" in first_line and "Instruments" in first_line and "Assets" in first_line:
        return "Portfolio Holdings"
    if "Category average" in table_md or "Rank" in first_line:
        return "Returns and Rankings"
    if "Fund Size" in first_line or "1Y" in first_line:
        return "Peer Comparison"
    return f"Table {table_index + 1}"


def _get_data_rows(table_md):
    """Return only data rows (skip header row at index 0 and separator at index 1)."""
    lines = table_md.strip().split("\n")
    return [
        line for i, line in enumerate(lines)
        if i >= 2 and line.strip().startswith("|") and line.strip().endswith("|")
    ]


def _extract_header(table_md):
    """Return (header_row, separator_row) from a markdown table."""
    lines = table_md.strip().split("\n")
    header_row = lines[0] if len(lines) > 0 else ""
    separator_row = lines[1] if len(lines) > 1 else "| --- |"
    return header_row, separator_row


def _batch_rows(rows, batch_size):
    """Split rows into batches of at most batch_size."""
    return [rows[i: i + batch_size] for i in range(0, len(rows), batch_size)]


def _deduplicate_exit_load(raw_text):
    """
    Cleans up noisy 'Exit load' sections by removing historical date entries
    and their associated obsolete rules (e.g. 2% layered rules).
    """
    if not raw_text:
        return ""

    lines = raw_text.split("\n")
    cleaned_lines = []
    skip_next = False
    
    # Matches "## DD Mon YYYY" or just "DD Mon YYYY"
    date_heading_re = re.compile(r"^(?:##\s+)?\d{2}\s+[a-zA-Z]+\s+\d{4}\s*$")
    
    # Historical rules we want to explicitly drop if they appear standalone
    historical_rule_re = re.compile(r"^##\s+Exit load of (?:2%|1%)", re.IGNORECASE)

    for line in lines:
        stripped = line.strip()

        if skip_next:
            if not stripped:
                continue # Skip empty lines while looking for the rule to drop
            skip_next = False
            # Line immediately after a date heading = old rule text -- skip it
            if stripped.startswith("##"):
                continue
            cleaned_lines.append(line)
            continue

        if date_heading_re.match(stripped):
            skip_next = True
            continue  # drop the date heading itself

        if historical_rule_re.match(stripped) and "redeemed within 1 year" not in stripped:
            continue  # drop old rules, but be careful not to drop the current 1% rule if it's the only one

        cleaned_lines.append(line)

    result = "\n".join(cleaned_lines)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    all_chunks = chunk_all_documents()

    print(f"\n{'=' * 60}")
    print(f"Total chunks produced: {len(all_chunks)}")
    print(f"{'=' * 60}")

    type_counts = Counter(c["chunk_type"] for c in all_chunks)
    section_counts = Counter(
        c["section_key"] for c in all_chunks if c["chunk_type"] == "section"
    )
    scheme_counts = Counter(c["metadata"].get("scheme_name", "?") for c in all_chunks)

    print("\nBy chunk_type:")
    for t, n in sorted(type_counts.items()):
        print(f"  {t:15s}: {n}")

    print("\nSection chunks by section_key:")
    for k, n in sorted(section_counts.items()):
        print(f"  {k:25s}: {n}")

    print("\nChunks by scheme:")
    for s, n in sorted(scheme_counts.items()):
        print(f"  {s}: {n}")

    print("\n--- Sample chunks (first 3) ---")
    for chunk in all_chunks[:3]:
        print(f"\nchunk_id   : {chunk['chunk_id']}")
        print(f"chunk_type : {chunk['chunk_type']}")
        print(f"section_key: {chunk['section_key']}")
        print(f"table_index: {chunk['table_index']}")
        print(f"batch_index: {chunk['batch_index']}")
        print(f"scheme     : {chunk['metadata'].get('scheme_name')}")
        print(f"text[:300] :\n{chunk['text'][:300]}")
        print("-" * 60)
