from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)  # Assuming you have a products table
    quantity = Column(Integer, nullable=False)
    status = Column(String, default="Draft")  # Draft, Sent, Received, Closed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    ordered_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    product = relationship("Product", back_populates="orders")  # Assuming you have a Product model
    user = relationship("User", back_populates="orders")