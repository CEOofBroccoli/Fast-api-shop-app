import logging
from typing import Any, Dict, List, Union

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom exception handler for validation errors.

    Formats validation errors in a consistent, user-friendly structure
    and logs the error details for debugging purposes.
    """
    error_details = []

    for error in exc.errors():
        error_details.append(
            {"loc": error["loc"], "msg": error["msg"], "type": error["type"]}
        )

    logger.warning(f"Validation error: {error_details}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Validation failed",
            "details": error_details,
        },
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Custom exception handler for database errors.

    Provides a clean response to the client while logging detailed
    error information for troubleshooting.
    """
    error_message = "Database operation failed"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    # Handle specific database exceptions differently
    if isinstance(exc, IntegrityError):
        error_message = "Database integrity constraint violated"
        status_code = status.HTTP_409_CONFLICT

    logger.error(f"Database error: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status_code, content={"status": "error", "message": error_message}
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Fallback exception handler for all other exceptions.

    Ensures all unhandled exceptions return a consistent error response
    format without exposing internal details to the client.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": "An unexpected error occurred"},
    )


def register_exception_handlers(app):
    """
    Register all custom exception handlers with the FastAPI application.
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
