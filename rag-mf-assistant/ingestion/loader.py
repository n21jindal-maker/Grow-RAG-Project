"""
ingestion/loader.py
-------------------
Task 1.2 — Web Page Loader

Implements `load_web_page()` using BeautifulSoup + requests to fetch
and parse HDFC Mutual Fund scheme pages from Groww.

Key design decisions:
- Plain HTTP (no headless browser) — Groww pages render critical financial
  data server-side and are fully accessible via requests.
- Raw HTML is persisted to data/raw/ so re-scraping is needed only when
  the corpus is explicitly refreshed (mitigates risk of page structure changes).
- Table structures are preserved as pipe-delimited Markdown tables so that
  downstream chunker can treat them as atomic units.
- A structured document dict is returned that carries all metadata needed
  by the preprocessor (task 1.3) and chunker (task 2.1).
"""

import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, Tag

from config import MANIFEST_PATH, RAW_DATA_DIR

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Groww-specific CSS selectors / text patterns for key financial fields.
# Using text-pattern extraction because Groww uses dynamic class names.
KEY_FIELD_LABELS: list[str] = [
    "NAV",
    "Min. for SIP",
    "Fund size (AUM)",
    "Expense ratio",
    "Rating",
]

# Sections that contain high-value structured data — we always include these.
HIGH_VALUE_SECTION_KEYWORDS: list[str] = [
    "exit load",
    "stamp duty",
    "expense ratio",
    "minimum investment",
    "minimum investments",
    "benchmark",
    "investment objective",
    "fund management",
    "returns and rankings",
    "holdings",
    "about",
]

# Noise patterns in navigation / footer text that should be excluded.
BOILERPLATE_PATTERNS: list[str] = [
    r"^Invest in Stocks$",
    r"^Start SIP$",
    r"^Mutual Fund Houses$",
    r"^Compare Funds$",
    r"^Track Funds$",
    r"^SIP calculator$",
    r"^Brokerage calculator$",
    r"^Download App$",
    r"^Follow us",
    r"^©\s*\d{4}",
    r"Groww Arbitrage Fund",
    r"Groww ELSS Tax Saver Fund",
    r"Groww Banking",
    r"Groww Gold ETF",
    r"Groww Aggressive",
    r"Groww Nifty",
    r"Groww Liquid",
    r"Groww Dynamic",
    r"Groww Multi",
    r"Groww Large",
    r"Groww Overnight",
    r"Groww Silver",
    r"Groww Value",
    r"SBI Contra",
    r"Nippon India Nifty",
    r"HDFC Balanced Advantage",
    r"Quant Mid Cap",
    r"Bank of India Small",
    r"^RD Calculator$",
    r"^HRA Calculator$",
    r"^FD Calculator$",
    r"^Home Loan",
    r"^Lumpsum Calculator$",
    r"^Margin Calculator$",
]

_BOILERPLATE_RE = re.compile(
    "|".join(BOILERPLATE_PATTERNS), re.IGNORECASE
)

# ---------------------------------------------------------------------------
# Table → Markdown helper
# ---------------------------------------------------------------------------

def _table_to_markdown(table: Tag) -> str:
    """
    Convert a BeautifulSoup <table> element to a pipe-delimited Markdown table.

    The Markdown format keeps table data human-readable and allows the
    chunker to detect and preserve tables as atomic units (never split a
    table mid-row).

    Args:
        table: A BeautifulSoup Tag representing a <table> element.

    Returns:
        A string of Markdown-formatted table text, or an empty string if
        the table contains no data rows.
    """
    rows: list[list[str]] = []
    for tr in table.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue
        row = [cell.get_text(separator=" ", strip=True) for cell in cells]
        # Skip rows that are entirely empty
        if any(cell for cell in row):
            rows.append(row)

    if not rows:
        return ""

    # Build Markdown table
    lines: list[str] = []
    # Header row
    header = rows[0]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")
    # Data rows
    for row in rows[1:]:
        # Pad or trim row to match header column count
        while len(row) < len(header):
            row.append("")
        lines.append("| " + " | ".join(row[: len(header)]) + " |")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Section extraction helpers
# ---------------------------------------------------------------------------

def _extract_fund_summary_block(soup: BeautifulSoup) -> str:
    """
    Extract the key metrics block (NAV, SIP min, AUM, Expense ratio) that
    appears near the top of each Groww fund page.

    Groww renders these as label-value pairs in the page text. We extract
    them by scanning for known label strings and grabbing the following
    sibling text nodes.

    Args:
        soup: Parsed BeautifulSoup object for the fund page.

    Returns:
        A formatted string of the key fund metrics, or empty string if
        none are found.
    """
    body_text = soup.get_text(separator="\n")
    lines = [l.strip() for l in body_text.split("\n") if l.strip()]

    summary_items: list[str] = []
    for i, line in enumerate(lines):
        for label in KEY_FIELD_LABELS:
            if line == label and i + 1 < len(lines):
                value = lines[i + 1]
                summary_items.append(f"{label}: {value}")
                break

    return "\n".join(summary_items)


