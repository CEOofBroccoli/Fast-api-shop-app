from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.order import PurchaseOrder as PurchaseOrderModel
from app.schemas.order import PurchaseOrder, PurchaseOrderCreate, PurchaseOrderUpdate
from app.auth.jwt_handler import verify_token
from app.models.user import User
import logging
from app.exceptions import AuthenticationError, AuthorizationError,  ResourceNotFoundError, ValidationError, BusinessLogicError, OrderStatusError
from app.utils import validate_token_header, get_authenticated_user, validate_role_access, validate_order_status_transition

router = APIRouter(prefix="/orders", tags=["Orders"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=PurchaseOrder, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    try:
        token = validate_token_header(authorization)
        user = get_authenticated_user(token, db)
        
        # Check role access (as per Persian doc requirements)
        validate_role_access(user, 'employee')  # Only employees and above can create orders
        
        db_order = PurchaseOrderModel(**order.model_dump(), ordered_by=user.id) #validate order data
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
        
    except (AuthenticationError, AuthorizationError, ValidationError, BusinessLogicError):
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create order: {str(e)}")
        raise BusinessLogicError("Failed to create order")
    
    
@router.put("/{order_id}", response_model=PurchaseOrder) # Update order
async def update_order(
    order_id: int,
    order_update: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    try:
        token = validate_token_header(authorization)
        user = get_authenticated_user(token, db)
        
        validate_role_access(user, 'employee')
        db_order = db.query(PurchaseOrderModel).filter(PurchaseOrderModel.id == order_id).first()
        if not db_order:
            raise ResourceNotFoundError("Order", order_id)
        if order_update.status:
            try:
                validate_order_status_transition(str(db_order.status), order_update.status)
            except ValidationError as e:
                raise OrderStatusError(str(db_order.status), order_update.status)
        
        for key, value in order_update.model_dump(exclude_unset=True).items():
            setattr(db_order, key, value)
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        return db_order
        
    except (AuthenticationError, AuthorizationError, ResourceNotFoundError, 
            ValidationError, BusinessLogicError, OrderStatusError):
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update order {order_id}: {str(e)}")
        raise BusinessLogicError("Failed to update order")