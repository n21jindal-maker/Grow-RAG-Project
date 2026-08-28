import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from retrieval.query_preprocessor import QueryPreprocessor
from retrieval.hybrid_retriever import HybridRetriever
from retrieval.reranker import CrossEncoderReranker

class RetrievalPipeline:
    def __init__(self):
        self.preprocessor = QueryPreprocessor()
        self.retriever = HybridRetriever()
        self.reranker = CrossEncoderReranker()

    def retrieve_context(self, query: str) -> str:
        # 1. Preprocess & Extract Entity
        prep_res = self.preprocessor.preprocess(query)
        processed_query = prep_res["processed_query"]
        scheme_name = prep_res["scheme_name"]

        print(f"  [Pipeline] Extracted Scheme: {scheme_name}")
        print(f"  [Pipeline] Processed Query: {processed_query}")

        # 2. Metadata-Filtered Hybrid Retrieval + RRF
        candidates = self.retriever.retrieve(processed_query, scheme_name)
        
        # 3. Reranking (Cross-Encoder or fallback to RRF)
        top_chunks = self.reranker.rerank(processed_query, candidates)

        # 4. Context Assembly
        if not top_chunks:
            return "No relevant context found."

        context_blocks = []
        for i, chunk in enumerate(top_chunks):
            meta = chunk.get("metadata", {})
            
            # Format metadata
            source_url = meta.get("source_url", "Unknown URL")
            chunk_scheme = meta.get("scheme_name", "Unknown Scheme")
            last_updated = meta.get("last_updated", "Unknown Date")
            
            block = f"--- Chunk {i+1} ---\n"
            block += f"Scheme: {chunk_scheme}\n"
            block += f"Source: {source_url}\n"
            block += f"Last Updated: {last_updated}\n"
            block += f"Content:\n{chunk['text']}\n"
            
            context_blocks.append(block)

        return "\n".join(context_blocks)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.WARNING) # hide info logs to keep output clean

    pipeline = RetrievalPipeline()
    
    test_queries = [
        "What is the expense ratio of HDFC Mid-Cap fund?",
        "What is the exit load for the Gold ETF?",
        "Tell me the minimum SIP amount for the small cap fund",
        "What are the top portfolio holdings of Large and Mid Cap fund?"
    ]
    
    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {q}")
        print(f"{'='*60}")
        
        context = pipeline.retrieve_context(q)
        print(context)
