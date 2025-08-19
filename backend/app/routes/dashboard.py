# Dashboard API routes for business analytics and metrics
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Any, List, Optional
from backend.app.database import get_db
from backend.app.models.product import Product
from backend.app.models.sales_order import SalesOrder, SalesOrderStatus
from backend.app.models.order import PurchaseOrder, InvoiceStatus
from backend.app.models.user import User
from backend.app.models.supplier import Supplier
from backend.app.auth.jwt_handler import verify_token
from backend.app.utils.redis_cache import cached
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging

# Setup logging for debugging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class DashboardStats(BaseModel):
    """Data model for dashboard statistics"""
    total_products: int
    total_customers: int
    total_suppliers: int
    low_stock_products: int
    pending_sales_orders: int
    pending_purchase_orders: int
    total_sales_value: float
    total_purchase_value: float
    top_selling_products: List[Dict[str, Any]]
    recent_sales_orders: List[Dict[str, Any]]


def get_user_from_token(token: str, db: Session):
    """Extract and validate user from JWT token"""
    try:
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
    except Exception as e:
        logger.error(f"Error getting user from token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


@router.get("/stats", response_model=DashboardStats)
@cached(expire=300, prefix="dashboard:stats")  # Cache for 5 minutes
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """Get comprehensive dashboard statistics and business metrics"""
    # Validate authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    try:
        token = authorization.split(" ")[1]
        user = get_user_from_token(token, db)
        
        # Check user permissions
        user_role = getattr(user, 'role', '')
        if user_role not in ["admin", "manager", "staff"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access dashboard"
            )
        
        # Get basic counts with error handling
        try:
            total_products = db.query(Product).count()
            total_customers = db.query(User).filter(User.role == "customer").count()
            total_suppliers = db.query(Supplier).filter(Supplier.is_active == True).count()
            
            # Low stock products count
            low_stock_products = db.query(Product).filter(
                Product.quantity <= Product.min_threshold
            ).count()
            
            # Pending orders count
            pending_sales_orders = db.query(SalesOrder).filter(
                SalesOrder.status == SalesOrderStatus.PENDING
            ).count()
            
            pending_purchase_orders = db.query(PurchaseOrder).filter(
                PurchaseOrder.status == InvoiceStatus.DRAFT
            ).count()
            
        except Exception as e:
            logger.error(f"Error getting basic counts: {str(e)}")
            # Return default values if database queries fail
            total_products = total_customers = total_suppliers = 0
            low_stock_products = pending_sales_orders = pending_purchase_orders = 0
        
        # Calculate total values with safe error handling
        try:
            total_sales_value = db.query(func.sum(SalesOrder.total_amount)).filter(
                SalesOrder.status.in_([
                    SalesOrderStatus.CONFIRMED,
                    SalesOrderStatus.SHIPPED,
                    SalesOrderStatus.DELIVERED
                ])
            ).scalar() or 0.0
            
            total_purchase_value = db.query(func.sum(PurchaseOrder.total_cost)).filter(
                PurchaseOrder.status != InvoiceStatus.DRAFT
            ).scalar() or 0.0
        except Exception as e:
            logger.error(f"Error calculating totals: {str(e)}")
            total_sales_value = total_purchase_value = 0.0
    
        # Get top selling products (last 30 days) with safe handling
        try:
            thirty_days_ago = datetime.now() - timedelta(days=30)
            top_selling_query = db.query(
                Product.name,
                Product.sku,
                func.sum(SalesOrder.quantity).label('total_sold'),
                func.sum(SalesOrder.total_amount).label('total_revenue')
            ).join(
                SalesOrder, Product.id == SalesOrder.product_id
            ).filter(
                and_(
                    SalesOrder.order_date >= thirty_days_ago,
                    SalesOrder.status.in_([
                        SalesOrderStatus.CONFIRMED,
                        SalesOrderStatus.SHIPPED,
                        SalesOrderStatus.DELIVERED
                    ])
                )
            ).group_by(Product.id, Product.name, Product.sku).order_by(
                func.sum(SalesOrder.quantity).desc()
            ).limit(5).all()
            
            top_selling_products = [
                {
                    "name": row.name,
                    "sku": row.sku,
                    "total_sold": int(row.total_sold or 0),
                    "total_revenue": float(row.total_revenue or 0)
                }
                for row in top_selling_query
            ]
        except Exception as e:
            logger.error(f"Error getting top selling products: {str(e)}")
            top_selling_products = []
        
        # Get recent sales orders with safe handling
        try:
            recent_sales_query = db.query(SalesOrder).order_by(
                SalesOrder.created_at.desc()
            ).limit(10).all()
            
            recent_sales_orders = []
            for order in recent_sales_query:
                try:
                    # Safe attribute access for order properties
                    order_id = getattr(order, 'id', 0)
                    customer_id = getattr(order, 'customer_id', 0)
                    total_amount_val = getattr(order, 'total_amount', 0)
                    total_amount = float(total_amount_val) if total_amount_val is not None else 0.0
                    order_status = str(getattr(order, 'status', ''))
                    order_date_val = getattr(order, 'order_date', None)
                    order_date = order_date_val.isoformat() if order_date_val is not None else datetime.now().isoformat()
                    
                    recent_sales_orders.append({
                        "id": order_id,
                        "customer_id": customer_id,
                        "total_amount": total_amount,
                        "status": order_status,
                        "order_date": order_date
                    })
                except Exception as e:
                    logger.error(f"Error processing order: {str(e)}")
                    continue
        except Exception as e:
            logger.error(f"Error getting recent sales orders: {str(e)}")
            recent_sales_orders = []
        
        return DashboardStats(
            total_products=total_products,
            total_customers=total_customers,
            total_suppliers=total_suppliers,
            low_stock_products=low_stock_products,
            pending_sales_orders=pending_sales_orders,
            pending_purchase_orders=pending_purchase_orders,
            total_sales_value=float(total_sales_value),
            total_purchase_value=float(total_purchase_value),
            top_selling_products=top_selling_products,
            recent_sales_orders=recent_sales_orders
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching dashboard statistics"
        )


@router.get("/inventory-status")
async def get_inventory_status(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """Get detailed inventory status breakdown with safe error handling"""
    # Validate authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    try:
        token = authorization.split(" ")[1]
        user = get_user_from_token(token, db)
        
        # Check permissions
        user_role = getattr(user, 'role', '')
        if user_role not in ["admin", "manager", "staff"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Get inventory breakdown with error handling
        try:
            total_products = db.query(Product).count()
            in_stock = db.query(Product).filter(Product.quantity > Product.min_threshold).count()
            low_stock = db.query(Product).filter(
                and_(Product.quantity <= Product.min_threshold, Product.quantity > 0)
            ).count()
            out_of_stock = db.query(Product).filter(Product.quantity == 0).count()
            
            # Calculate total inventory value
            inventory_value = db.query(
                func.sum(Product.price * Product.quantity)
            ).scalar() or 0.0
            
        except Exception as e:
            logger.error(f"Error getting inventory status: {str(e)}")
            # Return default values if queries fail
            total_products = in_stock = low_stock = out_of_stock = 0
            inventory_value = 0.0
        
        return {
            "total_products": total_products,
            "in_stock": in_stock,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
            "inventory_value": float(inventory_value),
            "percentages": {
                "in_stock": round((in_stock / total_products * 100) if total_products > 0 else 0, 2),
                "low_stock": round((low_stock / total_products * 100) if total_products > 0 else 0, 2),
                "out_of_stock": round((out_of_stock / total_products * 100) if total_products > 0 else 0, 2)
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in inventory status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching inventory status"
        )


@router.get("/order-overview")
async def get_order_overview(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """Get order status overview for both sales and purchase orders with safe error handling"""
    # Validate authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    try:
        token = authorization.split(" ")[1]
        user = get_user_from_token(token, db)
        
        # Check permissions
        user_role = getattr(user, 'role', '')
        if user_role not in ["admin", "manager", "staff"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Get order status counts with error handling
        try:
            # Sales order status counts
            sales_orders = {}
            for order_status in SalesOrderStatus:
                count = db.query(SalesOrder).filter(SalesOrder.status == order_status).count()
                sales_orders[order_status.value] = count
            
            # Purchase order status counts
            purchase_orders = {}
            for order_status in InvoiceStatus:
                count = db.query(PurchaseOrder).filter(PurchaseOrder.status == order_status).count()
                purchase_orders[order_status.value] = count
                
        except Exception as e:
            logger.error(f"Error getting order overview: {str(e)}")
            # Return empty dictionaries if queries fail
            sales_orders = {}
            purchase_orders = {}
        
        return {
            "sales_orders": sales_orders,
            "purchase_orders": purchase_orders,
            "totals": {
                "total_sales_orders": sum(sales_orders.values()),
                "total_purchase_orders": sum(purchase_orders.values())
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in order overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching order overview"
        )
