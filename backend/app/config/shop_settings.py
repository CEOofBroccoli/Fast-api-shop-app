"""
Shop/Company Configuration
Centralized settings for business information and branding.
"""

import os
from typing import Optional


class ShopSettings:
    """Shop configuration settings"""

    def __init__(self):
        # Basic Shop Information
        self.shop_name = os.getenv("SHOP_NAME", "N-Market")
        self.shop_description = os.getenv("SHOP_DESCRIPTION", "Your One-Stop Inventory Solution")
        self.shop_email = os.getenv("SHOP_EMAIL", "modavari005@gmail.com")
        self.shop_phone = os.getenv("SHOP_PHONE", "+1-555-0123")
        self.shop_address = os.getenv("SHOP_ADDRESS", "123 Business Street, City, State 12345")
        self.shop_website = os.getenv("SHOP_WEBSITE", "https://n-market.com")

        # Branding - Primary logo (square) recommended for most uses
        self.company_logo_url = os.getenv("COMPANY_LOGO_URL", "/static/images/logos/n-market-logo.png")
        self.company_logo_square_url = os.getenv("COMPANY_LOGO_SQUARE_URL", "/static/images/logos/n-market-logo.png")
        # Note: Wide logo may need improvement - consider using square logo for headers
        self.company_logo_wide_url = os.getenv(
            "COMPANY_LOGO_WIDE_URL", "/static/images/logos/n-market-logo.png"
        )  # Using square as fallback
        self.company_favicon_url = os.getenv("COMPANY_FAVICON_URL", "/static/images/logos/icon3.ico")

        # Additional logo variants
        self.company_logo_hd_url = os.getenv("COMPANY_LOGO_HD_URL", "/static/images/logos/hd-logo.png")
        self.company_logo_small_url = os.getenv("COMPANY_LOGO_SMALL_URL", "/static/images/logos/small.png")

        # Email Configuration
        self.email_from = os.getenv("EMAIL_FROM", f'"{self.shop_name}" <{self.shop_email}>')

        # Business Settings
        self.default_currency = "USD"
        self.tax_rate = 0.08  # 8% tax rate

        # Invoice Settings
        self.invoice_prefix = "NM"  # N-Market prefix for invoice numbers
        self.invoice_terms = "Payment due within 30 days"


# Global shop settings instance
shop_settings = ShopSettings()


def get_shop_context() -> dict:
    """Get shop context for templates and emails"""
    return {
        "shop_name": shop_settings.shop_name,
        "shop_description": shop_settings.shop_description,
        "shop_email": shop_settings.shop_email,
        "shop_phone": shop_settings.shop_phone,
        "shop_address": shop_settings.shop_address,
        "shop_website": shop_settings.shop_website,
        "company_logo_url": shop_settings.company_logo_url,
        "default_currency": shop_settings.default_currency,
    }


def get_branded_email_from() -> str:
    """Get properly formatted email sender"""
    return f'"{shop_settings.shop_name}" <{shop_settings.shop_email}>'
