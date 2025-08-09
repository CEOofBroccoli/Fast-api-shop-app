from sqlalchemy import Column, Integer, String, Float, DateTime, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0, nullable=False)
    
    sku = Column(String, unique=True, index=True, nullable=False)
    min_stock_level = Column(Integer, default=1, nullable=False)
    category = Column(String, nullable=False, index=True)
    image_url = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    orders = relationship("PurchaseOrder", back_populates="product")