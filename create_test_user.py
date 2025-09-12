from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models.user import User
from passlib.context import CryptContext

# Create database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./backend/app/shop.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Use the same password hashing config as auth_handler.py
from backend.app.auth.auth_handler import pwd_context

def create_admin_user():
    """Create an admin user for testing"""
    password = "admin123"  # Plain text password
    
    # Delete existing admin user if exists
    existing_user = db.query(User).filter(User.username == "admin").first()
    if existing_user:
        print("Removing existing admin user")
        db.delete(existing_user)
        db.commit()
        
    # Hash the password and create user
    print(f"Creating admin user with password: {password}")
    password_hash = pwd_context.hash(password)
    print(f"Password hash: {password_hash}")
    
    # Create new admin user
    password_hash = pwd_context.hash("admin123")
    admin_user = User(
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        hashed_password=password_hash,
        role="admin",
        is_verified=True
    )
    
    try:
        db.add(admin_user)
        db.commit()
        print("Admin user created successfully")
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()