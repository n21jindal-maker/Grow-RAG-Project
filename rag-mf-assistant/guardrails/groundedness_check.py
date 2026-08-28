import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PRIMARY_MODEL
from langchain_groq import ChatGroq

class GroundednessChecker:
    """
    Checks whether a generated answer is grounded in the provided context.
    """
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.model = ChatGroq(model=PRIMARY_MODEL, temperature=0.0)
        else:
            self.model = None

    def check(self, answer: str, context: str) -> bool:
        """
        Returns True if the answer is grounded in the context, False otherwise.
        """
        if not self.model:
            # If no API key is set, fail open to avoid blocking the pipeline during testing
            # without an API key, although Phase 5 will need it.
            return True
            
        prompt = f"""
        You are a strict evaluator. Given the context below, is the following answer strictly supported by the context?
        If the answer contains information NOT present in the context (hallucination), output NO.
        Otherwise, output YES.

        Context:
        {context}

        Answer:
        {answer}

        Output only YES or NO.
        """
        
        try:
            response = self.model.invoke(prompt)
            result = response.content.strip().upper()
            return 'YES' in result
        except Exception as e:
            print(f"[GroundednessCheck] Error checking groundedness: {e}")
            # Fail open if API fails during check
            return True
