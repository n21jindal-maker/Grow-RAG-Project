import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retrieval.hybrid_retriever import HybridRetriever
from retrieval.reranker import CrossEncoderReranker

retriever = HybridRetriever()
reranker = CrossEncoderReranker()

query = "exit load of hdfc mid cap fund"
scheme_name = "HDFC Mid-Cap Opportunities Fund" # Processed scheme name

results = retriever.retrieve(query, scheme_name=scheme_name)
print(f"Retrieved {len(results)} chunks")
for i, r in enumerate(results):
    print(f"\n--- Chunk {i+1} ---")
    print(r.get("text", "")[:200])
    
top = reranker.rerank(query, results)
print(f"\nTop reranked:")
if top:
    print(top[0].get("text", "")[:200])
else:
    print("No chunks after reranking")
