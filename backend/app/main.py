from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import engine, Base, get_db
from app.models import user, order, product
from app.schemas.user import user as UserSchema, user_create, token
from app.auth.auth_handler import create_user, authenticate_user, get_user_by_email
from app.auth.jwt_handler import create_access_token, get_current_user
from datetime import timedelta
from typing import List
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.routes import orders, reports
from app.exceptions import EXCEPTION_HANDLERS, DuplicateResourceError, AuthenticationError
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(
    title="Inventory Management System",
    description="A comprehensive inventory management system with proper error handling",
    version="1.0.0"
)

for exception_class, handler in EXCEPTION_HANDLERS.items():
    app.add_exception_handler(exception_class, handler)

Base.metadata.create_all(bind=engine)

app.include_router(orders.router)
app.include_router(reports.router)

@app.get("/")
def root():
    return {"message": "Inventory Management System API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/signup", response_model=UserSchema)
def sign_up(user_data: user_create, db: Session = Depends(get_db)):
    try:
        db_user = get_user_by_email(db, user_data.email)
        if db_user:
            raise DuplicateResourceError("User", "email", user_data.email)
        return create_user(db=db, user=user_data)
    except DuplicateResourceError:
        raise
    except Exception as e:
        logger.error(f"Error during user signup: {str(e)}")
        raise

@app.post("/login", response_model=token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise AuthenticationError("Incorrect username or password")
        
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error during user login: {str(e)}")
        raise AuthenticationError("Login failed")

@app.get("/users/me", response_model=UserSchema)
def read_users_me(current_user: UserSchema = Depends(get_current_user)):
    return current_user

@app.get("/test-db")
def test_db(db_session: Session = Depends(get_db)):
    try:
        db_session.execute(text("SELECT 1"))
        return {"message": "Database connection is working"}
    except Exception as error:
        logger.error(f"Database connection test failed: {str(error)}")
        raise