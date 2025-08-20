# Authentication handler for user management and password security
import re
from datetime import datetime, timezone

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.app.auth.jwt_handler import create_access_token
from backend.app.models.user import User
from backend.app.schemas.user import user_create

# Password hashing configuration using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Generate password hash using bcrypt"""
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    """Get user by username with input validation"""
    # Input validation to prevent injection
    if not username or not isinstance(username, str) or len(username) > 50:
        return None
    # Sanitize username - allow only alphanumeric and basic characters
    if not re.match(r"^[a-zA-Z0-9_.-]+$", username):
        return None
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    """Get user by email with validation"""
    # Input validation to prevent injection
    if not email or not isinstance(email, str) or len(email) > 100:
        return None
    # Basic email format validation
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return None
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user with username and password"""
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_user_secure(db: Session, user: user_create):
    """Create new user with password validation and security checks"""
    if not is_password_complex(user.password):
        raise ValueError(
            "Password must be at least 8 characters and include letters, numbers, and special characters."
        )
    if get_user_by_email(db, user.email):
        raise ValueError("Email already registered.")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        full_name=user.full_name,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Password complexity enforcement
def is_password_complex(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Za-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
        return False
    return True


# Role-based access control utility
def require_role(user, allowed_roles):
    if user.role not in allowed_roles:
        raise Exception("Insufficient permissions")


# Enhanced create_user with password complexity and email uniqueness
def create_user(db: Session, user: user_create):
    if not is_password_complex(user.password):
        raise ValueError(
            "Password must be at least 8 characters and include letters, numbers, and special characters."
        )
    if get_user_by_email(db, user.email):
        raise ValueError("Email already registered.")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        full_name=user.full_name,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Update last_login on successful login
def update_last_login(db: Session, user: User):
    db.query(User).filter(User.id == user.id).update(
        {User.last_login: datetime.now(timezone.utc)}
    )
    db.commit()
    db.refresh(user)
