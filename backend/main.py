from fastapi import FastAPI, status, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Annotated, List
from sqlalchemy import text
from app.database import get_db, Base, engine
from app.models import user

app = FastAPI(title="Inventory Management System")

Base.metadata.create_all(bind=engine)

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

@app.get("/TDB")
def test_DB(db_session: Session = Depends(get_db)):
    try:
        db_session.execute(text("SELECT 1"))
        return {"message": "Database connection is working"}
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))