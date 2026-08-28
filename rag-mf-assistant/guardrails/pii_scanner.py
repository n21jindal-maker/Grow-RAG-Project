import re
from typing import Dict, Tuple

class PIIScanner:
    """
    Scans input text for sensitive Personally Identifiable Information (PII)
    such as PAN, Aadhaar, Phone Numbers, Emails, and Account Numbers.
    """
    def __init__(self):
        self.patterns = {
            "PAN": re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', re.IGNORECASE),
            "Aadhaar": re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b'),
            "Phone": re.compile(r'\b(?:\+91[\s-]?)?[6-9]\d{9}\b'),
            "Email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "Account Number": re.compile(r'\b\d{9,18}\b')
        }

    def scan(self, text: str) -> Tuple[bool, Dict[str, list]]:
        """
        Scans text for PII. 
        Returns (has_pii, detected_pii_dict)
        """
        detected = {}
        has_pii = False
        
        for pii_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                has_pii = True
                # Deduplicate matches
                detected[pii_type] = list(set(matches))
                
        return has_pii, detected
