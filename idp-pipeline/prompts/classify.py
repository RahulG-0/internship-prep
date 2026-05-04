CLASSIFY_PROMPT = """
You are a document classification system for a financial institution.

Analyze the following document text and classify it as exactly one of these types:
- invoice
- bank_statement
- loan_application
- unknown

Use "unknown" only if the document clearly does not belong to any of the above types.

Return ONLY a JSON object with no preamble, explanation, or markdown formatting:
{{
    "doc_type": "invoice",
    "confidence": 0.95,
    "reasoning": "Document contains vendor details, line items, and a total amount due"
}}

Document text:
{text}
"""