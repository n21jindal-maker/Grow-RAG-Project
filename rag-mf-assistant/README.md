# Mutual Fund Facts-Only FAQ Assistant

RAG-based FAQ Assistant for HDFC Mutual Fund Schemes.

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
   Copy `.env.template` to `.env` and fill in your API keys.
   ```bash
   cp .env.template .env
   ```

## Architecture
(RAG diagram placeholder)

## Running the application
```bash
streamlit run ui/app.py
```
