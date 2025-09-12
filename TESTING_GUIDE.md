# FastAPI Shop App - Complete Testing Guide for Swagger UI

## Pre-Testing Setup

### 1. Environment Setup

Before starting tests, ensure the following:

```powershell
# Navigate to project directory
cd "c:\Users\SHIELD SYSTEM\OneDrive\Desktop\fastapi\Fast-api-shop-app"

# Install dependencies (if not already done)
pip install -r backend/requirements.txt

# Start the FastAPI server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Access Swagger UI

- Open browser: `http://localhost:8000/docs`
- Verify all endpoints are visible
- Check that API documentation loads properly

---

## Phase 1: User Authentication & Registration

### Step 1.1: User Signup

**Endpoint:** `POST /signup`

**Test Data:**

```json
{
  "full_name": "Test Manager",
  "username": "testmanager",
  "email": "testmanager@example.com",
  "password": "SecurePass123!"
}
```

**Expected Results:**

- ✅ Status 200 with user object returned
- ✅ `is_verified: false` initially
- ✅ No `hashed_password` in response

**Test Variations:**

1. **Weak Password Test:**

   ```json
   { "username": "weak", "email": "weak@test.com", "password": "123" }
   ```

   Expected: ❌ 400 "Password must be at least 8 characters..."

2. **Duplicate Email Test:**
   Use same email as step 1
   Expected: ❌ 400 "Email already registered"

3. **Duplicate Username Test:**
   Use same username as step 1
   Expected: ❌ 400 "Username already taken"

### Step 1.2: Email Verification (Optional)

**Endpoint:** `POST /auth/send-verification-email`

```json
{ "email": "testmanager@example.com" }
```

**Note:** Email verification is implemented but requires SMTP setup. For testing purposes, you can manually set `is_verified=true` in database or skip this step.

### Step 1.3: User Login

**Endpoint:** `POST /login`

**Test Data:**

```
username: testmanager
password: SecurePass123!
```

**Expected Results:**

- ✅ Status 200 with access token
- ✅ `token_type: "bearer"`
- ✅ Token contains user info (uid, role, exp)

**Save the access_token for subsequent requests!**

### Step 1.4: Rate Limiting Test

**Endpoint:** `POST /login`

Attempt to login 6+ times rapidly with wrong password:

```
username: testmanager
password: wrongpassword
```

**Expected Results:**

- ✅ First 5 attempts: 401 Unauthorized
- ✅ 6th attempt: 429 Too Many Requests

### Step 1.5: Get Current User

**Endpoint:** `GET /users/me`

**Authorization:** Click 🔒 "Authorize" button, enter: `Bearer YOUR_ACCESS_TOKEN`

**Expected Results:**

- ✅ Status 200 with full user object
- ✅ Contains id, username, email, role, timestamps

---

## Phase 2: Product Management

### Step 2.1: Create Products

**Endpoint:** `POST /products/`

**Authorization Required:** Use token from login

**Test Data - Product 1:**

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

**Test Data - Product 2:**

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

**Test Data - Product 3:**

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

**Expected Results:**

- ✅ Status 200 for each product
- ✅ Unique SKU enforced
- ✅ Proper timestamps added

**Test Validation:**

1. **Duplicate SKU Test:**
   Try creating product with existing SKU
   Expected: ❌ 400 "SKU already exists"

2. **Negative Price Test:**
   ```json
   {
     "name": "Test",
     "sku": "TEST-001",
     "price": -10,
     "quantity": 5,
     "min_threshold": 1
   }
   ```
   Expected: ❌ 400 "Price cannot be negative"

### Step 2.2: List Products with Filters

**Endpoint:** `GET /products/`

**Test Cases:**

1. **Basic List:**
   No parameters
   Expected: ✅ Returns all 3 products

2. **Search by Name:**
   `search=Laptop`
   Expected: ✅ Returns Dell XPS 13 only

3. **Search by SKU:**
   `search=MOUSE-WIRE-001`
   Expected: ✅ Returns wireless mouse only

4. **Filter by Category:**
   `product_group=Electronics`
   Expected: ✅ Returns laptop and mouse

5. **Price Range Filter:**
   `min_price=200&max_price=1000`
   Expected: ✅ Returns office chair only

6. **Low Stock Filter:**
   `low_stock=true`
   Expected: ✅ Returns office chair (qty 1 < min_threshold 3)

7. **Sorting Tests:**

   - `sort_by=name_asc`: ✅ Laptop, Mouse, Office Chair
   - `sort_by=price_desc`: ✅ Laptop, Office Chair, Mouse

8. **Pagination:**
   `page=1&limit=2`
   Expected: ✅ Returns 2 products only

### Step 2.3: Get Single Product

**Endpoint:** `GET /products/{product_id}`

Use ID from any created product
Expected: ✅ Returns complete product details

### Step 2.4: Update Product

**Endpoint:** `PUT /products/{product_id}`

**Test Data:**

```json
{
  "name": "Laptop Dell XPS 13 - Updated",
  "sku": "DELL-XPS13-001",
  "description": "Updated description",
  "price": 1399.99,
  "quantity": 15,
  "min_threshold": 3,
  "product_group": "Electronics"
}
```

Expected: ✅ Status 200 with updated product

### Step 2.5: Stock Adjustment

**Endpoint:** `POST /products/{product_id}/adjust-stock`

**Test Data:**

```json
{
  "change": -2,
  "reason": "Sold to customer"
}
```

Expected: ✅ Quantity decreased by 2, logged in audit trail

### Step 2.6: Stock History

**Endpoint:** `GET /products/{product_id}/stock-history`

Expected: ✅ Returns list of stock changes with timestamps and reasons

