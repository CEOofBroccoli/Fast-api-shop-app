from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi import Header
from sqlalchemy.orm import Session
from typing import Dict, List
from backend.app.database import get_db
from backend.app.models.sales_order import SalesOrder, SalesOrderItem, SalesOrderStatus
from backend.app.models.user import User
from backend.app.models.product import Product
from backend.app.auth.jwt_handler import verify_token
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.platypus.tableofcontents import TableOfContents
from io import BytesIO
import tempfile
import os

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/{sales_order_id}/generate")
async def generate_invoice(
    sales_order_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Generate and download invoice for a sales order."""
    # Verify token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    token = authorization.split(" ")[1]
    user_id = verify_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user"
        )
    
    # Get sales order with items
    sales_order = db.query(SalesOrder).filter(SalesOrder.id == sales_order_id).first()
    if not sales_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales order not found"
        )
    
    # Check permissions - users can only access their own orders unless they're staff/admin
    if user.role not in ["admin", "manager", "staff"] and getattr(sales_order, 'customer_id') != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this invoice"
        )
    
    # Only generate invoice for confirmed, shipped, or delivered orders
    order_status = getattr(sales_order, 'status')
    if order_status not in [SalesOrderStatus.CONFIRMED, SalesOrderStatus.SHIPPED, SalesOrderStatus.DELIVERED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice can only be generated for confirmed, shipped, or delivered orders"
        )
    
    # Get order items
    order_items = db.query(SalesOrderItem).filter(
        SalesOrderItem.sales_order_id == sales_order_id
    ).all()
    
    if not order_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No items found for this sales order"
        )
    
    # Get customer details
    customer = db.query(User).filter(User.id == getattr(sales_order, 'customer_id')).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer not found for this order"
        )
    
    # Generate PDF invoice
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Company header
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.darkblue,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("FastAPI Shop", title_style))
    story.append(Spacer(1, 12))
    
    # Invoice details
    invoice_style = ParagraphStyle(
        'InvoiceHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20
    )
    story.append(Paragraph(f"INVOICE #{sales_order.id:06d}", invoice_style))
    story.append(Spacer(1, 12))
    
    # Date and customer info
    info_data = [
        ["Invoice Date:", datetime.utcnow().strftime("%Y-%m-%d")],
        ["Order Date:", getattr(sales_order, 'created_at').strftime("%Y-%m-%d")],
        ["Order Status:", getattr(sales_order, 'status').value],
        ["", ""],
        ["Bill To:", ""],
        ["Customer Name:", f"{getattr(customer, 'first_name', '')} {getattr(customer, 'last_name', '')}"],
        ["Email:", getattr(customer, 'email', '')],
        ["Customer ID:", str(getattr(customer, 'id', ''))]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Items table
    item_data = [["Item", "Product Name", "Quantity", "Unit Price", "Total"]]
    
    subtotal = 0
    for i, item in enumerate(order_items, 1):
        product = db.query(Product).filter(Product.id == item.product_id).first()
        item_total = item.quantity * item.unit_price
        subtotal += item_total
        
        item_data.append([
            str(i),
            getattr(product, 'name', f"Product ID: {item.product_id}") if product else f"Product ID: {item.product_id}",
            str(item.quantity),
            f"${item.unit_price:.2f}",
            f"${item_total:.2f}"
        ])
    
    # Add totals
    tax_rate = 0.10  # 10% tax
    tax_amount = subtotal * tax_rate
    total_amount = subtotal + tax_amount
    
    item_data.extend([
        ["", "", "", "Subtotal:", f"${subtotal:.2f}"],
        ["", "", "", "Tax (10%):", f"${tax_amount:.2f}"],
        ["", "", "", "TOTAL:", f"${total_amount:.2f}"]
    ])
    
    items_table = Table(item_data, colWidths=[0.5*inch, 3*inch, 1*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -4), 10),
        ('GRID', (0, 0), (-1, -4), 1, colors.black),
        
        # Total rows
        ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -3), (-1, -1), 10),
        ('ALIGN', (3, -3), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        
        # Align product names to left
        ('ALIGN', (1, 1), (1, -4), 'LEFT'),
        # Align numbers to right
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 30))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("Thank you for your business!", footer_style))
    story.append(Paragraph("FastAPI Shop - Your trusted online store", footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Return PDF as response
    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{sales_order.id:06d}.pdf"
        }
    )


@router.get("/{sales_order_id}/receipt")
async def generate_receipt(
    sales_order_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Generate and download receipt for a sales order."""
    # Verify token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    token = authorization.split(" ")[1]
    user_id = verify_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user"
        )
    
    # Get sales order with items
    sales_order = db.query(SalesOrder).filter(SalesOrder.id == sales_order_id).first()
    if not sales_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales order not found"
        )
    
    # Check permissions
    if user.role not in ["admin", "manager", "staff"] and getattr(sales_order, 'customer_id') != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this receipt"
        )
    
    # Only generate receipt for delivered orders
    if getattr(sales_order, 'status') != SalesOrderStatus.DELIVERED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Receipt can only be generated for delivered orders"
        )
    
    # Get order items
    order_items = db.query(SalesOrderItem).filter(
        SalesOrderItem.sales_order_id == sales_order_id
    ).all()
    
    # Get customer details
    customer = db.query(User).filter(User.id == getattr(sales_order, 'customer_id')).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer not found for this order"
        )
    
    # Generate simple receipt PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Receipt header
    title_style = ParagraphStyle(
        'ReceiptTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20,
        alignment=1
    )
    story.append(Paragraph("RECEIPT", title_style))
    story.append(Spacer(1, 12))
    
    # Receipt details
    receipt_data = [
        ["Receipt #:", f"R{getattr(sales_order, 'id'):06d}"],
        ["Order #:", f"{getattr(sales_order, 'id'):06d}"],
        ["Date:", datetime.utcnow().strftime("%Y-%m-%d %H:%M")],
        ["Customer:", f"{getattr(customer, 'first_name', '')} {getattr(customer, 'last_name', '')}"],
        ["Email:", getattr(customer, 'email', '')]
    ]
    
    receipt_table = Table(receipt_data, colWidths=[1.5*inch, 3*inch])
    receipt_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(receipt_table)
    story.append(Spacer(1, 20))
    
    # Items
    item_data = [["Item", "Qty", "Price", "Total"]]
    
    subtotal = 0
    for item in order_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        item_total = item.quantity * item.unit_price
        subtotal += item_total
        
        item_data.append([
            getattr(product, 'name', f"Product ID: {item.product_id}") if product else f"Product ID: {item.product_id}",
            str(item.quantity),
            f"${item.unit_price:.2f}",
            f"${item_total:.2f}"
        ])
    
    # Add totals
    tax_amount = subtotal * 0.10
    total_amount = subtotal + tax_amount
    
    item_data.extend([
        ["", "", "Subtotal:", f"${subtotal:.2f}"],
        ["", "", "Tax:", f"${tax_amount:.2f}"],
        ["", "", "TOTAL:", f"${total_amount:.2f}"]
    ])
    
    items_table = Table(item_data, colWidths=[3*inch, 0.75*inch, 1*inch, 1*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -4), 1, colors.black),
        ('ALIGN', (0, 1), (0, -4), 'LEFT'),  # Product names left aligned
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Numbers right aligned
        ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 30))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=1
    )
    story.append(Paragraph("Thank you for your purchase!", footer_style))
    story.append(Paragraph("Items delivered on " + getattr(sales_order, 'updated_at').strftime("%Y-%m-%d"), footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Return PDF as response
    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=receipt_{getattr(sales_order, 'id'):06d}.pdf"
        }
    )
