from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import engine, Base, get_db
from app.models import user, order # Import order model
from app.schemas.user import user_create, user, token
from app.auth.auth_handler import create_user, authenticate_user
from app.auth.jwt_handler import create_access_token, verify_token
from datetime import timedelta
from typing import List
from app.routes import orders, reports  # Import the reports router

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

@app.get("Sign Up")
def sign_up():
    return {"message": "Sign Up endpoint"}

@app.get("Login")
def Login():
    return {"message": "Login endpoint"}

@app.get("/TDB") # function baraye test connection database
def test_DB(db_session: Session = Depends(get_db)):
    try:
        db_session.execute(text("SELECT 1"))
        return {"message": "Database connection is working"}
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))