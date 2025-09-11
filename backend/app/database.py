# Database configuration and connection management
import logging
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check if running in test mode
TESTING = "pytest" in sys.modules

# Database URL selection - SQLite for testing, PostgreSQL for production
if TESTING:
    DB_URL = "sqlite:///./test.db"
    logger.info("Running in test mode with SQLite database")
else:
    # Use data directory for SQLite in Docker, fallback to current directory
    data_dir = "/app/data" if os.path.exists("/app/data") else "."
    default_db_path = f"sqlite:///{data_dir}/inventory_app.db"
    DB_URL = os.getenv("DATABASE_URL", default_db_path)
    logger.info(f"Using database URL: {DB_URL}")

# JWT secret key for token generation
JWT_SECRET = os.getenv("JWT_SECRET_KEY")

# Database engine and session configuration
engine = create_engine(DB_URL)
session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()  # Base class for database models


def get_db():
    """Database session dependency for FastAPI endpoints"""
    db_session = session_maker()
    try:
        yield db_session
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {str(e)[:500]}")
        db_session.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected database error: {str(e)[:500]}")
        db_session.rollback()
        raise
    finally:
        db_session.close()
