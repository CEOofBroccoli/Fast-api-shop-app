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

**Important:**

- Use **port 8000** for Swagger UI access, not port 80
- If you see a white page, restart the app container: `docker-compose restart app`
- The Swagger UI loads external resources from CDN - this is normal and secure

**🔓 TESTING MODE: Authentication is DISABLED for all endpoints!**

- You can test all API endpoints without needing to login or provide authorization headers
- All endpoints will automatically use a test admin user
- This is for presentation/testing purposes only

## 🔑 How to Sign In as Admin (Optional - for Demo Purposes)

**Method 1: Get Admin Token via Login**

1. **Login**: POST `/login` with username: `testmanager`, password: `SecurePass123!`
2. **Copy access_token** from response (looks like: `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...`)
3. **Click 🔒 Authorize** button in Swagger UI
4. **Enter**: `Bearer YOUR_ACCESS_TOKEN` (replace YOUR_ACCESS_TOKEN with the actual token)
5. **Click Authorize** - now all requests will include the admin token

**Method 2: Direct Authorization Header (for individual requests)**

- In any endpoint that has "authorization" parameter
- Enter: `Bearer YOUR_ACCESS_TOKEN` (get token from login first)

**Method 3: No Auth Needed (Current Testing Mode)**

- Just test endpoints directly - they automatically use admin privileges

**For /signup endpoint:**

1. Click on "POST /signup"
2. Click "Try it out"
3. You should see a JSON input box where you can paste the User Signup data below
4. If you see args/kwargs instead, restart the container: `docker-compose restart app`

**For /login endpoint:**

1. Click on "POST /login"
2. Click "Try it out"
3. You'll see OAuth2 form fields - only fill these:
   - **grant_type:** Leave as "password"
   - **username:** Enter "testmanager" OR "testmanager@example.com"
   - **password:** Enter "SecurePass123!"
   - **client_id, client_secret, scope:** Leave empty (not required)

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

**Option 1: Login with username**

```
username: testmanager
password: SecurePass123!
```

**Option 2: Login with email (put email in username field)**

```
username: testmanager@example.com
password: SecurePass123!
```

**Important:** In Swagger UI's login form, you can enter either your username OR email in the "username" field. Leave client_id, client_secret, and scope empty - they're optional OAuth2 fields not needed for this API.

**Note:** Email verification is disabled for testing purposes, so you can login immediately after signup without needing to verify your email.

### Product Creation (Create ONE at a time)

**❗ Important: Create each product separately using POST /products**

**Product 1: Laptop**

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

**Product 2: Office Chair**

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

**Product 3: Wireless Mouse**

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

**Note: If you get 401 Unauthorized error, restart the container:**

```powershell
docker-compose restart app
```

### Purchase Order

**❗ Note: Make sure you created a supplier first (supplier_id: 1) and a product (product_id: 1)**

```json
{
  "supplier_id": 1,
  "product_id": 1,
  "quantity": 5,
  "unit_cost": 1200.0,
  "expected_delivery_date": "2025-09-20"
}
```

**✅ FINAL FIX: Both authorization AND role checks removed! No restrictions at all!**

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

## 5. Demo Sequence (NO AUTHENTICATION REQUIRED!)

**Step-by-Step Product Creation:**

1. ✅ **Create Product 1**: POST `/products` with Laptop JSON → Note the product_id in response
2. ✅ **Create Product 2**: POST `/products` with Chair JSON → Note the product_id in response
3. ✅ **Create Product 3**: POST `/products` with Mouse JSON → Note the product_id in response
4. ✅ **List Products**: GET `/products` to see all created products
5. ✅ **Create Supplier**: POST `/suppliers` with supplier JSON
6. ✅ **Create Purchase Order**: POST `/orders` (use product_id from step 1)
7. ✅ **Create Sales Order**: POST `/sales-orders` (use product_ids from steps 1 & 3)
8. ✅ **Show Dashboard**: GET `/dashboard/stats`
9. ✅ **Show Reports**: GET `/report/low-stock` and `/report/best-selling-products`

**Common 422 Error Fixes:**

- ❌ Don't try to create multiple products in one request
- ✅ Create each product individually
- ✅ Make sure each SKU is unique
- ✅ Ensure all required fields are filled
- ✅ Check that price and quantity are positive numbers

## Remember:

- � **Authentication is DISABLED** - no need for tokens or login!
- You can test ALL endpoints directly without authorization
- This is for TESTING/PRESENTATION only
- All requests automatically use admin privileges
- No need to click 🔒 "Authorize" in Swagger
