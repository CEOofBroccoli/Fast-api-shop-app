import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from backend.app.auth.jwt_handler import verify_token
from backend.app.database import get_db
from backend.app.models.order import PurchaseOrder
from backend.app.models.product import Product
from backend.app.models.sales_order import SalesOrder, SalesOrderStatus
from backend.app.models.supplier import Supplier
from backend.app.models.user import User

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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username format")
    # Sanitize username
    if not re.match(r"^[a-zA-Z0-9_.-]+$", username):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username format")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/low-stock")
async def get_low_stock_items(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Generate a report of all products with low stock levels.

    This endpoint returns a list of all products where the current quantity is at or
    below the defined minimum threshold. This report helps managers and staff
    identify products that need reordering.

    Args:
        db: Database session
        authorization: Bearer token for authentication

    Returns:
        List of products with low stock levels, including:
        - Product ID
        - Name
        - SKU
        - Current quantity
        - Minimum threshold
        - Shortage amount (threshold - quantity)

    Raises:
        401: Unauthorized - Missing or invalid authentication
        403: Forbidden - User lacks required permissions (admin/manager only)
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]
    get_user_from_token(token, db)

    low_stock_items = db.query(Product).filter(Product.quantity <= Product.min_threshold).all()

    stock_report = []
    for product in low_stock_items:
        stock_report.append(
            {
                "id": product.id,
                "name": product.name,
                "sku": product.sku,
                "current_quantity": product.quantity,
                "min_threshold": product.min_threshold,
                "price": float(getattr(product, "price")),
                "category": product.product_group,
            }
        )

    return stock_report


@router.get("/best-selling-products")
async def get_best_selling_products(
    limit: int = Query(10, ge=1, le=100, description="Number of top products to return"),
    days: int = Query(30, ge=1, description="Number of days to look back"),
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Get best-selling products based on sales order data."""
    # Verify token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    token = authorization.split(" ")[1]
    user_id = verify_token(token)
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    # Only admin, manager, and staff can view reports
    if user.role not in ["admin", "manager", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view reports",
        )

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Query for best-selling products from sales orders
    from backend.app.models.sales_order import SalesOrderItem

    best_selling = (
        db.query(
            Product.id,
            Product.name,
            Product.price,
            func.sum(SalesOrderItem.quantity).label("total_sold"),
            func.sum(SalesOrderItem.quantity * SalesOrderItem.unit_price).label("total_revenue"),
            func.count(SalesOrder.id).label("order_count"),
        )
        .join(SalesOrderItem, Product.id == SalesOrderItem.product_id)
        .join(SalesOrder, SalesOrderItem.sales_order_id == SalesOrder.id)
        .filter(
            and_(
                SalesOrder.created_at >= start_date,
                SalesOrder.created_at <= end_date,
                SalesOrder.status.in_(
                    [
                        SalesOrderStatus.CONFIRMED,
                        SalesOrderStatus.SHIPPED,
                        SalesOrderStatus.DELIVERED,
                    ]
                ),
            )
        )
        .group_by(Product.id, Product.name, Product.price)
        .order_by(func.sum(SalesOrderItem.quantity).desc())
        .limit(limit)
        .all()
    )

    # Format response
    best_selling_report = []
    for product in best_selling:
        best_selling_report.append(
            {
                "product_id": product.id,
                "product_name": product.name,
                "current_price": float(product.price),
                "total_sold": product.total_sold,
                "total_revenue": float(product.total_revenue),
                "order_count": product.order_count,
                "average_quantity_per_order": (
                    round(product.total_sold / product.order_count, 2) if product.order_count > 0 else 0
                ),
            }
        )

    return {
        "period": f"{days} days",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "products": best_selling_report,
    }


@router.get("/supplier-ratings")
async def get_supplier_ratings(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Get supplier performance ratings and statistics."""
    # Verify token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    token = authorization.split(" ")[1]
    user_id = verify_token(token)
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    # Only admin and manager can view supplier ratings
    if user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view supplier ratings",
        )

    # Get supplier performance data
    suppliers = db.query(Supplier).filter(Supplier.is_active == True).all()

    supplier_ratings = []
    for supplier in suppliers:
        # Get purchase order statistics
        total_orders = (
            db.query(func.count(PurchaseOrder.id)).filter(PurchaseOrder.supplier_id == supplier.id).scalar() or 0
        )

        # Get on-time delivery count
        on_time_deliveries = (
            db.query(func.count(PurchaseOrder.id))
            .filter(
                and_(
                    PurchaseOrder.supplier_id == supplier.id,
                    PurchaseOrder.actual_delivery_date <= PurchaseOrder.expected_delivery_date,
                    PurchaseOrder.actual_delivery_date.isnot(None),
                )
            )
            .scalar()
            or 0
        )

        # Get completed orders
        completed_orders = (
            db.query(func.count(PurchaseOrder.id))
            .filter(
                and_(
                    PurchaseOrder.supplier_id == supplier.id,
                    PurchaseOrder.actual_delivery_date.isnot(None),
                )
            )
            .scalar()
            or 0
        )

        # Calculate on-time delivery rate
        on_time_rate = (on_time_deliveries / completed_orders * 100) if completed_orders > 0 else 0

        # Calculate average delivery delay
        avg_delay_query = (
            db.query(
                func.avg(
                    func.extract("epoch", PurchaseOrder.actual_delivery_date)
                    - func.extract("epoch", PurchaseOrder.expected_delivery_date)
                ).label("avg_delay_seconds")
            )
            .filter(
                and_(
                    PurchaseOrder.supplier_id == supplier.id,
                    PurchaseOrder.actual_delivery_date.isnot(None),
                    PurchaseOrder.expected_delivery_date.isnot(None),
                )
            )
            .first()
        )

        avg_delay_days = 0
        if avg_delay_query and avg_delay_query.avg_delay_seconds:
            avg_delay_days = round(avg_delay_query.avg_delay_seconds / (24 * 60 * 60), 1)

        # Calculate total order value
        total_value = (
            db.query(func.sum(PurchaseOrder.total_cost)).filter(PurchaseOrder.supplier_id == supplier.id).scalar() or 0
        )

        # Calculate rating (based on on-time delivery rate and other factors)
        base_rating = on_time_rate / 20  # 0-5 scale based on on-time delivery

        # Adjust rating based on average delay
        if avg_delay_days <= 0:
            delay_adjustment = 0.5  # Bonus for early delivery
        elif avg_delay_days <= 1:
            delay_adjustment = 0
        elif avg_delay_days <= 3:
            delay_adjustment = -0.5
        else:
            delay_adjustment = -1

        calculated_rating = max(1, min(5, base_rating + delay_adjustment))

        supplier_ratings.append(
            {
                "supplier_id": supplier.id,
                "supplier_name": supplier.name,
                "contact_person": supplier.contact_person,
                "email": supplier.email,
                "phone": supplier.phone,
                "rating": round(calculated_rating, 1),
                "total_orders": total_orders,
                "completed_orders": completed_orders,
                "on_time_deliveries": on_time_deliveries,
                "on_time_delivery_rate": round(on_time_rate, 1),
                "average_delay_days": avg_delay_days,
                "total_order_value": float(total_value),
                "delivery_lead_time_days": supplier.delivery_lead_time_days,
            }
        )

    # Sort by rating (highest first)
    supplier_ratings.sort(key=lambda x: x["rating"], reverse=True)

    return {
        "suppliers": supplier_ratings,
        "summary": {
            "total_suppliers": len(supplier_ratings),
            "average_rating": (
                round(
                    sum(s["rating"] for s in supplier_ratings) / len(supplier_ratings),
                    1,
                )
                if supplier_ratings
                else 0
            ),
            "top_performer": (supplier_ratings[0]["supplier_name"] if supplier_ratings else None),
            "overall_on_time_rate": round(
                sum(s["on_time_deliveries"] for s in supplier_ratings)
                / max(sum(s["completed_orders"] for s in supplier_ratings), 1)
                * 100,
                1,
            ),
        },
    }


