from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    
    Created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    Updated_at = Column(DateTime(timezone=True), nullable=False, onupdate=func.now(), server_default=func.now())

