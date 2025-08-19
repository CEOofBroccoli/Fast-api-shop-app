import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import get_db, Base, engine
import logging
from sqlalchemy import text
from backend.app.models.order import InvoiceStatus

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
    logger.info("Test database tables created for order tests")
    yield
    # Clean up after test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def authenticated_client():
    """Create a test user and return an authenticated client"""
    # Create a test user
    signup_response = client.post("/signup", json={
        "username": "orderuser",
        "email": "orderuser@example.com",
        "password": "TestPassword123!"
    })
    assert signup_response.status_code == 200
    
    # Verify the user directly in the database
    from sqlalchemy.orm import Session
    from backend.app.database import session_maker
    from backend.app.models.user import User
    
    db = session_maker()
    try:
        db.execute(text("UPDATE users SET is_verified = 1 WHERE username = 'orderuser'"))
        db.commit()
    finally:
        db.close()
    
    # Log in the user
    login_response = client.post(
        "/login",
        data={"username": "orderuser", "password": "TestPassword123!"}
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    
    # Create a client with the token in the header
    auth_client = TestClient(app)
    auth_client.headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    
    return auth_client

@pytest.fixture(scope="function")
def test_product(authenticated_client):
    """Create a test product for orders"""
    product_data = {
        "name": "Order Test Product",
        "sku": "ORDER-TEST-123",
        "description": "Test product for orders",
        "price": 29.99,
        "quantity": 100,
        "min_threshold": 10,
        "product_group": "Test Group"
    }
    
    response = authenticated_client.post("/products/", json=product_data)
    assert response.status_code == 200
    return response.json()

def test_create_order(authenticated_client, test_product):
    """Test creating a new order"""
    order_data = {
        "product_id": test_product["id"],
        "quantity": 5,
        "status": "Draft"
    }
    
    response = authenticated_client.post("/orders/", json=order_data)
    assert response.status_code == 201
    created_order = response.json()
    assert created_order["product_id"] == test_product["id"]
    assert created_order["quantity"] == 5
    assert created_order["status"] == "Draft"

def test_list_orders(authenticated_client, test_product):
    """Test listing all orders"""
    # Create multiple orders
    for i in range(3):
        order_data = {
            "product_id": test_product["id"],
            "quantity": i + 1,
            "status": "Draft"
        }
        response = authenticated_client.post("/orders/", json=order_data)
        assert response.status_code == 201
    
    # List all orders
    response = authenticated_client.get("/orders/")
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) >= 3

def test_update_order(authenticated_client, test_product):
    """Test updating an order"""
    # Create an order
    order_data = {
        "product_id": test_product["id"],
        "quantity": 3,
        "status": "Draft"
    }
    
    response = authenticated_client.post("/orders/", json=order_data)
    assert response.status_code == 201
    created_order = response.json()
    
    # Update the order
    update_data = {
        "status": "Sent",
        "quantity": 5
    }
    
    response = authenticated_client.put(f"/orders/{created_order['id']}", json=update_data)
    assert response.status_code == 200
    updated_order = response.json()
    assert updated_order["id"] == created_order["id"]
    assert updated_order["status"] == "Sent"
    assert updated_order["quantity"] == 5

def test_delete_order(authenticated_client, test_product):
    """Test deleting an order"""
    # Create an order
    order_data = {
        "product_id": test_product["id"],
        "quantity": 2,
        "status": "Draft"
    }
    
    response = authenticated_client.post("/orders/", json=order_data)
    assert response.status_code == 201
    created_order = response.json()
    
    # Delete the order
    response = authenticated_client.delete(f"/orders/{created_order['id']}")
    assert response.status_code == 204
    
    # Verify the order is deleted
    response = authenticated_client.get(f"/orders/{created_order['id']}")
    assert response.status_code == 404

def test_filter_orders_by_status(authenticated_client, test_product):
    """Test filtering orders by status"""
    # Create orders with different statuses
    statuses = ["Draft", "Sent", "Received"]
    for status in statuses:
        order_data = {
            "product_id": test_product["id"],
            "quantity": 1,
            "status": status
        }
        response = authenticated_client.post("/orders/", json=order_data)
        assert response.status_code == 201
    
    # Filter orders by status
    for status in statuses:
        response = authenticated_client.get(f"/orders/?status_filter={status}")
        assert response.status_code == 200
        orders = response.json()
        assert all(order["status"] == status for order in orders)
