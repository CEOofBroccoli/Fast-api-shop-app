from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import engine, Base, get_db
from app.models import user, order # Import order model
from app.schemas.user import user_create, user, token
from app.auth.auth_handler import create_user, authenticate_user, get_user_by_email, get_user
from app.auth.jwt_handler import create_access_token, verify_token, get_current_user
from datetime import timedelta
from typing import List
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.routes import orders, reports  # Import the reports router
from app.models import user, order, product

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(title="Inventory Management System")
Base.metadata.create_all(bind=engine) #sakht table to database

app.include_router(orders.router)  # Include the orders router
app.include_router(reports.router)  # Include the reports router

@app.get("/")
def root():
    return {"message": "Inventory Management System API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/signup", response_model=user)
def sign_up(user_data: user_create, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user_data.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return create_user(db=db, user=user_data)

@app.post("/login", response_model=token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
@app.get("/users/me", response_model=user)
def read_users_me(current_user = Depends(get_current_user)):
    return current_user

@app.get("/TDB") # function baraye test connection database
def test_DB(db_session: Session = Depends(get_db)):
    try:
        db_session.execute(text("SELECT 1"))
        return {"message": "Database connection is working"}
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))