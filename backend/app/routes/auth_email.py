from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.auth.jwt_handler import create_access_token, verify_token
from backend.app.auth.auth_handler import get_user_by_email, get_password_hash
from backend.app.schemas.user import user as UserSchema, user_create
from backend.app.models.email_token import EmailToken
from backend.app.email_utils import send_email
from backend.app.utils.rate_limiter import rate_limit
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import secrets
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])

class EmailVerificationRequest(BaseModel):
    email: str

class EmailVerificationConfirm(BaseModel):
    token: str

# Legacy rate limiting implementation kept for backward compatibility
# but we'll use the new rate limiter for actual rate limiting
rate_limits = {}
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 5      # max requests per window

def check_rate_limit(key: str):
    """
    Legacy rate limiting function. 
    This is kept for backward compatibility but actual rate limiting
    is now handled by the rate_limit decorator.
    """
    logger.debug(f"Rate limit check for {key} - using new rate limiter instead")
    # The actual rate limiting is now handled by the decorator

@router.post("/send-verification-email")
@rate_limit(endpoint_type="auth")
async def send_verification_email(request: Request, data: EmailVerificationRequest, db: Session = Depends(get_db)):
    # Legacy rate limit for backward compatibility
    check_rate_limit(f"verify:{data.email}")
    
    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if getattr(user, "is_verified", False):
        return {"message": "Email already verified"}
    
    # Remove any existing verification tokens for this user
    db.query(EmailToken).filter(EmailToken.user_id == user.id, EmailToken.type == "verification").delete()
    
    # Create secure token with sufficient entropy
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)
    db_token = EmailToken(user_id=user.id, token=token, type="verification", expires=expires)
    db.add(db_token)
    db.commit()
    
    # Send email with verification link
    verify_url = f"http://localhost:8000/auth/verify-email?token={token}"
    body = f"Your verification code is: {token}\nOr click: {verify_url}"
    send_email(str(user.email), "Verify your email", body)
    
    logger.info(f"Verification email sent to {data.email}")
    return {"message": "Verification email sent"}

@router.post("/verify-email")
@rate_limit(endpoint_type="auth")
async def verify_email(request: Request, data: EmailVerificationConfirm, db: Session = Depends(get_db)):
    # Validate and verify the token
    db_token = db.query(EmailToken).filter(EmailToken.token == data.token, EmailToken.type == "verification").first()
    from datetime import timezone
    now = datetime.now(timezone.utc)
    
    if db_token is None or db_token.expires.replace(tzinfo=timezone.utc) < now:
        logger.warning(f"Invalid or expired verification token attempt: {data.token[:8]}...")
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        logger.error(f"User not found for valid token: {db_token.user_id}")
        raise HTTPException(status_code=404, detail="User not found")
        
    # Update user verification status
    db.query(User).filter(User.id == user.id).update({"is_verified": True})
    db.commit()
    db.refresh(user)
    
    # Delete the used token for security
    db.delete(db_token)
    db.commit()
    
    logger.info(f"Email verified successfully for user ID: {user.id}")
    return {"message": "Email verified successfully"}

# Example: rate limit signup/login (add check_rate_limit to those endpoints)
