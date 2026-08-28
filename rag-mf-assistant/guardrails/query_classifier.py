import re

REFUSAL_TEMPLATE = """I'm designed to provide only factual information about mutual fund schemes.
For investment guidance, please consult a SEBI-registered advisor or visit
https://www.amfiindia.com/investor-corner/knowledge-center.html"""

OUT_OF_SCOPE_TEMPLATE = "I can only answer questions related to HDFC Mutual Fund schemes. Please ask a mutual fund related question."

PII_BLOCKED_TEMPLATE = "I cannot process this request because it contains sensitive personal information (PII). Please remove any PAN, Aadhaar, phone numbers, or account numbers and try again."

UNGROUNDED_TEMPLATE = "I don't have this information in my current sources. Please check the official HDFC MF website."

class QueryClassifier:
    """
    Classifies a user query into one of three categories:
    - 'factual': Safe to process via RAG
    - 'advisory': Investment advice seeking (should be blocked)
    - 'out_of_scope': Non-financial, irrelevant queries
    """
    def __init__(self):
        # Advisory intent keywords
        self.advisory_patterns = [
            r'\bshould i\b',
            r'\brecommend\b',
            r'\bbest\b',
            r'\bbetter\b',
            r'\bvs\b',
            r'\bcompare returns\b',
            r'\bexpected return\b',
            r'\bwill it give\b',
            r'\bfuture performance\b',
            r'\bsuggest\b',
            r'\bis it good\b',
            r'\binvest in\b'
        ]
        self.advisory_regex = re.compile('|'.join(self.advisory_patterns), re.IGNORECASE)
        
        # Out of scope keywords (a simple heuristic for obvious non-financial questions)
        self.out_of_scope_patterns = [
            r'\bweather\b', r'\bpolitics\b', r'\bjoke\b', r'\brecipe\b', r'\bmovie\b'
        ]
        self.out_of_scope_regex = re.compile('|'.join(self.out_of_scope_patterns), re.IGNORECASE)

    def classify(self, query: str) -> str:
        if self.out_of_scope_regex.search(query):
            return 'out_of_scope'
            
        if self.advisory_regex.search(query):
            return 'advisory'
            
        return 'factual'
