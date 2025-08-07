from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.order import PurchaseOrder
from app.schemas.order import PurchaseOrder, PurchaseOrderCreate, PurchaseOrderUpdate
from app.auth.jwt_handler import verify_token  # Import verify_token
from app.models.user import User  # Import User model
from fastapi import Header

router = APIRouter(prefix="/orders", tags=["Orders"])

# Helper function to get user from token
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

# 1. POST /orders - Create a new order
@router.post("/", response_model=PurchaseOrder, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]  # Assuming "Bearer <token>" format
    user = get_user_from_token(token, db)

    if user.role != "buyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyers can create orders",
        )

    db_order = PurchaseOrder(**order.model_dump(), ordered_by=user.id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


# 2. GET /orders - List all orders (with pagination and filter by status)
@router.get("/", response_model=List[PurchaseOrder])
async def list_orders(
    page: int = 1,
    limit: int = 10,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]  # Assuming "Bearer <token>" format
    get_user_from_token(token, db)  # Just to authenticate

    query = db.query(PurchaseOrder)
    if status_filter:
        query = query.filter(PurchaseOrder.status == status_filter)

    orders = query.offset((page - 1) * limit).limit(limit).all()
    return orders


# 3. PUT /orders/{id} - Update order
@router.put("/{id}", response_model=PurchaseOrder)
async def update_order(
    id: int,
    order: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]  # Assuming "Bearer <token>" format
    get_user_from_token(token, db)  # Just to authenticate

    db_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    # Status flow validation
    allowed_transitions = {
        "Draft": ["Sent"],
        "Sent": ["Received"],
        "Received": ["Closed"],
        "Closed": [],
    }
    if order.status not in allowed_transitions.get(db_order.status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {db_order.status} to {order.status}",
        )

    for key, value in order.model_dump(exclude_unset=True).items():
        setattr(db_order, key, value)

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Business logic for "Received" status
    if db_order.status == "Received":
        # Increase stock (assuming you have an inventory table)
        # This part needs to be adapted based on your actual inventory model
        # Example:
        # inventory_item = db.query(Inventory).filter(Inventory.product_id == db_order.product_id).first()
        # if inventory_item:
        #     inventory_item.quantity += db_order.quantity
        #     db.add(inventory_item)
        #     db.commit()
        #     db.refresh(inventory_item)
        pass  # Replace with your actual inventory update logic

    return db_order


# 4. DELETE /orders/{id} - Delete order (only allowed if status is "Draft")
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
    token = authorization.split(" ")[1]  # Assuming "Bearer <token>" format
    get_user_from_token(token, db)  # Just to authenticate

    db_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    if db_order.status != "Draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only orders with 'Draft' status can be deleted",
        )

    db.delete(db_order)
    db.commit()
    return