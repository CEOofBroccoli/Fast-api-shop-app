import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_url = os.getenv("DATABASE_URL", "** DB_url could'nt be found **") # gereftan URL database az docker-compose.yml

engine = create_engine(DB_url) #database
session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine) # session factory
Base = declarative_base() #tables

def get_db():  # function baraye ijad session 
    db_session = session_maker()
    try:
        yield db_session
    finally:
        db_session.close()