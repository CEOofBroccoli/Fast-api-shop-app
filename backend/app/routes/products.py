from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.product import Product
from app.schemas.product import Product as ProductSchema, ProductCreate
from app.auth.jwt_handler import verify_token
from fastapi import Header
from app.models.user import User

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductSchema)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    # Check if SKU already exists
    existing_product = db.query(Product).filter(Product.sku == product.sku).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists"
        )

    db_product = Product(
        name=product.name,
        sku=product.sku,
        price=product.price,
        product_group=product.product_group,
        min_threshold=product.min_threshold
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/", response_model=List[ProductSchema])
async def list_products(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    products = db.query(Product).all()
    return products