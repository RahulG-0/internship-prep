import json
from datetime import datetime
from config import OUTPUT_DIR
from db.database import Database

class OutputWriter:
    
    def __init__(self):
        self.db = Database()
    
    def write(self, result: dict) -> int:
        try:
            if result["needs_review"]:
                self._write_to_exceptions(result)
            else:
                self._write_to_approved(result)
            
            return self.db.save(result)
        finally:
            self.db.close()
    
    def _write_to_approved(self, result: dict) -> None:
        output_dir = OUTPUT_DIR / "approved"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_type = result["doc_type"]
        filename = output_dir / f"{doc_type}_{timestamp}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self._serialize(result), f, indent=2)
        
        print(f"Approved: {filename}")
    
    def _write_to_exceptions(self, result: dict) -> None:
        output_dir = OUTPUT_DIR / "exceptions"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_type = result["doc_type"]
        filename = output_dir / f"{doc_type}_{timestamp}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self._serialize(result), f, indent=2)
        
        print(f"Exception: {filename}")
    
    def _serialize(self, result: dict) -> dict:
        def convert(obj):
            if hasattr(obj, "model_dump"):
                return obj.model_dump()
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert(i) for i in obj]
            return obj
        return convert(result)
