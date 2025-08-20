import enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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


class PurchaseOrderCreate(PurchaseOrderBase):
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
