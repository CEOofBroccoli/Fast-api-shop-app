from fastapi import FastAPI, Depends, HTTPException, status
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import engine, Base, get_db
from app.models import user, order , product# Import  models
from app.schemas.user import user_create, user, token
from app.auth.auth_handler import create_user_secure, authenticate_user, get_user_by_email, get_user, update_last_login
from app.auth.jwt_handler import create_access_token, verify_token, get_current_user
from datetime import timedelta
from typing import List
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.routes import orders, reports, products
from app.routes import users


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI(title="Inventory Management System")
Base.metadata.create_all(bind=engine) #sakht table to database

app.include_router(orders.router)
app.include_router(reports.router)
app.include_router(products.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Inventory Management System API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/signup", response_model=user)
def sign_up(user_data: user_create, db: Session = Depends(get_db)):
    try:
        return create_user_secure(db=db, user=user_data)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Signup failed")

@app.post("/login", response_model=token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_obj = authenticate_user(db, form_data.username, form_data.password)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    update_last_login(db, user_obj)
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user_obj.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=user)
def read_users_me(current_user: user = Depends(get_current_user)):
    return current_user

@app.get("/test-db")
def test_db(db_session: Session = Depends(get_db)):
    try:
        db_session.execute(text("SELECT 1"))
        return {"message": "Database connection is working"}
    except Exception as error:
        logger.error(f"Database connection test failed: {str(error)}")
        raise