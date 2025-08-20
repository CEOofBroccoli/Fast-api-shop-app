# Product management API routes
from fastapi import APIRouter, Depends, HTTPException, status, Query, Header, Request
from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import and_
from backend.app.database import get_db
from backend.app.models.product import Product, StockChangeLog
from backend.app.schemas.product import (
    Product as ProductSchema,
    ProductCreate,
    ProductBase,
)
from backend.app.auth.jwt_handler import verify_token
from backend.app.models.user import User
from pydantic import BaseModel
from backend.app.utils.redis_cache import cached_async, cache

router = APIRouter(prefix="/products", tags=["Products"])


def get_user_from_token(token: str, db: Session):
    """Helper function to get user from JWT token"""
    username = verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


class StockAdjustment(BaseModel):
    change: int
    reason: str


@router.get("/{product_id}/stock-history")
async def get_stock_history(
    product_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Retrieve the stock change history for a specific product.

    This endpoint returns a chronological record of all stock adjustments made to a product,
    including the amount changed, reason for change, who made the change, and when.

    Args:
        product_id: The ID of the product to retrieve stock history for
        db: Database session
        authorization: Bearer token for authentication

    Returns:
        List of stock change log entries ordered by timestamp (most recent first)

    Raises:
        401: Unauthorized - Missing or invalid authentication
        403: Forbidden - User lacks required permissions (admin/manager only)
        404: Not Found - Product does not exist
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    token = authorization.split(" ")[1]
    user = get_user_from_token(token, db)
    # Only admin or manager can view stock history
    if user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )
    logs = (
        db.query(StockChangeLog)
        .filter(StockChangeLog.product_id == product_id)
        .order_by(StockChangeLog.timestamp.desc())
        .all()
    )
    return [
        {
            "change": log.change,
            "reason": log.reason,
            "changed_by": log.changed_by,
            "timestamp": log.timestamp,
        }
        for log in logs
    ]


