import requests
import json
from typing import Dict, Optional

BASE_URL = "http://localhost:8000"  # Update this if your server runs on a different port

def login(username: str, password: str) -> Optional[str]:
    """Login and return the access token."""
    login_data = {
        "grant_type": "password",  # Required by OAuth2PasswordRequestForm
        "username": username,
        "password": password,
        "scope": "",  # Optional
        "client_id": "",  # Optional
        "client_secret": ""  # Optional
    }
    try:
        response = requests.post(f"{BASE_URL}/login", data=login_data)
        if response.status_code == 200:
            return response.json().get("access_token")
        print(f"Login failed: {response.status_code}")
        print(response.json())
        return None
    except Exception as e:
        print(f"Login error: {str(e)}")
        return None

def create_sales_order(token: str) -> None:
    """Test creating a sales order with authentication."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Sample sales order data
    order_data = {
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "customer_phone": "1234567890",
        "items": [
            {
                "product_id": 1,  # Make sure this product ID exists in your database
                "quantity": 1
            }
        ]
    }
    
    try:
        print("\nAttempting to create sales order...")
        print(f"Using headers: {headers}")
        response = requests.post(
            f"{BASE_URL}/sales-orders/",
            headers=headers,
            json=order_data
        )
        print(f"\nStatus Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error creating sales order: {str(e)}")

def list_sales_orders(token: str) -> None:
    """Test listing sales orders with authentication."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("\nAttempting to list sales orders...")
        print(f"Using headers: {headers}")
        response = requests.get(
            f"{BASE_URL}/sales-orders/",
            headers=headers
        )
        print(f"\nStatus Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error listing sales orders: {str(e)}")

def main():
    # Update these credentials to match a valid user in your system
    username = "admin"  # Replace with a valid username
    password = "admin123"  # Replace with the correct password
    
    print("Testing Authentication and Sales Orders\n")
    print(f"Attempting to login as {username}...")
    
    token = login(username, password)
    if not token:
        print("Failed to get authentication token. Exiting.")
        return
    
    print("\nSuccessfully obtained token!")
    print(f"Token: {token}\n")
    
    # Test both endpoints
    list_sales_orders(token)
    create_sales_order(token)

if __name__ == "__main__":
    main()