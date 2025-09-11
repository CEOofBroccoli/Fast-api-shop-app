# 🏪 N-Market | فروشگاه ان-مارکت

<div align="center">

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688.svg?style=for-the-badge&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

### 🌟 A Beautiful Persian Inventory Management System

_Combining modern FastAPI backend with elegant Persian frontend design_

[🚀 Quick Start](#-quick-start) • [✨ Features](#-features) • [📖 Documentation](#-api-endpoints) • [🛠️ Development](#%EF%B8%8F-development)

</div>

---

## 🎯 Why Choose N-Market?

<table>
<tr>
<td width="50%">

### 🎨 **Beautiful Persian Design**

- **RTL Layout** - Native right-to-left interface
- **Persian Fonts** - Lalezar & IranianSans typography
- **Bootstrap 5** - Responsive, modern styling
- **Cultural Adaptation** - Designed for Persian markets

</td>
<td width="50%">

### ⚡ **Developer Friendly**

- **No Complex Setup** - Direct table creation, no migrations
- **One Command Deploy** - Docker-compose up and running
- **Clean Architecture** - Simplified, maintainable codebase
- **Comprehensive API** - Auto-generated documentation

</td>
</tr>
</table>

## 🚀 Quick Start

<details>
<summary><strong>🐳 Option 1: Docker (Recommended)</strong></summary>

```bash
# 📥 Clone the repository
git clone https://github.com/yourusername/Fast-api-shop-app.git
cd Fast-api-shop-app

# 🚀 Launch with one command
docker-compose up --build

# ✅ That's it! Your app is running
```

**🎉 Access your application:**

- 🌐 **Persian Frontend**: http://localhost
- 📋 **API Documentation**: http://localhost:8000/docs
- 🗄️ **Database**: Automatically created and ready

</details>

<details>
<summary><strong>💻 Option 2: Local Development</strong></summary>

```bash
# 📁 Setup Python environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 📦 Install dependencies
cd backend
pip install -r requirements.txt

# ⚙️ Configure environment
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux

# 🎯 Launch the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**🔗 Open your browser to:**

- 🌐 **Frontend**: http://localhost (serve index.html with a web server)
- 📋 **API**: http://localhost:8000/docs

</details>

> **💡 Pro Tip:** The Docker option sets up everything automatically, including the database!

## ✨ Features That Make N-Market Special

<div align="center">

|   🎨 **Persian-First Design**    |   📦 **Smart Inventory**    |  🔐 **Secure & Simple**   | 📊 **Business Intelligence** |
| :------------------------------: | :-------------------------: | :-----------------------: | :--------------------------: |
| RTL interface with Persian fonts |  Real-time stock tracking   |    JWT authentication     |   Live dashboard analytics   |
|  Bootstrap 5 responsive design   | Automated inventory updates | Role-based access control |  Sales performance reports   |
|      Cultural color schemes      |      Low stock alerts       |     Password security     |     Inventory valuation      |
|   Mobile-optimized navigation    | Multi-category organization |      Request logging      |      Business insights       |

</div>

### 🌟 **Core Capabilities**

```mermaid
graph LR
    A[Persian Frontend] --> B[FastAPI Backend]
    B --> C[PostgreSQL DB]
    B --> D[Authentication]
    B --> E[Product Management]
    B --> F[Order Processing]
    B --> G[Analytics Dashboard]

    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
```

- **🛍️ Complete E-commerce Flow** - From product display to order completion
- **📱 Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **🔄 Real-time Updates** - Inventory changes reflect immediately
- **📈 Growth Ready** - Scalable architecture for business expansion

## 🏗️ Architecture & Tech Stack

<div align="center">

```ascii
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│  🎨 Persian Frontend │◄──►│  ⚡ FastAPI Backend  │◄──►│  🗄️ PostgreSQL DB   │
│                     │    │                      │    │                     │
│ • RTL Bootstrap 5   │    │ • Python 3.12+      │    │ • Direct Tables     │
│ • Persian Fonts     │    │ • SQLAlchemy ORM     │    │ • Auto-Creation     │
│ • Responsive Design │    │ • JWT Security       │    │ • No Migrations     │
│ • Mobile Optimized  │    │ • Request Logging    │    │ • Simple & Clean    │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

</div>

### 🛠️ **Technology Choices**

<table>
<tr>
<td width="33%">

#### **Frontend Stack**

- 🎨 **HTML5 & CSS3** - Modern web standards
- 🅱️ **Bootstrap 5** - RTL-enabled responsive framework
- 🔤 **Persian Fonts** - Lalezar & IranianSans typography
- 📱 **Mobile-First** - Progressive enhancement design

</td>
<td width="33%">

#### **Backend Stack**

- 🐍 **Python 3.12+** - Latest language features
- ⚡ **FastAPI 0.115.6** - High-performance async framework
- 🗃️ **SQLAlchemy** - Powerful ORM with direct table creation
- 🔐 **JWT Authentication** - Stateless security tokens

</td>
<td width="33%">

#### **Infrastructure**

- 🐳 **Docker & Compose** - Containerized deployment
- 🗄️ **PostgreSQL 13+** - Robust relational database
- 📊 **Automatic API Docs** - OpenAPI/Swagger integration
- 🚀 **Production Ready** - Scalable architecture

</td>
</tr>
</table>

> **🎯 Design Philosophy:** Simplicity without sacrificing functionality. Every component serves a clear purpose.

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

## 📋 API Documentation

<div align="center">

**🔗 Interactive API Documentation Available at `/docs`**

_All endpoints are automatically documented with request/response examples_

</div>

### 🔐 **Authentication & Security**

<table>
<tr>
<td width="60%">

```http
POST /signup              # 👤 User registration with validation
POST /login               # 🔑 JWT token authentication
```

</td>
<td width="40%">

**Security Features:**

- 🔒 Password hashing (bcrypt)
- 🎫 JWT token-based auth
- 📝 Request logging
- 🛡️ CORS protection

</td>
</tr>
</table>

### 📦 **Product Management**

```http
GET    /products              # 📋 List all products with pagination & search
POST   /products              # ➕ Create new product with validation
GET    /products/{id}         # 🔍 Get detailed product information
PUT    /products/{id}         # ✏️ Update product details & stock
DELETE /products/{id}         # 🗑️ Remove product from inventory
```

### 🛒 **Order Management**

```http
GET    /sales-orders          # 📊 List orders with filters & status
POST   /sales-orders          # 🛍️ Create new sales order
GET    /sales-orders/{id}     # 📄 Get complete order details
PUT    /sales-orders/{id}     # 🔄 Update order status & tracking
```

### 📈 **Analytics & Reporting**

```http
GET /dashboard/stats          # 📊 Real-time business metrics
GET /dashboard/low-stock      # ⚠️ Products needing restock
GET /reports/sales-summary    # 📈 Sales performance analysis
```

> **💡 Try it Live:** Visit `/docs` to test all endpoints with the interactive Swagger UI!

## 🛠️ Development

<details>
<summary><strong>🚀 Quick Development Commands</strong></summary>

```bash
# 🔧 Setup everything
make setup          # Install dependencies & setup environment

# 🏃‍♂️ Run development server
make serve          # Start with auto-reload

# 🐳 Docker development
make run-docker     # Run full stack with Docker

# 🧹 Cleanup
make clean          # Remove cache files & cleanup
```

</details>

<details>
<summary><strong>⚙️ Environment Configuration</strong></summary>

Create a `.env` file based on `.env.example`:

```env
# 🗄️ Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/nmarket_db

# 🔐 Security Settings
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 🐛 Development Settings
DEBUG=True
ENVIRONMENT=development

# 🏪 Shop Configuration
SHOP_NAME=N-Market
SHOP_EMAIL=your-shop@example.com
```

> **🔒 Security Note:** Always use a strong, unique SECRET_KEY in production!

</details>

### 🎯 **Why This Architecture?**

<div align="center">

| **Traditional Complex Setup**    | **😫** | **N-Market Simplified**     | **😊** |
| :------------------------------- | :----: | :-------------------------- | :----: |
| Database migrations with Alembic |   ❌   | Direct table creation       |   ✅   |
| Complex CI/CD pipelines          |   ❌   | Simple development workflow |   ✅   |
| Redis caching setup              |   ❌   | Efficient without caching   |   ✅   |
| Extensive testing infrastructure |   ❌   | Manual testing via Swagger  |   ✅   |
| Configuration overhead           |   ❌   | One-file environment setup  |   ✅   |

</div>

**🎉 Result:** 80% less complexity, 100% of the functionality you need!

## 🤝 Contributing

We love contributions! Here's how you can help make N-Market even better:

<details>
<summary><strong>🎯 Ways to Contribute</strong></summary>

- 🐛 **Report Bugs** - Found something broken? Let us know!
- 💡 **Suggest Features** - Have ideas for improvements?
- 🔧 **Submit Code** - Fix issues or add new features
- � **Improve Documentation** - Help others understand the project
- 🌍 **Translations** - Add support for more languages

</details>

<details>
<summary><strong>🚀 Quick Contribution Guide</strong></summary>

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/yourusername/Fast-api-shop-app.git

# 3. Create a feature branch
git checkout -b feature/amazing-new-feature

# 4. Make your changes and test them
make serve  # Test locally

# 5. Commit with a clear message
git commit -m "Add amazing new feature that does X"

# 6. Push and create a Pull Request
git push origin feature/amazing-new-feature
```

</details>

> **💡 Pro Tip:** Test your changes using the Swagger UI at `/docs` before submitting!

---

## �📄 License

<div align="center">

**MIT License** - Feel free to use this project for your business needs!

See the [LICENSE](LICENSE) file for full details.

</div>

---

<div align="center">

## 🎉 **Ready to Start Your Persian E-commerce Journey?**

### **N-Market | فروشگاه ان-مارکت**

_Where simplicity meets functionality_

**Built with ❤️ by developers, for developers**

[⭐ **Star us on GitHub**](https://github.com/yourusername/Fast-api-shop-app) • [🐛 **Report Issues**](https://github.com/yourusername/Fast-api-shop-app/issues) • [💬 **Join Discussions**](https://github.com/yourusername/Fast-api-shop-app/discussions)

---

_Made with FastAPI 🚀 • Designed for Persian Markets 🇮🇷 • Optimized for Developers 👨‍💻_

</div>
