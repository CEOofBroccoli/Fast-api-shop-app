from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.order import PurchaseOrder
from app.schemas.order import PurchaseOrder, PurchaseOrderCreate, PurchaseOrderUpdate
from app.auth.jwt_handler import verify_token
from app.models.user import User 
from fastapi import Header
from app.models.prodcut import Product

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user

#  create a new order
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
    token = authorization.split(" ")[1] 
    user = get_user_from_token(token, db)

    if user.role != "buyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyers can create orders",
        )
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Product not found"
        )

    db_order = PurchaseOrder(**order.model_dump(), ordered_by=user.id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


# List all orders
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
    token = authorization.split(" ")[1]  
    get_user_from_token(token, db) 

    query = db.query(PurchaseOrder)
    if status_filter:
        query = query.filter(PurchaseOrder.status == status_filter)

    orders = query.offset((page - 1) * limit).limit(limit).all()
    return orders


# Updateing orders
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
    token = authorization.split(" ")[1]  
    get_user_from_token(token, db)

    db_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

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

    if db_order.status == "Received":
        # Increase stock
        inventory_item = db.query(Product).filter(Product.id == db_order.product_id).first()
        if inventory_item:
            inventory_item.quantity += db_order.quantity
            db.add(inventory_item)
            db.commit()
            db.refresh(inventory_item)

    return db_order


#- Delete order 
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