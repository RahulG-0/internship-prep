import sqlite3
import json
from datetime import datetime
from pathlib import Path
from config import DB_PATH

class Database:
    
    def __init__(self):
        Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_type TEXT,
                filename TEXT,
                file_path TEXT,
                state TEXT,
                extracted_data JSON,
                rule_flags JSON,
                confidence_scores JSON,
                needs_review INTEGER,
                valid INTEGER,
                errors JSON,
                created_at TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def _serialize_row(self, row: sqlite3.Row) -> dict:
        d = dict(row)
        for col in ["extracted_data", "rule_flags", "confidence_scores", "errors"]:
            if d.get(col):
                try:
                    d[col] = json.loads(d[col])
                except Exception:
                    pass
        return d
    
    def save(self, result: dict) -> int:
        data = result.get("data")
        extracted_data = (
            data.model_dump() if hasattr(data, "model_dump") else data
        )
        
        cursor = self.conn.execute("""
            INSERT INTO jobs (
                doc_type, filename, file_path, state, extracted_data,
                rule_flags, confidence_scores, needs_review, valid, errors, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.get("doc_type"),
            result.get("filename"),
            result.get("file_path"),
            "needs_review" if result.get("needs_review") else "approved",
            json.dumps(extracted_data, default=str),
            json.dumps(result.get("flags", {})),
            json.dumps(result.get("confidence_scores", {})),
            int(result.get("needs_review", False)),
            int(result.get("valid", False)),
            json.dumps(result.get("errors", [])),
            datetime.now().isoformat()
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_all(self) -> list:
        cursor = self.conn.execute(
            "SELECT * FROM jobs ORDER BY created_at DESC"
        )
        return [self._serialize_row(row) for row in cursor.fetchall()]
    
    def get_exceptions(self) -> list:
        cursor = self.conn.execute(
            "SELECT * FROM jobs WHERE needs_review = 1 ORDER BY created_at DESC"
        )
        return [self._serialize_row(row) for row in cursor.fetchall()]
    
    def get_by_id(self, job_id: int) -> dict | None:
        cursor = self.conn.execute(
            "SELECT * FROM jobs WHERE id = ?",
            (job_id,)
        )
        row = cursor.fetchone()
        return self._serialize_row(row) if row else None
    
    def close(self) -> None:
        self.conn.close()
