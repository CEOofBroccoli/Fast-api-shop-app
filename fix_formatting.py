#!/usr/bin/env python3
"""
Fix Black formatting issues reported by GitHub Actions
"""

import os

def fix_email_utils():
    """Fix email_utils.py formatting"""
    file_path = "backend/app/email_utils.py"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the Subject assignment
    old_pattern = '''        msg[
            "Subject"
        ] = f"{shop_settings.shop_name} - {subject}"  # Add shop name to subject'''
    
    new_pattern = '''        msg["Subject"] = (
            f"{shop_settings.shop_name} - {subject}"  # Add shop name to subject
        )'''
    
    content = content.replace(old_pattern, new_pattern)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {file_path}")

def fix_utils_init():
    """Fix utils/__init__.py formatting"""
    file_path = "backend/app/utils/__init__.py"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the assignment
    old_pattern = '''    setup_logging = (
        get_request_logger
    ) = configure_logging_from_env = JsonFormatter = None'''
    
    new_pattern = '''    setup_logging = get_request_logger = configure_logging_from_env = JsonFormatter = (
        None
    )'''
    
    content = content.replace(old_pattern, new_pattern)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {file_path}")

def fix_security_headers():
    """Fix security_headers.py formatting"""
    file_path = "backend/app/utils/security_headers.py"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the header assignment
    old_pattern = '''            response.headers[
                "Strict-Transport-Security"
            ] = "max-age=31536000; includeSubDomains"'''
    
    new_pattern = '''            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )'''
    
    content = content.replace(old_pattern, new_pattern)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {file_path}")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    fix_email_utils()
    fix_utils_init()
    fix_security_headers()
    print("All formatting fixes applied!")