---

## Phase 3: Supplier Management

### Step 3.1: Create Suppliers

**Endpoint:** `POST /suppliers/`

**Test Data - Supplier 1:**

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

**Test Data - Supplier 2:**

```json
{
  "name": "Office Solutions Inc",
  "contact_name": "Jane Doe",
  "email": "jane@officesolutions.com",
  "phone": "+1-555-0456",
  "address": "456 Business Ave, Commerce City",
  "delivery_lead_time_days": 14
}
```

Expected: ✅ Status 200 with supplier objects

### Step 3.2: List Suppliers

**Endpoint:** `GET /suppliers/`

Expected: ✅ Returns all suppliers with performance metrics

### Step 3.3: Get Supplier Details

**Endpoint:** `GET /suppliers/{supplier_id}`

Expected: ✅ Returns complete supplier information

---

## Phase 4: Purchase Orders

### Step 4.1: Create Purchase Orders

**Endpoint:** `POST /orders/`

**Test Data:**

```json
{
  "supplier_id": 1,
  "product_id": 1,
  "quantity": 5,
  "unit_cost": 1200.0,
  "expected_delivery_date": "2025-09-20"
}
```

Expected: ✅ Status 200, order created with "Draft" status

### Step 4.2: List Purchase Orders

**Endpoint:** `GET /orders/`

**Test with filters:**

- `status_filter=Draft`
- `page=1&limit=10`

Expected: ✅ Returns filtered results

### Step 4.3: Update Order Status

**Endpoint:** `PUT /orders/{order_id}/status`

**Test Data:**

```json
{
  "status": "Received",
  "actual_delivery_date": "2025-09-18"
}
```

Expected: ✅ Status updated, inventory increased by order quantity

---

## Phase 5: Sales Orders

### Step 5.1: Create Sales Order

**Endpoint:** `POST /sales-orders/`

**Test Data:**

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

Expected: ✅ Order created, inventory reserved

### Step 5.2: Confirm Sales Order

**Endpoint:** `PUT /sales-orders/{order_id}/confirm`

Expected: ✅ Status changed to "Confirmed", inventory decremented

### Step 5.3: List Sales Orders

**Endpoint:** `GET /sales-orders/`

Expected: ✅ Returns all sales orders with items

---

## Phase 6: Reports & Analytics

### Step 6.1: Low Stock Report

**Endpoint:** `GET /report/low-stock`

Expected: ✅ Returns products below minimum threshold

### Step 6.2: Best Selling Products

**Endpoint:** `GET /report/best-selling-products?days=30`

Expected: ✅ Returns products ranked by sales volume

### Step 6.3: Supplier Ratings

**Endpoint:** `GET /report/supplier-ratings`

Expected: ✅ Returns suppliers with performance metrics

### Step 6.4: Dashboard Stats

**Endpoint:** `GET /dashboard/stats`

Expected: ✅ Returns comprehensive business metrics:

- Total counts (products, orders, suppliers)
- Low stock count
- Recent orders
- Top selling products
- Financial aggregates

---

## Phase 7: Invoice Generation

### Step 7.1: Generate Invoice

**Endpoint:** `GET /invoices/{sales_order_id}/pdf`

Expected: ✅ PDF file download with professional invoice

---

## Phase 8: Security & Error Testing

### Step 8.1: Unauthorized Access Test

Remove authorization header and try:

- `GET /products/`
  Expected: ❌ 401 Unauthorized

### Step 8.2: Insufficient Permissions Test

Create a regular user (role="user") and try:

- `DELETE /products/{id}`
  Expected: ❌ 403 Forbidden

### Step 8.3: Invalid Token Test

Use malformed token: `Bearer invalid_token_here`
Expected: ❌ 401 Unauthorized

### Step 8.4: Rate Limiting

Rapidly call signup endpoint 4+ times:
Expected: ❌ 429 Too Many Requests

---

## Phase 9: Health & System Endpoints

### Step 9.1: Health Check

**Endpoint:** `GET /health`

Expected: ✅ System status with database and Redis status

### Step 9.2: API Root

**Endpoint:** `GET /`

Expected: ✅ Welcome message with endpoint navigation

### Step 9.3: Shop Info

**Endpoint:** `GET /shop/info`

Expected: ✅ Public shop information and branding

---

## Presentation Checklist

Before presenting, verify:

- [ ] All endpoints return expected status codes
- [ ] Authentication flow works completely
- [ ] Product CRUD with all filters/sorting works
- [ ] Purchase and sales order workflows complete
- [ ] Reports generate meaningful data
- [ ] PDF invoice downloads successfully
- [ ] Error handling is graceful
- [ ] Rate limiting prevents abuse
- [ ] Role-based access control enforced
- [ ] No 500 errors or unexpected crashes

## Demo Flow Recommendation

1. **Start with authentication:** Signup → Login → Get user info
2. **Show product management:** Create → List with filters → Update → Stock adjust
3. **Demo supplier workflow:** Create supplier → Create purchase order → Receive order
4. **Show sales process:** Create sales order → Confirm → Generate invoice
5. **Display analytics:** Dashboard → Reports → Low stock alerts
6. **Demonstrate security:** Show role restrictions and rate limiting

## Troubleshooting Notes

- If database errors occur, ensure SQLite/PostgreSQL is accessible
- If Redis errors appear, reports/caching may be degraded but core functionality works
- Rate limiting may interfere with rapid testing - wait 60 seconds if blocked
- Token expires in 30 minutes - re-login if getting 401 errors
- Ensure proper `Content-Type: application/json` for POST/PUT requests

This comprehensive guide ensures you can confidently demonstrate every feature during your presentation!
