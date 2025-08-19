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
    """Create a test user and return an authenticated client"""
    # Create a test user
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
def setup_test_data(authenticated_client):
    """Create test products and orders for reports"""
    # Create products with different stock levels
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
        "quantity": 50,  # Above threshold
        "min_threshold": 10,
        "product_group": "Test Group"
    }
    response = authenticated_client.post("/products/", json=normal_stock_product)
    assert response.status_code == 200
    products.append(response.json())
    
    # Create orders with different statuses
    orders = []
    statuses = ["Draft", "Sent", "Received", "Closed", "Draft"]  # Extra Draft to test counting
    
    for i, status in enumerate(statuses):
        order_data = {
            "product_id": products[i % len(products)]["id"],
            "quantity": i + 1,
            "status": status
        }
        response = authenticated_client.post("/orders/", json=order_data)
        assert response.status_code == 201
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

def test_order_status_report(authenticated_client, setup_test_data):
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

def test_order_history_for_product(authenticated_client, setup_test_data):
    """Test retrieving order history for a specific product"""
    # Get the first product
    product_id = setup_test_data["products"][0]["id"]
    
    response = authenticated_client.get(f"/report/order-history/{product_id}")
    assert response.status_code == 200
    order_history = response.json()
    
    # There should be at least some orders for this product
    assert len(order_history) >= 1
    
    # All orders should be for the specified product
    assert all(order["product_id"] == product_id for order in order_history)
