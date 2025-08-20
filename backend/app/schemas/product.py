from pydantic import BaseModel, Field
from typing import Optional


class ProductBase(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None
    price: float
    quantity: int
    min_threshold: int
    product_group: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True
