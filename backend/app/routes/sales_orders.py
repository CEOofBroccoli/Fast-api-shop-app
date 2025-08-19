from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models.sales_order import SalesOrder, SalesOrderStatus, SalesOrderItem
from backend.app.models.product import Product
from backend.app.models.user import User
from backend.app.schemas.sales_order import (
    SalesOrder as SalesOrderSchema,
    SalesOrderCreate,
    SalesOrderUpdate,
    SalesOrderWithItems
)
from backend.app.auth.jwt_handler import verify_token
from datetime import datetime

router = APIRouter(prefix="/sales-orders", tags=["Sales Orders"])


def get_user_from_token(token: str, db: Session):
    username = verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def validate_stock_availability(db: Session, product_id: int, quantity: int):
    """Validate that sufficient stock is available for the order."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    current_quantity = getattr(product, 'quantity', 0)
    if current_quantity < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {current_quantity}, Requested: {quantity}"
        )
    
    return product


@router.post("/", response_model=SalesOrderSchema, status_code=status.HTTP_201_CREATED)
async def create_sales_order(
    order: SalesOrderCreate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Create a new sales order with stock validation.
    
    This endpoint validates stock availability and automatically decreases
    inventory when the order is confirmed.
    
    Args:
        order: Sales order details with customer and items
        db: Database session
        authorization: Bearer token for authentication
        
    Returns:
        Newly created sales order
        
    Raises:
        400: Bad Request - Insufficient stock
        401: Unauthorized - Missing or invalid authentication
        404: Not Found - Product or customer not found
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    token = authorization.split(" ")[1]
    user = get_user_from_token(token, db)
    
    # Check if user can create sales orders (staff, manager, admin)
    if user.role not in ["admin", "manager", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create sales orders"
        )
    
    # Validate customer exists
    customer = db.query(User).filter(User.id == order.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    total_amount = 0
    
    # For simplified version, we'll handle single item orders
    # In a full implementation, you'd handle multiple items
    if order.items:
        item = order.items[0]  # Take first item for now
        
        # Validate stock availability
        product = validate_stock_availability(db, item.product_id, item.quantity)
        
        total_amount = item.quantity * item.unit_price
        
        # Create sales order
        db_order = SalesOrder(
            customer_id=order.customer_id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_amount=total_amount,
            notes=order.notes,
            status=SalesOrderStatus.CONFIRMED  # Auto-confirm for now
        )
        
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        # Automatically decrease inventory when order is confirmed
        current_quantity = getattr(product, 'quantity', 0)
        setattr(product, 'quantity', current_quantity - item.quantity)
        db.commit()
        
        return db_order
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Order must contain at least one item"
    )


@router.get("/", response_model=List[SalesOrderSchema])
async def list_sales_orders(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    status_filter: Optional[SalesOrderStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
):
    """List sales orders with filtering and pagination."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    token = authorization.split(" ")[1]
    user = get_user_from_token(token, db)
    
    query = db.query(SalesOrder)
    
    # If customer role, only show their own orders
    user_role = getattr(user, 'role', '')
    if user_role == "customer":
        user_id = getattr(user, 'id', 0)
        query = query.filter(SalesOrder.customer_id == user_id)
    elif customer_id:
        query = query.filter(SalesOrder.customer_id == customer_id)
    
    if status_filter:
        query = query.filter(SalesOrder.status == status_filter)
    
    orders = query.offset((page - 1) * limit).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=SalesOrderSchema)
async def get_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """Get sales order details by ID."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    token = authorization.split(" ")[1]
    user = get_user_from_token(token, db)
    
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales order not found"
        )
    
    # Check permissions - customers can only see their own orders
    user_role = getattr(user, 'role', '')
    user_id = getattr(user, 'id', 0)
    order_customer_id = getattr(order, 'customer_id', 0)
    if user_role == "customer" and order_customer_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return order


@router.put("/{order_id}", response_model=SalesOrderSchema)
async def update_sales_order(
    order_id: int,
    order_update: SalesOrderUpdate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """Update sales order status and details."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    token = authorization.split(" ")[1]
    user = get_user_from_token(token, db)
    
    # Only staff and above can update orders
    if user.role not in ["admin", "manager", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update orders"
        )
    
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales order not found"
        )
    
    # Update fields
    update_data = order_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    # Auto-set dates based on status changes
    if order_update.status == SalesOrderStatus.SHIPPED:
        shipped_date = getattr(order, 'shipped_date', None)
        if not shipped_date:
            setattr(order, 'shipped_date', datetime.now())
    elif order_update.status == SalesOrderStatus.DELIVERED:
        delivered_date = getattr(order, 'delivered_date', None)
        if not delivered_date:
            setattr(order, 'delivered_date', datetime.now())
    
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Cancel a sales order and restore inventory.
    
    Only pending or confirmed orders can be cancelled.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    token = authorization.split(" ")[1]
    user = get_user_from_token(token, db)
    
    # Only staff and above can cancel orders
    if user.role not in ["admin", "manager", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to cancel orders"
        )
    
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales order not found"
        )
    
    # Check if order can be cancelled
    if order.status in [SalesOrderStatus.SHIPPED, SalesOrderStatus.DELIVERED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel shipped or delivered orders"
        )
    
    # Restore inventory if order was confirmed
    order_status = getattr(order, 'status', None)
    if order_status == SalesOrderStatus.CONFIRMED:
        product_id = getattr(order, 'product_id', 0)
        order_quantity = getattr(order, 'quantity', 0)
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            current_quantity = getattr(product, 'quantity', 0)
            setattr(product, 'quantity', current_quantity + order_quantity)
    
    # Mark as cancelled
    setattr(order, 'status', SalesOrderStatus.CANCELLED)
    db.commit()
    return