def _extract_exit_load_section(soup: BeautifulSoup) -> str:
    """
    Extract the Exit Load section and its surrounding context (stamp duty,
    tax implication) from the page.

    Args:
        soup: Parsed BeautifulSoup object.

    Returns:
        A multi-line string with exit load details, or empty string.
    """
    body_text = soup.get_text(separator="\n")
    lines = [l.strip() for l in body_text.split("\n") if l.strip()]

    result_lines: list[str] = []
    capturing = False
    capture_count = 0
    max_capture = 8  # number of lines to capture after the exit load heading

    for line in lines:
        if "exit load" in line.lower() and "stamp duty" not in line.lower():
            # Start of exit load section heading
            result_lines.append(f"\n## {line}")
            capturing = True
            capture_count = 0
            continue

        if capturing:
            capture_count += 1
            # Stop if we hit another major heading or ran out of context lines
            if capture_count > max_capture:
                capturing = False
                continue
            # Skip nav/footer noise
            if _BOILERPLATE_RE.search(line):
                continue
            result_lines.append(line)

    return "\n".join(result_lines)


def _extract_about_section(soup: BeautifulSoup) -> str:
    """
    Extract the 'About <Fund Name>' section which contains the investment
    objective, fund benchmark, fund house, and minimum investment details.

    Args:
        soup: Parsed BeautifulSoup object.

    Returns:
        A multi-line string with about section content.
    """
    body_text = soup.get_text(separator="\n")
    lines = [l.strip() for l in body_text.split("\n") if l.strip()]

    result_lines: list[str] = []
    capturing = False
    capture_count = 0
    max_capture = 20

    for line in lines:
        if line.lower().startswith("about") and len(line) > 10:
            if not result_lines:  # Only capture first "About" section
                result_lines.append(f"\n## {line}")
                capturing = True
                capture_count = 0
                continue

        if capturing:
            capture_count += 1
            if capture_count > max_capture:
                capturing = False
                continue
            if _BOILERPLATE_RE.search(line):
                continue
            result_lines.append(line)

    return "\n".join(result_lines)


def _extract_returns_section(soup: BeautifulSoup) -> str:
    """
    Extract the Returns and Rankings section, including the performance
    table data, from the page.

    Args:
        soup: Parsed BeautifulSoup object.

    Returns:
        A formatted string containing returns data.
    """
    # The returns table (Table index 2 on Groww pages) contains:
    # Fund returns vs category average vs rank
    tables = soup.find_all("table")
    if len(tables) >= 3:
        returns_table = _table_to_markdown(tables[2])
        if returns_table:
            return f"\n## Returns and Rankings\n{returns_table}"
    return ""


def _extract_minimum_investments_section(soup: BeautifulSoup) -> str:
    """
    Extract minimum SIP and lumpsum investment amounts from the page.

    Args:
        soup: Parsed BeautifulSoup object.

    Returns:
        A formatted string with minimum investment details.
    """
    body_text = soup.get_text(separator="\n")
    lines = [l.strip() for l in body_text.split("\n") if l.strip()]

    result_lines: list[str] = []
    capturing = False
    capture_count = 0
    max_capture = 10

    for line in lines:
        if "minimum investment" in line.lower():
            result_lines.append(f"\n## {line}")
            capturing = True
            capture_count = 0
            continue

        if capturing:
            capture_count += 1
            if capture_count > max_capture:
                capturing = False
                continue
            if _BOILERPLATE_RE.search(line):
                continue
            result_lines.append(line)

    return "\n".join(result_lines)


def _extract_full_content(soup: BeautifulSoup) -> str:
    """
    Extract all text from the page body, filtering out boilerplate navigation and footer.
    """
    body_text = soup.get_text(separator="\n")
    lines = [l.strip() for l in body_text.split("\n") if l.strip()]
    cleaned_lines = [l for l in lines if not _BOILERPLATE_RE.search(l)]
    return "\n".join(cleaned_lines)


# ---------------------------------------------------------------------------
# Core loader function
# ---------------------------------------------------------------------------

