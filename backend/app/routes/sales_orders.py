from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session
from logging import getLogger

from typing import Tuple
from fastapi import Request
from backend.app.auth.jwt_handler import decode_token
from backend.app.database import get_db
from backend.app.main import get_authenticated_user_header
from backend.app.models.product import Product
from backend.app.models.sales_order import SalesOrder, SalesOrderItem, SalesOrderStatus
from backend.app.models.user import User
from backend.app.schemas.sales_order import SalesOrderCreate, SalesOrderUpdate, SalesOrderWithItems

router = APIRouter(prefix="/sales-orders", tags=["Sales Orders"])
logger = getLogger(__name__)


def authorize_user_from_header(authorization: Optional[str], db: Session) -> User:
    """Authorize a user from an Authorization header value (Bearer token).

    This helper is explicit and returns clear 401/404 messages instead of relying on OAuth2
    dependency injection which can produce generic "Not authenticated" errors.
    """
    if not authorization or not isinstance(authorization, str) or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header. Use: Authorization: Bearer <token>",
        )
    try:
        token = authorization.split(" ", 1)[1].strip()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Use: Authorization: Bearer <token>",
        )

    payload = decode_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def get_current_user_from_header(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    """FastAPI dependency to get current user from the Authorization header."""
    return authorize_user_from_header(authorization, db)


def validate_stock_availability(db: Session, product_id: int, quantity: int):
    """Validate that sufficient stock is available for the order."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )

    current_quantity = getattr(product, "quantity", 0)
    if current_quantity < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {current_quantity}, Requested: {quantity}",
        )

    return product


@router.post("/", response_model=SalesOrderWithItems, status_code=status.HTTP_201_CREATED)
async def create_sales_order(
    request: Request,
    order: SalesOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user_header)
):
    """Create a new sales order with stock validation."""
    logger.debug("Received request to create sales order")
    logger.debug(f"Current user: {current_user.username}, Role: {current_user.role}")

    # Verify user has permission to create orders
    if current_user.role not in ["admin", "manager", "staff", "customer"]:
        logger.warning(f"User {current_user.username} does not have permission to create sales orders")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create sales orders"
        )

    # Create sales order with customer details
    try:
        logger.debug("Creating sales order in database")
        db_order = SalesOrder(
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            customer_phone=order.customer_phone,
            status=SalesOrderStatus.CONFIRMED,  # Auto-confirm for now
            total_amount=0  # Will be updated with items total
        )
        db.add(db_order)
        db.flush()  # Get order ID without committing

        total_amount = 0

        # Handle all items in the order
        for item in order.items:
            # Validate stock availability
            product = validate_stock_availability(db, item.product_id, item.quantity)
            
            # Calculate item total
            item_total = item.quantity * product.price
            total_amount += item_total

            # Create order item
            order_item = SalesOrderItem(
                sales_order_id=db_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=product.price,
                total=item_total
            )
            db.add(order_item)

            # Decrease inventory
            current_quantity = getattr(product, "quantity", 0)
            setattr(product, "quantity", current_quantity - item.quantity)

        # Update order total
        setattr(db_order, "total_amount", total_amount)
        
        db.commit()
        db.refresh(db_order)
        return db_order

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sales order: {str(e)}"
        )


@router.get("/", response_model=List[SalesOrderWithItems])
async def list_sales_orders(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user_header),
    customer_email: Optional[str] = Query(None, description="Filter by customer email"),
    customer_name: Optional[str] = Query(None, description="Filter by customer name"),
    status_filter: Optional[SalesOrderStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
):
    """List sales orders with filtering and pagination."""
    # Verify user has permission to list orders
    if current_user.role not in ["admin", "manager", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to list sales orders"
        )
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Missing authorization header",
    #     )

    # Authentication provided via Depends(get_user_from_token)

    query = db.query(SalesOrder)

    # Filter by customer details if provided
    if customer_email:
        query = query.filter(SalesOrder.customer_email == customer_email)
    if customer_name:
        query = query.filter(SalesOrder.customer_name.ilike(f"%{customer_name}%"))

    if status_filter:
        query = query.filter(SalesOrder.status == status_filter)

    orders = query.offset((page - 1) * limit).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=SalesOrderWithItems)
async def get_sales_order(
    request: Request,
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user_header)
):
    """Get sales order details by ID."""
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")

    # Check permissions - customers can only see their own orders
    if str(getattr(current_user, "role", "")) == "customer":
        if str(order.customer_email) != str(getattr(current_user, "email", "")):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return order


@router.put("/{order_id}", response_model=SalesOrderWithItems)
async def update_sales_order(
    request: Request,
    order_id: int,
    order_update: SalesOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user_header)
):
    """Update sales order status and details."""
    # Only staff and above can update orders
    if str(getattr(current_user, "role", "")) not in ["admin", "manager", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update orders",
        )

    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")

    # Update fields
    update_data = order_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)

    # Auto-set dates based on status changes
    if order_update.status == SalesOrderStatus.SHIPPED:
        shipped_date = getattr(order, "shipped_date", None)
        if not shipped_date:
            setattr(order, "shipped_date", datetime.now())
    elif order_update.status == SalesOrderStatus.DELIVERED:
        delivered_date = getattr(order, "delivered_date", None)
        if not delivered_date:
            setattr(order, "delivered_date", datetime.now())

    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_sales_order(
    request: Request,
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user_header),
):
    """
    Cancel a sales order and restore inventory.

    Only pending or confirmed orders can be cancelled.
    """
    # Only staff and above can cancel orders
    if str(getattr(current_user, "role", "")) not in ["admin", "manager", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to cancel orders",
        )

    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")

    # Check if order can be cancelled
    if order.status in [SalesOrderStatus.SHIPPED, SalesOrderStatus.DELIVERED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel shipped or delivered orders",
        )

    # Restore inventory if order was confirmed
    order_status = getattr(order, "status", None)
    if order_status == SalesOrderStatus.CONFIRMED:
        product_id = getattr(order, "product_id", 0)
        order_quantity = getattr(order, "quantity", 0)
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            current_quantity = getattr(product, "quantity", 0)
            setattr(product, "quantity", current_quantity + order_quantity)

    # Mark as cancelled
    setattr(order, "status", SalesOrderStatus.CANCELLED)
    db.commit()
    return
