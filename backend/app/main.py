# Main FastAPI application for N-Market inventory management system
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

# Authentication imports
from backend.app.auth.auth_handler import (
    authenticate_user,
    create_user_secure,
    get_user,
    get_user_by_email,
    update_last_login,
)
from backend.app.auth.jwt_handler import create_access_token, get_current_user, verify_token
from backend.app.config.shop_settings import get_shop_context, shop_settings

# Database imports
from backend.app.database import Base, engine, get_db
from backend.app.models import order, product, user

# Route imports
from backend.app.routes import dashboard, invoices, orders, products, reports, sales_orders, shop, suppliers, users
from backend.app.schemas.user import token, user, user_create

# Utility imports
from backend.app.utils.redis_cache import cache as redis_cache

# Basic logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
logger = logging.getLogger(__name__)

# Create FastAPI app with shop branding
app = FastAPI(
    title=f"{shop_settings.shop_name} - Inventory Management API",
    description=f"""
    ## {shop_settings.shop_name}
    *{shop_settings.shop_description}*
    
    A comprehensive inventory and order management API for businesses.
    
    ## Features
    
    * **User Management**: Secure registration, authentication, and role-based access control
    * **Product Management**: Inventory tracking, stock adjustments with audit trail
    * **Supplier Management**: Supplier registration, performance tracking, and ratings
    * **Sales Orders**: Complete order lifecycle management with status tracking
    * **Purchase Orders**: Automated reordering and supplier management
    * **Dashboard & Analytics**: Real-time business insights and performance metrics
    * **Invoice Generation**: Professional PDF invoices and receipts
    * **Reporting**: Generate insights and analytics on sales and inventory
    
    ## Authentication
    
    All endpoints except login and signup require JWT authentication using bearer tokens.
    Include an `Authorization: Bearer <token>` header with all requests.
    
    ## Role-Based Access
    
    * **admin**: Full system access
    * **manager**: Product and order management, reporting
    * **staff**: Limited product management, order processing
    * **customer**: View products, manage own orders
    
    ## Contact Information
    
    * **Email**: {shop_settings.shop_email}
    * **Phone**: {shop_settings.shop_phone}
    * **Website**: {shop_settings.shop_website}
    """,
    version="1.0.0",
    contact={
        "name": f"{shop_settings.shop_name} API Support",
        "email": shop_settings.shop_email,
        "url": shop_settings.shop_website,
    },
    license_info={
        "name": "MIT",
    },
)

# Create database tables - with error handling
try:
    Base.metadata.create_all(bind=engine)
    logging.info("Database tables created successfully")
except Exception as e:
    logging.warning(f"Could not create database tables: {e}")
    logging.info("This is expected in Docker test environment without database service")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers
from backend.app.utils.security_headers import add_security_headers_middleware

add_security_headers_middleware(app)

# Serve static files (logos, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register error handlers
from backend.app.error_handlers import register_exception_handlers

register_exception_handlers(app)

# Include API route modules
app.include_router(orders.router)
app.include_router(reports.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(suppliers.router)
app.include_router(sales_orders.router)
app.include_router(dashboard.router)
app.include_router(invoices.router)
app.include_router(shop.router)


@app.get("/")
def root():
    """API root endpoint with navigation information"""
    return {
        "message": f"Welcome to {shop_settings.shop_name} API",
        "shop": shop_settings.shop_name,
        "description": shop_settings.shop_description,
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health",
        "shop_info": "/shop/info",
        "login": "/login",
        "logo_showcase": "/logo-showcase",  # Link to logo implementation showcase
        "endpoints": {
            "products": "/products",
            "orders": "/orders (purchase orders)",
            "sales_orders": "/sales-orders",
            "users": "/users",
            "suppliers": "/suppliers",
            "reports": "/reports",
            "dashboard": "/dashboard",
            "invoices": "/invoices",
        },
    }


@app.get("/logo-showcase")
def logo_showcase():
    """Redirect to logo implementation showcase page"""
    from fastapi.responses import FileResponse

    return FileResponse("static/logo-implementation-showcase.html")


@app.get("/shop/info")
def get_shop_info() -> Dict:
    """Get public shop information and branding details"""
    return {
        "shop_name": shop_settings.shop_name,
        "shop_description": shop_settings.shop_description,
        "contact": {
            "email": shop_settings.shop_email,
            "phone": shop_settings.shop_phone,
            "address": shop_settings.shop_address,
            "website": shop_settings.shop_website,
        },
        "branding": {
            "logo_url": shop_settings.company_logo_url,
            "currency": shop_settings.default_currency,
        },
        "business_info": {
            "invoice_prefix": shop_settings.invoice_prefix,
            "tax_rate": shop_settings.tax_rate,
            "invoice_terms": shop_settings.invoice_terms,
        },
    }


@app.get("/health")
def health_check(db_session: Session = Depends(get_db)):
    """Health check endpoint for monitoring system status"""
    # Check database connection
    db_status = "active"
    try:
        db_session.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "inactive"

    # Check Redis connection
    redis_status = "active" if redis_cache._client else "inactive"

    return {
        "status": ("healthy" if db_status == "active" and redis_status == "active" else "degraded"),
        "api_version": "1.0.0",
        "components": {"database": db_status, "redis_cache": redis_status},
        "timestamp": datetime.now().isoformat(),
    }


# Rate limiting for signup endpoint
from backend.app.routes.auth_email import check_rate_limit


@app.post("/signup", response_model=user)
def sign_up(user_data: user_create, db: Session = Depends(get_db)):
    """User registration endpoint with rate limiting"""
    logger.setLevel(logging.DEBUG)

    check_rate_limit(f"signup:{user_data.email}")
    try:
        logger.debug(f"Creating user with email: {user_data.email}")
        user_obj = create_user_secure(db=db, user=user_data)
        logger.debug(f"User created successfully: {user_obj.username}")
        return user_obj
    except ValueError as ve:
        logger.error(f"Validation error during signup: {str(ve)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Signup failed")


@app.post("/login", response_model=token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """User login endpoint with rate limiting and email verification"""
    check_rate_limit(f"login:{form_data.username}")
    user_obj = authenticate_user(db, form_data.username, form_data.password)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not getattr(user_obj, "is_verified", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")
    update_last_login(db, user_obj)
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user_obj.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=user)
def read_users_me(current_user: user = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@app.get("/test-db")
def test_db(db_session: Session = Depends(get_db)):
    """Test database connection endpoint"""
    try:
        db_session.execute(text("SELECT 1"))
        return {"message": "Database connection is working"}
    except Exception as error:
        logger.error(f"Database connection test failed: {str(error)}")
        raise
