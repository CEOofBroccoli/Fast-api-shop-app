#!/bin/bash
# N-Market Development Setup Script
# Run this after cloning the repository

echo "🏪 Setting up N-Market Inventory System..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env file and update:"
    echo "   - JWT_SECRET_KEY (generate a secure key)"
    echo "   - SMTP_USERNAME and SMTP_PASSWORD (for email features)"
    echo "   - SHOP_EMAIL (your business email)"
else
    echo "✅ .env file already exists"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate  # For Unix systems
pip install -r backend/requirements.txt

echo "🗄️  Setting up database..."
# Run migrations
python -m alembic upgrade head

echo "🚀 Setup complete!"
echo ""
echo "To start the development server:"
echo "1. Activate virtual environment: source venv/bin/activate (Unix) or venv\\Scripts\\activate (Windows)"
echo "2. Start server: uvicorn backend.app.main:app --reload --port 8000"
echo "3. Visit: http://localhost:8000/docs for API documentation"
echo "4. Visit: http://localhost:8000/logo-showcase for branding showcase"
echo ""
echo "For Docker development:"
echo "1. docker-compose --profile dev up -d"
echo "2. Visit: http://localhost/docs"
