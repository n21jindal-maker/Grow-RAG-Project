import os
import sys

# Ensure modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from guardrails.pii_scanner import PIIScanner
from guardrails.query_classifier import QueryClassifier, PII_BLOCKED_TEMPLATE, REFUSAL_TEMPLATE, OUT_OF_SCOPE_TEMPLATE, UNGROUNDED_TEMPLATE
from retrieval.query_preprocessor import QueryPreprocessor
from retrieval.hybrid_retriever import HybridRetriever
from retrieval.reranker import CrossEncoderReranker
from generation.generator import LLMGenerator
from guardrails.groundedness_check import GroundednessChecker
from generation.response_formatter import ResponseFormatter

class MutualFundAssistant:
    def __init__(self):
        self.pii_scanner = PIIScanner()
        self.classifier = QueryClassifier()
        self.preprocessor = QueryPreprocessor()
        self.retriever = HybridRetriever()
        self.reranker = CrossEncoderReranker()
        self.generator = LLMGenerator()
        self.groundedness_checker = GroundednessChecker()
        self.formatter = ResponseFormatter()

    def _assemble_context(self, top_chunks: list) -> str:
        if not top_chunks:
            return ""
        
        context_parts = []
        for i, chunk in enumerate(top_chunks):
            url = chunk.get("metadata", {}).get("source_url", "Unknown URL")
            date = chunk.get("metadata", {}).get("last_updated", "Unknown Date")
            text = chunk.get("text", "")
            
            part = f"[Context {i+1}]\nText: {text}\nSource: {url}\nDate: {date}\n"
            context_parts.append(part)
            
        return "\n".join(context_parts)

    def process_query(self, query: str) -> str:
        # 1. PII Scan
        has_pii, detected = self.pii_scanner.scan(query)
        if has_pii:
            return PII_BLOCKED_TEMPLATE

        # 2. Query Classification
        intent = self.classifier.classify(query)
        if intent == 'out_of_scope':
            return OUT_OF_SCOPE_TEMPLATE
        elif intent == 'advisory':
            return REFUSAL_TEMPLATE

        # 3. Preprocess Query
        prep_res = self.preprocessor.preprocess(query)
        processed_query = prep_res['processed_query']
        scheme_name = prep_res['scheme_name']

        # 4. Retrieval
        retrieved_chunks = self.retriever.retrieve(processed_query, scheme_name=scheme_name)

        if not retrieved_chunks:
            return UNGROUNDED_TEMPLATE

        # 5. Reranking
        top_chunks = self.reranker.rerank(processed_query, retrieved_chunks)

        # 6. Context Assembly
        assembled_context = self._assemble_context(top_chunks)

        # 7. LLM Generation
        raw_answer = self.generator.generate_response(query, assembled_context)
        
        # Check if fallback strings were triggered during generation
        if "I don't have this information" in raw_answer or "I'm designed to provide only factual information" in raw_answer or "Error:" in raw_answer:
            return raw_answer

        # 8. Groundedness Check
        is_grounded = self.groundedness_checker.check(raw_answer, assembled_context)
        if not is_grounded:
            return UNGROUNDED_TEMPLATE

        # 9. Format Response
        final_answer = self.formatter.format_response(raw_answer, top_chunks)

        return final_answer

    def process_query_json(self, query: str) -> dict:
        result = {
            "answer": "",
            "query_type": "factual",
            "source_url": None,
            "last_updated": None
        }

        # 1. PII Scan
        has_pii, detected = self.pii_scanner.scan(query)
        if has_pii:
            result["answer"] = PII_BLOCKED_TEMPLATE
            result["query_type"] = "pii"
            return result

        # 2. Query Classification
        intent = self.classifier.classify(query)
        if intent == 'out_of_scope':
            result["answer"] = OUT_OF_SCOPE_TEMPLATE
            result["query_type"] = "out_of_scope"
            return result
        elif intent == 'advisory':
            result["answer"] = REFUSAL_TEMPLATE
            result["query_type"] = "advisory"
            return result
            
        result["query_type"] = intent

        # 3. Preprocess Query
        prep_res = self.preprocessor.preprocess(query)
        processed_query = prep_res['processed_query']
        scheme_name = prep_res['scheme_name']

        # 4. Retrieval
        retrieved_chunks = self.retriever.retrieve(processed_query, scheme_name=scheme_name)

        if not retrieved_chunks:
            result["answer"] = UNGROUNDED_TEMPLATE
            return result

        # 5. Reranking
        top_chunks = self.reranker.rerank(processed_query, retrieved_chunks)

        if top_chunks:
            top_metadata = top_chunks[0].get("metadata", {})
            result["source_url"] = top_metadata.get("source_url")
            result["last_updated"] = top_metadata.get("last_updated")

        # 6. Context Assembly
        assembled_context = self._assemble_context(top_chunks)

        # 7. LLM Generation
        raw_answer = self.generator.generate_response(query, assembled_context)
        
        # Check if fallback strings were triggered during generation
        if "I don't have this information" in raw_answer or "I'm designed to provide only factual information" in raw_answer or "Error:" in raw_answer:
            result["answer"] = raw_answer
            return result

        # 8. Groundedness Check
        is_grounded = self.groundedness_checker.check(raw_answer, assembled_context)
        if not is_grounded:
            result["answer"] = UNGROUNDED_TEMPLATE
            return result

        # 9. Format Response
        final_answer = self.formatter.format_response(raw_answer, top_chunks)
        result["answer"] = final_answer

        return result

if __name__ == "__main__":
    import sys
    
    if "--ingest-only" in sys.argv:
        print("Running ingestion pipeline...")
        from ingestion.indexer import build_index
        build_index(reset=True)
        print("Ingestion complete. Exiting.")
        sys.exit(0)
        
    assistant = MutualFundAssistant()
    
    # Simple test loop
    print("HDFC Mutual Fund Assistant Initialized. Type 'exit' to quit.")
    while True:
        try:
            q = input("\nYou: ")
            if q.lower() in ['exit', 'quit']:
                break
            
            response = assistant.process_query(q)
            print(f"\nAssistant:\n{response}")
        except (KeyboardInterrupt, EOFError):
            break
