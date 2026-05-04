from validation.models import get_model

class Validator:
    
    def validate(self, extracted: dict, doc_type: str) -> dict:
        try:
            model_class = get_model(doc_type)
        except ValueError as e:
            return {
                "valid": False,
                "doc_type": doc_type,
                "data": extracted,
                "errors": [str(e)]
            }
        
        try:
            validated = model_class(**extracted)
            return {
                "valid": True,
                "doc_type": doc_type,
                "data": validated,
                "errors": []
            }
        except Exception as e:
            return {
                "valid": False,
                "doc_type": doc_type,
                "data": extracted,
                "errors": [str(e)]
            }
