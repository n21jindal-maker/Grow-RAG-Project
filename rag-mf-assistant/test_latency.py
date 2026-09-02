import time
from dotenv import load_dotenv
load_dotenv()
from main import MutualFundAssistant

start_total = time.time()
print("Initializing assistant...")
assistant = MutualFundAssistant()
print(f"Init took {time.time() - start_total:.2f}s")

query = "What is the exit load for HDFC Mid-Cap Opportunities Fund?"
print(f"\nProcessing query: {query}")

t0 = time.time()
has_pii, _ = assistant.pii_scanner.scan(query)
print(f"PII Scan took {time.time() - t0:.4f}s")

t0 = time.time()
intent = assistant.classifier.classify(query)
print(f"Classification took {time.time() - t0:.4f}s")

t0 = time.time()
prep_res = assistant.preprocessor.preprocess(query)
print(f"Preprocess took {time.time() - t0:.4f}s")

t0 = time.time()
retrieved_chunks = assistant.retriever.retrieve(prep_res['processed_query'], scheme_name=prep_res['scheme_name'])
print(f"Retrieval took {time.time() - t0:.4f}s")

t0 = time.time()
top_chunks = assistant.reranker.rerank(prep_res['processed_query'], retrieved_chunks)
print(f"Reranking took {time.time() - t0:.4f}s")

t0 = time.time()
assembled_context = assistant._assemble_context(top_chunks)
print(f"Assembly took {time.time() - t0:.4f}s")

t0 = time.time()
raw_answer = assistant.generator.generate_response(query, assembled_context)
print(f"LLM Generation took {time.time() - t0:.4f}s")

t0 = time.time()
is_grounded = assistant.groundedness_checker.check(raw_answer, assembled_context)
print(f"Groundedness check took {time.time() - t0:.4f}s")

print(f"\nTotal latency: {time.time() - start_total:.4f}s")
