# Mutual Fund Facts-Only FAQ Assistant

A **Retrieval-Augmented Generation (RAG)** assistant that answers objective, verifiable questions about HDFC Mutual Fund schemes. It retrieves facts exclusively from official public documents (AMC factsheets, SIDs, AMFI, SEBI circulars) and generates concise, cited responses. It **never** provides investment advice, opinions, or recommendations.

## Features

- **Facts-Only**: Every answer must be grounded in retrieved source text. No hallucination, no opinion.
- **Source Transparency**: Every response includes exactly one citation link and a "Last updated" footer.
- **Strict Refusal**: Advisory/opinion queries are politely declined with an educational link.
- **Privacy by Design**: Regex-based PII scanner blocks queries containing PAN, Aadhaar, phone, email, or account numbers before any processing occurs.
- **Offline/Online Separation**: Ingestion and indexing are decoupled from real-time query serving.

## Supported Schemes
Currently, the assistant focuses on the following HDFC Mutual Fund schemes via official Groww pages:
- HDFC Mid-Cap Opportunities Fund
- HDFC Small Cap Fund
- HDFC Multi Cap Fund
- HDFC Large and Mid Cap Fund
- HDFC Gold ETF Fund of Fund

## Architecture

- **Data Ingestion**: A robust web scraper extracts clean plaintext and table structures.
- **Structure-Aware Chunking**: Specialized chunking engine that ensures high-value data (e.g. exit loads, expense ratio tables) is not split mid-row.
- **Hybrid Retrieval**: Combines semantic Vector Search (`BAAI/bge-large-en-v1.5` embeddings in ChromaDB) and Lexical Search (`rank_bm25`) for domain-specific exact-matches. Results are fused using Reciprocal Rank Fusion (RRF).
- **Reranking**: Uses Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) to re-score query-chunk relevance.
- **Generation Layer**: Powered by Google Gemini 3.1 Pro (with Groq fallback), instructed to strictly answer in 3 sentences or fewer using retrieved context.

## Setup Instructions

1. **Environment:**
   Ensure Python 3.11+ is installed.
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   > **Note on Windows:** If you want to install `ragas` (for Phase 7 evaluation), you may need [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) installed, as one of its dependencies (`scikit-network`) requires compilation.

3. **API Keys:**
   Copy `.env.template` to `.env` and fill in your API keys (e.g., `GEMINI_API_KEY`, `GROQ_API_KEY`).
   ```bash
   cp .env.template .env
   ```

## Running the Application

1. **Data Ingestion (Optional):**
   To fetch new data from sources, run the offline pipeline to build the vector and keyword indexes.
   ```bash
   python main.py --ingest-only
   ```

2. **Run in CLI Mode:**
   You can run a quick interactive CLI to test the pipeline end-to-end.
   ```bash
   python main.py
   ```

3. **Backend API (FastAPI):**
   Run the backend RESTful API.
   ```bash
   uvicorn api.main:app --reload
   ```

4. **Frontend UI:**
   The production frontend is built with Next.js. Navigate to the `frontend/` directory and run:
   ```bash
   cd frontend
   npm run dev
   ```

## Known Limitations

- **Static Corpus**: Data is fetched on demand. The ingestion pipeline needs to be run to fetch the latest factsheets.
- **Single AMC**: Currently limited to specific HDFC MF schemes.