def load_web_page(
    url: str,
    scheme_name: str,
    publisher: str,
    last_updated: str,
    *,
    save_raw: bool = True,
    request_delay: float = 1.0,
    timeout: int = 30,
    retries: int = 3,
    session: Optional[requests.Session] = None,
) -> dict[str, Any]:
    """
    Fetch and parse a single web page (Groww HDFC fund page) into a
    structured document dictionary ready for downstream preprocessing
    and chunking.

    The function:
      1. Fetches the page via HTTP (with retry logic).
      2. Persists the raw HTML to ``data/raw/`` for reproducibility.
      3. Extracts key financial sections: summary metrics, exit load,
         minimum investments, returns/rankings, and about section.
      4. Extracts and converts all tables to Markdown format (atomic,
         never split rows).
      5. Returns a structured document dict with all metadata.

    Args:
        url:          The full URL of the Groww fund page.
        scheme_name:  Human-readable scheme name (e.g., "HDFC Mid-Cap
                      Opportunities Fund").
        publisher:    Source publisher (e.g., "Groww").
        last_updated: ISO date string when the corpus was last updated
                      (e.g., "2026-08-27").
        save_raw:     If True, persist raw HTML to ``data/raw/``.
        request_delay: Seconds to sleep before making the request (be
                       polite to the server).
        timeout:      HTTP request timeout in seconds.
        retries:      Number of retry attempts on failure.
        session:      Optional pre-configured requests.Session to reuse
                      (useful for batch loading).

    Returns:
        A document dict with the following keys:
          - ``source_url``    (str): The original URL.
          - ``document_type`` (str): Always ``"web"`` for this loader.
          - ``scheme_name``   (str): The mutual fund scheme name.
          - ``publisher``     (str): The source publisher.
          - ``last_updated``  (str): ISO date string.
          - ``title``         (str): Page <title> text.
          - ``full_text``     (str): Complete, cleaned page text.
          - ``sections``      (dict): Named text sections extracted from
                              the page (summary, exit_load, returns,
                              min_investments, about).
          - ``tables``        (list[str]): All tables as Markdown strings.
          - ``raw_html_path`` (str | None): Absolute path to the saved raw
                              HTML file, or None if save_raw=False.
          - ``status``        (str): ``"success"`` or ``"error"``.
          - ``error``         (str | None): Error message if status is
                              ``"error"``, else None.

    Raises:
        Does not raise — errors are captured into the returned dict's
        ``status`` and ``error`` fields so batch loading can continue.
    """
    if request_delay > 0:
        time.sleep(request_delay)

    logger.info("Fetching: %s", url)

    # --- Fetch with retries ---
    html_content: Optional[str] = None
    last_error: Optional[str] = None
    _session = session or requests.Session()

    for attempt in range(1, retries + 1):
        try:
            response = _session.get(
                url,
                headers=DEFAULT_HEADERS,
                timeout=timeout,
            )
            response.raise_for_status()
            response.encoding = response.apparent_encoding or "utf-8"
            html_content = response.text
            logger.info(
                "Fetched %s (attempt %d, status %d, %d bytes)",
                url,
                attempt,
                response.status_code,
                len(html_content),
            )
            break
        except requests.RequestException as exc:
            last_error = str(exc)
            logger.warning(
                "Attempt %d/%d failed for %s: %s",
                attempt,
                retries,
                url,
                last_error,
            )
            if attempt < retries:
                time.sleep(2 ** attempt)  # exponential back-off

    if html_content is None:
        return {
            "source_url": url,
            "document_type": "web",
            "scheme_name": scheme_name,
            "publisher": publisher,
            "last_updated": last_updated,
            "title": "",
            "full_text": "",
            "sections": {},
            "tables": [],
            "raw_html_path": None,
            "status": "error",
            "error": last_error,
        }

    # --- Persist raw HTML ---
    raw_html_path: Optional[str] = None
    if save_raw:
        raw_dir = Path(RAW_DATA_DIR)
        raw_dir.mkdir(parents=True, exist_ok=True)
        # Create a safe filename from the URL slug
        url_slug = urlparse(url).path.strip("/").replace("/", "_")
        raw_file = raw_dir / f"{url_slug}.html"
        raw_file.write_text(html_content, encoding="utf-8")
        raw_html_path = str(raw_file.resolve())
        logger.info("Raw HTML saved to: %s", raw_html_path)

    # --- Parse HTML ---
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract page title
    title_tag = soup.find("title")
    page_title = title_tag.get_text(strip=True) if title_tag else scheme_name

    # --- Extract tables (preserve as Markdown) ---
    all_tables_md: list[str] = []
    for table in soup.find_all("table"):
        md = _table_to_markdown(table)
        if md:
            all_tables_md.append(md)

    # --- Extract named sections ---
    summary_block = _extract_fund_summary_block(soup)
    exit_load_section = _extract_exit_load_section(soup)
    returns_section = _extract_returns_section(soup)
    min_investment_section = _extract_minimum_investments_section(soup)
    about_section = _extract_about_section(soup)
    full_content = _extract_full_content(soup)

    sections: dict[str, str] = {}
    if summary_block:
        sections["summary_metrics"] = summary_block
    if exit_load_section:
        sections["exit_load"] = exit_load_section
    if returns_section:
        sections["returns_rankings"] = returns_section
    if min_investment_section:
        sections["minimum_investments"] = min_investment_section
    if about_section:
        sections["about"] = about_section
    if full_content:
        sections["full_content"] = full_content

    # --- Build structured full text ---
    # Compose a clean document text with labelled sections so the preprocessor
    # can operate on structured content rather than raw HTML soup.
    text_parts: list[str] = [
        f"# {page_title}",
        f"Source: {url}",
        f"Scheme: {scheme_name}",
        f"Publisher: {publisher}",
        f"Last Updated: {last_updated}",
        "",
    ]

    if summary_block:
        text_parts.append("## Fund Summary")
        text_parts.append(summary_block)
        text_parts.append("")

    if all_tables_md:
        text_parts.append("## Tables")
        for i, table_md in enumerate(all_tables_md, 1):
            text_parts.append(f"### Table {i}")
            text_parts.append(table_md)
            text_parts.append("")

    if exit_load_section:
        text_parts.append(exit_load_section)
        text_parts.append("")

    if min_investment_section:
        text_parts.append(min_investment_section)
        text_parts.append("")

    if returns_section:
        text_parts.append(returns_section)
        text_parts.append("")

    if about_section:
        text_parts.append(about_section)
        text_parts.append("")

    full_text = "\n".join(text_parts)

    logger.info(
        "Parsed '%s': %d chars, %d tables, %d sections",
        scheme_name,
        len(full_text),
        len(all_tables_md),
        len(sections),
    )

    return {
        "source_url": url,
        "document_type": "web",
        "scheme_name": scheme_name,
        "publisher": publisher,
        "last_updated": last_updated,
        "title": page_title,
        "full_text": full_text,
        "sections": sections,
        "tables": all_tables_md,
        "raw_html_path": raw_html_path,
        "status": "success",
        "error": None,
    }


