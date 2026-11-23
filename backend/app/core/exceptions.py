from typing import Any, Optional
from fastapi import HTTPException, status

class AppException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "An unexpected error occurred",
        code: str = "INTERNAL_ERROR",
        extra: Optional[Any] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code
        self.extra = extra

class DocumentNotFoundError(AppException):
    def __init__(self, document_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' was not found.",
            code="DOCUMENT_NOT_FOUND"
        )

class JobNotFoundError(AppException):
    def __init__(self, job_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transformation job with ID '{job_id}' was not found.",
            code="JOB_NOT_FOUND"
        )

class OutputNotFoundError(AppException):
    def __init__(self, output_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generated output with ID '{output_id}' was not found.",
            code="OUTPUT_NOT_FOUND"
        )

class ModelNotFoundError(AppException):
    def __init__(self, model_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model engine '{model_id}' is not registered or unavailable.",
            code="MODEL_NOT_FOUND"
        )

class ModelInferenceError(AppException):
    def __init__(self, model_id: str, message: str):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Inference failed for model '{model_id}': {message}",
            code="MODEL_INFERENCE_ERROR"
        )

class DocumentProcessingError(AppException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Document processing failed: {message}",
            code="DOCUMENT_PROCESSING_ERROR"
        )

class SSRFSecurityViolation(AppException):
    def __init__(self, url: str, reason: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"SSRF Protection: URL '{url}' is forbidden: {reason}",
            code="SSRF_FORBIDDEN"
        )
