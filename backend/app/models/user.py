# User model for authentication and user management
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base
from sqlalchemy.sql import func


class User(Base):
    """User model for storing user account information"""

    __tablename__ = "users"

    # Primary key and identifiers
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    # Authentication and profile
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="user")  # user, staff, manager, admin
    is_verified = Column(Boolean, default=False)  # Email verification status

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        onupdate=func.now(),
        server_default=func.now(),
    )
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    orders = relationship("PurchaseOrder", back_populates="user")
