from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    sku: str
    description: str
    price: float
    quantity: int
    min_threshold: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: str
    description: str
    price: float
    quantity: int
    min_threshold: int

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True