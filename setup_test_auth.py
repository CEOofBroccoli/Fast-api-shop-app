from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models.user import User
from backend.app.auth.auth_handler import get_password_hash
import os
import sys

# Create database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./backend/app/shop.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def setup_test_user():
    """Create a test user with known credentials"""
    username = "testuser"
    password = "test123"
    email = "test@example.com"
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        print(f"Deleting existing user {username}")
        db.delete(existing_user)
        db.commit()
    
    # Create new user with hashed password
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name="Test User",
        role="admin",  # Make them admin for full access
        is_verified=True  # Skip email verification
    )
    
    try:
        db.add(user)
        db.commit()
        print(f"""
Test user created successfully!
================================
Username: {username}
Password: {password}
Email: {email}
Role: admin
================================
To test the login:
1. Start the server with: uvicorn backend.app.main:app --reload
2. Go to http://localhost:8000/docs
3. Click the "Authorize" button
4. Enter these credentials:
   - Username: {username}
   - Password: {password}
5. After login, copy the token and use it in the "Authorization: Bearer <token>" header
""")
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating test user for authentication...")
    setup_test_user()