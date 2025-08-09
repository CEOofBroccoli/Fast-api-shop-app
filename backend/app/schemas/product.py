from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str = Field(..., description="Product name")
    sku: str = Field(..., description="Stock Keeping Unit")
    price: float = Field(..., gt=0, description="Product price")
    product_group: str = Field(..., description="Product group/category")
    min_threshold: int = Field(default=5, ge=0, description="Minimum stock threshold")

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True