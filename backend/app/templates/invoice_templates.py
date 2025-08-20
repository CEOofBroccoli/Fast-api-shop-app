"""
Invoice template generator with improved N-Market branding
"""

from backend.app.config.shop_settings import shop_settings


def generate_invoice_header_html():
    """Generate professional invoice header with centered square logo"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            .invoice-header {{
                text-align: center;
                padding: 40px 30px;
                border-bottom: 3px solid #2c3e50;
                margin-bottom: 30px;
                background: #f8f9fa;
            }}
            
            .invoice-logo {{
                width: 100px;
                height: 100px;
                margin: 0 auto 20px auto;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                display: block;
            }}
            
            .company-name {{
                font-size: 32px;
                font-weight: bold;
                color: #2c3e50;
                margin: 0 0 8px 0;
                letter-spacing: 1px;
            }}
            
            .company-tagline {{
                font-size: 16px;
                color: #666;
                margin: 0 0 20px 0;
                font-style: italic;
            }}
            
            .company-info {{
                color: #555;
                font-size: 14px;
                line-height: 1.6;
                margin-top: 15px;
            }}
            
            .company-info div {{
                margin: 5px 0;
            }}
            
            .invoice-title {{
                background: #2c3e50;
                color: white;
                padding: 15px 30px;
                margin: 30px 0;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            
            .invoice-details {{
                display: flex;
                justify-content: space-between;
                margin: 30px 0;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
            }}
            
            @media print {{
                .invoice-header {{
                    background: white !important;
                    box-shadow: none;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="invoice-header">
            <img src="{shop_settings.company_logo_url}" 
                 alt="{shop_settings.shop_name} Logo" 
                 class="invoice-logo">
            
            <h1 class="company-name">{shop_settings.shop_name}</h1>
            <p class="company-tagline">{shop_settings.shop_description}</p>
            
            <div class="company-info">
                <div><strong>Email:</strong> {shop_settings.shop_email}</div>
                <div><strong>Phone:</strong> {shop_settings.shop_phone}</div>
                <div><strong>Website:</strong> {shop_settings.shop_website}</div>
                <div><strong>Address:</strong> {shop_settings.shop_address}</div>
            </div>
        </div>
        
        <div class="invoice-title">
            INVOICE
        </div>
        
        <div class="invoice-details">
            <div>
                <h3>Bill To:</h3>
                <div>[Customer Information]</div>
            </div>
            <div style="text-align: right;">
                <h3>Invoice Details:</h3>
                <div><strong>Invoice #:</strong> [Invoice Number]</div>
                <div><strong>Date:</strong> [Invoice Date]</div>
                <div><strong>Due Date:</strong> [Due Date]</div>
            </div>
        </div>
        
        <!-- Invoice content would go here -->
    </body>
    </html>
    """


def generate_compact_header_html():
    """Generate compact header layout for navigation/mobile"""
    return f"""
    <div style="display: flex; align-items: center; gap: 12px; padding: 12px 20px; 
                background: white; border-bottom: 1px solid #e9ecef; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <img src="{getattr(shop_settings, 'company_logo_small_url', shop_settings.company_logo_url)}" 
             alt="{shop_settings.shop_name}" 
             style="width: 40px; height: 40px; border-radius: 6px;">
        <div>
            <div style="font-weight: bold; color: #333; font-size: 18px; margin: 0;">{shop_settings.shop_name}</div>
            <div style="font-size: 12px; color: #666; margin: 0;">{shop_settings.shop_description}</div>
        </div>
    </div>
    """


def generate_email_signature_html():
    """Generate professional email signature with logo"""
    return f"""
    <div style="border-top: 2px solid #2c3e50; margin-top: 30px; padding-top: 20px; text-align: center;">
        <img src="{shop_settings.company_logo_url}" 
             style="width: 60px; height: 60px; border-radius: 6px; margin-bottom: 10px;">
        <div style="font-weight: bold; color: #2c3e50; font-size: 16px;">{shop_settings.shop_name}</div>
        <div style="color: #666; font-size: 14px; margin: 5px 0;">{shop_settings.shop_description}</div>
        <div style="color: #666; font-size: 12px; line-height: 1.4;">
            {shop_settings.shop_email} | {shop_settings.shop_phone}<br>
            <a href="{shop_settings.shop_website}" style="color: #3498db;">{shop_settings.shop_website}</a>
        </div>
    </div>
    """
