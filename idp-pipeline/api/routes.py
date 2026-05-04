from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from db.database import Database
from config import CORS_ORIGINS

from ingestion.pdf_extractor import PDFExtraction
from extraction.llm_extractor import LLMExtractor
from validation.validate_inputs import Validator
from rules.Format_Review import RulesEngine
from output.writer import OutputWriter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"]
)

def _is_pdf_upload(file: UploadFile, pdf_bytes: bytes) -> bool:
    filename = file.filename or ""
    content_type = file.content_type or ""
    return (
        filename.lower().endswith(".pdf")
        or content_type == "application/pdf"
        or pdf_bytes.startswith(b"%PDF")
    )

def _collect_confidence_scores(data) -> dict:
    if hasattr(data, "model_dump"):
        data = data.model_dump()

    if not isinstance(data, dict):
        return {}

    scores = {}
    for field_name, field_value in data.items():
        if isinstance(field_value, dict):
            confidence = field_value.get("confidence")
            if confidence is not None:
                scores[field_name] = confidence

    classification_confidence = data.get("classification_confidence")
    if classification_confidence is not None:
        scores["classification"] = classification_confidence

    return scores

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/jobs")
def get_jobs():
    db = Database()
    try:
        return db.get_all()
    finally:
        db.close()

@app.get("/jobs/exceptions")
def get_exceptions():
    db = Database()
    try:
        return db.get_exceptions()
    finally:
        db.close()

@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    db = Database()
    try:
        job = db.get_by_id(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    finally:
        db.close()

@app.post("/process")
async def extract(file: UploadFile = File(...)):
    pdf_bytes = await file.read()

    if not _is_pdf_upload(file, pdf_bytes):
        raise HTTPException(
            status_code=400,
            detail="Only PDF uploads are supported."
        )

    try:
        text = PDFExtraction().extract_text(pdf_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read this PDF: {e}"
        ) from e

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="This PDF did not contain extractable text."
        )
    
    extracted = LLMExtractor()
    extracted = extracted.classify_and_extract(text)
    doc_type = extracted["doc_type"]

    validated = Validator().validate(extracted, doc_type)
    validated["filename"] = file.filename

    flagged = RulesEngine().apply(validated, doc_type)
    flagged["filename"] = file.filename
    flagged["confidence_scores"] = _collect_confidence_scores(flagged.get("data"))

    flagged["job_id"] = OutputWriter().write(flagged)
    return flagged
