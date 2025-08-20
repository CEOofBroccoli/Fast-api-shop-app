# 🏪 N-Market - FastAPI Inventory Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7.0+-DC382D.svg?style=flat&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **N-Market: inventory management system built with FastAPI, featuring professional branding, real-time analytics, and production-ready deployment.**

## 🌟 **What Makes N-Market Special**

- 🎨 **Professional Branding System** - Context-aware logo layouts for emails, websites, invoices, and mobile
- 📧 **Branded Email Templates** - Professional email communications with centered logo headers
- 🏪 **Complete Shop Management** - From suppliers to sales with full business intelligence
- 🚀 **Production Ready** - Docker containerization with CI/CD pipelines
- 📱 **Responsive Design** - Works seamlessly across all devices and platforms

## 🚀 Features Overview

### 🎨 **Professional Branding System**

- **Context-Aware Logo Layouts** - Different layouts for different use cases
  - 📧 **Email Headers**: Centered 120px square logo with professional typography
  - 🌐 **Website Headers**: Horizontal logo + text layout with gradient backgrounds
  - 📱 **Compact Spaces**: Small icon + "N-Market" text for mobile/sidebar navigation
  - 🧾 **Invoice Headers**: Centered logo with company information for official documents
- **Logo Implementation Showcase** - Visual demonstration of all branding layouts
- **Shop Configuration Management** - Centralized branding settings
- **Professional Email Templates** - Branded communications with company styling

### 🔐 **Authentication & Security**

- **JWT-based authentication** with role-based access control
- **Secure password hashing** using bcrypt
- **Email verification** with token-based system
- **Rate limiting** and security headers
- **RBAC (Role-Based Access Control)** for different user types

### 📦 **Product Management**

- **Complete CRUD operations** for products
- **Advanced search & filtering** by name, SKU, category, price ranges
- **Stock management** with automatic reorder alerts
- **Audit trail** for all stock changes
- **Bulk operations** for efficiency
- **Category management** with hierarchical structure

### 🏢 **Supplier Management**

- **Supplier registration** with contact information
- **Performance tracking** and rating system
- **Delivery lead time management**
- **Purchase order integration**
- **Supplier analytics** and reporting

### 🛒 **Sales & Order Management**

- **Sales order processing** with multi-item support
- **Order status tracking** throughout lifecycle
- **Automatic inventory updates** on order completion
- **Order validation** and stock checking
- **Customer order history**

### 📊 **Business Intelligence Dashboard**

- **Real-time analytics** with Redis caching
- **Low stock alerts** and inventory insights
- **Sales performance metrics**
- **Best-selling products analysis**
- **Revenue tracking** and trend analysis
- **Supplier performance metrics**

### 📋 **Reporting & Invoicing**

- **Professional PDF invoice generation** with branded templates
- **Sales receipts** with N-Market company branding
- **Inventory reports** (low stock, valuation)
- **Sales analytics** by period and category
- **Supplier performance reports**
- **Custom report generation**

### 🔧 **Technical Features**

- **RESTful API** with OpenAPI 3.0 documentation
- **Async/await support** for high performance
- **Redis caching** for optimized response times
- **Database migrations** with Alembic
- **Comprehensive test suite** with pytest
- **Docker containerization** for easy deployment
- **CI/CD ready** with GitHub Actions
- **Monitoring & logging** system
- **Professional error handling** and exception management

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   N-Market UI   │    │   FastAPI API   │    │   PostgreSQL   │
│ (Logo Showcase) │◄──►│     Server      │◄──►│    Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Redis Cache    │
                       │ (Session Store) │
                       └─────────────────┘
