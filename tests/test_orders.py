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
def admin_client():
    """Create an admin user and return an authenticated client for creating suppliers"""
    # Create an admin user
    signup_response = client.post("/signup", json={
        "username": "adminuser",
        "email": "adminuser@example.com", 
        "password": "TestPassword123!"
    })
    assert signup_response.status_code == 200
    
    # Verify and set admin role
    from sqlalchemy.orm import Session
    from backend.app.database import session_maker
    from backend.app.models.user import User
    
    db = session_maker()
    try:
        db.execute(text("UPDATE users SET is_verified = 1, role = 'admin' WHERE username = 'adminuser'"))
        db.commit()
    finally:
        db.close()
    
    # Log in the admin user
    login_response = client.post(
        "/login",
        data={"username": "adminuser", "password": "TestPassword123!"}
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    
    # Create a client with the admin token
    admin_auth_client = TestClient(app)
    admin_auth_client.headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    
    return admin_auth_client

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
        db.execute(text("UPDATE users SET is_verified = 1, role = 'buyer' WHERE username = 'orderuser'"))
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
def test_supplier(admin_client):
    """Create a test supplier for orders using admin privileges"""
    supplier_data = {
        "name": "Test Supplier Corp",
        "contact_person": "John Supplier",
        "email": "john@testsupplier.com",
        "phone": "+1-555-0123",
        "address": "123 Supplier St, Supply City, SC 12345",
        "delivery_lead_time_days": 5
    }
    
    response = admin_client.post("/suppliers/", json=supplier_data)
    assert response.status_code == 201
    return response.json()

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

def test_create_order(authenticated_client, test_product, test_supplier):
    """Test creating a new order"""
    order_data = {
        "supplier_id": test_supplier["id"],
        "product_id": test_product["id"],
        "quantity": 5,
        "unit_cost": 25.50,
        "notes": "Test order creation"
    }
    
    response = authenticated_client.post("/orders/", json=order_data)
    assert response.status_code == 201
    created_order = response.json()
    assert created_order["supplier_id"] == test_supplier["id"]
    assert created_order["product_id"] == test_product["id"]
    assert created_order["quantity"] == 5
    assert created_order["unit_cost"] == 25.50
    assert created_order["status"] == "Draft"

def test_list_orders(authenticated_client, test_product, test_supplier):
    """Test listing all orders"""
    # Create multiple orders
    for i in range(3):
        order_data = {
            "supplier_id": test_supplier["id"],
            "product_id": test_product["id"],
            "quantity": i + 1,
            "unit_cost": 20.00 + i * 5.00,
            "notes": f"Test order {i+1}"
        }
        response = authenticated_client.post("/orders/", json=order_data)
        assert response.status_code == 201
    
    # List all orders
    response = authenticated_client.get("/orders/")
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) >= 3

def test_update_order(authenticated_client, test_product, test_supplier):
    """Test updating an order"""
    # Create an order
    order_data = {
        "supplier_id": test_supplier["id"],
        "product_id": test_product["id"],
        "quantity": 3,
        "unit_cost": 30.00,
        "notes": "Initial order"
    }
    
    response = authenticated_client.post("/orders/", json=order_data)
    assert response.status_code == 201
    created_order = response.json()
    
    # Update the order
    update_data = {
        "status": "Sent",
        "notes": "Updated order notes"
    }
    
    response = authenticated_client.put(f"/orders/{created_order['id']}", json=update_data)
    assert response.status_code == 200
    updated_order = response.json()
    assert updated_order["id"] == created_order["id"]
    assert updated_order["status"] == "Sent"
    assert updated_order["notes"] == "Updated order notes"

def test_delete_order(authenticated_client, test_product, test_supplier):
    """Test deleting an order"""
    # Create an order
    order_data = {
        "supplier_id": test_supplier["id"],
        "product_id": test_product["id"],
        "quantity": 2,
        "unit_cost": 15.75,
        "notes": "Order to be deleted"
    }
    
    response = authenticated_client.post("/orders/", json=order_data)
    assert response.status_code == 201
    created_order = response.json()
    
    # Delete the order
    response = authenticated_client.delete(f"/orders/{created_order['id']}")
    assert response.status_code == 204

    # Verify the order is deleted by listing all orders
    response = authenticated_client.get("/orders/")
    assert response.status_code == 200
    orders = response.json()
    
    # Check that the deleted order is not in the list
    order_ids = [order["id"] for order in orders]
    assert created_order["id"] not in order_ids


def test_filter_orders_by_status(authenticated_client, test_product, test_supplier):
    """Test filtering orders by status"""
    # Create orders and update them to different statuses following the allowed transitions
    order_ids = []

    # Create 3 base orders (all start as Draft)
    for i in range(3):
        order_data = {
            "supplier_id": test_supplier["id"],
            "product_id": test_product["id"],
            "quantity": 1,
            "unit_cost": 10.00 + i * 5.00,
            "notes": f"Test order {i+1}"
        }
        response = authenticated_client.post("/orders/", json=order_data)
        assert response.status_code == 201
        order_ids.append(response.json()["id"])

    # Order 1: Keep as Draft (no update needed)
    # Order 2: Draft → Sent
    update_data = {"status": "Sent"}
    response = authenticated_client.put(f"/orders/{order_ids[1]}", json=update_data)
    assert response.status_code == 200

    # Order 3: Draft → Sent → Received (requires two updates)
    update_data = {"status": "Sent"}
    response = authenticated_client.put(f"/orders/{order_ids[2]}", json=update_data)
    assert response.status_code == 200
    
    update_data = {"status": "Received"}
    response = authenticated_client.put(f"/orders/{order_ids[2]}", json=update_data)
    assert response.status_code == 200

    # Now test filtering by status
    # Filter for Draft orders
    response = authenticated_client.get("/orders/?status_filter=Draft")
    assert response.status_code == 200
    draft_orders = response.json()
    assert len(draft_orders) == 1
    assert draft_orders[0]["id"] == order_ids[0]

    # Filter for Sent orders  
    response = authenticated_client.get("/orders/?status_filter=Sent")
    assert response.status_code == 200
    sent_orders = response.json()
    assert len(sent_orders) == 1
    assert sent_orders[0]["id"] == order_ids[1]

    # Filter for Received orders
    response = authenticated_client.get("/orders/?status_filter=Received")
    assert response.status_code == 200
    received_orders = response.json()
    assert len(received_orders) == 1
    assert received_orders[0]["id"] == order_ids[2]
