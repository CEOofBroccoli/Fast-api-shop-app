from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.schemas.user import user as UserSchema, user_update
from app.auth.jwt_handler import verify_token
from app.auth.auth_handler import get_user_by_email, require_role

router = APIRouter(prefix="/users", tags=["Users"])

# Helper to get current user and check role
async def get_current_user_and_check_role(authorization: Optional[str], db: Session, allowed_roles: list):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    token = authorization.split(" ")[1]
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return user

@router.get("/", response_model=List[UserSchema])
async def list_users(db: Session = Depends(get_db), authorization: Optional[str] = Header(None)):
    await get_current_user_and_check_role(authorization, db, ["admin"])
    return db.query(User).all()

@router.get("/{user_id}", response_model=UserSchema)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db), authorization: Optional[str] = Header(None)):
    await get_current_user_and_check_role(authorization, db, ["admin"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(user_id: int, user_data: user_update, db: Session = Depends(get_db), authorization: Optional[str] = Header(None)):
    await get_current_user_and_check_role(authorization, db, ["admin"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db), authorization: Optional[str] = Header(None)):
    await get_current_user_and_check_role(authorization, db, ["admin"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return
