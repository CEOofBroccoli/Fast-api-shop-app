from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PurchaseOrderBase(BaseModel):
    product_id: int
    quantity: int

class PurchaseOrderCreate(PurchaseOrderBase):
    pass

class PurchaseOrderUpdate(PurchaseOrderBase):
    status: str

class PurchaseOrder(PurchaseOrderBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    ordered_by: int

    class Config:
        from_attributes = True