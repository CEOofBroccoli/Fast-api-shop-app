# 🏪 FastAPI Inventory Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7.0+-DC382D.svg?style=flat&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **A comprehensive, enterprise-grade inventory management system built with FastAPI, featuring real-time analytics, automated workflows, and production-ready deployment.**

## 🚀 Features Overview

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

- **Professional PDF invoice generation**
- **Sales receipts** with company branding
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

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Frontend    │    │   FastAPI API   │    │   PostgreSQL   │
│   (React/Vue)   │◄──►│     Server      │◄──►│    Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Redis Cache    │
                       │ (Session Store) │
                       └─────────────────┘
```

**Tech Stack:**

- **Backend:** FastAPI 0.109.0, Python 3.8+
- **Database:** PostgreSQL 13+ (Production) / SQLite (Testing)
- **Cache:** Redis 7.0+
- **ORM:** SQLAlchemy 2.0+
- **Authentication:** JWT with python-jose
- **PDF Generation:** ReportLab
- **Testing:** pytest, httpx
- **Deployment:** Docker, Docker Compose

## 📖 API Documentation

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

- Python 3.8+
- PostgreSQL 13+
- Redis 7.0+
- Docker & Docker Compose (optional)

### 🐳 **Docker Deployment (Recommended)**

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/fastapi-inventory-system.git
   cd fastapi-inventory-system
   ```

2. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services**

   ```bash
   # Development with PGAdmin
   docker-compose --profile dev up -d

   # Production
   docker-compose up -d
   ```

4. **Run migrations**

   ```bash
   docker-compose exec app alembic upgrade head
   ```

5. **Access the application**
   - **API:** https://localhost/api
   - **Docs:** https://localhost/api/docs
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
   export DATABASE_URL="postgresql://user:pass@localhost/dbname"
   export SECRET_KEY="your-secret-key"
   export REDIS_URL="redis://localhost:6379"
   ```

4. **Run migrations**

   ```bash
   alembic upgrade head
   ```

5. **Start development server**
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

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
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname
REDIS_URL=redis://host:6379/0

# Security
SECRET_KEY=your-super-secure-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration
EMAIL_USERNAME=your-email@company.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=noreply@company.com
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587

# Application
APP_NAME="Inventory Management System"
DEBUG=false
ENVIRONMENT=production
```

### **Cloud Deployment Options**

#### **AWS ECS/Fargate**

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin account.dkr.ecr.us-east-1.amazonaws.com
docker build -t inventory-api .
docker tag inventory-api:latest account.dkr.ecr.us-east-1.amazonaws.com/inventory-api:latest
docker push account.dkr.ecr.us-east-1.amazonaws.com/inventory-api:latest
```

#### **Google Cloud Run**

```bash
# Deploy to Cloud Run
gcloud run deploy inventory-api \
  --image gcr.io/project-id/inventory-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### **Azure Container Apps**

```bash
# Deploy to Azure
az containerapp create \
  --name inventory-api \
  --resource-group myResourceGroup \
  --environment myEnvironment \
  --image myregistry.azurecr.io/inventory-api:latest
```

## 📊 Performance & Monitoring

### **Performance Features**

- **Redis caching** for frequently accessed data
- **Database indexing** for optimized queries
- **Async/await** for concurrent request handling
- **Connection pooling** for database efficiency
- **Response compression** for faster API calls

### **Monitoring & Observability**

- **Health check endpoints** (`/health`, `/ready`)
- **Prometheus metrics** integration
- **Structured logging** with correlation IDs
- **Error tracking** and alerting
- **Performance metrics** dashboard

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

## 📈 Roadmap

### **Upcoming Features**

- [ ] **Multi-tenant support** for SaaS deployment
- [ ] **Advanced analytics** with machine learning insights
- [ ] **Mobile app** with React Native
- [ ] **Barcode scanning** integration
- [ ] **Automated reordering** based on demand forecasting
- [ ] **Integration APIs** for accounting software
- [ ] **Warehouse management** with location tracking
- [ ] **Notification system** with webhooks

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### **Development Process**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **Contribution Areas**

- 🐛 Bug fixes and improvements
- ✨ New features and enhancements
- 📚 Documentation improvements
- 🧪 Test coverage expansion
- 🔧 DevOps and deployment optimization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** team for the amazing framework
- **SQLAlchemy** team for the robust ORM
- **Pydantic** team for data validation
- Open source community for continuous inspiration

---

**⭐ Star this repository if it helped you!**

For questions, issues, or feature requests, please [open an issue](https://github.com/yourusername/fastapi-inventory-system/issues).

📧 **Contact:** [your-email@company.com](mailto:your-email@company.com)
