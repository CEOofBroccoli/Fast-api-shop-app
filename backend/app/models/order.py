from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class InvoiceStatus(enum.Enum):
    DRAFT = "Draft"
    SENT = "Sent"
    RECEIVED = "Received"
    CLOSED = "Closed"

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)  # Using Enum
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    ordered_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    product = relationship("Product", back_populates="orders")
    user = relationship("User", back_populates="orders")