import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import get_db, Base, engine
import sqlalchemy
from fastapi import FastAPI
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Setup test client
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    # Drop all tables first to ensure a clean state
    Base.metadata.drop_all(bind=engine)
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Log that tables were created
    logger.info("Test database tables created")
    
    yield
    
    # Clean up after test
    Base.metadata.drop_all(bind=engine)
    logger.info("Test database tables dropped")

def test_signup_and_login():
    # Signup
    resp = client.post("/signup", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "Testpass123!"
    })
    print(f"Response: {resp.status_code}")
    if resp.status_code != 200:
        print(f"Error content: {resp.content}")
    assert resp.status_code == 200
    # Try login before verification
    resp = client.post("/login", data={"username": "testuser", "password": "Testpass123!"})
    assert resp.status_code == 403
    # Simulate verification (direct DB update for test)
    from sqlalchemy.orm import Session
    from backend.app.database import session_maker
    from backend.app.models.user import User
    from sqlalchemy import text
    
    db = session_maker()
    try:
        # Find the user
        user = db.query(User).filter(User.username == "testuser").first()
        logger.debug(f"Found user: {user}")
        
        # Use SQL update instead of ORM to avoid type issues
        db.execute(text("UPDATE users SET is_verified = 1 WHERE username = 'testuser'"))
        db.commit()
        logger.info("User verification status updated")
    except Exception as e:
        logger.error(f"Error updating user verification: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
    # Login after verification
    resp = client.post("/login", data={"username": "testuser", "password": "Testpass123!"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
