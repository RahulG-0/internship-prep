from extraction.extraction_base import BaseExtractor
from prompts.invoice import INVOICE_PROMPT

class InvoiceExtractor(BaseExtractor):
    
    def extract(self, text: str) -> dict:
        prompt = INVOICE_PROMPT.format(text=text)
        response = self._call_llm(prompt)
        return self._parse_json(response)