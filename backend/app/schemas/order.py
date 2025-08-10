from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import enum

class InvoiceStatus(str, enum.Enum):
    DRAFT = "Draft"
    SENT = "Sent"
    RECEIVED = "Received"
    CLOSED = "Closed"

class PurchaseOrderBase(BaseModel):
    product_id: int
    quantity: int

class PurchaseOrderCreate(PurchaseOrderBase):
    pass

class PurchaseOrderUpdate(PurchaseOrderBase):
    status: InvoiceStatus

class PurchaseOrder(PurchaseOrderBase):
    id: int
    status: InvoiceStatus
    created_at: datetime
    updated_at: datetime
    ordered_by: int

    class Config:
        from_attributes = True