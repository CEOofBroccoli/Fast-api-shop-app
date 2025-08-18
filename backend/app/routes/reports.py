from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List
from backend.app.database import get_db
from backend.app.models.order import PurchaseOrder
from backend.app.models.product import Product  
from sqlalchemy import func
from backend.app.auth.jwt_handler import verify_token
from fastapi import Header
from typing import Optional
from backend.app.models.user import User
import re

router = APIRouter(prefix="/report", tags=["Reports"])

# geting user from token
def get_user_from_token(token: str, db: Session):
    username = verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Input validation to prevent injection
    if not isinstance(username, str) or len(username) > 50:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username format"
        )
    # Sanitize username
    if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username format"
        )
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user

# 1. GET /report/low-stock
@router.get("/low-stock")
async def get_low_stock_items(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]  
    get_user_from_token(token, db) 

    low_stock_items = (
        db.query(Product)
        .filter(Product.quantity <= Product.min_threshold)
        .all()
    )
    return low_stock_items


# 2. GET /report/order-status
@router.get("/order-status")
async def get_order_status_counts(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]  
    get_user_from_token(token, db) 

    order_status_counts = (
        db.query(PurchaseOrder.status, func.count(PurchaseOrder.status))
        .group_by(PurchaseOrder.status)
        .all()
    )
    return dict(order_status_counts)


# 3. GET /report/inventory-value
@router.get("/inventory-value")
async def get_total_inventory_value(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]  
    get_user_from_token(token, db) 


    total_inventory_value = (
        db.query(func.sum(Product.quantity * Product.price)).scalar()
    )
    return {"total_inventory_value": total_inventory_value or 0}


#  GET /report/order-history/{product_id}
@router.get("/order-history/{product_id}")
async def get_order_history_for_product(
    product_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]  
    get_user_from_token(token, db)  

    # Input validation for product_id
    if not isinstance(product_id, int) or product_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID"
        )

    order_history = (
        db.query(PurchaseOrder)
        .filter(PurchaseOrder.product_id == product_id)
        .order_by(PurchaseOrder.created_at)
        .all()
    )
    return order_history