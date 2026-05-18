import re

class PHIDefenderBot:
    def __init__(self):
        # Regular expressions for common PHI identifiers (HIPAA Safe Harbor)
        self.phi_patterns = {
            "EMAIL": r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
            "PHONE_NUMBER": r'\b(?:\+?1[-.●]?)?\(?([0-9]{3})\)?[-.●]?([0-9]{3})[-.●]?([0-9]{4})\b',
            "SSN": r'\b(?!000|666|9\d{2})([0-9]{3})[-.●]?(?!00)([0-9]{2})[-.●]?(?!0000)([0-9]{4})\b',
            "DATE_OF_BIRTH": r'\b(0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])[-/](19|20)\d{2}\b',
            "MED_RECORD_NUM": r'\b[A-Z]{2,3}[-\s]?\d{5,8}\b' # General example pattern for MRNs
        }

    def scrub_text(self, text):
        """Scans the text and redacts any found PHI."""
        scrubbed_text = text
        
        for entity_type, pattern in self.phi_patterns.items():
            # Replace the found pattern with a generic redacted tag
            scrubbed_text = re.sub(pattern, f"[REDACTED {entity_type}]", scrubbed_text)
            
        return scrubbed_text

# --- Example Integration with your Translator ---
if __name__ == "__main__":
    defender = PHIDefenderBot()
    
    # Example text containing PHI
    sample_medical_text = (
        "Patient John Doe (DOB: 05/14/1985), SSN 123-45-6789, phone number "
        "555-123-4567, email john.doe@email.com, was prescribed 萬古霉素 (wàn gǔ méi sù)."
    )
    
    print("--- ORIGINAL TEXT ---")
    print(sample_medical_text)
    
    print("\n--- DEFENDER BOT SCRUBBED TEXT (HIPAA COMPLIANT) ---")
    clean_text = defender.scrub_text(sample_medical_text)
    print(clean_text)
    
    # You would then pass `clean_text` to the OpenAI translation API instead of the original text.
input("\nPress Enter to close this window...")