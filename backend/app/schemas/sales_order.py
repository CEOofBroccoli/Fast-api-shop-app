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
    unit_price: float
    total: float
    sales_order_id: int

    class Config:
        from_attributes = True


class SalesOrderBase(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    notes: Optional[str] = None


class SalesOrderCreate(SalesOrderBase):
    items: List[SalesOrderItemCreate]


class SalesOrderUpdate(BaseModel):
    status: Optional[SalesOrderStatus] = None
    shipped_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    notes: Optional[str] = None


class SalesOrder(SalesOrderBase):
    id: int
    total_amount: float
    status: SalesOrderStatus
    order_date: datetime = datetime.now()
    shipped_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    items: List[SalesOrderItem] = []

    class Config:
        from_attributes = True


class SalesOrderWithItems(SalesOrder):
    items: List[SalesOrderItem] = []
