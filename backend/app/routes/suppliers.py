from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.auth.jwt_handler import verify_token
from backend.app.database import get_db
from backend.app.models.supplier import Supplier
from backend.app.models.user import User
from backend.app.schemas.supplier import Supplier as SupplierSchema
from backend.app.schemas.supplier import SupplierCreate, SupplierSummary, SupplierUpdate
from backend.app.utils.redis_cache import cached

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


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


@router.post("/", response_model=SupplierSchema, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier: SupplierCreate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Create a new supplier in the system.

    This endpoint allows authorized users (admin/manager) to register new suppliers
    with their contact information and delivery lead time.

    Args:
        supplier: Supplier details including name, contact info, and lead time
        db: Database session
        authorization: Bearer token for authentication

    Returns:
        Newly created supplier object with assigned ID

    Raises:
        401: Unauthorized - Missing or invalid authentication
        403: Forbidden - User lacks required permissions
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    token = authorization.split(" ")[1]
    user = get_user_from_token(token, db)

    # Check if user has permission (admin or manager)
    if user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and manager can create suppliers",
        )

    db_supplier = Supplier(**supplier.model_dump())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


@router.get("/", response_model=List[SupplierSummary])
@cached(expire=300, prefix="suppliers:list")
async def list_suppliers(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
    active_only: bool = Query(True, description="Filter active suppliers only"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
):
    """
    List all suppliers with pagination and filtering.

    Args:
        db: Database session
        authorization: Bearer token for authentication
        active_only: Filter to show only active suppliers
        page: Page number for pagination
        limit: Number of items per page

    Returns:
        List of supplier summaries
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    token = authorization.split(" ")[1]
    get_user_from_token(token, db)

    query = db.query(Supplier)
    if active_only:
        query = query.filter(Supplier.is_active == True)

    suppliers = query.offset((page - 1) * limit).limit(limit).all()
    return suppliers


@router.get("/{supplier_id}", response_model=SupplierSchema)
async def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """Get detailed supplier information by ID."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    token = authorization.split(" ")[1]
    get_user_from_token(token, db)

    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found"
        )
    return supplier


@router.put("/{supplier_id}", response_model=SupplierSchema)
async def update_supplier(
    supplier_id: int,
    supplier_update: SupplierUpdate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """Update supplier details."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    token = authorization.split(" ")[1]
    user = get_user_from_token(token, db)

    # Check permissions
    if user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and manager can update suppliers",
        )

    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found"
        )

    # Update fields
    update_data = supplier_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Deactivate a supplier instead of deleting.

    This maintains referential integrity with existing purchase orders.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    token = authorization.split(" ")[1]
    user = get_user_from_token(token, db)

    # Check permissions
    if user.role not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can deactivate suppliers",
        )

    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found"
        )

    setattr(supplier, "is_active", False)
    db.commit()
    return
