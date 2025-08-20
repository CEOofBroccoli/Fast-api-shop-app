from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
    OperationalError,
    TimeoutError,
)
from pydantic import ValidationError as PydanticValidationError
from jose import JWTError
import logging
import traceback
from typing import Dict, Any, Optional
import uuid
from datetime import datetime, timezone
import re
import html

# Configure logging
logger = logging.getLogger(__name__)


# Custom Exception Classes
class BaseCustomException(Exception):
    """Base exception class for custom exceptions"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc)
        self.request_id = str(uuid.uuid4())
        super().__init__(self.message)


class DatabaseError(BaseCustomException):
    """Database related errors"""

    pass


class AuthenticationError(BaseCustomException):
    """Authentication related errors"""

    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, details)


class AuthorizationError(BaseCustomException):
    """Authorization related errors"""

    def __init__(
        self,
        message: str = "Access denied",
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, details)


class ValidationError(BaseCustomException):
    """Input validation errors"""

    pass


class BusinessLogicError(BaseCustomException):
    """Business logic related errors"""

    pass


class ResourceNotFoundError(BaseCustomException):
    """Resource not found errors"""

    def __init__(self, resource_type: str, resource_id: Any = None):
        message = f"{resource_type} not found"
        if resource_id:
            message += f" with ID: {resource_id}"
        super().__init__(
            message,
            "RESOURCE_NOT_FOUND",
            {"resource_type": resource_type, "resource_id": resource_id},
        )


class DuplicateResourceError(BaseCustomException):
    """Duplicate resource errors"""

    def __init__(self, resource_type: str, field: str, value: Any):
        message = f"{resource_type} with {field} '{value}' already exists"
        super().__init__(
            message,
            "DUPLICATE_RESOURCE",
            {"resource_type": resource_type, "field": field, "value": value},
        )


class RateLimitError(BaseCustomException):
    """Rate limiting errors"""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT_EXCEEDED")


class ExternalServiceError(BaseCustomException):
    """External service errors"""

    pass


class InventoryBusinessError(BusinessLogicError):
    """Inventory-specific business logic errors"""

    def __init__(
        self,
        message: str,
        error_code: str = "INVENTORY_BUSINESS_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, details)


class OrderStatusError(InventoryBusinessError):
    """Order status transition errors"""

    def __init__(self, current_status: str, target_status: str):
        message = (
            f"Invalid status transition from '{current_status}' to '{target_status}'"
        )
        super().__init__(
            message,
            "ORDER_STATUS_ERROR",
            {"current_status": current_status, "target_status": target_status},
        )


def sanitize_log_input(input_str: str) -> str:
    """Sanitize input for logging to prevent log injection"""
    if not isinstance(input_str, str):
        input_str = str(input_str)

    # Remove or replace newline characters and other control characters
    sanitized = re.sub(r"[\r\n\t\x00-\x1f\x7f-\x9f]", " ", input_str)
    # HTML encode to prevent XSS in log viewers
    sanitized = html.escape(sanitized)
    # Limit length to prevent log flooding
    return sanitized[:1000] if len(sanitized) > 1000 else sanitized


# Exception Handlers
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors"""
    error_id = str(uuid.uuid4())

    # Log detailed error information with sanitized inputs
    logger.error(
        f"Database error [{error_id}]: {sanitize_log_input(str(exc))}",
        extra={
            "error_id": error_id,
            "url": sanitize_log_input(str(request.url)),
            "method": sanitize_log_input(request.method),
            "exception_type": type(exc).__name__,
            "traceback": sanitize_log_input(traceback.format_exc()),
        },
    )

    # Determine specific error type and response
    if isinstance(exc, OperationalError):
        if "connection" in str(exc).lower():
            detail = "Database connection failed"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            detail = "Database operation failed"
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(exc, TimeoutError):
        detail = "Database operation timed out"
        status_code = status.HTTP_504_GATEWAY_TIMEOUT
    else:
        detail = "Database error occurred"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": "DATABASE_ERROR",
                "message": detail,
                "error_id": error_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )


