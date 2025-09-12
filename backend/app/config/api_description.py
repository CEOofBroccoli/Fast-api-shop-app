"""API Description
Here we define the API description for the FastAPI app without any syntax issues."""

FASTAPI_DESCRIPTION = '''
## Features

* **User Management**: Secure registration, authentication, and role-based access control
* **Product Management**: Inventory tracking, stock adjustments with audit trail
* **Supplier Management**: Supplier registration, performance tracking, and ratings
* **Sales Orders**: Complete order lifecycle management with status tracking
* **Purchase Orders**: Automated reordering and supplier management
* **Dashboard & Analytics**: Real-time business insights and performance metrics
* **Invoice Generation**: Professional PDF invoices and receipts
* **Reporting**: Generate insights and analytics on sales and inventory

## Authentication

All endpoints except login and signup require JWT authentication using bearer tokens.
Include an `Authorization: Bearer <token>` header with all requests.

## Role-Based Access

* **admin**: Full system access
* **manager**: Product and order management, reporting
* **staff**: Limited product management, order processing
* **customer**: View products, manage own orders
'''