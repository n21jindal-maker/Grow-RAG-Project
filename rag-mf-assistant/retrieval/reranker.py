import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CROSS_ENCODER_MODEL, TOP_K_RERANK

logger = logging.getLogger(__name__)

class CrossEncoderReranker:
    def __init__(self):
        self.model = None
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(CROSS_ENCODER_MODEL)
            logger.info(f"Loaded CrossEncoder: {CROSS_ENCODER_MODEL}")
        except ImportError:
            logger.warning("sentence_transformers not installed. Reranking will fallback to RRF scores.")
        except Exception as e:
            logger.error(f"Error loading CrossEncoder: {e}. Falling back to RRF.")

    def rerank(self, query: str, chunks: list) -> list:
        if not chunks:
            return []
            
        if self.model is None:
            # Fallback to sorting by RRF score
            sorted_chunks = sorted(chunks, key=lambda x: x.get("rrf_score", 0), reverse=True)
            return sorted_chunks[:TOP_K_RERANK]
            
        # Prepare pairs for cross-encoder
        pairs = [[query, chunk["text"]] for chunk in chunks]
        scores = self.model.predict(pairs)
        
        # Inject scores
        for i, chunk in enumerate(chunks):
            chunk["ce_score"] = float(scores[i])
            
        sorted_chunks = sorted(chunks, key=lambda x: x["ce_score"], reverse=True)
        return sorted_chunks[:TOP_K_RERANK]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    reranker = CrossEncoderReranker()
    dummy_chunks = [
        {"chunk_id": "1", "text": "HDFC Mid Cap expense ratio is 0.90%", "rrf_score": 0.5},
        {"chunk_id": "2", "text": "HDFC Mid Cap fund size is 100000 Cr", "rrf_score": 0.4}
    ]
    res = reranker.rerank("expense ratio", dummy_chunks)
    print("Top 1 chunk:")
    print(res[0])
