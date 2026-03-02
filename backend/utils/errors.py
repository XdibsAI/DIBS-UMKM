"""
Standard Error Handling untuk DIBS AI
"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from functools import wraps
import logging
from typing import Callable, Type, Dict, Any

logger = logging.getLogger(__name__)

class DibsException(Exception):
    """Base exception untuk DIBS AI"""
    def __init__(self, message: str, code: int = 400, details: Dict[str, Any] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class NotFoundError(DibsException):
    """Resource tidak ditemukan"""
    def __init__(self, message: str = "Resource tidak ditemukan", details: Dict[str, Any] = None):
        super().__init__(message, 404, details)

class ValidationError(DibsException):
    """Validasi input error"""
    def __init__(self, message: str = "Data tidak valid", details: Dict[str, Any] = None):
        super().__init__(message, 400, details)

class AuthError(DibsException):
    """Authentication/Authorization error"""
    def __init__(self, message: str = "Tidak memiliki akses", details: Dict[str, Any] = None):
        super().__init__(message, 401, details)

class DatabaseError(DibsException):
    """Database operation error"""
    def __init__(self, message: str = "Database error", details: Dict[str, Any] = None):
        super().__init__(message, 500, details)

def handle_errors(func: Callable) -> Callable:
    """Decorator untuk handle exceptions di routes"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except DibsException as e:
            logger.warning(f"DibsException: {e.message} (code: {e.code})")
            return JSONResponse(
                status_code=e.code,
                content={
                    "success": False,
                    "error": e.message,
                    "details": e.details
                }
            )
        except HTTPException as e:
            logger.warning(f"HTTPException: {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": e.detail
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Internal server error",
                    "detail": str(e) if logger.isEnabledFor(logging.DEBUG) else None
                }
            )
    return wrapper

def with_transaction(func: Callable) -> Callable:
    """Decorator untuk database transaction"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # This will be implemented with database transaction
        # For now, just pass through
        return await func(*args, **kwargs)
    return wrapper

# Alias untuk backward compatibility
with_error_handling = handle_errors

# Alias for backward compatibility
with_error_handling = handle_errors
