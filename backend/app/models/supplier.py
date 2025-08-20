from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_person = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    delivery_lead_time_days = Column(
        Integer, nullable=False, default=7
    )  # Lead time in days
    is_active = Column(Boolean, default=True)
    rating = Column(Float, default=0.0)  # Average rating 0-5
    total_orders = Column(Integer, default=0)
    on_time_deliveries = Column(Integer, default=0)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        onupdate=func.now(),
        server_default=func.now(),
    )

    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
