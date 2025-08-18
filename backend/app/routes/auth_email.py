from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.auth.jwt_handler import create_access_token, verify_token
from backend.app.auth.auth_handler import get_user_by_email, get_password_hash
from backend.app.schemas.user import user as UserSchema, user_create
from backend.app.models.email_token import EmailToken
from backend.app.utils import send_email
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import secrets

router = APIRouter(prefix="/auth", tags=["Auth"])

# In-memory rate limit store (keep for now)
rate_limits = {}

class EmailVerificationRequest(BaseModel):
    email: str

class EmailVerificationConfirm(BaseModel):
    token: str

RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 5      # max requests per window

def check_rate_limit(key: str):
    now = datetime.utcnow().timestamp()
    window = int(now // RATE_LIMIT_WINDOW)
    if key not in rate_limits:
        rate_limits[key] = {}
    if window not in rate_limits[key]:
        rate_limits[key] = {window: 1}
    else:
        rate_limits[key][window] += 1
    if rate_limits[key][window] > RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")

@router.post("/send-verification-email")
async def send_verification_email(data: EmailVerificationRequest, db: Session = Depends(get_db)):
    check_rate_limit(f"verify:{data.email}")
    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if getattr(user, "is_verified", False):
        return {"message": "Email already verified"}
    # Remove any existing verification tokens for this user
    db.query(EmailToken).filter(EmailToken.user_id == user.id, EmailToken.type == "verification").delete()
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)
    db_token = EmailToken(user_id=user.id, token=token, type="verification", expires=expires)
    db.add(db_token)
    db.commit()
    # Send email
    verify_url = f"http://localhost:8000/auth/verify-email?token={token}"
    body = f"Your verification code is: {token}\nOr click: {verify_url}"
    send_email(str(user.email), "Verify your email", body)
    return {"message": "Verification email sent"}

@router.post("/verify-email")
async def verify_email(data: EmailVerificationConfirm, db: Session = Depends(get_db)):
    db_token = db.query(EmailToken).filter(EmailToken.token == data.token, EmailToken.type == "verification").first()
    from datetime import timezone
    now = datetime.now(timezone.utc)
    if db_token is None or db_token.expires.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = bool(True)
    db.commit()
    db.refresh(user)
    db.delete(db_token)
    db.commit()
    return {"message": "Email verified successfully"}

# Example: rate limit signup/login (add check_rate_limit to those endpoints)