@router.post("/", response_model=ProductSchema)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Create a new product in the inventory system.

    This endpoint allows authorized users to create new products with a unique SKU.
    Products must have a name, SKU, price, and optional grouping and minimum stock threshold.
    It also invalidates the products list cache to ensure data consistency.

    Args:
        product: ProductCreate schema object with product details
        db: Database session
        authorization: Bearer token for authentication

    Returns:
        Newly created product object with assigned ID

    Raises:
        400: Bad Request - SKU already exists
        401: Unauthorized - Missing or invalid authentication
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    # Check if SKU already exists
    existing_product = db.query(Product).filter(Product.sku == product.sku).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="SKU already exists"
        )
    db_product = Product(
        name=product.name,
        sku=product.sku,
        price=product.price,
        quantity=product.quantity,
        product_group=product.product_group,
        min_threshold=product.min_threshold,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Invalidate the products list cache when a new product is added
    cache.delete("products:list:*")

    return db_product


@router.get("/", response_model=List[ProductSchema])
@cached_async(expire=300, prefix="products:list")  # Cache for 5 minutes
async def list_products(
    request: Request,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
    search: Optional[str] = Query(None, description="Search by name or SKU"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    sort_by: Optional[str] = Query(
        None, description="Sort by: name_asc, name_desc, price_asc, price_desc"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    low_stock: Optional[bool] = Query(None, description="Filter by low stock items"),
):
    """
    List and filter products in the inventory system.

    This endpoint supports comprehensive filtering, searching, sorting and pagination
    options to efficiently retrieve product data based on various criteria.
    Results are cached for 5 minutes to improve performance.

    Args:
        request: FastAPI request object
        db: Database session
        authorization: Bearer token for authentication
        search: Optional text to search in product names or exact SKU match
        min_price: Optional minimum price filter
        max_price: Optional maximum price filter
        sort_by: Optional sorting parameter (name_asc, name_desc, price_asc, price_desc)
        page: Page number for pagination (starts at 1)
        limit: Number of items per page (1-100)
        low_stock: When true, only returns products with quantity below their minimum threshold

    Returns:
        Paginated list of product objects matching the filter criteria

    Raises:
        401: Unauthorized - Missing or invalid authentication
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
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
@cached_async(expire=300, prefix="products:detail")  # Cache for 5 minutes
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Get a specific product by ID.

    This endpoint returns detailed information about a specific product.
    Results are cached for 5 minutes to improve performance.

    Args:
        product_id: The ID of the product to retrieve
        db: Database session
        authorization: Bearer token for authentication

    Returns:
        Product object with all details

    Raises:
        401: Unauthorized - Missing or invalid authentication
        404: Not Found - Product does not exist
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product: ProductBase,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Update an existing product.

    This endpoint allows updating all fields of a product. It also invalidates
    any cache entries for this product to ensure data consistency.

    Args:
        product_id: The ID of the product to update
        product: ProductBase schema object with updated product details
        db: Database session
        authorization: Bearer token for authentication

    Returns:
        Updated product object

    Raises:
        400: Bad Request - SKU already exists
        401: Unauthorized - Missing or invalid authentication
        404: Not Found - Product does not exist
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    # Ensure SKU uniqueness on update
    if product.sku != getattr(db_product, "sku", None):
        if db.query(Product).filter(Product.sku == product.sku).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="SKU already exists"
            )
    # Update fields using setattr for proper SQLAlchemy attribute assignment
    for field, value in product.dict().items():
        if hasattr(db_product, field):
            setattr(db_product, field, value)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Invalidate cache for this product and the products list
    cache.delete(f"products:detail:{product_id}")
    cache.delete("products:list:*")

    return db_product


@router.post("/{product_id}/adjust-stock", response_model=ProductSchema)
async def adjust_stock(
    product_id: int,
    adjustment: StockAdjustment,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Adjust the stock quantity for a specific product.

    This endpoint allows authorized users to increase or decrease the stock level
    of a product and records the change in the audit log with the provided reason.

    Args:
        product_id: The ID of the product to adjust stock for
        adjustment: StockAdjustment object containing:
            - change (int): Positive or negative number indicating quantity change
            - reason (str): Explanation for the stock adjustment
        db: Database session
        authorization: Bearer token for authentication

    Returns:
        Updated product object with new quantity

    Raises:
        400: Bad Request - Invalid adjustment or would result in negative stock
        401: Unauthorized - Missing or invalid authentication
        404: Not Found - Product does not exist
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    token = authorization.split(" ")[1]
    user = get_user_from_token(token, db)
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    current_quantity = getattr(db_product, "quantity", 0) or 0
    new_quantity = int(current_quantity) + int(adjustment.change)

    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Stock cannot go below zero"
        )

    setattr(db_product, "quantity", new_quantity)
    db.add(db_product)

    # Log the stock change
    log = StockChangeLog(
        product_id=product_id,
        change=adjustment.change,
        reason=adjustment.reason,
        changed_by=user.id,
    )
    db.add(log)
    db.commit()
    db.refresh(db_product)

    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Delete a product from the inventory.

    This endpoint permanently removes a product from the system.
    Only managers and admins can delete products.

    Args:
        product_id: The ID of the product to delete
        db: Database session
        authorization: Bearer token for authentication

    Returns:
        204 No Content on successful deletion

    Raises:
        401: Unauthorized - Missing or invalid authentication
        403: Forbidden - User lacks required permissions (admin/manager only)
        404: Not Found - Product does not exist
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    token = authorization.split(" ")[1]
    user = get_user_from_token(token, db)

    # Only admin or manager can delete products
    if user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    # Check if product exists
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # Delete related stock change logs first
    db.query(StockChangeLog).filter(StockChangeLog.product_id == product_id).delete()

    # Delete the product
    db.delete(db_product)
    db.commit()

    # Clear cache for product list and specific product
    cache.delete("products:list:*")
    cache.delete(f"products:detail:{product_id}")

    return  # 204 No Content
