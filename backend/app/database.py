import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./inventory_app.db") # gereftan URL database
JWT_SECRET = os.getenv("JWT_SECRET_KEY")

engine = create_engine(DB_URL) #database
session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine) # session factory
Base = declarative_base() #tables

def get_db():  # function baraye ijad session 
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