"""
Custom exceptions for the B-Search API
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException


class BSearchException(Exception):
    """Base exception for B-Search API"""

    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BSearchException):
    """Validation error"""

    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details or {})
        if field:
            self.details["field"] = field


class NotFoundError(BSearchException):
    """Resource not found error"""

    def __init__(self, resource: str, resource_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(message, status_code=404, details=details or {})


class AuthenticationError(BSearchException):
    """Authentication error"""

    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details or {})


class AuthorizationError(BSearchException):
    """Authorization error"""

    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details or {})


class ExternalServiceError(BSearchException):
    """External service error"""

    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"{service} error: {message}", status_code=502, details=details or {})
        self.service = service


class ConfigurationError(BSearchException):
    """Configuration error"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details or {})


class DatabaseError(BSearchException):
    """Database error"""

    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details or {})
        if operation:
            self.details["operation"] = operation


class CollectorError(BSearchException):
    """Data collection error"""

    def __init__(self, collector: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Collection error ({collector}): {message}", status_code=502, details=details or {})
        self.collector = collector


class AIError(BSearchException):
    """AI processing error"""

    def __init__(self, operation: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"AI error ({operation}): {message}", status_code=500, details=details or {})
        self.operation = operation


class FileProcessingError(BSearchException):
    """File processing error"""

    def __init__(self, filename: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"File processing error ({filename}): {message}", status_code=400, details=details or {})
        self.filename = filename


def handle_bsearch_exception(exc: BSearchException) -> HTTPException:
    """Convert BSearchException to FastAPI HTTPException"""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details
        }
    )


def handle_generic_exception(exc: Exception, status_code: int = 500) -> HTTPException:
    """Convert generic exception to FastAPI HTTPException"""
    return HTTPException(
        status_code=status_code,
        detail={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {"type": exc.__class__.__name__}
        }
    )