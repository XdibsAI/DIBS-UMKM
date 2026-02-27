from typing import Optional, Any
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class DibsError(Exception):
    """Base exception class for DIBS"""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)

class VideoGenerationError(DibsError):
    """Video generation specific errors"""
    def __init__(self, message: str, project_id: Optional[str] = None):
        super().__init__(
            message=f"Video generation failed: {message}",
            code="VIDEO_GEN_ERROR",
            status_code=500
        )
        self.project_id = project_id

class DatabaseError(DibsError):
    """Database operation errors"""
    def __init__(self, message: str, query: Optional[str] = None):
        super().__init__(
            message=f"Database error: {message}",
            code="DB_ERROR",
            status_code=500
        )
        self.query = query

class ValidationError(DibsError):
    """Input validation errors"""
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=f"Validation error: {message}",
            code="VALIDATION_ERROR",
            status_code=400
        )
        self.field = field

async def error_handler_middleware(request: Request, call_next):
    """Global error handling middleware"""
    try:
        return await call_next(request)
    except DibsError as e:
        logger.error(f"DIBS Error: {e.message} (code: {e.code})")
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "details": getattr(e, "project_id", None) or getattr(e, "field", None) or getattr(e, "query", None)
                }
            }
        )
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"error": {"code": "HTTP_ERROR", "message": e.detail}}
        )
    except Exception as e:
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred"
                }
            }
        )

def with_error_handling(func):
    """Decorator for error handling in routes"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except DibsError:
            raise
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error in {func.__name__}")
            raise VideoGenerationError(str(e))
    return wrapper
