from extraction.extraction_base import BaseExtractor
from prompts.classify import CLASSIFY_PROMPT

class Classifier(BaseExtractor):
    
    def classify(self, text: str) -> dict:
        prompt = CLASSIFY_PROMPT.format(text=text)
        response = self._call_llm(prompt)
        result = self._parse_json(response)
        
        valid_types = {"invoice", "bank_statement", "loan_application", "unknown"}
        if result.get("doc_type") not in valid_types:
            result["doc_type"] = "unknown"
            result["confidence"] = 0.0
        
        return result
        