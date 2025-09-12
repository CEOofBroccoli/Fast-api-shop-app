import enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class InvoiceStatus(str, enum.Enum):
    DRAFT = "Draft"
    SENT = "Sent"
    RECEIVED = "Received"
    CLOSED = "Closed"


class PurchaseOrderBase(BaseModel):
    supplier_id: int
    product_id: int
    quantity: int
    unit_cost: float
    notes: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None  # Allow input during create

    @field_validator("quantity")
    @classmethod
    def positive_quantity(cls, v: int):
        if v <= 0:
            raise ValueError("quantity must be positive")
        return v

    @field_validator("unit_cost")
    @classmethod
    def positive_unit_cost(cls, v: float):
        if v <= 0:
            raise ValueError("unit_cost must be positive")
        return v


class PurchaseOrderCreate(PurchaseOrderBase):
    """Schema for creating a purchase order (expected_delivery_date optional)."""
    pass


class PurchaseOrderUpdate(BaseModel):
    status: Optional[InvoiceStatus] = None
    actual_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None


class PurchaseOrder(PurchaseOrderBase):
    id: int
    total_cost: float
    status: InvoiceStatus
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    ordered_by: int

    class Config:
        from_attributes = True
