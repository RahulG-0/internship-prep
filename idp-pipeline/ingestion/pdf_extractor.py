import pymupdf
from pathlib import Path
import io
from typing import Union

class PDFExtraction:

    def extract_text(self, source: Union[str, bytes]) -> str:
        if isinstance(source, str):
            # Existing path logic
            with pymupdf.open(source) as doc:
                pages = [page.get_text("text") for page in doc]
        else:
            # New stream logic for FastAPI bytes
            with pymupdf.open(stream=source, filetype="pdf") as doc:
                pages = [page.get_text("text") for page in doc]
                
        return "\n".join(pages)


if __name__ == "__main__":
    print(PDFExtraction().extract_text("../samples/sample_invoice_1.pdf"))
