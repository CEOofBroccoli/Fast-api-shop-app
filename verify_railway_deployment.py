#!/usr/bin/env python3
"""
Railway deployment verification script
Checks import paths and configurations for Railway deployment
"""

import sys
import os
from pathlib import Path

def check_railway_structure():
    """Check if the project structure is compatible with Railway deployment"""
    print("🔍 Checking Railway deployment compatibility...")
    
    # Check required files
    required_files = [
        "railway.dockerfile",
        "railway.json", 
        "backend/requirements.txt",
        "backend/app/main.py",
        "alembic.ini"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files present")
    
    # Check Python path compatibility
    print("\n🔍 Checking Python import paths...")
    
    # Add backend to Python path temporarily
    backend_path = os.path.join(os.getcwd(), "backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    try:
        # Test critical imports
        from app.main import app
        from app.database import get_db
        from app.config.shop_settings import shop_settings
        print("✅ Core imports successful")
        
        # Check if health endpoint exists
        routes = [route.path for route in app.routes]
        if "/health" in routes:
            print("✅ Health endpoint configured")
        else:
            print("❌ Health endpoint missing")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def generate_deployment_checklist():
    """Generate a deployment checklist"""
    print("\n📋 Railway Deployment Checklist:")
    print("="*50)
    
    checklist = [
        "□ GitHub repository pushed with latest changes",
        "□ Railway account created and connected to GitHub",
        "□ Environment variables configured in Railway",
        "□ PostgreSQL service added to Railway project",
        "□ Redis service added to Railway project (optional)",
        "□ Custom domain configured (optional)",
        "□ SSL certificate configured (automatic with Railway)",
        "□ Health check endpoint tested locally",
        "□ Database migrations tested",
        "□ API documentation accessible at /docs"
    ]
    
    for item in checklist:
        print(f"  {item}")
    
    print("\n🚀 Ready for Railway deployment!")

if __name__ == "__main__":
    print("Railway Deployment Verification")
    print("="*40)
    
    # Change to project root directory if running from subdirectory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    success = check_railway_structure()
    
    if success:
        generate_deployment_checklist()
        print("\n✅ Project is ready for Railway deployment!")
        print("\nNext steps:")
        print("1. Push your code to GitHub")
        print("2. Follow the Railway deployment guide")
        print("3. Monitor the deployment logs")
    else:
        print("\n❌ Project needs fixes before Railway deployment")
        sys.exit(1)
