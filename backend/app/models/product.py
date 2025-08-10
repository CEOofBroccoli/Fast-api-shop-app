from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sku = Column(String, unique=True, index=True, nullable=False)
    price = Column(Float, nullable=False)
    product_group = Column(String, nullable=False)
    min_threshold = Column(Integer, nullable=False, default=5)

    orders = relationship("PurchaseOrder", back_populates="product")