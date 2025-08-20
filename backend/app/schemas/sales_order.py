import enum
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class SalesOrderStatus(str, enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class SalesOrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class SalesOrderItemCreate(SalesOrderItemBase):
    pass


class SalesOrderItem(SalesOrderItemBase):
    id: int
    total_price: float

    class Config:
        from_attributes = True


class SalesOrderBase(BaseModel):
    customer_id: int
    product_id: int
    quantity: int
    unit_price: float
    notes: Optional[str] = None


class SalesOrderCreate(BaseModel):
    customer_id: int
    items: List[SalesOrderItemCreate]
    notes: Optional[str] = None


class SalesOrderUpdate(BaseModel):
    status: Optional[SalesOrderStatus] = None
    shipped_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    notes: Optional[str] = None


class SalesOrder(SalesOrderBase):
    id: int
    total_amount: float
    status: SalesOrderStatus
    order_date: datetime
    shipped_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SalesOrderWithItems(BaseModel):
    id: int
    customer_id: int
    product_id: int
    quantity: int
    unit_price: float
    total_amount: float
    status: SalesOrderStatus
    order_date: datetime
    shipped_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    order_items: List[SalesOrderItem] = []

    class Config:
        from_attributes = True
