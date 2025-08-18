from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str
    sku: str
    description: str
    price: float
    quantity: int
    min_threshold: int
    product_group: str | None = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True