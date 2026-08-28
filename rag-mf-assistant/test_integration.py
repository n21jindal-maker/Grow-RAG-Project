import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import MutualFundAssistant

def main():
    assistant = MutualFundAssistant()
    
    test_queries = [
        # Factual - Expense Ratio
        "What is the expense ratio of HDFC Small Cap Fund?",
        "What is the ER of HDFC Mid-Cap?",
        # Factual - Exit Load
        "Is there an exit load for HDFC Mid-Cap Opportunities Fund?",
        "What is the exit load for HDFC Multi Cap Fund?",
        # Factual - SIP / Min Investment
        "What is the minimum SIP amount for HDFC Large Cap?",
        "minimum investment for small cap fund",
        # Factual - Process / How-To (May not be in DB but tests standard operation)
        "How do I download my capital gains statement?",
        # Factual - Riskometer / Benchmark
        "What is the benchmark for HDFC Mid-Cap Fund?",
        "Tell me the riskometer level of HDFC gold etf",
        # Advisory (Must Refuse)
        "Should I switch from HDFC ELSS to Mid-Cap?",
        "Which is better, small cap or mid cap?",
        "Will HDFC multi cap give me good returns next year?",
        # PII (Must Block)
        "My PAN is ABCDE1234F, check my portfolio",
        "Call me at +919876543210 regarding my mutual fund",
        # Out of Scope
        "What is the weather today?",
        "Who won the cricket match yesterday?"
    ]
    
    print("Running integration tests...\n" + "-"*50)
    for q in test_queries:
        print(f"Query: {q}")
        response = assistant.process_query(q)
        print(f"Response:\n{response}")
        print("-" * 50)

if __name__ == "__main__":
    main()
