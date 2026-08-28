import unittest
from pii_scanner import PIIScanner
from query_classifier import QueryClassifier
from groundedness_check import GroundednessChecker

class TestPIIScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = PIIScanner()
        
    def test_pii_positive(self):
        positives = [
            ("My PAN is ABCDE1234F, check my portfolio", True),
            ("Please call me at +919876543210 for investment.", True),
            ("My Aadhaar is 1234 5678 9012, is it linked?", True),
            ("Email me at user@example.com", True),
            ("Transfer to account 123456789012 please.", True)
        ]
        for text, expected in positives:
            has_pii, detected = self.scanner.scan(text)
            self.assertTrue(has_pii, f"Failed to detect PII in: {text}")

    def test_pii_negative(self):
        negatives = [
            ("What is the expense ratio?", False),
            ("Is there an exit load for HDFC ELSS Tax Saver?", False),
            ("Tell me about the fund manager.", False),
            ("SIP amount is 100", False),
            ("I have 10000 rupees to invest.", False)
        ]
        for text, expected in negatives:
            has_pii, detected = self.scanner.scan(text)
            self.assertFalse(has_pii, f"Falsely detected PII in: {text}")

class TestQueryClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = QueryClassifier()
        
    def test_factual(self):
        queries = [
            "What is the expense ratio of HDFC Small Cap Fund?",
            "Is there an exit load for HDFC ELSS Tax Saver?",
            "What is the minimum SIP amount for HDFC Large Cap?",
            "How do I download my capital gains statement?",
            "What is the benchmark for HDFC Mid-Cap Fund?"
        ]
        for q in queries:
            self.assertEqual(self.classifier.classify(q), 'factual', f"Failed on factual: {q}")
            
    def test_advisory(self):
        queries = [
            "Should I switch from HDFC ELSS to Mid-Cap?",
            "What is the best fund to invest in right now?",
            "Would you recommend investing in Gold ETF?",
            "Which is better, HDFC Small Cap or Mid Cap?",
            "Compare returns of Large Cap vs Small Cap",
            "What is the expected return for 5 years?",
            "Will it give me 12% return?",
            "Suggest a good portfolio",
            "Is it good to invest now?",
            "Future performance of this fund?"
        ]
        for q in queries:
            self.assertEqual(self.classifier.classify(q), 'advisory', f"Failed on advisory: {q}")
            
    def test_out_of_scope(self):
        queries = [
            "What is the weather today?",
            "Who will win the election politics?",
            "Tell me a joke",
            "Give me a recipe for cake",
            "What movie should I watch?"
        ]
        for q in queries:
            self.assertEqual(self.classifier.classify(q), 'out_of_scope', f"Failed on out_of_scope: {q}")

class TestGroundedness(unittest.TestCase):
    def setUp(self):
        self.checker = GroundednessChecker()
        
    def test_grounded_vs_hallucinated(self):
        # We only test if API key is present, otherwise it fails open
        if self.checker.model:
            context = "The HDFC Mid-Cap Opportunities Fund has an expense ratio of 0.74%."
            
            grounded_answer = "The expense ratio is 0.74%."
            self.assertTrue(self.checker.check(grounded_answer, context))
            
            hallucinated_answer = "The expense ratio is 0.74% and the fund is managed by Chirag Setalvad."
            # Chirag is true in real life, but not in the context provided!
            self.assertFalse(self.checker.check(hallucinated_answer, context))

if __name__ == '__main__':
    unittest.main()
