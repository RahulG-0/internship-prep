from extraction.extraction_base import BaseExtractor
from prompts.bank_statement import BANK_STATEMENT_PROMPT

class BankStatementExtractor(BaseExtractor):
    
    def extract(self, text: str) -> dict:
        prompt = BANK_STATEMENT_PROMPT.format(text=text)
        response = self._call_llm(prompt)
        return self._parse_json(response)