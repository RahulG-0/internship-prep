from ingestion.pdf_extractor import PDFExtraction
from extraction.llm_extractor import LLMExtractor
from validation.validate_inputs import Validator
from rules.Format_Review import RulesEngine
from output.writer import OutputWriter
import sys

def process_document(filepath: str) -> None:
    print(f"\nProcessing: {filepath}")
    print("-" * 50)

    print("Step 1: Extracting text from PDF...")
    raw_text = PDFExtraction()
    raw_text = raw_text.extract_text(filepath)

    print("Step 2: Classifying and extracting fields...")
    extracted = LLMExtractor()
    extracted = extracted.classify_and_extract(raw_text)
    doc_type = extracted["doc_type"]
    print(f"         Classified as: {doc_type} "
          f"(confidence: {extracted.get('classification_confidence')})")

    if doc_type == "unknown":
        print("         Unknown document type. Skipping.")
        return

    print("Step 3: Validating extracted data...")
    validated = Validator().validate(extracted, doc_type)
    print(f"         Valid: {validated['valid']}")
    if validated["errors"]:
        print(f"         Errors: {validated['errors']}")

    print("Step 4: Applying business rules...")
    flagged = RulesEngine().apply(validated, doc_type)
    print(f"         Needs review: {flagged['needs_review']}")
    print(f"         Flags: {flagged['flags']}")

    print("Step 5: Writing output...")
    OutputWriter().write(flagged)

    print("Done.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path-to-pdf>")
        sys.exit(1)
    
    process_document(sys.argv[1])