# ---------------------------------------------------------------------------
# Batch loader from corpus manifest
# ---------------------------------------------------------------------------

def load_all_from_manifest(
    manifest_path: str = MANIFEST_PATH,
    *,
    save_raw: bool = True,
    request_delay: float = 2.0,
) -> list[dict[str, Any]]:
    """
    Load all web page documents defined in ``corpus_manifest.json``.

    Iterates through each entry in the manifest and calls
    ``load_web_page()`` for ``"web"`` type entries. PDF entries are
    skipped here (handled by a separate PDF loader in a future task).

    Args:
        manifest_path:  Path to corpus_manifest.json.
        save_raw:       Whether to save raw HTML files.
        request_delay:  Seconds to wait between requests (be polite).

    Returns:
        A list of document dicts (one per manifest entry processed).
        Entries with ``status == "error"`` are included so the caller
        can decide how to handle failures.
    """
    manifest_file = Path(manifest_path)
    if not manifest_file.exists():
        raise FileNotFoundError(
            f"Corpus manifest not found: {manifest_path}"
        )

    with manifest_file.open(encoding="utf-8") as f:
        manifest: list[dict[str, Any]] = json.load(f)

    logger.info("Loaded manifest with %d entries", len(manifest))

    documents: list[dict[str, Any]] = []
    session = requests.Session()

    for entry in manifest:
        doc_type = entry.get("type", "web")

        if doc_type == "web":
            doc = load_web_page(
                url=entry["url"],
                scheme_name=entry.get("scheme", "Unknown Scheme"),
                publisher=entry.get("publisher", "Unknown Publisher"),
                last_updated=entry.get("date", ""),
                save_raw=save_raw,
                request_delay=request_delay,
                session=session,
            )
            documents.append(doc)
        else:
            logger.info(
                "Skipping non-web entry (type=%s): %s",
                doc_type,
                entry.get("url", entry.get("path", "?")),
            )

    success_count = sum(1 for d in documents if d["status"] == "success")
    error_count = len(documents) - success_count
    logger.info(
        "Batch load complete: %d success, %d error (of %d web entries)",
        success_count,
        error_count,
        len(documents),
    )

    return documents


# ---------------------------------------------------------------------------
# CLI entry point for manual testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    print("Running loader on all manifest entries...\n")
    docs = load_all_from_manifest()

    for doc in docs:
        status_label = "[OK]  " if doc["status"] == "success" else "[FAIL]"
        print(
            f"  {status_label} {doc['scheme_name']}"
            f"  |  tables={len(doc['tables'])}"
            f"  |  sections={list(doc['sections'].keys())}"
            f"  |  chars={len(doc['full_text'])}"
        )
        if doc["status"] == "error":
            print(f"      ERROR: {doc['error']}")

    print(
        f"\nDone. {sum(1 for d in docs if d['status'] == 'success')}/{len(docs)} pages loaded successfully."
    )
    sys.exit(0 if all(d["status"] == "success" for d in docs) else 1)
