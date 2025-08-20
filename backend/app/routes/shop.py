import os
import shutil
import time
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.auth.jwt_handler import verify_token
from backend.app.config.shop_settings import shop_settings
from backend.app.database import get_db
from backend.app.models.user import User

router = APIRouter(prefix="/shop", tags=["shop"])

# Allowed image formats
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/upload-logo")
async def upload_logo(
    file: UploadFile = File(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """
    Upload shop logo image (Admin only).

    Uploads a new logo image and updates the shop configuration.
    Only administrators can upload logos.
    """
    # Verify admin token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )

    token = authorization.split(" ")[1]
    user_id = verify_token(token)
    user = db.query(User).filter(User.id == user_id).first()

    if not user or getattr(user, "role", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided"
        )

    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size: 5MB",
        )

    # Create logos directory if it doesn't exist
    logos_dir = Path("static/images/logos")
    logos_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    timestamp = int(time.time())
    filename = f"n-market-logo-{timestamp}{file_ext}"
    file_path = logos_dir / filename

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}",
        )

    # Update logo URL (you might want to update this in a database or config file)
    logo_url = f"/static/images/logos/{filename}"

    return {
        "message": "Logo uploaded successfully",
        "filename": filename,
        "logo_url": logo_url,
        "file_size": len(content),
        "file_type": file_ext,
    }


@router.get("/logo")
async def get_current_logo():
    """
    Get current shop logo information.

    Returns the current logo URL and shop branding information.
    This is a public endpoint.
    """
    return {
        "logo_url": shop_settings.company_logo_url,
        "shop_name": shop_settings.shop_name,
        "full_logo_url": f"{shop_settings.shop_website}{shop_settings.company_logo_url}",
    }


@router.get("/branding")
async def get_shop_branding():
    """
    Get complete shop branding information.

    Returns all shop branding elements including logos, colors, and styling.
    This is a public endpoint for frontend applications.
    """
    return {
        "shop_name": shop_settings.shop_name,
        "shop_description": shop_settings.shop_description,
        "logos": {
            "main": {
                "url": shop_settings.company_logo_url,
                "full_url": f"{shop_settings.shop_website}{shop_settings.company_logo_url}",
                "alt_text": f"{shop_settings.shop_name} Logo",
                "description": "Main square logo (300x300px)",
                "recommended_size": "300x300px",
                "use_case": "General branding, email headers, centered layouts",
            },
            "square": {
                "url": shop_settings.company_logo_square_url,
                "full_url": f"{shop_settings.shop_website}{shop_settings.company_logo_square_url}",
                "alt_text": f"{shop_settings.shop_name} Square Logo",
                "description": "Square logo for profile pictures and icons",
                "recommended_size": "120x120px for emails, 300x300px for general use",
                "use_case": "Email headers (120px), app icons, profile pictures",
            },
            "wide": {
                "url": shop_settings.company_logo_square_url,  # Using square logo for better quality
                "full_url": f"{shop_settings.shop_website}{shop_settings.company_logo_square_url}",
                "alt_text": f"{shop_settings.shop_name} Header Logo",
                "description": "Square logo recommended for headers (better than stretched wide)",
                "recommended_size": "80px height for headers",
                "use_case": "Website headers, invoice headers (use centered square logo)",
            },
            "compact": {
                "url": getattr(
                    shop_settings,
                    "company_logo_small_url",
                    shop_settings.company_logo_url,
                ),
                "full_url": f"{shop_settings.shop_website}{getattr(shop_settings, 'company_logo_small_url', shop_settings.company_logo_url)}",
                "alt_text": f"{shop_settings.shop_name} Compact Icon",
                "description": "Small icon for compact spaces with text",
                "recommended_size": "40x40px icon + N-Market text",
                "use_case": "Navigation bars, mobile headers, compact layouts",
            },
            "favicon": {
                "url": shop_settings.company_favicon_url,
                "full_url": f"{shop_settings.shop_website}{shop_settings.company_favicon_url}",
                "alt_text": f"{shop_settings.shop_name} Icon",
                "description": "Browser favicon (32x32px)",
                "recommended_size": "32x32px",
                "use_case": "Browser tabs, bookmarks, app icons",
            },
        },
        "layout_templates": {
            "email_header": {
                "description": "Centered square logo (120px) with shop name below",
                "html": f'<div style="text-align: center; padding: 30px 20px; background: #2c3e50; color: white;"><img src="{shop_settings.company_logo_url}" style="width: 120px; height: 120px; border-radius: 8px; margin-bottom: 15px;"><h1 style="margin: 0 0 8px 0; font-size: 28px;">{shop_settings.shop_name}</h1><p style="margin: 0; opacity: 0.9; font-size: 16px;">{shop_settings.shop_description}</p></div>',
            },
            "website_header": {
                "description": "Horizontal logo + text layout for website headers",
                "html": f'<div style="display: flex; align-items: center; gap: 15px; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;"><img src="{shop_settings.company_logo_url}" style="width: 50px; height: 50px; border-radius: 8px;"><div><h1 style="margin: 0; font-size: 28px;">{shop_settings.shop_name}</h1><p style="margin: 2px 0 0 0; font-size: 14px; opacity: 0.9;">{shop_settings.shop_description}</p></div></div>',
            },
            "compact_nav": {
                "description": "Small icon + text for compact spaces",
                "html": f'<div style="display: flex; align-items: center; gap: 10px; padding: 10px;"><img src="{getattr(shop_settings, "company_logo_small_url", shop_settings.company_logo_url)}" style="width: 40px; height: 40px;"><span style="font-weight: bold; color: #333;">{shop_settings.shop_name}</span></div>',
            },
            "invoice_header": {
                "description": "Centered square logo with company info below",
                "html": f'<div style="text-align: center; padding: 30px; border-bottom: 2px solid #2c3e50;"><img src="{shop_settings.company_logo_url}" style="width: 100px; height: 100px; margin-bottom: 20px;"><h1 style="margin: 0 0 10px 0; color: #2c3e50;">{shop_settings.shop_name}</h1><p style="margin: 0; color: #666;">{shop_settings.shop_description}</p></div>',
            },
        },
        "colors": {
            "primary": "#2c3e50",
            "secondary": "#3498db",
            "accent": "#e74c3c",
            "text": "#333333",
            "background": "#f8f9fa",
        },
        "contact": {
            "email": shop_settings.shop_email,
            "phone": shop_settings.shop_phone,
            "website": shop_settings.shop_website,
            "address": shop_settings.shop_address,
        },
    }