```

**Tech Stack:**

- **Backend:** FastAPI 0.109.0, Python 3.13+
- **Database:** PostgreSQL 13+ (Production) / SQLite (Development)
- **Cache:** Redis 7.0+
- **ORM:** SQLAlchemy 2.0+
- **Authentication:** JWT with python-jose
- **PDF Generation:** ReportLab
- **Testing:** pytest, httpx
- **Deployment:** Docker, Docker Compose, Nginx
- **Email:** SMTP with branded templates

## 📖 API Documentation

### 🎨 **Branding & Shop Management**

```http
GET    /shop/info              # Get shop information and branding
GET    /shop/branding          # Get branding assets and layouts
GET    /logo-showcase          # View logo implementation showcase
```

### 🔑 **Authentication Endpoints**

```http
POST   /auth/register          # User registration
POST   /auth/login             # User login
POST   /auth/verify-email/{token}  # Email verification
POST   /auth/forgot-password   # Password reset request
POST   /auth/reset-password    # Password reset
```

### 📦 **Product Management**

```http
GET    /products               # List products (with search/filter)
POST   /products               # Create product
GET    /products/{id}          # Get product details
PUT    /products/{id}          # Update product
DELETE /products/{id}          # Delete product
POST   /products/{id}/adjust-stock  # Manual stock adjustment
GET    /products/{id}/stock-history # Stock change history
```

### 🏢 **Supplier Management**

```http
GET    /suppliers              # List suppliers
POST   /suppliers              # Create supplier
GET    /suppliers/{id}         # Get supplier details
PUT    /suppliers/{id}         # Update supplier
DELETE /suppliers/{id}         # Delete supplier
GET    /suppliers/{id}/performance  # Supplier analytics
```

### 🛒 **Sales Orders**

```http
GET    /sales-orders           # List sales orders
POST   /sales-orders           # Create sales order
GET    /sales-orders/{id}      # Get order details
PUT    /sales-orders/{id}      # Update order status
DELETE /sales-orders/{id}      # Cancel order
```

### 📊 **Dashboard & Analytics**

```http
GET    /dashboard/stats        # Real-time dashboard data
GET    /dashboard/low-stock    # Low stock alerts
GET    /dashboard/best-selling # Best performing products
GET    /dashboard/revenue      # Revenue analytics
```

### 📋 **Reports & Invoicing**

```http
GET    /reports/sales-summary  # Sales performance report
GET    /reports/inventory-valuation  # Inventory value report
GET    /reports/supplier-performance  # Supplier metrics
POST   /invoices/{order_id}/generate  # Generate PDF invoice
POST   /receipts/{order_id}/generate  # Generate PDF receipt
```

## 🚀 Quick Start

### 📋 **Prerequisites**

- Python 3.13+
- PostgreSQL 13+
- Redis 7.0+
- Docker & Docker Compose (recommended)

### 🐳 **Docker Deployment (Recommended)**

1. **Clone the repository**

   ```bash

   ```

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/n-market-inventory-system.git
   cd n-market-inventory-system
   ```

1. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your N-Market configuration
   ```

1. **Start services**

   ```bash
   # Development with PGAdmin
   docker-compose --profile dev up -d

   # Production
   docker-compose up -d
   ```

1. **Run migrations**

   ```bash
   docker-compose exec app alembic upgrade head
   ```

1. **Access the application**
   - **API:** https://localhost/api
   - **API Docs:** https://localhost/api/docs
   - **Logo Showcase:** https://localhost/logo-showcase
   - **PGAdmin:** http://localhost:5050 (dev only)

### 💻 **Local Development**

1. **Set up virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Configure environment variables**

   ```bash
   export DATABASE_URL="postgresql://user:pass@localhost/n_market_db"
   export SECRET_KEY="your-secret-key"
   export REDIS_URL="redis://localhost:6379"
   export SHOP_NAME="N-Market"
   export SHOP_EMAIL="modavari005@gmail.com"
   ```

4. **Run migrations**

   ```bash
   alembic upgrade head
   ```

5. **Start development server**

   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **View logo showcase**
   ```bash
   # Visit http://localhost:8000/logo-showcase to see branding implementations
   ```

## ✨ **Logo Showcase**

N-Market includes a comprehensive logo implementation showcase demonstrating professional branding across different contexts:

- **📧 Email Templates** - Centered 120px logos with professional typography
- **🌐 Website Headers** - Horizontal layouts with gradient backgrounds
- **📱 Mobile Navigation** - Compact layouts for small screens
- **🧾 Invoice Documents** - Professional letterhead formatting

**View the showcase:** `http://localhost:8000/logo-showcase`

