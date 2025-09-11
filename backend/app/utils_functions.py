import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(to_email: str, subject: str, body: str):
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM", smtp_user)

    # Ensure all required config is present
    if not all([smtp_host, smtp_port, smtp_user, smtp_password, email_from]):
        raise RuntimeError("SMTP configuration is incomplete. Please check your .env file.")

    msg = MIMEMultipart()
    msg["From"] = str(email_from)
    msg["To"] = str(to_email)
    msg["Subject"] = str(subject)
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(str(smtp_user), str(smtp_password))
        server.sendmail(str(email_from), str(to_email), msg.as_string())


import logging
import re
from typing import Optional, Tuple

from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.auth.jwt_handler import verify_token
from backend.app.exceptions import AuthenticationError, AuthorizationError, ResourceNotFoundError, ValidationError
from backend.app.models.user import User

logger = logging.getLogger(__name__)


def validate_token_header(authorization: Optional[str]) -> str:
    """
    Extract and validate Bearer token from authorization header

    Args:
        authorization: Authorization header value

    Returns:
        str: Valid JWT token

    Raises:
        AuthenticationError: If token is invalid or missing
    """
    if not authorization:
        raise AuthenticationError("Missing authorization header")

    if not isinstance(authorization, str):
        raise AuthenticationError("Invalid authorization header type")

    if not authorization.startswith("Bearer "):
        raise AuthenticationError("Invalid authorization header format. Use 'Bearer <token>'")

    try:
        token = authorization.split(" ", 1)[1]  # More robust splitting
        if not token.strip():
            raise AuthenticationError("Missing token")
        return token
    except IndexError:
        raise AuthenticationError("Invalid authorization header format")


def get_authenticated_user(token: str, db: Session) -> User:
    """
    Get authenticated user from token with proper validation

    Args:
        token: JWT token
        db: Database session

    Returns:
        User: Authenticated user object

    Raises:
        AuthenticationError: If authentication fails
    """
    if not token:
        raise AuthenticationError("Token is required")

    try:
        username = verify_token(token)
        if not username:
            raise AuthenticationError("Invalid or expired token")

        # Input validation (as per Persian doc requirements)
        if not isinstance(username, str) or len(username) > 50:
            raise AuthenticationError("Invalid username format")

        # Sanitize username - allow only alphanumeric and basic characters
        if not re.match(r"^[a-zA-Z0-9_.-]+$", username):
            raise AuthenticationError("Invalid username format")

        # Database query with error handling
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise AuthenticationError("User not found")

        # Check if user is active (as per doc requirements)
        if not getattr(user, "is_active", True):
            raise AuthenticationError("User account is deactivated")

        return user

    except AuthenticationError:
        # Re-raise authentication errors
        raise
    except Exception as e:
        logger.error(f"Database error while fetching user: {str(e)}")
        raise AuthenticationError("Authentication service unavailable")


def validate_positive_integer(value: int, field_name: str) -> int:
    """
    Validate that a value is a positive integer

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Returns:
        int: Validated value

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, int):
        raise ValidationError(f"{field_name} must be an integer", "INVALID_TYPE", {"field": field_name})

    if value <= 0:
        raise ValidationError(
            f"{field_name} must be a positive integer",
            "INVALID_VALUE",
            {"field": field_name, "value": value},
        )

    return value


def validate_pagination(page: int, limit: int) -> Tuple[int, int]:
    """
    Validate pagination parameters

    Args:
        page: Page number
        limit: Items per page

    Returns:
        tuple: Validated (page, limit)

    Raises:
        ValidationError: If validation fails
    """
    page = max(1, validate_positive_integer(page, "page"))
    limit = validate_positive_integer(limit, "limit")

    if limit > 100:
        raise ValidationError(
            "Limit cannot exceed 100 items per page",
            "INVALID_LIMIT",
            {"limit": limit, "max_allowed": 100},
        )

    return page, limit


def validate_sku(sku: str) -> str:
    """
    Validate SKU format (as per Persian documentation requirements)

    Args:
        sku: Stock Keeping Unit identifier

    Returns:
        str: Validated SKU

    Raises:
        ValidationError: If SKU is invalid
    """
    if not sku or not isinstance(sku, str):
        raise ValidationError("SKU is required and must be a string", "MISSING_SKU")

    sku = sku.strip()

    if len(sku) > 50:
        raise ValidationError(
            "SKU cannot exceed 50 characters",
            "INVALID_SKU_LENGTH",
            {"length": len(sku), "max_length": 50},
        )

    if not re.match(r"^[A-Z0-9_-]+$", sku.upper()):
        raise ValidationError(
            "SKU must contain only uppercase letters, numbers, hyphens, and underscores",
            "INVALID_SKU_FORMAT",
        )

    return sku.upper()


def validate_role_access(user: User, required_role: str) -> bool:
    """
    Validate user role access (as per Persian documentation requirements)

    Args:
        user: Authenticated user
        required_role: Required role for operation

    Returns:
        bool: True if user has required role

    Raises:
        AuthorizationError: If user doesn't have required permissions
    """
    user_role = getattr(user, "role", "user")

    # Define role hierarchy (as per doc requirements)
    role_hierarchy = {
        "admin": ["admin"],
        "manager": ["admin", "manager"],
        "employee": ["admin", "manager", "employee"],
        "user": ["admin", "manager", "employee", "user"],
    }

    if required_role not in role_hierarchy.get(user_role, []):
        raise AuthorizationError(
            f"Insufficient permissions. Required role: {required_role}",
            "INSUFFICIENT_PERMISSIONS",
            {"user_role": user_role, "required_role": required_role},
        )

    return True


def sanitize_input(text: str, max_length: int = 255) -> str:
    """
    Sanitize user input to prevent injection attacks

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        str: Sanitized text
    """
    if not text or not isinstance(text, str):
        return ""

    # Strip whitespace and limit length
    sanitized = text.strip()[:max_length]

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', "", sanitized)

    return sanitized


def validate_order_status_transition(current_status: str, new_status: str) -> bool:
    """
    Validate order status transitions according to business rules

    Args:
        current_status: Current order status
        new_status: Target order status

    Returns:
        bool: True if transition is valid

    Raises:
        ValidationError: If transition is invalid
    """
    allowed_transitions = {
        "Draft": ["Sent"],
        "Sent": ["Received"],
        "Received": ["Closed"],
        "Closed": [],
    }

    if new_status not in allowed_transitions.get(current_status, []):
        raise ValidationError(
            f"Invalid status transition from '{current_status}' to '{new_status}'",
            "INVALID_STATUS_TRANSITION",
            {"current_status": current_status, "target_status": new_status},
        )

    return True
