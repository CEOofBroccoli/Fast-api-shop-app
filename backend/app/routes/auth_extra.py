import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.auth.auth_handler import (
    get_password_hash,
    get_user_by_email,
    update_last_login,
)
from backend.app.auth.jwt_handler import create_access_token, verify_token
from backend.app.database import get_db
from backend.app.email_utils import send_email
from backend.app.models.email_token import EmailToken
from backend.app.models.user import User
from backend.app.schemas.user import user as UserSchema

router = APIRouter(prefix="/auth", tags=["Auth"])


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


@router.post("/request-password-reset")
async def request_password_reset(
    data: PasswordResetRequest, db: Session = Depends(get_db)
):
    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Remove any existing reset tokens for this user
    db.query(EmailToken).filter(
        EmailToken.user_id == user.id, EmailToken.type == "reset"
    ).delete()
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)
    db_token = EmailToken(user_id=user.id, token=token, type="reset", expires=expires)
    db.add(db_token)
    db.commit()
    # Send email
    reset_url = f"http://localhost:8000/auth/reset-password?token={token}"
    body = f"Your password reset code is: {token}\nOr click: {reset_url}"
    send_email(str(user.email), "Password Reset Request", body)
    return {"message": "Password reset email sent"}


@router.post("/reset-password")
async def reset_password(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    from datetime import timezone

    db_token = (
        db.query(EmailToken)
        .filter(EmailToken.token == data.token, EmailToken.type == "reset")
        .first()
    )
    now = datetime.now(timezone.utc)
    if db_token is None or db_token.expires.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    setattr(user, "hashed_password", get_password_hash(data.new_password))
    db.commit()
    db.refresh(user)
    db.delete(db_token)
    db.commit()
    return {"message": "Password reset successful"}
