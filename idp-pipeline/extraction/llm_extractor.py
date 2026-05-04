from extraction.classify import Classifier
from extraction.invoice import InvoiceExtractor
from extraction.bank_statement import BankStatementExtractor
from extraction.loan_application import LoanApplicationExtractor

EXTRACTOR_MAP = {
    "invoice": InvoiceExtractor,
    "bank_statement": BankStatementExtractor,
    "loan_application": LoanApplicationExtractor
}

class LLMExtractor:
    
    def __init__(self):
        self.classifier = Classifier()
    
    def classify_and_extract(self, text: str) -> dict:
        classification = self.classifier.classify(text)
        doc_type = classification.get("doc_type", "unknown")
        classification_confidence = classification.get("confidence", 0.0)
        classification_reasoning = classification.get("reasoning", "")
        
        if doc_type == "unknown":
            return {
                "doc_type": "unknown",
                "classification_confidence": classification_confidence,
                "classification_reasoning": classification_reasoning,
                "extracted_data": None
            }
        
        extractor = EXTRACTOR_MAP[doc_type]()
        extracted = extractor.extract(text)
        
        extracted["doc_type"] = doc_type
        extracted["classification_confidence"] = classification_confidence
        extracted["classification_reasoning"] = classification_reasoning
        
        return extracted
