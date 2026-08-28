import sys
import os

from ingestion.indexer import load_chroma_collection
from config import TOP_K_RETRIEVAL

def view_embeddings():
    print("Loading ChromaDB Collection...")
    collection = load_chroma_collection()
    
    count = collection.count()
    print(f"Total chunks in ChromaDB: {count}")
    
    if count == 0:
        print("Collection is empty!")
        return
        
    print("\n--- 1. Peeking at the first 2 Embeddings ---")
    # Peek at the first 2 items
    peek_res = collection.peek(limit=2)
    
    ids = peek_res["ids"]
    metadatas = peek_res["metadatas"]
    embeddings = peek_res["embeddings"]
    documents = peek_res["documents"]
    
    for i in range(len(ids)):
        print(f"\nChunk ID: {ids[i]}")
        print(f"Scheme Name: {metadatas[i].get('scheme_name')}")
        print(f"Section/Type: {metadatas[i].get('section_key')} | {metadatas[i].get('chunk_type')}")
        # Print just a snippet of text
        print(f"Text Snippet: {documents[i][:100]}...")
        if embeddings is not None and len(embeddings) > i:
            emb = embeddings[i]
            print(f"Embedding Dimensions: {len(emb)}")
            print(f"Embedding Vector (first 5 dims): {emb[:5]}")
            
    print("\n--- 2. Example Retrieval ---")
    query = "What is the expense ratio?"
    print(f"Query: '{query}'")
    
    # Simple vector search without metadata filter
    results = collection.query(
        query_texts=[query],
        n_results=3,
        include=["documents", "metadatas", "distances", "embeddings"]
    )
    
    if results and results["documents"]:
        r_docs = results["documents"][0]
        r_metas = results["metadatas"][0]
        r_dists = results["distances"][0]
        
        for i in range(len(r_docs)):
            print(f"\nResult {i+1} (Distance: {r_dists[i]:.4f})")
            print(f"Scheme: {r_metas[i].get('scheme_name')}")
            print(f"Text: {r_docs[i][:150]}...")
            
    print("\n--- 3. Example Retrieval WITH Metadata Filter ---")
    query_filtered = "expense ratio"
    scheme_filter = "HDFC Small Cap Fund"
    print(f"Query: '{query_filtered}' | Filter: {scheme_filter}")
    
    results_filtered = collection.query(
        query_texts=[query_filtered],
        n_results=3,
        where={"scheme_name": scheme_filter},
        include=["documents", "metadatas", "distances"]
    )
    
    if results_filtered and results_filtered["documents"]:
        r_docs_f = results_filtered["documents"][0]
        r_metas_f = results_filtered["metadatas"][0]
        r_dists_f = results_filtered["distances"][0]
        
        for i in range(len(r_docs_f)):
            print(f"\nResult {i+1} (Distance: {r_dists_f[i]:.4f})")
            print(f"Scheme: {r_metas_f[i].get('scheme_name')}")
            print(f"Text: {r_docs_f[i][:150]}...")

if __name__ == "__main__":
    # Ensure Windows uses utf-8 printing for Rupees symbol
    sys.stdout.reconfigure(encoding='utf-8')
    view_embeddings()
