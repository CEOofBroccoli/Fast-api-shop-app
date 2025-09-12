from .auth_email import router as auth_email_router
from .auth_extra import router as auth_extra_router
from .dashboard import router as dashboard_router
from .invoices import router as invoices_router
from .orders import router as orders_router
from .products import router as products_router
from .reports import router as reports_router
from .sales_orders import router as sales_orders_router
from .shop import router as shop_router
from .suppliers import router as suppliers_router
from .users import router as users_router

__all__ = [
    "auth_email_router",
    "auth_extra_router", 
    "dashboard_router",
    "invoices_router",
    "orders_router",
    "products_router",
    "reports_router",
    "sales_orders_router",
    "shop_router",
    "suppliers_router",
    "users_router"
]
