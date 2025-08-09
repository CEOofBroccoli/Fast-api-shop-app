from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import and_

from app.database import get_db
from app.models.product import Product
from app.schemas.product import Product as ProductSchema, ProductCreate, ProductBase
from app.auth.jwt_handler import verify_token
from fastapi import Header
from app.models.user import User

router = APIRouter(prefix="/products", tags=["Products"])

# Helper function to get user from token
def get_user_from_token(token: str, db: Session):
    username = verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user

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
    authorization: Optional[str] = Header(None),
    search: Optional[str] = Query(None, description="Search by name or SKU"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    sort_by: Optional[str] = Query(None, description="Sort by: name_asc, name_desc, price_asc, price_desc"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    low_stock: Optional[bool] = Query(None, description="Filter by low stock items"),
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    query = db.query(Product)
    
    # Search by Name or SKU
    if search:
        query = query.filter((Product.name.contains(search)) | (Product.sku == search))
    
    # Filter by Price Range
    if min_price is not None and max_price is not None:
        query = query.filter(Product.price >= min_price, Product.price <= max_price)
    elif min_price is not None:
        query = query.filter(Product.price >= min_price)
    elif max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Sort by
    if sort_by:
        if sort_by == "name_asc":
            query = query.order_by(Product.name.asc())
        elif sort_by == "name_desc":
            query = query.order_by(Product.name.desc())
        elif sort_by == "price_asc":
            query = query.order_by(Product.price.asc())
        elif sort_by == "price_desc":
            query = query.order_by(Product.price.desc())
            
    # Filter by Low Stock
    if low_stock is True:
        query = query.filter(Product.quantity <= Product.min_threshold)
    
    # Pagination
    products = query.offset((page - 1) * limit).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product: ProductBase,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update product attributes
    db_product.name = product.name
    db_product.sku = product.sku
    db_product.price = product.price
    db_product.product_group = product.product_group
    db_product.min_threshold = product.min_threshold
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db.delete(product)
    db.commit()
    return
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import and_

from app.database import get_db
from app.models.product import Product
from app.schemas.product import Product as ProductSchema, ProductCreate, ProductBase
from app.auth.jwt_handler import verify_token
from fastapi import Header
from app.models.user import User

router = APIRouter(prefix="/products", tags=["Products"])

# Helper function to get user from token
def get_user_from_token(token: str, db: Session):
    username = verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user

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
    authorization: Optional[str] = Header(None),
    search: Optional[str] = Query(None, description="Search by name or SKU"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    sort_by: Optional[str] = Query(None, description="Sort by: name_asc, name_desc, price_asc, price_desc"),
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    query = db.query(Product)
    
    # Search by Name or SKU
    if search:
        query = query.filter((Product.name.contains(search)) | (Product.sku == search))
    
    # Filter by Price Range
    if min_price is not None and max_price is not None:
        query = query.filter(Product.price >= min_price, Product.price <= max_price)
    elif min_price is not None:
        query = query.filter(Product.price >= min_price)
    elif max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Sort by
    if sort_by:
        if sort_by == "name_asc":
            query = query.order_by(Product.name.asc())
        elif sort_by == "name_desc":
            query = query.order_by(Product.name.desc())
        elif sort_by == "price_asc":
            query = query.order_by(Product.price.asc())
        elif sort_by == "price_desc":
            query = query.order_by(Product.price.desc())
    
    products = query.all()
    return products

@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product: ProductBase,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update product attributes
    db_product.name = product.name
    db_product.sku = product.sku
    db_product.price = product.price
    db_product.product_group = product.product_group
    db_product.min_threshold = product.min_threshold
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db.delete(product)
    db.commit()
    return