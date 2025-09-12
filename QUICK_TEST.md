# Quick Start Testing Commands

## 1. Start the Server

**Option 1: Full Docker Stack (Recommended)**

```powershell
cd "c:\Users\SHIELD SYSTEM\OneDrive\Desktop\fastapi\Fast-api-shop-app"
docker-compose up -d
```

**Option 2: Development Mode (FastAPI only)**

```powershell
cd "c:\Users\SHIELD SYSTEM\OneDrive\Desktop\fastapi\Fast-api-shop-app"
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## 2. Access Swagger UI

**With Docker (Full Stack):** http://localhost:8000/docs
**Development Mode:** http://localhost:8000/docs

**Important:** Use the **port 8000** for Swagger UI access, not port 80.

## 3. Test Data Templates (Copy-Paste Ready)

### User Signup

```json
{
  "full_name": "Test Manager",
  "username": "testmanager",
  "email": "testmanager@example.com",
  "password": "SecurePass123!"
}
```

### Login Credentials

```
username: testmanager
password: SecurePass123!
```

### Product Creation (3 products)

```json
{
  "name": "Laptop Dell XPS 13",
  "sku": "DELL-XPS13-001",
  "description": "High-performance ultrabook",
  "price": 1299.99,
  "quantity": 10,
  "min_threshold": 2,
  "product_group": "Electronics"
}
```

```json
{
  "name": "Office Chair Premium",
  "sku": "CHAIR-PREM-001",
  "description": "Ergonomic office chair",
  "price": 299.99,
  "quantity": 1,
  "min_threshold": 3,
  "product_group": "Furniture"
}
```

```json
{
  "name": "Wireless Mouse",
  "sku": "MOUSE-WIRE-001",
  "description": "Bluetooth wireless mouse",
  "price": 49.99,
  "quantity": 50,
  "min_threshold": 10,
  "product_group": "Electronics"
}
```

### Supplier Creation

```json
{
  "name": "TechCorp Supplies",
  "contact_name": "John Smith",
  "email": "john@techcorp.com",
  "phone": "+1-555-0123",
  "address": "123 Tech Street, Silicon Valley",
  "delivery_lead_time_days": 7
}
```

### Purchase Order

```json
{
  "supplier_id": 1,
  "product_id": 1,
  "quantity": 5,
  "unit_cost": 1200.0,
  "expected_delivery_date": "2025-09-20"
}
```

### Sales Order

```json
{
  "customer_name": "ABC Company",
  "customer_email": "orders@abc.com",
  "customer_phone": "+1-555-9999",
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "unit_price": 1399.99
    },
    {
      "product_id": 3,
      "quantity": 5,
      "unit_price": 49.99
    }
  ]
}
```

### Stock Adjustment

```json
{
  "change": -2,
  "reason": "Sold to customer"
}
```

## 4. Key Testing URLs

- Health: http://localhost:8000/health
- Shop Info: http://localhost:8000/shop/info
- Dashboard: GET /dashboard/stats
- Low Stock: GET /report/low-stock
- Best Selling: GET /report/best-selling-products?days=30

## 5. Demo Sequence

1. Signup → Login → Get /users/me
2. Create 3 products → List with filters
3. Create supplier → Create purchase order
4. Create sales order → Confirm → Generate invoice
5. Show dashboard and reports
6. Demonstrate security (try without token)

## Remember:

- Click 🔒 "Authorize" in Swagger after login
- Use: `Bearer YOUR_ACCESS_TOKEN`
- Token expires in 30 minutes
- Save product/supplier IDs for later steps