async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """Handle database integrity constraint violations"""
    error_id = str(uuid.uuid4())

    logger.error(
        f"Database integrity error [{error_id}]: {sanitize_log_input(str(exc))}",
        extra={
            "error_id": error_id,
            "url": sanitize_log_input(str(request.url)),
            "method": sanitize_log_input(request.method),
            "exception_type": type(exc).__name__,
        },
    )

    # Parse common integrity errors
    error_message = str(exc.orig) if hasattr(exc, "orig") else str(exc)

    if "unique constraint" in error_message.lower():
        detail = "Resource already exists"
        error_code = "DUPLICATE_RESOURCE"
    elif "foreign key constraint" in error_message.lower():
        detail = "Referenced resource does not exist"
        error_code = "INVALID_REFERENCE"
    elif "not null constraint" in error_message.lower():
        detail = "Required field is missing"
        error_code = "MISSING_REQUIRED_FIELD"
    else:
        detail = "Data integrity constraint violated"
        error_code = "INTEGRITY_ERROR"

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": error_code,
                "message": detail,
                "error_id": error_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )


async def pydantic_validation_exception_handler(
    request: Request, exc: PydanticValidationError
):
    """Handle Pydantic validation errors"""
    error_id = str(uuid.uuid4())

    logger.warning(
        f"Pydantic validation error [{error_id}]: {sanitize_log_input(str(exc))}",
        extra={
            "error_id": error_id,
            "url": sanitize_log_input(str(request.url)),
            "method": sanitize_log_input(request.method),
            "validation_errors": [
                sanitize_log_input(str(error)) for error in exc.errors()
            ],
        },
    )

    # Format validation errors for better client understanding
    formatted_errors = []
    for error in exc.errors():
        formatted_errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "error_id": error_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": formatted_errors,
            }
        },
    )


async def authentication_exception_handler(request: Request, exc: AuthenticationError):
    """Handle authentication errors"""
    error_id = str(uuid.uuid4())

    logger.warning(
        f"Authentication error [{error_id}]: {sanitize_log_input(exc.message)}",
        extra={
            "error_id": error_id,
            "url": sanitize_log_input(str(request.url)),
            "method": sanitize_log_input(request.method),
            "error_code": sanitize_log_input(exc.error_code),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "error_id": error_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


async def authorization_exception_handler(request: Request, exc: AuthorizationError):
    """Handle authorization errors"""
    error_id = str(uuid.uuid4())

    logger.warning(
        f"Authorization error [{error_id}]: {sanitize_log_input(exc.message)}",
        extra={
            "error_id": error_id,
            "url": sanitize_log_input(str(request.url)),
            "method": sanitize_log_input(request.method),
            "error_code": sanitize_log_input(exc.error_code),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "error_id": error_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )


async def business_logic_exception_handler(request: Request, exc: BusinessLogicError):
    """Handle business logic errors"""
    error_id = str(uuid.uuid4())

    logger.warning(
        f"Business logic error [{error_id}]: {sanitize_log_input(exc.message)}",
        extra={
            "error_id": error_id,
            "url": sanitize_log_input(str(request.url)),
            "method": sanitize_log_input(request.method),
            "error_code": sanitize_log_input(exc.error_code),
            "details": {k: sanitize_log_input(str(v)) for k, v in exc.details.items()},
        },
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "error_id": error_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": exc.details,
            }
        },
    )


async def resource_not_found_exception_handler(
    request: Request, exc: ResourceNotFoundError
):
    """Handle resource not found errors"""
    error_id = str(uuid.uuid4())

    logger.info(
        f"Resource not found [{error_id}]: {sanitize_log_input(exc.message)}",
        extra={
            "error_id": error_id,
            "url": sanitize_log_input(str(request.url)),
            "method": sanitize_log_input(request.method),
            "error_code": sanitize_log_input(exc.error_code),
            "details": {k: sanitize_log_input(str(v)) for k, v in exc.details.items()},
        },
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "error_id": error_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": exc.details,
            }
        },
    )


