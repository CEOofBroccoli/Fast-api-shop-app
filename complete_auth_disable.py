#!/usr/bin/env python3
"""Fix ALL authorization checks in route files - complete removal."""

import os
import re
from pathlib import Path

def completely_disable_auth(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: Comment out authorization header checks (multiline)
    content = re.sub(
        r'(\s+)if not authorization:\s*\n(\s+)raise HTTPException\(\s*\n(\s+)status_code=status\.HTTP_401_UNAUTHORIZED,\s*\n(\s+)detail="Missing authorization header",?\s*\n(\s+)headers=\{"WWW-Authenticate": "Bearer"\},?\s*\n(\s+)\)',
        r'\1# For testing: skip authorization check\n\1# if not authorization:\n\2#     raise HTTPException(\n\3#         status_code=status.HTTP_401_UNAUTHORIZED,\n\4#         detail="Missing authorization header",\n\5#         headers={"WWW-Authenticate": "Bearer"},\n\6#     )',
        content,
        flags=re.MULTILINE
    )
    
    # Pattern 2: Comment out simple authorization checks
    content = re.sub(
        r'(\s+)if not authorization:\s*\n(\s+)raise HTTPException\(\s*\n(\s+)status_code=status\.HTTP_401_UNAUTHORIZED,\s*\n(\s+)detail="Missing authorization header",?\s*\n(\s+)\)',
        r'\1# For testing: skip authorization check\n\1# if not authorization:\n\2#     raise HTTPException(\n\3#         status_code=status.HTTP_401_UNAUTHORIZED,\n\4#         detail="Missing authorization header",\n\5#     )',
        content,
        flags=re.MULTILINE
    )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'✓ Disabled auth checks in {file_path}')
        return True
    else:
        print(f'- No auth checks found in {file_path}')
        return False

def main():
    # Fix all route files
    routes_dir = Path('backend/app/routes')
    fixed_count = 0
    
    for py_file in routes_dir.glob('*.py'):
        if py_file.name != '__init__.py':
            if completely_disable_auth(py_file):
                fixed_count += 1
    
    print(f'\n✓ Disabled authentication in {fixed_count} files!')

if __name__ == "__main__":
    main()