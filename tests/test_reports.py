import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import get_db, Base, engine
import logging
from sqlalchemy import text

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Setup test client
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    # Drop all tables first to ensure a clean state
    Base.metadata.drop_all(bind=engine)
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Test database tables created for report tests")
    yield
    # Clean up after test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def authenticated_client():
    """Create a test admin user and return an authenticated client for reports"""
    # Create an admin user for accessing reports
    signup_response = client.post("/signup", json={
        "username": "reportuser",
        "email": "reportuser@example.com",
        "password": "TestPassword123!"
    })
    assert signup_response.status_code == 200
    
    # Verify the user directly in the database
    from sqlalchemy.orm import Session
    from backend.app.database import session_maker
    from backend.app.models.user import User
    
    db = session_maker()
    try:
        # Make user an admin to access reports
        db.execute(text("UPDATE users SET is_verified = 1, role = 'admin' WHERE username = 'reportuser'"))
        db.commit()
    finally:
        db.close()
    
    # Log in the user
    login_response = client.post(
        "/login",
        data={"username": "reportuser", "password": "TestPassword123!"}
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    
    # Create a client with the token in the header
    auth_client = TestClient(app)
    auth_client.headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    
    return auth_client

@pytest.fixture(scope="function")
def buyer_client():
    """Create a test buyer user and return an authenticated client for order creation"""
    # Create a buyer user for creating orders
    signup_response = client.post("/signup", json={
        "username": "buyeruser",
        "email": "buyeruser@example.com",
        "password": "TestPassword123!"
    })
    assert signup_response.status_code == 200
    
    # Verify the user directly in the database
    from sqlalchemy.orm import Session
    from backend.app.database import session_maker
    from backend.app.models.user import User
    
    db = session_maker()
    try:
        # Make user a buyer to create orders
        db.execute(text("UPDATE users SET is_verified = 1, role = 'buyer' WHERE username = 'buyeruser'"))
        db.commit()
    finally:
        db.close()
    
    # Log in the buyer user
    login_response = client.post(
        "/login",
        data={"username": "buyeruser", "password": "TestPassword123!"}
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    
    # Create a client with the buyer token
    buyer_auth_client = TestClient(app)
    buyer_auth_client.headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    
    return buyer_auth_client

@pytest.fixture(scope="function")
def test_supplier(authenticated_client):
    """Create a test supplier for reports"""
    supplier_data = {
        "name": "Report Test Supplier",
        "contact_person": "Jane Supplier",
        "email": "jane@reportsupplier.com",
        "phone": "+1-555-0456",
        "address": "456 Report Ave, Data City, DC 67890",
        "delivery_lead_time_days": 7
    }
    
    response = authenticated_client.post("/suppliers/", json=supplier_data)
    assert response.status_code == 201
    return response.json()

@pytest.fixture(scope="function")
def setup_test_data(authenticated_client, buyer_client, test_supplier):
    """Create test products for reports without any order interactions"""
    # Create products with different stock levels using admin client
    products = []
    
    # Product below threshold
    low_stock_product = {
        "name": "Low Stock Item",
        "sku": "LOW-STOCK-123",
        "description": "Low stock test product",
        "price": 19.99,
        "quantity": 2,  # Below threshold
        "min_threshold": 10,
        "product_group": "Test Group"
    }
    response = authenticated_client.post("/products/", json=low_stock_product)
    assert response.status_code == 200
    products.append(response.json())
    
    # Product with normal stock
    normal_stock_product = {
        "name": "Normal Stock Item",
        "sku": "NORMAL-STOCK-123",
        "description": "Normal stock test product",
        "price": 29.99,
        "quantity": 100,  # Well above threshold
        "min_threshold": 5,
        "product_group": "Test Group"
    }
    response = authenticated_client.post("/products/", json=normal_stock_product)
    assert response.status_code == 200
    products.append(response.json())
    
    # Don't create any orders to avoid inventory changes
    return {"products": products, "orders": []}


@pytest.fixture(scope="function")
def setup_test_data_with_orders(authenticated_client, buyer_client, test_supplier):
    """Create test products and orders for reports that need order data"""
    # Create products with different stock levels using admin client
    products = []
    
    # Product below threshold
    low_stock_product = {
        "name": "Low Stock Item",
        "sku": "LOW-STOCK-123",
        "description": "Low stock test product",
        "price": 19.99,
        "quantity": 20,  # Start with more to allow for order consumption
        "min_threshold": 10,
        "product_group": "Test Group"
    }
    response = authenticated_client.post("/products/", json=low_stock_product)
    assert response.status_code == 200
    products.append(response.json())
    
    # Product with normal stock
    normal_stock_product = {
        "name": "Normal Stock Item",
        "sku": "NORMAL-STOCK-123",
        "description": "Normal stock test product",
        "price": 29.99,
        "quantity": 100,  # Well above threshold
        "min_threshold": 5,
        "product_group": "Test Group"
    }
    response = authenticated_client.post("/products/", json=normal_stock_product)
    assert response.status_code == 200
    products.append(response.json())
    
    # Create orders with different statuses using buyer client
    orders = []
    statuses = ["Draft", "Sent", "Received", "Closed", "Draft"]  # Extra Draft to test counting
    
    for i, status in enumerate(statuses):
        # Create order with required fields using buyer client
        order_data = {
            "supplier_id": test_supplier["id"],
            "product_id": products[i % len(products)]["id"],
            "quantity": i + 1,
            "unit_cost": 15.00 + i * 2.50,
            "notes": f"Report test order {i+1}"
        }
        response = buyer_client.post("/orders/", json=order_data)
        assert response.status_code == 201
        
        # Update status if not Draft (which is default) - follow proper transitions
        order_id = response.json()["id"]
        if status == "Sent":
            update_data = {"status": "Sent"}
            update_response = buyer_client.put(f"/orders/{order_id}", json=update_data)
            assert update_response.status_code == 200
            orders.append(update_response.json())
        elif status == "Received":
            # Draft -> Sent -> Received
            update_data = {"status": "Sent"}
            update_response = buyer_client.put(f"/orders/{order_id}", json=update_data)
            assert update_response.status_code == 200
            update_data = {"status": "Received"}
            update_response = buyer_client.put(f"/orders/{order_id}", json=update_data)
            assert update_response.status_code == 200
            orders.append(update_response.json())
        elif status == "Closed":
            # Draft -> Sent -> Received -> Closed
            update_data = {"status": "Sent"}
            update_response = buyer_client.put(f"/orders/{order_id}", json=update_data)
            assert update_response.status_code == 200
            update_data = {"status": "Received"}
            update_response = buyer_client.put(f"/orders/{order_id}", json=update_data)
            assert update_response.status_code == 200
            update_data = {"status": "Closed"}
            update_response = buyer_client.put(f"/orders/{order_id}", json=update_data)
            assert update_response.status_code == 200
            orders.append(update_response.json())
        else:  # Draft
            orders.append(response.json())
    
    return {"products": products, "orders": orders}

def test_low_stock_report(authenticated_client, setup_test_data):
    """Test the low stock report endpoint"""
    response = authenticated_client.get("/report/low-stock")
    assert response.status_code == 200
    low_stock_items = response.json()

    # We should have at least one low stock item
    assert len(low_stock_items) >= 1

    # Verify the low stock item is in the report
    assert any(item["sku"] == "LOW-STOCK-123" for item in low_stock_items)

    # The normal stock item should not be in the report
    assert not any(item["sku"] == "NORMAL-STOCK-123" for item in low_stock_items)


def test_order_status_report(authenticated_client, setup_test_data_with_orders):
    """Test the order status report endpoint"""
    response = authenticated_client.get("/report/order-status")
    assert response.status_code == 200
    status_counts = response.json()
    
    # Check that we have entries for all statuses
    assert "Draft" in status_counts
    assert status_counts["Draft"] == 2  # We created 2 Draft orders
    
    assert "Sent" in status_counts
    assert status_counts["Sent"] == 1
    
    assert "Received" in status_counts
    assert status_counts["Received"] == 1
    
    assert "Closed" in status_counts
    assert status_counts["Closed"] == 1

def test_inventory_value_report(authenticated_client, setup_test_data):
    """Test the inventory value report endpoint"""
    response = authenticated_client.get("/report/inventory-value")
    assert response.status_code == 200
    inventory_value = response.json()
    
    # Verify the inventory value includes product groups
    assert "Test Group" in inventory_value
    
    # Calculate expected value manually
    products = setup_test_data["products"]
    expected_value = 0
    for product in products:
        if product["product_group"] == "Test Group":
            expected_value += product["price"] * product["quantity"]
    
    # Compare with reported value
    assert abs(inventory_value["Test Group"] - expected_value) < 0.01  # Allow for small float differences

def test_order_history_for_product(authenticated_client, setup_test_data_with_orders):
    """Test retrieving order history for a specific product"""
    # Get the first product
    product_id = setup_test_data_with_orders["products"][0]["id"]
    
    response = authenticated_client.get(f"/report/order-history/{product_id}")
    assert response.status_code == 200
    order_history = response.json()
    
    # There should be at least some orders for this product
    assert len(order_history) >= 1
    
    # All orders should be for the specified product
    assert all(order["product_id"] == product_id for order in order_history)
