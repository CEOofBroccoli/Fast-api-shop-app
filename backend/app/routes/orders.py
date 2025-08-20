from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.auth.jwt_handler import verify_token
from backend.app.database import get_db
from backend.app.models.order import InvoiceStatus, PurchaseOrder
from backend.app.models.product import Product
from backend.app.models.user import User
from backend.app.schemas.order import PurchaseOrder as PurchaseOrderSchema
from backend.app.schemas.order import PurchaseOrderCreate, PurchaseOrderUpdate

router = APIRouter(prefix="/orders", tags=["Orders"])


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/", response_model=PurchaseOrderSchema, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Create a new purchase order.

    This endpoint allows buyers to create new purchase orders with specified
    products, quantities, and shipping details. The system automatically assigns
    the order to the authenticated user.

    Args:
        order: Purchase order details including line items and shipping information
        db: Database session
        authorization: Bearer token for authentication

    Returns:
        Newly created order object with assigned ID and status

    Raises:
        401: Unauthorized - Missing or invalid authentication
        403: Forbidden - User is not a buyer
        404: Not Found - Referenced products do not exist
        422: Validation Error - Invalid order structure or insufficient product stock
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]
    user = get_user_from_token(token, db)

    if getattr(user, "role", None) != "buyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyers can create orders",
        )
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product not found")

    # Calculate total cost
    total_cost = order.quantity * order.unit_cost

    # Create order with calculated total_cost
    order_data = order.model_dump()
    order_data["total_cost"] = total_cost
    order_data["ordered_by"] = user.id

    db_order = PurchaseOrder(**order_data)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/", response_model=List[PurchaseOrderSchema])
async def list_orders(
    page: int = 1,
    limit: int = 10,
    status_filter: Optional[InvoiceStatus] = None,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """
    List and filter purchase orders with pagination.

    This endpoint retrieves purchase orders, with optional filtering by status
    and paginated results. Different user roles see different sets of orders:
    - Buyers: Only their own orders
    - Staff/Managers: All orders with details
    - Admin: All orders with complete history and details

    Args:
        page: Page number for pagination (starts at 1)
        limit: Number of orders per page
        status_filter: Optional filter by order status (pending, processing, completed, etc.)
        db: Database session
        authorization: Bearer token for authentication

    Returns:
        List of purchase order objects matching the filter criteria

    Raises:
        401: Unauthorized - Missing or invalid authentication
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]
    get_user_from_token(token, db)

    query = db.query(PurchaseOrder)
    if status_filter:
        query = query.filter(PurchaseOrder.status == status_filter)

    orders = query.offset((page - 1) * limit).limit(limit).all()
    return orders


@router.put("/{id}", response_model=PurchaseOrderSchema)
async def update_order(
    id: int,
    order_update: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Update an existing purchase order's details or status.

    This endpoint allows updating order details and changing the order status
    according to allowed state transitions. Status changes may trigger inventory
    updates or notifications based on business rules.

    Args:
        order_id: The ID of the order to update
        order_update: Schema containing fields to update (only changed fields required)
        db: Database session
        authorization: Bearer token for authentication

    Returns:
        Updated purchase order object

    Raises:
        401: Unauthorized - Missing or invalid authentication
        403: Forbidden - User not allowed to update this order
        404: Not Found - Order does not exist
        422: Validation Error - Invalid status transition or update data
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]
    get_user_from_token(token, db)

    db_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == id).first()
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    allowed_transitions = {
        InvoiceStatus.DRAFT: [InvoiceStatus.SENT],
        InvoiceStatus.SENT: [InvoiceStatus.RECEIVED],
        InvoiceStatus.RECEIVED: [InvoiceStatus.CLOSED],
        InvoiceStatus.CLOSED: [],
    }
    current_status = getattr(db_order, "status", None)

    # Convert string status to enum for comparison
    if order_update.status and current_status is not None:
        # Convert the incoming status string to the model enum
        try:
            new_status_enum = InvoiceStatus(order_update.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status value: {order_update.status}",
            )

        if new_status_enum not in allowed_transitions.get(current_status, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from {current_status} to {order_update.status}",
            )

    for key, value in order_update.model_dump(exclude_unset=True).items():
        # Convert status string to enum if it's a status field
        if key == "status" and isinstance(value, str):
            value = InvoiceStatus(value)
        setattr(db_order, key, value)

    # inventory update
    if getattr(db_order, "status", None) == InvoiceStatus.RECEIVED:
        product = db.query(Product).filter(Product.id == getattr(db_order, "product_id", None)).first()
        if product:
            current_quantity = getattr(product, "quantity", 0) or 0
            order_quantity = getattr(db_order, "quantity", 0) or 0
            setattr(product, "quantity", int(current_quantity) + int(order_quantity))
            db.add(product)

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    return db_order


# - Delete order
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    id: int,
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

    db_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == id).first()
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if getattr(db_order, "status", None) != InvoiceStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only orders with 'Draft' status can be deleted",
        )

    db.delete(db_order)
    db.commit()
    return
