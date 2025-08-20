import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from backend.app.config.shop_settings import shop_settings

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, body: str, is_html: bool = True):
    """Send branded email using shop configuration"""
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USERNAME")  # Changed from SMTP_USER
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_user or not smtp_password:
        logger.error("SMTP credentials not configured")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = shop_settings.email_from  # Use branded email_from
        msg["To"] = to_email
        msg[
            "Subject"
        ] = f"{shop_settings.shop_name} - {subject}"  # Add shop name to subject

        # Add shop branding to email body
        branded_body = get_branded_email_template(body, subject)

        content_type = "html" if is_html else "plain"
        msg.attach(MIMEText(branded_body, content_type))

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()

        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


def get_branded_email_template(content: str, subject: str) -> str:
    """Create branded email template with shop information and logo"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .header {{
                background-color: #2c3e50;
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .logo {{
                width: 120px;
                height: 120px;
                max-width: 120px;
                max-height: 120px;
                margin: 0 auto 15px auto;
                border-radius: 8px;
                display: block;
            }}
            .content {{
                padding: 30px 20px;
                background-color: #f9f9f9;
            }}
            .footer {{
                background-color: #34495e;
                color: white;
                padding: 20px;
                text-align: center;
                font-size: 12px;
            }}
            .shop-name {{
                font-size: 28px;
                font-weight: bold;
                margin: 0 0 8px 0;
            }}
            .shop-description {{
                margin: 0;
                opacity: 0.9;
                font-size: 16px;
                margin: 5px 0 0 0;
                opacity: 0.9;
            }}
            .button {{
                background-color: #3498db;
                color: white !important;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <img src="{shop_settings.shop_website}{shop_settings.company_logo_url}" 
                     alt="{shop_settings.shop_name} Logo" class="logo" />
                <h1 class="shop-name">{shop_settings.shop_name}</h1>
                <p class="shop-description">{shop_settings.shop_description}</p>
            </div>
            
            <div class="content">
                <h2>{subject}</h2>
                {content}
            </div>
            
            <div class="footer">
                <p><strong>{shop_settings.shop_name}</strong></p>
                <p>{shop_settings.shop_address}</p>
                <p>Phone: {shop_settings.shop_phone} | Email: {shop_settings.shop_email}</p>
                <p>Website: {shop_settings.shop_website}</p>
                <p style="margin-top: 15px; opacity: 0.8;">
                    This email was sent from {shop_settings.shop_name} inventory management system.
                </p>
            </div>
        </div>
    </body>
    </html>
    """


def send_welcome_email(user_email: str, user_name: str, verification_token: str):
    """Send branded welcome email"""
    subject = "Welcome! Please verify your email"

    content = f"""
    <p>Hello <strong>{user_name}</strong>,</p>
    
    <p>Welcome to {shop_settings.shop_name}! We're excited to have you join our inventory management platform.</p>
    
    <p>To get started, please verify your email address by clicking the button below:</p>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="{shop_settings.shop_website}/verify/{verification_token}" 
           style="background-color: #3498db; color: white; padding: 12px 30px; 
                  text-decoration: none; border-radius: 5px; display: inline-block;">
            Verify Email Address
        </a>
    </div>
    
    <p>If the button doesn't work, copy and paste this link into your browser:</p>
    <p><a href="{shop_settings.shop_website}/verify/{verification_token}">
        {shop_settings.shop_website}/verify/{verification_token}
    </a></p>
    
    <p>If you didn't create an account with us, please ignore this email.</p>
    
    <p>Best regards,<br>
    The {shop_settings.shop_name} Team</p>
    """

    return send_email(user_email, subject, content)


def send_order_confirmation_email(user_email: str, order_id: int, order_total: float):
    """Send branded order confirmation email"""
    subject = f"Order #{shop_settings.invoice_prefix}-{order_id:04d} Confirmed"

    content = f"""
    <p>Hello,</p>
    
    <p>Thank you for your order! We've received your order and it's being processed.</p>
    
    <div style="background-color: #e8f5e8; padding: 20px; border-radius: 5px; margin: 20px 0;">
        <h3 style="margin: 0; color: #27ae60;">Order Details</h3>
        <p style="margin: 10px 0 0 0;">
            <strong>Order Number:</strong> {shop_settings.invoice_prefix}-{order_id:04d}<br>
            <strong>Total Amount:</strong> {shop_settings.default_currency} {order_total:.2f}
        </p>
    </div>
    
    <p>You will receive another email once your order has been shipped with tracking information.</p>
    
    <p>If you have any questions about your order, please contact us at {shop_settings.shop_email} 
       or call {shop_settings.shop_phone}.</p>
    
    <p>Thank you for choosing {shop_settings.shop_name}!</p>
    
    <p>Best regards,<br>
    The {shop_settings.shop_name} Team</p>
    """

    return send_email(user_email, subject, content)


def send_low_stock_alert(
    admin_email: str, product_name: str, current_stock: int, reorder_point: int
):
    """Send branded low stock alert to admin"""
    subject = f"Low Stock Alert - {product_name}"

    content = f"""
    <p>Hello Admin,</p>
    
    <div style="background-color: #fff3cd; padding: 20px; border-radius: 5px; margin: 20px 0; 
                border-left: 4px solid #ffc107;">
        <h3 style="margin: 0; color: #856404;">⚠️ Low Stock Alert</h3>
        <p style="margin: 10px 0 0 0;">
            <strong>Product:</strong> {product_name}<br>
            <strong>Current Stock:</strong> {current_stock} units<br>
            <strong>Reorder Point:</strong> {reorder_point} units
        </p>
    </div>
    
    <p>The product <strong>{product_name}</strong> is running low on stock. 
       Current stock ({current_stock} units) is below the reorder point ({reorder_point} units).</p>
    
    <p>Please consider reordering this product to avoid stockouts.</p>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="{shop_settings.shop_website}/admin/products" 
           style="background-color: #e74c3c; color: white; padding: 12px 30px; 
                  text-decoration: none; border-radius: 5px; display: inline-block;">
            Manage Products
        </a>
    </div>
    
    <p>Best regards,<br>
    {shop_settings.shop_name} Inventory System</p>
    """

    return send_email(admin_email, subject, content)
