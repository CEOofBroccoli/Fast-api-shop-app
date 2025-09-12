#!/usr/bin/env python3
"""
Script to disable authentication across all route files for easier testing.
This script will comment out authorization checks in all route files.
"""

import os
import re
from pathlib import Path

def disable_auth_in_file(file_path):
    """Disable authentication checks in a route file."""
    print(f"Processing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: Comment out authorization header checks
    content = re.sub(
        r'(\s+)if not authorization:\s*\n(\s+)raise HTTPException\(\s*\n(\s+)status_code=status\.HTTP_401_UNAUTHORIZED,\s*\n(\s+)detail="Missing authorization header",?\s*\n(\s+)\)',
        r'\1# For testing: skip authorization check\n\1# if not authorization:\n\2#     raise HTTPException(\n\3#         status_code=status.HTTP_401_UNAUTHORIZED,\n\4#         detail="Missing authorization header",\n\5#     )',
        content,
        flags=re.MULTILINE
    )
    
    # Pattern 2: Comment out token extraction
    content = re.sub(
        r'(\s+)token = authorization\.split\(" "\)\[1\]',
        r'\1# token = authorization.split(" ")[1]  # Disabled for testing',
        content
    )
    
    # Pattern 3: Replace get_user_from_token calls with test version
    content = re.sub(
        r'(\s+)user = get_user_from_token\(token, db\)',
        r'\1user = get_user_from_token("", db)  # Pass empty token for testing',
        content
    )
    
    # Pattern 4: Comment out role checks
    content = re.sub(
        r'(\s+)if user\.role not in \[([^\]]+)\]:\s*\n(\s+)raise HTTPException\(status_code=40[23], detail="[^"]+"\)',
        r'\1# For testing: skip role check\n\1# if user.role not in [\2]:\n\3#     raise HTTPException(status_code=403, detail="Insufficient permissions")',
        content,
        flags=re.MULTILINE
    )
    
    # Pattern 5: Comment out get_current_user_and_check_role calls
    content = re.sub(
        r'(\s+)await get_current_user_and_check_role\(authorization, db, \[([^\]]+)\]\)',
        r'\1# For testing: skip role check\n\1# await get_current_user_and_check_role(authorization, db, [\2])',
        content
    )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Updated {file_path}")
        return True
    else:
        print(f"- No changes needed in {file_path}")
        return False

def main():
    """Main function to process all route files."""
    routes_dir = Path("backend/app/routes")
    
    if not routes_dir.exists():
        print(f"Routes directory not found: {routes_dir}")
        return
    
    updated_files = 0
    
    # Process all Python files in routes directory
    for py_file in routes_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        if disable_auth_in_file(py_file):
            updated_files += 1
    
    print(f"\n✓ Processing complete. Updated {updated_files} files.")
    print("\n⚠️  REMEMBER: This is for TESTING ONLY!")
    print("   Re-enable authentication before production deployment.")

if __name__ == "__main__":
    main()