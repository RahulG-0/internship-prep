from dotenv import load_dotenv
import os
import json
from google import genai
from config import BASE_DIR, GEMINI_MODEL

class BaseExtractor:
    
    def __init__(self):
        load_dotenv(BASE_DIR / ".env")
        self.api_key = os.getenv("API_GEMINI_KEY")
        if not self.api_key:
            raise ValueError("Missing API_GEMINI_KEY in .env")
        self.client = genai.Client(api_key=self.api_key)
    
    def _call_llm(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt],
            config={
                'response_mime_type': 'application/json',
            },
        )
        return response.text
    
    def _parse_json(self, response: str) -> dict:
        clean = response.strip()
        
        if "```json" in clean:
            clean = clean.split("```json")[1].split("```")[0]
        elif "```" in clean:
            clean = clean.split("```")[1].split("```")[0]
        
        return json.loads(clean.strip())
    
    def extract(self, text: str) -> dict:
        raise NotImplementedError("Subclasses must implement extract()")