## 🧪 Testing

### **Run Test Suite**

```bash
# All tests
pytest

# With coverage
pytest --cov=backend/app --cov-report=html

# Specific test file
pytest tests/test_products.py

# Integration tests only
pytest tests/ -k "integration"
```

### **Test Categories**

- **Unit Tests:** Individual component testing
- **Integration Tests:** API endpoint testing
- **Authentication Tests:** Security validation
- **Database Tests:** ORM and query testing

## 🔧 Development Tools

### **Code Quality**

```bash
# Format code
black backend/

# Sort imports
isort backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/

# Security audit
bandit -r backend/
```

### **Pre-commit Hooks**

```bash
pre-commit install
pre-commit run --all-files
```

## 🚀 Deployment

### **Production Environment Variables**

```env
# N-Market Configuration
SHOP_NAME="N-Market"
SHOP_DESCRIPTION="Your One-Stop Inventory Solution"
SHOP_EMAIL="modavari005@gmail.com"
SHOP_WEBSITE="https://n-market.ir"

# Database
DATABASE_URL=postgresql://user:password@host:5432/n_market_db
REDIS_URL=redis://host:6379/0

# Security
JWT_SECRET_KEY=your-super-secure-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (for branded emails)
SMTP_USERNAME=modavari005@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM="N-Market <modavari005@gmail.com>"
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Application
DEBUG=false
ENVIRONMENT=production
```

### **Cloud Deployment Options**

#### **Docker Hub (Recommended)**

```bash
# Build and push N-Market
docker build -t n-market/inventory-api .
docker tag n-market/inventory-api:latest n-market/inventory-api:v1.0.0
docker push n-market/inventory-api:latest
```

#### **AWS ECS/Fargate**

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin account.dkr.ecr.us-east-1.amazonaws.com
docker build -t n-market-api .
docker tag n-market-api:latest account.dkr.ecr.us-east-1.amazonaws.com/n-market-api:latest
docker push account.dkr.ecr.us-east-1.amazonaws.com/n-market-api:latest
```

#### **Google Cloud Run**

```bash
# Deploy N-Market to Cloud Run
gcloud run deploy n-market-api \
  --image gcr.io/project-id/n-market-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### **Azure Container Apps**

```bash
# Deploy N-Market to Azure
az containerapp create \
  --name n-market-api \
  --resource-group n-market-rg \
  --environment n-market-env \
  --image myregistry.azurecr.io/n-market-api:latest
```

## 📊 Performance & Monitoring

### **Performance Features**

- **Redis caching** for frequently accessed data and shop settings
- **Database indexing** for optimized product and order queries
- **Async/await** for concurrent request handling
- **Connection pooling** for database efficiency
- **Response compression** for faster API calls
- **Professional branding caching** for optimized logo delivery

### **Monitoring & Observability**

- **Health check endpoints** (`/health`, `/ready`)
- **Prometheus metrics** integration
- **Structured logging** with correlation IDs
- **Error tracking** and alerting
- **Performance metrics** dashboard
- **Logo showcase analytics** for branding insights

## 🔒 Security

### **Security Features**

- **JWT tokens** with expiration
- **Password hashing** with bcrypt + salt
- **Rate limiting** to prevent abuse
- **CORS configuration** for secure cross-origin requests
- **Security headers** (HSTS, CSP, etc.)
- **Input validation** with Pydantic
- **SQL injection prevention** with SQLAlchemy ORM

### **Security Best Practices**

- Regular dependency updates
- Environment variable management
- Secure session handling
- API versioning strategy
- Audit logging for sensitive operations

### **Development Process**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
📧 **Contact:** [modavari005@gmail.com](mailto:modavari005@gmail.com)  
🌐 **Website:** [https://n-market.ir](https://n-market.ir)  
📱 **Logo Showcase:** [http://localhost:8000/logo-showcase](http://localhost:8000/logo-showcase)
