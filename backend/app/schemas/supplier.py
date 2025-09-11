from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class SupplierBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    delivery_lead_time_days: int = 7


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    delivery_lead_time_days: Optional[int] = None
    is_active: Optional[bool] = None


class Supplier(SupplierBase):
    id: int
    is_active: bool
    rating: float
    total_orders: int
    on_time_deliveries: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SupplierSummary(BaseModel):
    id: int
    name: str
    rating: float
    total_orders: int
    on_time_deliveries: int
    delivery_lead_time_days: int
    is_active: bool

    class Config:
        from_attributes = True
