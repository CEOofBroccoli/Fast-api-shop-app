# 🏪 N-Market | فروشگاه ان-مارکت

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://docker.com)

> A simplified, production-ready inventory management system with Persian frontend and FastAPI backend.

## 🚀 Quick Start

### Docker (Recommended)
```bash
git clone https://github.com/yourusername/Fast-api-shop-app.git
cd Fast-api-shop-app
docker-compose up --build
```

### Local Development
```bash
# Setup environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
copy .env.example .env

# Run application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Access Points:**
- 🌐 Frontend: http://localhost
- 📋 API Docs: http://localhost:8000/docs

## ✨ Features

- **Persian RTL Interface** - Complete e-commerce frontend with Persian fonts
- **Product Management** - CRUD operations with stock tracking  
- **Order Processing** - Sales orders with inventory updates
- **User Authentication** - JWT-based security
- **Dashboard Analytics** - Real-time reports and insights
- **Docker Ready** - One-command deployment

## 🏗️ Architecture

```
Persian Frontend (RTL) ↔ FastAPI Backend ↔ PostgreSQL Database
```

**Tech Stack:**
- **Frontend**: HTML5, CSS3, Bootstrap 5 (RTL), Persian fonts
- **Backend**: FastAPI 0.115.6, SQLAlchemy, Python 3.12+
- **Database**: PostgreSQL with direct table creation
- **Deployment**: Docker, Docker Compose

## 📁 Project Structure

```
Fast-api-shop-app/
├── assets/fonts/          # Persian fonts (Lalezar, IranianSans)
├── index.html             # Main Persian frontend
├── style.css              # Persian typography & styling
├── pages/                 # Additional pages (about, etc.)
├── backend/app/           # FastAPI application
│   ├── main.py           # App entry point
│   ├── models/           # Database models
│   ├── routes/           # API endpoints
│   └── auth/             # Authentication
├── docker-compose.yml     # Docker configuration
└── Makefile              # Development commands
```

## 📋 API Endpoints

### Authentication
```http
POST /signup              # User registration
POST /login               # User authentication
```

### Products
```http
GET    /products          # List products
POST   /products          # Create product
GET    /products/{id}     # Get product details
PUT    /products/{id}     # Update product
DELETE /products/{id}     # Delete product
```

### Orders
```http
GET    /sales-orders      # List orders
POST   /sales-orders      # Create order
GET    /sales-orders/{id} # Get order details
PUT    /sales-orders/{id} # Update order
```

### Dashboard
```http
GET /dashboard/stats      # Dashboard data
GET /dashboard/low-stock  # Low stock alerts
GET /reports/sales-summary # Sales reports
```

## 🛠️ Development

### Using Makefile
```bash
make setup          # Install dependencies
make run-dev        # Run development server
make run-docker     # Run with Docker
make clean          # Clean cache
```

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/nmarket_db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=True
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**N-Market Shop Application**

*Simple, Persian-ready, and powerful inventory management*

Made with ❤️ using FastAPI

</div>
