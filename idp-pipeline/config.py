import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value not in (None, "") else default


APPROVAL_THRESHOLD = _float_env("APPROVAL_THRESHOLD", 10000.00)
CONFIDENCE_THRESHOLD = _float_env("CONFIDENCE_THRESHOLD", 0.75)
DTI_THRESHOLD = _float_env("DTI_THRESHOLD", 0.43)
DB_PATH = Path(os.getenv("DB_PATH", BASE_DIR / "db" / "idp_pipeline.sqlite3"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", BASE_DIR / "output"))
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173",
    ).split(",")
    if origin.strip()
]