async def duplicate_resource_exception_handler(
    request: Request, exc: DuplicateResourceError
):
    """Handle duplicate resource errors"""
    error_id = str(uuid.uuid4())

    logger.warning(
        f"Duplicate resource error [{error_id}]: {sanitize_log_input(exc.message)}",
        extra={
            "error_id": error_id,
            "url": sanitize_log_input(str(request.url)),
            "method": sanitize_log_input(request.method),
            "error_code": sanitize_log_input(exc.error_code),
            "details": {k: sanitize_log_input(str(v)) for k, v in exc.details.items()},
        },
    )

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "error_id": error_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": exc.details,
            }
        },
    )


async def rate_limit_exception_handler(request: Request, exc: RateLimitError):
    """Handle rate limiting errors"""
    error_id = str(uuid.uuid4())

    logger.warning(
        f"Rate limit error [{error_id}]: {sanitize_log_input(exc.message)}",
        extra={
            "error_id": error_id,
            "url": sanitize_log_input(str(request.url)),
            "method": sanitize_log_input(request.method),
            "error_code": sanitize_log_input(exc.error_code),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "error_id": error_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
        headers={"Retry-After": "60"},
    )


async def external_service_exception_handler(
    request: Request, exc: ExternalServiceError
):
    """Handle external service errors"""
    error_id = str(uuid.uuid4())

    logger.error(
        f"External service error [{error_id}]: {sanitize_log_input(exc.message)}",
        extra={
            "error_id": error_id,
            "url": sanitize_log_input(str(request.url)),
            "method": sanitize_log_input(request.method),
            "error_code": sanitize_log_input(exc.error_code),
            "details": {k: sanitize_log_input(str(v)) for k, v in exc.details.items()},
        },
    )

    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "error_id": error_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": exc.details,
            }
        },
    )


async def jwt_exception_handler(request: Request, exc: JWTError):
    """Handle JWT errors"""
    error_id = str(uuid.uuid4())

    logger.warning(
        f"JWT error [{error_id}]: {sanitize_log_input(str(exc))}",
        extra={
            "error_id": error_id,
            "url": sanitize_log_input(str(request.url)),
            "method": sanitize_log_input(request.method),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": {
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired token",
                "error_id": error_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions"""
    error_id = str(uuid.uuid4())

    logger.warning(
        f"HTTP exception [{error_id}]: {sanitize_log_input(str(exc.detail))}",
        extra={
            "error_id": error_id,
            "url": sanitize_log_input(str(request.url)),
            "method": sanitize_log_input(request.method),
            "status_code": exc.status_code,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "error_id": error_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
        headers=getattr(exc, "headers", None),
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    error_id = str(uuid.uuid4())

    logger.error(
        f"Unhandled exception [{error_id}]: {sanitize_log_input(str(exc))}",
        extra={
            "error_id": error_id,
            "url": sanitize_log_input(str(request.url)),
            "method": sanitize_log_input(request.method),
            "exception_type": type(exc).__name__,
            "traceback": sanitize_log_input(traceback.format_exc()),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "error_id": error_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )


# Exception handler mapping for easy registration
EXCEPTION_HANDLERS = {
    SQLAlchemyError: database_exception_handler,
    IntegrityError: integrity_exception_handler,
    PydanticValidationError: pydantic_validation_exception_handler,
    AuthenticationError: authentication_exception_handler,
    AuthorizationError: authorization_exception_handler,
    BusinessLogicError: business_logic_exception_handler,
    InventoryBusinessError: business_logic_exception_handler,
    OrderStatusError: business_logic_exception_handler,
    ResourceNotFoundError: resource_not_found_exception_handler,
    DuplicateResourceError: duplicate_resource_exception_handler,
    RateLimitError: rate_limit_exception_handler,
    ExternalServiceError: external_service_exception_handler,
    JWTError: jwt_exception_handler,
    HTTPException: http_exception_handler,
    Exception: general_exception_handler,
}