@router.get("/order-status")
async def get_order_status_counts(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Generate a summary report of orders by status.

    This endpoint returns a count of orders grouped by their current status.
    It provides a quick overview of the order processing pipeline for business
    reporting and operations management.

    Args:
        db: Database session
        authorization: Bearer token for authentication

    Returns:
        Dictionary with status names as keys and counts as values:
        {
            "pending": 5,
            "processing": 3,
            "shipped": 10,
            "delivered": 42,
            "cancelled": 2
        }

    Raises:
        401: Unauthorized - Missing or invalid authentication
        403: Forbidden - User lacks required permissions (admin/manager only)
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]
    get_user_from_token(token, db)

    order_status_counts = (
        db.query(PurchaseOrder.status, func.count(PurchaseOrder.status)).group_by(PurchaseOrder.status).all()
    )
    # Convert query results to dictionary
    result = {}
    for order_status, count in order_status_counts:
        # Get the enum value (e.g., "Draft" instead of "DRAFT")
        status_value = order_status.value if hasattr(order_status, "value") else str(order_status)
        result[status_value] = count
    return result


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

    # Get inventory value grouped by product_group
    inventory_by_group = (
        db.query(
            Product.product_group,
            func.sum(Product.quantity * Product.price).label("group_value"),
        )
        .group_by(Product.product_group)
        .all()
    )

    # Create result dictionary with product groups as keys
    result = {}
    total_value = 0
    for group, value in inventory_by_group:
        group_value = float(value) if value else 0
        result[group] = group_value
        total_value += group_value

    # Also include total
    result["total_inventory_value"] = total_value

    return result


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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid product ID")

    order_history = (
        db.query(PurchaseOrder).filter(PurchaseOrder.product_id == product_id).order_by(PurchaseOrder.created_at).all()
    )
    return order_history
