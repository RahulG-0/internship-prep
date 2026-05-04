from extraction.extraction_base import BaseExtractor
from prompts.loan_application import LOAN_APPLICATION_PROMPT

class LoanApplicationExtractor(BaseExtractor):
    
    def extract(self, text: str) -> dict:
        prompt = LOAN_APPLICATION_PROMPT.format(text=text)
        response = self._call_llm(prompt)
        return self._parse_json(response)