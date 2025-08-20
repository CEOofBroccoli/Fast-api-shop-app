@echo off
REM N-Market Development Setup Script for Windows
REM Run this after cloning the repository

echo 🏪 Setting up N-Market Inventory System...

REM Check if .env exists
if not exist .env (
    echo 📋 Creating .env file from template...
    copy .env.example .env
    echo ✅ .env file created
    echo ⚠️  Please edit .env file and update:
    echo    - JWT_SECRET_KEY ^(generate a secure key^)
    echo    - SMTP_USERNAME and SMTP_PASSWORD ^(for email features^)
    echo    - SHOP_EMAIL ^(your business email^)
) else (
    echo ✅ .env file already exists
)

REM Check if virtual environment exists
if not exist venv (
    echo 🐍 Creating Python virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment and install dependencies
echo 📦 Installing dependencies...
call venv\Scripts\activate
pip install -r backend\requirements.txt

echo 🗄️  Setting up database...
REM Run migrations
python -m alembic upgrade head

echo 🚀 Setup complete!
echo.
echo To start the development server:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Start server: uvicorn backend.app.main:app --reload --port 8000
echo 3. Visit: http://localhost:8000/docs for API documentation
echo 4. Visit: http://localhost:8000/logo-showcase for branding showcase
echo.
echo For Docker development:
echo 1. docker-compose --profile dev up -d
echo 2. Visit: http://localhost/docs

pause
