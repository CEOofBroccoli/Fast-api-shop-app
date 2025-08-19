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
    logger.info("Test database tables created for product tests")
    yield
    # Clean up after test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def authenticated_client():
    """Create a test user and return an authenticated client"""
    # Create a test user
    signup_response = client.post("/signup", json={
        "username": "productuser",
        "email": "productuser@example.com",
        "password": "TestPassword123!"
    })
    assert signup_response.status_code == 200
    
    # Verify the user directly in the database
    from sqlalchemy.orm import Session
    from backend.app.database import session_maker
    from backend.app.models.user import User
    
    db = session_maker()
    try:
        db.execute(text("UPDATE users SET is_verified = 1, role = 'manager' WHERE username = 'productuser'"))
        db.commit()
    finally:
        db.close()
    
    # Log in the user
    login_response = client.post(
        "/login",
        data={"username": "productuser", "password": "TestPassword123!"}
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    
    # Create a client with the token in the header
    auth_client = TestClient(app)
    auth_client.headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    
    return auth_client

def test_create_and_list_products(authenticated_client):
    """Test creating a product and then listing all products"""
    # Create a product
    product_data = {
        "name": "Test Product",
        "sku": "TEST-123",
        "description": "Test description",
        "price": 19.99,
        "quantity": 100,
        "min_threshold": 10,
        "product_group": "Test Group"
    }
    
    response = authenticated_client.post("/products/", json=product_data)
    assert response.status_code == 200
    created_product = response.json()
    assert created_product["name"] == product_data["name"]
    assert created_product["sku"] == product_data["sku"]
    
    # List all products
    response = authenticated_client.get("/products/")
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 1
    assert any(p["sku"] == "TEST-123" for p in products)

def test_get_product_by_id(authenticated_client):
    """Test retrieving a product by ID"""
    # Create a product
    product_data = {
        "name": "Get By ID Product",
        "sku": "GET-ID-123",
        "description": "Test get by ID",
        "price": 29.99,
        "quantity": 50,
        "min_threshold": 5,
        "product_group": "Test Group"
    }
    
    response = authenticated_client.post("/products/", json=product_data)
    assert response.status_code == 200
    created_product = response.json()
    product_id = created_product["id"]
    
    # Get the product by ID
    response = authenticated_client.get(f"/products/{product_id}")
    assert response.status_code == 200
    retrieved_product = response.json()
    assert retrieved_product["id"] == product_id
    assert retrieved_product["name"] == product_data["name"]

def test_update_product(authenticated_client):
    """Test updating a product"""
    # Create a product
    product_data = {
        "name": "Update Product",
        "sku": "UPDATE-123",
        "description": "Before update",
        "price": 39.99,
        "quantity": 30,
        "min_threshold": 5,
        "product_group": "Test Group"
    }
    
    response = authenticated_client.post("/products/", json=product_data)
    assert response.status_code == 200
    created_product = response.json()
    product_id = created_product["id"]
    
    # Update the product
    updated_data = {
        "name": "Updated Product",
        "sku": "UPDATE-123",  # Keeping the same SKU
        "description": "After update",
        "price": 49.99,
        "quantity": 40,
        "min_threshold": 8,
        "product_group": "Updated Group"
    }
    
    response = authenticated_client.put(f"/products/{product_id}", json=updated_data)
    assert response.status_code == 200
    updated_product = response.json()
    assert updated_product["id"] == product_id
    assert updated_product["name"] == updated_data["name"]
    assert updated_product["price"] == updated_data["price"]

def test_delete_product(authenticated_client):
    """Test deleting a product"""
    # Create a product
    product_data = {
        "name": "Delete Product",
        "sku": "DELETE-123",
        "description": "To be deleted",
        "price": 59.99,
        "quantity": 20,
        "min_threshold": 5,
        "product_group": "Test Group"
    }
    
    response = authenticated_client.post("/products/", json=product_data)
    assert response.status_code == 200
    created_product = response.json()
    product_id = created_product["id"]
    
    # Delete the product
    response = authenticated_client.delete(f"/products/{product_id}")
    assert response.status_code == 204
    
    # Verify the product is deleted
    response = authenticated_client.get(f"/products/{product_id}")
    assert response.status_code == 404

def test_adjust_stock(authenticated_client):
    """Test adjusting product stock"""
    # Create a product
    product_data = {
        "name": "Stock Adjustment Product",
        "sku": "STOCK-123",
        "description": "Test stock adjustment",
        "price": 69.99,
        "quantity": 50,
        "min_threshold": 10,
        "product_group": "Test Group"
    }
    
    response = authenticated_client.post("/products/", json=product_data)
    assert response.status_code == 200
    created_product = response.json()
    product_id = created_product["id"]
    initial_quantity = created_product["quantity"]
    
    # Adjust stock (add 10 units)
    adjustment_data = {
        "change": 10,
        "reason": "Received new inventory"
    }
    
    response = authenticated_client.post(f"/products/{product_id}/adjust-stock", json=adjustment_data)
    assert response.status_code == 200
    updated_product = response.json()
    assert updated_product["quantity"] == initial_quantity + 10
    
    # Adjust stock (remove 5 units)
    adjustment_data = {
        "change": -5,
        "reason": "Damaged items"
    }
    
    response = authenticated_client.post(f"/products/{product_id}/adjust-stock", json=adjustment_data)
    assert response.status_code == 200
    updated_product = response.json()
    assert updated_product["quantity"] == initial_quantity + 10 - 5

def test_stock_history(authenticated_client):
    """Test retrieving stock history for a product"""
    # Create a product
    product_data = {
        "name": "History Product",
        "sku": "HISTORY-123",
        "description": "Test stock history",
        "price": 79.99,
        "quantity": 100,
        "min_threshold": 15,
        "product_group": "Test Group"
    }
    
    response = authenticated_client.post("/products/", json=product_data)
    assert response.status_code == 200
    created_product = response.json()
    product_id = created_product["id"]
    
    # Make multiple stock adjustments
    adjustments = [
        {"change": 10, "reason": "Initial stock"},
        {"change": -5, "reason": "Sold items"},
        {"change": 20, "reason": "Restocked"}
    ]
    
    for adjustment in adjustments:
        response = authenticated_client.post(f"/products/{product_id}/adjust-stock", json=adjustment)
        assert response.status_code == 200
    
    # Get stock history
    response = authenticated_client.get(f"/products/{product_id}/stock-history")
    assert response.status_code == 200
    history = response.json()
    
    # Verify history contains all adjustments
    assert len(history) == len(adjustments)
    
    # Extract the changes and reasons from history
    history_changes = [entry["change"] for entry in history]
    history_reasons = [entry["reason"] for entry in history]
    
    # Extract expected changes and reasons from adjustments
    expected_changes = [adj["change"] for adj in adjustments]
    expected_reasons = [adj["reason"] for adj in adjustments]
    
    # Verify all changes and reasons are present (order may vary due to timing)
    assert sorted(history_changes) == sorted(expected_changes)
    assert sorted(history_reasons) == sorted(expected_reasons)
