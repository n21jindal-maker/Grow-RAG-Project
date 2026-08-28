import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.indexer import load_chroma_collection, load_bm25_index, _tokenize
from config import TOP_K_RETRIEVAL, RRF_K

class HybridRetriever:
    def __init__(self):
        self.chroma_collection = load_chroma_collection()
        self.bm25_index, self.bm25_chunks = load_bm25_index()
        
    def retrieve(self, processed_query: str, scheme_name: str = None) -> list:
        # 1. Vector Search
        where_filter = {"scheme_name": scheme_name} if scheme_name else None
        
        vector_res = self.chroma_collection.query(
            query_texts=[processed_query],
            n_results=TOP_K_RETRIEVAL,
            where=where_filter
        )
        
        vector_chunks = []
        if vector_res and vector_res["documents"] and len(vector_res["documents"]) > 0:
            docs = vector_res["documents"][0]
            metas = vector_res["metadatas"][0]
            ids = vector_res["ids"][0]
            distances = vector_res["distances"][0] 
            
            for i in range(len(docs)):
                vector_chunks.append({
                    "chunk_id": ids[i],
                    "text": docs[i],
                    "metadata": metas[i],
                    "score": distances[i],
                    "rank": i + 1
                })
        
        # 2. BM25 Search
        tokenized_query = _tokenize(processed_query)
        bm25_scores = self.bm25_index.get_scores(tokenized_query)
        
        bm25_scored_chunks = []
        for i, chunk in enumerate(self.bm25_chunks):
            # BM25 chunks have full metadata in the 'metadata' dict
            c_meta = chunk.get("metadata", {})
            c_scheme = c_meta.get("scheme_name")
            
            if scheme_name and c_scheme != scheme_name:
                continue
                
            bm25_scored_chunks.append({
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "metadata": c_meta,
                "score": bm25_scores[i]
            })
            
        # Sort descending by score
        bm25_scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        top_bm25 = bm25_scored_chunks[:TOP_K_RETRIEVAL]
        
        for i, c in enumerate(top_bm25):
            c["rank"] = i + 1
            
        # 3. Reciprocal Rank Fusion
        fused_scores = {}
        chunk_map = {}
        
        for c in vector_chunks:
            cid = c["chunk_id"]
            fused_scores[cid] = fused_scores.get(cid, 0.0) + (1.0 / (RRF_K + c["rank"]))
            chunk_map[cid] = c
            
        for c in top_bm25:
            cid = c["chunk_id"]
            fused_scores[cid] = fused_scores.get(cid, 0.0) + (1.0 / (RRF_K + c["rank"]))
            chunk_map[cid] = c
            
        # Sort by fused score
        sorted_fused = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        
        final_results = []
        for cid, score in sorted_fused:
            c = chunk_map[cid]
            c["rrf_score"] = score
            final_results.append(c)
            
        return final_results

if __name__ == "__main__":
    import pprint
    retriever = HybridRetriever()
    query = "expense ratio"
    scheme = "HDFC Mid-Cap Opportunities Fund"
    
    print(f"Testing query: '{query}' with filter: '{scheme}'")
    results = retriever.retrieve(query, scheme_name=scheme)
    
    print(f"Found {len(results)} chunks:")
    for r in results[:3]:
        print(f"\n--- Rank (Score: {r['rrf_score']:.4f}) ---")
        print(f"Scheme: {r['metadata'].get('scheme_name')}")
        print(f"Section: {r['metadata'].get('section_key')}")
        print(r["text"][:200] + "...")
