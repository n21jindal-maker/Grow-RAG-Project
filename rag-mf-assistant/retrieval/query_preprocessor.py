import re

class QueryPreprocessor:
    def __init__(self):
        # Common financial/mutual fund abbreviations
        self.abbreviations = {
            r"\ber\b": "expense ratio",
            r"\baum\b": "fund size",
            r"\bnav\b": "net asset value",
            r"\belss\b": "equity linked savings scheme",
            r"\bsip\b": "systematic investment plan"
        }

        # Map colloquial scheme mentions to exact metadata scheme_names
        # Order matters! We will sort by length descending to avoid 
        # "mid cap" matching before "large and mid cap".
        self.scheme_mappings = {
            "large and mid": "HDFC Large and Mid Cap Fund",
            "large & mid": "HDFC Large and Mid Cap Fund",
            "mid cap": "HDFC Mid-Cap Opportunities Fund",
            "mid-cap": "HDFC Mid-Cap Opportunities Fund",
            "multi cap": "HDFC Multi Cap Fund",
            "multi-cap": "HDFC Multi Cap Fund",
            "small cap": "HDFC Small Cap Fund",
            "small-cap": "HDFC Small Cap Fund",
            "gold": "HDFC Gold ETF Fund of Fund",
            "gold etf": "HDFC Gold ETF Fund of Fund"
        }
        self._sorted_keywords = sorted(self.scheme_mappings.keys(), key=len, reverse=True)

    def preprocess(self, query: str) -> dict:
        """
        Processes the query to extract intent (scheme_name) and clean the text.
        Returns a dict: {'processed_query': str, 'scheme_name': str | None}
        """
        processed_query = query.lower()
        
        # 1. Expand abbreviations
        for abbr, expansion in self.abbreviations.items():
            processed_query = re.sub(abbr, expansion, processed_query, flags=re.IGNORECASE)
            
        # 2. Extract scheme name using keyword matching
        extracted_scheme = None
        for keyword in self._sorted_keywords:
            if keyword in processed_query:
                extracted_scheme = self.scheme_mappings[keyword]
                break

        return {
            "processed_query": processed_query,
            "scheme_name": extracted_scheme
        }

if __name__ == "__main__":
    # Test cases
    qp = QueryPreprocessor()
    test_queries = [
        "What is the ER of HDFC mid cap fund?",
        "Tell me the AUM of HDFC Large and Mid-cap",
        "Does the gold ETF have an exit load?",
        "What is the minimum SIP for the small cap fund?",
        "General mutual fund taxation rules" # No scheme mentioned
    ]
    
    for q in test_queries:
        res = qp.preprocess(q)
        print(f"Q: {q}")
        print(f"  Processed: {res['processed_query']}")
        print(f"  Scheme: {res['scheme_name']}\n")
